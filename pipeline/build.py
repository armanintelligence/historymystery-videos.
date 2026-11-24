"""Build one Short from an episode folder.

Usage:  python3 pipeline/build.py episodes/<slug>
Output: videos/<slug>.mp4  (1080x1920, 30 fps, AI narrator + natural sounds, no music)

The episode folder holds scenes.py, which must define:
  SCENES  list of (name, draw_fn(t) -> PIL.Image, base_duration_s, captions)
          captions = list of (start, end, text, [highlight words]) in base-duration time
  SFX(track, G)   adds natural sounds; G(scene_name, base_time) -> time in the final video
Optional: SPOKEN dict {caption text: how to say it}, OUTRO (spoken last line, no caption),
          VOICE, SPEED.
"""
import os, sys, json, math, subprocess, importlib.util
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import W, H, FPS, caption, caps_at, ramp
from sfx import Track, SR

ep_dir = os.path.abspath(sys.argv[1])
slug = os.path.basename(ep_dir.rstrip('/'))
repo = os.path.dirname(HERE)
work = os.path.join('/tmp/build', slug)
os.makedirs(work + '/parts', exist_ok=True)
os.makedirs(os.path.join(repo, 'videos'), exist_ok=True)

spec = importlib.util.spec_from_file_location('ep', os.path.join(ep_dir, 'scenes.py'))
ep = importlib.util.module_from_spec(spec); sys.path.insert(0, ep_dir); spec.loader.exec_module(ep)
SCENES = ep.SCENES
SPOKEN = getattr(ep, 'SPOKEN', {})
OUTRO = getattr(ep, 'OUTRO', 'Follow for more unexplained history.')
VOICE = getattr(ep, 'VOICE', 'bm_george')
SPEED = getattr(ep, 'SPEED', 0.92)

# ---------- 1. narration ----------
from kokoro_onnx import Kokoro
KD = os.environ.get('KOKORO_DIR', os.path.expanduser('~/.cache/kokoro'))
kk = Kokoro(os.path.join(KD, 'kokoro-v1.0.onnx'), os.path.join(KD, 'voices-v1.0.bin'))

def say(text, fn):
    a, sr = kk.create(text.replace('…', '...'), voice=VOICE, speed=SPEED,
                      lang='en-gb' if VOICE.startswith('b') else 'en-us')
    thr = 0.01 * np.abs(a).max(); nz = np.where(np.abs(a) > thr)[0]
    a = a[max(nz[0] - 600, 0): nz[-1] + 1200]
    sf.write(fn, a, sr)
    return len(a) / sr

clips = {}
for name, fn, dur, caps in SCENES:
    lst = []
    for j, (a, b, text, hl) in enumerate(caps):
        f = f'{work}/{name}_{j}.wav'
        lst.append([f, say(SPOKEN.get(text, text), f), text, hl])
    clips[name] = lst
last = SCENES[-1][0]
f = f'{work}/outro.wav'
clips[last].append([f, say(OUTRO, f), None, []])

# ---------- 2. timeline ----------
LEAD, GAP, TAIL, MINF = 0.35, 0.35, 0.45, 0.7
TL, t0 = [], 0.0
for name, fn, dur, caps in SCENES:
    cl = clips[name]
    need = LEAD + sum(c[1] for c in cl) + GAP * (len(cl) - 1) + TAIL
    new = max(need, dur * MINF)
    placed, caps2, t = [], [], LEAD
    for (f, d, text, hl) in cl:
        placed.append((f, t, d))
        if text:
            caps2.append([t - 0.15, None, text, hl])
        t += d + GAP
    starts = [p[1] for p in placed]
    for i, c in enumerate(caps2):
        nxt = [s for s in starts if s > c[0] + 0.2]
        c[1] = nxt[0] - 0.05 if nxt else new
    if caps2: caps2[0][0] = 0.0
    TL.append(dict(name=name, fn=fn, dur=dur, new=new, ratio=dur / new, caps=[tuple(c) for c in caps2], voice=placed, offset=t0))
    t0 += new
TOTAL = t0
TLD = {s['name']: s for s in TL}
def G(scene, t): return TLD[scene]['offset'] + t / TLD[scene]['ratio']

# ---------- 3. sound ----------
tr = Track(TOTAL)
ep.SFX(tr, G)
sfx = tr.finish()
N = len(sfx)
voice = np.zeros(N)
for s in TL:
    for f, st, d in s['voice']:
        a, sr = sf.read(f)
        a = resample_poly(a, SR, sr); a = a / np.abs(a).max() * 0.9
        i = int((s['offset'] + st) * SR); e = min(i + len(a), N)
        voice[i:e] += a[:e - i]
env = np.convolve(np.abs(voice), np.ones(4800) / 4800, mode='same')
mix = voice + sfx * 0.55 * (1 - 0.55 * np.clip(env / 0.05, 0, 1))
mix = mix / np.abs(mix).max() * 0.95
sf.write(f'{work}/mix.wav', np.stack([mix, mix], 1), SR, subtype='PCM_24')

# ---------- 4. pictures ----------
def frame(s, t):
    img = s['fn'](min(t * s['ratio'], s['dur'] - 1e-3))
    txt, hl, a = caps_at(t, s['caps'])
    caption(img, txt, hl, a)
    new = s['new']
    fade = min(ramp(t, 0, 0.2), 1 - ramp(t, new - 0.2, new))
    if s is TL[0]: fade = 1 - ramp(t, new - 0.2, new)
    if s is TL[-1]: fade = ramp(t, 0, 0.2)
    if fade < 1:
        img = Image.fromarray((np.asarray(img, np.float32) * fade).astype(np.uint8))
    return img

if os.environ.get('PREVIEW'):
    # contact sheet of 2 frames per scene, for checking before the full render
    ims = []
    for s in TL:
        for q in (0.3, 0.75):
            ims.append(frame(s, s['new'] * q).resize((216, 384)))
    sheet = Image.new('RGB', (216 * 10, 384 * math.ceil(len(ims) / 10)))
    for i, im in enumerate(ims): sheet.paste(im, ((i % 10) * 216, (i // 10) * 384))
    sheet.save(f'{work}/preview.png'); print('preview', f'{work}/preview.png'); sys.exit()

prev, lst = 0, []
for s in TL:
    end = int(round((s['offset'] + s['new']) * FPS)); n = end - prev; prev = end
    out = f"{work}/parts/{s['name']}.mp4"; tmp = out.replace('.mp4', '.tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(s, i / FPS).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    os.rename(tmp, out); lst.append(out); print(s['name'], 'rendered', flush=True)
open(f'{work}/list.txt', 'w').write(''.join(f"file '{x}'\n" for x in lst))
final = os.path.join(repo, 'videos', slug + '.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{work}/video.mp4', '-i', f'{work}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', final], check=True)
print('done', final, round(TOTAL, 1), 's')

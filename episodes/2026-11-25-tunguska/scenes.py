"""Episode: The Tunguska Event (1908). Visuals: maps, sky, forest, bog, globe. No living faces."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

# ---------- S1: hook ----------
FB_A, FB_B = (1010, 260), (400, 860)

def s1(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    # sky gradient
    for i in range(0, 1150, 6):
        k = i / 1150
        d.rectangle([0, i, W, i + 6], fill=(int(4 + 10 * k), int(6 + 18 * k), int(13 + 38 * k)))
    draw_stars(d, t)
    # horizon forest silhouette
    d.rectangle([0, 1100, W, H], fill=(3, 5, 9))
    rng = np.random.default_rng(1)
    for x in range(-20, W + 40, 26):
        conifer(d, x + rng.uniform(-6, 6), 1104, rng.uniform(50, 110), (3, 5, 9))
    arr = to_arr(img)
    k = ramp(t, 0.4, 3.3)
    if 0.4 <= t < 3.35:
        e = k ** 1.6
        hx, hy = lerp(FB_A[0], FB_B[0], e), lerp(FB_A[1], FB_B[1], e)
        for j in range(28):
            q = max(e - j * 0.018, 0)
            tx, ty = lerp(FB_A[0], FB_B[0], q), lerp(FB_A[1], FB_B[1], q)
            glow(arr, tx, ty, 26 - j * 0.7, (255, 140, 50), 0.5 * (1 - j / 28))
        glow(arr, hx, hy, 60, (255, 170, 80), 0.9)
        glow(arr, hx, hy, 20, (255, 255, 230), 1.6)
    if t >= 3.35:
        f = math.exp(-(t - 3.35) * 2.2)
        arr += 255 * f
        glow(arr, FB_B[0], 1100, 420, (255, 120, 40), 0.9 * math.exp(-(t - 3.35) * 0.5))
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 3.9, 4.4)
    if a > 0:
        text_c(d, (W / 2, 520), '1908', F_BIG, WHITE + (int(255 * a),))
        text_c(d, (W / 2, 700), '= 1,000 ATOMIC BOMBS', F_MED, AMBER + (int(255 * a),))
    a2 = ramp(t, 6.5, 6.8)
    if a2 > 0:
        d.rounded_rectangle([290, 790, 790, 900], radius=18, outline=(255, 90, 70, int(255 * a2)), width=6)
        text_c(d, (W / 2, 845), 'NO CRATER', F_MED, (255, 90, 70, int(255 * a2)))
    top_label(img, 'SIBERIA · 1908', ramp(t, 0.2, 0.6))
    return img

CAPS1 = [(0.3, 6.4, 'In 1908, something exploded over Siberia with the force of a thousand atomic bombs…', ['1908,', 'thousand', 'atomic', 'bombs…']),
         (6.4, 9.0, '…and left no crater.', ['no', 'crater.'])]

# ---------- S2: map zoom ----------
def cam2(t):
    k = ease(ramp(t, 0.0, 3.6))
    s = math.exp(lerp(math.log(9), math.log(55), k))
    return Cam(lerp(72, SITE[0], k), lerp(50, SITE[1], k), s)

def pin(d, x, y, t0, t, label=None):
    a = ramp(t, t0, t0 + 0.3)
    if a <= 0:
        return
    pr = 30 + 40 * ((t - t0) % 1.2) / 1.2
    pa = int(200 * a * (1 - ((t - t0) % 1.2) / 1.2))
    d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=AMBER + (pa,), width=4)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=AMBER + (int(255 * a),))
    if label:
        d.text((x - 30, y - 42), label, font=F_LABEL, fill=WHITE + (int(255 * a),), anchor='rs')

def s2(t):
    cam = cam2(t)
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    x, y = cam.xy(*SITE)
    if t >= 3.9:
        arr = to_arr(img)
        e = ramp(t, 3.9, 5.7) ** 1.4
        ax, ay = x + 600, y + 260
        hx, hy = lerp(ax, x, e), lerp(ay, y, e)
        for j in range(22):
            q = max(e - j * 0.03, 0)
            glow(arr, lerp(ax, x, q), lerp(ay, y, q), 18 - j * 0.5, (255, 140, 50), 0.5 * (1 - j / 22))
        glow(arr, hx, hy, 40, (255, 180, 90), 1.0)
        img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    pin(d, x, y, 2.6, t, 'TUNGUSKA')
    top_label(img, '30 JUNE 1908 · JUST AFTER 7 AM')
    return img

CAPS2 = [(0.0, 3.0, 'June 30th, just after 7 a.m.', ['June', '30th,']),
         (3.0, 6.0, 'A fireball as bright as the Sun streaks across the sky.', ['fireball', 'Sun'])]

# ---------- S3: blast ----------
def s3(t):
    cam = Cam(SITE[0], SITE[1], 55 * (1 + 0.04 * t))
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    x, y = cam.xy(*SITE)
    arr = to_arr(img)
    f = math.exp(-max(t - 0.1, 0) * 3)
    glow(arr, x, y, 260, (255, 130, 40), 1.4 * f)
    glow(arr, x, y, 80, (255, 240, 200), 2.0 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(4):
        tt = t - 0.1 - i * 0.35
        if tt > 0:
            r = 40 + tt * 330
            a = max(0, 1 - tt / 2.2)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 170, 90, int(230 * a)), width=8)
    top_label(img, 'THE BLAST')
    return img

CAPS3 = [(0.0, 3.5, 'Then a blast knocks people off their feet.', ['blast'])]

# ---------- S4: trees ----------
rng4 = np.random.default_rng(7)
TREES = []
while len(TREES) < 1700:
    px, py = rng4.uniform(-420, 420, 2)
    if px * px + py * py < 420 * 420:
        TREES.append((px, py, rng4.uniform(0.75, 1.25), rng4.uniform(-0.25, 0.25)))
TC = (540, 720)

def s4(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([TC[0] - 450, TC[1] - 450, TC[0] + 450, TC[1] + 450], fill=(24, 32, 22))
    wave = lerp(0, 470, ease(ramp(t, 0.4, 3.4)))
    for px, py, sc, jit in TREES:
        dist = math.hypot(px, py)
        x, y = TC[0] + px, TC[1] + py
        if dist < wave and dist > 45:
            ang = math.atan2(py, px) + jit * 0.3
            L = 30 * sc
            x2, y2 = x + L * math.cos(ang), y + L * math.sin(ang)
            d.line([x, y, x2, y2], fill=(150, 112, 74), width=4)
        elif dist <= 45 and wave > 45:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 100, 80))
        else:
            r = 8 * sc
            g = int(80 + 30 * jit * 4)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(30, g, 48))
    if wave > 0:
        d.ellipse([TC[0] - wave, TC[1] - wave, TC[0] + wave, TC[1] + wave], outline=(255, 170, 90, 140), width=3)
    d.ellipse([TC[0] - 10, TC[1] - 10, TC[0] + 10, TC[1] + 10], fill=AMBER)
    n = int(80_000_000 * ease(ramp(t, 0.4, 3.4)))
    text_c(d, (W / 2, 205), f'{n:,}', F_HUGE, WHITE)
    text_c(d, (W / 2, 1215), 'TREES FLATTENED · 2,150 km²', F_LABEL, AMBER)
    return img

CAPS4 = [(0.0, 5.5, 'Eighty million trees are flattened…', ['Eighty', 'million'])]

# ---------- S5: London comparison ----------
def s5(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    k = ease(ramp(t, 0.1, 1.0)); k2 = ease(ramp(t, 0.9, 1.9))
    rb = 400 * k
    rl = 400 * math.sqrt(1570 / 2150) * k2
    cx, cy = 540, 700
    if rb > 0:
        d.ellipse([cx - rb, cy - rb, cx + rb, cy + rb], fill=(255, 140, 50, 70), outline=AMBER, width=6)
    if rl > 0:
        d.ellipse([cx - rl, cy - rl, cx + rl, cy + rl], outline=CYAN, width=6)
    a = ramp(t, 1.0, 1.4)
    text_c(d, (cx, cy - 120), 'GREATER LONDON', F_LABEL, CYAN + (int(255 * ramp(t, 1.9, 2.3)),))
    text_c(d, (cx, cy - 70), '≈1,570 km²', F_LABEL, CYAN + (int(255 * ramp(t, 1.9, 2.3)),))
    text_c(d, (cx, 240), 'BLAST ZONE · 2,150 km²', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'TO SCALE', 1)
    return img

CAPS5 = [(0.0, 3.5, '…across an area bigger than London.', ['bigger', 'London.'])]

# ---------- S6: bright nights ----------
def s6(t):
    cam = Cam(18, 54, 15)
    img = draw_map(Image.new('RGB', (W, H)), cam, land=(30, 38, 54), coast=(70, 86, 112), water=(6, 10, 18))
    arr = to_arr(img)
    pulse = 0.85 + 0.15 * math.sin(t * 2.4)
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.clip(1 - yy / 900, 0, 1) ** 1.5 * 70 * pulse * ramp(t, 0, 1.2)
    arr += band[..., None] * np.array([0.8, 0.9, 1.0], np.float32)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ease(ramp(t, 2.6, 3.3))
    if a > 0:
        ox = lerp(1200, 560, a)
        y0 = 780
        d.rounded_rectangle([ox - 230, y0, ox + 230, y0 + 300], radius=10, fill=(236, 230, 214, int(255 * a)))
        d.text((ox, y0 + 40), 'NEWS', font=F_MED, fill=(30, 30, 30, int(255 * a)), anchor='mm')
        for i in range(6):
            w_ = 380 if i % 3 else 300
            d.rectangle([ox - 190, y0 + 90 + i * 30, ox - 190 + w_, y0 + 104 + i * 30], fill=(120, 115, 105, int(255 * a)))
        d.rounded_rectangle([ox + 70, y0 - 50, ox + 260, y0 + 20], radius=14, fill=(10, 14, 24, int(240 * a)))
        d.text((ox + 165, y0 - 15), '00:00', font=F_LABEL, fill=AMBER + (int(255 * a),), anchor='mm')
    top_label(img, 'THE NIGHTS AFTER')
    return img

CAPS6 = [(0.0, 3.2, 'For nights afterwards, the sky over Europe glows so bright', ['Europe', 'glows']),
         (3.2, 6.5, 'that people read newspapers at midnight.', ['midnight.'])]

# ---------- S7: Kulik 1927 ----------
def s7(t):
    cam = Cam(102.0, 60.55, 300)
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    d = ImageDraw.Draw(img, 'RGBA')
    pts = [cam.xy(102.6, 59.6), cam.xy(*VANAVARA), cam.xy(*SITE)]
    k = ramp(t, 0.8, 4.2)
    segl = [math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])]
    total = sum(segl); drawn = total * k
    acc = 0
    for i in range(2):
        a, b = pts[i], pts[i + 1]
        L = segl[i]
        upto = min(max(drawn - acc, 0), L)
        n = int(upto // 22)
        for j in range(n):
            q0, q1 = j * 22 / L, (j * 22 + 12) / L
            d.line([lerp(a[0], b[0], q0), lerp(a[1], b[1], q0), lerp(a[0], b[0], q1), lerp(a[1], b[1], q1)], fill=CYAN, width=6)
        acc += L
    for (p, name, t0) in ((pts[1], 'Vanavara trading post', 2.0),):
        a = ramp(t, t0, t0 + 0.3)
        d.ellipse([p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10], fill=CYAN + (int(255 * a),))
        d.text((p[0] + 22, p[1]), name, font=F_SMALL, fill=WHITE + (int(255 * a),), anchor='lm')
    x, y = pts[2]
    a = ramp(t, 4.3, 4.7)
    if a > 0:
        d.ellipse([x - 70, y - 70, x + 70, y + 70], outline=(255, 255, 255, int(200 * a)), width=4)
        a2 = ramp(t, 4.9, 5.2)
        if a2 > 0:
            c = (255, 90, 70, int(255 * a2))
            d.line([x - 55, y - 55, x + 55, y + 55], fill=c, width=12)
            d.line([x - 55, y + 55, x + 55, y - 55], fill=c, width=12)
            d.text((x, y - 100), 'NO CRATER', font=F_MED, fill=c, anchor='ms')
    ab = 1 - ramp(t, 2.0, 2.5)
    if ab > 0:
        text_c(d, (W / 2, 470), '1927', F_BIG, WHITE + (int(235 * ab),))
    top_label(img, "KULIK'S EXPEDITION · 19 YEARS LATER")
    return img

CAPS7 = [(0.0, 4.6, 'Nineteen years later, scientist Leonid Kulik finally reaches the site, expecting a giant crater.', ['Nineteen', 'Leonid', 'Kulik', 'crater.']),
         (4.6, 7.5, "There isn't one.", ["isn't"])]

# ---------- S8: the bog ----------
def s8(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    gy = 560
    d.rectangle([0, gy, W, H], fill=(52, 38, 28))
    d.rectangle([0, gy, W, gy + 40], fill=(40, 58, 36))
    for i, col in enumerate([(62, 45, 32), (74, 56, 40), (58, 64, 74)]):
        d.rectangle([0, gy + 160 + i * 140, W, gy + 300 + i * 140], fill=col)
    cx, bw, bd = 540, 380, 470
    basin = [(cx - bw + i * (2 * bw / 60), gy + bd * math.sin(math.pi * i / 60) ** 0.8) for i in range(61)]
    d.polygon(basin, fill=(34, 25, 19))
    lvl = gy + bd * ease(ramp(t, 0.8, 4.4))
    wpoly = [(x, max(y, lvl)) for x, y in basin]
    if lvl < gy + bd - 5:
        d.polygon(wpoly + [(cx + bw, lvl), (cx - bw, lvl)], fill=(40, 100, 140))
    # stump at bottom
    sb = gy + bd - 6
    stump = (120, 88, 58)
    d.polygon([(cx - 55, sb), (cx + 55, sb), (cx + 40, sb - 120), (cx - 40, sb - 128)], fill=stump)
    for dx, L in ((-60, 70), (60, 70), (-30, 45), (30, 45)):
        d.line([cx + dx * 0.6, sb - 5, cx + dx * 0.6 + (L if dx > 0 else -L), sb + 18], fill=stump, width=12)
    d.ellipse([cx - 41, sb - 140, cx + 40, sb - 116], fill=(150, 116, 80))
    if lvl < sb - 130:
        d.polygon(wpoly + [(cx + bw, lvl), (cx - bw, lvl)], fill=(40, 100, 140, 210))
    a1 = 1 - ramp(t, 2.6, 3.0)
    text_c(d, (W / 2, 420), "THE 'SUSLOV CRATER'", F_MED, WHITE + (int(255 * a1),))
    a2 = ramp(t, 4.5, 4.9)
    if a2 > 0:
        text_c(d, (W / 2, 330), 'AN OLD TREE STUMP', F_MED, AMBER + (int(255 * a2),))
        text_c(d, (W / 2, 410), '→ not an impact crater', F_LABEL, WHITE + (int(255 * a2),))
        d.line([cx, 450, cx, sb - 170], fill=AMBER + (int(255 * a2),), width=5)
    top_label(img, 'DRAINING THE BOG')
    return img

CAPS8 = [(0.0, 3.4, 'He drains a bog he thinks is the impact hole,', ['bog']),
         (3.4, 6.5, 'and finds an old tree stump at the bottom.', ['tree', 'stump'])]

# ---------- S9: airburst ----------
GY9 = 1100
KM = 50
BURST = (600, GY9 - 8 * KM)
rng9 = np.random.default_rng(4)
FOREST9 = [(x, rng9.uniform(70, 120)) for x in range(170, 1090, 30)]

def s9(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(0, GY9, 8):
        k = i / GY9
        d.rectangle([0, i, W, i + 8], fill=(int(8 + 14 * k), int(14 + 26 * k), int(28 + 40 * k)))
    d.rectangle([150, GY9 - 10 * KM, W, GY9 - 5 * KM], fill=(255, 150, 60, 28))
    d.rectangle([0, GY9, W, H], fill=(16, 20, 14))
    d.line([150, GY9, 150, GY9 - 15 * KM], fill=GREY, width=3)
    for km in (0, 5, 10, 15):
        yk = GY9 - km * KM
        d.line([140, yk, 160, yk], fill=GREY, width=3)
        d.text((125, yk), f'{km} km', font=F_SMALL, fill=GREY, anchor='rm')
    d.text((W - 40, GY9 - 7.5 * KM), '5–10 km', font=F_LABEL, fill=AMBER, anchor='rm')
    # shock reaching ground at ~t=3.2
    shock_r = max(t - 2.0, 0) * 420
    for x, h in FOREST9:
        dx = x - BURST[0]
        dist = math.hypot(dx, GY9 - BURST[1])
        tilt = 0.0
        if shock_r > dist:
            tilt = (1.35 if dx >= 0 else -1.35) * min((shock_r - dist) / 120, 1)
            if abs(dx) < 50:
                tilt = 0.0
        conifer(d, x, GY9, h, (34, 62, 40), tilt)
    arr = to_arr(img)
    A = (1080, 160)
    if 0.3 <= t < 2.0:
        e = ramp(t, 0.3, 2.0) ** 1.3
        for j in range(24):
            q = max(e - j * 0.025, 0)
            glow(arr, lerp(A[0], BURST[0], q), lerp(A[1], BURST[1], q), 20 - j * 0.6, (255, 140, 50), 0.5 * (1 - j / 24))
        glow(arr, lerp(A[0], BURST[0], e), lerp(A[1], BURST[1], e), 36, (255, 200, 120), 1.2)
    if t >= 2.0:
        f = math.exp(-(t - 2.0) * 1.6)
        glow(arr, BURST[0], BURST[1], 260, (255, 140, 50), 2.4 * f)
        glow(arr, BURST[0], BURST[1], 90, (255, 250, 220), 3.0 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    if t >= 2.0 and shock_r < 1400:
        a = max(0, 1 - shock_r / 1400)
        d.ellipse([BURST[0] - shock_r, BURST[1] - shock_r, BURST[0] + shock_r, BURST[1] + shock_r], outline=(255, 190, 120, int(220 * a)), width=6)
    a = ramp(t, 6.4, 6.8)
    if a > 0:
        d.rounded_rectangle([140, 230, 940, 420], radius=22, fill=(0, 0, 0, int(170 * a)))
        parts = [('ASTEROID', F_MED, WHITE), (' or ', F_LABEL, GREY), ('COMET?', F_MED, AMBER)]
        tw = sum(d.textlength(p_, font=f_) for p_, f_, _ in parts)
        x = W / 2 - tw / 2
        for p_, f_, c_ in parts:
            d.text((x, 325), p_, font=f_, fill=c_ + (int(255 * a),), anchor='lm')
            x += d.textlength(p_, font=f_)
    top_label(img, 'AN AIRBURST')
    return img

CAPS9 = [(0.0, 4.3, 'Today, scientists think a space rock exploded five to ten kilometres up,', ['space', 'rock', 'five', 'ten', 'kilometres']),
         (4.3, 6.4, 'before it ever hit the ground.', ['ground.']),
         (6.4, 9.0, "Asteroid or comet? That's still debated.", ['debated.'])]

# ---------- S10: globe + end ----------
GC, GR = (540, 700), 330

def ortho(lon, lat, lon0, lat0):
    lo, la = np.radians(lon), np.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    x = np.cos(la) * np.sin(lo - l0)
    y = math.cos(p0) * np.sin(la) - math.sin(p0) * np.cos(la) * np.cos(lo - l0)
    z = math.sin(p0) * np.sin(la) + math.cos(p0) * np.cos(la) * np.cos(lo - l0)
    n = np.hypot(x, y) + 1e-9
    x = np.where(z < 0, x / n, x); y = np.where(z < 0, y / n, y)
    return GC[0] + x * GR, GC[1] - y * GR, z

def s10(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_stars(d, t, 0.7, ymax=H)
    arr = to_arr(img)
    glow(arr, GC[0], GC[1], GR * 1.05, (60, 120, 220), 0.45)
    img = to_img(arr)
    d = ImageDraw.Draw(img)
    d.ellipse([GC[0] - GR, GC[1] - GR, GC[0] + GR, GC[1] + GR], fill=(14, 40, 78))
    lon0 = 70 + t * 9
    for p in GEO['l']['land']:
        x, y, z = ortho(p[:, 0], p[:, 1], lon0, 35)
        if (z > 0).any() and len(p) > 2:
            d.polygon(list(zip(x.tolist(), y.tolist())), fill=(46, 84, 62))
    # rock passing
    arr = to_arr(img)
    if 0.4 <= t < 4.2:
        e = ramp(t, 0.4, 4.2)
        rx, ry = lerp(-80, 1160, e), 300 + 60 * math.sin(e * 3.1)
        for j in range(18):
            glow(arr, rx - j * 14, ry + j * 1.2, 10 - j * 0.4, (255, 150, 70), 0.6 * (1 - j / 18))
        glow(arr, rx, ry, 14, (255, 230, 180), 1.4)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.3, 0.7) * (1 - ramp(t, 3.9, 4.2))
    text_c(d, (W / 2, 1150), 'EVERY FEW HUNDRED YEARS', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'HOW OFTEN?', 1 - ramp(t, 3.9, 4.2))
    a2 = ramp(t, 4.1, 4.5)
    if a2 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(150 * a2)))
        text_c(d, (W / 2, 600), 'FOLLOW', F_HUGE, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 720), 'for more unexplained history', F_MED, AMBER + (int(255 * a2),))
    return img

CAPS10 = [(0.0, 4.1, 'And something that size hits Earth every few hundred years.', ['few', 'hundred', 'years.'])]

SCENES = [
    ('s01', s1, 9.0, CAPS1),
    ('s02', s2, 6.0, CAPS2),
    ('s03', s3, 3.5, CAPS3),
    ('s04', s4, 5.5, CAPS4),
    ('s05', s5, 3.5, CAPS5),
    ('s06', s6, 6.5, CAPS6),
    ('s07', s7, 7.5, CAPS7),
    ('s08', s8, 6.5, CAPS8),
    ('s09', s9, 9.0, CAPS9),
    ('s10', s10, 7.0, CAPS10),
]



SPOKEN = {
    'June 30th, just after 7 a.m.': 'June thirtieth, just after seven a.m.',
    'Then a blast knocks people off their feet.': 'Then, a blast knocks people off their feet.',
}


def SFX(tr, G):
    tr.wind([(0, 1.0), (G('s02', 0), 0.8), (G('s03', 0), 0.6), (G('s07', 0), 0.55),
             (G('s08', 0), 0.5), (G('s10', 0), 0.8), (G('s10', 6.5), 0.8), (G('s10', 7.0), 0.0)])
    tr.whoosh(G('s01', 0.4), G('s01', 3.35), 0.28)
    tr.boom(G('s01', 3.35), 0.95)
    tr.rumble(G('s01', 3.4), G('s01', 8.5), 0.25)
    tr.whoosh(G('s02', 3.9), G('s02', 5.7), 0.22)
    tr.boom(G('s03', 0.1), 0.8)
    tr.rumble(G('s03', 0.2), G('s04', 0.1), 0.25)
    tr.rumble(G('s04', 0.1), G('s04', 4.0), 0.18)
    tr.snaps(G('s04', 0.4), G('s04', 3.4), 70)
    tr.gurgle(G('s08', 0.8), G('s08', 4.4))
    tr.whoosh(G('s09', 0.3), G('s09', 2.0), 0.25)
    tr.boom(G('s09', 2.0), 0.85)
    tr.rumble(G('s09', 2.1), G('s09', 6.0), 0.22)
    tr.whoosh(G('s10', 0.4), G('s10', 4.2), 0.08, 400, 1500)

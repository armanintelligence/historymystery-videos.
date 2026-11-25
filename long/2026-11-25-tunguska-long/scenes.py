"""Long video: The Tunguska Event, full story (1920x1080). Build with HM_FORMAT=long.
Visuals: skies, forest (plants), maps, diagrams, globe. No living beings."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

assert W == 1920, 'build with HM_FORMAT=long'
RED = (255, 90, 70)
F_TITLE = font('InterDisplay-Black.otf', 140)
VB = 830
CHEKO = (101.86, 60.96)


def new(bg=BG):
    img = Image.new('RGB', (W, H), bg)
    return img, ImageDraw.Draw(img, 'RGBA')


def A(c, a):
    return c + (int(255 * max(0, min(1, a))),)


def sky(d, top=(4, 6, 13), bot=(14, 24, 51), ymax=H):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=tuple(int(lerp(a, b, k)) for a, b in zip(top, bot)))


def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0, int(170 * a)))


rngF = np.random.default_rng(1)
FOREST = [(x + rngF.uniform(-6, 6), rngF.uniform(50, 110)) for x in range(-20, W + 40, 26)]


def treeline(d, gy, col=(3, 5, 9)):
    d.rectangle([0, gy, W, H], fill=col)
    for x, h in FOREST:
        conifer(d, x, gy + 4, h, col)


def fireball(arr, a, b, e, n=28, r=26):
    for j in range(n):
        q = max(e - j * 0.018, 0)
        glow(arr, lerp(a[0], b[0], q), lerp(a[1], b[1], q), r - j * 0.7, (255, 140, 50), 0.5 * (1 - j / n))
    hx, hy = lerp(a[0], b[0], e), lerp(a[1], b[1], e)
    glow(arr, hx, hy, 60, (255, 170, 80), 0.9)
    glow(arr, hx, hy, 20, (255, 255, 230), 1.6)


def pin(d, x, y, t0, t, label=None, sub=None):
    a = ramp(t, t0, t0 + 0.3)
    if a <= 0:
        return
    pr = 30 + 40 * ((t - t0) % 1.2) / 1.2
    d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=A(AMBER, 0.8 * (1 - ((t - t0) % 1.2) / 1.2)), width=4)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=A(AMBER, a))
    if label:
        d.text((x + 30, y - 30), label, font=F_LABEL, fill=A(WHITE, a), anchor='ls')
    if sub:
        d.text((x + 30, y + 14), sub, font=F_SMALL, fill=A(GREY, a), anchor='lt')


# ---------- 1. cold open ----------
FA, FBp = (1880, 120), (760, 700)

def c01(t):
    img, d = new()
    sky(d, ymax=VB)
    draw_stars(d, t, ymax=VB)
    treeline(d, VB - 60)
    arr = to_arr(img)
    if 0.5 <= t < 4.0:
        fireball(arr, FA, FBp, ramp(t, 0.5, 4.0) ** 1.5)
    if t >= 4.0:
        arr += 255 * math.exp(-(t - 4.0) * 2.2)
        glow(arr, FBp[0], VB - 60, 520, (255, 120, 40), 0.9 * math.exp(-(t - 4.0) * 0.4))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 6.0, 6.5) * (1 - ramp(t, 11.5, 12))
    text_c(d, (W / 2, 300), '30 JUNE 1908', F_HUGE, A(WHITE, a))
    a2 = ramp(t, 12.0, 12.4)
    if a2 > 0:
        d.rounded_rectangle([660, 240, 1260, 370], radius=18, outline=A(RED, a2), width=6)
        text_c(d, (W / 2, 305), 'NO CRATER', F_HUGE, A(RED, a2))
    top_label(img, 'SIBERIA · 1908', ramp(t, 0.2, 0.6))
    return img

CAP01 = [(0, 6, 'On the morning of June 30th, 1908, something exploded above the forests of Siberia.', ['June', '30th,', '1908,', 'Siberia.']),
         (6, 11, 'It flattened tens of millions of trees… and left no crater.', ['millions', 'no', 'crater.']),
         (11, 16, 'More than a century later, no one has found a single piece of the thing that did it.', ['single', 'piece'])]

# ---------- 2. title ----------
def c02(t):
    img, d = new()
    draw_stars(d, t, 0.8)
    text_c(d, (W / 2, 380), 'THE TUNGUSKA EVENT', F_TITLE, A(WHITE, ramp(t, 0.2, 0.9)))
    text_c(d, (W / 2, 510), 'the biggest impact in recorded history, and no crater', F_MED, A(AMBER, ramp(t, 0.8, 1.4)))
    return img

CAP02 = [(0, 3, 'This is the story of the Tunguska event, and what scientists now think happened.', ['Tunguska', 'event,']),
         (3, 5.5, "We'll follow the clues from the forest floor to the edge of space.", ['clues'])]

# ---------- 3. map zoom ----------
def c03(t):
    k = ease(ramp(t, 0.0, 4.5))
    cam = Cam(lerp(75, SITE[0], k), lerp(52, SITE[1], k), math.exp(lerp(math.log(6), math.log(45), k)))
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    d = ImageDraw.Draw(img, 'RGBA')
    x, y = cam.xy(*SITE)
    pin(d, x, y, 4.0, t, 'TUNGUSKA', 'Podkamennaya Tunguska River')
    if t > 7.5:
        arr = to_arr(img)
        fireball(arr, (x + 900, y - 350), (x, y), ramp(t, 7.5, 10.5) ** 1.4, 22, 18)
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 11, 11.4)
    if a > 0:
        r = 800 / 111 * cam.s  # ~800 km visibility radius
        d.ellipse([x - r, y - r, x + r, y + r], outline=A(CYAN, a), width=4)
        d.text((x + r * 0.75, y + r * 0.75), 'seen from ~800 km away', font=F_LABEL, fill=A(CYAN, a), anchor='lt')
    top_label(img, 'CHAPTER 1 · THE MORNING')
    return img

CAP03 = [(0, 5, 'It happened near the Podkamennaya Tunguska River, in one of the remotest corners of Siberia.', ['Podkamennaya', 'Tunguska']),
         (5, 10.5, 'A little after seven in the morning, a fireball streaked across the sky.', ['seven', 'fireball']),
         (10.5, 14, 'The flash was visible from about eight hundred kilometres away.', ['eight', 'hundred'])]

# ---------- 4. blast ----------
def c04(t):
    cam = Cam(SITE[0], SITE[1], 45 * (1 + 0.03 * t))
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    x, y = cam.xy(*SITE)
    arr = to_arr(img)
    f = math.exp(-max(t - 0.1, 0) * 1.5)
    glow(arr, x, y, 300, (255, 130, 40), 1.4 * f)
    glow(arr, x, y, 90, (255, 240, 200), 2.0 * f)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    for i in range(6):
        tt = (t - 0.1 - i * 0.8)
        if tt > 0:
            r = 40 + tt * 260
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 170, 90, int(230 * max(0, 1 - tt / 4))), width=8)
    a = ramp(t, 6.5, 7.0)
    if a > 0:
        card(d, 360, 130, 1560, 260, a)
        text_c(d, (W / 2, 195), '“as if my shirt was on fire”', F_MED, A(AMBER, a))
    top_label(img, 'THE BLAST')
    return img

CAP04 = [(0, 3, 'Then came the blast.', ['blast.']),
         (3, 6.5, 'Hot winds strong enough to throw people down, and shake buildings like an earthquake.', ['Hot', 'winds', 'earthquake.']),
         (6.5, 10, 'One eyewitness said the heat felt as if their shirt was on fire.', ['shirt', 'fire.'])]

# ---------- 5. recorded far away ----------
def c05(t):
    cam = Cam(55, 57, 9)
    img = draw_map(Image.new('RGB', (W, H)), cam)
    d = ImageDraw.Draw(img, 'RGBA')
    sx, sy = cam.xy(*SITE)
    for i in range(6):
        tt = t - i * 0.9
        if tt > 0:
            r = tt * 300
            d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=A(AMBER, 0.6 * max(0, 1 - r / 2200)), width=4)
    d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=AMBER)
    # seismograph trace box
    a = ramp(t, 2.5, 3.0)
    card(d, 200, 560, 900, 780, a)
    d.text((230, 590), 'SEISMOGRAPH · WESTERN EUROPE', font=F_SMALL, fill=A(GREY, a), anchor='lt')
    xs = np.arange(230, 870, 3)
    k = ramp(t, 3.0, 6.0)
    pts = []
    for i, x in enumerate(xs):
        q = i / len(xs)
        if q > k:
            break
        amp = 60 * math.exp(-((q - 0.45) / 0.08) ** 2) * math.sin(q * 140)
        pts.append((x, 700 + amp + np.random.default_rng(i).uniform(-3, 3)))
    if len(pts) > 1:
        d.line(pts, fill=A(CYAN, a), width=3)
    a2 = ramp(t, 7.5, 8.0)
    if a2 > 0:
        card(d, 1060, 560, 1760, 780, a2)
        text_c(d, (1410, 620), 'NEWSPAPER GUESSES:', F_SMALL, A(GREY, a2))
        text_c(d, (1410, 690), 'volcano? mining accident?', F_MED, A(WHITE, a2))
    top_label(img, 'FELT ACROSS A CONTINENT')
    return img

CAP05 = [(0, 2.5, 'Seismographs as far away as western Europe recorded the shock waves.', ['western', 'Europe']),
         (2.5, 4, 'Instruments in Russia, hundreds of kilometres away, felt the tremors too.', ['tremors']),
         (4, 6, 'Pressure waves in the air were detected around the world.', ['around', 'world.']),
         (6, 8, 'Newspapers guessed at a volcanic eruption, or a mining accident.', ['volcanic', 'mining'])]

# ---------- 6. bright nights ----------
ARMAGH = (-6.65, 54.35)

def c06(t):
    cam = Cam(20, 55, 14)
    img = draw_map(Image.new('RGB', (W, H)), cam, land=(30, 38, 54), coast=(70, 86, 112), water=(6, 10, 18))
    arr = to_arr(img)
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.clip(1 - yy / 700, 0, 1) ** 1.5 * 70 * (0.85 + 0.15 * math.sin(t * 2)) * ramp(t, 0, 1.2)
    arr += band[..., None] * np.array([0.8, 0.9, 1.0], np.float32)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    x, y = cam.xy(*ARMAGH)
    pin(d, x, y, 3.0, t, 'Armagh Observatory', 'Northern Ireland')
    a = ease(ramp(t, 4.5, 5.2))
    if a > 0:
        ox, y0 = lerp(2200, 1400, a), 420
        d.rounded_rectangle([ox - 230, y0, ox + 230, y0 + 300], radius=10, fill=A((236, 230, 214), a))
        d.text((ox, y0 + 40), 'NEWS', font=F_MED, fill=(30, 30, 30, int(255 * a)), anchor='mm')
        for i in range(6):
            w_ = 380 if i % 3 else 300
            d.rectangle([ox - 190, y0 + 90 + i * 30, ox - 190 + w_, y0 + 104 + i * 30], fill=(120, 115, 105, int(255 * a)))
        d.rounded_rectangle([ox + 70, y0 - 50, ox + 260, y0 + 20], radius=14, fill=(10, 14, 24, int(240 * a)))
        d.text((ox + 165, y0 - 15), 'NIGHT', font=F_LABEL, fill=A(AMBER, a), anchor='mm')
    top_label(img, 'THE NIGHTS AFTER')
    return img

CAP06 = [(0, 4.5, 'For nights afterwards, skies over Siberia and Europe glowed strangely bright.', ['glowed', 'bright.']),
         (4.5, 7.5, 'At Armagh Observatory in Northern Ireland, the glow was bright enough to read a newspaper by.', ['Armagh', 'newspaper']),
         (7.5, 9, 'In London, the Royal Observatory at Greenwich photographed the glowing night sky.', ['Greenwich'])]

# ---------- 7. flattened forest ----------
rng7 = np.random.default_rng(7)
TREES = []
while len(TREES) < 2600:
    px, py = rng7.uniform(-360, 360, 2)
    if px * px / 1.4 + py * py < 360 * 360:
        TREES.append((px * 1.18, py, rng7.uniform(0.75, 1.25), rng7.uniform(-0.25, 0.25)))
TC = (960, 470)

def c07(t):
    img, d = new()
    d.ellipse([TC[0] - 470, TC[1] - 380, TC[0] + 470, TC[1] + 380], fill=(24, 32, 22))
    wave = lerp(0, 520, ease(ramp(t, 0.5, 4.0)))
    for px, py, sc, jit in TREES:
        dist = math.hypot(px, py)
        x, y = TC[0] + px, TC[1] + py
        if 45 < dist < wave:
            ang = math.atan2(py, px) + jit * 0.3
            L = 26 * sc
            d.line([x, y, x + L * math.cos(ang), y + L * math.sin(ang)], fill=(150, 112, 74), width=4)
        elif dist <= 45 and wave > 45:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 100, 80))
        else:
            r = 7 * sc
            d.ellipse([x - r, y - r, x + r, y + r], fill=(30, int(80 + 30 * jit * 4), 48))
    d.ellipse([TC[0] - 10, TC[1] - 10, TC[0] + 10, TC[1] + 10], fill=AMBER)
    n = int(80_000_000 * ease(ramp(t, 0.5, 4.0)))
    card(d, 1440, 330, 1860, 560, 1)
    text_c(d, (1650, 410), f'{n / 1e6:.0f} million', F_MED, WHITE)
    text_c(d, (1650, 480), 'trees flattened', F_LABEL, GREY)
    text_c(d, (1650, 525), '≈2,000 km²', F_LABEL, AMBER)
    top_label(img, 'CHAPTER 2 · THE FOREST')
    return img

CAP07 = [(0, 4, 'The forest took the worst of it. About two thousand square kilometres were flattened…', ['two', 'thousand']),
         (4, 8, '…some eighty million trees, all pointing away from one spot.', ['eighty', 'million', 'away'])]

# ---------- 8. London ----------
def c08(t):
    img, d = new()
    k = ease(ramp(t, 0.1, 1.0)); k2 = ease(ramp(t, 0.9, 1.9))
    rb = 330 * k
    rl = 330 * math.sqrt(1570 / 2000) * k2
    cx, cy = 960, 480
    if rb > 0:
        d.ellipse([cx - rb, cy - rb, cx + rb, cy + rb], fill=(255, 140, 50, 70), outline=AMBER, width=6)
    if rl > 0:
        d.ellipse([cx - rl, cy - rl, cx + rl, cy + rl], outline=CYAN, width=6)
    a = ramp(t, 1.9, 2.3)
    text_c(d, (cx, cy - 30), 'GREATER LONDON', F_LABEL, A(CYAN, a))
    text_c(d, (cx, cy + 20), '≈1,570 km²', F_LABEL, A(CYAN, a))
    text_c(d, (cx + 560, cy), 'BLAST ZONE', F_LABEL, A(AMBER, ramp(t, 1.0, 1.4)))
    text_c(d, (cx + 560, cy + 50), '≈2,000 km²', F_LABEL, A(AMBER, ramp(t, 1.0, 1.4)))
    top_label(img, 'TO SCALE')
    return img

CAP08 = [(0, 2.2, "That's an area bigger than the whole of Greater London.", ['bigger', 'London.']),
         (2.2, 3.5, 'Luckily, it struck an almost empty forest.', ['empty', 'forest.'])]

# ---------- 9. butterfly ----------
def butterfly(d, cx, cy, s, a):
    pts = []
    for i in range(361):
        th = math.radians(i)
        r = s * (1 + 0.45 * math.cos(2 * th) - 0.2 * math.cos(4 * th))
        pts.append((cx + r * math.cos(th) * 1.25, cy + r * math.sin(th) * 0.8))
    d.polygon(pts, fill=A((80, 60, 40), 0.7 * a), outline=A(AMBER, a))

def c09(t):
    cam = Cam(SITE[0], SITE[1], 900)
    img, d = new()
    for i in range(0, H, 40):
        d.line([0, i, W, i], fill=(16, 22, 34), width=1)
    for i in range(0, W, 40):
        d.line([i, 0, i, H], fill=(16, 22, 34), width=1)
    k = ease(ramp(t, 0.3, 2.5))
    butterfly(d, 960, 470, 260 * k + 1, k)
    rng = np.random.default_rng(9)
    for _ in range(500):
        th = rng.uniform(0, 6.283)
        r = rng.uniform(40, 300) * k
        x, y = 960 + r * math.cos(th) * 1.25, 470 + r * math.sin(th) * 0.8
        d.line([x, y, x + 12 * math.cos(th), y + 12 * math.sin(th)], fill=A((170, 130, 90), k), width=2)
    d.ellipse([950, 460, 970, 480], fill=AMBER)
    top_label(img, 'THE BUTTERFLY')
    return img

CAP09 = [(0, 4, 'Mapped from above, the fallen trees form a strange butterfly shape.', ['butterfly'])]

# ---------- 10. telegraph-pole trees ----------
def c10(t):
    img, d = new()
    sky(d, (10, 16, 28), (40, 52, 70), VB - 120)
    gy = VB - 120
    d.rectangle([0, gy, W, H], fill=(34, 30, 24))
    rng = np.random.default_rng(10)
    k = ramp(t, 0.3, 3.0)
    for i, x in enumerate(range(140, 1800, 95)):
        h = rng.uniform(320, 470)
        d.rectangle([x - 7, gy - h, x + 7, gy], fill=(70, 58, 46))
        if k < 1:
            for j in range(6):
                yb = gy - h + 40 + j * 50
                L = 60 * (1 - k)
                d.line([x, yb, x - L, yb + 30], fill=(40, 70, 44), width=6)
                d.line([x, yb, x + L, yb + 30], fill=(40, 70, 44), width=6)
    for x in range(0, W, 160):
        d.line([x, gy + 20, x + 120, gy + 30], fill=(80, 64, 50), width=8)
    text_c(d, (W / 2, 160), "'TELEGRAPH POLE' FOREST", F_MED, A(AMBER, ramp(t, 3.0, 3.5)))
    top_label(img, 'AT THE CENTRE')
    return img

CAP10 = [(0, 4, 'But at the very centre, the trees were still standing, stripped of branches and bark, like telegraph poles.', ['still', 'standing,', 'telegraph', 'poles.']),
         (4, 6.5, 'And more than a hundred square kilometres of forest were scorched by the heat.', ['scorched'])]

# ---------- 11. Kulik ----------
def c11(t):
    cam = Cam(102.0, 60.4, 260)
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    d = ImageDraw.Draw(img, 'RGBA')
    pts = [cam.xy(102.6, 59.6), cam.xy(*VANAVARA), cam.xy(*SITE)]
    k = ramp(t, 4.5, 9.0)
    segl = [math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])]
    drawn = sum(segl) * k; acc = 0
    for i in range(2):
        a_, b_ = pts[i], pts[i + 1]; L = segl[i]
        upto = min(max(drawn - acc, 0), L)
        for j in range(int(upto // 22)):
            q0, q1 = j * 22 / L, (j * 22 + 12) / L
            d.line([lerp(a_[0], b_[0], q0), lerp(a_[1], b_[1], q0), lerp(a_[0], b_[0], q1), lerp(a_[1], b_[1], q1)], fill=CYAN, width=6)
        acc += L
    a = ramp(t, 6.0, 6.3)
    p = pts[1]
    d.ellipse([p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10], fill=A(CYAN, a))
    d.text((p[0] + 22, p[1]), 'Vanavara trading post', font=F_SMALL, fill=A(WHITE, a), anchor='lm')
    ab = 1 - ramp(t, 3.5, 4.0)
    a19 = ramp(t, 0.3, 0.6) * ab
    card(d, 610, 220, 1310, 460, a19)
    text_c(d, (W / 2, 300), '1921', F_HUGE, A(WHITE, a19))
    text_c(d, (W / 2, 400), 'could not reach the site', F_LABEL, A(RED, a19))
    a27 = ramp(t, 4.0, 4.4) * (1 - ramp(t, 8.5, 9.0))
    text_c(d, (W / 2, 220), '1927', F_BIG, A(WHITE, 0.92 * a27))
    top_label(img, 'CHAPTER 3 · THE SEARCH')
    return img

CAP11 = [(0, 4, 'The site was so remote that the first expedition, in 1921, could not even reach it.', ['1921,', 'remote']),
         (4, 7, 'In 1927, scientist Leonid Kulik, sent by the Soviet Academy of Sciences, finally made it.', ['1927,', 'Leonid', 'Kulik,']),
         (7, 9, 'Nineteen years after the blast, a scientist was finally standing in the flattened forest.', ['Nineteen', 'years'])]

# ---------- 12. bog, no crater ----------
def c12(t):
    cam = Cam(SITE[0], SITE[1], 3000)
    img, d = new((18, 26, 20))
    rng = np.random.default_rng(12)
    for _ in range(400):
        x, y = rng.uniform(0, W), rng.uniform(100, VB)
        d.line([x, y, x + rng.uniform(-30, 30), y + rng.uniform(-8, 8)], fill=(90, 72, 54), width=3)
    k = ease(ramp(t, 0.5, 2.0))
    d.ellipse([960 - 330 * k, 470 - 170 * k, 960 + 330 * k, 470 + 170 * k], fill=(36, 70, 80))
    a = ramp(t, 1.5, 2.0)
    text_c(d, (960, 470), 'MARSHY BOG', F_LABEL, A(WHITE, a))
    a2 = ramp(t, 4.5, 4.9)
    if a2 > 0:
        c = A(RED, a2)
        d.line([1460, 230, 1620, 390], fill=c, width=12); d.line([1460, 390, 1620, 230], fill=c, width=12)
        d.text((1540, 430), 'NO CRATER', font=F_MED, fill=c, anchor='mt')
        d.line([300, 230, 460, 390], fill=c, width=12); d.line([300, 390, 460, 230], fill=c, width=12)
        d.text((380, 430), 'NO METEORITE', font=F_MED, fill=c, anchor='mt')
    top_label(img, 'THE EPICENTRE')
    return img

CAP12 = [(0, 4, 'He found the flattened forest, and a marshy bog at its centre.', ['marshy', 'bog']),
         (4, 5, 'But no crater, and no meteorite.', ['no', 'crater,', 'meteorite.']),
         (5, 5.5, 'Photographs from his 1929 expedition show the fallen trunks, all pointing the same way.', ['1929', 'same', 'way.']),
         (5.5, 6.5, 'He kept returning on expeditions until 1930, mapping the fallen trees. The rock itself was never found.', ['1930,', 'never', 'found.'])]

# ---------- 13. airburst ----------
GY = 760
KM = 50
BURST = (1100, GY - 8 * KM)
FOREST13 = [(x, np.random.default_rng(x).uniform(50, 90)) for x in range(320, 1880, 28)]

def c13(t):
    img, d = new()
    for i in range(0, GY, 8):
        k = i / GY
        d.rectangle([0, i, W, i + 8], fill=(int(8 + 14 * k), int(14 + 26 * k), int(28 + 40 * k)))
    d.rectangle([300, GY - 10 * KM, W, GY - 5 * KM], fill=(255, 150, 60, 28))
    d.rectangle([0, GY, W, H], fill=(16, 20, 14))
    d.line([300, GY, 300, GY - 12 * KM], fill=GREY, width=3)
    for km in (0, 5, 10):
        yk = GY - km * KM
        d.line([290, yk, 310, yk], fill=GREY, width=3)
        d.text((275, yk), f'{km} km', font=F_SMALL, fill=GREY, anchor='rm')
    d.text((W - 40, GY - 7.5 * KM), '5–10 km up', font=F_LABEL, fill=AMBER, anchor='rm')
    shock_r = max(t - 4.0, 0) * 380
    for x, h in FOREST13:
        dx = x - BURST[0]
        dist = math.hypot(dx, GY - BURST[1])
        tilt = 0.0
        if shock_r > dist and abs(dx) > 60:
            tilt = (1.35 if dx > 0 else -1.35) * min((shock_r - dist) / 120, 1)
        conifer(d, x, GY, h, (34, 62, 40), tilt)
    arr = to_arr(img)
    A0 = (1900, 60)
    if 0.5 <= t < 4.0:
        fireball(arr, A0, BURST, ramp(t, 0.5, 4.0) ** 1.3, 24, 20)
    if t >= 4.0:
        f = math.exp(-(t - 4.0) * 1.2)
        glow(arr, BURST[0], BURST[1], 260, (255, 140, 50), 2.4 * f)
        glow(arr, BURST[0], BURST[1], 90, (255, 250, 220), 3.0 * f)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    if t >= 4.0 and shock_r < 1600:
        d.ellipse([BURST[0] - shock_r, BURST[1] - shock_r, BURST[0] + shock_r, BURST[1] + shock_r], outline=(255, 190, 120, int(220 * max(0, 1 - shock_r / 1600))), width=6)
    a = ramp(t, 1.0, 1.4) * (1 - ramp(t, 3.8, 4.0))
    d.text((1500, 120), '≈55,000 km/h', font=F_LABEL, fill=A(WHITE, a), anchor='mm')
    top_label(img, 'CHAPTER 4 · AN EXPLOSION IN THE SKY')
    return img

CAP13 = [(0, 5, 'Today, most scientists think it was a stony space rock, perhaps fifty to a hundred metres across.', ['fifty', 'hundred', 'metres']),
         (5, 9, 'It hit the atmosphere at around fifty-five thousand kilometres an hour…', ['fifty-five', 'thousand']),
         (9, 13, '…and exploded in the air, about five to ten kilometres up, before it ever reached the ground.', ['five', 'ten', 'kilometres', 'up,']),
         (13, 14.5, 'The rock itself was most likely vaporised. That is why there is no crater.', ['vaporised.', 'no', 'crater.']),
         (14.5, 16, 'In 2019, NASA researchers recreated the blast using computer models and 1908 pressure records.', ['2019,', 'recreated'])]

# ---------- 14. energy ----------
def c14(t):
    img, d = new()
    k = ease(ramp(t, 0.3, 2.0))
    text_c(d, (W / 2, 260), f'{lerp(0, 10, k):.0f}–{lerp(0, 15, k):.0f}', F_BIG, WHITE)
    text_c(d, (W / 2, 420), 'MEGATONS OF TNT', F_MED, AMBER)
    a = ramp(t, 5.0, 5.5)
    if a > 0:
        n = int(lerp(0, 200, ramp(t, 5.0, 8.0)))
        for i in range(n):
            x = 260 + (i % 50) * 28; y = 560 + (i // 50) * 30
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=A(CYAN, a))
        d.text((260, 700), '≈ 185 to 1,000 × the Hiroshima bomb (estimates vary)', font=F_LABEL, fill=A(WHITE, a), anchor='lt')
    top_label(img, 'HOW BIG?')
    return img

CAP14 = [(0, 5, 'The energy released was around ten to fifteen megatons of TNT.', ['ten', 'fifteen', 'megatons']),
         (5, 7.5, 'Depending on the estimate, that is somewhere between about two hundred…', ['two', 'hundred…']),
         (7.5, 10, '…and a thousand times the bomb dropped on Hiroshima.', ['thousand', 'times'])]

# ---------- 15. asteroid or comet ----------
def c15(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    arr = to_arr(img)
    glow(arr, 1380, 400, 18, (240, 250, 255), 1.4)
    for j in range(30):
        glow(arr, 1380 + j * 16, 400 - j * 6, 26 - j * 0.6, (160, 210, 255), 0.4 * (1 - j / 30))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    rng = np.random.default_rng(15)
    pts = [(540 + (110 + rng.uniform(-18, 18)) * math.cos(a_), 400 + (90 + rng.uniform(-15, 15)) * math.sin(a_)) for a_ in np.linspace(0, 6.283, 18)]
    d.polygon(pts, fill=(110, 100, 90))
    for _ in range(6):
        cx, cy = 540 + rng.uniform(-60, 60), 400 + rng.uniform(-50, 50)
        d.ellipse([cx - 12, cy - 9, cx + 12, cy + 9], fill=(80, 72, 66))
    d.text((540, 560), 'STONY ASTEROID', font=F_LABEL, fill=WHITE, anchor='mt')
    d.text((540, 605), 'favoured by most', font=F_SMALL, fill=AMBER, anchor='mt')
    d.text((1380, 560), 'COMET', font=F_LABEL, fill=WHITE, anchor='mt')
    d.text((1380, 605), 'ice and dust', font=F_SMALL, fill=GREY, anchor='mt')
    text_c(d, (W / 2, 400), 'or', F_MED, GREY)
    a = ramp(t, 10.0, 10.4)
    if a > 0:
        card(d, 360, 660, 1560, 800, a)
        text_c(d, (W / 2, 730), '2020 idea: an iron asteroid that skimmed the air and flew on', F_LABEL, A(CYAN, a))
    top_label(img, 'CHAPTER 5 · ASTEROID OR COMET?')
    return img

CAP15 = [(0, 3.5, 'But what kind of space rock? Most scientists favour a stony asteroid.', ['stony', 'asteroid.']),
         (3.5, 7, 'Others argue for a comet, pointing to the strange glowing clouds seen after the blast.', ['comet,', 'glowing']),
         (7, 10, 'It also struck at the peak of the Beta Taurid meteor shower, linked to Comet Encke.', ['Beta', 'Taurid', 'Encke.']),
         (10, 12, 'And in 2020, one study suggested an iron asteroid…', ['iron', 'asteroid…']),
         (12, 14, '…that skimmed the atmosphere and flew back into space.', ['skimmed'])]

# ---------- 16. Lake Cheko ----------
def c16(t):
    cam = Cam(101.92, 60.93, 9000)
    img, d = new((24, 34, 26))
    x, y = cam.xy(*CHEKO)
    sx, sy = cam.xy(*SITE)
    rng = np.random.default_rng(16)
    for _ in range(300):
        px, py = rng.uniform(0, W), rng.uniform(90, VB)
        conifer(d, px, py, rng.uniform(16, 30), (34, 62, 40))
    k = ease(ramp(t, 0.5, 1.5))
    d.ellipse([x - 140 * k, y - 90 * k, x + 140 * k, y + 90 * k], fill=(30, 70, 100), outline=CYAN, width=3)
    d.text((x, y + 110), 'LAKE CHEKO · ~500 m wide', font=F_LABEL, fill=A(WHITE, k), anchor='mt')
    pin(d, sx, sy, 1.0, t, 'EPICENTRE')
    a = ramp(t, 2.0, 2.4)
    d.line([x, y, sx, sy], fill=A(GREY, a), width=3)
    d.text(((x + sx) / 2, (y + sy) / 2 - 16), '~8 km', font=F_LABEL, fill=A(AMBER, a), anchor='ms')
    a2 = ramp(t, 8.0, 8.4)
    if a2 > 0:
        card(d, 1100, 300, 1860, 440, a2)
        text_c(d, (1480, 370), 'CRATER? STILL DISPUTED', F_MED, A(RED, a2))
    top_label(img, 'A HIDDEN CRATER?')
    return img

CAP16 = [(0, 2.5, 'In 2007, Italian scientists led by Luca Gasperini made a bold claim.', ['Luca', 'Gasperini']),
         (2.5, 4.5, 'They proposed that Lake Cheko, about eight kilometres away…', ['Cheko,']),
         (4.5, 8, '…was a crater made by a fragment that survived the blast.', ['crater', 'fragment']),
         (8, 12, "Other teams disagree. One study found the lake's sediments are much older than 1908.", ['disagree.', 'older'])]

# ---------- 17. how often ----------
GC, GR = (960, 470), 300

def ortho(lon, lat, lon0, lat0):
    lo, la = np.radians(lon), np.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    x = np.cos(la) * np.sin(lo - l0)
    y = math.cos(p0) * np.sin(la) - math.sin(p0) * np.cos(la) * np.cos(lo - l0)
    z = math.sin(p0) * np.sin(la) + math.cos(p0) * np.cos(la) * np.cos(lo - l0)
    n = np.hypot(x, y) + 1e-9
    x = np.where(z < 0, x / n, x); y = np.where(z < 0, y / n, y)
    return GC[0] + x * GR, GC[1] - y * GR, z

def globe(img, t, lon_start=60):
    d = ImageDraw.Draw(img)
    arr = to_arr(img)
    glow(arr, GC[0], GC[1], GR * 1.05, (60, 120, 220), 0.45)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([GC[0] - GR, GC[1] - GR, GC[0] + GR, GC[1] + GR], fill=(14, 40, 78))
    for p in GEO['l']['land']:
        x, y, z = ortho(p[:, 0], p[:, 1], lon_start + t * 6, 35)
        if (z > 0).any() and len(p) > 2:
            d.polygon(list(zip(x.tolist(), y.tolist())), fill=(46, 84, 62))
    return img, d

def c17(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    img, d = globe(img, t)
    a = ramp(t, 0.8, 1.2)
    for i, (s, x) in enumerate((('once a century?', 360), ('every few hundred years?', 960), ('once in millennia?', 1560))):
        aa = ramp(t, 0.8 + i * 0.8, 1.2 + i * 0.8)
        card(d, x - 260, 80, x + 260, 160, aa)
        text_c(d, (x, 120), s, F_LABEL, A(AMBER, aa))
    top_label(img, 'CHAPTER 6 · COULD IT HAPPEN AGAIN?', 1 - ramp(t, 0.5, 0.8))
    return img

CAP17 = [(0, 2, 'How often does something like this happen?', ['How', 'often']),
         (2, 4.5, 'Estimates range from once a century to once every few thousand years.', ['once', 'century', 'thousand']),
         (4.5, 6.5, 'Smaller airbursts, like the one over Chelyabinsk in 2013, come every ten to a hundred years.', ['Chelyabinsk', 'ten', 'hundred']),
         (6.5, 7.5, 'A Tunguska-sized blast could devastate a whole region.', ['devastate']),
         (7.5, 9, 'So in 2016, NASA set up a Planetary Defense office.', ['Planetary', 'Defense'])]

# ---------- 18. DART ----------
def c18(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    cx, cy = 900, 470
    d.ellipse([cx - 160, cy - 150, cx + 160, cy + 150], fill=(110, 100, 90))
    ang = 0.6 * t
    mx, my = cx + 360 * math.cos(ang), cy + 150 * math.sin(ang)
    d.ellipse([cx - 360, cy - 150, cx + 360, cy + 150], outline=(60, 70, 90), width=2)
    d.ellipse([mx - 40, my - 36, mx + 40, my + 36], fill=(130, 118, 104))
    d.text((cx, cy + 190), 'DIDYMOS', font=F_SMALL, fill=GREY, anchor='mt')
    d.text((mx, my - 50), 'DIMORPHOS', font=F_SMALL, fill=GREY, anchor='ms')
    k = ramp(t, 1.0, 4.0)
    if k < 1:
        sx, sy = lerp(1900, mx, k), lerp(100, my, k)
        d.rectangle([sx - 14, sy - 10, sx + 14, sy + 10], fill=(220, 220, 230))
        d.line([sx - 40, sy, sx + 40, sy], fill=CYAN, width=4)
    elif t < 5.5:
        arr = to_arr(img); glow(arr, mx, my, 80, (255, 200, 120), 1.5 * math.exp(-(t - 4.0) * 2)); img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 5.5, 6.0)
    if a > 0:
        card(d, 1300, 330, 1840, 560, a)
        text_c(d, (1570, 400), '−33 min', F_HUGE, A(AMBER, a))
        text_c(d, (1570, 510), 'orbit changed', F_LABEL, A(WHITE, a))
    top_label(img, 'NASA DART · 2022')
    return img

CAP18 = [(0, 5.5, "In 2022, NASA's DART spacecraft crashed into a small asteroid called Dimorphos, on purpose.", ['DART', 'Dimorphos,', 'purpose.']),
         (5.5, 9, 'It changed the asteroid’s orbit by thirty-three minutes: proof that we can nudge a space rock.', ['thirty-three', 'minutes:'])]

# ---------- 19. Asteroid Day ----------
def c19(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    a = ramp(t, 0.3, 0.8)
    d.rounded_rectangle([760, 170, 1160, 600], radius=26, fill=A((236, 230, 214), a))
    d.rectangle([760, 170, 1160, 270], fill=A(RED, a))
    text_c(d, (960, 222), 'JUNE', F_MED, A(WHITE, a))
    text_c(d, (960, 440), '30', F_BIG, A((30, 30, 30), a))
    text_c(d, (960, 680), 'INTERNATIONAL ASTEROID DAY', F_MED, A(AMBER, ramp(t, 1.5, 2.0)))
    top_label(img, 'REMEMBERING TUNGUSKA')
    return img

CAP19 = [(0, 3, 'And since 2016, June 30th, the anniversary of Tunguska…', ['June', '30th,']),
         (3, 6, '…has been International Asteroid Day, proclaimed by the United Nations.', ['Asteroid', 'Day,'])]

# ---------- 20. ending ----------
def c20(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    img, d = globe(img, t, 70)
    a = ramp(t, 0.5, 1.0) * (1 - ramp(t, 9.0, 9.5))
    card(d, 460, 90, 1460, 220, a)
    text_c(d, (W / 2, 155), 'BIGGEST IMPACT IN RECORDED HISTORY', F_MED, A(AMBER, a))
    a3 = ramp(t, 9.5, 10.0)
    if a3 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(170 * a3)))
        text_c(d, (W / 2, 380), 'FOLLOW', F_HUGE, A(WHITE, a3))
        text_c(d, (W / 2, 500), 'for more unexplained history', F_MED, A(AMBER, a3))
    top_label(img, 'STILL A MYSTERY', 1 - a3)
    return img

CAP20 = [(0, 1, "So here's what we know: an object fifty to a hundred metres wide…", ['know:']),
          (1, 2, '…exploding five to ten kilometres up, with the force of ten to fifteen megatons.', ['megatons.']),
          (2, 4.5, "What we still don't know: was it rock or ice, and did any piece of it reach the ground?", ['rock', 'ice,', 'ground?']),
          (4.5, 6.5, 'A blast felt across a continent, a forest knocked flat, and no crater to show for it.', ['continent,', 'no', 'crater']),
         (6.5, 8, 'Whatever it was, its secrets are still somewhere in the Siberian forest.', ['secrets']),
          (8, 9.5, 'More than a century on, Tunguska is still the biggest impact in recorded history.', ['biggest', 'impact'])]

SCENES = [
    ('c01', c01, 16.0, CAP01), ('c02', c02, 5.5, CAP02), ('c03', c03, 14.0, CAP03), ('c04', c04, 10.0, CAP04),
    ('c05', c05, 8.5, CAP05), ('c06', c06, 9.0, CAP06), ('c07', c07, 8.0, CAP07), ('c08', c08, 3.5, CAP08),
    ('c09', c09, 4.0, CAP09), ('c10', c10, 6.5, CAP10), ('c11', c11, 9.5, CAP11), ('c12', c12, 6.5, CAP12),
    ('c13', c13, 16.0, CAP13), ('c14', c14, 10.0, CAP14), ('c15', c15, 14.0, CAP15), ('c16', c16, 12.0, CAP16),
    ('c17', c17, 9.0, CAP17), ('c18', c18, 9.0, CAP18), ('c19', c19, 6.0, CAP19), ('c20', c20, 13.0, CAP20),
]

SPOKEN = {
    'Photographs from his 1929 expedition show the fallen trunks, all pointing the same way.':
        'Photographs from his nineteen twenty-nine expedition show the fallen trunks, all pointing the same way.',
    'In 2019, NASA researchers recreated the blast using computer models and 1908 pressure records.':
        'In twenty nineteen, NASA researchers recreated the blast, using computer models and pressure records from nineteen-oh-eight.',
    'On the morning of June 30th, 1908, something exploded above the forests of Siberia.':
        'On the morning of June thirtieth, nineteen-oh-eight, something exploded above the forests of Siberia.',
    'The site was so remote that the first expedition, in 1921, could not even reach it.':
        'The site was so remote that the first expedition, in nineteen twenty-one, could not even reach it.',
    'In 1927, scientist Leonid Kulik, sent by the Soviet Academy of Sciences, finally made it.':
        'In nineteen twenty-seven, scientist Leonid Kulik, sent by the Soviet Academy of Sciences, finally made it.',
    'And in 2020, one study suggested an iron asteroid…': 'And in twenty twenty, one study suggested an iron asteroid,',
    '…that skimmed the atmosphere and flew back into space.': 'that skimmed the atmosphere, and flew back into space.',
    'He kept returning on expeditions until 1930, mapping the fallen trees. The rock itself was never found.':
        'He kept returning on expeditions until nineteen thirty, mapping the fallen trees. The rock itself was never found.',
    'Smaller airbursts, like the one over Chelyabinsk in 2013, come every ten to a hundred years.':
        'Smaller airbursts, like the one over Chelyabinsk in twenty thirteen, come every ten to a hundred years.',
    'So in 2016, NASA set up a Planetary Defense office.': 'So in twenty sixteen, NASA set up a Planetary Defense office.',
    'And since 2016, June 30th, the anniversary of Tunguska…': 'And since twenty sixteen, June thirtieth, the anniversary of Tunguska,',
    '…has been International Asteroid Day, proclaimed by the United Nations.': 'has been International Asteroid Day, proclaimed by the United Nations.',
    '…and a thousand times the bomb dropped on Hiroshima.': 'and a thousand times the bomb dropped on Hiroshima.',
    'In 2007, Italian scientists led by Luca Gasperini made a bold claim.': 'In two thousand and seven, Italian scientists led by Luca Gasperini made a bold claim.',
    'They proposed that Lake Cheko, about eight kilometres away…': 'They proposed that Lake Cheko, about eight kilometres away,',
    '…was a crater made by a fragment that survived the blast.': 'was a crater made by a fragment that survived the blast.',
    "Other teams disagree. One study found the lake's sediments are much older than 1908.":
        "Other teams disagree. One study found the lake's sediments are much older than nineteen-oh-eight.",
    "In 2022, NASA's DART spacecraft crashed into a small asteroid called Dimorphos, on purpose.":
        "In twenty twenty-two, NASA's DART spacecraft crashed into a small asteroid called Dimorphos, on purpose.",
    'It flattened tens of millions of trees… and left no crater.': 'It flattened tens of millions of trees... and left no crater.',
}


def SFX(tr, G):
    tr.wind([(0, 1.0), (G('c02', 0), 0.7), (G('c03', 0), 0.6), (G('c07', 0), 0.6), (G('c10', 0), 0.8),
             (G('c13', 0), 0.6), (G('c17', 0), 0.6), (G('c20', 0), 0.8), (G('c20', 12.5), 0.8), (G('c20', 13.0), 0.0)])
    tr.whoosh(G('c01', 0.5), G('c01', 4.0), 0.28)
    tr.boom(G('c01', 4.0), 0.95)
    tr.rumble(G('c01', 4.1), G('c01', 10.0), 0.25)
    tr.whoosh(G('c03', 7.5), G('c03', 10.5), 0.2)
    tr.boom(G('c04', 0.1), 0.8)
    tr.rumble(G('c04', 0.2), G('c04', 6.0), 0.25)
    tr.rumble(G('c05', 0.0), G('c05', 5.0), 0.15)
    tr.rumble(G('c07', 0.5), G('c07', 4.5), 0.18)
    tr.snaps(G('c07', 0.5), G('c07', 4.0), 80)
    tr.whoosh(G('c13', 0.5), G('c13', 4.0), 0.25)
    tr.boom(G('c13', 4.0), 0.85)
    tr.rumble(G('c13', 4.1), G('c13', 9.0), 0.22)
    tr.snaps(G('c13', 4.5), G('c13', 7.0), 40)
    tr.whoosh(G('c18', 1.0), G('c18', 4.0), 0.12, 400, 1500)
    tr.boom(G('c18', 4.0), 0.35, 2.0)

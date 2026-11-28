"""Long video: The Antikythera Mechanism, full story (1920x1080). Build with HM_FORMAT=long.
Visuals: sea, seabed, a boat hull, jars, coins, the bronze lump, gears, dials, X-ray scans, maps, timelines, text.
No people, animals, birds, statues or figures of any living being."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

assert W == 1920, 'build with HM_FORMAT=long'
VB = 830  # bottom of the visual area (captions sit below)
ISLAND = (23.30, 35.87)
SYRACUSE = (15.29, 37.08)
CORINTH = (22.93, 37.94)
ATHENS = (23.73, 37.98)
BRONZE = (78, 104, 86)
BRONZE_D = (52, 70, 60)
BRASS = (196, 150, 82)
WOOD = (92, 64, 40)
RED = (255, 90, 70)
F_TITLE = font('InterDisplay-Black.otf', 140)
F_TINY = font('Inter-SemiBold.otf', 24)
F_GLYPH = font('Inter-Bold.otf', 30)
GLYPHS = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'


def new(bg=BG):
    img = Image.new('RGB', (W, H), bg)
    return img, ImageDraw.Draw(img, 'RGBA')


def A(c, a):
    return tuple(c[:3]) + (int(255 * max(0, min(1, a))),)


def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0, int(170 * a)))


def gear_pts(cx, cy, r, teeth, ang=0.0, depth=None):
    depth = depth or max(5, r * 0.10)
    pts = []
    n = teeth * 4
    for i in range(n):
        a = ang + 2 * math.pi * i / n
        rr = r if (i % 4) in (1, 2) else r - depth
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def gear(d, cx, cy, r, teeth, ang=0.0, fill=None, outline=None, width=3, spokes=4, hub=None):
    d.polygon(gear_pts(cx, cy, r, teeth, ang), fill=fill, outline=outline, width=width)
    bg = hub if hub is not None else BG
    ri = r * 0.74
    col = fill if fill is not None else outline
    if spokes and r > 40:
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=bg, outline=outline, width=width)
        for k in range(spokes):
            a = ang + 2 * math.pi * k / spokes
            d.line([cx, cy, cx + ri * math.cos(a), cy + ri * math.sin(a)], fill=col, width=max(6, int(r * 0.09)))
    hr = max(5, r * 0.12)
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=col)


def blob(cx, cy, r, seed, n=40, rough=0.18, sx=1.25, sy=0.85):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 4)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rough * (0.5 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2])) + rng.uniform(-0.04, 0.04)
        pts.append((cx + r * sx * k * math.cos(a), cy + r * sy * k * math.sin(a)))
    return pts


def lump(d, cx, cy, r, seed=3, a=1.0):
    d.polygon(blob(cx, cy, r, seed), fill=A(BRONZE, a), outline=A(BRONZE_D, a))
    rng = np.random.default_rng(seed + 50)
    for k in range(10):
        px, py = cx + rng.uniform(-0.9, 0.9) * r, cy + rng.uniform(-0.5, 0.5) * r
        rr = rng.uniform(0.07, 0.18) * r
        d.ellipse([px - rr, py - rr * 0.7, px + rr, py + rr * 0.7], fill=A((62, 88, 72), a))


def amphora(d, x, base, h, ang, col):
    """Ancient two-handled storage jar (an object)."""
    w = h * 0.42
    c, s = math.cos(ang), math.sin(ang)
    def P(px, py):
        return (x + px * c + py * s, base + px * s - py * c)
    prof = [(0.04, 0.0), (0.10, 0.08), (0.36, 0.30), (0.50, 0.48), (0.46, 0.62), (0.30, 0.70),
            (0.13, 0.74), (0.12, 0.90), (0.20, 0.91), (0.20, 1.0)]
    right = [P(px * w, py * h) for px, py in prof]
    left = [P(-px * w, py * h) for px, py in reversed(prof)]
    dark = tuple(int(v * 0.6) for v in col)
    lw = max(4, int(h * 0.045))
    for sx in (-1, 1):
        d.line([P(sx * 0.12 * w, 0.88 * h), P(sx * 0.36 * w, 0.90 * h), P(sx * 0.40 * w, 0.78 * h), P(sx * 0.36 * w, 0.66 * h)],
               fill=dark, width=lw, joint='curve')
    d.polygon(right + left, fill=col, outline=dark)
    for yy in (0.40, 0.56):
        d.line([P(-0.47 * w, yy * h), P(0.47 * w, yy * h)], fill=dark, width=max(3, int(h * 0.02)))


# ---------- seabed (cached background + moving light shafts) ----------
SAND_Y = 700
_SEA = None
_SHAFTS = None

def _sea_base():
    global _SEA, _SHAFTS
    if _SEA is None:
        img = Image.new('RGB', (W, H), BG)
        d = ImageDraw.Draw(img)
        for i in range(0, VB, 6):
            k = i / VB
            d.rectangle([0, i, W, i + 6], fill=(int(10 + 4 * k), int(40 - 18 * k), int(66 - 28 * k)))
        d.rectangle([0, VB, W, H], fill=(8, 11, 16))
        sand = [(x, SAND_Y + 22 * math.sin(x / 170) + 12 * math.sin(x / 53 + 1)) for x in range(0, W + 20, 20)]
        d.polygon(sand + [(W, VB), (0, VB)], fill=(58, 60, 54))
        _SEA = to_arr(img)
        xx = np.arange(W, dtype=np.float32)[None, :]
        yy = np.arange(VB, dtype=np.float32)[:, None]
        _SHAFTS = []
        for x0 in (260, 700, 1150, 1600):
            cx = x0 + yy * 0.3
            band = np.exp(-((xx - cx) ** 2) / (70 ** 2)) * np.clip(1 - yy / 760, 0, 1) * 24
            _SHAFTS.append(band.astype(np.float32))
    return _SEA, _SHAFTS


def seabed(t, light=1.0):
    base, shafts = _sea_base()
    arr = base.copy()
    tot = np.zeros((VB, W), np.float32)
    for j, b in enumerate(shafts):
        tot += b * (0.5 + 0.5 * math.sin(t * 0.9 + j * 1.7)) * light
    arr[:VB] += tot[..., None] * np.array([0.6, 0.9, 1.0], np.float32)
    return to_img(arr)


def particles(d, t, n=80, seed=5):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x0, y0, sp, r = rng.uniform(0, W), rng.uniform(110, VB), rng.uniform(8, 30), rng.uniform(1.2, 3.2)
        y = 110 + (y0 - 110 - t * sp) % (VB - 110)
        x = x0 + 10 * math.sin(t * 0.7 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 190, 200, 70))


# =================== INTRO ===================
def c01(t):
    img = seabed(t)
    d = ImageDraw.Draw(img, 'RGBA')
    for x, b, h, an in ((260, 735, 230, -0.2), (430, 728, 170, 0.35), (1500, 730, 210, 0.15), (1680, 738, 180, -0.4)):
        amphora(d, x, b, h, an, (146, 96, 62))
    rise = ease(ramp(t, 0.4, 4.5))
    cy = 690 - 250 * rise
    lump(d, 960, cy, 140)
    a = ramp(t, 5.0, 6.0)
    if a > 0:
        d.ellipse([960 - 125, cy - 100, 960 + 125, cy + 100], fill=(14, 20, 24, int(235 * a)))
        gear(d, 960, cy, 88, 30, t * 0.25, outline=A(AMBER, a), width=4, hub=(14, 20, 24))
    particles(d, t)
    a1 = ramp(t, 0.5, 0.9) * (1 - ramp(t, 4.4, 4.8))
    text_c(d, (W / 2, 220), '1901', F_BIG, A(WHITE, a1))
    a2 = ramp(t, 9.0, 9.5)
    if a2 > 0:
        card(d, 160, 140, 1760, 300, a2)
        text_c(d, (W / 2, 222), 'A MACHINE FOR THE SKY', F_HUGE, A(AMBER, a2))
    top_label(img, 'ANTIKYTHERA · GREECE', ramp(t, 0.2, 0.6))
    return img

CAP01 = [(0, 5, 'In 1901, divers lifted a lump of corroded bronze from an ancient shipwreck in Greece.', ['1901,', 'bronze', 'shipwreck']),
         (5, 9, 'Months later, someone noticed a gearwheel hidden inside it.', ['gearwheel']),
         (9, 14, 'It turned out to be a machine for predicting the sky, more than two thousand years old.', ['predicting', 'sky,', 'two', 'thousand'])]


def c02(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    gear(d, 300, 470, 230, 60, t * 0.12, fill=(24, 32, 44), hub=BG, spokes=4)
    gear(d, 1640, 470, 170, 44, -t * 0.16, fill=(24, 32, 44), hub=BG, spokes=4)
    a = ramp(t, 0.2, 0.9)
    text_c(d, (W / 2, 400), 'THE ANTIKYTHERA', F_TITLE, A(WHITE, a))
    text_c(d, (W / 2, 540), 'MECHANISM', F_TITLE, A(WHITE, a))
    text_c(d, (W / 2, 670), 'the ancient Greek computer, and how science decoded it', F_MED, A(AMBER, ramp(t, 0.8, 1.4)))
    return img

CAP02 = [(0, 6, 'This is the full story of the Antikythera mechanism, and how science finally learned to read it.', ['Antikythera', 'mechanism,', 'science'])]


# =================== CHAPTER 1 · THE WRECK ===================
def island(d, cam, a=1.0):
    pts = []
    for i in range(24):
        an = 2 * math.pi * i / 24
        u, v = 0.055 * math.cos(an), 0.022 * math.sin(an) * (1 + 0.25 * math.sin(3 * an))
        lon = ISLAND[0] + u * math.cos(-0.6) - v * math.sin(-0.6)
        lat = ISLAND[1] + u * math.sin(-0.6) + v * math.cos(-0.6)
        pts.append(tuple(float(q) for q in cam.xy(lon, lat)))
    d.polygon(pts, fill=LAND, outline=COAST)


def c03(t):
    k = ease(ramp(t, 0.0, 5.0))
    s = math.exp(lerp(math.log(32), math.log(170), k))
    cam = Cam(lerp(22.5, ISLAND[0], k), lerp(37.2, ISLAND[1] + 0.2, k), s)
    img = draw_map(Image.new('RGB', (W, H)), cam)
    d = ImageDraw.Draw(img, 'RGBA')
    island(d, cam)
    la = ramp(t, 2.0, 2.8)
    for name, lon, lat in (('MAINLAND GREECE', 22.2, 37.5), ('CRETE', 24.8, 35.1)):
        x, y = cam.xy(lon, lat)
        if 120 < y < VB - 20 and 100 < x < W - 100:
            text_c(d, (x, y), name, F_LABEL, A(GREY, 0.9 * la))
    x, y = cam.xy(*ISLAND)
    a = ramp(t, 4.5, 5.0)
    if a > 0:
        q = ((t - 4.5) % 1.2) / 1.2
        pr = 30 + 50 * q
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=A(AMBER, a * (1 - q)), width=4)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=A(AMBER, a))
        d.text((x + 40, y - 20), 'ANTIKYTHERA', font=F_MED, fill=A(WHITE, a), anchor='ls')
        d.text((x + 40, y + 16), 'the wreck site', font=F_LABEL, fill=A(AMBER, a), anchor='lt')
    top_label(img, 'CHAPTER 1 · THE WRECK')
    return img

CAP03 = [(0, 3.5, 'In 1900, Greek sponge divers were working off the tiny island of Antikythera…', ['1900,', 'sponge', 'Antikythera…']),
         (3.5, 8, '…between Crete and mainland Greece, when they found the remains of an ancient ship.', ['ancient', 'ship.'])]


def boat(d, cx, y, a=1.0):
    d.polygon([(cx - 120, y - 6), (cx + 130, y - 6), (cx + 95, y + 26), (cx - 95, y + 26)], fill=A((70, 50, 34), a))
    d.line([cx - 10, y - 6, cx - 10, y - 130], fill=A((120, 100, 80), a), width=6)
    d.polygon([(cx - 4, y - 125), (cx + 80, y - 20), (cx - 4, y - 20)], fill=A((200, 190, 170), a))


def c04(t):
    img, d = new()
    for i in range(0, 250, 6):
        d.rectangle([0, i, W, i + 6], fill=(int(lerp(12, 30, i / 250)), int(lerp(18, 44, i / 250)), int(lerp(34, 70, i / 250))))
    for i in range(250, VB, 6):
        k = (i - 250) / (VB - 250)
        d.rectangle([0, i, W, i + 6], fill=(int(lerp(14, 6, k)), int(lerp(52, 16, k)), int(lerp(84, 34, k))))
    wave = [(x, 250 + 6 * math.sin(x / 60 + t * 1.6)) for x in range(0, W + 20, 20)]
    d.line(wave, fill=(120, 170, 200), width=3)
    boat(d, 900, 250 + 6 * math.sin(900 / 60 + t * 1.6))
    sb = [(x, 780 + 10 * math.sin(x / 120)) for x in range(0, W + 20, 20)]
    d.polygon(sb + [(W, VB), (0, VB)], fill=(58, 60, 54))
    for x, an in ((1180, 0.5), (1260, -0.3), (1330, 1.2)):
        amphora(d, x, 786, 70, an, (146, 96, 62))
    for i in range(5):
        x0 = 1050 + i * 70
        d.polygon([(x0, 790), (x0 + 60, 780), (x0 + 64, 790), (x0 + 4, 800)], fill=(70, 52, 38))
    k = ramp(t, 0.5, 3.5)
    sx = 560
    d.line([sx, 255, sx, lerp(255, 780, k)], fill=A(AMBER, 1), width=4)
    for m in range(0, 56, 10):
        y = lerp(255, 780, m / 55)
        if y <= lerp(255, 780, k):
            d.line([sx - 14, y, sx + 14, y], fill=AMBER, width=3)
            d.text((sx - 26, y), f'{m} m', font=F_SMALL, fill=GREY, anchor='rm')
    a = ramp(t, 3.3, 3.7)
    if a > 0:
        d.line([sx - 14, 780, sx + 14, 780], fill=A(AMBER, a), width=4)
        d.text((sx + 30, 760), '≈ 55 m', font=F_MED, fill=A(WHITE, a), anchor='ls')
    a2 = ramp(t, 4.0, 4.4) * (1 - ramp(t, 8.6, 9.0))
    if a2 > 0:
        card(d, 1240, 300, 1800, 520, a2)
        text_c(d, (1520, 380), '≈ 5 MIN', F_HUGE, A(AMBER, a2))
        text_c(d, (1520, 470), 'at the bottom per dive', F_LABEL, A(WHITE, a2))
    a3 = ramp(t, 9.0, 9.4)
    if a3 > 0:
        card(d, 1180, 300, 1860, 520, a3)
        text_c(d, (1520, 380), '1ST CENTURY BC', F_MED, A(AMBER, a3))
        text_c(d, (1520, 460), 'exact date still debated', F_LABEL, A(WHITE, a3))
    for i in range(6):
        q = ((t * 0.5 + i / 6) % 1)
        bx = 1220 + 20 * math.sin(i * 2 + t)
        by = lerp(770, 270, q)
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], outline=(170, 210, 230, 140), width=2)
    top_label(img, 'DEEP AND DANGEROUS')
    return img

CAP04 = [(0, 4, 'The wreck lay in about fifty-five metres of water.', ['fifty-five', 'metres']),
         (4, 9, 'With the diving gear of the time, each diver could stay at the bottom for only about five minutes.', ['five', 'minutes.']),
         (9, 14, 'The ship had gone down in the first century BC. Exactly when is still debated.', ['first', 'century', 'debated.'])]


def coin(d, x, y, r, a=1.0):
    d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=A((170, 160, 120), a), outline=A((110, 100, 70), a), width=2)


def c05(t):
    img = seabed(t, 0.9)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(8):
        x0 = 140 + i * 210
        d.polygon([(x0, 760), (x0 + 170, 742), (x0 + 178, 760), (x0 + 8, 782)], fill=(70, 52, 38))
    items = [(0.5, 'JARS'), (2.5, 'COINS'), (4.0, 'GLASS'), (5.5, 'BRONZE & MARBLE STATUES')]
    for x, b, h, an in ((220, 720, 200, -0.15), (400, 728, 160, 0.3), (1420, 722, 190, 0.1), (1620, 732, 150, -0.35)):
        amphora(d, x, b, h, an, (146, 96, 62))
    ca = ramp(t, 2.3, 2.8)
    for i in range(9):
        coin(d, 640 + i * 26 + 8 * math.sin(i * 3), 708 + 6 * math.cos(i * 2), 16, ca)
    ga = ramp(t, 3.8, 4.3)
    if ga > 0:
        d.chord([1140, 600, 1300, 760], 0, 180, fill=(120, 200, 190, int(110 * ga)), outline=(170, 230, 220, int(220 * ga)), width=3)
        d.ellipse([1140, 660, 1300, 700], outline=(170, 230, 220, int(220 * ga)), width=3)
    la = ramp(t, 8.0, 8.6)
    if la > 0:
        lump(d, 960, 640, 70, a=la)
        d.rounded_rectangle([960 - 140, 640 - 95, 960 + 140, 640 + 95], radius=14, outline=A(AMBER, la), width=5)
    particles(d, t, seed=8)
    for i, (t0, s) in enumerate(items):
        t1 = items[i + 1][0] if i + 1 < len(items) else 8.0
        a = ramp(t, t0, t0 + 0.3) * (1 - ramp(t, t1 - 0.2, t1))
        text_c(d, (W / 2, 220), s, F_MED, A(WHITE, a))
    a = ramp(t, 8.0, 8.4)
    text_c(d, (W / 2, 220), 'A LUMP THE SIZE OF A COOKBOOK', F_MED, A(AMBER, a))
    top_label(img, 'THE CARGO · 1900–1901')
    return img

CAP05 = [(0, 4, 'Over late 1900 and 1901, they brought up a treasure: jars, coins, jewellery and glass…', ['1900', '1901,', 'treasure:']),
         (4, 8, '…and statues of bronze and marble.', ['statues', 'bronze', 'marble.']),
         (8, 13, 'Among the finds was a plain, rocky lump of corroded bronze, about the size of a cookbook.', ['lump', 'cookbook.'])]


# =================== CHAPTER 2 · A GEAR IN THE ROCK ===================
def museum(d):
    d.rectangle([0, 760, W, VB], fill=(30, 36, 48))
    for x in range(120, W, 340):
        d.rectangle([x, 150, x + 60, 760], fill=(22, 28, 38))
    d.rectangle([620, 700, 1300, 740], fill=(46, 54, 68))
    d.rectangle([660, 740, 1260, 760], fill=(38, 44, 58))
    d.rectangle([620, 300, 1300, 700], outline=(90, 120, 150, 120), width=3)
    d.line([640, 320, 720, 400], fill=(160, 200, 230, 60), width=3)


def c06(t):
    img, d = new()
    museum(d)
    lump(d, 960, 600, 110)
    k = ease(ramp(t, 4.0, 6.0))
    if k > 0:
        mx, my = lerp(1420, 990, k), lerp(260, 590, k)
        R = 110
        sub = Image.new('RGB', (W, H), (18, 26, 30))
        d2 = ImageDraw.Draw(sub)
        gear(d2, mx - 20, my - 10, 72, 26, t * 0.15, fill=(150, 160, 120), hub=(18, 26, 30))
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).ellipse([mx - R, my - R, mx + R, my + R], fill=255)
        img.paste(sub, (0, 0), m)
        d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([mx - R, my - R, mx + R, my + R], outline=(200, 205, 215), width=12)
        d.line([mx + R * 0.72, my + R * 0.72, mx + R * 1.4, my + R * 1.4], fill=(200, 205, 215), width=24)
    a = ramp(t, 0.3, 0.8) * (1 - ramp(t, 3.6, 4.0))
    text_c(d, (W / 2, 210), 'ATHENS', F_HUGE, A(WHITE, a))
    a2 = ramp(t, 4.2, 4.6) * (1 - ramp(t, 7.0, 7.3))
    text_c(d, (W / 2, 210), 'MAY 1902', F_HUGE, A(WHITE, a2))
    a3 = ramp(t, 7.3, 7.7)
    text_c(d, (W / 2, 210), 'A GEARWHEEL', F_HUGE, A(AMBER, a3))
    top_label(img, 'CHAPTER 2 · A GEAR IN THE ROCK')
    return img

CAP06 = [(0, 4, 'The finds went to the National Archaeological Museum in Athens.', ['National', 'Archaeological', 'Museum']),
         (4, 7.5, 'Then, in May 1902, an archaeologist there looked more closely at the lump…', ['May', '1902,']),
         (7.5, 11, '…and saw what seemed to be part of a gearwheel, embedded in the rock.', ['gearwheel,'])]


def c07(t):
    img, d = new()
    x0, x1, y = 320, 1720, 520
    d.line([x0, y, x1, y], fill=GREY, width=5)
    pts = [(-200, 'ANCIENT GREECE', 'no geared machines like this known'), (1300, 'MIDDLE AGES', 'complex clockwork')]
    def X(yr): return lerp(x0, x1, (yr + 300) / 1800)
    for i, (yr, a_, b_) in enumerate(pts):
        a = ramp(t, 0.4 + i * 1.6, 0.8 + i * 1.6)
        x = X(yr)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=A(CYAN, a))
        d.text((x, y - 50), a_, font=F_LABEL, fill=A(WHITE, a), anchor='ms')
        d.text((x, y + 50), b_, font=F_SMALL, fill=A(GREY, a), anchor='mt')
    for yr in range(-300, 1501, 300):
        d.text((X(yr), y + 120), f'{-yr} BC' if yr < 0 else ('AD 1' if yr == 0 else f'AD {yr}'), font=F_SMALL, fill=GREY, anchor='mt')
    a = ramp(t, 3.2, 3.7)
    if a > 0:
        card(d, 460, 140, 1460, 330, a)
        text_c(d, (W / 2, 205), 'TOO ADVANCED?', F_MED, A(AMBER, a))
        text_c(d, (W / 2, 280), 'many assumed it was much later than the wreck', F_LABEL, A(WHITE, a))
    a2 = ramp(t, 7.0, 7.5)
    if a2 > 0:
        d.rectangle([0, 100, W, VB], fill=(7, 11, 20, int(250 * a2)))
        text_c(d, (W / 2, 330), 'c. 1905', F_HUGE, A(WHITE, a2))
        text_c(d, (W / 2, 470), 'ALBERT REHM: AN ASTRONOMICAL CALCULATOR', F_MED, A(AMBER, a2))
    top_label(img, 'A PUZZLE')
    return img

CAP07 = [(0, 4.5, 'Nothing like it was known from the ancient world.', ['Nothing']),
         (4.5, 9, 'So at first, many assumed it had to be much younger than the shipwreck.', ['younger']),
         (9, 13.5, 'Around 1905, the scholar Albert Rehm was the first to understand it as an astronomical calculator.', ['Albert', 'Rehm', 'astronomical', 'calculator.']),
         (13.5, 17, 'But for decades, no one could see far enough inside to prove it.', ['inside'])]


# =================== CHAPTER 3 · SEEING INSIDE ===================
FRAG_A = blob(960, 480, 250, 17, n=30, rough=0.22)
INNER = [(860, 450, 190, 56, 1), (1110, 560, 80, 20, -1), (760, 620, 60, 15, 1), (1120, 360, 55, 14, 1)]


def xray_frag(d, t, a=1.0, col=CYAN):
    d.polygon(FRAG_A, fill=A((14, 40, 60), a), outline=A(col, a))
    for x, y, r, n, s in INNER:
        gear(d, x, y, r, n, s * t * 0.08, outline=A(col, a), width=3, hub=(14, 40, 60), spokes=4 if r > 100 else 0)


def c08(t):
    img, d = new()
    d.rounded_rectangle([520, 140, 1400, 820], radius=12, fill=(18, 22, 30), outline=(70, 80, 100), width=3)
    k = ramp(t, 4.0, 7.0)
    xray_frag(d, t, a=0.25 + 0.75 * k, col=(200, 215, 230))
    n = int(27 * ramp(t, 8.0, 11.5))
    if t > 8:
        for i, (x, y, r, nn, s) in enumerate(INNER):
            if i < max(1, n // 7):
                d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=A(AMBER, 0.9))
        card(d, 1460, 330, 1840, 560)
        text_c(d, (1650, 420), f'{n}', F_HUGE, AMBER)
        text_c(d, (1650, 510), 'gears counted', F_LABEL, WHITE)
    a = ramp(t, 12.5, 13.0)
    if a > 0:
        card(d, 80, 330, 500, 560, a)
        text_c(d, (290, 400), '1974', F_MED, A(WHITE, a))
        text_c(d, (290, 470), '“a calendar', F_LABEL, A(AMBER, a))
        text_c(d, (290, 515), 'computer”', F_LABEL, A(AMBER, a))
    top_label(img, 'CHAPTER 3 · SEEING INSIDE')
    return img

CAP08 = [(0, 4, 'In the 1950s, the historian of science Derek de Solla Price took up the puzzle.', ['Derek', 'de', 'Solla', 'Price']),
         (4, 8, 'Using X-ray images made by the Greek radiologist Charalambos Karakalos…', ['X-ray', 'Charalambos', 'Karakalos…']),
         (8, 12, '…he counted twenty-seven gears in the main fragment.', ['twenty-seven', 'gears']),
         (12, 15.5, 'In 1974, he called it a calendar computer.', ['1974,', 'calendar', 'computer.'])]


def spiral_pts(cx, cy, r0, r1, turns, n=400, a0=-math.pi / 2):
    out = []
    for i in range(n + 1):
        q = i / n
        a = a0 + 2 * math.pi * turns * q
        r = lerp(r0, r1, q)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def c09(t):
    img, d = new()
    for L in range(5):
        a = ramp(t, 0.3 + L * 0.5, 0.8 + L * 0.5)
        off = (L - 2) * 34
        d.polygon([(x + off, y - off * 0.5) for x, y in blob(760, 480, 180, 17, n=30, rough=0.22)],
                  outline=A(CYAN, 0.25 + 0.15 * a), fill=A((14, 40, 60), 0.18 * a), width=2)
    gear(d, 760, 480, 130, 40, t * 0.1, outline=A(CYAN, 0.8), width=3, hub=(14, 30, 44))
    k = ramp(t, 5.0, 9.0)
    if k > 0:
        pts = spiral_pts(1360, 480, 70, 270, 5, 500)
        n = max(2, int(len(pts) * k))
        d.line(pts[:n], fill=AMBER, width=5)
        d.text((1360, 800), 'THE BACK DIALS: SPIRALS', font=F_LABEL, fill=A(AMBER, k), anchor='ms')
    a = ramp(t, 4.0, 4.5) * (1 - ramp(t, 9.5, 10))
    if a > 0:
        d.line([520, 220, 1000, 740], fill=A(RED, a), width=10)
        d.line([1000, 220, 520, 740], fill=A(RED, a), width=10)
        d.text((760, 170), "PRICE'S MODEL", font=F_LABEL, fill=A(WHITE, a), anchor='ms')
    top_label(img, 'THE FIRST 3D X-RAYS')
    return img

CAP09 = [(0, 2.8, "Later, Michael Wright of London's Science Museum and Allan Bromley…", ['Michael', 'Wright', 'Allan', 'Bromley…']),
         (2.8, 4.5, '…took the first three-dimensional X-rays.', ['three-dimensional']),
         (4.5, 10, "They showed that Price's model had to be wrong, and that the dials on the back were spirals.", ['wrong,', 'spirals.'])]


def c10(t):
    img, d = new()
    # basement room
    d.rectangle([0, 110, W, VB], fill=(14, 18, 26))
    d.rectangle([0, 760, W, VB], fill=(26, 30, 38))
    for x in range(0, W, 160):
        d.line([x, 110, x, 760], fill=(20, 26, 36), width=3)
    # the X-ray machine: big cabinet
    mx0, mx1 = 360, 1060
    d.rounded_rectangle([mx0, 230, mx1, 760], radius=18, fill=(70, 78, 92), outline=(120, 130, 150), width=4)
    d.rounded_rectangle([mx0 + 60, 300, mx1 - 60, 620], radius=12, fill=(10, 14, 20))
    for i in range(6):
        d.rectangle([mx0 + 60, 650 + i * 14, mx0 + 300, 656 + i * 14], fill=(50, 56, 68))
    d.ellipse([mx1 - 140, 660, mx1 - 80, 720], fill=(255, 150, 60, 200))
    # fragment rotating inside
    ang = t * 0.8
    cx, cy = (mx0 + mx1) / 2, 460
    w_ = 150 * abs(math.cos(ang)) + 20
    d.polygon([(cx + (x - 960) * w_ / 300, cy + (y - 480) * 0.5) for x, y in FRAG_A], fill=BRONZE, outline=BRONZE_D)
    arr = to_arr(img)
    if int(t * 3) % 2 == 0:
        glow(arr, cx, cy, 120, (110, 210, 255), 0.25)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    text_c(d, ((mx0 + mx1) / 2, 200), '≈ 8 TONNES', F_MED, A(AMBER, ramp(t, 0.6, 1.0)))
    # right: dome of flashes
    a = ramp(t, 9.0, 9.5)
    if a > 0:
        dx, dy, R = 1480, 640, 280
        d.pieslice([dx - R, dy - R, dx + R, dy + R], 180, 360, fill=A((40, 48, 62), a), outline=A((120, 130, 150), a), width=3)
        lit = int(t * 8) % 24
        for i in range(24):
            an = math.pi + math.pi * (i + 0.5) / 24
            for rr in (0.55, 0.85):
                px, py = dx + R * rr * math.cos(an), dy + R * rr * math.sin(an)
                on = (i == lit and rr == 0.85) or (i == (lit + 12) % 24 and rr == 0.55)
                d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=A((255, 250, 220) if on else (90, 96, 110), a))
        d.rectangle([dx - 90, dy - 16, dx + 90, dy], fill=A(BRONZE, a))
        d.text((dx, dy + 30), 'surface imaging', font=F_SMALL, fill=A(GREY, a), anchor='mt')
    top_label(img, 'ATHENS · 2005')
    return img

CAP10 = [(0, 4.5, "In 2005, a new team brought an eight-ton X-ray machine into the museum's basement.", ['2005,', 'eight-ton', 'X-ray']),
         (4.5, 9, 'It made 3D scans, like a hospital CT scan, but at much higher resolution.', ['CT', 'scan,', 'higher']),
         (9, 14, 'Others photographed every surface under a dome of flashing lights, to make the faintest marks stand out.', ['dome', 'faintest'])]


rng11 = np.random.default_rng(21)
FRAGS = []
for i in range(82):
    big = i < 7
    r = rng11.uniform(48, 80) if big else rng11.uniform(10, 24)
    ang = rng11.uniform(0, 6.28); dist = rng11.uniform(150, 560) if not big else rng11.uniform(40, 300)
    FRAGS.append((960 + dist * math.cos(ang) * 1.4, 470 + dist * math.sin(ang) * 0.55, r, i))


def c11(t):
    img, d = new()
    k = ease(ramp(t, 0.3, 2.0))
    pie = ramp(t, 4.5, 5.0)
    fa = 1 - 0.8 * pie
    for fx, fy, r, i in FRAGS:
        x, y = lerp(960, fx, k), lerp(470, fy, k)
        d.polygon(blob(x, y, r, 100 + i, n=14, rough=0.3), fill=A(BRONZE, fa))
        if i < 7 and r > 55:
            gear(d, x, y, r * 0.55, 14, t * 0.3 + i, outline=A((170, 180, 140), 0.85 * fa), width=3, spokes=0)
    n = int(round(82 * k))
    a = ramp(t, 0.3, 0.6) * (1 - ramp(t, 3.9, 4.4))
    text_c(d, (W / 2, 170), f'{n} FRAGMENTS', F_MED, A(WHITE, a))
    if pie > 0:
        cx, cy, R = 700, 480, 270
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=A(WHITE, 0.5 * pie), width=4)
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -90, -90 + 120 * ease(ramp(t, 4.6, 5.4)), fill=A(AMBER, 0.9 * pie))
        text_c(d, (cx + 120, cy + 110), 'missing', F_LABEL, A(GREY, pie))
        text_c(d, (cx, 160), '≈ 1/3 SURVIVES', F_MED, A(WHITE, pie))
        a2 = ramp(t, 6.0, 6.4)
        card(d, 1140, 260, 1720, 700, a2)
        text_c(d, (1430, 380), '30', F_BIG, A(AMBER, a2))
        text_c(d, (1430, 540), 'bronze gearwheels', F_LABEL, A(WHITE, a2))
        text_c(d, (1430, 600), '27 in the largest piece', F_SMALL, A(GREY, ramp(t, 8.0, 8.4)))
    top_label(img, 'WHAT SURVIVES')
    return img

CAP11 = [(0, 4.5, 'Today the mechanism is eighty-two fragments, and only about a third of it survives…', ['eighty-two', 'third']),
         (4.5, 11, '…including thirty corroded bronze gearwheels, twenty-seven of them in the largest piece.', ['thirty', 'gearwheels,', 'twenty-seven'])]


rng12 = np.random.default_rng(9)
LETTERS = [(rng12.uniform(320, 1600), rng12.uniform(170, 790), GLYPHS[rng12.integers(len(GLYPHS))]) for _ in range(420)]


def c12(t):
    img, d = new()
    d.rounded_rectangle([260, 140, 1660, 810], radius=10, fill=(30, 40, 44), outline=(80, 100, 96), width=3)
    show = ramp(t, 0.3, 4.0)
    for i, (x, y, g) in enumerate(LETTERS):
        if i / len(LETTERS) < show:
            d.text((x, y), g, font=F_GLYPH, fill=(210, 220, 200, 200), anchor='mm')
    a = ramp(t, 4.5, 5.0) * (1 - ramp(t, 8.6, 9.0))
    if a > 0:
        d.rounded_rectangle([520, 300, 1400, 640], radius=22, fill=(0, 0, 0, int(240 * a)))
        text_c(d, (W / 2, 400), '≈ 3,000', F_HUGE, A(AMBER, a))
        text_c(d, (W / 2, 500), 'characters read', F_LABEL, A(WHITE, a))
        text_c(d, (W / 2, 570), 'of perhaps 15,000', F_LABEL, A(GREY, a))
    a2 = ramp(t, 9.0, 9.4)
    if a2 > 0:
        d.rectangle([0, 100, W, VB], fill=(7, 11, 20, int(235 * a2)))
        off = (t * 30) % 160
        d.rectangle([0, 600, W, 760], fill=A(BRASS, a2))
        for i in range(-1, 14):
            x = i * 160 - off
            d.polygon([(x + 20, 600), (x + 60, 430), (x + 100, 430), (x + 140, 600)], fill=A(BRASS, a2))
        tx = 6 * 160 - off + 80
        d.line([tx + 110, 430, tx + 110, 600], fill=A(AMBER, a2), width=4)
        for yy in (430, 600):
            d.line([tx + 95, yy, tx + 125, yy], fill=A(AMBER, a2), width=4)
        d.text((tx + 140, 515), '≈ 1.5 mm', font=F_MED, fill=A(WHITE, a2), anchor='lm')
        text_c(d, (W / 2, 220), 'GEAR TEETH, MAGNIFIED', F_MED, A(AMBER, a2))
    top_label(img, 'A HIDDEN MANUAL')
    return img

CAP12 = [(0, 4.5, 'The scans also revealed hidden text: essentially an instruction manual, engraved on its plates.', ['instruction', 'manual,']),
         (4.5, 9, 'About three thousand characters have been read, out of perhaps fifteen thousand.', ['three', 'thousand', 'fifteen']),
         (9, 13, 'And its gear teeth? Some are just one and a half millimetres long.', ['one', 'half', 'millimetres'])]


# =================== CHAPTER 4 · THE FRONT ===================
def wood_box(d, x0, y0, x1, y1, a=1.0):
    d.rectangle([x0, y0, x1, y1], fill=A(WOOD, a), outline=A((60, 40, 26), a), width=5)
    for i in range(6):
        yy = lerp(y0 + 20, y1 - 20, i / 5)
        d.line([x0 + 10, yy, x1 - 10, yy + 6], fill=A((80, 55, 34), a), width=2)


def c13(t):
    img, d = new()
    a = ramp(t, 0.2, 0.8)
    bx0, by0, bx1, by1 = 700, 150, 1140, 800
    d.polygon([(bx1, by0), (bx1 + 120, by0 - 60), (bx1 + 120, by1 - 60), (bx1, by1)], fill=A((70, 48, 30), a))
    d.polygon([(bx0, by0), (bx0 + 120, by0 - 60), (bx1 + 120, by0 - 60), (bx1, by0)], fill=A((110, 78, 50), a))
    wood_box(d, bx0, by0, bx1, by1, a)
    d.ellipse([bx0 + 50, by0 + 100, bx1 - 50, by0 + 440], fill=A((20, 26, 36), a), outline=A(BRASS, a), width=5)
    kx, ky = bx1 + 60, (by0 + by1) / 2 - 30
    ca = ease(ramp(t, 5.0, 10.0)) * 12
    d.ellipse([kx - 18, ky - 18, kx + 18, ky + 18], fill=A(BRASS, a))
    hx, hy = kx + 70 * math.cos(ca), ky + 70 * math.sin(ca)
    d.line([kx, ky, hx, hy], fill=A(BRASS, a), width=10)
    d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=A((160, 120, 70), a))
    da = ramp(t, 1.0, 1.4)
    d.line([bx0 - 60, by0, bx0 - 60, by1], fill=A(AMBER, da), width=4)
    d.text((bx0 - 80, (by0 + by1) / 2), '≈ 32 cm', font=F_LABEL, fill=A(WHITE, da), anchor='rm')
    d.line([bx0, by1 + 0, bx1, by1], fill=A(AMBER, da), width=4)
    card(d, 1360, 330, 1820, 520, da)
    text_c(d, (1590, 395), '32 × 18 × 10 cm', F_LABEL, A(WHITE, da))
    text_c(d, (1590, 460), 'a wooden case', F_SMALL, A(GREY, da))
    for g, (gx, gy, r, n) in enumerate(((1450, 680, 100, 32), (1620, 610, 70, 22), (1740, 730, 55, 16))):
        gear(d, gx, gy, r, n, (1 if g % 2 else -1) * ca * 40 / n, fill=A(BRASS, ramp(t, 5.0, 5.5)), hub=BG, spokes=4 if r > 80 else 0)
    top_label(img, 'CHAPTER 4 · THE FRONT')
    return img

CAP13 = [(0, 5, 'Put back together, it was a wooden case of about thirty-two by eighteen by ten centimetres.', ['thirty-two', 'eighteen', 'ten']),
         (5, 10, 'Turn a handle on the side, and the gears drove dials on the front and on the back.', ['handle', 'dials'])]


DC = (960, 470)


def front_dial(d, t, spin, rings=True, rot=0.0):
    cx, cy = DC
    d.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], fill=(40, 30, 22), outline=(90, 66, 44), width=6)
    d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], outline=CYAN, width=4)
    for i in range(365):
        if i % 5 == 0:
            a = 2 * math.pi * i / 365 + rot
            d.line([cx + 308 * math.cos(a), cy + 308 * math.sin(a), cx + 328 * math.cos(a), cy + 328 * math.sin(a)], fill=CYAN, width=2)
    d.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], fill=(20, 26, 36), outline=BRASS, width=5)
    for i in range(12):
        a = 2 * math.pi * i / 12
        d.line([cx + 240 * math.cos(a), cy + 240 * math.sin(a), cx + 300 * math.cos(a), cy + 300 * math.sin(a)], fill=BRASS, width=3)
        am = a + math.pi / 12
        d.text((cx + 270 * math.cos(am), cy + 270 * math.sin(am)), GLYPHS[i], font=F_GLYPH, fill=BRASS, anchor='mm')
    d.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], outline=BRASS, width=3)


def c14(t):
    img, d = new()
    za = ramp(t, 0.5, 1.0)
    front_dial(d, t, 0, rot=0.6 * ease(ramp(t, 7.0, 9.0)))
    cx, cy = DC
    a = ramp(t, 0.6, 1.0) * (1 - ramp(t, 5.6, 6.0))
    if a > 0:
        d.arc([cx - 300, cy - 300, cx + 300, cy + 300], 0, 360, fill=A(AMBER, a), width=10)
        d.text((cx + 380, 220), 'ZODIAC: 12 SIGNS', font=F_LABEL, fill=A(AMBER, a), anchor='lm')
        d.text((cx + 380, 270), "the Sun's yearly path", font=F_SMALL, fill=A(GREY, a), anchor='lm')
    a2 = ramp(t, 6.0, 6.4)
    if a2 > 0:
        d.arc([cx - 330, cy - 330, cx + 330, cy + 330], 0, 360, fill=A(CYAN, a2), width=10)
        d.text((cx + 380, 220), '365-DAY CALENDAR', font=F_LABEL, fill=A(CYAN, a2), anchor='lm')
        d.text((cx + 380, 270), 'a movable ring', font=F_SMALL, fill=A(GREY, a2), anchor='lm')
        d.text((cx + 380, 310), '(+1 day every 4 years)', font=F_SMALL, fill=A(GREY, ramp(t, 8.5, 9.0)), anchor='lm')
    top_label(img, 'THE FRONT DIAL')
    return img

CAP14 = [(0, 6, "On the front was a ring for the twelve signs of the zodiac, the Sun's path through the sky…", ['twelve', 'zodiac,']),
         (6, 12, '…and a 365-day calendar ring that could be moved, to allow for an extra day every four years.', ['365-day', 'extra', 'four'])]


def c15(t):
    img, d = new()
    front_dial(d, t, 0)
    cx, cy = DC
    spin = t * 0.5
    arr = to_arr(img)
    sa = spin * 0.3
    sx, sy = cx + 200 * math.cos(sa), cy + 200 * math.sin(sa)
    glow(arr, sx, sy, 30, (255, 190, 80), 1.0)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.line([cx, cy, sx, sy], fill=(230, 190, 110), width=5)
    d.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=(255, 200, 60))
    ma = spin * 1.6
    mx, my = cx + 150 * math.cos(ma), cy + 150 * math.sin(ma)
    d.line([cx, cy, mx, my], fill=(200, 200, 210), width=4)
    R = 26
    d.ellipse([mx - R, my - R, mx + R, my + R], fill=(230, 230, 230))
    ph = (spin * 1.3) % (2 * math.pi)
    k = math.cos(ph)
    d.pieslice([mx - R, my - R, mx + R, my + R], 90, 270, fill=(30, 30, 36))
    d.ellipse([mx - R * abs(k), my - R, mx + R * abs(k), my + R], fill=(30, 30, 36) if k > 0 else (230, 230, 230))
    pa = ramp(t, 6.5, 7.0)
    if pa > 0:
        for r, col, sp in ((90, (200, 200, 200), 2.0), (115, (240, 230, 200), 1.2), (230, (230, 80, 60), 0.5), (255, (220, 180, 120), 0.2), (280, (200, 200, 170), 0.1)):
            pa_ = r * 0.37 + sp * spin
            px, py = cx + r * math.cos(pa_), cy + r * math.sin(pa_)
            d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=A(col, pa))
        d.text((cx + 380, 300), 'MARS: fiery red', font=F_LABEL, fill=A(RED, pa), anchor='lm')
        d.text((cx + 380, 350), 'SUN: gold', font=F_LABEL, fill=A((255, 200, 60), pa), anchor='lm')
    a = ramp(t, 2.5, 3.0) * (1 - ramp(t, 6.2, 6.5))
    d.text((cx + 380, 300), "MOON'S PHASE", font=F_LABEL, fill=A(WHITE, a), anchor='lm')
    d.text((cx + 380, 350), 'a black and silver ball', font=F_SMALL, fill=A(GREY, a), anchor='lm')
    top_label(img, 'SUN, MOON AND PLANETS')
    return img

CAP15 = [(0, 2.5, 'Pointers showed the Sun and the Moon.', ['Sun', 'Moon.']),
         (2.5, 6.5, "A little turning ball, half black and half silver, showed the Moon's phase.", ['black', 'silver,', 'phase.']),
         (6.5, 12, 'Coloured balls probably marked the planets: fiery red for Mars, gold for the Sun.', ['planets:', 'red', 'gold'])]


def c16(t):
    img, d = new()
    draw_stars(d, t, 0.5, ymax=VB)
    # left: Moon's path, fast and slow
    ex, ey, ea, eb = 520, 470, 300, 220
    d.ellipse([ex - ea, ey - eb, ex + ea, ey + eb], outline=(80, 100, 130), width=3)
    d.ellipse([ex + 90 - 26, ey - 26, ex + 90 + 26, ey + 26], fill=(60, 120, 200))
    # Kepler-ish varying speed
    M = t * 0.7
    E = M
    for _ in range(5):
        E = M + 0.45 * math.sin(E)
    mx, my = ex + ea * math.cos(E), ey + eb * math.sin(E)
    d.ellipse([mx - 18, my - 18, mx + 18, my + 18], fill=(230, 230, 230))
    d.text((ex + 90, ey + 50), 'Earth', font=F_SMALL, fill=GREY, anchor='mt')
    a = ramp(t, 2.0, 2.5)
    d.text((ex, 190), 'FASTER  ·  SLOWER', font=F_LABEL, fill=A(AMBER, a), anchor='mm')
    # right: pin and slot
    g1 = (1330, 470); g2 = (1372, 470)
    a2 = ramp(t, 5.0, 5.5)
    if a2 > 0:
        r1 = 150
        th = t * 1.0
        gear(d, g1[0], g1[1], r1, 50, th, outline=A(BRASS, a2), width=3, hub=BG, spokes=0)
        gear(d, g2[0], g2[1], r1, 50, -th * 0.98, outline=A(CYAN, a2), width=3, hub=BG, spokes=0)
        px, py = g1[0] + 110 * math.cos(th), g1[1] + 110 * math.sin(th)
        d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=A(AMBER, a2))
        ang = math.atan2(py - g2[1], px - g2[0])
        d.line([g2[0] + 40 * math.cos(ang), g2[1] + 40 * math.sin(ang), g2[0] + 150 * math.cos(ang), g2[1] + 150 * math.sin(ang)], fill=A(CYAN, a2), width=14)
        d.line([g2[0] + 40 * math.cos(ang), g2[1] + 40 * math.sin(ang), g2[0] + 150 * math.cos(ang), g2[1] + 150 * math.sin(ang)], fill=A(BG, a2), width=6)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=A(AMBER, a2))
        d.text((1350, 700), 'PIN  +  SLOT', font=F_MED, fill=A(WHITE, a2), anchor='mm')
    a3 = ramp(t, 11.0, 11.4)
    if a3 > 0:
        card(d, 960, 140, 1800, 260, a3)
        text_c(d, (1380, 200), 'a theory often linked to HIPPARCHUS', F_LABEL, A(AMBER, a3))
    top_label(img, 'A CLEVER TRICK')
    return img

CAP16 = [(0, 1.8, 'Then there was a clever trick.', ['clever', 'trick.']),
         (1.8, 5, 'Seen from Earth, the Moon speeds up and slows down as it crosses the sky.', ['speeds', 'up', 'slows', 'down']),
         (5, 11, "A pin on one gear, sliding in a slot on another, made the Moon's pointer do the same…", ['pin', 'slot']),
         (11, 15, '…following an astronomical theory often linked to the Greek astronomer Hipparchus.', ['Hipparchus.'])]


# =================== CHAPTER 5 · THE BACK ===================
MONTHS = ['ΦΟΙΝΙΚΑΙΟΣ', 'ΚΡΑΝΕΙΟΣ', 'ΛΑΝΟΤΡΟΠΙΟΣ', 'ΜΑΧΑΝΕΥΣ', 'ΔΩΔΕΚΑΤΕΥΣ', 'ΕΥΚΛΕΙΟΣ']


def back_spiral(d, cx, cy, r0, r1, turns, cells, k, col, label=None, ptr=None):
    pts = spiral_pts(cx, cy, r0, r1, turns, 600)
    n = max(2, int(len(pts) * k))
    d.line(pts[:n], fill=col, width=4)
    inner = spiral_pts(cx, cy, r0 + (r1 - r0) / turns, r1 + (r1 - r0) / turns, turns, 600)
    for i in range(0, int(cells * k)):
        q = i / cells
        j = int(q * 600)
        x0, y0 = pts[j]; x1, y1 = inner[j]
        d.line([x0, y0, lerp(x0, x1, 0.8), lerp(y0, y1, 0.8)], fill=col + (140,), width=1)
    if ptr is not None:
        j = int(ptr * 600) % 600
        x, y = pts[j]
        d.line([cx, cy, x, y], fill=WHITE, width=4)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=WHITE)


def c17(t):
    img, d = new()
    d.rounded_rectangle([520, 120, 1400, 820], radius=10, fill=(40, 30, 22), outline=(90, 66, 44), width=5)
    k = ramp(t, 0.5, 5.0)
    back_spiral(d, 960, 470, 70, 320, 5, 235, k, AMBER, ptr=ramp(t, 5.0, 12) * 0.98)
    a = ramp(t, 3.0, 3.4)
    card(d, 1440, 280, 1860, 520, a)
    text_c(d, (1650, 350), '235', F_HUGE, A(AMBER, a))
    text_c(d, (1650, 430), 'lunar months', F_LABEL, A(WHITE, a))
    text_c(d, (1650, 480), '≈ 19 years', F_LABEL, A(GREY, ramp(t, 4.0, 4.4)))
    a2 = ramp(t, 8.0, 8.4)
    if a2 > 0:
        for i, m in enumerate(MONTHS):
            d.text((280, 220 + i * 70), m, font=F_SMALL, fill=A(WHITE, a2 * (0.6 + 0.4 * (i % 2))), anchor='mm')
        d.text((280, 660), 'CORINTHIAN', font=F_LABEL, fill=A(AMBER, a2), anchor='mm')
        d.text((280, 705), 'month names', font=F_SMALL, fill=A(GREY, a2), anchor='mm')
    top_label(img, 'CHAPTER 5 · THE BACK')
    return img

CAP17 = [(0, 4, 'On the back, an upper spiral of five turns counted 235 lunar months…', ['five', '235', 'lunar', 'months…']),
         (4, 8, '…which fit almost exactly into nineteen years.', ['nineteen', 'years.']),
         (8, 13, 'Its month names match a calendar used in Corinthian colonies in north-west Greece.', ['Corinthian', 'colonies'])]


def c18(t):
    img, d = new()
    cx, cy, R = 960, 470, 300
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(40, 30, 22), outline=BRASS, width=6)
    d.line([cx - R, cy, cx + R, cy], fill=BRASS, width=4)
    d.line([cx, cy - R, cx, cy + R], fill=BRASS, width=4)
    names = [('ΙΣΘΜΙΑ', -45), ('ΟΛΥΜΠΙΑ', 45), ('ΝΕΜΕΑ', 135), ('ΠΥΘΙΑ', -135)]
    for s, an in names:
        a = math.radians(an)
        d.text((cx + 160 * math.cos(a), cy + 160 * math.sin(a)), s, font=F_LABEL, fill=BRASS, anchor='mm')
    q = ease(ramp(t, 1.0, 9.0)) * 4
    pa = math.radians(45) - math.pi / 2 * q + math.pi / 2 * 0
    pa = math.radians(45) + math.pi / 2 * int(q)
    d.line([cx, cy, cx + 90 * math.cos(pa), cy + 90 * math.sin(pa)], fill=WHITE, width=8)
    d.polygon([(cx + 120 * math.cos(pa), cy + 120 * math.sin(pa)), (cx + 85 * math.cos(pa + 0.25), cy + 85 * math.sin(pa + 0.25)), (cx + 85 * math.cos(pa - 0.25), cy + 85 * math.sin(pa - 0.25))], fill=WHITE)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=WHITE)
    labs = [(0.3, 'OLYMPIC'), (5.0, 'NEMEAN · ISTHMIAN · PYTHIAN')]
    for i, (t0, s) in enumerate(labs):
        t1 = labs[i + 1][0] if i + 1 < len(labs) else 99
        a = ramp(t, t0, t0 + 0.3) * (1 - ramp(t, t1 - 0.2, t1))
        d.text((1300, 470), s if len(s) < 10 else '', font=F_MED, fill=A(AMBER, a), anchor='lm')
        if len(s) > 10 and a > 0:
            for j, w_ in enumerate(s.split(' · ')):
                d.text((1300, 360 + j * 80), w_, font=F_MED, fill=A(AMBER, a), anchor='lm')
    d.text((cx, 120 + 20), '4-YEAR CYCLE OF GAMES', font=F_LABEL, fill=CYAN, anchor='mt')
    top_label(img, 'THE GAMES DIAL')
    return img

CAP18 = [(0, 5, 'A small dial inside it followed the four-year cycle of the great Greek games, including the Olympics.', ['four-year', 'Olympics.']),
         (5, 10, 'The Nemean, Isthmian and Pythian games are named on it too.', ['Nemean,', 'Isthmian', 'Pythian'])]


def c19(t):
    img, d = new()
    d.rounded_rectangle([140, 120, 1060, 820], radius=10, fill=(40, 30, 22), outline=(90, 66, 44), width=5)
    k = ramp(t, 0.5, 4.5)
    back_spiral(d, 600, 470, 90, 320, 4, 223, k, CYAN, ptr=ramp(t, 4.5, 14) * 0.98)
    pts = spiral_pts(600, 470, 90, 320, 4, 600)
    ga = ramp(t, 5.5, 6.0)
    for i in range(0, 223, 6):
        if (i * 7) % 5 == 0:
            j = int(i / 223 * 600)
            x, y = pts[j]
            d.text((x, y - 4), 'Σ' if (i // 6) % 2 else 'Η', font=F_TINY, fill=A(AMBER, ga), anchor='mm')
    a = ramp(t, 2.5, 3.0) * (1 - ramp(t, 9.5, 10))
    if a > 0:
        card(d, 1140, 280, 1800, 520, a)
        text_c(d, (1470, 360), '223 MONTHS', F_MED, A(CYAN, a))
        text_c(d, (1470, 440), 'the Saros cycle, ≈ 18 years', F_LABEL, A(WHITE, a))
    if 5.5 < t < 10:
        card(d, 1140, 560, 1800, 760, ga)
        text_c(d, (1470, 620), 'Σ  = Selene, the Moon', F_LABEL, A(AMBER, ga))
        text_c(d, (1470, 690), 'Η  = Helios, the Sun', F_LABEL, A(AMBER, ga))
    e = ramp(t, 10, 14)
    if t >= 10:
        sx, sy = 1470, 470
        arr = to_arr(img)
        glow(arr, sx, sy, 150, (255, 200, 120), 0.6 + 0.3 * math.sin(t * 2) * 0.2)
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([sx - 110, sy - 110, sx + 110, sy + 110], fill=(255, 210, 120))
        mx = lerp(sx + 300, sx, ease(min(e * 1.6, 1)))
        d.ellipse([mx - 112, sy - 112, mx + 112, sy + 112], fill=(10, 12, 18))
        text_c(d, (sx, 160), 'ECLIPSE AHEAD', F_MED, A(WHITE, ramp(t, 11, 11.5)))
    top_label(img, 'THE ECLIPSE DIAL')
    return img

CAP19 = [(0, 5, 'A lower spiral of four turns had 223 divisions: the Saros cycle, about eighteen years of eclipses.', ['four', '223', 'Saros']),
         (5, 7, 'Small symbols marked the months with eclipses…', ['symbols', 'eclipses…']),
         (7, 10, '…sigma for the Moon, Selene, and eta for the Sun, Helios.', ['Selene,', 'Helios.']),
         (10, 14, 'So by turning the handle, its user could see which months would bring an eclipse.', ['eclipse.'])]


# =================== CHAPTER 6 · THE 2021 MODEL ===================
def c20(t):
    img, d = new()
    cx, cy = 760, 470
    rings = [(60, 'MOON', (230, 230, 230)), (95, 'MERCURY', (170, 170, 170)), (125, 'VENUS', (240, 230, 200)),
             (160, 'SUN', (255, 200, 60)), (200, 'MARS', (230, 80, 60)), (240, 'JUPITER', (220, 180, 120)), (280, 'SATURN', (200, 200, 170))]
    d.ellipse([cx - 320, cy - 320, cx + 320, cy + 320], fill=(20, 26, 36), outline=BRASS, width=5)
    for i, (r, name, col) in enumerate(rings):
        a = ramp(t, 0.5 + i * 0.35, 0.9 + i * 0.35)
        if a <= 0:
            continue
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=A(BRASS, 0.7 * a), width=3)
        an = r * 0.53 + t * (1.2 - i * 0.14)
        px, py = cx + r * math.cos(an), cy + r * math.sin(an)
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=A(col, a))
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(120, 170, 220))
    a = ramp(t, 9.0, 9.4)
    if a > 0:
        card(d, 1180, 200, 1820, 420, a)
        text_c(d, (1500, 270), 'ΥΞΒ = 462', F_MED, A(AMBER, a))
        text_c(d, (1500, 350), 'Venus: 289 cycles in 462 years', F_LABEL, A(WHITE, ramp(t, 13.0, 13.4)))
        a2 = ramp(t, 10.5, 10.9)
        card(d, 1180, 470, 1820, 690, a2)
        text_c(d, (1500, 540), 'ΥΜΒ = 442', F_MED, A(CYAN, a2))
        text_c(d, (1500, 620), 'Saturn: 427 cycles in 442 years', F_LABEL, A(WHITE, ramp(t, 15.0, 15.4)))
    a3 = ramp(t, 0.5, 1.0) * (1 - ramp(t, 8.6, 9.0))
    if a3 > 0:
        text_c(d, (1500, 380), 'UCL · 2021', F_HUGE, A(WHITE, a3))
        text_c(d, (1500, 480), 'a new model of the front', F_LABEL, A(GREY, a3))
    top_label(img, 'CHAPTER 6 · THE 2021 MODEL')
    return img

CAP20 = [(0, 4.5, 'In 2021, a team at University College London published a new model of the front of the machine.', ['2021,', 'University', 'College', 'London']),
         (4.5, 9, 'It shows nested rings for the Moon, the Sun and the five planets known in ancient times.', ['nested', 'rings', 'five', 'planets']),
         (9, 13, 'The key was two numbers found in the inscriptions: 462 for Venus, and 442 for Saturn.', ['462', 'Venus,', '442', 'Saturn.']),
         (13, 17.5, 'They match ancient cycles: Venus repeats 289 times in 462 years, and Saturn 427 times in 442 years.', ['289', '427']),
         (17.5, 21, 'But with two-thirds of it lost, parts of any model are still a best guess.', ['two-thirds', 'best', 'guess.'])]


# =================== CHAPTER 7 · WHO MADE IT? ===================
def c21(t):
    k = ease(ramp(t, 0.0, 3.0))
    cam = Cam(lerp(22, 19.5, k), lerp(37.5, 37.4, k), lerp(60, 85, k))
    img = draw_map(Image.new('RGB', (W, H)), cam)
    d = ImageDraw.Draw(img, 'RGBA')
    for (lon, lat), name, t0, col in ((SYRACUSE, 'SYRACUSE', 8.0, AMBER), (CORINTH, 'CORINTH', 6.4, CYAN), (ISLAND, 'ANTIKYTHERA', 0.5, WHITE)):
        a = ramp(t, t0, t0 + 0.4)
        if a <= 0:
            continue
        x, y = cam.xy(lon, lat)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=A(col, a))
        d.text((x + 22, y), name, font=F_LABEL, fill=A(col, a), anchor='lm')
    a = ramp(t, 0.5, 0.9) * (1 - ramp(t, 6.0, 6.3))
    if a > 0:
        card(d, 480, 130, 1440, 300, a)
        text_c(d, (W / 2, 190), 'MADE WHEN?', F_MED, A(WHITE, a))
        text_c(d, (W / 2, 260), '2nd century BC to early 1st century BC', F_LABEL, A(AMBER, a))
    a2 = ramp(t, 11.2, 11.6)
    if a2 > 0:
        card(d, 460, 130, 1460, 320, a2)
        text_c(d, (W / 2, 190), 'ARCHIMEDES · died 212 BC', F_MED, A(AMBER, a2))
        text_c(d, (W / 2, 265), 'probably too early to have built it', F_LABEL, A(WHITE, a2))
    top_label(img, 'CHAPTER 7 · WHO MADE IT?')
    return img

CAP21 = [(0, 4, 'Who made it, and when, is still debated.', ['debated.']),
         (4, 8.5, 'Estimates range from the second century BC to the early first century BC.', ['second', 'century', 'first']),
         (8.5, 13, 'Its Corinthian calendar has led some to suggest Syracuse, in Sicily, the home of Archimedes.', ['Corinthian', 'Syracuse,', 'Archimedes.']),
         (13, 15, 'Archimedes died in 212 BC, so he probably did not build it.', ['212', 'BC,']),
         (15, 17.5, 'But the Roman writer Cicero credited him with a similar machine…', ['Cicero']),
         (17.5, 21, '…and some experts think the idea may go back to him.', ['idea'])]


def c22(t):
    img, d = new()
    x0, x1, y = 160, 1760, 520
    def X(yr): return lerp(x0, x1, (yr + 300) / 1800)
    k = ease(ramp(t, 0.3, 4.0))
    d.line([x0, y, lerp(x0, x1, k), y], fill=GREY, width=6)
    for yr in range(-300, 1501, 300):
        if X(yr) <= lerp(x0, x1, k):
            d.line([X(yr), y - 12, X(yr), y + 12], fill=GREY, width=3)
            d.text((X(yr), y + 30), f'{-yr} BC' if yr < 0 else ('AD 1' if yr == 0 else f'AD {yr}'), font=F_SMALL, fill=GREY, anchor='mt')
    gear(d, X(-120), y - 160, 80, 22, t * 0.4, fill=AMBER, hub=BG)
    d.text((X(-120), y + 90), 'ANTIKYTHERA MECHANISM', font=F_SMALL, fill=AMBER, anchor='mt')
    for i in range(6):
        qa = ramp(t, 1.0 + 0.4 * i, 1.4 + 0.4 * i)
        text_c(d, (X(150 + i * 200), y - 80), '?', F_MED, A(GREY, 0.7 * qa))
    a = ramp(t, 4.0, 4.5)
    if a > 0:
        gear(d, X(1350), y - 160, 80, 22, -t * 0.4, fill=A(CYAN, a), hub=BG)
        d.text((X(1350), y + 90), 'LATER MIDDLE AGES', font=F_SMALL, fill=A(CYAN, a), anchor='mt')
        d.text((X(1350), y + 125), 'clockwork', font=F_SMALL, fill=A(WHITE, a), anchor='mt')
    a2 = ramp(t, 5.0, 5.5)
    text_c(d, (W / 2, 180), '1,000+ YEARS', F_HUGE, A(WHITE, a2))
    top_label(img, 'A LOST TECHNOLOGY')
    return img

CAP22 = [(0, 5, 'Whoever made it, nothing this complex is known again until the clockwork of the later Middle Ages…', ['complex', 'Middle', 'Ages…']),
         (5, 8, '…more than a thousand years later.', ['thousand', 'years']),
         (8, 12, 'How much ancient knowledge sank with ships like this one, no one can say.', ['no', 'one'])]


def c23(t):
    img, d = new()
    draw_stars(d, t, 0.6, ymax=VB)
    gear(d, 760, 470, 260, 64, t * 0.15, fill=(30, 38, 50), hub=BG, spokes=4)
    gear(d, 1150, 610, 130, 32, -t * 0.3, fill=(30, 38, 50), hub=BG, spokes=4)
    gear(d, 1160, 300, 90, 22, -t * 0.43, fill=(30, 38, 50), hub=BG, spokes=0)
    a = ramp(t, 0.4, 1.0) * (1 - ramp(t, 12.6, 13.0))
    if a > 0:
        card(d, 230, 190, 1690, 420, a)
        text_c(d, (W / 2, 270), 'STILL A MYSTERY', F_HUGE, A(AMBER, a))
        text_c(d, (W / 2, 370), 'who built it · where · how many existed', F_LABEL, A(WHITE, a))
    a3 = ramp(t, 13.0, 13.4)
    if a3 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(170 * a3)))
        text_c(d, (W / 2, 380), 'FOLLOW', F_HUGE, A(WHITE, a3))
        text_c(d, (W / 2, 500), 'for more unexplained history', F_MED, A(AMBER, a3))
    top_label(img, 'STILL A MYSTERY', 1 - a3)
    return img

CAP23 = [(0, 5, 'A lump from the seabed turned out to be a model of the heavens, in bronze.', ['model', 'heavens,', 'bronze.']),
         (5, 8.5, 'Its maker is unknown, and so is whether it was one of a kind.', ['unknown,', 'one', 'kind.']),
         (8.5, 12, 'But its gears still turn, in scans, in models and in our imagination.', ['gears', 'turn,'])]


SCENES = [
    ('c01', c01, 14.0, CAP01), ('c02', c02, 6.0, CAP02), ('c03', c03, 8.0, CAP03), ('c04', c04, 14.0, CAP04),
    ('c05', c05, 13.0, CAP05), ('c06', c06, 11.0, CAP06), ('c07', c07, 17.0, CAP07), ('c08', c08, 15.5, CAP08),
    ('c09', c09, 10.0, CAP09), ('c10', c10, 14.0, CAP10), ('c11', c11, 11.0, CAP11), ('c12', c12, 13.0, CAP12),
    ('c13', c13, 10.0, CAP13), ('c14', c14, 12.0, CAP14), ('c15', c15, 12.0, CAP15), ('c16', c16, 15.0, CAP16),
    ('c17', c17, 13.0, CAP17), ('c18', c18, 10.0, CAP18), ('c19', c19, 14.0, CAP19), ('c20', c20, 21.0, CAP20),
    ('c21', c21, 21.0, CAP21), ('c22', c22, 12.0, CAP22), ('c23', c23, 16.0, CAP23),
]

ANTI = 'Anti-kithera'
SPOKEN = {
    'In 1901, divers lifted a lump of corroded bronze from an ancient shipwreck in Greece.':
        'In nineteen oh one, divers lifted a lump of corroded bronze from an ancient shipwreck in Greece.',
    'This is the full story of the Antikythera mechanism, and how science finally learned to read it.':
        f'This is the full story of the {ANTI} mechanism, and how science finally learned to read it.',
    'In 1900, Greek sponge divers were working off the tiny island of Antikythera…':
        f'In nineteen hundred, Greek sponge divers were working off the tiny island of {ANTI},',
    '…between Crete and mainland Greece, when they found the remains of an ancient ship.':
        'between Crete and mainland Greece, when they found the remains of an ancient ship.',
    'The ship had gone down in the first century BC. Exactly when is still debated.':
        'The ship had gone down in the first century B.C. Exactly when, is still debated.',
    'Over late 1900 and 1901, they brought up a treasure: jars, coins, jewellery and glass…':
        'Over late nineteen hundred and nineteen oh one, they brought up a treasure: jars, coins, jewellery and glass,',
    '…and statues of bronze and marble.': 'and statues of bronze and marble.',
    'Then, in May 1902, an archaeologist there looked more closely at the lump…':
        'Then, in May nineteen oh two, an archaeologist there looked more closely at the lump,',
    '…and saw what seemed to be part of a gearwheel, embedded in the rock.': 'and saw what seemed to be part of a gear wheel, embedded in the rock.',
    'Months later, someone noticed a gearwheel hidden inside it.': 'Months later, someone noticed a gear wheel hidden inside it.',
    'Around 1905, the scholar Albert Rehm was the first to understand it as an astronomical calculator.':
        'Around nineteen oh five, the scholar Albert Raym was the first to understand it as an astronomical calculator.',
    'In the 1950s, the historian of science Derek de Solla Price took up the puzzle.':
        'In the nineteen fifties, the historian of science Derek de Solla Price took up the puzzle.',
    'Using X-ray images made by the Greek radiologist Charalambos Karakalos…':
        'Using X-ray images made by the Greek radiologist Kharalambos Karakalos,',
    '…he counted twenty-seven gears in the main fragment.': 'he counted twenty-seven gears in the main fragment.',
    'In 1974, he called it a calendar computer.': 'In nineteen seventy-four, he called it a calendar computer.',
    "In 2005, a new team brought an eight-ton X-ray machine into the museum's basement.":
        "In two thousand five, a new team brought an eight-ton X-ray machine into the museum's basement.",
    'It made 3D scans, like a hospital CT scan, but at much higher resolution.':
        'It made three-D scans, like a hospital C.T. scan, but at much higher resolution.',
    'Today the mechanism is eighty-two fragments, and only about a third of it survives…':
        'Today the mechanism is eighty-two fragments, and only about a third of it survives,',
    '…including thirty corroded bronze gearwheels, twenty-seven of them in the largest piece.':
        'including thirty corroded bronze gear wheels, twenty-seven of them in the largest piece.',
    '…and a 365-day calendar ring that could be moved, to allow for an extra day every four years.':
        'and a three hundred and sixty-five day calendar ring that could be moved, to allow for an extra day every four years.',
    "On the front was a ring for the twelve signs of the zodiac, the Sun's path through the sky…":
        "On the front was a ring for the twelve signs of the zodiac, the Sun's path through the sky,",
    "A pin on one gear, sliding in a slot on another, made the Moon's pointer do the same…":
        "A pin on one gear, sliding in a slot on another, made the Moon's pointer do the same,",
    '…following an astronomical theory often linked to the Greek astronomer Hipparchus.':
        'following an astronomical theory often linked to the Greek astronomer Hipparkus.',
    'On the back, an upper spiral of five turns counted 235 lunar months…':
        'On the back, an upper spiral of five turns counted two hundred and thirty-five lunar months,',
    '…which fit almost exactly into nineteen years.': 'which fit almost exactly into nineteen years.',
    'A lower spiral of four turns had 223 divisions: the Saros cycle, about eighteen years of eclipses.':
        'A lower spiral of four turns had two hundred and twenty-three divisions: the Sair-oss cycle, about eighteen years of eclipses.',
    'Small symbols marked the months with eclipses…': 'Small symbols marked the months with eclipses:',
    '…sigma for the Moon, Selene, and eta for the Sun, Helios.': 'sigma for the Moon, Seh-lee-nee, and eta for the Sun, Hee-lee-oss.',
    'In 2021, a team at University College London published a new model of the front of the machine.':
        'In twenty twenty-one, a team at University College London published a new model of the front of the machine.',
    'The key was two numbers found in the inscriptions: 462 for Venus, and 442 for Saturn.':
        'The key was two numbers found in the inscriptions: four hundred and sixty-two for Venus, and four hundred and forty-two for Saturn.',
    'They match ancient cycles: Venus repeats 289 times in 462 years, and Saturn 427 times in 442 years.':
        'They match ancient cycles: Venus repeats two hundred and eighty-nine times in four hundred and sixty-two years, and Saturn, four hundred and twenty-seven times in four hundred and forty-two years.',
    'Its Corinthian calendar has led some to suggest Syracuse, in Sicily, the home of Archimedes.':
        'Its Corinthian calendar has led some to suggest Syracuse, in Sicily, the home of Arkimedees.',
    'Archimedes died in 212 BC, so he probably did not build it.':
        'Arkimedees died in two hundred and twelve B.C., so he probably did not build it.',
    'But the Roman writer Cicero credited him with a similar machine…': 'But the Roman writer Sisero credited him with a similar machine,',
    '…and some experts think the idea may go back to him.': 'and some experts think the idea may go back to him.',
    'Estimates range from the second century BC to the early first century BC.':
        'Estimates range from the second century B.C. to the early first century B.C.',
    'Whoever made it, nothing this complex is known again until the clockwork of the later Middle Ages…':
        'Whoever made it, nothing this complex is known again until the clockwork of the later Middle Ages,',
    '…more than a thousand years later.': 'more than a thousand years later.',
}


def SFX(tr, G):
    tr.waves(G('c01', 0), G('c01', 14.0), 0.2)
    tr.gurgle(G('c01', 0.4), G('c01', 4.5), 0.12)
    tr.rumble(G('c01', 0.3), G('c01', 5.0), 0.14)
    tr.wind([(0, 0.2), (G('c02', 0), 0.5), (G('c03', 0), 0.7), (G('c04', 0), 0.4), (G('c05', 0), 0.1),
             (G('c06', 0), 0.3), (G('c08', 0), 0.35), (G('c13', 0), 0.3), (G('c16', 0), 0.45), (G('c17', 0), 0.3),
             (G('c21', 0), 0.6), (G('c23', 0), 0.6), (G('c23', 15.0), 0.6), (G('c23', 16.0), 0.0)])
    tr.whoosh(G('c03', 0.0), G('c03', 5.0), 0.08, 300, 1200)
    tr.waves(G('c04', 0), G('c04', 14.0), 0.25)
    tr.gurgle(G('c04', 3.0), G('c04', 12.0), 0.08)
    tr.waves(G('c05', 0), G('c05', 13.0), 0.18)
    tr.gurgle(G('c05', 0.5), G('c05', 8.0), 0.07)
    tr.snaps(G('c06', 4.0), G('c06', 6.0), 10, 0.12)
    tr.rumble(G('c10', 0.5), G('c10', 9.0), 0.16)
    tr.snaps(G('c11', 0.3), G('c11', 2.0), 40, 0.16)
    tr.snaps(G('c13', 5.0), G('c13', 10.0), 45, 0.1)
    tr.snaps(G('c16', 5.0), G('c16', 15.0), 40, 0.07)
    tr.snaps(G('c17', 5.0), G('c17', 12.0), 30, 0.06)
    tr.rumble(G('c19', 10.0), G('c19', 14.0), 0.2)
    tr.whoosh(G('c21', 0.0), G('c21', 3.0), 0.08, 300, 1200)
    tr.rumble(G('c22', 0.3), G('c22', 4.0), 0.1)
    tr.waves(G('c23', 0), G('c23', 16.0), 0.14)

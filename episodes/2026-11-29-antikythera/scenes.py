"""Episode: The Antikythera Mechanism. Visuals: seabed, jars, bronze lump, gears, dials, maps, timeline. No living beings."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

ISLAND = (23.30, 35.87)      # Antikythera
BRONZE = (78, 104, 86)       # corroded green bronze
BRONZE_D = (52, 70, 60)
BRASS = (196, 150, 82)       # clean bronze (model)

# ---------- helpers ----------
def gear_pts(cx, cy, r, teeth, ang=0.0, depth=None):
    depth = depth or max(6, r * 0.12)
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
    ri = r * 0.72
    if spokes and r > 40:
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=bg, outline=outline, width=width)
        col = fill if fill is not None else outline
        for k in range(spokes):
            a = ang + 2 * math.pi * k / spokes
            d.line([cx, cy, cx + ri * math.cos(a), cy + ri * math.sin(a)], fill=col, width=max(6, int(r * 0.1)))
    hr = max(5, r * 0.12)
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=(fill if fill is not None else outline))

def blob(cx, cy, r, seed, n=40, rough=0.18):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 4)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rough * (0.5 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2])) + rng.uniform(-0.04, 0.04)
        pts.append((cx + r * 1.25 * k * math.cos(a), cy + r * 0.85 * k * math.sin(a)))
    return pts

def amphora(d, x, base, h, ang, col):
    """Ancient two-handled storage jar (an object), standing almost upright, tilted by ang radians."""
    w = h * 0.42
    c, s = math.cos(ang), math.sin(ang)
    def P(px, py):  # local (x right, y up) -> screen
        return (x + px * c + py * s, base + px * s - py * c)
    prof = [(0.04, 0.0), (0.10, 0.08), (0.36, 0.30), (0.50, 0.48), (0.46, 0.62), (0.30, 0.70),
            (0.13, 0.74), (0.12, 0.90), (0.20, 0.91), (0.20, 1.0)]
    right = [P(px * w, py * h) for px, py in prof]
    left = [P(-px * w, py * h) for px, py in reversed(prof)]
    dark = tuple(int(v * 0.6) for v in col)
    lw = max(5, int(h * 0.045))
    for sx in (-1, 1):  # loop handles: neck -> out -> shoulder
        d.line([P(sx * 0.12 * w, 0.88 * h), P(sx * 0.36 * w, 0.90 * h), P(sx * 0.40 * w, 0.78 * h), P(sx * 0.36 * w, 0.66 * h)],
               fill=dark, width=lw, joint='curve')
    d.polygon(right + left, fill=col, outline=dark)
    for yy in (0.40, 0.56):  # painted bands
        d.line([P(-0.47 * w, yy * h), P(0.47 * w, yy * h)], fill=dark, width=max(3, int(h * 0.02)))
    d.line([P(-0.20 * w, 1.0 * h), P(0.20 * w, 1.0 * h)], fill=dark, width=max(3, int(h * 0.025)))

def seabed(t, light=1.0):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    for i in range(0, 1150, 6):
        k = i / 1150
        d.rectangle([0, i, W, i + 6], fill=(int(8 + 6 * k * light), int(34 - 14 * k), int(58 - 22 * k)))
    d.rectangle([0, 1150, W, H], fill=(10, 14, 20))
    sand = [(x, 960 + 26 * math.sin(x / 140) + 14 * math.sin(x / 47 + 1)) for x in range(0, W + 20, 20)]
    d.polygon(sand + [(W, 1150), (0, 1150)], fill=(58, 60, 54))
    arr = to_arr(img)
    for j, x0 in enumerate((180, 430, 700, 930)):  # light shafts from the surface
        sh = 0.5 + 0.5 * math.sin(t * 0.9 + j * 1.7)
        xx = np.arange(W, dtype=np.float32)[None, :]
        yy = np.arange(1150, dtype=np.float32)[:, None]
        cx = x0 + yy * 0.25
        band = np.exp(-((xx - cx) ** 2) / (60 ** 2)) * np.clip(1 - yy / 1000, 0, 1) * 26 * sh * light
        arr[:1150] += band[..., None] * np.array([0.6, 0.9, 1.0], np.float32)
    return to_img(arr)

def particles(d, t, n=70, seed=5):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x0, y0, sp, r = rng.uniform(0, W), rng.uniform(220, 1150), rng.uniform(8, 30), rng.uniform(1.2, 3.2)
        y = 220 + (y0 - 220 - t * sp) % 930
        x = x0 + 10 * math.sin(t * 0.7 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 190, 200, 70))

LUMP = blob(540, 820, 150, 3)

# ---------- S1: hook ----------
def s1(t):
    img = seabed(t)
    d = ImageDraw.Draw(img, 'RGBA')
    amphora(d, 170, 990, 250, -0.22, (150, 98, 64))
    amphora(d, 920, 995, 220, 0.3, (140, 92, 60))
    rise = ease(ramp(t, 0.3, 4.0))
    dy = -260 * rise
    pts = [(x, y + dy) for x, y in LUMP]
    d.polygon(pts, fill=BRONZE, outline=BRONZE_D)
    for k in range(9):  # corrosion speckle
        rng = np.random.default_rng(k)
        px, py = 540 + rng.uniform(-140, 140), 820 + dy + rng.uniform(-80, 80)
        r = rng.uniform(10, 28)
        d.ellipse([px - r, py - r * 0.7, px + r, py + r * 0.7], fill=(62, 88, 72))
    a = ramp(t, 4.6, 5.4)
    if a > 0:  # glimpse of a gear inside
        cy = 820 + dy
        d.ellipse([540 - 120, cy - 105, 540 + 120, cy + 105], fill=(14, 20, 24, int(235 * a)))
        gear(d, 540, cy, 88, 24, t * 0.25, fill=None, outline=AMBER + (int(255 * a),), width=4, hub=(14, 20, 24))
    particles(d, t)
    a1 = ramp(t, 0.5, 0.9) * (1 - ramp(t, 4.2, 4.6))
    if a1 > 0:
        text_c(d, (W / 2, 330), '1901', F_BIG, WHITE + (int(255 * a1),))
    a2 = ramp(t, 5.6, 6.0)
    if a2 > 0:
        text_c(d, (W / 2, 290), "WORLD'S FIRST", F_MED, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 380), 'COMPUTER?', F_HUGE, AMBER + (int(255 * a2),))
    return img

CAPS1 = [(0.0, 4.5, 'In 1901, divers pulled a corroded bronze lump from an ancient shipwreck.', ['1901,', 'bronze', 'shipwreck.']),
         (4.5, 9.0, "Inside was a machine many call the world's first computer.", ['machine', 'first', 'computer.'])]

# ---------- S2: map ----------
def cam2(t):
    k = ease(ramp(t, 0.0, 3.4))
    s = math.exp(lerp(math.log(28), math.log(600), k))
    return Cam(lerp(20, ISLAND[0], k), lerp(38, ISLAND[1], k), s)

def island(d, cam):
    # small hand-drawn outline at Antikythera's real position (~10 km long, NW-SE)
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        u, v = 0.055 * math.cos(a), 0.022 * math.sin(a) * (1 + 0.25 * math.sin(3 * a))
        lon = ISLAND[0] + u * math.cos(-0.6) - v * math.sin(-0.6)
        lat = ISLAND[1] + u * math.sin(-0.6) + v * math.cos(-0.6)
        pts.append(tuple(float(q) for q in cam.xy(lon, lat)))
    d.polygon(pts, fill=LAND, outline=COAST)

def s2(t):
    cam = cam2(t)
    img = draw_map(Image.new('RGB', (W, H)), cam)
    d = ImageDraw.Draw(img, 'RGBA')
    island(d, cam)
    la = 1 - ramp(t, 2.0, 2.6)
    if la > 0:
        for name, lon, lat in (('GREECE', 22.0, 39.3), ('CRETE', 24.9, 35.0)):
            x, y = cam.xy(lon, lat)
            d.text((x, y), name, font=F_LABEL, fill=GREY + (int(255 * la),), anchor='mm')
    else:
        la2 = int(255 * ramp(t, 2.9, 3.3))
        x, y = cam.xy(23.75, 35.45)
        d.text((x, y), 'CRETE', font=F_LABEL, fill=GREY + (la2,), anchor='mm')
        x, y = cam.xy(22.72, 36.27)
        d.text((x, y), 'KYTHERA', font=F_LABEL, fill=GREY + (la2,), anchor='mm')
    x, y = cam.xy(*ISLAND)
    a = ramp(t, 3.2, 3.5)
    if a > 0:
        pr = 40 + 50 * ((t - 3.2) % 1.2) / 1.2
        pa = int(200 * a * (1 - ((t - 3.2) % 1.2) / 1.2))
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=AMBER + (pa,), width=4)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=AMBER + (int(255 * a),))
        text_c(d, (x, y - 150), 'ANTIKYTHERA', F_MED, WHITE + (int(255 * a),))
        text_c(d, (x, y - 95), 'the wreck site', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'ANTIKYTHERA · GREECE')
    return img

CAPS2 = [(0.0, 4.2, 'Greek sponge divers had found the wreck near the tiny island of Antikythera.', ['sponge', 'Antikythera.']),
         (4.2, 7.0, 'The ship sank in the first century BC.', ['first', 'century', 'BC.'])]

# ---------- S3: the wreck ----------
JARS = [(150, 1000, 220, -0.15), (320, 1015, 180, 0.25), (790, 1005, 230, 0.1), (960, 1020, 190, -0.3)]

def s3(t):
    img = seabed(t, 0.8)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(6):  # broken hull planks
        x0 = 120 + i * 150
        d.polygon([(x0, 1060), (x0 + 120, 1040), (x0 + 128, 1060), (x0 + 6, 1082)], fill=(70, 52, 38))
    for x, b, h, a in JARS:
        amphora(d, x, b, h, a, (146, 96, 62))
    cx, cy = 540, 880
    pts = blob(cx, cy, 70, 3)
    d.polygon(pts, fill=BRONZE, outline=BRONZE_D)
    a = ramp(t, 1.4, 1.9)
    if a > 0:
        d.rounded_rectangle([cx - 140, cy - 100, cx + 140, cy + 100], radius=14, outline=AMBER + (int(255 * a),), width=5)
        # scale bar ~ shoebox
        d.line([cx - 140, cy + 140, cx + 140, cy + 140], fill=AMBER + (int(255 * a),), width=4)
        for xx in (cx - 140, cx + 140):
            d.line([xx, cy + 125, xx, cy + 155], fill=AMBER + (int(255 * a),), width=4)
        text_c(d, (cx, cy + 190), 'ABOUT THE SIZE OF A SHOEBOX', F_LABEL, WHITE + (int(255 * a),))
    particles(d, t, seed=8)
    top_label(img, 'THE WRECK · 1ST CENTURY BC')
    return img

CAPS3 = [(0.0, 6.0, 'Among the finds: a lump about the size of a shoebox.', ['lump', 'shoebox.'])]

# ---------- S4: Athens, 1902 ----------
def s4(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    # museum display plinth
    d.rectangle([250, 960, 830, 1000], fill=(46, 54, 68))
    d.rectangle([290, 1000, 790, 1150], fill=(30, 36, 48))
    d.rectangle([250, 420, 830, 960], outline=(90, 120, 150, 120), width=3)  # glass case
    d.line([270, 440, 360, 520], fill=(160, 200, 230, 60), width=3)
    pts = blob(540, 800, 140, 3)
    d.polygon(pts, fill=BRONZE, outline=BRONZE_D)
    # magnifier reveals gearwheels
    k = ease(ramp(t, 0.8, 2.4))
    mx, my = lerp(860, 560, k), lerp(380, 780, k)
    if k > 0:
        R = 120
        d.ellipse([mx - R, my - R, mx + R, my + R], fill=(18, 26, 30))
        img2 = Image.new('RGB', (W, H), (18, 26, 30))
        d2 = ImageDraw.Draw(img2)
        gear(d2, mx - 30, my - 10, 70, 22, t * 0.2, fill=(150, 160, 120), hub=(18, 26, 30))
        gear(d2, mx + 68, my + 52, 38, 12, -t * 0.4, fill=(130, 140, 110), spokes=0)
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).ellipse([mx - R, my - R, mx + R, my + R], fill=255)
        img.paste(img2, (0, 0), m)
        d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([mx - R, my - R, mx + R, my + R], outline=(200, 205, 215), width=12)
        d.line([mx + R * 0.72, my + R * 0.72, mx + R * 1.5, my + R * 1.5], fill=(200, 205, 215), width=26)
    a = ramp(t, 2.6, 3.0)
    if a > 0:
        text_c(d, (W / 2, 300), 'GEARWHEELS', F_MED, AMBER + (int(255 * a),))
    a1 = 1 - ramp(t, 2.3, 2.6)
    if a1 > 0:
        text_c(d, (W / 2, 300), '1902', F_HUGE, WHITE + (int(255 * a1),))
    top_label(img, 'NATIONAL ARCHAEOLOGICAL MUSEUM · ATHENS')
    return img

CAPS4 = [(0.0, 6.0, 'In 1902, a visitor to the Athens museum spotted gearwheels inside.', ['1902,', 'Athens', 'gearwheels'])]

# ---------- S5: what survives ----------
rng5 = np.random.default_rng(21)
FRAGS = []
for i in range(82):
    big = i < 7
    r = rng5.uniform(42, 70) if big else rng5.uniform(9, 22)
    ang = rng5.uniform(0, 6.28); dist = rng5.uniform(120, 380) if not big else rng5.uniform(40, 220)
    FRAGS.append((540 + dist * math.cos(ang) * 1.0, 700 + dist * math.sin(ang) * 0.9, r, i))

def s5(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    k = ease(ramp(t, 0.3, 1.6))
    show_pie = ramp(t, 4.2, 4.7)
    fa = 1 - 0.75 * show_pie
    for fx, fy, r, i in FRAGS:
        x, y = lerp(540, fx, k), lerp(700, fy, k)
        pts = blob(x, y, r, 100 + i, n=14, rough=0.3)
        d.polygon(pts, fill=BRONZE + (int(255 * fa),))
        if i < 7 and r > 50:
            gear(d, x, y, r * 0.55, 14, t * 0.3 + i, fill=None, outline=(170, 180, 140, int(220 * fa)), width=3, spokes=0)
    n = int(round(82 * k))
    a = ramp(t, 0.3, 0.6) * (1 - show_pie)
    if a > 0:
        text_c(d, (W / 2, 260), f'{n} FRAGMENTS', F_MED, WHITE + (int(255 * a),))
        a2 = ramp(t, 2.0, 2.4)
        text_c(d, (W / 2, 1120), '30 BRONZE GEARS', F_MED, AMBER + (int(255 * a * a2),))
    if show_pie > 0:
        cx, cy, R = 540, 700, 300
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, int(120 * show_pie)), width=4)
        for q in range(0, 360, 12):
            if q >= 120:
                a0 = math.radians(q - 90)
                d.arc([cx - R, cy - R, cx + R, cy + R], q - 90, q - 84, fill=(255, 255, 255, int(110 * show_pie)), width=6)
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -90, -90 + 120 * ease(ramp(t, 4.3, 5.0)), fill=AMBER + (int(230 * show_pie),))
        text_c(d, (W / 2, 280), '≈ 1/3 SURVIVES', F_MED, WHITE + (int(255 * show_pie),))
        text_c(d, (cx + 150, cy + 120), 'MISSING', F_LABEL, GREY + (int(255 * show_pie),))
    top_label(img, 'WHAT SURVIVES')
    return img

CAPS5 = [(0.0, 7.0, '82 fragments and 30 bronze gears: only about a third of it survives.', ['82', '30', 'gears:', 'third'])]

# ---------- S6: X-ray CT ----------
GLYPHS = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
rng6 = np.random.default_rng(9)
LETTERS = [(rng6.uniform(250, 830), rng6.uniform(520, 1000), GLYPHS[rng6.integers(len(GLYPHS))]) for _ in range(140)]
F_TINY = font('Inter-SemiBold.otf', 24)
FRAG_A = blob(540, 760, 250, 17, n=30, rough=0.22)

def s6(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    d.polygon(FRAG_A, fill=BRONZE, outline=BRONZE_D)
    sy = lerp(380, 1150, ramp(t, 0.6, 5.0))
    # x-ray view: everything above the scan line
    xr = Image.new('RGB', (W, H), BG)
    dx = ImageDraw.Draw(xr, 'RGBA')
    dx.polygon(FRAG_A, fill=(14, 40, 60), outline=CYAN)
    gear(dx, 500, 720, 190, 56, t * 0.05, fill=None, outline=CYAN, width=3, hub=(14, 40, 60), spokes=4)
    gear(dx, 720, 900, 80, 20, -t * 0.12, fill=None, outline=CYAN, width=3, hub=(14, 40, 60), spokes=0)
    gear(dx, 330, 930, 55, 15, t * 0.2, fill=None, outline=CYAN, width=3, spokes=0)
    if t > 3.0:
        for x, y, g in LETTERS:
            dx.text((x, y), g, font=F_TINY, fill=WHITE + (int(220 * ramp(t, 3.0, 3.8)),), anchor='mm')
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rectangle([0, 0, W, int(sy)], fill=255)
    img.paste(xr, (0, 0), m)
    d = ImageDraw.Draw(img, 'RGBA')
    if t < 5.0:
        d.rectangle([60, sy - 3, W - 60, sy + 3], fill=CYAN)
        arr = to_arr(img)
        for x in range(120, W - 100, 120):
            glow(arr, x, sy, 30, (110, 210, 255), 0.25)
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 3.4, 3.8)
    if a > 0:
        d.rounded_rectangle([200, 250, 880, 360], radius=18, fill=(0, 0, 0, int(170 * a)))
        text_c(d, (W / 2, 305), 'THOUSANDS OF LETTERS', F_MED, AMBER + (int(255 * a),))
    top_label(img, 'X-RAY SCANS · 2005')
    return img

CAPS6 = [(0.0, 3.3, 'In 2005, X-ray scans looked inside.', ['2005,', 'X-ray']),
         (3.3, 7.0, 'They found thousands of tiny letters, unread for nearly two thousand years.', ['thousands', 'letters,', 'two', 'thousand'])]

# ---------- S7: what it did ----------
DC = (540, 690)
RINGS = [(95, 'MERCURY', 4.1), (135, 'VENUS', 1.6), (210, 'MARS', 0.53), (260, 'JUPITER', 0.084), (305, 'SATURN', 0.034)]

def s7(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    cx, cy = DC
    # case
    d.rounded_rectangle([cx - 380, cy - 400, cx + 380, cy + 400], radius=18, fill=(40, 30, 22), outline=(90, 66, 44), width=6)
    d.ellipse([cx - 345, cy - 345, cx + 345, cy + 345], fill=(20, 26, 36), outline=BRASS, width=6)
    # zodiac ring ticks
    for i in range(72):
        a = 2 * math.pi * i / 72
        r0 = 330 if i % 6 else 315
        d.line([cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + 342 * math.cos(a), cy + 342 * math.sin(a)], fill=BRASS, width=2)
    spin = ease(ramp(t, 0.4, 9.5)) * 9.5  # crank turns
    # planet rings
    p_on = ramp(t, 0.8, 1.6)
    for r, name, sp in RINGS:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 100, 130, int(200 * p_on)), width=2)
        a = 0.7 * sp * spin + r
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=CYAN + (int(255 * p_on),))
    # sun
    arr = to_arr(img)
    glow(arr, cx, cy, 55, (255, 170, 70), 0.9 * ramp(t, 0.3, 1.0))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=AMBER)
    # moon pointer with phase ball
    ma = spin * 1.3 - 1.0
    mr = 175
    mx, my = cx + mr * math.cos(ma), cy + mr * math.sin(ma)
    d.line([cx, cy, mx, my], fill=(200, 200, 210), width=4)
    R = 26
    d.ellipse([mx - R, my - R, mx + R, my + R], fill=(230, 230, 230))
    ph = (spin * 0.9) % (2 * math.pi)
    sx = math.cos(ph)
    d.pieslice([mx - R, my - R, mx + R, my + R], 90, 270, fill=(30, 30, 36))
    d.ellipse([mx - R * abs(sx), my - R, mx + R * abs(sx), my + R], fill=(30, 30, 36) if sx > 0 else (230, 230, 230))
    # crank on the side
    kx, ky = cx + 410, cy
    ca = spin * 4
    d.ellipse([kx - 20, ky - 20, kx + 20, ky + 20], fill=BRASS)
    hx, hy = kx + 60 * math.cos(ca), ky + 60 * math.sin(ca)
    d.line([kx, ky, hx, hy], fill=BRASS, width=10)
    d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=(160, 120, 70))
    # labels by narration
    labs = [(0.6, 'SUN · MOON · PLANETS', WHITE), (4.6, 'MOON PHASES · ECLIPSES', AMBER), (7.4, 'OLYMPIC GAMES', CYAN)]
    for i, (t0, s, c) in enumerate(labs):
        t1 = labs[i + 1][0] if i + 1 < len(labs) else 99
        a = ramp(t, t0, t0 + 0.3) * (1 - ramp(t, t1 - 0.2, t1))
        if a > 0:
            text_c(d, (W / 2, 250), s, F_MED, c + (int(255 * a),))
    # eclipse marker
    if 4.6 <= t < 7.4:
        a = ramp(t, 4.8, 5.1) * (1 - ramp(t, 7.2, 7.4))
        d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(10, 10, 14, int(220 * a)))
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=(255, 230, 180, int(255 * a)), width=5)
    top_label(img, 'WHAT IT DID')
    return img

CAPS7 = [(0.0, 4.6, 'Turn a handle, and it showed the Sun, the Moon and the planets,', ['handle,', 'Sun,', 'Moon', 'planets,']),
         (4.6, 7.4, 'the phases of the Moon, coming eclipses,', ['phases', 'eclipses,']),
         (7.4, 10.0, 'and even the dates of the Olympic Games.', ['Olympic', 'Games.'])]

# ---------- S8: the gap ----------
def s8(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    y = 760
    x0, x1 = 140, 940
    k = ease(ramp(t, 0.8, 3.6))
    d.line([x0, y, lerp(x0, x1, k), y], fill=GREY, width=6)
    for i in range(1, 12):
        xx = lerp(x0, x1, i / 12)
        if xx <= lerp(x0, x1, k):
            d.line([xx, y - 12, xx, y + 12], fill=GREY, width=3)
    gear(d, x0, y - 150, 70, 18, t * 0.4, fill=AMBER, hub=BG)
    text_c(d, (x0 + 40, y + 70), 'ANTIKYTHERA', F_SMALL, AMBER, 'mm')
    text_c(d, (x0 + 40, y + 110), 'MECHANISM', F_SMALL, AMBER, 'mm')
    a = ramp(t, 3.4, 3.9)
    if a > 0:
        gear(d, x1, y - 150, 70, 18, -t * 0.4, fill=CYAN + (int(255 * a),), hub=BG)
        text_c(d, (x1 - 40, y + 70), 'MIDDLE AGES', F_SMALL, CYAN + (int(255 * a),))
        text_c(d, (x1 - 40, y + 110), 'astronomical clocks', F_SMALL, WHITE + (int(255 * a),))
    for i in range(5):
        qx = lerp(x0, x1, 0.3 + 0.1 * i)
        qa = ramp(t, 1.0 + 0.4 * i, 1.4 + 0.4 * i)
        if qa > 0:
            text_c(d, (qx, y - 70), '?', F_MED, GREY + (int(180 * qa),))
    a2 = ramp(t, 4.0, 4.5)
    if a2 > 0:
        text_c(d, (W / 2, 330), '1,000+ YEARS', F_HUGE, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 430), 'with nothing like it', F_LABEL, GREY + (int(255 * a2),))
    top_label(img, 'A LOST TECHNOLOGY')
    return img

CAPS8 = [(0.0, 6.5, 'Nothing this complex appears again for over a thousand years.', ['complex', 'thousand', 'years.'])]

# ---------- S9: the 2021 model ----------
TRAIN = [(380, 600, 150, 40, 1), (568, 760, 95, 24, -1), (720, 600, 80, 20, 1), (700, 920, 60, 16, 1), (420, 900, 110, 30, -1)]

def s9(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    for i, (x, y, r, n, s) in enumerate(TRAIN):
        a = ease(ramp(t, 0.3 + i * 0.4, 0.8 + i * 0.4))
        if a <= 0:
            continue
        yy = lerp(y + 80, y, a)
        gear(d, x, yy, r, n, s * t * 1.2 * 40 / n, fill=BRASS + (int(255 * a),), hub=BG)
    # missing parts, dashed
    ma = ramp(t, 5.0, 5.5)
    if ma > 0:
        for (x, y, r) in ((860, 400, 90), (240, 1030, 70), (880, 1060, 60)):
            for q in range(0, 360, 20):
                d.arc([x - r, y - r, x + r, y + r], q, q + 10, fill=(255, 255, 255, int(150 * ma)), width=4)
            text_c(d, (x, y), '?', F_MED, (255, 255, 255, int(180 * ma)))
    a = ramp(t, 0.5, 0.9) * (1 - ramp(t, 4.8, 5.2))
    if a > 0:
        text_c(d, (W / 2, 290), 'A NEW MODEL', F_MED, CYAN + (int(255 * a),))
    a2 = ramp(t, 5.2, 5.6)
    if a2 > 0:
        text_c(d, (W / 2, 290), 'WHO BUILT IT?', F_MED, AMBER + (int(255 * a2),))
    top_label(img, 'UCL RECONSTRUCTION · 2021')
    return img

CAPS9 = [(0.0, 5.0, 'In 2021, a UCL team built a model they say fits all the evidence.', ['2021,', 'UCL', 'model']),
         (5.0, 8.0, 'But who built the original is still debated.', ['who', 'debated.'])]

# ---------- S10: end ----------
def s10(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    gear(d, 540, 700, 300, 64, t * 0.15, fill=(26, 34, 46), hub=BG, spokes=4)
    gear(d, 860, 1010, 110, 24, -t * 0.4, fill=(26, 34, 46), hub=BG, spokes=0)
    a = ramp(t, 0.1, 0.5)
    d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(110 * a)))
    text_c(d, (W / 2, 640), 'FOLLOW', F_HUGE, WHITE + (int(255 * a),))
    text_c(d, (W / 2, 760), 'for more unexplained history', F_MED, AMBER + (int(255 * a),))
    return img

CAPS10 = []

SCENES = [
    ('s01', s1, 9.0, CAPS1),
    ('s02', s2, 7.0, CAPS2),
    ('s03', s3, 6.0, CAPS3),
    ('s04', s4, 6.0, CAPS4),
    ('s05', s5, 7.0, CAPS5),
    ('s06', s6, 7.0, CAPS6),
    ('s07', s7, 10.0, CAPS7),
    ('s08', s8, 6.5, CAPS8),
    ('s09', s9, 8.0, CAPS9),
    ('s10', s10, 3.5, CAPS10),
]

SPOKEN = {
    'In 1901, divers pulled a corroded bronze lump from an ancient shipwreck.': 'In nineteen oh one, divers pulled a corroded bronze lump from an ancient shipwreck.',
    'Greek sponge divers had found the wreck near the tiny island of Antikythera.': 'Greek sponge divers had found the wreck near the tiny island of Anti-kithera.',
    'The ship sank in the first century BC.': 'The ship sank in the first century B.C.',
    'In 1902, a visitor to the Athens museum spotted gearwheels inside.': 'In nineteen oh two, a visitor to the Athens museum spotted gear wheels inside.',
    '82 fragments and 30 bronze gears: only about a third of it survives.': 'Eighty-two fragments and thirty bronze gears. Only about a third of it survives.',
    'In 2005, X-ray scans looked inside.': 'In two thousand five, X-ray scans looked inside.',
    'In 2021, a UCL team built a model they say fits all the evidence.': 'In twenty twenty-one, a U.C.L. team built a model they say fits all the evidence.',
}


def SFX(tr, G):
    tr.wind([(0, 0.0), (G('s02', 0), 0.0), (G('s02', 0.1), 0.6), (G('s03', 0), 0.0), (G('s04', 0), 0.3),
             (G('s07', 0), 0.35), (G('s09', 0), 0.4), (G('s10', 0), 0.5), (G('s10', 3.5), 0.0)])
    tr.waves(G('s01', 0), G('s02', 0.3), 0.22)
    tr.gurgle(G('s01', 0.3), G('s01', 4.0), 0.12)
    tr.rumble(G('s01', 0.2), G('s01', 5.0), 0.15)
    tr.waves(G('s02', 0), G('s03', 0), 0.18)
    tr.waves(G('s03', 0), G('s04', 0.2), 0.2)
    tr.gurgle(G('s03', 0.5), G('s03', 5.0), 0.08)
    tr.snaps(G('s05', 0.3), G('s05', 1.6), 30, 0.18)
    tr.rumble(G('s05', 0.2), G('s05', 2.5), 0.12)
    tr.whoosh(G('s06', 0.6), G('s06', 5.0), 0.06, 200, 900)
    tr.rumble(G('s08', 0.5), G('s08', 5.0), 0.1)
    tr.waves(G('s10', 0), G('s10', 3.5), 0.15)

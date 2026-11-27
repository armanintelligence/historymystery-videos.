"""Episode: Lonar Crater, India. Visuals: a crater lake from above, maps, cross-sections, lava layers,
a volcano shape, a rock sample, an impact diagram, the Moon, a timeline, rain. No people, animals or birds."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

LONAR = (76.508, 19.976)
GREEN_L = (48, 112, 78)
PINK_L = (226, 112, 150)
RED_X = (255, 90, 70)


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def sky(d, top=(4, 6, 13), bot=(12, 20, 40), ymax=1150):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=mix(top, bot, k))


# ---------- crater seen from above ----------
_rng = np.random.default_rng(5)
SCRUB = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(3, 9)) for _ in range(900)]
SLOPE = []
while len(SLOPE) < 700:
    a = _rng.uniform(0, 2 * math.pi); r = _rng.uniform(0.80, 1.02)
    SLOPE.append((a, r, _rng.uniform(4, 10), _rng.uniform(0, 1)))


def crater_top(img, cx, cy, R, lake, t=0.0, shimmer=0.0):
    """Lonar from above: scrubland, ejecta, rim, wooded inner slope, oval lake."""
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, H], fill=(62, 54, 38))
    for x, y, r in SCRUB:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(74, 72, 44, 150))
    d.ellipse([cx - R * 1.5, cy - R * 1.42, cx + R * 1.5, cy + R * 1.42], fill=(78, 66, 46))
    d.ellipse([cx - R * 1.12, cy - R * 1.06, cx + R * 1.12, cy + R * 1.06], fill=(112, 96, 68))
    for i in range(10):
        k = i / 10
        rr = lerp(1.02, 0.72, k)
        d.ellipse([cx - R * rr, cy - R * rr * 0.95, cx + R * rr, cy + R * rr * 0.95], fill=mix((84, 74, 50), (44, 70, 42), k))
    for a, r, s, g in SLOPE:
        x = cx + math.cos(a) * R * r * 0.92
        y = cy + math.sin(a) * R * r * 0.88
        d.ellipse([x - s, y - s, x + s, y + s], fill=(int(36 + 20 * g), int(80 + 30 * g), int(40 + 10 * g)))
    lw, lh = R * 0.74, R * 0.66
    d.ellipse([cx - lw - 10, cy - lh - 10, cx + lw + 10, cy + lh + 10], fill=(150, 140, 110))
    d.ellipse([cx - lw, cy - lh, cx + lw, cy + lh], fill=lake)
    if shimmer > 0:
        for j in range(26):
            a = j * 2.4 + t * 0.3
            x = cx + math.cos(a) * lw * 0.75 * ((j * 37 % 10) / 10)
            y = cy + math.sin(a) * lh * 0.75 * ((j * 53 % 10) / 10)
            w_ = 30 + 20 * math.sin(t * 2 + j)
            d.line([x - w_, y, x + w_, y], fill=(255, 255, 255, int(40 * shimmer)), width=3)
    return img


def fade_bottom(img, y0=1180, y1=1290):
    d = ImageDraw.Draw(img, 'RGBA')
    for y in range(y0, y1, 4):
        d.rectangle([0, y, W, y + 4], fill=BG + (int(255 * (y - y0) / (y1 - y0)),))
    d.rectangle([0, y1, W, H], fill=BG)


# ---------- S1: hook ----------
def s1(t):
    k = ease(ramp(t, 1.2, 3.6))
    img = Image.new('RGB', (W, H), BG)
    crater_top(img, 540, 690, 400, mix(GREEN_L, PINK_L, k), t, 1.0)
    fade_bottom(img)
    d = ImageDraw.Draw(img, 'RGBA')
    a1 = 1 - ramp(t, 1.6, 2.0)
    a2 = ramp(t, 2.0, 2.4)
    d.rounded_rectangle([340, 250, 740, 330], radius=16, fill=(0, 0, 0, 150))
    if a1 > 0:
        text_c(d, (540, 290), '25 MAY 2020', F_LABEL, CYAN + (int(255 * a1),))
    if a2 > 0:
        text_c(d, (540, 290), '10 JUNE 2020', F_LABEL, (255, 150, 190, int(255 * a2)))
    a3 = ramp(t, 4.4, 4.8)
    if a3 > 0:
        d.rounded_rectangle([200, 1040, 880, 1130], radius=18, fill=(0, 0, 0, int(170 * a3)))
        text_c(d, (540, 1085), 'WHAT MADE THIS HOLE?', F_MED, AMBER + (int(255 * a3),))
    top_label(img, 'LONAR LAKE · INDIA', ramp(t, 0.1, 0.5))
    return img

CAPS1 = [(0.0, 4.3, 'In 2020, a lake in India turned pink in days.', ['pink', 'days.']),
         (4.3, 7.5, 'But the hole it sits in is stranger.', ['hole', 'stranger.'])]


# ---------- S2: map zoom ----------
def cam2(t):
    k = ease(ramp(t, 0.2, 3.0))
    s = math.exp(lerp(math.log(36), math.log(420), k))
    return Cam(lerp(79.5, LONAR[0], k), lerp(22.5, LONAR[1], k), s)


def land_only(cam, land=(44, 52, 46), coast=(90, 110, 120)):
    """Coastlines only: inland lakes are left out (small lake shapes can read as silhouettes)."""
    img = Image.new('RGB', (W, H), WATER)
    d = ImageDraw.Draw(img)
    res = 'i' if cam.s >= 35 else 'l'
    for p in GEO[res]['land']:
        if p[:, 0].max() < 55 or p[:, 0].min() > 100 or p[:, 1].max() < 0 or p[:, 1].min() > 45:
            continue
        x, y = cam.xy(p[:, 0], p[:, 1])
        pts = list(zip(x.tolist(), y.tolist()))
        if len(pts) > 2:
            d.polygon(pts, fill=land, outline=coast)
    return img


def s2(t):
    cam = cam2(t)
    img = land_only(cam)
    d = ImageDraw.Draw(img, 'RGBA')
    a0 = 1 - ramp(t, 0.9, 1.4)
    if a0 > 0:
        text_c(d, (560, 620), 'INDIA', F_MED, WHITE + (int(200 * a0),))
    x, y = cam.xy(*LONAR)
    a = ramp(t, 2.6, 3.0)
    if a > 0:
        pr = 30 + 40 * ((t - 2.6) % 1.2) / 1.2
        pa = int(200 * a * (1 - ((t - 2.6) % 1.2) / 1.2))
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=AMBER + (pa,), width=4)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=AMBER + (int(255 * a),))
        d.text((x, y - 50), 'LONAR', font=F_MED, fill=WHITE + (int(255 * a),), anchor='ms')
        d.text((x, y + 60), 'Buldhana district', font=F_SMALL, fill=GREY + (int(255 * a),), anchor='mt')
    top_label(img, 'MAHARASHTRA · INDIA')
    return img

CAPS2 = [(0.0, 4.5, 'This is Lonar, in Maharashtra: a near-perfect bowl.', ['Lonar,', 'Maharashtra:', 'bowl.'])]


# ---------- S3: cross-section ----------
GY3, CX3, HW3 = 640, 540, 400
D3 = HW3 * 2 / 1880 * 150 * 3      # depth, vertical scale x3


def prof3(x):
    u = (x - CX3) / HW3
    if abs(u) < 1:
        return GY3 - 26 + (D3 + 26) * (1 - u * u) ** 1.2
    return GY3 - 26 * math.exp(-(abs(u) - 1) * 5)


def s3(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, ymax=GY3 + 40)
    xs = list(range(0, W + 1, 6))
    top = [(x, prof3(x)) for x in xs]
    d.polygon(top + [(W, 1150), (0, 1150)], fill=(46, 48, 54))
    for i, col in enumerate([(56, 58, 64), (40, 42, 48), (52, 52, 58), (36, 38, 44)]):
        d.rectangle([0, 960 + i * 48, W, 1008 + i * 48], fill=col)
    d.polygon(top + [(W, 1150), (0, 1150)], outline=(90, 92, 100))
    d.line(top, fill=(120, 104, 74), width=8)
    # lake at the bottom
    lvl = GY3 + D3 - 34
    lake = [(x, y) for x, y in top if y > lvl]
    if len(lake) > 2:
        d.polygon([(lake[0][0], lvl)] + lake + [(lake[-1][0], lvl)], fill=GREEN_L)
    fade_bottom(img, 1110, 1200)
    a = ease(ramp(t, 0.3, 1.4))
    if a > 0:
        yy = GY3 - 90
        L = HW3 * a
        d.line([CX3 - L, yy, CX3 + L, yy], fill=AMBER, width=6)
        for sx in (-1, 1):
            ex = CX3 + sx * L
            d.polygon([(ex, yy), (ex - sx * 22, yy - 13), (ex - sx * 22, yy + 13)], fill=AMBER)
        text_c(d, (CX3, yy - 60), '1.88 km', F_MED, AMBER + (int(255 * ramp(t, 1.0, 1.4)),))
    b = ease(ramp(t, 3.0, 3.8))
    if b > 0:
        x = CX3
        y0, y1 = GY3, GY3 + D3
        d.line([x, y0, x, lerp(y0, y1, b)], fill=CYAN, width=6)
        d.line([x - 20, y0, x + 20, y0], fill=CYAN, width=4)
        if b >= 1:
            d.line([x - 20, y1, x + 20, y1], fill=CYAN, width=4)
        d.text((x + 34, (y0 + y1) / 2 - 20), '≈150 m', font=F_MED, fill=CYAN + (int(255 * ramp(t, 3.4, 3.8)),), anchor='lm')
    d.text((W - 50, 1120), 'depth shown ×3', font=F_SMALL, fill=GREY, anchor='rm')
    top_label(img, 'CROSS-SECTION')
    return img

CAPS3 = [(0.0, 6.5, 'It is 1.88 kilometres across, and about 150 metres deep.', ['1.88', 'kilometres', '150', 'metres'])]


# ---------- S4: lava layers ----------
NL4 = 8
LH4 = 66


def s4(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, (6, 8, 14), (30, 18, 16), 1150)
    base = 1120
    n = 1 + int(min(t / 0.6, NL4 - 1))
    arr = None
    for i in range(n):
        y1 = base - i * LH4
        y0 = y1 - LH4
        tt = t - i * 0.6
        heat = math.exp(-max(tt, 0) * 1.1)
        grey = 44 + (i % 2) * 10
        col = mix((grey, grey + 2, grey + 8), (255, 110, 40), heat)
        rng = np.random.default_rng(i)
        wav = [(x, y0 + 6 * math.sin(x / 90 + i * 1.7) + rng.uniform(-3, 3)) for x in range(0, W + 1, 30)]
        flow = ease(ramp(tt, 0, 0.5))
        xr = W * flow
        poly = [(x, y) for x, y in wav if x <= xr] + [(xr, y1), (0, y1)]
        if len(poly) > 2:
            d.polygon(poly, fill=col)
            d.line([(x, y) for x, y in wav if x <= xr], fill=mix((70, 70, 78), (255, 200, 120), heat), width=3)
    img2 = img
    arr = to_arr(img2)
    if n >= 1:
        i = n - 1
        tt = t - i * 0.6
        h = math.exp(-max(tt, 0) * 1.1)
        glow(arr, 540, base - n * LH4 + 10, 380, (255, 100, 30), 0.35 * h)
    img = to_img(arr)
    fade_bottom(img, 1130, 1200)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 4.6, 5.0)
    if a > 0:
        d.rounded_rectangle([160, 270, 920, 420], radius=20, fill=(0, 0, 0, int(160 * a)))
        text_c(d, (540, 320), 'DECCAN TRAPS', F_MED, AMBER + (int(255 * a),))
        text_c(d, (540, 385), 'layer upon layer of lava rock', F_LABEL, WHITE + (int(255 * a),))
    top_label(img, '≈65 MILLION YEARS AGO')
    return img

CAPS4 = [(0.0, 6.5, 'The ground here is basalt: lava from eruptions about 65 million years ago.', ['basalt:', 'lava', '65', 'million'])]


# ---------- S5: the volcano idea ----------
def s5(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, ymax=1100)
    d.rectangle([0, 1040, W, 1150], fill=(40, 42, 48))
    k = ease(ramp(t, 0.1, 1.0))
    peak = lerp(1040, 520, k)
    cone = [(140, 1040), (430, peak), (470, peak + 26), (610, peak + 26), (650, peak), (940, 1040)]
    d.polygon(cone, fill=(58, 54, 56))
    d.line(cone, fill=(96, 90, 92), width=4)
    a = ramp(t, 1.2, 1.6)
    if a > 0:
        text_c(d, (540, 340), 'A VOLCANO?', F_MED, WHITE + (int(255 * a),))
    b = ramp(t, 3.4, 3.7)
    if b > 0:
        c = RED_X + (int(255 * b),)
        d.line([300, 560, 780, 1020], fill=c, width=16)
        d.line([300, 1020, 780, 560], fill=c, width=16)
    fade_bottom(img, 1130, 1200)
    top_label(img, 'THE FIRST GUESS')
    return img

CAPS5 = [(0.0, 5.0, 'So at first, scientists thought the bowl was a volcano.', ['volcano.'])]


# ---------- S6: maskelynite ----------
_r6 = np.random.default_rng(9)
GRAINS = [(_r6.uniform(-320, 320), _r6.uniform(-320, 320), _r6.uniform(18, 46), _r6.uniform(0, 6.28), int(_r6.uniform(36, 80))) for _ in range(260)]
GLASS = [(-120, -60, 60), (90, 40, 70), (-40, 140, 50), (150, -150, 46)]


def s6(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    cx, cy, R = 540, 700, 340
    k = ease(ramp(t, 0.2, 1.0))
    r = R * k
    if r > 4:
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        tex = Image.new('RGB', (W, H), (40, 40, 46))
        dt = ImageDraw.Draw(tex)
        for gx, gy, s, a, g in GRAINS:
            pts = [(cx + gx + s * math.cos(a + j * 2.1), cy + gy + s * math.sin(a + j * 2.1) * 0.8) for j in range(3)]
            dt.polygon(pts, fill=(g, g, g + 6))
        sh = ramp(t, 2.6, 3.4)
        arr = to_arr(tex)
        for i, (gx, gy, s) in enumerate(GLASS):
            if sh > 0:
                pts = [(cx + gx + s * math.cos(0.6 + j * 1.25), cy + gy + s * math.sin(0.6 + j * 1.25)) for j in range(5)]
                ImageDraw.Draw(tex).polygon(pts, fill=mix((70, 70, 76), (170, 230, 255), sh))
        arr = to_arr(tex)
        if sh > 0:
            for i, (gx, gy, s) in enumerate(GLASS):
                tw = 0.6 + 0.4 * math.sin(t * 4 + i * 2)
                glow(arr, cx + gx, cy + gy, s * 0.9, (120, 210, 255), 0.7 * sh * tw)
        tex = to_img(arr)
        img.paste(tex, (0, 0), m)
        d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(200, 205, 215), width=10)
        hx, hy = cx + r * 0.72, cy + r * 0.72
        d.line([hx, hy, hx + 150 * k, hy + 150 * k], fill=(200, 205, 215), width=30)
    a = ramp(t, 3.0, 3.4)
    if a > 0:
        d.rounded_rectangle([250, 245, 830, 335], radius=18, fill=(0, 0, 0, int(170 * a)))
        text_c(d, (540, 290), 'MASKELYNITE', F_MED, CYAN + (int(255 * a),))
    b = ramp(t, 4.4, 4.8)
    if b > 0:
        text_c(d, (540, 1110), 'forms only in high-speed impacts', F_LABEL, AMBER + (int(255 * b),))
    top_label(img, '1970s · THE CLUE')
    return img

CAPS6 = [(0.0, 3.4, 'In the 1970s, scientists found maskelynite,', ['1970s,', 'maskelynite,']),
         (3.4, 7.0, 'a glass made only by high-speed impacts.', ['glass', 'high-speed', 'impacts.'])]


# ---------- S7: the impact ----------
GY7 = 800
_r7 = np.random.default_rng(3)
EJ = [(_r7.uniform(0.25, 2.9), _r7.uniform(380, 900), _r7.uniform(4, 10)) for _ in range(150)]


def prof7(x, k):
    u = (x - 540) / 300
    rim = 24 * k * math.exp(-max(abs(u) - 1, 0) * 4) if abs(u) >= 1 else 24 * k
    if abs(u) < 1:
        return GY7 - rim + (190 * k + rim) * (1 - u * u) ** 1.2
    return GY7 - rim


def s7(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, (4, 6, 13), (14, 24, 44), GY7 + 60)
    k = ease(ramp(t, 1.9, 2.6))
    top = [(x, prof7(x, k)) for x in range(0, W + 1, 6)]
    d.polygon(top + [(W, 1150), (0, 1150)], fill=(48, 50, 56))
    for i, col in enumerate([(56, 58, 64), (40, 42, 48), (52, 52, 58)]):
        d.rectangle([0, 1000 + i * 50, W, 1050 + i * 50], fill=col)
    d.line(top, fill=(90, 92, 100), width=5)
    arr = to_arr(img)
    A, B = (1060, 200), (540, GY7)
    if 0.3 <= t < 1.9:
        e = ramp(t, 0.3, 1.9) ** 1.4
        for j in range(24):
            q = max(e - j * 0.025, 0)
            glow(arr, lerp(A[0], B[0], q), lerp(A[1], B[1], q), 18 - j * 0.55, (255, 140, 50), 0.5 * (1 - j / 24))
        glow(arr, lerp(A[0], B[0], e), lerp(A[1], B[1], e), 32, (255, 210, 140), 1.2)
    if t >= 1.9:
        f = math.exp(-(t - 1.9) * 1.8)
        glow(arr, 540, GY7, 300, (255, 140, 50), 2.2 * f)
        glow(arr, 540, GY7, 90, (255, 250, 220), 3.0 * f)
        te = t - 1.9
        for i, (ang, v, s) in enumerate(EJ):
            px = 540 + math.cos(ang) * v * te
            py = GY7 - math.sin(ang) * v * te + 0.5 * 900 * te * te
            if py < prof7(px, k) and 0 < px < W:
                glow(arr, px, py, s, (255, 160, 80), 0.9 * math.exp(-te * 0.8))
    img = to_img(arr)
    fade_bottom(img, 1130, 1200)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 3.4, 3.8)
    if a > 0:
        text_c(d, (540, 330), 'A ROCK FROM SPACE', F_MED, AMBER + (int(255 * a),))
        text_c(d, (540, 400), 'into solid lava rock', F_LABEL, WHITE + (int(255 * a),))
    top_label(img, 'THE IMPACT')
    return img

CAPS7 = [(0.0, 5.5, 'A rock from space had slammed into solid lava rock.', ['rock', 'space', 'slammed'])]


# ---------- S8: the Moon ----------
_r8 = np.random.default_rng(12)
MOONC = [(_r8.uniform(-0.8, 0.8), _r8.uniform(-0.8, 0.8), _r8.uniform(0.03, 0.12)) for _ in range(40)]


def s8(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    draw_stars(d, t, 0.8, ymax=1150)
    a = ramp(t, 0.2, 0.7)
    d.rounded_rectangle([110, 240, 970, 420], radius=22, fill=(0, 0, 0, int(160 * a)))
    text_c(d, (540, 300), "EARTH'S ONLY FRESH IMPACT", F_LABEL, WHITE + (int(255 * a),))
    text_c(d, (540, 360), 'CRATER IN BASALT', F_MED, AMBER + (int(255 * a),))
    k = ease(ramp(t, 2.6, 3.6))
    if k > 0:
        cx, cy, R = 540, 770, 300 * k
        arr = to_arr(img)
        glow(arr, cx, cy, R * 1.1, (120, 130, 150), 0.35)
        img = to_img(arr)
        d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(150, 150, 158))
        for mx, my, mr in MOONC:
            if mx * mx + my * my < 0.75:
                x, y, r = cx + mx * R, cy + my * R, mr * R
                d.ellipse([x - r, y - r, x + r, y + r], fill=(118, 118, 128), outline=(185, 185, 192), width=max(1, int(r * 0.15)))
        for mx, my, mr in ((-0.3, -0.25, 0.35), (0.25, 0.2, 0.28)):
            x, y, r = cx + mx * R, cy + my * R, mr * R
            d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(100, 100, 112, 150))
        b = ramp(t, 3.6, 4.0)
        text_c(d, (540, 1120), 'A STAND-IN FOR THE MOON', F_LABEL, CYAN + (int(255 * b),))
    top_label(img, 'WHY IT MATTERS')
    return img

CAPS8 = [(0.0, 3.0, "It's Earth's only fresh impact crater in basalt,", ['only', 'fresh', 'basalt,']),
         (3.0, 6.0, "a stand-in for the Moon's craters.", ["Moon's"])]


# ---------- S9: how old? ----------
X0, X1, AY = 120, 960, 760


def ax(years):
    return X0 + (X1 - X0) * years / 700000


def s9(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    k = ease(ramp(t, 0.1, 1.0))
    d.line([X0, AY, lerp(X0, X1, k), AY], fill=GREY, width=6)
    for yrs in range(0, 700001, 100000):
        x = ax(yrs)
        if x <= lerp(X0, X1, k):
            d.line([x, AY - 14, x, AY + 14], fill=GREY, width=3)
    if k >= 1:
        d.text((X0, AY + 30), 'NOW', font=F_SMALL, fill=GREY, anchor='mt')
        d.text((X1, AY + 30), '700,000', font=F_SMALL, fill=GREY, anchor='mt')
        d.text((540, AY + 80), 'YEARS AGO', font=F_SMALL, fill=GREY, anchor='mt')

    def marker(yrs, t0, label, sub, col, up):
        a = ramp(t, t0, t0 + 0.3)
        if a <= 0:
            return
        x = ax(yrs)
        pr = 22 + 26 * ((t - t0) % 1.2) / 1.2
        d.ellipse([x - pr, AY - pr, x + pr, AY + pr], outline=col + (int(180 * a * (1 - ((t - t0) % 1.2) / 1.2)),), width=4)
        d.ellipse([x - 16, AY - 16, x + 16, AY + 16], fill=col + (int(255 * a),))
        ly = AY - 200 if up else AY + 160
        d.line([x, AY - 20 if up else AY + 20, x, ly + (60 if up else -10)], fill=col + (int(255 * a),), width=4)
        anc = 'l' if x < 540 else 'r'
        tx = x - 20 if anc == 'l' else x + 20
        d.text((tx, ly), label, font=F_MED, fill=col + (int(255 * a),), anchor=anc + 's')
        d.text((tx, ly + 14), sub, font=F_SMALL, fill=WHITE + (int(255 * a),), anchor=anc + 't')

    marker(37500, 0.6, '≈37,500', 'rock-surface dating', CYAN, True)
    marker(570000, 3.4, '≈570,000', 'argon dating, 2011', AMBER, False)
    a = ramp(t, 5.6, 6.0)
    if a > 0:
        d.rounded_rectangle([220, 360, 860, 470], radius=20, outline=RED_X + (int(255 * a),), width=6)
        text_c(d, (540, 415), 'STILL DEBATED', F_MED, RED_X + (int(255 * a),))
    top_label(img, 'HOW OLD IS IT?')
    return img

CAPS9 = [(0.0, 3.3, 'One study says 37,500 years ago.', ['37,500']),
         (3.3, 8.0, 'Another says 570,000. Still debated.', ['570,000.', 'debated.'])]


# ---------- S10: the pink explained + end ----------
_r10 = np.random.default_rng(21)
RAIN = [(_r10.uniform(0, W + 300), _r10.uniform(0, H), _r10.uniform(0.7, 1.3)) for _ in range(260)]


def s10(t):
    back = ease(ramp(t, 7.2, 9.4))
    lake = mix(PINK_L, GREEN_L, back)
    img = Image.new('RGB', (W, H), BG)
    crater_top(img, 540, 720, 330, lake, t, 0.6)
    fade_bottom(img)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.6, 1.0) * (1 - ramp(t, 6.8, 7.2))
    if a > 0:
        d.rounded_rectangle([170, 230, 910, 380], radius=20, fill=(0, 0, 0, int(170 * a)))
        text_c(d, (540, 285), 'HALOARCHAEA', F_MED, (255, 150, 190, int(255 * a)))
        text_c(d, (540, 345), 'salt-loving microbes', F_LABEL, WHITE + (int(255 * a),))
    b = ramp(t, 4.0, 4.4) * (1 - ramp(t, 6.8, 7.2))
    if b > 0:
        for i, s in enumerate(('SALT  ▲', 'pH  ▲')):
            x = 330 + i * 420
            d.rounded_rectangle([x - 150, 1070, x + 150, 1150], radius=16, fill=(0, 0, 0, int(170 * b)))
            text_c(d, (x, 1110), s, F_MED, AMBER + (int(255 * b),))
    r = ramp(t, 6.8, 7.3) * (1 - ramp(t, 9.8, 10.2))
    if r > 0:
        for x, y, s in RAIN:
            yy = (y + t * 1400 * s) % 1200
            xx = x - yy * 0.25
            d.line([xx, yy, xx - 10 * s, yy + 44 * s], fill=(180, 210, 240, int(150 * r)), width=3)
        text_c(d, (540, 300), 'MONSOON RAIN', F_MED, CYAN + (int(255 * r),))
    top_label(img, 'SO WHY PINK?', 1 - ramp(t, 9.8, 10.2))
    a2 = ramp(t, 10.0, 10.4)
    if a2 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(160 * a2)))
        text_c(d, (W / 2, 600), 'FOLLOW', F_HUGE, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 720), 'for more unexplained history', F_MED, AMBER + (int(255 * a2),))
    return img

CAPS10 = [(0.0, 3.8, 'The pink? Salt-loving microbes called haloarchaea,', ['pink?', 'haloarchaea,']),
          (3.8, 6.8, 'blooming as salt and alkalinity rose.', ['salt', 'alkalinity']),
          (6.8, 10.0, 'Monsoon rain diluted the lake, and it turned green again.', ['Monsoon', 'green'])]


SCENES = [
    ('s01', s1, 7.5, CAPS1),
    ('s02', s2, 4.5, CAPS2),
    ('s03', s3, 6.5, CAPS3),
    ('s04', s4, 6.5, CAPS4),
    ('s05', s5, 5.0, CAPS5),
    ('s06', s6, 7.0, CAPS6),
    ('s07', s7, 5.5, CAPS7),
    ('s08', s8, 6.0, CAPS8),
    ('s09', s9, 8.0, CAPS9),
    ('s10', s10, 11.5, CAPS10),
]


SPOKEN = {
    'In 2020, a lake in India turned pink in days.': 'In twenty twenty, a lake in India turned pink, in days.',
    'It is 1.88 kilometres across, and about 150 metres deep.': 'It is one point eight eight kilometres across, and about a hundred and fifty metres deep.',
    'The ground here is basalt: lava from eruptions about 65 million years ago.': 'The ground here is basalt. Lava, from eruptions about sixty-five million years ago.',
    'In the 1970s, scientists found maskelynite,': 'In the nineteen seventies, scientists found maskelynite,',
    'One study says 37,500 years ago.': 'One study says thirty-seven thousand five hundred years ago.',
    'Another says 570,000. Still debated.': 'Another says five hundred and seventy thousand. Still debated.',
    'The pink? Salt-loving microbes called haloarchaea,': 'The pink? Salt-loving microbes, called halo-ar-kee-a,',
}


def SFX(tr, G):
    tr.wind([(0, 0.8), (G('s02', 0), 0.4), (G('s04', 0), 0.3), (G('s05', 0), 0.6), (G('s06', 0), 0.3),
             (G('s08', 0), 0.6), (G('s09', 0), 0.4), (G('s10', 0), 0.7), (G('s10', 11.0), 0.6), (G('s10', 11.5), 0.0)])
    tr.waves(G('s01', 0), G('s01', 7.5), 0.12)
    tr.whoosh(G('s02', 0.3), G('s02', 4.2), 0.06, 300, 1200)
    tr.rumble(G('s04', 0.0), G('s04', 6.0), 0.22)
    tr.crackle(G('s04', 0.0), G('s04', 4.6), 0.12)
    tr.whoosh(G('s07', 0.3), G('s07', 1.9), 0.25)
    tr.boom(G('s07', 1.9), 0.95)
    tr.rumble(G('s07', 2.0), G('s07', 5.4), 0.25)
    tr.snaps(G('s07', 2.0), G('s07', 3.6), 30, 0.12)
    tr.waves(G('s10', 0), G('s10', 6.8), 0.10)
    tr.crackle(G('s10', 6.8), G('s10', 10.0), 0.10)   # light hiss of rain
    tr.gurgle(G('s10', 7.2), G('s10', 9.6), 0.10)

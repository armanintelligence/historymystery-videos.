"""Long video: Lonar Crater, India, full story (1920x1080). Build with HM_FORMAT=long.
Visuals: the crater from above, maps, cross-sections, lava layers, a volcano shape, a drill rig, rock cores,
a rock sample, the impact, the Moon, a timeline, satellite frames, sample bottles, gauges, rain.
No people, animals, birds or any other living being (no microbes drawn either: the pink is shown as colour only)."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

assert W == 1920, 'build with HM_FORMAT=long'
LONAR = (76.508, 19.976)
GREEN_L = (48, 112, 78)
PINK_L = (226, 112, 150)
PINK_T = (255, 150, 190)
RED = (255, 90, 70)
F_TITLE = font('InterDisplay-Black.otf', 150)
VB = 830  # bottom of the visual area (captions sit below)


def new(bg=BG):
    img = Image.new('RGB', (W, H), bg)
    return img, ImageDraw.Draw(img, 'RGBA')


def A(c, a):
    return c + (int(255 * max(0, min(1, a))),)


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def sky(d, top=(4, 6, 13), bot=(14, 24, 51), ymax=H):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=mix(top, bot, k))


def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0, int(170 * a)))


# ---------- the crater seen from above ----------
_rng = np.random.default_rng(5)
SCRUB = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(3, 9)) for _ in range(1400)]
SLOPE = []
while len(SLOPE) < 800:
    a_ = _rng.uniform(0, 2 * math.pi); r_ = _rng.uniform(0.80, 1.02)
    SLOPE.append((a_, r_, _rng.uniform(4, 10), _rng.uniform(0, 1)))


def crater_top(img, cx, cy, R, lake, t=0.0, shimmer=0.0, ejecta=1.0):
    """Lonar from above: scrubland, ejecta, rim, wooded inner slope (plants), oval lake."""
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, H], fill=(62, 54, 38))
    for x, y, r in SCRUB:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(74, 72, 44, 150))
    if ejecta > 0:
        d.ellipse([cx - R * 1.5, cy - R * 1.42, cx + R * 1.5, cy + R * 1.42], fill=A((78, 66, 46), ejecta))
    d.ellipse([cx - R * 1.12, cy - R * 1.06, cx + R * 1.12, cy + R * 1.06], fill=(112, 96, 68))
    for i in range(10):
        k = i / 10
        rr = lerp(1.02, 0.72, k)
        d.ellipse([cx - R * rr, cy - R * rr * 0.95, cx + R * rr, cy + R * rr * 0.95], fill=mix((84, 74, 50), (44, 70, 42), k))
    for a, r, s, g in SLOPE:
        x = cx + math.cos(a) * R * r * 0.92
        y = cy + math.sin(a) * R * r * 0.88
        s2 = s * R / 400
        d.ellipse([x - s2, y - s2, x + s2, y + s2], fill=(int(36 + 20 * g), int(80 + 30 * g), int(40 + 10 * g)))
    lw, lh = R * 0.74, R * 0.66
    d.ellipse([cx - lw - 10, cy - lh - 10, cx + lw + 10, cy + lh + 10], fill=(150, 140, 110))
    d.ellipse([cx - lw, cy - lh, cx + lw, cy + lh], fill=lake)
    if shimmer > 0:
        for j in range(30):
            a = j * 2.4 + t * 0.3
            x = cx + math.cos(a) * lw * 0.75 * ((j * 37 % 10) / 10)
            y = cy + math.sin(a) * lh * 0.75 * ((j * 53 % 10) / 10)
            w_ = (30 + 20 * math.sin(t * 2 + j)) * R / 400
            d.line([x - w_, y, x + w_, y], fill=(255, 255, 255, int(40 * shimmer)), width=3)
    return img


def land_only(cam, land=(44, 52, 46), coast=(90, 110, 120)):
    """Coastlines only: inland lakes are left out (small lake shapes can read as silhouettes)."""
    img = Image.new('RGB', (W, H), WATER)
    d = ImageDraw.Draw(img)
    res = 'i' if cam.s >= 35 else 'l'
    for p in GEO[res]['land']:
        if p[:, 0].max() < 40 or p[:, 0].min() > 115 or p[:, 1].max() < -5 or p[:, 1].min() > 45:
            continue
        x, y = cam.xy(p[:, 0], p[:, 1])
        pts = list(zip(x.tolist(), y.tolist()))
        if len(pts) > 2:
            d.polygon(pts, fill=land, outline=coast)
    return img


# ---------- 1. cold open ----------
def c01(t):
    k = ease(ramp(t, 5.0, 8.0))
    img = Image.new('RGB', (W, H), BG)
    crater_top(img, 960, 470, 330, mix(GREEN_L, PINK_L, k), t, 1.0)
    d = ImageDraw.Draw(img, 'RGBA')
    a1 = ramp(t, 4.0, 4.4) * (1 - ramp(t, 6.0, 6.4))
    a2 = ramp(t, 6.4, 6.8)
    if a1 + a2 > 0:
        card(d, 1430, 150, 1840, 250, max(a1, a2))
        if a1 > 0:
            text_c(d, (1635, 200), '25 MAY 2020', F_LABEL, A(CYAN, a1))
        if a2 > 0:
            text_c(d, (1635, 200), '10 JUNE 2020', F_LABEL, A(PINK_T, a2))
    a3 = ramp(t, 12.0, 12.5)
    if a3 > 0:
        card(d, 560, 380, 1360, 560, a3)
        text_c(d, (W / 2, 470), 'WHAT MADE THIS HOLE?', F_MED, A(AMBER, a3))
    top_label(img, 'LONAR LAKE · INDIA', ramp(t, 0.1, 0.5))
    return img

CAP01 = [(0, 4, 'In early June 2020, a lake in western India changed colour, from green to pink.', ['green', 'pink.']),
         (4, 8, 'A Landsat satellite saw it: green on the 25th of May… pink by the 10th of June.', ['Landsat', 'green', 'pink']),
         (8, 11, 'But the colour is not the strangest thing about Lonar Lake.', ['Lonar']),
         (11, 14, 'The strangest thing is the hole it sits in.', ['hole'])]

# ---------- 2. title ----------
def c02(t):
    img, d = new()
    draw_stars(d, t, 0.8)
    a = ramp(t, 0.2, 0.9)
    text_c(d, (W / 2, 380), 'LONAR CRATER', F_TITLE, A(WHITE, a))
    text_c(d, (W / 2, 520), 'A lake in lava rock, made by a rock from space', F_MED, A(AMBER, ramp(t, 0.8, 1.4)))
    return img

CAP02 = [(0, 5.5, 'This is the story of Lonar, and how science worked out what made it.', ['Lonar,', 'science'])]

# ---------- 3. map zoom ----------
def cam3(t):
    k = ease(ramp(t, 0.2, 4.0))
    s = math.exp(lerp(math.log(18), math.log(420), k))
    return Cam(lerp(80.0, LONAR[0], k), lerp(22.0, LONAR[1], k), s)


def c03(t):
    cam = cam3(t)
    img = land_only(cam)
    d = ImageDraw.Draw(img, 'RGBA')
    a0 = 1 - ramp(t, 1.4, 2.0)
    if a0 > 0:
        text_c(d, (W / 2 + 60, 470), 'INDIA', F_MED, A(WHITE, 0.8 * a0))
    x, y = cam.xy(*LONAR)
    a = ramp(t, 3.6, 4.0)
    if a > 0:
        q = ((t - 3.6) % 1.2) / 1.2
        pr = 30 + 40 * q
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=A(AMBER, 0.8 * a * (1 - q)), width=4)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=A(AMBER, a))
        d.text((x + 36, y - 20), 'LONAR', font=F_MED, fill=A(WHITE, a), anchor='ls')
        d.text((x + 36, y + 16), 'Buldhana district, Maharashtra', font=F_SMALL, fill=A(GREY, a), anchor='lt')
    top_label(img, 'CHAPTER 1 · A BOWL IN THE LAVA')
    return img

CAP03 = [(0, 4.5, 'Lonar sits in Buldhana district, in the Indian state of Maharashtra.', ['Buldhana', 'Maharashtra.']),
         (4.5, 7.5, 'From above, it looks almost perfectly round.', ['round.'])]

# ---------- 4. crater from above, with sizes ----------
def c04(t):
    img = Image.new('RGB', (W, H), BG)
    cx, cy, R = 960, 470, 300
    crater_top(img, cx, cy, R, GREEN_L, t, 0.7)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ease(ramp(t, 0.4, 1.6))
    if a > 0:
        yy = cy - R * 1.06 - 34
        L = R * 1.02 * a
        d.line([cx - L, yy, cx + L, yy], fill=AMBER, width=6)
        for sx in (-1, 1):
            ex = cx + sx * L
            d.polygon([(ex, yy), (ex - sx * 22, yy - 13), (ex - sx * 22, yy + 13)], fill=AMBER)
        card(d, 1430, 150, 1840, 260, ramp(t, 1.2, 1.6))
        text_c(d, (1635, 205), 'RIM ≈ 1.8 km', F_MED, A(AMBER, ramp(t, 1.2, 1.6)))
    b = ramp(t, 9.0, 9.5)
    if b > 0:
        lw = R * 0.74
        y2 = cy + R * 0.66 + 40
        d.line([cx - lw, y2, cx + lw, y2], fill=A(CYAN, b), width=5)
        for x in (cx - lw, cx + lw):
            d.line([x, y2 - 14, x, y2 + 14], fill=A(CYAN, b), width=5)
        card(d, 80, 620, 520, 730, b)
        text_c(d, (300, 675), 'LAKE ≈ 1.2 km', F_MED, A(CYAN, b))
    c = ramp(t, 4.0, 4.5)
    if c > 0:
        card(d, 80, 150, 520, 260, c)
        text_c(d, (300, 205), 'DEPTH ≈ 150 m', F_MED, A(WHITE, c))
    top_label(img, 'FROM ABOVE')
    return img

CAP04 = [(0, 4.5, 'The crater is about 1.8 kilometres across, and roughly 150 metres deep.', ['1.8', 'kilometres', '150', 'metres']),
         (4.5, 8.5, 'Its rim rises some twenty to thirty metres above the flat land around it.', ['rim', 'twenty', 'thirty']),
         (8.5, 12, 'And at the bottom lies a lake, about 1.2 kilometres wide.', ['lake,', '1.2'])]

# ---------- 5. lava layers (Deccan Traps) ----------
NL5, LH5 = 9, 62


def c05(t):
    img, d = new()
    sky(d, (6, 8, 14), (30, 18, 16), VB)
    base = VB
    n = 1 + int(min(t / 0.9, NL5 - 1))
    for i in range(n):
        y1 = base - i * LH5
        y0 = y1 - LH5
        tt = t - i * 0.9
        heat = math.exp(-max(tt, 0) * 1.1)
        grey = 44 + (i % 2) * 10
        col = mix((grey, grey + 2, grey + 8), (255, 110, 40), heat)
        rng = np.random.default_rng(i)
        wav = [(x, y0 + 6 * math.sin(x / 120 + i * 1.7) + rng.uniform(-3, 3)) for x in range(0, W + 1, 30)]
        xr = W * ease(ramp(tt, 0, 0.7))
        poly = [(x, y) for x, y in wav if x <= xr] + [(xr, y1), (0, y1)]
        if len(poly) > 2:
            d.polygon(poly, fill=col)
            d.line([(x, y) for x, y in wav if x <= xr], fill=mix((70, 70, 78), (255, 200, 120), heat), width=3)
    d.rectangle([0, VB, W, H], fill=(30, 32, 38))
    arr = to_arr(img)
    tt = t - (n - 1) * 0.9
    glow(arr, 960, base - n * LH5 + 10, 520, (255, 100, 30), 0.35 * math.exp(-max(tt, 0) * 1.1))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 1.0, 1.5)
    card(d, 560, 140, 1360, 290, a)
    text_c(d, (W / 2, 195), 'DECCAN TRAPS', F_MED, A(AMBER, a))
    text_c(d, (W / 2, 255), 'layer upon layer of basalt', F_LABEL, A(WHITE, a))
    b = ramp(t, 9.0, 9.4)
    if b > 0:
        x = 1700
        y1, y0 = base - 4 * LH5, base - 5 * LH5
        d.line([x, y0, x, y1], fill=A(CYAN, b), width=5)
        for y in (y0, y1):
            d.line([x - 16, y, x + 16, y], fill=A(CYAN, b), width=5)
        d.text((x - 30, (y0 + y1) / 2), 'one flow: 3–20 m', font=F_SMALL, fill=A(WHITE, b), anchor='rm')
    top_label(img, '≈66 MILLION YEARS AGO')
    return img

CAP05 = [(0, 3.5, 'The ground here is basalt, part of the Deccan Traps.', ['basalt,', 'Deccan', 'Traps.']),
         (3.5, 8, 'About 66 million years ago, huge eruptions flooded this part of India with lava…', ['66', 'million', 'lava…']),
         (8, 11.5, '…layer upon layer, each flow a few metres to twenty metres thick.', ['layer', 'twenty']),
         (11.5, 15, 'Basalt is hard, dark volcanic rock. And that is where the puzzle began.', ['volcanic', 'puzzle'])]

# ---------- 6. 1823 ----------
def c06(t):
    img, d = new()
    a = ease(ramp(t, 0.2, 1.0))
    x0 = lerp(2000, 560, a)
    d.rectangle([x0, 130, x0 + 800, 810], fill=(232, 222, 196))
    for i in range(0, 680, 40):
        d.line([x0 + 50, 150 + i, x0 + 750, 150 + i], fill=(205, 192, 165), width=2)
    d.text((x0 + 400, 220), '1823', font=F_HUGE, fill=(60, 48, 36), anchor='mm')
    d.text((x0 + 400, 320), 'a British officer, C. J. E. Alexander,', font=F_LABEL, fill=(70, 58, 44), anchor='mm')
    d.text((x0 + 400, 365), 'records the crater', font=F_LABEL, fill=(70, 58, 44), anchor='mm')
    # sketch of the bowl
    cx, cy = x0 + 400, 560
    pts = [(cx - 300 + i * 10, cy - 30 + 160 * max(0, 1 - ((i * 10 - 300) / 230) ** 2) ** 1.2) for i in range(61)]
    d.line(pts, fill=(90, 70, 50), width=5)
    d.line([cx - 300, cy - 30, cx - 360, cy - 10], fill=(90, 70, 50), width=5)
    d.line([cx + 300, cy - 30, cx + 360, cy - 10], fill=(90, 70, 50), width=5)
    d.polygon([(cx - 120, cy + 110), (cx + 120, cy + 110), (cx + 90, cy + 128), (cx - 90, cy + 128)], fill=(110, 130, 120))
    q = ramp(t, 5.0, 5.5)
    if q > 0:
        text_c(d, (cx, 740), '?', F_HUGE, A((150, 60, 40), q))
    top_label(img, 'CHAPTER 2 · A VOLCANO?')
    return img

CAP06 = [(0, 4.5, 'In 1823, a British officer named C. J. E. Alexander recorded the crater.', ['1823,', 'Alexander']),
         (4.5, 8, 'For a long time, many geologists thought the bowl must be volcanic.', ['volcanic.'])]

# ---------- 7. the volcano idea vs the impact idea ----------
def c07(t):
    img, d = new()
    sky(d, ymax=VB)
    d.rectangle([0, VB - 90, W, H], fill=(40, 42, 48))
    k = ease(ramp(t, 0.2, 1.2))
    peak = lerp(VB - 90, 330, k)
    cx = 700
    cone = [(cx - 440, VB - 90), (cx - 70, peak), (cx - 40, peak + 24), (cx + 40, peak + 24), (cx + 70, peak), (cx + 440, VB - 90)]
    d.polygon(cone, fill=(58, 54, 56))
    d.line(cone, fill=(96, 90, 92), width=4)
    arr = to_arr(img)
    glow(arr, cx, peak + 10, 60, (255, 110, 40), 0.6 * k * (0.7 + 0.3 * math.sin(t * 3)))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 1.0, 1.4)
    text_c(d, (cx, 220), 'VOLCANO?', F_MED, A(WHITE, a))
    b = ramp(t, 7.5, 8.0)
    if b > 0:
        arr = to_arr(img)
        e = ramp(t, 7.5, 9.5)
        for j in range(20):
            q = max(e - j * 0.03, 0)
            glow(arr, lerp(1850, 1450, q), lerp(120, VB - 120, q), 14 - j * 0.5, (255, 150, 60), 0.6 * b * (1 - j / 20))
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
        text_c(d, (1450, 220), 'FROM SPACE?', F_MED, A(AMBER, b))
    top_label(img, 'TWO IDEAS')
    return img

CAP07 = [(0, 3, 'It made sense. The whole region is made of old lava.', ['old', 'lava.']),
         (3, 7, 'And a round pit in volcanic land looks a lot like a volcanic crater.', ['volcanic', 'crater.']),
         (7, 11, 'But there was a far stranger idea: that something had hit it from space.', ['stranger', 'space.'])]

# ---------- 8. drilling, 1973 ----------
GY8 = 420


def prof8(x):
    u = (x - 960) / 640
    if abs(u) < 1:
        return GY8 - 28 + (300 + 28) * (1 - u * u) ** 1.2
    return GY8 - 28 * math.exp(-(abs(u) - 1) * 5)


def c08(t):
    return _c08(max(t - 3.5, 0.0))


def _c08(t):
    img, d = new()
    sky(d, ymax=GY8 + 40)
    top = [(x, prof8(x)) for x in range(0, W + 1, 6)]
    d.polygon(top + [(W, H), (0, H)], fill=(46, 48, 54))
    for i, col in enumerate([(56, 58, 64), (40, 42, 48), (52, 52, 58), (36, 38, 44)]):
        d.rectangle([0, 760 + i * 50, W, 810 + i * 50], fill=col)
    d.polygon(top + [(W, H), (0, H)], outline=(90, 92, 100))
    d.line(top, fill=(120, 104, 74), width=8)
    floor = prof8(960)
    # breccia lens under the floor
    rng = np.random.default_rng(8)
    for _ in range(140):
        x, y = rng.uniform(760, 1160), rng.uniform(floor + 10, floor + 90)
        if abs(x - 960) / 200 + (y - floor) / 110 < 1:
            s = rng.uniform(5, 13)
            d.polygon([(x, y - s), (x + s, y + s * 0.6), (x - s, y + s * 0.4)], fill=(80, 76, 70))
    a = ramp(t, 0.5, 1.2)
    # drill rig: a lattice tower (object)
    bx = 1040
    d.line([bx - 60, floor - 4, bx, floor - 230], fill=A((200, 205, 215), a), width=6)
    d.line([bx + 60, floor - 4, bx, floor - 230], fill=A((200, 205, 215), a), width=6)
    for k in range(1, 5):
        y = floor - 4 - k * 45
        hw = 60 * (1 - k * 45 / 226)
        d.line([bx - hw, y, bx + hw, y], fill=A((200, 205, 215), a), width=3)
    dep = ease(ramp(t, 1.5, 6.0)) * 100
    d.line([bx, floor - 230, bx, floor + dep], fill=A(AMBER, a), width=5)
    b = ramp(t, 2.0, 2.4)
    card(d, 560, 120, 1360, 230, b)
    text_c(d, (W / 2, 175), 'SCIENCE · 1973', F_MED, A(AMBER, b))
    c = ramp(t, 6.0, 6.4)
    for sx in (520, 1400):
        d.rectangle([sx - 40, prof8(sx) - 30, sx + 40, prof8(sx) + 10], fill=A((20, 22, 26), c))
    text_c(d, (520, prof8(520) - 70), 'trench', F_SMALL, A(WHITE, c))
    text_c(d, (1400, prof8(1400) - 70), 'trench', F_SMALL, A(WHITE, c))
    top_label(img, 'CHAPTER 3 · THE PROOF')
    return img

CAP08 = [(0, 3.5, 'If something had hit Lonar, the rock should carry scars that only an impact can leave.', ['scars', 'impact']),
         (3.5, 8, 'In 1973, a team of scientists reported what they had found, in the journal Science.', ['1973,', 'Science.']),
         (4.5, 8.5, 'They had drilled through the floor of the crater, and dug trenches in its rim.', ['drilled', 'trenches'])]

# ---------- 9. drill cores: breccia, shatter cones, melt beads ----------
def c09(t):
    img, d = new()
    rng = np.random.default_rng(9)
    for i in range(3):
        a = ramp(t, 0.3 + i * 0.4, 0.8 + i * 0.4)
        y = 200 + i * 110
        d.rounded_rectangle([200, y, 1000, y + 70], radius=35, fill=A((70, 68, 66), a))
        for _ in range(70):
            x, yy, s = rng.uniform(220, 980), rng.uniform(y + 10, y + 60), rng.uniform(4, 12)
            g = int(rng.uniform(90, 150))
            d.polygon([(x, yy - s), (x + s, yy + s * 0.5), (x - s * 0.8, yy + s * 0.6)], fill=A((g, g - 4, g - 8), a))
    d.text((600, 560), 'CRUSHED ROCK (BRECCIA)', font=F_LABEL, fill=A(WHITE, ramp(t, 1.4, 1.8)), anchor='mm')
    b = ramp(t, 3.0, 3.5)
    if b > 0:
        cx, cy = 1450, 360
        d.polygon([(cx, cy - 170), (cx + 150, cy + 150), (cx - 150, cy + 150)], fill=A((86, 84, 82), b))
        for j in range(-6, 7):
            d.line([cx, cy - 170, cx + j * 25, cy + 150], fill=A((150, 148, 144), b), width=3)
        d.text((cx, cy + 200), 'SHATTER CONE', font=F_LABEL, fill=A(AMBER, b), anchor='mm')
    c = ramp(t, 7.0, 7.5)
    if c > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(255 * c)))
        arr = to_arr(img)
        r2 = np.random.default_rng(19)
        for j in range(26):
            x, y, s = r2.uniform(260, 1660), r2.uniform(220, 700), r2.uniform(10, 34)
            glow(arr, x, y, s * 1.2, (110, 160, 200), 0.35 * c)
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
        r2 = np.random.default_rng(19)
        for j in range(26):
            x, y, s = r2.uniform(260, 1660), r2.uniform(220, 700), r2.uniform(10, 34)
            d.ellipse([x - s, y - s, x + s, y + s], fill=A((60, 70, 78), c), outline=A((160, 190, 210), c), width=2)
        text_c(d, (W / 2, 160), 'BEADS & BOMBS OF MELTED ROCK', F_MED, A(CYAN, c))
    top_label(img, 'WHAT THEY FOUND')
    return img

CAP09 = [(0, 4.5, 'In the drill cores they found shattered, crushed rock, called breccia…', ['crushed', 'breccia…']),
         (4.5, 7.5, '…with cone-shaped fractures known as shatter cones.', ['shatter', 'cones.']),
         (7.5, 12.5, 'In the rim, they found minerals that had melted and frothed, and little beads and bombs of melted rock.', ['melted', 'beads', 'bombs'])]

# ---------- 10. maskelynite ----------
_r10 = np.random.default_rng(9)
GRAINS = [(_r10.uniform(-320, 320), _r10.uniform(-320, 320), _r10.uniform(18, 46), _r10.uniform(0, 6.28), int(_r10.uniform(36, 80))) for _ in range(260)]
GLASS = [(-120, -60, 60), (90, 40, 70), (-40, 140, 50), (150, -150, 46)]


def c10(t):
    img, d = new()
    cx, cy, R = 700, 470, 300
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
        sh = ramp(t, 4.0, 5.0)
        for gx, gy, s in GLASS:
            if sh > 0:
                pts = [(cx + gx + s * math.cos(0.6 + j * 1.25), cy + gy + s * math.sin(0.6 + j * 1.25)) for j in range(5)]
                dt.polygon(pts, fill=mix((70, 70, 76), (170, 230, 255), sh))
        arr = to_arr(tex)
        if sh > 0:
            for i, (gx, gy, s) in enumerate(GLASS):
                tw = 0.6 + 0.4 * math.sin(t * 4 + i * 2)
                glow(arr, cx + gx, cy + gy, s * 0.9, (120, 210, 255), 0.7 * sh * tw)
        img.paste(to_img(arr), (0, 0), m)
        d = ImageDraw.Draw(img, 'RGBA')
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(200, 205, 215), width=10)
    a = ramp(t, 0.8, 1.2)
    text_c(d, (1400, 300), 'MASKELYNITE', F_MED, A(CYAN, a))
    b = ramp(t, 3.0, 3.4)
    d.text((1400, 390), 'plagioclase turned to glass', font=F_LABEL, fill=A(WHITE, b), anchor='mm')
    d.text((1400, 440), 'by a sudden, crushing shock', font=F_LABEL, fill=A(WHITE, b), anchor='mm')
    c = ramp(t, 9.5, 10.0)
    if c > 0:
        card(d, 1080, 540, 1720, 660, c)
        text_c(d, (1400, 600), 'IMPACT ORIGIN', F_MED, A(AMBER, c))
    top_label(img, 'THE KEY CLUE')
    return img

CAP10 = [(0, 2.5, 'And deep in the crater, they found maskelynite.', ['maskelynite.']),
         (2.5, 6.5, 'It forms when a mineral called plagioclase is turned to glass by a sudden, crushing shock…', ['plagioclase', 'glass', 'shock…']),
         (6.5, 9, '…a shock far beyond anything a volcano can make.', ['volcano']),
         (9, 12.5, 'The team wrote that it established the impact origin of Lonar Crater.', ['impact', 'origin'])]

# ---------- 11. the impact ----------
GY11 = 640
_r11 = np.random.default_rng(3)
EJ = [(_r11.uniform(0.25, 2.9), _r11.uniform(380, 1000), _r11.uniform(4, 10)) for _ in range(200)]


def prof11(x, k):
    u = (x - 960) / 420
    rim = 26 * k * math.exp(-max(abs(u) - 1, 0) * 4) if abs(u) >= 1 else 26 * k
    if abs(u) < 1:
        return GY11 - rim + (170 * k + rim) * (1 - u * u) ** 1.2
    return GY11 - rim


def c11(t):
    img, d = new()
    sky(d, (4, 6, 13), (14, 24, 44), GY11 + 60)
    k = ease(ramp(t, 3.2, 4.0))
    top = [(x, prof11(x, k)) for x in range(0, W + 1, 6)]
    d.polygon(top + [(W, H), (0, H)], fill=(48, 50, 56))
    for i, col in enumerate([(56, 58, 64), (40, 42, 48), (52, 52, 58)]):
        d.rectangle([0, 860 + i * 50, W, 910 + i * 50], fill=col)
    d.line(top, fill=(90, 92, 100), width=5)
    arr = to_arr(img)
    P0, P1 = (1750, 130), (960, GY11)
    if 0.5 <= t < 3.2:
        e = ramp(t, 0.5, 3.2) ** 1.4
        for j in range(26):
            q = max(e - j * 0.022, 0)
            glow(arr, lerp(P0[0], P1[0], q), lerp(P0[1], P1[1], q), 18 - j * 0.5, (255, 140, 50), 0.5 * (1 - j / 26))
        glow(arr, lerp(P0[0], P1[0], e), lerp(P0[1], P1[1], e), 32, (255, 210, 140), 1.2)
    if t >= 3.2:
        f = math.exp(-(t - 3.2) * 1.6)
        glow(arr, 960, GY11, 380, (255, 140, 50), 2.2 * f)
        glow(arr, 960, GY11, 110, (255, 250, 220), 3.0 * f)
        te = t - 3.2
        for ang, v, s in EJ:
            px = 960 + math.cos(ang) * v * te
            py = GY11 - math.sin(ang) * v * te + 0.5 * 900 * te * te
            if py < prof11(px, k) and 0 < px < W:
                glow(arr, px, py, s, (255, 160, 80), 0.9 * math.exp(-te * 0.8))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 6.0, 6.5)
    if a > 0:
        text_c(d, (W / 2, 220), 'A ROCK FROM SPACE', F_MED, A(AMBER, a))
        text_c(d, (W / 2, 290), 'into solid lava rock', F_LABEL, A(WHITE, a))
    top_label(img, 'CHAPTER 4 · THE IMPACT')
    return img

CAP11 = [(0, 4.5, 'Something from space, moving many kilometres every second, slammed into the lava plain.', ['space,', 'kilometres', 'second,']),
         (4.5, 9, 'In an instant, it blasted out a bowl and threw rock in every direction.', ['instant,', 'bowl']),
          (9, 11, 'Scientists call this a hypervelocity impact.', ['hypervelocity'])]

# ---------- 12. ejecta blanket ----------
def c12(t):
    img = Image.new('RGB', (W, H), BG)
    cx, cy, R = 960, 470, 140
    crater_top(img, cx, cy, R, GREEN_L, t, 0.0, ejecta=0.0)
    d = ImageDraw.Draw(img, 'RGBA')
    k = ease(ramp(t, 0.4, 2.4))
    rr = R * 1.06 + 1.35 / 0.9 * R * k  # rim radius ~0.9 km -> blanket 1.35 km beyond the rim
    d.ellipse([cx - rr, cy - rr * 0.95, cx + rr, cy + rr * 0.95], outline=A(AMBER, 0.9 * k), width=5)
    for i in range(48):
        a = i / 48 * 2 * math.pi
        r1, r2 = R * 1.12, R * 1.12 + (rr - R * 1.12) * (0.6 + 0.4 * ((i * 7) % 5) / 5)
        d.line([cx + math.cos(a) * r1, cy + math.sin(a) * r1 * 0.95, cx + math.cos(a) * r2, cy + math.sin(a) * r2 * 0.95],
               fill=A((150, 128, 92), 0.55 * k), width=4)
    a = ramp(t, 2.2, 2.6)
    card(d, 1380, 140, 1860, 300, a)
    text_c(d, (1620, 195), 'EJECTA BLANKET', F_LABEL, A(AMBER, a))
    text_c(d, (1620, 255), '≈1.35 km beyond the rim', F_LABEL, A(WHITE, a))
    b = ramp(t, 5.5, 6.0)
    if b > 0:
        card(d, 60, 560, 600, 760, b)
        for j, (x, y, s) in enumerate(((150, 640, 22), (240, 670, 14), (320, 630, 18), (400, 680, 11))):
            d.ellipse([x - s, y - s, x + s, y + s], fill=A((60, 80, 90), b), outline=A(CYAN, b), width=3)
        d.text((330, 735), 'glassy melt, up to 5 cm', font=F_SMALL, fill=A(WHITE, b), anchor='mm')
    top_label(img, 'THE DEBRIS IS STILL THERE')
    return img

CAP12 = [(0, 2.5, 'That debris still lies around the crater…', ['debris']),
         (2.5, 5.5, '…a blanket of ejected rock, reaching about 1.35 kilometres beyond the rim.', ['blanket', '1.35']),
         (5.5, 9.5, 'Glassy pieces of melted rock, up to five centimetres across, have been found in it.', ['Glassy', 'five', 'centimetres'])]

# ---------- 13. the Moon ----------
_r13 = np.random.default_rng(12)
MOONC = [(_r13.uniform(-0.8, 0.8), _r13.uniform(-0.8, 0.8), _r13.uniform(0.03, 0.12)) for _ in range(46)]


def moon(d, img, cx, cy, R, maria=1.0):
    arr = to_arr(img)
    glow(arr, cx, cy, R * 1.1, (120, 130, 150), 0.35)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(150, 150, 158))
    for mx, my, mr in ((-0.3, -0.25, 0.35), (0.25, 0.2, 0.28), (0.35, -0.4, 0.18)):
        x, y, r = cx + mx * R, cy + my * R, mr * R
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=A((88, 88, 100), maria))
    for mx, my, mr in MOONC:
        if mx * mx + my * my < 0.75:
            x, y, r = cx + mx * R, cy + my * R, mr * R
            d.ellipse([x - r, y - r, x + r, y + r], fill=(118, 118, 128), outline=(185, 185, 192), width=max(1, int(r * 0.15)))
    return img, d


def c13(t):
    img, d = new()
    draw_stars(d, t, 0.8)
    k = ease(ramp(t, 0.3, 1.3))
    img, d = moon(d, img, 620, 470, 300 * k + 1, ramp(t, 5.5, 6.5) * 0.5 + 0.5)
    a = ramp(t, 6.0, 6.5)
    if a > 0:
        d.line([700, 380, 1080, 260], fill=A(AMBER, a), width=4)
        d.text((1100, 260), 'dark plains = BASALT', font=F_LABEL, fill=A(AMBER, a), anchor='lm')
    b = ramp(t, 10.0, 10.5)
    if b > 0:
        card(d, 1060, 420, 1840, 600, b)
        text_c(d, (1450, 475), 'LONAR', F_MED, A(WHITE, b))
        text_c(d, (1450, 550), 'a rare impact crater in basalt on Earth', F_LABEL, A(CYAN, b))
    top_label(img, 'CHAPTER 5 · WHY IT MATTERS')
    return img

CAP13 = [(0, 3, 'Here is why scientists care so much about this one bowl.', ['care']),
         (3, 5.5, 'On Earth, wind, rain and plants slowly wear craters away.', ['wear', 'away.']),
         (3, 7.5, 'The dark plains on the Moon are basalt too, and they are covered in impact craters.', ['Moon', 'basalt', 'craters.']),
         (7.5, 11, 'Lonar is one of very few craters on Earth made directly in basalt…', ['very', 'few', 'basalt…']),
         (11, 14.5, '…so the 1973 team called it an analogue for craters on the Moon.', ['analogue', 'Moon.'])]

# ---------- 14. Mars comparison ----------
def c14(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    arr = to_arr(img)
    mx, my, R = 1300, 470, 270
    glow(arr, mx, my, R * 1.1, (200, 100, 60), 0.3)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([mx - R, my - R, mx + R, my + R], fill=(170, 92, 60))
    rng = np.random.default_rng(14)
    for _ in range(26):
        x, y, r = rng.uniform(-0.75, 0.75), rng.uniform(-0.75, 0.75), rng.uniform(0.03, 0.1)
        if x * x + y * y < 0.6:
            d.ellipse([mx + x * R - r * R, my + y * R - r * R, mx + x * R + r * R, my + y * R + r * R], fill=(140, 72, 48), outline=(200, 120, 84), width=2)
    # layered ejecta sketch
    cx, cy = 520, 470
    for i, (rr, col) in enumerate(((240, (120, 100, 74)), (190, (100, 84, 62)), (140, (120, 100, 74)), (100, (60, 56, 50)))):
        a = ramp(t, 0.5 + i * 0.4, 0.9 + i * 0.4)
        d.ellipse([cx - rr, cy - rr * 0.95, cx + rr, cy + rr * 0.95], fill=A(col, a))
    d.text((cx, cy + 290), 'LAYERED DEBRIS', font=F_LABEL, fill=A(WHITE, ramp(t, 2.0, 2.4)), anchor='mm')
    d.text((mx, my + 320), 'MARS', font=F_LABEL, fill=A(AMBER, ramp(t, 2.0, 2.4)), anchor='mm')
    text_c(d, (910, 470), '≈', F_HUGE, A(GREY, ramp(t, 2.5, 3.0)))
    top_label(img, 'AND MARS, TOO')
    return img

CAP14 = [(0, 5, 'Later studies even compared the layered debris around Lonar to craters on Mars.', ['layered', 'Mars.'])]

# ---------- 15. how old? timeline ----------
X0, X1, AY = 200, 1720, 520


def ax_(years):
    return X0 + (X1 - X0) * years / 700000


AGES = [(52000, 3.0, '≈52,000', 'glass, 1997', WHITE, True),
        (15000, 7.0, '≈15,000 ± 13,000', 'fission tracks', GREY, None),
        (570000, 11.0, '≈570,000', 'argon dating, 2011', AMBER, False),
        (37500, 16.0, '≈37,500', 'cosmic-ray exposure, 2014', CYAN, False)]


def c15(t):
    img, d = new()
    k = ease(ramp(t, 0.2, 1.4))
    d.line([X0, AY, lerp(X0, X1, k), AY], fill=GREY, width=6)
    for yrs in range(0, 700001, 100000):
        x = ax_(yrs)
        if x <= lerp(X0, X1, k):
            d.line([x, AY - 14, x, AY + 14], fill=GREY, width=3)
            if k >= 1:
                d.text((x, AY + 30), 'NOW' if yrs == 0 else f'{yrs // 1000}k', font=F_SMALL, fill=GREY, anchor='mt')
    if k >= 1:
        d.text((X1, AY + 80), 'years ago →', font=F_SMALL, fill=GREY, anchor='rt')
    for yrs, t0, lab, sub, col, up in AGES:
        a = ramp(t, t0, t0 + 0.4)
        if a <= 0:
            continue
        x = ax_(yrs)
        q = ((t - t0) % 1.2) / 1.2
        pr = 20 + 24 * q
        d.ellipse([x - pr, AY - pr, x + pr, AY + pr], outline=A(col, 0.7 * a * (1 - q)), width=4)
        d.ellipse([x - 15, AY - 15, x + 15, AY + 15], fill=A(col, a))
        if yrs == 37500:
            ly, anc, tx = AY + 280, 'l', x - 10
        elif up is None:
            ly, anc, tx = AY - 310, 'l', x - 10
        elif up:
            ly, anc, tx = AY - 170, 'l', x - 10
        else:
            ly, anc, tx = AY - 170, 'r', x + 10
        d.line([x, AY + (20 if ly > AY else -20), x, ly + (-70 if ly > AY else 30)], fill=A(col, a), width=3)
        d.text((tx, ly - 10), lab, font=F_MED, fill=A(col, a), anchor=anc + 's')
        d.text((tx, ly + 4), sub, font=F_SMALL, fill=A(WHITE, a), anchor=anc + 't')
    top_label(img, 'CHAPTER 6 · HOW OLD IS IT?')
    return img

CAP15 = [(0, 3, "So when did it happen? You might think that's easy to answer. It isn't.", ['when', "isn't."]),
         (3, 7, 'In 1997, glass from the impact was dated to about 52,000 years old.', ['1997,', '52,000']),
         (7, 11, 'Another method, fission-track dating, pointed to about 15,000 years, give or take 13,000.', ['fission-track', '15,000']),
         (7, 11, 'In 2011, argon dating of melted rock gave a far older answer: about 570,000 years.', ['2011,', 'argon', '570,000']),
         (11, 15, 'In 2014, another team measured how long the surface had been hit by cosmic rays…', ['2014,', 'cosmic', 'rays…']),
         (15, 17.5, '…and got about 37,500 years.', ['37,500'])]

# ---------- 16. still debated ----------
def c16(t):
    img, d = new()
    # an argon "trap" diagram: glass grain with old atoms inside
    cx, cy, R = 560, 470, 230
    d.polygon([(cx + R * math.cos(a), cy + R * 0.85 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]],
              fill=(60, 80, 96), outline=(160, 200, 220))
    rng = np.random.default_rng(16)
    for i in range(30):
        a = ramp(t, 0.5 + i * 0.05, 0.8 + i * 0.05)
        x, y = cx + rng.uniform(-150, 150), cy + rng.uniform(-120, 120)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=A(AMBER, a))
    d.text((cx, cy + 260), 'old argon trapped in the glass?', font=F_LABEL, fill=A(WHITE, ramp(t, 1.0, 1.4)), anchor='mm')
    a = ramp(t, 5.0, 5.4)
    if a > 0:
        card(d, 1000, 250, 1820, 420, a)
        text_c(d, (1410, 305), 'NASA', F_LABEL, A(GREY, a))
        text_c(d, (1410, 370), '35,000 – 50,000 years', F_MED, A(WHITE, a))
    b = ramp(t, 8.5, 9.0)
    if b > 0:
        d.rounded_rectangle([1090, 520, 1730, 630], radius=20, outline=A(RED, b), width=6)
        text_c(d, (1410, 575), 'STILL DEBATED', F_MED, A(RED, b))
    top_label(img, 'WHICH CLOCK IS RIGHT?')
    return img

CAP16 = [(0, 5, 'They argued the argon age was thrown off by old argon, already trapped in the glass.', ['old', 'argon,', 'trapped']),
         (5, 8.5, 'NASA puts the impact at about 35,000 to 50,000 years ago.', ['35,000', '50,000']),
         (8.5, 11.5, 'But the question is still debated.', ['debated.'])]

# ---------- 17. back to 2020: two satellite frames ----------
def c17(t):
    img, d = new()
    for i, (col, lab, lc) in enumerate(((GREEN_L, '25 MAY 2020', CYAN), (PINK_L, '10 JUNE 2020', PINK_T))):
        a = ramp(t, 0.3 + i * 1.5, 0.8 + i * 1.5)
        if a <= 0:
            continue
        x0 = 160 + i * 860
        tile = Image.new('RGB', (W, H), BG)
        crater_top(tile, 960, 540, 260, col, t, 0.5)
        tile = tile.crop((960 - 370, 540 - 290, 960 + 370, 540 + 290))
        img.paste(Image.blend(Image.new('RGB', tile.size, BG), tile, a), (x0, 160))
        d = ImageDraw.Draw(img, 'RGBA')
        d.rectangle([x0, 160, x0 + 740, 740], outline=A((120, 130, 150), a), width=3)
        d.text((x0 + 370, 790), lab, font=F_LABEL, fill=A(lc, a), anchor='mm')
    top_label(img, 'CHAPTER 7 · WHY DID IT TURN PINK?')
    return img

CAP17 = [(0, 4, 'Now, back to the summer of 2020, and the lake that changed colour.', ['2020,', 'colour.'])]

# ---------- 18. salt, pH, no outflow ----------
def c18(t):
    img, d = new()
    sky(d, (10, 16, 30), (60, 40, 30), VB)
    GY = 300
    def pf(x):
        u = (x - 960) / 700
        return GY + 380 * max(0, 1 - u * u) ** 1.2 if abs(u) < 1 else GY
    top = [(x, pf(x)) for x in range(0, W + 1, 8)]
    d.polygon(top + [(W, H), (0, H)], fill=(46, 48, 54))
    lvl = lerp(560, 610, ease(ramp(t, 8.5, 13.5)))
    lake = [(x, y) for x, y in top if y > lvl]
    if len(lake) > 2:
        col = mix(GREEN_L, (150, 112, 108), ramp(t, 11.5, 15.5))
        d.polygon([(lake[0][0], lvl)] + lake + [(lake[-1][0], lvl)], fill=col)
    d.line(top, fill=(120, 104, 74), width=6)
    a = ramp(t, 6.0, 6.5)
    if a > 0:
        for j in range(5):
            q = ((t * 0.5 + j * 0.2) % 1.0)
            x = 760 + j * 100
            y = lvl - 20 - q * 260
            d.line([x, y, x + 10 * math.sin(q * 6), y - 40], fill=A((200, 220, 240), a * (1 - q) * 0.8), width=4)
        d.text((960, 220), 'water evaporates · no river flows out', font=F_LABEL, fill=A(WHITE, a), anchor='mm')
    sun = ramp(t, 8.5, 9.0)
    if sun > 0:
        arr = to_arr(img)
        glow(arr, 1680, 150, 70, (255, 200, 120), 1.2 * sun)
        img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    # gauges
    for i, (lab, x) in enumerate((('SALT', 210), ('pH 9–10.5', 1710))):
        g = ramp(t, 0.6, 1.0)
        d.rounded_rectangle([x - 40, 360, x + 40, 740], radius=20, outline=A(WHITE, g), width=4)
        lv = lerp(0.45, 0.9, ease(ramp(t, 11.5, 15.5)))
        d.rounded_rectangle([x - 30, 740 - 370 * lv, x + 30, 730], radius=14, fill=A(AMBER, g))
        d.text((x, 780), lab, font=F_LABEL, fill=A(WHITE, g), anchor='mm')
    top_label(img, 'A SALTY, ALKALINE LAKE')
    return img

CAP18 = [(0, 4, "Lonar's water is salty, and strongly alkaline, with a pH of about 9 to 10.5.", ['salty,', 'alkaline,', '9', '10.5.']),
         (4, 6.5, 'For comparison, pure water has a pH of 7.', ['7.']),
         (4, 8, 'No river flows out of it. As water evaporates, minerals stay behind and build up.', ['evaporates,', 'minerals']),
         (8, 11, 'Warm, dry weather made water evaporate, and the level dropped.', ['Warm,', 'dry', 'dropped.']),
         (11, 13.5, 'The salt and the pH climbed.', ['salt', 'pH', 'climbed.'])]

# ---------- 19. samples to the lab ----------
def bottle(d, x, y, col, a=1.0, s=1.0):
    d.rounded_rectangle([x - 50 * s, y - 120 * s, x + 50 * s, y + 120 * s], radius=int(24 * s), outline=A((220, 225, 235), a), width=5)
    d.rectangle([x - 26 * s, y - 160 * s, x + 26 * s, y - 120 * s], fill=A((120, 130, 150), a))
    d.rounded_rectangle([x - 42 * s, y - 40 * s, x + 42 * s, y + 112 * s], radius=int(18 * s), fill=A(col, a))


def c19(t):
    img, d = new()
    for i in range(3):
        a = ramp(t, 0.3 + i * 0.3, 0.7 + i * 0.3)
        bottle(d, 300 + i * 160, 470, mix(PINK_L, (200, 120, 140), i / 3), a)
    h = ramp(t, 0.5, 1.0) * (1 - ramp(t, 4.6, 5.0))
    if h > 0:
        card(d, 960, 360, 1820, 520, h)
        text_c(d, (1390, 410), 'BOMBAY HIGH COURT', F_MED, A(WHITE, h))
        text_c(d, (1390, 475), 'told: samples sent for testing', F_LABEL, A(GREY, h))
    a = ramp(t, 5.0, 5.5)
    d.line([700, 470, 900, 470], fill=A(GREY, a), width=4)
    d.polygon([(900, 456), (926, 470), (900, 484)], fill=A(GREY, a))
    if a > 0:
        card(d, 960, 240, 1820, 460, a)
        text_c(d, (1390, 290), 'NEERI', F_LABEL, A(WHITE, a))
        text_c(d, (1390, 335), 'Nagpur', F_SMALL, A(GREY, a))
        text_c(d, (1390, 385), 'AGHARKAR RESEARCH INSTITUTE', F_LABEL, A(WHITE, a))
        text_c(d, (1390, 430), 'Pune', F_SMALL, A(GREY, a))
    b = ramp(t, 7.5, 8.0) * (1 - ramp(t, 10.6, 11.0))
    if b > 0:
        card(d, 960, 520, 1820, 640, b)
        text_c(d, (1390, 580), 'red algae?  ✗', F_MED, A(GREY, b))
    c = ramp(t, 11.0, 11.5)
    if c > 0:
        card(d, 960, 520, 1820, 700, c)
        text_c(d, (1390, 580), 'HALOARCHAEA', F_MED, A(PINK_T, c))
        text_c(d, (1390, 650), 'salt-loving microbes · pink pigment', F_LABEL, A(WHITE, c))
    top_label(img, 'THE INVESTIGATION')
    return img

CAP19 = [(0, 2.5, 'The puzzle even reached the Bombay High Court.', ['Bombay', 'High', 'Court.']),
         (2.5, 4.5, 'The state forest department told the court it had sent water samples for testing…', ['samples']),
         (4.5, 6.5, '…to NEERI in Nagpur, and the Agharkar Research Institute in Pune.', ['NEERI', 'Agharkar', 'Pune.']),
         (4.5, 8, 'At first, the scientists suspected a red-pigmented alga called Dunaliella.', ['Dunaliella.']),
         (8, 12, 'But the answer was haloarchaea: salt-loving microbes that make a pink pigment.', ['haloarchaea:', 'pink', 'pigment.']),
         (12, 16, 'They had thrived in the saltier water, and formed a pink layer on the surface.', ['pink', 'layer'])]

# ---------- 20. monsoon ----------
_r20 = np.random.default_rng(21)
RAIN = [(_r20.uniform(0, W + 400), _r20.uniform(0, H), _r20.uniform(0.7, 1.3)) for _ in range(380)]


def c20(t):
    back = ease(ramp(t, 3.0, 8.0))
    img = Image.new('RGB', (W, H), BG)
    crater_top(img, 960, 470, 300, mix(PINK_L, GREEN_L, back), t, 0.6)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, H], fill=(20, 30, 50, 70))
    r = ramp(t, 0.3, 0.8) * (1 - ramp(t, 8.5, 9.0))
    if r > 0:
        for x, y, s in RAIN:
            yy = (y + t * 1500 * s) % 1100
            xx = x - yy * 0.25
            d.line([xx, yy, xx - 10 * s, yy + 44 * s], fill=(180, 210, 240, int(150 * r)), width=3)
        card(d, 700, 120, 1220, 220, r)
        text_c(d, (W / 2, 170), 'MONSOON RAIN', F_MED, A(CYAN, r))
    top_label(img, 'GREEN AGAIN')
    return img

CAP20 = [(0, 4.5, 'Then the monsoon arrived. Rain diluted the lake, and the salt and pH came down…', ['monsoon', 'diluted']),
         (4.5, 8.5, '…the pink material settled to the bottom, and the lake slowly turned green again.', ['settled', 'green'])]

# ---------- 21. ending ----------
def c21(t):
    img = Image.new('RGB', (W, H), BG)
    crater_top(img, 960, 470, 300, mix(GREEN_L, (40, 90, 70), 0.3), t, 0.6)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(120 * ramp(t, 0.0, 1.0))))
    a = ramp(t, 0.5, 1.0) * (1 - ramp(t, 7.6, 8.0))
    if a > 0:
        card(d, 500, 140, 1420, 290, a)
        text_c(d, (W / 2, 195), 'RAMSAR SITE · 2020', F_MED, A(CYAN, a))
        text_c(d, (W / 2, 255), 'a wetland of international importance', F_LABEL, A(WHITE, a))
    g = ramp(t, 5.0, 5.4) * (1 - ramp(t, 7.6, 8.0))
    if g > 0:
        card(d, 400, 330, 1520, 430, g)
        text_c(d, (W / 2, 380), 'NATIONAL GEO-HERITAGE SITE', F_MED, A(WHITE, g))
    s = ramp(t, 8.2, 8.6) * (1 - ramp(t, 12.1, 12.5))
    if s > 0:
        for i, lab in enumerate(('SHOCK GLASS', 'SHATTER CONES', 'EJECTA BLANKET')):
            y = 300 + i * 110
            card(d, 560, y - 45, 1360, y + 45, s)
            text_c(d, (W / 2, y), lab, F_MED, A(CYAN, s))
    items = [('A BOWL IN THE LAVA', 12.5), ('A LAKE THAT CHANGED COLOUR', 14.0), ('AN AGE STILL DEBATED', 16.5)]
    for i, (s_, t0) in enumerate(items):
        b = ramp(t, t0, t0 + 0.4) * (1 - ramp(t, 19.5, 20.0))
        if b > 0:
            y = 300 + i * 110
            card(d, 420, y - 45, 1500, y + 45, b)
            text_c(d, (W / 2, y), s_, F_MED, A(AMBER if i == 2 else WHITE, b))
    a3 = ramp(t, 20.0, 20.5)
    if a3 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(190 * a3)))
        text_c(d, (W / 2, 380), 'FOLLOW', F_HUGE, A(WHITE, a3))
        text_c(d, (W / 2, 500), 'for more unexplained history', F_MED, A(AMBER, a3))
    top_label(img, 'CHAPTER 8 · STILL A MYSTERY', 1 - a3)
    return img

CAP21 = [(0, 5, 'In 2020, Lonar was also added to the Ramsar list of wetlands of international importance.', ['Ramsar', 'wetlands']),
         (5, 8, 'In India, it is protected as a national geo-heritage site.', ['geo-heritage']),
         (8, 12.5, 'Shock glass, shatter cones, a blanket of debris: the marks of a blast, kept in lava rock.', ['Shock', 'glass,', 'shatter', 'cones,', 'blast,']),
         (12.5, 16,'A bowl punched into lava rock, a lake that can change colour in days…', ['lava', 'colour']),
         (16, 19.5, '…and an age that scientists are still arguing about.', ['still', 'arguing'])]

SCENES = [
    ('c01', c01, 14.0, CAP01), ('c02', c02, 5.5, CAP02), ('c03', c03, 7.5, CAP03), ('c04', c04, 12.0, CAP04),
    ('c05', c05, 15.0, CAP05), ('c06', c06, 8.0, CAP06), ('c07', c07, 11.0, CAP07), ('c08', c08, 12.0, CAP08),
    ('c09', c09, 12.5, CAP09), ('c10', c10, 12.5, CAP10), ('c11', c11, 11.0, CAP11), ('c12', c12, 9.5, CAP12),
    ('c13', c13, 17.0, CAP13), ('c14', c14, 5.0, CAP14), ('c15', c15, 21.5, CAP15), ('c16', c16, 11.5, CAP16),
    ('c17', c17, 4.0, CAP17), ('c18', c18, 16.0, CAP18), ('c19', c19, 19.0, CAP19), ('c20', c20, 8.5, CAP20),
    ('c21', c21, 22.0, CAP21),
]

SPOKEN = {
    'In early June 2020, a lake in western India changed colour, from green to pink.':
        'In early June, twenty twenty, a lake in western India changed colour, from green to pink.',
    'A Landsat satellite saw it: green on the 25th of May… pink by the 10th of June.':
        'A Landsat satellite saw it. Green, on the twenty-fifth of May... pink, by the tenth of June.',
    'Lonar sits in Buldhana district, in the Indian state of Maharashtra.':
        'Lonar sits in Buldana district, in the Indian state of Maharashtra.',
    'The crater is about 1.8 kilometres across, and roughly 150 metres deep.':
        'The crater is about one point eight kilometres across, and roughly a hundred and fifty metres deep.',
    'And at the bottom lies a lake, about 1.2 kilometres wide.':
        'And at the bottom lies a lake, about one point two kilometres wide.',
    'About 66 million years ago, huge eruptions flooded this part of India with lava…':
        'About sixty-six million years ago, huge eruptions flooded this part of India with lava,',
    '…layer upon layer, each flow a few metres to twenty metres thick.':
        'layer upon layer, each flow a few metres to twenty metres thick.',
    'In 1823, a British officer named C. J. E. Alexander recorded the crater.':
        'In eighteen twenty-three, a British officer named C. J. E. Alexander recorded the crater.',
    'In 1973, a team of scientists reported what they had found, in the journal Science.':
        'In nineteen seventy-three, a team of scientists reported what they had found, in the journal Science.',
    'In the drill cores they found shattered, crushed rock, called breccia…':
        'In the drill cores, they found shattered, crushed rock, called breccha,',
    '…with cone-shaped fractures known as shatter cones.': 'with cone-shaped fractures, known as shatter cones.',
    'And deep in the crater, they found maskelynite.': 'And deep in the crater, they found maskelinite.',
    'It forms when a mineral called plagioclase is turned to glass by a sudden, crushing shock…':
        'It forms when a mineral called plajio-clase is turned to glass, by a sudden, crushing shock,',
    '…a shock far beyond anything a volcano can make.': 'a shock far beyond anything a volcano can make.',
    'That debris still lies around the crater: a blanket of ejected rock, reaching about 1.35 kilometres beyond the rim.':
        'That debris still lies around the crater: a blanket of ejected rock, reaching about one point three five kilometres beyond the rim.',
    'Lonar is one of very few craters on Earth made directly in basalt…':
        'Lonar is one of very few craters on Earth made directly in basalt,',
    '…so the 1973 team called it an analogue for craters on the Moon.':
        'so the nineteen seventy-three team called it an analogue for craters on the Moon.',
    'In 1997, glass from the impact was dated to about 52,000 years old.':
        'In nineteen ninety-seven, glass from the impact was dated to about fifty-two thousand years old.',
    'In 2011, argon dating of melted rock gave a far older answer: about 570,000 years.':
        'In twenty eleven, argon dating of melted rock gave a far older answer: about five hundred and seventy thousand years.',
    'Another method, fission-track dating, pointed to about 15,000 years, give or take 13,000.':
        'Another method, fission-track dating, pointed to about fifteen thousand years, give or take thirteen thousand.',
    'In 2014, another team measured how long the surface had been hit by cosmic rays…':
        'In twenty fourteen, another team measured how long the surface had been hit by cosmic rays,',
    '…and got about 37,500 years.': 'and got about thirty-seven thousand, five hundred years.',
    'NASA puts the impact at about 35,000 to 50,000 years ago.':
        'NASA puts the impact at about thirty-five thousand to fifty thousand years ago.',
    'For comparison, pure water has a pH of 7.': 'For comparison, pure water has a P H of seven.',
    'Scientists call this a hypervelocity impact.': 'Scientists call this a hyper-velocity impact.',
    'Now, back to the summer of 2020, and the lake that changed colour.':
        'Now, back to the summer of twenty twenty, and the lake that changed colour.',
    "Lonar's water is salty, and strongly alkaline, with a pH of about 9 to 10.5.":
        "Lonar's water is salty, and strongly alkaline, with a P H of about nine to ten and a half.",
    'The salt and the pH climbed.': 'The salt, and the P H, climbed.',
    'The state forest department sent water samples for testing, including to the Agharkar Research Institute in Pune.':
        'The state forest department sent water samples for testing, including to the Agarkar Research Institute, in Poona.',
    'At first, the scientists suspected a red-pigmented alga called Dunaliella.':
        'At first, the scientists suspected a red-pigmented alga, called Doona-lee-ella.',
    'But the answer was haloarchaea: salt-loving microbes that make a pink pigment.':
        'But the answer was halo-ar-kee-a: salt-loving microbes that make a pink pigment.',
    'Then the monsoon arrived. Rain diluted the lake, and the salt and pH came down…':
        'Then the monsoon arrived. Rain diluted the lake, and the salt and P H came down,',
    '…the pink material settled to the bottom, and the lake slowly turned green again.':
        'the pink material settled to the bottom, and the lake slowly turned green again.',
    'In 2020, Lonar was also added to the Ramsar list of wetlands of international importance.':
        'In twenty twenty, Lonar was also added to the Ramsar list of wetlands of international importance.',
    'A bowl punched into lava rock, a lake that can change colour in days…':
        'A bowl punched into lava rock, a lake that can change colour in days,',
    '…and an age that scientists are still arguing about.': 'and an age that scientists are still arguing about.',
}


def SFX(tr, G):
    tr.wind([(0, 0.7), (G('c02', 0), 0.6), (G('c03', 0), 0.4), (G('c05', 0), 0.3), (G('c06', 0), 0.4),
             (G('c08', 0), 0.6), (G('c10', 0), 0.3), (G('c11', 0), 0.7), (G('c13', 0), 0.6), (G('c15', 0), 0.4),
             (G('c17', 0), 0.5), (G('c18', 0), 0.8), (G('c19', 0), 0.3), (G('c20', 0), 0.7), (G('c21', 0), 0.6),
             (G('c21', 15.5), 0.6), (G('c21', 16.5), 0.0)])
    tr.waves(G('c01', 0), G('c01', 14.0), 0.10)
    tr.whoosh(G('c03', 0.2), G('c03', 4.0), 0.06, 300, 1200)
    tr.rumble(G('c05', 0.0), G('c05', 9.0), 0.22)
    tr.crackle(G('c05', 0.0), G('c05', 8.0), 0.12)
    tr.whoosh(G('c06', 0.2), G('c06', 1.0), 0.10, 400, 2000)
    tr.rumble(G('c07', 0.2), G('c07', 2.5), 0.12)
    tr.whoosh(G('c07', 7.5), G('c07', 9.5), 0.15)
    tr.rumble(G('c08', 1.5), G('c08', 6.0), 0.10)
    tr.snaps(G('c09', 0.3), G('c09', 1.6), 12, 0.10)
    tr.whoosh(G('c11', 0.5), G('c11', 3.2), 0.25)
    tr.boom(G('c11', 3.2), 0.95)
    tr.rumble(G('c11', 3.3), G('c11', 8.0), 0.25)
    tr.snaps(G('c11', 3.3), G('c11', 5.5), 40, 0.12)
    tr.waves(G('c17', 0), G('c17', 4.0), 0.08)
    tr.gurgle(G('c19', 0.3), G('c19', 1.8), 0.10)
    tr.crackle(G('c20', 0.3), G('c20', 8.5), 0.12)   # hiss of rain
    tr.waves(G('c20', 3.0), G('c20', 8.5), 0.10)
    tr.waves(G('c21', 0), G('c21', 14.0), 0.08)

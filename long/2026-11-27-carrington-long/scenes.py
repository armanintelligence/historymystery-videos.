"""Long video: The Carrington Event, full story (1920x1080). Build with HM_FORMAT=long.
Visuals: the Sun, skies, auroras, maps, telegraph objects, a campfire, charts, a globe, orbit diagrams.
No people, animals or birds."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

assert W == 1920, 'build with HM_FORMAT=long'
GREEN = (90, 255, 150)
RED = (255, 80, 80)
F_TITLE = font('InterDisplay-Black.otf', 132)
F_MONO = font('Inter-SemiBold.otf', 34)
VB = 830  # bottom of the visual area (captions sit below)
XS = np.arange(W, dtype=np.float32)
YS = np.arange(H, dtype=np.float32)[:, None]


def new(bg=BG):
    img = Image.new('RGB', (W, H), bg)
    return img, ImageDraw.Draw(img, 'RGBA')


def sky(d, top=(4, 6, 13), bot=(14, 24, 51), ymax=H):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=tuple(int(lerp(a, b, k)) for a, b in zip(top, bot)))


def A(c, a):
    return c + (int(255 * max(0, min(1, a))),)


def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0, int(170 * a)))


def aurora(arr, t, base=420, height=320, k=1.0, ymax=VB, red=0.8):
    """Curtain aurora added to a float array (rows above ymax only). Green at the foot, red higher up."""
    if k <= 0:
        return
    ys = YS[:ymax]
    foot = base + 40 * np.sin(XS / 230 + t * 0.55) + 20 * np.sin(XS / 83 - t * 0.9)
    col = (0.55 + 0.45 * np.sin(XS / 31 + t * 1.3) * np.sin(XS / 101 - t * 0.4)) ** 2
    q = (foot[None, :] - ys) / height
    inside = (q > -0.06) & (q < 1.6)
    g = np.where(q >= 0, np.exp(-q * 3.2), np.exp(np.minimum(q, 0) * 40)) * inside
    qq = np.clip(q - 0.35, 0, None)
    r = qq * np.exp(-qq * 1.6) * inside * red
    sub = arr[:ymax]
    sub += (g * col[None, :] * k)[..., None] * np.array(GREEN, np.float32) * 0.55
    sub += (r * col[None, :] * k)[..., None] * np.array(RED, np.float32) * 0.9


rngS = np.random.default_rng(9)
SPOTS = [(rngS.uniform(-0.5, 0.5), rngS.uniform(-0.3, 0.3), rngS.uniform(0.02, 0.09)) for _ in range(14)]


def sun_disc(d, cx, cy, r, spots=1.0):
    for i in range(30, 0, -1):
        k = i / 30
        c = (int(255 * (0.75 + 0.25 * (1 - k))), int(205 * (0.65 + 0.35 * (1 - k))), int(120 * (0.5 + 0.5 * (1 - k))))
        d.ellipse([cx - r * k, cy - r * k, cx + r * k, cy + r * k], fill=c)
    for i, (sx, sy, sr) in enumerate(SPOTS):
        if i / len(SPOTS) >= spots:
            break
        x, y, s = cx + sx * r, cy + sy * r, sr * r
        d.ellipse([x - s, y - s * 0.8, x + s, y + s * 0.8], fill=(120, 70, 35))
        d.ellipse([x - s * 0.5, y - s * 0.4, x + s * 0.5, y + s * 0.4], fill=(55, 30, 18))


def pole(d, x, gy, h, col=(26, 30, 40)):
    d.rectangle([x - 6, gy - h, x + 6, gy], fill=col)
    d.rectangle([x - 46, gy - h + 18, x + 46, gy - h + 30], fill=col)
    for dx in (-36, 36):
        d.ellipse([x + dx - 7, gy - h + 8, x + dx + 7, gy - h + 20], fill=col)


def ortho(lon, lat, lon0, lat0, gc, gr):
    lo, la = np.radians(lon), np.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    x = np.cos(la) * np.sin(lo - l0)
    y = math.cos(p0) * np.sin(la) - math.sin(p0) * np.cos(la) * np.cos(lo - l0)
    z = math.sin(p0) * np.sin(la) + math.cos(p0) * np.cos(la) * np.cos(lo - l0)
    n = np.hypot(x, y) + 1e-9
    x = np.where(z < 0, x / n, x); y = np.where(z < 0, y / n, y)
    return gc[0] + x * gr, gc[1] - y * gr, z


def globe(d, gc, gr, lon0, lat0=30, land=(46, 84, 62), sea=(14, 40, 78)):
    d.ellipse([gc[0] - gr, gc[1] - gr, gc[0] + gr, gc[1] + gr], fill=sea)
    for p in GEO['l']['land']:
        x, y, z = ortho(p[:, 0], p[:, 1], lon0, lat0, gc, gr)
        if (z > 0).any() and len(p) > 2:
            d.polygon(list(zip(x.tolist(), y.tolist())), fill=land)


# ---------- 1. cold open: wires spark under an aurora ----------
POLES = [(-80, 300), (360, 270), (800, 245), (1240, 222), (1680, 200), (2120, 180)]
GY1 = VB - 20
rng1 = np.random.default_rng(5)
SPARKS1 = [(rng1.uniform(0.6, 13.0), int(rng1.integers(0, 5)), rng1.uniform(0.1, 0.9)) for _ in range(50)]

def c01(t):
    img, d = new()
    sky(d, ymax=VB)
    draw_stars(d, t, 0.6, ymax=VB)
    arr = to_arr(img)
    aurora(arr, t, base=330, height=300, k=ramp(t, 0.0, 2.0), red=1.3)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.polygon([(0, GY1 - 30)] + [(x, GY1 - 30 - 22 * math.sin(x / 260)) for x in range(0, W + 1, 20)] + [(W, H), (0, H)], fill=(6, 9, 12))
    d.rectangle([0, GY1, W, H], fill=(5, 7, 10))
    tops = []
    for x, h in POLES:
        pole(d, x, GY1, h)
        tops.append((x, GY1 - h + 24))
    for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
        for dx in (-36, 36):
            d.line([(lerp(x0 + dx, x1 + dx, i / 30), lerp(y0, y1, i / 30) + 34 * math.sin(math.pi * i / 30)) for i in range(31)],
                   fill=(34, 40, 52), width=3)
    arr = to_arr(img)
    for ts, seg, u in SPARKS1:
        if 0 <= t - ts < 0.25:
            (x0, y0), (x1, y1) = tops[seg], tops[seg + 1]
            x, y = lerp(x0, x1, u), lerp(y0, y1, u) + 34 * math.sin(math.pi * u)
            f = 1 - (t - ts) / 0.25
            glow(arr, x, y, 26, (170, 210, 255), 1.6 * f)
            glow(arr, x, y, 7, (255, 255, 255), 2.5 * f)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.6, 1.2)
    text_c(d, (W / 2, 230), '1859', F_BIG, A(WHITE, a * 0.92))
    top_label(img, 'SEPTEMBER 1859', ramp(t, 0.2, 0.6))
    return img

CAP01 = [(0, 4.5, 'In September 1859, telegraph wires began to throw sparks.', ['September', '1859,', 'sparks.']),
         (4.5, 8.5, 'Operators got electric shocks, and paper on their desks caught fire.', ['shocks,', 'fire.']),
         (8.5, 13.5, 'And the night sky glowed red and green, as far south as the Caribbean.', ['red', 'green,', 'Caribbean.'])]

# ---------- 2. title ----------
def c02(t):
    img, d = new()
    draw_stars(d, t, 0.8)
    arr = to_arr(img)
    glow(arr, -60, 470, 420, (255, 150, 60), 0.9)
    glow(arr, -60, 470, 160, (255, 235, 190), 1.2)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.2, 0.9)
    text_c(d, (W / 2 + 60, 400), 'THE CARRINGTON EVENT', F_TITLE, A(WHITE, a))
    text_c(d, (W / 2 + 60, 530), 'The biggest solar storm ever recorded', F_MED, A(AMBER, ramp(t, 0.8, 1.4)))
    return img

CAP02 = [(0, 4, 'This is the Carrington Event, the biggest solar storm ever recorded…', ['Carrington', 'Event,']),
         (4, 8, '…and the reason scientists keep a constant watch on the Sun.', ['watch', 'Sun.'])]

# ---------- 3. map: Redhill ----------
REDHILL, LONDON = (-0.17, 51.24), (-0.13, 51.51)

def c03(t):
    k = ease(ramp(t, 0.0, 4.5))
    cam = Cam(lerp(-15, REDHILL[0], k), lerp(45, REDHILL[1] + 0.12, k), math.exp(lerp(math.log(9), math.log(420), k)))
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 4.0, 4.5)
    if a > 0:
        x, y = cam.xy(*REDHILL)
        pr = 30 + 40 * ((t - 4.0) % 1.2) / 1.2
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=A(AMBER, 0.8 * (1 - ((t - 4.0) % 1.2) / 1.2)), width=4)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=A(AMBER, a))
        d.text((x + 30, y - 10), 'REDHILL', font=F_LABEL, fill=A(WHITE, a), anchor='ls')
        d.text((x + 30, y + 24), 'Surrey', font=F_SMALL, fill=A(GREY, a), anchor='lt')
        lx, ly = cam.xy(*LONDON)
        d.ellipse([lx - 9, ly - 9, lx + 9, ly + 9], fill=A(CYAN, a))
        d.text((lx + 24, ly), 'LONDON', font=F_SMALL, fill=A(CYAN, a), anchor='lm')
    a2 = ramp(t, 5.0, 5.5)
    if a2 > 0:
        card(d, 160, 640, 900, 780, a2)
        d.text((200, 690), 'RICHARD CARRINGTON', font=F_LABEL, fill=A(AMBER, a2), anchor='lm')
        d.text((200, 740), 'astronomer · 33 years old in 1859', font=F_SMALL, fill=A(WHITE, a2), anchor='lm')
    top_label(img, 'CHAPTER 1 · THE SUNSPOT WATCHER')
    return img

CAP03 = [(0, 4, 'Richard Carrington was a thirty-three-year-old astronomer with his own observatory…', ['Richard', 'Carrington']),
         (4, 6.5, '…at Redhill, in Surrey, not far from London.', ['Redhill,', 'Surrey,']),
         (6.5, 10.5, 'On every clear day, he made careful maps of the dark spots on the Sun.', ['maps', 'spots']),
         (10.5, 14, 'Years later, he would show that the Sun spins faster at its equator than at its poles.', ['faster', 'equator'])]

# ---------- 4-5. the projected Sun ----------
SC, SRAD = (1000, 470), 250
FLARE = (SC[0] + 70, SC[1] - 40)

def observatory(d, t, spots=1.0):
    d.rectangle([0, 800, W, H], fill=(40, 30, 24))
    d.rectangle([0, 800, W, 814], fill=(60, 46, 34))
    d.rectangle([700, 140, 1300, 790], fill=(225, 222, 210))
    d.rectangle([700, 140, 1300, 790], outline=(90, 80, 70), width=8)
    d.polygon([(260, -40), (360, -80), (640, 250), (560, 300)], fill=(70, 60, 50))
    d.polygon([(560, 300), (640, 250), (665, 272), (585, 322)], fill=(110, 95, 70))
    d.polygon([(625, 290), (SC[0] - SRAD, SC[1]), (SC[0], SC[1] + SRAD), (SC[0] + SRAD, SC[1])], fill=(255, 230, 170, 22))
    sun_disc(d, *SC, SRAD)
    # drawing sheet on the right
    d.polygon([(1420, 300), (1830, 280), (1850, 760), (1440, 780)], fill=(236, 230, 214))
    cx, cy, r = 1636, 530, 170
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 70, 60), width=3)
    for i, (sx, sy, sr) in enumerate(SPOTS):
        if i / len(SPOTS) >= spots:
            break
        x, y, s = cx + sx * r, cy + sy * r, max(sr * r, 3)
        d.ellipse([x - s, y - s * 0.8, x + s, y + s * 0.8], fill=(50, 45, 40))
    # pencil (an object)
    pi = int(spots * len(SPOTS)) % len(SPOTS)
    px, py = cx + SPOTS[pi][0] * r, cy + SPOTS[pi][1] * r
    d.line([px, py, px + 120, py + 150], fill=(200, 150, 60), width=12)
    d.line([px, py, px + 12, py + 15], fill=(40, 40, 40), width=6)


def c04(t):
    img, d = new((18, 20, 28))
    observatory(d, t, spots=0.3 + 0.7 * ramp(t, 0.5, 9.0))
    a = ramp(t, 7.5, 8.0)
    if a > 0:
        card(d, 640, 150, 1360, 240, a)
        text_c(d, (1000, 195), '1 SEPTEMBER 1859 · MORNING', F_LABEL, A(AMBER, a))
    top_label(img, 'HE NEVER LOOKED AT THE SUN DIRECTLY')
    return img

CAP04 = [(0, 4.5, 'He never looked straight at the Sun. He projected its image from his telescope onto a white screen…', ['projected', 'screen…']),
         (4.5, 6.5, '…and drew the spots by hand.', ['drew']),
         (6.5, 10.5, 'On the morning of September 1st, 1859, a cluster of enormous sunspots was crossing the Sun.', ['September', '1st,', 'enormous'])]


def c05(t):
    img, d = new((18, 20, 28))
    observatory(d, t, 1.0)
    arr = to_arr(img)
    f = ramp(t, 0.4, 0.8) * (1 - 0.75 * ramp(t, 6.0, 8.0)) * (1 - ramp(t, 10.0, 11.5))
    if f > 0:
        flick = 0.85 + 0.15 * math.sin(t * 30)
        for dx, dy in ((0, 0), (40, 22)):
            glow(arr, FLARE[0] + dx, FLARE[1] + dy, 30, (255, 255, 255), 2.2 * f * flick)
            glow(arr, FLARE[0] + dx, FLARE[1] + dy, 70, (255, 240, 210), 0.6 * f)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.9, 1.3) * (1 - ramp(t, 5.5, 6.0))
    if a > 0:
        d.line([FLARE[0] + 60, FLARE[1] - 40, 1180, 230], fill=A(AMBER, a), width=4)
        card(d, 1000, 150, 1700, 230, a)
        text_c(d, (1350, 190), 'TWO PATCHES OF WHITE LIGHT', F_LABEL, A(AMBER, a))
    a2 = ramp(t, 6.5, 7.0)
    if a2 > 0:
        card(d, 480, 150, 1520, 290, a2)
        text_c(d, (1000, 195), 'BACK WITHIN 60 SECONDS:', F_SMALL, A(GREY, a2))
        text_c(d, (1000, 250), '“much changed and enfeebled”', font('InterDisplay-Bold.otf', 54), A(WHITE, a2))
    top_label(img, 'JUST BEFORE NOON')
    return img

CAP05 = [(0, 4.5, 'Just before noon, two patches of intensely bright, white light broke out among the spots.', ['intensely', 'bright,', 'white']),
         (4.5, 6.5, 'Carrington ran to call someone to witness it.', ['witness']),
         (6.5, 10, 'He was back within sixty seconds, and it was already much changed and enfeebled.', ['sixty', 'enfeebled.']),
         (10, 12, 'Very shortly afterwards, the last trace was gone.', ['gone.'])]

# ---------- 6. Hodgson, five minutes ----------
def c06(t):
    img, d = new()
    draw_stars(d, t, 0.5)
    sc = (620, 470)
    arr = to_arr(img)
    glow(arr, sc[0], sc[1], 360, (255, 140, 50), 0.35)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    sun_disc(d, sc[0], sc[1], 290)
    arr = to_arr(img)
    f = 1 - ramp(t, 0.5, 5.0)
    fx, fy = sc[0] + 81, sc[1] - 46
    glow(arr, fx, fy, 40, (255, 255, 255), 2.4 * f)
    glow(arr, fx + 46, fy + 25, 36, (255, 255, 255), 2.0 * f)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    k = ramp(t, 0.5, 5.0)
    d.arc([1240, 180, 1480, 420], -90, -90 + 360 * k, fill=AMBER, width=12)
    text_c(d, (1360, 300), f'{int(5 * k + 1e-4)} min' if k < 1 else '5 min', F_MED, WHITE)
    d.text((1360, 450), 'Richard Hodgson, London', font=F_SMALL, fill=GREY, anchor='mt')
    a = ramp(t, 6.0, 6.4)
    if a > 0:
        card(d, 1010, 560, 1800, 680, a)
        text_c(d, (1405, 620), 'FIRST SOLAR FLARE EVER RECORDED', F_LABEL, A(AMBER, a))
    top_label(img, 'A SECOND WITNESS')
    return img

CAP06 = [(0, 3.5, 'In London, another amateur astronomer, Richard Hodgson, saw it too.', ['Richard', 'Hodgson,']),
         (3.5, 5.5, 'He said it lasted about five minutes.', ['five', 'minutes.']),
         (5.5, 8.5, 'It was the first solar flare ever recorded.', ['first', 'solar', 'flare'])]

# ---------- 7. the magnetic jolt ----------
rng7 = np.random.default_rng(17)
TRACE = np.cumsum(rng7.normal(0, 1.2, 600))
TRACE = TRACE - np.convolve(TRACE, np.ones(80) / 80, mode='same')

def c07(t):
    img, d = new()
    px0, px1, py0, py1 = 160, 1760, 330, 790
    d.rectangle([px0, py0, px1, py1], fill=(232, 228, 214))
    for x in range(px0, px1, 80):
        d.line([x, py0, x, py1], fill=(205, 200, 185), width=2)
    for y in range(py0, py1, 60):
        d.line([px0, y, px1, y], fill=(205, 200, 185), width=2)
    k = ramp(t, 0.3, 7.0)
    n = int(600 * k)
    xs = np.linspace(px0 + 20, px1 - 20, 600)
    jump = np.where(np.arange(600) > 330, 1.0, 0.0) * 120 * np.exp(-np.clip(np.arange(600) - 330, 0, None) / 55)
    ys = (py0 + py1) / 2 + TRACE * 3 - jump
    if n > 1:
        d.line(list(zip(xs[:n].tolist(), ys[:n].tolist())), fill=(40, 40, 60), width=4)
    a = ramp(t, 4.5, 5.0)
    if a > 0:
        x = xs[340]
        d.ellipse([x - 70, ys[345] - 70, x + 70, ys[345] + 70], outline=A((210, 30, 30), a), width=6)
        d.text((x + 90, py0 + 40), 'sudden jolt', font=F_LABEL, fill=A((170, 30, 30), a), anchor='lm')
    d.text((px0, py0 - 20), 'MAGNETIC RECORD, NEAR LONDON (illustration)', font=F_SMALL, fill=GREY, anchor='ls')
    # light travel diagram at top
    arr = to_arr(img)
    glow(arr, 220, 190, 40, (255, 170, 80), 1.2)
    a2 = ramp(t, 7.0, 7.5)
    if a2 > 0:
        e = ramp(t, 7.5, 10.0)
        glow(arr, lerp(260, 1660, e), 190, 10, (255, 255, 255), 1.6 * a2)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([1680, 165, 1730, 215], fill=(20, 60, 120))
    d.text((220, 250), 'SUN', font=F_SMALL, fill=AMBER, anchor='mt')
    d.text((1705, 250), 'EARTH', font=F_SMALL, fill=CYAN, anchor='mt')
    if a2 > 0:
        text_c(d, (960, 150), 'flare light: about 8 minutes', F_LABEL, A(WHITE, a2))
    top_label(img, 'CHAPTER 2 · A TWITCH IN THE NEEDLE')
    return img

CAP07 = [(0, 2.5, 'At that same moment, something else happened.', ['same', 'moment,']),
         (2.5, 5, 'Magnetic instruments near London, which tracked the Earth’s magnetic field…', ['magnetic', 'field…']),
         (5, 6.5, '…recorded a sudden disturbance.', ['sudden', 'disturbance.']),
         (6.5, 11, 'Light from the flare had reached Earth in about eight minutes, and jolted the upper atmosphere.', ['eight', 'minutes,'])]

# ---------- 8. calendar ----------
DAYS = [('28', 'AUG'), ('29', 'AUG'), ('30', 'AUG'), ('31', 'AUG'), ('1', 'SEP'), ('2', 'SEP')]

def c08(t):
    img, d = new()
    x0, w_, y0, h_ = 210, 250, 260, 300
    for i, (dn, mo) in enumerate(DAYS):
        a = ramp(t, 0.3 + i * 0.25, 0.6 + i * 0.25)
        x = x0 + i * (w_ + 10)
        hl = (i == 0 and t > 2.5) or (i == 4 and t > 0.5) or (i == 5 and t > 9.5)
        col = AMBER if i in (0, 4) else RED
        d.rounded_rectangle([x, y0, x + w_, y0 + h_], radius=18, fill=A((20, 28, 44), a), outline=A(col if hl else (60, 80, 110), a), width=6 if hl else 3)
        d.text((x + w_ / 2, y0 + 50), mo, font=F_LABEL, fill=A(GREY, a), anchor='mm')
        d.text((x + w_ / 2, y0 + 160), dn, font=F_HUGE, fill=A(WHITE, a), anchor='mm')
    a = ramp(t, 2.5, 3.0)
    d.text((x0 + w_ / 2, y0 + h_ + 50), 'FIRST STORM', font=F_LABEL, fill=A(AMBER, a), anchor='mm')
    d.text((x0 + 4 * (w_ + 10) + w_ / 2, y0 + h_ + 50), 'THE FLARE', font=F_LABEL, fill=A(AMBER, ramp(t, 0.5, 1.0)), anchor='mm')
    a3 = ramp(t, 9.5, 10.0)
    d.text((x0 + 5 * (w_ + 10) + w_ / 2, y0 + h_ + 50), 'THE BIG ONE', font=F_LABEL, fill=A(RED, a3), anchor='mm')
    top_label(img, 'AUGUST – SEPTEMBER 1859')
    return img

CAP08 = [(0, 2.5, 'And it was not the first warning.', ['first', 'warning.']),
         (2.5, 6.5, 'Days earlier, on the night of August 28th, a first solar storm had already struck.', ['August', '28th,']),
         (6.5, 9.5, 'In New Orleans, crowds gathered on street corners to look up at the sky.', ['New', 'Orleans,']),
         (6.5, 9, 'But the worst was still on its way.', ['worst'])]

# ---------- 9. the cloud crosses ----------
rng9 = np.random.default_rng(12)
PUFF = [(rng9.uniform(-1, 1), rng9.uniform(-1, 1), rng9.uniform(0.4, 1)) for _ in range(220)]
EX, EY = 1700, 470

def c09(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    arr = to_arr(img)
    glow(arr, -60, 470, 330, (255, 150, 60), 1.1)
    glow(arr, -60, 470, 140, (255, 235, 190), 1.4)
    e = ease(ramp(t, 1.0, 10.5))
    cx = lerp(220, EX - 40, e)
    spread = lerp(70, 300, e)
    for px, py, w_ in PUFF:
        if px * px + py * py > 1:
            continue
        x = cx + px * spread * 0.5 - abs(py) * spread * 0.35
        y = 470 + py * spread
        glow(arr, x, y, 20 + 16 * e, (255, 160, 90), 0.2 * w_ * (1 - 0.4 * e))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    er = 60
    d.ellipse([EX - er, EY - er, EX + er, EY + er], fill=(20, 60, 120))
    d.chord([EX - er, EY - er, EX + er, EY + er], 200, 330, fill=(40, 90, 60))
    d.arc([EX - er - 40, EY - er - 40, EX + er + 40, EY + er + 40], 110, 250, fill=A(CYAN, 0.5), width=3)
    d.text((EX, EY + 110), 'EARTH', font=F_SMALL, fill=CYAN, anchor='mm')
    d.text((140, 700), 'SUN', font=F_SMALL, fill=AMBER, anchor='mm')
    hrs = 17.5 * e
    card(d, 680, 115, 1240, 255)
    text_c(d, (960, 185), f'{hrs:4.1f} h', F_HUGE, WHITE)
    a = ramp(t, 7.0, 7.5)
    d.line([300, 780, 1600, 780], fill=A(GREY, a), width=3)
    text_c(d, (950, 755), '≈150 million km', F_SMALL, A(GREY, a))
    d.text((1840, 800), 'not to scale', font=F_SMALL, fill=GREY, anchor='rm')
    top_label(img, 'CHAPTER 3 · SEVENTEEN AND A HALF HOURS')
    return img

CAP09 = [(0, 3.5, 'The flare had come with a vast cloud of charged gas, hurled out from the Sun.', ['charged', 'gas,']),
         (3.5, 6, 'Today, scientists call it a coronal mass ejection.', ['coronal', 'mass', 'ejection.']),
         (6, 10.5, 'It crossed a hundred and fifty million kilometres to Earth in about seventeen and a half hours.', ['seventeen', 'half', 'hours.'])]

# ---------- 10. how fast ----------
def c10(t):
    img, d = new()
    a0 = ramp(t, 0.3, 0.8)
    card(d, 610, 130, 1310, 300, a0)
    text_c(d, (960, 200), '≈2,500 km/s', F_HUGE, A(AMBER, a0))
    text_c(d, (960, 270), 'the 1859 cloud', F_SMALL, A(GREY, a0))
    rows = [('CARRINGTON, 1859', 17.5, 17.5, AMBER, 3.5), ('FASTEST CLOUDS TODAY', 15, 18, CYAN, 5.0), ('SLOWER CLOUDS', 72, 96, GREY, 7.0)]
    x0, sc = 640, 13.0  # px per hour
    for i, (lab, lo, hi, col, t0) in enumerate(rows):
        y = 420 + i * 120
        a = ramp(t, t0, t0 + 0.4)
        k = ease(ramp(t, t0, t0 + 1.2))
        d.text((x0 - 30, y), lab, font=F_LABEL, fill=A(WHITE, a), anchor='rm')
        end = min(x0 + hi * sc * k, 1840)
        d.rounded_rectangle([x0, y - 26, max(end, x0 + 4), y + 26], radius=10, fill=A(col, 0.85 * a))
        if lo != hi and i == 1:
            d.rectangle([x0 + lo * sc, y - 26, x0 + hi * sc, y + 26], fill=A(WHITE, 0.25 * a))
        txt = f'{lo:g}–{hi:g} h' if (lo != hi and i == 1) else ('several days →' if i == 2 else f'≈{hi:g} h')
        d.text((x0 + 16 if i == 2 else end + 20, y), txt, font=F_LABEL, fill=A(BG if i == 2 else WHITE, a), anchor='lm')
    top_label(img, 'HOW FAST WAS IT?')
    return img

CAP10 = [(0, 3.5, 'That is roughly two and a half thousand kilometres every second.', ['two', 'half', 'thousand']),
         (3.5, 7, 'Even today, the fastest of these clouds take fifteen to eighteen hours to reach us.', ['fifteen', 'eighteen']),
         (7, 9.5, 'Slower ones take several days.', ['several', 'days.'])]

# ---------- 11. aurora map ----------
PLACES = [('BOSTON', -71.06, 42.36), ('CUBA', -79.5, 21.8), ('JAMAICA', -77.3, 18.1), ('VENEZUELA', -66.6, 7.5)]

def c11(t):
    cam = Cam(-75, 30, 11.5)
    img = draw_map(Image.new('RGB', (W, H)), cam, land=(26, 34, 48), coast=(66, 82, 108), water=(6, 10, 20))
    arr = to_arr(img)
    lat_edge = lerp(68, 6, ease(ramp(t, 3.0, 9.0)))
    edge_y = float(cam.xy(0, lat_edge)[1])
    wob = 18 * np.sin(XS / 120 + t * 1.5)
    ys = YS[:VB]
    dy = ys - (edge_y + wob[None, :])
    band = np.clip(1 + dy / 60, 0, 1) * np.where(dy < 0, np.exp(dy / 240), np.clip(1 - dy / 60, 0, 1)) * 1.4
    shimmer = (0.75 + 0.25 * np.sin(XS / 41 + t * 2))[None, :]
    arr[:VB] += (band * shimmer * 0.5)[..., None] * (np.array(GREEN, np.float32) * 0.6 + np.array(RED, np.float32) * 0.35)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    for i, (name, lo, la) in enumerate(PLACES):
        x, y = cam.xy(lo, la)
        a = ramp(t, 6.5 + i * 0.7, 6.9 + i * 0.7) if i else ramp(t, 4.0, 4.4)
        if a > 0:
            d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=A(AMBER, a))
            d.text((x + 24, y), name, font=F_LABEL, fill=A(WHITE, a), anchor='lm')
    a = ramp(t, 0.3, 0.8) * (1 - ramp(t, 2.8, 3.2))
    if a > 0:
        card(d, 610, 380, 1310, 520, a)
        text_c(d, (960, 450), '2 SEPTEMBER 1859', F_MED, A(WHITE, a))
    top_label(img, 'CHAPTER 4 · THE SKY ON FIRE')
    return img

CAP11 = [(0, 3, 'In the early hours of September 2nd, the cloud hit the Earth.', ['September', '2nd,', 'hit']),
         (3, 6.5, 'Auroras, normally seen near the poles, spread toward the equator.', ['Auroras,', 'equator.']),
         (6.5, 10.5, 'They were seen over Cuba and Jamaica, and as far south as Venezuela.', ['Cuba', 'Jamaica,', 'Venezuela.'])]

# ---------- 12. Rocky Mountains campfire ----------
rng12 = np.random.default_rng(3)
RIDGE_A = [(x, 520 - 220 * abs(math.sin(x / 330 + 0.6)) - rng12.uniform(0, 40)) for x in range(-40, W + 80, 60)]
RIDGE_B = [(x, 660 - 130 * abs(math.sin(x / 240 + 2.0)) - rng12.uniform(0, 30)) for x in range(-40, W + 80, 50)]
FIRE = (1180, 770)

def c12(t):
    img, d = new()
    sky(d, bot=(14, 30, 34), ymax=VB)
    draw_stars(d, t, 0.4, ymax=VB)
    arr = to_arr(img)
    aurora(arr, t * 1.1, base=330, height=260, k=1.25, red=1.0)
    arr[:VB] += (np.clip(1 - YS[:VB] / 820, 0, 1) * 18)[..., None] * np.array([0.6, 1.0, 0.8], np.float32)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.polygon(RIDGE_A + [(W + 80, H), (-40, H)], fill=(18, 24, 34))
    for x, y in RIDGE_A[1:-1:3]:
        d.polygon([(x - 26, y + 28), (x + 26, y + 28), (x, y)], fill=(170, 185, 200, 120))
    d.polygon(RIDGE_B + [(W + 80, H), (-40, H)], fill=(10, 14, 20))
    d.rectangle([0, 790, W, H], fill=(8, 10, 14))
    for x in range(-20, W + 40, 42):
        if abs(x - FIRE[0]) > 220:
            conifer(d, x, 796, 80 + 60 * ((x * 37) % 11) / 11, (6, 9, 12))
    fx, fy = FIRE
    for dx in (-50, 0, 50):
        d.line([fx + dx - 30, fy + 34, fx + dx + 30, fy + 20], fill=(70, 50, 32), width=10)
    arr = to_arr(img)
    fl = 0.8 + 0.2 * math.sin(t * 17) * math.sin(t * 7.3)
    k = ramp(t, 0.5, 2.0)
    glow(arr, fx, fy, 90, (255, 120, 40), 0.9 * fl * k)
    glow(arr, fx, fy + 5, 30, (255, 220, 140), 1.6 * fl * k)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.line([fx - 120, fy - 60, fx + 120, fy - 60], fill=(40, 40, 44), width=6)
    d.polygon([(fx - 95, fy - 56), (fx - 55, fy - 56), (fx - 62, fy - 110), (fx - 88, fy - 110)], fill=(60, 64, 70))
    d.line([fx - 88, fy - 110, fx - 104, fy - 124], fill=(60, 64, 70), width=6)
    d.ellipse([fx + 20, fy - 70, fx + 110, fy - 48], fill=(34, 34, 38))
    d.line([fx + 110, fy - 60, fx + 175, fy - 70], fill=(34, 34, 38), width=8)
    if t > 2.0:
        for j in range(3):
            q = ((t - 2.0) * 0.4 + j / 3) % 1
            d.ellipse([fx - 75 - 10 + 10 * math.sin(q * 6 + j), fy - 130 - q * 120 - 10, fx - 75 + 10 + 10 * math.sin(q * 6 + j), fy - 130 - q * 120 + 10],
                      fill=(200, 200, 210, int(80 * (1 - q))))
    a = ramp(t, 3.5, 4.0)
    if a > 0:
        card(d, 300, 160, 760, 270, a)
        text_c(d, (530, 215), 'DAWN?', F_MED, A(AMBER, a))
    top_label(img, 'ROCKY MOUNTAINS')
    return img

CAP12 = [(0, 3.5, 'In the Rocky Mountains, gold miners woke up and started making breakfast…', ['gold', 'miners', 'breakfast…']),
         (3.5, 5.5, '…sure that it was already dawn.', ['dawn.'])]

# ---------- 13. newspaper by aurora light ----------
rng13 = np.random.default_rng(21)
ROOFS = []
_x = -20
while _x < W + 20:
    _w = rng13.uniform(80, 170); _h = rng13.uniform(110, 260)
    ROOFS.append((_x, _w, _h, rng13.random() < 0.25)); _x += _w + rng13.uniform(0, 8)

def c13(t):
    img, d = new()
    sky(d, bot=(26, 18, 34), ymax=VB)
    draw_stars(d, t, 0.3, ymax=VB)
    arr = to_arr(img)
    aurora(arr, t, base=330, height=300, k=1.0, red=1.8)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    gy = VB
    for x, w_, h_, steeple in ROOFS:
        d.rectangle([x, gy - h_, x + w_, gy], fill=(10, 12, 18))
        if steeple:
            d.polygon([(x + w_ * 0.3, gy - h_), (x + w_ * 0.7, gy - h_), (x + w_ * 0.5, gy - h_ - 80)], fill=(10, 12, 18))
        for wy in range(int(gy - h_ + 20), gy - 20, 44):
            for wx in range(int(x + 14), int(x + w_ - 20), 30):
                if (wx * 7 + wy * 3) % 5 == 0:
                    d.rectangle([wx, wy, wx + 12, wy + 18], fill=(90, 70, 40))
    d.rectangle([0, gy, W, H], fill=(8, 9, 12))
    a = ease(ramp(t, 1.0, 2.0))
    if a > 0:
        ox, y0 = lerp(2300, 1340, a), 400
        paper = (232, 226, 208, int(255 * a))
        d.polygon([(ox - 300, y0), (ox + 300, y0 - 24), (ox + 314, y0 + 380), (ox - 286, y0 + 404)], fill=paper)
        d.text((ox, y0 + 55), 'THE MORNING NEWS', font=F_LABEL, fill=(30, 30, 30, int(255 * a)), anchor='mm')
        for i in range(8):
            w_ = 480 if i % 3 else 380
            yy = y0 + 110 + i * 32 - 8 * (i / 8)
            d.rectangle([ox - 240, yy, ox - 240 + w_, yy + 14], fill=(120, 115, 105, int(255 * a)))
        d.polygon([(ox - 300, y0), (ox + 300, y0 - 24), (ox + 314, y0 + 380), (ox - 286, y0 + 404)], fill=(255, 60, 80, int(30 * a)))
    a2 = ramp(t, 2.5, 3.0)
    if a2 > 0:
        card(d, 220, 160, 760, 270, a2)
        text_c(d, (490, 215), 'PAST MIDNIGHT', F_MED, A(WHITE, a2))
    top_label(img, 'NORTHEASTERN UNITED STATES')
    return img

CAP13 = [(0, 4.5, 'In the northeastern United States, people could read newspapers outdoors, well past midnight.', ['newspapers', 'midnight.']),
         (4.5, 6.5, 'In Boston, some of them did just that.', ['Boston,'])]

# ---------- 14. telegraph office ----------
rng14 = np.random.default_rng(31)
SPARKS14 = sorted(rng14.uniform(0.3, 12.0, 46))

def telegraph_desk(d):
    d.rectangle([0, 700, W, H], fill=(52, 36, 24))
    d.rectangle([0, 700, W, 718], fill=(78, 56, 36))
    d.rectangle([520, 560, 930, 700], fill=(60, 50, 40))
    d.rectangle([520, 560, 930, 576], fill=(90, 74, 56))
    for cx in (620, 700):
        d.rounded_rectangle([cx - 30, 410, cx + 30, 560], radius=10, fill=(150, 90, 50))
        for yy in range(420, 550, 12):
            d.line([cx - 30, yy, cx + 30, yy], fill=(120, 70, 40), width=3)
    d.rectangle([570, 395, 850, 412], fill=(110, 110, 118))
    for tx in (550, 900):
        d.ellipse([tx - 16, 540, tx + 16, 572], fill=(200, 160, 70))
    d.line([900, 556, 1050, 480, 1500, 380, 1940, 330], fill=(30, 30, 34), width=6)
    d.line([550, 556, 420, 470, -20, 420], fill=(30, 30, 34), width=6)
    # key on the left
    d.rectangle([180, 650, 380, 700], fill=(60, 50, 40))
    d.line([200, 640, 360, 620], fill=(150, 150, 160), width=10)
    d.ellipse([340, 600, 380, 640], fill=(30, 30, 30))


def c14(t):
    img, d = new((14, 14, 20))
    telegraph_desk(d)
    burn = ramp(t, 4.0, 8.0)
    d.polygon([(800, 560), (1310, 600), (1310, 646), (800, 606)], fill=(232, 226, 208))
    for i in range(14):
        x0 = 850 + i * 32
        if (i * 5) % 3:
            d.rectangle([x0, 583 + i * 2.5, x0 + 18, 587 + i * 2.5], fill=(40, 40, 40))
    if burn > 0:
        bx = lerp(1310, 970, burn)
        d.polygon([(bx, 560 + (bx - 800) * 40 / 510), (1310, 600), (1310, 646), (bx, 606 + (bx - 800) * 40 / 510)], fill=(30, 22, 16))
    arr = to_arr(img)
    for ts in SPARKS14:
        if 0 <= t - ts < 0.2:
            f = 1 - (t - ts) / 0.2
            for sx, sy in ((550, 556), (900, 556)):
                glow(arr, sx, sy, 34, (170, 210, 255), 1.5 * f)
                glow(arr, sx, sy, 9, (255, 255, 255), 2.4 * f)
    if burn > 0:
        bx = lerp(1310, 970, burn)
        fl = 0.8 + 0.2 * math.sin(t * 19)
        glow(arr, bx, 605 + (bx - 800) * 40 / 510 - 20, 50, (255, 120, 40), 1.2 * fl)
        glow(arr, bx, 605 + (bx - 800) * 40 / 510 - 10, 18, (255, 230, 150), 1.6 * fl)
    # arc of fire from the key, during the Royce line
    if 9.0 <= t < 12.0:
        f = ramp(t, 9.0, 9.3) * (1 - ramp(t, 11.4, 12.0)) * (0.7 + 0.3 * math.sin(t * 40))
        rr = np.random.default_rng(int(t * 20))
        pts = [(360, 620)]
        for j in range(1, 9):
            pts.append((360 - j * 12 + rr.uniform(-14, 14), 620 - j * 30 + rr.uniform(-10, 10)))
        img = to_img(arr); dd = ImageDraw.Draw(img, 'RGBA')
        dd.line(pts, fill=(200, 230, 255, int(255 * f)), width=5)
        arr = to_arr(img)
        for p in pts[::2]:
            glow(arr, p[0], p[1], 26, (150, 200, 255), 0.9 * f)
    img = to_img(arr)
    top_label(img, 'CHAPTER 5 · THE TELEGRAPH GOES WILD')
    return img

CAP14 = [(0, 2, 'Then the telegraph went wild.', ['telegraph', 'wild.']),
         (2, 4.5, 'Some operators got electric shocks from their equipment.', ['electric', 'shocks']),
         (4.5, 7.5, 'Sparks jumped from the machines and set paper ablaze.', ['Sparks', 'ablaze.']),
         (7.5, 12, 'In Washington, operator Frederick Royce took a shock, and an arc of fire jumped from his head.', ['Washington,', 'arc', 'fire']),
         (12, 15, 'Electricity from the ground was rushing up into poorly grounded equipment.', ['ground', 'grounded'])]

# ---------- 15. gibberish ----------
rng15 = np.random.default_rng(15)
GIB = [''.join(rng15.choice(list('·—  ·—·—#%&?'), 40)) for _ in range(8)]

def c15(t):
    img, d = new((14, 14, 20))
    off = t * 220
    for i in range(6):
        y = 170 + i * 105
        d.rectangle([0, y, W, y + 64], fill=(232, 226, 208))
        s = GIB[i]
        for j, ch in enumerate(s * 3):
            x = (j * 52 - off * (1 + 0.2 * i)) % (W + 400) - 200
            d.text((x, y + 32), ch, font=F_MONO, fill=(50, 50, 60), anchor='mm')
    a = ramp(t, 4.5, 5.0)
    if a > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(150 * a)))
        card(d, 460, 330, 1460, 560, a)
        text_c(d, (960, 410), 'BOSTON · 2 SEPT · 8 AM', F_LABEL, A(GREY, a))
        text_c(d, (960, 490), 'NO SIGNAL IN OR OUT', F_MED, A(RED, a))
    top_label(img, 'GIBBERISH ON THE LINE')
    return img

CAP15 = [(0, 4.5, 'Machines printed gibberish, and many messages could not get through.', ['gibberish,']),
         (4.5, 8.5, 'By 8 a.m. on September 2nd, the Boston office could not send or receive at all.', ['8', 'a.m.', 'Boston'])]

# ---------- 16-17. Boston-Portland ----------
BOS, POR = (-71.06, 42.36), (-70.26, 43.66)

def battery(d, x, y, a, unplugged):
    c = A(WHITE, a)
    d.rounded_rectangle([x - 70, y - 36, x + 60, y + 36], radius=8, outline=c, width=5)
    d.rectangle([x + 60, y - 14, x + 74, y + 14], fill=c)
    d.text((x - 5, y), '+ −', font=F_SMALL, fill=c, anchor='mm')
    if unplugged:
        r = A(RED, a)
        d.line([x - 60, y - 50, x + 64, y + 50], fill=r, width=9)
        d.line([x - 60, y + 50, x + 64, y - 50], fill=r, width=9)


def bp_map(t, aur=0.6):
    cam = Cam(-70.0, 43.0, 380)
    img = draw_map(Image.new('RGB', (W, H)), cam)
    arr = to_arr(img)
    aurora(arr, t, base=200, height=160, k=aur, red=1.2, ymax=420)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    b, p = cam.xy(*BOS), cam.xy(*POR)
    b = (float(b[0]), float(b[1])); p = (float(p[0]), float(p[1]))
    d.line([b, p], fill=GREY, width=4)
    for (x, y), name in ((b, 'BOSTON'), (p, 'PORTLAND, MAINE')):
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=AMBER)
        d.text((x - 30, y), name, font=F_LABEL, fill=WHITE, anchor='rm')
    return img, d, b, p


def bubble(d, x0, y0, who, lines, a, col):
    if a <= 0:
        return
    h = 70 + 50 * len(lines)
    card(d, x0, y0, x0 + 760, y0 + h, a)
    d.text((x0 + 30, y0 + 38), who, font=F_SMALL, fill=A(col, a), anchor='lm')
    for i, s in enumerate(lines):
        d.text((x0 + 30, y0 + 88 + i * 50), s, font=F_LABEL, fill=A(WHITE, a), anchor='lm')


def c16(t):
    img, d, b, p = bp_map(t)
    a = ramp(t, 0.5, 0.9)
    battery(d, b[0] + 120, b[1] - 10, a, t > 11.0)
    battery(d, p[0] + 120, p[1] + 10, a, t > 11.3)
    bubble(d, 1100, 160, 'BOSTON →', ['“Please cut off your battery', 'entirely from the line', 'for fifteen minutes.”'], ramp(t, 4.0, 4.4), AMBER)
    bubble(d, 1100, 510, 'PORTLAND →', ['“Will do so.', 'It is now disconnected.”'], ramp(t, 8.5, 8.9), CYAN)
    top_label(img, 'BOSTON ↔ PORTLAND · 2 SEPT 1859')
    return img

CAP16 = [(0, 4, 'Then operators in Boston and Portland, Maine, tried something strange.', ['Boston', 'Portland,', 'strange.']),
         (4, 8.5, 'Boston asked: “Please cut off your battery entirely from the line for fifteen minutes.”', ['battery', 'fifteen']),
         (8.5, 11.5, 'Portland replied: “Will do so. It is now disconnected.”', ['disconnected.”'])]


def c17(t):
    img, d, b, p = bp_map(t, aur=0.6 + 0.4 * ramp(t, 0, 2))
    battery(d, b[0] + 120, b[1] - 10, 1.0, True)
    battery(d, p[0] + 120, p[1] + 10, 1.0, True)
    for k in range(4):
        q = (t * 0.45 + k / 4) % 1
        if k % 2:
            q = 1 - q
        x, y = lerp(b[0], p[0], q), lerp(b[1], p[1], q)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=CYAN)
    a = ramp(t, 0.5, 1.0)
    card(d, 1100, 160, 1860, 290, a)
    text_c(d, (1480, 225), 'NO BATTERIES · STORM CURRENT', F_LABEL, A(GREEN, a))
    bubble(d, 1100, 330, 'BOSTON →', ['“We can work better', 'without batteries.”'], ramp(t, 5.0, 5.4), AMBER)
    a3 = ramp(t, 9.0, 9.4)
    if a3 > 0:
        card(d, 1100, 590, 1860, 720, a3)
        text_c(d, (1480, 655), 'ABOUT 2 HOURS', F_MED, A(WHITE, a3))
    top_label(img, 'POWERED BY THE STORM')
    return img

CAP17 = [(0, 2.5, 'With no batteries at all, the messages kept going…', ['no', 'batteries']),
         (2.5, 5, '…carried by electric currents that the storm drove through the wires.', ['storm', 'wires.']),
         (5, 8.5, 'Boston’s verdict: “We can work better without batteries.”', ['better', 'without']),
         (8.5, 11, 'They kept talking this way for about two hours.', ['two', 'hours.'])]

# ---------- 18. how big ----------
def c18(t):
    img, d = new()
    y0, scl = 200, 0.33  # y of 0 nT, px per nT
    x0, x1 = 300, 1620
    d.line([x0, y0, x1, y0], fill=GREY, width=3)
    d.text((x0 - 20, y0), '0', font=F_SMALL, fill=GREY, anchor='rm')
    for v in (500, 1000, 1500):
        y = y0 + v * scl
        d.line([x0, y, x1, y], fill=(40, 50, 70), width=2)
        d.text((x0 - 20, y), f'−{v:,}', font=F_SMALL, fill=GREY, anchor='rm')
    d.text((x0 - 20, y0 - 50), 'Dst (nT)', font=F_SMALL, fill=GREY, anchor='rm')
    bars = [('QUEBEC, 1989', 600, CYAN, 9.2), ('1859, REVISED', 900, AMBER, 7.3), ('1859, COLABA READING', 1760, (120, 120, 130), 2.6)]
    bw = 300
    for i, (lab, v, col, t0) in enumerate(bars):
        cx = 520 + i * 450
        k = ease(ramp(t, t0, t0 + 1.2))
        a = ramp(t, t0, t0 + 0.3)
        if a <= 0:
            continue
        bot = y0 + v * scl * k
        if i == 2:
            for yy in range(int(y0), int(bot), 24):
                d.rectangle([cx - bw / 2, yy, cx + bw / 2, min(yy + 12, bot)], fill=A(col, 0.7))
        else:
            d.rectangle([cx - bw / 2, y0, cx + bw / 2, bot], fill=A(col, 0.85))
        d.text((cx, y0 - 30), lab, font=F_SMALL, fill=A(WHITE, a), anchor='ms')
        d.text((cx, bot + 14), f'≈ −{v:,}', font=F_LABEL, fill=A(col if i < 2 else WHITE, ramp(t, t0 + 1.0, t0 + 1.3)), anchor='mt')
    a2 = ramp(t, 5.3, 5.7)
    if a2 > 0:
        card(d, 1250, 370, 1590, 430, a2)
        d.text((1420, 400), 'caught the aurora too?', font=F_SMALL, fill=A(WHITE, a2), anchor='mm')
    a3 = ramp(t, 11.5, 11.9)
    if a3 > 0:
        d.rectangle([0, 110, W, VB], fill=(7, 11, 20, int(190 * a3)))
        card(d, 400, 400, 1520, 540, a3)
        text_c(d, (960, 470), 'STILL DEBATED · STILL THE RECORD', F_MED, A(AMBER, a3))
    top_label(img, 'CHAPTER 6 · HOW BIG WAS IT?')
    return img

CAP18 = [(0, 2.5, 'Scientists rank magnetic storms with a number called Dst. The more negative, the stronger.', ['Dst.', 'negative,']),
         (2.5, 6, 'A reading from Colaba, near Mumbai, once put 1859 at about minus 1,760.', ['Colaba,', '1,760.']),
         (6, 8, 'Later work found that reading had also caught the aurora…', ['aurora…']),
         (8, 9.5, '…and lowered the estimate to about minus 900.', ['900.']),
         (9.5, 12.5, 'The storm that blacked out Quebec in 1989 measured about minus 600.', ['Quebec', '600.']),
         (12.5, 16, 'The exact number is still debated, but 1859 remains the largest magnetic storm on record.', ['debated,', 'largest'])]

# ---------- 19. Quebec 1989 ----------
rng19 = np.random.default_rng(19)
QC_CITIES = [(-71.2, 46.8), (-73.6, 45.5), (-72.5, 46.3), (-71.9, 45.4), (-68.5, 48.4), (-71.1, 48.4), (-77.8, 48.1), (-73.1, 46.0)]
QC_LIGHTS = [(lo + rng19.normal(0, 0.35), la + rng19.normal(0, 0.2)) for lo, la in QC_CITIES for _ in range(14)]

def c19(t):
    cam = Cam(-72.5, 48.0, 70)
    img = draw_map(Image.new('RGB', (W, H)), cam, land=(24, 30, 42), coast=(60, 74, 98), water=(6, 10, 20))
    arr = to_arr(img)
    out = ramp(t, 7.5, 8.3)
    for i, (lo, la) in enumerate(QC_LIGHTS):
        x, y = cam.xy(lo, la)
        flick = 1.0
        if 7.0 < t < 8.3:
            flick = 0.5 + 0.5 * math.sin(t * 40 + i)
        glow(arr, float(x), float(y), 6, (255, 200, 120), 1.1 * (1 - out) * flick)
    # power line pylons as glowing link lines
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    pts = [cam.xy(-77.0, 52.5), cam.xy(-73.6, 45.5)], [cam.xy(-69.5, 51.0), cam.xy(-71.2, 46.8)]
    for (xa, ya), (xb, yb) in pts:
        d.line([float(xa), float(ya), float(xb), float(yb)], fill=A(CYAN, 0.6 * (1 - out)), width=4)
    a = ramp(t, 3.0, 3.4)
    if a > 0:
        card(d, 120, 130, 640, 260, a)
        d.text((160, 170), '13 MARCH 1989', font=F_SMALL, fill=A(GREY, a), anchor='lm')
        d.text((160, 225), '2:44 AM', font=F_MED, fill=A(WHITE, a), anchor='lm')
    a2 = ramp(t, 8.3, 8.7)
    if a2 > 0:
        card(d, 1280, 130, 1840, 260, a2)
        d.text((1320, 170), 'GRID DOWN IN', font=F_SMALL, fill=A(GREY, a2), anchor='lm')
        d.text((1320, 225), '< 1 MINUTE', font=F_MED, fill=A(RED, a2), anchor='lm')
    a3 = ramp(t, 10.5, 10.9)
    if a3 > 0:
        card(d, 1280, 600, 1840, 760, a3)
        d.text((1320, 650), '6 MILLION PEOPLE', font=F_LABEL, fill=A(AMBER, a3), anchor='lm')
        d.text((1320, 710), 'without power ≈ 9 hours', font=F_SMALL, fill=A(WHITE, a3), anchor='lm')
    top_label(img, 'CHAPTER 7 · CLOSE CALLS')
    return img

CAP19 = [(0, 3, 'In 1859, the world had no power grid. Today, it depends on one.', ['no', 'power', 'grid.']),
         (3, 7, 'On March 13th, 1989, at 2:44 a.m., a much smaller storm hit Quebec’s power grid.', ['1989,', 'smaller', 'Quebec’s']),
         (7, 9.5, 'In less than a minute, the grid collapsed.', ['less', 'minute,', 'collapsed.']),
         (9.5, 12.5, 'About six million people lost power, for around nine hours.', ['six', 'million', 'nine'])]

# ---------- 20. July 2012 ----------
SUN2, ORB = (700, 470), 330

def c20(t):
    img, d = new()
    draw_stars(d, t, 0.5)
    arr = to_arr(img)
    glow(arr, SUN2[0], SUN2[1], 60, (255, 160, 70), 1.4)
    glow(arr, SUN2[0], SUN2[1], 22, (255, 240, 200), 2.0)
    ang_st = -30  # STEREO-A position (deg); cloud direction
    k = ease(ramp(t, 3.0, 7.0))
    if k > 0:
        for j in range(60):
            rr = np.random.default_rng(j)
            r = (60 + (ORB + 120) * k) * rr.uniform(0.75, 1.0)
            th = math.radians(ang_st + rr.uniform(-22, 22))
            glow(arr, SUN2[0] + r * math.cos(th), SUN2[1] - r * math.sin(th), 22, (255, 150, 90), 0.25 * (1 - 0.5 * k))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([SUN2[0] - ORB, SUN2[1] - ORB, SUN2[0] + ORB, SUN2[1] + ORB], outline=(60, 80, 110), width=2)
    th = math.radians(ang_st)
    sx, sy = SUN2[0] + ORB * math.cos(th), SUN2[1] - ORB * math.sin(th)
    d.rectangle([sx - 10, sy - 10, sx + 10, sy + 10], fill=WHITE)
    d.line([sx - 30, sy, sx + 30, sy], fill=WHITE, width=3)
    d.text((sx + 40, sy + 10), 'STEREO-A', font=F_SMALL, fill=WHITE, anchor='lt')
    e_ang = ang_st + 180  # Earth far away on its orbit (illustration)
    te = math.radians(e_ang)
    ex, ey = SUN2[0] + ORB * math.cos(te), SUN2[1] - ORB * math.sin(te)
    d.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=(30, 90, 170))
    d.text((ex, ey - 34), 'EARTH', font=F_SMALL, fill=CYAN, anchor='ms')
    a = ramp(t, 9.5, 10.0)
    if a > 0:
        # Earth one week earlier along its orbit (about 7 degrees ahead)
        tg = math.radians(ang_st + 7)
        gx, gy = SUN2[0] + ORB * math.cos(tg), SUN2[1] - ORB * math.sin(tg)
        d.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], outline=A(CYAN, a), width=4)
    a1 = ramp(t, 0.3, 0.8)
    card(d, 1180, 140, 1840, 260, a1)
    d.text((1220, 200), '23 JULY 2012', font=F_MED, fill=A(WHITE, a1), anchor='lm')
    a2 = ramp(t, 13.5, 13.9)
    if a2 > 0:
        card(d, 1180, 330, 1840, 560, a2)
        d.text((1220, 385), '“at least as strong as', font=F_LABEL, fill=A(WHITE, a2), anchor='lm')
        d.text((1220, 435), 'the 1859 Carrington event”', font=F_LABEL, fill=A(WHITE, a2), anchor='lm')
        d.text((1220, 505), 'Daniel Baker, Univ. of Colorado', font=F_SMALL, fill=A(AMBER, a2), anchor='lm')
    d.text((1840, 800), 'positions illustrative', font=F_SMALL, fill=GREY, anchor='rm')
    top_label(img, 'THE NEAR MISS')
    return img

CAP20 = [(0, 3.5, 'Then, on July 23rd, 2012, the Sun launched a huge cloud across Earth’s orbit.', ['July', '23rd,', '2012,']),
         (3.5, 7, 'Earth wasn’t there. The cloud hit a NASA spacecraft, STEREO-A, instead.', ['STEREO-A,']),
         (7, 10.5, 'If it had erupted one week earlier, Earth would have been in the line of fire.', ['one', 'week', 'earlier,']),
         (10.5, 13, 'Two smaller eruptions, launched a little earlier, had cleared a path for it.', ['cleared', 'path']),
         (13, 17.5, 'Physicist Daniel Baker said it was at least as strong as the Carrington event. It just missed.', ['Daniel', 'Baker', 'missed.'])]

# ---------- 21. the cost ----------
def transformer(d, x, y, a):
    c = A((120, 130, 150), a)
    d.rectangle([x - 150, y - 140, x + 150, y + 100], fill=c)
    for i in range(7):
        d.rectangle([x - 140 + i * 42, y - 120, x - 128 + i * 42, y + 80], fill=A((90, 100, 120), a))
    for dx in (-90, 0, 90):
        d.rectangle([x + dx - 10, y - 220, x + dx + 10, y - 140], fill=A((200, 200, 210), a))
        for k in range(4):
            d.ellipse([x + dx - 22, y - 210 + k * 18, x + dx + 22, y - 198 + k * 18], fill=A((170, 170, 185), a))
    d.rectangle([x - 170, y + 100, x + 170, y + 120], fill=A((60, 66, 80), a))


def c21(t):
    img, d = new()
    a = ramp(t, 0.3, 0.8) * (1 - ramp(t, 8.6, 9.0))
    if a > 0:
        text_c(d, (620, 300), '$2 TRILLION+', F_HUGE, A(AMBER, a))
        text_c(d, (620, 400), 'possible cost of a direct hit today', F_LABEL, A(WHITE, a))
        text_c(d, (620, 450), 'National Academy of Sciences study', F_SMALL, A(GREY, a))
        transformer(d, 1400, 520, ramp(t, 4.0, 4.5) * a)
        a2 = ramp(t, 4.5, 5.0) * a
        text_c(d, (1400, 720), 'repairs might take years', F_LABEL, A(WHITE, a2))
    a3 = ramp(t, 9.0, 9.5)
    if a3 > 0:
        text_c(d, (960, 330), '12%', F_BIG, A(WHITE, a3))
        text_c(d, (960, 520), 'chance of a Carrington-class storm in a decade', F_MED, A(AMBER, a3))
        text_c(d, (960, 600), 'Pete Riley’s 2014 estimate', F_LABEL, A(GREY, a3))
    top_label(img, 'IF IT HIT US TODAY')
    return img

CAP21 = [(0, 2.5, 'A National Academy of Sciences study estimated that a direct hit today…', ['National', 'Academy']),
         (2.5, 4.5, '…could cost more than two trillion dollars.', ['two', 'trillion']),
         (4.5, 8.5, 'Huge transformers damaged by such a storm might take years to repair.', ['transformers', 'years']),
         (8.5, 11, 'In 2014, physicist Pete Riley estimated the chance of a Carrington-class storm…', ['Pete', 'Riley']),
         (11, 13, '…hitting Earth within a decade: about twelve percent.', ['twelve', 'percent.'])]

# ---------- 22. ending ----------
GC2, GR2 = (960, 470), 280

def c22(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    arr = to_arr(img)
    glow(arr, -100, 470, 300, (255, 150, 60), 0.9)
    glow(arr, GC2[0], GC2[1], GR2 * 1.05, (60, 120, 220), 0.45)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    globe(d, GC2, GR2, -100 + t * 5, 35)
    arr = to_arr(img)
    glow(arr, GC2[0], GC2[1] - GR2 * 0.86, 170, (80, 255, 150), 0.35 + 0.1 * math.sin(t * 2))
    sx = 560
    glow(arr, sx, 470, 10, (230, 240, 255), 1.4)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.line([sx - 26, 470, sx + 26, 470], fill=WHITE, width=3)
    a = ramp(t, 3.5, 4.0) * (1 - ramp(t, 8.0, 8.4))
    if a > 0:
        d.text((sx, 520), 'DSCOVR', font=F_SMALL, fill=A(WHITE, a), anchor='mt')
        card(d, 100, 130, 840, 250, a)
        d.text((140, 190), '15–60 MIN WARNING', font=F_MED, fill=A(AMBER, a), anchor='lm')
    a2 = ramp(t, 8.5, 9.0) * (1 - ramp(t, 12.0, 12.4))
    if a2 > 0:
        card(d, 1160, 130, 1840, 250, a2)
        d.text((1200, 165), 'MAY 2024', font=F_SMALL, fill=A(GREY, a2), anchor='lm')
        d.text((1200, 215), 'AURORAS OVER HAWAII', font=F_LABEL, fill=A(GREEN, a2), anchor='lm')
    a4 = ramp(t, 19.3, 19.8) * (1 - ramp(t, 22.3, 22.6))
    if a4 > 0:
        card(d, 460, 640, 1460, 780, a4)
        text_c(d, (960, 710), 'NOT IF, BUT WHEN', F_MED, A(WHITE, a4))
    a3 = ramp(t, 22.7, 23.2)
    if a3 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(170 * a3)))
        text_c(d, (W / 2, 380), 'FOLLOW', F_HUGE, A(WHITE, a3))
        text_c(d, (W / 2, 500), 'for more unexplained history', F_MED, A(AMBER, a3))
    top_label(img, 'CHAPTER 8 · WATCHING THE SUN', 1 - a3)
    return img

CAP22 = [(0, 3.5, 'Today, spacecraft watch the Sun every day for storms on the way.', ['spacecraft', 'watch']),
         (3.5, 8, 'One satellite, DSCOVR, can warn of a storm cloud fifteen to sixty minutes before it arrives.', ['DSCOVR,', 'fifteen', 'sixty']),
         (8, 12, 'In May 2024, a strong storm pushed auroras as far south as Hawaii.', ['May', '2024,', 'Hawaii.']),
         (12, 15.5, 'But no storm to hit Earth since 1859 has matched the Carrington Event.', ['no', 'storm', 'matched']),
         (15.5, 18, 'Scientists still call the most extreme storms Carrington-class.', ['Carrington-class.']),
         (15.5, 20, 'Nobody knows when the next one will come. Only that, one day, it almost certainly will.', ['next', 'one', 'will.'])]

SCENES = [
    ('c01', c01, 13.5, CAP01), ('c02', c02, 8.0, CAP02), ('c03', c03, 14.0, CAP03), ('c04', c04, 10.5, CAP04),
    ('c05', c05, 12.0, CAP05), ('c06', c06, 8.5, CAP06), ('c07', c07, 11.0, CAP07), ('c08', c08, 12.0, CAP08),
    ('c09', c09, 11.0, CAP09), ('c10', c10, 9.5, CAP10), ('c11', c11, 11.0, CAP11), ('c12', c12, 6.0, CAP12),
    ('c13', c13, 7.0, CAP13), ('c14', c14, 15.5, CAP14), ('c15', c15, 8.5, CAP15), ('c16', c16, 12.0, CAP16),
    ('c17', c17, 11.5, CAP17), ('c18', c18, 16.5, CAP18), ('c19', c19, 13.0, CAP19), ('c20', c20, 18.5, CAP20),
    ('c21', c21, 13.5, CAP21), ('c22', c22, 25.0, CAP22),
]

SPOKEN = {
    'In September 1859, telegraph wires began to throw sparks.':
        'In September, eighteen fifty-nine, telegraph wires began to throw sparks.',
    'On every clear day, he made careful maps of the dark spots on the Sun.':
        'On every clear day, he made careful maps of the dark spots on the Sun.',
    'On the morning of September 1st, 1859, a cluster of enormous sunspots was crossing the Sun.':
        'On the morning of September the first, eighteen fifty-nine, a cluster of enormous sunspots was crossing the Sun.',
    'Days earlier, on the night of August 28th, a first solar storm had already struck.':
        'Days earlier, on the night of August the twenty-eighth, a first solar storm had already struck.',
    'In the early hours of September 2nd, the cloud hit the Earth.':
        'In the early hours of September the second, the cloud hit the Earth.',
    'By 8 a.m. on September 2nd, the Boston office could not send or receive at all.':
        'By eight a.m. on September the second, the Boston office could not send or receive at all.',
    'Scientists rank magnetic storms with a number called Dst. The more negative, the stronger.':
        'Scientists rank magnetic storms with a number called D S T. The more negative, the stronger.',
    'A reading from Colaba, near Mumbai, once put 1859 at about minus 1,760.':
        'A reading from Colaba, near Mumbai, once put eighteen fifty-nine at about minus seventeen hundred and sixty.',
    'Later work found that reading had also caught the aurora…': 'Later work found that reading had also caught the aurora,',
    '…and lowered the estimate to about minus 900.': 'and lowered the estimate to about minus nine hundred.',
    'The storm that blacked out Quebec in 1989 measured about minus 600.':
        'The storm that blacked out Quebec in nineteen eighty-nine measured about minus six hundred.',
    'The exact number is still debated, but 1859 remains the largest magnetic storm on record.':
        'The exact number is still debated, but eighteen fifty-nine remains the largest magnetic storm on record.',
    'In 1859, the world had no power grid. Today, it depends on one.':
        'In eighteen fifty-nine, the world had no power grid. Today, it depends on one.',
    'On March 13th, 1989, at 2:44 a.m., a much smaller storm hit Quebec’s power grid.':
        "On March the thirteenth, nineteen eighty-nine, at two forty-four a.m., a much smaller storm hit Quebec's power grid.",
    'Then, on July 23rd, 2012, the Sun launched a huge cloud across Earth’s orbit.':
        "Then, on July the twenty-third, twenty twelve, the Sun launched a huge cloud across Earth's orbit.",
    'Earth wasn’t there. The cloud hit a NASA spacecraft, STEREO-A, instead.':
        "Earth wasn't there. The cloud hit a NASA spacecraft, Stereo A, instead.",
    'In 2014, physicist Pete Riley estimated the chance of a Carrington-class storm…':
        'In twenty fourteen, physicist Pete Riley estimated the chance of a Carrington-class storm,',
    '…hitting Earth within a decade: about twelve percent.': 'hitting Earth within a decade: about twelve percent.',
    'One satellite, DSCOVR, can warn of a storm cloud fifteen to sixty minutes before it arrives.':
        'One satellite, Discover, can warn of a storm cloud fifteen to sixty minutes before it arrives.',
    'In May 2024, a strong storm pushed auroras as far south as Hawaii.':
        'In May, twenty twenty-four, a strong storm pushed auroras as far south as Hawaii.',
    'But no storm to hit Earth since 1859 has matched the Carrington Event.':
        'But no storm to hit Earth since eighteen fifty-nine has matched the Carrington Event.',
    'Boston’s verdict: “We can work better without batteries.”': "Boston's verdict: We can work better without batteries.",
    'Boston asked: “Please cut off your battery entirely from the line for fifteen minutes.”':
        'Boston asked: Please cut off your battery entirely from the line, for fifteen minutes.',
    'Portland replied: “Will do so. It is now disconnected.”': 'Portland replied: Will do so. It is now disconnected.',
}


def SFX(tr, G):
    tr.wind([(0, 0.9), (G('c02', 0), 0.5), (G('c04', 0), 0.25), (G('c07', 0), 0.3), (G('c09', 0), 0.5),
             (G('c11', 0), 0.7), (G('c12', 0), 0.9), (G('c14', 0), 0.3), (G('c16', 0), 0.6), (G('c18', 0), 0.4),
             (G('c19', 0), 0.6), (G('c20', 0), 0.5), (G('c22', 0), 0.7), (G('c22', 24.0), 0.6), (G('c22', 25.0), 0.0)])
    for ts, _, _ in SPARKS1:
        tr.snaps(G('c01', ts), G('c01', ts + 0.15), 4, 0.22)
    tr.whoosh(G('c02', 0.2), G('c02', 1.0), 0.12, 400, 2000)
    tr.whoosh(G('c03', 0.0), G('c03', 4.5), 0.1, 300, 1200)
    tr.whoosh(G('c05', 0.3), G('c05', 0.9), 0.14, 500, 3000)
    tr.rumble(G('c06', 0.5), G('c06', 5.0), 0.1)
    tr.rumble(G('c07', 4.4), G('c07', 6.0), 0.15)
    tr.whoosh(G('c09', 1.0), G('c09', 10.5), 0.1, 200, 900)
    tr.rumble(G('c09', 1.0), G('c09', 10.5), 0.16)
    tr.rumble(G('c11', 0.0), G('c11', 3.0), 0.25)
    tr.crackle(G('c12', 0.5), G('c12', 6.0), 0.16)
    for ts in SPARKS14:
        tr.snaps(G('c14', ts), G('c14', ts + 0.12), 3, 0.28)
    tr.crackle(G('c14', 4.0), G('c14', 8.5), 0.2)
    tr.snaps(G('c14', 9.0), G('c14', 11.8), 40, 0.25)
    tr.snaps(G('c15', 0.0), G('c15', 4.5), 30, 0.12)
    tr.rumble(G('c18', 2.5), G('c18', 4.0), 0.12)
    tr.rumble(G('c19', 7.0), G('c19', 8.5), 0.3)
    tr.boom(G('c19', 8.2), 0.35, 2.5)
    tr.whoosh(G('c20', 3.0), G('c20', 7.0), 0.18, 300, 1500)
    tr.rumble(G('c20', 3.0), G('c20', 7.0), 0.15)

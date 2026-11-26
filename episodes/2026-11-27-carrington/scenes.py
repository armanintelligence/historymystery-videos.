"""Episode: The Carrington Event (1859). Visuals: auroras, the Sun, maps, telegraph objects, mountains,
a campfire, a newspaper, a globe. No people, animals or birds."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

GREEN = (90, 255, 150)
RED = (255, 70, 90)
XS = np.arange(W, dtype=np.float32)
YS = np.arange(H, dtype=np.float32)[:, None]


def sky(d, top=(4, 6, 13), bot=(12, 20, 40), ymax=1150):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=tuple(int(lerp(a, b, k)) for a, b in zip(top, bot)))


def aurora(arr, t, base=560, height=420, k=1.0, ymax=1150, red=0.8):
    """Curtain aurora added to a float array. Green at the foot, red higher up."""
    if k <= 0:
        return
    foot = base + 45 * np.sin(XS / 170 + t * 0.55) + 22 * np.sin(XS / 61 - t * 0.9)
    col = (0.55 + 0.45 * np.sin(XS / 23 + t * 1.3) * np.sin(XS / 77 - t * 0.4)) ** 2
    q = (foot[None, :] - YS) / height                     # 0 at the foot, 1 at the top
    inside = (q > -0.06) & (q < 1.6) & (YS < ymax)
    g = np.where(q >= 0, np.exp(-q * 3.2), np.exp(q * 40)) * inside
    r = np.clip(q - 0.35, 0, None) * np.exp(-np.clip(q - 0.35, 0, None) * 1.6) * inside * red
    arr += (g * col[None, :] * k)[..., None] * np.array(GREEN, np.float32) * 0.55
    arr += (r * col[None, :] * k)[..., None] * np.array(RED, np.float32) * 0.9


def pole(d, x, gy, h, col=(26, 30, 40)):
    d.rectangle([x - 6, gy - h, x + 6, gy], fill=col)
    d.rectangle([x - 46, gy - h + 18, x + 46, gy - h + 30], fill=col)
    for dx in (-36, 36):
        d.ellipse([x + dx - 7, gy - h + 8, x + dx + 7, gy - h + 20], fill=col)


def sag(d, x0, x1, y, dip, col, width=3):
    pts = [(lerp(x0, x1, i / 30), y + dip * math.sin(math.pi * i / 30)) for i in range(31)]
    d.line(pts, fill=col, width=width)


# ---------- S1: hook: wires spark under a red sky ----------
POLES = [(-60, 380), (300, 330), (660, 290), (1020, 250), (1380, 215)]
GY1 = 1110
rng1 = np.random.default_rng(5)
SPARKS1 = [(rng1.uniform(0.6, 8.5), rng1.integers(0, 4), rng1.uniform(0.1, 0.9)) for _ in range(40)]

def s1(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    sky(d)
    draw_stars(d, t, 0.6)
    arr = to_arr(img)
    aurora(arr, t, base=600, height=460, k=ramp(t, 0.0, 1.5), red=1.3)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    # low hills and grass
    d.polygon([(0, GY1 - 30)] + [(x, GY1 - 30 - 25 * math.sin(x / 210)) for x in range(0, W + 1, 20)] + [(W, H), (0, H)], fill=(6, 9, 12))
    d.rectangle([0, GY1, W, H], fill=(5, 7, 10))
    tops = []
    for x, h in POLES:
        pole(d, x, GY1, h)
        tops.append((x, GY1 - h + 24))
    for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
        for dx in (-36, 36):
            d.line([(lerp(x0 + dx, x1 + dx, i / 30), lerp(y0, y1, i / 30) + 30 * math.sin(math.pi * i / 30)) for i in range(31)],
                   fill=(34, 40, 52), width=3)
    arr = to_arr(img)
    for ts, seg, u in SPARKS1:
        if 0 <= t - ts < 0.25:
            (x0, y0), (x1, y1) = tops[seg], tops[seg + 1]
            x, y = lerp(x0, x1, u), lerp(y0, y1, u) + 30 * math.sin(math.pi * u)
            f = 1 - (t - ts) / 0.25
            glow(arr, x, y, 26, (170, 210, 255), 1.6 * f)
            glow(arr, x, y, 7, (255, 255, 255), 2.5 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.6, 1.1)
    text_c(d, (W / 2, 420), '1859', F_BIG, WHITE + (int(240 * a),))
    top_label(img, 'SEPTEMBER 1859', ramp(t, 0.2, 0.6))
    return img

CAPS1 = [(0.3, 5.0, 'In 1859, telegraph wires threw sparks and set paper on fire.', ['1859,', 'sparks', 'fire.']),
         (5.0, 9.0, 'The cause? The Sun.', ['Sun.'])]


# ---------- S2: Carrington's projected Sun ----------
SC = (600, 760)  # centre of the Sun image on the screen
SR_ = 230
rng2 = np.random.default_rng(9)
SPOTS = [(rng2.uniform(-0.55, 0.55), rng2.uniform(-0.35, 0.35), rng2.uniform(6, 26)) for _ in range(14)]
FLARE = (SC[0] + 70, SC[1] - 40)

def sun_disc(d, cx, cy, r):
    for i in range(30, 0, -1):
        k = i / 30
        c = (int(255 * (0.75 + 0.25 * (1 - k))), int(205 * (0.65 + 0.35 * (1 - k))), int(120 * (0.5 + 0.5 * (1 - k))))
        d.ellipse([cx - r * k, cy - r * k, cx + r * k, cy + r * k], fill=c)
    for sx, sy, sr in SPOTS:
        x, y = cx + sx * r, cy + sy * r
        d.ellipse([x - sr, y - sr * 0.8, x + sr, y + sr * 0.8], fill=(120, 70, 35))
        d.ellipse([x - sr * 0.5, y - sr * 0.4, x + sr * 0.5, y + sr * 0.4], fill=(55, 30, 18))

def s2(t):
    img = Image.new('RGB', (W, H), (18, 20, 28))
    d = ImageDraw.Draw(img, 'RGBA')
    # wall and table
    d.rectangle([0, 1080, W, H], fill=(40, 30, 24))
    d.rectangle([0, 1080, W, 1096], fill=(60, 46, 34))
    # the screen board
    d.rectangle([300, 450, 900, 1070], fill=(225, 222, 210))
    d.rectangle([300, 450, 900, 1070], outline=(90, 80, 70), width=8)
    # telescope tube coming from the upper left
    d.polygon([(-40, 230), (40, 150), (300, 400), (230, 470)], fill=(70, 60, 50))
    d.polygon([(230, 470), (300, 400), (320, 420), (250, 490)], fill=(110, 95, 70))
    # light cone onto the screen
    d.polygon([(285, 445), (SC[0] - SR_, SC[1]), (SC[0], SC[1] + SR_), (SC[0] + SR_, SC[1])], fill=(255, 230, 170, 22))
    sun_disc(d, *SC, SR_)
    arr = to_arr(img)
    if 4.1 <= t:
        f = ramp(t, 4.1, 4.4) * (1 - ramp(t, 5.6, 6.5))
        flick = 0.85 + 0.15 * math.sin(t * 30)
        for dx, dy in ((0, 0), (34, 18)):
            glow(arr, FLARE[0] + dx, FLARE[1] + dy, 30, (255, 255, 255), 2.2 * f * flick)
            glow(arr, FLARE[0] + dx, FLARE[1] + dy, 70, (255, 240, 210), 0.6 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 4.5, 4.9)
    if a > 0:
        d.line([FLARE[0] + 60, FLARE[1] - 40, 880, 330], fill=AMBER + (int(255 * a),), width=4)
        text_c(d, (W / 2 + 160, 300), 'WHITE-LIGHT FLARE', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'NEAR LONDON · 1 SEPT 1859 · MORNING')
    return img

CAPS2 = [(0.0, 3.2, 'On September 1st, Richard Carrington was watching sunspots near London.', ['Richard', 'Carrington', 'sunspots']),
         (3.2, 6.5, 'Suddenly, a blinding white light flared up.', ['blinding', 'white', 'light'])]


# ---------- S3: first recorded flare ----------
def s3(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_stars(d, t, 0.5)
    arr = to_arr(img)
    glow(arr, 540, 690, 380, (255, 140, 50), 0.35)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    sun_disc(d, 540, 690, 300)
    arr = to_arr(img)
    f = 1 - ramp(t, 0.5, 3.0)
    fx, fy = 540 + 92, 690 - 52
    glow(arr, fx, fy, 40, (255, 255, 255), 2.4 * f)
    glow(arr, fx + 44, fy + 23, 36, (255, 255, 255), 2.0 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    # 5-minute clock ring
    k = ramp(t, 0.5, 3.0)
    d.arc([840, 240, 1000, 400], -90, -90 + 360 * k, fill=AMBER, width=10)
    text_c(d, (920, 320), f'{int(5 * k + 0.0001)} min' if k < 1 else '5 min', F_SMALL, WHITE)
    a = ramp(t, 3.2, 3.6)
    if a > 0:
        d.rounded_rectangle([110, 1040, 970, 1150], radius=20, fill=(0, 0, 0, int(170 * a)))
        text_c(d, (W / 2, 1095), 'FIRST SOLAR FLARE EVER RECORDED', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'ABOUT FIVE MINUTES')
    return img

CAPS3 = [(0.0, 3.0, 'Five minutes later, it was gone.', ['Five', 'minutes']),
         (3.0, 6.5, 'The first solar flare ever recorded.', ['first', 'solar', 'flare'])]


# ---------- S4: the cloud travels to Earth ----------
rng4 = np.random.default_rng(12)
PUFF = [(rng4.uniform(-1, 1), rng4.uniform(-1, 1), rng4.uniform(0.4, 1)) for _ in range(160)]

def s4(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_stars(d, t, 0.6, ymax=H)
    arr = to_arr(img)
    glow(arr, -40, 690, 330, (255, 150, 60), 1.1)
    glow(arr, -40, 690, 140, (255, 235, 190), 1.4)
    e = ease(ramp(t, 0.6, 5.2))
    cx = lerp(160, 900, e)
    spread = lerp(60, 260, e)
    for px, py, w_ in PUFF:
        if px * px + py * py > 1:
            continue
        x = cx + px * spread * 0.55 - abs(py) * spread * 0.35
        y = 690 + py * spread
        glow(arr, x, y, 18 + 14 * e, (255, 160, 90), 0.22 * w_ * (1 - 0.4 * e))
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    # Earth
    ex, ey, er = 930, 690, 58
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(20, 60, 120))
    d.chord([ex - er, ey - er, ex + er, ey + er], 200, 330, fill=(40, 90, 60))
    d.arc([ex - er - 40, ey - er - 40, ex + er + 40, ey + er + 40], 110, 250, fill=CYAN + (120,), width=3)
    text_c(d, (ex, ey + 100), 'EARTH', F_SMALL, CYAN)
    text_c(d, (110, 1000), 'SUN', F_SMALL, AMBER)
    hrs = 17.5 * e
    text_c(d, (W / 2, 330), f'{hrs:4.1f} h', F_HUGE, WHITE)
    d.text((W / 2, 1080), 'not to scale', font=F_SMALL, fill=GREY, anchor='mm')
    top_label(img, 'A CLOUD OF CHARGED GAS')
    return img

CAPS4 = [(0.0, 3.4, 'It also hurled a cloud of charged gas at Earth.', ['charged', 'gas', 'Earth.']),
         (3.4, 6.5, 'It arrived in under eighteen hours.', ['eighteen', 'hours.'])]


# ---------- S5: aurora reaches the tropics ----------
PLACES = [('CUBA', -79.5, 21.8), ('JAMAICA', -77.3, 18.1), ('PANAMA', -80.0, 8.8)]

def s5(t):
    cam = Cam(-82, 30, 17)
    img = draw_map(Image.new('RGB', (W, H)), cam, land=(26, 34, 48), coast=(66, 82, 108), water=(6, 10, 20))
    arr = to_arr(img)
    lat_edge = lerp(62, 7, ease(ramp(t, 0.4, 4.0)))
    edge_y = float(cam.xy(0, lat_edge)[1])
    wob = 18 * np.sin(XS / 90 + t * 1.5)
    band = np.clip(1 - (YS - (edge_y + wob[None, :])) / 70, 0, 1) * (YS < 1150)
    shimmer = (0.75 + 0.25 * np.sin(XS / 31 + t * 2))[None, :]
    arr += (band * shimmer * 0.5)[..., None] * (np.array(GREEN, np.float32) * 0.6 + np.array(RED, np.float32) * 0.35)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    for i, (name, lo, la) in enumerate(PLACES):
        x, y = cam.xy(lo, la)
        a = ramp(t, 2.4 + i * 0.5, 2.7 + i * 0.5)
        if a > 0:
            d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=AMBER + (int(255 * a),))
            d.text((x + 24, y), name, font=F_LABEL, fill=WHITE + (int(255 * a),), anchor='lm')
    top_label(img, 'AURORAS IN THE TROPICS')
    return img

CAPS5 = [(0.0, 6.5, 'Auroras lit the night sky as far south as Cuba and Panama.', ['Auroras', 'Cuba', 'Panama.'])]


# ---------- S6: Rocky Mountains, breakfast at 1 a.m. ----------
rng6 = np.random.default_rng(3)
RIDGE_A = [(x, 760 - 260 * abs(math.sin(x / 300 + 0.6)) - rng6.uniform(0, 40)) for x in range(-40, W + 80, 60)]
RIDGE_B = [(x, 900 - 160 * abs(math.sin(x / 210 + 2.0)) - rng6.uniform(0, 30)) for x in range(-40, W + 80, 50)]
FIRE = (540, 1060)

def s6(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    sky(d, bot=(14, 30, 34), ymax=1150)
    draw_stars(d, t, 0.4)
    arr = to_arr(img)
    aurora(arr, t * 1.1, base=560, height=380, k=1.25, red=1.0)
    # brightened sky like dawn
    arr += (np.clip(1 - YS / 1100, 0, 1) * 18)[..., None] * np.array([0.6, 1.0, 0.8], np.float32)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    d.polygon(RIDGE_A + [(W + 80, H), (-40, H)], fill=(18, 24, 34))
    for x, y in RIDGE_A[1:-1:3]:
        d.polygon([(x - 26, y + 28), (x + 26, y + 28), (x, y)], fill=(170, 185, 200, 120))
    d.polygon(RIDGE_B + [(W + 80, H), (-40, H)], fill=(10, 14, 20))
    d.rectangle([0, 1080, W, H], fill=(8, 10, 14))
    for x in range(-20, W + 40, 38):
        conifer(d, x, 1086 if abs(x - FIRE[0]) > 160 else 1090, 70 + 50 * ((x * 37) % 11) / 11, (6, 9, 12))
    # campfire with a coffee pot and a pan
    fx, fy = FIRE
    d.rectangle([fx - 140, fy + 10, fx + 140, fy + 40], fill=(8, 10, 14))
    for dx in (-50, 0, 50):
        d.line([fx + dx - 30, fy + 34, fx + dx + 30, fy + 20], fill=(70, 50, 32), width=10)
    arr = to_arr(img)
    fl = 0.8 + 0.2 * math.sin(t * 17) * math.sin(t * 7.3)
    glow(arr, fx, fy, 90, (255, 120, 40), 0.9 * fl)
    glow(arr, fx, fy + 5, 30, (255, 220, 140), 1.6 * fl)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    d.line([fx - 120, fy - 60, fx + 120, fy - 60], fill=(40, 40, 44), width=6)
    d.polygon([(fx - 95, fy - 56), (fx - 55, fy - 56), (fx - 62, fy - 110), (fx - 88, fy - 110)], fill=(60, 64, 70))
    d.line([fx - 88, fy - 110, fx - 104, fy - 124], fill=(60, 64, 70), width=6)
    d.ellipse([fx + 20, fy - 70, fx + 110, fy - 48], fill=(34, 34, 38))
    d.line([fx + 110, fy - 60, fx + 175, fy - 70], fill=(34, 34, 38), width=8)
    # clock
    a = ramp(t, 0.5, 0.9)
    d.rounded_rectangle([380, 260, 700, 370], radius=20, fill=(0, 0, 0, int(160 * a)))
    text_c(d, (540, 315), '1:00 AM', F_MED, AMBER + (int(255 * a),))
    top_label(img, 'ROCKY MOUNTAINS')
    return img

CAPS6 = [(0.0, 6.5, 'Rocky Mountain gold miners woke at 1 a.m. and made breakfast, thinking it was dawn.', ['gold', 'miners', '1', 'a.m.', 'breakfast,'])]


# ---------- S7: newspaper by aurora light ----------
rng7 = np.random.default_rng(21)
ROOFS = []
x = -20
while x < W + 20:
    w_ = rng7.uniform(70, 150); h_ = rng7.uniform(120, 300)
    ROOFS.append((x, w_, h_, rng7.random() < 0.3)); x += w_ + rng7.uniform(0, 8)

def s7(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    sky(d, bot=(26, 18, 34), ymax=1150)
    draw_stars(d, t, 0.3)
    arr = to_arr(img)
    aurora(arr, t, base=520, height=420, k=1.0, red=1.8)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    gy = 1150
    for x, w_, h_, steeple in ROOFS:
        d.rectangle([x, gy - h_, x + w_, gy], fill=(10, 12, 18))
        if steeple:
            d.polygon([(x + w_ * 0.3, gy - h_), (x + w_ * 0.7, gy - h_), (x + w_ * 0.5, gy - h_ - 90)], fill=(10, 12, 18))
        for wy in range(int(gy - h_ + 20), gy - 20, 44):
            for wx in range(int(x + 14), int(x + w_ - 20), 30):
                if (wx * 7 + wy * 3) % 5 == 0:
                    d.rectangle([wx, wy, wx + 12, wy + 18], fill=(90, 70, 40))
    # newspaper slides in
    a = ease(ramp(t, 1.0, 2.0))
    if a > 0:
        ox, y0 = lerp(1300, 540, a), 640
        paper = (232, 226, 208, int(255 * a))
        d.polygon([(ox - 250, y0), (ox + 250, y0 - 20), (ox + 262, y0 + 320), (ox - 238, y0 + 340)], fill=paper)
        d.text((ox, y0 + 50), 'THE EVENING NEWS', font=F_LABEL, fill=(30, 30, 30, int(255 * a)), anchor='mm')
        for i in range(7):
            w_ = 400 if i % 3 else 320
            yy = y0 + 100 + i * 30 - 8 * (i / 7)
            d.rectangle([ox - 200, yy, ox - 200 + w_, yy + 13], fill=(120, 115, 105, int(255 * a)))
        # aurora tint on the paper
        d.polygon([(ox - 250, y0), (ox + 250, y0 - 20), (ox + 262, y0 + 320), (ox - 238, y0 + 340)], fill=(255, 60, 80, int(30 * a)))
    top_label(img, 'BOSTON · NIGHT')
    return img

CAPS7 = [(0.0, 4.5, 'In Boston, people read newspapers by its light.', ['Boston,', 'newspapers', 'light.'])]


# ---------- S8: telegraph office sparks and fire ----------
rng8 = np.random.default_rng(31)
SPARKS8 = sorted(rng8.uniform(0.3, 6.5, 26))

def s8(t):
    img = Image.new('RGB', (W, H), (14, 14, 20))
    d = ImageDraw.Draw(img, 'RGBA')
    # desk
    d.rectangle([0, 900, W, H], fill=(52, 36, 24))
    d.rectangle([0, 900, W, 918], fill=(78, 56, 36))
    # register: base, coils, lever
    d.rectangle([190, 760, 600, 900], fill=(60, 50, 40))
    d.rectangle([190, 760, 600, 776], fill=(90, 74, 56))
    for cx in (290, 370):
        d.rounded_rectangle([cx - 30, 610, cx + 30, 760], radius=10, fill=(150, 90, 50))
        for yy in range(620, 750, 12):
            d.line([cx - 30, yy, cx + 30, yy], fill=(120, 70, 40), width=3)
    d.rectangle([240, 595, 520, 612], fill=(110, 110, 118))
    # brass terminals and wires
    for tx in (220, 570):
        d.ellipse([tx - 16, 740, tx + 16, 772], fill=(200, 160, 70))
    d.line([570, 756, 700, 700, 1100, 640], fill=(30, 30, 34), width=6)
    d.line([220, 756, 120, 690, -20, 660], fill=(30, 30, 34), width=6)
    # paper tape running out of the register
    burn = ramp(t, 3.6, 6.5)
    d.polygon([(470, 760), (980, 800), (980, 846), (470, 806)], fill=(232, 226, 208))
    for i in range(14):
        x0 = 520 + i * 32
        if (i * 5) % 3:
            d.rectangle([x0, 783 + i * 2.5, x0 + 18, 787 + i * 2.5], fill=(40, 40, 40))
    if burn > 0:
        bx = lerp(980, 640, burn)
        d.polygon([(bx, 760 + (bx - 470) * 40 / 510), (980, 800), (980, 846), (bx, 806 + (bx - 470) * 40 / 510)], fill=(30, 22, 16))
    arr = to_arr(img)
    for ts in SPARKS8:
        if 0 <= t - ts < 0.2:
            f = 1 - (t - ts) / 0.2
            for sx, sy in ((220, 756), (570, 756)):
                glow(arr, sx, sy, 34, (170, 210, 255), 1.5 * f)
                glow(arr, sx, sy, 9, (255, 255, 255), 2.4 * f)
    if burn > 0:
        bx = lerp(980, 640, burn)
        fl = 0.8 + 0.2 * math.sin(t * 19)
        glow(arr, bx, 805 + (bx - 470) * 40 / 510 - 20, 50, (255, 120, 40), 1.2 * fl)
        glow(arr, bx, 805 + (bx - 470) * 40 / 510 - 10, 18, (255, 230, 150), 1.6 * fl)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    top_label(img, 'TELEGRAPH OFFICE')
    return img

CAPS8 = [(0.0, 3.4, 'Telegraph operators got electric shocks.', ['electric', 'shocks.']),
         (3.4, 6.5, 'Sparks set paper on fire.', ['Sparks', 'fire.'])]


# ---------- S9: Boston to Portland, batteries unplugged ----------
BOS, POR = (-71.06, 42.36), (-70.26, 43.66)

def battery(d, x, y, a, unplugged):
    c = WHITE + (int(255 * a),)
    d.rounded_rectangle([x - 70, y - 36, x + 60, y + 36], radius=8, outline=c, width=5)
    d.rectangle([x + 60, y - 14, x + 74, y + 14], fill=c)
    if unplugged:
        r = (255, 90, 70, int(255 * a))
        d.line([x - 60, y - 50, x + 64, y + 50], fill=r, width=9)
        d.line([x - 60, y + 50, x + 64, y - 50], fill=r, width=9)

def s9(t):
    cam = Cam(-70.6, 43.0, 380)
    img = draw_map(Image.new('RGB', (W, H)), cam)
    arr = to_arr(img)
    aurora(arr, t, base=330, height=240, k=0.7, red=1.2, ymax=700)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    b, p = cam.xy(*BOS), cam.xy(*POR)
    d.line([b, p], fill=GREY, width=4)
    for (x, y), name, side in ((b, 'BOSTON', 1), (p, 'PORTLAND, MAINE', -1)):
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=AMBER)
        d.text((x - 30 if side < 0 else x - 30, y + (50 if side > 0 else -40)), name, font=F_LABEL, fill=WHITE, anchor='rm' if side < 0 else 'rm')
    a = ramp(t, 0.6, 1.0)
    battery(d, b[0] + 190, b[1] + 10, a, t > 2.8)
    battery(d, p[0] + 190, p[1] - 10, a, t > 3.1)
    # messages still flow after unplugging
    if t > 4.2:
        for k in range(3):
            q = ((t - 4.2) * 0.6 + k / 3) % 1
            x, y = lerp(b[0], p[0], q), lerp(b[1], p[1], q)
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=CYAN)
        a2 = ramp(t, 4.2, 4.6)
        d.rounded_rectangle([150, 1010, 930, 1130], radius=20, fill=(0, 0, 0, int(170 * a2)))
        text_c(d, (W / 2, 1070), 'POWERED BY THE AURORA', F_LABEL, GREEN + (int(255 * a2),))
    top_label(img, '2 SEPT 1859 · MORNING')
    return img

CAPS9 = [(0.0, 3.4, 'The strangest part: operators in Boston and Portland unplugged their batteries…', ['strangest', 'unplugged', 'batteries…']),
         (3.4, 7.0, '…and kept sending messages on aurora power alone.', ['aurora', 'alone.'])]


# ---------- S10: once every 500 years + end ----------
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

rng10 = np.random.default_rng(8)
CITIES = [(-74.0, 40.7), (-71.1, 42.4), (-77.0, 38.9), (-87.6, 41.9), (-84.4, 33.7), (-79.4, 43.7), (-73.6, 45.5),
          (-95.4, 29.8), (-96.8, 32.8), (-118.2, 34.1), (-122.4, 37.8), (-122.3, 47.6), (-105.0, 39.7), (-80.2, 25.8),
          (-90.1, 30.0), (-83.0, 42.3), (-0.1, 51.5), (2.35, 48.9), (-3.7, 40.4), (13.4, 52.5), (12.5, 41.9), (4.9, 52.4),
          (4.35, 50.8), (21.0, 52.2), (18.1, 59.3), (-9.1, 38.7), (-6.3, 53.3), (-99.1, 19.4), (-2.2, 53.5), (9.2, 45.5)]
LIGHTS = [(lo + rng10.normal(0, 0.9), la + rng10.normal(0, 0.6)) for lo, la in CITIES for _ in range(5)]

def s10(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_stars(d, t, 0.7, ymax=H)
    d.ellipse([GC[0] - GR, GC[1] - GR, GC[0] + GR, GC[1] + GR], fill=(10, 26, 52))
    lon0 = -40 + t * 4
    for p in GEO['l']['land']:
        x, y, z = ortho(p[:, 0], p[:, 1], lon0, 30)
        if (z > 0).any() and len(p) > 2:
            d.polygon(list(zip(x.tolist(), y.tolist())), fill=(28, 40, 46))
    arr = to_arr(img)
    out = ramp(t, 4.0, 5.0)  # city lights go out
    for lo, la in LIGHTS:
        x, y, z = ortho(np.array([lo]), np.array([la]), lon0, 30)
        if z[0] > 0.1:
            glow(arr, float(x[0]), float(y[0]), 5, (255, 200, 120), 1.2 * (1 - out))
    # aurora oval glow at the top of the globe
    glow(arr, GC[0], GC[1] - GR * 0.85, 200, (80, 255, 150), 0.35 + 0.1 * math.sin(t * 2))
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 0.3, 0.7) * (1 - ramp(t, 5.4, 5.7))
    text_c(d, (W / 2, 1150), 'ABOUT ONCE EVERY 500 YEARS', F_LABEL, AMBER + (int(255 * a),))
    top_label(img, 'IF IT HAPPENED TODAY', 1 - ramp(t, 5.4, 5.7))
    a2 = ramp(t, 5.6, 6.0)
    if a2 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(150 * a2)))
        text_c(d, (W / 2, 600), 'FOLLOW', F_HUGE, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 720), 'for more unexplained history', F_MED, AMBER + (int(255 * a2),))
    return img

CAPS10 = [(0.0, 3.4, 'Storms this strong strike about once every five hundred years.', ['five', 'hundred', 'years.']),
          (3.4, 7.0, 'Today, one could black out whole continents.', ['black', 'out', 'continents.'])]


SCENES = [
    ('s01', s1, 9.0, CAPS1),
    ('s02', s2, 6.5, CAPS2),
    ('s03', s3, 6.5, CAPS3),
    ('s04', s4, 6.5, CAPS4),
    ('s05', s5, 6.5, CAPS5),
    ('s06', s6, 6.5, CAPS6),
    ('s07', s7, 4.5, CAPS7),
    ('s08', s8, 6.5, CAPS8),
    ('s09', s9, 7.0, CAPS9),
    ('s10', s10, 7.6, CAPS10),
]

SPOKEN = {
    'Rocky Mountain gold miners woke at 1 a.m. and made breakfast, thinking it was dawn.': 'Rocky Mountain gold miners woke at one a.m., and made breakfast, thinking it was dawn.',
    'In 1859, telegraph wires threw sparks and set paper on fire.': 'In eighteen fifty-nine, telegraph wires threw sparks, and set paper on fire.',
    'On September 1st, Richard Carrington was watching sunspots near London.': 'On September the first, Richard Carrington was watching sunspots, near London.',
}


def SFX(tr, G):
    tr.wind([(0, 0.9), (G('s02', 0), 0.25), (G('s04', 0), 0.5), (G('s05', 0), 0.7), (G('s06', 0), 0.9),
             (G('s08', 0), 0.3), (G('s09', 0), 0.6), (G('s10', 0), 0.7), (G('s10', 7.0), 0.6), (G('s10', 7.6), 0.0)])
    for ts, _, _ in SPARKS1:
        tr.snaps(G('s01', ts), G('s01', ts + 0.15), 4, 0.25)
    tr.whoosh(G('s02', 2.4), G('s02', 2.9), 0.12, 500, 3000)
    tr.rumble(G('s03', 0.3), G('s03', 3.0), 0.12)
    tr.whoosh(G('s04', 0.6), G('s04', 5.2), 0.10, 200, 900)
    tr.rumble(G('s04', 0.6), G('s04', 6.0), 0.18)
    tr.crackle(G('s06', 0.0), G('s06', 6.5), 0.14)
    for ts in SPARKS8:
        tr.snaps(G('s08', ts), G('s08', ts + 0.12), 3, 0.3)
    tr.crackle(G('s08', 3.6), G('s08', 6.5), 0.2)
    tr.rumble(G('s10', 4.0), G('s10', 6.5), 0.2)

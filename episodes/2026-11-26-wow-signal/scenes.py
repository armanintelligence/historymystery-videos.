"""Episode: The Wow! Signal (1977). Visuals: sky, telescope diagram, map, printout, graphs, star field. No living faces."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

DELAWARE = (-83.07, 40.30)  # Delaware, Ohio (Big Ear site)
RED = (255, 90, 70)


def sky(d, top=(4, 6, 13), bot=(14, 24, 51), ymax=1150):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=tuple(int(lerp(a, b, k)) for a, b in zip(top, bot)))


def big_ear(d, gx0, gx1, gy, col=(120, 135, 160), a=255):
    """Side view of the Big Ear: tilting flat reflector (left), ground plane, parabolic reflector (right)."""
    c = col + (a,)
    # ground plane
    d.rectangle([gx0, gy, gx1, gy + 10], fill=(150, 165, 190, a))
    # flat reflector, tilted, on a frame
    fx = gx0 + 40
    top = (fx + 70, gy - 230)
    d.line([fx, gy, top[0], top[1]], fill=c, width=14)
    for k in (0.33, 0.66):
        px, py = lerp(fx, top[0], k), lerp(gy, top[1], k)
        d.line([px, py, px - 50 * k - 30, gy], fill=c, width=5)
    # parabolic reflector (curved wall), right side
    pts = []
    for i in range(21):
        q = i / 20
        y = gy - 160 * q
        x = gx1 - 30 - 55 * (q ** 2)
        pts.append((x, y))
    d.line(pts, fill=c, width=14)
    for k in (0.3, 0.6, 0.9):
        x, y = pts[int(k * 20)]
        d.line([x, y, x + 40, gy], fill=c, width=5)
    # feed horn hut in the middle
    hx = (gx0 + gx1) / 2 + 60
    d.rectangle([hx - 22, gy - 34, hx + 22, gy], fill=(90, 100, 120, a))


# ---------- S1: hook ----------
def s1(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d)
    draw_stars(d, t)
    d.rectangle([0, 1100, W, H], fill=(5, 8, 12))
    big_ear(d, 120, 960, 1100, col=(28, 34, 46))
    arr = to_arr(img)
    # incoming pulse from deep space
    if 0.4 <= t < 3.0:
        e = ramp(t, 0.4, 3.0)
        y = lerp(120, 950, e ** 1.2)
        glow(arr, 560, y, 40, (110, 210, 255), 0.8)
        glow(arr, 560, y, 12, (230, 250, 255), 1.4)
    if t >= 3.0:
        f = math.exp(-(t - 3.0) * 1.5)
        glow(arr, 600, 1060, 220, (110, 210, 255), 0.9 * f)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(5):
        tt = t - 3.0 - i * 0.3
        if tt > 0:
            r = 30 + tt * 260
            a = max(0, 1 - tt / 2.0)
            d.arc([600 - r, 1060 - r, 600 + r, 1060 + r], 180, 360, fill=CYAN + (int(220 * a),), width=6)
    a = ramp(t, 3.6, 4.0)
    if a > 0:
        text_c(d, (W / 2, 470), '72', F_BIG, WHITE + (int(255 * a),))
        text_c(d, (W / 2, 640), 'SECONDS', F_MED, CYAN + (int(255 * a),))
    a2 = ramp(t, 6.6, 6.9)
    if a2 > 0:
        d.rounded_rectangle([200, 720, 880, 830], radius=18, outline=RED + (int(255 * a2),), width=6)
        text_c(d, (W / 2, 775), 'NEVER HEARD AGAIN', F_MED, RED + (int(255 * a2),))
    top_label(img, 'OHIO · 1977', ramp(t, 0.2, 0.6))
    return img

CAPS1 = [(0.3, 6.5, 'In 1977, a signal arrived from deep space. It lasted 72 seconds…', ['1977,', 'deep', 'space.', '72', 'seconds…']),
         (6.5, 9.0, '…and was never heard again.', ['never'])]

# ---------- S2: map zoom to Ohio ----------
def cam2(t):
    k = ease(ramp(t, 0.0, 3.4))
    s = math.exp(lerp(math.log(7), math.log(60), k))
    return Cam(lerp(-98, DELAWARE[0], k), lerp(40, DELAWARE[1], k), s)

def pin(d, x, y, t0, t, label=None):
    a = ramp(t, t0, t0 + 0.3)
    if a <= 0:
        return
    pr = 30 + 40 * ((t - t0) % 1.2) / 1.2
    pa = int(200 * a * (1 - ((t - t0) % 1.2) / 1.2))
    d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=AMBER + (pa,), width=4)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=AMBER + (int(255 * a),))
    if label:
        d.text((x + 30, y - 30), label, font=F_LABEL, fill=WHITE + (int(255 * a),), anchor='ls')

def s2(t):
    cam = cam2(t)
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    x, y = cam.xy(*DELAWARE)
    d = ImageDraw.Draw(img, 'RGBA')
    pin(d, x, y, 2.6, t, 'BIG EAR')
    a = ramp(t, 3.4, 3.8)
    if a > 0:
        d.text((x + 30, y + 14), 'Delaware, Ohio', font=F_SMALL, fill=GREY + (int(255 * a),), anchor='lt')
    top_label(img, '15 AUGUST 1977')
    return img

CAPS2 = [(0.0, 6.5, "Ohio, August 1977. The Big Ear telescope is listening for alien signals.", ['August', '1977.', 'Big', 'Ear', 'alien'])]

# ---------- S3: Big Ear diagram ----------
def s3(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, (6, 10, 20), (12, 20, 40), 1000)
    d.rectangle([0, 1000, W, H], fill=(18, 26, 20))
    k = ease(ramp(t, 0.2, 1.4))
    big_ear(d, 90, 990, 1000, col=(150, 165, 190), a=int(255 * k))
    # incoming radio waves bouncing: flat reflector -> parabola -> feed
    d2 = ImageDraw.Draw(img, 'RGBA')
    for i in range(3):
        q = ((t - 1.4 - i * 0.6) % 2.4) / 2.4 if t > 1.4 else -1
        if q < 0:
            continue
        pts = [(260, 200), (180, 850), (930, 900), (650, 970)]
        seg = q * 3
        j = min(int(seg), 2); f = seg - j
        x = lerp(pts[j][0], pts[j + 1][0], f); y = lerp(pts[j][1], pts[j + 1][1], f)
        d2.ellipse([x - 12, y - 12, x + 12, y + 12], fill=CYAN + (220,))
    a = ramp(t, 1.6, 2.0)
    d.line([90, 1060, 990, 1060], fill=AMBER + (int(255 * a),), width=4)
    d.line([90, 1045, 90, 1075], fill=AMBER + (int(255 * a),), width=4)
    d.line([990, 1045, 990, 1075], fill=AMBER + (int(255 * a),), width=4)
    text_c(d, (W / 2, 1110), 'ABOUT 3 FOOTBALL FIELDS', F_LABEL, AMBER + (int(255 * a),))
    a2 = ramp(t, 0.8, 1.2)
    d.text((150, 700), 'flat\nreflector', font=F_SMALL, fill=GREY + (int(255 * a2),), anchor='la')
    d.text((900, 760), 'curved\nreflector', font=F_SMALL, fill=GREY + (int(255 * a2),), anchor='ra')
    top_label(img, 'THE BIG EAR')
    return img

CAPS3 = [(0.0, 4.5, 'It is about the size of three football fields.', ['three', 'football', 'fields.'])]

# ---------- S4: drift curve ----------
CHARS = list('6EQUJ5')
LEV = [6, 14, 26, 30, 19, 5]
GX0, GX1, GY0, GYB = 140, 960, 440, 1080

def s4(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    # axes
    d.line([GX0, GY0, GX0, GYB], fill=GREY, width=3)
    d.line([GX0, GYB, GX1, GYB], fill=GREY, width=3)
    d.text((GX0, GYB + 30), '0 s', font=F_SMALL, fill=GREY, anchor='mt')
    d.text((GX1, GYB + 30), '72 s', font=F_SMALL, fill=GREY, anchor='mt')
    d.text((GX0 - 20, GY0), 'strength', font=F_SMALL, fill=GREY, anchor='rt')
    k = ramp(t, 0.3, 5.0)
    xs = np.linspace(GX0, GX1, 200)
    mu, sg = (GX0 + GX1) / 2, (GX1 - GX0) / 5.2
    ys = GYB - (GYB - GY0 - 40) * np.exp(-((xs - mu) ** 2) / (2 * sg * sg))
    n = int(200 * k)
    if n > 1:
        d.line(list(zip(xs[:n].tolist(), ys[:n].tolist())), fill=CYAN, width=7)
    bw = (GX1 - GX0) / 6
    for i, (c, lv) in enumerate(zip(CHARS, LEV)):
        cx = GX0 + bw * (i + 0.5)
        a = ramp(k * 6, i + 0.3, i + 0.8)
        if a <= 0:
            continue
        top = GYB - (GYB - GY0 - 40) * lv / 30
        d.rectangle([cx - bw * 0.32, top, cx + bw * 0.32, GYB], fill=AMBER + (int(70 * a),))
        d.text((cx, top - 18), c, font=F_MED, fill=WHITE + (int(255 * a),), anchor='ms')
    sec = int(72 * k)
    text_c(d, (W / 2, 310), f'{sec} s', F_HUGE, WHITE)
    top_label(img, 'EARTH TURNS, THE SKY DRIFTS PAST')
    return img

CAPS4 = [(0.0, 3.3, 'As Earth turns, the sky drifts through its view.', ['Earth', 'turns,']),
         (3.3, 6.5, 'The signal rises, peaks, and fades.', ['rises,', 'peaks,', 'fades.'])]

# ---------- S5: the printout ----------
rng5 = np.random.default_rng(5)
ALPH = '1111112222233344567'
ROWS = [''.join(rng5.choice(list(ALPH + '      '), 6)) for _ in range(16)]

def s5(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    px0, px1, py0, py1 = 200, 880, 230, 1130
    d.rectangle([px0, py0, px1, py1], fill=(232, 228, 214))
    for i in range(0, py1 - py0, 60):
        d.rectangle([px0, py0 + i, px1, py0 + i + 30], fill=(214, 228, 212))
    for y in range(py0 + 20, py1, 40):
        d.ellipse([px0 + 14, y - 7, px0 + 28, y + 7], fill=BG)
        d.ellipse([px1 - 28, y - 7, px1 - 14, y + 7], fill=BG)
    mono = font('Inter-SemiBold.otf', 40)
    col = 520
    for i in range(16):
        y = py0 + 50 + i * 54
        row = list(ROWS[i])
        if 5 <= i <= 10:
            row[2] = '6EQUJ5'[i - 5]
        for j, ch in enumerate(row):
            d.text((300 + j * 56, y), ch, font=mono, fill=(60, 60, 70), anchor='mm')
    # circle + Wow!
    a = ramp(t, 1.8, 2.4)
    cx = 300 + 2 * 56
    yc0, yc1 = py0 + 50 + 5 * 54 - 34, py0 + 50 + 10 * 54 + 34
    if a > 0:
        sweep = int(360 * a)
        d.arc([cx - 46, yc0, cx + 46, yc1], -90, -90 + sweep, fill=(210, 30, 30), width=7)
    a2 = ramp(t, 3.0, 3.4)
    if a2 > 0:
        wf = font('InterDisplay-Black.otf', 88)
        d.text((cx + 190, (yc0 + yc1) / 2 - 120), 'Wow!', font=wf, fill=(210, 30, 30, int(255 * a2)), anchor='lm')
    top_label(img, 'THE PRINTOUT')
    return img

CAPS5 = [(0.0, 6.0, 'Days later, astronomer Jerry Ehman circles it on a printout and writes: "Wow!"', ['Jerry', 'Ehman', 'printout', '"Wow!"'])]

# ---------- S6: 30x background ----------
def s6(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    gy = 1080
    k = ease(ramp(t, 0.8, 2.6))
    # noise bar
    nh = 22
    d.rectangle([220, gy - nh, 420, gy], fill=GREY)
    d.text((320, gy + 30), 'background', font=F_SMALL, fill=GREY, anchor='mt')
    d.text((320, gy + 70), 'noise', font=F_SMALL, fill=GREY, anchor='mt')
    sh = nh * 30 * k
    d.rectangle([640, gy - sh, 840, gy], fill=AMBER)
    d.text((740, gy + 30), 'the Wow!', font=F_SMALL, fill=AMBER, anchor='mt')
    d.text((740, gy + 70), 'signal', font=F_SMALL, fill=AMBER, anchor='mt')
    d.line([120, gy, 960, gy], fill=GREY, width=3)
    n = max(1, int(round(30 * k)))
    text_c(d, (W / 2, 310), f'×{n}', F_HUGE, WHITE)
    top_label(img, 'HOW STRONG?')
    return img

CAPS6 = [(0.0, 4.0, 'It was about thirty times stronger than the background noise.', ['thirty', 'times', 'stronger'])]

# ---------- S7: 1420 MHz ----------
def s7(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    # hydrogen atom diagram
    ax, ay = 540, 420
    d.ellipse([ax - 150, ay - 150, ax + 150, ay + 150], outline=(80, 100, 130), width=3)
    arr = to_arr(img)
    glow(arr, ax, ay, 26, (255, 150, 60), 1.4)
    th = t * 2.2
    glow(arr, ax + 150 * math.cos(th), ay + 150 * math.sin(th), 14, (110, 210, 255), 1.6)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    d.text((ax, ay + 190), 'HYDROGEN', font=F_LABEL, fill=WHITE, anchor='mt')
    # spectrum with spike
    sx0, sx1, sy = 120, 960, 1080
    rng = np.random.default_rng(int(t * 10))
    xs = np.linspace(sx0, sx1, 160)
    ys = sy - 18 - rng.uniform(0, 22, 160)
    k = ramp(t, 1.0, 1.8)
    ys[78:82] = sy - 18 - 300 * k * np.array([0.5, 1, 1, 0.5])
    d.line(list(zip(xs.tolist(), ys.tolist())), fill=CYAN, width=4)
    d.line([sx0, sy, sx1, sy], fill=GREY, width=3)
    a = ramp(t, 1.6, 2.0)
    text_c(d, (W / 2, sy - 370), '1420 MHz', F_MED, AMBER + (int(255 * a),))
    top_label(img, "HYDROGEN'S FREQUENCY")
    return img

CAPS7 = [(0.0, 3.6, "It came in at 1420 megahertz, hydrogen's natural frequency,", ['1420', 'megahertz,', "hydrogen's"]),
         (3.6, 7.0, 'where aliens might call.', ['aliens'])]

# ---------- S8: Sagittarius, never again ----------
rng8 = np.random.default_rng(8)
FIELD = np.c_[rng8.uniform(0, W, 420), rng8.uniform(220, 1180, 420), rng8.uniform(0.8, 3.0, 420)]

def s8(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    for x, y, r in FIELD:
        b = int(120 + 50 * r)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(b + 25, 255)))
    # scanning beam strip
    bx = 540
    d.rectangle([bx - 70, 220, bx + 70, 1180], fill=CYAN + (28,), outline=CYAN + (120,), width=3)
    # days counter
    day = int(lerp(1, 30, ramp(t, 0.6, 3.4)))
    text_c(d, (W / 2, 330), f'DAY {day}', F_MED, WHITE)
    a = ramp(t, 3.6, 4.0)
    if a > 0:
        d.rounded_rectangle([250, 640, 830, 760], radius=18, fill=(0, 0, 0, int(190 * a)), outline=RED + (int(255 * a),), width=6)
        text_c(d, (W / 2, 700), 'NOTHING', F_MED, RED + (int(255 * a),))
    text_c(d, (W / 2, 1120), 'toward SAGITTARIUS', F_LABEL, AMBER)
    top_label(img, 'LISTENING AGAIN')
    return img

CAPS8 = [(0.0, 3.6, 'They listened to that patch of sky, in Sagittarius, for a month.', ['month.', 'Sagittarius,']),
         (3.6, 6.5, 'Nothing. It was never detected again.', ['Nothing.', 'never'])]

# ---------- S9: Big Ear torn down ----------
def s9(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    sky(d, (10, 18, 36), (40, 60, 90), 1000)
    k = ease(ramp(t, 1.0, 3.2))
    d.rectangle([0, 1000, W, H], fill=(int(lerp(18, 34, k)), int(lerp(26, 92, k)), int(lerp(20, 44, k))))
    a = int(255 * (1 - k))
    if a > 0:
        big_ear(d, 90, 990, 1000 + 160 * k, col=(150, 165, 190), a=a)
    # golf flag (an object)
    fa = ramp(t, 3.0, 3.5)
    if fa > 0:
        fx, fy = 700, 1000
        d.ellipse([fx - 40, fy - 8, fx + 40, fy + 8], fill=(10, 20, 12, int(255 * fa)))
        d.line([fx, fy, fx, fy - 260], fill=(230, 230, 230, int(255 * fa)), width=6)
        d.polygon([(fx, fy - 260), (fx + 120, fy - 225), (fx, fy - 190)], fill=RED + (int(255 * fa),))
    ab = 1 - ramp(t, 0.9, 1.3)
    if ab > 0:
        text_c(d, (W / 2, 470), '1998', F_BIG, WHITE + (int(235 * ab),))
    top_label(img, 'THE END OF BIG EAR')
    return img

CAPS9 = [(0.0, 4.6, 'In 1998, Big Ear was torn down for a golf course.', ['1998,', 'torn', 'down', 'golf'])]

# ---------- S10: modern idea + end ----------
def s10(t):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_stars(d, t, 0.6, ymax=H)
    arr = to_arr(img)
    # magnetar (dead star) on the left
    mx, my = 200, 420
    glow(arr, mx, my, 30, (200, 220, 255), 1.6)
    # hydrogen cloud on the right
    cx, cy = 760, 820
    rng = np.random.default_rng(10)
    flash = 0.0
    if t >= 2.2:
        flash = math.exp(-(t - 2.2) * 0.9)
    for _ in range(14):
        ox, oy, r = rng.uniform(-170, 170), rng.uniform(-110, 110), rng.uniform(70, 130)
        glow(arr, cx + ox, cy + oy, r, (60, 90, 160), 0.22 + 0.8 * flash)
    # flare beam travelling
    if 0.5 <= t < 2.3:
        e = ramp(t, 0.5, 2.2)
        for j in range(20):
            q = max(e - j * 0.02, 0)
            glow(arr, lerp(mx, cx, q), lerp(my, cy, q), 16 - j * 0.5, (255, 150, 60), 0.6 * (1 - j / 20))
    if flash > 0:
        glow(arr, cx, cy, 90, (110, 210, 255), 1.6 * flash)
    img = to_img(arr)
    d = ImageDraw.Draw(img, 'RGBA')
    a0 = 1 - ramp(t, 6.4, 6.8)
    d.text((mx, my + 60), 'MAGNETAR', font=F_SMALL, fill=GREY + (int(255 * ramp(t, 0.2, 0.6) * a0),), anchor='mt')
    d.text((cx, cy + 190), 'COLD HYDROGEN CLOUD', font=F_SMALL, fill=GREY + (int(255 * ramp(t, 0.2, 0.6) * a0),), anchor='mt')
    a = ramp(t, 4.6, 5.0) * a0
    if a > 0:
        d.rounded_rectangle([170, 230, 910, 360], radius=22, fill=(0, 0, 0, int(170 * a)))
        parts = [('ALIENS', F_MED, WHITE), (' or ', F_LABEL, GREY), ('NATURE?', F_MED, AMBER)]
        tw = sum(d.textlength(p_, font=f_) for p_, f_, _ in parts)
        x = W / 2 - tw / 2
        for p_, f_, c_ in parts:
            d.text((x, 295), p_, font=f_, fill=c_ + (int(255 * a),), anchor='lm')
            x += d.textlength(p_, font=f_)
    top_label(img, 'A NEW IDEA · 2024', a0)
    a2 = ramp(t, 6.6, 7.0)
    if a2 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(170 * a2)))
        text_c(d, (W / 2, 600), 'FOLLOW', F_HUGE, WHITE + (int(255 * a2),))
        text_c(d, (W / 2, 720), 'for more unexplained history', F_MED, AMBER + (int(255 * a2),))
    return img

CAPS10 = [(0.0, 4.6, 'In 2024, scientists blamed a flare from a dead star, lighting up a cold hydrogen cloud.', ['2024,', 'flare', 'hydrogen']),
          (4.6, 6.8, "Aliens or nature? It's still debated.", ['debated.'])]

SCENES = [
    ('s01', s1, 9.0, CAPS1),
    ('s02', s2, 6.5, CAPS2),
    ('s03', s3, 4.5, CAPS3),
    ('s04', s4, 6.5, CAPS4),
    ('s05', s5, 6.0, CAPS5),
    ('s06', s6, 4.0, CAPS6),
    ('s07', s7, 7.0, CAPS7),
    ('s08', s8, 6.5, CAPS8),
    ('s09', s9, 4.6, CAPS9),
    ('s10', s10, 8.0, CAPS10),
]

SPOKEN = {
    'In 1977, a signal arrived from deep space. It lasted 72 seconds…':
        'In nineteen seventy-seven, a signal arrived from deep space. It lasted seventy-two seconds...',
    "Ohio, August 1977. The Big Ear telescope is listening for alien signals.":
        'Ohio, August, nineteen seventy-seven. The Big Ear telescope is listening for alien signals.',
    'Days later, astronomer Jerry Ehman circles it on a printout and writes: "Wow!"':
        'Days later, astronomer Jerry Eeman circles it on a printout, and writes: Wow!',
    "It came in at 1420 megahertz, hydrogen's natural frequency,": "It came in at fourteen twenty megahertz, hydrogen's natural frequency,",
    'In 1998, Big Ear was torn down for a golf course.': 'In nineteen ninety-eight, Big Ear was torn down for a golf course.',
    'In 2024, scientists blamed a flare from a dead star, lighting up a cold hydrogen cloud.':
        'In twenty twenty-four, scientists blamed a flare from a dead star, lighting up a cold hydrogen cloud.',
}


def SFX(tr, G):
    tr.wind([(0, 0.9), (G('s02', 0), 0.6), (G('s04', 0), 0.45), (G('s08', 0), 0.6),
             (G('s09', 0), 0.8), (G('s10', 0), 0.6), (G('s10', 7.5), 0.6), (G('s10', 8.0), 0.0)])
    tr.whoosh(G('s01', 0.4), G('s01', 3.0), 0.2, 600, 3000)
    tr.rumble(G('s01', 3.0), G('s01', 7.0), 0.18)
    tr.whoosh(G('s02', 0.0), G('s02', 3.4), 0.1, 300, 1200)
    tr.rumble(G('s04', 0.3), G('s04', 5.0), 0.12)
    tr.rumble(G('s09', 1.0), G('s09', 3.3), 0.3)
    tr.snaps(G('s09', 1.0), G('s09', 3.0), 40, 0.2)
    tr.whoosh(G('s10', 0.5), G('s10', 2.2), 0.22)
    tr.boom(G('s10', 2.2), 0.5, 3.0)

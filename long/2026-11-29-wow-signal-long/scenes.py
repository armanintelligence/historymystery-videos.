"""Long video: The Wow! Signal, full story (1920x1080). Build with HM_FORMAT=long.
Visuals: skies, maps, the telescope structure, printouts, charts, diagrams, star fields. No living beings."""
import math, numpy as np
from PIL import Image, ImageDraw
from lib import *

assert W == 1920, 'build with HM_FORMAT=long'
DELAWARE = (-83.07, 40.30)
RED = (255, 90, 70)
INK = (210, 30, 30)
F_TITLE = font('InterDisplay-Black.otf', 150)
F_MONO = font('Inter-SemiBold.otf', 34)
VB = 830  # bottom of the visual area (captions sit below)


def new(bg=BG):
    img = Image.new('RGB', (W, H), bg)
    return img, ImageDraw.Draw(img, 'RGBA')


def sky(d, top=(4, 6, 13), bot=(14, 24, 51), ymax=H):
    for i in range(0, ymax, 6):
        k = i / ymax
        d.rectangle([0, i, W, i + 6], fill=tuple(int(lerp(a, b, k)) for a, b in zip(top, bot)))


def A(c, a):
    return c + (int(255 * max(0, min(1, a))),)


def big_ear(d, gx0, gx1, gy, col=(150, 165, 190), a=1.0, s=1.0):
    """Side view: tilting flat reflector (left), ground plane, curved reflector (right), feed hut."""
    c = A(col, a)
    d.rectangle([gx0, gy, gx1, gy + 8 * s], fill=A((150, 165, 190), a))
    fx = gx0 + 30 * s
    top = (fx + 60 * s, gy - 200 * s)
    d.line([fx, gy, top[0], top[1]], fill=c, width=int(12 * s))
    for k in (0.33, 0.66):
        px, py = lerp(fx, top[0], k), lerp(gy, top[1], k)
        d.line([px, py, px - (50 * k + 30) * s, gy], fill=c, width=int(4 * s) + 1)
    pts = [(gx1 - 25 * s - 50 * s * (i / 20) ** 2, gy - 140 * s * i / 20) for i in range(21)]
    d.line(pts, fill=c, width=int(12 * s))
    for k in (0.3, 0.6, 0.9):
        x, y = pts[int(k * 20)]
        d.line([x, y, x + 36 * s, gy], fill=c, width=int(4 * s) + 1)
    hx = (gx0 + gx1) / 2 + 60 * s
    d.rectangle([hx - 20 * s, gy - 30 * s, hx + 20 * s, gy], fill=A((90, 100, 120), a))


def card(d, x0, y0, x1, y1, a=1.0):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(0, 0, 0, int(170 * a)))


# ---------- 1. cold open ----------
def c01(t):
    img, d = new()
    sky(d, ymax=VB)
    draw_stars(d, t, ymax=VB - 40)
    d.rectangle([0, VB - 40, W, H], fill=(5, 8, 12))
    big_ear(d, 560, 1360, VB - 40, col=(28, 34, 46))
    arr = to_arr(img)
    if 4.0 <= t < 7.0:
        e = ramp(t, 4.0, 7.0)
        y = lerp(60, VB - 80, e ** 1.2)
        glow(arr, 980, y, 40, (110, 210, 255), 0.8)
        glow(arr, 980, y, 12, (230, 250, 255), 1.4)
    if t >= 7.0:
        glow(arr, 1000, VB - 60, 260, (110, 210, 255), 0.9 * math.exp(-(t - 7.0) * 0.8))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    for i in range(5):
        tt = t - 7.0 - i * 0.4
        if tt > 0:
            r = 30 + tt * 220
            d.arc([1000 - r, VB - 60 - r, 1000 + r, VB - 60 + r], 180, 360, fill=A(CYAN, 0.85 * max(0, 1 - tt / 2.6)), width=6)
    a = ramp(t, 8.0, 8.5) * (1 - ramp(t, 12.5, 13.0))
    text_c(d, (W / 2, 300), '72 SECONDS', F_HUGE, A(WHITE, a))
    a2 = ramp(t, 13.2, 13.6)
    text_c(d, (W / 2, 300), 'NEVER HEARD AGAIN', F_HUGE, A(RED, a2))
    top_label(img, 'OHIO · 1977', ramp(t, 0.2, 0.6))
    return img

CAP01 = [(0, 5, 'On a summer night in 1977, a radio telescope in Ohio heard something no one could explain.', ['1977,', 'Ohio']),
         (5, 10, 'For seventy-two seconds, a signal rose out of the noise of space… and then it was gone.', ['seventy-two', 'seconds,']),
         (10, 15, 'In almost fifty years, no one has heard it again.', ['no', 'one'])]

# ---------- 2. title ----------
def c02(t):
    img, d = new()
    draw_stars(d, t, 0.8)
    a = ramp(t, 0.2, 0.9)
    text_c(d, (W / 2, 380), 'THE WOW! SIGNAL', F_TITLE, A(WHITE, a))
    text_c(d, (W / 2, 520), '72 seconds from deep space, and the science of what it was', F_MED, A(AMBER, ramp(t, 0.8, 1.4)))
    return img

CAP02 = [(0, 5.5, 'This is the story of the Wow! signal, and what science now thinks it really was.', ['Wow!', 'science'])]

# ---------- 3. Nature 1959 ----------
def c03(t):
    img, d = new()
    a = ease(ramp(t, 0.2, 1.0))
    x0 = lerp(2000, 560, a)
    d.rectangle([x0, 130, x0 + 800, 800], fill=(236, 230, 214))
    d.text((x0 + 400, 200), 'NATURE', font=F_HUGE, fill=(30, 30, 30), anchor='mm')
    d.text((x0 + 400, 290), '19 September 1959', font=F_SMALL, fill=(90, 90, 90), anchor='mm')
    d.line([x0 + 60, 320, x0 + 740, 320], fill=(60, 60, 60), width=3)
    d.text((x0 + 400, 370), 'Searching for Interstellar', font=F_LABEL, fill=(20, 20, 20), anchor='mm')
    d.text((x0 + 400, 415), 'Communications', font=F_LABEL, fill=(20, 20, 20), anchor='mm')
    d.text((x0 + 400, 470), 'GIUSEPPE COCCONI · PHILIP MORRISON', font=F_SMALL, fill=(90, 90, 90), anchor='mm')
    for i in range(7):
        for c in range(2):
            w_ = 330 if (i + c) % 3 else 260
            d.rectangle([x0 + 60 + c * 360, 520 + i * 38, x0 + 60 + c * 360 + w_, 534 + i * 38], fill=(150, 145, 135))
    a2 = ramp(t, 6.5, 7.0)
    if a2 > 0:
        card(d, 560, 380, 1360, 520, a2)
        text_c(d, (W / 2, 450), 'WHICH FREQUENCY?', F_MED, A(AMBER, a2))
    top_label(img, 'CHAPTER 1 · HOW DO YOU LISTEN FOR ALIENS?')
    return img

CAP03 = [(0, 2.5, 'In 1959, two physicists at Cornell University…', ['1959,', 'Cornell']),
         (2.5, 5.5, '…Giuseppe Cocconi and Philip Morrison, asked a simple question.', ['Cocconi', 'Morrison,']),
         (5.5, 9.5, 'If another civilization wanted to be heard, which radio frequency would it use?', ['frequency'])]

# ---------- 4. hydrogen ----------
def c04(t):
    img, d = new()
    ax, ay = 520, 540
    d.ellipse([ax - 200, ay - 200, ax + 200, ay + 200], outline=(80, 100, 130), width=3)
    arr = to_arr(img)
    glow(arr, ax, ay, 34, (255, 150, 60), 1.4)
    th = t * 1.6
    glow(arr, ax + 200 * math.cos(th), ay + 200 * math.sin(th), 18, (110, 210, 255), 1.6)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.text((ax, ay + 230), 'HYDROGEN', font=F_LABEL, fill=WHITE, anchor='mt')
    sx0, sx1, sy = 960, 1760, 760
    rng = np.random.default_rng(int(t * 10))
    xs = np.linspace(sx0, sx1, 200)
    ys = sy - 14 - rng.uniform(0, 18, 200)
    k = ramp(t, 3.5, 4.5)
    ys[98:102] = sy - 14 - 360 * k * np.array([0.5, 1, 1, 0.5])
    d.line(list(zip(xs.tolist(), ys.tolist())), fill=CYAN, width=4)
    d.line([sx0, sy, sx1, sy], fill=GREY, width=3)
    d.text((sx0, sy + 20), 'radio frequency →', font=F_SMALL, fill=GREY, anchor='lt')
    text_c(d, ((sx0 + sx1) / 2, sy - 420), '≈1420 MHz', F_MED, A(AMBER, ramp(t, 4.2, 4.6) * (1 - ramp(t, 8.2, 8.5))))
    a = ramp(t, 8.5, 9.0)
    if a > 0:
        card(d, 160, 110, 1760, 300, a)
        text_c(d, (W / 2, 165), '“a unique, objective standard of frequency,', F_LABEL, A(WHITE, a))
        text_c(d, (W / 2, 220), 'which must be known to every observer in the universe”', F_LABEL, A(WHITE, a))
        text_c(d, (W / 2, 270), 'Cocconi & Morrison, Nature, 1959', F_SMALL, A(GREY, a))
    top_label(img, "HYDROGEN'S RADIO FREQUENCY")
    return img

CAP04 = [(0, 4, 'Their answer was hydrogen, the most common element in the universe.', ['hydrogen,']),
         (4, 8.5, 'Neutral hydrogen gives off radio waves at one exact frequency: about 1420 megahertz.', ['1420', 'megahertz.']),
         (8.5, 13, 'They called it a standard of frequency known to every observer in the universe.', ['every', 'observer']),
         (13, 15.5, 'So that is where the listeners should tune in.', ['tune', 'in.'])]

# ---------- 5. map ----------
def c05(t):
    k = ease(ramp(t, 0.0, 4.0))
    cam = Cam(lerp(-60, DELAWARE[0], k), lerp(35, DELAWARE[1], k), math.exp(lerp(math.log(5), math.log(55), k)))
    img = draw_map(Image.new('RGB', (W, H)), cam, rivers=True)
    d = ImageDraw.Draw(img, 'RGBA')
    x, y = cam.xy(*DELAWARE)
    a = ramp(t, 3.6, 4.0)
    if a > 0:
        pr = 30 + 40 * ((t - 3.6) % 1.2) / 1.2
        d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=A(AMBER, 0.8 * (1 - ((t - 3.6) % 1.2) / 1.2)), width=4)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=A(AMBER, a))
        d.text((x + 30, y - 30), 'BIG EAR', font=F_LABEL, fill=A(WHITE, a), anchor='ls')
        d.text((x + 30, y + 14), 'near Delaware, Ohio', font=F_SMALL, fill=A(GREY, a), anchor='lt')
    top_label(img, 'CHAPTER 2 · THE BIG EAR')
    return img

CAP05 = [(0, 4, 'In Ohio, a telescope was built for exactly that kind of listening.', ['Ohio,']),
         (4, 8.5, 'It was designed by radio astronomer John Kraus, and switched on in 1963.', ['John', 'Kraus,', '1963.'])]

# ---------- 6. Big Ear diagram ----------
def c06(t):
    img, d = new()
    sky(d, (6, 10, 20), (12, 20, 40), VB - 80)
    d.rectangle([0, VB - 80, W, H], fill=(18, 26, 20))
    k = ramp(t, 0.2, 1.2)
    big_ear(d, 260, 1660, VB - 80, a=k, s=2.0)
    for i in range(3):
        if t < 1.4:
            break
        q = ((t - 1.4 - i * 0.6) % 2.4) / 2.4
        pts = [(520, 60), (420, VB - 420), (1560, VB - 300), (1090, VB - 140)]
        seg = q * 3; j = min(int(seg), 2); f = seg - j
        x = lerp(pts[j][0], pts[j + 1][0], f); y = lerp(pts[j][1], pts[j + 1][1], f)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=A(CYAN, 0.86))
    a2 = ramp(t, 1.0, 1.4)
    d.text((300, 330), 'flat reflector', font=F_LABEL, fill=A(WHITE, a2), anchor='la')
    d.text((1640, 420), 'curved reflector', font=F_LABEL, fill=A(WHITE, a2), anchor='ra')
    d.text((640, VB - 28), 'aluminium-covered ground plane', font=F_SMALL, fill=A(GREY, a2), anchor='ms')
    a = ramp(t, 6.5, 7.0)
    d.line([260, VB - 12, 1660, VB - 12], fill=A(AMBER, a), width=4)
    for x in (260, 1660):
        d.line([x, VB - 27, x, VB + 3], fill=A(AMBER, a), width=4)
    text_c(d, (W / 2, 160), 'ABOUT THE SIZE OF 3 FOOTBALL FIELDS', F_MED, A(AMBER, a))
    top_label(img, 'THE BIG EAR')
    return img

CAP06 = [(0, 2.0, "It didn't look like a dish.", ['dish.']),
         (2.0, 6.5, 'It was a giant flat reflector, a curved reflector, and an aluminium-covered field in between.', ['flat', 'curved', 'reflector,']),
         (6.5, 9.5, 'Altogether, it was about the size of three football fields.', ['three', 'football', 'fields.'])]

# ---------- 7. sky survey -> SETI ----------
rng7 = np.random.default_rng(7)
SRC = np.c_[rng7.uniform(160, 1760, 1400), rng7.uniform(160, 760, 1400), rng7.uniform(0, 1, 1400)]

def c07(t):
    img, d = new()
    d.rounded_rectangle([140, 140, 1780, 780], radius=30, outline=(60, 80, 110), width=3)
    k = ramp(t, 0.3, 5.5)
    for x, y, r in SRC:
        if r < k:
            new_ = r * 1400 % 2 < 1
            col = AMBER if new_ else CYAN
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col)
    n = int(20000 * k)
    a1 = 1 - ramp(t, 8.0, 8.5)
    card(d, 640, 380, 1280, 540, a1)
    text_c(d, (W / 2, 440), f'{n:,}', F_HUGE, A(WHITE, a1))
    text_c(d, (W / 2, 510), 'radio sources measured', F_SMALL, A(GREY, a1))
    a2 = ramp(t, 8.5, 9.0)
    if a2 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(200 * a2)))
        text_c(d, (W / 2, 330), '1973', F_BIG, A(WHITE, a2))
        text_c(d, (W / 2, 520), 'THE SEARCH FOR ALIEN SIGNALS BEGINS', F_MED, A(AMBER, a2))
    top_label(img, 'MAPPING THE RADIO SKY' if t < 8.5 else 'A NEW JOB')
    return img

CAP07 = [(0, 3.0, 'For years it mapped the radio sky, measuring nearly twenty thousand radio sources…', ['twenty', 'thousand']),
         (3.0, 5.5, '…about half of them never measured before.', ['half']),
         (5.5, 9, 'Then, in 1973, it turned to a new search: signals from alien civilizations.', ['1973,', 'alien']),
         (9, 13, 'Guinness World Records later called it the longest-running search of its kind.', ['longest-running'])]

# ---------- 8. Earth turns, sky drifts ----------
rng8 = np.random.default_rng(8)
FIELD = np.c_[rng8.uniform(0, 4000, 700), rng8.uniform(120, 560, 700), rng8.uniform(0.8, 2.6, 700)]

def c08(t):
    img, d = new()
    off = t * 160
    for x, y, r in FIELD:
        xx = (x - off) % 4000 - 1000
        if -10 < xx < W + 10:
            b = int(130 + 40 * r)
            d.ellipse([xx - r, y - r, xx + r, y + r], fill=(b, b, min(b + 25, 255)))
    bx = 960
    d.rectangle([bx - 90, 120, bx + 90, 560], fill=A(CYAN, 0.1), outline=A(CYAN, 0.5), width=3)
    text_c(d, (bx, 590), 'BIG EAR’S BEAM (fixed)', F_SMALL, CYAN)
    # source crossing
    sxp = lerp(1900, 20, ramp(t, 2.0, 12.0))
    arr = to_arr(img)
    glow(arr, sxp, 340, 10, (255, 200, 120), 1.4)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    # strength trace below
    gx0, gx1, gy = 360, 1560, 800
    d.line([gx0, gy, gx1, gy], fill=GREY, width=3)
    xs = np.arange(gx0, gx1, 4)
    pos = lerp(1900, 20, np.clip((np.linspace(0, 1, len(xs))), 0, 1))
    done = ramp(t, 2.0, 12.0)
    pts = []
    for i, x in enumerate(xs):
        q = i / len(xs)
        if q > done:
            break
        sp = lerp(1900, 20, q)
        pts.append((x, gy - 170 * math.exp(-((sp - bx) / 110) ** 2)))
    if len(pts) > 1:
        d.line(pts, fill=AMBER, width=5)
    d.text((gx0 - 20, gy - 85), 'signal\nstrength', font=F_SMALL, fill=GREY, anchor='rm')
    top_label(img, 'AS THE EARTH TURNS, THE SKY DRIFTS PAST')
    return img

CAP08 = [(0, 4.5, "Big Ear couldn't turn to follow the stars. Instead, it let the Earth do the work.", ['Earth']),
         (4.5, 8, 'As the planet turned, the sky drifted slowly through its beam.', ['drifted']),
         (8, 13, 'So a signal from one point in the sky would rise, peak and fade over about seventy-two seconds.', ['rise,', 'peak', 'fade', 'seventy-two'])]

# ---------- 9. 50 channels ----------
rng9 = np.random.default_rng(9)
GRID = rng9.choice(list('     1111112223'), (11, 50))

def c09(t):
    img, d = new()
    x0, y0, cw, rh = 210, 190, 30, 42
    rows = min(11, int(ramp(t, 3.0, 12.0) * 11) + (1 if t > 3 else 0))
    for c in range(50):
        a = ramp(t, 0.2 + c * 0.03, 0.5 + c * 0.03)
        d.rectangle([x0 + c * cw + 3, y0 - 40, x0 + c * cw + cw - 3, y0 - 14], fill=A(CYAN, 0.6 * a))
    for r in range(rows):
        for c in range(50):
            ch = GRID[r][c]
            if ch != ' ':
                d.text((x0 + c * cw + cw / 2, y0 + 20 + r * rh), ch, font=F_MONO, fill=(200, 205, 215), anchor='mm')
    a = ramp(t, 1.0, 1.4)
    d.text((x0, y0 - 60), '50 CHANNELS · EACH 10 kHz WIDE', font=F_LABEL, fill=A(AMBER, a), anchor='ls')
    d.text((x0 + 50 * cw, y0 - 60), 'one row ≈ every 12 s', font=F_SMALL, fill=A(GREY, ramp(t, 4, 4.4)), anchor='rs')
    a2 = ramp(t, 9.5, 10)
    if a2 > 0:
        card(d, 420, 700, 1500, 800, a2)
        text_c(d, (W / 2, 750), 'blank = nothing   ·   1–9 = weak   ·   A–Z = stronger than 9', F_LABEL, A(WHITE, a2))
    top_label(img, 'HOW BIG EAR LISTENED')
    return img

CAP09 = [(0, 4.5, 'A computer listened on fifty narrow channels at once, each just ten kilohertz wide.', ['fifty', 'ten', 'kilohertz']),
         (4.5, 8.5, 'Every twelve seconds or so, it printed a row of characters, one for each channel.', ['twelve', 'seconds']),
         (8.5, 13.5, 'A blank meant nothing, numbers meant weak, and letters meant stronger than nine.', ['letters', 'stronger'])]

# ---------- 10. the night ----------
def c10(t):
    img, d = new()
    sky(d, ymax=VB)
    draw_stars(d, t, ymax=VB - 40)
    d.rectangle([0, VB - 40, W, H], fill=(5, 8, 12))
    big_ear(d, 560, 1360, VB - 40, col=(28, 34, 46))
    a = ramp(t, 0.3, 0.8)
    card(d, 610, 220, 1310, 470, a)
    text_c(d, (W / 2, 300), '15 · 08 · 1977', F_MED, A(GREY, a))
    text_c(d, (W / 2, 400), '11:16 PM', F_HUGE, A(WHITE, a))
    arr = to_arr(img)
    if t > 3:
        glow(arr, lerp(1700, 200, ramp(t, 3, 7)), 140, 14, (255, 200, 120), 1.2)
    img = to_img(arr)
    top_label(img, 'CHAPTER 3 · THE NIGHT OF THE SIGNAL')
    return img

CAP10 = [(0, 6, 'On the night of August 15th, 1977, at about 11:16 p.m., something drifted through the beam.', ['August', '15th,', '11:16'])]

# ---------- 11-13. printout ----------
rng11 = np.random.default_rng(11)
ROWS = [''.join(rng11.choice(list('1111112222233344   '), 12)) for _ in range(14)]

def printout(d, t, reveal=6, circle=0.0, wow=0.0):
    px0, px1, py0, py1 = 560, 1360, 110, 830
    d.rectangle([px0, py0, px1, py1], fill=(232, 228, 214))
    for i in range(0, py1 - py0, 64):
        d.rectangle([px0, py0 + i, px1, py0 + i + 32], fill=(214, 228, 212))
    for y in range(py0 + 20, py1, 40):
        d.ellipse([px0 + 14, y - 7, px0 + 28, y + 7], fill=BG)
        d.ellipse([px1 - 28, y - 7, px1 - 14, y + 7], fill=BG)
    cx = 700 + 1 * 52
    for i in range(14):
        y = py0 + 64 + i * 48
        row = list(ROWS[i])
        if 4 <= i <= 9:
            row[1] = '6EQUJ5'[i - 4] if i - 4 < reveal else ' '
        for j, ch in enumerate(row):
            d.text((700 + j * 52, y), ch, font=F_MONO, fill=(60, 60, 70), anchor='mm')
    yc0, yc1 = py0 + 64 + 4 * 48 - 30, py0 + 64 + 9 * 48 + 30
    if circle > 0:
        d.arc([cx - 40, yc0, cx + 40, yc1], -90, -90 + int(360 * circle), fill=INK, width=7)
    if wow > 0:
        d.text((cx - 70, (yc0 + yc1) / 2), 'Wow!', font=font('InterDisplay-Black.otf', 96), fill=A(INK, wow), anchor='rm')
    d.text((cx, py0 + 6), 'ch 2', font=F_SMALL, fill=(120, 120, 120), anchor='mt')

def c11(t):
    img, d = new()
    printout(d, t, reveal=int(ramp(t, 1.0, 5.5) * 6.99))
    top_label(img, 'CHANNEL 2')
    return img

CAP11 = [(0, 6, 'In channel two, the computer printed six characters: six, E, Q, U, J, five.', ['six,', 'E,', 'Q,', 'U,', 'J,', 'five.'])]

CHARS, LEV = list('6EQUJ5'), [6, 14, 26, 30, 19, 5]

def c12(t):
    img, d = new()
    gx0, gx1, gy0, gyb = 420, 1500, 200, 760
    d.line([gx0, gy0, gx0, gyb], fill=GREY, width=3)
    d.line([gx0, gyb, gx1, gyb], fill=GREY, width=3)
    d.text((gx0 - 20, gy0), 'strength', font=F_SMALL, fill=GREY, anchor='rt')
    d.text((gx0, gyb + 20), '0 s', font=F_SMALL, fill=GREY, anchor='mt')
    d.text((gx1, gyb + 20), '≈72 s', font=F_SMALL, fill=GREY, anchor='mt')
    k = ramp(t, 0.3, 5.0)
    bw = (gx1 - gx0) / 6
    for i, (c, lv) in enumerate(zip(CHARS, LEV)):
        a = ramp(k * 6, i + 0.2, i + 0.8)
        if a <= 0:
            continue
        cx = gx0 + bw * (i + 0.5)
        top = gyb - (gyb - gy0 - 40) * lv / 30
        d.rectangle([cx - bw * 0.32, top, cx + bw * 0.32, gyb], fill=A(AMBER, 0.35 * a))
        d.text((cx, top - 14), c, font=F_MED, fill=A(WHITE, a), anchor='ms')
    xs = np.linspace(gx0, gx1, 200)
    mu, sg = (gx0 + gx1) / 2, (gx1 - gx0) / 5.2
    ys = gyb - (gyb - gy0 - 40) * np.exp(-((xs - mu) ** 2) / (2 * sg * sg))
    n = int(200 * k)
    if n > 1:
        d.line(list(zip(xs[:n].tolist(), ys[:n].tolist())), fill=CYAN, width=6)
    a = ramp(t, 7.0, 7.5)
    if a > 0:
        card(d, 1540, 260, 1860, 470, a)
        text_c(d, (1700, 340), '×30', F_HUGE, A(AMBER, a))
        text_c(d, (1700, 430), 'the background noise', F_SMALL, A(WHITE, a))
    top_label(img, 'RISE, PEAK, FADE')
    return img

CAP12 = [(0, 5.5, 'They rose and fell exactly the way a source in the sky should, as the Earth carried it past.', ['rose', 'fell']),
         (5.5, 10, 'At its peak, the letter U, it was about thirty times stronger than the background noise.', ['U,', 'thirty', 'times'])]

def c13(t):
    img, d = new()
    printout(d, t, 6, ease(ramp(t, 3.2, 4.4)), ramp(t, 5.2, 5.7))
    top_label(img, 'A FEW DAYS LATER')
    return img

CAP13 = [(0, 4, 'A few days later, astronomer Jerry Ehman was going through the printouts.', ['Jerry', 'Ehman']),
         (4, 8, 'He highlighted the six characters, and wrote one word in the margin in red: Wow!', ['red:', 'Wow!'])]

# ---------- 14. why it mattered ----------
def c14(t):
    img, d = new()
    sx0, sx1, sy = 260, 1660, 700
    cw = (sx1 - sx0) / 50
    rng = np.random.default_rng(int(t * 8))
    for c in range(50):
        h = rng.uniform(8, 30)
        if c == 1:
            h = 420 * ramp(t, 3.0, 4.0) + 20
        d.rectangle([sx0 + c * cw + 2, sy - h, sx0 + c * cw + cw - 2, sy], fill=AMBER if c == 1 else (70, 90, 120))
    d.line([sx0, sy, sx1, sy], fill=GREY, width=3)
    d.text((sx0, sy + 20), '50 channels →', font=F_SMALL, fill=GREY, anchor='lt')
    items = [('STRONG', 2.0), ('NARROW: 1 CHANNEL OF 50', 4.5), ('NEAR 1420 MHz', 8.0)]
    for i, (s, t0) in enumerate(items):
        a = ramp(t, t0, t0 + 0.4)
        d.ellipse([820, 190 + i * 80 - 10, 840, 190 + i * 80 + 10], fill=A(AMBER, a))
        d.text((865, 190 + i * 80), s, font=F_LABEL, fill=A(WHITE, a), anchor='lm')
    a = ramp(t, 11.5, 12.0)
    if a > 0:
        card(d, 470, 450, 1450, 560, a)
        text_c(d, (W / 2, 505), 'NO GLITCH · NO KNOWN SOURCE', F_MED, A(CYAN, a))
    top_label(img, 'CHAPTER 4 · WHY IT MATTERED')
    return img

CAP14 = [(0, 2.5, 'Three things made it special.', ['Three']),
         (2.5, 4.5, 'It was strong.', ['strong.']),
         (4.5, 7.5, 'It sat in one narrow channel, the kind of signal SETI scientists hoped a transmitter would make.', ['one', 'narrow']),
         (7.5, 11.5, 'And it was close to hydrogen’s frequency, right where Cocconi and Morrison said to listen.', ['hydrogen’s', 'frequency,']),
         (11.5, 15.5, 'The team found no glitch in the system, and no known source that could explain it.', ['no', 'glitch', 'known', 'source'])]

# ---------- 15. two horns ----------
def c15(t):
    img, d = new()
    hy = 560
    for i, (hx, name) in enumerate(((760, 'HORN 1'), (1160, 'HORN 2'))):
        d.polygon([(hx - 70, hy + 120), (hx + 70, hy + 120), (hx + 30, hy), (hx - 30, hy)], fill=(120, 135, 160))
        d.text((hx, hy + 150), name, font=F_LABEL, fill=WHITE, anchor='mt')
        d.rectangle([hx - 60, 160, hx + 60, hy - 20], fill=A(CYAN, 0.08), outline=A(CYAN, 0.4), width=2)
    sx = lerp(1900, 20, ramp(t, 2.0, 11.0))
    arr = to_arr(img)
    glow(arr, sx, 220, 12, (255, 200, 120), 1.4)
    if abs(sx - 1160) < 80:
        glow(arr, 1160, hy + 60, 90, (255, 150, 60), 1.0 * (1 - abs(sx - 1160) / 80))
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a1 = ramp(t, 4.0, 4.3)
    d.text((1160, 120), '✓ SEEN', font=F_LABEL, fill=A(AMBER, a1), anchor='mm')
    a2 = ramp(t, 8.5, 8.8)
    if a2 > 0:
        d.text((760, 120), 'NOT SEEN', font=F_LABEL, fill=A(RED, a2), anchor='mm')
        d.line([700, hy + 20, 820, hy + 110], fill=A(RED, a2), width=8)
        d.line([700, hy + 110, 820, hy + 20], fill=A(RED, a2), width=8)
    a3 = ramp(t, 5.0, 5.4)
    d.line([1100, 330, 820, 330], fill=A(GREY, a3), width=3)
    d.polygon([(820, 318), (800, 330), (820, 342)], fill=A(GREY, a3))
    d.text((960, 310), 'a few minutes later?', font=F_SMALL, fill=A(GREY, a3), anchor='ms')
    top_label(img, 'CHAPTER 5 · THE MISSING ECHO')
    return img

CAP15 = [(0, 4.5, 'But there was a puzzle. Big Ear listened through two feed horns, side by side.', ['two', 'feed', 'horns,']),
         (4.5, 8.5, 'A real source in the sky should have passed through one, and then the other, a few minutes later.', ['one,', 'other,']),
         (8.5, 10.5, 'It showed up only once.', ['once.']),
         (10.5, 14, 'Either it switched off within minutes, or something else was going on.', ['switched', 'off'])]

# ---------- 16. Sagittarius ----------
rng16 = np.random.default_rng(16)
STF = np.c_[rng16.uniform(0, W, 900), rng16.uniform(110, 830, 900), rng16.uniform(0.6, 2.8, 900)]

def c16(t):
    img, d = new()
    for x, y, r in STF:
        b = int(110 + 50 * r)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(b + 25, 255)))
    for i, (x, lab) in enumerate(((840, 'RA 19h25m'), (1080, 'RA 19h28m'))):
        a = ramp(t, 1.5 + i * 0.6, 2.0 + i * 0.6)
        d.rectangle([x - 70, 300, x + 70, 620], outline=A(AMBER, a), width=5, fill=A(AMBER, 0.08 * a))
        d.text((x, 650), lab, font=F_SMALL, fill=A(WHITE, a), anchor='mt')
        text_c(d, (x, 460), '?', F_MED, A(AMBER, a))
    text_c(d, (W / 2, 190), 'SAGITTARIUS', F_MED, A(CYAN, ramp(t, 3.5, 4.0)))
    top_label(img, 'TWO POSSIBLE POSITIONS')
    return img

CAP16 = [(0, 3, 'And because no one knows which horn caught it…', ['which', 'horn']),
         (3, 7, '…the signal has two possible positions, both in the constellation Sagittarius.', ['two', 'possible', 'Sagittarius.'])]

# ---------- 17. listening again ----------
EVENTS = [(1977, 'Big Ear: close to 2 months', 'same strip of sky'),
          (1983, 'Robert Gray', 'own dish, Chicago'),
          (1987, 'Harvard / Oak Ridge', 'Massachusetts'),
          (1995, 'Very Large Array', 'New Mexico'),
          (1998, 'Mount Pleasant dish', 'Tasmania')]

def c17(t):
    img, d = new()
    x0, x1, ty = 200, 1720, 460
    d.line([x0, ty, x1, ty], fill=GREY, width=4)
    for i, (yr, a_, b_) in enumerate(EVENTS):
        x = lerp(x0 + 60, x1 - 60, i / (len(EVENTS) - 1))
        a = ramp(t, 1.0 + i * 2.2, 1.4 + i * 2.2)
        if a <= 0:
            continue
        up = i % 2 == 0
        d.ellipse([x - 12, ty - 12, x + 12, ty + 12], fill=A(AMBER, a))
        y = ty - 70 if up else ty + 70
        d.text((x, y), str(yr), font=F_MED, fill=A(WHITE, a), anchor='ms' if up else 'mt')
        y2 = y - 80 if up else y + 80
        d.text((x, y2), a_, font=F_LABEL, fill=A(CYAN, a), anchor='ms' if up else 'mt')
        d.text((x, y2 + (-40 if up else 44)), b_, font=F_SMALL, fill=A(GREY, a), anchor='ms' if up else 'mt')
        ra = ramp(t, 1.6 + i * 2.2, 2.0 + i * 2.2)
        yx = ty + (34 if up else -34)
        d.line([x - 10, yx - 10, x + 10, yx + 10], fill=A(RED, ra), width=5)
        d.line([x - 10, yx + 10, x + 10, yx - 10], fill=A(RED, ra), width=5)
    a = ramp(t, 12.5, 13.0)
    if a > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(190 * a)))
        text_c(d, (W / 2, 450), 'NEVER HEARD AGAIN', F_HUGE, A(RED, a))
    top_label(img, 'CHAPTER 6 · LISTENING AGAIN')
    return img

CAP17 = [(0, 4, 'The Big Ear team watched that strip of sky for close to two months. Nothing.', ['two', 'months.', 'Nothing.']),
         (4, 6.5, 'Over the years, they went back more than fifty times.', ['fifty']),
         (6.5, 8.5, 'An amateur astronomer, Robert Gray, spent decades on the hunt.', ['Robert', 'Gray,', 'decades']),
         (8.5, 12.5, 'His own dish in Chicago, a Harvard telescope, the Very Large Array in New Mexico, a dish in Tasmania.', ['Chicago,', 'Harvard', 'Very', 'Large', 'Array', 'Tasmania.']),
         (12.5, 15, 'No one ever heard it again.', ['No', 'one'])]

# ---------- 18. Big Ear torn down ----------
def c18(t):
    img, d = new()
    sky(d, (10, 18, 36), (40, 60, 90), VB - 80)
    k = ease(ramp(t, 1.0, 4.0))
    d.rectangle([0, VB - 80, W, H], fill=(int(lerp(18, 34, k)), int(lerp(26, 92, k)), int(lerp(20, 44, k))))
    if k < 1:
        big_ear(d, 260, 1660, VB - 80 + 220 * k, a=1 - k, s=2.0)
    fa = ramp(t, 4.0, 4.5)
    if fa > 0:
        fx, fy = 1300, VB - 80
        d.ellipse([fx - 40, fy - 8, fx + 40, fy + 8], fill=A((10, 20, 12), fa))
        d.line([fx, fy, fx, fy - 300], fill=A((230, 230, 230), fa), width=6)
        d.polygon([(fx, fy - 300), (fx + 130, fy - 262), (fx, fy - 224)], fill=A(RED, fa))
    for i in range(6):
        ha = ramp(t, 5.0 + i * 0.25, 5.4 + i * 0.25)
        if ha <= 0:
            continue
        hx, hy = 200 + i * 130, VB - 80
        d.rectangle([hx, hy - 70, hx + 100, hy], fill=A((70, 80, 100), ha))
        d.polygon([(hx - 10, hy - 70), (hx + 50, hy - 115), (hx + 110, hy - 70)], fill=A((110, 70, 60), ha))
        d.rectangle([hx + 38, hy - 40, hx + 62, hy], fill=A((40, 45, 55), ha))
    ab = 1 - ramp(t, 1.0, 1.4)
    text_c(d, (W / 2, 320), '1998', F_BIG, A(WHITE, ab * 0.92))
    top_label(img, 'THE END OF BIG EAR')
    return img

CAP18 = [(0, 3, 'In 1998, Big Ear itself was torn down.', ['1998,', 'torn', 'down.']),
         (3, 7.5, 'Developers bought the land to expand a golf course and build about four hundred houses.', ['golf', 'course', 'houses.'])]

# ---------- 19. comet idea ----------
def c19(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    arr = to_arr(img)
    e = ramp(t, 0.3, 7.0)
    cx, cy = lerp(1700, 300, e), lerp(250, 520, e)
    glow(arr, cx, cy, 160, (60, 110, 200), 0.5)
    for j in range(30):
        glow(arr, cx + j * 14, cy - j * 5, 22 - j * 0.5, (180, 220, 255), 0.35 * (1 - j / 30))
    glow(arr, cx, cy, 14, (240, 250, 255), 1.6)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 1.0, 1.4) * (1 - ramp(t, 6.5, 7.0))
    d.text((cx, cy + 190), 'comet + hydrogen cloud?', font=F_LABEL, fill=A(GREY, a), anchor='mt')
    a2 = ramp(t, 7.5, 8.0)
    if a2 > 0:
        card(d, 360, 300, 1560, 520, a2)
        text_c(d, (W / 2, 370), 'REJECTED BY THE BIG EAR TEAM', F_MED, A(RED, a2))
        text_c(d, (W / 2, 460), 'it should have shown up in both horns', F_LABEL, A(WHITE, a2))
    top_label(img, 'CHAPTER 7 · WHAT WAS IT?')
    return img

CAP19 = [(0, 7, 'So what was it? In 2016, one astronomer suggested a passing comet, wrapped in a cloud of hydrogen.', ['comet,', 'hydrogen.']),
         (7, 12, 'But the Big Ear team rejected it. A real source in the sky, they said, should have shown up in both horns.', ['rejected', 'both', 'horns.'])]

# ---------- 20. magnetar + cloud ----------
def c20(t):
    img, d = new()
    draw_stars(d, t, 0.6)
    arr = to_arr(img)
    mx, my = 330, 300
    glow(arr, mx, my, 30, (200, 220, 255), 1.6)
    cx, cy = 1350, 500
    rng = np.random.default_rng(20)
    flash = math.exp(-(t - 10.0) * 0.8) if t >= 10.0 else 0.0
    for _ in range(16):
        ox, oy, r = rng.uniform(-260, 260), rng.uniform(-140, 140), rng.uniform(90, 160)
        glow(arr, cx + ox, cy + oy, r, (60, 90, 160), 0.22 + 0.8 * flash)
    if 8.0 <= t < 10.1:
        e = ramp(t, 8.0, 10.0)
        for j in range(20):
            q = max(e - j * 0.02, 0)
            glow(arr, lerp(mx, cx, q), lerp(my, cy, q), 16 - j * 0.5, (255, 150, 60), 0.6 * (1 - j / 20))
    if flash > 0:
        glow(arr, cx, cy, 120, (110, 210, 255), 1.6 * flash)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    a = ramp(t, 6.0, 6.5)
    d.text((mx, my + 60), 'MAGNETAR (a dead star)', font=F_SMALL, fill=A(GREY, a), anchor='mt')
    d.text((cx, cy + 240), 'COLD HYDROGEN CLOUD', font=F_SMALL, fill=A(GREY, ramp(t, 1.0, 1.4)), anchor='mt')
    top_label(img, 'A NEW IDEA · 2024')
    return img

CAP20 = [(0, 2.5, 'In 2024, a team led by Abel Méndez, at the University of Puerto Rico at Arecibo…', ['2024,', 'Abel', 'Méndez,']),
         (2.5, 6, '…found faint, similar signals in old Arecibo data, coming from cold clouds of hydrogen.', ['cold', 'hydrogen.']),
         (6, 9, 'Their idea: a sudden burst of energy, perhaps a flare from a magnetar, a dead star…', ['flare', 'magnetar,']),
         (9, 12, '…hit one of these clouds and made it flash like a laser.', ['flash', 'laser.'])]

# ---------- 21. 2025 reanalysis ----------
def c21(t):
    img, d = new()
    for i in range(18):
        k = ramp(t, 0.2 + i * 0.08, 0.5 + i * 0.08)
        if k <= 0:
            continue
        y = 760 - i * 22
        d.rectangle([220 + (i % 3) * 6, y - 120, 620 + (i % 3) * 6, y], fill=(int(220 * k), int(216 * k), int(204 * k)), outline=(120, 120, 120))
    text_c(d, (420, 210), '75,000+ PAGES', F_LABEL, A(AMBER, ramp(t, 1.5, 2.0)))
    rows = [('FREQUENCY', '1420.4556 MHz', '1420.726 MHz', 5.0),
            ('BRIGHTNESS', '54–212 Jy', '250+ Jy', 6.5),
            ('POSITION', 'wide area', 'narrower area', 8.0)]
    for i, (lab, old, new_, t0) in enumerate(rows):
        a = ramp(t, t0, t0 + 0.4)
        y = 300 + i * 150
        d.text((820, y), lab, font=F_SMALL, fill=A(GREY, a), anchor='ls')
        d.text((820, y + 60), old, font=F_LABEL, fill=A(GREY, a), anchor='ls')
        d.text((1200, y + 60), '→', font=F_LABEL, fill=A(WHITE, a), anchor='ms')
        d.text((1260, y + 60), new_, font=F_MED, fill=A(AMBER, a), anchor='ls')
    top_label(img, 'ARECIBO WOW! II · 2025 REANALYSIS')
    return img

CAP21 = [(0, 4.5, 'In 2025, they went back to the original Big Ear data, more than seventy-five thousand pages of it.', ['2025,', 'seventy-five', 'thousand']),
         (4.5, 7, 'The signal turned out to be even stronger than thought…', ['stronger']),
         (7, 9.5, '…at a slightly higher frequency, from a smaller patch of sky.', ['higher', 'smaller']),
         (9.5, 13, 'They say it most likely came from nature, not from interference here on Earth.', ['nature,'])]

# ---------- 22. ending ----------
GC, GR = (960, 460), 300

def ortho(lon, lat, lon0, lat0):
    lo, la = np.radians(lon), np.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    x = np.cos(la) * np.sin(lo - l0)
    y = math.cos(p0) * np.sin(la) - math.sin(p0) * np.cos(la) * np.cos(lo - l0)
    z = math.sin(p0) * np.sin(la) + math.cos(p0) * np.cos(la) * np.cos(lo - l0)
    n = np.hypot(x, y) + 1e-9
    x = np.where(z < 0, x / n, x); y = np.where(z < 0, y / n, y)
    return GC[0] + x * GR, GC[1] - y * GR, z

def c22(t):
    img, d = new()
    draw_stars(d, t, 0.7)
    arr = to_arr(img)
    glow(arr, GC[0], GC[1], GR * 1.05, (60, 120, 220), 0.45)
    img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([GC[0] - GR, GC[1] - GR, GC[0] + GR, GC[1] + GR], fill=(14, 40, 78))
    lon0 = -100 + t * 6
    for p in GEO['l']['land']:
        x, y, z = ortho(p[:, 0], p[:, 1], lon0, 30)
        if (z > 0).any() and len(p) > 2:
            d.polygon(list(zip(x.tolist(), y.tolist())), fill=(46, 84, 62))
    a = ramp(t, 0.5, 1.0) * (1 - ramp(t, 4.5, 5.0))
    card(d, 560, 110, 1360, 250, a)
    parts = [('ALIENS', F_MED, WHITE), (' or ', F_LABEL, GREY), ('NATURE?', F_MED, AMBER)]
    tw = sum(d.textlength(p_, font=f_) for p_, f_, _ in parts)
    x = W / 2 - tw / 2
    for p_, f_, c_ in parts:
        d.text((x, 180), p_, font=f_, fill=A(c_, a), anchor='lm')
        x += d.textlength(p_, font=f_)
    a2 = ramp(t, 5.0, 5.5) * (1 - ramp(t, 9.5, 10.0))
    if a2 > 0:
        card(d, 260, 330, 1660, 590, a2)
        text_c(d, (W / 2, 420), '“It’s still an open question', F_MED, A(WHITE, a2))
        text_c(d, (W / 2, 500), 'what the source of the signal was.”', F_MED, A(WHITE, a2))
        text_c(d, (W / 2, 560), 'Jerry Ehman', F_LABEL, A(AMBER, a2))
    a3 = ramp(t, 15.5, 16.0)
    if a3 > 0:
        d.rectangle([0, 0, W, H], fill=(7, 11, 20, int(170 * a3)))
        text_c(d, (W / 2, 380), 'FOLLOW', F_HUGE, A(WHITE, a3))
        text_c(d, (W / 2, 500), 'for more unexplained history', F_MED, A(AMBER, a3))
    top_label(img, 'STILL A MYSTERY', 1 - a3)
    return img

CAP22 = [(0, 5, 'But the idea still has to be proven, and the debate goes on.', ['proven,', 'debate']),
         (5, 10, 'Jerry Ehman put it simply: it’s still an open question what the source of the signal was.', ['open', 'question']),
         (10, 15.5, 'Seventy-two seconds, one word in red ink, and a mystery that has outlived the telescope that heard it.', ['Seventy-two', 'red', 'ink,', 'mystery'])]

SCENES = [
    ('c01', c01, 15.0, CAP01), ('c02', c02, 5.5, CAP02), ('c03', c03, 9.5, CAP03), ('c04', c04, 15.5, CAP04),
    ('c05', c05, 8.5, CAP05), ('c06', c06, 9.5, CAP06), ('c07', c07, 13.0, CAP07), ('c08', c08, 13.0, CAP08),
    ('c09', c09, 13.5, CAP09), ('c10', c10, 7.0, CAP10), ('c11', c11, 6.5, CAP11), ('c12', c12, 10.0, CAP12),
    ('c13', c13, 8.0, CAP13), ('c14', c14, 15.5, CAP14), ('c15', c15, 14.0, CAP15), ('c16', c16, 7.0, CAP16),
    ('c17', c17, 15.0, CAP17), ('c18', c18, 7.5, CAP18), ('c19', c19, 12.0, CAP19), ('c20', c20, 12.5, CAP20),
    ('c21', c21, 13.0, CAP21), ('c22', c22, 18.0, CAP22),
]

SPOKEN = {
    'On a summer night in 1977, a radio telescope in Ohio heard something no one could explain.':
        'On a summer night in nineteen seventy-seven, a radio telescope in Ohio heard something no one could explain.',
    'In 1959, two physicists at Cornell University…': 'In nineteen fifty-nine, two physicists at Cornell University,',
    '…Giuseppe Cocconi and Philip Morrison, asked a simple question.': 'Giuseppe Cocconi and Philip Morrison, asked a simple question.',
    'Neutral hydrogen gives off radio waves at one exact frequency: about 1420 megahertz.':
        'Neutral hydrogen gives off radio waves at one exact frequency: about fourteen twenty megahertz.',
    'It was designed by radio astronomer John Kraus, and switched on in 1963.':
        'It was designed by radio astronomer John Kraus, and switched on in nineteen sixty-three.',
    'Then, in 1973, it turned to a new search: signals from alien civilizations.':
        'Then, in nineteen seventy-three, it turned to a new search: signals from alien civilizations.',
    'On the night of August 15th, 1977, at about 11:16 p.m., something drifted through the beam.':
        'On the night of August fifteenth, nineteen seventy-seven, at about eleven sixteen p.m., something drifted through the beam.',
    'In channel two, the computer printed six characters: six, E, Q, U, J, five.':
        'In channel two, the computer printed six characters: six... E... Q... U... J... five.',
    'At its peak, the letter U, it was about thirty times stronger than the background noise.':
        'At its peak, the letter U, it was about thirty times stronger than the background noise.',
    'A few days later, astronomer Jerry Ehman was going through the printouts.':
        'A few days later, astronomer Jerry Eeman was going through the printouts.',
    'He highlighted the six characters, and wrote one word in the margin in red: Wow!':
        'He highlighted the six characters, and wrote one word in the margin, in red: Wow!',
    'In 1998, Big Ear itself was torn down.': 'In nineteen ninety-eight, Big Ear itself was torn down.',
    'So what was it? In 2016, one astronomer suggested a passing comet, wrapped in a cloud of hydrogen.':
        'So what was it? In twenty sixteen, one astronomer suggested a passing comet, wrapped in a cloud of hydrogen.',
    'In 2024, a team led by Abel Méndez, at the University of Puerto Rico at Arecibo…':
        'In twenty twenty-four, a team led by Abel Mendez, at the University of Puerto Rico at Arecibo,',
    '…found faint, similar signals in old Arecibo data, coming from cold clouds of hydrogen.':
        'found faint, similar signals in old Arecibo data, coming from cold clouds of hydrogen.',
    'Their idea: a sudden burst of energy, perhaps a flare from a magnetar, a dead star…':
        'Their idea: a sudden burst of energy, perhaps a flare from a magnetar, a dead star,',
    '…hit one of these clouds and made it flash like a laser.': 'hit one of these clouds, and made it flash like a laser.',
    'In 2025, they went back to the original Big Ear data, more than seventy-five thousand pages of it.':
        'In twenty twenty-five, they went back to the original Big Ear data, more than seventy-five thousand pages of it.',
    'Jerry Ehman put it simply: it’s still an open question what the source of the signal was.':
        "Jerry Eeman put it simply: it's still an open question what the source of the signal was.",
}


def SFX(tr, G):
    tr.wind([(0, 0.9), (G('c02', 0), 0.6), (G('c05', 0), 0.5), (G('c10', 0), 0.8), (G('c11', 0), 0.4),
             (G('c16', 0), 0.6), (G('c18', 0), 0.8), (G('c19', 0), 0.6), (G('c22', 0), 0.7),
             (G('c22', 17.0), 0.7), (G('c22', 18.0), 0.0)])
    tr.whoosh(G('c01', 4.0), G('c01', 7.0), 0.2, 600, 3000)
    tr.rumble(G('c01', 7.0), G('c01', 11.0), 0.18)
    tr.whoosh(G('c03', 0.2), G('c03', 1.0), 0.12, 400, 2000)
    tr.whoosh(G('c05', 0.0), G('c05', 4.0), 0.1, 300, 1200)
    tr.rumble(G('c08', 2.0), G('c08', 12.0), 0.1)
    tr.rumble(G('c12', 0.3), G('c12', 5.0), 0.12)
    tr.rumble(G('c18', 1.0), G('c18', 4.0), 0.3)
    tr.snaps(G('c18', 1.0), G('c18', 3.8), 50, 0.2)
    tr.whoosh(G('c19', 0.3), G('c19', 7.0), 0.1, 400, 1500)
    tr.whoosh(G('c20', 8.0), G('c20', 10.0), 0.22)
    tr.boom(G('c20', 10.0), 0.5, 3.0)

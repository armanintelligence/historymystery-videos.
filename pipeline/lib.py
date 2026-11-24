import numpy as np, pickle, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
VIS_CY = 690  # centre of the visual area

FD = os.path.join(HERE, 'fonts') + '/'
def font(name, size):
    return ImageFont.truetype(FD + name, size)

F_CAP = font('Inter-Bold.otf', 58)
F_LABEL = font('Inter-SemiBold.otf', 34)
F_SMALL = font('Inter-SemiBold.otf', 30)
F_MED = font('InterDisplay-Bold.otf', 64)
F_BIG = font('InterDisplay-Black.otf', 250)
F_HUGE = font('InterDisplay-Black.otf', 120)

BG = (7, 11, 20)
LAND = (30, 39, 54)
COAST = (70, 88, 116)
WATER = (10, 18, 32)
AMBER = (255, 150, 60)
CYAN = (110, 210, 255)
WHITE = (245, 245, 245)
GREY = (150, 160, 175)

_orig_text = ImageDraw.ImageDraw.text
def _text(self, xy, text, fill=None, *a, **k):
    if isinstance(fill, tuple) and len(fill) == 4 and fill[3] <= 2:
        return
    return _orig_text(self, xy, text, fill, *a, **k)
ImageDraw.ImageDraw.text = _text

GEO = pickle.load(open(os.path.join(HERE, 'geo.pkl'), 'rb'))

SITE = (101.9, 60.9)
VANAVARA = (102.28, 60.34)
KANSK = (95.7, 56.2)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    if b == a:
        return 1.0 if t >= a else 0.0
    return min(max((t - a) / (b - a), 0.0), 1.0)


def lerp(a, b, k):
    return a + (b - a) * k


class Cam:
    def __init__(self, lon0, lat0, s, cy=VIS_CY):
        self.lon0, self.lat0, self.s, self.cy = lon0, lat0, s, cy
        self.c = math.cos(math.radians(lat0))

    def xy(self, lon, lat):
        return (W / 2 + (np.asarray(lon) - self.lon0) * self.s * self.c,
                self.cy - (np.asarray(lat) - self.lat0) * self.s)


def draw_map(img, cam, rivers=False, land=LAND, coast=COAST, water=WATER):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=water)
    res = 'i' if cam.s >= 35 else 'l'
    lonspan = W / (cam.s * cam.c) / 2 + 2
    latspan = H / cam.s / 2 + 2
    for key, fill in (('land', land), ('lakes', water)):
        for p in GEO[res][key]:
            lo, la = p[:, 0], p[:, 1]
            if lo.max() < cam.lon0 - lonspan or lo.min() > cam.lon0 + lonspan:
                continue
            if la.max() < cam.lat0 - latspan or la.min() > cam.lat0 + latspan:
                continue
            x, y = cam.xy(lo, la)
            pts = list(zip(x.tolist(), y.tolist()))
            if len(pts) > 2:
                d.polygon(pts, fill=fill, outline=coast if key == 'land' else None)
    if rivers and cam.s >= 30:
        wdt = 2 if cam.s < 80 else 3
        for seg in GEO['rivers']:
            x, y = cam.xy(seg[:, 0], seg[:, 1])
            d.line(list(zip(x.tolist(), y.tolist())), fill=(40, 95, 140), width=wdt)
    return img


def glow(arr, x, y, r, color, k=1.0):
    """Additive gaussian glow on a float32 HxWx3 array (0..255)."""
    R = int(r * 3) + 2
    x0, x1 = max(int(x) - R, 0), min(int(x) + R, W)
    y0, y1 = max(int(y) - R, 0), min(int(y) + R, H)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (r * r))).astype(np.float32) * k
    arr[y0:y1, x0:x1] += g[..., None] * np.array(color, np.float32)[None, None, :]


def to_arr(img):
    return np.asarray(img, dtype=np.float32).copy()


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def text_c(d, xy, s, f, fill, anchor='mm'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def top_label(img, s, a=1.0):
    if a <= 0:
        return
    d = ImageDraw.Draw(img, 'RGBA')
    tw = d.textlength(s, font=F_LABEL)
    x = W / 2 - (tw + 34) / 2
    d.ellipse([x, 178 - 9, x + 18, 178 + 9], fill=AMBER + (int(255 * a),))
    d.text((x + 34, 178), s, font=F_LABEL, fill=WHITE + (int(255 * a),), anchor='lm')


def caption(img, text, hl=(), a=1.0, cy=1360):
    """Burnt-in caption box. Words in hl are amber."""
    if a <= 0 or not text:
        return
    d = ImageDraw.Draw(img, 'RGBA')
    words = text.split()
    maxw = 860
    lines, cur = [], []
    for w_ in words:
        test = ' '.join(cur + [w_])
        if d.textlength(test, font=F_CAP) > maxw and cur:
            lines.append(cur); cur = [w_]
        else:
            cur.append(w_)
    if cur:
        lines.append(cur)
    lh = 74
    bh = lh * len(lines) + 44
    bw = max(d.textlength(' '.join(l), font=F_CAP) for l in lines) + 70
    cx = 520
    y0 = cy - bh / 2
    d.rounded_rectangle([cx - bw / 2, y0, cx + bw / 2, y0 + bh], radius=26,
                        fill=(0, 0, 0, int(165 * a)))
    hls = {h.lower().strip('.,…?') for h in hl}
    for i, l in enumerate(lines):
        lw = d.textlength(' '.join(l), font=F_CAP)
        x = cx - lw / 2
        y = y0 + 22 + lh * i + lh / 2
        for w_ in l:
            col = AMBER if w_.lower().strip('.,…?') in hls else WHITE
            d.text((x, y), w_, font=F_CAP, fill=col + (int(255 * a),), anchor='lm')
            x += d.textlength(w_ + ' ', font=F_CAP)


def caps_at(t, caps):
    """caps: list of (start, end, text, hl). Returns (text, hl, alpha)."""
    for (a, b, s, hl) in caps:
        if a <= t < b:
            al = min(ramp(t, a, a + 0.15), 1 - ramp(t, b - 0.12, b))
            return s, hl, max(al, 0.0)
    return None, (), 0


def stars(n=260, seed=3):
    rng = np.random.default_rng(seed)
    return np.c_[rng.uniform(0, W, n), rng.uniform(0, 1100, n), rng.uniform(0.6, 2.4, n), rng.uniform(0, 6.28, n)]

STARS = stars()


def draw_stars(d, t, a=1.0, ymax=1100):
    for x, y, r, ph in STARS:
        if y > ymax:
            continue
        b = int((150 + 100 * math.sin(t * 2 + ph)) * a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(b + 20, 255)))


def conifer(d, x, base, h, fill, tilt=0.0):
    """Conifer silhouette (a plant, allowed). tilt in radians rotates around base."""
    w = h * 0.38
    pts = [(-w / 2, 0), (w / 2, 0), (0, -h)]
    c, s = math.cos(tilt), math.sin(tilt)
    pts = [(x + px * c - py * s, base + px * s + py * c) for px, py in pts]
    d.polygon(pts, fill=fill)

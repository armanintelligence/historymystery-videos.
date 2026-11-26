"""Thumbnail for the Carrington long video. Usage: HM_FORMAT=long python3 thumbnail.py out.jpg"""
import os, sys, math, importlib.util
os.environ['HM_FORMAT'] = 'long'
EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(EP, "..", "..", "pipeline"))
from lib import *
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('ep', os.path.join(EP, "scenes.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')
m.sky(d, ymax=H)
draw_stars(d, 2.0, 0.6, ymax=H)
arr = to_arr(img)
m.aurora(arr, 3.0, base=520, height=420, k=1.5, ymax=H, red=1.6)
# the Sun with a white flare, top right
glow(arr, 1580, 300, 300, (255, 150, 60), 0.9)
img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
m.sun_disc(d, 1580, 300, 200)
arr = to_arr(img)
glow(arr, 1636, 268, 34, (255, 255, 255), 2.6)
glow(arr, 1670, 286, 30, (255, 255, 255), 2.2)
img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
# ground, telegraph poles and wires
gy = 1040
d.rectangle([0, gy, W, H], fill=(5, 7, 10))
poles = [(980, 330), (1400, 300), (1820, 275), (2240, 255)]
tops = []
for x, h in poles:
    m.pole(d, x, gy, h)
    tops.append((x, gy - h + 24))
for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
    for dx in (-36, 36):
        d.line([(lerp(x0 + dx, x1 + dx, i / 30), lerp(y0, y1, i / 30) + 34 * math.sin(math.pi * i / 30)) for i in range(31)], fill=(40, 46, 60), width=4)
arr = to_arr(img)
for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
    for u in (0.3, 0.62):
        x, y = lerp(x0, x1, u), lerp(y0, y1, u) + 34 * math.sin(math.pi * u)
        glow(arr, x, y, 40, (170, 210, 255), 1.6)
        glow(arr, x, y, 10, (255, 255, 255), 2.6)
img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
FB = font('InterDisplay-Black.otf', 150)
d.text((80, 260), 'THE SUN SET', font=FB, fill=WHITE, anchor='ls')
d.text((80, 430), 'TELEGRAPHS', font=FB, fill=AMBER, anchor='ls')
d.text((80, 600), 'ON FIRE', font=FB, fill=(255, 90, 70), anchor='ls')
d.rounded_rectangle([80, 700, 760, 820], radius=20, fill=(0, 0, 0, 170))
d.text((110, 760), 'CARRINGTON EVENT · 1859', font=font('Inter-Bold.otf', 50), fill=CYAN, anchor='lm')
img.resize((1280, 720), Image.LANCZOS).save(sys.argv[1], quality=90)

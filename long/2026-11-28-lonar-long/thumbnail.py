import os, sys, importlib.util
os.environ['HM_FORMAT'] = 'long'
sys.path.insert(0, '/home/claude/historymystery-videos./pipeline')
from lib import *
from PIL import Image, ImageDraw
ep = '/home/claude/historymystery-videos./long/2026-11-28-lonar-long'
sys.path.insert(0, ep)
spec = importlib.util.spec_from_file_location('ep', ep + '/scenes.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
# crater from above, pink lake (as in June 2020), on the right
img = Image.new('RGB', (W, H), BG)
m.crater_top(img, 1400, 560, 400, m.PINK_L, 1.0, 0.8)
d = ImageDraw.Draw(img, 'RGBA')
# darken the left half for the text
for x in range(0, 1100, 4):
    a = int(235 * max(0, 1 - x / 1100) ** 0.7)
    d.rectangle([x, 0, x + 4, H], fill=(7, 11, 20, a))
F = font('InterDisplay-Black.otf', 130)
d.text((80, 330), 'A ROCK FROM', font=F, fill=WHITE, anchor='ls')
d.text((80, 490), 'SPACE MADE', font=F, fill=WHITE, anchor='ls')
d.text((80, 650), 'THIS CRATER', font=F, fill=AMBER, anchor='ls')
d.rounded_rectangle([80, 760, 860, 880], radius=20, fill=(0, 0, 0, 180))
d.text((110, 820), 'LONAR CRATER · INDIA', font=font('Inter-Bold.otf', 56), fill=CYAN, anchor='lm')
img.resize((1280, 720), Image.LANCZOS).save(sys.argv[1], quality=90)

import os, sys, importlib.util
os.environ['HM_FORMAT'] = 'long'
sys.path.insert(0, '/home/claude/historymystery-videos./pipeline')
from lib import *
from PIL import Image, ImageDraw
ep = '/home/claude/historymystery-videos./long/2026-11-29-antikythera-long'
spec = importlib.util.spec_from_file_location('ep', ep + '/scenes.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img = m.seabed(2.0)
d = ImageDraw.Draw(img, 'RGBA')
d.rectangle([0, 828, W, H], fill=(58, 60, 54))
d.rectangle([0, 0, W, H], fill=(7, 11, 20, 90))
# corroded lump on the right with an X-ray window showing glowing gears
cx, cy = 1450, 560
m.lump(d, cx, cy, 300, seed=3)
d.ellipse([cx - 260, cy - 215, cx + 260, cy + 215], fill=(10, 22, 34, 245))
m.gear(d, cx - 60, cy - 10, 170, 48, 0.2, outline=AMBER, width=6, hub=(10, 22, 34))
m.gear(d, cx + 150, cy + 110, 80, 22, 0.5, outline=CYAN, width=5, hub=(10, 22, 34), spokes=0)
m.gear(d, cx + 140, cy - 130, 60, 16, 0.1, outline=CYAN, width=5, hub=(10, 22, 34), spokes=0)
arr = to_arr(img)
glow(arr, cx - 60, cy - 10, 200, (255, 150, 60), 0.25)
img = to_img(arr); d = ImageDraw.Draw(img, 'RGBA')
F = font('InterDisplay-Black.otf', 150)
d.text((90, 300), '2,000-YEAR-OLD', font=F, fill=WHITE, anchor='ls')
d.text((90, 480), 'COMPUTER', font=F, fill=AMBER, anchor='ls')
d.text((90, 640), 'FROM THE SEA', font=font('InterDisplay-Black.otf', 110), fill=CYAN, anchor='ls')
d.rounded_rectangle([90, 760, 900, 880], radius=20, fill=(0, 0, 0, 180))
d.text((120, 820), 'THE ANTIKYTHERA MECHANISM', font=font('Inter-Bold.otf', 52), fill=WHITE, anchor='lm')
img.resize((1280, 720), Image.LANCZOS).save(sys.argv[1], quality=90)

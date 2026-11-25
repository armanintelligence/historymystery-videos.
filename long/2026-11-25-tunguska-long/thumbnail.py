"""Thumbnail for the Tunguska long video. Usage: python3 thumbnail.py out.jpg"""
import os, sys, importlib.util
os.environ['HM_FORMAT'] = 'long'
EPDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(EPDIR, '..', '..', 'pipeline'))
from lib import *
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('ep', os.path.join(EPDIR, 'scenes.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img, d = m.new()
m.sky(d, ymax=m.VB)
draw_stars(d, 1.0, ymax=m.VB)
m.treeline(d, m.VB - 60)
arr = to_arr(img)
m.fireball(arr, (1900, 60), (1450, 330), 1.0, 30, 34)
glow(arr, 1450, 330, 140, (255, 150, 60), 0.6)
img = to_img(arr)
d = ImageDraw.Draw(img, 'RGBA')
F = font('InterDisplay-Black.otf', 150)
d.text((90, 300), 'IT EXPLODED', font=F, fill=WHITE, anchor='ls')
d.text((90, 470), 'OVER SIBERIA.', font=F, fill=AMBER, anchor='ls')
d.text((90, 640), 'NO CRATER.', font=F, fill=(255, 90, 70), anchor='ls')
d.rounded_rectangle([90, 760, 900, 880], radius=20, fill=(0, 0, 0, 170))
d.text((120, 820), 'THE TUNGUSKA EVENT · 1908', font=font('Inter-Bold.otf', 56), fill=CYAN, anchor='lm')
img.resize((1280, 720), Image.LANCZOS).save(sys.argv[1], quality=90)

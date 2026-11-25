import os, sys, importlib.util
os.environ['HM_FORMAT']='long'
sys.path.insert(0,'/home/claude/historymystery-videos./pipeline')
from lib import *
from PIL import Image, ImageDraw
ep='/home/claude/historymystery-videos./long/2026-11-29-wow-signal-long'
spec=importlib.util.spec_from_file_location('ep', ep+'/scenes.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
draw_stars(d,1.0,0.8)
# printout on the right, shifted
pr=Image.new('RGB',(W,H),BG); pd=ImageDraw.Draw(pr,'RGBA'); m.printout(pd,0,6,1.0,0.0)
crop=pr.crop((560,110,1360,830)).resize((720,648))
img.paste(crop,(1120,330))
d=ImageDraw.Draw(img,'RGBA')
# circled column emphasis already drawn; big text left
d.text((90,300),'72 SECONDS', font=font('InterDisplay-Black.otf',132), fill=WHITE, anchor='ls')
d.text((90,470),'FROM SPACE.', font=font('InterDisplay-Black.otf',132), fill=AMBER, anchor='ls')
d.text((90,640),'NEVER AGAIN.', font=font('InterDisplay-Black.otf',132), fill=(255,90,70), anchor='ls')
d.text((1480,215),'Wow!', font=font('InterDisplay-Black.otf',170), fill=(225,35,35), anchor='mm')
d.rounded_rectangle([90,760,800,880],radius=20,fill=(0,0,0,170))
d.text((120,820),'THE WOW! SIGNAL · 1977', font=font('Inter-Bold.otf',56), fill=CYAN, anchor='lm')
img.resize((1280,720), Image.LANCZOS).save(sys.argv[1], quality=90)

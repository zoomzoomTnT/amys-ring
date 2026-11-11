# python3 closeup.py [out] [prefix] -> reference vs model at the SAME registered scale (uses overlay_report.json fit)
import sys, json, glob
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else 'compare_front_closeup.png'
PRE = sys.argv[2] if len(sys.argv) > 2 else 'render_'
rep = json.load(open('overlay_report.json'))['front']
ref = Image.open('reference_original.jpg').convert('RGB').crop(tuple(rep['quad']))
N = Image.open(PRE + 'front.png').convert('RGB'); s, ox, oy = rep['fit_s'], rep['fit_ox'], rep['fit_oy']
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
boxes = [('Left side of band', (240, 240, 420, 640), 2.4), ('Top of band under the centre stone', (300, 120, 700, 300), 1.25)]
rows = []
for title, (x0, y0, x1, y1), z in boxes:
    r = ref.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.LANCZOS)
    m = N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s))).resize(r.size, Image.LANCZOS)
    rows.append((title, r, m))
Wd = max(2 * r.width + 20 for _, r, _ in rows); Hd = sum(r.height + 60 for _, r, _ in rows)
sh = Image.new('RGB', (Wd, Hd), (38, 38, 38)); d = ImageDraw.Draw(sh); y = 0
for title, r, m in rows:
    d.text((6, y + 4), title, fill=(255, 220, 120), font=font); d.text((6, y + 30), 'Reference', fill='white', font=font); d.text((r.width + 26, y + 30), 'New model (same scale)', fill='white', font=font)
    sh.paste(r, (0, y + 56)); sh.paste(m, (r.width + 20, y + 56)); y += r.height + 60
sh.save(OUT); print(OUT, sh.size)

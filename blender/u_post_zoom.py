# python3 u_post_zoom.py [out] [render_front] [notes a|b|c] -> zoom on the side-gallery points (teeth), reference vs model
# at the same registered scale, plus one tooth each on a 0.25 mm grid with measured numbers
import sys, json
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else 'u_post_zoom.png'
RF = sys.argv[2] if len(sys.argv) > 2 else 'render_front.png'
NOTES = sys.argv[3].split('|') if len(sys.argv) > 3 else []
rep = json.load(open('overlay_report.json'))['front']
ref = Image.open('reference_original.jpg').convert('RGB').crop(tuple(rep['quad']))
N = Image.open(RF).convert('RGB'); s, ox, oy = rep['fit_s'], rep['fit_ox'], rep['fit_oy']
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
def mcrop(x0, y0, x1, y1):
    return N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s)))
x0, y0, x1, y1 = 215, 300, 345, 580; z = 3
r = ref.crop((x0, y0, x1, y1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.LANCZOS)
m = mcrop(x0, y0, x1, y1).resize(r.size, Image.LANCZOS)
step = 0.25 / rep['mm_per_px']; zz = r.width / 80
def grid(c, cx, cy, model):
    b = (cx - 20, cy - 35, cx + 60, cy + 35)
    c = (mcrop(*b) if model else c.crop(b)).resize((round(80 * zz), round(70 * zz)), Image.LANCZOS); d = ImageDraw.Draw(c); k = 0
    while k * step < 80: d.line([(k * step * zz, 0), (k * step * zz, c.height)], fill=(255, 0, 0) if k % 4 == 0 else (0, 150, 255)); k += 1
    k = 0
    while k * step < 70: d.line([(0, k * step * zz), (c.width, k * step * zz)], fill=(255, 0, 0) if k % 4 == 0 else (0, 150, 255)); k += 1
    return c
gr, gm = grid(ref, 247, 443, 0), grid(N, 248, 404, 1)
W = 2 * r.width + 20; H = 40 + r.height + 34 + gr.height + 10 + 20 * len(NOTES) + 10
sh = Image.new('RGB', (W, H), (38, 38, 38)); d = ImageDraw.Draw(sh)
d.text((6, 8), 'Reference', fill='white', font=font); d.text((r.width + 26, 8), 'Model (same scale)', fill='white', font=font)
sh.paste(r, (0, 40)); sh.paste(m, (r.width + 20, 40)); y = 40 + r.height + 6
d.text((6, y), 'One tooth each, grid = 0.25 mm (red = 1 mm)', fill=(255, 210, 120), font=small); y += 28
sh.paste(gr, (0, y)); sh.paste(gm, (r.width + 20, y)); y += gr.height + 10
for n in NOTES: d.text((6, y), n, fill='white', font=small); y += 20
sh.save(OUT); print(OUT, sh.size)

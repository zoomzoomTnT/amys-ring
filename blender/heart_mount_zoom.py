# python3 heart_mount_zoom.py [out] [render_prefix] -> heart-mount crops, reference vs model at the same registered scale
import sys, json
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else 'heart_mount_zoom.png'
PRE = sys.argv[2] if len(sys.argv) > 2 else 'render_'
NOTES = sys.argv[3].split('|') if len(sys.argv) > 3 else []
rep = json.load(open('overlay_report.json'))
REF = Image.open('reference_original.jpg').convert('RGB')
BOX = [('front', (236, 85, 426, 285), 'Front view - left heart (edge-on)'),
       ('side', (110, 70, 310, 250), 'Side view - heart and its V claw'),
       ('top', (220, 215, 410, 385), 'Top view - left heart'),
       ('three_quarter', (40, 120, 240, 430), '3/4 view - near heart')]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
rows = []
for v, (x0, y0, x1, y1), title in BOX:
    R = rep[v]; ref = REF.crop(tuple(R['quad'])); N = Image.open(PRE + v + '.png').convert('RGB')
    s, ox, oy = R['fit_s'], R['fit_ox'], R['fit_oy']; z = 440 / (x1 - x0)
    r = ref.crop((x0, y0, x1, y1)).resize((440, round((y1 - y0) * z)), Image.LANCZOS)
    m = N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s))).resize(r.size, Image.LANCZOS)
    rows.append((title, r, m, R['mm_per_px'] / z))
W = 2 * 440 + 20; H = sum(r.height + 34 for _, r, _, _ in rows) + 40 + 20 * len(NOTES) + 10
sh = Image.new('RGB', (W, H), (38, 38, 38)); d = ImageDraw.Draw(sh)
d.text((6, 8), 'Reference', fill='white', font=font); d.text((466, 8), 'Model (same scale)', fill='white', font=font)
y = 40
for title, r, m, mmpp in rows:
    d.text((6, y + 6), '%s   (1 mm = %d px)' % (title, round(1 / mmpp)), fill=(255, 210, 120), font=small); y += 30
    sh.paste(r, (0, y)); sh.paste(m, (460, y)); y += r.height + 4
for n in NOTES: d.text((6, y), n, fill='white', font=small); y += 20
sh.save(OUT); print(OUT, sh.size)

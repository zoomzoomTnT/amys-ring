# python3 gear_check.py [out] -> whole-ring front view, reference vs model at the same registered scale (normal viewing size)
import sys, json
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else 'gear_check.png'
R = json.load(open('overlay_report.json'))['front']
ref = Image.open('reference_original.jpg').convert('RGB').crop(tuple(R['quad']))
N = Image.open('render_front.png').convert('RGB'); s, ox, oy = R['fit_s'], R['fit_ox'], R['fit_oy']
x0, y0, x1, y1 = 140, 0, 680, 649
r = ref.crop((x0, y0, x1, y1))
m = N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s))).resize(r.size, Image.LANCZOS)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
sh = Image.new('RGB', (2 * r.width + 20, r.height + 40), (38, 38, 38)); d = ImageDraw.Draw(sh)
d.text((6, 8), 'Reference (front)', fill='white', font=font); d.text((r.width + 26, 8), 'Model (same scale)', fill='white', font=font)
sh.paste(r, (0, 40)); sh.paste(m, (r.width + 20, 40)); sh.save(OUT); print(OUT, sh.size)

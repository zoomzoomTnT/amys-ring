# python3 u_post_zoom.py [out] [render_front] -> tight zoom on 3 U-posts, reference vs model at the same registered scale
import sys, json
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else 'u_post_zoom.png'
RF = sys.argv[2] if len(sys.argv) > 2 else 'render_front.png'
rep = json.load(open('overlay_report.json'))['front']
ref = Image.open('reference_original.jpg').convert('RGB').crop(tuple(rep['quad']))
N = Image.open(RF).convert('RGB'); s, ox, oy = rep['fit_s'], rep['fit_ox'], rep['fit_oy']
x0, y0, x1, y1 = 236, 285, 336, 470; z = 4.5
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
r = ref.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.LANCZOS)
m = N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s))).resize(r.size, Image.LANCZOS)
sh = Image.new('RGB', (2 * r.width + 20, r.height + 40), (38, 38, 38)); d = ImageDraw.Draw(sh)
d.text((6, 8), 'Reference', fill='white', font=font); d.text((r.width + 26, 8), 'Model (same scale)', fill='white', font=font)
sh.paste(r, (0, 40)); sh.paste(m, (r.width + 20, 40)); sh.save(OUT); print(OUT, sh.size)

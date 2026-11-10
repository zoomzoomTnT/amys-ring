# python3 compare_sheet.py [out.png] [render_prefix] -> reference vs new, per view
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob
OUT = sys.argv[1] if len(sys.argv) > 1 else 'compare_v1fix.png'
PRE = sys.argv[2] if len(sys.argv) > 2 else 'render_'
ref = Image.open('reference_original.jpg').convert('RGB'); W, H = ref.size
a = np.array(ref).astype(int)
red = (a[..., 0] > 170) & (a[..., 1] < 140) & (a[..., 2] < 140)
red = np.array(Image.fromarray((red * 255).astype('uint8')).filter(ImageFilter.MaxFilter(15))) > 0
a[red] = [128, 128, 128]
ref = Image.fromarray(a.astype('uint8'))
mx, my = int(W * 0.488), int(H * 0.452)
quads = {'top': (0, 0, mx, my), 'three_quarter': (mx, 0, W, my), 'front': (0, my, mx, H), 'side': (mx, my, W, H)}
def autocrop(im, pad=12, thr=28):
    b = np.array(im).astype(int); bg = np.median(np.concatenate([b[:4].reshape(-1, 3), b[-4:].reshape(-1, 3), b[:, :4].reshape(-1, 3), b[:, -4:].reshape(-1, 3)]), axis=0)
    m = np.abs(b - bg).sum(-1) > thr
    m = np.array(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MinFilter(3))) > 0
    ys, xs = np.where(m)
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))
fonts = glob.glob('/usr/share/fonts/**/*Sans*Bold*.ttf', recursive=True) + glob.glob('/usr/share/fonts/**/*.ttf', recursive=True)
font = ImageFont.truetype(fonts[0], 30) if fonts else ImageFont.load_default()
HH = 620; rows = []
names = {'top': 'Top', 'three_quarter': 'Three-quarter', 'front': 'Front', 'side': 'Side'}
for v in ['top', 'three_quarter', 'front', 'side']:
    r = autocrop(ref.crop(quads[v])); n = autocrop(Image.open(PRE + v + '.png').convert('RGB'))
    r = r.resize((round(r.width * HH / r.height), HH), Image.LANCZOS); n = n.resize((round(n.width * HH / n.height), HH), Image.LANCZOS)
    rows.append((v, r, n))
cw = max(max(r.width, n.width) for _, r, n in rows) + 40
sheet = Image.new('RGB', (2 * cw, len(rows) * (HH + 60) + 70), (128, 128, 128)); d = ImageDraw.Draw(sheet)
d.text((20, 18), 'Reference (original design)', fill=(255, 255, 255), font=font); d.text((cw + 20, 18), 'New Blender model', fill=(255, 255, 255), font=font)
y = 70
for v, r, n in rows:
    d.text((20, y), names[v], fill=(235, 235, 235), font=font)
    sheet.paste(r, ((cw - r.width) // 2, y + 45)); sheet.paste(n, (cw + (cw - n.width) // 2, y + 45))
    y += HH + 60
d.line([(cw, 60), (cw, sheet.height)], fill=(90, 90, 90), width=3)
sheet.save(OUT); print(OUT, sheet.size)

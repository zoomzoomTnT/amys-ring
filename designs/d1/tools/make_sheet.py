# python3 designs/d1/tools/make_sheet.py -> ring_views.png (2x2 contact sheet of the 1600px renders)
from PIL import Image, ImageDraw, ImageFont
import glob
import os as _os   # run from anywhere: works in designs/d1/build (renders, overlay_report.json); picture in reference/
_D = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))); _os.chdir(_os.path.join(_D, 'build'))
REF = _os.path.join(_D, 'reference', 'original.jpg')
views = [('top', 'Top'), ('three_quarter', 'Three-quarter'), ('front', 'Front'), ('side', 'Side')]
T = 1000; sheet = Image.new('RGB', (2 * T, 2 * T), (128, 128, 128)); d = ImageDraw.Draw(sheet)
fonts = glob.glob('/usr/share/fonts/**/*Sans*Regular*.ttf', recursive=True) + glob.glob('/usr/share/fonts/**/*.ttf', recursive=True)
font = ImageFont.truetype(fonts[0], 34) if fonts else ImageFont.load_default()
for i, (v, label) in enumerate(views):
    im = Image.open(f'render_{v}.png').convert('RGB').resize((T, T), Image.LANCZOS)
    x, y = (i % 2) * T, (i // 2) * T; sheet.paste(im, (x, y)); d.text((x + 24, y + 18), label, fill=(240, 240, 240), font=font)
d.text((24, 2 * T - 56), '15.68 ct oval (19.22 x 12.83 x 8.17 mm) | 2 x 6 mm hearts | 146 accent rounds | 18K white gold | US 5.5', fill=(235, 235, 235), font=font)
sheet.save('ring_views.png'); print('ok')

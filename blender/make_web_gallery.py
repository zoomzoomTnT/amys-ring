# Compress gallery images for the website: full (WebP, ~1400px).
import sys, os
from PIL import Image
G = '/workspace/ring/gallery'; OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
src = {'front': 'render_front_1600.png', 'top': 'render_top_1600.png', 'on_hand': 'on_hand.jpg'}
for k, f in src.items():
    im = Image.open(os.path.join(G, f)).convert('RGB')
    if f.startswith('render_'):  # lift the 246 studio gray to pure page white
        im = im.point(lambda v: min(255, round(v * 255 / 244)))
    full = im.copy(); full.thumbnail((1400, 1400), Image.LANCZOS)
    for q in (90, 84, 78, 70):
        p = os.path.join(OUT, k + '.webp'); full.save(p, 'WEBP', quality=q, method=6)
        if os.path.getsize(p) < 400_000: break
    w, h = im.size; s = min(w, h)
    print(k, full.size, os.path.getsize(p), 'q', q)

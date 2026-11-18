"""
Side-by-side zoom: the reference picture next to one or more sets of renders, at the same registered scale.

    python3 tools/zoom_compare.py designs/d2 front 0 150 200 460
    python3 tools/zoom_compare.py designs/d1 front 236 85 426 285 --against designs/d1/renders/current --out heart.png

The box (x0 y0 x1 y1) is in pixels of that view's panel in the reference picture (see reference/overlay.json).
Columns: reference, the design's build/ renders, then each --against folder (render_<view>.png, e.g. an older round).
Needs <build>/overlay_report.json (run tools/overlay_views.py first); other folders are fitted on the fly.
Writes <design>/build/zoom_<view>_<x0>_<y0>.png unless --out is given.
"""
import sys, os, json
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay_views import load_reference, fit_views


def report_for(design, folder):
    rp = os.path.join(folder, 'overlay_report.json')
    return json.load(open(rp)) if os.path.exists(rp) else fit_views(design, folder, write_images=False)


def model_crop(folder, view, rep, box, size):
    N = Image.open(os.path.join(folder, 'render_' + view + '.png')).convert('RGB')
    s, ox, oy = rep['fit_s'], rep['fit_ox'], rep['fit_oy']
    x0, y0, x1, y1 = box
    return N.crop((round((x0 - ox) / s), round((y0 - oy) / s), round((x1 - ox) / s), round((y1 - oy) / s))).resize(size, Image.LANCZOS)


def zoom_tiles(design, view, box, folders, width=420):
    """[reference tile, one tile per folder] for one crop box."""
    ref, quads = load_reference(design)
    x0, y0, x1, y1 = box
    size = (width, round((y1 - y0) * width / (x1 - x0)))
    tiles = [ref.crop(quads[view]).crop(box).resize(size, Image.LANCZOS)]
    for f in folders:
        tiles.append(model_crop(f, view, report_for(design, f)[view], box, size))
    return tiles


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 6: sys.exit(__doc__)
    design, view = a[0].rstrip('/'), a[1]; box = tuple(int(v) for v in a[2:6]); rest = a[6:]
    folders = [os.path.join(design, 'build')] + [rest[i + 1] for i, k in enumerate(rest) if k == '--against']
    out = rest[rest.index('--out') + 1] if '--out' in rest else os.path.join(design, 'build', 'zoom_%s_%d_%d.png' % (view, box[0], box[1]))
    tiles = zoom_tiles(design, view, box, folders)
    labels = ['reference'] + [os.path.relpath(f) for f in folders]
    W, H = tiles[0].size
    sheet = Image.new('RGB', (len(tiles) * (W + 10), H + 24), (38, 38, 38)); d = ImageDraw.Draw(sheet)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        sheet.paste(t, (i * (W + 10), 24)); d.text((i * (W + 10) + 4, 5), lab, fill='white')
    sheet.save(out); print(out, sheet.size)

"""
Review sheet for a refinement round: reference picture | before | after, one row per named close-up.

    python3 tools/review_sheet.py designs/d1                               # before = renders/current, after = build/
    python3 tools/review_sheet.py designs/d1 --before-label "Round 16" --after-label "Round 17" --out designs/d1/build/review.png
    python3 tools/review_sheet.py designs/d2 --before DIR                  # compare against any folder of renders

Rows come from <design>/reference/review_boxes.json: [{"title": ..., "view": "front", "box": [x0, y0, x1, y1]}, ...]
(boxes in pixels of that view's panel in the reference picture). Run tools/overlay_views.py on the build first.
The footer lists the outline IoU before -> after for every view. Default output: <design>/build/review.png.
Keep a finished round's sheet as <design>/renders/rounds/rNN-review.png.
"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_compare import zoom_tiles, report_for

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0].startswith('-'): sys.exit(__doc__)
    design = a[0].rstrip('/')
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    before = opt('--before', os.path.join(design, 'renders', 'current'))
    after = opt('--after', os.path.join(design, 'build'))
    labels = ['Reference picture', opt('--before-label', 'Before (committed)'), opt('--after-label', 'After (this build)')]
    rows = json.load(open(os.path.join(design, 'reference', 'review_boxes.json')))
    W = int(opt('--width', 340))
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    built = [(r['title'], zoom_tiles(design, r['view'], tuple(r['box']), [before, after], W)) for r in rows]
    TW = 3 * (W + 12) + 10; TH = 50 + sum(t[1][0].height + 40 for t in built) + 40
    sheet = Image.new('RGB', (TW, TH), (36, 36, 36)); d = ImageDraw.Draw(sheet)
    for i, h in enumerate(labels): d.text((10 + i * (W + 12), 14), h, fill='white', font=f)
    y = 50
    for title, tiles in built:
        d.text((10, y + 8), title, fill=(255, 210, 120), font=sm); y += 34
        for i, t in enumerate(tiles): sheet.paste(t, (10 + i * (W + 12), y))
        y += tiles[0].height + 6
    rb, ra = report_for(design, before), report_for(design, after)
    d.text((10, y + 6), 'Outline IoU before -> after: ' + ', '.join('%s %.3f -> %.3f' % (v, rb[v]['iou'], ra[v]['iou']) for v in ('front', 'side', 'top', 'three_quarter')), fill='white', font=sm)
    out = opt('--out', os.path.join(design, 'build', 'review.png'))
    sheet.save(out); print(out, sheet.size)

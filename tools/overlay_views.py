"""
Outline overlays: how closely a design's renders match its reference picture, view by view.

    python3 tools/overlay_views.py designs/d2                 # renders from designs/d2/build/
    python3 tools/overlay_views.py designs/d1 --renders DIR   # score other renders (e.g. an older round)

Reads   <design>/reference/overlay.json  {"ref": "original.jpg", "quads": {view: [x0, y0, x1, y1]}} (where each view sits
        in the picture), <renders>/render_<view>.png and <renders>/cams.json (written by the build).
Writes  <out>/overlay_<view>.png, overlay_all.png and overlay_report.json (IoU, fit scale/offset, mm per pixel).
        <out> defaults to the renders folder. Other tools (zoom_compare.py, review_sheet.py) read overlay_report.json.
IoU = overlap of the two silhouettes (1.0 = identical outlines).
"""
import sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

VIEWS = ['top', 'three_quarter', 'front', 'side']


def load_reference(design):
    """The design's reference picture (any red caption box blanked out) and the box of each view inside it."""
    cfg = json.load(open(os.path.join(design, 'reference', 'overlay.json')))
    ref = Image.open(os.path.join(design, 'reference', cfg['ref'])).convert('RGB')
    a = np.array(ref).astype(int)
    red = (a[..., 0] > 170) & (a[..., 1] < 140) & (a[..., 2] < 140)
    red = np.array(Image.fromarray((red * 255).astype('uint8')).filter(ImageFilter.MaxFilter(15))) > 0
    ys, xs = np.where(red)
    if len(xs): a[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = [128, 128, 128]  # blank the whole caption box incl. its white text
    return Image.fromarray(a.astype('uint8')), {k: tuple(v) for k, v in cfg['quads'].items()}


def mask(im, thr=28):
    b = np.array(im).astype(int)
    bg = np.median(np.concatenate([b[:4].reshape(-1, 3), b[-4:].reshape(-1, 3), b[:, :4].reshape(-1, 3), b[:, -4:].reshape(-1, 3)]), axis=0)
    m = (np.abs(b - bg).sum(-1) > thr).astype('uint8') * 255
    m = Image.fromarray(m).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    return fill_small_holes(largest(np.array(m) > 0))
def fill_small_holes(m, frac=0.02):
    # enclosed background pockets (metal that happens to match the grey backdrop) are filled; the finger hole stays open
    from collections import deque
    h, w = m.shape; inv = ~m; seen = np.zeros(m.shape, bool); out = m.copy()
    ys, xs = np.nonzero(inv)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]: continue
        q = deque([(y0, x0)]); seen[y0, x0] = True; comp = []; border = False
        while q:
            y, x = q.popleft(); comp.append((y, x))
            if y in (0, h - 1) or x in (0, w - 1): border = True
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and inv[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; q.append((yy, xx))
        if not border and len(comp) < frac * h * w:
            for (y, x) in comp: out[y, x] = True
    return out
def largest(m):
    # keep only the biggest connected blob (drops caption remnants / panel borders)
    from collections import deque
    h, w = m.shape; lab = np.zeros(m.shape, np.int32); best = (0, 0); cur = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]: continue
        cur += 1; lab[y0, x0] = cur; q = deque([(y0, x0)]); n = 0
        while q:
            y, x = q.popleft(); n += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur; q.append((yy, xx))
        if n > best[0]: best = (n, cur)
    return lab == best[1]
def bbox(m):
    ys, xs = np.where(m); return xs.min(), ys.min(), xs.max(), ys.max()
def edges(m):
    im = Image.fromarray((m * 255).astype('uint8'))
    return (np.array(im.filter(ImageFilter.MaxFilter(3))) > 0) & ~(np.array(im.filter(ImageFilter.MinFilter(3))) > 0)
def fit_views(design, renders, out=None, write_images=True):
    """Fit each render onto its view of the reference picture; returns the report dict (and writes images to out)."""
    out_dir = out or renders
    ref, quads = load_reference(design)
    # cams.json (ortho scale per view) only feeds the mm figures; fall back to the design's latest build if missing
    cp = next((c for c in (os.path.join(renders, 'cams.json'), os.path.join(design, 'build', 'cams.json')) if os.path.exists(c)), None)
    cams = json.load(open(cp)) if cp else {}
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
    outs = []; report = {}
    for v in VIEWS:
        R = ref.crop(quads[v]); mr = mask(R)
        N = Image.open(os.path.join(renders, 'render_' + v + '.png')).convert('RGB'); mn = mask(N)
        rb = bbox(mr); nb = bbox(mn)
        rw, rh = rb[2] - rb[0], rb[3] - rb[1]; nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        trunc = rb[3] >= mr.shape[0] - 3  # reference view runs off the bottom of its panel (side view)
        s0 = rw / nw if trunc else (rw / nw + rh / nh) / 2
        best = None
        for s in np.linspace(s0 * 0.94, s0 * 1.06, 13):
            Nm = Image.fromarray((mn * 255).astype('uint8')).resize((round(N.width * s), round(N.height * s)), Image.BILINEAR)
            nm = np.array(Nm) > 127; b2 = bbox(nm)
            for dx in range(-8, 9, 2):
                for dy in range(-8, 9, 2):
                    ox = rb[0] + (rw - (b2[2] - b2[0])) // 2 - b2[0] + dx
                    oy = (rb[1] - b2[1] + dy) if trunc else (rb[1] + (rh - (b2[3] - b2[1])) // 2 - b2[1] + dy)
                    can = np.zeros_like(mr)
                    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(mr.shape[1], ox + nm.shape[1]), min(mr.shape[0], oy + nm.shape[0])
                    can[y0:y1, x0:x1] = nm[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                    iou = (can & mr).sum() / max(1, (can | mr).sum())
                    if best is None or iou > best[0]: best = (iou, s, ox, oy, can)
        iou, s, ox, oy, can = best
        Ns = N.resize((round(N.width * s), round(N.height * s)), Image.LANCZOS)
        canvas = Image.new('RGB', R.size, (128, 128, 128)); canvas.paste(Ns, (ox, oy))
        blend = Image.blend(R, canvas, 0.5)
        arr = np.array(blend.convert('L').convert('RGB'))
        er, en = edges(mr), edges(can)
        arr[er] = [255, 40, 40]; arr[en] = [40, 220, 255]; arr[er & en] = [255, 255, 0]
        img = Image.fromarray(arr)
        # mm per reference pixel: render ortho scale (mm across the render width) / render px * (1/s)
        mm_px = cams[v] / N.width / s if v in cams else 0.0
        rb2 = bbox(can)
        diff = dict(iou=round(float(iou), 3), mm_per_px=round(mm_px, 4),
                    width_mm_ref=round(rw * mm_px, 2), width_mm_model=round((rb2[2] - rb2[0]) * mm_px, 2),
                    height_mm_ref=round(rh * mm_px, 2), height_mm_model=round((rb2[3] - rb2[1]) * mm_px, 2), ref_truncated=bool(trunc),
                    outline_mismatch_px=int((er ^ en).sum()), xor_area_mm2=round(float((can ^ mr).sum()) * mm_px ** 2, 1))
        diff.update(fit_s=float(s), fit_ox=int(ox), fit_oy=int(oy), quad=list(quads[v]))
        report[v] = diff
        d = ImageDraw.Draw(img); d.rectangle([0, 0, img.width, 26], fill=(30, 30, 30))
        d.text((6, 4), f'{v}: red=reference outline, cyan=model, IoU {diff["iou"]}', fill=(255, 255, 255), font=font)
        if write_images: img.save(os.path.join(out_dir, f'overlay_{v}.png'))
        outs.append(img)
    if write_images:
        HH = 560; tiles = [o.resize((round(o.width * HH / o.height), HH), Image.LANCZOS) for o in outs]
        Wt = max(tiles[0].width + tiles[1].width, tiles[2].width + tiles[3].width)
        sheet = Image.new('RGB', (Wt + 10, 2 * HH + 10), (40, 40, 40))
        sheet.paste(tiles[0], (0, 0)); sheet.paste(tiles[1], (tiles[0].width + 10, 0)); sheet.paste(tiles[2], (0, HH + 10)); sheet.paste(tiles[3], (tiles[2].width + 10, HH + 10))
        sheet.save(os.path.join(out_dir, 'overlay_all.png'))
        json.dump(report, open(os.path.join(out_dir, 'overlay_report.json'), 'w'), indent=1)
    return report


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0].startswith('-'):
        sys.exit(__doc__)
    design = a[0].rstrip('/')
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    renders = opt('--renders', os.path.join(design, 'build'))
    rep = fit_views(design, renders, opt('--out'))
    print(json.dumps(rep, indent=1))
    print('IoU: ' + ', '.join('%s %.3f' % (v, rep[v]['iou']) for v in ('front', 'side', 'top', 'three_quarter')))

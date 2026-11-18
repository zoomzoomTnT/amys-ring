"""
Finish a round: check the design's hard limits, then copy the new web model and renders into place.

    python3 tools/publish.py designs/d2                    # check + publish
    python3 tools/publish.py designs/d2 --check            # only check the limits
    python3 tools/publish.py designs/d2 --review r03       # also keep build/review.png as renders/rounds/r03-review.png

Checks <design>/model/stats.json against <design>/limits.json (gold weight, ring size, stone counts, GLB size).
Publishing copies
  build/ring.glb                       -> site/<dN>/ring.glb  (and updates that design's `bytes` in site/index.html)
  build/render_*.png, overlay_*.png,   -> <design>/renders/current/   (only full-size renders, 1600 px and up)
  overlay_report.json, cams.json
Then: add the round to DESIGN.md (round table + numbers), a CHANGELOG line, commit, push, check the live site.
"""
import sys, os, json, re, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(design):
    st = json.load(open(os.path.join(design, 'model', 'stats.json')))
    lim = json.load(open(os.path.join(design, 'limits.json')))
    glb = os.path.join(design, 'build', 'ring.glb')
    glb_mb = os.path.getsize(glb) / 1e6 if os.path.exists(glb) else st.get('glb_MB', 0)
    rows, ok = [], True
    def row(name, val, good, want):
        nonlocal ok
        ok &= bool(good); rows.append(('OK ' if good else 'FAIL') + '  %-16s %-34s %s' % (name, val, want))
    g = st['est_weight_g_18kw_14_7']
    if lim.get('gold_g'): row('gold weight', '%.2f g' % g, lim['gold_g'][0] <= g <= lim['gold_g'][1], 'want %s-%s g' % tuple(lim['gold_g']))
    else: rows.append('info  %-16s %-34s %s' % ('gold weight', '%.2f g' % g, '(informational for this design)'))
    d = st['inner_diameter_mm']; lo, hi = lim['inner_diameter_mm']
    row('ring size', '%.3f mm inner diameter' % d, lo <= d <= hi, 'want %s-%s mm (US 5.5)' % (lo, hi))
    row('stone counts', json.dumps(st['stone_counts'], sort_keys=True), st['stone_counts'] == lim['stones'], 'want ' + json.dumps(lim['stones'], sort_keys=True))
    row('web model', '%.2f MB' % glb_mb, glb_mb <= lim['glb_max_mb'], 'want <= %s MB' % lim['glb_max_mb'])
    print('\n'.join(rows))
    return ok


def publish(design, review=None):
    dn = os.path.basename(design)                      # 'd1', 'd2', ...
    n = dn.lstrip('d')
    glb = os.path.join(design, 'build', 'ring.glb')
    site_glb = os.path.join(ROOT, 'site', dn, 'ring.glb')
    shutil.copyfile(glb, site_glb); size = os.path.getsize(site_glb)
    idx = os.path.join(ROOT, 'site', 'index.html'); html = open(idx).read()
    pat = r'(label: "Design #%s", model: "\./%s/ring\.glb", bytes: )\d+' % (n, dn)
    html, k = re.subn(pat, r'\g<1>%d' % size, html)
    if k != 1: sys.exit('could not find the DESIGNS entry for %s in site/index.html' % dn)
    open(idx, 'w').write(html)
    print('site/%s/ring.glb  %d bytes (index.html updated)' % (dn, size))
    b, cur = os.path.join(design, 'build'), os.path.join(design, 'renders', 'current')
    rend = [f for f in os.listdir(b) if f.startswith('render_') and f.endswith('.png')]
    if rend and min(Image.open(os.path.join(b, f)).width for f in rend) >= 1600:
        for f in sorted(os.listdir(b)):
            if (f.startswith(('render_', 'overlay_')) and f.endswith('.png')) or f in ('overlay_report.json', 'cams.json'):
                shutil.copyfile(os.path.join(b, f), os.path.join(cur, f))
        print('renders + overlays -> %s' % os.path.relpath(cur, ROOT))
    else:
        print('renders not copied: build/ has no full-size (1600 px) renders; run the full build with --render first')
    if review:
        dst = os.path.join(design, 'renders', 'rounds', '%s-review.png' % review)
        shutil.copyfile(os.path.join(b, 'review.png'), dst); print('review sheet ->', os.path.relpath(dst, ROOT))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0].startswith('-'): sys.exit(__doc__)
    design = os.path.abspath(a[0].rstrip('/'))
    ok = check(design)
    if '--check' in a: sys.exit(0 if ok else 1)
    if not ok and '--force' not in a: sys.exit('hard limits not met: fix the model (or pass --force if the owner agreed)')
    publish(design, a[a.index('--review') + 1] if '--review' in a else None)

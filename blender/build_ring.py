"""
Engagement ring builder (Blender 4.2, headless).
  blender -b -P build_ring.py -- [--render] [--res 1600] [--samples 128] [--views top,three_quarter,front,side]
Units: 1 Blender unit = 1 mm.  Finger axis = Y.  Ring band lies in the XZ plane, head on +Z.
Center oval long axis along Y (along the finger); hearts at +/-X on the shoulders.
"""
import bpy, bmesh, math, sys, os, json, time
from mathutils import Vector, Matrix
from math import sin, cos, pi, radians, sqrt, atan2

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
DO_RENDER = '--render' in argv
RES = int(arg('--res', 1600))
SAMPLES = int(arg('--samples', 128))
VIEWS = arg('--views', 'top,three_quarter,front,side').split(',')
T0 = time.time()
def log(*a): print('[ring %6.1fs]' % (time.time() - T0), *a, flush=True)

# --------------------------------------------------------------------------- parameters
R_IN = 16.1 / 2                 # US 5.5
# center stone (IGI LG843655695)
C_L, C_W, C_D = 19.22, 12.83, 8.17
C_A, C_B = C_L / 2, C_W / 2     # a along Y, b along X
C_HC, C_HP = 0.16 * C_W, 0.405 * C_W
C_G = C_D - C_HC - C_HP         # ~0.92 mm girdle
Z_CULET = 10.40
Z_GB = Z_CULET + C_HP           # girdle bottom
Z_GT = Z_GB + C_G               # girdle top
Z_GM = (Z_GB + Z_GT) / 2
Z_TABLE = Z_GT + C_HC
C_TABLE_S = 0.60 / cos(pi / 8)
PRONG_TH = [radians(a) for a in (40, 140, 220, 320)]   # claw positions (ellipse parameter), from the top view
# heart
H_SIZE, H_HC, H_G, H_HP, H_TS = 6.0, 0.85, 0.24, 2.40, 0.55
H_TILT = radians(float(arg('--htilt', 50)))         # lobe->point axis 50 deg from horizontal: lobes up/in at the gallery, point down/out, table faces up-outward
H_X, H_Z = float(arg('--hx', 8.1)), float(arg('--hz', 10.95))   # heart girdle centre
H_COUNTS = [4, 4, 3]
H_WRAP = '--nowrap' not in argv
H_LOBE_T = float(arg('--lobet', 0.95))   # heart outline parameter of the two lobe prongs
POST_B = int(arg('--postb', 2))
TIES = '--ties' in argv
POST_Y = float(arg('--posty', -1.8))
TIE_X, TIE_Y = float(arg('--tiex', 1.6)), float(arg('--tiey', 1.6))           # shank claw boundary the heart-point post lands on (2 = ~42 deg)          # 1.4 mm frame stones per heart: side, side, over the lobes
# shank
SH_T0, SH_T, SH_TB = 2.25, float(arg('--sht', 2.30)), float(arg('--shtb', 1.60))   # radial thickness (top centre, shoulders/sides, bottom)
SH_W, SH_WB = float(arg('--shw', 1.78)), 1.55      # half width (along the finger)
STONE3_START = radians(16.5)  # first 3.0 mm stone, 7 per side
PITCH3 = 3.05
STONE3_LIFT = float(arg('--lift3', 0.25))   # 3.0 mm girdles sit proud of the metal, held by the claws
SIDE_SPAN = radians(130)      # 1.0 mm side-wall rows run +/-130 deg over the top
SIDE_R = 0.95                 # their centre, measured out from the inner surface
# gallery rail + arms
RAIL_ZT, RAIL_ZB, RAIL_IN = 14.50, 13.00, 0.35
ARM_S, ARM_ZT = 0.86, 12.85
ARM_BX, ARM_BY, ARM_BZ = 0.85, 1.45, 10.05
ARM_PITCH = 1.36
ARM_OFF = float(arg('--armoff', -0.60))

# --------------------------------------------------------------------------- mesh builder
class MB:
    def __init__(s): s.v = []; s.f = []
    def vert(s, p): s.v.append(tuple(p)); return len(s.v) - 1
    def face(s, *idx): s.f.append(tuple(idx))
    def extend(s, o):
        n = len(s.v); s.v += o.v; s.f += [tuple(i + n for i in f) for f in o.f]; return s
    def xform(s, M):
        o = MB(); o.v = [tuple(M @ Vector(p)) for p in s.v]; o.f = list(s.f); return o
    def mirror_x(s):
        o = MB(); o.v = [(-x, y, z) for (x, y, z) in s.v]; o.f = [tuple(reversed(f)) for f in s.f]; return o

COLL = None
def to_obj(name, mb, mat, smooth=False, sharp_deg=40):
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.v, [], mb.f)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    if smooth:
        me.shade_smooth(); me.set_sharp_from_angle(angle=radians(sharp_deg))
    ob = bpy.data.objects.new(name, me); COLL.objects.link(ob)
    return ob

def frame(origin, zax, xhint=Vector((1, 0, 0))):
    z = Vector(zax).normalized()
    if abs(z.dot(xhint)) > 0.95: xhint = Vector((0, 1, 0)) if abs(z.y) < 0.9 else Vector((0, 0, 1))
    x = (xhint - z * xhint.dot(z)).normalized(); y = z.cross(x)
    M = Matrix.Identity(4)
    for i in range(3): M[i][0], M[i][1], M[i][2], M[i][3] = x[i], y[i], z[i], origin[i]
    return M

# --------------------------------------------------------------------------- faceted stones
def zipper(mb, A, pa, B, pb, N):
    nA, nB = len(A), len(B)
    pa2 = list(pa) + [pa[0] + N]; pb2 = list(pb) + [pb[0] + N]
    i = j = 0
    while i < nA or j < nB:
        if j >= nB or (i < nA and pa2[i + 1] <= pb2[j + 1]):
            mb.face(A[i % nA], A[(i + 1) % nA], B[j % nB]); i += 1
        else:
            mb.face(A[i % nA], B[(j + 1) % nB], B[j % nB]); j += 1

def stone_mb(outline, N, rings, z_top, z_bot, c=(0.0, 0.0)):
    mb = MB(); idx = []
    for (s, z, pos) in rings:
        row = []
        for p in pos:
            q = outline(p)
            row.append(mb.vert((c[0] + s * (q[0] - c[0]), c[1] + s * (q[1] - c[1]), z)))
        idx.append(row)
    top = mb.vert((c[0], c[1], z_top)); bot = mb.vert((c[0], c[1], z_bot))
    r0 = idx[0]
    for i in range(len(r0)): mb.face(top, r0[i], r0[(i + 1) % len(r0)])
    for k in range(len(rings) - 1): zipper(mb, idx[k], rings[k][2], idx[k + 1], rings[k + 1][2], N)
    rl = idx[-1]
    for i in range(len(rl)): mb.face(bot, rl[(i + 1) % len(rl)], rl[i])
    return mb

def round_brilliant(D):
    """girdle centre at z=0, table up (+z). Ideal-ish cut: table 57%, crown 15.5%, pavilion 43%."""
    N = 32 if D >= 2.5 else 16
    R = D / 2; g = 0.025 * D; hc = 0.155 * D; hp = 0.43 * D
    st = 0.285 / cos(pi / 8) / 0.5
    outline = lambda f: (R * cos(2 * pi * f / N), R * sin(2 * pi * f / N))
    step = N // 8
    tab = [k * step for k in range(8)]
    mid = [k * step + step / 2 for k in range(8)]
    gir = list(range(N))
    pav = [k * step for k in range(8)]
    zc = lambda s: g / 2 + hc * (1 - s) / (1 - st)
    rings = [(st, g / 2 + hc, tab), (0.80, zc(0.80) + 0.012 * D, mid), (1, g / 2, gir), (1, -g / 2, gir),
             (0.30, -g / 2 - hp * 0.70 - 0.012 * D, pav)]
    return stone_mb(outline, N, rings, g / 2 + hc, -g / 2 - hp), dict(D=D, g=g, hc=hc, hp=hp)

def oval_brilliant():
    N = 64; a, b = C_A, C_B; g, hc, hp = C_G, C_HC, C_HP; st = C_TABLE_S
    outline = lambda f: (b * cos(2 * pi * f / N), a * sin(2 * pi * f / N))
    zc = lambda s: g / 2 + hc * (1 - s) / (1 - st)
    zp = lambda s: -g / 2 - hp * (1 - s)
    rings = [(st, g / 2 + hc, [4 + 8 * k for k in range(8)]),
             (0.82, zc(0.82) + 0.05, [8 * k for k in range(8)]),
             (0.95, zc(0.95) + 0.03, [2 + 4 * k for k in range(16)]),
             (1, g / 2, list(range(N))), (1, -g / 2, list(range(N))),
             (0.62, zp(0.62) - 0.06, [4 * k for k in range(16)]),
             (0.25, zp(0.25) - 0.05, [8 * k for k in range(8)])]
    return stone_mb(outline, N, rings, g / 2 + hc, -g / 2 - hp)

def heart_outline_pts(size=H_SIZE, N=40):
    M = 8000
    raw = []
    for i in range(M + 1):
        t = 2 * pi * i / M
        raw.append((t, 16 * sin(t) ** 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)))
    xs = [p[1] for p in raw]; ys = [p[2] for p in raw]
    sx = size / (max(xs) - min(xs)); sy = size / (max(ys) - min(ys)); yc = (max(ys) + min(ys)) / 2
    pts = [(t, x * sx, (y - yc) * sy) for (t, x, y) in raw]
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.hypot(pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]))
    L = cum[-1]; out = []; ts = []; j = 0
    for k in range(N):
        s = L * k / N
        while cum[j + 1] < s: j += 1
        u = (s - cum[j]) / max(1e-9, cum[j + 1] - cum[j])
        out.append((pts[j][1] + u * (pts[j + 1][1] - pts[j][1]), pts[j][2] + u * (pts[j + 1][2] - pts[j][2])))
        ts.append(pts[j][0])
    return out, ts, L

H_PTS, H_TS_PARAM, H_PERIM = heart_outline_pts()
H_N = len(H_PTS)
def h_outline(f):
    f = f % H_N; i = int(math.floor(f)); u = f - i
    p, q = H_PTS[i], H_PTS[(i + 1) % H_N]
    return (p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1]))
H_LOBE_X = abs(max(H_PTS, key=lambda p: p[1])[0]); H_LOBE_Y = max(p[1] for p in H_PTS)
def h_hull(f):
    x, y = h_outline(f)
    if y > 0 and abs(x) < H_LOBE_X: y = max(y, H_LOBE_Y)
    return (x, y)

def heart_stone():
    N = H_N; g, hc, hp, st = H_G, H_HC, H_HP, H_TS
    zc = lambda s: g / 2 + hc * (1 - s) / (1 - st)
    ev = list(range(0, N, 2)); od = [i + 1 for i in ev]
    rings = [(st, g / 2 + hc, ev), (0.80, zc(0.8) + 0.03, od), (1, g / 2, list(range(N))), (1, -g / 2, list(range(N))),
             (0.45, -g / 2 - hp * 0.55 - 0.03, ev)]
    return stone_mb(h_outline, N, rings, g / 2 + hc, -g / 2 - hp)

# --------------------------------------------------------------------------- metal primitives
def loft(sections, closed_v=True, cap=False):
    """sections: list of profiles (each list of K Vectors, closed loop)."""
    mb = MB(); K = len(sections[0]); M = len(sections)
    ids = [[mb.vert(p) for p in sec] for sec in sections]
    rng = M if closed_v else M - 1
    for m in range(rng):
        A, B = ids[m], ids[(m + 1) % M]
        for k in range(K): mb.face(A[k], A[(k + 1) % K], B[(k + 1) % K], B[k])
    if cap and not closed_v:
        for sec, ii, rev in ((sections[0], ids[0], True), (sections[-1], ids[-1], False)):
            c = mb.vert(sum((Vector(p) for p in sec), Vector()) / K)
            for k in range(K):
                f = (c, ii[k], ii[(k + 1) % K]); mb.face(*(reversed(f) if rev else f))
    return mb

def catmull(pts, rads, sub=6):
    P = [Vector(p) for p in pts]; P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    R = [rads[0]] + list(rads) + [rads[-1]]
    op, orr = [], []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(sub):
            t = k / sub; t2, t3 = t * t, t * t * t
            op.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            orr.append(R[i] + (R[i + 1] - R[i]) * t)
    op.append(P[-2]); orr.append(R[-2])
    return op, orr

def tube(pts, rads, seg=12, smooth=True, tip=True):
    if smooth: pts, rads = catmull(pts, rads)
    pts = [Vector(p) for p in pts]; n = len(pts)
    T = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    nrm = T[0].orthogonal().normalized(); secs = []
    for i in range(n):
        if i > 0:
            nrm = (nrm - T[i] * nrm.dot(T[i])).normalized()
        bn = T[i].cross(nrm)
        secs.append([pts[i] + rads[i] * (cos(2 * pi * k / seg) * nrm + sin(2 * pi * k / seg) * bn) for k in range(seg)])
    mb = loft(secs, closed_v=False, cap=False)
    K = seg
    c0 = mb.vert(pts[0] - T[0] * rads[0] * 0.3)
    for k in range(K): mb.face(c0, (k + 1) % K, k)
    c1 = mb.vert(pts[-1] + T[-1] * rads[-1] * (0.9 if tip else 0.3))
    base = (n - 1) * K
    for k in range(K): mb.face(c1, base + k, base + (k + 1) % K)
    return mb

def sphere(c, r, seg=10, rings=6):
    mb = MB(); c = Vector(c)
    top = mb.vert(c + Vector((0, 0, r))); bot = mb.vert(c - Vector((0, 0, r))); ids = []
    for i in range(1, rings):
        th = pi * i / rings
        ids.append([mb.vert(c + r * Vector((sin(th) * cos(2 * pi * k / seg), sin(th) * sin(2 * pi * k / seg), cos(th)))) for k in range(seg)])
    for k in range(seg):
        mb.face(top, ids[0][k], ids[0][(k + 1) % seg]); mb.face(bot, ids[-1][(k + 1) % seg], ids[-1][k])
    for i in range(len(ids) - 1):
        for k in range(seg): mb.face(ids[i][k], ids[i + 1][k], ids[i + 1][(k + 1) % seg], ids[i][(k + 1) % seg])
    return mb

def torus_ellipse(cx, cy, bx, ay, z, r, M=64, K=10):
    secs = []
    for m in range(M):
        th = 2 * pi * m / M
        P = Vector((cx + bx * cos(th), cy + ay * sin(th), z))
        n = Vector((cos(th) / bx, sin(th) / ay, 0)).normalized()
        secs.append([P + r * (cos(2 * pi * k / K) * n + sin(2 * pi * k / K) * Vector((0, 0, 1))) for k in range(K)])
    return loft(secs)

def revolve(profile, M, seg=16):
    """profile: list of (radius, h) top->bottom; first and last radius 0 -> closed solid around local z."""
    mb = MB(); rows = []
    for (r, h) in profile:
        if r < 1e-6: rows.append([mb.vert((0, 0, h))])
        else: rows.append([mb.vert((r * cos(2 * pi * k / seg), r * sin(2 * pi * k / seg), h)) for k in range(seg)])
    for i in range(len(rows) - 1):
        A, B = rows[i], rows[i + 1]
        for k in range(seg):
            if len(A) == 1: mb.face(A[0], B[k], B[(k + 1) % seg])
            elif len(B) == 1: mb.face(A[k], B[0], A[(k + 1) % seg])
            else: mb.face(A[k], B[k], B[(k + 1) % seg], A[(k + 1) % seg])
    return mb.xform(M)

def seat_cutter(info, M, through=None, hole_frac=0.45):
    Rg = info['D'] / 2; g = info['g']; hp = info['hp']
    hr = Rg * hole_frac
    # bore = girdle diameter + 0.02 mm; seat cone slightly narrower than the pavilion so the stone rests on it
    prof = [(0, 3.0), (Rg + 0.01, 3.0), (Rg + 0.01, -g / 2), (Rg * 0.96, -g / 2 - 0.01), (hr, -g / 2 - hp * (1 - hr / Rg))]
    if through: prof += [(hr, -through), (0, -through)]
    else: prof += [(0, -g / 2 - hp - 0.1)]
    return revolve(prof, M)

# --------------------------------------------------------------------------- stones registry
STONES = []          # dicts: kind, D, M (matrix)
BEADS = MB(); CLAWS = MB(); CUTTERS = {}
STONE_MB = {}
def add_round(D, center, axis, target, through=None, tangent=None, hole_frac=0.45):
    M = frame(Vector(center), Vector(axis), Vector(tangent) if tangent else Vector((1, 0, 0)))
    STONES.append(dict(kind='round', D=D, M=M, center=Vector(center), axis=Vector(axis).normalized(), target=target))
    if D not in STONE_MB: STONE_MB[D] = round_brilliant(D)
    if target:
        CUTTERS.setdefault(target, MB()).extend(seat_cutter(STONE_MB[D][1], M, through, hole_frac))
    return STONES[-1]

def bead_row(row, closed=False, rb=None, ends=True):
    """row: list of stone dicts (same D) in order; adds shared bead prongs between neighbours."""
    if len(row) < 1: return
    D = row[0]['D']; info = STONE_MB[D][1]; rb = rb or max(0.16, 0.14 * D)
    pairs = []
    for i in range(len(row) - 1): pairs.append((row[i]['center'], row[i + 1]['center'], row[i]['axis'] + row[i + 1]['axis']))
    if closed and len(row) > 2: pairs.append((row[-1]['center'], row[0]['center'], row[-1]['axis'] + row[0]['axis']))
    if ends and not closed and len(row) > 1:
        c0, c1 = row[0]['center'], row[1]['center']; pairs.append((c0 * 2 - c1, c0, row[0]['axis'] * 2))
        c0, c1 = row[-1]['center'], row[-2]['center']; pairs.append((c0, c0 * 2 - c1, row[-1]['axis'] * 2))
    for (p, q, ax) in pairs:
        ax = ax.normalized(); m = (p + q) / 2; half = (q - p).length / 2; tg = (q - p).normalized()
        v = ax.cross(tg).normalized(); lift = ax * (info['g'] / 2 + 0.03)
        target = D / 2 + rb * 0.55
        if half < target - 0.12:
            off = sqrt(target ** 2 - half ** 2)
            for sgn in (-1, 1): BEADS.extend(sphere(m + sgn * off * v + lift, rb, 8, 5))
        else:
            BEADS.extend(sphere(m + lift, max(rb, half - D / 2 + 0.10), 8, 5))

def place_on_curve(curve, prong_s, counts, L, margin):
    """curve(s)->(point, axis) by arc length s in [0,L); prong_s sorted; counts per segment between prongs."""
    out = []
    for i, n in enumerate(counts):
        sa = prong_s[i]; sb = prong_s[(i + 1) % len(prong_s)]
        if sb <= sa: sb += L
        a, b = sa + margin, sb - margin
        seg = [(a + b) / 2] if n == 1 else [a + (b - a) * k / (n - 1) for k in range(n)]
        out.append([curve(s % L) for s in seg])
    return out

def arclen_table(fn, M=4000):
    pts = [fn(2 * pi * i / M) for i in range(M + 1)]
    cum = [0.0]
    for i in range(1, len(pts)): cum.append(cum[-1] + (pts[i] - pts[i - 1]).length)
    return pts, cum

def th_at(cum, s, M=4000):
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cum[mid] < s: lo = mid
        else: hi = mid
    u = (s - cum[lo]) / max(1e-9, cum[hi] - cum[lo])
    return 2 * pi * (lo + u) / M

# --------------------------------------------------------------------------- materials
def materials():
    gold = bpy.data.materials.new('WhiteGold18K'); gold.use_nodes = True
    b = gold.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.86, 0.86, 0.85, 1)
    b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.10
    dia = bpy.data.materials.new('Diamond'); dia.use_nodes = True
    d = dia.node_tree.nodes['Principled BSDF']
    d.inputs['Base Color'].default_value = (1, 1, 1, 1)
    d.inputs['Metallic'].default_value = 0.0; d.inputs['Roughness'].default_value = 0.0
    d.inputs['IOR'].default_value = 2.42
    d.inputs['Transmission Weight'].default_value = 1.0
    if 'Dispersion' in d.inputs: d.inputs['Dispersion'].default_value = 0.02
    return gold, dia

# --------------------------------------------------------------------------- build
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def claw_row(row, rb=0.40, ext=0.75, base=0.55, off_min=0.0, store=None):
    """Shared claw prongs (short radial posts with round tips) between neighbouring stones and at both row ends."""
    D = row[0]['D']; info = STONE_MB[D][1]
    store = store if store is not None else CLAWS
    pairs = []
    for i in range(len(row) - 1): pairs.append((row[i]['center'], row[i + 1]['center'], row[i]['axis'] + row[i + 1]['axis']))
    c0, c1 = row[0]['center'], row[1]['center']; pairs.insert(0, (c0 * 2 - c1, c0, row[0]['axis'] * 2))
    c0, c1 = row[-1]['center'], row[-2]['center']; pairs.append((c0, c0 * 2 - c1, row[-1]['axis'] * 2))
    tips = []
    for (p, q, ax) in pairs:
        ax = ax.normalized(); m = (p + q) / 2; half = (q - p).length / 2; tg = (q - p).normalized()
        v = ax.cross(tg).normalized()
        target = D / 2 + rb * 0.55
        off = sqrt(max(0.0, target ** 2 - half ** 2)); off = max(off, off_min)
        for sgn in (-1, 1):
            c = m + sgn * off * v
            p0 = c - ax * base; p2 = c + ax * (info['g'] / 2 + ext)
            store.extend(tube([p0, (p0 + p2) / 2, p2], [rb, rb, rb * 0.92], seg=12, tip=True))
            tips.append(p2)
    return tips

def bar(A, B, n, W, T, rr=0.22, k=3):
    """straight bar A->B with rounded-rectangle section (W across, T along n), capped."""
    A, B, n = Vector(A), Vector(B), Vector(n).normalized()
    d = (B - A).normalized(); w = d.cross(n).normalized(); n = w.cross(d).normalized()
    sec = []
    for (cx, cy, a0) in ((W / 2 - rr, T / 2 - rr, 0), (-W / 2 + rr, T / 2 - rr, 90), (-W / 2 + rr, -T / 2 + rr, 180), (W / 2 - rr, -T / 2 + rr, 270)):
        for i in range(k + 1):
            a = radians(a0 + 90 * i / k); sec.append((cx + rr * cos(a), cy + rr * sin(a)))
    secs = [[P + x * w + y * n for (x, y) in sec] for P in (A, B)]
    return loft(secs, closed_v=False, cap=True), d, w, n

def build():
    global COLL
    clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
    COLL = bpy.data.collections.new('Ring'); sc.collection.children.link(COLL)
    GOLD, DIA = materials()
    metal = {}       # name -> MB
    Z = lambda z: Vector((0, 0, z))
    for D in (1.0, 1.2, 1.3, 1.4, 3.0): STONE_MB[D] = round_brilliant(D)

    # ---------------- shank -------------------------------------------------
    def smooth(x0, x1, x):
        t = min(1, max(0, (x - x0) / (x1 - x0))); return t * t * (3 - 2 * t)
    def thick(phi):
        p = abs(phi)
        return SH_T0 + (SH_T - SH_T0) * smooth(radians(4), radians(28), p) + (SH_TB - SH_T) * smooth(radians(128), pi, p)
    def half_w(phi):
        return SH_W + (SH_WB - SH_W) * smooth(radians(122), pi, abs(phi))
    def profile(t, w, n=5):
        ro, ri = 0.55, 0.30; pts = []
        corners = [((R_IN + t - ro, w - ro), ro, 0), ((R_IN + ri, w - ri), ri, 90), ((R_IN + ri, -w + ri), ri, 180), ((R_IN + t - ro, -w + ro), ro, 270)]
        for (c, r, a0) in corners:
            for k in range(n):
                a = radians(a0 + 90 * k / (n - 1)); pts.append((c[0] + r * cos(a), c[1] + r * sin(a)))
        return pts
    secs = []; M = 360
    for m in range(M):
        phi = -pi + 2 * pi * m / M
        secs.append([Vector((r * sin(phi), y, r * cos(phi))) for (r, y) in profile(thick(phi), half_w(phi))])
    metal['Shank'] = loft(secs)
    r_out = lambda phi: R_IN + thick(phi)

    # 3.0 mm stones on the outer face: 7 per side from 16.5 deg, shared claw prongs that stand proud (the 'teeth')
    tooth_tips = {}
    for side in (1, -1):
        row = []
        dphi = PITCH3 / (r_out(radians(60)) + STONE3_LIFT)
        for k in range(7):
            ph = side * (STONE3_START + k * dphi)
            ax = Vector((sin(ph), 0, cos(ph)))
            row.append(add_round(3.0, ax * (r_out(ph) + STONE3_LIFT), ax, 'Shank', through=3.0, tangent=Vector((0, 1, 0))))
        tips = claw_row(row, rb=0.48, ext=0.85, base=0.9, off_min=1.10)
        tooth_tips[side] = [(tips[2 * i], tips[2 * i + 1]) for i in range(len(tips) // 2)]   # per boundary: (y-, y+)
    # 1.0 mm stones on both side walls: one continuous row of 31 per wall, over the top, +/-130 deg
    for ysgn in (1, -1):
        srow = []
        for k in range(-15, 16):
            ph = k * SIDE_SPAN / 15
            r = R_IN + SIDE_R
            c = Vector((r * sin(ph), ysgn * (half_w(ph) - 0.05), r * cos(ph)))
            srow.append(add_round(1.0, c, Vector((0, ysgn, 0)), 'Shank', through=None, hole_frac=0.2, tangent=Vector((sin(ph), 0, cos(ph)))))
        bead_row(srow, rb=0.17)
    log('shank stones', len(STONES))

    # ---------------- center head ------------------------------------------
    a, b = C_A, C_B
    E = lambda th, sx=1, sy=1: Vector((b * sx * cos(th), a * sy * sin(th), 0))
    En = lambda th: Vector((cos(th) / b, sin(th) / a, 0)).normalized()
    # gallery rail: flat channel rail ~1.1 mm below the girdle, 32 x 1.3 mm channel-set on its outer face
    s_in = (RAIL_ZT - Z_CULET) / C_HP
    secs = []
    for m in range(192):
        th = 2 * pi * m / 192; P = E(th); n = En(th)
        outer = P - RAIL_IN * n; inner = P * s_in + 0.12 * n
        secs.append([inner + Z(RAIL_ZT), inner + Z(RAIL_ZB), outer + Z(RAIL_ZB), outer + Z(RAIL_ZT)])
    metal['GalleryRail'] = loft(secs)
    # 4 claw prongs, continuing below the rail as pave arms that run down the pavilion to the shank (the 'V')
    pr = MB(); arms = MB(); arm_rows = []
    zcrown = lambda s: Z_GT + C_HC * (1 - s) / (1 - C_TABLE_S)
    for th in PRONG_TH:
        n = En(th); P = E(th)
        sx = 1 if cos(th) > 0 else -1; sy = 1 if sin(th) > 0 else -1
        A = E(th, ARM_S, ARM_S) + Z(ARM_ZT)
        B = Vector((ARM_BX * sx, ARM_BY * sy, ARM_BZ))
        Ptip = E(th, 0.905, 0.905) + Z(zcrown(0.905) + 0.16)
        P4 = P + 0.22 * n + Z(Z_GT + 0.55)
        P3 = P + 0.56 * n + Z(Z_GM)
        P2 = P + 0.40 * n + Z(Z_GB - 0.55)
        Pr = P - RAIL_IN * n + 0.50 * n + Z((RAIL_ZT + RAIL_ZB) / 2)
        pr.extend(tube([A + Z(0.25), Pr, P2, P3, P4, Ptip], [0.62, 0.64, 0.68, 0.72, 0.66, 0.50], seg=16))
        rad = Vector((A.x, A.y, 0)).normalized(); d = (B - A).normalized(); an = (rad - d * rad.dot(d)).normalized()
        mb_, d, w, an = bar(A - d * 0.3, B, an, 1.45, 1.05)
        arms.extend(mb_)
        L = (B - A).length; row = []
        for k in range(4):
            t = L / 2 + ARM_OFF + (k - 1.5) * ARM_PITCH
            c = A + d * t + an * (1.05 / 2 - 0.04)
            row.append(add_round(1.2, c, an, 'Arms', through=None, hole_frac=0.3, tangent=d))
        arm_rows.append(row)
    metal['CenterProngs'] = pr; metal['Arms'] = arms
    for row in arm_rows: bead_row(row, rb=0.2)
    def ring_row(curve_fn, axis_fn, D, total, margin, target, through, zrow, beads=True):
        pts, cum = arclen_table(lambda th: curve_fn(th))
        L = cum[-1]
        ps = [cum[int(round(th / (2 * pi) * 4000))] for th in PRONG_TH]
        LBseg = ps[1] - ps[0]; LAseg = (ps[0] + L) - ps[3]
        best = None
        for nA in range(1, total // 2):
            nB = total // 2 - nA
            pA = (LAseg - 2 * margin) / max(1, nA - 1); pB = (LBseg - 2 * margin) / max(1, nB - 1)
            sc_ = abs(pA - pB) + (100 if min(pA, pB) < D * 1.0 else 0)
            if best is None or sc_ < best[0]: best = (sc_, nA, nB, pA, pB)
        _, nA, nB, pA, pB = best
        rows = place_on_curve(lambda s: th_at(cum, s), ps, [nB, nA, nB, nA], L, margin)
        for seg in rows:
            srow = []
            for th in seg:
                c = curve_fn(th); ax = axis_fn(th)
                srow.append(add_round(D, c - ax * 0.05 + Vector((0, 0, zrow)), ax, target, through=through, hole_frac=0.3, tangent=Vector((0, 0, 1))))
                if target == 'GalleryRail':   # the heart frames butt into the rail: cut the same seats through them
                    CUTTERS.setdefault('HeartRail', MB()).extend(seat_cutter(STONE_MB[D][1], srow[-1]['M'], through, 0.3))
            if beads: bead_row(srow, ends=False)
        return dict(nA=nA, nB=nB, pitchA=pA, pitchB=pB, perimeter=L)
    gal = ring_row(lambda th: E(th) - RAIL_IN * En(th), En, 1.3, 32, 0.64 + 0.65, 'GalleryRail', None, (RAIL_ZT + RAIL_ZB) / 2, beads=False)
    log('gallery', gal)

    # ---------------- hearts (built for +X then mirrored) ------------------
    tau = H_TILT
    e_u = Vector((-cos(tau), 0, sin(tau)))      # local +y (point -> lobes): lobes up and in, toward the centre stone
    e_v = Vector((0, 1, 0))                      # local +x (along the finger)
    e_n = Vector((sin(tau), 0, cos(tau)))        # table normal: up and outward
    H_CENTER = Vector((H_X, 0, H_Z))
    HM = Matrix.Identity(4)
    for i in range(3): HM[i][0], HM[i][1], HM[i][2], HM[i][3] = e_v[i], e_u[i], e_n[i], H_CENTER[i]
    def hl(x, y, z): return HM @ Vector((x, y, z))
    def radial(i):
        q = Vector(h_outline(i)); return q, q.normalized()
    def normal2(i):
        p0 = Vector(h_outline(i - 1.0)); p1 = Vector(h_outline(i + 1.0)); t = (p1 - p0).normalized()
        n = Vector((t.y, -t.x)); q = Vector(h_outline(i))
        if n.dot(q) < 0: n = -n
        return n
    hmetal = {}
    HR_OUT, HZT, HZB = 0.30, -H_G / 2 - 0.10, -H_G / 2 - 1.70
    secs = []
    for m in range(H_N * 3):
        f = m / 3.0; q = Vector(h_outline(f)); r = q.normalized(); qh = Vector(h_hull(f))
        secs.append([hl(*(q * 0.995), HZT), hl(*(q * 0.62), HZB), hl(*(qh + HR_OUT * r), HZB), hl(*(qh + HR_OUT * r), HZT)])
    hmetal['HeartRail'] = loft(secs)
    HBZ = -H_G / 2 - H_HP - 0.08
    secs = []
    for m in range(40):
        a_ = 2 * pi * m / 40; P = Vector((1.0 * cos(a_), 1.0 * sin(a_), HBZ)); n = Vector((cos(a_), sin(a_), 0))
        secs.append([HM @ (P + 0.40 * (cos(2 * pi * k / 10) * n + sin(2 * pi * k / 10) * Vector((0, 0, 1)))) for k in range(10)])
    # (no base ring under the culet: the heart sits in its frame rail)
    iP = H_N // 2
    tl = [abs(t - H_LOBE_T) for t in H_TS_PARAM]; iL1 = tl.index(min(tl))
    iL2 = (H_N - iL1) % H_N
    hzc = lambda s: H_G / 2 + H_HC * (1 - s) / (1 - H_TS)
    hp_ = MB(); prong_idx = sorted([iL1, iP, iL2]) if not H_WRAP else sorted([iL1, iL2])
    for i in prong_idx:
        q, r = radial(i)
        P0 = hl(*(r * 1.0), HBZ)
        P1 = hl(*(q + 0.42 * r), -1.35)
        P2 = hl(*(q + (0.50 - 0.13) * r), 0.0)
        P3 = hl(*(q + 0.06 * r), H_G / 2 + 0.40)
        P4 = hl(*(q * 0.90), hzc(0.90) + 0.09)
        hp_.extend(tube([P1, P2, P3, P4], [0.50, 0.50, 0.42, 0.15], seg=12))
    hmetal['HeartProngs'] = hp_
    # supports: V-posts from the heart base and from the heart point down onto the shank claws
    posts = MB()
    pt_c = hl(0, POST_Y, HZB + 0.15)
    tt = tooth_tips[1]
    bi = POST_B
    for tip in tt[bi]:
        tgt = tip - Vector((sin(atan2(tip.x, tip.z)), 0, cos(atan2(tip.x, tip.z)))) * 0.25
        posts.extend(tube([pt_c, (pt_c + tgt) / 2, tgt], [0.45, 0.42, 0.42], seg=12, tip=False))
    # heart frame ties into the underside of the gallery rail (the short bars seen in the front view)
    s_in_ = (RAIL_ZT - Z_CULET) / C_HP
    for sx_ in ((-1, 1) if TIES else ()):
        top_c = hl(sx_ * TIE_X, TIE_Y, HZB + 0.15)
        th_ = math.asin(max(-1, min(1, top_c.y / (C_A * 0.95))))
        P_ = E(th_); n_ = En(th_)
        rail_pt = (P_ * s_in_ + 0.12 * n_ + P_ - RAIL_IN * n_) / 2 + Z(RAIL_ZB + 0.15)
        posts.extend(tube([top_c, (top_c + rail_pt) / 2, rail_pt], [0.42, 0.42, 0.42], seg=12, tip=False))
    hmetal['HeartPosts'] = posts
    log('heart centre', tuple(round(x, 2) for x in H_CENTER), 'point-> boundary', bi, 'post start', tuple(round(x, 2) for x in pt_c),
        'lobe tip', tuple(round(x, 2) for x in hl(0, 3, 0)), 'point', tuple(round(x, 2) for x in hl(0, -3, 0)))
    # heart frame stones 1.4 mm x 11 per heart on the rail's outer face, skipping prongs
    curve = lambda f: Vector(h_hull(f)) + HR_OUT * Vector(h_outline(f)).normalized()
    Msub = H_N * 20; cpts = [curve(H_N * i / Msub) for i in range(Msub + 1)]
    cum = [0.0]
    for i in range(1, len(cpts)): cum.append(cum[-1] + (cpts[i] - cpts[i - 1]).length)
    Lh = cum[-1]
    def f_at(s):
        s %= Lh; j = max(0, min(len(cum) - 2, next(k for k in range(len(cum) - 1) if cum[k + 1] >= s)))
        u = (s - cum[j]) / max(1e-9, cum[j + 1] - cum[j]); return H_N * (j + u) / Msub
    ps = [cum[int(i * 20)] for i in prong_idx]
    NP = len(prong_idx)
    segL = [(ps[(k + 1) % NP] - ps[k]) % Lh for k in range(NP)]
    counts = H_COUNTS if not H_WRAP else [11, 0]
    margin = 0.70 + 0.50 + 0.02
    hstones = []
    zrow = (HZT + HZB) / 2
    for k in range(NP):
        sa = ps[k]; L_ = segL[k]; n = counts[k]
        if n == 0: continue
        a_, b_ = sa + margin, sa + L_ - margin
        srow = []
        for j in range(n):
            s = (a_ + b_) / 2 if n == 1 else a_ + (b_ - a_) * j / (n - 1)
            f = f_at(s); q = curve(f); nn = (normal2(f) + Vector(h_outline(f)).normalized()).normalized()
            c = hl(*(q - 0.05 * nn), zrow); ax = (HM.to_3x3() @ Vector((nn.x, nn.y, 0))).normalized()
            srow.append(dict(D=1.4, center=c, axis=ax, f=f))
        hstones.append(srow)
    hpitch = [(segL[k] - 2 * margin) / max(1, counts[k] - 1) for k in range(NP)]
    log('heart seg lengths', [round(x, 2) for x in segL], 'pitch', [round(x, 2) for x in hpitch])
    for side in (1, -1):
        mir = (lambda v: Vector((-v.x, v.y, v.z))) if side < 0 else (lambda v: v)
        for srow in hstones:
            row = []
            for s in srow:
                row.append(add_round(1.4, mir(s['center']), mir(s['axis']), 'HeartRail', through=2.5, tangent=mir(e_n)))
            bead_row(row, ends=False)
        STONES.append(dict(kind='heart', D=6.0, M=(Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ HM) if side < 0 else HM.copy(),
                           center=mir(H_CENTER), axis=mir(e_n), target='GalleryRail'))
        # the heart's lobes nest against the gallery rail: notch the rail with a slightly enlarged heart
        CUTTERS.setdefault('GalleryRail', MB()).extend(heart_stone().xform(STONES[-1]['M'] @ Matrix.Scale(1.04, 4)))
    for k, mb in hmetal.items():
        metal[k] = MB().extend(mb).extend(mb.mirror_x())
    metal['ShankClaws'] = CLAWS
    low = {}

    # ---------------- objects ---------------------------------------------
    objs = {}
    for k, mb in metal.items():
        objs[k] = to_obj(k, mb, GOLD, smooth=True)
    beads = to_obj('PaveBeads', BEADS, GOLD, smooth=True, sharp_deg=80)
    # booleans: seats
    for tgt, cmb in CUTTERS.items():
        cut = to_obj('cut_' + tgt, cmb, GOLD)
        mod = objs[tgt].modifiers.new('seats', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'
        mod.object = cut; mod.use_self = True; mod.use_hole_tolerant = True
        bpy.context.view_layer.objects.active = objs[tgt]
        t = time.time(); v0 = mesh_volume(objs[tgt])
        if '--nobool' in argv: objs[tgt].modifiers.remove(mod)
        else: bpy.ops.object.modifier_apply(modifier=mod.name)
        log('vol before/after', tgt, round(v0, 2), round(mesh_volume(objs[tgt]), 2))
        bpy.data.objects.remove(cut, do_unlink=True)
        log('boolean', tgt, 'faces', len(objs[tgt].data.polygons), '%.1fs' % (time.time() - t))
        objs[tgt].data.shade_smooth(); objs[tgt].data.set_sharp_from_angle(angle=radians(40))
    # stones: one mesh per family (joined) to keep the scene light
    fam = {}
    for s in STONES:
        if s['kind'] == 'round':
            fam.setdefault('Diamonds_%.1fmm' % s['D'], MB()).extend(STONE_MB[s['D']][0].xform(s['M']))
        elif s['kind'] == 'heart':
            fam.setdefault('Diamonds_Heart', MB()).extend(heart_stone().xform(s['M']))
    for k, mb in fam.items(): to_obj(k, mb, DIA)
    center = oval_brilliant().xform(Matrix.Translation((0, 0, Z_GM)))
    to_obj('Diamond_Center_Oval', center, DIA)
    counts = {}
    for s in STONES: counts['%s %.1f' % (s['kind'], s['D'])] = counts.get('%s %.1f' % (s['kind'], s['D']), 0) + 1
    log('stone counts', counts)
    return GOLD, DIA, counts, dict(gallery=gal, heart_pitch=hpitch)

def collision_report():
    from mathutils.bvhtree import BVHTree
    tr = lambda mb: BVHTree.FromPolygons([Vector(v) for v in mb.v], mb.f, epsilon=0.0)
    items = []
    for s in STONES:
        mb = STONE_MB[s['D']][0].xform(s['M']) if s['kind'] == 'round' else heart_stone().xform(s['M'])
        items.append(('r%.1f' % s['D'] if s['kind'] == 'round' else 'heart', s, tr(mb)))
    items.append(('center', dict(center=Vector((0, 0, Z_GM)), D=19.4), tr(oval_brilliant().xform(Matrix.Translation((0, 0, Z_GM))))))
    ss = {}
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if (a[1]['center'] - b[1]['center']).length > (a[1]['D'] + b[1]['D']) / 2 + 0.6: continue
            if a[2].overlap(b[2]):
                k = '/'.join(sorted((a[0], b[0]))); ss[k] = ss.get(k, 0) + 1
                if '--verbose' in argv: log('  ss', a[0], tuple(round(x, 2) for x in a[1]['center']), b[0], tuple(round(x, 2) for x in b[1]['center']))
    sm = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for o in metal_objects():
        if o.name in ('PaveBeads', 'ShankClaws', 'CenterProngs', 'HeartProngs'): continue
        t = BVHTree.FromObject(o, dg)
        for (name, s, st) in items:
            if s.get('target') == o.name or (o.name == 'HeartRail' and s.get('target') == 'GalleryRail'): continue
            if st.overlap(t):
                k = name + '>' + o.name; sm[k] = sm.get(k, 0) + 1
                if '--verbose' in argv: log('  sm', name, tuple(round(x, 2) for x in s['center']), o.name)
    log('COLLISIONS stone-stone', json.dumps(ss)); log('COLLISIONS stone-metal', json.dumps(sm))
    return ss, sm

# --------------------------------------------------------------------------- measurement
def metal_objects():
    return [o for o in COLL.objects if o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('WhiteGold')]

def mesh_volume(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); v = bm.calc_volume(signed=True); bm.free(); return abs(v)

def union_metal(voxel=0.05):
    bm = bmesh.new()
    for o in metal_objects():
        tmp = o.data.copy(); tmp.transform(o.matrix_world); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new('MetalUnion'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('MetalUnion', me); bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new('vox', 'REMESH'); mod.mode = 'VOXEL'; mod.voxel_size = voxel; mod.adaptivity = 0.0
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='vox')
    return ob

def inner_diameter():
    me = bpy.data.objects['Shank'].data
    rs = [sqrt(v.co.x ** 2 + v.co.z ** 2) for v in me.vertices]
    return 2 * min(rs)

# --------------------------------------------------------------------------- scene
def scene_setup():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; cy = sc.cycles
    cy.device = 'CPU'; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.015
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    cy.max_bounces = 32; cy.transmission_bounces = 24; cy.glossy_bounces = 16; cy.diffuse_bounces = 4; cy.transparent_max_bounces = 8
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.sample_clamp_indirect = 20
    sc.render.threads_mode = 'FIXED'; sc.render.threads = 8
    sc.render.resolution_x = sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0.25
    w = bpy.data.worlds.new('Studio'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); mix = nt.nodes.new('ShaderNodeMixShader'); lp = nt.nodes.new('ShaderNodeLightPath')
    bg_env = nt.nodes.new('ShaderNodeBackground'); bg_cam = nt.nodes.new('ShaderNodeBackground')
    hdr = os.path.join(OUT, 'studio.hdr')
    if os.path.exists(hdr):
        env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(hdr)
        mapn = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Generated'], mapn.inputs['Vector']); mapn.inputs['Rotation'].default_value[2] = radians(30)
        nt.links.new(mapn.outputs['Vector'], env.inputs['Vector'])
        nt.links.new(env.outputs['Color'], bg_env.inputs['Color']); bg_env.inputs['Strength'].default_value = 1.6
    else:
        grad = nt.nodes.new('ShaderNodeTexGradient'); nt.links.new(grad.outputs['Color'], bg_env.inputs['Color'])
    bg_cam.inputs['Color'].default_value = (0.17, 0.17, 0.17, 1); bg_cam.inputs['Strength'].default_value = 1.0
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    nt.links.new(bg_env.outputs['Background'], mix.inputs[1]); nt.links.new(bg_cam.outputs['Background'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    # soft key light from above-front for diamond sparkle (power tuned for mm scale scene)
    L = bpy.data.lights.new('Softbox', 'AREA'); L.shape = 'RECTANGLE'; L.size = 60; L.size_y = 30; L.energy = 6.0e4
    lo = bpy.data.objects.new('Softbox', L); sc.collection.objects.link(lo)
    lo.matrix_world = frame(Vector((0, -40, 90)), Vector((0, -40, 90)).normalized().__neg__().__neg__(), Vector((1, 0, 0)))
    # area light points along its local -Z; frame() put +Z away from origin => fine
    lo.visible_camera = False; lo.visible_glossy = True

def bbox_world():
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in COLL.objects:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx

VIEW_DIRS = {
    'top': (Vector((0, 0, 1)), Vector((0, 1, 0))),
    'front': (Vector((0, -1, 0)), Vector((0, 0, 1))),
    'side': (Vector((1, 0, 0)), Vector((0, 0, 1))),
    'three_quarter': (Vector((0.20, -0.22, 0.955)), Vector((0, 0, 1))),
}
def make_camera(view):
    d, up = VIEW_DIRS[view]; d = d.normalized()
    cam = bpy.data.cameras.new('Cam_' + view); cam.type = 'ORTHO'; cam.clip_start = 1; cam.clip_end = 2000
    ob = bpy.data.objects.new('Cam_' + view, cam); bpy.context.scene.collection.objects.link(ob)
    mn, mx = bbox_world(); ctr = (mn + mx) / 2
    x = up.cross(d).normalized(); y = d.cross(x)
    ext = 0
    for i in range(8):
        c = Vector((mn.x if i & 1 else mx.x, mn.y if i & 2 else mx.y, mn.z if i & 4 else mx.z)) - ctr
        ext = max(ext, abs(c.dot(x)), abs(c.dot(y)))
    cam.ortho_scale = 2 * ext * 1.08
    M = Matrix.Identity(4); pos = ctr + d * 200
    for i in range(3): M[i][0], M[i][1], M[i][2], M[i][3] = x[i], y[i], d[i], pos[i]
    ob.matrix_world = M
    return ob

# --------------------------------------------------------------------------- main
def main():
    GOLD, DIA, counts, rowinfo = build()
    collision_report()
    if '--checkonly' in argv: return
    scene_setup()
    cams = {v: make_camera(v) for v in VIEW_DIRS}
    bpy.context.scene.camera = cams['three_quarter']
    idia = inner_diameter()
    parts = {o.name: round(mesh_volume(o), 2) for o in metal_objects()}
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'ring.blend'))
    log('saved blend')
    # ---- union metal -> STL + volume
    un = union_metal(0.05)
    vol = mesh_volume(un)
    nf = len(un.data.polygons)
    dec = un.modifiers.new('dec', 'DECIMATE'); dec.ratio = min(1.0, 400000 / max(1, nf))
    bpy.context.view_layer.objects.active = un; bpy.ops.object.modifier_apply(modifier='dec')
    for o in bpy.context.scene.objects: o.select_set(False)
    un.select_set(True); bpy.context.view_layer.objects.active = un
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, 'ring.stl'), export_selected_objects=True, global_scale=1.0, use_scene_unit=False, apply_modifiers=True)
    stl_faces = len(un.data.polygons)
    bpy.data.objects.remove(un, do_unlink=True)
    stats = dict(inner_diameter_mm=round(idia, 3), metal_volume_union_mm3=round(vol, 1), metal_volume_sum_parts_mm3=round(sum(parts.values()), 1),
                 parts_mm3=parts, est_weight_g_18kw_14_7=round(vol * 14.7 / 1000, 2), stl_faces=stl_faces, stone_counts=counts,
                 rows=rowinfo, center=dict(L=C_L, W=C_W, D=C_D, crown=C_HC, pavilion=C_HP, girdle=C_G, table_mm=0.6 * C_W))
    # ---- GLB (meters, true scale)
    root = bpy.data.objects.new('RingRoot', None); bpy.context.scene.collection.objects.link(root)
    for o in COLL.objects: o.parent = root
    root.scale = (0.001, 0.001, 0.001)
    for o in bpy.context.scene.objects: o.select_set(o.name in COLL.objects or o == root)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'ring.glb'), export_format='GLB', use_selection=True, export_apply=True,
                              export_cameras=False, export_lights=False, export_yup=True)
    stats['glb_MB'] = round(os.path.getsize(os.path.join(OUT, 'ring.glb')) / 1e6, 2)
    stats['tris'] = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in COLL.objects)
    json.dump(stats, open(os.path.join(OUT, 'stats.json'), 'w'), indent=1)
    log(json.dumps(stats, indent=1))
    if DO_RENDER:
        bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'ring.blend'))
        sc = bpy.context.scene
        sc.render.resolution_x = sc.render.resolution_y = RES; sc.cycles.samples = SAMPLES
        FL = bpy.data.lights.new('Fill', 'AREA'); FL.size = 90; FL.energy = float(arg('--fill', 6e4))
        flo = bpy.data.objects.new('Fill', FL); sc.collection.objects.link(flo); flo.visible_camera = False
        for v in VIEWS:
            sc.camera = bpy.data.objects['Cam_' + v]
            cm = sc.camera.matrix_world; cpos = cm.translation; cz = Vector((cm[0][2], cm[1][2], cm[2][2]))
            up_ = Vector((0, 0, 1)) if abs(cz.z) < 0.9 else Vector((0, 1, 0))
            flo.matrix_world = frame(cpos + up_ * 60, (cpos + up_ * 60).normalized(), Vector((1, 0, 0)))
            sc.render.filepath = os.path.join(OUT, 'render_%s.png' % v)
            t = time.time(); bpy.ops.render.render(write_still=True); log('rendered', v, '%.0fs' % (time.time() - t))

if "--nobuild" not in argv: main()

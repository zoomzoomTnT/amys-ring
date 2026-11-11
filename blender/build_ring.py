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
# v1.0 round 8 settings (thick half-round U rims with rounded tulip peaks, elliptical U-seats, sideways 3.0 mm stones, flush pave beads, softened metal). Command-line values win (first match).
TUNED = ('--tilt3 0 --yoff3 0 --sht 2.92 --lift3 -0.57 --u3c 0.57 --u3r 1.45 --u3b 1.0 --u3f 0 --claw3 0 --scr 0 --scl 0.4 '
         '--rimr 0.3 --rimrb 0.2 --rimh 0.2 --rimseg 10 --bzseg 8 --segseat 12 '
         '--cove3 0.2 --ro 0.5 --ri 0.45 --gd 0.55 --htilt 60 --legsink -0.6 --shtb 2.5 --bezel 0.05 --bezelz 0.0 --envfloor 0.02 --shm 176 --hairpin 1 --sri 0.66 --sro 1.02 --rimin 0.75 --hpst 0.42 --hpsb 0.52 --hprt 10.8').split()
argv = argv + TUNED
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
H_TILT = radians(float(arg('--htilt', 53)))         # lobe->point axis 50 deg from horizontal: lobes up/in at the gallery, point down/out, table faces up-outward
H_LOBE_XW, H_LOBE_ZW = float(arg('--hlx', 7.4)), float(arg('--hlz', 14.4))   # world X/Z of the heart's lobe end (top of the arm, at the rail end)
H_WALL_PITCH = 1.5
H_Y0, H_Y1 = float(arg('--hy0', -3.3)), float(arg('--hy1', 3.0))
H_WALL_SHIFT = float(arg('--wshift', -0.7))
LEG_DEG = float(arg('--legdeg', 46))
LEG_DY = float(arg('--legdy', -0.4)); LEG_R = float(arg('--legr', 0.42))
LEG_SINK = float(arg('--legsink', -0.8))
H_COUNTS = [4, 4, 3]
H_WRAP = '--nowrap' not in argv
H_LOBE_T = float(arg('--lobet', 0.95))   # heart outline parameter of the two lobe prongs
POST_B = int(arg('--postb', 2))
TIES = '--ties' in argv
POST_Y = float(arg('--posty', -1.8))
TIE_X, TIE_Y = float(arg('--tiex', 1.6)), float(arg('--tiey', 1.6))           # shank claw boundary the heart-point post lands on (2 = ~42 deg)          # 1.4 mm frame stones per heart: side, side, over the lobes
# shank
SH_T0, SH_T, SH_TB = 2.25, float(arg('--sht', 2.75)), float(arg('--shtb', 1.7))   # radial thickness (top centre, shoulders/sides, bottom)
SH_W, SH_WB = float(arg('--shw', 1.85)), 1.55      # half width (along the finger)
STONE3_START = radians(float(arg('--s3start', 20)))  # first 3.0 mm stone, 7 per side
SH_RO = float(arg('--ro', 0.3))
SH_RI = float(arg('--ri', 0.30))
RAIL_RF = float(arg('--railrf', 0.35)); SOFT_RR = float(arg('--softrr', 0.40)); SOFT_BEVEL = float(arg('--bevel', 0.07)); SOFT_SHARP = float(arg('--sharp', 60))
TB_START = float(arg('--tbstart', 125))
GROOVE_W = float(arg('--gw', 1.0)); GROOVE_D = float(arg('--gd', 0.78))
PITCH3 = float(arg('--pitch3', 3.4))
SCALLOP = int(arg('--scallop', 1)); SC_R = float(arg('--scr', 0.6)); SC_L = float(arg('--scl', 1.1)); SC_H = float(arg('--sch', 0.0)); SC_FY = float(arg('--scfy', 1.15)); SC_SYM = int(arg('--scsym', 1))
STONE3_LIFT = float(arg('--lift3', -0.2))
STONE3_TILT = radians(float(arg('--tilt3', 40)))   # 3.0 mm tables tilted toward the front face so they read from the front
CLAW_EXT = float(arg('--clawext', 0.45))
STONE3_YOFF = float(arg('--yoff3', -0.4))   # 3.0 mm girdles sit proud of the metal, held by the claws
TOOTH_L = float(arg('--tooth', 1.4))
TOOTH_IN = float(arg('--toothin', 0.3))
TOOTH_Y = float(arg('--toothy', 0.0))
TOOTH_R = float(arg('--toothr', 0.5))
CLAW3 = int(arg('--claw3', 1)); CL_Y = float(arg('--cly', 1.05)); CL_FOOT = float(arg('--clfoot', 1.1)); CL_TIP = float(arg('--cltip', 1.05))
CL_IN = float(arg('--clin', 0.2)); CL_R0 = float(arg('--clr0', 0.34)); CL_R1 = float(arg('--clr1', 0.17))
THRU3 = int(arg('--thru3', 0)); WNORM = int(arg('--wnorm', 1)); LIFT3_FIRST = float(arg('--lift3first', 0.0)); U3_R = float(arg('--u3r', 1.45)); U3_C = float(arg('--u3c', 0.6)); U3_F = float(arg('--u3f', 0.35)); U3_STACK = int(arg('--u3stack', 1)); RIM_R = float(arg('--rimr', 0.0)); RIM_RB = float(arg('--rimrb', 0.24)); U3_B = float(arg('--u3b', 0.0)); RIM_H = float(arg('--rimh', 0.12)); RIM_IN = float(arg('--rimin', 1.0)); RIM_SEG = int(arg('--rimseg', 12))
HAIRPIN = int(arg('--hairpin', 0))   # round 8: U-prong posts (hairpins) phase-locked to the zigzag: 1.3 at each post, 1.0 under each 3.0 stone
HP_RC = float(arg('--hprc', 9.62)); HP_RHO = float(arg('--hprho', 1.03)); HP_SB = float(arg('--hpsb', 0.46)); HP_ST = float(arg('--hpst', 0.32)); HP_RT = float(arg('--hprt', 10.85))
HP_GR = float(arg('--hpgr', 0.17)); HP_G0 = float(arg('--hpg0', 10.02)); HP_RB = float(arg('--hprb', 0.28)); HP_SUB = int(arg('--hpsub', 2))
ENV_FLOOR = float(arg('--envfloor', 0.30)); ENV_STR = float(arg('--envstr', 1.8))
SIDE_SPAN = radians(130)      # 1.0 mm side-wall rows run +/-130 deg over the top
SIDE_R = 0.95                 # their centre, measured out from the inner surface
# gallery rail + arms
RAIL_ZT, RAIL_ZB, RAIL_IN = 14.50, 13.00, float(arg('--railin', -0.25))
RAIL_DEPTH = float(arg('--raild', 1.0))
ARM_S, ARM_ZT = float(arg('--arms', 1.0)), 12.85
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

def seat_cutter(info, M, through=None, hole_frac=0.45, cove=0.0, cove_z=0.0):
    Rg = info['D'] / 2; g = info['g']; hp = info['hp']
    hr = Rg * hole_frac
    # bore = girdle diameter + 0.02 mm; seat cone slightly narrower than the pavilion so the stone rests on it
    if cove > 0:
        # rounded cove: the metal rolls smoothly into the seat (scalloped cup edge instead of a sharp drilled hole)
        prof = [(0, 3.0), (Rg + 0.01 + cove, 3.0)]
        for i in range(9):
            a = radians(90 + 90 * i / 8); prof.append((Rg + 0.01 + cove + cove * cos(a), cove_z + cove * sin(a)))
        prof += [(Rg + 0.01, -g / 2), (Rg * 0.96, -g / 2 - 0.01), (hr, -g / 2 - hp * (1 - hr / Rg))]
    else:
        prof = [(0, 3.0), (Rg + 0.01, 3.0), (Rg + 0.01, -g / 2), (Rg * 0.96, -g / 2 - 0.01), (hr, -g / 2 - hp * (1 - hr / Rg))]
    if through: prof += [(hr, -through), (0, -through)]
    else: prof += [(0, -g / 2 - hp - 0.1)]
    return revolve(prof, M, seg=SEG_SEAT)

def revolve_loop(loop, M, seg=24):
    """closed (r, h) loop revolved around local z -> closed ring solid"""
    mb = MB(); rows = [[mb.vert((r * cos(2 * pi * k / seg), r * sin(2 * pi * k / seg), h)) for k in range(seg)] for (r, h) in loop]
    n = len(rows)
    for i in range(n):
        A, B = rows[i], rows[(i + 1) % n]
        for k in range(seg): mb.face(A[k], B[k], B[(k + 1) % seg], A[(k + 1) % seg])
    return mb.xform(M)

def bezel_row(row, closed=False, z=None):
    z = BEZEL_Z if z is None else z
    """smooth rounded bezel rim (half-torus lip) around every stone: the soft cup the stone sits in"""
    for i, st in enumerate(row):
        D = st['D']; Rg = D / 2
        gap = 9.0
        for j, o in enumerate(row):
            if j != i: gap = min(gap, (o['center'] - st['center']).length - D / 2 - o['D'] / 2)
        for o in STONES:
            if o is not st and o['kind'] == 'round' and (o['center'] - st['center']).length < D + o['D']:
                gap = min(gap, (o['center'] - st['center']).length - D / 2 - o['D'] / 2)
        rm = max(0.06, min(BEZEL_RM, gap - 0.05))
        loop = [(Rg + 0.02 + rm * cos(2 * pi * k / BZ_K), z + rm * sin(2 * pi * k / BZ_K)) for k in range(BZ_K)]
        BEZELS.extend(revolve_loop(loop, st['M'], seg=BZ_SEG))

def cup_for(st, t=None):
    """rounded scallop cup under a big stone's girdle (follows the pavilion, rolled rim)"""
    info = STONE_MB[st['D']][1]; Rg = st['D'] / 2; g = info['g']; hp = info['hp']
    t = t or CUP_T
    pav = lambda z: Rg * (1 - (-g / 2 - z) / hp)
    z0 = -g / 2 - CUP_DROP; z1 = -g / 2 - hp * 0.68
    loop = []
    for i in range(9):   # rolled rim, inner -> outer over the top
        a = radians(180 - 180 * i / 8); rr = t / 2
        loop.append((pav(z0) + 0.08 + rr * Rg / hp + rr + rr * cos(a), z0 + rr * sin(a)))   # rim clears the shallow pavilion
    loop += [(pav(z1) + 0.08 + t + rr * Rg / hp, z1), (pav(z1) + 0.08, z1)]
    return revolve_loop(loop, st['M'], seg=CUP_SEG)


# --------------------------------------------------------------------------- stones registry
STONES = []          # dicts: kind, D, M (matrix)
BEADS = MB(); CLAWS = MB(); RIMS = MB(); RIM_JOBS = []; CUTTERS = {}
STONE_MB = {}
BEZELS = MB(); CUPS = MB(); BEZEL_ROWS = []
CUP_SEG = int(arg('--cupseg', 24)); SEG_SEAT = int(arg('--segseat', 16)); BZ_SEG = int(arg('--bzseg', 12)); BZ_K = int(arg('--bzk', 6))
ZZ_BIG = float(arg('--zzbig', 1.3))
RAIL_D = float(arg('--raild_stone', 1.0))
BEZEL_RM = float(arg('--bezel', 0.12)); BEZEL_Z = float(arg('--bezelz', 0.05))
CUP_T = float(arg('--cupt', 0))
CUP_DROP = float(arg('--cupdrop', 0.22))
COVE3 = float(arg('--cove3', 0.30))
SIDE_R_IN, SIDE_R_OUT = float(arg('--sri', 0.55)), float(arg('--sro', 0.98))
def add_round(D, center, axis, target, through=None, tangent=None, hole_frac=0.45, cove=0.0, cove_z=0.0):
    M = frame(Vector(center), Vector(axis), Vector(tangent) if tangent else Vector((1, 0, 0)))
    STONES.append(dict(kind='round', D=D, M=M, center=Vector(center), axis=Vector(axis).normalized(), target=target))
    if D not in STONE_MB: STONE_MB[D] = round_brilliant(D)
    if target:
        CUTTERS.setdefault(target, MB()).extend(seat_cutter(STONE_MB[D][1], M, through, hole_frac, cove, cove_z))
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
    b.inputs['Base Color'].default_value = (0.91, 0.91, 0.90, 1)
    b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = float(arg('--rough', 0.12))
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

def claw_row(row, rb=0.40, ext=0.75, base=0.55, off_min=0.0, store=None, tooth=0.0):
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
        if tooth > 0:
            # flat radial 'tooth' between the stones, reading as a spike from the front
            rxz = Vector((m.x, 0, m.z)).normalized()
            g = m + ax * (info['g'] / 2) + Vector((0, TOOTH_Y, 0))
            r0 = Vector((g.x, 0, g.z)).length
            A = g - rxz * TOOTH_IN; B = g + rxz * tooth
            store.extend(tube([A, (A + B) / 2, B], [TOOTH_R, TOOTH_R, TOOTH_R * 0.85], seg=12, tip=True))
    return tips

def scallop_row(row, store=None):
    """Shared rounded beads between neighbouring big stones: a short broad capsule lying across the band
    (front to back) at girdle height, on a wide rounded foot that flows into the band. No radial spikes."""
    D = row[0]['D']; info = STONE_MB[D][1]
    store = store if store is not None else CLAWS
    pairs = []
    for i in range(len(row) - 1): pairs.append((row[i]['center'], row[i + 1]['center'], row[i]['axis'] + row[i + 1]['axis']))
    c0, c1 = row[0]['center'], row[1]['center']; pairs.insert(0, (c0 * 2 - c1, c0, row[0]['axis'] * 2))
    c0, c1 = row[-1]['center'], row[-2]['center']; pairs.append((c0, c0 * 2 - c1, row[-1]['axis'] * 2))
    tips = []
    for (p, q, ax) in pairs:
        ax = ax.normalized(); m = (p + q) / 2; tg = (q - p).normalized()
        v = ax.cross(tg).normalized()
        top = m + ax * (info['g'] / 2 + SC_H)
        A = top - v * SC_L; B = top + v * SC_L
        if CLAW3:
            # tulip claws (reference front view): a thin tapered claw at each band edge between neighbouring 3.0 stones,
            # rising out of the band wall on a flared foot and curling slightly over the two girdles
            rxz = Vector((m.x, 0, m.z)).normalized()
            for ys in (-1, 1):
                ey = Vector((0, ys, 0))
                base = m + ey * CL_Y
                P = [base - rxz * CL_FOOT, base - rxz * (CL_FOOT * 0.45), base + rxz * (info['g'] / 2),
                     base + rxz * CL_TIP - ey * CL_IN]
                store.extend(tube(P, [CL_R0 * 1.6, CL_R0, CL_R1 * 1.15, CL_R1], seg=12, tip=True))
        elif SC_R > 0:
            # U-shaped prong: broad flared foot rising out of the band, tapering to a soft rounded tip between the two stones
            rxz = Vector((m.x, 0, m.z)).normalized()
            for fy_ in ((-SC_FY, SC_FY) if SC_SYM else (SC_FY,)):
                # U-shaped shared prong: broad flared foot rising out of the band, tapering to a soft rounded tip
                base = top + Vector((0, fy_, 0))
                store.extend(tube([base - rxz * 1.0, base - rxz * 0.45, base, base + rxz * SC_L],
                                  [SC_R * 1.9, SC_R * 1.45, SC_R * 1.05, SC_R * 0.85], seg=14, tip=True))
        tips.extend([A, B])
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
        return SH_T0 + (SH_T - SH_T0) * smooth(radians(4), radians(28), p) + (SH_TB - SH_T) * smooth(radians(TB_START), pi, p)
    def half_w(phi):
        return SH_W + (SH_WB - SH_W) * smooth(radians(122), pi, abs(phi))
    def profile(t, w, n=5):
        ro, ri = SH_RO, SH_RI; pts = []
        corners = [((R_IN + t - ro, w - ro), ro, 0), ((R_IN + ri, w - ri), ri, 90), ((R_IN + ri, -w + ri), ri, 180), ((R_IN + t - ro, -w + ro), ro, 270)]
        for ci, (c, r, a0) in enumerate(corners):
            for k in range(n):
                a = radians(a0 + 90 * k / (n - 1)); pts.append((c[0] + r * cos(a), c[1] + r * sin(a)))
            if ci == 1:
                # comfort / lightening channel in the inner bore (the finger still bears on both inner rims, so size is unchanged)
                gw = min(GROOVE_W, w - ri - 0.25); gd = GROOVE_D
                for (yy, dd) in ((gw, 0.0), (gw - 0.18, gd * 0.75), (gw - 0.45, gd), (-gw + 0.45, gd), (-gw + 0.18, gd * 0.75), (-gw, 0.0)):
                    pts.append((R_IN + dd, yy))
        return pts
    secs = []; M = int(arg('--shm', 360))
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
            rad = Vector((sin(ph), 0, cos(ph)))
            ax = (rad * cos(STONE3_TILT) - Vector((0, 1, 0)) * sin(STONE3_TILT)).normalized()
            row.append(add_round(3.0, rad * (r_out(ph) + STONE3_LIFT + (LIFT3_FIRST if k == 0 else 0.0)) + Vector((0, STONE3_YOFF, 0)), ax, 'Shank', through=(3.0 if THRU3 else None), tangent=Vector((0, 1, 0)), cove=COVE3, cove_z=-0.05))
            if CUP_T > 0: CUPS.extend(cup_for(row[-1]))
            if U3_R > 0 and not HAIRPIN:
                # tulip scallop: a round notch through the whole band width under each 3.0 stone, so from the front the wall
                # top dips in a smooth U under every stone and rises to a peak (the claw foot) between neighbours
                if U3_B > 0:
                  # elliptical U (U3_R across, U3_B deep): matches the thick rounded rim laid along its edge
                  cc = row[-1]['center'] + rad * U3_C; hw = SH_W + 0.6
                  tgk = Vector((0, 1, 0)).cross(rad).normalized(); sb = rad * (U3_B / U3_R)
                  Mn = Matrix(((tgk.x, 0, sb.x, cc.x), (tgk.y, 1, sb.y, cc.y), (tgk.z, 0, sb.z, cc.z), (0, 0, 0, 1)))
                  CUTTERS.setdefault('Shank', MB()).extend(tube([Vector((0, -hw, 0)), Vector((0, 0, 0)), Vector((0, hw, 0))], [U3_R] * 3, seg=40, smooth=False, tip=False).xform(Mn))
                for so in ((0.0, 0.45, 0.9)[:U3_STACK] if U3_B <= 0 else ()):   # stacked notches -> straight U sides above the round bottom
                  cc = row[-1]['center'] + rad * (U3_C + so); hw = SH_W + 0.6
                  ey = Vector((0, 1, 0)); hf = SH_W - U3_F   # flare starts U3_F inside each band face -> rolled, bright U lip
                  CUTTERS.setdefault('Shank', MB()).extend(tube(
                    [cc - ey * hw, cc - ey * (SH_W + 0.05), cc - ey * (hf + U3_F * 0.5), cc - ey * hf, cc, cc + ey * hf, cc + ey * (hf + U3_F * 0.5), cc + ey * (SH_W + 0.05), cc + ey * hw],
                    [U3_R + U3_F * 1.3, U3_R + U3_F, U3_R + U3_F * 0.3, U3_R, U3_R, U3_R, U3_R + U3_F * 0.3, U3_R + U3_F, U3_R + U3_F * 1.3], seg=32, smooth=False, tip=False))
        def make_rims(row=row, side=side):
            if HAIRPIN: return make_hairpins(row, side)
            if RIM_R > 0 and U3_R > 0:
                # thick half-round rim (a rounded wire ~2*RIM_R thick) running along the U edge on both band faces:
                # a continuous U under every 3.0 stone, arching over the wall top between neighbours as a blunt rounded tulip peak
                Rp = U3_R
                for ys in (-1, 1):
                    path = []; rads = []
                    def frame_k(k):
                        st = row[k]; c = st['center']; radk = Vector((c.x, 0, c.z)).normalized()
                        tg = Vector((0, 1, 0)).cross(radk).normalized() * side
                        yv = Vector((0, ys * (half_w(atan2(c.x, c.z)) - RIM_R * RIM_IN), 0))
                        cc = Vector((c.x, 0, c.z)) + radk * U3_C + yv
                        return cc, radk, tg
                    for k in range(len(row)):
                        cc, radk, tg = frame_k(k)
                        Bd = U3_B if U3_B > 0 else Rp
                        ts = [pi + pi * i / 16 for i in range(17)]
                        U = [cc + Rp * cos(t) * tg + Bd * sin(t) * radk for t in ts]
                        UR = [RIM_R - (RIM_R - RIM_RB) * (-sin(t)) for t in ts]
                        if k == 0:
                            path += [U[0] + radk * (RIM_H + 0.2) * 1.2, U[0] + radk * (RIM_H + 0.2) * 0.5]; rads += [RIM_R, RIM_R]
                        path += U; rads += UR
                        if k < len(row) - 1:
                            cn, rn, tn = frame_k(k + 1); B = cn + Rp * (-tn)
                            A = U[-1]; hh = RIM_H
                            mid = (A + B) / 2
                            if any(o.get('target') != 'Shank' and (o['center'] - mid).length < 1.6 for o in STONES): hh = -0.45   # dip under the heart-arm cap stones
                            P1 = A + radk * hh * 1.33; P2 = B + rn * hh * 1.33
                            for i in range(1, 8):
                                u = i / 8; path.append(A * (1 - u) ** 3 + P1 * 3 * u * (1 - u) ** 2 + P2 * 3 * u * u * (1 - u) + B * u ** 3); rads.append(RIM_R)
                        else:
                            path += [U[-1] + radk * (RIM_H + 0.2) * 0.5, U[-1] + radk * (RIM_H + 0.2) * 1.2]; rads += [RIM_R, RIM_R]
                    # thin the rim locally (smoothly) where a heart-arm cap stone sits right above it
                    caps = [o for o in STONES if o.get('target') != 'Shank']
                    for _ in range(2):
                        for ii, pp in enumerate(path):
                            for o in caps:
                                d = (pp - o['center']).length
                                lim = d - o['D'] / 2 - 0.05
                                if lim < rads[ii]: rads[ii] = max(0.1, lim)
                                if lim < 0.1:   # still too close: push the rim point inward (toward the finger)
                                    rr_ = Vector((pp.x, 0, pp.z)).normalized(); path[ii] = pp - rr_ * (0.15 - lim)
                        rads = [min(rads[ii], (rads[max(ii - 1, 0)] + rads[ii] + rads[min(ii + 1, len(rads) - 1)]) / 3 + 0.04) for ii in range(len(rads))]
                    if '--verbose' in argv:
                        for o in STONES:
                            if o.get('target') != 'Shank':
                                dmin = min(range(len(path)), key=lambda i: (path[i] - o['center']).length)
                                if (path[dmin] - o['center']).length < 1.3: log('rimnear', o['D'], o.get('target'), tuple(round(x, 2) for x in o['center']), dmin, len(path), round((path[dmin] - o['center']).length, 2), tuple(round(x, 2) for x in path[dmin]))
                    RIMS.extend(tube(path, rads, seg=RIM_SEG, smooth=False, tip=True))
        RIM_JOBS.append(make_rims)
        tips = scallop_row(row) if SCALLOP else claw_row(row, rb=0.44, ext=CLAW_EXT, base=0.9, off_min=1.10, tooth=TOOTH_L)
        tooth_tips[side] = [(tips[2 * i], tips[2 * i + 1]) for i in range(len(tips) // 2)]   # per boundary: (y-, y+)
    def make_hairpins(row, side):
        # Reference front view: between neighbouring 3.0 stones each band face carries a U-shaped prong (a hairpin of
        # thick half-round wire with a dark slot in it) whose open bottom cradles a 1.3 zigzag stone; the cup of every
        # 3.0 stone dips between two of them and hugs the 1.0 stone that sits right under the 3.0 stone.
        phs = [abs(atan2(st['center'].x, st['center'].z)) for st in row]
        D_ = phs[1] - phs[0]
        posts = [phs[0] + (j - 0.5) * D_ for j in range(len(row) + 1)]
        rbg = R_IN + SIDE_R_OUT
        a0 = math.acos(max(-1, min(1, (HP_RC - rbg) / HP_RHO)))
        def post_pts(j, first=False, last=False):
            out = []
            asc = [(-HP_RHO * sin(a), rbg + HP_RHO * cos(a)) for a in (a0, (a0 + radians(27)) / 2, radians(27))]
            asc += [(-(HP_SB * 0.62 + HP_ST * 0.38), (rbg + HP_RHO * cos(radians(27))) * 0.55 + HP_RT * 0.45), (-HP_ST, HP_RT)]
            tip = [(-HP_ST * cos(radians(a)), HP_RT + HP_ST * sin(radians(a))) for a in (40, 90)]
            half = asc + tip
            pts_ = half + [(-t, r) for (t, r) in reversed(half[:-1])]
            if first: pts_ = pts_[len(asc) - 1:]          # top-end post: only the strand that runs down into the first cup
            if last: pts_ = pts_[:len(pts_) - len(asc) + 1]
            return [(posts[j] + t / r, r) for (t, r) in pts_]
        def cup_pts(k):
            return [(phs[k] + t / HP_RC, HP_RC + 0.03 * abs(t) / 0.6) for t in (-0.6, -0.3, 0.0, 0.3, 0.6)]
        seq = []
        for j in range(len(row) + 1):
            seq.append(('p', j, post_pts(j, first=(j == 0), last=(j == len(row)))))
            if j < len(row): seq.append(('c', j, cup_pts(j)))
        ctrl = [pr for (_, _, L) in seq for pr in L]
        P2 = lambda ph, r: (r * sin(ph), r * cos(ph))
        # notch cutter for each 3.0 stone: the region outside its U (between the two post apexes), through the band width
        dense, _ = catmull([Vector((x, 0, z)) for (x, z) in (P2(ph, r) for (ph, r) in ctrl)], [0] * len(ctrl), sub=int(arg('--hpcsub', 1)))
        dpol = [(atan2(v.x, v.z), v.length) for v in dense]
        hw = SH_W + 0.6
        poly = list(dpol)
        f0, f1 = poly[0][0], poly[-1][0]
        far = [(f1 + (f0 - f1) * i / 24, 13.5) for i in range(25)]
        poly = poly + far
        cmb = MB(); n = len(poly)
        A = [cmb.vert((side * r * sin(ph), -hw, r * cos(ph))) for (ph, r) in poly]
        B = [cmb.vert((side * r * sin(ph), hw, r * cos(ph))) for (ph, r) in poly]
        cmb.face(*A); cmb.face(*reversed(B))
        for i in range(n): cmb.face(A[i], A[(i + 1) % n], B[(i + 1) % n], B[i])
        CUTTERS.setdefault('Shank', MB()).extend(cmb)
        for ys in (-1, 1):
            def V(ph, r, inset=RIM_R * RIM_IN):
                return Vector((side * r * sin(ph), ys * (half_w(ph) - inset), r * cos(ph)))
            path = [V(ph, r) for (ph, r) in ctrl]
            rads = []
            for (kind, j, L) in seq:
                rads += ([HP_RB] * len(L)) if kind == 'c' else ([RIM_R] * len(L))
            # slot groove down the middle of every U-prong, ending in a round bottom just above its 1.3 stone
            for j in range(1, len(row)):
                g = [V(posts[j], r, 0.0) for r in (HP_G0, (HP_G0 + 11.8) / 2, 11.8)]
                CUTTERS.setdefault('Shank', MB()).extend(tube(g, [HP_GR] * 3, seg=8, smooth=False, tip=True))
            caps = [o for o in STONES if o.get('target') != 'Shank']
            for _ in range(2):
                for ii, pp in enumerate(path):
                    for o in caps:
                        d = (pp - o['center']).length
                        lim = d - o['D'] / 2 - 0.05
                        if lim < rads[ii]: rads[ii] = max(0.1, lim)
                        if lim < 0.1:
                            rr_ = Vector((pp.x, 0, pp.z)).normalized(); path[ii] = pp - rr_ * (0.15 - lim)
                rads = [min(rads[ii], (rads[max(ii - 1, 0)] + rads[ii] + rads[min(ii + 1, len(rads) - 1)]) / 3 + 0.04) for ii in range(len(rads))]
            dp, dr = catmull(path, rads, sub=HP_SUB)
            RIMS.extend(tube(dp, dr, seg=int(arg('--hpseg', 8)), smooth=False, tip=True))
    ZZ_PH = {}   # zigzag angle per |k| (phase-locked to the 3.0 stones in hairpin mode)
    if HAIRPIN:
        a3 = STONE3_START; d3 = PITCH3 / (r_out(radians(60)) + STONE3_LIFT)
        ZZ_PH[0] = 0.0; ZZ_PH[1] = a3 - d3 / 2
        for kk in range(2, 16): ZZ_PH[kk] = a3 + (kk - 2) * d3 / 2
    # 1.0 mm stones on both side walls: one continuous row of 31 per wall, over the top, +/-130 deg
    for ysgn in (1, -1):
        srow = []
        for k in range(-15, 16):
            ph = (k * SIDE_SPAN / 15) if not HAIRPIN else (ZZ_PH[abs(k)] * (1 if k >= 0 else -1))
            big = (k % 2 != 0)                                        # staggered zigzag: big 1.3 (outer) alternating with small 1.0 (inner)
            Dz = ZZ_BIG if big else 1.0
            r = R_IN + (SIDE_R_OUT if big else SIDE_R_IN)
            c = Vector((r * sin(ph), ysgn * (half_w(ph) - 0.05), r * cos(ph)))
            srow.append(add_round(Dz, c, Vector((0, ysgn, 0)), 'Shank', through=None, hole_frac=0.2, tangent=Vector((sin(ph), 0, cos(ph)))))
        BEZEL_ROWS.append(srow)
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
        if (outer - inner).length > RAIL_DEPTH: inner = outer - RAIL_DEPTH * n
        # rounded (filleted) rail section instead of a hard rectangle
        rf = min(RAIL_RF, (outer - inner).length / 2 - 0.02, (RAIL_ZT - RAIL_ZB) / 2 - 0.02); sec = []
        for (cn, cz, a0) in ((0.0 + rf, RAIL_ZT - rf, 90), (0.0 + rf, RAIL_ZB + rf, 180), (None, RAIL_ZB + rf, 270), (None, RAIL_ZT - rf, 0)):
            L_ = (outer - inner).length
            cn_ = cn if cn is not None else L_ - rf
            for k_ in range(4):
                a_ = radians(a0 + 90 * k_ / 3); sec.append(inner + n * (cn_ + rf * cos(a_)) + Z(cz + rf * sin(a_)))
        secs.append(sec)
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
        mb_, d, w, an = bar(A - d * 0.3, B, an, 1.45, 1.05, rr=SOFT_RR)
        arms.extend(mb_)
        L = (B - A).length; row = []
        for k in range(4):
            t = L / 2 + ARM_OFF + (k - 1.5) * ARM_PITCH
            c = A + d * t + an * (1.05 / 2 - 0.04)
            row.append(add_round(1.2, c, an, 'Arms', through=None, hole_frac=0.3, tangent=d))
        arm_rows.append(row)
    metal['CenterProngs'] = pr; metal['Arms'] = arms
    for row in arm_rows: BEZEL_ROWS.append(row)
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
                    CUTTERS.setdefault('HeartArm', MB()).extend(seat_cutter(STONE_MB[D][1], srow[-1]['M'], through, 0.3))
            BEZEL_ROWS.append(srow)
        return dict(nA=nA, nB=nB, pitchA=pA, pitchB=pB, perimeter=L)
    gal = ring_row(lambda th: E(th) - RAIL_IN * En(th), En, RAIL_D, 32, 0.64 + 0.65, 'GalleryRail', None, (RAIL_ZT + RAIL_ZB) / 2, beads=False)
    log('gallery', gal)

    # ---------------- hearts (built for +X then mirrored) ------------------
    # Each heart lies in a straight channel arm running diagonally down and out from the end of the gallery rail
    # (lobes up/in at the rail, point down/out past the band). Seen from the front it is edge-on; from the side face-on, point down.
    tau = H_TILT
    e_u = Vector((-cos(tau), 0, sin(tau)))      # local +y (point -> lobes)
    e_v = Vector((0, 1, 0))                      # local +x (along the finger)
    e_n = Vector((sin(tau), 0, cos(tau)))        # table normal: up and outward
    H_CENTER = Vector((H_LOBE_XW + H_LOBE_Y * cos(tau), 0, H_LOBE_ZW - H_LOBE_Y * sin(tau)))
    HM = Matrix.Identity(4)
    for i in range(3): HM[i][0], HM[i][1], HM[i][2], HM[i][3] = e_v[i], e_u[i], e_n[i], H_CENTER[i]
    def hl(x, y, z): return HM @ Vector((x, y, z))
    ez = Vector((0, 0, 1))
    def lbar(p, q, W, T, n=None):
        mb_, _, _, _ = bar(hl(*p), hl(*q), HM.to_3x3() @ (n or ez), W, T, rr=min(SOFT_RR, W / 2 - 0.02, T / 2 - 0.02)); return mb_
    hmetal = {}
    WX0, WX1 = float(arg('--wx0', 2.2)), float(arg('--wx1', 2.8))                     # channel walls (local x), stones on their outer faces
    Y0, Y1 = H_Y0, H_Y1                        # wall ends (local y)
    ZB, ZT = float(arg('--wzb', -2.9)), float(arg('--wzt', -1.3))                     # low walls: the heart's crown and girdle stay visible above them
    zc = (ZB + ZT) / 2; T_ = ZT - ZB
    CAP_O = 0.85
    CAP_DZ, CAP_DT = float(arg('--capdz', 0.35)), float(arg('--capdt', 0.7))
    arm = MB()
    for s in (-1, 1):
        arm.extend(lbar((s * (WX0 + WX1) / 2, Y0, zc), (s * (WX0 + WX1) / 2, Y1, zc), WX1 - WX0, T_))
    arm.extend(lbar((-WX1, Y1 + 0.25, zc), (WX1, Y1 + 0.25, zc), 0.5, T_))               # inner end cap (meets the rail)
    arm.extend(lbar((-WX1, Y0 - CAP_O / 2, zc + CAP_DZ), (WX1, Y0 - CAP_O / 2, zc + CAP_DZ), CAP_O, T_ + CAP_DT))   # outer end cap
    hmetal['HeartArm'] = arm
    # claws: two over each long side + one over the point
    hzc = lambda s: H_G / 2 + H_HC * (1 - s) / (1 - H_TS)
    def side_pt(yq, sgn):
        best = min(range(H_N * 4), key=lambda i: abs(h_outline(i / 4)[1] - yq) + (0 if h_outline(i / 4)[0] * sgn > 0 else 99))
        return Vector(h_outline(best / 4))
    hp_ = MB()
    for yq in (1.5, -0.9):
        for sgn in (-1, 1):
            q = side_pt(yq, sgn)
            hp_.extend(tube([hl(sgn * (WX0 + 0.35), q.y, ZT - 0.5), hl(sgn * (WX0 + 0.1), q.y, ZT + 0.5),
                             hl(q.x * 1.04, q.y, H_G / 2 + 0.35), hl(q.x * 0.90, q.y * 0.90, hzc(0.90) + 0.08)], [0.42, 0.42, 0.36, 0.16], seg=12))
    q = Vector((0, -H_SIZE / 2))
    hp_.extend(tube([hl(0, Y0 - 0.3, zc + 0.6), hl(0, Y0 - 0.1, ZT + 0.9), hl(0, -3.05, H_G / 2 + 0.35), hl(0, -2.75, hzc(0.9) + 0.08)], [0.45, 0.42, 0.36, 0.16], seg=12))
    hmetal['HeartProngs'] = hp_
    # support legs: from the outer end cap down onto the nearest shank claw pair (the L-bar seen in the front view)
    posts = MB()
    leg_c = hl(0, Y0 - CAP_O / 2, ZB + 0.3)
    tt = tooth_tips[1]
    ang = lambda P: atan2(P.x, P.z)
    bi = min(range(len(tt)), key=lambda i: abs(ang((tt[i][0] + tt[i][1]) / 2) - radians(LEG_DEG)))
    for tip in (tt[bi] if not SCALLOP else [min(tt[bi], key=lambda P: P.y)]):
        tgt = tip - Vector((sin(ang(tip)), 0, cos(ang(tip)))) * LEG_SINK + Vector((0, LEG_DY, 0))
        posts.extend(tube([leg_c, (leg_c + tgt) / 2, tgt], [LEG_R, LEG_R * 0.92, LEG_R * 0.92], seg=12, tip=False))
    hmetal['HeartPosts'] = posts
    log('heart centre', tuple(round(x, 2) for x in H_CENTER), 'lobe tip', tuple(round(x, 2) for x in hl(0, 3, 0)),
        'point', tuple(round(x, 2) for x in hl(0, -3, 0)), 'outer cap', tuple(round(x, 2) for x in hl(0, Y0 - 0.9, 0)), 'leg->boundary', bi,
        'deg', round(math.degrees(ang((tt[bi][0] + tt[bi][1]) / 2)), 1))
    # 1.4 mm stones: 4 on each wall's outer face + 3 on the outer end cap (11 per heart)
    hst = []
    for s in (-1, 1):
        for k in range(4):
            y = (Y0 + Y1) / 2 + H_WALL_SHIFT + (k - 1.5) * H_WALL_PITCH
            hst.append((Vector((s * (WX1 - 0.04), y, zc)), Vector((s, 0, 0)), s))
    for k in (-1, 0, 1):
        hst.append((Vector((k * 1.55, Y0 - CAP_O + 0.04, zc + CAP_DZ)), Vector((0, -1, 0)), 0))
    hpitch = H_WALL_PITCH
    for side in (1, -1):
        mir = (lambda v: Vector((-v.x, v.y, v.z))) if side < 0 else (lambda v: v)
        rows = {}
        for (c, a_, key) in hst:
            C = mir(HM @ c); A = mir(HM.to_3x3() @ a_)
            st = add_round(1.4, C, A, 'HeartArm', through=None, hole_frac=0.3, tangent=mir(HM.to_3x3() @ Vector((0, 0, 1))))
            if key != 0: CUTTERS.setdefault('GalleryRail', MB()).extend(seat_cutter(STONE_MB[1.4][1], st['M'], None, 0.3))   # arm walls butt into the rail
            rows.setdefault(key, []).append(st)
        for key, row in rows.items():
            BEZEL_ROWS.append(row)
        STONES.append(dict(kind='heart', D=6.0, M=(Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ HM) if side < 0 else HM.copy(),
                           center=mir(H_CENTER), axis=mir(e_n), target='GalleryRail'))
        CUTTERS.setdefault('GalleryRail', MB()).extend(heart_stone().xform(STONES[-1]['M'] @ Matrix.Scale(1.04, 4)))
    for k, mb in hmetal.items():
        metal[k] = MB().extend(mb).extend(mb.mirror_x())
    metal['ShankClaws'] = CLAWS
    for job in RIM_JOBS: job()   # after every stone exists, so rims can dip under the heart-arm caps
    metal['ShankRims'] = RIMS
    for r_ in BEZEL_ROWS: bezel_row(r_)
    metal['PaveBezels'] = BEZELS; metal['ShankCups'] = CUPS
    low = {}

    # ---------------- objects ---------------------------------------------
    objs = {}
    for k, mb in metal.items():
        objs[k] = to_obj(k, mb, GOLD, smooth=True, sharp_deg=(85 if k in ('PaveBezels', 'ShankCups', 'ShankClaws', 'ShankRims') else 40))
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
        if '--keepcut' not in argv: bpy.data.objects.remove(cut, do_unlink=True)
        log('boolean', tgt, 'faces', len(objs[tgt].data.polygons), '%.1fs' % (time.time() - t))
        if SOFT_BEVEL > 0 and '--nobool' not in argv:
            # soften every hard edge left by the boolean seats and the slabs (rounded, polished transitions)
            bv = objs[tgt].modifiers.new('soft', 'BEVEL'); bv.limit_method = 'ANGLE'; bv.angle_limit = radians(30)
            bv.width = SOFT_BEVEL; bv.segments = int(arg('--bvseg', 1)); bv.profile = 0.5; bv.miter_outer = 'MITER_ARC'
            bpy.context.view_layer.objects.active = objs[tgt]
            try: bpy.ops.object.modifier_apply(modifier=bv.name)
            except Exception as e: log('bevel failed', tgt, e); objs[tgt].modifiers.remove(bv)
        objs[tgt].data.shade_smooth(); objs[tgt].data.set_sharp_from_angle(angle=radians(SOFT_SHARP))
        if WNORM and '--nobool' not in argv:
            # face-weighted normals: removes the dark streak shading that long boolean triangles leave on flat/curved metal
            wn = objs[tgt].modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True; wn.weight = 50; wn.mode = 'FACE_AREA'
            bpy.context.view_layer.objects.active = objs[tgt]
            try: bpy.ops.object.modifier_apply(modifier=wn.name)
            except Exception as e: log('wnormal failed', tgt, e); objs[tgt].modifiers.remove(wn)
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
        if o.name in ('PaveBeads', 'ShankClaws', 'CenterProngs', 'HeartProngs', 'PaveBezels'): continue
        t = BVHTree.FromObject(o, dg)
        for (name, s, st) in items:
            if s.get('target') == o.name or (o.name == 'HeartArm' and s.get('target') == 'GalleryRail') or (o.name == 'GalleryRail' and s.get('target') == 'HeartArm'): continue
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
        lift = nt.nodes.new('ShaderNodeMixRGB'); lift.blend_type = 'ADD'; lift.inputs['Fac'].default_value = 1.0
        lift.inputs['Color2'].default_value = (ENV_FLOOR, ENV_FLOOR, ENV_FLOOR, 1)
        nt.links.new(env.outputs['Color'], lift.inputs['Color1']); nt.links.new(lift.outputs['Color'], bg_env.inputs['Color'])
        bg_env.inputs['Strength'].default_value = ENV_STR
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
    # matched to the reference 3/4 panel by a silhouette-IoU camera search (elev 72.7, azim -57.7, roll -8 deg)
    'three_quarter': (Vector((cos(radians(72.7)) * cos(radians(-57.7)), cos(radians(72.7)) * sin(radians(-57.7)), sin(radians(72.7)))), Vector((0, 0, 1))),
}
VIEW_ROLL = {'three_quarter': -8.0}
CAM_SCALES = {}
def make_camera(view):
    d, up = VIEW_DIRS[view]; d = d.normalized()
    cam = bpy.data.cameras.new('Cam_' + view); cam.type = 'ORTHO'; cam.clip_start = 1; cam.clip_end = 2000
    ob = bpy.data.objects.new('Cam_' + view, cam); bpy.context.scene.collection.objects.link(ob)
    mn, mx = bbox_world(); ctr = (mn + mx) / 2
    x = up.cross(d).normalized(); y = d.cross(x)
    r = radians(VIEW_ROLL.get(view, 0.0)); x, y = x * cos(r) + y * sin(r), -x * sin(r) + y * cos(r)
    ext = 0
    for i in range(8):
        c = Vector((mn.x if i & 1 else mx.x, mn.y if i & 2 else mx.y, mn.z if i & 4 else mx.z)) - ctr
        ext = max(ext, abs(c.dot(x)), abs(c.dot(y)))
    cam.ortho_scale = 2 * ext * 1.08
    CAM_SCALES[view] = cam.ortho_scale
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
    json.dump(CAM_SCALES, open(os.path.join(OUT, 'cams.json'), 'w'))
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

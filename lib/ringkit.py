"""
ringkit: the Blender toolkit shared by every ring design in this repo (Blender 4.2, headless).

A design's build script (designs/dN/build.py) defines DESIGN_DIR and TUNED, then loads this file with exec(),
so the helpers below and the design's own geometry share one namespace (the design calls them directly):

    DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))
    TUNED = '--some-option 1.0 ...'.split()            # the design's baked settings (command line wins)
    exec(compile(open(RINGKIT).read(), RINGKIT, 'exec'))
    def build(): ...                                   # the design's geometry -> (GOLD, DIA, counts, rowinfo)
    def collision_report(): ...
    main()

Outputs (per design):
  model/  ring.blend, ring.stl (metal only, mm), stats.json    <- committed at the end of each round
  build/  ring.glb (web model), cams.json, render_<view>.png    <- scratch, git-ignored; --fast also puts its trial
          ring.blend here so a quick trial never overwrites the committed model
Units: 1 Blender unit = 1 mm. Finger axis = Y. The band lies in the XZ plane, head on +Z.
"""
import bpy, bmesh, math, sys, os, json, time
from mathutils import Vector, Matrix
from math import sin, cos, pi, radians, sqrt, atan2

# --------------------------------------------------------------------------- configuration (from the design script)
MODEL_DIR = os.path.join(DESIGN_DIR, 'model')
BUILD_DIR = os.path.join(DESIGN_DIR, 'build')
for _d in (MODEL_DIR, BUILD_DIR): os.makedirs(_d, exist_ok=True)
argv = (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []) + list(TUNED)   # command line first: first match wins
BLEND_PATH = os.path.join(BUILD_DIR if '--fast' in argv else MODEL_DIR, 'ring.blend')
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
DO_RENDER = '--render' in argv
RES = int(arg('--res', 1600))
SAMPLES = int(arg('--samples', 128))
VIEWS = arg('--views', 'top,three_quarter,front,side').split(',')
T0 = time.time()
def log(*a): print('[ring %6.1fs]' % (time.time() - T0), *a, flush=True)

# --------------------------------------------------------------------------- shared constants
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
# studio environment for the Cycles renders
ENV_FLOOR = float(arg('--envfloor', 0.02)); ENV_STR = float(arg('--envstr', 1.8))

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

# --------------------------------------------------------------------------- stones registry
STONES = []          # dicts: kind, D, M (matrix)
CUTTERS = {}         # target object name -> MB of boolean cutters (stone seats etc.)
STONE_MB = {}
BEZELS = MB(); BEZEL_ROWS = []
SEG_SEAT = int(arg('--segseat', 12)); BZ_SEG = int(arg('--bzseg', 12)); BZ_K = int(arg('--bzk', 6))   # seat / bezel resolution
BEZEL_RM = float(arg('--bezel', 0.05)); BEZEL_Z = float(arg('--bezelz', 0.0))   # rounded lip round every small stone
def add_round(D, center, axis, target, through=None, tangent=None, hole_frac=0.45, cove=0.0, cove_z=0.0):
    M = frame(Vector(center), Vector(axis), Vector(tangent) if tangent else Vector((1, 0, 0)))
    STONES.append(dict(kind='round', D=D, M=M, center=Vector(center), axis=Vector(axis).normalized(), target=target))
    if D not in STONE_MB: STONE_MB[D] = round_brilliant(D)
    if target:
        CUTTERS.setdefault(target, MB()).extend(seat_cutter(STONE_MB[D][1], M, through, hole_frac, cove, cove_z))
    return STONES[-1]

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
    gc = [float(x) for x in arg('--goldcol', '0.80,0.79,0.76').split(',')]   # 18K white gold (rhodium): faintly warm
    b.inputs['Base Color'].default_value = (gc[0], gc[1], gc[2], 1)
    if 'Specular Tint' in b.inputs and len(gc) >= 3:   # 18K white gold: faintly warm, slightly darker than chrome
        try: b.inputs['Specular Tint'].default_value = (1.0, 0.99, 0.97, 1)
        except Exception: pass
    b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = float(arg('--rough', 0.16))
    dia = bpy.data.materials.new('Diamond'); dia.use_nodes = True
    d = dia.node_tree.nodes['Principled BSDF']
    d.inputs['Base Color'].default_value = (1, 1, 1, 1)
    d.inputs['Metallic'].default_value = 0.0; d.inputs['Roughness'].default_value = 0.0
    d.inputs['IOR'].default_value = 2.42
    d.inputs['Transmission Weight'].default_value = 1.0
    if 'Dispersion' in d.inputs: d.inputs['Dispersion'].default_value = 0.02
    return gold, dia

# --------------------------------------------------------------------------- scene reset
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)

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
    hdr = os.path.join(DESIGN_DIR, 'studio.hdr')   # optional HDR environment next to the design's build.py
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
    json.dump(CAM_SCALES, open(os.path.join(BUILD_DIR, 'cams.json'), 'w'))
    bpy.context.scene.camera = cams['three_quarter']
    idia = inner_diameter()
    parts = {o.name: round(mesh_volume(o), 2) for o in metal_objects()}
    bpy.context.preferences.filepaths.save_version = 0   # no ring.blend1 backups: git keeps the versions
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log('saved blend', os.path.relpath(BLEND_PATH, DESIGN_DIR))
    if '--fast' in argv:   # trial renders only: skip the metal union, STL, GLB and stats
        log('parts', json.dumps(parts)); return fast_render()
    # ---- union metal -> STL + volume
    un = union_metal(0.05)
    vol = mesh_volume(un)
    nf = len(un.data.polygons)
    dec = un.modifiers.new('dec', 'DECIMATE'); dec.ratio = min(1.0, 400000 / max(1, nf))
    bpy.context.view_layer.objects.active = un; bpy.ops.object.modifier_apply(modifier='dec')
    for o in bpy.context.scene.objects: o.select_set(False)
    un.select_set(True); bpy.context.view_layer.objects.active = un
    bpy.ops.wm.stl_export(filepath=os.path.join(MODEL_DIR, 'ring.stl'), export_selected_objects=True, global_scale=1.0, use_scene_unit=False, apply_modifiers=True)
    stl_faces = len(un.data.polygons)
    bpy.data.objects.remove(un, do_unlink=True)
    stats = dict(inner_diameter_mm=round(idia, 3), metal_volume_union_mm3=round(vol, 1), metal_volume_sum_parts_mm3=round(sum(parts.values()), 1),
                 parts_mm3=parts, est_weight_g_18kw_14_7=round(vol * 14.7 / 1000, 2), stl_faces=stl_faces, stone_counts=counts,
                 rows=rowinfo, center=dict(L=C_L, W=C_W, D=C_D, crown=C_HC, pavilion=C_HP, girdle=C_G, table_mm=0.6 * C_W))
    # ---- GLB (meters, true scale)
    # the web viewer shades diamonds from screen-space facet normals (dFdx/dFdy) and ignores mesh normals, so export
    # them with shared vertices (smooth) - ~5x fewer GLB vertices; renders above use the flat-shaded blend
    for o in COLL.objects:
        if o.type == 'MESH' and o.data.materials and o.data.materials[0].name == 'Diamond':
            o.data.shade_smooth()
            try: o.data.set_sharp_from_angle(angle=pi)
            except Exception: pass
    root = bpy.data.objects.new('RingRoot', None); bpy.context.scene.collection.objects.link(root)
    for o in COLL.objects: o.parent = root
    root.scale = (0.001, 0.001, 0.001)
    for o in bpy.context.scene.objects: o.select_set(o.name in COLL.objects or o == root)
    bpy.ops.export_scene.gltf(filepath=os.path.join(BUILD_DIR, 'ring.glb'), export_format='GLB', use_selection=True, export_apply=True,
                              export_cameras=False, export_lights=False, export_yup=True)
    stats['glb_MB'] = round(os.path.getsize(os.path.join(BUILD_DIR, 'ring.glb')) / 1e6, 2)
    stats['tris'] = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in COLL.objects)
    json.dump(stats, open(os.path.join(MODEL_DIR, 'stats.json'), 'w'), indent=1)
    log(json.dumps(stats, indent=1))
    if DO_RENDER: fast_render()

def fast_render():
    if DO_RENDER:
        bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
        sc = bpy.context.scene
        sc.render.resolution_x = sc.render.resolution_y = RES; sc.cycles.samples = SAMPLES
        FL = bpy.data.lights.new('Fill', 'AREA'); FL.size = 90; FL.energy = float(arg('--fill', 6e4))
        flo = bpy.data.objects.new('Fill', FL); sc.collection.objects.link(flo); flo.visible_camera = False
        for v in VIEWS:
            sc.camera = bpy.data.objects['Cam_' + v]
            cm = sc.camera.matrix_world; cpos = cm.translation; cz = Vector((cm[0][2], cm[1][2], cm[2][2]))
            up_ = Vector((0, 0, 1)) if abs(cz.z) < 0.9 else Vector((0, 1, 0))
            flo.matrix_world = frame(cpos + up_ * 60, (cpos + up_ * 60).normalized(), Vector((1, 0, 0)))
            sc.render.filepath = os.path.join(BUILD_DIR, 'render_%s.png' % v)
            t = time.time(); bpy.ops.render.render(write_still=True); log('rendered', v, '%.0fs' % (time.time() - t))


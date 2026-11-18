"""
Design #2 builder: oval side stones on a thin round band (v2.0). Blender 4.2, headless:
  blender -b -P designs/d2/build.py -- [--render] [--fast] [--checkonly] [--res 1600] [--samples 128] [--views ...]
Same 15.68 ct oval centre stone as design #1 on a four-claw head with a pave gallery rail (26 x 1.3 mm), and 8 oval side
stones (6.7 x 4.5 mm, ~0.7 ct each, long axis along the finger) in shared claws, 4 per side, on a thin round band.
Reference picture: designs/d2/reference/original.jpg. Notes, owner decisions and round history: designs/d2/DESIGN.md.
Shared helpers (stones, seats, materials, scene, cameras, export) come from lib/ringkit.py; this file holds only
design #2's settings and geometry. Outputs: model/ (committed) and build/ (scratch), see lib/ringkit.py.
"""
import os
DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))
RINGKIT = os.path.normpath(os.path.join(DESIGN_DIR, '..', '..', 'lib', 'ringkit.py'))
# Baked settings, newest round first (the first match wins; the command line beats all of them):
# round 2 (owner review): thin round women's band ~3 mm wide (much narrower than the 6.7 mm ovals), claw feet on the
# OUTSIDE of the band; head claws land on the narrow band top. Gold ~5.2 g in the model (owner keeps 8.6 g as the spec).
# round 1 (matched to the reference picture): open band under the ovals (thin inner ring + claws + cradles), 8.6 g
TUNED = ('--round 1 --wst 1.5 --wbot 1.5 --ttop 1.8 --tst 1.8 --tbot 1.8 --bri 0.6 --cry 1.6 --prly 1.0 --ovrg 10.85 --postr1 12.1 --postr0 8.5 --postr 0.47 --ch 0 --tst 1.4 --tbot 1.95 --wbot 2.2 --ts0 11 --ts1 17 --tb0 112 --tb1 128 --bri 0.5 --bro 0.6 --cry 1.4 --crr 0.36 --crtop 10.2').split()
exec(compile(open(RINGKIT).read(), RINGKIT, 'exec'))   # shared helpers + arg(), argv, log(), constants

# --------------------------------------------------------------------------- design #2 parameters
# centre stone: same IGI oval as design #1, seated a little lower on this head
Z_CULET = float(arg('--zculet', 10.1))
Z_GB = Z_CULET + C_HP; Z_GT = Z_GB + C_G; Z_GM = (Z_GB + Z_GT) / 2; Z_TABLE = Z_GT + C_HC

# band
B_T_TOP = float(arg('--ttop', 1.70))    # radial thickness under the head
B_T_ST = float(arg('--tst', 1.95))      # under the oval stones
B_T_BOT = float(arg('--tbot', 1.55))    # plain bottom
B_W_ST = float(arg('--wst', 3.2))       # half width at the shoulders (stones)
B_W_BOT = float(arg('--wbot', 2.0))     # half width at the bottom
B_TAPER0, B_TAPER1 = float(arg('--taper0', 112)), float(arg('--taper1', 150))
B_RO, B_RI = float(arg('--bro', 0.7)), float(arg('--bri', 0.7))
B_TS0, B_TS1 = float(arg('--ts0', 8)), float(arg('--ts1', 20))      # head -> stone section transition (deg)
B_TB0, B_TB1 = float(arg('--tb0', B_TAPER0)), float(arg('--tb1', B_TAPER1))   # stone section -> plain bottom
CH = int(arg('--ch', 1)); CH_WALL = float(arg('--chwall', 0.7)); CH_FLOOR = float(arg('--chfloor', 0.75))
CH_C0, CH_C1 = float(arg('--chc0', 14.0)), float(arg('--chc1', 114.0))

# oval side stones
OV_L, OV_W = float(arg('--ovl', 6.7)), float(arg('--ovw', 4.5))
OV_N = int(arg('--ovn', 4)); OV_PH0 = float(arg('--ovph0', 26.0)); OV_PITCH = float(arg('--ovpitch', 25.0))
OV_RG = float(arg('--ovrg', 10.55))     # girdle radius (stone centre)
POST_Y = float(arg('--posty', 2.05)); POST_R = float(arg('--postr', 0.45)); POST_R0 = float(arg('--postr0', 9.2)); POST_R1 = float(arg('--postr1', 11.75))

# head
PR_R = float(arg('--prr', 0.6)); PR_LX, PR_LY, PR_LZ = float(arg('--prlx', 1.9)), float(arg('--prly', 2.3)), float(arg('--prlz', 9.45))
RL_IN = float(arg('--rlin', 0.30)); RL_H = float(arg('--rlh', 1.2)); RL_TOPGAP = float(arg('--rltop', 0.85)); RL_DEPTH = float(arg('--rld', 0.9))
RL_N = int(arg('--rln', 26)); RL_D = 1.3
B_ROUND = int(arg('--round', 0)); POST_FOOTIN = float(arg('--postfoot', 0.55))
CR = int(arg('--cr', 1)); CR_Y = float(arg('--cry', 2.3)); CR_R = float(arg('--crr', 0.33)); CR_TOP = float(arg('--crtop', 10.3)); CR_GAP = float(arg('--crgap', 0.15))
BRIDGE = int(arg('--bridge', 1)); BR_R = float(arg('--brr', 0.42)); BR_DZ = float(arg('--brdz', 0.25))

OVALS = []   # dicts: center, M, L, W


def oval_stone(L, W):
    """faceted oval brilliant, girdle centre at z=0, long axis along local x."""
    N = 48; a, b = L / 2, W / 2; g = 0.03 * W; hc = 0.15 * W; hp = 0.43 * W; st = 0.58
    outline = lambda f: (a * cos(2 * pi * f / N), b * sin(2 * pi * f / N))
    zc = lambda s: g / 2 + hc * (1 - s) / (1 - st)
    zp = lambda s: -g / 2 - hp * (1 - s)
    rings = [(st, g / 2 + hc, [3 + 6 * k for k in range(8)]),
             (0.82, zc(0.82) + 0.02, [6 * k for k in range(8)]),
             (0.95, zc(0.95) + 0.01, [3 * k for k in range(16)]),
             (1, g / 2, list(range(N))), (1, -g / 2, list(range(N))),
             (0.62, zp(0.62) - 0.03, [3 * k for k in range(16)]),
             (0.25, zp(0.25) - 0.02, [6 * k for k in range(8)])]
    return stone_mb(outline, N, rings, g / 2 + hc, -g / 2 - hp), dict(a=a, b=b, g=g, hc=hc, hp=hp)


def oval_cutter(info, M, through=None, n=40):
    a, b, g, hp = info['a'], info['b'], info['g'], info['hp']
    hf = 0.45
    secs = [(1.004, 3.0), (1.004, -g / 2), (0.96, -g / 2 - 0.01), (hf, -g / 2 - hp * (1 - hf))]
    secs += [(hf, -through)] if through else [(0.02, -g / 2 - hp - 0.1)]
    loops = [[M @ Vector((s * (a + 0.01) * cos(2 * pi * k / n), s * (b + 0.01) * sin(2 * pi * k / n), z)) for k in range(n)] for (s, z) in secs]
    return loft(loops, closed_v=False, cap=True)


def build():
    global COLL
    clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
    COLL = bpy.data.collections.new('Ring'); sc.collection.children.link(COLL)
    GOLD, DIA = materials()
    metal = {}
    Z = lambda z: Vector((0, 0, z))
    STONE_MB[RL_D] = round_brilliant(RL_D)

    # ---------------- band ----------------------------------------------------
    def smooth(x0, x1, x):
        t = min(1, max(0, (x - x0) / (x1 - x0))); return t * t * (3 - 2 * t)
    def thick(phi):
        p = abs(phi)
        return B_T_TOP + (B_T_ST - B_T_TOP) * smooth(radians(B_TS0), radians(B_TS1), p) + (B_T_BOT - B_T_ST) * smooth(radians(B_TB0), radians(B_TB1), p)
    def half_w(phi):
        return B_W_ST + (B_W_BOT - B_W_ST) * smooth(radians(B_TAPER0), radians(B_TAPER1), abs(phi))
    def profile(t, w, n=10):
        if B_ROUND:   # round women's band: the outer side is one full curve edge to edge, softly rounded inside
            ro, ri = min(t, w) - 0.02, min(B_RI, t / 2 - 0.02, w - 0.05); ro = min(ro, w - 0.01, t - ri - 0.02)
        else:
            ro, ri = min(B_RO, t / 2 - 0.02, w - 0.05), min(B_RI, t / 2 - 0.02); pts = []
        pts = []
        for (c, r, a0) in [((R_IN + t - ro, w - ro), ro, 0), ((R_IN + ri, w - ri), ri, 90), ((R_IN + ri, -w + ri), ri, 180), ((R_IN + t - ro, -w + ro), ro, 270)]:
            for k in range(n):
                a = radians(a0 + 90 * k / (n - 1)); pts.append((c[0] + r * cos(a), c[1] + r * sin(a)))
        return pts
    secs = []; M = 240
    for m in range(M):
        phi = -pi + 2 * pi * m / M
        secs.append([Vector((r * sin(phi), y, r * cos(phi))) for (r, y) in profile(thick(phi), half_w(phi))])
    metal['Shank'] = loft(secs)
    r_out = lambda phi: R_IN + thick(phi)

    # open channel between the side walls under the oval stones (shared-claw channel setting)
    if CH:
        for side in (1, -1):
            cs = []
            for i in range(41):
                ph = side * radians(CH_C0 + (CH_C1 - CH_C0) * i / 40)
                w = half_w(ph) - CH_WALL; r0 = R_IN + CH_FLOOR; r1 = r_out(ph) + 2.0; rr = 0.35
                loop = [(r1, -w), (r0 + rr, -w)] + [(r0 + rr - rr * sin(radians(90 * k / 6)), -w + rr - rr * cos(radians(90 * k / 6))) for k in range(1, 6)] + \
                       [(r0, -w + rr), (r0, w - rr)] + [(r0 + rr - rr * cos(radians(90 * k / 6)), w - rr + rr * sin(radians(90 * k / 6))) for k in range(1, 6)] + [(r0 + rr, w), (r1, w)]
                cs.append([Vector((r * sin(ph), y, r * cos(ph))) for (r, y) in loop])
            if side < 0: cs = cs[::-1]
            CUTTERS.setdefault('Shank', MB()).extend(loft(cs, closed_v=False, cap=True))

    # oval side stones: 4 per side, table facing out, long axis along the finger
    omb, oinfo = oval_stone(OV_L, OV_W)
    posts = MB()
    for side in (1, -1):
        for k in range(OV_N):
            ph = side * radians(OV_PH0 + k * OV_PITCH)
            rad = Vector((sin(ph), 0, cos(ph)))
            Mo = frame(rad * OV_RG, rad, Vector((0, 1, 0)))
            OVALS.append(dict(center=rad * OV_RG, M=Mo, L=OV_L, W=OV_W, axis=rad))
            STONES.append(dict(kind='oval', D=OV_L, M=Mo, center=rad * OV_RG, axis=rad, target='Shank'))
            CUTTERS.setdefault('Shank', MB()).extend(oval_cutter(oinfo, Mo, through=4.0))
        # shared claws: a pair of round posts (one at each band edge) at every boundary between stones and at both ends
        for j in range(OV_N + 1):
            ph = side * radians(OV_PH0 + (j - 0.5) * OV_PITCH)
            rad = Vector((sin(ph), 0, cos(ph)))
            for ys in (-1, 1):
                yv = Vector((0, ys * POST_Y, 0))
                tip_ = rad * (POST_R1 - POST_R * 0.92) + yv     # round (domed) claw ends, as in the reference
                # the claw's foot sits on the OUTSIDE of the band (against its side face) and leans out to the tip
                foot = rad * POST_R0 + Vector((0, ys * (half_w(ph) + POST_R * POST_FOOTIN), 0))
                posts.extend(tube([foot, (foot + tip_) / 2, tip_], [POST_R, POST_R * 0.96, POST_R * 0.92], seg=16, tip=False))
                posts.extend(sphere(tip_, POST_R * 0.92, 16, 8))
        # cradles: at each band edge a round wire runs from claw to claw, dipping under each oval's pavilion (U arcs from the front)
        if CR:
            for k in range(OV_N):
                phc = radians(OV_PH0 + k * OV_PITCH)
                for ys in (-1, 1):
                    path = []; rr = []
                    for i in range(17):
                        th = radians(OV_PH0 + (k - 0.5) * OV_PITCH) + radians(OV_PITCH) * i / 16
                        u = (th - phc) * OV_RG
                        rho = sqrt((CR_Y / oinfo['a']) ** 2 + (u / oinfo['b']) ** 2)
                        rc = CR_TOP if rho >= 1 else min(CR_TOP, OV_RG - oinfo['g'] / 2 - oinfo['hp'] * (1 - rho) - CR_R - CR_GAP)
                        # (the wire may sink into the inner ring: it simply merges with it)
                        ph = side * th; path.append(Vector((rc * sin(ph), ys * CR_Y, rc * cos(ph))))
                    posts.extend(tube(path, [CR_R] * len(path), seg=12, tip=False))
    metal['ShankClaws'] = posts

    # ---------------- head ----------------------------------------------------
    a, b = C_A, C_B
    E = lambda th, s=1.0: Vector((b * s * cos(th), a * s * sin(th), 0))
    En = lambda th: Vector((cos(th) / b, sin(th) / a, 0)).normalized()
    ZT = Z_GB - RL_TOPGAP; ZB = ZT - RL_H
    s_in = (ZB - Z_CULET) / C_HP
    secs = []
    for m in range(192):
        th = 2 * pi * m / 192; P = E(th); n = En(th)
        outer = P - RL_IN * n; inner = P * s_in + 0.15 * n
        if (outer - inner).length > RL_DEPTH: inner = outer - RL_DEPTH * n
        L_ = (outer - inner).length; rf = min(0.3, L_ / 2 - 0.02, RL_H / 2 - 0.02); sec = []
        for (cn, cz, a0) in ((rf, ZT - rf, 90), (rf, ZB + rf, 180), (L_ - rf, ZB + rf, 270), (L_ - rf, ZT - rf, 0)):
            for k_ in range(4):
                a_ = radians(a0 + 90 * k_ / 3); sec.append(inner + n * (cn + rf * cos(a_)) + Z(cz + rf * sin(a_)))
        secs.append(sec)
    metal['GalleryRail'] = loft(secs)
    # 4 claws: over the crown, down outside the rail, then sweeping in under the stone onto the band top
    zcrown = lambda s: Z_GT + C_HC * (1 - s) / (1 - C_TABLE_S)
    pr = MB()
    for th in PRONG_TH:
        n = En(th); P = E(th)
        sx = 1 if cos(th) > 0 else -1; sy = 1 if sin(th) > 0 else -1
        Ptip = E(th, 0.905) + Z(zcrown(0.905) + 0.16)
        P4 = P + 0.25 * n + Z(Z_GT + 0.45)
        P3 = P + 0.55 * n + Z(Z_GM)
        Pr = P - RL_IN * n + (PR_R + 0.05) * n + Z((ZT + ZB) / 2)
        Lf = Vector((sx * PR_LX, sy * PR_LY, PR_LZ))
        Pm = Pr * 0.42 + Lf * 0.58 + Vector((sx * 0.55, sy * 0.55, -0.15))
        pr.extend(tube([Lf + Z(-0.4), Lf, Pm, Pr, P3, P4, Ptip], [PR_R, PR_R, PR_R, PR_R, PR_R * 1.02, PR_R * 0.95, PR_R * 0.72], seg=16))
    if BRIDGE:   # short saddle bar joining the two claw feet on each side of the band top (under the culet)
        for sy in (-1, 1):
            pr.extend(tube([Vector((-PR_LX - 0.2, sy * PR_LY, PR_LZ + BR_DZ)), Vector((0, sy * PR_LY, PR_LZ + BR_DZ + 0.12)), Vector((PR_LX + 0.2, sy * PR_LY, PR_LZ + BR_DZ))], [BR_R] * 3, seg=12))
    metal['CenterProngs'] = pr
    # 26 x 1.3 mm pave on the rail's outer face, spaced evenly between the claws
    curve = lambda th: E(th) - RL_IN * En(th)
    pts, cum = arclen_table(curve); Lc = cum[-1]
    ps = [cum[int(round(th / (2 * pi) * 4000))] for th in PRONG_TH]
    segs = [(ps[(i + 1) % 4] - ps[i]) % Lc for i in range(4)]
    margin = PR_R + 0.05 + RL_D / 2 + 0.15
    # split RL_N over the 4 claw gaps in proportion to their free length
    free = [s - 2 * margin for s in segs]; tot = sum(free)
    cnt = [max(1, round(RL_N * f / tot)) for f in free]
    while sum(cnt) > RL_N: cnt[cnt.index(max(cnt))] -= 1
    while sum(cnt) < RL_N: cnt[free.index(max(free))] += 1
    rows = place_on_curve(lambda s: th_at(cum, s), ps, cnt, Lc, margin)
    for seg in rows:
        srow = []
        for th in seg:
            c = curve(th); ax = En(th)
            srow.append(add_round(RL_D, c - ax * 0.05 + Z((ZT + ZB) / 2), ax, 'GalleryRail', hole_frac=0.3, tangent=Vector((0, 0, 1))))
        BEZEL_ROWS.append(srow)
    for r_ in BEZEL_ROWS: bezel_row(r_)
    metal['PaveBezels'] = BEZELS
    rowinfo = dict(rail_counts=cnt, rail_perimeter=round(Lc, 2), oval_pitch_deg=OV_PITCH,
                   oval_gap_at_posts_mm=round(OV_RG * radians(OV_PITCH) - 2 * (OV_W / 2) * sqrt(max(0, 1 - (POST_Y / (OV_L / 2)) ** 2)), 2))
    log('rail counts', cnt, 'oval gap at posts', rowinfo['oval_gap_at_posts_mm'])

    # ---------------- objects -------------------------------------------------
    objs = {k: to_obj(k, mb, GOLD, smooth=True, sharp_deg=(85 if k in ('PaveBezels', 'ShankClaws') else 40)) for k, mb in metal.items()}
    for tgt, cmb in CUTTERS.items():
        cut = to_obj('cut_' + tgt, cmb, GOLD)
        mod = objs[tgt].modifiers.new('seats', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'
        mod.object = cut; mod.use_self = True; mod.use_hole_tolerant = True
        bpy.context.view_layer.objects.active = objs[tgt]
        t = time.time(); v0 = mesh_volume(objs[tgt])
        bpy.ops.object.modifier_apply(modifier=mod.name)
        log('vol before/after', tgt, round(v0, 2), round(mesh_volume(objs[tgt]), 2), '%.1fs' % (time.time() - t))
        bpy.data.objects.remove(cut, do_unlink=True)
        bv = objs[tgt].modifiers.new('soft', 'BEVEL'); bv.limit_method = 'ANGLE'; bv.angle_limit = radians(30)
        bv.width = 0.08; bv.segments = 2; bv.profile = 0.5; bv.miter_outer = 'MITER_ARC'
        try: bpy.ops.object.modifier_apply(modifier=bv.name)
        except Exception as e: log('bevel failed', tgt, e); objs[tgt].modifiers.remove(bv)
        objs[tgt].data.shade_smooth(); objs[tgt].data.set_sharp_from_angle(angle=radians(60))
        wn = objs[tgt].modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True; wn.weight = 50; wn.mode = 'FACE_AREA'
        try: bpy.ops.object.modifier_apply(modifier=wn.name)
        except Exception as e: log('wnormal failed', tgt, e); objs[tgt].modifiers.remove(wn)
    fam = {}
    for s in STONES:
        if s['kind'] == 'round': fam.setdefault('Diamonds_%.1fmm' % s['D'], MB()).extend(STONE_MB[s['D']][0].xform(s['M']))
        elif s['kind'] == 'oval': fam.setdefault('Diamonds_Oval_%.1fx%.1f' % (OV_L, OV_W), MB()).extend(omb.xform(s['M']))
    for k, mb in fam.items(): to_obj(k, mb, DIA)
    to_obj('Diamond_Center_Oval', oval_brilliant().xform(Matrix.Translation((0, 0, Z_GM))), DIA)
    counts = {}
    for s in STONES:
        k = ('oval %.1fx%.1f' % (OV_L, OV_W)) if s['kind'] == 'oval' else ('%s %.1f' % (s['kind'], s['D']))
        counts[k] = counts.get(k, 0) + 1
    log('stone counts', counts)
    return GOLD, DIA, counts, rowinfo


def collision_report():
    from mathutils.bvhtree import BVHTree
    tr = lambda mb: BVHTree.FromPolygons([Vector(v) for v in mb.v], mb.f, epsilon=0.0)
    omb, _ = oval_stone(OV_L, OV_W)
    items = []
    for s in STONES:
        mb = STONE_MB[s['D']][0].xform(s['M']) if s['kind'] == 'round' else omb.xform(s['M'])
        items.append(('r%.1f' % s['D'] if s['kind'] == 'round' else 'oval', s, tr(mb), s['D']))
    items.append(('center', dict(center=Vector((0, 0, Z_GM))), tr(oval_brilliant().xform(Matrix.Translation((0, 0, Z_GM)))), 19.4))
    ss = {}
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            A, B = items[i], items[j]
            if (A[1]['center'] - B[1]['center']).length > (A[3] + B[3]) / 2 + 0.6: continue
            if A[2].overlap(B[2]):
                k = '/'.join(sorted((A[0], B[0]))); ss[k] = ss.get(k, 0) + 1
    sm = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for o in metal_objects():
        if o.name in ('PaveBezels', 'CenterProngs'): continue   # claws grip the stones by design (as in design #1)
        t = BVHTree.FromObject(o, dg)
        for (name, s, st, _) in items:
            if s.get('target') == o.name: continue
            if st.overlap(t): k = name + '>' + o.name; sm[k] = sm.get(k, 0) + 1
    log('COLLISIONS stone-stone', json.dumps(ss)); log('COLLISIONS stone-metal', json.dumps(sm))
    return ss, sm


if '--nobuild' not in argv: main()

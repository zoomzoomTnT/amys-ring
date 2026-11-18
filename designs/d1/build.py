"""
Design #1 builder: the heart-shoulder ring (v1.0, refinement rounds 1-16). Blender 4.2, headless:
  blender -b -P designs/d1/build.py -- [--render] [--fast] [--checkonly] [--res 1600] [--samples 128] [--views top,three_quarter,front,side]
Reference picture: designs/d1/reference/original.jpg. Notes and round history: designs/d1/DESIGN.md.
Center oval long axis along Y (along the finger); hearts at +/-X on the shoulders.
Shared helpers (stones, seats, materials, scene, cameras, export) come from lib/ringkit.py; this file holds only
design #1's settings and geometry. Outputs: model/ (committed) and build/ (scratch), see lib/ringkit.py.
"""
import os
DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))
RINGKIT = os.path.normpath(os.path.join(DESIGN_DIR, '..', '..', 'lib', 'ringkit.py'))
# v1.0 round 8 settings (thick half-round U rims with rounded tulip peaks, elliptical U-seats, sideways 3.0 mm stones, flush pave beads, softened metal). Command-line values win (first match).
# Round 14 (owner review): straight centre claws, smaller U cups at the photo's 3.0 mm pitch with the stones raised,
# longer tapered points (shortened under the heart-arm stones), a thin flat heart foot bar, rounder pave bezels.
# Round 15 (owner review): heart foot is a V prong (two plates meeting at an outward ridge, cradling the point), wider
# rounded U rims that catch the light, U cups back near round-13 size, and a rounded women's-ring section on the plain band.
# Round 16 (owner review): U rims flush with the band face (no raised outline), shorter and wider points,
# rounder inner band edges (1.0 mm side stones moved out a touch, cup bottoms raised to clear them).
TUNED = ('--shtb 2.25 --cuflat 1 --cure 11.4 --cufl -2 --ri 0.6 --sri 0.6 --cubot 9.33 --shrib 1.0 '
         '--hm2footv 1 --hm2footw 1.8 --hm2footd 0.95 --hm2foott 0.42 --hm2footin 0.25 --hm2footz1 1.1 --hm2footz0 -2.4 --hm2foottilt 12 '
         '--cua 1.5 --pitch3 3.3 --cue 0.42 --cufr 0.32 --shpn 12 --shrob 1.25 --shrib 0.8 --shdome 0 --shr0 128 --shr1 158 '
         '--prongst 1 --pitch3 3.2 --cua 1.42 --lift3 -0.15 --hm2foot 1 --hm2footz0 -2.7 --hm2footz1 1.1 --cure 11.55 --cufl 15 --sro 0.9 --cutipgap 0.35 --bzseg 12 '
         '--tilt3 0 --yoff3 0 --sht 2.92 --u3c 0.57 --u3r 1.45 --u3b 1.0 --u3f 0 --claw3 0 --scr 0 --scl 0.4 '
         '--rimr 0.3 --rimrb 0.2 --rimh 0.2 --rimseg 10 --bzseg 8 --segseat 12 '
         '--cove3 0.2 --ro 0.5 --ri 0.45 --gd 0.0 --htilt 60 --legsink -0.6 --shtb 2.5 --bezel 0.05 --bezelz 0.0 --envfloor 0.02 --shm 176 --hairpin 1 --sro 1.02 --hpsb 0.62 --hprt 10.75 --hpdw 0.32 --hprho 1.1 --hpwb 0.3 --hpang 7 --hpmaxl 0.35 --hpnb 5 --hpnr 5 --hpwbt 0.3 --hpst 0.5 --hpgr 0 --hpm0 20 --hpm1 21 --cub 0.8 --cudrop 0.15 --curid 0 --curt 11.1 --cuw 0.3 --curcut 10.2 --cuplz 0.002 --cusq 1 --cusolid 1 --cufr 0.2 --cue 0.3 --cure 11.15 --cufl 6 --cucr 0.1 --cua 1.55 --hm2 1 --hm2st 1 --hm2tc 1.4 --hm2vd 0.55 --hm2vw 1.0 --hm2vy -2.2 --hm2ay1 -2.9 --hm2ax1 1.4 --hm2s0 0.4 --hm2pitch 1.5 --rough 0.16 --goldcol 0.80,0.79,0.76 --curib 1 --cubot 9.27 --curo 0.22 --cuft 0.24 --cuwb 0.18 --sri 0.56 --lift3 -0.6').split()
exec(compile(open(RINGKIT).read(), RINGKIT, 'exec'))   # shared helpers + arg(), argv, log(), constants

# --------------------------------------------------------------------------- design #1 parameters
# heart
H_SIZE, H_HC, H_G, H_HP, H_TS = 6.0, 0.85, 0.24, 2.40, 0.55
H_TILT = radians(float(arg('--htilt', 53)))         # lobe->point axis 50 deg from horizontal: lobes up/in at the gallery, point down/out, table faces up-outward
H_LOBE_XW, H_LOBE_ZW = float(arg('--hlx', 7.4)), float(arg('--hlz', 14.4))   # world X/Z of the heart's lobe end (top of the arm, at the rail end)
H_WALL_PITCH = 1.5
H_Y0, H_Y1 = float(arg('--hy0', -3.3)), float(arg('--hy1', 3.0))
H_WALL_SHIFT = float(arg('--wshift', -0.7))
LEG_DEG = float(arg('--legdeg', 46))
HM2 = int(arg('--hm2', 0)); HM2_D = float(arg('--hm2d', 0.65)); HM2_W = float(arg('--hm2w', 0.6)); HM2_YT = float(arg('--hm2yt', 2.6)); HM2_MIT = float(arg('--hm2mit', 1.4))
HM2_VD = float(arg('--hm2vd', 0.3)); HM2_VW = float(arg('--hm2vw', 0.8)); HM2_VY = float(arg('--hm2vy', -1.5)); HM2_VZ = float(arg('--hm2vz', 0.45)); HM2_CX = float(arg('--hm2cx', 3.0))
HM2_SINK = float(arg('--hm2sink', 0.5)); HM2_TR = float(arg('--hm2tr', 11.4)); HM2_PW = float(arg('--hm2pw', 2.2)); HM2_PT = float(arg('--hm2pt', 0.8)); HM2_PS = float(arg('--hm2ps', 0.5))
HM2_S0 = float(arg('--hm2s0', 0.5)); HM2_NW = int(arg('--hm2nw', 4)); HM2_STRAIGHT = int(arg('--hm2st', 0)); HM2_VB = float(arg('--hm2vb', 0.0)); HM2_TC = float(arg('--hm2tc', 0)); HM2_TCY = float(arg('--hm2tcy', 0.15)); HM2_TCW = float(arg('--hm2tcw', 0.7)); HM2_AX0 = float(arg('--hm2ax0', 4.2)); HM2_AY0 = float(arg('--hm2ay0', 2.0)); HM2_AX1 = float(arg('--hm2ax1', 1.3)); HM2_AY1 = float(arg('--hm2ay1', -3.3)); HM2_PLANK = int(arg('--hm2plank', 0)); HM2_CP = float(arg('--hm2cp', 1.5)); HM2_CZ = float(arg('--hm2cz', 0.0)); HM2_FX0 = float(arg('--hm2fx0', 0.95)); HM2_FY0 = float(arg('--hm2fy0', -1.75)); HM2_FX1 = float(arg('--hm2fx1', 0.55)); HM2_FY1 = float(arg('--hm2fy1', -3.3)); HM2_FZ1 = float(arg('--hm2fz1', -3.0)); HM2_FW = float(arg('--hm2fw', 0.8)); HM2_FT = float(arg('--hm2ft', 0.8)); HM2_PITCH = float(arg('--hm2pitch', 1.46)); HM2_PLST = int(arg('--hm2plst', 1)); HM2_FOOT = int(arg('--hm2foot', 0)); HM2_FOOTT = float(arg('--hm2foott', 0.75)); HM2_FOOTW = float(arg('--hm2footw', 1.6)); HM2_FOOTZ0 = float(arg('--hm2footz0', -3.6)); HM2_FOOTIN = float(arg('--hm2footin', 0.15)); HM2_FOOTZ1 = float(arg('--hm2footz1', -99)); HM2_FOOTV = int(arg('--hm2footv', 0)); HM2_FOOTD = float(arg('--hm2footd', 0.6)); HM2_FOOTTILT = float(arg('--hm2foottilt', 0.0)); HM2_FOOTOFF = float(arg('--hm2footoff', 0.55))
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
HP_ANG = float(arg('--hpang', 5)); HP_MAXL = float(arg('--hpmaxl', 0.18)); HP_NB = int(arg('--hpnb', 6)); HP_NR = int(arg('--hpnr', 6))
HP_WB = float(arg('--hpwb', 0.36)); HP_H = float(arg('--hph', 0.2)); HP_RO = float(arg('--hpro', 0.3)); HP_DW = float(arg('--hpdw', 0.7)); HP_END = float(arg('--hpend', 0.3))
HP_GY = float(arg('--hpgy', 0.1)); CU_A = float(arg('--cua', 1.35)); CU_B = float(arg('--cub', 1.05)); CU_RT = float(arg('--curt', 11.0)); CU_W = float(arg('--cuw', 0.22)); CU_RID = int(arg('--curid', 1)); CU_DROP = float(arg('--cudrop', 0.25)); HP_SHIFT = float(arg('--hpshift', 0.08)); CU_BOT = float(arg('--cubot', 9.6)); CU_FLUSH = int(arg('--cuflush', 1)); CU_SQ = int(arg('--cusq', 0)); CU_SOLID = int(arg('--cusolid', 0)); CU_E = float(arg('--cue', 0.46)); CU_FR = float(arg('--cufr', 0.28)); CU_Z = float(arg('--cuz', 0.004)); CU_FL = float(arg('--cufl', 0)); CU_RE = float(arg('--cure', 11.15)); CU_CR = float(arg('--cucr', 0.14)); CU_HALF = float(arg('--cuhalf', 0.35)); CU_RIB = int(arg('--curib', 0)); CU_HC = float(arg('--cuhc', 0.06)); CU_WB = float(arg('--cuwb', 0.18)); CU_FT = float(arg('--cuft', 0.12)); CU_PLZ = float(arg('--cuplz', 0.0)); CU_RO = float(arg('--curo', 0.3)); CU_RCUT = float(arg('--curcut', 10.45)); CU_PT = float(arg('--cupt', 0.8)); HP_SCMIN = float(arg('--hpscmin', 0.45)); HP_CR = float(arg('--hpcr', 0.36)); HP_WBT = float(arg('--hpwbt', 0.55)); HP_M0 = float(arg('--hpm0', 9.95)); HP_GD = float(arg('--hpgd', 0.3)); HP_GE = float(arg('--hpge', 0.3)); HP_M1 = float(arg('--hpm1', 10.25)); HP_W0 = float(arg('--hpw0', 10.25)); HP_W1 = float(arg('--hpw1', 10.85)); HP_G1 = float(arg('--hpg1', 0.05))
SH_PN = int(arg('--shpn', 5)); SH_ROB = float(arg('--shrob', 0.5)); SH_RIB = float(arg('--shrib', 0.45)); SH_DOME = float(arg('--shdome', 0.0)); SH_R0 = float(arg('--shr0', 140)); SH_R1 = float(arg('--shr1', 165))
RIM_CAPGAP = float(arg('--rimcapgap', 0.05)); CU_TIPGAP = float(arg('--cutipgap', 0.0)); CU_FLAT = int(arg('--cuflat', 0))
SIDE_SPAN = radians(130)      # 1.0 mm side-wall rows run +/-130 deg over the top
SIDE_R = 0.95                 # their centre, measured out from the inner surface
# gallery rail + arms
RAIL_ZT, RAIL_ZB, RAIL_IN = 14.50, 13.00, float(arg('--railin', -0.25))
RAIL_DEPTH = float(arg('--raild', 1.0))
ARM_S, ARM_ZT = float(arg('--arms', 1.0)), 12.85
ARM_BX, ARM_BY, ARM_BZ = 0.85, 1.45, 10.05
ARM_PITCH = 1.36
ARM_OFF = float(arg('--armoff', -0.60))
PRONG_STRAIGHT = int(arg('--prongst', 0)); PRONG_R = float(arg('--prongr', 0.55)); PRONG_TOP = float(arg('--prongtop', 0.25))

# --------------------------------------------------------------------------- heart side stones
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

# --------------------------------------------------------------------------- design #1 helpers
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


# design #1 registries and settings (the shared ones live in lib/ringkit.py)
BEADS = MB(); CLAWS = MB(); RIMS = MB(); PLATES = MB(); RIM_JOBS = []
CUPS = MB()
CUP_SEG = int(arg('--cupseg', 24))
ZZ_BIG = float(arg('--zzbig', 1.3))
RAIL_D = float(arg('--raild_stone', 1.0))
CUP_T = float(arg('--cupt', 0))
CUP_DROP = float(arg('--cupdrop', 0.22))
COVE3 = float(arg('--cove3', 0.30))
SIDE_R_IN, SIDE_R_OUT = float(arg('--sri', 0.55)), float(arg('--sro', 0.98))

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
    def profile(t, w, n=SH_PN, rnd=0.0):
        # rnd 0..1: the plain (stone-free) bottom of the band blends into a soft, rounded women's-ring section:
        # big outer fillets, a gently domed outer face and rounder inner edges
        ro = SH_RO + (min(SH_ROB, w - 0.05, t / 2) - SH_RO) * rnd; ri = SH_RI + (SH_RIB - SH_RI) * rnd; dome = SH_DOME * rnd; pts = []
        corners = [((R_IN + t - ro - dome, w - ro), ro, 0), ((R_IN + ri, w - ri), ri, 90), ((R_IN + ri, -w + ri), ri, 180), ((R_IN + t - ro - dome, -w + ro), ro, 270)]
        for ci, (c, r, a0) in enumerate(corners):
            if ci == 0:   # domed outer face from the -w corner over to the +w corner (drawn before corner 0)
                yy0 = w - ro
                for k in range(1, 2 * n):
                    yy = -yy0 + 2 * yy0 * k / (2 * n); pts.append((R_IN + t - dome + dome * (1 - (yy / max(yy0, 1e-6)) ** 2) - 0.0, yy))
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
        secs.append([Vector((r * sin(phi), y, r * cos(phi))) for (r, y) in profile(thick(phi), half_w(phi), rnd=smooth(radians(SH_R0), radians(SH_R1), abs(phi)))])
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
                                lim = d - o['D'] / 2 - RIM_CAPGAP
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
        # Round 10: every 3.0 stone sits INSIDE its own deep round U cup (opening outward); neighbouring cups rise into
        # long tapered points between the stones. Built directly as one smooth, tangent-continuous centre-line.
        av = lambda ph: Vector((sin(ph), 0, cos(ph))); ev = lambda ph: Vector((cos(ph), 0, -sin(ph)))
        rc0 = [Vector((st['center'].x, 0, st['center'].z)).length for st in row]
        def cup(k, n=24):
            Bk = CU_B; c = av(phs[k]) * (CU_BOT + Bk)
            return [c + ev(phs[k]) * (CU_A * cos(radians(th))) + av(phs[k]) * (Bk * sin(radians(th)))
                    for th in [180 + 180 * i / n for i in range(n + 1)]]
        def tip_arc(j, a0_, a1_, n=8):
            c = av(posts[j]) * CU_RT
            return [c + ev(posts[j]) * (CU_W * cos(radians(a))) + av(posts[j]) * (CU_W * sin(radians(a)))
                    for a in [a0_ + (a1_ - a0_) * i / n for i in range(n + 1)]]
        def bez(P0, T0, P3, T3, n=10):
            L = (P3 - P0).length / 2.2; P1 = P0 + T0 * L; P2 = P3 - T3 * L
            return [P0 * (1 - u) ** 3 + P1 * 3 * u * (1 - u) ** 2 + P2 * 3 * u * u * (1 - u) + P3 * u ** 3 for u in [i / n for i in range(n + 1)]]
        fine = []
        def add(L):
            for q in L:
                if not fine or (q - fine[-1]).length > 1e-6: fine.append(q)
        nS = len(row)
        for j in range(nS + 1):
            if j > 0:     # up the right wall of cup j-1 to the point
                add(bez(cup(j - 1)[-1], av(phs[j - 1]), av(posts[j]) * CU_RT - ev(posts[j]) * CU_W, av(posts[j])))
            add(tip_arc(j, 180 if j > 0 else 90, 0 if j < nS else 90))
            if j < nS:    # down from the point into cup j
                add(bez(av(posts[j]) * CU_RT + ev(posts[j]) * CU_W, -av(posts[j]), cup(j)[0], -av(phs[j])))
                add(cup(j))
        if CU_SQ:
            # Round 11: deep U cups (round bottom, straight parallel walls) and long fingers with squared-off ends
            fine = []
            cc = lambda k: av(phs[k]) * (CU_BOT + CU_A)
            fl = radians(CU_FL)
            def cupc(k, n=28):
                return [cc(k) + ev(phs[k]) * (CU_A * cos(radians(th))) + av(phs[k]) * (CU_A * sin(radians(th))) for th in [180 + CU_FL + (180 - 2 * CU_FL) * i / n for i in range(n + 1)]]
            def re_post(j):   # shorter point where a heart-arm stone sits right above the point's tip
                tipc = av(posts[j]) * CU_RE; near = 9.0
                for o in STONES:
                    if o.get('target') != 'Shank' and o['kind'] == 'round':
                        c_ = o['center']; near = min(near, (Vector((c_.x, 0, c_.z)) - tipc).length - o['D'] / 2)
                return CU_RE - max(0.0, CU_TIPGAP - near)
            REJ = [re_post(j) for j in range(nS + 1)]
            def wall_s(E, d, j=None):   # distance along d from E to radius CU_RE
                R_ = REJ[j] if j is not None else CU_RE
                b_ = E.dot(d); c_ = E.dot(E) - R_ ** 2; return -b_ + sqrt(max(0.0, b_ * b_ - c_))
            def qb(P0, P1, P2, n=6):
                return [P0 * (1 - u) ** 2 + P1 * 2 * u * (1 - u) + P2 * u * u for u in [i / n for i in range(n + 1)]]
            def line(P, Q, n):
                return [P + (Q - P) * (i / n) for i in range(n + 1)]
            for j in range(nS + 1):
                if j > 0:
                    El = cc(j - 1) + ev(phs[j - 1]) * (CU_A * cos(fl)) - av(phs[j - 1]) * (CU_A * sin(fl)); dl = av(phs[j - 1]) * cos(fl) + ev(phs[j - 1]) * sin(fl); sl = wall_s(El, dl, j); Le = El + dl * sl
                if j < nS:
                    Er = cc(j) - ev(phs[j]) * (CU_A * cos(fl)) - av(phs[j]) * (CU_A * sin(fl)); dr = av(phs[j]) * cos(fl) - ev(phs[j]) * sin(fl); sr = wall_s(Er, dr, j); Re = Er + dr * sr
                if j == 0: Le = Re - ev(posts[j]) * CU_HALF; El = None
                if j == nS: Re = Le + ev(posts[j]) * CU_HALF; Er = None
                ue = (Re - Le).normalized(); cr = min(CU_CR, (Re - Le).length / 2.5)
                if El is not None:
                    add(line(El, Le - dl * cr, 8)); add(qb(Le - dl * cr, Le, Le + ue * cr))
                else:
                    add([Le + ue * cr])
                if Er is not None:
                    add(line(Le + ue * cr, Re - ue * cr, 4)); add(qb(Re - ue * cr, Re, Re - dr * cr)); add(line(Re - dr * cr, Er, 8)); add(cupc(j))
                else:
                    add(line(Le + ue * cr, Re, 3))
        fine = [Vector((v.x, 0, v.z)) for v in fine]
        keep = [fine[0]]; acc = 0.0
        for i in range(1, len(fine) - 1):
            t0 = fine[i] - fine[i - 1]; t1 = fine[i + 1] - fine[i]
            if t0.length > 1e-9 and t1.length > 1e-9: acc += t0.angle(t1)
            if acc > radians(HP_ANG) or (fine[i] - keep[-1]).length > HP_MAXL: keep.append(fine[i]); acc = 0.0
        keep.append(fine[-1])
        dpol = [(atan2(v.x, v.z), v.length) for v in keep]
        # notch cutter: everything outside the centre-line (the cups and the space beyond the post tips), through the band
        hw = SH_W + 0.6
        f0, f1 = dpol[0][0], dpol[-1][0]
        poly = dpol + [(f1 + (f0 - f1) * i / 24, 13.5) for i in range(25)]
        cmb = MB(); n = len(poly)
        A = [cmb.vert((side * r * sin(ph), -hw, r * cos(ph))) for (ph, r) in poly]
        B = [cmb.vert((side * r * sin(ph), hw, r * cos(ph))) for (ph, r) in poly]
        cmb.face(*A); cmb.face(*reversed(B))
        for i in range(n): cmb.face(A[i], A[(i + 1) % n], B[(i + 1) % n], B[i])
        CUTTERS.setdefault('Shank', MB()).extend(cmb)
        # rim cross-section (b across the path, + = open/cut side; h out of the band face): on the metal side it rises
        # out of the face with zero slope (no seam), crowns, and rolls over a full round edge down into the cut
        def make_prof(m):
            # m = 0: metal side blends flat into the band face (cup bottom); m = 1: metal side is a full round roll too (legs/tip, facing the slot)
            pr = []
            for i in range(HP_NB + 1):
                u = -1 + i / HP_NB; th = radians(90 * (1 + u))           # u=-1 -> outer edge, u=0 -> crown
                sk = (u * HP_WB, HP_H * (1 - u * u) ** 2)
                rl = (-HP_RO * sin(radians(90) - th) if False else -HP_RO * cos(radians(90 * (1 + u))) , HP_H - HP_RO + HP_RO * sin(radians(90 * (1 + u))))
                pr.append((sk[0] * (1 - m) + rl[0] * m, sk[1] * (1 - m) + rl[1] * m))
            for i in range(1, HP_NR + 1):
                th = radians(90 * i / HP_NR); pr.append((HP_RO * sin(th), HP_H - HP_RO + HP_RO * cos(th)))
            pr += [(HP_RO, -HP_DW), (-HP_WB * 0.3 * (1 - m) - HP_RO * m, -HP_DW), (-HP_WB * 0.85 * (1 - m) - HP_RO * m, -0.04 * (1 - m) - HP_DW * 0.5 * m)]
            return pr
        PROFS = [make_prof(k / 8) for k in range(9)]
        if CU_SOLID:
            # Round 12: NO raised border. The gallery is one solid, flush metal body; its outer edge is a soft polished
            # fillet (radius CU_FR) so the light itself draws the thin bright line. Top sits a hair above the band face.
            E_, R_, z_ = CU_E, CU_FR, CU_Z
            fp = [(-CU_WB, -0.02), (-CU_WB * 0.6, z_), (E_ - R_, z_)]
            if CU_FLAT:   # round 16: the metal side tucks just under the band face, so the face runs flat to the U edge (no seam, no ridge)
                fp = [(-CU_WB, -0.10), (-0.03, -0.015), (0.0, 0.0), (E_ - R_, 0.0)]; z_ = 0.0
            for i in range(1, 9):
                th = radians(90 * i / 8); fp.append((E_ - R_ + R_ * sin(th), z_ - R_ + R_ * cos(th)))
            fp += [(E_, -HP_DW - R_), (0.05, -HP_DW - R_), (-CU_WB * 0.8, -0.05)]
            PROFS = [fp] * 9
        elif CU_RIB:
            # wide flat ribbon: zero-slope blend on the metal side, broad bright crowned top, soft rounded edge into the cut
            Hc = CU_HC
            fp = [(-CU_WB, -0.02), (-CU_WB * 0.66, Hc * 0.45), (-CU_WB * 0.33, Hc * 0.9), (0.0, Hc), (CU_FT, Hc * 0.97)]
            for i in range(1, HP_NR + 1):
                th = radians(90 * i / HP_NR); fp.append((CU_FT + CU_RO * sin(th), Hc - CU_RO + CU_RO * cos(th)))
            fp += [(CU_FT + CU_RO, -HP_DW - CU_RO), (0.05, -HP_DW - CU_RO), (-CU_WB * 0.8, -0.05)]
            PROFS = [fp] * 9
        elif CU_FLUSH:
            # flush rolled edge: flat (coplanar) on the metal side, a full quarter-round roll over into the cut
            fp = [(-HP_WB, -0.03), (-HP_WB * 0.5, -0.004), (0.0, 0.0)]
            for i in range(1, HP_NR + 1):
                th = radians(90 * i / HP_NR); fp.append((CU_RO * sin(th), -CU_RO + CU_RO * cos(th)))
            fp += [(CU_RO, -HP_DW - CU_RO), (-HP_WB * 0.5, -HP_DW - CU_RO)]
            PROFS = [fp] * 9
        Pw = [Vector((side * v.x, 0, v.z)) for v in keep]
        nP = len(Pw)
        # which in-plane normal points into the cut: test at the bottom of the first cup (cut side = radially outward)
        ic = min(range(nP), key=lambda i: abs(dpol[i][0] - phs[0]) + abs(dpol[i][1] - HP_RC))
        Tc = (Pw[min(ic + 1, nP - 1)] - Pw[max(ic - 1, 0)]).normalized()
        osgn = 1 if Vector((0, 1, 0)).cross(Tc).dot(Vector((Pw[ic].x, 0, Pw[ic].z)).normalized()) > 0 else -1
        # taper both free ends to a rounded nose
        cum = [0.0]
        for i in range(1, nP): cum.append(cum[-1] + (Pw[i] - Pw[i - 1]).length)
        Lt = cum[-1]
        def end_sc(i):
            e = min(cum[i], Lt - cum[i]); return 1.0 if e >= HP_END else max(0.08, sqrt(max(0.0, 1 - ((HP_END - e) / HP_END) ** 2)))
        caps = [o for o in STONES if o.get('target') != 'Shank']
        for ys in (-1, 1):
            secs = []; scs = [end_sc(i) for i in range(nP)]; shifts = [0.0] * nP
            def section(i, sc_, sh_):
                T = (Pw[min(i + 1, nP - 1)] - Pw[max(i - 1, 0)]); T.y = 0; T.normalize()
                Bv = Vector((0, 1, 0)).cross(T) * osgn
                ph = atan2(abs(Pw[i].x), Pw[i].z); yf = ys * half_w(ph)
                rr_ = Vector((Pw[i].x, 0, Pw[i].z)).normalized()
                base = Pw[i] - rr_ * sh_
                rI = Pw[i].length; u_ = min(1.0, max(0.0, (rI - HP_W0) / (HP_W1 - HP_W0))); u_ = u_ * u_ * (3 - 2 * u_)
                wf = 1 + (HP_WBT / HP_WB - 1) * u_      # wider skirt near the tip: the two legs' skirts meet and close the slot smoothly
                v_ = min(1.0, max(0.0, (rI - HP_M0) / (HP_M1 - HP_M0))); v_ = v_ * v_ * (3 - 2 * v_)
                prof = PROFS[round(v_ * 8)] if HP_M1 > HP_M0 else PROFS[0]
                return [base + Bv * (b_ * sc_ * (wf if b_ < 0 else 1.0)) + Vector((0, yf + ys * h_ * sc_, 0)) for (b_, h_) in prof]
            # dip / thin locally under the heart-arm cap stones
            for _ in range(6):
                hit = False
                for i in range(nP):
                    sec = section(i, scs[i], shifts[i])
                    for o in caps:
                        if (Pw[i] - o['center']).length > o['D'] + 1.5: continue
                        if min((q - o['center']).length for q in sec) < o['D'] / 2 + 0.05:
                            hit = True
                            if scs[i] > HP_SCMIN: scs[i] *= 0.85
                            else: shifts[i] += HP_SHIFT
                if not hit: break
                scs = [min(scs[i], (scs[max(i - 1, 0)] + scs[i] + scs[min(i + 1, nP - 1)]) / 3 + 0.03) for i in range(nP)]
                shifts = [max(shifts[i], (shifts[max(i - 1, 0)] + shifts[i] + shifts[min(i + 1, nP - 1)]) / 3 - 0.02) for i in range(nP)]
            for i in range(nP): secs.append(section(i, scs[i], shifts[i]))
            RIMS.extend(loft(secs, closed_v=False, cap=True))
            if CU_FLUSH:
                # solid plate under each point (flush with the band face) so the tapered point is one piece of metal
                for j in range(nS + 1):
                    idx = [i for i, q in enumerate(fine) if q.length >= CU_RCUT and abs(atan2(q.x, q.z) - posts[j]) < D_ * 0.5]
                    if len(idx) < 3: continue
                    seg_ = [fine[i] for i in range(idx[0], idx[-1] + 1)]
                    segr = []
                    for q in seg_:
                        if not segr or (q - segr[-1]).length > 0.04: segr.append(q)
                    if len(segr) < 3: continue
                    ph_ = posts[j]; yf = half_w(ph_)
                    pm = MB(); n_ = len(segr)
                    A_ = [pm.vert((side * q.x, ys * (yf + (CU_Z if CU_SOLID else -CU_PLZ)), q.z)) for q in segr]
                    B_ = [pm.vert((side * q.x, ys * (yf - CU_PT), q.z)) for q in segr]
                    pm.face(*A_); pm.face(*reversed(B_))
                    for i in range(n_): pm.face(A_[i], A_[(i + 1) % n_], B_[(i + 1) % n_], B_[i])
                    (PLATES if CU_SOLID else RIMS).extend(pm)
            if CU_RID:
                # flat-topped ridge filling each point between the two cup walls, flush with their crowns -> one solid tapered point
                for j in range(1, nS):
                    ra = CU_BOT + CU_B - CU_DROP; rb_ = CU_RT + CU_W * 0.7
                    ap, ep = av(posts[j]), ev(posts[j])
                    ap = Vector((side * ap.x, 0, ap.z)); ep = Vector((side * ep.x, 0, ep.z))
                    rs = [ra + (rb_ - ra) * i / 14 for i in range(15)]
                    rsecs = []
                    for i, rr in enumerate(rs):
                        # half-width of the flat top: distance from the post line to the wall centre-lines at this radius
                        apu, epu = av(posts[j]), ev(posts[j])
                        cand = [q for q in fine if abs(q.length - rr) < 0.05 and abs(atan2(q.x, q.z) - posts[j]) < D_ * 0.5]
                        hwid = min([abs(q.dot(epu) - 0.0) for q in cand] or [CU_W]); hwid = min(hwid, 0.7)
                        e = min(rr - ra, rb_ - rr); f = 1.0 if e >= 0.25 else max(0.05, sqrt(max(0.0, 1 - ((0.25 - e) / 0.25) ** 2)))
                        ph_ = posts[j]; yf = ys * half_w(ph_); c = ap * rr
                        pr_ = [(-hwid - 0.18, 0.0), (-hwid - 0.08, HP_H * 0.7), (-hwid, HP_H), (0, HP_H), (hwid, HP_H), (hwid + 0.08, HP_H * 0.7), (hwid + 0.18, 0.0), (hwid * 0.5, -0.25), (-hwid * 0.5, -0.25)]
                        rsecs.append([c + ep * bb + Vector((0, yf + ys * hh * f - ys * (1 - f) * 0.05, 0)) for (bb, hh) in pr_])
                    RIMS.extend(loft(rsecs, closed_v=False, cap=True))
            # smooth rounded slot groove down the middle of every U-prong (hemispherical ends)
            if HP_GR > 0:
                # smooth rounded slot down the middle of every U-prong: elliptical section (HP_GR across, HP_GD deep),
                # tapered to rounded ends; it runs from the round tip down to the 1.3 stone nestled in its open bottom
                for j in range(1, len(row)):
                    r0, r1 = HP_G0, HP_RT + HP_G1; ng = 18; E = HP_GE
                    nrm_y = Vector((0, ys, 0)); secs_g = []
                    rad_ = Vector((side * sin(posts[j]), 0, cos(posts[j]))); tg_ = Vector((0, 1, 0)).cross(rad_).normalized()
                    for i in range(ng + 1):
                        rr = r0 + (r1 - r0) * i / ng; e = min(rr - r0, r1 - rr)
                        f = 1.0 if e >= E else sqrt(max(0.0, 1 - ((E - e) / E) ** 2)); f = max(f, 0.03)
                        c = rad_ * rr + Vector((0, ys * (half_w(posts[j]) + HP_GY), 0))
                        secs_g.append([c + tg_ * (HP_GR * f * cos(2 * pi * k / 16)) + nrm_y * ((HP_GD + HP_GY) * f * sin(2 * pi * k / 16)) for k in range(16)])
                    CUTTERS.setdefault('Shank', MB()).extend(loft(secs_g, closed_v=False, cap=True))
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
        if PRONG_STRAIGHT:
            # reference front view: each claw rises as one straight post from the rail, leaning slightly in toward
            # the stone, and only hooks over at the very top (no bulge around the girdle)
            Pt = P + PRONG_TOP * n + Z(Z_GT + 0.45)
            mids = [Pr + (Pt - Pr) * u for u in (0.33, 0.66)]
            pr.extend(tube([A + Z(0.25), Pr] + mids + [Pt, Ptip], [PRONG_R, PRONG_R, PRONG_R, PRONG_R * 0.98, PRONG_R * 0.94, PRONG_R * 0.75], seg=16))
        else:
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
    HMI = HM.inverted()
    if HM2:
        # Round 13: heart-shaped basket. Two solid walls follow the heart's outline (offset outward) from the lobes down
        # to the point, meet in a V under the point, a solid V claw grips the point over the girdle, and one flat
        # polished plank runs from the V down onto the shank (as in the reference side/front views).
        def opath(d, ymax, ymin=-9):
            i0 = min(range(H_N), key=lambda i: H_PTS[i][1]); st_ = 1 if H_PTS[(i0 + 1) % H_N][0] > 0 else -1
            rs = []; i = i0
            for _ in range(H_N):
                x, y = H_PTS[i % H_N]
                if y > ymax or x < -0.01: break
                if x > 0.02 and y >= ymin: rs.append((x, y))
                i += st_
            rs.reverse(); out = []
            for i, (x, y) in enumerate(rs):
                x0_, y0_ = rs[max(i - 1, 0)]; x1_, y1_ = rs[min(i + 1, len(rs) - 1)]
                tx, ty = x1_ - x0_, y1_ - y0_; L = math.hypot(tx, ty) or 1
                nx, ny = -ty / L, tx / L
                if nx * x + ny * (y + 0.0) < 0: nx, ny = -nx, -ny
                out.append((x + nx * d, y + ny * d))
            return out
        def vpath(d, ymax, ymin=-9):
            r_ = opath(d, ymax, ymin); r_ = [q for q in r_ if q[0] > 0.12]
            tip = (0.0, -H_SIZE / 2 - d * HM2_MIT)
            return [(-x, y) for (x, y) in r_] + [tip] + list(reversed(r_))
        def lsweep(path2, W, z0, z1, rr=0.22, k=3):
            zc_, T2 = (z0 + z1) / 2, z1 - z0; rr = min(rr, W / 2 - 0.02, T2 / 2 - 0.02); secs = []
            sec = []
            for (cx, cy, a0) in ((W / 2 - rr, T2 / 2 - rr, 0), (-W / 2 + rr, T2 / 2 - rr, 90), (-W / 2 + rr, -T2 / 2 + rr, 180), (W / 2 - rr, -T2 / 2 + rr, 270)):
                for i in range(k + 1):
                    a = radians(a0 + 90 * i / k); sec.append((cx + rr * cos(a), cy + rr * sin(a)))
            n_ = len(path2)
            for i in range(n_):
                x0_, y0_ = path2[max(i - 1, 0)]; x1_, y1_ = path2[min(i + 1, n_ - 1)]
                tx, ty = x1_ - x0_, y1_ - y0_; L = math.hypot(tx, ty) or 1; wx, wy = ty / L, -tx / L
                px, py = path2[i]
                secs.append([hl(px + wx * u, py + wy * u, zc_ + v) for (u, v) in sec])
            return loft(secs, closed_v=False, cap=True)
        if HM2_STRAIGHT:
            # straight splayed arms (reference side view): wide under the lobes, converging onto the V claw at the point
            WPATH = [(HM2_AX0 + (HM2_AX1 - HM2_AX0) * i / 12, HM2_AY0 + (HM2_AY1 - HM2_AY0) * i / 12) for i in range(13)]
            for sx_ in (-1, 1): arm.extend(lsweep([(sx_ * x, y) for (x, y) in WPATH][::sx_], HM2_W, ZB, ZT))
            if HM2_FOOT:
                # reference: one flat polished bar across the heart's point (edge-on from the front, ~0.75 mm thick),
                # from just above the crown straight down past the pavilion to the band
                yt = -H_SIZE / 2 - HM2_FOOTT / 2 + HM2_FOOTIN
                z1_ = HM2_FOOTZ1 if HM2_FOOTZ1 > -50 else HM2_VZ
                if HM2_FOOTV:
                    # round 15: the foot is a V prong (two plates meeting at a ridge): the open V cradles the heart's point
                    # and the ridge faces outward; it runs straight down past the pavilion to the band
                    Wv, Dv, Tv = HM2_FOOTW, HM2_FOOTD, HM2_FOOTT
                    ai = -H_SIZE / 2 + HM2_FOOTIN; ao = ai - Tv * 1.25
                    # two rounded plates whose outer faces form the chevron; they overlap along the ridge.
                    # The ridge points horizontally outward (world +X for this heart), as the reference side view shows it.
                    dy_ = -math.tan(radians(HM2_FOOTTILT)) * (z1_ - HM2_FOOTZ0)
                    Tp, Bp = hl(0, -H_SIZE / 2, z1_), hl(0, -H_SIZE / 2 + dy_, HM2_FOOTZ0)
                    ax_ = (Bp - Tp).normalized()
                    rr_ = Vector((1, 0, 0)); rr_ = (rr_ - ax_ * rr_.dot(ax_)).normalized(); ss_ = ax_.cross(rr_).normalized()
                    for sx_ in (-1, 1):
                        u_ = (ss_ * (sx_ * Wv / 2) - rr_ * Dv); L_ = u_.length; u_ = u_ / L_
                        n_ = -(ss_ * (sx_ * Dv) + rr_ * (Wv / 2)).normalized()      # into the V
                        off = rr_ * HM2_FOOTOFF + u_ * (L_ / 2) + n_ * (Tv / 2)
                        mbp, _, _, _ = bar(Tp + off, Bp + off, n_, L_ + Tv * 0.6, Tv, rr=min(SOFT_RR, Tv / 2 - 0.02))
                        arm.extend(mbp)
                else:
                    arm.extend(lbar((-HM2_FOOTW / 2, yt, (z1_ + HM2_FOOTZ0) / 2), (HM2_FOOTW / 2, yt, (z1_ + HM2_FOOTZ0) / 2), HM2_FOOTT, z1_ - HM2_FOOTZ0))
            else:
                VP = vpath(HM2_VD, HM2_VY)
                arm.extend(lsweep(VP, HM2_VW, ZB + HM2_VB, HM2_VZ, rr=0.28))
            if HM2_TC > 0:   # solid top cap across the lobes (front view: thick bar at the heart's upper end, meeting the rail)
                arm.extend(lbar((-HM2_TC, H_SIZE / 2 + HM2_TCY, (ZT + HM2_VZ) / 2 - 0.3), (HM2_TC, H_SIZE / 2 + HM2_TCY, (ZT + HM2_VZ) / 2 - 0.3), HM2_TCW, HM2_VZ - ZT + 0.6))
        else:
            WPATH = vpath(HM2_D, HM2_YT)
            arm.extend(lsweep(WPATH, HM2_W, ZB, ZT))
        for sx_ in ((-1, 1) if not HM2_STRAIGHT else ()):   # V fork: two flat polished bars grip the point over the crown and run down onto the band
            arm.extend(lbar((sx_ * HM2_FX0, HM2_FY0, HM2_VZ), (sx_ * HM2_FX1, HM2_FY1, HM2_FZ1), HM2_FW, HM2_FT, n=Vector((0, 1, 0))))
        arm.extend(lbar((-HM2_CX, Y1 + 0.25, zc), (HM2_CX, Y1 + 0.25, zc), 0.5, T_))   # inner end cap under the lobes (meets the rail)
    for s in ((-1, 1) if not HM2 else ()):
        arm.extend(lbar((s * (WX0 + WX1) / 2, Y0, zc), (s * (WX0 + WX1) / 2, Y1, zc), WX1 - WX0, T_))
    if not HM2:
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
            r0_ = (hl(q.x + sgn * (HM2_D + 0.05), q.y, ZT - 0.5), hl(q.x + sgn * (HM2_D - 0.15), q.y, ZT + 0.5)) if HM2 else (hl(sgn * (WX0 + 0.35), q.y, ZT - 0.5), hl(sgn * (WX0 + 0.1), q.y, ZT + 0.5))
            if HM2 and yq < 0: continue      # the V claw now holds the lower sides
            hp_.extend(tube([r0_[0], r0_[1],
                             hl(q.x * 1.04, q.y, H_G / 2 + 0.35), hl(q.x * 0.90, q.y * 0.90, hzc(0.90) + 0.08)], [0.42, 0.42, 0.36, 0.16], seg=12))
    q = Vector((0, -H_SIZE / 2))
    if not HM2: hp_.extend(tube([hl(0, Y0 - 0.3, zc + 0.6), hl(0, Y0 - 0.1, ZT + 0.9), hl(0, -3.05, H_G / 2 + 0.35), hl(0, -2.75, hzc(0.9) + 0.08)], [0.45, 0.42, 0.36, 0.16], seg=12))
    hmetal['HeartProngs'] = hp_
    # support legs: from the outer end cap down onto the nearest shank claw pair (the L-bar seen in the front view)
    posts = MB()
    leg_c = hl(0, Y0 - CAP_O / 2, ZB + 0.3)
    tt = tooth_tips[1]
    ang = lambda P: atan2(P.x, P.z)
    bi = min(range(len(tt)), key=lambda i: abs(ang((tt[i][0] + tt[i][1]) / 2) - radians(LEG_DEG)))
    PLANK = None
    if HM2 and HM2_PLANK:
        a3s = sorted(atan2(o['center'].x, o['center'].z) for o in STONES if o['kind'] == 'round' and o['D'] == 3.0 and o['center'].x > 0)
        mids = [(a3s[i] + a3s[i + 1]) / 2 for i in range(len(a3s) - 1)]
        pa = min(mids, key=lambda m: abs(m - radians(LEG_DEG)))
        tgt = Vector((sin(pa), 0, cos(pa))) * HM2_TR
        A_ = hl(0, -H_SIZE / 2 - HM2_D * HM2_MIT + 0.35, (ZB + HM2_VZ) / 2 - 0.4)
        dd = (tgt - A_).normalized(); nn = Vector((0, 1, 0)).cross(dd).normalized()
        if nn.dot(Vector((A_.x, 0, A_.z)).normalized()) < 0: nn = -nn
        pmb, _, _, _ = bar(A_ - dd * 0.2, tgt, nn, HM2_PW, HM2_PT, rr=0.28)
        arm.extend(pmb); PLANK = (A_, tgt, nn); log('plank', tuple(round(v, 2) for v in A_), tuple(round(v, 2) for v in tgt), 'len', round((tgt - A_).length, 2))
    for tip in ((tt[bi] if not SCALLOP else [min(tt[bi], key=lambda P: P.y)]) if not HM2 else []):
        tgt = tip - Vector((sin(ang(tip)), 0, cos(ang(tip)))) * LEG_SINK + Vector((0, LEG_DY, 0))
        posts.extend(tube([leg_c, (leg_c + tgt) / 2, tgt], [LEG_R, LEG_R * 0.92, LEG_R * 0.92], seg=12, tip=False))
    hmetal['HeartPosts'] = posts
    log('heart centre', tuple(round(x, 2) for x in H_CENTER), 'lobe tip', tuple(round(x, 2) for x in hl(0, 3, 0)),
        'point', tuple(round(x, 2) for x in hl(0, -3, 0)), 'outer cap', tuple(round(x, 2) for x in hl(0, Y0 - 0.9, 0)), 'leg->boundary', bi,
        'deg', round(math.degrees(ang((tt[bi][0] + tt[bi][1]) / 2)), 1))
    # 1.4 mm stones: 4 on each wall's outer face + 3 on the outer end cap (11 per heart)
    hst = []
    if HM2:
        # 5 x 1.4 on the outer face of each basket wall + 1 on the plank's outer face (11 per heart, as before)
        rp = [q for q in WPATH if q[0] > 0.05]; rp.sort(key=lambda q: -q[1])
        cum_ = [0.0]
        for i in range(1, len(rp)): cum_.append(cum_[-1] + math.hypot(rp[i][0] - rp[i - 1][0], rp[i][1] - rp[i - 1][1]))
        def at(sv):
            for i in range(1, len(rp)):
                if cum_[i] >= sv:
                    u = (sv - cum_[i - 1]) / max(1e-9, cum_[i] - cum_[i - 1]); x0_, y0_ = rp[i - 1]; x1_, y1_ = rp[i]
                    tx, ty = x1_ - x0_, y1_ - y0_; L = math.hypot(tx, ty) or 1
                    nx, ny = ty / L, -tx / L
                    if nx < 0: nx, ny = -nx, -ny
                    return x0_ + u * tx, y0_ + u * ty, nx, ny
            return rp[-1][0], rp[-1][1], 1.0, 0.0
        for k in range(HM2_NW):
            x_, y_, nx, ny = at(HM2_S0 + k * HM2_PITCH)
            for s in (-1, 1):
                hst.append((Vector((s * (x_ + nx * (HM2_W / 2 - 0.04)), y_ + ny * (HM2_W / 2 - 0.04), zc)), Vector((s * nx, ny, 0)), s))
        if PLANK and HM2_PLST:
            A_, B_, nn = PLANK; mid = A_ + (B_ - A_) * HM2_PS
            hst.append((HMI @ (mid + nn * (HM2_PT / 2 - 0.04)), HMI.to_3x3() @ nn, 0))
        else:
            for k in (-1, 0, 1):   # 3 on the inner end cap, facing the centre head
                hst.append((Vector((k * HM2_CP, Y1 + 0.5 - 0.04, zc + HM2_CZ)), Vector((0, 1, 0)), 0))
    for s in ((-1, 1) if not HM2 else ()):
        for k in range(4):
            y = (Y0 + Y1) / 2 + H_WALL_SHIFT + (k - 1.5) * H_WALL_PITCH
            hst.append((Vector((s * (WX1 - 0.04), y, zc)), Vector((s, 0, 0)), s))
    for k in ((-1, 0, 1) if not HM2 else ()):
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
        if HM2: CUTTERS.setdefault('HeartArm', MB()).extend(heart_stone().xform(STONES[-1]['M'] @ Matrix.Scale(1.03, 4)))
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
    if CU_SOLID and len(PLATES.v) and 'ShankRims' in objs:
        # fuse the point plates and the filleted edge into ONE solid gallery body (no coplanar double surfaces)
        pl = to_obj('gal_plates', PLATES, GOLD)
        mod = objs['ShankRims'].modifiers.new('fuse', 'BOOLEAN'); mod.operation = 'UNION'; mod.solver = 'EXACT'
        mod.object = pl; mod.use_self = True; mod.use_hole_tolerant = True
        bpy.context.view_layer.objects.active = objs['ShankRims']
        bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(pl, do_unlink=True)
        objs['ShankRims'].data.shade_smooth(); objs['ShankRims'].data.set_sharp_from_angle(angle=radians(50))
        wn = objs['ShankRims'].modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True; wn.weight = 50; wn.mode = 'FACE_AREA'
        bpy.ops.object.modifier_apply(modifier=wn.name)
        log('gallery fused', len(objs['ShankRims'].data.polygons))
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


if "--nobuild" not in argv: main()

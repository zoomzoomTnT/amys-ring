# blender -b ring.blend -P check_fit.py : stone/metal contact report
import bpy, bmesh
from mathutils.bvhtree import BVHTree
def bvh(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); t = BVHTree.FromBMesh(bm); return t, bm
metal = {o.name: bvh(o)[0] for o in bpy.data.objects if o.type == 'MESH' and o.data.materials[0].name.startswith('White')}
dias = [o for o in bpy.data.objects if o.type == 'MESH' and o.data.materials[0].name == 'Diamond']
for o in dias:
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    # loose parts
    seen = set(); parts = []
    for f in bm.faces:
        if f.index in seen: continue
        stack = [f]; comp = []; seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); stack.append(h)
        parts.append(comp)
    floating = 0; touch = {}
    for comp in parts:
        verts = list({v for f in comp for v in f.verts}); idx = {v: i for i, v in enumerate(verts)}
        t = BVHTree.FromPolygons([v.co for v in verts], [[idx[v] for v in f.verts] for f in comp])
        hit = [k for k, m in metal.items() if t.overlap(m)]
        if not hit: floating += 1
        for k in hit: touch[k] = touch.get(k, 0) + 1
    print('CHECK', o.name, 'stones', len(parts), 'floating', floating, 'touches', touch)

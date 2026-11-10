# Render gallery images (front, top) on a clean white background.
# usage: blender -b ring.blend -P render_gallery.py -- OUTDIR RES SAMPLES
import bpy, sys, os
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(bpy.data.filepath), 'gallery')
RES = int(argv[1]) if len(argv) > 1 else 1600
SAMPLES = int(argv[2]) if len(argv) > 2 else 192
VIEWS = argv[3].split(',') if len(argv) > 3 else ['front', 'top']
sc = bpy.context.scene
sc.render.resolution_x = sc.render.resolution_y = RES
sc.cycles.samples = SAMPLES
sc.render.threads_mode = 'FIXED'; sc.render.threads = 7
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = -0.3
sc.view_settings.look = 'None'
# what the camera sees directly: very light gray / near white studio sweep
nt = sc.world.node_tree
for n in nt.nodes:
    if n.type == 'BACKGROUND' and not n.inputs['Color'].is_linked:
        n.inputs['Color'].default_value = (1.13, 1.13, 1.13, 1); n.inputs['Strength'].default_value = 1.0
    if n.type == 'BACKGROUND' and n.inputs['Color'].is_linked:
        n.inputs['Strength'].default_value = 1.3
# brighter, higher-contrast diamond: stronger dispersion for fire
dia = bpy.data.materials['Diamond']
d = dia.node_tree.nodes['Principled BSDF']
if 'Dispersion' in d.inputs: d.inputs['Dispersion'].default_value = 0.05
for o in bpy.data.objects:
    if o.type == 'LIGHT': o.data.energy *= 1.3
for v in VIEWS:
    sc.camera = bpy.data.objects['Cam_' + v]
    sc.render.filepath = os.path.join(OUT, 'render_%s_%d.png' % (v, RES))
    bpy.ops.render.render(write_still=True)
    print('WROTE', sc.render.filepath, flush=True)

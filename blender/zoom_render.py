# blender -b ring.blend -P zoom_render.py -- out.png [res] [samples] [phi_deg] [scale_mm]
import bpy, sys
from math import radians, sin, cos
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
a = sys.argv[sys.argv.index('--') + 1:]
out = a[0]; res = int(a[1]) if len(a) > 1 else 900; spp = int(a[2]) if len(a) > 2 else 32
phi = radians(float(a[3]) if len(a) > 3 else -76.0); sc_mm = float(a[4]) if len(a) > 4 else 6.0
sc = bpy.context.scene; cam = bpy.data.objects['Cam_front']
M = cam.matrix_world.copy(); M.translation = Vector((10.0 * sin(phi), M.translation.y, 10.0 * cos(phi)))
cam.matrix_world = M; cam.data.ortho_scale = sc_mm; sc.camera = cam
sc.render.resolution_x = sc.render.resolution_y = res; sc.cycles.samples = spp
FL = bpy.data.lights.new('Fill', 'AREA'); FL.size = 90; FL.energy = 6e4
flo = bpy.data.objects.new('Fill', FL); sc.collection.objects.link(flo); flo.visible_camera = False
flo.location = M.translation + Vector((0, 0, 60)); flo.rotation_euler = (radians(90), 0, 0)
d = (Vector((0, 0, 0)) - flo.location).normalized(); flo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = out; bpy.ops.render.render(write_still=True)

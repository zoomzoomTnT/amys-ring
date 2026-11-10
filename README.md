# Amy's Ring

A minimal, phone-friendly web page that shows a 3D model of the ring. Visitors can rotate, zoom, and pan it.

- `site/` holds the static page (Google model-viewer, vendored locally) and the `ring.glb` model.
- Serve it with `sudo ./site/serve.sh 80` from the repo, or any static web server.

`blender/build_ring.py` rebuilds the model in Blender 4.2 (`blender -b -P blender/build_ring.py -- --render`). `renders/` has studio renders, and `blender/ring.stl` is the metal-only mesh in mm.

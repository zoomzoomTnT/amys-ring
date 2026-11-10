# Amy's Ring

A minimal, phone-friendly web page that shows a 3D model of the ring. Visitors can rotate, zoom, and pan it.

- `site/` holds the static page, the `ring.glb` model, and `gallery/` (front/top Cycles renders and an on-hand illustration, WebP). The arrow beside Reset view opens Front view / Top view / On hand.
- `site/viewer.js` is a local bundle of three.js r187 + three-mesh-bvh 0.9 built from `viewer-src/main.js`. Diamonds use a ray-traced refraction shader (IOR 2.42, internal bounces, per-channel IOR for fire) against a high-contrast studio environment; the metal is polished PBR white gold.
  Rebuild: `npm i three three-mesh-bvh esbuild && npx esbuild viewer-src/main.js --bundle --format=esm --minify --outfile=site/viewer.js`
- Live at https://amysring.duckdns.org (Caddy + Let's Encrypt; see `deploy/README.md`). For a local preview: `./site/serve.sh 8080`.

`blender/build_ring.py` rebuilds the model in Blender 4.2 (`blender -b -P blender/build_ring.py -- --render`). `renders/` has studio renders, and `blender/ring.stl` is the metal-only mesh in mm.

`blender/render_gallery.py` renders the white-background gallery shots (`blender -b blender/ring.blend -P blender/render_gallery.py -- OUTDIR 1600 256 front,top`), and `blender/make_web_gallery.py` compresses them for the site.

# Amy's Ring: notes for Claude

A 3D model of Amy's 18K white gold engagement ring, built in Blender from a reference photo and shown on a phone-friendly three.js page.
Live site: https://amysring.duckdns.org

## Owner's rules (zoomzoom): follow these exactly

- **Commit and push straight to `main`.** No feature branches and no pull requests in this repo. This overrides any default of pushing a `claude/` branch.
- **Versioning**
  - Fixes that make the model match the reference photo count as v1.0: add one line under `## v1.0` in `CHANGELOG.md`, with no new tag.
  - Only the owner's own design changes get a version bump (v2.0 and up), a git tag (`vX.Y`) and a CHANGELOG entry.
  - Once v2 exists, add a version switcher to the site.
- **Compare every refinement round closely against the reference photo**: side-by-side zooms plus per-view outline overlays with IoU scores. Show the images to the owner so they can point at problems precisely.
- **Hard limits** (check them before every commit):
  - Gold weight about 8.2 g (`est_weight_g_18kw_14_7` in `blender/stats.json`).
  - `site/ring.glb` at 3.5 MB or less.
  - Stone counts unchanged: centre stone, 2 hearts, 14 × 3.0 mm, 62 × 1.0 mm, 32 × 1.3 mm, 16 × 1.2 mm, 22 × 1.4 mm.
  - Ring size 5.5.
- **Never copy files to the server by hand.** Deploys happen only through a push to `main` (see Deploy below).
- **Verify the live site after each deploy** at desktop and phone widths.

## Reference photo

The model must match the original ring photo: four views on a grey background, labelled "18K White Gold 8.2g / size: 5.5".
- It's committed at `blender/reference_original.jpg` (1664 × 1184).
- Don't edit, crop or replace it.

## Commands

- **Build the model** (Blender 4.2, headless, renders with Cycles; CPU is fine):
  `blender -b -P blender/build_ring.py -- --render`
  - Writes `site/ring.glb`, `blender/ring.blend`, `blender/ring.stl` (metal only, mm) and `blender/stats.json` (weight, stone counts).
  - With `--render` it also writes `render_<view>.png` and `cams.json` into `blender/`.
  - The script is fully parametric; its options are the `arg('--name', default)` calls near the top.
- **Comparison scripts** in `blender/` (system `python3` with Pillow and numpy):
  - They open `reference_original.jpg`, `render_<view>.png`, `cams.json` and `overlay_report.json` relative to the **current directory**, so run them from `blender/` (`cd blender`) after a `--render` build.
  - Run `overlay_views.py` first: it writes `overlay_report.json`, which the zoom scripts read.
  - The zoom scripts are `u_post_zoom.py`, `heart_mount_zoom.py`, `gear_check.py`, `closeup.py` and `compare_sheet.py`. Check each one's `sys.argv` defaults before running it.
  - Their output lands in `blender/`, which is git-ignored for images. Copy the comparison images you want to keep into `renders/`.
- **Gallery images**:
  `blender -b blender/ring.blend -P blender/render_gallery.py -- OUTDIR 1600 256 front,top`, then `blender/make_web_gallery.py`.
  - `make_web_gallery.py` still hard-codes `/workspace/ring/gallery` from an old machine. Fix the path before using it.
- **Viewer bundle** (three.js r187, three-mesh-bvh 0.9):
  `npm i three@0.187 three-mesh-bvh@0.9 esbuild && npx esbuild viewer-src/main.js --bundle --format=esm --minify --outfile=site/viewer.js`
  - When `site/ring.glb` changes size, set `GLB_BYTES` in `viewer-src/main.js` to its exact byte size, then rebuild `site/viewer.js`.
  - `node_modules/` and `package*.json` are git-ignored, so don't commit them.
- **Local preview**: `./site/serve.sh 8080`

## Deploy

- A push to `main` that touches `site/**` runs `.github/workflows/deploy.yml`.
- The workflow copies `site/` to `/opt/amys-ring/site` on the Aliyun ECS server (Caddy, Let's Encrypt, DuckDNS domain), then checks the live URLs.
- It uses the repo secrets `SERVER_IP`, `SERVER_UN` and `SERVER_PK`.
- Server notes are in `deploy/README.md`.

## Cloud sessions

- `deploy/claude-cloud-setup.sh` is the setup script for the Claude Code cloud environment.
- It installs Blender 4.2 at `/opt/blender`, available as `blender`, plus Pillow and numpy.

## Open issues (as of the 2026-11-18 handover; update this list as you fix them)

1. **Side gallery still slightly gear-like.**
   - The points are 1.0 mm long (photo: 1.75 mm) and stick out 0.7 mm (photo: 0.42 mm). They also have a small T-shaped head.
   - They should be longer and sit closer to the stones. See `renders/gear_check.png` and `renders/u_post_zoom.png`.
2. **Left heart claw** shows as a dark block from the front.
   - It is 2.5 mm long (photo: 3.8 mm) and 0.9 mm thick (photo: 0.75 mm).
   - The heart angle is 56° (photo: 49°). See `renders/heart_mount_zoom.png`.
3. **Comfort groove** inside the band was removed to hold 8.2 g. Restore it, for example by thickening the band slightly.
4. **3.0 mm stone spacing**: the stones sit about 1.4 mm too far along the band (pitch 18.7°; photo: 17.2°).
5. **Metal shading** reads flatter and lighter than the photo, which shows strong light-to-dark gradients on the points.
6. **Gallery images**: re-render `site/gallery/front.webp`, `top.webp` and the on-hand image from the current model.

Outline match against the photo (IoU, 1.0 = perfect): front 0.86, side 0.93, top 0.93, three-quarter 0.93.

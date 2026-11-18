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

## Designs (v2.0 and up)

- Two designs now live side by side; `designs/README.md` is the index and each design's `DESIGN.md` is its memory
  (spec, tuned settings, final numbers, owner decisions, open issues). Read it before touching a design and update it
  at the end of every round.
- Design #1: everything below under Reference photo / Commands (files in `blender/`, `site/ring.glb`, `site/gallery/`).
- Design #2: `designs/d2/` (picture `reference.jpg`, `build_ring_d2.py`, outputs next to it), web files in `site/d2/`.
  Build: `blender -b -P designs/d2/build_ring_d2.py -- --render`. Compare: `cd designs/d2 && python3 ../../blender/overlay_views.py`.
  Its hard limits: gold about 8.6 g, 8 ovals + 26 × 1.3 mm + centre, size 5.5, GLB at 3.5 MB or less.
- The site picks the design from `?design=N`; per-design model, specs and photos are the `DESIGNS` table in `site/index.html`.
  When a design's GLB changes, update its `bytes` there.
- The "Hard limits" and "Open issues" sections below are design #1's.

## Reference photo

The model must match the original ring photo: four views on a grey background, labelled "18K White Gold 8.2g / size: 5.5".
- It's committed at `blender/reference_original.jpg` (1664 × 1184).
- Don't edit, crop or replace it.

## Commands

- **Build the model** (Blender 4.2, headless, renders with Cycles; CPU is fine):
  `blender -b -P blender/build_ring.py -- --render`
  - Writes `blender/ring.glb` (copy it to `site/ring.glb`), `blender/ring.blend`, `blender/ring.stl` (metal only, mm) and `blender/stats.json` (weight, stone counts).
  - With `--render` it also writes `render_<view>.png` and `cams.json` into `blender/`.
  - The script is fully parametric; its options are the `arg('--name', default)` calls near the top. The tuned values live in the `TUNED` string, and the first match wins, so put new values at its front.
  - For quick trials add `--fast --render --res 1000 --samples 24 --views front,side` (about 1 minute; it skips the union, STL, GLB and stats). `--checkonly` only builds and prints collisions.
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

1. **Side gallery points**: since round 16 they are short and wide with flat ends, and the U edges sit flush with the band face (`--cuflat`), as the owner asked. See `renders/review_round16.png`.
2. **Heart angle** is 56° (photo: 49°). The heart foot is a V prong since round 15 (`--hm2footv`); the owner rejected the round-14 flat bar.
3. **Comfort groove** inside the band was removed to hold 8.2 g. Since round 15 the plain lower band has rounded inner edges (`--shrib`), which gives some comfort-fit feel.
4. **Metal shading**: surfaces facing sideways (the heart channel walls, the front of the heart V prong) render near-black in the Cycles renders, while the photo shows them bright grey. The studio lighting needs more light from the sides.
5. **Gallery images**: front, side, top and top side (three-quarter) views are crops of the reference photo. The on-hand image is still an old illustration.

Outline match against the photo (IoU, 1.0 = perfect): front 0.884, side 0.932, top 0.935, three-quarter 0.938 (round 16). The owner preferred wider U rims over the round-14 front score (0.895).

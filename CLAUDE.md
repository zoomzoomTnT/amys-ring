# Amy's Ring: notes for Claude

3D models of Amy's 18K white gold engagement ring, built in Blender from the owner's pictures and shown on a phone-friendly three.js page.
Live site: https://amysring.duckdns.org

## Owner's rules (zoomzoom): follow these exactly

- **Commit and push straight to `main`.** No feature branches and no pull requests in this repo. This overrides any default of pushing a `claude/` branch.
- **Versioning**
  - Fixes that make the model match the reference photo count as v1.0: add one line under `## v1.0` in `CHANGELOG.md`, with no new tag.
  - Only the owner's own design changes get a version bump (v2.0 and up), a git tag (`vX.Y`) and a CHANGELOG entry.
  - Once v2 exists, add a version switcher to the site.
- **Compare every refinement round closely against the reference photo**: side-by-side zooms plus per-view outline overlays with IoU scores. Show the images to the owner so they can point at problems precisely.
- **Hard limits** (check them before every commit):
  - Gold weight about 8.2 g (`est_weight_g_18kw_14_7` in `designs/d1/model/stats.json`).
  - `site/d1/ring.glb` at 3.5 MB or less.
  - Stone counts unchanged: centre stone, 2 hearts, 14 × 3.0 mm, 62 × 1.0 mm, 32 × 1.3 mm, 16 × 1.2 mm, 22 × 1.4 mm.
  - Ring size 5.5.
- **Never copy files to the server by hand.** Deploys happen only through a push to `main` (see Deploy below).
- **Verify the live site after each deploy** at desktop and phone widths.

The hard limits above are design #1's. Every design's limits are in `designs/dN/limits.json`; `make limits D=N`
checks them and `make publish D=N` refuses to publish a build that breaks them.

## Repository layout (reorganized 2026-11-18)

- `README.md` is the map; `designs/README.md` indexes the designs; `docs/VERSIONING.md` explains how versions are kept.
- One folder per design, `designs/dN/`: `DESIGN.md` (the design's memory: spec, owner decisions, round -> commit
  table, numbers, open issues; read it before touching the design and update it at the end of every round),
  `reference/` (owner's picture + view boxes + review close-ups), `build.py`, `limits.json`, `model/` (committed
  ring.blend, ring.stl, stats.json), `renders/current/` and `renders/rounds/` (committed), `build/` (scratch, ignored).
- `lib/ringkit.py`: Blender helpers shared by all designs (stones, seats, materials, scene, cameras, union/STL/GLB
  export). A design's `build.py` sets `DESIGN_DIR` and `TUNED`, exec()s ringkit, then defines `build()` and
  `collision_report()`. Changing ringkit changes every design: rebuild all of them and compare stats/GLB hashes.
- `tools/`: `overlay_views.py`, `zoom_compare.py`, `review_sheet.py`, `publish.py`, `get_version.py`,
  `tag_versions.sh`. Each prints its usage when run without arguments. Design #1's older helpers: `designs/d1/tools/`.
- `site/`: deployed as is; `site/d1/` and `site/d2/` hold each design's `ring.glb` and `gallery/` photos.

## Designs

- Design #1 (heart shoulders, v1.0): `designs/d1/`, web files `site/d1/`.
- Design #2 (oval side stones, v2.0): `designs/d2/`, web files `site/d2/`. Its limits: 8 ovals + 26 × 1.3 mm + centre,
  size 5.5, GLB at 3.5 MB or less, thin round band (~3 mm). The site shows the owner's 8.6 g gold spec although the
  thin-band model weighs ~5.2 g (owner decision, round 2): don't bulk it up to 8.6 g.
- The site picks the design from `?design=N`; per-design model, specs and photos are the `DESIGNS` table in
  `site/index.html` (`tools/publish.py` keeps each design's `bytes` in step with its GLB).

## Reference photos

Each model must match its owner's picture, `designs/dN/reference/original.jpg`. Don't edit, crop or replace them.
- Design #1: four views on a grey background, labelled "18K White Gold 8.2g / size: 5.5" (1664 × 1184).
- Design #2: four views on grey (three-quarter, top, front, side), 1520 × 1296.

## Commands

Run from the repo root. `make` lists the tasks; `D` picks the design (Blender 4.2 headless, Cycles on CPU).
- `make trial D=N`: quick front + side renders (~1 min). Writes everything to `build/`, never touches `model/`.
- `make build D=N`: full build + 4 renders (~15 min) = `blender -b -P designs/dN/build.py -- --render`.
  Writes `model/` (ring.blend, ring.stl, stats.json) and `build/` (ring.glb, cams.json, render_<view>.png).
  `--checkonly` (`make check D=N`) only builds the geometry and prints stone counts and collisions.
- The build scripts are fully parametric: options are the `arg('--name', default)` calls; the tuned values live in
  the `TUNED` string at the top of each `build.py`, the first match wins, so put new values at its front.
- `make compare D=N`: outline overlays + IoU (`tools/overlay_views.py`, writes into `build/`).
- `make review D=N`: review sheet, picture | committed renders | this build (`tools/review_sheet.py`); zoom on any box
  with `tools/zoom_compare.py`. Keep a round's sheet as `designs/dN/renders/rounds/rNN-review.png`.
- `make publish D=N`: checks `limits.json`, copies `build/ring.glb` to `site/dN/ring.glb` (updating `bytes` in
  `site/index.html`) and full-size renders + overlays to `renders/current/`.
- `make version D=N REV=<commit|tag>`: pulls an old version's files into `build/versions/<rev>/`.
- A fresh build reproduces the committed GLB/STL byte for byte; after a verification build, restore `model/ring.blend`
  with `git checkout` instead of committing a binary that only changed its timestamps.
- **Viewer bundle** (three.js r187, three-mesh-bvh 0.9): `make viewer`. `node_modules/` and `package*.json` are
  git-ignored. `GLB_BYTES` in `viewer-src/main.js` is only a fallback: the page passes each design's `bytes`.
- **Local preview**: `make serve` (http://localhost:8080).
- Design #1 gallery renders: `blender -b designs/d1/model/ring.blend -P designs/d1/tools/render_gallery.py -- OUTDIR 1600 256 front,top`,
  then `python3 designs/d1/tools/make_web_gallery.py OUTDIR site/d1/gallery`.

## Versions

- Each round is one commit; each `DESIGN.md` has the round -> commit table. Tags: `vX.Y` (owner designs) and `dN-rNN`
  (rounds), listed in `tools/tag_versions.sh`. Cloud sessions can't push tags, so the owner runs that script locally;
  add new rounds to it.
- Repo history is ~727 MB, mostly old `ring.stl` versions. Git LFS / STL-at-milestones is an open owner decision
  (`docs/VERSIONING.md`); until decided, keep committing `model/` as before.

## Deploy

- A push to `main` that touches `site/**` runs `.github/workflows/deploy.yml`.
- The workflow checks the site files, copies `site/` to `/opt/amys-ring/site` on the Aliyun ECS server (Caddy, Let's Encrypt, DuckDNS domain), then checks the live URLs (`/`, `/d1/ring.glb`, `/d2/ring.glb`).
- It uses the repo secrets `SERVER_IP`, `SERVER_UN` and `SERVER_PK`.
- Server notes are in `deploy/README.md`.

## Cloud sessions

- `deploy/claude-cloud-setup.sh` is the setup script for the Claude Code cloud environment.
- It installs Blender 4.2 at `/opt/blender`, available as `blender`, plus Pillow and numpy.

## Open issues

Design #1's are in `designs/d1/DESIGN.md`, design #2's in `designs/d2/DESIGN.md`.

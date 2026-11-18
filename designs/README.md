# Designs

Each design of Amy's ring keeps its own reference image, build script, Blender file, measurements and notes, so any of
them can be reopened, rebuilt or compared later. The site shows them all; the **Details** panel has a switcher
(`?design=2` in the URL opens design #2 directly).

| Design | Version | Status | Reference | Build script | Site files |
|---|---|---|---|---|---|
| #1 | v1.0 (refinement rounds 1-16) | live | `blender/reference_original.jpg` | `blender/build_ring.py` | `site/ring.glb`, `site/gallery/` |
| #2 | v2.0 | live | `designs/d2/reference.jpg` | `designs/d2/build_ring_d2.py` | `site/d2/ring.glb`, `site/d2/gallery/` |

Per-design notes (spec, tuned settings, final numbers, open issues, how to rebuild):
- [`d1/DESIGN.md`](d1/DESIGN.md)
- [`d2/DESIGN.md`](d2/DESIGN.md)

## What each design folder holds

- `reference.jpg` (or, for design #1, `blender/reference_original.jpg`): the owner's picture. Never edit it.
- The build script. Its tuned settings are baked in (`TUNED` / `D2_TUNED`), so a plain run reproduces the committed model.
- `ring.blend` (Blender scene), `ring.stl` (metal only, mm), `ring.glb` (web model), `stats.json` (gold weight, stone counts).
- `renders/`: the committed renders, outline overlays and review sheets for each round.
- `DESIGN.md`: the design's memory. Update it at the end of every round.

## Adding a design

1. Make `designs/dN/` with the owner's picture as `reference.jpg` and an `overlay_config.json` that marks where each
   view sits in the picture (see `d2/`).
2. Start from `d2/build_ring_d2.py`: it loads design #1's helpers from `blender/build_ring.py` and only replaces the
   geometry. Run it from the repo root; outputs land next to the script.
3. Copy `ring.glb` to `site/dN/ring.glb`, crop the gallery photos into `site/dN/gallery/`, and add an entry to
   `DESIGNS` in `site/index.html` (set `bytes` to the GLB's exact size).
4. An owner design is a new major version: CHANGELOG entry, git tag `vN.0`.

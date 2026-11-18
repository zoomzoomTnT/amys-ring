# Designs

One folder per design. Everything about a design lives inside its folder, so any design can be reopened, rebuilt or
compared later. The site shows all of them; the Details panel switches between designs (`?design=N` in the URL).

| Design | What | Version | Rounds | Notes and history | Site files |
|---|---|---|---|---|---|
| [#1](d1/) | Heart shoulders: hearts in V-prong baskets, 14 × 3.0 mm stones in U holders, pave | v1.0 | 16 (+13b) | [d1/DESIGN.md](d1/DESIGN.md) | `site/d1/` |
| [#2](d2/) | 8 oval side stones in shared claws on a thin round band, pave gallery rail | v2.0 | 2 | [d2/DESIGN.md](d2/DESIGN.md) | `site/d2/` |

Both use the same 15.68 ct lab-grown oval centre stone (IGI LG843655695), ring size 5.5, 18K white gold.

## Inside a design folder

| Path | What | In git? |
|---|---|---|
| `DESIGN.md` | The design's memory: spec, owner decisions, round table (round -> commit), numbers, open issues | yes |
| `reference/original.jpg` | The owner's picture. Never edit, crop or replace it | yes |
| `reference/overlay.json` | Where each view (top, three-quarter, front, side) sits in the picture | yes |
| `reference/review_boxes.json` | Named close-ups used by `tools/review_sheet.py` | yes |
| `build.py` | Blender build script. Tuned settings baked into `TUNED` (newest round first; first match wins) | yes |
| `limits.json` | Hard limits checked by `tools/publish.py` | yes |
| `model/` | `ring.blend`, `ring.stl` (metal only, mm), `stats.json` from the last full build | yes |
| `renders/current/` | Latest renders, outline overlays, `overlay_report.json`, `cams.json` | yes |
| `renders/rounds/` | One review sheet per round (`rNN-review.png` and extra close-ups) | yes |
| `tools/` | Design-specific helper scripts (design #1 only) | yes |
| `build/` | Scratch: renders, web GLB, overlays, trial blends, old versions pulled out of git | no |

## Adding a design

1. Copy `d2/` as `dN/` and drop `model/`, `renders/` and the round history from `DESIGN.md`.
2. Put the owner's picture in `reference/original.jpg`; mark the four views in `reference/overlay.json` and some
   close-ups in `reference/review_boxes.json`; set `limits.json`.
3. Rewrite `build()` in `build.py` (the shared helpers come from `lib/ringkit.py`); iterate with `make trial D=N`
   and `make compare D=N`.
4. Add the design to `PATHS` in `tools/get_version.py`, give it a `site/dN/` folder and an entry in `DESIGNS` in
   `site/index.html`, then `make build D=N` and `make publish D=N`.
5. An owner design is a new major version: CHANGELOG entry and git tag `vN.0` (`tools/tag_versions.sh`).

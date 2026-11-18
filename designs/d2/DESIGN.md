# Design #2: oval side stones (v2.0)

State: round 2, last changed 2026-11-18 (commit `0541137`). Live as Design #2 on the site.
Added 2026-11-18 from the owner's picture `reference/original.jpg` (four views on grey: three-quarter, top, front, side).

## Spec (from the owner)
- Centre: the same 15.68 ct lab-grown oval as design #1 (19.22 × 12.83 × 8.17 mm, D VVS1, IGI LG843655695).
- 8 oval side stones, about 0.7 ct each, 4 per side, long axis along the finger.
  - The owner wrote "5.7 mm", but at the centre stone's scale the picture shows about 6.7 × 4.5 mm, which is what a
    0.7 ct oval measures. The owner chose to **match the picture**: the model uses 6.7 × 4.5 mm (`--ovl`, `--ovw`).
- 26 round diamonds, 1.3 mm (about 0.01 ct each), set in the gallery rail under the centre stone.
- Accents 0.7 × 8 + 0.01 × 26 = 5.86 ct. 18K white gold about 8.6 g. Ring size 5.5.

## Construction (as read from the picture)
- Head: four claws over the crown, running down outside the rail and sweeping in under the stone onto the band top;
  a short saddle bar joins each pair of claw feet. Flat rail ring under the girdle with the 26 rounds on its outer face.
- Band (round 2, owner): a thin, round women's band about 3.0 mm wide and 1.8 mm thick all the way round, much narrower
  than the 6.7 mm ovals; no edges (`--round 1`). Shared claws, 5 pairs per side with domed ends: each claw's **foot sits
  on the outside of the band** (against its side face) and leans out to its tip at the stone's edge. A curved wire
  cradle under each oval dips toward the band (the U arcs in the front view). The head claws land on the narrow band top.

## Files
- Reference: `reference/original.jpg` (owner's picture, never edit), `reference/overlay.json` (where each view sits
  in it), `reference/review_boxes.json` (close-ups for review sheets).
- Build script: `build.py` (design #2's geometry and settings; shared helpers in `lib/ringkit.py`). Tuned settings:
  the `TUNED` string near the top, newest round first (the first match wins; command-line values beat it).
- Model: `model/ring.blend`, `model/ring.stl` (metal only, mm), `model/stats.json`; web model `site/d2/ring.glb` (2.10 MB).
- Gallery photos (crops of the picture): `site/d2/gallery/`.
- Renders: `renders/current/` (latest renders + overlays), `renders/rounds/r01-review.png` (picture vs model, every
  view) and `r02-review.png` (picture vs round 1 vs round 2).
- Hard limits: `limits.json` (checked by `make limits D=2`; gold is informational, see owner decisions).

## Rebuild and compare
```
make trial D=2      # quick front + side trial (~1 min), never touches model/
make build D=2      # = blender -b -P designs/d2/build.py -- --render   (~15 min)
make compare D=2    # outline overlays + IoU vs the picture
make review D=2     # review sheet: picture | committed | this build
make publish D=2    # check limits, copy the GLB to site/d2/ and the renders to renders/current/
```

## Owner decisions
- Ovals match the picture (6.7 × 4.5 mm), not the written 5.7 mm (round 1).
- Band thin and round, claw feet outside the band (round 2).
- **Gold weight:** the thin band makes the model about 5.2 g of 18K gold. The owner chose to keep showing **8.6 g** (their
  spec) on the site anyway, knowing the model is lighter (round 2). Don't "fix" the model back to 8.6 g by thickening it.

## Round 2 numbers
- Model gold 5.19 g (site shows the owner's 8.6 g), inner diameter 16.10 mm (size 5.5), GLB 2.10 MB; 8 ovals, 26 × 1.3 mm, centre; no collisions.
- Outline IoU: front 0.900, side 0.931, top 0.952, three-quarter 0.931. Sheet: `renders/rounds/r02-review.png` (picture vs round 1 vs round 2).

## Round 1 numbers
- Gold 8.59 g, inner diameter 16.10 mm (size 5.5), GLB 2.05 MB; stones: 8 ovals, 26 × 1.3 mm, centre. No collisions.
- Outline IoU: front 0.909, side 0.931, top 0.964, three-quarter 0.922.

## Round history
Get any round's files with `make version D=2 REV=<commit>`. Tags (`d2-rNN`) are created by `tools/tag_versions.sh`.

| Round | Commit | Date | What changed | Review sheet |
|---|---|---|---|---|
| r01 | `053e2de` (v2.0) | 2026-11-18 | First model from the owner's picture; design switcher added to the site | `r01-review.png` |
| r02 | `0541137` | 2026-11-18 | Owner review: thin round band (~3 mm), claw feet outside the band | `r02-review.png` |

## Open issues / next refinements
1. Front view: the picture's band claws look a little thicker and the ovals fill the gaps between claws more fully.
   Round 2's cradles read as busier wavy wire than the picture's smooth U arcs.
2. Side view: the picture's prongs splay outward more as they come down to the band.
3. The three-quarter camera is design #1's; a camera matched to this picture would make that overlay fairer.
4. No on-hand image yet for this design.

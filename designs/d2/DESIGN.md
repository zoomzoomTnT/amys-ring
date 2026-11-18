# Design #2: state after round 2 (v2.0)

Added 2026-11-18 from the owner's picture `reference.jpg` (four views on grey: three-quarter, top, front, side).

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
- `reference.jpg`: owner's picture (never edit). `overlay_config.json`: where each view sits in it.
- `build_ring_d2.py`: build script. It loads design #1's helpers from `blender/build_ring.py` (`--nobuild`) and replaces
  the geometry. Tuned settings: the `D2_TUNED` string (command-line values win).
- `ring.blend`, `ring.stl` (metal only, mm), `stats.json`; web model `site/d2/ring.glb` (2.10 MB).
- Gallery photos (crops of the picture): `site/d2/gallery/`.
- `renders/`: renders, outline overlays, `review_d2_round1.png` (picture vs model, every view) and `review_d2_round2.png`.

## Rebuild and compare
```
blender -b -P designs/d2/build_ring_d2.py -- --render     # ~15 min; quick trial: --fast --render --res 900 --samples 16 --views front,side
cd designs/d2 && python3 ../../blender/overlay_views.py    # reads overlay_config.json -> overlay_*.png, IoU
cp designs/d2/ring.glb site/d2/ring.glb                    # then set bytes: <size> for design 2 in site/index.html
```

## Owner decisions
- Ovals match the picture (6.7 × 4.5 mm), not the written 5.7 mm (round 1).
- Band thin and round, claw feet outside the band (round 2).
- **Gold weight:** the thin band makes the model about 5.2 g of 18K gold. The owner chose to keep showing **8.6 g** (their
  spec) on the site anyway, knowing the model is lighter (round 2). Don't "fix" the model back to 8.6 g by thickening it.

## Round 2 numbers
- Model gold 5.19 g (site shows the owner's 8.6 g), inner diameter 16.10 mm (size 5.5), GLB 2.10 MB; 8 ovals, 26 × 1.3 mm, centre; no collisions.
- Outline IoU: front 0.900, side 0.931, top 0.952, three-quarter 0.931. Sheet: `renders/review_d2_round2.png` (picture vs round 1 vs round 2).

## Round 1 numbers
- Gold 8.59 g, inner diameter 16.10 mm (size 5.5), GLB 2.05 MB; stones: 8 ovals, 26 × 1.3 mm, centre. No collisions.
- Outline IoU: front 0.909, side 0.931, top 0.964, three-quarter 0.922.

## Open issues / next refinements
1. Front view: the picture's band claws look a little thicker and the ovals fill the gaps between claws more fully.
   Round 2's cradles read as busier wavy wire than the picture's smooth U arcs.
2. Side view: the picture's prongs splay outward more as they come down to the band.
3. The three-quarter camera is design #1's; a camera matched to this picture would make that overlay fairer.
4. No on-hand image yet for this design.

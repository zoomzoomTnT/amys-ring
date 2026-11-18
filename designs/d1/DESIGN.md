# Design #1: final state (v1.0, round 16)

Last model commit: `2eeddcf` (2026-11-18, "Owner review round 16"). Check out that commit, or use the files below, to
reopen it exactly as it was when design #2 was added.

## Spec (from the owner's picture, "18K White Gold 8.2g / size: 5.5")
- Centre: 15.68 ct lab-grown oval, 19.22 × 12.83 × 8.17 mm, D VVS1, IGI LG843655695, four straight claws.
- 2 heart side stones (6.0 mm), each in a basket with a V-prong foot running down to the band.
- 146 small rounds: 14 × 3.0 mm (sideways in U holders, 7 per side), 62 × 1.0 mm, 32 × 1.3 mm, 16 × 1.2 mm, 22 × 1.4 mm.
- 18K white gold 8.21 g (model), ring size 5.5 (16.1 mm inner diameter). Accents about 4.35 ct; total about 12.2 g.

## Where the files are
- Reference picture: `blender/reference_original.jpg` (never edit or replace).
- Build script: `blender/build_ring.py`. The tuned settings are the `TUNED` string near the top; the first match wins,
  so the newest round's values sit at its front.
- Blender scene `blender/ring.blend`, metal STL `blender/ring.stl`, stats `blender/stats.json`.
- Web model: `site/ring.glb` (3.21 MB). Gallery photos: `site/gallery/` (crops of the reference + an old on-hand illustration).
- Review sheets per round: `renders/review_round14.png`, `review_round15.png`, `review_round16.png`,
  `front_shape_round16.png`, `band_round15.png`; outline overlays `renders/overlay_*.png`.
- History of every round: the `## v1.0` section of `CHANGELOG.md`.

## Rebuild
```
blender -b -P blender/build_ring.py -- --render          # full build + 4 renders (~15 min on 4 CPUs)
cd blender && python3 overlay_views.py                    # outline IoU vs the picture
```
Quick trial: add `--fast --render --res 1000 --samples 24 --views front,side`.

## Final numbers
- Outline IoU: front 0.884, side 0.932, top 0.935, three-quarter 0.938.
- Gold 8.21 g, GLB 3.21 MB, no stone-stone or stone-metal collisions.

## Owner decisions worth remembering
- Side stones stay 3.0 mm; the U holders were shrunk to hug them (round 14).
- Wider U rims preferred over the round-14 front IoU; U edges flush with the band face, short wide flat-ended points (rounds 15-16).
- Heart foot is a V prong, not a flat bar (round 15). Centre claws are straight (round 14).
- Band should read round and soft (women's ring): rounded inner edges and rounded plain bottom (rounds 15-16).

## Open issues
1. Heart angle 56° (picture 49°).
2. Comfort groove was dropped to hold 8.2 g.
3. Sideways-facing metal renders too dark in the Cycles comparison renders (lighting, not shape).
4. The on-hand gallery image is an old illustration.

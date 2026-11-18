# Design #1: heart shoulders (v1.0)

State: round 16, last changed 2026-11-18 (commit `2eeddcf`). Live as Design #1 on the site.

## Spec (from the owner's picture, "18K White Gold 8.2g / size: 5.5")
- Centre: 15.68 ct lab-grown oval, 19.22 × 12.83 × 8.17 mm, D VVS1, IGI LG843655695, four straight claws.
- 2 heart side stones (6.0 mm), each in a basket with a V-prong foot running down to the band.
- 146 small rounds: 14 × 3.0 mm (sideways in U holders, 7 per side), 62 × 1.0 mm, 32 × 1.3 mm, 16 × 1.2 mm, 22 × 1.4 mm.
- 18K white gold 8.21 g (model), ring size 5.5 (16.1 mm inner diameter). Accents about 4.35 ct; total about 12.2 g.

## Files
- Reference picture: `reference/original.jpg` (never edit or replace); view boxes `reference/overlay.json`.
- Build script: `build.py` (design #1's geometry and settings; shared helpers in `lib/ringkit.py`). The tuned
  settings are the `TUNED` string near the top; the first match wins, so the newest round's values sit at its front.
- Model: `model/ring.blend`, `model/ring.stl`, `model/stats.json`. Web model: `site/d1/ring.glb` (3.21 MB).
  Gallery photos: `site/d1/gallery/` (crops of the reference + an old on-hand illustration).
- Renders: `renders/current/` (latest renders + overlays), `renders/rounds/` (review sheets per round).
- Helper scripts from earlier rounds: `tools/` (zoom crops, contact sheets, gallery renders; each says how to run it).
- Hard limits: `limits.json` (checked by `make limits D=1`).

## Rebuild
```
make build D=1      # = blender -b -P designs/d1/build.py -- --render   (~15 min on 4 CPUs)
make compare D=1    # outline IoU vs the picture
make trial D=1      # quick front + side trial (~1 min), never touches model/
```

## Final numbers (round 16)
- Outline IoU: front 0.884, side 0.932, top 0.935, three-quarter 0.939 (all four renders regenerated from the round-16 model on 2026-11-18; the top and three-quarter renders committed with round 16 were still round 15's).
- Gold 8.21 g, GLB 3.21 MB, no stone-stone or stone-metal collisions.

## Owner decisions worth remembering
- Side stones stay 3.0 mm; the U holders were shrunk to hug them (round 14).
- Wider U rims preferred over the round-14 front IoU; U edges flush with the band face, short wide flat-ended points (rounds 15-16).
- Heart foot is a V prong, not a flat bar (round 15). Centre claws are straight (round 14).
- Band should read round and soft (women's ring): rounded inner edges and rounded plain bottom (rounds 15-16).

## Round history
Get any round's files with `make version D=1 REV=<commit>`. Tags (`d1-rNN`) are created by `tools/tag_versions.sh`.
Before round 1, `v1.0` (`471988c`) marked the first model. Sheets for rounds 1-13 were overwritten as work went on;
older images are in git history at those commits.

| Round | Commit | Date | What changed | Review sheet |
|---|---|---|---|---|
| r01 | `2276d86` | 2026-11-10 | Rebuilt to match the picture: claw head over a channel gallery rail, V pave arms, tilted hearts | |
| r02 | `88f4edb` | 2026-11-10 | Hearts edge-on in diagonal pave arms, front-facing 3.0 mm stones with claw teeth | |
| r03 | `1c20620` | 2026-11-11 | Rounded bezel/scallop seats on every stone, staggered zigzag pave | |
| r04 | `ace7ff1` | 2026-11-11 | Two-size 1.3/1.0 mm zigzag, exact stone totals, lighter GLB | |
| r05 | `19b075d` | 2026-11-11 | Wider band face, sunk 3.0 mm stones, inner comfort channel | `r05-ring-views.png` |
| r06 | `c233c1b` | 2026-11-11 | Side band from a pixel-measured study: sideways 3.0 mm stones in tulip U-seats | |
| r07 | `9c41b07` | 2026-11-11 | Thick half-round U rims with rounded tulip peaks | |
| r08 | `9c7efab` | 2026-11-11 | Zigzag phase-locked to the 3.0 mm stones (hairpin U-prongs) | |
| r09 | `c69bbc2` | 2026-11-11 | One smooth swept rim per side, round tips | |
| r10 | `e91e987` | 2026-11-11 | Every 3.0 mm stone in its own deep round U cup, tapered points between | |
| r11 | `7a1fb35` | 2026-11-12 | Refined cups, longer squared-off points, wider ribbon rim | |
| r12 | `be857ce` | 2026-11-12 | Side gallery as one solid polished body | `r12-u-post-zoom-model-hi.png` |
| r13 | `006dc6b` | 2026-11-12 | Heart mounts rebuilt: V claw at the point, splayed straight arms | |
| r13b | `3ee9032` | 2026-11-12 | Slimmer side-gallery points (no gear look) | `r13b-*.png` |
| r14 | `d407ebb` | 2026-11-18 | Owner review: straight centre claws, U holders hug the 3.0 mm stones, calmer 3D view | `r14-review.png` |
| r15 | `e405e4b` | 2026-11-18 | Owner review: V-prong heart feet, wider rounded U rims, rounded women's band | `r15-review.png`, `r15-band.png` |
| r16 | `2eeddcf` | 2026-11-18 | Owner review: flush U edges, short wide tips, rounder band | `r16-review.png`, `r16-front-shape.png` |

## Open issues
1. Heart angle 56° (picture 49°).
2. Comfort groove was dropped to hold 8.2 g; the rounded inner edges give some comfort-fit feel.
3. Sideways-facing metal (heart channel walls, the front of the heart V prong) renders near-black in the Cycles
   comparison renders, while the picture shows it bright grey: a lighting problem, not the shape.
4. The on-hand gallery image is an old illustration.

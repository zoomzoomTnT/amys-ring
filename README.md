# Amy's Ring

3D models of Amy's 18K white gold engagement ring, built in Blender from the owner's pictures, and a phone-friendly
website to view them: **https://amysring.duckdns.org** (the Details panel switches between designs; `?design=2` opens
design #2 directly).

## Where things are

```
designs/                 one folder per design: everything about that design lives inside it
  README.md              index of the designs
  d1/                    Design #1, heart shoulders (v1.0, refinement rounds 1-16)
  d2/                    Design #2, oval side stones (v2.0)
    DESIGN.md            start here: spec, owner decisions, round history (round -> commit), open issues
    reference/           the owner's picture (never edited) + where each view sits in it + review close-ups
    build.py             the design's Blender build script (its tuned settings are baked in at the top)
    limits.json          hard limits checked before publishing (gold weight, ring size, stone counts, GLB size)
    model/               ring.blend, ring.stl (metal only, mm), stats.json: committed at the end of each round
    renders/current/     the latest renders and outline overlays against the picture
    renders/rounds/      one review sheet per round (rNN-review.png ...), kept forever
    build/               scratch output of builds and tools (git-ignored)
lib/ringkit.py           Blender code shared by every design: stones, seats, materials, scene, cameras, export
tools/                   compare, review, publish and version scripts (plain python3 + Pillow + numpy)
site/                    the live website, deployed on every push to main that touches it
  d1/, d2/               each design's web model (ring.glb) and photos (gallery/)
viewer-src/              source of site/viewer.js (three.js viewer)
deploy/                  server (Caddy) and cloud-session setup notes
docs/VERSIONING.md       how versions of the Blender files are kept, and why (with research and sources)
CHANGELOG.md             what changed in each version and round
CLAUDE.md                rules and notes for Claude sessions working on this repo
```

## Common tasks

Run from the repo root. `make` lists everything; `D` picks the design.

| Task | Command |
|---|---|
| Quick trial render (front + side, ~1 min) | `make trial D=2` |
| Full build + 4 renders (~15 min) | `make build D=2` |
| Outline overlays + IoU against the picture | `make compare D=2` |
| Review sheet: picture / committed / new | `make review D=2` |
| Check the hard limits | `make limits D=2` |
| Publish the new model to the site | `make publish D=2` |
| Pull an old version out of history | `make version D=1 REV=2eeddcf` (or a tag such as `v2.0`) |
| Preview the site locally | `make serve` |
| Rebuild the 3D viewer bundle | `make viewer` |

Without make: `blender -b -P designs/d2/build.py -- --render`, then `python3 tools/<script>.py designs/d2`
(each tool prints its usage when run without arguments).

## A refinement round, start to finish

1. Read `designs/dN/DESIGN.md` (decisions and open issues), change `designs/dN/build.py`.
2. `make trial D=N` and `make compare D=N` until it looks right; `make review D=N` for close-ups.
3. `make build D=N`, `make compare D=N`, `make review D=N`, then `make publish D=N` (fails if a hard limit is broken).
4. Keep the review sheet as `designs/dN/renders/rounds/rNN-review.png`, add the round to the table in `DESIGN.md`
   and a line to `CHANGELOG.md`, commit to `main` and push. The site deploys itself; check it on desktop and phone.

Requirements: Blender 4.2 LTS (`deploy/claude-cloud-setup.sh` installs it), python3 with Pillow and numpy, and
Node.js only to rebuild the viewer.

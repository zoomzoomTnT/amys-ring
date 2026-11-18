#!/usr/bin/env bash
# Create the version tags on your own machine, then push them (cloud sessions can't push tags):
#   bash tools/tag_versions.sh && git push origin --tags
# vX.Y = owner design versions. dN-rNN = refinement rounds of design N (same commits as the tables in designs/dN/DESIGN.md).
# Existing tags are left alone, so it is safe to run again after new rounds are added below.
set -euo pipefail
cd "$(dirname "$0")/.."
tag() {
  if git rev-parse -q --verify "refs/tags/$1" >/dev/null; then echo "exists   $1"
  else git tag -a "$1" "$2" -m "$3"; echo "created  $1 -> $2"; fi
}
tag v2.0    053e2de "v2.0: Design #2 added alongside Design #1"
tag d1-r01  2276d86 "Design #1 round 1: claw head over a channel gallery rail, V pave arms, tilted hearts"
tag d1-r02  88f4edb "Design #1 round 2: hearts edge-on in diagonal pave arms, front-facing 3.0 mm stones"
tag d1-r03  1c20620 "Design #1 round 3: rounded bezel/scallop seats, staggered zigzag pave"
tag d1-r04  ace7ff1 "Design #1 round 4: two-size 1.3/1.0 mm zigzag, exact stone totals"
tag d1-r05  19b075d "Design #1 round 5: wider band face, sunk 3.0 mm stones, comfort channel"
tag d1-r06  c233c1b "Design #1 round 6: sideways 3.0 mm stones in tulip U-seats"
tag d1-r07  9c41b07 "Design #1 round 7: thick half-round U rims"
tag d1-r08  9c7efab "Design #1 round 8: zigzag phase-locked to the 3.0 mm stones (hairpins)"
tag d1-r09  c69bbc2 "Design #1 round 9: smooth swept U-prongs"
tag d1-r10  e91e987 "Design #1 round 10: deep round U cups with tapered points"
tag d1-r11  7a1fb35 "Design #1 round 11: refined U cups, squared-off points"
tag d1-r12  be857ce "Design #1 round 12: side gallery as one solid polished body"
tag d1-r13  006dc6b "Design #1 round 13: heart baskets rebuilt (V claw, splayed arms)"
tag d1-r13b 3ee9032 "Design #1 round 13b: slimmer side-gallery points"
tag d1-r14  d407ebb "Design #1 round 14: straight centre claws, U holders hug the stones"
tag d1-r15  e405e4b "Design #1 round 15: V-prong heart feet, wider U rims, rounded band"
tag d1-r16  2eeddcf "Design #1 round 16: flush U edges, short wide tips, rounder band"
tag d2-r01  053e2de "Design #2 round 1: first model from the owner's picture"
tag d2-r02  0541137 "Design #2 round 2: thin round band, claw feet outside the band"

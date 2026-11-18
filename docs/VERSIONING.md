# How versions of the ring are kept

Short version: **the build scripts are the source; git commits are the versions.** Every round is one commit on
`main`, every design keeps a round-to-commit table in its `DESIGN.md`, and any version can be pulled back out with
`make version D=<n> REV=<commit or tag>` without disturbing the working copy.

## The rules this repo follows

1. **Scripts are the source of truth.** A design is `designs/dN/build.py` (its settings are baked into the `TUNED`
   string at the top) plus the shared `lib/ringkit.py`. Builds are deterministic: on 2026-11-18, rebuilding both
   designs from their scripts reproduced byte-identical `ring.glb` and `ring.stl` files and identical `stats.json`.
   So any old version can also be regenerated exactly from its commit (`git worktree add ../amys-ring-<rev> <rev>`,
   then build there).
2. **One round = one commit; names come from tags.** Major versions are owner designs (`v1.0`, `v2.0`, ...). Rounds
   are named `dN-rNN` (for example `d1-r16`, `d2-r02`). Cloud sessions can't push tags, so the owner creates them
   once on their own machine: `bash tools/tag_versions.sh && git push origin --tags` (add new rounds to that script).
   Until then, the round tables in `designs/dN/DESIGN.md` map every round to its commit.
3. **What is committed every round** (per design): `model/ring.blend` (the raw Blender file), `model/ring.stl`,
   `model/stats.json`, `renders/current/` (latest renders, overlays, fit report) and one review sheet in
   `renders/rounds/rNN-review.png` that is never overwritten. Everything a build or tool writes goes to the
   design's `build/` folder, which git ignores; `tools/publish.py` copies the keepers out.
4. **No version numbers in working file names.** It is `model/ring.blend`, never `ring_v16_final2.blend`: git holds
   the versions. Exported review images do carry the round (`r16-review.png`). This is how Blender Studio names files:
   working files are named by asset and task, and versions appear only on exports and renders.
5. **No Blender backup copies.** Blender's "Save Versions" preference writes `ring.blend1`, `ring.blend2` next to a
   saved file; builds turn it off (`save_version = 0`) and `.gitignore` ignores them.
6. **`.blend` files are saved uncompressed.** Blender Studio's benchmark found uncompressed files diff better between
   revisions; here 18 versions of design #1's `ring.blend` (100.5 MB raw) pack into 24.1 MB of git history.
7. **Shared code is shared on purpose.** Both designs use `lib/ringkit.py`; each design's geometry lives only in its
   own `build.py`. Before the 2026-11 reorganization, design #2 ran design #1's whole script, so editing design #1
   could silently change design #2.

## Getting an old version back

| Want | Do |
|---|---|
| The files of a round (blend, STL, stats, GLB, renders) | `make version D=1 REV=e405e4b` -> `designs/d1/build/versions/e405e4b/` |
| The whole repo as it was, to rebuild or browse | `git worktree add ../amys-ring-r15 e405e4b` (remove later with `git worktree remove`) |
| Just look | on GitHub, pick the tag or commit in the branch menu, or open the commit from `DESIGN.md` |
| Compare an old round with the current build | `python3 tools/zoom_compare.py designs/d1 front 236 85 426 285 --against designs/d1/build/versions/e405e4b` |

`tools/get_version.py` also knows where files lived before the reorganization (`blender/`, `renders/`,
`site/ring.glb`, `designs/d2/ring.blend`).

## What other Blender projects do (research, November 2026)

- **Blender Studio** (Blender's own film studio) versions every production `.blend` file in Subversion (SVN), which it
  calls robust and efficient for large binary files. Renders and playblasts live outside version control in a shared
  folder. Its design principles say working files should not be versioned by hand. It has benchmarked Git LFS, SVN and
  Mercurial: Git LFS with compressed `.blend` files was competitive on size, uncompressed files give smaller diffs,
  and merging two people's edits to one `.blend` remains unsolved, so only one person should change a `.blend` at a time.
- **Game projects** (the Godot docs, for example) put `.blend` files in Git LFS with a `.gitattributes` line like
  `*.blend filter=lfs diff=lfs merge=lfs -text`, ideally from the first commit. Tools such as Anchorpoint automate
  this for artists.
- **Code-CAD projects** (OpenSCAD, CadQuery), the closest match to this repo's script-built models, keep the scripts
  in git and handle generated meshes in one of two ways: ignore them and let CI build and attach them to a GitHub
  Release, or track them with Git LFS.
- **GitHub's limits:** a warning for files over 50 MiB, a hard block over 100 MiB, and Releases recommended for
  distributing big binaries. Git LFS on the Free plan includes 10 GiB of storage and 10 GiB of download bandwidth
  per month. Downloads by GitHub Actions count against that bandwidth when a workflow checks out with `lfs: true`.

## This repo's numbers, and the open decisions

On 2026-11-18 the repository history was **727 MB after 32 commits**. 315 MB of it is the 18 versions of design #1's
`ring.stl` (40 MB each), and about 220 MB is committed renders (2-3 MB per PNG). A round currently adds roughly 30 MB
of history: about 17 MB for the STL, 11 MB for four renders and 1.5 MB for the blend.

Choices for the owner, roughly in order of effort:

1. **STL only at milestones (no new tools).** Stop committing `ring.stl` every round and commit it, or attach it to a
   GitHub Release, when a design version is final. Any round's STL can still be regenerated exactly from its commit.
   This cuts each round's growth roughly in half.
2. **Git LFS from now on.** Track `designs/**/model/*.blend`, `designs/**/model/*.stl` and `designs/**/renders/**/*.png`
   with LFS. `site/` stays plain git, because the deploy workflow checks out without LFS. Clones then download only
   the versions they need, and the quota allows hundreds of rounds. This needs LFS uploads to work from cloud sessions;
   that couldn't be tested here (the session's permission rules blocked the test), and everyone who clones needs
   git-lfs (GitHub Desktop includes it).
3. **Shrink the existing history.** `git lfs migrate import --everything` (or dropping old STLs) would bring the
   history down from 727 MB to a few tens of MB. It rewrites every commit hash and needs a force push to `main`, so
   every clone must be re-made and the commit tables updated. Only worth it if the size starts to hurt.

## Sources

- Blender Studio: [SVN setup](https://studio.blender.org/tools/td-guide/svn-setup),
  [design principles](https://studio.blender.org/tools/overview/design-principles),
  [folder structure](https://studio.blender.org/tools/td-guide/folder_structure_overview),
  [file naming](https://studio.blender.org/tools/naming-conventions/file-types),
  [benchmarking Git LFS, SVN and Mercurial](https://studio.blender.org/blog/benchmarking-version-control-git-lfs-svn-mercurial)
- [Godot docs: version control systems](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html)
- [Anchorpoint: Git with Blender](https://www.anchorpoint.app/blog/git-with-blender)
- [Blender manual: Save & Load preferences (Save Versions)](https://docs.blender.org/manual/en/dev/editors/preferences/save_load.html)
- [SCADPipeline: OpenSCAD built in CI, STLs attached to Releases](https://numberformat.github.io/SCADPipeline/),
  [OpenSCAD's .gitignore](https://www.Github.com/openscad/openscad/blob/master/.gitignore)
- GitHub: [conditions for large files](https://docs.github.com/en/enterprise/2.16/user/github/managing-large-files/conditions-for-large-files),
  [Git LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs),
  [LFS storage and bandwidth](https://docs.github.com/enterprise-cloud@latest/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage),
  [Actions checkout and LFS bandwidth](https://github.community/t/does-actions-checkout-count-against-git-lfs-bandwidth-usage/17835)

"""
Pull an earlier version of a design out of git history, without touching your working copy.

    python3 tools/get_version.py designs/d1 2eeddcf          # a commit, a tag (v2.0) or e.g. HEAD~3
    python3 tools/get_version.py designs/d2 v2.0 --out /tmp/d2-v2.0

Writes ring.blend, ring.stl, stats.json, ring.glb and the four renders of that version (whichever existed then) into
<design>/build/versions/<rev>/ (git-ignored). It knows where the files lived before the 2026-11 reorganization
(blender/, renders/, site/ring.glb, designs/d2/ring.blend ...). Round -> commit tables are in each DESIGN.md.
To rebuild or browse a whole old version instead:  git worktree add ../amys-ring-<rev> <rev>
"""
import sys, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS = ['front', 'side', 'top', 'three_quarter']
# current path first, then where the same file lived in older commits
PATHS = {
 'd1': {'ring.blend': ['designs/d1/model/ring.blend', 'blender/ring.blend'],
        'ring.stl': ['designs/d1/model/ring.stl', 'blender/ring.stl'],
        'stats.json': ['designs/d1/model/stats.json', 'blender/stats.json'],
        'ring.glb': ['site/d1/ring.glb', 'site/ring.glb'],
        **{'render_%s.png' % v: ['designs/d1/renders/current/render_%s.png' % v, 'renders/render_%s.png' % v] for v in VIEWS}},
 'd2': {'ring.blend': ['designs/d2/model/ring.blend', 'designs/d2/ring.blend'],
        'ring.stl': ['designs/d2/model/ring.stl', 'designs/d2/ring.stl'],
        'stats.json': ['designs/d2/model/stats.json', 'designs/d2/stats.json'],
        'ring.glb': ['site/d2/ring.glb'],
        **{'render_%s.png' % v: ['designs/d2/renders/current/render_%s.png' % v, 'designs/d2/renders/render_%s.png' % v] for v in VIEWS}},
}


def git(*a, **k): return subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True, **k)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    dn = os.path.basename(a[0].rstrip('/')); rev = a[1]
    if dn not in PATHS: sys.exit('unknown design %s (add its paths to PATHS in this script)' % dn)
    full = git('rev-parse', '--short', rev + '^{commit}', text=True)
    if full.returncode: sys.exit('unknown revision: ' + rev)
    out = a[a.index('--out') + 1] if '--out' in a else os.path.join(ROOT, 'designs', dn, 'build', 'versions', rev.replace('/', '_'))
    os.makedirs(out, exist_ok=True)
    print('%s at %s (%s)' % (dn, rev, full.stdout.strip()))
    for name, cands in PATHS[dn].items():
        for p in cands:
            r = git('show', '%s:%s' % (rev, p))
            if r.returncode == 0:
                open(os.path.join(out, name), 'wb').write(r.stdout)
                print('  %-24s <- %s' % (name, p)); break
        else:
            print('  %-24s (not in this version)' % name)
    print('->', os.path.relpath(out, os.getcwd()))

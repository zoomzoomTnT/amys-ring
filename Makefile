# Amy's Ring: common tasks.  `make` lists them.  D picks the design: D=1 or D=2.
BLENDER ?= blender
DESIGN = designs/d$(D)
need-design = $(if $(D),,$(error pick a design, e.g. make $@ D=2))

help:      ## list the tasks
	@echo "Amy's Ring: make <task> D=<design number>   (designs: $$(ls -d designs/d*/ | xargs -n1 basename | tr '\n' ' '))"
	@grep -E '^[a-z-]+: .*## ' Makefile | awk -F': +## ' '{printf "  make %-9s %s\n", $$1, $$2}'

build:     ## full build + 4 Cycles renders, ~15 min (writes model/ and build/)
	$(need-design)$(BLENDER) -b -P $(DESIGN)/build.py -- --render

trial:     ## quick trial renders of front + side, ~1 min (never touches model/)
	$(need-design)$(BLENDER) -b -P $(DESIGN)/build.py -- --fast --render --res 1000 --samples 24 --views front,side

check:     ## geometry only: stone counts and stone/metal collisions
	$(need-design)$(BLENDER) -b -P $(DESIGN)/build.py -- --checkonly

compare:   ## outline overlays + IoU against the reference picture
	$(need-design)python3 tools/overlay_views.py $(DESIGN)

review:    ## review sheet: reference | committed | this build
	$(need-design)python3 tools/review_sheet.py $(DESIGN)

limits:    ## check the hard limits (gold, ring size, stones, web model size)
	$(need-design)python3 tools/publish.py $(DESIGN) --check

publish:   ## check limits, then copy the GLB to site/ and the renders to renders/current/
	$(need-design)python3 tools/publish.py $(DESIGN)

version:   ## pull an old version out of git: make version D=1 REV=2eeddcf
	$(need-design)python3 tools/get_version.py $(DESIGN) $(REV)

viewer:    ## rebuild site/viewer.js from viewer-src/main.js
	npm i three@0.187 three-mesh-bvh@0.9 esbuild && npx esbuild viewer-src/main.js --bundle --format=esm --minify --outfile=site/viewer.js

serve:     ## preview the site at http://localhost:8080
	./site/serve.sh 8080

.PHONY: help build trial check compare review limits publish version viewer serve

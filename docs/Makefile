# Sphinx + MyST — Project Knowledge Pack
# Source: docs/source  →  Output: docs/build
# Usage: make html | clean | serve

SPHINXOPTS    ?=
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: html clean serve

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)
	@echo "Build finished. Open $(BUILDDIR)/html/index.html"

clean:
	rm -rf $(BUILDDIR)

serve: html
	@echo "Serving at http://localhost:8000 (open build/html/index.html if no autobuild)"
	-python -m http.server 8000 --directory $(BUILDDIR)/html

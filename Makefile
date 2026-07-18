PYTHON := venv/bin/python

.PHONY: build preview highlight image

build:
	$(PYTHON) build.py

preview:
	$(PYTHON) build.py preview

# regenerate syntax highlighting colours (rarely needed)
highlight:
	$(PYTHON) highlight.py > assets/static/highlight.css

# make image IMG=~/Desktop/books_2025.png
image:
	@test -n "$(IMG)" || { echo "usage: make image IMG=path/to/image.png"; exit 1; }
	@test -f "$(IMG)" || { echo "no such file: $(IMG)"; exit 1; }
	@out="input/images/$(basename $(notdir $(IMG))).jpg"; \
	sips -Z 900 -s format jpeg -s formatOptions 85 "$(IMG)" --out "$$out" >/dev/null; \
	echo "$$out  $$(du -h "$(IMG)" | cut -f1) -> $$(du -h "$$out" | cut -f1)"

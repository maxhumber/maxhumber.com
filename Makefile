PYTHON := venv/bin/python

.PHONY: build preview

build:
	$(PYTHON) build.py

preview:
	$(PYTHON) build.py preview

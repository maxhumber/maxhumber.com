PYTHON := venv/bin/python

.PHONY: build preview clean

build:
	$(PYTHON) build.py

preview:
	$(PYTHON) build.py preview

clean:
	rm -rf output/

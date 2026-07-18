PYTHON := venv/bin/python

.PHONY: build preview clean

build:
	$(PYTHON) blog.py

preview:
	$(PYTHON) blog.py preview

clean:
	rm -rf output/

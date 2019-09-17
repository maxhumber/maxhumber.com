preview:
	python blog.py preview
publish:
	python blog.py publish
highlight:
	pygmentize -S default -f html -a .codehilite > static/default.css

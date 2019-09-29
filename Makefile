preview:
	pipenv run python build.py preview
publish:
	pipenv run python build.py publish
highlight:
	pipenv run pygmentize -S default -f html -a .highlight > static/highlight.css

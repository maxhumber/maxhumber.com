import re
import pathlib
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

jin = Environment(loader=FileSystemLoader('templates'))

config = {
    'title': 'Max Humber'
}

# posts = list(pathlib.Path('content').glob('*.md'))
# file = 'content/2019-07-24_this_is_the_slug.md'

file = 'content/2019-07-25_blog_2.md'
stub = re.search('\/(.*)\.', file, re.IGNORECASE).group(1)
date, slug = stub.split('_', 1)

with open(file, 'r') as f:
    md = f.read()

html = markdown(md)
template = jin.get_template('post.html')
post = template.render(post=html, config=config)

# dump
p = pathlib.Path("output/content")
p.mkdir(parents=True, exist_ok=True)

filepath = p / f'{slug}.html'
with filepath.open("w", encoding="utf-8") as f:
    f.write(post)

# convert markdown
# move to output folder
# move static files
# replace references to stuff
# jinja templates
# jinja rendering


# jupyter to html





#

import re
import os
from pathlib import Path
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

jin = Environment(loader=FileSystemLoader('templates'))

CONFIG = {
    'title': 'Max Humber',
    'site_url': 'http://localhost:8000/'
}


# deal with configs for different viewing
# os.environ['BLOG_ENV'] = 'GITHUB'
# os.environ['BLOG_ENV'] = 'LOCAL'
#
# if os.environ['BLOG_ENV'] == 'LOCAL':
#     CONFIG['url'] = 'localhost'

# need to create index pages

posts = Path(input_folder).glob('*.md')


post = {
    'title': '', # in the header
    'date': '', # in the header
    'tags': [], # for rss feeds should be a list
    'content': '' # formatted as ready-to-go-html to be dropped in
}



t = jin.get_template('index.html')
html = t.render(posts=posts, config=CONFIG)
file = output_folder / f'{slug}.html'
with file.open('w', encoding='utf-8') as f:
    f.write(html)





def md_to_html(file, output_folder):
    stub = re.search('\/(.*)\.', str(file)).group(1)
    date, slug = stub.split('_', 1)
    with file.open('r') as f:
        md = f.read()
    html = markdown(md)
    t = jin.get_template('post.html')
    html = t.render(post=html, config=CONFIG)
    file = output_folder / f'{slug}.html'
    with file.open('w', encoding='utf-8') as f:
        f.write(html)

def convert(input_folder='content', output_folder='output'):
    output_folder = Path() / output_folder / input_folder
    output_folder.mkdir(parents=True, exist_ok=True)
    posts = Path(input_folder).glob('*.md')
    for post in posts:
        md_to_html(post, output_folder)

posts = Path(input_folder).glob('*.md')
post_slugs = []

p = list(posts)[0]
for p in post:
    stub = re.search('\/(.*)\.', str(p)).group(1)
    date, slug = stub.split('_', 1)
    post_slugs.append(slug)











# TODO:
# move static files
# replace references to stuff
# jinja templates
# jinja rendering
# jupyter to html
# python syntax highlight with pygments
# css files
# setup README instructions
# fix indent bug on conversion
# quick bootstrap mobile
# better config file
# linking in the index page
# rss feeds + tags
# setup environment
# bring in requirements.txt
# command line everything
# convert + local + publish
# separate github branch folder


import shutil
src = pathlib.Path('images')
dst = pathlib.Path('output/images')
shutil.copytree(src, dst)

# bits that I had before...

import os
import subprocess
from fire import Fire

def shell(command):
    '''Execute bash commands'''
    if isinstance(command, str):
        command = [command]
    [subprocess.call([c], shell=True) for c in command]

def html(pelican='pelicanconf.py', output='output', content='content', theme='theme'):
    '''Build website artifacts'''
    shell(f'pelican -s {pelican} -o {output} -t {theme} {content}')

def local(output='output'):
    '''Preview website content'''
    os.environ['PELICAN_ENV'] = 'DEV'
    html(output='output')
    shell(f'cd {output}; python -m http.server')

def publish(branch='gh-pages', output='output'):
    '''Push content to GitHub Pages'''
    os.environ['PELICAN_ENV'] = 'PROD'
    html(output='output')
    shell([
        f'ghp-import -m "Generate Pelican site" -b {branch} {output}',
        f'git push origin {branch}'
    ])

def convert(notebook, input='jupyter', output='content'):
    '''Convert a jupyter notebook to a pelican-compatible markdown file'''
    shell([
        f'cp {input}/{notebook}.ipynb {output}/{notebook}.ipynb',
        f'cd {output}; jupyter nbconvert --to markdown {notebook}.ipynb',
        f'cd {output}; rm {notebook}.ipynb'
    ])
    if os.path.isdir(f'{notebook}_files'):
        shell([
            f'cd {output}; cp -a {notebook}_files/. images/',
            f'cd {output}; rm -rf {notebook}_files'
        ])
    with open(f'{output}/{notebook}.md', encoding='UTF-8') as f:
        chapter = f.read().strip()
        chapter = chapter.replace(f'({notebook}_files/', '(images/')
    with open(f'{output}/{notebook}.md', 'w', encoding='UTF-8') as f:
        f.write(chapter)

def flush(output='output'):
    shell(f'rm -rf {output}')
#
# if __name__ == '__main__':
#     Fire({
#         'local': local,
#         'publish': publish,
#         'convert': convert,
#         'flush': flush
#     })

#

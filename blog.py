import shutil
import subprocess
from pathlib import Path

from fire import Fire
from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown_path

from config import website

JIN = Environment(loader=FileSystemLoader('templates'))
IN = Path(website['input_folder'])
OUT = Path(website['output_folder'])

def build_posts(website):
    '''Build, render, and write posts to the output/ folder'''
    posts = []
    template = JIN.get_template('post.html')
    for m in IN.glob('*.md'):
        html = markdown_path(m, extras=['metadata'])
        container = html.metadata.copy()
        container['content'] = template.render(html=str(html), website=website)
        posts.append(container)
        file = OUT / f"{container['slug']}.html"
        with file.open('w', encoding='utf-8') as f:
            f.write(container["content"])
    return posts

def build_index(website, posts):
    '''Build the index for all the blog posts'''
    template = JIN.get_template('index.html')
    index = template.render(posts=posts, website=website)
    file = OUT / 'index.html'
    with file.open('w', encoding='utf-8') as f:
        f.write(index)

def build_blog(website):
    '''Actually build the entire blog'''
    try:
        shutil.rmtree(OUT)
    except FileNotFoundError:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    posts = build_posts(website)
    build_index(website, posts)
    shutil.copytree(IN / 'images', OUT / 'images')

def shell(command):
    '''Execute bash commands'''
    if isinstance(command, str):
        command = [command]
    [subprocess.call([c], shell=True) for c in command]

def preview():
    '''Preview website content'''
    website['url'] = 'localhost:8000'
    JIN.globals['localhost'] = True
    build_blog(website)
    shell('cd output; python -m http.server')

def publish():
    '''Push content to GitHub Pages'''
    build_blog(website)
    shell([
        'git add .',
        'git commit -m "new blog post"',
        'git subtree push --prefix output origin gh-pages'
    ])

if __name__ == '__main__':
    Fire({
        'preview': preview,
        'publish': publish,
    })

# TODO:
# remove .html on the production version
# better theme-ing templating (bootstrap)
# add extra pages?
# python syntax highlight with pygments
# jupyter to html
# setup README instructions
# rss feeds + tags
# setup environment + requirements.txt

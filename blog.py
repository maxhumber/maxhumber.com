import shutil
import subprocess
from pathlib import Path
from fire import Fire
from markdown2 import markdown_path
from jinja2 import Environment, FileSystemLoader
from config import website

JIN = Environment(loader=FileSystemLoader('templates'))
IN = Path(website['input_folder'])
OUT = Path(website['output_folder'])

def build_posts(website):
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
    template = JIN.get_template('index.html')
    index = template.render(posts=posts, website=website)
    file = OUT / 'index.html'
    with file.open('w', encoding='utf-8') as f:
        f.write(index)

def build_blog(website):
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
    build_blog(website)
    shell('cd output; python -m http.server')

def publish():
    '''Push content to GitHub Pages'''
    build_blog(website)
    shell([
        'git add .',
        'git commit -m "new blog post"',
        'git push',
        'git subtree push --prefix output origin gh-pages'
    ])

if __name__ == '__main__':
    Fire({
        'preview': preview,
        'publish': publish,
    })

# TODO:
# local vs prod
# python syntax highlight with pygments
# jupyter to html
# css files
# setup README instructions
# quick bootstrap mobile
# rss feeds + tags
# setup environment
# bring in requirements.txt
# command line everything
# convert + local + publish
# separate github branch folder

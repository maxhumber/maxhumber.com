from pathlib import Path
import shutil
import subprocess
from fire import Fire
from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown_path

JIN = Environment(
    loader=FileSystemLoader('templates'),
    trim_blocks=True,
    lstrip_blocks=True
)

JIN.globals['URL'] = 'https://maxhumber.github.io/blog.py'
JIN.globals['TITLE'] = 'Max Humber'
IN = Path('content')
OUT = Path('output')

def build_posts():
    '''Build, render, and write posts to the output folder'''
    posts = []
    template = JIN.get_template('post.html')
    for m in IN.glob('*.md'):
        html = markdown_path(m, extras=['metadata', 'fenced-code-blocks'])
        container = html.metadata.copy()
        container['content'] = template.render(html=str(html))
        posts.append(container)
        file = OUT / f"{container['slug']}.html"
        with file.open('w', encoding='utf-8') as f:
            f.write(container["content"])
    return posts

def build_blog(posts):
    '''Build the index for all the blog posts'''
    template = JIN.get_template('blog.html')
    index = template.render(posts=posts)
    file = OUT / 'blog.html'
    with file.open('w', encoding='utf-8') as f:
        f.write(index)

def build_pages():
    '''Build, render, and write pages to the output folder'''
    template = JIN.get_template('page.html')
    for m in Path('pages').glob('*.md'):
        html = template.render(html=markdown_path(m))
        file = OUT / m.name.replace('.md', '.html')
        with file.open('w', encoding='utf-8') as f:
            f.write(html)

def build():
    '''Actually build the entire blog'''
    try:
        shutil.rmtree(OUT)
    except FileNotFoundError:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    build_pages()
    build_blog(build_posts())
    shutil.copytree(IN / 'images', OUT / 'images')
    shutil.copytree('static', OUT / 'static')

def shell(command):
    '''Execute bash commands'''
    if isinstance(command, str):
        command = [command]
    [subprocess.call([c], shell=True) for c in command]

def preview():
    '''Preview website content'''
    JIN.globals['URL'] = 'localhost:8000'
    build()
    shell('cd output; python -m http.server')

def publish():
    '''Push content to GitHub Pages'''
    build()
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
# fix the publish
# fix code indentation problem
# add talks, about, projects
# rss feeds for python tags
# jupyter to html
# submit to python blog aggregator
# favicons
# move to maxhumber.com

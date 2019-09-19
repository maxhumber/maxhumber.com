from pathlib import Path
import shutil
import subprocess
from fire import Fire
from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown, markdown_path
from nbconvert import MarkdownExporter
import nbformat

JIN = Environment(
    loader=FileSystemLoader('templates'),
    trim_blocks=True,
    lstrip_blocks=True
)

BLOG = Path('blog')
PAGES = Path('pages')
OUT = Path('output')

def jupyter_to_container(path):
    '''Convert a Jupyter Notebook into a Markdown Container'''
    with open(path, 'r', encoding='utf-8') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    metadata = notebook['cells'].pop(0)
    metadata = metadata['source'].split('\n')[1:-1]
    metadata = [m.split(':') for m in metadata]
    container = {m[0]:m[1].strip() for m in metadata}
    md_exporter = MarkdownExporter()
    # TODO: FIX THE IMAGE OUTPUT PROBLEM > resources
    md, resources = md_exporter.from_notebook_node(notebook)
    html = markdown(md, extras=['fenced-code-blocks'])
    template = JIN.get_template('blog_post.html')
    container['content'] = template.render(html=html)
    return container

def build_pages():
    '''Build, render, and write pages to the output folder'''
    template = JIN.get_template('page.html')
    for p in PAGES.glob('*.md'):
        html = template.render(html=markdown_path(p))
        file = OUT / p.name.replace('.md', '.html')
        with file.open('w', encoding='utf-8') as f:
            f.write(html)

def build_blog_posts():
    '''Build, render, and write blog posts to the output folder'''
    posts = []
    template = JIN.get_template('blog_post.html')
    for b in BLOG.glob('*.md'):
        html = markdown_path(b, extras=['metadata', 'fenced-code-blocks'])
        container = html.metadata.copy()
        container['content'] = template.render(html=str(html))
        posts.append(container)
    for j in BLOG.glob('*.ipynb'):
        container = jupyter_to_container(j)
        posts.append(container)
    for p in posts:
        file = OUT / f"{p['slug']}.html"
        with file.open('w', encoding='utf-8') as f:
            f.write(p['content'])
    return posts

def build_blog_index(posts):
    '''Build the index for all the blog posts'''
    template = JIN.get_template('blog_index.html')
    index = template.render(posts=posts)
    file = OUT / 'blog.html'
    with file.open('w', encoding='utf-8') as f:
        f.write(index)

def build():
    '''Actually build the entire blog'''
    try:
        shutil.rmtree(OUT)
    except FileNotFoundError:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    build_pages()
    build_blog_index(build_blog_posts())
    shutil.copyfile('CNAME', OUT / 'CNAME')
    shutil.copyfile('favicon.ico', OUT / 'favicon.ico')
    shutil.copytree(BLOG / 'images', OUT / 'images')
    shutil.copytree('static', OUT / 'static')

def shell(command):
    '''Execute bash commands'''
    if isinstance(command, str):
        command = [command]
    [subprocess.call([c], shell=True) for c in command]

def preview():
    '''Preview static website'''
    JIN.globals['DEVELOPMENT'] = True
    build()
    shell('cd output; python -m http.server')

def publish():
    '''Push static website to GitHub Pages'''
    build()
    shell([
        f'git add {str(OUT)}',
        'git commit -m "new blog post"',
        'git push origin `git subtree split --prefix output master`:gh-pages --force'
    ])

if __name__ == '__main__':
    Fire({
        'preview': preview,
        'publish': publish,
    })

# TODO:
# fix the jupyter image problem (resources)
# fix the /blog.html vs /blog
# rss feeds for python tags
# blog aggregator (eventually)

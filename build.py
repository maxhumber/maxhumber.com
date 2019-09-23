from pathlib import Path
import shutil
from subprocess import call
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

def extract_notebook_metadata(notebook):
    '''Extract metadata from the first Jupyter Notebook cell'''
    metadata = notebook['cells'].pop(0)
    metadata = metadata['source'].split('\n')[1:-1]
    metadata = [m.split(':') for m in metadata]
    return {m[0]:m[1].strip() for m in metadata}

def convert_notebook(path):
    '''Convert a Jupyter Notebook into Markdown and a Container'''
    with open(path, 'r', encoding='utf-8') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    container = extract_notebook_metadata(notebook)
    md, resources = MarkdownExporter().from_notebook_node(notebook)
    for fn, bytes in resources['outputs'].items():
        with open(f"{BLOG}/images/{container['slug']}-{fn}", 'wb') as f:
            f.write(bytes)
    md = md.replace('![png](', f"![png](images/{container['slug']}-")
    return md, container

def build_blog_posts():
    '''Build and render all the blog posts'''
    template = JIN.get_template('blog_post.html')
    posts = []
    for blog_post in BLOG.iterdir():
        if blog_post.name.endswith('.md'):
            html = markdown_path(blog_post, extras=['metadata', 'fenced-code-blocks'])
            container = html.metadata.copy()
        elif blog_post.name.endswith('.ipynb'):
            md, container = convert_notebook(blog_post)
            html = markdown(md, extras=['fenced-code-blocks'])
        else:
            continue
        container['content'] = template.render(html=html)
        posts.append(container)
    return posts

def build_blog_index(posts):
    '''Build the index for all the blog posts'''
    template = JIN.get_template('blog_index.html')
    html = template.render(posts=posts)
    container = {'slug': 'blog', 'content': html}
    return [container]

def build_pages():
    '''Build and render all the additional pages'''
    template = JIN.get_template('page.html')
    pages = []
    for p in PAGES.glob('*.md'):
        html = template.render(html=markdown_path(p))
        container = {'slug': p.name.replace('.md', ''), 'content': html}
        pages.append(container)
    return pages

def build():
    '''Actually build the entire blog'''
    try:
        shutil.rmtree(OUT)
    except FileNotFoundError:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    posts = build_blog_posts()
    blog_index = build_blog_index(posts)
    pages = build_pages()
    everything = posts + blog_index + pages
    for page in everything:
        file = OUT / f"{page['slug']}.html"
        with file.open('w', encoding='utf-8') as f:
            f.write(page['content'])
    shutil.copyfile('CNAME', OUT / 'CNAME')
    shutil.copyfile('favicon.ico', OUT / 'favicon.ico')
    shutil.copytree(BLOG / 'images', OUT / 'images')
    shutil.copytree('static', OUT / 'static')

def preview():
    '''Preview static website'''
    JIN.globals['DEVELOPMENT'] = True
    build()
    call('cd output; python -m http.server', shell=True)

def publish():
    '''Push static website to GitHub Pages'''
    build()
    call(f'git add {str(OUT)} {str(BLOG)}', shell=True)
    call('git commit -m "new blog post"', shell=True)
    call('git push', shell=True)
    call('git push origin `git subtree split --prefix output master`:gh-pages --force', shell=True)

if __name__ == '__main__':
    Fire({
        'preview': preview,
        'publish': publish,
    })

# TODO:
# fix /blog.html vs /blog on local
# rss feeds for python tags
# blog aggregator (eventually)
# only regenerate changed files

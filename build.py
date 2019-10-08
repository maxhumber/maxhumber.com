from pathlib import Path
import re
import shutil
from subprocess import run, Popen
import webbrowser
from fire import Fire
from jinja2 import Environment, FileSystemLoader
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
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

class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return f'\n<pre><code>{mistune.escape(code)}</code></pre>\n'
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

markdown = mistune.Markdown(renderer=HighlightRenderer())

def extract_metadata(md):
    dash_splits = md.split('---', maxsplit=2)
    meta = dash_splits[1]
    meta = meta.split('\n')[1:-1]
    meta = [m.split(': ', 1) for m in meta]
    meta = {k.strip(): v.strip() for k, v in meta}
    body = dash_splits[2].strip()
    return meta, body

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
    body = md.replace('![png](', f"![png](images/{container['slug']}-")
    return container, body

def fix_notebook_html(html):
    # add break line after code
    html = re.sub('\n</pre></div>','\n</pre></div>\n<br/>\n', html)
    # fix code outputs
    html = re.sub('\n\n\n</code></pre>','</code></pre>\n<br/>', html)
    # remove table style
    html = re.sub(r'\n<style scoped>.*?</style>', '', html, 0, flags=re.DOTALL)
    # remove table border
    html = re.sub('<table border="1" class="dataframe">', '<table class="table table-hover table-striped table-sm">', html)
    # remove silly right align
    html = re.sub('<tr style="text-align: right;">', '<tr>', html)
    # add break line after table
    html = re.sub('\n</table>\n</div>', '\n</table>\n</div>\n<br/>\n', html)
    # add table responsive
    html = re.sub('\n<div>\n<table', '\n<div class="table-responsive">\n<table', html)
    # add images responsive
    html = re.sub('(?<=\w\")(.*)(?=alt)', ' class="img-fluid mx-auto d-block" ', html)
    return html

def build_blog_posts():
    '''Build and render all the blog posts'''
    template = JIN.get_template('blog_post.html')
    posts = []
    for blog_post in BLOG.iterdir():
        if blog_post.name.endswith('.md'):
            with open(blog_post, 'r') as f:
                md = f.read()
            container, body = extract_metadata(md)
            html = markdown(body)
        elif blog_post.name.endswith('.ipynb'):
            container, body = convert_notebook(blog_post)
            html = markdown(body)
            html = fix_notebook_html(html)
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
        with open(p, 'r') as f:
            md = f.read()
        html = template.render(html=markdown(md))
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
    Popen('cd output; python -m http.server', shell=True)
    webbrowser.open('localhost:8000/blog.html')

def publish():
    '''Push static website to GitHub Pages'''
    build()
    run(f'git add {str(OUT)} {str(BLOG)}', shell=True)
    run('git commit -m "new blog post"', shell=True)
    run('git push', shell=True)
    run('git push origin `git subtree split --prefix output master`:gh-pages --force', shell=True)

if __name__ == '__main__':
    Fire({
        'preview': preview,
        'publish': publish,
    })

import re
import os
from pathlib import Path
from markdown import markdown as md_to_html
from jinja2 import Environment, FileSystemLoader

jin = Environment(loader=FileSystemLoader('templates'))

website = {
    'title': 'Max Humber',
    'url': 'http://localhost:8000',
    'input_folder': 'content',
    'output_folder': 'output'
}

def extract_and_delete(pattern, text):
    '''Extract and delete a regex pattern from a block of text.
    '''
    try:
        extract = re.search(pattern, text).group(1)
        text = re.sub(pattern, '', text).strip()
        return extract, text
    except AttributeError:
        return None, text

def path_to_post(markdown_file_path):
    '''Convert a markdown file path to a post metadata object.
    '''
    with markdown_file_path.open('r') as f:
        md = f.read()
    # extract and delete header information
    slug = re.search('\/(.*)\.', str(markdown_file_path)).group(1)
    title, md = extract_and_delete('title:\s(.*)\n', md)
    date, md = extract_and_delete('date:\s(.*)\n', md)
    tags, md = extract_and_delete('tags:\s(.*)\n', md)
    # convert and render with jinja
    html = md_to_html(md)
    template = jin.get_template('post.html')
    content = template.render(html=html, website=website)
    # create the post metadata object container
    post = {
        'title': title,
        'date': date,
        'tags': tags,
        'slug': f'{slug}.html',
        'content': content
    }
    return post

markdown_file_paths = Path(website['input_folder']).glob('*.md')
posts = []
for path in markdown_file_paths:
    post = path_to_post(path)
    posts.append(post)

output_folder = Path() / website['output_folder']
output_folder.mkdir(parents=True, exist_ok=True)

for post in posts:
    file = output_folder / f"{post['slug']}"
    with file.open('w', encoding='utf-8') as f:
        f.write(post["content"])

template = jin.get_template('index.html')
index = template.render(posts=posts, website=website)

file = output_folder / "index.html"
with file.open('w', encoding='utf-8') as f:
    f.write(index)

# spin up local server
cd output; python -m http.server

# push to subtree
git subtree push --prefix output origin gh-pages

# deal with configs for different viewing
# os.environ['BLOG_ENV'] = 'GITHUB'
# os.environ['BLOG_ENV'] = 'LOCAL'
#
# if os.environ['BLOG_ENV'] == 'LOCAL':
#     CONFIG['url'] = 'localhost'



# TODO:
# linking in the index page
# move static files
# replace references to stuff
# jupyter to html
# python syntax highlight with pygments
# css files
# setup README instructions
# quick bootstrap mobile
# better config file
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

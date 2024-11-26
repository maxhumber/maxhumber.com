from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, List
from shutil import copytree, copy2
from subprocess import run
from xml.etree import ElementTree as ET

import http.server
import socketserver
import signal
import sys

import markdown
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter


@dataclass
class Post:
    title: str
    date: str
    tags: List[str]
    content: str
    slug: str


def convert_markdown(content: str) -> tuple[Dict, str]:
    """Convert markdown to HTML and extract metadata"""
    md = markdown.Markdown(
        extensions=["fenced_code", "meta", "codehilite"],
        extension_configs={
            "codehilite": {"css_class": "highlight", "use_pygments": True}
        },
    )
    html = md.convert(content)
    meta = {k: v[0] for k, v in md.Meta.items()}
    return meta, html


def generate_post(file_path: Path) -> Post:
    """Read a markdown file and return a Post"""
    content = file_path.read_text()
    meta, html = convert_markdown(content)
    slug = file_path.stem.split("_", 1)[-1]
    return Post(
        title=meta.get("title", ""),
        date=meta.get("date", ""),
        tags=meta.get("tags", "").split(","),
        content=html,
        slug=slug,
    )


def copy_static_files(source: Path, destination: Path) -> None:
    """Copy static files from source to destination"""
    if source.exists():
        copytree(source, destination, dirs_exist_ok=True)


def copy_file(file: Path, destination: Path) -> None:
    """Copy a single file to dest"""
    if file.exists():
        copy2(file, destination)


def setup_output(input_dir: Path, output_dir: Path) -> None:
    """Setup output directory and copy static files"""
    output_dir.mkdir(exist_ok=True)
    static_dir = output_dir / "static"
    static_dir.mkdir(exist_ok=True)
    # Syntax highlighting CSS
    formatter = HtmlFormatter(
        style="lovelace",
        linenos=False,
        cssclass="highlight",
        noclasses=False,
        nobackground=False,
    )
    css = formatter.get_style_defs(".highlight")
    (static_dir / "highlight.css").write_text(css)
    # Copy static assets
    copy_file(Path("assets/signature.png"), static_dir / "signature.png")
    copy_file(Path("assets/style.css"), static_dir / "style.css")
    copy_static_files(Path("static"), static_dir)
    copy_static_files(input_dir / "images", output_dir / "images")
    # Copy root assets
    for file in ["CNAME", "favicon.ico", "blog.html"]:
        copy_file(Path("assets") / file, output_dir / file)


def build_site(
    input_dir: Path = Path("input"), output_dir: Path = Path("output")
) -> None:
    """Build the entire static site"""
    env = Environment(
        loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
    )
    setup_output(input_dir, output_dir)
    # Process all posts
    posts = [generate_post(f) for f in input_dir.glob("*.md")]
    posts.sort(key=lambda x: x.date, reverse=True)
    # Get all tags
    tags = {tag for post in posts for tag in post.tags}
    posts_by_tag = {tag: [p for p in posts if tag in p.tags] for tag in tags}
    # Generate tag pages
    for tag, tag_posts in posts_by_tag.items():
        html = env.get_template("tag.html").render(tag=f"#{tag}", posts=tag_posts)
        (output_dir / f"{tag}.html").write_text(html)
    # Generate post pages
    for post in posts:
        html = env.get_template("post.html").render(post=post)
        (output_dir / f"{post.slug}.html").write_text(html)
    # Generate RSS feed
    # generate_rss_feed(posts, output_dir) # Uncomment to generate RSS feed
    # Generate index
    html = env.get_template("index.html").render(tags=sorted(tags), is_index=True)
    (output_dir / "index.html").write_text(html)


def generate_rss_feed(posts: List[Post], output_dir: Path) -> None:
    """Generate RSS feed for posts tagged with 'code'"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Max Humber - Code Posts"
    ET.SubElement(channel, "link").text = "https://maxhumber.com"
    ET.SubElement(channel, "description").text = "Posts about coding by Max Humber"
    code_posts = [post for post in posts if "code" in post.tags]
    for post in code_posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "link").text = f"https://maxhumber.com/{post.slug}"
        ET.SubElement(item, "description").text = post.content
        pub_date = datetime.strptime(post.date, "%Y-%m-%d")
        ET.SubElement(item, "pubDate").text = format_datetime(pub_date)
        ET.SubElement(item, "guid").text = f"https://maxhumber.com/{post.slug}"
    tree = ET.ElementTree(rss)
    tree.write(output_dir / "feed.xml", encoding="utf-8", xml_declaration=True)


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.endswith(".html"):
            self.send_response(301)
            self.send_header("Location", self.path[:-5])
            self.end_headers()
            return
        path = self.path.rstrip("/")
        if not path or path == "/":
            path = "/index.html"
        elif "." not in path:
            if Path(self.directory + f"/{path}.html").exists():
                path = f"/{path}.html"
            else:
                path = f"{path}.html"
        self.path = path
        return super().do_GET()

    def log_message(self, format, *args):
        pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class SiteServer:
    def __init__(self, directory: str, port: int = 8000):
        self.directory = directory
        self.port = port
        handler = lambda *args: SiteHandler(*args, directory=directory)
        self.httpd = ReusableTCPServer(("", port), handler)

    def handle_shutdown(self, signum, frame):
        print("\nShutting down server...")
        self.httpd.server_close()
        sys.exit(0)

    def serve(self):
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        print(f"Serving at http://localhost:{self.port}")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.httpd.server_close()


def serve_site(directory: str, port: int = 8000) -> None:
    """Serve the site locally"""
    server = SiteServer(directory, port)
    server.serve()


def preview_site() -> None:
    """Build and preview the site"""
    build_site()
    serve_site("output")


def publish_site() -> None:
    """Build and publish to GitHub Pages"""
    build_site()
    run("git add output", shell=True)
    run('git commit -m "new blog post"', shell=True)
    run("git subtree split --prefix output -b gh-pages", shell=True)
    run("git push -f origin gh-pages:gh-pages", shell=True)
    run("git branch -D gh-pages", shell=True)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "build"
    if command == "preview":
        preview_site()
    elif command == "publish":
        publish_site()
    else:
        build_site()

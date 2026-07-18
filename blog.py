from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from functools import partial
from pathlib import Path
from shutil import copytree
from xml.etree import ElementTree as ET

import http.server
import sys

import markdown
from jinja2 import Environment, FileSystemLoader

INPUT = Path("input")
OUTPUT = Path("output")
SITE = "https://maxhumber.com"


@dataclass
class Post:
    title: str
    date: str
    tags: list[str]
    content: str
    slug: str


def read_post(path: Path) -> Post:
    """Read a markdown file and return a Post"""
    md = markdown.Markdown(
        extensions=["fenced_code", "meta", "codehilite", "tables"],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "guess_lang": False,
            }
        },
    )
    content = md.convert(path.read_text())
    meta = {k: v[0] for k, v in md.Meta.items()}
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    return Post(
        title=meta.get("title", ""),
        date=meta.get("date", ""),
        tags=tags,
        content=content,
        slug=meta.get("slug", path.stem),
    )


def render_rss(posts: list[Post], tag: str) -> bytes:
    """Build an RSS feed for a single tag"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Max Humber's #{tag} Posts"
    ET.SubElement(channel, "link").text = f"{SITE}/{tag}"
    description = f"Posts tagged with #{tag} by Max Humber"
    ET.SubElement(channel, "description").text = description
    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "link").text = f"{SITE}/{post.slug}"
        ET.SubElement(item, "description").text = post.content
        pub_date = datetime.strptime(post.date, "%Y-%m-%d")
        ET.SubElement(item, "pubDate").text = format_datetime(pub_date)
        ET.SubElement(item, "guid").text = f"{SITE}/{post.slug}"
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


def build() -> None:
    """Build the entire static site"""
    env = Environment(
        loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
    )
    OUTPUT.mkdir(exist_ok=True)
    copytree("assets", OUTPUT, dirs_exist_ok=True)
    copytree(INPUT / "images", OUTPUT / "images", dirs_exist_ok=True)
    posts = [read_post(f) for f in INPUT.glob("*.md")]
    for post in posts:
        html = env.get_template("post.html").render(post=post)
        (OUTPUT / f"{post.slug}.html").write_text(html)
    tagged = sorted((p for p in posts if p.tags), key=lambda p: p.date, reverse=True)
    tags = sorted({tag for post in tagged for tag in post.tags})
    (OUTPUT / "feed").mkdir(exist_ok=True)
    for tag in tags:
        tag_posts = [p for p in tagged if tag in p.tags]
        html = env.get_template("tag.html").render(
            tag=tag, posts=tag_posts, rss_path=f"/feed/{tag}.xml"
        )
        (OUTPUT / f"{tag}.html").write_text(html)
        (OUTPUT / "feed" / f"{tag}.xml").write_bytes(render_rss(tag_posts, tag))
    html = env.get_template("index.html").render(tags=tags, is_index=True)
    (OUTPUT / "index.html").write_text(html)


class Handler(http.server.SimpleHTTPRequestHandler):
    """Resolve extensionless URLs the way GitHub Pages does"""

    def translate_path(self, path):
        local = super().translate_path(path)
        if not Path(local).exists() and Path(local + ".html").exists():
            return local + ".html"
        return local


def preview(port: int = 8000) -> None:
    """Serve output/ locally"""
    handler = partial(Handler, directory=str(OUTPUT))
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    build()
    if "preview" in sys.argv[1:]:
        preview()

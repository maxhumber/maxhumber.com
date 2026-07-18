from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from html import unescape
from functools import partial
from pathlib import Path
from shutil import copytree, rmtree
from xml.etree import ElementTree as ET

import http.server
import re
import sys
import webbrowser

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

INPUT = Path("input")
OUTPUT = Path("output")
SITE = "https://maxhumber.com"
BLURB = "Writing about code, books, and quotes by Max Humber"
AVATAR = f"{SITE}/static/signature.png"


@dataclass
class Post:
    title: str
    date: str
    tags: list[str]
    content: str
    slug: str
    description: str
    image: str


def summarise(content: str, limit: int = 160) -> str:
    """First paragraph of a post, flattened for a meta description"""
    match = re.search(r"<p>(.*?)</p>", content, re.S)
    if not match:
        return BLURB
    text = " ".join(unescape(re.sub(r"<[^>]+>", "", match.group(1))).split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


def absolute_url(url: str) -> str:
    """Resolve a site-relative URL for feeds and social metadata."""
    if url.startswith(("http://", "https://")):
        return url
    return f"{SITE}/{url.lstrip('/')}"


def read_post(path: Path) -> Post:
    """Read a markdown file and return a Post"""
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "meta",
            "codehilite",
            "tables",
            "md_in_html",  # markdown inside <details> and friends
            "attr_list",
            "footnotes",
            "sane_lists",
            "smarty",  # curly quotes, proper dashes
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "guess_lang": False,
            }
        },
    )
    content = md.convert(path.read_text())
    # code blocks scroll sideways, so they need to be keyboard focusable
    content = content.replace("<pre>", '<pre tabindex="0">')
    # pygments wraps whitespace in spans we do not style, and they are 17% of the html
    content = re.sub(r'<span class="w">(\s*)</span>', r"\1", content)
    meta = {k: v[0] for k, v in md.Meta.items()}
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    first_image = re.search(r"""<img[^>]*src=["']([^"']+)""", content)
    return Post(
        title=meta.get("title", ""),
        date=meta.get("date", ""),
        tags=tags,
        content=content,
        slug=meta.get("slug", path.stem),
        description=meta.get("description") or summarise(content),
        image=absolute_url(first_image.group(1)) if first_image else AVATAR,
    )


def render_rss(posts: list[Post], tag: str) -> bytes:
    """Build an RSS feed for a single tag"""
    atom = "http://www.w3.org/2005/Atom"
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:atom": atom})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Max Humber's #{tag} Posts"
    ET.SubElement(channel, "link").text = f"{SITE}/{tag}"
    description = f"Posts tagged with #{tag} by Max Humber"
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(
        channel,
        "atom:link",
        href=f"{SITE}/feed/{tag}.xml",
        rel="self",
        type="application/rss+xml",
    )
    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "link").text = f"{SITE}/{post.slug}"
        # feed readers cannot resolve relative image paths, so make them absolute
        content = re.sub(r"""(src=["'])images/""", rf"\1{SITE}/images/", post.content)
        ET.SubElement(item, "description").text = content
        pub_date = datetime.strptime(post.date, "%Y-%m-%d")
        ET.SubElement(item, "pubDate").text = format_datetime(pub_date)
        ET.SubElement(item, "guid").text = f"{SITE}/{post.slug}"
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


def render_sitemap(posts: list[Post], tags: list[str]) -> bytes:
    """Build a sitemap of every page worth indexing"""
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urlset = ET.Element("urlset", xmlns=ns)
    pages = [(SITE, None)]
    pages += [(f"{SITE}/{p.slug}", p.date) for p in posts]
    pages += [(f"{SITE}/{tag}", None) for tag in tags]
    for loc, date in pages:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = loc
        if date:
            ET.SubElement(url, "lastmod").text = date
    return ET.tostring(urlset, encoding="utf-8", xml_declaration=True)


def build() -> None:
    """Build the entire static site"""
    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.globals.update(description=BLURB, image=AVATAR, og_type="website", url=SITE)
    rmtree(OUTPUT, ignore_errors=True)
    OUTPUT.mkdir()
    copytree("assets", OUTPUT, dirs_exist_ok=True)
    copytree(INPUT / "images", OUTPUT / "images", dirs_exist_ok=True)
    posts = [read_post(f) for f in INPUT.glob("*.md")]
    tagged = sorted((p for p in posts if p.tags), key=lambda p: p.date, reverse=True)
    tags = sorted({tag for post in tagged for tag in post.tags})
    env.globals["tags"] = tags  # every page advertises the feeds in its <head>
    for post in posts:
        html = env.get_template("post.html").render(
            post=post,
            description=post.description,
            image=post.image,
            og_type="article",
            url=f"{SITE}/{post.slug}",
        )
        (OUTPUT / f"{post.slug}.html").write_text(html)
    (OUTPUT / "feed").mkdir(exist_ok=True)
    for tag in tags:
        tag_posts = [p for p in tagged if tag in p.tags]
        html = env.get_template("tag.html").render(
            tag=tag,
            posts=tag_posts,
            rss_path=f"/feed/{tag}.xml",
            description=f"Posts tagged with #{tag} by Max Humber",
            url=f"{SITE}/{tag}",
        )
        (OUTPUT / f"{tag}.html").write_text(html)
        (OUTPUT / "feed" / f"{tag}.xml").write_bytes(render_rss(tag_posts, tag))
    html = env.get_template("index.html").render(posts=tagged)
    (OUTPUT / "index.html").write_text(html)
    (OUTPUT / "404.html").write_text(
        env.get_template("404.html").render(
            description="The requested page could not be found.", url=f"{SITE}/404"
        )
    )
    (OUTPUT / "sitemap.xml").write_bytes(render_sitemap(tagged, tags))


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
        webbrowser.open(f"http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    build()
    if "preview" in sys.argv[1:]:
        preview()

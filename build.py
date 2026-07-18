from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from functools import partial
from html import unescape
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

MARKDOWN_EXTENSIONS = [
    "extra",  # fenced code, tables, footnotes, attributes, and Markdown in HTML
    "meta",
    "codehilite",
    "sane_lists",
    "smarty",  # curly quotes, proper dashes
]
CODEHILITE_CONFIG = {
    "css_class": "highlight",
    "use_pygments": True,
    "guess_lang": False,
}


@dataclass
class Post:
    title: str
    date: str
    tags: list[str]
    content: str
    slug: str
    description: str


def markdown_parser() -> markdown.Markdown:
    """Create a fresh parser for one post."""
    return markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs={"codehilite": CODEHILITE_CONFIG},
    )


def clean_html(content: str) -> str:
    """Remove Pygments noise and make horizontal regions keyboard reachable."""
    content = content.replace("<pre>", '<pre tabindex="0">')
    content = content.replace("<table>", '<table tabindex="0">')
    return re.sub(r'<span class="w">(\s*)</span>', r"\1", content)


def summarise(content: str, limit: int = 160) -> str:
    """Return the first non-empty paragraph as a meta description."""
    for paragraph in re.findall(r"<p>(.*?)</p>", content, re.S):
        text = " ".join(unescape(re.sub(r"<[^>]+>", "", paragraph)).split())
        if text:
            return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"
    return BLURB


def read_post(path: Path) -> Post:
    """Parse one Markdown post and its frontmatter."""
    parser = markdown_parser()
    content = clean_html(parser.convert(path.read_text()))
    meta = {key: values[0] for key, values in parser.Meta.items()}
    tags = [tag.strip() for tag in meta.get("tags", "").split(",") if tag.strip()]
    return Post(
        title=meta.get("title", ""),
        date=meta.get("date", ""),
        tags=tags,
        content=content,
        slug=meta.get("slug", path.stem),
        description=meta.get("description") or summarise(content),
    )


def add_feed_item(channel: ET.Element, post: Post) -> None:
    """Append one post to an RSS channel."""
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = post.title
    ET.SubElement(item, "link").text = f"{SITE}/{post.slug}"
    content = re.sub(r"""(src=["'])images/""", rf"\1{SITE}/images/", post.content)
    ET.SubElement(item, "description").text = content
    ET.SubElement(item, "pubDate").text = format_datetime(
        datetime.strptime(post.date, "%Y-%m-%d")
    )
    ET.SubElement(item, "guid").text = f"{SITE}/{post.slug}"


def render_rss(posts: list[Post], tag: str) -> bytes:
    """Build an RSS feed for one tag."""
    rss = ET.Element(
        "rss",
        version="2.0",
        attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"},
    )
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
        add_feed_item(channel, post)
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


def sitemap_pages(posts: list[Post], tags: list[str]):
    """Yield every indexable URL and its optional last-modified date."""
    yield SITE, None
    yield from ((f"{SITE}/{post.slug}", post.date) for post in posts)
    yield from ((f"{SITE}/{tag}", None) for tag in tags)


def render_sitemap(posts: list[Post], tags: list[str]) -> bytes:
    """Build a sitemap of every page worth indexing."""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for location, date in sitemap_pages(posts, tags):
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = location
        if date:
            ET.SubElement(url, "lastmod").text = date
    return ET.tostring(urlset, encoding="utf-8", xml_declaration=True)


def site_environment(tags: list[str]) -> Environment:
    """Return templates with the metadata every page shares."""
    environment = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(["html", "xml"]),
    )
    environment.globals.update(
        description=BLURB,
        og_type="website",
        tags=tags,
        url=SITE,
    )
    return environment


def write_page(
    environment: Environment,
    template: str,
    destination: Path,
    **context: object,
) -> None:
    """Render a template to one HTML file."""
    destination.write_text(environment.get_template(template).render(**context))


def prepare_output() -> None:
    """Recreate the output directory with static assets."""
    rmtree(OUTPUT, ignore_errors=True)
    OUTPUT.mkdir()
    copytree("assets", OUTPUT, dirs_exist_ok=True)
    copytree(INPUT / "images", OUTPUT / "images", dirs_exist_ok=True)


def write_posts(environment: Environment, posts: list[Post]) -> None:
    """Render every post page."""
    for post in posts:
        write_page(
            environment,
            "post.html",
            OUTPUT / f"{post.slug}.html",
            post=post,
            description=post.description,
            og_type="article",
            url=f"{SITE}/{post.slug}",
        )


def write_tags(environment: Environment, posts: list[Post], tags: list[str]) -> None:
    """Render tag pages and their RSS feeds."""
    feed_directory = OUTPUT / "feed"
    feed_directory.mkdir()
    for tag in tags:
        tagged = [post for post in posts if tag in post.tags]
        write_page(
            environment,
            "tag.html",
            OUTPUT / f"{tag}.html",
            tag=tag,
            posts=tagged,
            rss_path=f"/feed/{tag}.xml",
            description=f"Posts tagged with #{tag} by Max Humber",
            url=f"{SITE}/{tag}",
        )
        (feed_directory / f"{tag}.xml").write_bytes(render_rss(tagged, tag))


def build() -> None:
    """Build the entire static site."""
    prepare_output()
    posts = [read_post(path) for path in INPUT.glob("*.md")]
    tagged = sorted(
        (post for post in posts if post.tags),
        key=lambda post: post.date,
        reverse=True,
    )
    tags = sorted({tag for post in tagged for tag in post.tags})
    environment = site_environment(tags)
    write_posts(environment, posts)
    write_tags(environment, tagged, tags)
    write_page(environment, "index.html", OUTPUT / "index.html", posts=tagged)
    write_page(
        environment,
        "404.html",
        OUTPUT / "404.html",
        description="The requested page could not be found.",
        url=f"{SITE}/404",
    )
    (OUTPUT / "sitemap.xml").write_bytes(render_sitemap(tagged, tags))


class Handler(http.server.SimpleHTTPRequestHandler):
    """Resolve extensionless URLs the way GitHub Pages does."""

    def translate_path(self, path: str) -> str:
        local = super().translate_path(path)
        if not Path(local).exists() and Path(local + ".html").exists():
            return local + ".html"
        return local


def preview(port: int = 8000) -> None:
    """Serve output locally."""
    handler = partial(Handler, directory=str(OUTPUT))
    with http.server.ThreadingHTTPServer(("", port), handler) as server:
        print(f"Serving at http://localhost:{port}")
        webbrowser.open(f"http://localhost:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    build()
    if "preview" in sys.argv[1:]:
        preview()

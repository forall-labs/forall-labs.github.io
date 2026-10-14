#!/usr/bin/env python3
"""Build the Forall Labs site: site/ -> public/

Every page is a fragment in site/pages/ whose first line is a JSON header in an
HTML comment. The fragment is dropped into site/base.html, which carries the
shared header, nav and footer, so the chrome is defined exactly once.

    python3 tools/build.py          # writes public/
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "public"
BASE_URL = "https://forall-labs.github.io"

# Order matters: this is the nav, left to right.
NAV = [
    ("/research/", "Research", False),
    ("/projects/", "Projects", False),
    ("/people/", "People", False),
    ("/news/", "News", False),
    ("/about/", "About", False),
    ("/join/", "Join us", True),
]

HEADER_RE = re.compile(r"^\s*<!--\s*(\{.*?\})\s*-->\s*", re.S)


def read_page(path):
    raw = path.read_text(encoding="utf-8")
    m = HEADER_RE.match(raw)
    if not m:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing JSON header comment on line 1")
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path.relative_to(ROOT)}: bad JSON header: {e}")
    for key in ("url", "title", "description"):
        if key not in meta:
            raise SystemExit(f"{path.relative_to(ROOT)}: header is missing '{key}'")
    return meta, raw[m.end():]


def render_nav(current):
    """`current` is the nav entry to mark. A page can override it with "nav" in
    its header, so /apply/ lights up "Join us" rather than nothing."""
    out = []
    for href, label, is_cta in NAV:
        cls = ' class="nav-cta"' if is_cta else ""
        # A section is current for its own page and anything beneath it.
        cur = ' aria-current="page"' if current == href or (href != "/" and current.startswith(href)) else ""
        out.append(f'        <a href="{href}"{cls}{cur}>{label}</a>')
    return "\n".join(out)


def out_path(url):
    """'/' -> public/index.html, '/research/' -> public/research/index.html,
    '/404.html' -> public/404.html"""
    if url.endswith(".html"):
        return OUT / url.lstrip("/")
    return OUT / url.strip("/") / "index.html" if url != "/" else OUT / "index.html"


def main():
    base = (SITE / "base.html").read_text(encoding="utf-8")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    pages = sorted((SITE / "pages").glob("*.html"))
    if not pages:
        raise SystemExit("no pages found in site/pages/")

    urls = []
    for path in pages:
        meta, body = read_page(path)
        html = (base
                .replace("{{nav}}", render_nav(meta.get("nav", meta["url"])))
                .replace("{{content}}", body.rstrip() + "\n")
                .replace("{{title}}", meta["title"])
                .replace("{{og_title}}", meta.get("og_title", meta["title"]))
                .replace("{{description}}", meta["description"])
                .replace("{{base}}", BASE_URL)
                .replace("{{url}}", meta["url"]))
        dest = out_path(meta["url"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        if meta.get("sitemap", True):
            urls.append(meta["url"])
        print(f"  {meta['url']:<28} <- site/pages/{path.name}")

    for item in (SITE / "static").iterdir():
        if item.is_dir():
            shutil.copytree(item, OUT / item.name)
        else:
            shutil.copy2(item, OUT / item.name)
    print(f"  static/                      <- {len(list((SITE / 'static').iterdir()))} files")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sorted(urls):
        sitemap.append(f"  <url><loc>{BASE_URL}{url}</loc></url>")
    sitemap.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")

    print(f"\nBuilt {len(pages)} pages into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()

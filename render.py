#!/usr/bin/env python
"""Render carousel slides from a markdown content file.

    python render.py my-post.md                    # -> ./out/my-post/slide-01.png ... (next to the .md)
    python render.py my-post.md --size ig          # Instagram 4:5 (1080x1350)
    python render.py my-post.md --out ./slides     # choose the output folder
    python render.py *.md                          # batch
    python render.py my-post.md --html             # also keep the slide HTML (debug)

Content file = YAML front matter + cards:

    ---
    format: listcards          # folder under formats/
    size: ref                  # ref | ig | ig-tall | x | x-compact   (see formats/<fmt>/theme.yaml)
    title: "How X does ==Y=="  # ==word== gets the marker highlight
    theme: {colors: {accent: "#0A84FF"}}  # optional per-post theme overrides
    ---
    ## Card heading
    - bullet
    <!-- slide -->           # optional: force a slide break before the next card

Slides are packed automatically: cards are measured in the browser and added to a
slide until the next one would not fit. The title only appears on slide 1.
"""
from __future__ import annotations

import argparse
import copy
import html
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
SLIDE_BREAK = "<!-- slide -->"


# ---------------------------------------------------------------- parsing
def parse_content(path: Path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        text = text[m.end():]
    cards, cur, breaks = [], None, set()
    for raw in text.split("\n"):
        line = raw.rstrip()
        if line.strip() == SLIDE_BREAK:
            breaks.add(len(cards))
        elif line.startswith("## "):
            cur = {"heading": line[3:].strip(), "bullets": []}
            cards.append(cur)
        elif re.match(r"^\s*[-*] ", line):
            if cur is None:
                sys.exit(f"{path.name}: bullet before any '## heading'")
            cur["bullets"].append(re.sub(r"^\s*[-*] ", "", line).strip())
        elif line.strip() and not line.startswith("#"):
            if cur is None or not cur["bullets"]:
                sys.exit(f"{path.name}: unexpected text: {line[:60]!r}")
            cur["bullets"][-1] += " " + line.strip()  # wrapped bullet continuation
    if not cards:
        sys.exit(f"{path.name}: no '## ' cards found")
    return meta, cards, breaks


def title_to_html(title: str) -> str:
    esc = html.escape(title, quote=False)
    return re.sub(r"==(.+?)==", r"<mark>\1</mark>", esc)


def deep_merge(a, b):
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


# ---------------------------------------------------------------- rendering
class Renderer:
    def __init__(self, fmt: str, theme_override: dict, size: str, tmp: Path):
        self.tmp = tmp
        self.dir = ROOT / "formats" / fmt
        if not self.dir.exists():
            sys.exit(f"unknown format '{fmt}' (have: {[p.name for p in (ROOT/'formats').iterdir()]})")
        self.t = deep_merge(yaml.safe_load((self.dir / "theme.yaml").read_text(encoding="utf-8")), theme_override)
        if size not in self.t["canvas"]:
            sys.exit(f"unknown size '{size}' (have: {list(self.t['canvas'])})")
        cv = self.t["canvas"][size]
        self.W, self.H, self.out_w = cv["w"], cv["h"], cv["out_w"]
        self.env = Environment(loader=FileSystemLoader(str(self.dir)), autoescape=True)
        self.tpl = self.env.get_template("template.html.j2")
        self.font_url = (ROOT / "fonts" / "Inter-Variable.woff2").as_uri()
        self.font_ext_url = (ROOT / "fonts" / "Inter-Variable-ext.woff2").as_uri()

    def html(self, cards, title_html=None):
        return self.tpl.render(t=self.t, W=self.W, H=self.H, cards=cards, title_html=title_html,
                               font_url=self.font_url, font_ext_url=self.font_ext_url)

    def measure(self, page, cards, title_html):
        """Return (title_block_height, [card heights]) using real browser layout."""
        self.load(page, self.html(cards, title_html))
        card_h = page.eval_on_selector_all(".card", "els => els.map(e => e.getBoundingClientRect().height)")
        title_h = page.eval_on_selector("h1", "e => e.getBoundingClientRect().height") if title_html else 0
        if title_html:
            title_h += self.t["space"]["title_to_cards"]
        return title_h, card_h

    def load(self, page, doc):
        self.tmp.parent.mkdir(parents=True, exist_ok=True)
        self.tmp.write_text(doc, encoding="utf-8")
        page.goto(self.tmp.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_function("document.fonts.status === 'loaded'")

    def pack(self, title_h, card_h, breaks):
        """Greedy pack into slides. Returns list of lists of card indexes."""
        avail = self.H - 2 * self.t["space"]["page_x"] + self.t["space"].get("fit_slack", 0)
        gap = self.t["space"]["card_gap"]
        slides, cur, used = [], [], title_h
        for i, h in enumerate(card_h):
            need = h + (gap if cur else 0)
            if cur and (used + need > avail or i in breaks):
                slides.append(cur)
                cur, used = [], 0
                need = h
            if h > avail:
                print(f"  ! card {i+1} is taller than a slide ({h:.0f}px > {avail}px) - shorten it", file=sys.stderr)
            cur.append(i)
            used += need
        slides.append(cur)
        return slides


def render_file(path: Path, args, browser):
    meta, cards, breaks = parse_content(path)
    fmt = args.format or meta.get("format", "listcards")
    size = args.size or meta.get("size", "ref")
    out_base = (args.out or path.resolve().parent / "out").resolve()
    slug = path.stem if size == "ref" else f"{path.stem}-{size}"  # one folder per size
    out_dir = out_base / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / ".tmp-slide.html"
    r = Renderer(fmt, meta.get("theme", {}), size, tmp)
    title_html = title_to_html(meta["title"]) if meta.get("title") else None
    for old in out_dir.glob("slide-*.png"):
        old.unlink()

    ctx = browser.new_context(viewport={"width": r.W, "height": r.H}, device_scale_factor=r.out_w / r.W)
    page = ctx.new_page()
    try:
        title_h, card_h = r.measure(page, cards, title_html)
        slides = r.pack(title_h, card_h, breaks)
        for n, idxs in enumerate(slides, 1):
            doc = r.html([cards[i] for i in idxs], title_html if n == 1 else None)
            r.load(page, doc)
            png = out_dir / f"slide-{n:02d}.png"
            page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": r.W, "height": r.H})
            if args.html:
                (out_dir / f"slide-{n:02d}.html").write_text(doc, encoding="utf-8")
            print(f"  {png}  ({len(idxs)} cards)")
    finally:
        ctx.close()
    tmp.unlink(missing_ok=True)
    print(f"{path.name}: {len(cards)} cards -> {len(slides)} slides [{fmt}/{size}]")
    return out_dir


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--size", help="override size preset (ref | ig | ig-tall | x | x-compact)")
    ap.add_argument("--out", type=Path, help="output folder (default: ./out next to each .md file)")
    ap.add_argument("--format", help="override format folder")
    ap.add_argument("--html", action="store_true", help="keep per-slide HTML next to the PNGs")
    args = ap.parse_args()
    with sync_playwright() as p:
        flags = ["--disable-lcd-text", "--font-render-hinting=none"]  # grayscale AA, like the reference
        for kw in ({"channel": "msedge"}, {"channel": "chrome"}, {}):  # {} needs `playwright install chromium`
            try:
                browser = p.chromium.launch(args=flags, **kw)
                break
            except Exception:
                continue
        else:
            sys.exit("No Chromium-based browser found. Install Edge/Chrome or run: playwright install chromium")
        for f in args.files:
            print(f"== {f}")
            render_file(f, args, browser)
        browser.close()


if __name__ == "__main__":
    main()

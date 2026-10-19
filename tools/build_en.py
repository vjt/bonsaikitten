#!/usr/bin/env python3
"""Generate gatti.sindro.me/en/: responsive remake of bonsaikitten.com (MIT, 2000).

Texts are NOT retyped: every page is parsed from the Wayback mirror (same parse a
browser does, via html5lib) and its body is re-serialised through a whitelist of
tags, layout tables turned into responsive blocks. Same look as the Italian
remake at / (shares /css/gatti.css and /js/gatti.js, adds en/css/bk.css).

usage: .venv/bin/python build_en.py <mirror-dir> <out-dir>
Verify with textdiff.py --macnbsp, page by page.
"""
import hashlib
import html
import os
import re
import shutil
import sys

import html5lib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keepbrowsing import block as keep_browsing  # noqa: E402

SRC, OUT = sys.argv[1], sys.argv[2]
MAIL = "gatti@sindro.me"
MAILS = re.compile(r"[\w.-]+@bonsaikitt(?:en|y)\.com")
CSS_V = hashlib.sha256(open(os.path.join(OUT, "css", "bk.css"), "rb").read()).hexdigest()[:8]
GATTI_V = hashlib.sha256(open(os.path.join(OUT, "..", "css", "gatti.css"), "rb").read()).hexdigest()[:8]

# page -> nav section it belongs to
PAGES = {
    "index": None, "bkintro": "bkintro", "bkmethod": "bkmethod", "bkgallery": "bkgallery",
    "bksales": "bksales", "bkguestbook": "bkguestbook", "bknews": "bknews",
    "bnw": "bkgallery", "gray": "bkgallery", "g4": "bkgallery", "white": "bkgallery",
    "vessels": "bksales", "tools": "bksales", "451c": "bknews",
    "techniques": "bkguestbook", "maildrop": "bkguestbook",
    "biocat/biocat": "bkguestbook", "framecat/framecat": "bknews",
    "tissuecat/tissuecat": "bknews", "xmascat/xmascat": "bknews",
}
NAV = [("bkintro", "Intro"), ("bkmethod", "Method"), ("bksales", "Sales"),
       ("bkgallery", "Gallery"), ("bkguestbook", "Guestbook"), ("bknews", "News")]
# "Next" chain, same order as the IT root (vjt 2026-10-19); intro and gallery hang off it
CHAIN = [("bkmethod", "Method"), ("bksales", "Sales"), ("bkguestbook", "Guestbook"), ("bknews", "News")]
CHAIN_EXTRA = [("bkintro", "Intro"), ("bkgallery", "Gallery")]
CHAIN_PARENT = {"bkintro": None, "bkgallery": "bksales"}
TAGLINE = """Dedicated to preserving
         the long lost art of body modification in
         housepets."""
WAYBACK = "https://web.archive.org/web/20021129165442/http://www.bonsaikitten.com/"
# Same one-liner the /2000/ archive pages carry (plus the /2000/ self link added there too).
BANNER = ('<div class="bufala">Archive of bonsaikitten.com &mdash; satirical hoax (MIT 2000), no cats were harmed '
          '/ bufala satirica, nessun gatto maltrattato. &middot; <a href="' + WAYBACK + '">Internet Archive</a> '
          '&middot; <a href="/2000/">2000</a> &middot; <a href="/">gattibonsai.it</a> &middot; <a href="/com/">.com</a></div>')
# pages that read better full width
WIDE = {"vessels", "tools", "bnw", "gray", "g4", "bknews", "biocat/biocat", "framecat/framecat",
        "tissuecat/tissuecat", "xmascat/xmascat", "bksales"}
LETTERS = {"bkguestbook", "maildrop", "techniques"}  # split into cards at each <hr>

BLOCK = {"p", "div", "table", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "center", "blockquote",
         "pre", "hr", "address", "dl", "form", "tbody", "tr", "td", "th"}
KEEP = {"b", "i", "em", "strong", "u", "tt", "code", "sup", "sub", "ul", "ol", "li", "blockquote", "pre",
        "h1", "h2", "h3", "h4", "h5", "h6", "dl", "dt", "dd"}
DROP = {"script", "embed", "noscript", "style", "meta", "title"}
IMG_EXT = re.compile(r"\.(jpe?g|gif|png)$", re.I)
CATALOG_BG = {"#ccffcc": "c1", "#ffffcc": "c2", "#ffcccc": "c3"}


def esc(t):
    return html.escape(t, quote=False).replace("\xa0", "&nbsp;")


def attr(v):
    return html.escape(v, quote=True)


def text_of(el):
    return "".join(el.itertext())


def blank(el):
    """No visible text and no image."""
    return not text_of(el).replace("\xa0", " ").strip() and el.find(".//img") is None


def has_block(el):
    return any(d.tag in BLOCK for d in el.iter() if d is not el)


def children(el):
    """Yield (kind, payload) in document order: ('text', str) / ('el', element)."""
    if el.text:
        yield "text", el.text
    for c in el:
        yield "el", c
        if c.tail:
            yield "text", c.tail


class Conv:
    def __init__(self, up):
        self.up = up

    def kids(self, el, **kw):
        return "".join(esc(p) if k == "text" else self.node(p, **kw) for k, p in children(el))

    def href(self, h):
        h = h.strip()
        if h == "/":  # bonsaikitten.com's own root
            return self.up + "index.html"
        return h

    def node(self, el, in_a=False, in_h=False):
        t = el.tag if isinstance(el.tag, str) else ""
        t = t.lower()
        if not t or t in DROP or t.startswith("x-claris"):
            return ""
        a = {k.lower(): v for k, v in el.attrib.items()}

        if t == "table":
            return self.table(el)
        if t == "img":
            return self.img(a, in_a)
        if t == "a":
            h = self.href(a.get("href", ""))
            extra = ' data-lb' if IMG_EXT.search(h) else ""
            if not h:
                return self.kids(el, in_a=True, in_h=in_h)
            return f'<a href="{attr(h)}"{extra}>' + self.kids(el, in_a=True, in_h=in_h) + "</a>"
        if t == "br":
            return "<br>"
        if t == "hr":
            return "<hr>\n"
        if t == "p":
            if blank(el):
                return ""
            tag = "div" if has_block(el) else "p"
            cls = ' class="center"' if a.get("align", "").lower() == "center" else ""
            return f"<{tag}{cls}>" + self.kids(el, in_a=in_a, in_h=in_h) + f"</{tag}>\n"
        if t == "center":
            if in_h:
                return self.kids(el, in_a=in_a, in_h=in_h)
            if blank(el):
                return ""
            return '<div class="center">' + self.kids(el, in_a=in_a) + "</div>\n"
        if t == "font":
            if has_block(el):
                return self.kids(el, in_a=in_a, in_h=in_h)
            cls = []
            size = a.get("size", "").replace(" ", "")
            if size in ("+2", "+3", "+4"):
                cls.append("fs-l")
            elif size == "+1":
                cls.append("fs-m")
            col = a.get("color", "").lower()
            if col in ("#ff0000", "#880022", "#880000"):
                cls.append("hl")
            elif col in ("#3366ff",):
                cls.append("hl-blue")
            inner = self.kids(el, in_a=in_a, in_h=in_h)
            return f'<span class="{" ".join(cls)}">{inner}</span>' if cls else inner
        if t == "blink":
            return '<span class="blink">' + self.kids(el, in_a=in_a, in_h=in_h) + "</span>"
        if t == "address":
            return '<span class="hint">' + self.kids(el, in_a=in_a) + "</span> "
        if t in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if blank(el):
                return ""
            # Kids' pages wrote whole paragraphs as <H3>: keep the weight, not the heading role.
            if t == "h3" and len(text_of(el).split()) > 18:
                return '<p class="h3p">' + self.kids(el, in_a=in_a, in_h=True) + "</p>\n"
            return f"<{t}>" + self.kids(el, in_a=in_a, in_h=True) + f"</{t}>\n"
        if t == "ul" or t == "ol":
            return f"<{t}>" + self.kids(el, in_a=in_a) + f"</{t}>\n"
        if t == "div":
            return "<div>" + self.kids(el, in_a=in_a, in_h=in_h) + "</div>\n"
        if t in KEEP:
            return f"<{t}>" + self.kids(el, in_a=in_a, in_h=in_h) + f"</{t}>"
        # body/html/tbody/unknown: unwrap
        return self.kids(el, in_a=in_a, in_h=in_h)

    def img(self, a, in_a):
        src = a.get("src", "")
        w, h = a.get("width", ""), a.get("height", "")
        dims = (f' width="{w}"' if w.isdigit() else "") + (f' height="{h}"' if h.isdigit() else "")
        alt = attr(a.get("alt", ""))
        small = w.isdigit() and int(w) < 100
        cls = ' class="ico"' if small else ""
        tag = f'<img src="{attr(src)}"{dims} alt="{alt}"{cls} loading="lazy">'
        if not in_a and not small:
            return f'<a href="{attr(src)}" data-lb class="zoom">{tag}</a>'
        return tag

    # ---------------------------------------------------------------- tables
    def rows(self, table):
        return [tr for tr in table.iter("tr") if self.owner(tr) is table]

    def owner(self, node):
        # nearest enclosing table (html5lib etree has no parent pointers: precomputed)
        return PARENT_TABLE.get(node)

    def cells(self, tr):
        return [c for c in tr if isinstance(c.tag, str) and c.tag in ("td", "th")]

    def table(self, el):
        bg = el.attrib.get("bgcolor", "").lower()
        rows = self.rows(el)
        if bg in CATALOG_BG and rows and rows[0].find(".//address") is not None:
            return self.catalog(el, CATALOG_BG[bg], rows)
        steps = el.attrib.get("border") == "1"
        cls = "tbl steps" if steps else ("tbl tint" if bg == "#ffffcc" else "tbl")
        out = []
        for tr in rows:
            cs = [c for c in self.cells(tr) if not blank(c)]
            if not cs:
                continue
            cells = []
            for c in cs:
                only_img = not text_of(c).replace("\xa0", " ").strip()
                cells.append(f'<div class="td{" pic" if only_img else ""}">' + self.kids(c) + "</div>")
            out.append('<div class="tr">' + "".join(cells) + "</div>")
        if not out:
            return ""
        return f'<div class="{cls}">\n' + "\n".join(out) + "\n</div>\n"

    def catalog(self, el, cnum, rows):
        head = self.cells(rows[0])
        title = text_of(head[0]).strip()
        hint = esc(" ".join(text_of(head[-1]).split()))
        items = []
        for tr in rows[1:]:
            cs = self.cells(tr)
            desc, pics = cs[1], cs[2]
            flag, body = "", []
            for p in desc:
                if p.tag != "p":
                    continue
                if p.find(".//i") is not None and p.find(".//b") is None and len(text_of(p).split()) <= 3:
                    flag = f'<p class="code"><span class="flag">{esc(text_of(p).strip())}</span></p>'
                else:
                    body.append('<p class="desc">' + self.kids(p) + "</p>")
            links = []
            for a in pics.iter("a"):
                h = a.attrib.get("href", "")
                if IMG_EXT.search(h):
                    links.append(f'<a href="{attr(h)}" data-lb><img src="{attr(h)}" alt="" loading="lazy"></a>')
                else:
                    links.append(f'<a class="nopic" href="{attr(h)}">' + self.kids(a, in_a=True) + "</a>")
            items.append(f'<article class="item">\n<div class="txt">{flag}\n{chr(10).join(body)}</div>\n'
                         f'<div class="pics">{"".join(links)}</div>\n</article>')
        return (f'<section class="catalog {cnum}">\n<div class="head">\n<h2>{esc(title)}</h2>\n'
                f'<span class="hint">{hint}</span>\n</div>\n<div class="grid">\n' + "\n".join(items) +
                "\n</div>\n</section>\n")


PARENT_TABLE = {}


def index_tables(root):
    def walk(el, table):
        for c in el:
            if not isinstance(c.tag, str):
                continue
            PARENT_TABLE[c] = table
            walk(c, c if c.tag == "table" else table)
    walk(root, None)


def load(name):
    raw = open(os.path.join(SRC, name + ".html"), "rb").read()
    raw = raw.replace(b"\xca", b"\xa0")  # MacRoman no-break space (Claris Home Page)
    # Claris' <X-CLARIS-WINDOW> in <head> would open the body and swallow the whole page
    raw = re.sub(rb"<X-CLARIS-[^>]*>", b"", raw, flags=re.I)
    doc = html5lib.parse(raw.decode("cp1252"), treebuilder="etree", namespaceHTMLElements=False)
    # the archive banner may sit deep inside unclosed <CENTER>/<H1>: drop it wherever it is
    for par in list(doc.iter()):
        for c in list(par):
            if c.tag == "div" and "#ffffe0" in (c.attrib.get("style") or "").lower():
                if (c.tail or "").strip():
                    raise SystemExit(f"{name}: text after banner")
                par.remove(c)
    index_tables(doc)
    title = (doc.find(".//title").text or "").strip()
    body = doc.find("body")
    kept = []
    for c in body:
        style = (c.attrib.get("style") or "").lower()
        if c.tag == "center" and c.find(".//img[@src]") is not None and any(
                "bklogo.gif" in (i.attrib.get("src") or "") for i in c.iter("img")):
            continue  # masthead + nav, rebuilt below
        if c.tag == "div" and "#ffffe0" in style:
            continue  # archive banner, rebuilt below
        kept.append(c)
    return title, body, kept


def letters(conv, body, kept):
    """Guestbook-style pages: one card per <hr>-separated letter."""
    groups, cur = [], []
    if body.text and body.text.strip():
        cur.append(esc(body.text))
    for c in kept:
        if c.tag == "hr":
            groups.append(cur)
            cur = []
        else:
            cur.append(conv.node(c))
        if c.tail:
            cur.append(esc(c.tail))
    groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        s = "".join(g).strip()
        if not s:
            continue
        cls = "card intro" if i == 0 else "card letter"
        out.append(f'<article class="{cls}">\n{s}\n</article>')
    return "\n".join(out)


def render(name, section):
    up = "../" * name.count("/")
    title, body, kept = load(name)
    conv = Conv(up)
    if name in LETTERS:
        main = letters(conv, body, kept)
    else:
        parts = [esc(body.text or "")]
        for c in kept:
            parts.append(conv.node(c))
            parts.append(esc(c.tail or ""))
        main = "".join(parts)
    main = re.sub(r"\n{3,}", "\n\n", main).strip()
    kb = keep_browsing("en", CHAIN, name, lambda k: up + k + ".html",
                       parent=CHAIN_PARENT.get(section, section), home=("index", "Home"), extra=CHAIN_EXTRA)
    lang_switch = '<li class="lang" data-nodiff><a href="/" lang="it" hreflang="it" data-lang="it">Italiano</a></li>'
    page_head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
{'<link rel="alternate" hreflang="it" href="https://gatti.sindro.me/">' + chr(10) + '<link rel="alternate" hreflang="en" href="https://gatti.sindro.me/en/">' + chr(10) if name == "index" else ""}<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#000000">
<link rel="stylesheet" href="/css/gatti.css?v={GATTI_V}">
<link rel="stylesheet" href="{up}css/bk.css?v={CSS_V}">
<script>document.documentElement.className+=' js'</script>
<script src="/js/gatti.js" defer></script>
</head>
"""
    if name == "white":  # the fake "403 Forbidden" page: no chrome, like the original
        html_ = page_head + f"""<body class="storia bk">
<header class="masthead">
<div class="brand"><a href="index.html"><img src="bklogo.gif" width="147" height="135" alt="Bonsai Kitten"></a></div>
</header>
<main>
<div class="forbidden">
{main}
</div>
{kb}
</main>
<footer>
{BANNER}
</footer>
</body>
</html>
"""
    else:
        items = "\n".join(
            f'<li><a href="{up}{p}.html"{" aria-current=\"page\"" if p == section else ""}>{label}</a>'
            + (f' <img class="throb" src="{up}newthrob.gif" width="25" height="9" alt="">' if p == "bknews" else "")
            + "</li>" for p, label in NAV)
        html_ = page_head + f"""<body class="bk">
<header class="masthead">
<img class="kitten" src="{up}facebw.jpg" width="144" height="108" alt="">
<div class="brand">
<a href="{up}index.html"><img src="{up}bklogo.gif" width="147" height="135" alt="Bonsai Kitten"></a>
<p class="tagline">{TAGLINE}</p>
</div>
<img class="kitten" src="{up}facebw.jpg" width="144" height="108" alt="">
</header>
<nav class="topnav" aria-label="Sections">
<div class="inner">
<a class="mini" href="{up}index.html"><img src="{up}bklogo.gif" width="147" height="135" alt=""></a>
<button class="burger" type="button" aria-expanded="false" aria-controls="navlist" aria-label="Menu"><span></span><span></span><span></span></button>
<ul id="navlist">
{items}
{lang_switch}
</ul>
</div>
</nav>
<main class="{'wide' if name in WIDE else ''}{' letters' if name in LETTERS else ''}">
{main}
{kb}
</main>
<footer>
{BANNER}
</footer>
</body>
</html>
"""
    dst = os.path.join(OUT, name + ".html")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(MAILS.sub(MAIL, html_.replace('<main class="">', "<main>")))


for n, sec in PAGES.items():
    render(n, sec)

# assets: every non-HTML file of the mirror, same relative paths (old image URLs keep working)
for d, _, fs in os.walk(SRC):
    for f in fs:
        if f.endswith(".html"):
            continue
        s = os.path.join(d, f)
        t = os.path.join(OUT, os.path.relpath(s, SRC))
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copy2(s, t)

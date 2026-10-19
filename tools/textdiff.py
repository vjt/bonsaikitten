#!/usr/bin/env python3
"""Visible-text diff: original Wayback mirror page vs 2026 remake.

Skips script/noscript/style and any element carrying data-nodiff (the
language switch added in 2026, which is not part of the original text);
splits off the hoax banner (div.bufala, or the archive's inline-styled
#ffffcc / #ffffe0 div) and compares it separately. Whitespace (incl. nbsp)
is collapsed. Title is compared too.

--macnbsp: the original is MacRoman-flavoured (bonsaikitten.com, Claris
Home Page): byte 0xCA is a no-break space, not cp1252 'Ê'.
"""
import sys, re, difflib
from html.parser import HTMLParser

SKIP = {"script", "noscript", "style"}
VOID = {"br", "img", "meta", "link", "hr", "input", "area", "base", "col", "source", "wbr"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.title = None
        self.in_title = False
        self.body, self.banner = [], []
        self.banner_depth = 0  # >0 while inside banner div
        self.nd_tag, self.nd_depth = None, 0  # inside a data-nodiff element

    def handle_starttag(self, tag, attrs):
        if self.nd_depth:
            if tag == self.nd_tag:
                self.nd_depth += 1
            return
        if "data-nodiff" in dict(attrs) and tag not in VOID:
            self.nd_tag, self.nd_depth = tag, 1
            return
        if tag in SKIP:
            self.skip += 1
        if tag == "title":
            self.in_title = True
            self.title = ""
        if tag == "div":
            a = dict(attrs)
            if self.banner_depth:
                self.banner_depth += 1
            elif "bufala" in (a.get("class") or "") or re.search(r"background:#ffff(cc|e0)", a.get("style") or ""):
                self.banner_depth = 1

    def handle_endtag(self, tag):
        if self.nd_depth:
            if tag == self.nd_tag:
                self.nd_depth -= 1
            return
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False
        if tag == "div" and self.banner_depth:
            self.banner_depth -= 1

    def handle_data(self, d):
        if self.in_title:
            self.title += d
            return
        if self.skip or self.nd_depth:
            return
        (self.banner if self.banner_depth else self.body).append(d)


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def load(path, enc, macnbsp=False):
    p = P()
    raw = open(path, "rb").read()
    if macnbsp:
        raw = raw.replace(b"\xca", "\xa0".encode(enc))
    p.feed(raw.decode(enc, errors="strict"))
    return norm(p.title or ""), norm("".join(p.body)), norm("".join(p.banner))


def main():
    orig, new = sys.argv[1], sys.argv[2]
    ot, ob, obn = load(orig, "cp1252", "--macnbsp" in sys.argv)
    if new == "-":
        print(f"TITLE: {ot}\nBODY: {ob}\nBANNER: {obn}\n")
        return
    nt, nb, nbn = load(new, "utf-8")
    ok = True
    if ot != nt:
        ok = False
        print(f"  TITLE: {ot!r} != {nt!r}")
    if ob != nb:
        ok = False
        for l in difflib.unified_diff(ob.split(" "), nb.split(" "), "orig", "new", n=3, lineterm=""):
            print("  " + l)
    if obn != nbn:
        ok = False
        print(f"  BANNER differs:\n   {obn!r}\n   {nbn!r}")
    print(("OK   " if ok else "DIFF ") + new + f"  ({len(ob.split())} words)")
    if "--dump" in sys.argv:
        print(ob)
    sys.exit(0 if ok else 1)


main()

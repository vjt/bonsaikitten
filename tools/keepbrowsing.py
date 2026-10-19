"""'Keep browsing' block at the end of every remade page (IT root and /en/).

Next page follows the nav order and wraps last -> first; pages outside the nav
hang off a parent section (next = the section after it, back = the parent).
It's 2026 UI chrome, not original text: marked data-nodiff for textdiff.py.
"""
import html

WORDS = {
    "it": {"next": "Continua:", "back": "Indietro:", "aria": "Continua a sfogliare", "home": "Home"},
    "en": {"next": "Next:", "back": "Back:", "aria": "Keep browsing", "home": "Home"},
}

# The other language's home, same link as the one in the hamburger menu.
SWITCH = {
    "it": ("/en/", "en", "English"),
    "en": ("/", "it", "Italiano"),
}


def block(lang, nav, current, href, parent=None, home=None, extra=()):
    """nav: [(key, label)]; current: page key; href(key) -> url;
    parent: nav key a non-nav page belongs to (None = home / start of nav);
    home: (key, label) of the home page, listed with the sections;
    extra: [(key, label)] non-nav pages appended to the sections list."""
    w = WORDS[lang]
    keys = [k for k, _ in nav]
    label = dict(nav)
    label.update(dict(extra))
    if home:
        label[home[0]] = home[1]
    if current in keys:
        i = keys.index(current)
        nxt, prev = keys[(i + 1) % len(keys)], keys[i - 1]
    elif parent in keys:
        i = keys.index(parent)
        nxt, prev = keys[(i + 1) % len(keys)], parent
    else:  # home or a page with no section: start of the nav
        nxt, prev = keys[0], None
    e = html.escape
    out = [f'<nav class="more" aria-label="{w["aria"]}" data-nodiff>',
           f'<a class="next" href="{e(href(nxt))}"><span class="k">{w["next"]}</span> '
           f'<span class="t">{e(label[nxt])}</span> <span class="arrow" aria-hidden="true">&rarr;</span></a>']
    if prev:
        out.append(f'<a class="prev" href="{e(href(prev))}"><span aria-hidden="true">&larr;</span> '
                   f'{w["back"]} {e(label[prev])}</a>')
    others = ([home] if home and current != home[0] else []) + [
        (k, l) for k, l in list(nav) + list(extra) if k not in (current, nxt)]
    to, code, name = SWITCH[lang]
    out.append(f'<a class="lang" href="{to}" lang="{code}" hreflang="{code}" data-lang="{code}">'
               f'<span aria-hidden="true">&#127760;</span> {name}</a>')
    out.append('<ul class="sections">' + "".join(
        f'<li><a href="{e(href(k))}">{e(l)}</a></li>' for k, l in others) + "</ul>")
    out.append("</nav>")
    return "\n".join(out)

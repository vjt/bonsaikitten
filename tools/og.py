import os, re, sys, html
from PIL import Image
root = sys.argv[1]; base = "https://gatti.sindro.me/"
def card(out, imgs, logo):
    c = Image.new("RGB", (1200, 630), "black")
    x = 40
    for p in imgs:
        im = Image.open(os.path.join(root, p)).convert("RGB"); r = 420 / im.height
        im = im.resize((int(im.width * r), 420), Image.LANCZOS); c.paste(im, (x, 40)); x += im.width + 30
    lg = Image.open(os.path.join(root, logo)).convert("RGBA"); r = 130 / lg.height
    lg = lg.resize((int(lg.width * r), 130), Image.NEAREST)
    c.paste(lg, ((1200 - lg.width) // 2, 470), lg); c.save(os.path.join(root, out), quality=88)
card("og-it.jpg", ["lb.jpg", "gall1.jpg"], "logo-com.gif")
card("en/og-en.jpg", ["en/facebw.jpg", "en/cube.jpg"], "en/bklogo.gif")
HEADER = {"lb.jpg", "logo-com.gif", "logo.gif", "facebw.jpg", "bklogo.gif"}
def size(p):
    try: return Image.open(p).size
    except Exception: return (0, 0)
n = 0
for d, _, fs in os.walk(root):
    rel = os.path.relpath(d, root)
    if rel.split(os.sep)[0] in ("2000", "2001", "com"): continue
    for f in fs:
        if not f.endswith(".html"): continue
        p = os.path.join(d, f); s = open(p, encoding="utf-8").read()
        s = re.sub(r'\n?<meta (property="og:[^"]+"|name="twitter:[^"]+"|name="description")[^>]*>', "", s)
        s = re.sub(r'\n?<link rel="canonical"[^>]*>', "", s)
        en = rel.split(os.sep)[0] == "en"
        relp = os.path.relpath(p, root).replace(os.sep, "/")
        url = base + ("" if relp == "index.html" else "en/" if relp == "en/index.html" else relp)
        title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip())
        body = s.split("</header>", 1)[-1]
        txt = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m)) for m in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S))
        txt = " ".join(txt.split())
        desc = (txt[:197].rsplit(" ", 1)[0] + "…") if len(txt) > 200 else txt
        if not desc: desc = "Bonsai Kitten — the original 2000 hoax, restored." if en else "Gatti Bonsai — l'originale del 2000, restaurato."
        img = None
        for src in re.findall(r'<img[^>]*src="([^"]+)"', body):
            ip = os.path.normpath(os.path.join(d, src.split("?")[0]))
            if os.path.basename(ip) in HEADER or not ip.lower().endswith((".jpg", ".jpeg", ".png")): continue
            w, h = size(ip)
            if w >= 200 and h >= 150: img = (os.path.relpath(ip, root).replace(os.sep, "/"), w, h); break
        if not img: img = ("en/og-en.jpg", 1200, 630) if en else ("og-it.jpg", 1200, 630)
        e = lambda v: html.escape(v, quote=True)
        tags = [f'<link rel="canonical" href="{url}">', f'<meta name="description" content="{e(desc)}">',
            '<meta property="og:type" content="website">', f'<meta property="og:site_name" content="{"Bonsai Kitten" if en else "Gatti Bonsai"}">',
            f'<meta property="og:locale" content="{"en_US" if en else "it_IT"}">', f'<meta property="og:title" content="{e(title)}">',
            f'<meta property="og:description" content="{e(desc)}">', f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{base}{img[0]}">', f'<meta property="og:image:width" content="{img[1]}">',
            f'<meta property="og:image:height" content="{img[2]}">',
            f'<meta name="twitter:card" content="{"summary_large_image" if img[1] >= 600 else "summary"}">',
            f'<meta name="twitter:title" content="{e(title)}">', f'<meta name="twitter:description" content="{e(desc)}">',
            f'<meta name="twitter:image" content="{base}{img[0]}">']
        s = re.sub(r"(</title>)", r"\1\n" + "\n".join(tags).replace("\\", "\\\\"), s, count=1)
        open(p, "w", encoding="utf-8").write(s); n += 1
        print(relp, img[0], desc[:60])
print(n)

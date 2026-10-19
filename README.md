# bonsaikitten

Source of [gatti.sindro.me](https://gatti.sindro.me/): a 2026 restoration of the
Bonsai Kitten satirical hoax (MIT, 2000) and of its Italian offshoots
gattibonsai.it / gattibonsai.com (2001–2002).

**It is a hoax. No cats were ever harmed.** The originals were satire; this is an archive.

## Layout

- `site/` — the document root, as deployed.
  - `/` — Italian remake (responsive), texts copied verbatim from the gattibonsai.com captures
  - `/en/` — English remake of bonsaikitten.com, texts verbatim
  - `/2000/`, `/2001/`, `/com/` — untouched mirrors of the Internet Archive captures
- `tools/` — the generators.
  - `build_com.py` — Italian root pages (texts are inline)
  - `build_en.py` — English pages, parsed from the `/2000/` mirror
  - `keepbrowsing.py` — the "Continua / Next" block at the end of each page
  - `og.py` — share cards and OpenGraph / Twitter tags; run it after every rebuild
  - `textdiff.py` — visible-text diff between an original and its remake

## Rebuild

```sh
python3 -m venv tools/.venv && tools/.venv/bin/pip install -r tools/requirements.txt
tools/.venv/bin/python tools/build_com.py site
tools/.venv/bin/python tools/build_en.py site/2000 site/en
tools/.venv/bin/python tools/og.py site
```

Mail addresses of the original sites are rewritten to gatti@sindro.me.

## Provenance

Every page links back to its Internet Archive capture. The original texts and images
belong to their authors; the 2026 markup, styles and tools are released as-is.

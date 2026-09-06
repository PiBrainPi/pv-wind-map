#!/usr/bin/env python3
# build_vorschau.py — baut klickbare HTML-Vorschau des LinkedIn-Artikels mit eingebetteten Screenshots
import base64, re, pathlib

root = pathlib.Path(__file__).parent
md = (root / 'artikel.md').read_text(encoding='utf-8')

def img_b64(p):
    return base64.b64encode((root / p).read_bytes()).decode()

def md_inline(s):
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'<img src="data:image/png;base64,{img_b64(m.group(2))}" alt="{m.group(1)}">', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s

lines = md.split('\n')
out, in_list = [], False
for raw in lines:
    ln = raw.rstrip()
    s = ln.lstrip()
    # Bullet-Listen auch eingerückt erkennen (3-Space-Indent aus Markdown)
    if s.startswith('- '):
        if not in_list:
            out.append('<ul>'); in_list = True
        out.append(f'<li>{md_inline(s[2:])}</li>')
        continue
    if in_list:
        out.append('</ul>'); in_list = False
    if ln.startswith('# '):
        out.append(f'<h1>{md_inline(ln[2:])}</h1>')
    elif ln.startswith('## '):
        out.append(f'<h2>{md_inline(ln[3:])}</h2>')
    elif ln.startswith('!['):
        out.append(f'<figure>{md_inline(ln)}')
    elif ln.startswith('*Abb.'):
        out.append(f'</figure><figcaption>{md_inline(ln.strip("*"))}</figcaption>')
    elif ln.strip() == '---':
        out.append('<hr>')
    elif ln.startswith('*') and ln.endswith('*') and not ln.startswith('**'):
        out.append(f'<p class="subtitle">{md_inline(ln)}</p>')
    elif ln.strip():
        out.append(f'<p>{md_inline(ln)}</p>')
if in_list: out.append('</ul>')

# figure-Capsules schließen: nach figcaption nichts nötig — CSS ordnet caption unter Bild
html_out = out

body = '\n'.join(html_out)

page = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LinkedIn-Artikel Vorschau — PV &amp; Wind Karte</title>
<style>
:root {{ --brand:#0a66c2; --ink:#24292f; --muted:#57606a; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background:#f4f2ee; color:var(--ink); line-height:1.65; }}
.paper {{ max-width:860px; margin:24px auto 60px; background:#fff; border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,.12); padding:48px 56px; }}
h1 {{ font-size:1.9rem; line-height:1.25; margin:8px 0 12px; color:var(--ink); }}
h2 {{ font-size:1.35rem; margin:36px 0 12px; color:var(--ink); border-top:1px solid #e5e5e5; padding-top:24px; }}
p {{ margin:0 0 14px; font-size:1.02rem; }}
p.subtitle {{ color:var(--muted); font-size:.95rem; }}
ul {{ margin:0 0 14px 22px; }}
li {{ margin-bottom:6px; }}
hr {{ border:none; border-top:1px solid #e5e5e5; margin:28px 0; }}
figure {{ margin:22px 0; }}
figure img {{ max-width:100%; border-radius:8px; border:1px solid #e0e0e0; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
figcaption {{ font-size:.88rem; color:var(--muted); margin-top:8px; font-style:italic; }}
code {{ background:#f0f2f5; padding:1px 5px; border-radius:4px; font-size:.9em; }}
a {{ color:var(--brand); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.brandbar {{ text-align:center; padding:18px 0 0; color:var(--muted); font-size:.85rem; }}
.brandbar strong {{ color:var(--ink); }}
.topnote {{ background:#eef3f8; border:1px solid #cfe0f1; border-radius:8px; padding:12px 16px; font-size:.9rem; color:#3b5b7d; margin-bottom:24px; }}
footer.brand {{ text-align:center; padding:22px 0 0; font-size:.85rem; color:var(--muted); }}
@media (max-width:700px) {{ .paper {{ padding:24px 18px; }} }}
</style>
</head>
<body>
<div class="paper">
<div class="topnote">📋 <strong>Vorschau</strong> — LinkedIn-Artikel-Entwurf (Fassung 1). Bilder eingebettet, Reihenfolge = Einfügereihenfolge bei LinkedIn. Text als Markdown-Datei <code>artikel.md</code> zum 1:1-Kopieren.</div>
{body}
<div class="brandbar">PiBrain by fabibuss@web.de</div>
</div>
<footer class="brand">Vorschau generiert für Fabian Bussenius · ingenieur-tools.de · wind-pv-map.ingenieur-tools.de</footer>
</body>
</html>'''

(root / 'LinkedIn_Artikel_Vorschau.html').write_text(page, encoding='utf-8')
print('OK:', (root / 'LinkedIn_Artikel_Vorschau.html').stat().st_size, 'bytes')

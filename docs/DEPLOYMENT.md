# Deployment — GitHub Pages + eigene Domain

> Stand: 2026-08-30 · Ziel: `ingenieur-tools.de` als Portal, `wind-pv-map.ingenieur-tools.de` für die Karte.

## Architektur

```
ingenieur-tools.de                  → Portal (Repo: PiBrainPi/ingenieur-tools-portal)
└── wind-pv-map.ingenieur-tools.de  → PV-/Wind-Karte (Repo: PiBrainPi/pv-wind-map)
```

Beide laufen auf **GitHub Pages** (kostenlos, 0 €/Monat). Einzige Kosten: die `.de`-Domain (~5–8 €/Jahr, vom USER gekauft).

## Live-URLs (GitHub Pages, vor Domain-Anbindung)

| Tool | Repo | GitHub-Pages-URL |
|---|---|---|
| Karte | `PiBrainPi/pv-wind-map` | `https://pibrainpi.github.io/pv-wind-map/` |
| Portal | `PiBrainPi/ingenieur-tools-portal` | `https://pibrainpi.github.io/ingenieur-tools-portal/` |

## Deployment-Mechanismus (statisch, kein CI)

Beide Repos nutzen den **`gh-pages`-Branch** als Pages-Quelle (statisch, keine GitHub-Actions nötig).

### Karte (`pv-wind-map`)
- `main` = Quellcode (src/, scripts/, docs/). `dist/` ist **gitignored** (nicht im Repo).
- `gh-pages`-Branch = fertige, deploybare Site: `index.html` (hostbar), `index_singlefile.html`, `assets/*.json`.
- **Update-Ablauf (Daten-Refresh):**
  1. **Backup zuerst:** `cp data/mastr.db ~/backups/mastr-$(date +%F).db` (Regel seit 2026-09-03!)
  2. Lokal `dist/` regenerieren: `cp src/index.html dist/index.html` + `python3 scripts/bundle_singlefile.py` (oder voll `bash scripts/build.sh`)
  3. `main` committen + pushen (vorher `git fetch origin && git rebase origin/main`)
  4. `gh-pages`-Branch: Quell-Dateien temporär aus main holen, `index.html` + `assets/*.json` committen, pushen
  5. Pages deployed automatisch (~30 s Cache-Delay)
- ⚠️ **Deploy-Cleanup-Regel (Lehre aus 2026-09-03):** Auf gh-pages niemals `rm -rf data/ dist/ iterations/`
  ausführen — diese Ordner sind Branch-übergreifend dieselben lokalen Verzeichnisse (gitignored)!
  Nur `src/` und `scripts/` vom gh-pages-Checkin entfernen (die werden temporär aus main ausgecheckt).
  Ein Fehlversuch am 2026-09-03 löschte `data/mastr.db` (DB muss dann via `import_mastr.py` neu
  aufgebaut werden — Snapshots/Historie gehen dabei verloren) und wurde nur durch Backups in
  `~/hermes_human-share/` begrenzbar.

### Portal (`ingenieur-tools-portal`)
- `main` = `index.html` (Startseite). `gh-pages` = identischer Inhalt (Pages-Quelle).
- Einfach: Startseite ändern → `main` + `gh-pages` pushen.

## Domain-Anbindung (Stand 2026-08-30)

### DNS-Records bei netcup (CCP → Domains → 🔍 → CloudDNS)

| Host | Typ | Wert | Zweck | Status |
|---|---|---|---|---|
| *(leer)* | A | `185.199.108.153` | Portal Apex | ✅ gesetzt |
| `www` | CNAME | `pibrainpi.github.io` | Portal kanonisch | ✅ gesetzt |
| `wind-pv-map` | CNAME | `pibrainpi.github.io` | Karte | ✅ gesetzt |
| `galton-board` | CNAME | `pibrainpi.github.io` | Galton-Board (Repo folgt) | ✅ DNS vorbereitet |

> netcup erlaubt **keinen CNAME direkt auf der Apex** (Konflikt mit SOA/NS) → für `ingenieur-tools.de` wird ein **A-Record** verwendet. Die anderen sind CNAMEs.

### Custom-Domains in den Repos (GitHub Pages)

| Repo | Custom Domain | Status |
|---|---|---|
| `pv-wind-map` (Karte) | `wind-pv-map.ingenieur-tools.de` | ✅ HTTPS fertig (Let's Encrypt) |
| `ingenieur-tools-portal` | `www.ingenieur-tools.de` | ⏳ HTTPS-Zertifikat in Ausstellung |

> Portal nutzt `www` als kanonische Domain — GitHub leitet `www` → Apex automatisch um. Zertifikat braucht nach CNAME-Setup Zeit (~30–60 Min.).

### Verifikation (durchgeführt 2026-08-30, aktualisiert 2026-09-03)

- ✅ Karte `index.html` → HTTP 200, Leaflet lädt, `assets/einheiten.json` (24 MB) → **65.659 Einheiten (V19, Stand 2026-09-04)**
- ✅ V19 live (04.09., User-Freigabe): Betroffenheits-Tab final — Deploy-Verifizierung
  served-SHA (index_singlefile.html) = local-SHA (d678a6c6…), Daten-JSON live OK
  (65.659 Anlagen), Pages `status: built`, Deployment-SHA = gh-pages-HEAD e66c774.
  gh-pages-Update künftig mit `/tmp/deploy_ghpages_v19.sh`-Muster (Worktree, CNAME unangetastet,
  kein dist/-Pickup — siehe Skill publishing-projects-to-github).
- ✅ V8j-Fixes live (`top: 86px` im HTML nachweisbar), Disclaimer-Trigger unter Zoom-Control
- ✅ Portal `index.html` → HTTP 200, enthält Link zur Karten-Subdomain
- ✅ Single-File rekonstruiert, SHA-identisch mit Backup (kein Datenverlust)
- ✅ `www.ingenieur-tools.de` + `galton-board.ingenieur-tools.de` DNS propagiert (Cloudflare DoH)
- ✅ Karte HTTPS fertig; Portal HTTPS-Zertifikat wartet auf LE-Rate-Limit-Fenster (~06./07.09.2026)

## Wichtige Hinweise

- **Keine Secrets im Repo** — `.env`, `data/`, `dist/` sind gitignored.
- Repos sind **öffentlich** (Website erreichbar + unbegrenzte Actions-Minuten).
- Domain-Kauf macht der USER selbst (Ausgabe mit eigenem Geld); der Agent richtet nur DNS/Pages ein.

# Deployment — Vercel (wind-pv-map.de) + GitHub Pages (parallel)

> Stand: 2026-09-20 (V52.2 **FINAL**) · **Haupt-URL: `https://wind-pv-map.de` (Vercel)** ·
> Alt-URL `https://wind-pv-map.ingenieur-tools.de` (GitHub Pages) bleibt **parallel live** bis zur
> Stilllegung (TODO, s. unten). Portal `ingenieur-tools.de` bleibt vollständig auf GitHub Pages.
>
> **Status 20.09. Abend — Umzug abgeschlossen, verifiziert:**
> - Beide URLs liefern identisches V52.2 (Vercel `dpl_5n8Z8…` / gh-pages `3b40bb9`)
> - deploy_ghpages.sh-Fix: impressum.html wird jetzt mitdeployt (fehlte vorher → 404 auf Alt-URL)
> - Verifikation komplett: HTTP-Codes, TLS, DNS (DoH), 5 JSON-Assets, Vercel-API, Watchdog, Cron
> - Details Session-Abschluss: docs/PROJEKTSTAND.md § „Aktueller Stand 2026-09-20 Abend"

## Architektur (seit 20.09.2026)

```
wind-pv-map.de (netcup)             → Vercel-Projekt „wind-pv-map" (Team pi-brain)  ← HAUPT-URL
└── www.wind-pv-map.de              → Redirect 308 → Apex (serverseitig in Vercel)
ingenieur-tools.de                  → Portal (GitHub Pages, Repo: PiBrainPi/ingenieur-tools-portal)
└── wind-pv-map.ingenieur-tools.de  → PV-/Wind-Karte (GitHub Pages, ALT — parallel live, TODO stilllegen)
```

- **Vercel Free (Hobby):** 0 €/Monat · Deploy via CLI (`scripts/deploy_vercel.sh`) · SSL automatisch
  (Let's Encrypt, Auto-Renew durch Vercel) · Zert gültig bis 19.12.2026.
- **GitHub Pages (Alt):** bleibt unverändert bestehen — Retention/Archiv + Rückfallebene.
- Gründe für Vercel: GitHub-Zert-Provisionierung auf `ingenieur-tools.de`-Subdomains lief in einen
  internen Zombie-State (`dns_changed` 20 Tage, kein Zert je issued — CT-Log-Verifiziert); Vercel
  provisioniert Zerts in Minuten nach DNS-Verify. Kein DNS-Zwangsumzug (netcup-NS blieben).

## Vercel-Setup (Ist-Stand, 20.09.2026)

| Element | Wert |
|---|---|
| Team | `pi-brain` (User: fabibuss-8478, Plan Hobby/Free) |
| Projekt | `wind-pv-map` (ID `prj_FBJzyKt2HI34a072uu2BhF3k8JRD`) |
| Production-Alias | `wind-pv-map.vercel.app` → zusätzlich `wind-pv-map.de` |
| Domains am Projekt | `wind-pv-map.de` (Apex, verified) + `www.wind-pv-map.de` (verified, Redirect 308 → Apex) |
| Deployment Protection | `prod_deployment_urls_and_all_previews` — Production-URLs (Custom Domain + Production-Links) öffentlich, nur Preview-Deployments geschützt |
| DNS (netcup, Zone `wind-pv-map.de`, CloudDNS) | `A @ → 76.76.21.21` + `A www → 76.76.21.21` (TTL 300) |
| Token | `~/.config/vercel_token` (chmod 600, Full-Account). **User-Entscheid:** bleibt für zukünftige Projekte aktiv. TODO: Rotation auf Project-Scope für Pipeline-Cron — s. Hosting-HANDOVER. |

## Deploy-Workflow (Regel 5 — gilt für BEIDE Ziele)

1. **Backup zuerst:** `cp data/mastr.db ~/backups/mastr-$(date +%F).db`
2. Pipeline/Build → `dist/` regenerieren (`build_all.sh` / `build.sh`)
3. `verify_update.sh` 100 % + UI-Checks (Regel 5) → Revision + klickbare HTML an Fabs
4. **User-Freigabe**
5. Deploy **beide Ziele:**
   - GitHub: `bash scripts/deploy_ghpages.sh` (Worktree, CNAME unangetastet)
   - Vercel: `bash scripts/deploy_vercel.sh` (dist/ → Production, aliasiert auf wind-pv-map.de)
6. Live-Verifikation beider URLs (meta.stand, einheiten.json, SHA-Abgleich)

> Bis zur Stilllegung der Alt-URL (TODO unten) gehen Deploys immer an beide Ziele.
> Nach Stilllegung: nur noch Vercel.

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
- ✅ V19 live (04.09., User-Freigabe): Betroffenheits-Tab final — Deploy per Worktree-Skript
  (CNAME unangetastet), Pages `built`, SHA-Abgleich live↔lokal identisch, 65.659 Einheiten
- ✅ **V20 live (04.09., User-Freigabe):** Laptop-Review-Paket (7 Punkte: Popup-Datum,
  Legende im Hinweise-Panel, Panel 820 px, Typ-Spalte 🆕/🗑️, senkrechte Chart-Labels,
  Trendlinie raus, Label-Trennung) — main `2c35f84`, gh-pages `0fe70b2`, Pages `built`,
  Live-SHA = lokal (`30c1fcd2…`), V20-Marker in Live-Datei, meta.json Stand 2026-09-01
  **Nächster Startpunkt: immer docs/PROJEKTSTAND.md (oben) lesen.**
  served-SHA (index_singlefile.html) = local-SHA (d678a6c6…), Daten-JSON live OK
  (65.659 Anlagen), Pages `status: built`, Deployment-SHA = gh-pages-HEAD e66c774.
  gh-pages-Update künftig mit `/tmp/deploy_ghpages_v19.sh`-Muster (Worktree, CNAME unangetastet,
  kein dist/-Pickup — siehe Skill publishing-projects-to-github).
- ✅ **Daten-Update + Deploy (06.09. Abend, außer der Planung, User-Wunsch):**
  `pipeline2_update.sh` (Backup `mastr.db.2026-09-06.preUpdateRun.bak` + Skript-Backup
  `mastr_20260906_185449.db`) → `build.sh` → `deploy_ghpages.sh`.
  gh-pages `edf116f → 5e94114`, Live-Verifikation: meta.json stand=2026-09-06T18:59:45,
  total=65.676. Funktionale Browser-Checks bestanden (LK-Tab, Geo-Suche, rwe-Suggest,
  Kritis-Cluster). **User plant häufigeres Intervall — Cron 79229dc1690d (1./15. 03:00)
  bleibt, ggf. Anpassung durch User.**
  1) **„Alle Anlagen anzeigen" repariert** (V23-Regression: `showAllUnits()` kannte die
  Geo-Filter nicht → `ReferenceError: lk is not defined`, Overlay öffnete nie; jetzt LK+
  Gemeinde einlesen + filtern; Test SH+Dithmarschen = 923 Anlagen).
  2) **Landkreis-Tab mobil:** Scroll-Container `#landkreis-scroll` (overflow-x, Touch),
  `table-layout:auto` + `min-width:860px` bei ≤767 px → Header nie abgekürzt
  (375-px-Test: Tabelle 1.024 px, alle Header FULL); PC bleibt Fixed-Layout.
  3) Such-Placeholder „…z.B. Solarpark Döllen GmbH".
- ✅ **V30–V34 (08./09.09.) lokal + Revisionen:** F-01..F-08 Fixrunde, V31 Netzbetreiber-Filter
  + Typ-Tab, V32 Bugfixrunde 5 WP + V32.1 Singlefile-TDZ-Hotfix, V33 UX-Runde (grün/rote Ringe,
  CARTO-File://-Fallback, V33.1 Popup-Hotfix), V34 UX-Runde 2 (LK-Scrollbalken oben,
  Popup-Re-Open-Fix, Panel 984 px). Bis 09.09. gesammelt nicht deployed (Revisionen in
  iterations/), dann gemeinsam mit V35 live.
- ✅ **V35+V35.1 live (10.09., User-Freigabe „pushe + stelle live"):**
  main `e158aaa` (V30…V35.1 gesammelt, 30 Dateien), gh-pages `4d1a17c` via
  `scripts/deploy_ghpages.sh`. Live-Verifikation: HTTP 200, last-modified 10.09. 12:21 UTC,
  „betreiber-charts-btn" im Live-HTML. Inhalt V35: Betreiber-Diagramme
  (Wachstum/Technologie/EEG, Exportfeld `eeg`), Filter-Reset = Ursprungszustand,
  Betroffenheits-Legende; V35.1: Donuts measure-steuerbar (Anlagen ⇄ MW).
  export_app-Fix: Historie-DB-Close („Historie übersprungen" behoben).
  Deploy: main `4cd13b1`, gh-pages `effd023`, DB-Backup `mastr.db.2026-09-06.preV25.bak`. Live-Verifikation: HTTP 200, Placeholder + landkreis-scroll im Live-HTML.
- ✅ **V24 live (06.09., User-Freigabe „pushe + stelle live"):** Politur — Landkreis-Tab-Header
  mit Leistungseinheiten („Leistung PV (MWp)" / „Leistung Wind (MW)") + Statistik-Panel ohne
  horizontales Scrollen (Landkreis-Tabelle `table-layout:fixed` + Spaltenverhältnisse,
  Spannungs-Zeilen flex-wrap; alle 9 Tabs browser-verifiziert `scrollWidth ≤ clientWidth`).
  **main `7172681` (V22+V23+V24 gemeinsam), gh-pages `1b9c85a`**, Deploy per
  `scripts/deploy_ghpages.sh` nach DB-Backup `~/backups/mastr.db.2026-09-06.preV24.bak`.
  Live-Verifikation: HTTP 200, beide Header-Strings im Live-HTML, `statistiken.json`
  (377 LKs · 6.499 Gemeinden · `groessen_cluster`) live abrufbar.
- ✅ **V22+V23 fertig gestellt → mit V24 live (06.09.):** V22 Größenklassen-Basis-Umschalter
  „Einzelanlagen / Parks aggregiert" (`groessen_cluster` im Export, Revision
  `iterations/V22_GroessenCluster.html`); V23 Geo-Ebene (Geo-Suche BL/LK/Gemeinde,
  Geo-Filter, Landkreis-Tab inkl. NAPs, Balken-Klick → Karte, park-aggregierter
  Leistungsfilter; Revision `iterations/V23_GeoEbene.html`). Beide waren zuvor
  browser-verifiziert und warteten auf Freigabe — mit V24-Deploy gemeinsam live gegangen.
- ✅ **V21 live (04.09. Abend, User-Freigabe):** 6 Revisionspakete — Betreiber-Tab
  (Live-Suggest + Gruppen/Portfolio-Filter, 'rwe'-False-Positive-Fix, Zahlformat 1 NK),
  Popup (TT.MM.JJJJ, NAP-Klick → alle Anlagen am NAP, 219-Anlagen-Test), Sortier-Fix
  Inbetriebnahme (numerisch statt String), Asset-Name-Klick in „Alle Anlagen anzeigen",
  Chart-Labels über den Datenpunkten. **main `d1096b4`, gh-pages `48da2ae`**, Deploy per
  `scripts/deploy_ghpages.sh` (datumsbasierte Message, CNAME unangetastet).
  Live-Verifikation: Index 433.686 B = lokal identisch, V21-Marker (tbl-name,
  „Gruppe oder Portfolio filtern…", V21.6) in Live-Datei + Live-JS.
  **CDN max-age=600:** erste ~10 min nach Deploy kann Cache Altstand zeigen —
  Cache-Buster-Query (`?v…=1`) umgeht das.
- ✅ V8j-Fixes live (`top: 86px` im HTML nachweisbar), Disclaimer-Trigger unter Zoom-Control
- ✅ Portal `index.html` → HTTP 200, enthält Link zur Karten-Subdomain
- ✅ Single-File rekonstruiert, SHA-identisch mit Backup (kein Datenverlust)
- ✅ `www.ingenieur-tools.de` + `galton-board.ingenieur-tools.de` DNS propagiert (Cloudflare DoH)
- ✅ Karte HTTPS fertig; Portal HTTPS-Zertifikat wartet auf LE-Rate-Limit-Fenster (~06./07.09.2026)

- ✅ **Datenstand 19.09. live (19.09., User-Freigabe, erste Anwendung Regel 5):**
  Pipeline-Cron 06:10–06:13 ok (Delta +30 W/+220 MW, +29 PV/+182 MW, 24 entfernt; NAP +12;
  Snapshot #17: 31.012 W / 22.467 PV / 53.479 gesamt; Karte 65.819). 100 %-Prüfkette nach
  Regel 5: verify_update.sh 6/6 ✅ + UI 17/17 je Build → Revision V51.1 → User-Freigabe →
  main `59058be` (Regel-5-Skripte verify_update.sh/verify_app.js + Doku) · gh-pages `271e026`.
  Live-Verifikation: meta.stand=19.09T06:12, index.html SHA live==lokal, Singlefile
  Content-Length 48.176.112 == lokal, historie.json live 5 Snapshots (letzter 19.09).
  DB-Backup `mastr_20260919_1315.db` vor Deploy. Pipeline-Cron prüft ab sofort selbst
  (Regel 5, 🚨-Alarm bei FAIL).

## Wichtige Hinweise

- **Keine Secrets im Repo** — `.env`, `data/`, `dist/` sind gitignored. Vercel-Token liegt **außerhalb**
  des Repos (`~/.config/vercel_token`, chmod 600) und wird nie committet.
- Repos sind **öffentlich** (Website erreichbar + unbegrenzte Actions-Minuten).
- Domain `wind-pv-map.de` (20.09.2026, netcup): DNS `A @` + `A www → 76.76.21.21` (Vercel).
- **TODO Alt-URL stilllegen** (nur nach User-Freigabe, nach erstem Pipeline-Lauf auf Vercel):
  1. Portal-Link `wind-pv-map.ingenieur-tools.de` → `wind-pv-map.de` ändern (Repo ingenieur-tools-portal)
  2. GitHub-Repo `pv-wind-map`: Custom Domain entfernen (API) — `gh-pages` bleibt als Archiv
  3. netcup Zone `ingenieur-tools.de`: CNAME `wind-pv-map` löschen
  4. Watchdog `https_watchdog_all.py`: Alt-Host entfernen (neue Hosts sind schon drin)
  5. Doku: HANDOVER.md, DNS-KONFIGURATION.md, dieses File (DEPLOYMENT.md) finalisieren
- **TODO Token-Rotation** (User-Entscheid 20.09.2026): Full-Account-Token bleibt zunächst aktiv
  (auch für zukünftige Vercel-Projekte). Später optional: separater Project-Scoped-Token für
  den Pipeline-Cron (Scope nur `wind-pv-map`), Full-Account-Token behält der User für Setup-Aufgaben.
- **DSGVO/Hosting-Texte (V52.1, 20.09.):** Datenschutzhinweise + Impressum wurden auf Vercel
  umgestellt und sind Teil des Deployments (`src/index.html` DS-Modal, `src/impressum.html`).
  Nach jeder Alt-URL-Stilllegung: GitHub-Hosting-Verweise in der Portal-DS entfernen.
  Details + Konformitäts-Fazit: `docs/DSGVO_VERCEL_50PUNKTE_PLAN.md`.

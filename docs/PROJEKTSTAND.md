# Projektstand (Handover) — PV & Wind Karte (MaStR)

> **Dieses Dokument dient als Einstieg für jede neue Agenten-/Arbeitssession.**
> Stand: 2026-08-31 · Repo: `/home/claw_01_rasbpi5_1/Projects/pv-wind-map`

## Was das Projekt ist
Interaktive, offline-fähige HTML-Karte aller **Wind- (≥100 kW) und PV-Anlagen (≥0,5 MWp)**
in Betrieb**, aus dem Marktstammdatenregister (MaStR, BNetzA). Klickbare Single-File + hostbare Version.

## Aktueller Stand (2026-08-31)
- **Datenbasis:** Wind 32.144 (31.114 georeferenziert) · PV 22.371 (22.368 georeferenziert)
  → **53.482 Anlagen auf der Karte**. Betreiber: 23.216.
- **Schwellen (final):** Wind ≥100 kW, PV ≥0,5 MWp (beide 2026-08-29 durch Nutzer-Wunsch gesenkt).
- **HEAD:** nach Doku-Update dieses Stands (vorher `b7951fd` „Impressum/Datenschutz…“) — siehe
  `git log`; `main` ist Quell-, `gh-pages` Deploy-Branch.
- **Remote:** `PiBrainPi/pv-wind-map` auf GitHub (**öffentlich**, `main`) + `gh-pages`-Branch (Deploy).
- **Klickbare Datei:** `dist/index_singlefile.html` (24,9 MB) + Kopie im Austauschordner
  `/home/claw_01_rasbpi5_1/hermes_human-share/PV-Wind-Karte_MaStR_mit_ArtFilter.html`.
- **Live im Internet:** `https://wind-pv-map.ingenieur-tools.de/` (Karte, HTTPS aktiv) ·
  `https://ingenieur-tools.de/` (Portal) — Details in `docs/DEPLOYMENT.md`.

## Features
- **Karte:** Leaflet + MarkerCluster, Filter nach Typ (Wind/PV), Bundesland, **Art des Assets**
  (Freiflächen-/Gebäude-/Sonstige Solaranlage, Windkraft an Land/auf See) und **Leistung (MW)** in
  festen Größenklassen `[von, bis)` (0.1–0.5 … 150–200, 200+), Detail-Popups.
- **Anlagen-Anzahl-Badge (Filter):** Sobald ein **Art-, Bundesland- oder Leistungs-**Filter gesetzt ist,
  zeigt ein blauer Badge `Anzahl: <n>`. Logik (Var. A): die Zahl zählt immer die **tatsächlich sichtbaren**
  Anlagen (alle gesetzten Filter inkl. Wind/PV), konsistent mit den Marker-Clustern. Ohne Filter versteckt.
  Format: Tausendertrennung (`de-DE`).
- **Größenklassen-Skala (feste Staffel, Nutzer-Vorgabe + Kritis-Recherche):**
  `0.1–0.5 · 0.5–1 · 1–2 · 2–5 · 5–10 · 10–30 · 30–60 · 60–100 · 100–104 · 104–150 · 150+`
  (immer `>= von && < bis`, in MW/MWp). **Kritis-Schwelle:** Erzeugungsanlagen sind erst **ab 104 MW**
  installierter Nettonennleistung kritisrelevant (BSI-KritisV Anhang 1, Kat. 1.1.1). Daher ist NUR die
  Klasse ab `104` Kritis (`104–150`, `150+`); die Klasse `100–104` ist **kein** Kritis.
- **Suche mit Autocomplete:** Anlagen-, Park-, Gemeinde- **und Betreibername** (akzent-/case-unabhängig).
- **⛁ Betreiber-Suche:** Suchtext im Betreibernamen → ein Klick filtert **alle** Anlagen aller
  gematchten Betreiber (deutschlandweit, Fit-Bounds). Beispiel: „CEE" → 60 Betreiber/184 Anlagen.
- **Popup-Deeplinks:** Anlagen-Popup enthält „Koordinaten" (Dezimalgrad) → öffnet **Google Maps**
  an der Anlage (Deeplink `maps?api=1&query=lat,lon`); „Betreiber" → öffnet **NorthData**-Firmenprofil
  (Deeplink `northdata.de/<Firmenname-Slug>`; MaStR-typischer Vollbreite-Ampersand ＆ wird auf `&` normalisiert).
- **Statistik-Panel:** Betreiber-Tabelle (Filter/Top-N/Sortierung, Klick → Karte; **ohne** Technik-Badge/Emoji),
  Hersteller-Tabelle (nur Wind, +%Anteil-Spalte, **identische CSS-Formatierung wie Betreiber** — Schrift/Farbe/
  Kopfzeilen/Hover/Sortierpfeile, **ohne** Badge), **Größenklassen-Diagramme** mit Toggle **Wind / PV / Wind + PV**
  (gemeinsames Diagramm beider Technologien), Hersteller-Verteilungs-Donut-Chart (interaktiv, Canvas).

## Build (Ein-Befehl)
```bash
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map
bash scripts/build.sh          # fetch → import → export → bundle (erzeugt dist/ + Single-File)
```
> Wichtig: `bash scripts/build.sh` (NICHT `python3` — build.sh ist ein Bash-Skript).

## Pipeline & Dateien
| Schritt | Datei | Zweck |
|---------|-------|-------|
| Fetch | `scripts/fetch_mastr.py` | MaStR-API (Wind ≥100 kW, PV ≥0,5 MWp) → `data/raw/*.json` |
| Import | `scripts/import_mastr.py` | Normalisierung (kW↔MW) + SQLite `data/mastr.db` |
| Export | `scripts/export_app.py` | `dist/assets/*.json` (nur georeferenziert) + Statistik (inkl. `groessenklassen.gesamt`) |
| Klassen-Rebuild | `scripts/rebuild_groessen.py` | DB-freies Rebuild der Größenklassen in `statistiken.json` (falls `mastr.db` fehlt, identische Logik) |
| Bundle | `scripts/bundle_singlefile.py` | `dist/index_singlefile.html` (eingebettete Daten) |
| App | `src/index.html` | Leaflet-Karte + Suche + Statistik-Panel + Impressum-Modal |

## Wichtige technische Details
- **Einheiten-Normalisierung:** Wind gemischt (kW/MW); Heuristik `>80 → kW`, sonst MW. PV immer kWp `/1000`.
- **Geolokation:** Nur Anlagen mit vorhandenen Koordinaten werden gezeichnet (kein Geocoding).
- **Statistik (gesamt):** `gesamt.wind_anzahl`/`pv_anzahl` = Direktzählung aus SQLite (Bugfix).
  `herstellbar_wind` = Summe der Hersteller.
- **Größenklassen (Staffel):** Feste 11-Klassen-Skala `0.1–0.5 … 100–104 · 104–150 · 150+`, einheitlich
  für Wind, PV und das gemeinsame Diagramm („Wind + PV"); definiert in `export_app.py` (`_staffel()`).
  **Alle Klassen werden immer gelistet** (auch leere), damit Kritis-Schwellen-Klassen sichtbar sind.
  Das Feld `kritis: true/false` markiert Kritis-relevante Klassen. **Kritis gilt erst ab 104 MW**
  (BSI-KritisV Kat. 1.1.1): nur `104–150` und `150+` tragen `kritis:true`; `100–104` ist **kein** Kritis.
  Die Karten-Statistik (`dist/assets/statistiken.json`) enthält den Schlüssel `groessenklassen.gesamt`
  für das gemeinsame Diagramm (zusätzlich zu `wind`/`pv`).
- **Kritis-Klassen:** Im Diagramm 🔴 rot markiert (`bar-fill.kritis`), mit `KRITIS`-Badge im Label +
  Tooltip-Hinweis. Leere Kritis-Klassen bei Wind (104+ real leer) bleiben sichtbar.
- **Gesamt-Diagramm („Wind + PV"):** zeigt pro Klasse **zwei Balken** (Wind blau, PV orange) nebeneinander
  mit getrennten Werten im Tooltip (Wind/PV Anlagen + Leistung), damit beide Technologien sichtbar sind.
- **Größen-Filter in der Toolbar:** HTML `<select id="filter-gr">` mit den 11 Größen-Klassen als
  `value="von,bis"` (z. B. `"0.5,1"`, `"104,150"`, `"150,1e9"`). `applyFilters()` parst
  `Number.parseFloat`, filtert `u.mw >= von && u.mw < bis`. Der Badge (`#art-count`) wird aktiviert
  bei `art || bl || gr`.
- **Rechtliches:** Quellenvermerk DL-De-BY-2.0 + Impressum (§5 DDG) fest in der App (Modal).
- **`data/`-Ist-Stand:** `data/raw/ + data/mastr.db` sind gitignored und aktuell **nicht vorhanden**;
  `fetch_mastr.py` legt sie beim nächsten vollständigen Update automatisch neu an.
- **rebuild_groessen.py:** Temporäres Hilfsskript (DB-frei) zur Neuberechnung der Größenklassen in
  `dist/assets/statistiken.json` aus `einheiten.json`, für den Fall, dass die SQLite-DB fehlt.
  Dieselbe Logik wie `export_app.py::build_statistiken()`.

## Offene Punkte / nächste Schritte (Vorschlag)
- [x] **DSGVO-Update (2026-08-31, Revision v2, deployed):** unpkg-CDN entfernt
      (Leaflet/MarkerCluster inline aus `src/vendor/`), OSM-Kacheln nur nach 2-Klick-Consent
      (localStorage `pvw_tiles_consent`), Datenschutz-Modal komplett überarbeitet (Drittland USA/UK,
      DPF, OSMF/UK-AD, TDDDG §25, HmbBfDI, Widerspruch, Deeplinks, Stand 31.08.2026), Meta
      `referrer`/`robots`. Details + Revisionen: `~/Projects/Domain_Hosting/ingenieur-tools.de/DSGVO/`.
- [x] **Fix Erstladen-ohne-Daten (2026-08-31, V3, as-built):** Beim ersten Besuch (ohne gesetzten Consent)
      lud die hostbare Karte keine Daten ("Lade Daten…" blieb stehen, keine Marker). **Root-Cause:**
      `L.map('map', { zoomControl:true })` ohne `maxZoom` → Leaflet warf die Promise-Rejection
      *"Map has no maxZoom specified"*, die den `await`-Datenblock (`fetch`) in der async `init()` abbrechen
      ließ, bevor er startete. **Fix:** `maxZoom:18` explizit auf der Map gesetzt + Datenladen robust
      (sequenzielle `fetchJson`-Helfer statt `Promise.all`, je Asset einzeln, `statistiken.json` optional,
      Zähler-Fallback aus den Daten). Verifiziert: Erstladen → 53.482 Einheiten, 53 Marker, 44 Cluster,
      0 JS-Fehler; Consent-Klick lädt 18 Kacheln. Revision `index_v3` / `index_singlefile_v3`.
- [x] **Alle Revisionen committet** (Betreiber-Suche, Hersteller-Formatierung, Badge-Removal, Deeplinks,
      Art-Filter, Anlagen-Anzahl-Badge, Größen-Filter + Leistungsklassen, Kritis-Markierung, Gesamt-Diagramm,
      Pipeline + Doku). Working tree sauber (Stand nach Commit dieses Dokuments).
- [x] `docs/statistik.md`, `docs/datenmodell.md`, `docs/update.md`, `docs/architektur.md` auf neue
      PV/Wind-Zahlen, Badge und Staffeln konsistent.
- [ ] **Performance:** Single-File ist auf ~25 MB gewachsen — optional hostbare Version nutzen,
      Daten-CDN, oder GeoJSON-Minify. Bei `file://`-Laden beachten (einmal war eine leere Seite transient).
- [ ] **Domain/HTTPS-Rest:** Portal-Zertifikat (`ingenieur-tools.de`) in Ausstellung; Sun-Tracker
      (`sonne.`) HTTPS hängt bei `authorization_created` (GitHub-Support-Ticket offen, Watchdog
      `d9880f4fff1e`). Karte + Galton laufen bereits über HTTPS.
- [x] **GitHub-Publishing** umgesetzt: Karten-Repo öffentlich auf GitHub + GitHub Pages live.

## Verifikation: Filter + Anlagen-Anzahl-Badge (per Browser-Konsole, reproduzierbar)
Sobald die App geladen ist (`allUnits` befüllt), im Devtools-Konsolen-`window`-Kontext:
```js
const set=(type,bl,art,gr)=>{document.getElementById('filter-type').value=type;
 document.getElementById('filter-bl').value=bl;document.getElementById('filter-art').value=art;
 document.getElementById('filter-gr').value=gr||'';
 applyFilters();const e=document.getElementById('art-count');
 return {text:e.textContent,hidden:e.hidden};};
set('','','Freiflächensolaranlage','');      // → {text:"Anzahl: 11.707", hidden:false}
set('','Bayern','','');                      // → {text:"Anzahl: 7.042", hidden:false}
set('','Bayern','Freiflächensolaranlage','');// → {text:"Anzahl: 4.396", hidden:false}
set('pv','','','104,150');                   // → {text:"Anzahl: 2", hidden:false}   (PV 104–150 MW)
set('wind','','','0.5,1');                   // → {text:"Anzahl: 4.079", hidden:false}
set('','','','');                            // → hidden:true
```
Referenzwerte (53.482-Datensatz): Freifläche 11.707, Bayern 7.042, Bayern+Freifläche 4.396,
PV 104–150 MW = 2, Wind 0.5–1 MW = 4.079, PV 100–104 MW = 1, PV 150+ MW = 3. Die Zahl muss
stets `allUnits.filter(...)` für die gerade aktiven (Art, BL, Gr, Typ-)Filter entsprechen.
Die Größenklassen in `_stats.groessenklassen` haben `wind`/`pv`/`gesamt` mit je **11 Einträgen**;
Kritis-Klassen (`kritis:true`) sind nur `104–150` und `150+` (Summen: Wind 31.114 · PV 22.368 ·
Gesamt 53.482).

## Besondere Hinweise für neue Sessions
- **Kein JSON/HTML-Rohcode in Telegram-Chat**; klickbare Datei per `MEDIA:` oder send_telegram_file senden.
- **Ergebnis-Kommunikation:** deutsch, kurze Alarm-Nachrichten bei Fehlern, hart prüfen (kein Halluzinieren),
  Änderungsliste mit Quellen.
- **GitHub-Publishing** (umsgesetzt): Repo `pv-wind-map` (und `ingenieur-tools-portal`) sind öffentlich auf
  GitHub, `main` ist das Quell-Repo, `gh-pages`-Branch deployt die Site. Keine Secrets im Repo.
- **Andere LLMs prüfen Ergebnisse gegengegen** — gemeldete Bugs ernst nehmen, verifizieren, fixen.
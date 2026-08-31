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
- **Karte:** Leaflet + MarkerCluster, Filter nach Typ (Wind/PV), Bundesland und **Art des Assets**
  (Freiflächen-/Gebäude-/Sonstige Solaranlage, Windkraft an Land/auf See), Detail-Popups.
- **Anlagen-Anzahl-Badge (Filter):** Sobald der **Art- oder Bundesland-**Filter gesetzt ist, zeigt ein
  blauer Badge direkt neben dem Art-Dropdown `Anzahl: <n>`. Logik (Var. A): die Zahl zählt immer die
  **tatsächlich sichtbaren** Anlagen (Art + Bundesland **+ evtl. Wind/PV-Filter**), ist also stets
  konsistent mit den Marker-Clustern. Ohne Art-/BL-Filter ist der Badge versteckt. Format:
  Tausendertrennung (`de-DE`).
- **Suche mit Autocomplete:** Anlagen-, Park-, Gemeinde- **und Betreibername** (akzent-/case-unabhängig).
- **⛁ Betreiber-Suche:** Suchtext im Betreibernamen → ein Klick filtert **alle** Anlagen aller
  gematchten Betreiber (deutschlandweit, Fit-Bounds). Beispiel: „CEE" → 60 Betreiber/184 Anlagen.
- **Popup-Deeplinks:** Anlagen-Popup enthält „Koordinaten" (Dezimalgrad) → öffnet **Google Maps**
  an der Anlage (Deeplink `maps?api=1&query=lat,lon`); „Betreiber" → öffnet **NorthData**-Firmenprofil
  (Deeplink `northdata.de/<Firmenname-Slug>`; MaStR-typischer Vollbreite-Ampersand ＆ wird auf `&` normalisiert).
- **Statistik-Panel:** Betreiber-Tabelle (Filter/Top-N/Sortierung, Klick → Karte; **ohne** Technik-Badge/Emoji),
  Hersteller-Tabelle (nur Wind, +%Anteil-Spalte, **identische CSS-Formatierung wie Betreiber** — Schrift/Farbe/
  Kopfzeilen/Hover/Sortierpfeile, **ohne** Badge), Größenklassen-Diagramm (Wind/PV),
  Hersteller-Verteilungs-Donut-Chart (interaktiv, Canvas).

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
| Export | `scripts/export_app.py` | `dist/assets/*.json` (nur georeferenziert) + Statistik |
| Bundle | `scripts/bundle_singlefile.py` | `dist/index_singlefile.html` (eingebettete Daten) |
| App | `src/index.html` | Leaflet-Karte + Suche + Statistik-Panel + Impressum-Modal |

## Wichtige technische Details
- **Einheiten-Normalisierung:** Wind gemischt (kW/MW); Heuristik `>80 → kW`, sonst MW. PV immer kWp `/1000`.
- **Geolokation:** Nur Anlagen mit vorhandenen Koordinaten werden gezeichnet (kein Geocoding).
- **Statistik (gesamt):** `gesamt.wind_anzahl`/`pv_anzahl` = Direktzählung aus SQLite (Bugfix).
  `herstellbar_wind` = Summe der Hersteller. **Achtung:** nach Nutzer-Änderung evtl. Grenzwerte prüfen.
- **Größenklassen:** Wind ab `0.1–1` MW, PV ab `0.5–1` MW (feste Staffeln in `export_app.py`).
- **Rechtliches:** Quellenvermerk DL-De-BY-2.0 + Impressum (§5 DDG) fest in der App (Modal).
- **Anlagen-Anzahl-Badge (Implementierung):** HTML-Element `#art-count` (mit Klasse `filter-count`)
  direkt nach dem `#filter-art`-Select in der Toolbar; CSS in `#toolbar .filter-count`; Logik in
  `applyFilters()` (zeigt Badge, sobald `art || bl` aktiv, zählt `filtered.length`). Verifikation:
  siehe § Verifikation in diesem Dokument bzw. Browser-Test über `applyFilters()`.
- **`data/`-Ist-Stand:** `data/raw/ + data/mastr.db` sind gitignored und aktuell **nicht vorhanden**;
  `fetch_mastr.py` legt sie beim nächsten vollständigen Update automatisch neu an.

## Offene Punkte / nächste Schritte (Vorschlag)
- [x] **Alle Revisionen committet** (Betreiber-Suche, Hersteller-Formatierung, Badge-Removal, Deeplinks,
      Art-Filter, Anlagen-Anzahl-Badge, Doku). Working tree sauber (Stand nach Commit dieses Dokuments).
- [x] `docs/statistik.md`, `docs/datenmodell.md`, `docs/update.md`, `docs/architektur.md` auf neue
      PV/Wind-Zahlen + Badge-Feature konsistent (Import 2026-08-29 / Badge 2026-08-31).
- [ ] **Performance:** Single-File ist auf ~25 MB gewachsen — optional hostbare Version nutzen,
      Daten-CDN, oder GeoJSON-Minify. Bei `file://`-Laden beachten (einmal war eine leere Seite transient).
- [ ] **Domain/HTTPS-Rest:** Portal-Zertifikat (`ingenieur-tools.de`) in Ausstellung; Sun-Tracker
      (`sonne.`) HTTPS hängt bei `authorization_created` (GitHub-Support-Ticket offen, Watchdog
      `d9880f4fff1e`). Karte + Galton laufen bereits über HTTPS.
- [x] **GitHub-Publishing** umgesetzt: Karten-Repo öffentlich auf GitHub + GitHub Pages live.

## Verifikation: Anlagen-Anzahl-Badge (per Browser-Konsole, reproduzierbar)
Sobald die App geladen ist (`allUnits` befüllt), im Devtools-Konsolen-`window`-Kontext:
```js
const set=(type,bl,art)=>{document.getElementById('filter-type').value=type;
 document.getElementById('filter-bl').value=bl;document.getElementById('filter-art').value=art;
 applyFilters();const e=document.getElementById('art-count');
 return {text:e.textContent,hidden:e.hidden};};
set('','','Freiflächensolaranlage');   // → {text:"Anzahl: 11.707", hidden:false}
set('','Bayern','');                   // → {text:"Anzahl: 7.042", hidden:false}
set('','Bayern','Freiflächensolaranlage'); // → {text:"Anzahl: 4.396", hidden:false}
set('','','');                         // → hidden:true
```
Referenzwerte (53.482-konsistenter Datensatz): Freifläche 11.707, Bayern 7.042, Bayern+Freifläche 4.396.
Die Zahl muss stets `allUnits.filter(...)` für die gerade aktiven (Art, BL, Typ-)Filter entsprechen.

## Besondere Hinweise für neue Sessions
- **Kein JSON/HTML-Rohcode in Telegram-Chat**; klickbare Datei per `MEDIA:` oder send_telegram_file senden.
- **Ergebnis-Kommunikation:** deutsch, kurze Alarm-Nachrichten bei Fehlern, hart prüfen (kein Halluzinieren),
  Änderungsliste mit Quellen.
- **GitHub-Publishing** (umsgesetzt): Repo `pv-wind-map` (und `ingenieur-tools-portal`) sind öffentlich auf
  GitHub, `main` ist das Quell-Repo, `gh-pages`-Branch deployt die Site. Keine Secrets im Repo.
- **Andere LLMs prüfen Ergebnisse gegengegen** — gemeldete Bugs ernst nehmen, verifizieren, fixen.
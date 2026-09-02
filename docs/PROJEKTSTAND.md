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
- [ ] **Domain/HTTPS-Rest:** Portal + Sun-HTTPS warten auf Let's Encrypt (Rate-Limit, 7-Tage-Fenster).
      Watchdog `b950b901245e` (alle 30 Min, alle Hosts) meldet automatisch bei Erfolg. Karte + Galton
      haben `https_enforced=true` (01.09.).
- [x] **GitHub-Publishing** umgesetzt: Karten-Repo öffentlich auf GitHub + GitHub Pages live.
- [x] **V4 — Bundesländer-Tab mit Pie-Charts (2026-09-01, lokal, nicht gepusht):** Neuer Statistik-
      Reiter „Bundesländer" mit interaktivem Donut-Chart (Canvas, keine Bibliothek). Drei Modi via
      Toggle: **Wind** (17 Bundesländer, 31.114 Anlagen, Top: Niedersachsen 6.301), **PV** (16 BL,
      22.363 Anlagen, Top: Bayern 5.850), **Wind + PV** (17 BL, 53.477 Anlagen, Top: Niedersachsen 7.956).
      Measure-Toggle: Anlagen ⇄ Leistung (MW). Klick auf Pie-Segment oder Legende → Karte filtert
      auf Bundesland (Fit-Bounds + Suchfeld-Label). Summary-Box: Tech, Bundesländer-Anzahl, Anlagen,
      Gesamtleistung, Top-Bundesland. 16-Farben-Palette (`BL_COLORS`). Verifiziert: 0 JS-Fehler,
      53.482 Anlagen geladen, Canvas gefunden, alle drei Modi + Measure-Toggle getestet.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V4_Bundeslaender-PieChart.html`.
      **Push-Freigabe vom User ausstehend.**
- [x] **V4 — Update-Historie-Tab (2026-09-01, lokal, nicht gepusht):** Neuer Statistik-Reiter
      „Update-Historie" mit Revisions-Tracker. Vergleicht Datenstände zwischen Updates und zeigt
      Veränderungen über die Zeit. **Erster echter Delta-Test:** 29.08.→01.09. = +19 Anlagen
      (Wind +3/+15 MW, PV +16/+96 MW), 1 entfernt, 7 Bundesländer verändert (Top: Schleswig-Holstein +5 PV).
      **Features:** (1) Delta-Summary-Karten (Wind/PV/Gesamt neu, MW neu, Gesamt-Δ), (2) Verlauf-Tabelle
      mit allen Snapshots (Datum, Wind/PV/Gesamt Anzahlen+MW, Δ Neu/Δ MW), (3) Bundesländer-Veränderung
      je Update (Wind/PV/MW pro Bundesland), (4) Mini-Zeitleiste (Balken der Gesamtanzahl pro Snapshot).
      **Pipeline:** `snapshot.py` (neu) — SQLite-Schema (`snapshots`+`snapshot_einheiten`), `save_snapshot()`,
      `compute_delta()`, `build_historie()`. `import_mastr.py` — sichert alten Stand vor Rebuild, neuen
      Stand nach Import, berechnet Delta. `export_app.py` — generiert `historie.json`. `bundle_singlefile.py`
      — bettet `window.__PVWIND_HISTORIE__` ein. **Cronjob-Plan:** 1. & 15. des Monats (`0 3 1,15 * *`).
      Verifiziert: 53.500 Anlagen, 2 Snapshots, 0 JS-Fehler, alle UI-Elemente getestet.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V4b — Asset-Detail-Ansicht (2026-09-01):** Klickbare Verlauf-Zeilen
      in der Update-Historie öffnen ein Detail-Overlay mit 4 Tabs: **Neu: Wind**, **Neu: PV**,
      **Entfernt: Wind**, **Entfernt: PV**. Jeder Tab zeigt eine Tabelle aller hinzugefügten/entfernten
      Assets mit vollen Daten: Name, MW, Bundesland, Gemeinde, Inbetriebnahme, **Betreiber (NorthData-Deeplink)**,
      MaStR-Nr., **Koordinaten (Google-Maps-Deeplink)**. Auto-Tab-Wechsel zum ersten Tab mit Inhalt.
      Escape schließt das Overlay. `snapshot.py` erweitert: `snapshot_einheiten` speichert jetzt alle
      Asset-Felder (26 Spalten), `compute_delta()` liefert `added_assets`/`removed_assets` als volle
      Asset-Dicts. Historie-JSON wuchs von 5,3 KB auf 18,8 KB (19 Assets × volle Daten).
      Verifiziert: 19 added (3 Wind + 16 PV), 1 removed (Wind), 32 Deeplinks in PV-Tabelle,
      0 JS-Fehler, Overlay öffnet/schließt korrekt.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V4c — Formatierung (2026-09-01):** (1) Bundesländer-Veränderung als
      professionelle Tabelle mit 6 Spalten (Bundesland | Wind Δ | PV Δ | Wind MW Δ | PV MW Δ | Gesamt MW Δ),
      farbcodiert (grün=+, rot=−, grau=—), Spaltenüberschriften in Caps, sortiert nach absoluter
      Veränderung. (2) Hinweis-Text unter „Daten-Verlauf": „💡 Klicke auf eine Zeile mit Δ-Wert, um die
      detaillierte Auflistung aller hinzugefügten und entfernten Wind- und PV-Anlagen zu sehen".
      Verifiziert: 7 Bundesländer-Zeilen, 6 Spalten, Klick-Overlay funktioniert, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V5 — Responsive Design (2026-09-01, LIVE):** 3 Breakpoints via `@media`-Queries.
      **PC (≥1024px):** Stats-Panel 700px breit (vorher 440px) — kein horizontaler Scroll mehr
      bei Statistik-Tabellen. **Tablet (768–1023px):** Stats-Panel 560px. **Mobile (<768px):**
      Stats-Panel 100vw Vollbild, Topbar vollbreit, Toolbar horizontal scrollbar, Modals/Overlay
      vollbreit. Betreiber-/Hersteller-Tabellen: `max-width` für Namensspalte 200→280px.
      Verifiziert: Panel 700px, Tabellen 649px kein horizontaler Scroll, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V5c — Three Fixes (2026-09-01, LIVE):** (1) Datenverlauf-Tabelle: `font-size:12px`,
      `min-width:560px`, `white-space:nowrap` — lesbar wie Bundesländer-Tabelle, horizontaler
      Scroll nur wenn Panel <560px. (2) Bundesländer-Pie: Canvas 220→280px, auf Mobile
      `flex-direction:column` (Chart über Legende, max 320px) — Legende voll sichtbar auf
      Smartphone. (3) Topbar: Meta-Legende + Statistik-Button **nebeneinander** (vorher
      untereinander) — Höhe 31px statt ~50px. "Anlagen" entfernt aus Pie-Legende.
      Verifiziert: Canvas 280px, kein horizontaler Scroll, Topbar 31px, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V6 — Art-Verteilungs-Pie + Sortierungs-Fixes (2026-09-01, LIVE):** Donut-Pie-Charts unter
      den Größenklassen-Balkendiagrammen zeigen die Verteilung nach Anlagentyp (unabhängig der
      Leistungsklasse). **Wind:** Windkraft an Land (29.343/94,3%) vs. Windkraft auf See (1.773/5,7%)
      — umschaltbar Anzahlen/Leistung (79.196 MW vs. 10.969 MW). **PV:** Freiflächensolaranlage
      (11.721/52,4%), Gebäudesolaranlage (10.629/47,5%), Sonstige Solaranlage (34/0,2%) — umschaltbar
      Anzahlen/Leistung (45.092/9.598/40 MW). Canvas 240px Donut mit Loch, Prozent-Labels in Segmenten,
      Legende rechts, Responsive (Mobile untereinander). Weitere Fixes: (5) Hinweistext Update-Historie
      gekürzt ("NorthData/Google-Maps-Links" entfernt), (6) Hersteller-Sortierung auf Anzahl/desc
      geändert (vorher Summe MW), (7) Betreiber bleibt Summe MW/desc.
      Verifiziert: Alle 4 Pie-Kombinationen, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V7 — Jahres-Filter nach Registrierungsdatum (2026-09-02, lokal, nicht gepusht):** Neuer Filter
      "Registrierung" (Dropdown) in der Toolbar unten links. Filtert nach `registrierungsdatum`
      (MaStR-Feld, Format YYYY-MM-DD, 0 NULL-Werte, Bereich 2019–2026). Neues JSON-Feld `"reg"` pro
      Anlage (`export_app.py` erweitert — `registrierungsdatum` zum SELECT + build_units hinzugefügt).
      Dropdown mit 8 Optionen (2019–2026), kombinierbar mit allen anderen Filtern.
      Verifiziert: 2019 → 16.771, 2026 → 2.454, 2019+Wind → 11.578, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7_JahresFilter.html`.
- [x] **V7b — Monats-Filter + Alle-Anlagen-Tabelle (2026-09-02, lokal, nicht gepusht):** (1) Neuer Filter
      "Registrierungsmonat" (Dropdown 1–12, Jan–Dez), kombinierbar mit Jahres-Filter und allen anderen.
      Filtert nach `registrierungsdatum.substring(5,7)` (Monatsteil). (2) "📋 Alle Anlagen anzeigen" Button
      in der Toolbar — erscheint automatisch bei aktivem Filter. Klick öffnet ein Vollbild-Overlay mit
      professioneller Tabelle aller gefilterten Anlagen (12 Spalten: #, Name, Typ, Art, MW, Bundesland,
      Landkreis, Gemeinde, Registriert, Inbetriebnahme, Betreiber, MaStR-Nr.). Chunk-Rendering (500
      Zeilen/Frame via `requestAnimationFrame`) verhindert Blockierung bei großen Mengen — getestet mit
      998 Anlagen. MW farbcodiert (Wind blau, PV orange). Sticky Header, Hover-Highlight, Escape/✕/Klick
      schließen. Responsive (Mobile: Vollbild).
      Verifiziert: 2020+März → 1.236, nur Januar → 5.816, 998 Zeilen gerendert, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7b_MonatFilter_AlleAnlagen.html`.
- [x] **V7c — Sortierbare Tabellen-Header (2026-09-02, lokal, nicht gepusht):** Klick auf jeden Spalten-Header
      in der Alle-Anlagen-Tabelle sortiert die Tabelle. Erster Klick = aufsteigend (▲), zweiter = absteigend (▼),
      Klick auf andere Spalte wechselt Sortierspalte. Sortierbar: alle 12 Spalten. Zahlen (MW) numerisch,
      Text alphabetisch (`localeCompare('de-DE')`), Datum als String (YYYY-MM-DD = chronologisch korrekt).
      Nach Sortierung: Chunk-Rendering für flüssiges Neu-Aufbauen. Header-Hover-Effekt (blau).
      Verifiziert: MW asc 0,3→6,8, MW desc 15→5,56, Name asc alphabetisch, Reg asc 2026-01-02→2026-06-23,
      ▲/▼ korrekt, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7c_SortierbareTabelle.html`.

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
Referenzwerte (53.500-Datensatz): Freifläche ~11.707, Bayern ~7.042, Bayern+Freifläche ~4.396,
PV 104–150 MW = 2, Wind 0.5–1 MW ~4.079, PV 100–104 MW = 1, PV 150+ MW = 3. Die Zahl muss
stets `allUnits.filter(...)` für die gerade aktiven (Art, BL, Gr, Typ-)Filter entsprechen.
Die Größenklassen in `_stats.groessenklassen` haben `wind`/`pv`/`gesamt` mit je **11 Einträgen**;
Kritis-Klassen (`kritis:true`) sind nur `104–150` und `150+` (Summen: Wind 31.116 · PV 22.384 ·
Gesamt 53.500).

## Besondere Hinweise für neue Sessions
- **Kein JSON/HTML-Rohcode in Telegram-Chat**; klickbare Datei per `MEDIA:` oder send_telegram_file senden.
- **Ergebnis-Kommunikation:** deutsch, kurze Alarm-Nachrichten bei Fehlern, hart prüfen (kein Halluzinieren),
  Änderungsliste mit Quellen.
- **GitHub-Publishing** (umsgesetzt): Repo `pv-wind-map` (und `ingenieur-tools-portal`) sind öffentlich auf
  GitHub, `main` ist das Quell-Repo, `gh-pages`-Branch deployt die Site. Keine Secrets im Repo.
- **Andere LLMs prüfen Ergebnisse gegengegen** — gemeldete Bugs ernst nehmen, verifizieren, fixen.

## ⚠️ Wichtige Regeln (unveränderlich)

### 1. Snapshots — niemals löschen, überschreiben oder verändern
Die in `data/mastr.db` gespeicherten Snapshots (Tabellen `snapshots` + `snapshot_einheiten`)
sind die **historische Datenbasis** des Projekts. Sie dienen dem Revisions-Tracker
(Update-Historie-Tab in der HTML-App) und bauen über Monate/Jahre eine vollständige
Veränderungshistorie auf.

- **Snapshots dürfen niemals gelöscht werden** — auch nicht alte oder scheinbar irrelevante.
- **Snapshots dürfen niemals überschrieben oder verändert werden** — jeder Snapshot ist
  ein unveränderlicher Punkt-in-Zeit-Datensatz.
- **Neue Snapshots werden nur angefügt** (`INSERT`, niemals `UPDATE`/`DELETE` auf bestehende).
- **`data/mastr.db` wird nicht auf GitHub gepusht** (gitignored, 64 MB) — die DB bleibt lokal.
- Bei Verlust der DB (z. B. SD-Karte defekt) ist die Historie unwiederherstellbar.
  `historie.json` (auf gh-pages, ~19 KB) enthält die aggregierten Deltas, aber nicht die
  vollen Asset-Daten — diese leben nur in der SQLite-DB.

### 2. Iterationen — alle speichern, niemals löschen
Jeder klickbare HTML-Iterationsschritt, der während der Entwicklung erstellt wird, muss im
Ordner `iterations/` gespeichert werden (`V<Version>_<Kurzbeschreibung>.html`).

- **Jede Iteration muss gespeichert werden** — auch fehlerhafte oder verworfene.
- **Dateien dürfen niemals gelöscht oder überschrieben werden.**
- Der Ordner ist gitignored (Dateien ~25 MB), bleibt also lokal.
- Übersicht: `iterations/README.md` (wird committet, enthält Versions-Tabelle).
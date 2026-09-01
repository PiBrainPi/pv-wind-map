# Architektur — PV & Wind Karte (MaStR)

> Stand: 2026-08-29 · Zweisprachig (DE / EN unten)

## Überblick (DE)

Das Projekt ist eine **statische, offline-fähige Web-App** (Single-File + hostbare Version)
plus eine **Python-Pipeline**, die die Daten aus dem Marktstammdatenregister (MaStR) der
Bundesnetzagentur lädt, bereinigt, in eine lokale SQLite-Datenbank importiert und in
kompakte JSON-Dateien für die Karte (inkl. Statistik) exportiert.

**Build:** `scripts/build.sh` (fetch → import → export → bundle, ein Befehl).

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐
│ MaStR (BNetzA)  │───▶│  fetch_mastr.py  │───▶│  import_mastr.py │───▶│  SQLite DB   │
│ öffentl. JSON   │    │  (Roh-JSON)      │    │  (Normalisierung)│    │  mastr.db    │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └──────┬───────┘
                                                                               │
                                            ┌────────────────────────────────┘
                                            ▼ export_app.py
                                     ┌───────────────────────────┐
                                     │ dist/assets/¹              │
                                     │  einheiten.json           │
                                     │  meta.json                │
                                     │  statistiken.json         │
                                     │  historie.json (V4)       │
                                     └──────────┬────────────────┘
                                                │
                      bundle_singlefile.py ──────┤  cp src/index.html
                                            ▼    ▼
                                    ┌──────────────────────┐   ┌────────────────┐
                                    │ src/index.html       │──▶│ dist/index.html│
                                    │ (Leaflet+Marker+     │   │ (hostbar,      │
                                    │  Cluster+Suche+      │   │  fetch Daten)  │
                                    │  Statistik-Panel)    │   └────────────────┘
                                    └──────────────────────┘
  ¹ build.sh fasst fetch→import→export→bundle in einem Befehl zusammen.
```

### Komponenten

| Komponente | Datei | Zweck |
|------------|-------|-------|
| **MaStR-API** | `https://www.marktstammdatenregister.de/MaStR/Einheit/EinheitJson/GetErweiterteOeffentlicheEinheitStromerzeugung` | Öffentlicher JSON-Endpoint (ohne Login). |
| **Download** | `scripts/fetch_mastr.py` | Paginierte Abfrage, Robustheit (Retry, Rate-Limit), Ausgabe `data/raw/{wind,pv}.json`. |
| **Import** | `scripts/import_mastr.py` | SQLite-Schema, Einheiten-Normalisierung, ≥100-kW-Wind / ≥0,5-MWp-PV-Filter, `data/mastr.db`. **V4:** Sichert alten Stand als Snapshot vor Rebuild, berechnet Delta nach Import. |
| **Export** | `scripts/export_app.py` | SQLite → kompaktes JSON für Karte (`dist/assets/*.json`) + Statistik (`statistiken.json`) + Historie (`historie.json`), nur Anlagen mit Geolokation. |
| **Snapshot** | `scripts/snapshot.py` | **V4 (neu):** SQLite-Schema für `snapshots` + `snapshot_einheiten` (26 Asset-Felder), `save_snapshot()`, `compute_delta()`, `build_historie()`. Grundlage für den Update-Historie-Tab. |
| **App** | `src/index.html` | Leaflet-Karte + MarkerCluster (beide **lokal in `src/vendor/`, inline eingebettet** seit 2026-08-31 / DSGVO — kein unpkg-CDN) + Filter + Detail-Popups + **Statistik-Panel (5 Tabs)** + **2-Klick-Consent für OSM-Kacheln**. |
| **Bundle** | `scripts/bundle_singlefile.py` | Erzeugt `dist/index_singlefile.html` (Daten eingebettet, direkt klickbar). |
| **Build** | `scripts/build.sh` | Ein-Befehl-Build (Export + Kopieren). |

### Datenfluss-Details

1. **fetch_mastr.py** fragt die MaStR-API mit Filter ab:
   - Wind: `Energieträger~eq~2497~and~Betriebs-Status~eq~35~and~Bruttoleistung der Einheit~gt~0.1` (≥ 100 kW)
   - PV:   `Energieträger~eq~2495~and~Betriebs-Status~eq~35~and~Bruttoleistung der Einheit~gt~499.9` (≥ 0,5 MWp)
   - Pagination mit `page`/`pageSize`, `chunkedLoading`-freundlich.
2. **import_mastr.py** normalisiert und speichert in SQLite.
3. **export_app.py** wählt nur Anlagen mit `geolokation=1`, schreibt die schlanken Karten-Datensätze
   (`einheiten.json`, `meta.json`) und berechnet zusätzlich die **Statistik** (`statistiken.json`:
   Betreiber-Aggregation + Größenklassen je Technologie).
4. **src/index.html** lädt die Daten (eingebettet aus Single-File ODER per `fetch()` im hostbaren Modus),
   rendert Leaflet-Cluster und bietet Suche + Statistik-Panel.
5. **build.sh** bündelt `fetch → import → export → bundle` in einem nicht-interaktiven Befehl
   (manuell oder als Cronjob; Pi5: in Cron kein `execute_code`).

### Warum zwei Ausgabeformen?

- **dist/index.html + assets/**: hostbar (GitHub Pages, eigener Server) — Daten per `fetch()`.
- **dist/index_singlefile.html**: eine einzige Datei mit eingebetteten Daten — doppelklick-fähig ab `file://`.
  (Hinweis: fetch() ab `file://` ist wegen CORS gesperrt, daher werden die Daten für die
  Single-File direkt eingebettet.)

---

## Overview (EN)

A **static, offline-capable web app** (single HTML file) plus a **Python pipeline** that
fetches data from the German Marktstammdatenregister (MaStR), cleans it, imports it into a
local SQLite database, and exports it as compact JSON for the map.

| Component | File | Purpose |
|-----------|------|---------|
| MaStR API | `GetErweiterteOeffentlicheEinheitStromerzeugung` | Public JSON endpoint (no login). |
| Download  | `scripts/fetch_mastr.py` | Paginated fetch, error handling, retry. |
| Import    | `scripts/import_mastr.py` | SQLite schema, unit normalization, ≥100 kW wind / ≥0.5 MWp PV filter. |
| Export    | `scripts/export_app.py` | SQLite → compact JSON (geo-only). |
| App       | `src/index.html`   | Leaflet map + MarkerCluster + filters + popups. |
| Bundle    | `scripts/bundle_singlefile.py` | Single self-contained HTML (embedded data). |
| Build     | `scripts/build.sh` | One-command build. |

### Data flow

1. `fetch_mastr.py` queries the MaStR API with filters (Wind/PV, "In Betrieb", ≥100 kW wind).
2. `import_mastr.py` normalizes (kW↔MW, dates) and stores into SQLite.
3. `export_app.py` selects only geolocated units and writes compact JSON.
4. `src/index.html` renders Leaflet clusters (embedded data or fetch()).

### Two output forms

- `dist/index.html` + `assets/` → hostable (GitHub Pages, own server).
- `dist/index_singlefile.html` → single file with embedded data, opens from `file://`.
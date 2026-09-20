# Hosting — PV & Wind Karte (MaStR)

> **Stand: 2026-09-20 (V53)** — Das Projekt ist **live auf Vercel** unter der Haupt-URL
> `https://wind-pv-map.de`. Details & alle Schritte: **[docs/DEPLOYMENT.md](DEPLOYMENT.md)**.
> Diese Datei fasst die Auslieferungsformen zusammen und dokumentiert den
> **Self-Hosting-Fallback**.

## Live-Status (Ist-Stand 20.09.2026, V53)

- **Karte:** `https://wind-pv-map.de/` — **Vercel**, HTTPS ✅ (LE bis 19.12.2026), Live-Revision **V53**
  (DSGVO-Konsolidierung, DS-Modal mit Querverweis auf zentrale Portal-DS).
- **Portal:** `https://ingenieur-tools.de/` — V53 (DS-§4 netcup, §6 4 Keys, Impressum o. GitHub).
- **Sun Tracker:** `https://sonne.ingenieur-tools.de/` — **V05** (DSGVO Vercel-Hosting-Block).
- **Galton Board:** `https://galton-board.ingenieur-tools.de/` — **V13** DE/EN (Vercel-Hosting-Block).
- **Hosting:** Vercel (Team pi-brain, Hobby) für **alle 4 Tools** — Deploy je Repo via
  `scripts/deploy_vercel.sh`.
- **Alt-URL stillgelegt:** `wind-pv-map.ingenieur-tools.de` ist tot (DNS gelöscht,
  GitHub-Custom-Domain entfernt). GitHub-Pages-Repos bleiben als **Archiv** erreichbar
  (`pibrainpi.github.io/…`), werden aber nicht mehr aktualisiert.
- **Domain:** netcup (Registrar + CloudDNS). DNS-Ziele in `docs/DEPLOYMENT.md`.

## Grundprinzip

Das Projekt erzeugt eine **statische Website** in `dist/`. Alles läuft clientseitig im Browser
(Leaflet + MarkerCluster + eingebettete/abgerufene JSON-Daten). Kein Server-Backend — nur beim
Daten-Update (lokal per Python-Skripte).

Zwei Auslieferungsformen:
- **`dist/index.html` + `dist/assets/*.json`** → hostbare Version (per `fetch()` geladen) — **das ist der Live-Stand**.
- **`dist/index_singlefile.html`** → eine einzelne Datei, Daten eingebettet (funktioniert ab `file://`).
  Bei Offline-Nutzung (file://) lädt die Karte CARTO-Basemaps (OSM-Daten, CC-BY 3.0) statt OSM-Direktabruf —
  online (live) irrelevant, bewusst nicht in der DS dokumentiert.

## Deploy-Pfad (Vercel, Standard seit 20.09.2026)

1. `dist/` neu bauen: `cp src/index.html dist/index.html` + `python3 scripts/bundle_singlefile.py`
2. `verify_update.sh` (Regel 5) + Revision + User-Freigabe
3. `bash scripts/deploy_vercel.sh` → Production (`wind-pv-map.de`)
4. Live-Verifikation (HTTP-Matrix, meta.stand, B-Checks)

Details, DNS-Tabelle, Pitfalls: **docs/DEPLOYMENT.md**.

## Self-Hosting-Fallback (ohne Vercel)

Statisch via beliebigem Webserver ausliefern — `python3 -m http.server`, nginx, etc.:

```bash
cd dist && python3 -m http.server 8000
# → http://localhost:8000/index.html          (hostbare Variante)
# → http://localhost:8000/index_singlefile.html (offline-fähig)
```

Alternativ bleibt das GitHub-Pages-**Archiv** bestehen: `https://pibrainpi.github.io/pv-wind-map/`
(Stand: Alt-Deploy, wird nicht mehr aktualisiert — nur Notfall-Rückfallebene).

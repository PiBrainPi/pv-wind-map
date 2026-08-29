# Projektstand (Handover) — PV & Wind Karte (MaStR)

> **Dieses Dokument dient als Einstieg für jede neue Agenten-/Arbeitssession.**
> Stand: 2026-08-29 · Repo: `/home/claw_01_rasbpi5_1/Projects/pv-wind-map`

## Was das Projekt ist
Interaktive, offline-fähige HTML-Karte aller **Wind- (≥100 kW) und PV-Anlagen (≥0,5 MWp)**
in Betrieb**, aus dem Marktstammdatenregister (MaStR, BNetzA). Klickbare Single-File + hostbare Version.

## Aktueller Stand (2026-08-29)
- **Datenbasis:** Wind 32.144 (31.114 georeferenziert) · PV 22.371 (22.368 georeferenziert)
  → **53.482 Anlagen auf der Karte**. Betreiber: 23.216.
- **Schwellen (final):** Wind ≥100 kW, PV ≥0,5 MWp (beide 2026-08-29 durch Nutzer-Wunsch gesenkt).
- **HEAD:** `86031e1` (Hersteller-Tabelle = Betreiber-CSS) — Commit-Kette der letzten Runden:
  `86031e1` → `af2ef2c` (Badge/Emoji entfernt) → `4a39fff` (Popup-Deeplinks) → `456c113` (Betreiber-Suche)
  → `5583654` (PV ≥0,5 MWp) → `5f417e7` (Wind ≥100 kW). **Working tree ist sauber/committet.**
- **Klickbare Datei:** `dist/index_singlefile.html` (24,9 MB) + Kopie im Austauschordner
  `/home/claw_01_rasbpi5_1/hermes_human-share/PV-Wind-Karte_MaStR.html`.

## Features
- **Karte:** Leaflet + MarkerCluster, Filter nach Typ (Wind/PV) und Bundesland, Detail-Popups.
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
- **Rechtliches:** Quellenvermerk DL-De-BY-2.0 + Impressum (§5 TMG) fest in der App (Modal).

## Offene Punkte / nächste Schritte (Vorschlag)
- [x] **Alle Revisionen committet** (Betreiber-Suche, Hersteller-Formatierung, Badge-Removal, Deeplinks, Doku). Working tree sauber.
- [x] `docs/statistik.md` & `docs/datenmodell.md` auf neue PV/Wind-Zahlen konsistent (Import 2026-08-29).
- [ ] **Performance:** Single-File ist auf 24,9 MB gewachsen — optional PHP/hostbare Version nutzen,
      Daten-CDN, oder GeoJSON-Minify. Bei `file://`-Laden beachten (einmal war eine leere Seite transient).
- [ ] Hosting (nur vorbereitet, nichts live): `docs/hosting.md` als Anleitung.
- [ ] **GitHub-Publishing** optional: Repo ist lokal `main` ohne Remote; kein automatischer Push.

## Besondere Hinweise für neue Sessions
- **Kein JSON/HTML-Rohcode in Telegram-Chat**; klickbare Datei per `MEDIA:` oder send_telegram_file senden.
- **Ergebnis-Kommunikation:** deutsch, kurze Alarm-Nachrichten bei Fehlern, hart prüfen (kein Halluzinieren),
  Änderungsliste mit Quellen.
- **GitHub-Publishing** (falls gewünscht): Repo ist lokal `main` ohne Remote; kein automatischer Push.
  Doku/README Englisch, keine Secrets, Default privat.
- **Andere LLMs prüfen Ergebnisse gegengegen** — gemeldete Bugs ernst nehmen, verifizieren, fixen.
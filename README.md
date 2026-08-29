# PV & Wind Karte (MaStR)

Interaktive Karte aller **Wind- und Photovoltaikanlagen** in Deutschland aus dem
**Marktstammdatenregister (MaStR)** der Bundesnetzagentur.

**Live-Ansicht (Single-File):** `dist/index_singlefile.html` — einfach im Browser öffnen
(Internet für die Kartenkacheln von OpenStreetMap nötig).

---

## Schnellstart (Build)

```bash
# 1. Daten aus dem MaStR laden (Wind >= 1 MW, PV >= 1 MWp, In Betrieb)
python3 scripts/fetch_mastr.py       # → data/raw/wind.json + pv.json

# 2. In SQLite importieren (Single Source of Truth)
python3 scripts/import_mastr.py      # → data/mastr.db

# 3. Export für die Karten-App (nur Anlagen mit Geolokation)
python3 scripts/export_app.py        # → dist/assets/*.json

# 4. Hostbare App bauen
mkdir -p dist/assets && cp src/index.html dist/index.html

# 5. Optional: eigenständige Einze-Datei (direkt klickbar, Daten eingebettet)
python3 scripts/bundle_singlefile.py # → dist/index_singlefile.html

# 6. Lokal testen (hostbare Version braucht einen HTTP-Server)
python3 -m http.server --directory dist 8080
# öffne http://localhost:8080
```

## Update (manuell, cronjob-fähig)

Die Pipeline ist nicht-interaktiv und damit direkt als Cronjob verwendbar
(Hinweis: in Cron auf dem Pi5 kein `execute_code` nutzen — nur shell/Python).

```bash
python3 scripts/fetch_mastr.py && python3 scripts/import_mastr.py && \
python3 scripts/export_app.py && cp src/index.html dist/index.html && \
python3 scripts/bundle_singlefile.py
```

## Datenbasis & Abgrenzung

| Kategorie | Umfang |
|-----------|--------|
| **Wind** | ≥ 1 MW (Bruttoleistung in MW), Status „In Betrieb“ |
| **Photovoltaik** | ≥ 1 MWp (Bruttoleistung in kWp), Status „In Betrieb“ |
| **Geolokation** | nur Anlagen MIT vorhandenen Koordinaten im MaStR (kein Geocoding) |
| **Quelle** | Marktstammdatenregister (MaStR), BNetzA, öffentliche Daten |

## Dokumentation

- [ANFORDERUNGEN.md](ANFORDERUNGEN.md) – Anforderungen (A1–A11)
- [ENTSCHEIDUNGEN.md](ENTSCHEIDUNGEN.md) – Architektur-Entscheidungen
- [PLAN.md](PLAN.md) – 30-Schritt-Plan
- [docs/](docs/) – detaillierte Doku (Architektur, Datenmodell, Update, Hosting)

## Lizenz

MIT
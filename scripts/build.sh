#!/usr/bin/env bash
# build.sh — Kompletter Projekt-Build in einem Befehl:
#   fetch (Daten vom MaStR) → import (SQLite) → export (+ Statistik) → bundle (Single-File)
#   Danach ist dist/ komplett neu gebaut und die Single-File klickbereit.
# Nicht-interaktiv → auch als Cronjob verwendbar (Pi5: kein execute_code in cron).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "➜ 1/4 Daten vom MaStR laden..."
python3 scripts/fetch_mastr.py

echo "➜ 2/4 Import in SQLite (Normalisierung, ≥100-kW-Wind-Filter)..."
python3 scripts/import_mastr.py

echo "➜ 3/4 Export (Karten-Daten + Statistik aus SQLite)..."
python3 scripts/export_app.py

echo "➜ 4/4 HTML + Impressum + Single-File-Bundle..."
mkdir -p dist/assets
cp src/index.html dist/index.html
cp src/impressum.html dist/impressum.html
python3 scripts/bundle_singlefile.py

echo ""
echo "Fertig. Starte lokal:   python3 -m http.server --directory dist 8080   → http://localhost:8080"
echo "Oder direkt klickbar:   dist/index_singlefile.html"
ls -la dist dist/assets
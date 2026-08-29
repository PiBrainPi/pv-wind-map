#!/usr/bin/env bash
# build.sh — Erzeugt die hostbare Ausgabe in dist/ aus src/ + exportierten Daten.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "➜ 1/2 Export erzuegt (Daten aus SQLite)..."
python3 scripts/export_app.py

echo "➜ 2/2 HTML nach dist/ kopieren..."
mkdir -p dist/assets
cp src/index.html dist/index.html
cp -f dist/assets/einheiten.json dist/assets/einheiten.json
cp -f dist/assets/meta.json dist/assets/meta.json

echo ""
echo "Fertig. Starte lokal:  python3 -m http.server --directory dist 8080"
echo "Dann öffnen:           http://localhost:8080"
ls -la dist dist/assets
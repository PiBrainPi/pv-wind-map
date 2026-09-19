#!/usr/bin/env bash
# build_all.sh — V51.2 (19.09.2026): Voll-Build inkl. Slim-Export + Progress-Fetch.
# Wie gehabt: nap_index → export_app (jetzt mit V51.2-Slim-JSON) → src→dist → bundle.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "➜ 1/4 NAP-Index (NAP-Suche/Ranking-Basis)..."
python3 scripts/export_nap_index.py

echo "➜ 2/4 Export (Karten-Daten + Statistik + Historie aus SQLite, V51.2 slim)..."
python3 scripts/export_app.py

echo "➜ 3/4 HTML → dist..."
cp src/index.html dist/index.html
cp src/impressum.html dist/impressum.html

echo "➜ 4/4 Single-File-Bundle..."
python3 scripts/bundle_singlefile.py

echo ""
echo "✅ Lokaler Build fertig (dist/ + dist/index_singlefile.html auf Datenstand der DB)."
echo "   Prüfvorschrift Regel 5: bash scripts/verify_update.sh — PFLICHT vor jedem Deploy."

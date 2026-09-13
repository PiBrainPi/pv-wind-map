#!/usr/bin/env bash
# build_all.sh — V43.2 (12.09.2026, User-Freigabe): Lokaler Voll-Build nach dem Pipeline-Cron.
# Schritte: nap_index → export_app (Karte+Statistiken+Historie) → src→dist → bundle_singlefile.
# Wird von pipeline2_update.sh NACH dem DB-Import aufgerufen (Schritt 5) — baut NUR LOKAL,
# kein Deploy (Deploy bleibt manuell per scripts/deploy_ghpages.sh nach User-Freigabe).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "➜ 1/4 NAP-Index (NAP-Suche/Ranking-Basis)..."
python3 scripts/export_nap_index.py

echo "➜ 2/4 Export (Karten-Daten + Statistik + Historie aus SQLite)..."
python3 scripts/export_app.py

echo "➜ 3/4 HTML → dist..."
cp src/index.html dist/index.html
cp src/impressum.html dist/impressum.html

echo "➜ 4/4 Single-File-Bundle..."
python3 scripts/bundle_singlefile.py

echo ""
echo "✅ Lokaler Build fertig (dist/ + dist/index_singlefile.html auf Datenstand der DB)."
echo "   Deploy NUR nach User-Freigabe: bash scripts/deploy_ghpages.sh"

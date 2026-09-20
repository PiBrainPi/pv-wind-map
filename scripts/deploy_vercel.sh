#!/usr/bin/env bash
# deploy_vercel.sh — Deploy der PV-&-Wind-Karte nach Vercel (Production).
# V51.3 (20.09.2026): Neue Top-Level-URL wind-pv-map.de (Vercel Free, Team pi-brain).
# Parallel bleibt die Alt-URL wind-pv-map.ingenieur-tools.de (GitHub Pages) live.
#
# Verwendung:
#   bash scripts/deploy_vercel.sh          # Deploy dist/ → Production (wind-pv-map.de)
#
# Voraussetzungen:
#   - Token-Datei ~/.config/vercel_token (chmod 600) — Full-Account-Token (User-Entscheid:
#     bleibt für zukünftige Projekte aktiv; Rotation auf Project-Scope = TODO, s. HANDOVER.md)
#   - node/npx auf dem Pi (npx lädt vercel CLI on-demand)
#
# Deploy-Reihenfolge (Regel 5): erst verify_update.sh + User-Freigabe, DANN deploy
# (gh-pages via deploy_ghpages.sh UND Vercel via dieses Skript).

set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="$HOME/.config/vercel_token"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ Token-Datei fehlt: $TOKEN_FILE" >&2
  exit 1
fi
TOKEN="$(cat "$TOKEN_FILE")"

cd "$PROJ/dist"

echo "➜ Vercel-Deploy (Production) …"
npx --yes vercel@latest deploy --prod --yes --token "$TOKEN"

echo ""
echo "✅ Deploy fertig. Verifikation:"
echo "   https://wind-pv-map.de/                  (Haupt-URL)"
echo "   https://www.wind-pv-map.de/              (Redirect → Apex)"
echo "   https://wind-pv-map.de/assets/einheiten.json  (Daten)"

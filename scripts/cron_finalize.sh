#!/usr/bin/env bash
# cron_finalize.sh — Revision + Verify + Retry als fester Teil des Pipeline-Crons (V57, 26.09.2026).
#
# Was der Cron nach dem Pipeline-Lauf ZUSÄTZLICH automatisiert (ehemals manuell, Schritte
# vom 26.09. — User-Beschluss 26.09.):
#   1. VERIFY (Regel 5): bash scripts/verify_update.sh — bei flüchtigem Chromium-Crash
#      AUTOMATISCHER RETRY (1×, 30 s Pause). Erneuter FAIL = Exit 1 → 🚨-Alarm, Deploy-Stop.
#   2. REVISION: dist/index_singlefile.html → iterations/V<n>_Datenstand_<heute>.html
#      + Kopie nach ~/hermes_human-share/ (Regel 3: niemals löschen, nur anfügen).
#   3. REPORT: kompakte Checkliste für den Cron-Report (stdout → Telegram an Fabs).
#
# NICHT automatisiert (bewusst, Regel 4): Deploy + git push bleiben an die manuelle
# Freigabe von Fabs gebunden — der Cron bereitet nur vor und stellt die klickbare
# HTML im Chat bereit (MEDIA:-Auslieferung durch den Cron-Agenten).
#
# Aufruf:  bash scripts/cron_finalize.sh          (nach pipeline2_update.sh im Cron)
#
# Exit: 0 = VERIFY OK + Revision abgelegt · 1 = VERIFY FAILED (Deploy-Stop, 🚨-Alarm)
set -uo pipefail
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map

TODAY="$(date +%Y-%m-%d)"
VERIFY_RC=1
ATTEMPTS=0
MAX_ATTEMPTS=2

echo "=== FINALIZE: Revision + 100%-Prüfung (TODAY=$TODAY) ==="

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  ATTEMPTS=$((ATTEMPTS + 1))
  echo "➜ verify_update.sh — Versuch $ATTEMPTS/$MAX_ATTEMPTS …"
  bash scripts/verify_update.sh
  VERIFY_RC=$?
  if [ $VERIFY_RC -eq 0 ]; then
    break
  fi
  if [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
    echo "⚠️  VERIFY FAILED (Versuch $ATTEMPTS) — flüchtiger Fehler möglich, Retry in 30 s …"
    sleep 30
  fi
done

if [ $VERIFY_RC -ne 0 ]; then
  echo "🚨 FINALIZE FAILED nach $ATTEMPTS Versuchen — Deploy GESTOPPT, keine Revision angelegt."
  echo "   Befund siehe VERIFY-Report oben. Manuell klären, dann verify erneut."
  exit 1
fi

# ---------- Revision anlegen (nur bei bestandener Prüfung) ----------
# Nächste freie Versionsnummer aus iterations/V*_Datenstand_* ableiten
NEXT=$(ls iterations/ 2>/dev/null | grep -oE '^V[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1)
NEXT=${NEXT:-55}
NEXT=$((NEXT + 1))
REV="iterations/V${NEXT}_Datenstand_${TODAY}.html"
cp dist/index_singlefile.html "$REV"
cp dist/index_singlefile.html "$HOME/hermes_human-share/V${NEXT}_Datenstand_${TODAY}.html"

SHA=$(sha256sum dist/index_singlefile.html | cut -c1-16)
echo ""
echo "✅ REVISION V$NEXT ANGELEGT: $REV"
echo "   (+ Kopie in ~/hermes_human-share/V${NEXT}_Datenstand_${TODAY}.html)"
echo "   SHA: $SHA"
echo ""
echo "FINALIZE OK — Revision V$NEXT bereit. Klickbare HTML: $REV"

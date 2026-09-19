#!/usr/bin/env bash
# verify_update.sh — Prüfvorschrift nach Pipeline-Update (User-Beschluss 19.09.2026)
#
# Nach JEDER Pipeline-Aktualisierung (Cron oder manuell) ist eine 100 %-Prüfung PFLICHT:
#   A) Datenintegration:  DB-Zähler, Snapshot frisch (heute), meta.stand = heute,
#      historie.json ohne Duplikate, Plausibilitäts-Grenzen (update.md V27b),
#      Build-Counts == bs35-Kern (Zahlendrift-Schutz, V30-Muster)
#   B) Funktionsfähigkeit: dist/index.html UND dist/index_singlefile.html im Headless-
#      Chromium — 0 JS-Errors, Infobar, 11 Statistik-Tabs, Historie-Charts (3 SVGs),
#      Zubau-Heatmap, Karten-Marker.
#
# Ergebnis: "✅ VERIFY OK" + Checkliste, oder "🚨 VERIFY FAILED" + Befund.
# Bei FAIL ist der Deploy-Workflow GESTOPPT (kein deploy_ghpages.sh) — erst Befund klären.
#
# Aufruf:   bash scripts/verify_update.sh            (nach jedem Pipeline-/Build-Lauf)
# Optional: node scripts/verify_app.js <html> [chrome]  (nur UI-Teil, eine Datei)
#
# Details der Vorschrift: docs/update.md § „Prüfvorschrift nach Pipeline-Update (PFLICHT)"
set -uo pipefail
cd "$(dirname "$0")/.."

FAIL=0
declare -a RESULTS
ok()  { RESULTS+=("✅ $1"); }
bad() { RESULTS+=("🚨 $1"); FAIL=1; }

# ---------- A1) DB + Snapshot frisch ----------
OUT=$(python3 - <<'PY'
import sqlite3, json, datetime
try:
    db = sqlite3.connect('data/mastr.db')
    c = db.cursor()
    raw = c.execute('select count(*) from einheiten_raw').fetchone()[0]
    sid, sdatum, w, pv, ges, wmw, pmw = c.execute(
        'select id, datum, wind_anzahl, pv_anzahl, gesamt_anzahl, wind_mw, pv_mw from snapshots order by id desc limit 1').fetchone()
    today = datetime.date.today().isoformat()
    if sdatum != today:
        print(f"FAIL: Neuester Snapshot #{sid} vom {sdatum}, erwartet heute ({today})")
        raise SystemExit(1)
    # Plausibilität absolut (nicht Delta): Kern-Bestand in realistischen Grenzen
    if not (25000 < w < 40000 and 15000 < pv < 30000):
        print(f"FAIL: Snapshot-Zahlen unplausibel: Wind {w} / PV {pv}")
        raise SystemExit(1)
    print(f"OK: raw={raw} · Snapshot #{sid} ({sdatum}): Wind {w} / PV {pv} / gesamt {ges} · {wmw:.0f} MW / {pmw:.0f} MW")
except SystemExit:
    raise
except Exception as e:
    print(f"FAIL: DB-Fehler: {e}")
    raise SystemExit(1)
PY
)
if [ $? -eq 0 ]; then ok "A1 DB + Snapshot frisch — $OUT"; else bad "A1 DB/Snapshot: $OUT"; fi

# ---------- A2) meta.stand + historie.json ----------
OUT=$(python3 - <<'PY'
import json, datetime, sys
try:
    m = json.load(open('dist/assets/meta.json'))
    h = json.load(open('dist/assets/historie.json'))
    stand = (m.get('stand') or '')[:10]
    today = datetime.date.today().isoformat()
    if stand != today:
        print(f"FAIL: meta.stand={stand}, erwartet {today}"); raise SystemExit(1)
    daten = [s.get('datum') for s in h]
    if len(daten) != len(set(daten)):
        print(f"FAIL: historie-Duplikate: {daten}"); raise SystemExit(1)
    if daten and daten[-1] != today:
        print(f"FAIL: historie letzter Eintrag {daten[-1]}, erwartet {today}"); raise SystemExit(1)
    print(f"OK: meta.stand={stand} · historie {len(h)} Snapshots, keine Duplikate")
except SystemExit: raise
except Exception as e:
    print(f"FAIL: {e}"); raise SystemExit(1)
PY
)
if [ $? -eq 0 ]; then ok "A2 Export-Meta + Historie — $OUT"; else bad "A2 meta/historie: $OUT"; fi

# ---------- A3) einheiten.json vollständig + Plausibilität (V27b) + Ladezeit-Budget (V51.2) ----------
OUT=$(python3 - <<'PY'
import json, sys, os
try:
    u = json.load(open('dist/assets/einheiten.json'))
    units = u if isinstance(u, list) else (u.get('units') or u.get('einheiten') or [])
    wind = [x for x in units if 'wind' in str(x.get('t', '')).lower()]
    pv   = [x for x in units if 'pv' in str(x.get('t', '')).lower() or 'solar' in str(x.get('t', '')).lower()]
    bad_pv = [x for x in pv if (x.get('mw') or 0) > 250]
    if bad_pv:
        print(f"FAIL: PV >250 MWp: {len(bad_pv)} (z. B. {bad_pv[0].get('m')})"); raise SystemExit(1)
    if not (50000 < len(units) < 90000):
        print(f"FAIL: Einheitenanzahl unplausibel: {len(units)}"); raise SystemExit(1)
    # V51.2 (19.09., User-Befund „LIVE lädt nichts"): Datei-Größe im Budget halten.
    # Root-Cause des Vorfalls: einheiten.json wuchs mit jedem Pipeline-Lauf (39,2 MB)
    # → bei schwacher Anbindung 1–3+ min „Lade Daten…" ohne Progress → User-Abbruch.
    # Slim-Export (V51.2) hält die Datei klein; wächst sie über 40 MB, ist das ein
    # Alarm (Datenwachstum oder Regression im Slim-Export) — Patch vor Deploy nötig.
    import os
    mb = os.path.getsize('dist/assets/einheiten.json') / 1048576
    if os.path.getsize('dist/assets/einheiten.json') > 40 * 1024 * 1024:
        print(f"FAIL: einheiten.json {os.path.getsize('dist/assets/einheiten.json')/1048576:.1f} MB > 40 MB (Ladezeit-Budget F-LADEPROGRESS-1 überschritten — Slim-Export prüfen/patchen vor Deploy)")
        raise SystemExit(1)
    print(f"OK: {len(units)} Einheiten (Karte, alle Status) · {len(wind)} Wind / {len(pv)} PV · V27b-Plausibilität ok · Größe {os.path.getsize('dist/assets/einheiten.json')/1048576:.1f} MB (Budget < 40 MB)")
except SystemExit: raise
except Exception as e:
    print(f"FAIL: {e}"); raise SystemExit(1)
PY
)
if [ $? -eq 0 ]; then ok "A3 einheiten.json — $OUT"; else bad "A3 einheiten.json: $OUT"; fi

# ---------- A4) Build-Counts == bs35-Kern in einheiten.json (Zahlendrift V30-Muster) ----------
OUT=$(python3 - <<'PY'
import json, re, sys, pathlib
try:
    u = json.load(open('dist/assets/einheiten.json'))
    units = u if isinstance(u, list) else (u.get('units') or u.get('einheiten') or [])
    # Infobar/Meta zählt NUR In-Betrieb-Kern (bs 35) — gleiche Semantik wie meta.counts
    wind35 = len([x for x in units if 'wind' in str(x.get('t', '')).lower() and x.get('bs') == 35])
    pv35   = len([x for x in units if ('pv' in str(x.get('t', '')).lower() or 'solar' in str(x.get('t', '')).lower()) and x.get('bs') == 35])
    single = pathlib.Path('dist/index_singlefile.html').read_text(encoding='utf-8')
    i = single.find('__PVWIND_META__')
    if i < 0:
        print("FAIL: __PVWIND_META__ nicht im Singlefile"); raise SystemExit(1)
    block = single[i:i+4000]
    mw = re.search(r'"Wind"\s*:\s*(\d+)', block)
    mp = re.search(r'"Solare Strahlungsenergie"\s*:\s*(\d+)', block)
    if not (mw and mp):
        print("FAIL: counts-Keys nicht gefunden"); raise SystemExit(1)
    bw, bp = int(mw.group(1)), int(mp.group(1))
    if (bw, bp) != (wind35, pv35):
        print(f"FAIL: Build-Meta ({bw}/{bp}) != einheiten.json bs35-Kern ({wind35}/{pv35})"); raise SystemExit(1)
    print(f"OK: Build-Counts == bs35-Kern: {bw} Wind / {bp} PV")
except SystemExit: raise
except Exception as e:
    print(f"FAIL: {e}"); raise SystemExit(1)
PY
)
if [ $? -eq 0 ]; then ok "A4 Counts==bs35-Kern — $OUT"; else bad "A4 Zahlendrift: $OUT"; fi

# ---------- B) Funktionsfähigkeit (beide Builds, Headless-Chromium) ----------
export NODE_PATH="$HOME/.hermes/node/node_modules"
NODE_BIN="$HOME/.hermes/node/bin/node"
CHROME="${CHROME_BIN:-$HOME/.cache/ms-playwright/chromium-1223/chrome-linux/chrome}"

for F in dist/index.html dist/index_singlefile.html; do
  if [ ! -f "$F" ]; then bad "B $F fehlt"; continue; fi
  OUT=$("$NODE_BIN" scripts/verify_app.js "$F" "$CHROME" 2>&1)
  RC=$?
  SUMMARY=$(echo "$OUT" | tail -1)
  if [ $RC -eq 0 ]; then
    ok "B $F — $SUMMARY"
  else
    bad "B $F — $SUMMARY"
    echo "$OUT" | grep -E "^🚨|FATAL" | head -10
  fi
done

echo ""
echo "================ VERIFY-REPORT ================"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "==============================================="
if [ $FAIL -eq 0 ]; then
  echo "✅ VERIFY OK — Prüfung 100 % bestanden."
  echo "   Nächste Schritte (Prüfvorschrift, User-Beschluss 19.09.2026):"
  echo "   1. Geprüfte Datei als Revision ablegen (iterations/ + human-share)"
  echo "   2. Klickbare HTML an Fabs im Chat"
  echo "   3. Auf manuelle Freigabe warten → DANN deploy_ghpages.sh (Regel 4)"
  exit 0
else
  echo "🚨 VERIFY FAILED — Deploy-Workflow GESTOPPT. Befunde oben klären, dann verify erneut."
  exit 1
fi

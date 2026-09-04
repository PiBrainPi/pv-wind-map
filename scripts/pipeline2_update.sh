#!/bin/bash
# pipeline2_update.sh — Pipeline 2.0 als Cronjob-Lauf (Punkt 5, 10-Punkte-Plan).
# Triggert ALLE DREI Datenstränge: Wind, PV (118 Felder) + Netzanschlusspunkte (NAP).
# Inkrementell: fetch_nap.py überspringt gecachte Lokationen (Laufzeit: Minuten).
# Exit != 0 bei jedem Fehler → Hermes-Cron sendet Fehler-Alarm (🚨).
set -euo pipefail
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map

echo "=== Pipeline 2.0 Lauf: $(date '+%Y-%m-%d %H:%M:%S') ==="

# 1+2. Wind & PV: alle 118 Felder holen + inkrementell importieren (mit DB-Backup)
# F5 (--extended-status, verpflichtend!): Holt ZUSÄTZLICH Status 31/37/38 in
# separate Dateien {wind,pv}_status{31,37,38}.json. Ohne das Flag würden die
# Status-Dateien NICHT aktualisiert, import_v2.py ließe alte Daten ein — der
# Status-Filter der Karte (F5) friere auf altem Stand ein.
python3 scripts/fetch_v2.py --extended-status
python3 scripts/import_v2.py

# 3. NAP: nur neue/veränderte Lokationen (Cache nap_fetch_log), resumable
python3 scripts/fetch_nap.py

# 4. NAP-JSONL in die DB importieren (UPSERT)
python3 scripts/import_v2.py

# Kompakter Telegram-fähiger Report (stdout wird vom Cron zugestellt)
python3 - <<'PYEOF'
import sqlite3, json
db = sqlite3.connect("data/mastr.db")
cur = db.cursor()
raw_stand = cur.execute("SELECT value FROM metadaten WHERE key='raw_import_stand'").fetchone()[0]
wind = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE energietraeger_id=2497").fetchone()[0]
pv   = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE energietraeger_id=2495").fetchone()[0]
nap  = cur.execute("SELECT COUNT(*) FROM netzanschlusspunkte").fetchone()[0]
lok  = cur.execute("SELECT COUNT(*) FROM nap_fetch_log WHERE status='ok'").fetchone()[0]
err  = cur.execute("SELECT COUNT(*) FROM nap_fetch_log WHERE status='error'").fetchone()[0]
snap = cur.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
print(f"✅ Pipeline 2.0 OK — Stand {raw_stand[:16]}")
print(f"Wind: {wind} | PV: {pv} | Raw: {wind+pv} (118 Felder 1:1)")
# F5: Status-Zusatz-Volumen im Report (In Planung 31 / Vorüb. stillg. 37 / Endg. stillg. 38)
s31 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=31").fetchone()[0]
s37 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=37").fetchone()[0]
s38 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=38").fetchone()[0]
print(f"F5-Status: Planung {s31} | Vorüb.stillg. {s37} | Endg.stillg. {s38}")
print(f"NAP: {nap} an {lok} Lokationen | MaStR-Datenfehler: {err} | Snapshots: {snap}")
db.close()
PYEOF

#!/bin/bash
# pipeline2_update.sh — Pipeline 2.0 als Cronjob-Lauf (Punkt 5, 10-Punkte-Plan).
# Triggert ALLE DREI Datenstränge: Wind, PV (118 Felder) + Netzanschlusspunkte (NAP).
# Inkrementell: fetch_nap.py überspringt gecachte Lokationen (Laufzeit: Minuten).
# Exit != 0 bei jedem Fehler → Hermes-Cron sendet Fehler-Alarm (🚨).
# V43.2 (12.09.): + sync_legacy.py (Legacy-Tabelle/Snapshots/stand) + build_all.sh
#                 (lokaler Build → dist/ fertig; Deploy bleibt manuell nach Freigabe).
set -euo pipefail
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map

echo "=== Pipeline 2.0 Lauf: $(date '+%Y-%m-%d %H:%M:%S') ==="

# 1+2. Wind & PV: DELTA-Abruf (seit letztem Lauf, F-Fetch-1-Fix: Umlaut-Filternamen!)
# F5 (--extended-status, verpflichtend!): Holt ZUSÄTZLICH Status 31/37/38 im Delta.
# Sicherheitsnetz: Total-Abgleich je Strang → bei Abweichung >5% automatischer
# Vollabruf-Fallback (Meldung im Log). Danach Merge der Delta-Dateien in die
# Basis-JSONs (UPSERT je MaStR-Nummer) + Statuswechsel-Bereinigung.
python3 scripts/fetch_v2.py --extended-status --delta
python3 scripts/merge_delta.py
python3 scripts/import_v2.py

# 3. NAP: nur neue/veränderte Lokationen (Cache nap_fetch_log), resumable
python3 scripts/fetch_nap.py

# 4. NAP-JSONL in die DB importieren (UPSERT)
python3 scripts/import_v2.py

# 4b. Legacy-Tabelle `einheiten` aus einheiten_raw synchronisieren (V43.2, 12.09.)
#     - statistiken.json (Charts) liest aus `einheiten` — ohne Sync drifteten Charts vs. Karte
#     - Snapshot + Delta + historie.json (Update-Historie bekam sonst keine Cron-Punkte)
#     - metadaten.stand = jetzt → Datenstand-Anzeige der App zeigt echten Pipeline-Stand
python3 scripts/sync_legacy.py

# 5. LOKALER BUILD (V43.2, 12.09.): nap_index + export_app + bundle → dist/ fertig.
#    Baut NUR LOKAL — kein Auto-Deploy (Grundsatzentscheidung); Deploy bleibt manuell
#    per scripts/deploy_ghpages.sh nach User-Freigabe.
bash scripts/build_all.sh

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
stand = (cur.execute("SELECT value FROM metadaten WHERE key='stand'").fetchone() or ("?",))[0]
e35w = cur.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2497 AND betriebs_status='In Betrieb'").fetchone()[0]
e35p = cur.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2495 AND betriebs_status='In Betrieb'").fetchone()[0]
print(f"✅ Pipeline 2.0 OK — Stand {raw_stand[:16]}")
print(f"Wind: {wind} | PV: {pv} | Raw: {wind+pv} (118 Felder 1:1)")
# F5: Status-Zusatz-Volumen im Report (In Planung 31 / Vorüb. stillg. 37 / Endg. stillg. 38)
s31 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=31").fetchone()[0]
s37 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=37").fetchone()[0]
s38 = cur.execute("SELECT COUNT(*) FROM einheiten_raw WHERE json_extract(raw_json,'$.BetriebsStatusId')=38").fetchone()[0]
print(f"F5-Status: Planung {s31} | Vorüb.stillg. {s37} | Endg.stillg. {s38}")
print(f"NAP: {nap} an {lok} Lokationen | MaStR-Datenfehler: {err} | Snapshots: {snap}")
print(f"Karte (In Betrieb): Wind {e35w} · PV {e35p} — Datenstand {stand[:16]} | Build: dist/ lokal aktualisiert (Deploy manuell)")
db.close()
PYEOF

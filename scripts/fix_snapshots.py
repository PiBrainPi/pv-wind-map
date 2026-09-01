#!/usr/bin/env python3
"""Fix snapshots V3: Korrekt — alte Daten aus gh-pages, neue aus DB."""
import json, sqlite3, sys
sys.path.insert(0, "scripts")
from snapshot import ensure_schema, save_snapshot, compute_delta, build_historie, _ASSET_COLS
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "mastr.db"
db = sqlite3.connect(DB)
ensure_schema(db)

# Alte Snapshot-Tabellen komplett neu aufbauen
db.execute("DROP TABLE IF EXISTS snapshot_einheiten")
db.execute("DELETE FROM snapshots")
db.commit()
ensure_schema(db)

# Snapshot 0: Alter Stand (29.08.) aus /tmp/old_einheiten.json (von gh-pages extrahiert)
old_units = json.loads(Path("/tmp/old_einheiten.json").read_text(encoding="utf-8"))
old_meta = json.loads(Path("/tmp/old_meta.json").read_text(encoding="utf-8"))
old_datum = old_meta.get("stand", "2026-08-29")[:10]
print(f"Old data: {len(old_units)} units from {old_datum}")

wind_anz = sum(1 for u in old_units if u["t"] == "wind")
pv_anz = sum(1 for u in old_units if u["t"] == "pv")
gesamt_anz = len(old_units)
wind_mw = round(sum(u["mw"] for u in old_units if u["t"] == "wind"), 2)
pv_mw = round(sum(u["mw"] for u in old_units if u["t"] == "pv"), 2)
gesamt_mw = round(wind_mw + pv_mw, 2)

bl_map = {}
for u in old_units:
    if not u.get("b"): continue
    bl = u["b"]
    if bl not in bl_map: bl_map[bl] = {"wind": 0, "pv": 0, "wind_mw": 0.0, "pv_mw": 0.0}
    if u["t"] == "wind":
        bl_map[bl]["wind"] += 1
        bl_map[bl]["wind_mw"] += u.get("mw", 0)
    else:
        bl_map[bl]["pv"] += 1
        bl_map[bl]["pv_mw"] += u.get("mw", 0)
for bl in bl_map:
    bl_map[bl]["wind_mw"] = round(bl_map[bl]["wind_mw"], 2)
    bl_map[bl]["pv_mw"] = round(bl_map[bl]["pv_mw"], 2)

cur = db.execute(
    "INSERT INTO snapshots (datum, wind_anzahl, pv_anzahl, gesamt_anzahl, "
    "wind_mw, pv_mw, gesamt_mw, bundeslaender_json) VALUES (?,?,?,?,?,?,?,?)",
    (old_datum, wind_anz, pv_anz, gesamt_anz, wind_mw, pv_mw, gesamt_mw, json.dumps(bl_map, ensure_ascii=False))
)
snap0_id = cur.lastrowid

# Alte Einheiten in snapshot_einheiten speichern (mit vollen Asset-Daten)
def old_unit_to_row(u, snap_id):
    et_id = 2497 if u["t"] == "wind" else 2495
    return (
        snap_id, u["m"], et_id,
        u.get("n"), u.get("art"), u.get("mw"),
        u.get("b"), u.get("lk"), u.get("g"), u.get("plz"), u.get("g"),  # ort fallback
        u.get("inb"), u.get("lat"), u.get("lon"),
        u.get("nb"), u.get("ab"), u.get("st"),
        u.get("mod"), u.get("ausr"), u.get("park"),
        u.get("nh"), u.get("rd"), u.get("lhh"), u.get("typ"),
        u.get("herst"), u.get("wp"), u.get("los"),
    )

ncols = len(_ASSET_COLS.split(",")) + 1  # +1 for snapshot_id
placeholders = ",".join("?" * ncols)
db.executemany(
    f"INSERT INTO snapshot_einheiten VALUES ({placeholders})",
    [old_unit_to_row(u, snap0_id) for u in old_units]
)
db.commit()
print(f"Snapshot #{snap0_id} ({old_datum}): Wind {wind_anz}, PV {pv_anz}, Gesamt {gesamt_anz}")

# Snapshot 1: Neuer Stand aus der DB (01.09.)
snap1_id = save_snapshot(db, "2026-09-01")

# Delta berechnen
delta = compute_delta(db, snap0_id, snap1_id)
print(f"\n=== Delta ({delta['old_datum']} → {delta['new_datum']}) ===")
print(f"  Wind neu: +{delta['wind_neu']} (+{delta['wind_mw_neu']} MW)")
print(f"  PV neu:   +{delta['pv_neu']} (+{delta['pv_mw_neu']} MW)")
print(f"  Gesamt neu: +{delta['gesamt_neu']} (+{delta['gesamt_mw_neu']} MW)")
print(f"  Entfernt: {delta['removed_anzahl']}")
print(f"  Added assets: {len(delta['added_assets'])}")
if delta['added_assets']:
    for a in delta['added_assets'][:5]:
        print(f"    + {a['n']} ({a['t']}, {a['mw']} MW, {a['b']})")
print(f"  Removed assets: {len(delta['removed_assets'])}")
if delta['removed_assets']:
    for a in delta['removed_assets'][:5]:
        print(f"    - {a['n']} ({a['t']}, {a['mw']} MW, {a['b']})")
print(f"  Bundesländer mit Veränderung: {len(delta['bundeslaender_delta'])}")

# Historie-JSON schreiben
historie = build_historie(db)
(ROOT / "dist/assets/historie.json").write_text(json.dumps(historie, ensure_ascii=False, indent=2), encoding="utf-8")
hist_size = (ROOT / "dist/assets/historie.json").stat().st_size / 1024
print(f"\nHistorie: {len(historie)} Snapshots → dist/assets/historie.json ({hist_size:.1f} KB)")
db.close()

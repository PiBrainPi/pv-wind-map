#!/usr/bin/env python3
"""
snapshot.py — Snapshot- & Delta-Logik für den Update-Historie-Tracker.

Speichert bei jedem Import-Update einen Snapshot der aggregierten Kennzahlen
(Anzahl, Leistung, Bundesländer-Verteilung je Wind/PV/Gesamt) in der SQLite-DB
und berechnet das Delta zum vorherigen Snapshot — inkl. der vollen Asset-Daten
aller hinzugefügten/entfernten Anlagen für die Detail-Ansicht in der HTML-App.

Tabellen:
  snapshots:          id, datum, wind/pv/gesamt_anzahl, wind/pv/gesamt_mw, bundeslaender_json
  snapshot_einheiten:  snapshot_id + alle Asset-Felder (für Detail-Delta)

Historie-JSON (für die HTML-App):
  Wird von build_historie(db) generiert; enthält je Snapshot die aggregierten
  Zahlen + das Delta zum Vorgänger mit allen added/removed Assets (volle Daten).
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mastr.db"

SNAPSHOT_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TEXT,
    wind_anzahl INTEGER,
    pv_anzahl INTEGER,
    gesamt_anzahl INTEGER,
    wind_mw REAL,
    pv_mw REAL,
    gesamt_mw REAL,
    bundeslaender_json TEXT
);
CREATE TABLE IF NOT EXISTS snapshot_einheiten (
    snapshot_id INTEGER,
    mastr_nummer TEXT,
    energietraeger_id INTEGER,
    einheit_name TEXT,
    art TEXT,
    bruttoleistung_mw REAL,
    bundesland TEXT,
    landkreis TEXT,
    gemeinde TEXT,
    plz TEXT,
    ort TEXT,
    inbetriebnahme_datum TEXT,
    lat REAL,
    lon REAL,
    netzbetreiber TEXT,
    anlagenbetreiber TEXT,
    system_status TEXT,
    anzahl_solar_module INTEGER,
    hauptausrichtung TEXT,
    solarpark_name TEXT,
    nabenhoehe_m REAL,
    rotordurchmesser_m REAL,
    lichte_hoehe_m REAL,
    typenbezeichnung TEXT,
    hersteller TEXT,
    windpark_name TEXT,
    land_oder_see TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);
CREATE INDEX IF NOT EXISTS idx_snap_einheiten ON snapshot_einheiten(snapshot_id, mastr_nummer);
"""

# Spalten für snapshot_einheiten (ohne snapshot_id)
_ASSET_COLS = (
    "mastr_nummer, energietraeger_id, einheit_name, art, bruttoleistung_mw, "
    "bundesland, landkreis, gemeinde, plz, ort, inbetriebnahme_datum, "
    "lat, lon, netzbetreiber, anlagenbetreiber, system_status, "
    "anzahl_solar_module, hauptausrichtung, solarpark_name, "
    "nabenhoehe_m, rotordurchmesser_m, lichte_hoehe_m, typenbezeichnung, "
    "hersteller, windpark_name, land_oder_see"
)


def ensure_schema(db: sqlite3.Connection):
    """Legt die Snapshot-Tabellen an, falls nicht vorhanden."""
    db.executescript(SNAPSHOT_SCHEMA)


def _bundeslaender_map(db: sqlite3.Connection) -> dict:
    """Aggregiert die aktuelle Bundesländer-Verteilung aus der DB (nur geolokation=1)."""
    bl = {}
    rows = db.execute(
        "SELECT bundesland, energietraeger_id, COUNT(*), SUM(bruttoleistung_mw) "
        "FROM einheiten WHERE geolokation=1 AND bundesland IS NOT NULL "
        "GROUP BY bundesland, energietraeger_id"
    ).fetchall()
    for name, et_id, anzahl, sum_mw in rows:
        if name not in bl:
            bl[name] = {"wind": 0, "pv": 0, "wind_mw": 0.0, "pv_mw": 0.0}
        if et_id == 2497:
            bl[name]["wind"] = anzahl
            bl[name]["wind_mw"] = round(sum_mw or 0, 2)
        else:
            bl[name]["pv"] = anzahl
            bl[name]["pv_mw"] = round(sum_mw or 0, 2)
    return bl


def _db_stats(db: sqlite3.Connection) -> dict:
    """Liest die aggregierten Kennzahlen aus der DB (nur geolokation=1)."""
    wind = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM einheiten "
        "WHERE geolokation=1 AND energietraeger_id=2497"
    ).fetchone()
    pv = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM einheiten "
        "WHERE geolokation=1 AND energietraeger_id=2495"
    ).fetchone()
    gesamt = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM einheiten "
        "WHERE geolokation=1"
    ).fetchone()
    return {
        "wind_anzahl": wind[0], "wind_mw": round(wind[1], 2),
        "pv_anzahl": pv[0], "pv_mw": round(pv[1], 2),
        "gesamt_anzahl": gesamt[0], "gesamt_mw": round(gesamt[1], 2),
    }


def _row_to_asset_dict(r: tuple) -> dict:
    """Konvertiert eine DB-Zeile (aus snapshot_einheiten oder einheiten) in ein Asset-Dict für die HTML-App."""
    is_pv = r[1] == 2495  # r[1] = energietraeger_id
    d = {
        "m": r[0],      # mastr_nummer
        "n": r[2],      # einheit_name
        "t": "pv" if is_pv else "wind",
        "art": r[3],
        "mw": r[4],
        "b": r[5],      # bundesland
        "lk": r[6],     # landkreis
        "g": r[7] or r[9],  # gemeinde (fallback ort)
        "plz": r[8],
        "inb": r[10],   # inbetriebnahme_datum
        "lat": r[11],
        "lon": r[12],
        "nb": r[13],    # netzbetreiber
        "ab": r[14],    # anlagenbetreiber
        "st": r[15],    # system_status
    }
    if is_pv:
        d["mod"] = r[16]   # anzahl_solar_module
        d["ausr"] = r[17]  # hauptausrichtung
        d["park"] = r[18]  # solarpark_name
    else:
        d["nh"] = r[19]     # nabenhoehe_m
        d["rd"] = r[20]     # rotordurchmesser_m
        d["lhh"] = r[21]    # lichte_hoehe_m
        d["typ"] = r[22]    # typenbezeichnung
        d["herst"] = r[23]  # hersteller
        d["wp"] = r[24]     # windpark_name
        d["los"] = r[25]    # land_oder_see
    return d


def save_snapshot(db: sqlite3.Connection, datum: str = None) -> int:
    """Speichert den aktuellen DB-Stand als Snapshot. Gibt die snapshot_id zurück."""
    ensure_schema(db)
    if datum is None:
        datum = datetime.now().strftime("%Y-%m-%d")

    stats = _db_stats(db)
    bl_map = _bundeslaender_map(db)

    cur = db.execute(
        "INSERT INTO snapshots (datum, wind_anzahl, pv_anzahl, gesamt_anzahl, "
        "wind_mw, pv_mw, gesamt_mw, bundeslaender_json) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (datum, stats["wind_anzahl"], stats["pv_anzahl"], stats["gesamt_anzahl"],
         stats["wind_mw"], stats["pv_mw"], stats["gesamt_mw"],
         json.dumps(bl_map, ensure_ascii=False))
    )
    snapshot_id = cur.lastrowid

    # Alle Asset-Daten für Detail-Delta speichern
    cols_str = _ASSET_COLS
    rows = db.execute(
        f"SELECT {cols_str} FROM einheiten WHERE geolokation=1"
    ).fetchall()
    placeholders = ",".join("?" * (len(cols_str.split(",")) + 1))  # +1 for snapshot_id
    db.executemany(
        f"INSERT INTO snapshot_einheiten VALUES ({placeholders})",
        [(snapshot_id,) + tuple(r) for r in rows]
    )

    db.commit()
    print(f"Snapshot #{snapshot_id} gespeichert: {datum} — "
          f"Wind {stats['wind_anzahl']}, PV {stats['pv_anzahl']}, "
          f"Gesamt {stats['gesamt_anzahl']}, {len(bl_map)} Bundesländer, "
          f"{len(rows)} Einheiten-Referenzen")
    return snapshot_id


def compute_delta(db: sqlite3.Connection, old_id: int, new_id: int) -> dict:
    """Berechnet das Delta zwischen zwei Snapshots, inkl. aller added/removed Assets."""
    old = db.execute("SELECT * FROM snapshots WHERE id=?", (old_id,)).fetchone()
    new = db.execute("SELECT * FROM snapshots WHERE id=?", (new_id,)).fetchone()
    if not old or not new:
        return {}

    old_bl = json.loads(old[8] or "{}")
    new_bl = json.loads(new[8] or "{}")

    # MaStR-Nummern vergleichen
    old_nums = set(r[0] for r in db.execute(
        "SELECT mastr_nummer FROM snapshot_einheiten WHERE snapshot_id=?", (old_id,)
    ).fetchall())
    new_nums = set(r[0] for r in db.execute(
        "SELECT mastr_nummer FROM snapshot_einheiten WHERE snapshot_id=?", (new_id,)
    ).fetchall())

    added = new_nums - old_nums
    removed = old_nums - new_nums

    # Vollen Asset-Daten für hinzugefügte Anlagen (aus neuen Snapshot)
    added_assets = []
    if added:
        cols_str = _ASSET_COLS
        placeholders = ",".join("?" * len(added))
        rows = db.execute(
            f"SELECT {cols_str} FROM snapshot_einheiten "
            f"WHERE snapshot_id=? AND mastr_nummer IN ({placeholders})",
            [new_id] + list(added)
        ).fetchall()
        added_assets = [_row_to_asset_dict(r) for r in rows]

    # Vollen Asset-Daten für entfernte Anlagen (aus altem Snapshot)
    removed_assets = []
    if removed:
        cols_str = _ASSET_COLS
        placeholders = ",".join("?" * len(removed))
        rows = db.execute(
            f"SELECT {cols_str} FROM snapshot_einheiten "
            f"WHERE snapshot_id=? AND mastr_nummer IN ({placeholders})",
            [old_id] + list(removed)
        ).fetchall()
        removed_assets = [_row_to_asset_dict(r) for r in rows]

    # Neuanlagen nach Wind/PV aufschlüsseln
    wind_neu = sum(1 for a in added_assets if a["t"] == "wind")
    pv_neu = sum(1 for a in added_assets if a["t"] == "pv")
    wind_mw_neu = round(sum(a["mw"] or 0 for a in added_assets if a["t"] == "wind"), 2)
    pv_mw_neu = round(sum(a["mw"] or 0 for a in added_assets if a["t"] == "pv"), 2)

    # Bundesländer-Delta
    all_bl = sorted(set(list(old_bl.keys()) + list(new_bl.keys())))
    bl_delta = {}
    for bl_name in all_bl:
        o = old_bl.get(bl_name, {"wind": 0, "pv": 0, "wind_mw": 0, "pv_mw": 0})
        n = new_bl.get(bl_name, {"wind": 0, "pv": 0, "wind_mw": 0, "pv_mw": 0})
        d = {
            "wind": n["wind"] - o["wind"],
            "pv": n["pv"] - o["pv"],
            "wind_mw": round(n["wind_mw"] - o["wind_mw"], 2),
            "pv_mw": round(n["pv_mw"] - o["pv_mw"], 2),
        }
        if any(v != 0 for v in d.values()):
            bl_delta[bl_name] = d

    return {
        "old_datum": old[1],
        "new_datum": new[1],
        "wind_neu": wind_neu,
        "pv_neu": pv_neu,
        "gesamt_neu": wind_neu + pv_neu,
        "wind_mw_neu": wind_mw_neu,
        "pv_mw_neu": pv_mw_neu,
        "gesamt_mw_neu": round(wind_mw_neu + pv_mw_neu, 2),
        "wind_diff_anzahl": new[2] - old[2],
        "pv_diff_anzahl": new[3] - old[3],
        "gesamt_diff_anzahl": new[4] - old[4],
        "wind_diff_mw": round(new[5] - old[5], 2),
        "pv_diff_mw": round(new[6] - old[6], 2),
        "gesamt_diff_mw": round(new[7] - old[7], 2),
        "removed_anzahl": len(removed),
        "bundeslaender_delta": bl_delta,
        "added_assets": added_assets,
        "removed_assets": removed_assets,
    }


def build_historie(db: sqlite3.Connection) -> list:
    """Generiert die komplette Historie-Liste für die HTML-App."""
    ensure_schema(db)
    snapshots = db.execute("SELECT * FROM snapshots ORDER BY id").fetchall()
    if not snapshots:
        return []

    historie = []
    for i, snap in enumerate(snapshots):
        entry = {
            "datum": snap[1],
            "wind_anzahl": snap[2],
            "pv_anzahl": snap[3],
            "gesamt_anzahl": snap[4],
            "wind_mw": snap[5],
            "pv_mw": snap[6],
            "gesamt_mw": snap[7],
            "bundeslaender": json.loads(snap[8] or "{}"),
        }
        if i > 0:
            delta = compute_delta(db, snapshots[i - 1][0], snap[0])
            entry["delta"] = delta
        else:
            entry["delta"] = None
        historie.append(entry)

    return historie

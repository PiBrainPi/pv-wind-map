#!/usr/bin/env python3
"""
export_app.py — Erzeugt aus der SQLite-Datenbank das kompakte JSON für die Karten-App.

Ausgabe (in project dist/):
  dist/assets/einheiten.json  -> kompakte Liste der anzuzeigenden Anlagen (nur mit Geolokation)
  dist/assets/meta.json       -> Metadaten (Stand, Zähler, Abgrenzung) für die App-Anzeige

Nur Anlagen MIT Geolokation werden exportiert (Entscheidung 1: keine erfundenen Positionen).
Die Daten werden bewusst schlank gehalten (nur Felder für Karte + Detail-Popup).

Nutzung: python3 scripts/export_app.py
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mastr.db"
DIST = ROOT / "dist" / "assets"

SELECT = """
SELECT
    mastr_nummer, einheit_name, energietraeger_id, energietraeger_name, art,
    bruttoleistung_mw, betriebs_status, system_status,
    inbetriebnahme_datum, bundesland, landkreis, gemeinde, plz, ort,
    lat, lon,
    netzbetreiber, anlagenbetreiber,
    anzahl_solar_module, hauptausrichtung, solarpark_name,
    nabenhoehe_m, rotordurchmesser_m, lichte_hoehe_m, typenbezeichnung,
    hersteller, windpark_name, land_oder_see
FROM einheiten
WHERE geolokation = 1
"""


def build_units(rows) -> list[dict]:
    # Spaltenreihenfolge laut SELECT:
    # 0 mastr, 1 name, 2 et_id, 3 et_name, 4 art, 5 mw, 6 status, 7 sysstatus,
    # 8 inb, 9 bundesland, 10 landkreis, 11 gemeinde, 12 plz, 13 ort,
    # 14 lat, 15 lon, 16 netz, 17 ab,
    # 18 anzahl_module, 19 ausr, 20 solarpark,
    # 21 nabenhoehe, 22 rotordurchmesser, 23 lichte, 24 typ, 25 hersteller,
    # 26 windpark, 27 land_oder_see
    units = []
    for r in rows:
        is_pv = (r[2] == 2495)
        u = {
            "m":  r[0],            # mastr_nummer
            "n":  r[1],            # name
            "t":  "pv" if is_pv else "wind",
            "art": r[4],
            "mw": r[5],
            "b":  r[9],            # bundesland
            "lk": r[10],           # landkreis
            "g":  r[11] or r[13],  # gemeinde (fallback ort)
            "plz": r[12],
            "inb": r[8],           # inbetriebnahmedatum
            "nb": r[16],           # netzbetreiber
            "ab": r[17],           # anlagenbetreiber
            "st": r[7],            # system_status
            "lat": r[14],
            "lon": r[15],
        }
        if is_pv:
            u["mod"]   = r[18]     # anzahl_solar_module
            u["ausr"]  = r[19]     # hauptausrichtung
            u["park"]  = r[20]     # solarpark_name
        else:
            u["nh"]    = r[21]     # nabenhoehe_m
            u["rd"]    = r[22]     # rotordurchmesser_m
            u["lhh"]   = r[23]     # lichte_hoehe_m
            u["typ"]   = r[24]     # typenbezeichnung
            u["herst"] = r[25]     # hersteller
            u["wp"]    = r[26]     # windpark_name
            u["los"]   = r[27]     # land_oder_see
        units.append(u)
    return units


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(SELECT + " ORDER BY energietraeger_id, mastr_nummer").fetchall()
    db.close()

    units = build_units(rows)

    # Metadaten + Zähler
    db = sqlite3.connect(DB_PATH)
    stand = (db.execute("SELECT value FROM metadaten WHERE key='stand'").fetchone() or (None,))[0]
    counts = {name: cnt for name, cnt in db.execute(
        "SELECT energietraeger_name, COUNT(*) FROM einheiten WHERE geolokation=1 GROUP BY energietraeger_name").fetchall()}
    db.close()

    meta = {
        "stand": stand or datetime.now().isoformat(timespec="seconds"),
        "quelle": "Marktstammdatenregister (BNetzA)",
        "abgrenzung": "Wind >= 1 MW und PV >= 1 MWp, Status 'In Betrieb', nur Anlagen mit vorhandener Geolokation",
        "counts": counts,
        "total_geolokation": len(units),
    }

    with open(DIST / "einheiten.json", "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False)
    with open(DIST / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    size = (DIST / "einheiten.json").stat().st_size / 1024 / 1024
    print(f"Export: {len(units)} Anlagen -> dist/assets/einheiten.json ({size:.1f} MB)")
    print(f"Metadaten -> dist/assets/meta.json")
    print(f"Zähler: {counts}")


if __name__ == "__main__":
    main()
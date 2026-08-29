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


def build_statistiken(db) -> dict:
    """Berechnet aus der Datenbank die Statistiken für das Statistik-Panel.

    Liefert:
      betreiber:  Liste {name, anzahl, sum_mw, avg_mw, tech:{pv,wind}} — nach sum_mw absteigend
      hersteller: Liste {name, anzahl, sum_mw, avg_mw} — nur Wind (PV hat keine Herstellerangaben im MaStR)
      groessenklassen: { wind: [...], pv: [...] } -> {label, von, bis, anzahl, sum_mw, anteil_anzahl, anteil_summe}
      gesamt:     {wind_anzahl, pv_anzahl, total_anzahl, wind_max_mw, pv_max_mw}
    """
    # Betreiber-Aggregation (nur georeferenzierte Anlagen, wie die Karte)
    betreiber = {}
    for r in db.execute(
        "SELECT anlagenbetreiber, energietraeger_name, bruttoleistung_mw "
        "FROM einheiten WHERE geolokation=1 AND anlagenbetreiber IS NOT NULL"
    ).fetchall():
        name, et, mw = r[0], r[1], r[2] or 0.0
        b = betreiber.setdefault(name, {"name": name, "anzahl": 0, "sum_mw": 0.0, "tech": {"pv": 0, "wind": 0}})
        b["anzahl"] += 1
        b["sum_mw"] += mw
        key = "pv" if et == "Solare Strahlungsenergie" else "wind"
        b["tech"][key] += 1
    betreiber_list = sorted(betreiber.values(), key=lambda x: -x["sum_mw"])
    for b in betreiber_list:
        b["avg_mw"] = round(b["sum_mw"] / b["anzahl"], 3)
        b["sum_mw"] = round(b["sum_mw"], 3)

    # Hersteller-Aggregation (nur Wind — PV hat keine Herstellerangaben im MaStR)
    hersteller = {}
    for r in db.execute(
        "SELECT hersteller, bruttoleistung_mw FROM einheiten "
        "WHERE geolokation=1 AND energietraeger_id=2497 "
        "AND hersteller IS NOT NULL AND hersteller != ''"
    ).fetchall():
        name, mw = (r[0] or "Unbekannt").strip(), r[1] or 0.0
        h = hersteller.setdefault(name, {"name": name, "anzahl": 0, "sum_mw": 0.0})
        h["anzahl"] += 1
        h["sum_mw"] += mw
    hersteller_list = sorted(hersteller.values(), key=lambda x: -x["sum_mw"])
    for h in hersteller_list:
        h["avg_mw"] = round(h["sum_mw"] / h["anzahl"], 3)
        h["sum_mw"] = round(h["sum_mw"], 3)

    # Größenklassen je Technologie (feste Staffel, bis zum realen Maximum)
    klassen = {
        "wind": [("1–2", 1, 2), ("2–3", 2, 3), ("3–4", 3, 4), ("4–5", 4, 5),
                 ("5–7", 5, 7), ("7–10", 7, 10), ("10–20", 10, 20),
                 ("20–50", 20, 50), ("50–100", 50, 100), ("100+", 100, 1e9)],
        "pv":   [("1–2", 1, 2), ("2–5", 2, 5), ("5–10", 5, 10),
                 ("10–30", 10, 30), ("30–60", 30, 60), ("60–100", 60, 100),
                 ("100–200", 100, 200), ("200+", 200, 1e9)],
    }
    et_ids = {"wind": 2497, "pv": 2495}
    groessen = {"wind": [], "pv": []}
    maxima = {}
    for tech, kliste in klassen.items():
        rows = db.execute(
            "SELECT bruttoleistung_mw FROM einheiten WHERE geolokation=1 AND energietraeger_id=?",
            (et_ids[tech],)).fetchall()
        mws = [r[0] for r in rows if r[0] is not None]
        total_mw = sum(mws)
        total_n = len(mws)
        maxima[tech] = round(max(mws), 2) if mws else 0
        for label, von, bis in kliste:
            n = sum(1 for v in mws if von <= v < bis)
            s = sum(v for v in mws if von <= v < bis)
            if n == 0:
                continue  # leere Klassen weglassen
            groessen[tech].append({
                "label": label, "von": von, "bis": bis,
                "anzahl": n, "sum_mw": round(s, 2),
                "anteil_anzahl": round(100.0 * n / total_n, 1) if total_n else 0,
                "anteil_summe": round(100.0 * s / total_mw, 1) if total_mw else 0,
            })

    totals = {
        "wind_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2497").fetchone()[0],
        "pv_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2495").fetchone()[0],
        "herstellbar_wind": sum(x["anzahl"] for x in hersteller_list),
        "total_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1").fetchone()[0],
        "wind_max_mw": maxima["wind"],
        "pv_max_mw": maxima["pv"],
    }

    return {
        "betreiber": betreiber_list,
        "hersteller": hersteller_list,
        "groessenklassen": groessen,
        "gesamt": totals,
    }


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

    # Statistik-Panel
    db = sqlite3.connect(DB_PATH)
    statistiken = build_statistiken(db)
    db.close()

    with open(DIST / "einheiten.json", "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False)
    with open(DIST / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    with open(DIST / "statistiken.json", "w", encoding="utf-8") as f:
        json.dump(statistiken, f, ensure_ascii=False)
    size = (DIST / "einheiten.json").stat().st_size / 1024 / 1024
    print(f"Export: {len(units)} Anlagen -> dist/assets/einheiten.json ({size:.1f} MB)")
    print("Metadaten -> dist/assets/meta.json")
    print(f"Zähler: {counts}")
    stat_et = statistiken["gesamt"]
    print(f"Statistik: {len(statistiken['betreiber'])} Betreiber | Wind max {stat_et['wind_max_mw']} MW | PV max {stat_et['pv_max_mw']} MW | gesamt {stat_et['total_anzahl']} -> dist/assets/statistiken.json")


if __name__ == "__main__":
    main()
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
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mastr.db"
DIST = ROOT / "dist" / "assets"

# V23: Park-Schlüssel auf Modulebene — identische Logik zu build_statistiken._park_key (V22),
# damit Frontend-Filter (Paket 8: park-aggregierter Leistungsfilter) und Statistik (V22-Cluster)
# denselben Schlüssel verwenden. ROMAN = Suffixe, die einen Park-Split bezeichnen.
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii",
         "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"}


def park_key(tech: str, park_name: str | None, einheit_name: str | None) -> str:
    """Normalisierter Park-Schlüssel: SolarparkName/WindparkName, sonst Namens-Präfix."""
    if park_name and park_name.strip():
        return park_name.strip().lower()
    p = re.split(r"\s+[-–]\s+", (einheit_name or "").strip())[0].strip()
    toks = p.rsplit(" ", 1)
    if len(toks) == 2 and toks[1].lower() in ROMAN and len(toks[0]) >= 4:
        return toks[0].lower()
    return p.lower() if p and len(p) >= 4 else f"__einzel__{(einheit_name or '').lower()}"


def cluster_key(tech: str, betreiber: str | None, pk: str) -> str:
    """V23: Cluster-Schlüssel (ET + Betreiber + Park-Schlüssel) für Mapping & Statistik."""
    return f"{tech}|{(betreiber or '').strip().lower()}|{pk}"

SELECT = """
SELECT
    mastr_nummer, einheit_name, energietraeger_id, energietraeger_name, art,
    bruttoleistung_mw, betriebs_status, system_status,
    inbetriebnahme_datum, bundesland, landkreis, gemeinde, plz, ort,
    lat, lon,
    netzbetreiber, anlagenbetreiber,
    anzahl_solar_module, hauptausrichtung, solarpark_name,
    nabenhoehe_m, rotordurchmesser_m, lichte_hoehe_m, typenbezeichnung,
    hersteller, windpark_name, land_oder_see,
    registrierungsdatum
FROM einheiten
WHERE geolokation = 1
"""

# F5: Zusatz-Status (In Planung / stillgelegt) leben in einheiten_raw (118-Feld-JSON).
# F5b (Heute): Die Status-35-Basis kommt AUCH aus einheiten_raw — der Karten-Export ist damit
# vollständig unabhängig von der V1-Tabelle `einheiten` (die nur beim Legacy-Update befüllt wird).
# Einheitliches Schema, bs_id = BetriebsStatusId (35/31/37/38) für ALLE Rows.
SELECT_RAW_EXTRA = """
SELECT
    json_extract(raw_json,'$.MaStRNummer'),
    json_extract(raw_json,'$.EinheitName'),
    energietraeger_id,
    json_extract(raw_json,'$.EnergietraegerName'),
    COALESCE(json_extract(raw_json,'$.ArtDerSolaranlageBezeichnung'),
             json_extract(raw_json,'$.WindAnLandOderSeeBezeichnung')),
    CAST(NULL AS REAL),  -- Platzhalter Spalte 5: bruttoleistung_mw wird in Python via to_mw normalisiert
    json_extract(raw_json,'$.BetriebsStatusName'),
    json_extract(raw_json,'$.SystemStatusName'),
    NULLIF(json_extract(raw_json,'$.InbetriebnahmeDatum'),''),
    json_extract(raw_json,'$.Bundesland'),
    json_extract(raw_json,'$.Landkreis'),
    json_extract(raw_json,'$.Gemeinde'),
    json_extract(raw_json,'$.Plz'),
    json_extract(raw_json,'$.Ort'),
    CAST(json_extract(raw_json,'$.Breitengrad') AS REAL),
    CAST(json_extract(raw_json,'$.Laengengrad') AS REAL),
    NULLIF(json_extract(raw_json,'$.NetzbetreiberNamen'),''),
    NULLIF(json_extract(raw_json,'$.AnlagenbetreiberName'),''),
    CAST(json_extract(raw_json,'$.AnzahlSolarModule') AS INTEGER),
    json_extract(raw_json,'$.HauptausrichtungSolarModuleBezeichnung'),
    json_extract(raw_json,'$.SolarparkName'),
    CAST(json_extract(raw_json,'$.NabenhoeheWindenergieanlage') AS REAL),
    CAST(json_extract(raw_json,'$.RotordurchmesserWindenergieanlage') AS REAL),
    CAST(json_extract(raw_json,'$.LichteHoehe') AS REAL),
    json_extract(raw_json,'$.Typenbezeichnung'),
    json_extract(raw_json,'$.HerstellerWindenergieanlageBezeichnung'),
    json_extract(raw_json,'$.WindparkName'),
    json_extract(raw_json,'$.WindAnLandOderSeeBezeichnung'),
    NULLIF(json_extract(raw_json,'$.EinheitRegistrierungsdatum'),''),
    CAST(json_extract(raw_json,'$.BetriebsStatusId') AS INTEGER) AS bs_id,
    CAST(json_extract(raw_json,'$.Bruttoleistung') AS REAL) AS brutto_raw,
    -- F2 (Punkt 2): Spannungsebene(n) via NAP-Join — Pipe-getrennt bei Mehrfach-NAPs
    -- (SQLite: GROUP_CONCAT(DISTINCT x, '|') ist verboten → DISTINCT in Subquery)
    (SELECT GROUP_CONCAT(ebene, '|') FROM (
        SELECT DISTINCT nap.spannungsebene AS ebene
        FROM netzanschlusspunkte nap WHERE nap.lokation_id = er.lokation_id
        AND nap.spannungsebene IS NOT NULL
     )) AS spannungsebene,
    -- F1 (Punkt 1): lokation_id für NAP-Suche (Klick auf NAP-Treffer → alle Anlagen der Lokation)
    er.lokation_id,
    -- V35 (AP1): EEG-Registrierung — EegInbetriebnahmeDatum vorhanden = „unter EEG registriert“.
    -- Definition laut User-Freigabe 10.09.: Mit/Ohne EEG-Registrierung (PV ~95 %, Wind ~81 %).
    CASE WHEN json_extract(er.raw_json,'$.EegInbetriebnahmeDatum') IS NOT NULL THEN 1 ELSE 0 END AS eeg_reg
FROM einheiten_raw er
WHERE json_extract(raw_json,'$.Breitengrad') IS NOT NULL
  AND json_extract(raw_json,'$.Breitengrad') != ''
"""



def build_nap_ranking() -> list[dict]:
    """V28 (Paket 2): NAP-Ranking fuer den Statistik-Tab 'NAP'.

    Pro NAP (typ=0, Wind/PV-Lokationen): angeschlossene Leistung (to_mw-normalisiert),
    Gesellschaften (DISTINCT Betreiber), Bundesland (Mehrheitskonsens der Einheiten),
    Name (netzanschlusspunktbezeichnung, Fallback MaStR-Nr), NB/SE, lat/lon (Mittel).
    Basis: einheiten_raw (118-Felder) — konsistent zum Karten-Export inkl. V27b-Physik-Check.
    """
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from import_mastr import to_mw as _to_mw

    db = sqlite3.connect(DB_PATH)
    rows = db.execute("""
        SELECT nap.nap_mastr_nummer,
               MAX(nap.netzanschlusspunktbezeichnung),
               MAX(nap.netzbetreiber),
               MAX(nap.spannungsebene),
               ROUND(AVG(CAST(json_extract(er.raw_json,'$.Breitengrad') AS REAL)), 6),
               ROUND(AVG(CAST(json_extract(er.raw_json,'$.Laengengrad') AS REAL)), 6),
               er.energietraeger_id,
               json_extract(er.raw_json,'$.Bruttoleistung'),
               json_extract(er.raw_json,'$.Typenbezeichnung'),
               json_extract(er.raw_json,'$.RotordurchmesserWindenergieanlage'),
               json_extract(er.raw_json,'$.AnlagenbetreiberName'),
               json_extract(er.raw_json,'$.Bundesland')
        FROM netzanschlusspunkte nap
        JOIN einheiten_raw er ON er.lokation_id = nap.lokation_id
        WHERE nap.typ = 0
        GROUP BY nap.nap_mastr_nummer, er.mastr_nummer
    """).fetchall()
    db.close()

    agg: dict = {}
    for (nap_m, name, nb, se, lat, lon, et_id, brutto, typ, rd, betreiber, bl) in rows:
        a = agg.setdefault(nap_m, {"nm": None, "mw": 0.0, "g": set(), "bls": {}, "nb": nb, "se": se, "lat": [], "lon": [], "n": 0})
        mw = _to_mw({"Bruttoleistung": brutto, "Typenbezeichnung": typ, "RotordurchmesserWindenergieanlage": rd}, et_id)
        if mw is not None and mw >= 0.1:   # konsistent: <100 kW Wind verworfen; PV alle
            a["mw"] += mw
            a["n"] += 1
        if name and not a["nm"]:
            a["nm"] = name
        if betreiber:
            a["g"].add(betreiber)
        if bl:
            a["bls"][bl] = a["bls"].get(bl, 0) + 1
        if lat is not None:
            a["lat"].append(lat)
        if lon is not None:
            a["lon"].append(lon)

    out = []
    for nap_m, a in agg.items():
        if a["n"] == 0:
            continue
        bl = max(a["bls"].items(), key=lambda kv: kv[1])[0] if a["bls"] else None
        out.append({
            "m": nap_m,
            "nm": a["nm"] or nap_m,
            "mw": round(a["mw"], 1),
            "g": len(a["g"]),
            "bl": bl,
            "nb": a["nb"],
            "se": a["se"],
            "lat": round(sum(a["lat"]) / len(a["lat"]), 6) if a["lat"] else None,
            "lon": round(sum(a["lon"]) / len(a["lon"]), 6) if a["lon"] else None,
        })
    out.sort(key=lambda x: -x["mw"])
    return out

def build_units(rows) -> list[dict]:
    # Spaltenreihenfolge laut SELECT:
    # 0 mastr, 1 name, 2 et_id, 3 et_name, 4 art, 5 mw, 6 status, 7 sysstatus,
    # 8 inb, 9 bundesland, 10 landkreis, 11 gemeinde, 12 plz, 13 ort,
    # 14 lat, 15 lon, 16 netz, 17 ab,
    # 18 anzahl_module, 19 ausr, 20 solarpark,
    # 21 nabenhoehe, 22 rotordurchmesser, 23 lichte, 24 typ, 25 hersteller,
    # 26 windpark, 27 land_oder_see, 28 registrierungsdatum
    # (nur bei F5-Raw-Extra-Rows:) 29 bs_id (BetriebsStatusId), 30 brutto_raw (kW/kWp-Original)
    # 31 spannungsebene (Pipe-getrennt), 32 lokation_id,
    # V35 (AP1): 33 eeg_reg (1 = EEG-Anlage registriert, EegInbetriebnahmeDatum vorhanden)
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
            "reg": r[28],           # registrierungsdatum (YYYY-MM-DD)
        }
        # F2 (Punkt 3): Spannungsebene(n) — Spalte 31, Pipe-getrennt bei Mehrfach-NAPs
        if len(r) > 31 and r[31]:
            u["se"] = r[31]
        # F1 (Punkt 1): lokation_id — Spalte 32, für NAP-Suche (Klick → alle Anlagen der Lokation)
        if len(r) > 32 and r[32] is not None:
            u["lid"] = int(r[32])
        # V35 (AP1): EEG-Registrierung — Spalte 33, nur wenn vorhanden (komprimiert Dateigröße)
        if len(r) > 33 and r[33]:
            u["eeg"] = 1
        # F5: Betriebs-Status-ID nur bei Raw-Extra-Rows (31/37/38) — V1-Rows (35) bekommen kein bs
        if len(r) > 29 and r[29] is not None:
            u["bs"] = int(r[29])
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


def _spannungsebenen_counts(units: list[dict]) -> dict:
    """F2 (Punkt 4): Verteilung der Spannungsebenen über den Export.

    Multi-Ebenen-Anlagen (Pipe-Liste) werden je Ebene 1x gezählt.
    Liefert {ebenenname: anzahl, ...} inkl. 'ohne Angabe' für Anlagen ohne NAP.
    """
    counts: dict[str, int] = {}
    for u in units:
        se = u.get("se")
        if not se:
            counts["ohne Angabe"] = counts.get("ohne Angabe", 0) + 1
            continue
        for ebene in se.split("|"):
            counts[ebene] = counts.get(ebene, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


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

    # Größenklassen je Technologie (feste Staffel, Nutzer-Vorgabe + Recherche Kritis 2026-08-31):
    # → Basis-Leistungsskala [von, bis) in MW / MWp:
    #   0.1·0.5 · 0.5·1 · 1·2 · 2·5 · 5·10 · 10·30 · 30·60 · 60·100 · 100·104 · 104–150 · 150–200
    # KRITIS-Schwelle (recherchiert, BSI-KritisV Anhang 1, Kategorie 1.1.1 Erzeugungsanlage):
    #   Erzeugungsanlagen sind ab 104 MW installierter Nettonennleistung Kritis-relevant.
    #   ⇒ kritis=True gilt NUR für Klassen ab der 104er-Grenze (104–150, 150+); die Klasse 100–104
    #   ist KEINE Kritis (unterhalb der Schwelle). Alle drei Tabs (Wind/PV/Gesamt) nutzen DIESELBE
    #   einheitliche Skala mit der Klassengrenze bei 104 (die frühere 103er-Variante entfällt: sie
    #   lag unterhalb der Schwelle und war ein Irrweg).
    def _staffel():
        return [
            ("0.1–0.5", 0.1, 0.5, False), ("0.5–1", 0.5, 1, False),
            ("1–2", 1, 2, False), ("2–5", 2, 5, False), ("5–10", 5, 10, False),
            ("10–30", 10, 30, False), ("30–60", 30, 60, False), ("60–100", 60, 100, False),
            ("100–104", 100, 104, False),      # UNTERHALB der Kritis-Schwelle → kein Kritis
            ("104–150", 104, 150, True),        # Kritis ≥104 MW
            ("150+", 150, 1e9, True),           # Kritis (Restklasse)
        ]

    klassen = {
        "wind": _staffel(),
        "pv":   _staffel(),
    }
    et_ids = {"wind": 2497, "pv": 2495}
    groessen = {"wind": [], "pv": []}
    maxima = {}

    # V22/V23: Park-Cluster — Splittungs-bereinigte Größenverteilung.
    # Problem: Das MaStR zersplittert große Parks in viele kleine Einheiten
    # (z. B. Solarpark Döllen GmbH = 13 Einheiten à 7,4–31,4 MW = 154,8 MW).
    # Einheiten-Basis ordnet sie in 5–10/10–30/30–60 ein; die Kritis-Schwelle
    # (≥104 MW) wird auf Einheiten-Ebene praktisch nie sichtbar (5 statt 52).
    # Lösung: zusätzlich eine CLUSTER-Basis ausliefern. Cluster-Schlüssel =
    # (Energieträger, Betreiber, Parkname) — Parkname aus solarpark_name /
    # windpark_name, sonst normalisiertes Namens-Präfix (röm./arab. Suffix am
    # Ende wird entfernt: „Döllen II" → „Döllen"); namenlose Einheiten bleiben
    # einzeln. Berechnung HIER (Export-Pipeline) ⇒ automatisch updatefähig.
    # V23: Schlüssel-Logik liegt auf Modulebene (park_key/cluster_key), damit
    # das Einheiten-Export-Mapping (pk/pkmw) dieselben Schlüssel nutzt.

    def _cluster_rows(tech: str):
        """Liefert (cluster_mw-Liste, clusters-Dict keyed by cluster_key)."""
        et = et_ids[tech]
        rows = db.execute(
            "SELECT anlagenbetreiber, einheit_name, bruttoleistung_mw,"
            "       solarpark_name, windpark_name FROM einheiten"
            " WHERE geolokation=1 AND energietraeger_id=?", (et,)).fetchall()
        clusters: dict = {}
        for betreiber, name, mw, sp_name, wp_name in rows:
            park = sp_name if tech == "pv" else wp_name
            key = cluster_key(tech, betreiber, park_key(tech, park, name))
            c = clusters.setdefault(key, {"n": 0, "mw": 0.0})
            c["n"] += 1
            c["mw"] += mw or 0.0
        mws = [c["mw"] for c in clusters.values() if c["mw"]]
        return mws, clusters

    def _verteilung(mws, staffel, total_mw, total_n):
        out = []
        for label, von, bis, kritis in staffel:
            n = sum(1 for v in mws if von <= v < bis)
            s = sum(v for v in mws if von <= v < bis)
            out.append({
                "label": label, "von": von, "bis": bis, "kritis": kritis,
                "anzahl": n, "sum_mw": round(s, 2),
                "anteil_anzahl": round(100.0 * n / total_n, 1) if total_n else 0,
                "anteil_summe": round(100.0 * s / total_mw, 1) if total_mw else 0,
            })
        return out

    for tech, kliste in klassen.items():
        rows = db.execute(
            "SELECT bruttoleistung_mw FROM einheiten WHERE geolokation=1 AND energietraeger_id=?",
            (et_ids[tech],)).fetchall()
        mws = [r[0] for r in rows if r[0] is not None]
        total_mw = sum(mws)
        total_n = len(mws)
        maxima[tech] = round(max(mws), 2) if mws else 0
        for label, von, bis, kritis in kliste:
            n = sum(1 for v in mws if von <= v < bis)
            s = sum(v for v in mws if von <= v < bis)
            # Klassen IMMER listen (auch n=0), damit Kritis-Schwellen sichtbar bleiben
            groessen[tech].append({
                "label": label, "von": von, "bis": bis, "kritis": kritis,
                "anzahl": n, "sum_mw": round(s, 2),
                "anteil_anzahl": round(100.0 * n / total_n, 1) if total_n else 0,
                "anteil_summe": round(100.0 * s / total_mw, 1) if total_mw else 0,
            })

    # Gemeinsames Diagramm (Wind + PV zusammen) über dieselbe Klassenskala.
    all_rows = db.execute(
        "SELECT bruttoleistung_mw FROM einheiten WHERE geolokation=1"
    ).fetchall()
    all_mws = [r[0] for r in all_rows if r[0] is not None]
    all_total_mw = sum(all_mws)
    all_total_n = len(all_mws)
    gesamt_klassen = []
    for label, von, bis, kritis in _staffel():
        n = sum(1 for v in all_mws if von <= v < bis)
        s = sum(v for v in all_mws if von <= v < bis)
        gesamt_klassen.append({
            "label": label, "von": von, "bis": bis, "kritis": kritis,
            "anzahl": n, "sum_mw": round(s, 2),
            "anteil_anzahl": round(100.0 * n / all_total_n, 1) if all_total_n else 0,
            "anteil_summe": round(100.0 * s / all_total_mw, 1) if all_total_mw else 0,
        })
    groessen["gesamt"] = gesamt_klassen

    # V22: Cluster-Basis je Tech + gesamt (aggregiert über Park-Schlüssel).
    # Struktur: groessen_cluster[tech] = Verteilung der CLUSTER-Größen (Summe MW
    # je Park) über dieselbe Staffel. „anzahl" = Anzahl Parks, „sum_mw" = deren
    # gemeinsame Leistung. Namenlose Einheiten bleiben Einzel-Cluster.
    groessen_cluster = {"wind": [], "pv": []}
    cluster_stats = {}
    for tech in ("wind", "pv"):
        kliste = klassen[tech]
        mws_c, clusters = _cluster_rows(tech)
        total_mw_c = sum(mws_c)
        total_n_c = len(mws_c)
        cluster_stats[tech] = {
            "n_cluster": len(clusters),
            "n_multi": sum(1 for c in clusters.values() if c["n"] > 1),
            "max_mw": round(max(mws_c), 2) if mws_c else 0,
        }
        groessen_cluster[tech] = _verteilung(mws_c, kliste, total_mw_c, total_n_c)

    # gesamt = Wind- und PV-Cluster gemischt → Schlüssel müssen getrennt bleiben
    # (gleicher Betreiber + gleicher Parkname über ET hinweg wäre Zufall, nicht
    # derselbe Park). Daher: beide Listen konkatenieren (Wind-Cluster + PV-Cluster).
    all_cluster_mws = []
    for tech in ("wind", "pv"):
        mws_c, _clusters = _cluster_rows(tech)
        all_cluster_mws.extend(mws_c)
    groessen_cluster["gesamt"] = _verteilung(
        all_cluster_mws, _staffel(), sum(all_cluster_mws), len(all_cluster_mws))

    # V23 (Paket 4): Landkreis-/Gemeinde-Statistik inkl. NAP-Join.
    # Basis: einheiten (georef, alle Status) — identisch zur Betreiber-Statistik.
    # NAPs: netzanschlusspunkte via lokation_id; NAP-MW = Nettoengpassleistung
    # (NAP-Kapazität, NICHT Anlagenleistung — Begriff im Tab dokumentieren).
    lk_stat: dict = {}
    for lk, et_id, mw, lid in db.execute(
            "SELECT landkreis, energietraeger_id, bruttoleistung_mw, lokation_nr "
            "FROM einheiten WHERE geolokation=1 AND landkreis IS NOT NULL AND landkreis!=''").fetchall():
        s = lk_stat.setdefault(lk, {"n": 0, "mw": 0.0, "n_pv": 0, "mw_pv": 0.0, "n_wind": 0, "mw_wind": 0.0})
        s["n"] += 1
        s["mw"] += mw or 0.0
        if et_id == 2495:
            s["n_pv"] += 1; s["mw_pv"] += mw or 0.0
        else:
            s["n_wind"] += 1; s["mw_wind"] += mw or 0.0

    # LK → NAPs: Join über einheiten_raw.lokation_id (numerische LokationId — die V1-Tabelle
    # speichert nur lokation_nr als SEL-String ohne ID). NAP-Menge = NAPs, deren lokation_id
    # zu einer georef-Einheit im LK gehört (Landkreis direkt aus dem 118-Feld-JSON).
    nap_lk: dict = {}
    for lk, n_nap, mw in db.execute("""
            SELECT json_extract(er.raw_json,'$.Landkreis') AS lk,
                   COUNT(DISTINCT n.nap_mastr_nummer),
                   SUM(n.nettoengpassleistung_mw)
            FROM netzanschlusspunkte n
            JOIN einheiten_raw er ON er.lokation_id = n.lokation_id
            WHERE json_extract(er.raw_json,'$.Breitengrad') IS NOT NULL
              AND json_extract(er.raw_json,'$.Breitengrad') != ''
              AND json_extract(er.raw_json,'$.Landkreis') IS NOT NULL
              AND json_extract(er.raw_json,'$.Landkreis') != ''
            GROUP BY lk""").fetchall():
        nap_lk[lk] = {"n": n_nap, "mw": mw or 0.0}

    landkreise = []
    for lk, s in lk_stat.items():
        ninfo = nap_lk.get(lk, {"n": 0, "mw": 0.0})
        landkreise.append({
            "lk": lk, "n": s["n"], "mw": round(s["mw"], 1),
            "n_pv": s["n_pv"], "mw_pv": round(s["mw_pv"], 1),
            "n_wind": s["n_wind"], "mw_wind": round(s["mw_wind"], 1),
            "n_nap": ninfo["n"], "mw_nap": round(ninfo["mw"], 1),
        })
    landkreise.sort(key=lambda x: -x["mw"])

    gemeinden = []
    g_stat: dict = {}
    for g, lk, b, et_id, mw in db.execute(
            "SELECT gemeinde, landkreis, bundesland, energietraeger_id, bruttoleistung_mw "
            "FROM einheiten WHERE geolokation=1 AND gemeinde IS NOT NULL AND gemeinde!=''").fetchall():
        s = g_stat.setdefault((g, lk, b), {"n": 0, "mw": 0.0, "n_pv": 0, "mw_pv": 0.0, "n_wind": 0, "mw_wind": 0.0})
        s["n"] += 1; s["mw"] += mw or 0.0
        if et_id == 2495: s["n_pv"] += 1; s["mw_pv"] += mw or 0.0
        else: s["n_wind"] += 1; s["mw_wind"] += mw or 0.0
    for (g, lk, b), s in g_stat.items():
        gemeinden.append({
            "g": g, "lk": lk, "b": b, "n": s["n"], "mw": round(s["mw"], 1),
            "n_pv": s["n_pv"], "mw_pv": round(s["mw_pv"], 1),
            "n_wind": s["n_wind"], "mw_wind": round(s["mw_wind"], 1),
        })
    gemeinden.sort(key=lambda x: -x["n"])

    totals = {
        "wind_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2497").fetchone()[0],
        "pv_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1 AND energietraeger_id=2495").fetchone()[0],
        "herstellbar_wind": sum(x["anzahl"] for x in hersteller_list),
        "total_anzahl": db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1").fetchone()[0],
        "wind_max_mw": maxima["wind"],
        "pv_max_mw": maxima["pv"],
        # V22: Cluster-Kennzahlen für Summary-Box
        "wind_cluster": cluster_stats["wind"]["n_cluster"],
        "pv_cluster": cluster_stats["pv"]["n_cluster"],
        "wind_cluster_max_mw": cluster_stats["wind"]["max_mw"],
        "pv_cluster_max_mw": cluster_stats["pv"]["max_mw"],
    }

    return {
        "betreiber": betreiber_list,
        "hersteller": hersteller_list,
        "groessenklassen": groessen,
        "groessen_cluster": groessen_cluster,
        "landkreise": landkreise,
        "gemeinden": gemeinden,
        "gesamt": totals,
    }


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(SELECT + " ORDER BY energietraeger_id, mastr_nummer").fetchall()

    # F5: Zusatz-Status aus einheiten_raw anhängen (bruttoleistung_mw via to_mw-Logik
    # hier normalisiert: Wind kW/MW-Heuristik, PV /1000 — identisch zu import_mastr.to_mw)
    sys.path.insert(0, str(ROOT / "scripts"))
    from import_mastr import to_mw, normalize_typ  # V37: Typen-Normalisierung (User-AP1)
    raw_rows = db.execute(SELECT_RAW_EXTRA).fetchall()
    db.close()
    extra_rows = []
    for r in raw_rows:
        r_list = list(r)
        et_id = r_list[2]
        # V37 (11.09.2026, User-AP1): Typenbezeichnung via Majority-Vote-Mapping
        # normalisieren (E40→E-40 etc.) — WIND-only (User-Entscheid). Vor to_mw,
        # damit die 15-MW-Ausnahme ('15mw' im Typ) den normalisierten Typ sieht.
        if et_id == 2497:
            r_list[24] = normalize_typ(r_list[24])
        # V27-Fix (06.09.2026): Rotordurchmesser MITGEBEN — to_mw-Physik-Check (RD<60 & >=1,5 MW
        # => kW-Falschangabe) braucht das Feld, sonst bleiben Kleinwindräder als "1,5 MW" … "80 MW".
        brutto = to_mw({
            "Bruttoleistung": r_list[30],
            "Typenbezeichnung": r_list[24],
            "RotordurchmesserWindenergieanlage": r_list[22],
        }, et_id)
        # Wind <100 kW nach Normalisierung verwerfen (konsistent zum Kern-Filter)
        if et_id == 2497 and (brutto is None or brutto < 0.1):
            continue
        r_list[5] = brutto
        extra_rows.append(tuple(r_list))

    units_raw = build_units(extra_rows)
    # Status-35-Rows bekommen das bs-Feld ebenfalls (uniform: bs=35)
    for u in units_raw:
        u.setdefault("bs", 35)
    # V30 F04 (Variante B, 08.09.2026): Abgrenzung strikt durchsetzen — PV >= 0.5 MWp,
    # Wind >= 0.1 MW (nach to_mw-Normalisierung). Fängt API-Grenzfälle (499.9x kWp > fetch-
    # Filter 499.9) ab, selbst wenn ein künftiger Fetch-Filter wieder laxer wäre.
    _before = len(units_raw)
    units_raw = [u for u in units_raw
                 if (u["t"] == "pv" and (u["mw"] or 0) >= 0.5)
                 or (u["t"] == "wind" and (u["mw"] or 0) >= 0.1)]
    if _before != len(units_raw):
        print(f"  V30 F04 Abgrenzungs-Filter: {_before - len(units_raw)} Einheiten < Schwelle verworfen")
    units = units_raw

    # V23 (Paket 8): unit→Park-Mapping für den park-aggregierten Leistungsfilter.
    # Für jede Einheit mit Mehrfach-Park (Cluster n>=2): pk = Cluster-Hash (kurz),
    # pkmw = Park-Gesamtleistung MW. Einheiten ohne Mehrfach-Park bleiben ohne Feld
    # (Filter fällt auf u.mw zurück) → Dateigröße bleibt ~konstant.
    # Updatefähigkeit: läuft in jedem Export-Lauf automatisch mit.
    park_sums: dict = {}
    for u in units:
        tech = u["t"]
        park_field = u.get("park") if tech == "pv" else u.get("wp")
        ck = cluster_key(tech, u.get("ab"), park_key(tech, park_field, u.get("n")))
        u["_ck"] = ck
        s = park_sums.setdefault(ck, {"n": 0, "mw": 0.0})
        s["n"] += 1
        s["mw"] += u.get("mw") or 0.0
    for u in units:
        ck = u.pop("_ck")
        s = park_sums[ck]
        if s["n"] >= 2:
            u["pk"] = ck
            u["pkmw"] = round(s["mw"], 2)

    # Metadaten + Zähler
    db = sqlite3.connect(DB_PATH)
    stand = (db.execute("SELECT value FROM metadaten WHERE key='stand'").fetchone() or (None,))[0]
    # V30 F04 (Variante B): counts aus dem EXPORT selbst zählen (identische Basis wie
    # einheiten.json) statt aus der Legacy-V1-Tabelle — eliminates Drift F-04 dauerhaft.
    # Infobar-Semantik: NUR In-Betrieb (bs 35) — Planung/Stillegungen zählen nicht.
    counts = {}
    for u in units:
        if (u.get("bs") or 35) != 35:
            continue
        et_name = "Wind" if u["t"] == "wind" else "Solare Strahlungsenergie"
        counts[et_name] = counts.get(et_name, 0) + 1
    db.close()

    meta = {
        "stand": stand or datetime.now().isoformat(timespec="seconds"),
        "quelle": "Marktstammdatenregister (BNetzA)",
        "abgrenzung": "Wind >= 100 kW und PV >= 0.5 MWp, Status 'In Betrieb' (weitere Status optional filterbar), nur Anlagen mit vorhandener Geolokation",
        "counts": counts,
        "total_geolokation": len(units),
        # F5: Status-Zähler (nur georeferenzierte Einheiten im Export, einheitlich bs-Feld)
        "status_counts": {
            "35_in_betrieb": sum(1 for u in units if u.get("bs") == 35),
            "31_in_planung": sum(1 for u in units if u.get("bs") == 31),
            "37_voruebergehend_stillgelegt": sum(1 for u in units if u.get("bs") == 37),
            "38_endgueltig_stillgelegt": sum(1 for u in units if u.get("bs") == 38),
        },
        # F2 (Punkt 4): Spannungsebenen-Verteilung (Pipe-Multi-Ebenen je 1x gezählt)
        "spannungsebenen": _spannungsebenen_counts(units),
    }

    # Statistik-Panel
    db = sqlite3.connect(DB_PATH)
    statistiken = build_statistiken(db)

    with open(DIST / "einheiten.json", "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False)
    with open(DIST / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    with open(DIST / "statistiken.json", "w", encoding="utf-8") as f:
        json.dump(statistiken, f, ensure_ascii=False)
    # V28 (Paket 2): NAP-Ranking fuer den neuen Statistik-Tab "NAP"
    nap_ranking = build_nap_ranking()
    with open(DIST / "nap_ranking.json", "w", encoding="utf-8") as f:
        json.dump(nap_ranking, f, ensure_ascii=False)
    print(f"NAP-Ranking: {len(nap_ranking)} NAPs -> dist/assets/nap_ranking.json")
    size = (DIST / "einheiten.json").stat().st_size / 1024 / 1024
    print(f"Export: {len(units)} Anlagen -> dist/assets/einheiten.json ({size:.1f} MB)")
    print("Metadaten -> dist/assets/meta.json")
    print(f"Zähler: {counts}")
    stat_et = statistiken["gesamt"]
    print(f"Statistik: {len(statistiken['betreiber'])} Betreiber | Wind max {stat_et['wind_max_mw']} MW | PV max {stat_et['pv_max_mw']} MW | gesamt {stat_et['total_anzahl']} -> dist/assets/statistiken.json")

    # V4: Historie-JSON generieren (falls Snapshots existieren)
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from snapshot import build_historie, ensure_schema
        ensure_schema(db)
        historie = build_historie(db)
        if historie:
            with open(DIST / "historie.json", "w", encoding="utf-8") as f:
                json.dump(historie, f, ensure_ascii=False, indent=2)
            print(f"Historie: {len(historie)} Snapshots -> dist/assets/historie.json")
        else:
            print("Historie: keine Snapshots vorhanden (erst nach Update mit import_mastr.py)")
    except Exception as e:
        print(f"Historie: übersprungen ({e})")
    finally:
        try:
            db.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
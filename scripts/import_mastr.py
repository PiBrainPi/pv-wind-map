#!/usr/bin/env python3
"""
import_mastr.py — Importiert die Roh-JSONs (data/raw/*.json) in die lokale SQLite-Datenbank.

Schema (Single Source of Truth):
  Tabelle `einheiten`:   eine Zeile je MaStR-Anlage (Wind + PV), normalisierte Felder
  Tabelle `metadaten`:   Abrufzeitpunkt, Quelle
  Tabelle `update_log`:  Historie der Importe

Normalisierung:
  - Bruttoleistung: PV wird vom MaStR in kWp geliefert -> in MW umgerechnet (/1000);
    Wind liegt in MW vor. Beide liegen danach einheitlich in MW vor.
  - MaStR-Nummern: String, eindeutig (unique).
  - Datumsfelder "/Date(millis)/" -> ISO 8601 (YYYY-MM-DD).
  - Koordinaten: NULL behalten; geolokation=1 nur wenn lat UND lon vorhanden.

Nutzung: python3 scripts/import_mastr.py
"""
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "mastr.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS einheiten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mastr_nummer TEXT UNIQUE,
    einheit_name TEXT,
    energietraeger_id INTEGER,
    energietraeger_name TEXT,
    art TEXT,
    bruttoleistung_mw REAL,
    betriebs_status TEXT,
    system_status TEXT,
    inbetriebnahme_datum TEXT,
    eeg_inbetriebnahme_datum TEXT,
    letzte_aktualisierung TEXT,
    bundesland TEXT,
    landkreis TEXT,
    gemeinde TEXT,
    plz TEXT,
    ort TEXT,
    strasse TEXT,
    lat REAL,
    lon REAL,
    geolokation INTEGER DEFAULT 0,
    netzbetreiber TEXT,
    anlagenbetreiber TEXT,
    -- PV-spezifisch
    anzahl_solar_module INTEGER,
    hauptausrichtung TEXT,
    solarpark_name TEXT,
    -- Wind-spezifisch
    nabenhoehe_m REAL,
    rotordurchmesser_m REAL,
    lichte_hoehe_m REAL,
    typenbezeichnung TEXT,
    hersteller TEXT,
    windpark_name TEXT,
    land_oder_see TEXT,
    lokation_nr TEXT,
    registrierungsdatum TEXT
);
CREATE TABLE IF NOT EXISTS metadaten (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pv_count INTEGER,
    wind_count INTEGER,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_et ON einheiten(energietraeger_id);
CREATE INDEX IF NOT EXISTS idx_geolok ON einheiten(geolokation);
CREATE INDEX IF NOT EXISTS idx_bundesland ON einheiten(bundesland);
CREATE INDEX IF NOT EXISTS idx_gemeinde ON einheiten(gemeinde);
CREATE INDEX IF NOT EXISTS idx_status ON einheiten(betriebs_status);
"""

INSERT_COLS = (
    "mastr_nummer, einheit_name, energietraeger_id, energietraeger_name, art, "
    "bruttoleistung_mw, betriebs_status, system_status, "
    "inbetriebnahme_datum, eeg_inbetriebnahme_datum, letzte_aktualisierung, "
    "bundesland, landkreis, gemeinde, plz, ort, strasse, "
    "lat, lon, geolokation, "
    "netzbetreiber, anlagenbetreiber, "
    "anzahl_solar_module, hauptausrichtung, solarpark_name, "
    "nabenhoehe_m, rotordurchmesser_m, lichte_hoehe_m, typenbezeichnung, hersteller, "
    "windpark_name, land_oder_see, lokation_nr, registrierungsdatum"
)


def parse_date(val) -> str | None:
    if not val or not isinstance(val, str):
        return None
    m = re.search(r"Date\((\d+)\)", val)
    if m:
        try:
            return datetime.utcfromtimestamp(int(m.group(1)) / 1000).strftime("%Y-%m-%d")
        except Exception:
            return None
    return val


def as_float(r, key):
    v = r.get(key)
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def to_mw(r, et_id: int) -> float | None:
    """Normalisiert die Bruttoleistung auf MW.

    MaStR-Einheiten sind inkonsistent (empirisch verifiziert an den Rohdaten):
      - PV:   Bruttoleistung in kWp   -> durch 1000 (z. B. 1617 = 1.6 MWp)
      - Wind: Mischung! Moderne Anlagen wie V236-15MW (=15000), SWT-6.0-154
              (=6300), E-126 (=7580) werden in kW geliefert; kleine Anlagen
              (500..1000 kW) ebenfalls kW. Nur sehr wenige Einträge liegen
              bereits in MW vor (z. B. 3.0, 4.5, 2.3).
      Heuristik: Wert > 80 -> kW (durch 1000); Wert <= 80 -> MW (bereits).
      Begründung Schwellwert 80: reale Einzel-WEA (>= 100 kW) haben kW-Werte
      zwischen ~80 und 15000 (also >80) ODER als MW-Werte zwischen 1 und ~16
      (also <= 80 trennt nicht eindeutig, da 1..16 <= 80). Werte 81-99 sind
      kW-Kleinstanlagen (= 0.08..0.099 MW). Mikro-Windanlagen unter 80 (z. B.
      0.5 = 0.5 kW, 0.6 = 0.6 kW) werden als MW missverstanden, sind aber per
      Schwellwert-Anforderung >= 100 kW ohnehin auszuschliessen.
    """
    v = as_float(r, "Bruttoleistung")
    if v is None:
        return None
    if et_id == 2495:             # PV: kWp -> MW
        return round(v / 1000.0, 4)
    # Wind: Mischung kW/MW. Wert > 80 -> kW, sonst MW (siehe Docstring).
    if v > 80:
        return round(v / 1000.0, 4)   # kW -> MW
    return round(v, 4)               # bereits MW


def make_row(r: dict, et_id: int, et_name: str):
    lat = as_float(r, "Breitengrad")
    lon = as_float(r, "Laengengrad")
    geolok = 1 if (lat is not None and lon is not None) else 0
    dirty_netz = r.get("NetzbetreiberNamen")
    netz = re.sub(r"<[^>]+>", "", dirty_netz).strip() if dirty_netz else None
    art = r.get("ArtDerSolaranlageBezeichnung") or r.get("WindAnLandOderSeeBezeichnung") or None
    return (
        r.get("MaStRNummer"), r.get("EinheitName"), et_id, et_name, art,
        to_mw(r, et_id),
        r.get("BetriebsStatusName"), r.get("SystemStatusName"),
        parse_date(r.get("InbetriebnahmeDatum")), parse_date(r.get("EegInbetriebnahmeDatum")),
        parse_date(r.get("DatumLetzteAktualisierung")),
        r.get("Bundesland"), r.get("Landkreis"), r.get("Gemeinde"), r.get("Plz"),
        r.get("Ort"), r.get("Strasse"),
        lat, lon, geolok,
        netz, r.get("AnlagenbetreiberName"),
        as_float(r, "AnzahlSolarModule"),
        r.get("HauptausrichtungSolarModuleBezeichnung"),
        r.get("SolarparkName"),
        as_float(r, "NabenhoeheWindenergieanlage"),
        as_float(r, "RotordurchmesserWindenergieanlage"),
        as_float(r, "LichteHoehe"),
        r.get("Typenbezeichnung"),
        r.get("HerstellerWindenergieanlageBezeichnung"),
        r.get("WindparkName"),
        r.get("WindAnLandOderSeeBezeichnung"),
        r.get("LokationMastrNr"),
        parse_date(r.get("EinheitRegistrierungsdatum")),
    )


def main() -> None:
    if not (RAW_DIR / "pv.json").exists() or not (RAW_DIR / "wind.json").exists():
        print("FEHLER: data/raw/pv.json und wind.json fehlen. Erst scripts/fetch_mastr.py ausführen.", file=sys.stderr)
        sys.exit(1)

    with open(RAW_DIR / "pv.json", encoding="utf-8") as f:
        pv = json.load(f)
    with open(RAW_DIR / "wind.json", encoding="utf-8") as f:
        wind = json.load(f)

    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    # Rebuild (robust für V0)
    db.execute("DELETE FROM einheiten")
    db.execute("DELETE FROM update_log")

    ncols = len([c for c in INSERT_COLS.split(",") if c.strip()])
    placeholders = ",".join("?" * ncols)
    psql = f"INSERT OR REPLACE INTO einheiten ({INSERT_COLS}) VALUES ({placeholders})"

    pv_inserted = 0
    wind_inserted = 0
    wind_filtered_lt100kw = 0
    for r in pv:
        db.execute(psql, make_row(r, 2495, "Solare Strahlungsenergie"))
        pv_inserted += 1
    for r in wind:
        mw = to_mw(r, 2497)
        # Anforderung: Wind >= 100 kW (= >= 0.1 MW) nach Einheiten-Normalisierung.
        # durch die gemischten kW/MW-Werte müssen wir hier nachfiltern.
        if mw is not None and mw < 0.1:
            wind_filtered_lt100kw += 1
            continue
        db.execute(psql, make_row(r, 2497, "Wind"))
        wind_inserted += 1

    now = datetime.now().isoformat(timespec="seconds")
    db.execute("INSERT OR REPLACE INTO metadaten VALUES (?,?)", ("stand", now))
    db.execute("INSERT OR REPLACE INTO metadaten VALUES (?,?)", ("quelle", "Marktstammdatenregister (BNetzA), öffentlich"))
    db.execute("INSERT OR REPLACE INTO metadaten VALUES (?,?)", ("einheiten_pv", str(pv_inserted)))
    db.execute("INSERT OR REPLACE INTO metadaten VALUES (?,?)", ("einheiten_wind", str(wind_inserted)))
    db.execute("INSERT INTO update_log (timestamp,pv_count,wind_count,notes) VALUES (?,?,?,?)",
               (now, pv_inserted, wind_inserted, f"Initialimport (Wind <100kW gefiltert: {wind_filtered_lt100kw})"))

    db.commit()
    rows = db.execute("SELECT energietraeger_name, COUNT(*) FROM einheiten GROUP BY energietraeger_name").fetchall()
    geolok = db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1").fetchone()[0]
    print("Import abgeschlossen. In Datenbank:")
    for name, cnt in rows:
        print(f"  {name}: {cnt}")
    print(f"  davon mit Geolokation: {geolok}")
    print(f"  Wind (<100 kW, = <0.1 MW, nach Normalisierung weggefiltert): {wind_filtered_lt100kw}")
    db.close()


if __name__ == "__main__":
    main()
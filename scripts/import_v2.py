#!/usr/bin/env python3
"""
import_v2.py — Schema 2.0: vollständige Rohdaten + NAP in data/mastr.db (Regel 2, Freigabe 03.09.).

NEU (neben den bestehenden Tabellen aus import_mastr.py, die UNBERÜHRT bleiben):
  einheiten_raw         — 1:1-Rohdatensatz (alle API-Felder als JSON) + Kern-Indexspalten
  netzanschlusspunkte   — NAP je Lokation (aus data/nap/netzanschlusspunkte.jsonl)
  nap_fetch_log         — Cache-Log von fetch_nap.py (wird hier nur geprüft/angelegt)

Regeln (Grundsatzentscheidung):
  - NICHTS löschen: bestehende Tabellen (einheiten, snapshots, snapshot_einheiten,
    update_log, metadaten) bleiben unangetastet. einheiten_raw wird per UPSERT befüllt.
  - Backup-Pflicht: vor jedem Lauf Kopie der DB nach ~/backups/ (wenn DB existiert & >0 Einheiten).
  - Inkrementell (P4): einheiten_raw kennt DatumLetzteAktualisierung je Record; nur neue/
    geänderte Records werden upgedatet (UPDATE per mastr_nummer).

Nutzung: python3 scripts/import_v2.py [--skip-backup]
"""
import argparse
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw_v2"
NAP_FILE = ROOT / "data" / "nap" / "netzanschlusspunkte.jsonl"
DB_PATH = ROOT / "data" / "mastr.db"
BACKUP_DIR = Path.home() / "backups"

SCHEMA_V2 = """
CREATE TABLE IF NOT EXISTS einheiten_raw (
    mastr_nummer TEXT PRIMARY KEY,
    energietraeger_id INTEGER NOT NULL,
    lokation_id INTEGER,
    datum_letzte_aktualisierung TEXT,
    raw_json TEXT NOT NULL,
    importiert_am TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_raw_et ON einheiten_raw(energietraeger_id);
CREATE INDEX IF NOT EXISTS idx_raw_lok ON einheiten_raw(lokation_id);
CREATE INDEX IF NOT EXISTS idx_raw_upd ON einheiten_raw(datum_letzte_aktualisierung);

CREATE TABLE IF NOT EXISTS netzanschlusspunkte (
    nap_mastr_nummer TEXT PRIMARY KEY,
    lokation_id INTEGER NOT NULL,
    messlokation TEXT,
    spannungsebene TEXT,
    regelzone TEXT,
    bilanzierungsgebiet TEXT,
    netzbetreiber TEXT,
    netzanschlusspunktbezeichnung TEXT,
    nettoengpassleistung_mw REAL,
    anschlusspunktkapazitaet REAL,
    marktgebiet TEXT,
    gasqualitaet TEXT,
    typ INTEGER,
    registrierungsdatum TEXT,
    aktualisierungsdatum TEXT,
    raw_json TEXT NOT NULL,
    importiert_am TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nap_lok ON netzanschlusspunkte(lokation_id);
"""


def parse_ms_date(val) -> str | None:
    if not val or not isinstance(val, str):
        return None
    m = re.search(r"Date\((\d+)\)", val)
    if m:
        try:
            return datetime.utcfromtimestamp(int(m.group(1)) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    return val


def backup_db() -> Path | None:
    if not DB_PATH.exists():
        return None
    db = sqlite3.connect(DB_PATH)
    n = db.execute("SELECT COUNT(*) FROM einheiten").fetchone()[0]
    db.close()
    if n == 0:
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"mastr_{stamp}.db"
    shutil.copy2(DB_PATH, dest)
    print(f"DB-Backup: {dest} ({dest.stat().st_size/1e6:.1f} MB)")
    return dest


def upsert_raw(db, records: list[dict], et_id: int) -> tuple[int, int]:
    """UPSERT: neue Records einfügen, geänderte (neuere DatumLetzteAktualisierung) updaten.

    F5-Erweiterung: Der UPSERT-Streitpunkt ist (neuere DatumLetzteAktualisierung) ODER
    abweichender BetriebsStatus — ein Anlagen-Statuswechsel (z. B. In Planung -> In Betrieb)
    MUSS im Datensatz ankommen, auch wenn das Aktualisierungsdatum gleich alt ist.
    """
    now = datetime.now().isoformat(timespec="seconds")
    new = upd = 0
    for r in records:
        mn = r.get("MaStRNummer")
        if not mn:
            continue
        upd_date = parse_ms_date(r.get("DatumLetzteAktualisierung"))
        row = db.execute(
            "SELECT datum_letzte_aktualisierung, json_extract(raw_json,'$.BetriebsStatusId') FROM einheiten_raw WHERE mastr_nummer=?",
            (mn,),
        ).fetchone()
        raw_json = json.dumps(r, ensure_ascii=False)
        if row is None:
            db.execute(
                "INSERT INTO einheiten_raw VALUES (?,?,?,?,?,?)",
                (mn, et_id, r.get("LokationId"), upd_date, raw_json, now),
            )
            new += 1
        elif (upd_date or "") > (row[0] or "") or str(r.get("BetriebsStatusId")) != str(row[1]):
            db.execute(
                """UPDATE einheiten_raw SET raw_json=?, datum_letzte_aktualisierung=?,
                   lokation_id=?, importiert_am=? WHERE mastr_nummer=?""",
                (raw_json, upd_date, r.get("LokationId"), now, mn),
            )
            upd += 1
    return new, upd


def import_naps(db) -> tuple[int, int]:
    """NAP-JSONL einlesen (append-only Quelle) und per UPSERT in Tabelle schreiben."""
    if not NAP_FILE.exists():
        print("NAP: keine Datei (fetch_nap.py noch nicht gelaufen) — übersprungen.")
        return 0, 0
    now = datetime.now().isoformat(timespec="seconds")
    seen_loc: set[int] = set()
    nap_new = nap_upd = 0
    with open(NAP_FILE, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            lid = doc["lokation_id"]
            if lid in seen_loc:
                continue  # JSONL kann Retries enthalten — letzter Wert gewinnt nicht, erster reicht
            seen_loc.add(lid)
            for n in doc.get("naps") or []:
                key = n.get("MastrNr") or f"LOK{lid}-ID{n.get('Id')}"
                exists = db.execute(
                    "SELECT 1 FROM netzanschlusspunkte WHERE nap_mastr_nummer=?", (key,)
                ).fetchone()
                db.execute(
                    """INSERT OR REPLACE INTO netzanschlusspunkte VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        key, lid, n.get("Messlokation"), n.get("SpannungsebeneName"),
                        n.get("RegelzonenName"), n.get("BilanzierungsgebietName"),
                        n.get("NetzbetreiberFullName"), n.get("Netzanschlusspunktbezeichnung"),
                        n.get("Nettoengpassleistung"), n.get("Netzanschlusspunktkapazitaet"),
                        n.get("MarktgebietName"), n.get("GasqualitaetName"), n.get("Typ"),
                        parse_ms_date(n.get("Registrierungsdatum")),
                        parse_ms_date(n.get("Aktualisierungsdatum")),
                        json.dumps(n, ensure_ascii=False), now,
                    ),
                )
                if exists:
                    nap_upd += 1
                else:
                    nap_new += 1
    return nap_new, nap_upd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-backup", action="store_true", help="Backup überspringen (nur für Tests)")
    args = ap.parse_args()

    for name in ("wind.json", "pv.json"):
        if not (RAW_DIR / name).exists():
            print(f"FEHLER: {RAW_DIR/name} fehlt. Erst scripts/fetch_v2.py ausführen.", file=sys.stderr)
            sys.exit(1)

    if not args.skip_backup:
        backup_db()

    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA_V2)

    stats = {}
    for name, et in (("pv.json", 2495), ("wind.json", 2497)):
        with open(RAW_DIR / name, encoding="utf-8") as f:
            records = json.load(f)
        new, upd = upsert_raw(db, records, et)
        stats[name] = (len(records), new, upd)
        print(f"{name}: {len(records)} Records | neu {new} | aktualisiert {upd}")

    # F5: Zusatz-Status (In Planung 31, Voruebergehend stillgelegt 37, Endgueltig stillgelegt 38)
    # in die GLEICHE Tabelle upserten — eine MaStR-Nummer hat immer GENAU einen aktuellen Status.
    for status_id in (31, 37, 38):
        for tech, et in (("wind", 2497), ("pv", 2495)):
            name = f"{tech}_status{status_id}.json"
            p = RAW_DIR / name
            if not p.exists():
                print(f"{name}: (nicht vorhanden — übersprungen)")
                continue
            with open(p, encoding="utf-8") as f:
                records = json.load(f)
            new, upd = upsert_raw(db, records, et)
            stats[name] = (len(records), new, upd)
            print(f"{name}: {len(records)} Records | neu {new} | aktualisiert {upd}")

    nap_new, nap_upd = import_naps(db)
    print(f"NAP: {nap_new} neu, {nap_upd} aktualisiert")

    db.execute(
        "INSERT OR REPLACE INTO metadaten VALUES ('schema_version','2.0')"
    )
    db.execute(
        "INSERT OR REPLACE INTO metadaten VALUES ('raw_import_stand', ?)",
        (datetime.now().isoformat(timespec="seconds"),),
    )
    db.commit()

    # Abschlussbericht
    print("\n=== DB-Zusammenfassung ===")
    for t in ("einheiten", "einheiten_raw", "netzanschlusspunkte", "snapshots", "snapshot_einheiten"):
        try:
            print(f"  {t}: {db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} Zeilen")
        except sqlite3.OperationalError:
            print(f"  {t}: (nicht vorhanden)")
    geolok = db.execute("SELECT COUNT(*) FROM einheiten WHERE geolokation=1").fetchone()[0]
    print(f"  einheiten georef: {geolok}")
    db.close()


if __name__ == "__main__":
    main()

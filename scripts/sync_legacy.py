#!/usr/bin/env python3
"""sync_legacy.py (V43.2) — Synchronisiert die Legacy-Tabelle `einheiten` inkrementell
aus einheiten_raw, NUR mit den In-Betrieb-Anlagen (BetriebsStatusId 35).

Zweck (User-Freigabe 12.09., V43.2):
- statistiken.json (Charts) + Snapshot-/Historie-Logik basieren auf `einheiten` — die
  Tabelle wurde bisher NUR vom Legacy-Rebuild (import_mastr.py, Full-Reset aus data/raw/,
  Basis-Filter Status 35) befüllt und driftete vom cron-gepflegten `einheiten_raw` weg
  (Befund V43.1 Punkt 3). Der Cron lief nie Snapshots → keine Delta-Punkte in der
  Update-Historie.

SEMANTIK (bewusst eng an der bisherigen Snapshot-Basis, dokumentiert):
- Sync-Basis = einheiten_raw mit BetriebsStatusId=35 (In Betrieb), georef,
  Grenzwerte wie gehabt: Wind >= 0.1 MW, PV >= 0.5 MWp (nach to_mw).
- Damit bleiben Snapshot-Reihe, Historie-Charts und statistiken.json auf der BEKANNTEN
  In-Betrieb-Basis (53.413-Stand-Linie) — keine künstlichen Basis-Sprünge.
- Verwaiste Legacy-Rows (nicht mehr in raw oder Status ≠ 35) werden entfernt — genau wie
  es der Legacy-Rebuild tat (Statuswechsel In-Betrieb→stillgelegt = „Entfernt"-Event,
  konsistent zur bisherigen Historien-Semantik).
- metadaten.stand = Laufzeit → meta.stand der App zeigt den echten Datenstand.
"""
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from import_mastr import to_mw, normalize_typ  # noqa: E402
from snapshot import ensure_schema, save_snapshot, compute_delta, build_historie  # noqa: E402

DB_PATH = ROOT / "data" / "mastr.db"
DIST_HIST = ROOT / "dist" / "assets" / "historie.json"


def parse_ms_date(val):
    if not val or not isinstance(val, str):
        return None
    m = re.search(r"Date\((\d+)\)", val)
    if m:
        try:
            return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            return None
    return val


def clean_html(s):
    return re.sub(r"<[^>]+>", "", s).strip() if s else None


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def raw_to_legacy_row(raw_json: str, et_id: int):
    """Konvertiert raw_json in ein Legacy-`einheiten`-Row-Tupel (Schema wie import_mastr).
    Returns None, wenn der Record NICHT in die In-Betrieb-Basis gehört."""
    r = json.loads(raw_json)
    if str(r.get("BetriebsStatusId")) != "35":
        return None
    lat = _f(r.get("Breitengrad"))
    lon = _f(r.get("Laengengrad"))
    if lat is None or lon is None:
        return None  # ohne Geolok nicht in Legacy-Basis (geolokation=1-Filter)
    mw = to_mw({"Bruttoleistung": r.get("Bruttoleistung"),
                "Typenbezeichnung": r.get("Typenbezeichnung"),
                "RotordurchmesserWindenergieanlage": r.get("RotordurchmesserWindenergieanlage")}, et_id)
    if et_id == 2497:
        if mw is None or mw < 0.1:
            return None
    else:
        if mw is None or mw < 0.5:
            return None
    art = r.get("ArtDerSolaranlageBezeichnung") or r.get("WindAnLandOderSeeBezeichnung") or None
    return (
        r.get("MaStRNummer"), r.get("EinheitName"), et_id,
        "Wind" if et_id == 2497 else "Solare Strahlungsenergie", art,
        mw,
        r.get("BetriebsStatusName"), r.get("SystemStatusName"),
        parse_ms_date(r.get("InbetriebnahmeDatum")),
        parse_ms_date(r.get("EegInbetriebnahmeDatum")),
        parse_ms_date(r.get("DatumLetzteAktualisierung")),
        r.get("Bundesland"), r.get("Landkreis"), r.get("Gemeinde"), r.get("Plz"),
        r.get("Ort"), r.get("Strasse"),
        lat, lon, 1,
        clean_html(r.get("NetzbetreiberNamen")), r.get("AnlagenbetreiberName"),
        int(r["AnzahlSolarModule"]) if r.get("AnzahlSolarModule") else None,
        r.get("HauptausrichtungSolarModuleBezeichnung"),
        r.get("SolarparkName"),
        _f(r.get("NabenhoeheWindenergieanlage")),
        _f(r.get("RotordurchmesserWindenergieanlage")),
        _f(r.get("LichteHoehe")),
        normalize_typ(r.get("Typenbezeichnung")),  # V37: Majority-Vote (Wind-relevant)
        r.get("HerstellerWindenergieanlageBezeichnung"),
        r.get("WindparkName"),
        r.get("WindAnLandOderSeeBezeichnung"),
        r.get("LokationMastrNr"),
        parse_ms_date(r.get("EinheitRegistrierungsdatum")),
    )


LEGACY_COLS = (
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


def main() -> None:
    db = sqlite3.connect(DB_PATH)
    ensure_schema(db)
    now = datetime.now().isoformat(timespec="seconds")

    # 0) Alter Stand sichern (VOR dem Schreiben — Snapshot-Dedup verhindert Duplikate)
    old_snapshot_id = None
    if db.execute("SELECT COUNT(*) FROM einheiten").fetchone()[0] > 0:
        old_stand = db.execute("SELECT value FROM metadaten WHERE key='stand'").fetchone()
        old_datum = old_stand[0][:10] if old_stand and old_stand[0] else "unknown"
        old_snapshot_id = save_snapshot(db, old_datum)
        print(f"Alter Stand: Snapshot #{old_snapshot_id} ({old_datum})")

    # 1) UPSERT aller In-Betrieb-Records (Status 35) aus raw in Legacy-Tabelle
    rows = db.execute(
        "SELECT mastr_nummer, energietraeger_id, raw_json FROM einheiten_raw"
    ).fetchall()
    written = skipped = 0
    ncols = len(LEGACY_COLS.split(","))
    placeholders = ",".join("?" * ncols)
    psql = f"INSERT OR REPLACE INTO einheiten ({LEGACY_COLS}) VALUES ({placeholders})"
    for mn, et_id, raw_json in rows:
        row = raw_to_legacy_row(raw_json, et_id)
        if row is None:
            skipped += 1
            continue
        db.execute(psql, row)
        written += 1
    db.commit()
    print(f"Legacy-Sync (nur Status 35): {written} Rows geschrieben | {skipped} übersprungen "
          f"(Status ≠ 35 / keine Geolok / Grenzwert / Leistung unbrauchbar)")

    # 2) Verwaiste Legacy-Rows entfernen: Record nicht mehr in raw ODER Status ≠ 35.
    #    (Statuswechsel In-Betrieb→stillgelegt = „Entfernt"-Event — konsistent zur
    #    bisherigen Historien-Semantik des Legacy-Rebuilds.)
    bs35_mns = {r[0] for r in db.execute(
        "SELECT mastr_nummer FROM einheiten_raw WHERE "
        "json_extract(raw_json,'$.BetriebsStatusId')=35").fetchall()}
    legacy_mns = {r[0] for r in db.execute("SELECT mastr_nummer FROM einheiten").fetchall()}
    verwaist = legacy_mns - bs35_mns
    if verwaist:
        db.executemany("DELETE FROM einheiten WHERE mastr_nummer=?", [(m,) for m in verwaist])
        db.commit()
        print(f"Verwaiste/Status-gewechselte Legacy-Rows entfernt: {len(verwaist)}")

    # 3) metadaten.stand = Pipeline-Stand (V43.2-Fix: war bisher nur Legacy-Rebuild)
    db.execute("INSERT OR REPLACE INTO metadaten VALUES ('stand', ?)", (now,))
    db.execute("INSERT OR REPLACE INTO metadaten VALUES ('einheiten_pv', ?)",
               (str(db.execute("SELECT COUNT(*) FROM einheiten WHERE energietraeger_id=2495").fetchone()[0]),))
    db.execute("INSERT OR REPLACE INTO metadaten VALUES ('einheiten_wind', ?)",
               (str(db.execute("SELECT COUNT(*) FROM einheiten WHERE energietraeger_id=2497").fetchone()[0]),))
    db.commit()
    print(f"metadaten.stand → {now}")

    # 4) Neuer Snapshot + Delta + historie.json (save_snapshot deduppt bei identischen Zahlen)
    new_snapshot_id = save_snapshot(db, now[:10])
    n_now = db.execute("SELECT COUNT(*) FROM einheiten").fetchone()[0]
    print(f"Snapshot #{new_snapshot_id} ({now[:10]}): {n_now} Einheiten (In-Betrieb-Basis)")
    if old_snapshot_id is not None and old_snapshot_id != new_snapshot_id:
        delta = compute_delta(db, old_snapshot_id, new_snapshot_id)
        print(f"Delta #{old_snapshot_id}→#{new_snapshot_id}: "
              f"Wind +{delta['wind_neu']}/+{delta['wind_mw_neu']} MW · PV +{delta['pv_neu']}/+{delta['pv_mw_neu']} MW · "
              f"Entfernt {delta['removed_anzahl']}")
    elif old_snapshot_id == new_snapshot_id:
        print("Snapshot-Dedup: Kennzahlen unverändert — kein neuer Historie-Punkt (korrekt)")
    historie = build_historie(db)
    DIST_HIST.parent.mkdir(parents=True, exist_ok=True)
    with open(DIST_HIST, "w", encoding="utf-8") as f:
        json.dump(historie, f, ensure_ascii=False, indent=2)
    print(f"historie.json: {len(historie)} Snapshots → {DIST_HIST}")
    db.close()


if __name__ == "__main__":
    main()

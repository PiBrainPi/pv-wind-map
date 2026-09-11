#!/usr/bin/env python3
"""
fix_typenbezeichnung.py — V37 (11.09.2026, User-AP1): Einmalige DB-Bereinigung.

Wendet die Majority-Vote-Mapping-Tabelle (data/typ_normalisierung.json) auf die
bestehende Datenbank an:
  1. einheiten_raw.raw_json: Typenbezeichnung im JSON-rewrite (NUR Feld Typenbezeichnung,
     alles andere byte-identisch), nur energietraeger_id=2497 (Wind, User-Entscheid).
  2. Legacy-Tabelle `einheiten`: Spalte typenbezeichnung (falls vorhanden).

Idempotent: ein 2. Lauf ändert 0 Records. DatumLetzteAktualisierung bleibt unangetastet
(keine künstliche „Aktualisierung" — die Rohdaten bleiben sonst bei Delta-UPSERTs
fälschlich „neuer" als MaStR).

Backup: vor dem Lauf wird data/mastr.db nach data/backups/mastr.db.backup_<datum> kopiert.

BEACHTEN (Pitfall, 1. Lauf 11.09.): Der Scan in build_typ_normalisierung.py läuft auf
der KARTEN-Basis (Geolokation + >= 0,1 MW). Einheiten OHNE Geolokation sind darin
NICHT enthalten — deren Dubletten bleiben im Rest-Rescan (der auf ALLEN Wind-Rows
läuft) stehen. Diese Rest-Dubletten (82 Gruppen, Kleinwind/Kleinstanlagen wie
EasyWind 6AC, TW 80, SkyWind NG) sind für den Typ-Tab irrelevant (Tab aggregiert
nur Karten-Basis), werden aber aus Konsistenzgründen mit einem erweiterten
Ganz-Bestand-Mapping bereinigt: build_typ_normalisierung.py --all-bestand erweitert
das Mapping auf alle Wind-Rows, dann dieser Fix erneut.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mastr.db"
MAP_PATH = ROOT / "data" / "typ_normalisierung.json"


def main() -> None:
    if not MAP_PATH.exists():
        print("FEHLER: data/typ_normalisierung.json fehlt. Erst scripts/build_typ_normalisierung.py ausführen.", file=sys.stderr)
        sys.exit(1)
    mapping: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    print(f"Mapping-Einträge: {len(mapping)}")

    # Backup (Pipeline-Regel: Backup vor jedem DB-Eingriff)
    backup_dir = ROOT / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"mastr.db.backup_{stamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup: {backup_path}")

    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT mastr_nummer, raw_json FROM einheiten_raw WHERE energietraeger_id = 2497"
    ).fetchall()

    fixed_raw = 0
    updates = []
    for mnr, rj in rows:
        d = json.loads(rj)
        t = d.get("Typenbezeichnung")
        if t is None:
            continue
        new_t = mapping.get(t, t)
        if new_t != t:
            d["Typenbezeichnung"] = new_t
            updates.append((json.dumps(d, ensure_ascii=False), mnr))
            fixed_raw += 1

    print(f"raw_json-Korrekturen: {fixed_raw}")
    if updates:
        db.executemany(
            "UPDATE einheiten_raw SET raw_json = ? WHERE mastr_nummer = ?",
            updates,
        )

    # Legacy-Tabelle (falls befüllt)
    try:
        legacy = db.execute(
            "SELECT mastr_nummer, typenbezeichnung FROM einheiten WHERE energietraeger_name='Wind' AND typenbezeichnung IS NOT NULL"
        ).fetchall()
    except sqlite3.OperationalError:
        legacy = []
    fixed_legacy = 0
    for mnr, t in legacy:
        new_t = mapping.get(t, t)
        if new_t != t:
            db.execute("UPDATE einheiten SET typenbezeichnung = ? WHERE mastr_nummer = ?", (new_t, mnr))
            fixed_legacy += 1
    print(f"Legacy-Tabelle Korrekturen: {fixed_legacy}")

    db.commit()

    # Rescan: verbleibende Dubletten-Gruppen (sollte 0 sein)
    import re
    from collections import defaultdict, Counter

    def norm_key(t: str) -> str:
        return re.sub(r"[\s\-_]+", "", (t or "").strip().upper())

    rows2 = db.execute(
        "SELECT raw_json FROM einheiten_raw WHERE energietraeger_id = 2497"
    ).fetchall()
    groups: dict[str, Counter] = defaultdict(Counter)
    for (rj,) in rows2:
        t = (json.loads(rj).get("Typenbezeichnung") or "").strip()
        if t:
            groups[norm_key(t)][t] += 1
    rest = {k: dict(v) for k, v in groups.items() if len(v) > 1}
    print(f"Rescan: verbleibende Gruppen mit mehreren Schreibweisen: {len(rest)}")
    if rest:
        for k, v in list(rest.items())[:10]:
            print(f"  REST: {k}: {v}")
    db.close()

    print("Fertig." if not rest else "⚠ Rest-Dubletten vorhanden (s. docstring: Ganz-Bestand-Mapping via --all-bestand nötig).")


if __name__ == "__main__":
    main()

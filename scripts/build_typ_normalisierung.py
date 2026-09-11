#!/usr/bin/env python3
"""
build_typ_normalisierung.py — V37 (11.09.2026, User-AP1)

Erzeugt die Typ-Normalisierungs-Tabelle data/typ_normalisierung.json aus den
Wind-Rohdaten (einheiten_raw) auf KARTEN-BASIS (Geolokation + to_mw >= 0,1 MW).

Regel (Majority-Vote, User-Vorgabe 11.09.): Innerhalb jeder Typ-Gruppe
(Normalisierungs-Key = uppercase ohne Leerzeichen/Bindestriche/Unterstriche) wird die
HÄUFIGSTE Schreibweise als korrekt betrachtet; alle anderen Varianten werden auf sie
gemappt. Tie-Break: kürzeste Schreibweise, dann alphabetisch.

Das Mapping wird als PIPELINE-REGEL angewandt:
  - import_mastr.py (Legacy-Import): vor to_mw (Typ-'15mw'-Ausnahme muss den
    normalisierten Typ sehen)
  - export_app.py (Karten-Export): vor to_mw + build_units
  - einmalige DB-Bereinigung: fix_typenbezeichnung.py (raw_json + Legacy-Tabelle)

Wichtig: Die Datenbasis kann sich ändern (Updates). Das Skript ist idempotent und
kann jederzeit neu gelaufen werden — der Majority-Vote wird dann frisch berechnet.
Report: data/typ_normalisierung_report.csv (eine Zeile je Gruppe).

--all-bestand (optional): Scan auf ALLEN Wind-Rows statt nur Karten-Basis — bereinigt
auch Dubletten von Einheiten ohne Geolokation/Kleinwind (relevant für die einmalige
DB-Bereinigung, nicht für den Typ-Tab selbst).
"""
from __future__ import annotations

import csv
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from import_mastr import to_mw  # noqa: E402

DB_PATH = ROOT / "data" / "mastr.db"
OUT_JSON = ROOT / "data" / "typ_normalisierung.json"
OUT_CSV = ROOT / "data" / "typ_normalisierung_report.csv"

ALL_BESTAND = "--all-bestand" in sys.argv


def norm_key(t: str) -> str:
    """Normalisierungs-Key: gross, ohne Leerzeichen/Bindestriche/Unterstriche/Punkte/Kommas."""
    return re.sub(r"[\s\-_.:,]+", "", (t or "").strip().upper())


def main() -> None:
    db = sqlite3.connect(DB_PATH)
    if ALL_BESTAND:
        # Ganz-Bestand: alle Wind-Rows (auch ohne Geolokation / < 0,1 MW)
        rows = db.execute(
            "SELECT mastr_nummer, raw_json FROM einheiten_raw WHERE energietraeger_id = 2497"
        ).fetchall()
        basis_label = "Ganz-Bestand Wind"
    else:
        rows = db.execute(
            """
            SELECT mastr_nummer, raw_json FROM einheiten_raw
            WHERE energietraeger_id = 2497
              AND json_extract(raw_json,'$.Breitengrad') IS NOT NULL
              AND json_extract(raw_json,'$.Breitengrad') != ''
            """
        ).fetchall()
        basis_label = "Karten-Basis Wind"
    db.close()

    groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
    basis = 0
    for mnr, rj in rows:
        d = json.loads(rj)
        if not ALL_BESTAND:
            mw = to_mw(
                {
                    "Bruttoleistung": d.get("Bruttoleistung"),
                    "Typenbezeichnung": d.get("Typenbezeichnung"),
                    "RotordurchmesserWindenergieanlage": d.get("RotordurchmesserWindenergieanlage"),
                },
                2497,
            )
            if mw is None or mw < 0.1:
                continue
        basis += 1
        typ = (d.get("Typenbezeichnung") or "").strip()
        if typ:
            groups[norm_key(typ)].append((mnr, typ))

    mapping: dict[str, str] = {}
    total_fix = 0
    csv_rows = []
    for key, items in groups.items():
        variants = Counter(raw for _, raw in items)
        if len(variants) < 2:
            continue
        best = sorted(variants.items(), key=lambda x: (-x[1], len(x[0]), x[0]))[0][0]
        n_fix = sum(n for raw, n in variants.items() if raw != best)
        for raw, n in variants.items():
            if raw != best:
                mapping[raw] = best
        total_fix += n_fix
        csv_rows.append(
            {
                "norm_key": key,
                "ziel": best,
                "anzahl_records": sum(variants.values()),
                "korrigierte_records": n_fix,
                "varianten": " || ".join(f"{raw}:{n}" for raw, n in sorted(variants.items(), key=lambda x: -x[1])),
            }
        )

    OUT_JSON.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["norm_key", "ziel", "anzahl_records", "korrigierte_records", "varianten"])
        w.writeheader()
        w.writerows(sorted(csv_rows, key=lambda r: -r["korrigierte_records"]))

    print(f"{basis_label}: {basis} Anlagen")
    print(f"Gruppen mit mehreren Schreibweisen: {len(csv_rows)}")
    print(f"Mapping-Eintraege: {len(mapping)}")
    print(f"Betroffene Records (fuer Fix-Lauf): {total_fix}")
    print(f"-> {OUT_JSON}")
    print(f"-> {OUT_CSV}")


if __name__ == "__main__":
    main()

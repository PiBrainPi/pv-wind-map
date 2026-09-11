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

    # ------------------------------------------------------------------
    # V42 (11.09.2026, User-AP1): Hersteller-Präfix-Regel (Post-Schritt)
    #
    # 'Enercon E-82' → 'E-82', 'Vestas V112' → 'V112', 'Nordex N117' → 'N117' …
    # Regel: Wenn ein Typ mit einem HERSTELLER-WORT beginnt und der Rest-Typ
    # BEREITS als eigene Gruppe in den Daten existiert, wird das Präfix entfernt.
    # Sicherheit: Es werden NUR Ziele gemappt, die es wirklich gibt — es werden
    # keine Typen erfunden. Bewusst NICHT als Präfix behandelt (Modellnamen!):
    #   GE (GE 1.5sl ist der volle Modellname), BARD (BARD 5.0), Haliade,
    #   eno (eno 82), AN Bonus (AN = Herstellerkürzel + zweiter Herstellername).
    # ------------------------------------------------------------------
    HER_PREFIXES = [
        "Enercon", "ENERCON", "Vestas", "Nordex", "Nordex Acciona", "Acciona",
        "Siemens", "Siemens Gamesa", "Gamesa", "SGRE", "Senvion", "REpower",
        "REpower Systems", "Fuhrlaender", "Fuhrländer", "Fuhrlander", "DeWind",
        "Goldwind", "Envision", "VENSYS", "Vensys", "WinWind", "Made",
        "Pfleiderer", "Jacobs", "Tacke", "Bonus", "Micon", "Wind World",
        "Nordex Energy", "Vestas Wind Systems", "General Electric",
        "GE Wind Energy", "Nordex-Acciona", "W2E", "Eozen",
    ]
    ziel_exists = None  # (entfernt — Canon-Formen werden direkt unten gesammelt)
    # Erst alle Kanon-Formen sammeln (nach Majority-Vote), dann Präfixe auflösen.
    canon: Counter = Counter()
    canon_mw: Counter = Counter()  # Werte sind kW-Summen (MaStR Nettonennleistung)
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
        typ = (d.get("Typenbezeichnung") or "").strip()
        if not typ:
            continue
        canon[mapping.get(typ, typ)] += 1
        brutto = d.get("Bruttoleistung")
        if brutto:
            canon_mw[mapping.get(typ, typ)] += float(brutto)

    prefix_added = 0
    prefix_rows = []
    for typ in sorted(canon):
        tl = typ.strip()
        for her in sorted(HER_PREFIXES, key=len, reverse=True):
            m = re.match(re.escape(her) + r"[\s\-_]+(\S.*)$", tl, re.IGNORECASE)
            if m:
                rest = m.group(1).strip()
                if re.search(r"\d", rest) and rest in canon:
                    mapping[typ] = rest
                    prefix_added += 1
                    prefix_rows.append({
                        "norm_key": norm_key(typ),
                        "ziel": rest,
                        "anzahl_records": canon[typ],
                        "korrigierte_records": canon[typ],
                        "varianten": f"PRÄFIX {her} | {typ}:{canon[typ]} -> {rest} (Ziel hat {canon[rest]})",
                    })
                break

    csv_rows.extend(prefix_rows)
    total_fix += sum(r["korrigierte_records"] for r in prefix_rows)

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

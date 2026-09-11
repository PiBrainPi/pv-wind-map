#!/usr/bin/env python3
"""
merge_delta.py — Merged Delta-JSONs (data/raw_v2/delta/*.json) in die Basis-JSONs.

Aufgabe (AP3, 30-Punkte-Plan 10.09.2026): Der Delta-Fetch (fetch_v2.py --delta) liefert
nur neue/veränderte Records in data/raw_v2/delta/<strang>_<stempel>.json. Dieses Skript
merged sie per UPSERT-Semantik (je MaStRNummer, neueres DatumLetzteAktualisierung gewinnt)
in die Basisdateien data/raw_v2/{wind,pv}{,_status31,37,38}.json — atomar (tmp+rename),
bestehende Basisdateien werden nicht beschädigt (Regel 1).

Statuswechsel: Ein Record, der im Delta mit Status 31/37/38 erscheint, wird aus der
Basis wind.json (Status 35) ENTFERNT und in der Ziel-Statusdatei upgedatet — und
umgekehrt (Reaktivierung). Damit bleibt die 1:1-Zuständigkeit je Datei erhalten.

Reihenfolge im Pipeline-Lauf: fetch_v2.py --delta  →  merge_delta.py  →  import_v2.py
Nutzung: python3 scripts/merge_delta.py [--dry-run]
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw_v2"
DELTA_DIR = OUT_DIR / "delta"

STATUS_STRANGE = ["", "_status31", "_status37", "_status38"]
TECHS = ["wind", "pv"]


def ms_date_iso(r: dict) -> str:
    """DatumLetzteAktualisierung (/Date(ms)/) -> ISO-String für Vergleiche."""
    raw = (r.get("DatumLetzteAktualisierung") or "").replace("/Date(", "").replace(")/", "")
    if raw.isdigit():
        return datetime.fromtimestamp(int(raw) / 1000, tz=timezone.utc).isoformat()
    return ""


def merge_strang(base_file: Path, delta_files: list[Path], dry: bool) -> dict:
    """Merged alle Delta-Dateien in eine Basisdatei. Returns Statistik."""
    with open(base_file, encoding="utf-8") as f:
        base: dict[str, dict] = {r["MaStRNummer"]: r for r in json.load(f)}
    stats = {"base": len(base), "upserted": 0, "new": 0, "unchanged": 0}

    for df in delta_files:
        with open(df, encoding="utf-8") as f:
            delta_records = json.load(f)
        for r in delta_records:
            mn = r.get("MaStRNummer")
            if not mn:
                continue
            existing = base.get(mn)
            if existing is None:
                base[mn] = r
                stats["new"] += 1
            elif ms_date_iso(r) >= ms_date_iso(existing):
                base[mn] = r
                stats["upserted"] += 1
            else:
                stats["unchanged"] += 1

    if not dry:
        tmp = base_file.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(list(base.values()), f, ensure_ascii=False)
        os.replace(tmp, base_file)  # atomar
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Nur Statistik, kein Schreiben")
    args = ap.parse_args()

    if not DELTA_DIR.exists():
        print("Kein data/raw_v2/delta/ Ordner — nichts zu mergen.")
        return

    delta_files = sorted(DELTA_DIR.glob("*.json"))
    if not delta_files:
        print("Keine Delta-Dateien vorhanden — nichts zu mergen.")
        return

    # Records je Strang gruppieren (wind / pv / *_statusNN)
    by_strang: dict[str, list[Path]] = {}
    merged_mns: dict[str, set[str]] = {}  # strang -> im Delta enthaltene MaStR-Nummern
    for tech in TECHS:
        for s in STATUS_STRANGE:
            strang = f"{tech}{s}"
            strang_files = [f for f in delta_files if f.name.startswith(strang + "_")]
            if strang_files:
                by_strang[strang] = strang_files
                mns = set()
                for f in strang_files:
                    with open(f, encoding="utf-8") as fh:
                        mns |= {r.get("MaStRNummer") for r in json.load(fh) if r.get("MaStRNummer")}
                merged_mns[strang] = mns

    print(f"Delta-Dateien: {len(delta_files)} in {len(by_strang)} Strängen")
    total = {"new": 0, "upserted": 0, "unchanged": 0}

    for strang, strang_files in by_strang.items():
        base_file = OUT_DIR / f"{strang}.json"
        if not base_file.exists():
            print(f"  (!) {strang}: Basisdatei fehlt — übersprungen (erst Vollabruf nötig)")
            continue
        stats = merge_strang(base_file, strang_files, args.dry_run)
        total["new"] += stats["new"]
        total["upserted"] += stats["upserted"]
        total["unchanged"] += stats["unchanged"]
        mode = "DRY-RUN" if args.dry_run else "gemerged"
        print(f"  {strang}: Basis {stats['base']} | neu {stats['new']} | upserted {stats['upserted']} | "
              f"unverändert {stats['unchanged']} ({mode})")

    # Statuswechsel-Bereinigung: Records, die im Delta eines FREMD-Strangs auftauchen,
    # sind in den anderen Status-Strängen überflüssig geworden (Status ist 1:1).
    # PERFORMANCE-FIX (10.09., erster Lauf brauchte 2,5 h): Vorher wurde je Duplikat
    # die komplette Basisdatei geladen UND geschrieben (O(duplikate × Dateigröße) —
    # 1407 Duplikate × ~100 MB = 45 GB Schreib-I/O). Jetzt: EIN Laden je Strang,
    # Dedup in Memory, EIN Schreiben je Strang.
    if not args.dry_run:
        moved = 0
        for tech in TECHS:
            strangs = [f"{tech}{s}" for s in STATUS_STRANGE]
            paths = {s: OUT_DIR / f"{s}.json" for s in strangs}
            data: dict[str, dict[str, dict]] = {}
            for s, p in paths.items():
                if p.exists():
                    with open(p, encoding="utf-8") as f:
                        data[s] = {r["MaStRNummer"]: r for r in json.load(f)}
            # Nummern in MEHREREN Strängen finden
            from collections import Counter
            cnt: Counter = Counter()
            for s, recs in data.items():
                for mn in recs:
                    cnt[mn] += 1
            duplicates = {mn for mn, c in cnt.items() if c > 1}
            if not duplicates:
                continue
            for mn in duplicates:
                best_strang, best_date = None, ""
                for s, recs in data.items():
                    if mn in recs:
                        d = ms_date_iso(recs[mn])
                        if d >= best_date:
                            best_strang, best_date = s, d
                for s, recs in data.items():
                    if s != best_strang and mn in recs:
                        del recs[mn]
                        moved += 1
            # EIN Schreiben je Strang (atomar)
            for s, recs in data.items():
                p = paths[s]
                tmp = p.with_suffix(".json.tmp")
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(list(recs.values()), f, ensure_ascii=False)
                os.replace(tmp, p)
        if moved:
            print(f"Statuswechsel-Bereinigung: {moved} Records aus Fremd-Strängen entfernt")

    print(f"\nGesamt: neu {total['new']} | upserted {total['upserted']} | "
          f"unverändert {total['unchanged']}{' (DRY-RUN, nichts geschrieben)' if args.dry_run else ''}")

    # Nach erfolgreichem Merge: Delta-Dateien archivieren (bleiben erhalten, aber
    # markiert als verarbeitet — Regel 1: nichts löschen)
    if not args.dry_run:
        archive = DELTA_DIR / "merged"
        archive.mkdir(exist_ok=True)
        for f in delta_files:
            f.rename(archive / f.name)
        print(f"Delta-Dateien nach delta/merged/ verschoben: {len(delta_files)}")


if __name__ == "__main__":
    main()

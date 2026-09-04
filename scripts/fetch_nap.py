#!/usr/bin/env python3
"""
fetch_nap.py — Lädt Netzanschlusspunkte (NAP) für alle Lokationen der Wind/PV-Einheiten.

Grundsatzentscheidung (Regel 2, Freigabe 2026-09-03): NAP-Daten werden dauerhaft auf dem
Server vorgehalten. Endpoint (live verifiziert 2026-09-03):
  GET /MaStR/Einheit/Json/NetzanschlusspunkteKendoList/{lokationId}?lokationId={lokationId}

Eigenschaften:
  - Inkrementell via Cache-Tabelle `nap_fetch_log` in data/mastr.db (Schema 2.0):
    bereits erfolgreich abgefragte Lokationen werden übersprungen (nicht gelöscht!).
  - Rate-limit-freundlich: 0.2 s Pause (40/40 Requests im Test fehlerfrei).
  - Resumable: Skript kann jederzeit abgebrochen & neu gestartet werden.
  - Schreibt Ergebnisse in data/nap/*.jsonl (append-only, je Zeile ein Lokation-Dokument).

Nutzung:
  python3 scripts/fetch_nap.py            # normal (bis zu --limit Lokationen)
  python3 scripts/fetch_nap.py --limit 500
"""
import argparse
import json
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://www.marktstammdatenregister.de/MaStR/Einheit/Json/NetzanschlusspunkteKendoList/{lid}?lokationId={lid}"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mastr.db"
NAP_DIR = ROOT / "data" / "nap"
PAUSE = 0.2
MAX_RETRIES = 4


def nap_request(lid: int) -> list[dict]:
    last = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(BASE.format(lid=lid), headers=UA), timeout=30
            )
            d = json.load(r)
            if d.get("Errors"):
                raise RuntimeError(f"API Errors: {d['Errors']}")
            return d.get("Data") or []
        except Exception as e:
            last = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"NAP-Abruf fehlgeschlagen für Lokation {lid}: {last}")


def all_lokationen(db: sqlite3.Connection) -> set[int]:
    """Alle bekannten numerischen LokationIds aus den Rohdaten (raw_v2 bevorzugt, sonst raw)."""
    ids: set[int] = set()
    for raw_dir in (ROOT / "data" / "raw_v2", ROOT / "data" / "raw"):
        for name in ("wind.json", "pv.json"):
            p = raw_dir / name
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for s in json.load(f):
                        if s.get("LokationId"):
                            ids.add(int(s["LokationId"]))
    return ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="max. Lokationen in diesem Lauf")
    args = ap.parse_args()

    if not DB_PATH.exists():
        print("FEHLER: data/mastr.db fehlt (erst import_v2.py laufen lassen).", file=sys.stderr)
        sys.exit(1)

    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS nap_fetch_log (
               lokation_id INTEGER PRIMARY KEY,
               status TEXT NOT NULL,             -- ok | error
               nap_count INTEGER,
               fetched_at TEXT NOT NULL
           )"""
    )
    db.commit()

    done = {r[0] for r in db.execute("SELECT lokation_id FROM nap_fetch_log WHERE status='ok'")}
    failed = {r[0] for r in db.execute("SELECT lokation_id FROM nap_fetch_log WHERE status='error'")}
    alle = all_lokationen(db)
    todo = sorted(alle - done)
    if args.limit:
        todo = todo[: args.limit]

    print(f"Lokationen gesamt: {len(alle)} | bereits ok: {len(done)} | Fehler vormals: {len(failed)}")
    print(f"Dieser Lauf: {len(todo)} Lokationen (geschätzt {len(todo)*0.36/3600:.1f} h)")

    NAP_DIR.mkdir(parents=True, exist_ok=True)
    out = NAP_DIR / "netzanschlusspunkte.jsonl"

    ok_ct = err_ct = nap_ct = 0
    t0 = time.time()
    with open(out, "a", encoding="utf-8") as fh:
        for i, lid in enumerate(todo, 1):
            try:
                naps = nap_request(lid)
                fh.write(json.dumps(
                    {"lokation_id": lid, "naps": naps}, ensure_ascii=False
                ) + "\n")
                db.execute(
                    "INSERT OR REPLACE INTO nap_fetch_log VALUES (?,?,?,datetime('now'))",
                    (lid, "ok", len(naps)),
                )
                ok_ct += 1
                nap_ct += len(naps)
            except Exception as e:
                print(f"    (!) Lokation {lid}: {e}", file=sys.stderr)
                db.execute(
                    "INSERT OR REPLACE INTO nap_fetch_log VALUES (?,?,NULL,datetime('now'))",
                    (lid, "error"),
                )
                err_ct += 1
            fh.flush()
            if i % 25 == 0:
                db.commit()
                rate = i / (time.time() - t0)
                print(f"    {i}/{len(todo)} | ok {ok_ct} err {err_ct} | NAPs {nap_ct} | {rate:.1f}/s | ETA {(len(todo)-i)/rate/60:.0f} min")
            time.sleep(PAUSE)
    db.commit()

    print(f"\nFertig: {ok_ct} ok, {err_ct} Fehler, {nap_ct} NAP-Datensätze -> {out}")
    print("Cache: nap_fetch_log in DB (ok-Lokationen werden bei erneutem Lauf übersprungen).")
    db.close()


if __name__ == "__main__":
    main()

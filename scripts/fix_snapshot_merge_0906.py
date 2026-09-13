#!/usr/bin/env python3
"""fix_snapshot_merge_0906.py — V44/AP4 (User-Freigabe 12.09.): Merge der beiden
06.09-Snapshots zu EINEM Eintrag.

Hintergrund: Am 06.09. entstanden zwei Snapshots (#10 vormittags nach Legacy-Import,
#15 am 12.09. via sync_legacy.py als 'Alter Stand'-Sicherung mit Datum 06.09 — korrigierte
Daten nach V37/V42-Typen-Bereinigung). Die Tabelle 'Daten-Verlauf' zeigte 06.09 doppelt.

Semantik (User-Entscheid): Snapshot #15 (korrigiert) bleibt als DER 06.09-Eintrag,
Snapshot #10 wird GELÖSCHT (inkl. snapshot_einheiten-Referenzen). Delta-Kette
(01.09→06.09→12.09) rechnet build_historie danach automatisch neu.

Idempotent: Existiert kein doppelter 06.09-Snapshot mehr, ist das Skript ein No-Op.
Regel 1: löscht NUR Snapshot #10 + dessen Referenzen — sonst nichts.
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "mastr.db"


def main() -> None:
    db = sqlite3.connect(DB)
    cur = db.cursor()
    rows = cur.execute(
        "SELECT id, datum, wind_anzahl, pv_anzahl, gesamt_anzahl FROM snapshots WHERE datum='2026-06-09' OR datum='2026-09-06' ORDER BY id"
    ).fetchall()
    print(f"06.09-Snapshots: {rows}")
    if len(rows) < 2:
        print("Kein doppelter 06.09-Snapshot — nichts zu tun (idempotent).")
        db.close()
        return
    ids_0906 = [r[0] for r in rows]
    # Behalten: der letzte (= korrigierte, #15); Löschen: alle anderen
    keep_id = ids_0906[-1]
    drop_ids = ids_0906[:-1]
    if keep_id != 15:
        print(f"⚠️  Erwartete #15 als Behalten-Kandidat, gefunden: {keep_id} — Abbruch (manuell prüfen).")
        db.close()
        sys.exit(1)
    for did in drop_ids:
        n = cur.execute("SELECT COUNT(*) FROM snapshot_einheiten WHERE snapshot_id=?", (did,)).fetchone()[0]
        cur.execute("DELETE FROM snapshot_einheiten WHERE snapshot_id=?", (did,))
        cur.execute("DELETE FROM snapshots WHERE id=?", (did,))
        print(f"Snapshot #{did} gelöscht ({n} Referenzen entfernt)")
    db.commit()
    # Verifikation
    rest = cur.execute("SELECT id, datum, gesamt_anzahl FROM snapshots ORDER BY id").fetchall()
    print("Snapshots danach:", rest)
    cnt = cur.execute("SELECT COUNT(*) FROM snapshots WHERE datum='2026-09-06'").fetchone()[0]
    print(f"06.09-Einträge: {cnt} (erwartet 1)")
    # historie.json neu bauen
    sys.path.insert(0, str(ROOT / "scripts"))
    from snapshot import build_historie
    historie = build_historie(db)
    out = ROOT / "dist" / "assets" / "historie.json"
    import json
    with open(out, "w", encoding="utf-8") as f:
        json.dump(historie, f, ensure_ascii=False, indent=2)
    print(f"historie.json neu: {len(historie)} Snapshots → {out}")
    # Delta-Spotcheck
    for h in historie:
        d = h.get("delta") or {}
        if d:
            print(f"  {h['datum']}: Δ {d['gesamt_diff_anzahl']:+d} Anlagen / {d['gesamt_diff_mw']:+.2f} MW (removed {d['removed_anzahl']})")
    db.close()


if __name__ == "__main__":
    main()

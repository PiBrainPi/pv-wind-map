#!/usr/bin/env python3
"""F1 (Punkt 2): NAP-Index für die Frontend-Suche.

Erzeugt dist/assets/nap_index.json — NUR NAPs mit ≥1 verknüpfter georef
In-Betrieb-Anlage (NAPs ohne sichtbare Anlagen landen auf einer leeren Karte
und sind deshalb nicht suchbar; 13,7 % der NAPs, dokumentiert).

Felder (kompakt): nap (SAN-Nr.), nb (Netzbetreiber ohne SNB-Klammer),
se (Spannungsebene, Pipe bei Multi), rz (Regelzone), n (Anzahl Anlagen), lid.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "mastr.db"
OUT = ROOT / "dist" / "assets" / "nap_index.json"


def main() -> None:
    db = sqlite3.connect(DB)
    cur = db.cursor()
    rows = cur.execute("""
        SELECT n.nap_mastr_nummer, n.lokation_id, n.netzbetreiber,
               GROUP_CONCAT(DISTINCT n.spannungsebene), n.regelzone,
               (SELECT COUNT(*) FROM einheiten_raw er
                WHERE er.lokation_id = n.lokation_id
                  AND json_extract(er.raw_json,'$.Breitengrad') IS NOT NULL
                  AND json_extract(er.raw_json,'$.BetriebsStatusId') = 35) AS n_anlagen
        FROM netzanschlusspunkte n
        GROUP BY n.nap_mastr_nummer
        HAVING n_anlagen > 0
        ORDER BY n_anlagen DESC
    """).fetchall()

    index = []
    for nap, lid, nb, se, rz, n in rows:
        index.append({
            "nap": nap,
            "lid": int(lid),
            "nb": (nb or "").split(" (")[0],   # SNB-Klammer weg — kürzer, suchbarer
            "se": se or "",
            "rz": rz or "",
            "n": int(n),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"nap_index.json: {len(index)} NAPs (von 27.870), {size_mb:.2f} MB → {OUT}")


if __name__ == "__main__":
    main()

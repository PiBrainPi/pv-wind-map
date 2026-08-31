#!/usr/bin/env python3
"""
rebuild_groessen.py — DB-freies Rebuild der Größenklassen in statistik.json.
Siehe export_app.py für die autoritative Staffeldefinition.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EINHEITEN = ROOT / "dist" / "assets" / "einheiten.json"
STAT = ROOT / "dist" / "assets" / "statistiken.json"

# Einheitliche Staffel [label, von, bis, kritis] — identisch zu export_app.py
# Kritis-Schwelle (BSI-KritisV): ≥104 MW. Klasse 100–104 = kein Kritis.
STAFFEL = [
    ("0.1–0.5", 0.1, 0.5, False), ("0.5–1", 0.5, 1, False),
    ("1–2", 1, 2, False), ("2–5", 2, 5, False), ("5–10", 5, 10, False),
    ("10–30", 10, 30, False), ("30–60", 30, 60, False), ("60–100", 60, 100, False),
    ("100–104", 100, 104, False),   # unterhalb Kritis-Schwelle
    ("104–150", 104, 150, True),    # Kritis ≥104 MW
    ("150+", 150, 1e9, True),       # Kritis
]


def compute(mws, staffel):
    total_mw = sum(mws)
    total_n = len(mws)
    out = []
    for label, von, bis, kritis in staffel:
        n = sum(1 for v in mws if von <= v < bis)
        s = sum(v for v in mws if von <= v < bis)
        out.append({
            "label": label, "von": von, "bis": bis, "kritis": kritis,
            "anzahl": n, "sum_mw": round(s, 2),
            "anteil_anzahl": round(100.0 * n / total_n, 1) if total_n else 0,
            "anteil_summe": round(100.0 * s / total_mw, 1) if total_mw else 0,
        })
    return out


def main():
    units = json.load(open(EINHEITEN, encoding="utf-8"))
    wind = [u["mw"] for u in units if u.get("t") == "wind" and u.get("mw") is not None]
    pv = [u["mw"] for u in units if u.get("t") == "pv" and u.get("mw") is not None]
    alle = [u["mw"] for u in units if u.get("mw") is not None]

    stats = json.load(open(STAT, encoding="utf-8"))
    stats["groessenklassen"] = {
        "wind": compute(wind, STAFFEL),
        "pv": compute(pv, STAFFEL),
        "gesamt": compute(alle, STAFFEL),
    }
    ges = stats.setdefault("gesamt", {})
    ges["wind_max_mw"] = round(max(wind), 2) if wind else 0
    ges["pv_max_mw"] = round(max(pv), 2) if pv else 0
    json.dump(stats, open(STAT, "w", encoding="utf-8"), ensure_ascii=False)

    print(f"Rebuild: wind {len(wind)} | pv {len(pv)} | gesamt {len(alle)}")
    for tech in ("wind", "pv", "gesamt"):
        for k in stats["groessenklassen"][tech]:
            print(f"  [{tech}] {k['label']:>10}: {k['anzahl']:>6} Anlagen | {k['sum_mw']:>10.1f} MW | kritis={'✅' if k['kritis'] else '❌'}")


if __name__ == "__main__":
    main()
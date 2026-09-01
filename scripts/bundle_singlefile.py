#!/usr/bin/env python3
"""
bundle_singlefile.py — Erzeugt eine eigenständige (einzelne) HTML-Datei mit eingebetteten Daten.

Die hostbare App (dist/) lädt Daten per fetch() aus assets/*.json — das braucht einen
HTTP-Server (fetch() ab file:// ist wegen CORS blockiert). Für eine direkt klickbare,
einzelne Datei (doppelklick -> Browser öffnet) betten wir die Daten direkt ein.

Ausgabe: dist/index_singlefile.html  (funktioniert ab file:// mit Internetverbindung)

Nutzung: python3 scripts/bundle_singlefile.py

Hinweis: Leaflet & MarkerCluster werden seit 2026-08-31 (DSGVO) LOKAL aus src/vendor/ inline
eingebettet und von DIESEM Skript mit in die Single-File übernommen (es liest dist/index.html,
das die eingebetteten Vendor-Libs enthält). Kein externes CDN (unpkg) mehr nötig.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def main() -> None:
    src = (DIST / "index.html").read_text(encoding="utf-8")
    units = json.loads((DIST / "assets" / "einheiten.json").read_text(encoding="utf-8"))
    meta = json.loads((DIST / "assets" / "meta.json").read_text(encoding="utf-8"))

    data_js = "window.__PVWIND_DATA__ = " + json.dumps(units, ensure_ascii=False, separators=(",", ":")) + ";"
    meta_js = "window.__PVWIND_META__ = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";"
    try:
        stats = json.loads((DIST / "assets" / "statistiken.json").read_text(encoding="utf-8"))
        stats_js = "window.__PVWIND_STATS__ = " + json.dumps(stats, ensure_ascii=False, separators=(",", ":")) + ";"
    except FileNotFoundError:
        stats_js = "window.__PVWIND_STATS__ = null;"

    # V4: Historie-JSON einbetten (falls vorhanden)
    try:
        historie = json.loads((DIST / "assets" / "historie.json").read_text(encoding="utf-8"))
        hist_js = "window.__PVWIND_HISTORIE__ = " + json.dumps(historie, ensure_ascii=False, separators=(",", ":")) + ";"
    except (FileNotFoundError, json.JSONDecodeError):
        hist_js = "window.__PVWIND_HISTORIE__ = null;"

    injection = f"<script>\n{data_js}\n{meta_js}\n{stats_js}\n{hist_js}\n</script>\n"
    # Daten-Skript VOR dem Haupt-App-Script einfügen (sonst ist window.__PVWIND_DATA__
    # beim init()-Aufruf noch nicht definiert). Anker: CSS-Block der App.
    anchor = "<style>\n* { margin:0;"
    idx = src.find(anchor)
    if idx == -1:
        raise SystemExit("Anker für Einfügung nicht gefunden.")
    out_src = src[:idx] + injection + src[idx:]

    out = DIST / "index_singlefile.html"
    out.write_text(out_src, encoding="utf-8")
    size = out.stat().st_size / 1e6
    print(f"Single-File erstellt: {out} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
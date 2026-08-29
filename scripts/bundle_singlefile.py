#!/usr/bin/env python3
"""
bundle_singlefile.py — Erzeugt eine eigenständige (einzelne) HTML-Datei mit eingebetteten Daten.

Die hostbare App (dist/) lädt Daten per fetch() aus assets/*.json — das braucht einen
HTTP-Server (fetch() ab file:// ist wegen CORS blockiert). Für eine direkt klickbare,
einzelne Datei (doppelklick -> Browser öffnet) betten wir die Daten direkt ein.

Hinweis: Leaflet & MarkerCluster werden weiter von CDN geladen (benötigt Internet).
         Für 100% Offline (ohne CDN) müssten die Bibliotheken zusätzlich eingebettet werden.

Ausgabe: dist/index_singlefile.html  (funktioniert ab file:// mit Internetverbindung)

Nutzung: python3 scripts/bundle_singlefile.py
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

    injection = f"<script>\n{data_js}\n{meta_js}\n</script>\n"
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
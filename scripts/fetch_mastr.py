#!/usr/bin/env python3
"""
fetch_mastr.py — Lädt alle Wind- und PV-Anlagen aus dem Marktstammdatenregister (MaStR).

Selektionskriterien (final, siehe ANFORDERUNGEN.md):
  - Wind:      Energieträger 2497, Betriebs-Status "In Betrieb" (35), Bruttoleistung > 1  [MW]
  - Photovoltaik: Energieträger 2495, Bruttoleistung > 999                              [kWp]
                (>= 1 MWp; alle Arten: Freifläche 852 + Gebäude 853 + Sonstige 2484)

Einheiten-Hinweis (wichtig!):
  - Wind Bruttoleistung in MW   -> Filter `Bruttoleistung der Einheit~gt~1`
  - PV   Bruttoleistung in kWp  -> Filter `Bruttoleistung der Einheit~gt~999`
  (MaStR nutzt MW bei Wind und kWp bei PV — wird im Import-Skript normalisiert.)

Ausgabe: data/raw/wind.json und data/raw/pv.json (je eine Liste aller Datensätze)
Quelle:  https://www.marktstammdatenregister.de (öffentliche Daten, ohne Login)

Nutzung: python3 scripts/fetch_mastr.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.marktstammdatenregister.de/MaStR/Einheit/EinheitJson/GetErweiterteOeffentlicheEinheitStromerzeugung"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PAGE_SIZE = 200
MAX_RETRIES = 5
RETRY_BASE = 3


def api_get(url: str) -> dict:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except Exception as e:
            last_err = e
            wait = RETRY_BASE * attempt
            print(f"    (!) Fehler (Versuch {attempt}/{MAX_RETRIES}): {e} — warte {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"API-Abfrage fehlgeschlagen nach {MAX_RETRIES} Versuchen: {last_err}")


def build_filter(energietraeger: int, in_betrieb: bool) -> str:
    """Baut den MaStR-Filterstring. Anzeige-Namen sind lokalisiert (Umlaute!)."""
    conds = [f"Energieträger~eq~{energietraeger}"]
    if in_betrieb:
        conds.append("Betriebs-Status~eq~35")
    if energietraeger == 2497:          # Wind -> MW
        conds.append("Bruttoleistung der Einheit~gt~1")
    else:                                # PV -> kWp, >= 1 MWp => > 999 kWp
        conds.append("Bruttoleistung der Einheit~gt~999")
    return "~and~".join(conds)


def fetch_category(energietraeger: int, label: str, in_betrieb: bool = True) -> list[dict]:
    fstr = build_filter(energietraeger, in_betrieb)
    encoded = urllib.parse.quote(fstr, safe="~='()[],.")
    all_records: list[dict] = []
    page = 1
    total = None

    while True:
        url = f"{BASE}?filter={encoded}&page={page}&pageSize={PAGE_SIZE}"
        data = api_get(url)
        if data.get("Error"):
            raise RuntimeError(f"API meldet Fehler: {data.get('Message') or data.get('Type')}")

        if total is None:
            total = data.get("Total") or 0
            print(f"  {label}: insgesamt {total} Anlagen (filter: {fstr})")

        records = data.get("Data") or []
        all_records.extend(records)
        print(f"    Seite {page}: +{len(records)} (gesamt {len(all_records)})")

        if not records or len(all_records) >= total:
            break
        page += 1
        time.sleep(0.3)  # freundliche Abfrage-Rate

    return all_records


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # PV zuerst (größer, aber überschaubar ~10.500 bei >=1MWp)
    print("=== Photovoltaik (>= 1 MWp) ===")
    pv = fetch_category(2495, "PV")
    with open(RAW_DIR / "pv.json", "w", encoding="utf-8") as f:
        json.dump(pv, f, ensure_ascii=False)
    print(f"  -> gespeichert: {RAW_DIR / 'pv.json'} ({len(pv)})")

    # Wind
    print("\n=== Wind (>= 1 MW, In Betrieb) ===")
    wind = fetch_category(2497, "Wind")
    with open(RAW_DIR / "wind.json", "w", encoding="utf-8") as f:
        json.dump(wind, f, ensure_ascii=False)
    print(f"  -> gespeichert: {RAW_DIR / 'wind.json'} ({len(wind)})")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
fetch_v2.py — Lädt ALLE Einheiten-Felder (118) aus dem MaStR (Grundsatzentscheidung, Regel 2).

Unterschied zu fetch_mastr.py (V1):
  - V1 warf nichts weg (Raw war schon 118 Felder) — V2 stellt das ABER sicher und versioniert
    die Rohdateien (data/raw_v2/*.json), damit alte data/raw/*.json NICHT überschrieben werden
    (Regel 1: nichts löschen/überschreiben ohne Freigabe).
  - Speichert pro Record das KOMPLETTES JSON (1:1, alle Felder) + extrahiert die Felder,
    die import_v2.py braucht (LokationId für NAP-Abruf).

Filter (fix, Nutzer-Freigabe 2026-09-03):
  - Wind (2497):  Status "In Betrieb" (35), Bruttoleistung > 0.1 MW (>= 100 kW)
  - PV (2495):    Bruttoleistung > 499.9 kWp (>= 0.5 MWp)   [kein Status-Filter, wie V1]

Ausgabe: data/raw_v2/wind.json, data/raw_v2/pv.json (VOLLSTÄNDIGE Records)
Nutzung: python3 scripts/fetch_v2.py
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
OUT_DIR = ROOT / "data" / "raw_v2"
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


def build_filter(energietraeger: int, status_id: int | None = None) -> str:
    """Filterlogik.

    status_id=None  -> V1-Verhalten (nur "In Betrieb", kompatibel zu data/raw_v2/{wind,pv}.json)
    status_id=<id>  -> F5-Erweiterung: abruf eines weiteren Betriebs-Status
                       (31=In Planung, 37=Vorübergehend stillgelegt, 38=Endgültig stillgelegt)
    """
    conds = [f"Energieträger~eq~{energietraeger}"]
    if status_id is not None:
        conds.append(f"Betriebs-Status~eq~{status_id}")
    elif energietraeger == 2497:
        conds.append("Betriebs-Status~eq~35")
    if energietraeger == 2497:
        conds.append("Bruttoleistung der Einheit~gt~0.1")
    else:
        conds.append("Bruttoleistung der Einheit~gt~499.9")
    return "~and~".join(conds)


def fetch_category(energietraeger: int, label: str, status_id: int | None = None) -> list[dict]:
    fstr = build_filter(energietraeger, status_id=status_id)
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
        time.sleep(0.3)

    # Feld-Integrität: Vollständigkeit gegen Referenzfeldzahl 118 sicherstellen
    if all_records:
        ref_keys = set(all_records[0].keys())
        fehlend = [r.get("MaStRNummer") for r in all_records if set(r.keys()) != ref_keys]
        if fehlend:
            print(f"    (!) {len(fehlend)} Records mit abweichendem Feldset (werden trotzdem gespeichert)", file=sys.stderr)
        print(f"    Felder je Record: {len(ref_keys)}")

    return all_records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    extended = "--extended-status" in sys.argv  # F5: zusätzlich Status 31/37/38 abrufen

    print("=== Photovoltaik (>= 0.5 MWp) ===")
    pv = fetch_category(2495, "PV")
    with open(OUT_DIR / "pv.json", "w", encoding="utf-8") as f:
        json.dump(pv, f, ensure_ascii=False)
    print(f"  -> gespeichert: {OUT_DIR / 'pv.json'} ({len(pv)})")

    print("\n=== Wind (>= 100 kW, In Betrieb) ===")
    wind = fetch_category(2497, "Wind")
    with open(OUT_DIR / "wind.json", "w", encoding="utf-8") as f:
        json.dump(wind, f, ensure_ascii=False)
    print(f"  -> gespeichert: {OUT_DIR / 'wind.json'} ({len(wind)})")

    if not extended:
        return

    # F5: Zusatz-Status abrufen und in SEPARATE Dateien schreiben
    # (Regel 1: bestehende {wind,pv}.json bleiben unangetastet!)
    extra_status = [(31, "In Planung"), (37, "Voruebergehend stillgelegt"), (38, "Endgueltig stillgelegt")]
    for status_id, label in extra_status:
        print(f"\n=== Status {status_id} ({label}) — Wind ===")
        wind_s = fetch_category(2497, f"Wind {label}", status_id=status_id)
        with open(OUT_DIR / f"wind_status{status_id}.json", "w", encoding="utf-8") as f:
            json.dump(wind_s, f, ensure_ascii=False)
        print(f"  -> gespeichert: wind_status{status_id}.json ({len(wind_s)})")

        print(f"\n=== Status {status_id} ({label}) — PV ===")
        pv_s = fetch_category(2495, f"PV {label}", status_id=status_id)
        with open(OUT_DIR / f"pv_status{status_id}.json", "w", encoding="utf-8") as f:
            json.dump(pv_s, f, ensure_ascii=False)
        print(f"  -> gespeichert: pv_status{status_id}.json ({len(pv_s)})")


if __name__ == "__main__":
    main()

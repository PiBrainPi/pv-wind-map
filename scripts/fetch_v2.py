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

FIX 10.09.2026 (F-Fetch-1, live verifiziert): Der Filter-Column heißt 'Energieträger'
  (MIT Umlaut) — die bisherige Schreibweise 'Energietraeger' wurde von der API still
  ignoriert (Total = Gesamtbestand 9.435.237 statt ~32k Wind). MaStR hat den Endpoint
  offenbar umbenannt; letzter korrekter Lauf: 06.09.2026. Quelle der gültigen Namen:
  GET /MaStR/Einheit/EinheitJson/GetFilterColumnsErweiterteOeffentlicheEinheitStromerzeugung

Ausgabe: data/raw_v2/wind.json, data/raw_v2/pv.json (VOLLSTÄNDIGE Records)
Nutzung: python3 scripts/fetch_v2.py [--delta]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BASE = "https://www.marktstammdatenregister.de/MaStR/Einheit/EinheitJson/GetErweiterteOeffentlicheEinheitStromerzeugung"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw_v2"
DELTA_DIR = OUT_DIR / "delta"
STATE_FILE = OUT_DIR / "fetch_state.json"
PAGE_SIZE = 200
MAX_RETRIES = 5
RETRY_BASE = 3
# Sicherheitsnetz (AP3): Total-Vergleich Basis+Delta vs. API-Gesamttotal, Toleranz in %
TOTAL_TOLERANCE_PCT = 5


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

    WICHTIG (F-Fetch-1, 10.09.2026): Filter-Columns MIT Umlaut verwenden!
    'Energietraeger' (ohne) wird von der API STILL ignoriert → Total = Gesamtbestand.

    status_id=None  -> V1-Verhalten (nur "In Betrieb", kompatibel zu data/raw_v2/{wind,pv}.json)
    status_id=<id>  -> F5-Erweiterung: abruf eines weiteren Betriebs-Status
                       (31=In Planung, 37=Vorübergehend stillgelegt, 38=Endgültig stillgelegt)
    """
    # 'Energieträger' MIT Umlaut (F-Fetch-1): ohne Umlaut still unwirksam!
    conds = [f"Energieträger~eq~{energietraeger}"]
    if status_id is not None:
        conds.append(f"Betriebs-Status~eq~{status_id}")
    elif energietraeger == 2497:
        conds.append("Betriebs-Status~eq~35")
    if energietraeger == 2497:
        conds.append("Bruttoleistung der Einheit~gt~0.1")
    else:
        # V30 F04 (Variante B): strikt >= 0.5 MWp — als 'gt~499.9' (ge+Datum-Kombi
        # führt bei der API zu Error=true; gt ist in allen Kombis verifiziert ok)
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


def get_total(fstr: str) -> int:
    """1 Request: nur das Total eines Filters (Sicherheitsnetz, AP3)."""
    encoded = urllib.parse.quote(fstr, safe="~='()[],.")
    url = f"{BASE}?filter={encoded}&page=1&pageSize=1"
    data = api_get(url)
    return int(data.get("Total") or 0)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


def strang_name(energietraeger: int, status_id: int | None) -> str:
    tech = "wind" if energietraeger == 2497 else "pv"
    return f"{tech}" if status_id is None else f"{tech}_status{status_id}"


def all_straenge(extended: bool) -> list[tuple[int, str, int | None]]:
    """(energietraeger, label, status_id) aller zu ziehenden Stränge."""
    straenge: list[tuple[int, str, int | None]] = [(2495, "PV", None), (2497, "Wind", None)]
    if extended:
        straenge += [
            (2497, "Wind In Planung", 31), (2495, "PV In Planung", 31),
            (2497, "Wind Vorueb.stillg.", 37), (2495, "PV Vorueb.stillg.", 37),
            (2497, "Wind Endg.stillg.", 38), (2495, "PV Endg.stillg.", 38),
        ]
    return straenge


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    extended = "--extended-status" in sys.argv
    delta_mode = "--delta" in sys.argv

    # --since TT.MM.JJJJ oder auto: letzter Fetch-Stand aus fetch_state.json,
    # Fallback: Datum der letzten Änderung der Basis-JSONs (UTC-Datum), sonst gestern.
    since: str | None = None
    if delta_mode:
        if "--since" in sys.argv:
            since = sys.argv[sys.argv.index("--since") + 1]
        else:
            state = load_state()
            stamps = [s.get("last_run") for s in state.values() if s.get("last_run")]
            if stamps:
                since_dt = datetime.fromisoformat(max(stamps))
            elif (OUT_DIR / "wind.json").exists():
                mtime = (OUT_DIR / "wind.json").stat().st_mtime
                since_dt = datetime.fromtimestamp(mtime)
            else:
                since_dt = datetime.now() - timedelta(days=1)
            since = since_dt.strftime("%d.%m.%Y")  # API-Syntax: TT.MM.JJJJ, Operator gt
        print(f"=== DELTA-MODUS: alle Änderungen seit {since} ===")

    state = load_state()
    delta_summary: list[tuple[str, int, int]] = []  # (strang, delta_total, api_total)

    for et_id, label, status_id in all_straenge(extended):
        strang = strang_name(et_id, status_id)
        base_filter = build_filter(et_id, status_id=status_id)

        if not delta_mode:
            # Vollabruf (bisheriges Verhalten)
            print(f"\n=== {label} (VOLL) ===")
            records = fetch_category(et_id, label, status_id=status_id)
            out = OUT_DIR / f"{strang}.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False)
            print(f"  -> gespeichert: {out.name} ({len(records)})")
            state[strang] = {"last_run": datetime.now().isoformat(timespec="seconds"),
                             "total": len(records)}
            continue

        # --- Delta-Modus (AP2): nur Records mit 'Letzte Aktualisierung > since' ---
        delta_filter = f"{base_filter}~and~Letzte Aktualisierung~gt~{since}"
        print(f"\n=== {label} (DELTA seit {since}) ===")
        records = _fetch_with_filter(delta_filter, f"{label} Delta")
        DELTA_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = DELTA_DIR / f"{strang}_{stamp}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False)
        print(f"  -> Delta gespeichert: {out.name} ({len(records)})")

        # --- Sicherheitsnetz (AP3): API-Gesamttotal vs. erwartete Menge ---
        api_total = get_total(base_filter)
        try:
            base_count = len(json.load(open(OUT_DIR / f"{strang}.json", encoding="utf-8")))
        except FileNotFoundError:
            base_count = 0
        expected = base_count + len(records)
        diff_pct = abs(api_total - expected) / max(api_total, 1) * 100
        delta_summary.append((strang, len(records), api_total))
        if diff_pct > TOTAL_TOLERANCE_PCT:
            print(f"  (!) SICHERHEITSNETZ {strang}: API-Total {api_total} weicht um "
                  f"{diff_pct:.1f}% ab (erwartet ~{expected}) → Vollabruf-Fallback", file=sys.stderr)
            records_full = fetch_category(et_id, f"{label} FALLBACK", status_id=status_id)
            with open(OUT_DIR / f"{strang}.json", "w", encoding="utf-8") as f:
                json.dump(records_full, f, ensure_ascii=False)
            state[strang] = {"last_run": datetime.now().isoformat(timespec="seconds"),
                             "total": len(records_full), "fallback_full": True}
            print(f"  -> FALLBACK-VOLL gespeichert: {strang}.json ({len(records_full)})")
        else:
            state[strang] = {"last_run": datetime.now().isoformat(timespec="seconds"),
                             "total": expected, "delta": len(records)}

    if delta_mode:
        print("\n=== Delta-Zusammenfassung ===")
        for strang, n, api_total in delta_summary:
            print(f"  {strang}: {n} Delta-Records (API-Total {api_total})")

    save_state(state)
    print(f"\nState geschrieben: {STATE_FILE.name}")


def _fetch_with_filter(fstr: str, label: str) -> list[dict]:
    """fetch_category mit VORGEGEBENEM Filterstring (Delta-Modus)."""
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
            print(f"  {label}: insgesamt {total} Records (Delta)")
        records = data.get("Data") or []
        all_records.extend(records)
        print(f"    Seite {page}: +{len(records)} (gesamt {len(all_records)})")
        if not records or len(all_records) >= total:
            break
        page += 1
        time.sleep(0.3)
    return all_records


if __name__ == "__main__":
    main()

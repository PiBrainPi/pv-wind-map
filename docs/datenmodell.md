# Datenmodell — PV & Wind Karte (MaStR)

> Stand: 2026-08-29 · Zweisprachig (DE / EN)

## Datenbasis (DE)

Quelle: **Marktstammdatenregister (MaStR)** der Bundesnetzagentur — öffentliche Daten,
abgerufen über den JSON-Endpoint. Rohdaten liegen in `data/raw/{wind,pv}.json`.
Single Source of Truth (nach Import): `data/mastr.db` (SQLite).

### Tabelle `einheiten`

Eine Zeile je MaStR-Anlage. Normalisierte Felder:

| Spalte | Typ | Herkunft / Anmerkung |
|--------|-----|----------------------|
| `id` | INTEGER PK | auto |
| `mastr_nummer` | TEXT UNIQUE | `MaStRNummer` (z. B. `SEE940146675093`) |
| `einheit_name` | TEXT | `EinheitName` |
| `energietraeger_id` | INTEGER | 2495 = PV, 2497 = Wind |
| `energietraeger_name` | TEXT | `EnergietraegerName` |
| `art` | TEXT | PV: Freiflächen-/Gebäude-/Sonstige; Wind: an Land/auf See |
| `bruttoleistung_mw` | REAL | **normalisiert auf MW** (PV kWp→MW, Wind gemischt) |
| `betriebs_status` | TEXT | „In Betrieb“ (Standard) |
| `system_status` | TEXT | z. B. „Aktiviert“ |
| `inbetriebnahme_datum` | TEXT | ISO `YYYY-MM-DD` aus `/Date(millis)/` |
| `eeg_inbetriebnahme_datum` | TEXT | ISO |
| `letzte_aktualisierung` | TEXT | ISO |
| `bundesland` | TEXT | `Bundesland` |
| `landkreis` | TEXT | `Landkreis` |
| `gemeinde` | TEXT | `Gemeinde` |
| `plz` | TEXT | `Plz` |
| `ort` | TEXT | `Ort` |
| `strasse` | TEXT | `Strasse` |
| `lat` / `lon` | REAL | `Breitengrad` / `Laengengrad` (WGS84) |
| `geolokation` | INTEGER | 1 = lat+lon vorhanden, sonst 0 |
| `netzbetreiber` | TEXT | `NetzbetreiberNamen` (HTML-Tags entfernt) |
| `anlagenbetreiber` | TEXT | `AnlagenbetreiberName` |
| PV: `anzahl_solar_module` | INTEGER | `AnzahlSolarModule` |
| PV: `hauptausrichtung` | TEXT | `HauptausrichtungSolarModuleBezeichnung` |
| PV: `solarpark_name` | TEXT | `SolarparkName` |
| Wind: `nabenhoehe_m` | REAL | `NabenhoeheWindenergieanlage` |
| Wind: `rotordurchmesser_m` | REAL | `RotordurchmesserWindenergieanlage` |
| Wind: `lichte_hoehe_m` | REAL | `LichteHoehe` |
| Wind: `typenbezeichnung` | TEXT | `Typenbezeichnung` (z. B. V236-15MW) |
| Wind: `hersteller` | TEXT | `HerstellerWindenergieanlageBezeichnung` |
| Wind: `windpark_name` | TEXT | `WindparkName` |
| Wind: `land_oder_see` | TEXT | `WindAnLandOderSeeBezeichnung` |
| `lokation_nr` | TEXT | `LokationMastrNr` |
| `registrierungsdatum` | TEXT | ISO |

### Tabelle `metadaten`
Schlüssel-Wert-Paare: `stand` (Importzeitpunkt), `quelle`, `einheiten_pv`, `einheiten_wind`.

### Tabelle `update_log`
Historie der Importe: `timestamp`, `pv_count`, `wind_count`, `notes`.

## WICHTIG — Einheiten-Konvention (kritisch!)

Das MaStR ist **inkonsistent bei der Bruttoleistung**. Empirisch verifiziert:

- **PV**: Bruttoleistung in **kWp**. 1 MWp = 1000 kWp.
  - Beispielwerte: 1617 (= 1.6 MWp), 3000 (= 3 MWp), 749 (= 0.75 MWp).
- **Wind**: **gemischt**! Moderne und große Anlagen in **kW**:
  - V236-15MW (Vestas) = **15000** (kW) → 15 MW
  - SWT-6.0-154 (Siemens) = **6300** → 6.3 MW
  - E-126 (Enercon) = **7580** → 7.58 MW
  - V47 (Vestas) = **660** → 0.66 MW
  - E-53 (Enercon) = **800** → 0.8 MW
  - Einige Einträge liegen bereits in **MW** vor (z. B. 3.0, 4.5, 2.3).

### Normalisierungs-Heuristik (im Import)

```
PV:   value / 1000            (immer kWp)
Wind: value > 80  -> /1000    (kW)
      value <= 80 -> value    (ist bereits MW)
```

Begründung Schwellwert 80: Reale Einzel-WEA (≥ 100 kW) liegen bei 1..16 MW als MW-Wert,
sonst als kW (100..15000). Werte 81-99 als „MW" (z. B. 95, 100) sind falsch etikettierte
kW-Kleinstanlagen (≈ 0.1 MW) und werden korrekt als kW behandelt; Anlagen <100 kW
(Mikro-Windräder mit Werten wie 0.5) werden per Schwellwert-Anforderung ausgeschlossen.

### Selektionskriterien (final)

- **Wind**: ≥ 100 kW nach Normalisierung, Status „In Betrieb".
- **PV**: ≥ 0,5 MWp (Bruttoleistung ≥ 500 kWp), Status „In Betrieb".
- **Karte**: nur Anlagen mit vorhandener Geolokation (`geolokation=1`). Kein Geocoding.

## Aktuelle Datenkennzahlen (Import 2026-08-29)

| Kategorie | Gesamt in DB | Mit Geolokation |
|-----------|-------------|-----------------|
| Wind (≥100 kW) | 32.155 | 31.116 |
| PV (≥0,5 MWp) | 22.389 | 22.384 |
| **Summe** | **54.544** | **53.500** |

```sql
-- Beispiel für eigene Abfragen
SELECT energietraeger_name, COUNT(*) FROM einheiten GROUP BY energietraeger_name;
SELECT art, COUNT(*) FROM einheiten WHERE energietraeger_id=2495 GROUP BY art;
SELECT land_oder_see, COUNT(*) FROM einheiten WHERE energietraeger_id=2497 GROUP BY land_oder_see;
```

---

## Data Model (EN)

Source: **MaStR** (German Market Master Data Register, public). Single source of truth:
`data/mastr.db` (SQLite), after `import_mastr.py`.

### Critical: unit convention
MaStR reports capacity inconsistently:
- **PV**: in **kWp** (1 MWp = 1000 kWp).
- **Wind**: **mixed** — modern/large turbines in **kW** (V236-15MW = 15000 kW → 15 MW;
  V47 = 660 kW → 0.66 MW); a few entries already in MW (3.0, 4.5).

Normalization heuristic in import:
```
PV:   value / 1000            (always kWp)
Wind: value > 80  -> /1000    (kW)
      value <= 80 -> value    (already MW)
```
Rationale: real single turbines (≥ 100 kW) reach 1–16 MW as MW, or 100–15000 as kW.
Values 81–99 mislabeled as “MW” (≈ 0.1 MW micro-turbines) are treated as kW; units below
100 kW (micro-wind values like 0.5) are excluded by the threshold requirement.

### Selection (final)
- **Wind**: ≥ 100 kW (after normalization), status "In Betrieb".
- **PV**: ≥ 0.5 MWp (≥ 500 kWp), status "In Betrieb".
- **Map**: only geolocated units (`geolokation=1`). No geocoding.

### Current figures (import 2026-09-04, V19)
| Category | In DB | Georeferenced |
|----------|-------|---------------|
| Wind (≥100 kW) | 31,116 | 31,116 |
| PV (≥0.5 MWp) | 22,384 | 22,384 |
| **Total** | **65,659** | **65,659** |

> Stand 04.09.2026 (V19-Live-Datenstand): infobar „31.116 Wind · 22.384 PV".
> Historie inkl. Updates (NEU/ENTFERNT) → `assets/historie.json`; NAP-Index
> 27.078 → 27.870 NAPs (`assets/nap_index.json`). Import-Sektion oben dokumentiert
> den ersten Stand vom 29.08. — die Live-Zahlen folgen dem jeweils aktuellen Export.
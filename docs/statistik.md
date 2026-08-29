# Statistik-Panel — Betreiber & Größenklassen (PV & Wind Karte)

> Stand: 2026-08-29 · Zweisprachig (DE / EN)

## Überblick (DE)

Das Statistik-Panel ist ein Seiten-Overlay (Sidebar rechts) in der Karten-App. Es
beantwortet zwei Fragen:
1. **Betreiber-Statistik:** welcher im MaStR hinterlegte Betreiber wie viele Anlagen
   (und welche Gesamt-/durchschnittliche MW-Leistung) betreibt.
2. **Größenklassen:** wie sich die Anlagen je Technologie (Wind/PV) von 1 MW bis zur
   höchsten bekannten MW-Größe verteilen.

Öffnen: Klick auf **„📊 Statistik"** in der oberen Leiste.

### Betreiber-Tabelle

| Spalte | Beschreibung |
|--------|--------------|
| **Betreiber** | Name aus dem MaStR (`Anlagenbetreiber`); Badge ⚡=Wind, 🟠=PV, ⚡🟠=beides |
| **Anzahl** | Zahl der Anlagen dieses Betreibers |
| **Summe MW** | Gesamte Bruttoleistung aller Anlagen (MW) |
| **Ø MW** | Durchschnittliche Anlagengröße (MW) |

Bedienelemente (oberhalb der Tabelle):
- **Technologie-Filter** (Alle/Wind/PV)
- **Top-N-Auswahl** (Top 10 / 50 / 100 / Alle) — da über 14.000 Betreiber existieren
- **Textfilter** auf den Betreibernamen (akzent-/groß/klein-unabhängig)
- **Sortierung:** Klick auf einen Spaltenkopf (Sortierpfeil ▲/▼). Standard nach **Summe MW** absteigend.

Klick auf eine **Zeile** → die Karte zeigt nur die Anlagen dieses Betreibers
(bei 1 Anlage Fly-to + Popup, sonst Fit-Bounds). Panel schließt sich dabei.

### Hersteller-Tabelle (nur Wind)

| Spalte | Beschreibung |
|--------|--------------|
| **Hersteller** | Name aus dem MaStR (`HerstellerWindenergieanlageBezeichnung`) |
| **Anzahl / Summe MW / Ø MW** | wie bei Betreibern |

- **Nur Windkraftanlagen** — das MaStR enthält **keine** Herstellerangaben für PV
  (verifiziert: 0 von 9.589 PV-Anlagen). Hinweis-Feld im Tab erklärt das.
- **53 Hersteller** über 26.469 Windanlagen (99,6 % mit Angabe). Top: ENERCON (~9.987),
  Vestas (~5.773), Siemens Wind Power (~1.455), Nordex (~1.987), Senvion (~1.390).
- Bedienelemente wie bei Betreibern (Top-N, Textfilter, Spaltensortierung, Standard Summe MW).
- Klick auf eine **Zeile** → Karte zeigt nur die Windanlagen dieses Herstellers.

### Größenklassen-Diagramm

Achsen-gestütztes Balkendiagramm (rein CSS/HTML, keine externe Chart-Bibliothek — offline-fähig):
- Toggle **Wind/PV** und **Anlagen ⇄ Leistung (MW)**; je Technologie eigene Klassen-Staffelung
  von 1 MW bis zum realen Maximum.
- **Summary-Box** oben: Technologie, Gesamtanzahl, Gesamtleistung (MW), max. Einzelanlage (MW).
- **Achsen:** Y-Skala (0/50/100 % des Maximalwerts), Wert direkt **im** Balken (bei wenig Platz daneben),
  rechts außen der Sekundärwert. Beschriftung "MW"/"Anlagen" überall explizit.
- **Hover-Tooltip** mit Klasse, Anlagen, Leistung, Anteil an Anlagen & Leistung (incl. Hinweis,
  ob Balkenhöhe = Anlagen oder Leistung).

Datenbasis (Import 2026-08-29):
| | Wind | PV |
|---|---|---|
| Anlagen | 26.586 | 9.589 |
| Min | 1,0 MW | 1,0 MW |
| Max | 80 MW | 162,26 MW |

### Datenfluss & Implementierung
- `scripts/export_app.py` → `build_statistiken(db)` aggregiert aus SQLite: Betreiber
  (`name, anzahl, sum_mw, avg_mw, tech{pv,wind}`) und Größenklassen je Technologie
  (`label, anzahl, sum_mw, anteil_anzahl, anteil_summe`); schreibt `dist/assets/statistiken.json`.
- `src/index.html` lädt die Statistik (fetch im Host-Modus / eingebettet via `window.__PVWIND_STATS__`
  in der Single-File; `scripts/bundle_singlefile.py` bettet sie ein).
- **Wichtig (Datenkonsistenz):** Es wird nur `geolokation=1` betrachtet, konsistent zur Karte.
  Leere Größenklassen werden ausgelassen.
- **14.141 Betreiber** (Stand Import 2026-08-29) erfordern Lazy-Layout → Top-N + Filter, nicht
  Volltext-Tabelle.

---

## Overview (EN)

A right-side overlay panel answering two questions:
1. **Operator stats:** how many plants (and total/avg MW) each MaStR-registered operator runs.
2. **Size classes:** how plants distribute per technology from 1 MW up to the largest MW known.

Open via the **“📊 Statistik”** button in the top bar.

### Operator table
Columns: **Operator** (name + Wind/PV badges), **Count**, **Sum MW**, **Avg MW**.
Controls: technology filter, Top-N (10/50/100/All), live text filter, and click-to-sort
columns (default: Sum MW desc). Clicking a row filters the map to that operator’s plants.

### Manufacturer table (wind only)
Columns **Manufacturer / Count / Sum MW / Avg MW** and the same controls (Top-N, text filter, sorting).
**Wind only** — MaStR carries no manufacturer data for PV (verified: 0 of 9,589 PV plants).
53 manufacturers over 26,469 wind turbines (99.6% with an entry). Clicking a row filters the map
to that manufacturer’s turbines.

### Size-class chart
Axis-based horizontal bars (pure CSS/HTML, no chart library, offline-capable). Wind/PV toggle and
**Anlagen ⇄ Leistung (MW)** measure toggle; summary box (tech, total plants, total MW, max single plant);
y-axis scale (0/50/100% of max); value shown inside/next to each bar with explicit "MW"/"Anlagen" units;
hover tooltip with class, plants, MW, share of plants & of capacity.

### Implementation
`export_app.py::build_statistiken()` aggregates from SQLite → `dist/assets/statistiken.json`;
`src/index.html` consumes it (fetch or embedded `window.__PVWIND_STATS__` in the single-file);
`bundle_singlefile.py` embeds it. Only geolocated units are counted (consistent with the map).
14,141 operators ⇒ Top-N + filter are required for a responsive table.
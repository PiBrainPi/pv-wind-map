# Statistik-Panel — Betreiber & Größenklassen (PV & Wind Karte)

> Stand: 2026-08-29 · Zweisprachig (DE / EN)

## Überblick (DE)

Das Statistik-Panel ist ein Seiten-Overlay (Sidebar rechts) in der Karten-App. Es
beantwortet zwei Fragen:
1. **Betreiber-Statistik:** welcher im MaStR hinterlegte Betreiber wie viele Anlagen
   (und welche Gesamt-/durchschnittliche MW-Leistung) betreibt.
2. **Größenklassen:** wie sich die Anlagen je Technologie (Wind/PV) von der unteren
   Leistungsgrenze (Wind 0,1 MW / PV 1 MW) bis zur höchsten bekannten MW-Größe verteilen.

Öffnen: Klick auf **„📊 Statistik"** in der oberen Leiste.

### Betreiber-Tabelle

| Spalte | Beschreibung |
|--------|--------------|
| **Betreiber** | Name aus dem MaStR (`Anlagenbetreiber`); auf Teil vor Klammern gekürzt, voller Name im Tooltip. **Kein Technik-Badge/Emoji** (Entfernt 2026-08-29) |
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

### Hersteller-Tabelle (nur Wind) + Verteilungs-Pie-Chart

| Spalte | Beschreibung |
|--------|--------------|
| **Hersteller** | Name aus dem MaStR (`HerstellerWindenergieanlageBezeichnung`) |
| **Anzahl** | Zahl der Windanlagen dieses Herstellers |
| **Anteil** | %-Anteil an allen Windanlagen mit Herstellerangabe (Basis 30.947) |
| **Summe MW / Ø MW** | wie bei Betreibern |

- **Nur Windkraftanlagen** — das MaStR enthält **keine** Herstellerangaben für PV
  (verifiziert: 0 von 22.368 PV-Anlagen). Hinweis-Feld im Tab erklärt das.
- **63 Hersteller** über 30.947 Windanlagen (99,5 % mit Angabe). Top: ENERCON (~12.354 = 39,9 %),
  Vestas (~6.404 = 20,7 %), Nordex (~2.091 = 6,8 %), Siemens Wind Power (~1.465 = 4,7 %),
  Senvion (~1.413 = 4,6 %).
- Bedienelemente wie bei Betreibern (Top-N, Textfilter mit ✕-Button, Spaltensortierung inkl. Anteil, Standard Summe MW).
- **Formatierung wie Betreiber-Tabelle (identisches CSS):** Schriftgröße 13px, Zellpadding 7px 8px,
  Kopfzeilen-Hintergrund `#f7f9fc` + Klick-Cursor, rechtbündige Zahlen, Sortier-Pfeile ▲▼ (blau, bei Klick),
  Zeilen-Hover `#eef3ff`, Namens-Ellipsis in der ersten Spalte. Anzeigename auf Teil vor Klammern gekürzt
  (z. B. „ENERCON, Vestas" statt „ENERCON GmbH"), rechtliche Zusätze im Tooltip (title); **ohne Technik-Badge/Emoji**.
  Der volle Name bleibt für den Klick-Filter auf der Karte relevant.
- Klick auf eine **Zeile** → Karte zeigt nur die Windanlagen dieses Herstellers.

**Pie-Chart „Verteilung nach Hersteller"** (unter der Tabelle, beim Scrollen sichtbar):
- Interaktives **Donut-Diagramm** (Canvas, keine Chart-Bibliothek, offline-fähig).
- Zeigt die **Top-10 Hersteller einzeln** + Rest als „Übrige Hersteller" zusammengefasst; jedes Segment
  ist farbcodiert, die **zentrale Ziffer** im Loch zeigt die Gesamtzahl (30.947).
- **Hover** auf ein Segment (oder Legenden-Zeile) → Segment hebt sich hervor, Legende markiert.
- **Klick** auf Segment/Legende → Karte filtert auf die Anlagen genau dieses Herstellers (außer „Übrige").
- Legende rechts: Farbfeld + Name + Anlagenzahl + %-Anteil je Hersteller.
- Notiz unter dem Chart: „Anteil jedes Herstellers an allen 30.947 Windanlagen mit Herstellerangabe ·
  Top 10 einzeln, Rest zusammengefasst · Hover oder Legenden-Klick für Details."

### Größenklassen-Diagramm

Achsen-gestütztes Balkendiagramm (rein CSS/HTML, keine externe Chart-Bibliothek — offline-fähig):
- Toggle **Wind/PV** und **Anlagen ⇄ Leistung (MW)**; je Technologie eigene Klassen-Staffelung
  von 0,1 MW (Wind) / 1 MW (PV) bis zum realen Maximum.
- **Summary-Box** oben: Technologie, Gesamtanzahl, Gesamtleistung (MW), max. Einzelanlage (MW).
- **Achsen:** Y-Skala (0/50/100 % des Maximalwerts), Wert direkt **im** Balken (bei wenig Platz daneben),
  rechts außen der Sekundärwert. Beschriftung "MW"/"Anlagen" überall explizit.
- **Hover-Tooltip** mit Klasse, Anlagen, Leistung, Anteil an Anlagen & Leistung (incl. Hinweis,
  ob Balkenhöhe = Anlagen oder Leistung).

Datenbasis (Import 2026-08-29, Wind ≥100 kW / PV ≥0,5 MWp):
| | Wind | PV |
|---|---|---|
| Anlagen | 31.114 | 22.368 |
| Min | 0,1 MW | 0,5 MW |
| Max | 80 MW | 162,26 MW |

### Datenfluss & Implementierung
- `scripts/export_app.py` → `build_statistiken(db)` aggregiert aus SQLite: Betreiber
  (`name, anzahl, sum_mw, avg_mw, tech{pv,wind}`), Hersteller (`name, anzahl, sum_mw, avg_mw`; nur Wind),
  und Größenklassen je Technologie (`label, anzahl, sum_mw, anteil_anzahl, anteil_summe`);
  schreibt `dist/assets/statistiken.json`.
- `src/index.html` lädt die Statistik (fetch im Host-Modus / eingebettet via `window.__PVWIND_STATS__`
  in der Single-File; `scripts/bundle_singlefile.py` bettet sie ein).
- **Wichtig (Datenkonsistenz):** Es wird nur `geolokation=1` betrachtet, konsistent zur Karte.
  Leere Größenklassen werden ausgelassen.
- **23.216 Betreiber** (Stand Import 2026-08-29) erfordern Lazy-Layout → Top-N + Filter, nicht
  Volltext-Tabelle.

### Fehlerbehebungen (2026-08-29)
- **`gesamt.wind_anzahl`/`pv_anzahl` waren falsch** (26.768/10.437 statt 26.586/9.589): die Summe
  lief über alle Betreiber-Einträge mit `tech[wind]`, womit Mehrfach-Technologie-Betreiber doppelt
  in die Wind-Zahl zählten. Fix: **Direktzählung** aus SQLite (`COUNT(*) WHERE geolokation=1 AND …`).
  Aktueller Wert (≥100-kW-Schwelle): `herstellbar_wind` = **30.947** (= Summe der Hersteller, konsistent).
- **Doppeltes „Anlagen" im Größenklassen-Sublabel** („Anlagen: 5.014 Anlagen" im Leistungs-Modus):
  Label-Text wurde aus einem bereits mit „Anlagen" suffizierten Wert erzeugt.
- **Pie-Canvas:** `#hersteller-pie` muss ein `<canvas>`-Element sein (nicht `<div>`), sonst
  `getContext is not a function`.

---

## Overview (EN)

A right-side overlay panel answering two questions:
1. **Operator stats:** how many plants (and total/avg MW) each MaStR-registered operator runs.
2. **Size classes:** how plants distribute per technology from the lower threshold
   (wind 0.1 MW / PV 1 MW) up to the largest MW known.

Open via the **“📊 Statistik”** button in the top bar.

### Operator table
Columns: **Operator** (name truncated before parentheses, no tech badge), **Count**, **Sum MW**, **Avg MW**.
Controls: technology filter, Top-N (10/50/100/All), live text filter, and click-to-sort
columns (default: Sum MW desc). Clicking a row filters the map to that operator’s plants.

### Manufacturer table (wind only) + share pie-chart
Columns **Manufacturer / Count / Share / Sum MW / Avg MW** and the same controls (Top-N, text filter with ✕,
sorting incl. share). Share = % of all wind plants with a manufacturer entry (base 30,947).
**Wind only** — MaStR carries no manufacturer data for PV (verified: 0 of 22,368 PV plants).
63 manufacturers over 30,947 wind turbines (99.5% with an entry). Clicking a row filters the map
to that manufacturer’s turbines.

**“Distribution by manufacturer” donut chart** below the table (visible when scrolling):
interactive Canvas donut (no chart library, offline-capable). Top-10 manufacturers shown individually,
remainder aggregated as “Übrige Hersteller”; central figure in the hole shows the total (30,947).
Hover highlights the segment + legend row; clicking a segment/legend row filters the map to that
manufacturer. Right-side legend shows color swatch, name, plant count and % share per manufacturer.

### Size-class chart
Axis-based horizontal bars (pure CSS/HTML, no chart library, offline-capable). Wind/PV toggle and
**Anlagen ⇄ Leistung (MW)** measure toggle; summary box (tech, total plants, total MW, max single plant);
y-axis scale (0/50/100% of max); value shown inside/next to each bar with explicit "MW"/"Anlagen" units;
hover tooltip with class, plants, MW, share of plants & of capacity.

### Implementation
`export_app.py::build_statistiken()` aggregates from SQLite → `dist/assets/statistiken.json`;
`src/index.html` consumes it (fetch or embedded `window.__PVWIND_STATS__` in the single-file);
`bundle_singlefile.py` embeds it. Only geolocated units are counted (consistent with the map).
23,216 operators ⇒ Top-N + filter are required for a responsive table.

### Bugfixes (2026-08-29)
- `gesamt.wind_anzahl` / `pv_anzahl` were wrong (26,768 / 10,437 instead of 26,586 / 9,589) because the
  sum ran over all operator entries with a wind tech badge, double-counting multi-tech operators.
  Fixed by **direct COUNT(*) from SQLite**. Current value (≥100 kW threshold): `herstellbar_wind` = 30,947.
- Duplicate “Anlagen” in the size-class sublabel (Leistung mode).
- `#hersteller-pie` must be a `<canvas>` element (not `<div>`), else `getContext is not a function`.
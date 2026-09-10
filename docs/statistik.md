# Statistik-Panel — Betreiber & Größenklassen (PV & Wind Karte)

> Stand: 2026-09-09 (V32.1: NAP-Klick → Kartenfokus) · Zweisprachig (DE / EN)

## Überblick (DE)

Das Statistik-Panel ist ein Seiten-Overlay (Sidebar rechts, 820 px, PC) in der Karten-App.
Es umfasst **11 Tabs** (V28 + V31 Typ-Tab; Prüfung 08.09.2026 DOM-verifiziert): Betreiber, Hersteller, **Typ (V31)**, **Größenklassen**,
Bundesländer, **Landkreis** (V23), **NAP-Ranking** (V28), Spannungsebenen, Update-Historie, Zubau,
**⚠ Betroffenheit**.
Kernfragen:
1. **Betreiber-Statistik:** welcher im MaStR hinterlegte Betreiber wie viele Anlagen
   (und welche Gesamt-/durchschnittliche MW-Leistung) betreibt.
2. **Größenklassen:** wie sich die Anlagen je Technologie (Wind/PV) von der unteren
   Leistungsgrenze (Wind 0,1 MW / PV 0,5 MWp) bis zur höchsten bekannten MW-Größe verteilen —
   **wahlweise pro Einheit oder pro Park (aggregiert, V22)**.

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
| **Anteil** | %-Anteil an allen Windanlagen mit Herstellerangabe (Basis 30.847, V30) |
| **Summe MW / Ø MW** | wie bei Betreibern |

- **Nur Windkraftanlagen** — das MaStR enthält **keine** Herstellerangaben für PV
  (verifiziert: 0 von 22.402 PV-Anlagen, V30). Hinweis-Feld im Tab erklärt das.
- **61 Hersteller** über 30.847 Windanlagen (99,5 % mit Angabe, V30-Export). Top:
  ENERCON (~12.316 = 39,9 %), Vestas, Nordex, Siemens Wind Power, Senvion (Reihenfolge
  wie V27 — Details live im Tab).
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
  ist farbcodiert, die **zentrale Ziffer** im Loch zeigt die Gesamtzahl (30.847).
- **Hover** auf ein Segment (oder Legenden-Zeile) → Segment hebt sich hervor, Legende markiert.
- **Klick** auf Segment/Legende → Karte filtert auf die Anlagen genau dieses Herstellers (außer „Übrige").
- Legende rechts: Farbfeld + Name + Anlagenzahl + %-Anteil je Hersteller.
- Notiz unter dem Chart: „Anteil jedes Herstellers an allen 30.847 Windanlagen mit Herstellerangabe ·
  Top 10 einzeln, Rest zusammengefasst · Hover oder Legenden-Klick für Details."

### Größenklassen-Diagramm

Achsen-gestütztes Balkendiagramm (rein CSS/HTML, keine externe Chart-Bibliothek — offline-fähig):
- **Drei Toggles:** **Wind / PV / Wind + PV** (Tech), **Anlagen ⇄ Leistung (MW)** (Measure) und
  seit **V22** die **Basis „Einzelanlagen ⇄ Parks aggregiert"** (teal hervorgehoben):
  - *Einzelanlagen* (Default): Register-Perspektive — jede MaStR-Einheit zählt einzeln.
  - *Parks aggregiert (V22):* Betreiber-Perspektive — zusammengehörige Einheiten (Splittungen!)
    werden über den Schlüssel **(Energieträger, Betreiber, Parkname)** zu einem Park summiert.
    Grund: Das MaStR zersplittert große Parks in viele Einheiten (Beispiel Solarpark Döllen =
    13 Einheiten à 7,4–31,4 MW, real **154,8 MW**). Nur so sind Kritis-Objekte (≥ 104 MW,
    BSI-KritisV) im Diagramm real sichtbar: 5 einzelne Einheiten vs. **52 Cluster**
    (u. a. Borkum Riffgrund 3, 83 EH = 958,7 MW). Parkname = `solarpark_name`/`windpark_name`,
    sonst normalisiertes Namens-Präfix („Döllen II - Block …" → „Döllen"); namenlose Einheiten
    bleiben einzeln. Ein Hinweis-Kasten erklärt die Basis, wenn „Parks aggregiert" aktiv ist.
    **Alle Klassen werden immer gelistet** (auch leere) — nötig für die Kritis-Sichtbarkeit.
- **Summary-Box** oben: Technologie, **Anlagen bzw. Parks**, Gesamtleistung (MW),
  max. Einzelanlage bzw. max. Park (MW).
- **Kritis-Markierung:** Klassen `104–150` und `150+` rot (🔴) mit KRITIS-Badge — in beiden Basen.
- **Art-Donut** unter den Balken: bleibt immer auf **MaStR-Einheiten**-Basis (Titel trägt bei
  „Parks aggregiert" den Zusatz „(MaStR-Einheiten)").
- **Achsen:** Y-Skala (0/50/100 % des Maximalwerts), Wert direkt **im** Balken (bei wenig Platz daneben),
  rechts außen der Sekundärwert. Beschriftung "MW"/"Anlagen" überall explizit.
- **Hover-Tooltip** mit Klasse, Anlagen/Parks, Leistung, Anteil an Anlagen & Leistung (incl. Hinweis,
  ob Balkenhöhe = Anlagen oder Leistung).
- **Balken-Klick → Karte (V23):** Jede Balkenzeile ist klickbar; die Karte zeigt alle Einheiten
  der Klasse (Label + fitBounds). Im **Wind + PV**-Modus entscheidet die Klick-Position:
  Wind-Balkenabschnitt → nur Wind, PV-Abschnitt → nur PV, Zeile/Label → beide. In der
  Cluster-Basis wird die **Park-MW** (`pkmw`) geprüft — Klick auf „150+" zeigt z. B. alle
  13 Döllen-Einheiten.

### Landkreis-Tabelle (V23)

Neuer Tab (zwischen Bundesländer und Spannungsebenen), Design analog Hersteller-Tabelle:

| Spalte | Beschreibung |
|--------|--------------|
| **Landkreis** | Name (klickbare Zeile → Karte zeigt nur Anlagen dieses LK) |
| **Anzahl / MW gesamt** | PV + Wind kombiniert |
| **PV Anzahl / MWp** | nur Photovoltaik (Header: „Leistung PV (MWp)", seit V24) |
| **Wind Anzahl / MW** | nur Wind (Header: „Leistung Wind (MW)", seit V24) |
| **NAP Anzahl / Gesamtleistung NAP (MW)** | Netzanschlusspunkte im LK (Join über numerische LokationId) |

Header sortierbar (Default: MW gesamt absteigend), **Gesamt**-Summenzeile unten,
Zähler-Zeile („377 Landkreise · …"). Datenbasis (V30-Export, 08.09.): 377 LKs ·
51.634 Assets · 125.552,1 MW · 27.338 NAPs · 260.567.403,7 NAP-MW. **Seit V24:** `table-layout:fixed`
mit festen Spaltenverhältnissen — die 9 Spalten passen ohne horizontales Scrollen in die
805-px-Panel-Breite (V24-Paket 2, alle 9 Tabs browser-verifiziert overflow-frei).
**Mobile (V25):** Bei ≤767 px wird die Tabelle über `#landkreis-scroll` horizontal
 scrollbar (Touch-Wischen) und erhält `min-width:860px` mit `table-layout:auto` —
 die Header bleiben vollständig lesbar, ein Hinweis „← seitlich wischen →" erscheint
 unter der Tabelle. PC-Ansicht unverändert (kein Scroll).

Datenbasis (V30-Export 2026-09-08, In-Betrieb-Kern 31.011 Wind · 22.402 PV = 53.413, geolokation=1):
| | Wind | PV |
|---|---|---|
| Einheiten | 31.011 | 22.402 |
| Max Einheit | 15 MW | 162 MW |
| Max Park (Cluster) | 959 MW | 198 MW |

### NAP-Ranking-Tabelle (V28, V32-Klick-Verhalten)

Alle 27.130 Netzanschlusspunkte mit angeschlossener Leistung, Gesellschaften, Bundesland.
Klick auf den **NAP-Namen** (V32): Karte zeigt **ausschließlich die Anlagen dieses NAPs**
(selectHersteller-Muster: `renderMarkers(grp.units)` + fitBounds + Suchfeld-Label
"NAP: <name> (N Anlagen)") und das NAP-Gruppen-Panel öffnet sich. Klick auf das
**Bundesland** filtert die Karte auf alle NAPs dieses Bundeslandes (wie bisher).
Suche mit Live-Suggest (Bundesländer zuerst, dann NAP-Namen).

### Datenfluss & Implementierung
- `scripts/export_app.py` → `build_statistiken(db)` aggregiert aus SQLite: Betreiber
  (`name, anzahl, sum_mw, avg_mw, tech{pv,wind}`), Hersteller (`name, anzahl, sum_mw, avg_mw`; nur Wind),
  Größenklassen je Technologie (`label, anzahl, sum_mw, anteil_anzahl, anteil_summe`) und
  **seit V22** `groessen_cluster` (gleiche Struktur, aber auf Park-Cluster-Basis; dazu
  `gesamt.wind_cluster_max_mw`/`pv_cluster_max_mw`/`*_n_cluster`); **seit V23** `landkreise`
  (377 LKs inkl. NAP-Anzahl/-MW, Join über numerische LokationId) und `gemeinden`
  (6.499, mit BL/LK-Kontext); schreibt `dist/assets/statistiken.json`.
- `src/index.html` lädt die Statistik (fetch im Host-Modus / eingebettet via `window.__PVWIND_STATS__`
  in der Single-File; `scripts/bundle_singlefile.py` bettet sie ein).
- **Wichtig (Datenkonsistenz):** Es wird nur `geolokation=1` betrachtet, konsistent zur Karte.
  **Alle Größenklassen werden immer gelistet** (auch leere) — Kritis-Klassen müssen sichtbar bleiben.
  Ältere `statistiken.json` ohne `groessen_cluster` → UI fällt automatisch auf Einzelanlagen zurück.
- **23.225 Betreiber** (Stand Import 2026-09-01) erfordern Lazy-Layout → Top-N + Filter, nicht
  Volltext-Tabelle.

### Fehlerbehebungen (2026-08-29)
- **`gesamt.wind_anzahl`/`pv_anzahl` waren falsch** (26.768/10.437 statt 26.586/9.589): die Summe
  lief über alle Betreiber-Einträge mit `tech[wind]`, womit Mehrfach-Technologie-Betreiber doppelt
  in die Wind-Zahl zählten. Fix: **Direktzählung** aus SQLite (`COUNT(*) WHERE geolokation=1 AND …`).
  Aktueller Wert (≥100-kW-Schwelle, V30): `herstellbar_wind` = **30.847** (= Summe der Hersteller, konsistent).
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

**Nine tabs** (as of V23): Operator, Manufacturer, **Size classes**, Federal states,
**District (Landkreis, V23)**, Voltage levels, Update history, Commissioning,
**⚠ Impact analysis**.

Open via the **“📊 Statistik”** button in the top bar.

### Operator table
Columns: **Operator** (name truncated before parentheses, no tech badge), **Count**, **Sum MW**, **Avg MW**.
Controls: technology filter, Top-N (10/50/100/All), live text filter, and click-to-sort
columns (default: Sum MW desc). Clicking a row filters the map to that operator’s plants.

### Manufacturer table (wind only) + share pie-chart
Columns **Manufacturer / Count / Share / Sum MW / Avg MW** and the same controls (Top-N, text filter with ✕,
sorting incl. share). Share = % of all wind plants with a manufacturer entry (base 30,847, V30).
**Wind only** — MaStR carries no manufacturer data for PV (verified: 0 of 22,402 PV plants).
61 manufacturers over 30,847 wind turbines (99.5% with an entry). Clicking a row filters the map
to that manufacturer’s turbines.

**“Distribution by manufacturer” donut chart** below the table (visible when scrolling):
interactive Canvas donut (no chart library, offline-capable). Top-10 manufacturers shown individually,
remainder aggregated as “Übrige Hersteller”; central figure in the hole shows the total (30.847).
Hover highlights the segment + legend row; clicking a segment/legend row filters the map to that
manufacturer. Right-side legend shows color swatch, name, plant count and % share per manufacturer.

### Size-class chart
Axis-based horizontal bars (pure CSS/HTML, no chart library, offline-capable). **Three toggles:**
Wind/PV/Wind+PV (tech), **Anlagen ⇄ Leistung (MW)** (measure), and — since **V22** — the
**basis toggle “Einzelanlagen ⇄ Parks aggregiert”** (units vs. aggregated parks): the register view
counts each MaStR unit separately, the park view sums split registrations into one park per
(energy carrier, operator, park name) — e.g. Solarpark Döllen = 13 units, 154.8 MW combined.
Critical classes (104–150, 150+ MW, BSI-KritisV) are highlighted red in both bases; the type donut
below always remains unit-based (title suffix “(MaStR-Einheiten)” in park mode). Summary box (tech,
plants/parks, total MW, max single plant/park); y-axis scale (0/50/100% of max); value shown
inside/next to each bar with explicit units; hover tooltip with class, plants/parks, MW, shares.

**V23 — bar click → map:** every bar row is clickable; the map shows all units of that class.
In the Wind+PV mode the click target decides: the wind bar segment → wind only, the PV segment
→ PV only, the row/label → both. In the park basis the check uses the park MW (`pkmw`), so
clicking “150+” shows all 13 Döllen units.

### District table (Landkreis, V23)
Nine sortable columns (design identical to the manufacturer table): district, plants combined
(count + MW), PV (count + MW), wind (count + MW), NAP count, NAP total MW. Default sort:
combined MW descending; **Gesamt** sum row at the bottom; clicking a row filters the map to
that district (same behavior as the geo search). Data basis (V30, Sep 8): 377 districts · 51,634 units ·
133,875 MW · 27,313 NAPs (NAP join via numeric LokationId).

### NAP ranking table (V28, V32 click behaviour)

All 27,130 grid connection points with connected capacity, companies, federal state.
Clicking the **NAP name** (V32): the map shows **only the assets of this NAP**
(selectHersteller pattern: `renderMarkers(grp.units)` + fitBounds + search label
"NAP: <name> (N assets)") and the NAP group panel opens. Clicking the **federal state**
filters the map to all NAPs of that state (as before). Search with live suggest.

### Implementation
`export_app.py::build_statistiken()` aggregates from SQLite → `dist/assets/statistiken.json`
(since V22 including `groessen_cluster` — park-level distribution with the same class scale and
`kritis` flags; since V23 also `landkreise` (377 incl. NAP count/MW) and `gemeinden` (6,499 with
BL/LK context)); `src/index.html` consumes it (fetch or embedded `window.__PVWIND_STATS__` in the
single-file); `bundle_singlefile.py` embeds it. Only geolocated units are counted (consistent with
the map). Older exports without `groessen_cluster` make the UI fall back to the unit basis.
23,216 operators ⇒ Top-N + filter are required for a responsive table.

### Bugfixes (2026-08-29)
- `gesamt.wind_anzahl` / `pv_anzahl` were wrong (26,768 / 10,437 instead of 26,586 / 9,589) because the
  sum ran over all operator entries with a wind tech badge, double-counting multi-tech operators.
  Fixed by **direct COUNT(*) from SQLite**. Current value (≥100 kW threshold, V30): `herstellbar_wind` = 30,847.
- Duplicate “Anlagen” in the size-class sublabel (Leistung mode).
- `#hersteller-pie` must be a `<canvas>` element (not `<div>`), else `getContext is not a function`.
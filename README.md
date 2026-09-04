# PV & Wind Karte (MaStR)

Interaktive Karte aller **Wind- und Photovoltaikanlagen** in Deutschland aus dem
**Marktstammdatenregister (MaStR)** der Bundesnetzagentur.

**🌐 Live im Internet:** **[https://wind-pv-map.ingenieur-tools.de/](https://wind-pv-map.ingenieur-tools.de/)**
(Portal: [https://ingenieur-tools.de/](https://ingenieur-tools.de/))

**Lokale Live-Ansicht (Single-File):** `dist/index_singlefile.html` — einfach im Browser öffnen
(Internet für die Kartenkacheln von OpenStreetMap nötig). Hosting-Details: `docs/DEPLOYMENT.md`.

## Funktionen

- 🗺️ Interaktive Karte (Leaflet) mit automatischem Clustering — Deutschland-Übersicht bis Einzelpunkt
- 🔍 **Suche mit Autocomplete:** Tippe Teil eines Anlagenamen ein (z. B. „Döllen") → Vorschläge ab
  2 Zeichen; sucht auch im Solarpark-/Windpark-, Gemeinde- **und Betreibernamen**, akzent-/groß-/klein-unabhängig
  („dol" findet „Döllen"). Auswahl per Klick oder Pfeiltasten+Enter → Fly-to + Popup. ✕-Button leert die Suche.
- ⛁ **Betreiber-Suche:** Gib einen Text ein, der im Betreibernamen vorkommt (z. B. „CEE") → oben im Dropdown
  erscheint „Betreiber: N Betreiber · M Anlagen in ganz Deutschland — alle anzeigen". Ein Klick filtert **alle**
  Anlagen aller Betreiber, deren Name den Text enthält (auch über ganz Deutschland verteilt), und zeigt sie
  gebündelt auf der Karte (Fit-Bounds). Ideal für Konzerne/SPVs mit mehreren Assets.
- 🎯 Klick auf Anlage → Detail-Popup mit allen MaStR-Daten (MaStR-Nr., Leistung, Standort, Netzbetreiber,
  Betreiber, **Inbetriebnahme TT.MM.JJJJ, Spannungsebene, NAP-Nummer klickbar → alle Anlagen am selben
  Netzanschlusspunkt auf der Karte**, wind-/PV-spezifische Felder)
- 🔍 **Filter (4):** Typ (Wind/PV), Bundesland (inkl. Offshore), **Art des Assets** (Freiflächen-/Gebäude-/Sonstige Solaranlage, Windkraft an Land/auf See) und **Leistung (MW)** in festen Größenklassen `[von, bis)`:
  `0.1–0.5 · 0.5–1 · 1–2 · 2–5 · 5–10 · 10–30 · 30–60 · 60–100 · 100–104 · 104–150 · 150+`
  (Wind ≈ Nennleistung/MW, PV = MWp — das MaStR unterscheidet nicht zwischen AC/DC; **Kritis-Schwelle: erst ab 104 MW** nach BSI-KritisV → nur `104–150` und `150+` sind Kritis). Sobald ein Art-/Bundesland-/Leistungs-Filter gesetzt ist, zeigt ein Badge neben dem Leistungs-Dropdown die **Anzahl der aktuell sichtbaren Anlagen** (`Anzahl: n` — zählt **alle** gesetzten Filter inkl. Wind/PV, konsistent mit den Marker-Clustern).
- 📊 **Statistik-Panel** (8 Tabs): Betreiber-Tabelle (Live-Suggest-Filter mit Betreibergruppen 👥 /
  Portfolios 📁 — Gruppen zuerst, 250 ms Debounce ab 2 Zeichen; Zahlformat 1 Nachkommastelle;
  Klick auf Zeile/Name → alle Anlagen des Betreibers/der Gruppe auf der Karte),
  Hersteller-Tab (nur Wind, + %-Anteil + interaktiver Donut), **Größenklassen-Diagramme** (Toggle
  Wind / PV / Wind + PV) mit fester Leistungsskala und Kritis-Markierung (ab 104 MW, BSI-KritisV),
  **Bundesländer-Tab** (interaktives Donut-Chart mit Wind/PV/Gesamt-Modus, Anlagen/Leistung-Umschalter,
  Klick → Karten-Filter), **Update-Historie** (Revisions-Tracker mit Snapshot-Vergleich, Delta-Summary,
  Verlauf-Tabelle, Bundesländer-Veränderung, Zeitleiste, Asset-Detail mit Deeplinks).

- 📱 **Responsive Design:** 3 Breakpoints (PC ≥1024px: Stats-Panel 700px, Tablet 768–1023px: 560px,
  Mobile <768px: Vollbild + Topbar/Toolbar-Anpassungen). Kein horizontaler Scroll auf PC bei Statistik-Tabellen.
- 🥧 **Art-Verteilungs-Pie:** Donut-Charts unter den Größenklassen-Balken zeigen Anlagen-/Leistungsverteilung
  pro Anlagentyp (Wind: Land/See; PV: Freifläche/Gebäude/Sonstige).
- 📅 **Registrierungs-Filter:** Dropdowns für Jahr (2019–2026) und Monat (1–12) filtern Anlagen nach
  Registrierungsdatum im MaStR. Kombinierbar mit allen anderen Filtern.
- 📅 **Inbetriebnahme-Filter:** Dropdowns für Jahr (1983–2026, dynamisch generiert) und Monat (1–12)
  filtern nach Inbetriebnahmedatum. Unabhängig von Registrierungs-Filter, kombinierbar mit allen anderen.
- 📋 **Alle-Anlagen-Tabelle:** Button "Alle Anlagen anzeigen" öffnet ein Overlay mit allen gefilterten
  Anlagen in einer professionellen Tabelle (12 Spalten, sortierbar nach jedem Header, Chunk-Rendering;
  Klick auf Asset-NAME oder 📍-Koordinaten → Karte zoomt hin + Popup, alle gefilterten Marker bleiben;
  Inbetriebnahme-Sortierung numerisch nach Jahr/Monat).
- 📈 **Zubau-Tab:** 6. Statistik-Tab mit zwei Sub-Tabs ("Registrierungsdatum" 2019–2026 und
  "Inbetriebnahmedatum" 1983–2026). Beide Sub-Tabs enthalten identisch aufgebaute 6 Charts:
  gestapeltes Balkendiagramm (Wind+PV), PV/Wind einzeln mit Trendlinie, Bundesländer-Heatmap
  (Rot→Gelb→Grün, sqrt-skaliert), Zubauraten (YoY-Wachstum %), Wachstum gegenüber kumuliertem Bestand.
  Toggle Anlagen/Leistung (MW). Senkrechte X-Achsen-Labels, Werte horizontal oberhalb der Balken;
  in den 2 Liniencharts (Zubauraten, kumuliertes Wachstum) stehen die senkrechten y-Wert-Labels
  ÜBER dem Datenpunkt (negative Werte: darunter).
- ⚡ **NAP-Gruppenansicht (V12):** Toggle zeigt Gruppen-Badges aller Anlagen am selben
  Netzanschlusspunkt; Panel listet alle Anlagen je Anschlusspunkt (Multi-NAP-Unterstützung).
- 📉 **Spannungsebenen-Filter (V10):** Dropdown (Mittel-/Hoch-/Höchstspannung, NS, 3 Umspann-
  ebenen, „ohne Angabe") via NAP-Join (99 % Abdeckung), Statistik-Tab + Tabellen-Spalte „Ebene".
- ⚠️ **Betroffenheits-Tab (V13–V19):** Referenzsuche (Anlage > Betreibergruppe > Portfolio >
  Betreiber > NAP) prüft Neu-/Entfernt-Updates aus der Historie gegen den Bestand — Match via
  NAP-Gleichheit **oder** Haversine-Umkreis (2–50 km, Default 20 km, Radius-Ringe um die
  getroffenen Bestandsanlagen). Vergleichstabelle Bestand↔Neu (Betreiber, Asset mit
  Karten-Deeplink, Anschlussleistung MW/MWp, Match-Kriterium + Distanz), „🗺️ Anzeigen"
  blendet alle betroffenen Assets ohne Filter-Schnittmenge und ohne Clustering ein,
  „Betroffene Gesellschaften" zählt über die Bestandsanlagen des Portfolios. Zeitfenster-
  Wahl (letztes/alle Updates). Expliziter Hinweis: **Indikation, keine rechtsverbindliche
  Auskunft** (Luftlinie ≠ Netztopologie; geplante Anlagen ohne NAP werden über die
  Geolokation geprüft).

---

## Schnellstart (Build)

Ein-Befehl-Build (fetch → import → export → bundle, Single-File inklusive):

```bash
bash scripts/build.sh
```

Oder einzeln, wenn du die Schritte nachvollziehen willst:
```bash
# 1. Daten aus dem MaStR laden (Wind >= 100 kW, PV >= 0.5 MWp, In Betrieb)
python3 scripts/fetch_mastr.py       # → data/raw/wind.json + pv.json
# 2. In SQLite importieren (Single Source of Truth)
python3 scripts/import_mastr.py      # → data/mastr.db
# 3. Export für die Karten-App (nur Anlagen mit Geolokation + Statistik)
python3 scripts/export_app.py        # → dist/assets/*.json
# 4. Hostbare App bauen
mkdir -p dist/assets && cp src/index.html dist/index.html
# 5. Optional: eigenständige Einzel-Datei (direkt klickbar, Daten eingebettet)
python3 scripts/bundle_singlefile.py # → dist/index_singlefile.html
# 6. Lokal testen (hostbare Version braucht einen HTTP-Server)
python3 -m http.server --directory dist 8080
# öffne http://localhost:8080
```

## Update (manuell, cronjob-fähig)

Die Pipeline ist nicht-interaktiv und damit direkt als Cronjob verwendbar
(Hinweis: in Cron auf dem Pi5 kein `execute_code` nutzen — nur shell/Python).

```bash
bash scripts/build.sh   # fetch + import + export + bundle in einem Schritt
```

## Datenbasis & Abgrenzung

| Kategorie | Umfang | In DB | Mit Geolokation |
|-----------|--------|-------|-----------------|
| **Wind** | ≥ 100 kW (nach Einheiten-Normalisierung MW), Status „In Betrieb“ | 32.155 | 30.996 |
| **Photovoltaik** | ≥ 0,5 MWp (Bruttoleistung ≥ 500 kWp), Status „In Betrieb“ | 22.389 | 22.384 |
| **Gesamt** | | **54.544** | **53.380** |

- **Geolokation**: nur Anlagen MIT vorhandenen Koordinaten im MaStR (kein Geocoding)
- **Einheiten-Hinweis**: MaStR liefert PV in kWp und Wind gemischt (kW/MW) — der Import normalisiert auf MW (Details: docs/datenmodell.md)
- **Quelle**: Marktstammdatenregister (MaStR), BNetzA, öffentliche Daten
- **Lizenz**: Datenlizenz Deutschland – Namensnennung – Version 2.0 (DL‑DE‑BY‑2.0), siehe https://www.govdata.de/dl-de/by-2-0
- **Hinweis zu Betreiberdaten**: Die Karte zeigt Betreibernamen (Feld `ab`) aller Anlagen, einschließlich
  natürlicher Personen (das MaStR kennzeichnet diese teils als „natürliche Person (…)"). Die Anzeige ist
  datenschutzrechtlich vertretbar, weil das Marktstammdatenregister ein gesetzlich öffentliches Register
  ist (Veröffentlichungspflicht, EnWG) und die Daten unter der DL‑DE‑BY‑2.0‑Lizenz veröffentlicht sind;
  es werden keine privaten Adressen oder Standorte natürlicher Personen angezeigt (nur der Anlagen-Standort).

## Dokumentation

- [ANFORDERUNGEN.md](ANFORDERUNGEN.md) – Anforderungen (A1–A11)
- [ENTSCHEIDUNGEN.md](ENTSCHEIDUNGEN.md) – Architektur-Entscheidungen
- [PLAN.md](PLAN.md) – 30-Schritt-Plan
- [docs/PROJEKTSTAND.md](docs/PROJEKTSTAND.md) – **aktueller Projektstand (Handover für neue Sessions)**
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) – **GitHub-Pages-Deployment + Domain-Anbindung**
- [docs/](docs/) – detaillierte Doku (Architektur, Datenmodell, Update, Hosting, Fehlerbehebung, Statistik)

## Lizenz

MIT
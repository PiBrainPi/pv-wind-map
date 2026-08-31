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
  Betreiber, wind-/PV-spezifische Felder)
- 🔍 **Filter (4):** Typ (Wind/PV), Bundesland (inkl. Offshore), **Art des Assets** (Freiflächen-/Gebäude-/Sonstige Solaranlage, Windkraft an Land/auf See) und **Leistung (MW)** in festen Größenklassen `[von, bis)`:
  `0.1–0.5 · 0.5–1 · 1–2 · 2–5 · 5–10 · 10–30 · 30–60 · 60–100 · 100–104 · 104–150 · 150–200 · 200+`
  (Wind ≈ Nennleistung/MW, PV = MWp — das MaStR unterscheidet nicht zwischen AC/DC; Klassen ab `100–104` betreffen **Kritis-Schwellwerte**). Sobald ein Art-/Bundesland-/Leistungs-Filter gesetzt ist, zeigt ein Badge neben dem Leistungs-Dropdown die **Anzahl der aktuell sichtbaren Anlagen** (`Anzahl: n` — zählt **alle** gesetzten Filter inkl. Wind/PV, konsistent mit den Marker-Clustern).
- 📊 **Statistik-Panel:** Betreiber-Tabelle (Filter, Top-N, Sortierung, Klick → Karte) und Hersteller-Tab
  (nur Wind, + %-Anteil + interaktiver Donut). **Größenklassen-Diagramme** (Toggle **Wind / PV / Wind + PV**)
  mit fester Leistungsskala `[von, bis)` (Min 0.1 MW bis `200+`); **Kritis-Klassen** (`100–104 · 104–150 ·
  150–200`) sind 🔴 rot markiert mit KRITIS-Badge; „Wind + PV" zeigt beide Technologien gemeinsam.
  Anlagen ⇄ Leistung (MW)-Umschalter.

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
| **Wind** | ≥ 100 kW (nach Einheiten-Normalisierung MW), Status „In Betrieb“ | 32.144 | 31.114 |
| **Photovoltaik** | ≥ 0,5 MWp (Bruttoleistung ≥ 500 kWp), Status „In Betrieb“ | 22.371 | 22.368 |
| **Gesamt** | | **54.515** | **53.482** |

- **Geolokation**: nur Anlagen MIT vorhandenen Koordinaten im MaStR (kein Geocoding)
- **Einheiten-Hinweis**: MaStR liefert PV in kWp und Wind gemischt (kW/MW) — der Import normalisiert auf MW (Details: docs/datenmodell.md)
- **Quelle**: Marktstammdatenregister (MaStR), BNetzA, öffentliche Daten
- **Lizenz**: Datenlizenz Deutschland – Namensnennung – Version 2.0 (DL‑DE‑BY‑2.0), siehe https://www.govdata.de/dl-de/by-2-0

## Dokumentation

- [ANFORDERUNGEN.md](ANFORDERUNGEN.md) – Anforderungen (A1–A11)
- [ENTSCHEIDUNGEN.md](ENTSCHEIDUNGEN.md) – Architektur-Entscheidungen
- [PLAN.md](PLAN.md) – 30-Schritt-Plan
- [docs/PROJEKTSTAND.md](docs/PROJEKTSTAND.md) – **aktueller Projektstand (Handover für neue Sessions)**
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) – **GitHub-Pages-Deployment + Domain-Anbindung**
- [docs/](docs/) – detaillierte Doku (Architektur, Datenmodell, Update, Hosting, Fehlerbehebung, Statistik)

## Lizenz

MIT
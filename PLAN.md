# 30-Schritt-Plan — PV & Wind Karte (MaStR)

> Stand: 2026-08-29 · Status: **V1 umgesetzt (Karte + Suche + Statistik) — Feinschliff & Hosting offen**
> Ziel: Interaktive, hostbare HTML-Karte aller deutschen Wind- & PV-Anlagen
> aus dem Marktstammdatenregister, mit lokaler Datenbasis und Update-Pipeline.

## Fortschritt

**Abgeschlossen (V1):** Schritte 1–17, 21, 24–26, 28 (teilw.) — inkl. zusätzlicher Features,
die über den ursprünglichen Plan hinausgehen:
- **Suche mit Autocomplete** + ✕-Button (Schritt 17 erweitert)
- **Statistik-Panel** (Betreiber-Tabelle + Größenklassen) — siehe `dokumente/PLAN_STATISTIK.md`

**Ergebnis:** funktionierende Karten-App (Leaflet + MarkerCluster) mit 40.703
georeferenzierten Anlagen (31.114 Wind ≥100 kW + 9.589 PV ≥1 MWp), Single-File
`dist/index_singlefile.html` (direkt klickbar) und hostbarer Version in `dist/`.
Pipeline: `build.sh` = `fetch → import → export → bundle`. Doku zweisprachig in `docs/`.

**Noch offen:** Feinschliff-QA (Schritt 20), Cron-Live Einrichtung (Teil von 21/23),
Hosting live schalten (Schritt 27 — nur vorbereitet, bewusst nicht live), vollständige
Fremdverifikation (Schritt 28/29), Launch (Schritt 30).

## Phasenübersicht

| Phase | Schritte | Thema |
|-------|----------|-------|
| A | 1–5 | Fundament & Anforderungen |
| B | 6–11 | Lokale Datenbasis (SQLite) |
| C | 12–17 | Frontend & Karte |
| D | 18–20 | Qualität, Design, Tests |
| E | 21–23 | Update-Fähigkeit & Automatisierung |
| F | 24–27 | Git, Build & Hosting |
| G | 28–30 | Doku-Abschluss & Launch |

---

## Phase A — Fundament & Anforderungen (1–5)

### Schritt 1: Projekt-Scaffolding
- [x] Ordner `~/Projects/pv-wind-map/` + `dokumente/` angelegt
- [x] `git init` (main), Git-Identity geprüft
- [ ] README.md, .gitignore, LICENSE (MIT) anlegen, erster Commit
- **Verifikation:** `git log --oneline` zeigt Initial-Commit

### Schritt 2: Anforderungen dokumentieren
- [x] `ANFORDERUNGEN.md` (Pflichtanforderungen A1–A10)
- [ ] Mit User final abnehmen („Letzte Iterationsschleife“)

### Schritt 3: Entscheidungslog anlegen
- [ ] `ENTSCHEIDUNGEN.md`: offene Fragen, getroffene Entscheidungen, Begründungen
- **Verifikation:** Alle offenen Fragen aus ANFORDERUNGEN §6 sind beantwortet

### Schritt 4: MaStR-Datenquellen erkunden
- [ ] JSON-Endpunkt (siehe Recherche: `GetErweiterteOeffentlicheEinheitStromerzeugung`) — Feldliste, Filter, Pagination, Limits
- [ ] XML-Komplettdownload (`/MaStR/Datendownload`) — Größe, Struktur, Aktualität
- [ ] Vergleich: JSON (inkrementell, filterbar) vs. XML (Vollabzug) → Empfehlung dokumentieren
- **Verifikation:** Stichprobe heruntergeladen; Feld- und Größen-Notizen in `docs/`

### Schritt 5: Datenqualitäts-Analyse (Stichprobe)
- [ ] Stichprobe PV + Wind ziehen: Wie viel % haben Koordinaten? Status-Verteilung? Leistungsspreizung?
- [ ] Erkenntnisse in `docs/datenqualitaet.md` festhalten — **entscheidet über Geocoding-Strategie**
- **Verifikation:** Zahlen pro Energieträger im Doku-File

---

## Phase B — Lokale Datenbasis (6–11)

### Schritt 6: SQLite-Datenmodell entwerfen
- [ ] Tabellen: `einheiten` (alle MaStR-Felder), `lokationen`, `metadaten` (Datenstand, Quelle), `update_log`
- [ ] Indexe: MaStRNummer (unique), Energieträger, Bundesland/Landkreis/Gemeinde, Status, Leistung, Koordinaten
- **Verifikation:** `sqlite3 data/mastr.db ".schema"` zeigt alle Tabellen

### Schritt 7: Download-Skript bauen (`scripts/fetch_mastr.py`)
- [ ] Paginierte JSON-Abfrage für Energieträger „Solare Strahlungsenergie“ + „Wind“ (Onshore/Offshore)
- [ ] Robustheit: Retry, Rate-Limit, Fortsetzen nach Abbruch, Logging
- **Verifikation:** Skript lädt N Seiten und schreibt Roh-JSON nach `data/raw/`

### Schritt 8: Import-Pipeline bauen (`scripts/import_mastr.py`)
- [ ] JSON → SQLite (normalisieren, Datenformate bereinigen, Datum konvertieren)
- [x] **Leistungsgrenze anwenden:** nur Anlagen mit Bruttoleistung ≥ 100 kW (Wind) bzw. ≥ 1 MWp (PV)
- [x] Upsert (MaStRNummer unique), Duplikat-Schutz
- **Verifikation:** Zählwerte in DB == Zähler aus MaStR (gefiltert auf ≥100 kW Wind); 0 Duplikat-Fehler

### Schritt 9: Koordinaten-Abgrenzung (nur vorhandene Geolokation)
- [ ] **Geocoding ist bewusst AUS** (Entscheidung 1). Anlagen ohne Koordinaten werden NICHT aufgelöst.
- [ ] Import speichert auch Anlagen ohne Koordinaten, kennzeichnet sie jedoch `geolokation=0`
- [ ] Frontend zeichnet deshalb nur Anlagen mit `geolokation=1`; Karte/Doku weist sichtbar auf die Abgrenzung hin
- **Verifikation:** Karte zeigt keine erfundenen Positionen; Statistik „Anlagen mit/ohne Koordinaten“ korrekt

### Schritt 10: Datenqualitäts-Report
- [ ] `scripts/quality_report.py`: Prüfungen (Anlagen mit/ohne Koordinaten, Leistung<1 MW-Werte, Datum vor 1990, Status-Konsistenz)
- [ ] Ausgabe als Markdown/HTML — wird bei jedem Update mitgeliefert
- **Verifikation:** Report zeigt 0 kritische Fehler

### Schritt 11: Datenstands-Verwaltung
- [ ] `metadaten`-Tabelle: letzter Abruf, Quellen-URL, Anzahl je Kategorie, Hash der Quelle
- [ ] Delta-Update-Logik (`update_log`): Was hat sich seit letztem Stand geändert?
- **Verifikation:** Nach erneutem Lauf zeigt `update_log` „keine Änderungen“ bzw. korrekte Deltas

---

## Phase C — Frontend & Karte (12–17)

### Schritt 12: Karten-Technologie festlegen
- [ ] Vergleich: **Leaflet + MarkerCluster** (einfach, offline-fähig) vs. **MapLibre GL + PMTiles/VTiles** (skaliert zu Mio. Punkten)
- [ ] Kriterien: Punktzahl (Mio.), Hosting (statisch), Offline, Entwicklungsaufwand
- [ ] Entscheidung dokumentiert → Standard: Leaflet + Cluster für V0; PMTiles-Erweiterung als Option
- **Verifikation:** Entscheidung in `ENTSCHEIDUNGEN.md`

### Schritt 13: HTML-Gerüst bauen (`src/index.html`)
- [ ] Basis: KartenContainer, Toolbar, Legende, Datenstand-Anzeige, mobil-responsiv
- [ ] Keine externen Datenbanken im V0 — App lädt optimerte JSON-Daten
- **Verifikation:** Datei öffnet sich im Browser, Karte rendert

### Schritt 14: Export-Skript (`scripts/export_app.py`)
- [ ] SQLite → kompaktes JSON (nur Felder für die Karte + Popup), optional gzip
- [ ] Bei Mio. Punkten: Vorab-Clusterung / Raster-Aggregation für Zoomstufen
- **Verifikation:** Export-Datei lädt in der App; Größe angemessen (< 50 MB, Ziel < 10 MB)

### Schritt 15: Karten-Rendering & Clustering
- [ ] Punkte + Cluster für PV (viele) und Wind (einzeln ab hohem Zoom)
- [ ] Maßstabsabhängige Darstellung (Zoom-Out = Raster/Heatmap, Zoom-In = Einzelpunkte)
- [ ] Maßstabbalken, Zoom-Controls
- **Verifikation:** Pan/Zoom flüssig; Cluster-Zähler korrekt

### Schritt 16: Detailansicht (Popup/Seitenpanel)
- [ ] Alle MaStR-Felder pro Anlage: MaStR-Nr, Name, Typ, Leistung (brutto/EEG), Status, Inbetriebnahme, Gemeinde/PLZ/LKreis, Netzbetreiber, Koordinaten-Typ
- [ ] Klickbare Links ins MaStR (Detailseite) wo möglich
- **Verifikation:** Stichprobe von 5 Anlagen vs. MaStR abgeglichen

### Schritt 17: Filter & Suche
- [ ] Filter: Energieträger (Wind/PV), Bundesland, Landkreis, Gemeinde, Leistungsklassen, Status, Koordinaten-Typ
- [x] **Suche mit Autocomplete:** Anlagename, Solarpark-/Windpark- und Gemeindenamen, akzent-/groß/klein-unabhängig (z. B. „Döll"/„dol" → „Döllen II..."), Vorschläge ab 2 Zeichen, Pfeiltasten+Enter, Klick → Fly-to + Popup
- [x] **✕-Button im Suchfeld:** leert Eingabe, setzt Karte auf alle Anlagen zurück
- **Verifikation:** Jeder Filter liefert erwartete Ergebnismenge

---

## Phase D — Qualität, Design, Tests (18–20)

### Schritt 18: UI/UX-Verfeinerung
- [ ] Dark/Light-Mode, Legende, Maßstab, Zugänglichkeit
- [ ] Optimierung für mobile Geräte (Touch, Layout)
- **Verifikation:** Screenshot-Prüfung Desktop + Mobil

### Schritt 19: Performance-Optimierung
- [ ] Lazy-Loading, Rendering-Tuning (Canvas/DOM-Ansatz), Dateigröße prüfen
- [ ] Messung: Ladezeit, Interaktions-FPS bei 100k+/1M+ Punkten
- **Verifikation:** Zielwerte dokumentiert und erreicht

### Schritt 20: Harte Prüfung (QA)
- [ ] Testplan (manuell+skriptbasiert): Vollständigkeit vs. MaStR, Filter, Suche, Detailansicht, Update-Verlauf (Simulation)
- [ ] Daten-Integritätstests (pytest) für Skripte
- **Verifikation:** Alle QA-Punkte grün; Abweichungen dokumentiert

---

## Phase E — Update-Fähigkeit (21–23)

### Schritt 21: Update-Skript & Automatisierung (manuell, cronjob-fähig)
- [ ] `scripts/update.sh` → fetch → import → export → test (ein Befehl, **ohne Interaktion**, damit als Cron verwendbar)
- [ ] Cron-Vorlage in `docs/` hinterlegen (crontab-Eintrag + Hinweis auf Pi5-Pflichten `execute_code` nicht nutzen → shell/Python-Skript)
- **Verifikation:** `update.sh` läuft von Anfang bis Ende durch (trockener Lauf + echter Lauf)

### Schritt 22: Datenstand in der App anzeigen
- [ ] „Stand: 2026-08-29 · 1.234.567 Anlagen“ + Changelog (aus `update_log`)
- [ ] Hinweis bei veraltetem Stand (älter als X Tage)
- **Verifikation:** App zeigt korrekten Stand nach Update

### Schritt 23: Regression nach Update
- [ ] Nach jedem Update: Quality-Report + Spot-Checks (Anzahl, neue Anlagen sichtbar)
- [ ] Automatische Benachrichtigung bei auffälligen Deltas (z. B. Telegram)
- **Verifikation:** Update-Changelog dokumentiert

---

## Phase F — Git, Build & Hosting (24–27)

### Schritt 24: Repo-Ordnung & Lizenz
- [ ] Ordnerstruktur final (README, docs/, scripts/, src/, data/, dist/, tests/)
- [ ] MIT-Lizenz, .gitignore (data/, secrets, caches); große Daten NICHT committen
- **Verifikation:** `git status` sauber; `data/` ausgeschlossen

### Schritt 25: Git-Workflow
- [ ] Konvention: `feat/fix/docs/chore`, semantische Tags (z. B. `v0.1.0`)
- [ ] Datenstände als Tag/Milestone dokumentieren (nicht die DB committen)
- **Verifikation:** Commit-Historie nachvollziehbar

### Schritt 26: Build-Prozess
- [ ] `scripts/build.sh` erzeugt `dist/` (HTML + Daten + Assets, alles relativ, offline-fähig)
- [ ] Optional: Single-File-Bundle (alles in eine HTML) für einfache Verteilung
- **Verifikation:** `dist/` funktioniert von `file://` UND über jeden Static-Server

### Schritt 27: Hosting vorbereiten (nicht live)
- [ ] Ziel: App als **statische Site** hostbar; Doku für GitHub Pages (öffentlich) UND eigenen Server (Pi5/Cloudflare) fertig
- [ ] Relative Pfade, `dist/` von jedem Static-Server lauffähig
- [ ] **Kein Live-Deployment** in dieser Iteration — Hosting später, sobald User entscheidet
- **Verifikation:** `dist/` läuft lokal über `python3 -m http.server` + auf GitHub-Pages-Struktur prüfbar

---

## Phase G — Doku-Abschluss & Launch (28–30)

### Schritt 28: Detaillierte Doku
- [ ] docs/architektur.md, docs/datenmodell.md, docs/update.md, docs/hosting.md, docs/fehlerbehebung.md — **je DE + EN**
- [ ] README mit Quickstart („Daten laden“, „Update“, „Bauen“, „Hosting vorbereiten“) — DE + EN
- **Verifikation:** Fremdperson (oder zweiter LLM) kann Projekt ohne Nachfragen benutzen

### Schritt 29: Verfizierung & Freigabe (le tzte I terationsschleife)
- [ ] Anforderungen A1–A10 gegen Plan checken, Lücken schließen
- [ ] Brutal ehrliche Review: was fehlt noch, was ist überflüssig?
- **Verifikation:** Abhaken-Liste komplett; Freigabe durch User

### Schritt 30: Launch & Übergabe (lokal)
- [ ] Projekt fertig für lokale Nutzung & Doku; Hosting dokumentiert (nicht live)
- [ ] Wartungsplan: Update-Rhythmus (manuell, Cron-fähig), Verantwortlichkeiten
- **Verifikation:** Launch-Checkliste abgearbeitet, Übergabe-Notiz an User

---

## Entscheidungen (verabschiedet)

1. **Koordinaten:** nur vorhandene Geolokation; kein Geocoding → Schritt 9 angepasst.
2. **Leistungsgrenze:** ≥ 100 kW (Wind) / ≥ 1 MWp (PV) → Schritt 8 angepasst.
3. **Repo/Hosting:** lokal; zweisprachige Doku (DE+EN); Hosting nur vorbereitet → Schritte 27, 28.
4. **Update:** manuell auslösbar, cronjob-fähig → Schritte 21, 23.

## Offene Fragen an den User (abgeklärt)

- ~~PV ohne Koordinaten?~~ → **entschieden:** nur vorhandene
- ~~Repo öffentlich/privat?~~ → **entschieden:** lokal, Hosting vorbereitet
- ~~Update-Rhythmus?~~ → **entschieden:** manuell, Cron-fähig
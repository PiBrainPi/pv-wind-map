# 30-Schritt-Plan — PV & Wind Karte (MaStR)

> Stand: 2026-08-29 · Status: Entwurf zur Freigabe
> Ziel: Interaktive, hostbare HTML-Karte aller deutschen Wind- & PV-Anlagen
> aus dem Marktstammdatenregister, mit lokaler Datenbasis und Update-Pipeline.

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
- [ ] Upsert (MaStRNummer unique), Duplikat-Schutz
- **Verifikation:** Zählwerte in DB == Zähler aus MaStR; 0 Duplikat-Fehler

### Schritt 9: Geocoding-Strategie umsetzen
- [ ] Entscheidung aus Schritt 5 umsetzen (Gemeinde-Centric / Nominatim-OSM / nur präzise)
- [ ] Bei Gemeinde-Ebene: Gemeinde-Centroid aus offenem Datensatz (z. B. OSM/BKG) nutzen
- [ ] Ergebnis als Attribut `koordinaten_typ` (exakt / gemeinde / keine) speichern
- **Verifikation:** Anteil fehlender Koordinaten deutlich reduziert; Report wird aktualisiert

### Schritt 10: Datenqualitäts-Report
- [ ] `scripts/quality_report.py`: Prüfungen (fehlende Koordinaten, Leistung=0, Datum vor 1990, Status-Konsistenz)
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
- [ ] Suche: Ort/PLZ/MaStR-Nr/Einheitname
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

### Schritt 21: Update-Skript & Automatisierung
- [ ] `scripts/update.sh` → fetch → import → geocode → export → test (ein Befehl)
- [ ] Cron-Anbindung Pi5 (z. B. monatlich; analog bestehender MSCI-Charts-Cron)
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

### Schritt 27: Hosting einrichten
- [ ] Ziel: GitHub Pages (öffentlich, kostenlos) oder eigener Server (Pi5, Cloudflare) — Entscheidung mit User
- [ ] HTTPS, Cusom-Domaine wenn gewünscht, Deployment-Anleitung in docs/
- **Verifikation:** Live-URL aufrufbar; Datenstand sichtbar

---

## Phase G — Doku-Abschluss & Launch (28–30)

### Schritt 28: Detaillierte Doku
- [ ] docs/architektur.md, docs/datenmodell.md, docs/update.md, docs/hosting.md, docs/fehlerbehebung.md
- [ ] README mit Quickstart („Daten laden“, „Update“, „Bauen“, „Deploen“)
- **Verifikation:** Fremdperson (oder zweiter LLM) kann Projekt ohne Nachfragen benutzen

### Schritt 29: Verfizierung & Freigabe (le tzte I terationsschleife)
- [ ] Anforderungen A1–A10 gegen Plan checken, Lücken schließen
- [ ] Brutal ehrliche Review: was fehlt noch, was ist überflüssig?
- **Verifikation:** Abhaken-Liste komplett; Freigabe durch User

### Schritt 30: Launch & Übergabe
- [ ] Hosting live, Repo veröffentlicht (falls gewünscht), Doku verlinkt
- [ ] Wartungsplan: Update-Rhythmus, Verantwortlichkeiten
- **Verifikation:** Launch-Checkliste abgearbeitet, Übergabe-Notiz an User

---

## Annahmen (vorläufig, werden in Schritt 3 verabschiedet)

1. Standard-Darstellung: „In Betrieb“-Anlagen; andere Status als Filter.
2. PV ohne Koordinaten → Gemeinde-Ebene (kein teures/risikantes Geocoding aller Adressen in V0).
3. Frontend: Leaflet + Clustering zunächst; skallerbare Erweiterung (PMTiles) erst bei Bedarf.
4. Sprache der künftigen öffentlichen Doku: **Englisch** (bei öffentlichem Repo); intern deutsch erlaubt.
5. Keine sensiblen Daten im Repo: keine Adressen-Dumps, keine MaStR-Keys.

## Offene Fragen an den User

1. PV ohne Koordinaten: Gemeinde-Ebene ok, oder jede Adresse per Geocoding auflösen?
2. Repo öffentlich (GitHub Pages, Doku dann Englisch) oder privat (eigenes Hosting)?
3. Update-Rhythmus: automatisch per Pi5-Cron (monatlich) oder manuell?
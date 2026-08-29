# Anforderungen — PV & Wind Karte (MaStR)

> Status: **Brainstorming / Entwurf** · Stand: 2026-08-29
> Dieses Dokument lebt und wird im Laufe des Projekts ergänzt.

## 1. Zielbild

Eine interaktive Karte, die **alle** im Marktstammdatenregister (MaStR) der
Bundesnetzagentur registrierten **Wind- und Photovoltaikanlagen** anzeigt —
mit allen relevanten Stammdaten pro Anlage.

## 2. Pflichtanforderungen

| ID | Anforderung | Beschreibung |
|----|-------------|--------------|
| A1 | **HTML-Datei** | Das Ergebnis ist eine (weitgehend) eigenständige HTML-App, die im Browser läuft. |
| A2 | **Interaktive Karte** | Pan/Zoom, Klick auf Anlage → Detailinfos. |
| A3 | **Alle Wind- & PV-Anlagen (≥1 MW)** | Alle MaStR-Anlagen der Energieträger Wind (Onshore/Offshore) und Photovoltaik — **nur Bruttoleistung ≥ 1 MW (Wind) bzw. ≥ 1 MWp (PV)**. Kleinere (v. a. Dach-)Anlagen sind bewusst ausgeschlossen. |
| A4 | **Vollständige Infos** | Standort (Gemeinde, PLZ, Landkreis, Bundesland, Adresse), Größe/Leistung (Bruttoleistung, EEG-Leistung), Status, Inbetriebnahme, MaStR-Nr., Netzbetreiber usw. — alles, was MaStR liefert. |
| A5 | **Update-Fähigkeit** | Datenbasis muss bei Bedarf aktualisierbar sein (ohne Neuentwicklung). Vorbereitet für spätere Automatisierung (Cronjob), aber initial manuell auslösbar. |
| A6 | **Datengrundlage MaStR** | Quelle: Marktstammdatenregister der Bundesnetzagentur (öffentliche Daten / Webdienst / Download). |
| A7 | **Lokale Datenbasis** | Alle Assets werden in einer lokalen Datenbank (SQLite) gespeichert — als Single Source of Truth. |
| A8 | **Lokales Git-Projekt** | Projekt liegt lokal in `~/Projects/pv-wind-map/` mit git-Versionierung. |
| A9 | **Detaillierte Doku** | Architektur, Datenmodell, Update-Anleitung, Hosting-Vorbereitung, Fehlerbehebung. **Deutsch und Englisch** (zweisprachig). |
| A10 | **Hostbar (vorbereitet)** | Die App soll als statische Site hostbar sein. Hosting wird nur **vorbereitet** (nicht live geschaltet), kann später erfolgen — Doku dafür fertig. |
| A11 | **Nur vorhandene Geolokation** | Um für Anlagen werden nur koordinierte gezeichnet; keine Geocoding-Auflösung fehlender Koordinaten. |

## 3. Datenquelle: Marktstammdatenregister (MaStR)

- Betreiber: Bundesnetzagentur
- Web: https://www.marktstammdatenregister.de
- Zugangswege:
  1. **Öffentliche JSON-Endpunkte** (z. B. `EinheitJson/GetErweiterteOeffentlicheEinheitStromerzeugung`) — paginiert, filterbar, kein Login. **Gewählt.**
  2. Kompletter Datenexport (XML) — für Einmal-Initialisierung möglich, aber unnötig groß.
  3. Webdienst (SOAP/API) mit Key — nicht nötig.

### Wichtige Daten-Fakten (verifiziert, Details in docs/datenmodell.md)

- **Einheiten-Konvention:** PV-Bruttoleistung in **kWp**; Wind **gemischt** (kW/MW).
  → Import normalisiert auf **MW** (Heuristik: PV /1000; Wind >80 → /1000).
- Selektionsfilter (final):
  - Wind: `Energieträger~eq~2497~and~Betriebs-Status~eq~35~and~Bruttoleistung der Einheit~gt~1`
  - PV:   `Energieträger~eq~2495~and~Betriebs-Status~eq~35~and~Bruttoleistung der Einheit~gt~999`
- **Anzahl (Import 2026-08-29):** Wind ≥1 MW = 27.397 (26.586 mit Geolokation);
  PV ≥1 MWp = 9.591 (9.589 mit Geolokation). Gesamt darstellbar = 36.175 Anlagen.
- Viele PV-Dachanlagen (klein) haben keine Koordinaten — bewusst nur ≥1 MWp betrachtet.
- Filter-Operatoren der API: `~eq~`, `~and~`, `~gt~` (nur `gt` für Zahlen funktioniert zuverlässig);
  Feld-/Filter-Namen sind lokalisiert (mit Umlauten, z. B. „Energieträger").

## 4. Umfang & Abgrenzung (final)

- **Energieträger:** Wind (Onshore + Offshore) und Photovoltaik (alle Größenklassen).
- **Leistungsgrenze:** nur Anlagen mit **Bruttoleistung ≥ 1 MW (Wind)** bzw. **≥ 1 MWp (PV)**. Kleinere Anlagen (v. a. Dach-PV) werden **nicht** importiert.
- **Geolokation:** Es werden **nur Anlagen mit vorhandenen Koordinaten** im MaStR gezeichnet. Anlagen ohne Koordinaten werden im Datensatz gespeichert (Statistik/Transparenz), aber **nicht** per Geocoding nachträglich aufgelöst.
- **Status:** Standardmäßig „In Betrieb“, Filter für andere Status (geplant, Stillgelegt, etc.) wünschenswert.
- **Nicht im Scope (V0):** Keine Biomasse/Wasser/Konventionell, keine Netz- oder Lokationsgrafiken, kein Login/Bot, kein Geocoding fehlender Koordinaten, kein Live-Hosting (nur vorbereitet).

## 5. Qualitätskriterien

1. **Vollständigkeit:** Anzahl Anlagen in der Karte ≈ Anzahl im MaStR (Abgleich über Zähler/Statistik).
2. **Korrektheit:** Keine erfundenen Daten; alle Werte direkt aus MaStR.
3. **Performance:** Flüssiges Pan/Zoom auch bei sehr vielen Punkten (Clustering).
4. **Aktualität:** Datenstand wird sichtbar angezeigt („Stand: …“).
5. **Wartbarkeit:** Update in einem Schritt (Skript) möglich; Doku aktuell.

## 6. Offene Fragen (Entscheidungen)

Siehe `ENTSCHEIDUNGEN.md` — die zuvor offenen Punkte sind jeweils entschieden:

- ~~Wie mit fehlenden Koordinaten umgehen?~~ → **Entschieden:** Nur vorhandene Geolokation; kein Geocoding.
- ~~Leistungsgrenze~~ → **Entschieden:** ≥ 1 MW (Wind) / ≥ 1 MWp (PV).
- ~~Repo/Hosting~~ → **Entschieden:** Lokal; Hosting nur vorbereitet (nicht live).
- ~~Update-Rhythmus~~ → **Entschieden:** Manuell auslösbar; jederzeit Cronjob-fähig.

Verbleibende Detailfragen werden während der Umsetzung im Entscheidungslog dokumentiert.

## 7. Dokumentations- & Ordnerstruktur (Ziel)

```
pv-wind-map/
├── README.md            # Kurzvorstellung, Quickstart (DE + EN)
├── ANFORDERUNGEN.md     # dieses Dokument
├── ENTSCHEIDUNGEN.md    # Architektur-Entscheidungen & offene Fragen
├── PLAN.md              # 30-Schritt-Plan
├── docs/                # Detaillierte Doku (Architektur, Datenmodell, Hosting, Update) — DE + EN
├── scripts/             # Python-Pipeline (Download, Import, Export, Update)
├── src/                 # Frontend-Quelle (HTML/JS/CSS)
├── data/                # Lokale Datenbasis (SQLite) + roh-Downloads (gitignored, groß)
├── dist/                # Generierte, hostbare Ausgabe (Auslieferung)
└── tests/               # Tests & Verifikationsskripte
```
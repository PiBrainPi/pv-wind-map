# Entscheidungen (EVL) — PV & Wind Karte

> Status: laufend geführt. Neue Entscheidungen anhängen, nie löschen.
> Format: Datum · Entscheidung · Begründung · Status

## Gefällte Entscheidungen

1. **Geolokation (2026-08-29):** Nur Anlagen mit **vorhandenen Koordinaten** im MaStR werden gezeichnet. **Kein** Geocoding fehlender Koordinaten.
   - Begründung: Geocoding von ~100k+ Adressen (MaStR liefert bei vielen PV-Anlagen keine Koordinaten) wäre teuer, langsam und datenschutzsensibel. Bewusste Abgrenzung auf präzise, vorhandene Daten.

2. **Leistungsgrenze (2026-08-29):** Nur **Bruttoleistung ≥ 100 kW (Wind)** bzw. **≥ 0,5 MWp (PV)**.
   - Begründung: Fokussiert auf relevante Assets (alle gewerblichen WEA ab 100 kW + große PV),
     reduziert die Datenmenge gegenüber allen Kleinstanlagen, aber vollständiger als ≥1 MW.
     **Änderungen 2026-08-29:** Wind von ≥1 MW auf ≥100 kW gesenkt (Nutzer-Wunsch) und PV von
     ≥1 MWp auf ≥0,5 MWp gesenkt (Nutzer-Wunsch: mehr Vollständigkeit für Recherche).

3. **Haltung / Repo (2026-08-29):** Nur **lokal**; Git-Repo lokal. Hosting wird **vorbereitet** (Doku, Hostbarkeit), aber nicht live geschaltet; ggf. später. Zweisprachige Doku (DE + EN).
   - Begründung: User möchte zunächst lokal validieren und hosten später entscheiden.
   - **→ Überholt 2026-08-30** (siehe Nr. 4): Hosting inzwischen **live** umgesetzt.

4. **Hosting / GitHub Pages (2026-08-30):** **Live deployed** auf GitHub Pages unter eigener Domain
   `ingenieur-tools.de` (netcup). Repos öffentlich (`pv-wind-map`, `ingenieur-tools-portal`).
   - **Domain/Portale:** `ingenieur-tools.de` (A-Record Apex), `www` (CNAME), Subdomains via CNAME
     (`wind-pv-map`→Karte, `galton-board`→vorbereitet). Portal nutzt `www` als kanonische Domain (GitHub leitet Apex→www um).
   - Karte: `https://wind-pv-map.ingenieur-tools.de/` (HTTPS aktiv). Portal: `https://ingenieur-tools.de/`
     (Zertifikat in Ausstellung, < 1 Std.).
   - Begründung: eigener Auftritt als Tool-Portal, 0 € Hosting, voller Agent-Zugriff via gh-CLI.

5. **Update-Rhythmus (2026-08-29):** **Manuell** auslösbar; Pipeline so gebaut, dass daraus **jederzeit ein Cronjob** entstehen kann.
   - Begründung: Volle Kontrolle erstmal; Automatisierung als Option vorbereitet (Skript als Einstiegsbefehl ohne Interaktion).

6. **Kartentechnologie (2026-08-29):** **Leaflet + MarkerCluster** gewählt (statt PMTiles).
   - Begründung: Datenvolumen ~36 k Punkte ist für Leaflet + Clustering ideal beherrschbar;
     hostbar als statische Site; Single-File möglich. Kein Vektortiling nötig für V1.

## Wichtige Daten-Erkenntnisse (aus Umsetzung)

7. **MaStR-Einheiten inkonsistent:** PV-Bruttoleistung in **kWp**; Wind **gemischt**
   (kW für moderne/große Anlagen wie V236-15MW=15000, aber auch alte wie V47=660;
   wenige in MW). → Import normalisiert auf **MW** mit Heuristik `>80 → kW`.
   (siehe docs/datenmodell.md). Erst festgestellt, nachdem erste Summen absurd waren
   (Wind „avg 2556 MW"); mit korrekter Normalisierung avg ≈ 3.4 MW.

8. **Filter-Operator:** Für Zahlenfilter funktioniert nur `~gt~` zuverlässig
   (`~gte~`/`~ge~`/`>=` schlagen fehl). Feldnamen lokalisiert (Umlaute).

9. **PV-Datenmenge:** MaStR enthält ~6,4 Mio. PV-Einträge (davon ~4,85 Mio. Dachanlagen).
   Die ≥1-MWp-Grenze reduziert auf ~10,5 k in Betrieb — entscheidend für das Design
   (sonst wären Download & Karte unpraktikabel).

Die zuvor offenen Detailfragen (Clustering-Strategie, MaStR-Quelle, schlanke
Remote-Feldliste) sind alle in den Entscheidungen 4–7 bzw. in docs/ dokumentiert.

## Statistik-Modul — Entscheidungen (2026-08-29)

10. **Panel-Typ:** Overlay-**Sidebar rechts** (statt separatem Tab/Karte) — öffnet per
    „📊 Statistik"-Button in der Top-Bar; Overlay verdunkelt die Karte.
    - Begründung: klare Fokustrennung (Karte ↔ Statistik), schlank, responsiv.

11. **Größenklassen:** **feste Staffel** je Technologie (Wind: 1–2…50–100 MW; PV: 1–2…100–200 MW)
    bis zum realen Maximum (Wind 80 MW, PV 162 MW). Keine dynamische/equidistante Skala.
    - Begründung: einfacher, konsistenter und aussagekräftiger für die Zielnutzung.

12. **CSV-Export:** **bewusst NICHT umgesetzt** — vom User explizit abgelehnt (Punkt B8 entfällt).

13. **Betreiber-Kopplung:** Klick auf eine Betreiber-Zeile filtert die Karte auf dessen Anlagen
    (bei mehreren Anlagen Fit-Bounds, bei einer Fly-to + Popup).

## Wichtige Daten-Erkenntnis (Statistik)

- **23.225 eindeutige Betreiber** über 53.500 georeferenzierte Anlagen
  (31.116 Wind ≥100 kW + 22.384 PV ≥0,5 MWp). Top-Betreiber nach Anzahl: PROKON (275 Anlagen).
- Statistik-Aggregation erfolgt in `export_app.py` aus SQLite (nur `geolokation=1`,
  konsistent zur Karte) → `dist/assets/statistiken.json`.
## 2026-09-06 · V25 — Bugfix + Mobile + Live-Gang (User-Freigabe)

- **Bugfix:** „Alle Anlagen anzeigen" tot seit V23 (`showAllUnits()` ohne Geo-Filter →
  ReferenceError). Lektion dokumentiert: **neue Filter immer in BOTH `applyFilters()` UND
  `showAllUnits()` ergänzen** — der Betroffenheits-Overlay-Code spiegelte genau dieses
  Muster schon früher (F5-Fix).
- **Mobile:** Landkreis-Tab horizontal scrollbar (Header vollständig), PC unverändert.
- **Placeholder:** „Solarpark Döllen GmbH".
- **Deploy:** User-Freigabe → push main + gh-pages, Live-Verifikation wie gehabt.

## 2026-09-06 · V24 — Politur + Live-Gang (User-Freigabe)

- **Entscheidung:** Landkreis-Tab-Header tragen die Leistungseinheit — „Leistung PV (MWp)"
  und „Leistung Wind (MW)" (konsistent zur Größenklassen-Konvention der Karte).
- **Layout:** Landkreis-Tabelle auf `table-layout:fixed` mit festen Spaltenverhältnissen,
  Spannungs-Balken-Titel flex-wrap → **alle 9 Statistik-Tabs ohne horizontales Scrollen**
  (vorher: Tabelle 996 px > 805 px Container).
- **Deploy:** User-Freigabe „pushe die neueste Revision auf GitHub und stelle live" →
  main `7172681` (V22+V23+V24), gh-pages `1b9c85a`, DB-Backup `mastr.db.2026-09-06.preV24.bak`
  vorher. Live-Verifikation: HTTP 200 + Header-Strings + statistiken.json (377/6.499/cluster).

## 2026-09-06 · V23 — „Geo-Ebene" (Arbeitspakete 1–8)

- **Entscheidung:** Bundesland/Landkreis/Gemeinde als eigene Suche- und Filter-Dimension
  (kontextuelle Dropdowns BL→LK→Gemeinde, kombinierbar); neuer Stats-Tab „Landkreis" mit
  NAP-Spalten (Join über numerische LokationId — SEL-String-Join ist leer); Größenklassen-Balken
  klickbar (gesamt-Modus: Klick-Position entscheidet Wind vs. PV); Leistungsfilter mit
  Basis-Umschalter **„Park (aggregiert)" als Default** — zersplitterte Parks erfüllen
  Größenklassen über ihre Park-Summe (`pkmw`), nicht je Registrierung.
- **User-Entscheidung (Darstellung):** Variante A — bei Park-Filter erscheinen alle Einheiten
  des Parks als Marker (konsistent zum V22-Diagramm), kein Zusammenfassen zu einem Marker.
- **Updatefähigkeit:** `pk`/`pkmw` + `landkreise`/`gemeinden` entstehen komplett in
  `export_app.py` → jeder build.sh-Lauf berechnet sie automatisch frisch.
- **Status:** implementiert, browser-verifiziert (Döllen-Kontrollfall: Park 150+ = 1.603
  inkl. 13 EH vs. Einzel = 3), NICHT deployed — wartet auf User-Freigabe (gemeinsam mit V22).

## 2026-09-06 · V22 — Größenklassen: Park-Cluster-Basis („Parks aggregiert")

- **Entscheidung:** Die Größenklassen-Statistik bekommt eine zweite Auswertungsbasis.
  Neben der bestehenden Einheiten-Sicht (Register-Perspektive) rechnet der Export eine
  Park-Cluster-Verteilung (Betreiber-Perspektive) nach Schlüssel (Energieträger, Betreiber,
  Parkname mit Suffix-Normalisierung). UI: Umschalter im Größen-Tab, Default bleibt
  „Einzelanlagen" (V21-Verhalten unverändert).
- **Begründung:** Das MaStR zersplittert große Parks in viele Einheiten (Solarpark Döllen =
  13 EH à 7,4–31,4 MW = 154,8 MW). Auf Einheiten-Ebene sind Kritis-Objekte (≥104 MW,
  BSI-KritisV) praktisch unsichtbar: nur 5 Einzel-Einheiten vs. 52 reale Cluster
  (Offshore-Windparks bis 958,7 MW). User-Meldung 06.09., Umsetzung gleicher Tag.
- **Updatefähigkeit:** Cluster-Aggregation läuft vollständig in `export_app.py::build_statistiken()`
  — jeder Daten-Update-Lauf erzeugt `groessen_cluster` automatisch frisch. Keine manuellen Schritte.
- **Status:** Umgesetzt + browser-verifiziert (12 Kombi-Stufen, F5-Regression ok).
  Revision `iterations/V22_GroessenCluster.html`. Commit/Deploy nach User-Freigabe (Regel 4).

## 2026-09-11 · V36 — Betroffenheit: Zeitraum-Option (Semantik „Inbetriebnahme")

- **Entscheidung:** Die 3. Zeitfenster-Option „Zeitraum (von–bis)" im Betroffenheits-Tab
  gleicht die Referenz mit Anlagen ab, deren **Inbetriebnahme- bzw. Registrierungsdatum**
  (je Modus-Feld: inb/reg/both) in den gewählten Zeitraum fällt — NICHT mit den
  Update-Deltas.
- **Begründung:** Update-Deltas existieren erst seit 01.09.2026 (Snapshot-Historie);
  User-Beispiel „01.01.2023 – 01.03.2023" wäre dort leer. Die Inbetriebnahme-Daten sind
  historisch bis 1988 vollständig in der Datenbasis (56.399/65.663 Anlagen, live
  verifiziert). User-Entscheid per clarify() (Option A, 10.09.).
- **Konsequenz:** Entfernte Anlagen sind im Zeitraum-Modus bewusst nicht Teil der
  Prüfung (nur Update-Deltas enthalten sie). Modus-Feld (reg/inb/both) wird im
  Zeitraum-Modus als Datumswahl interpretiert — Dokumentation im Erklärtext (Tab) +
  statistik.md.
- **Status:** Umgesetzt + browser-verifiziert (Multi-File + Singlefile, je 0 JS-Errors;
  beide User-Beispiele geprüft, Kandidaten-Counts gegen unabhängige JS-Gegenrechnung
  identisch). Revision `iterations/V36_Zeitraum_Betroffenheit.html`. Kein Commit/Push
  ohne User-Freigabe (Regel 4).

## 2026-09-11 · V37 — Typen-Normalisierung Wind (Majority-Vote, User-AP1)

- **Entscheidung:** Inkonsistente MaStR-Typenbezeichnungen (E40/E-40/E 40/e40 …, 752
  Dubletten-Gruppen, 9.741 Karten-Basis-Records) werden per **Majority-Vote** normalisiert:
  häufigste Schreibweise = korrekt (User-Vorgabe; Beispiele E40→E-40, E80→E-80 bestätigen
  die Regel). Tie-Break: kürzeste, dann alphabetische Schreibweise. Scope: nur Wind
  (User-Entscheid per clarify(); PV hat kein Typ-Tab).
- **Umsetzung als Pipeline-Regel** (Grundsatzentscheidung „Fehler als Regel, nicht als
  Daten-Flick"): `data/typ_normalisierung.json` (1.547 Mappings) via
  `build_typ_normalisierung.py`; Anwendung in `import_mastr.py::normalize_typ()` und
  `export_app.py` (jeweils vor to_mw — 15-MW-Ausnahme bleibt intakt, to_mw-Diff 0/43.478).
  Einmalige DB-Bereinigung via `fix_typenbezeichnung.py` (10.000 raw_json + 7.405 Legacy,
  Backup vorher, idempotent, Rescan 0 Dubletten).
- **Konsequenz:** Typ-Tab kumuliert jetzt korrekt (E-40 = 1 Zeile/628 Anlagen);
  Klick-Filter trifft alle Varianten; künftige Delta-UPSERTS mit falscher Schreibweise
  werden beim Export automatisch normalisiert.
- **Status:** Umgesetzt + browser-verifiziert (Multi + Singlefile, 0 JS-Errors, Regression
  ok). Revision `iterations/V37_TypenNormalisierung.html`. Kein Commit/Push ohne
  User-Freigabe (Regel 4).

## 2026-09-11 · V38 — Betreiber-Diagramme: Technologie-Filter + Panel +8 % (User-AP1/2)

- **AP1 (Technologie-Filter):** Zweiter Toggle „Alle / Wind / PV" über den Betreiber-Diagrammen.
  Im Wind-/PV-Modus filtert er ALLE Charts (Wachstum, Tech-Donut, EEG-Donut, Summary); der
  EEG-Donut zeigt dann nur 2 Segmente (mit/ohne EEG) der gewählten Technologie. Motivation
  (User): der kombinierte 4-Segment-Donut „EEG-Registrierung" trennte Wind/PV nicht eindeutig
  auf den ersten Blick. „Alle" = kombinierte Ansicht, Verhalten unverändert.
- **AP2 (Panel-Breite):** `#stats-panel` Desktop 984 → 1063 px (+8 %), Off-Canvas-Offset
  −1024 → −1103; Tablet/Mobil-Breakpoints unverändert.
- **Status:** Umgesetzt + browser-verifiziert (Multi + Singlefile, 0 JS-Errors, 6 Kombi-Stufen
  Measure×Tech geprüft, Breite via getBoundingClientRect bestätigt). Revision
  `iterations/V38_BetreiberDiagramme_TechFilter_PanelBreite.html`. Kein Commit/Push ohne
  User-Freigabe (Regel 4).

## 2026-09-11 · V39 — EEG-Donut: Semantik klargestellt (User-Meldung „CEE-Bug")

- **Meldung:** User (CEE-Mitarbeiter) vermutete Bug: PV-Assets nach Leistung überwiegend
  nicht EEG-vergütet, Diagramm zeigte 100 % „mit EEG".
- **Audit (hart, DB + MaStR-Doku):** Kein Daten-Bug. Das Feld `EegInbetriebnahmeDatum`
  bedeutet „EEG-Anlage registriert" — MaStR-Registrierung ist für ALLE ortsfesten Anlagen
  Pflicht, unabhängig vom Zahlungsanspruch (MaStR-Webhilfe, abgerufen 11.09.). Das MaStR
  hat KEIN Feld für Vermarktungsweg/PPA/Direktvermarktungsart. CEE-Audit: 184 Anlagen/
  827 MW, 100 % EEG-registriert (Datum+MaStR-Nr. je Einheit) — die Daten stimmen; nur die
  Frage „wird vergütet?" beantwortet das MaStR strukturell nicht. PPA-/Strompreisgeschäfte
  laufen i. d. R. ÜBER registrierte EEG-Anlagen → zwingend „mit EEG" im Diagramm.
- **Fix (UI-Präzisierung):** Chart-Untertitel „EEG-Anlage registriert: ja/nein
  (MaStR-Feld EegInbetriebnahmeDatum)" statt „Mit/ohne EEG-Anlagen-Registrierung";
  Erklärtext nennt explizit, dass PPA unter „mit EEG" läuft und der Vergütungsweg im
  MaStR nicht abgebildet ist. Nur belastbarer Zusatzhinweis: `EegZuschlag`
  (Ausschreibung) — bewusst NICHT als Segment gemischt (deckt nur 26,5 % Wind-/40 % PV-
  Leistung ab und ist kein Vermarktungsweg).
- **Status:** Umgesetzt + verifiziert (Multi + Singlefile, 0 JS-Errors). Details:
  `docs/fehlerbehebung.md` F-EEG-1. Kein Commit/Push ohne User-Freigabe.

## 2026-09-11 · V40 — EEG-Donut entfernt + 2-Spalten-Layout + DEPLOY (User-AP1–3)

- **AP1:** Chart „EEG-Registrierung" komplett entfernt (Nachwirkung V39: das MaStR kann
  den Vergütungsweg nicht abbilden — Chart führte zu Fehlinterpretation). Wachstum +
  Technologie-Verteilung jetzt nebeneinander (flex; Wachstum flex-basis 480px, Donut 240px;
  Stack bei schmalem Viewport). Measure-Toggle + Tech-Filter wirken auf beide Charts.
- **AP2:** Doku as-built (PROJEKTSTAND, statistik.md, fehlerbehebung.md F-EEG-1,
  ENTSCHEIDUNGEN, Hosting HANDOVER/README).
- **AP3:** User-Freigabe erteilt → Deploy über scripts/deploy_ghpages.sh (main + gh-pages).
- **Status:** Verifiziert Multi + Singlefile (0 JS-Errors, 2 Charts, Layout nebeneinander,
  Measure×Tech-Regression ok).

## 2026-09-11 · V41 — „Online ≠ lokal" war Browser-Cache + URL-Verwirrung (User-AP1)

- **Meldung:** Online fehle die V36-Zeitraum-Option im Betroffenheit-Tab.
- **Analyse:** Live-HTML (Subdomain + github.io) byte-identisch mit lokal (md5
  4c952ab0df, ETag 6aa3dd09-7df89) — Option WAR live. Root Causes: (1) Browser-Cache
  (Pages: max-age=600; alte Session-Tabs heuristisch gecacht), (2) URL-Verwirrung
  (Karte lebt auf wind-pv-map.ingenieur-tools.de; /pv-wind-map → 404; apex ohne www →
  SSL-Fallback-Zert). 
- **Fix (V41):** Build-Stempel in der Infobar („Build V41 (11.09.2026)") — sofort
  sichtbarer Indikator, welche Version der Browser tatsächlich geladen hat.
  Prozessregel dokumentiert: nach Deploy hart neuladen.
- Kein Funktions-/Datenbug. Deploy V41 auf User-Freigabe (AP2).

# Projektstand (Handover) — PV & Wind Karte (MaStR)

> **Dieses Dokument dient als Einstieg für jede neue Agenten-/Arbeitssession.**
> Stand: 2026-09-04 · Repo: `/home/claw_01_rasbpi5_1/Projects/pv-wind-map`

## Aktueller Stand (2026-09-04, V19 — Betroffenheits-Tab final, LIVE deployed)

**LIVE:** https://wind-pv-map.ingenieur-tools.de · **Code-Stand:** V19 · **Single-File:** 38,7 MB
**Letzter Deploy:** 04.09.2026 (V19, User freigegeben) · **Deploy-Verifizierung:** served-SHA = local-SHA, Daten-JSON live OK
- **Grundsatzentscheidung (2026-09-03, User-Freigabe):** `GRUNDSATZENTSCHEIDUNG.md` im Repo-Root —
  Regel 1 (NICHTS löschen ohne explizite Zustimmung), Regel 2 (100 % der MaStR-Daten Wind/PV auf
  den Server: alle 118 Felder + NAP), Regel 3 (iterierte HTML-Versionen niemals löschen), Regel 4
  (GitHub nur nach explizitem „Ja": kein Push, keine Settings-Änderungen).
- **Pipeline 2.0 (neu, neben V1):** `fetch_v2.py` (volle 118-Feld-Records → `data/raw_v2/`) +
  `fetch_nap.py` (Netzanschlusspunkte je Lokation, Cache in `nap_fetch_log`, append-only
  `data/nap/netzanschlusspunkte.jsonl`) + `import_v2.py` (Schema 2.0: Tabellen `einheiten_raw`
  1:1-Rohdaten, `netzanschlusspunkte`, UPSERT-inkrementell via DatumLetzteAktualisierung,
  DB-Backup-Pflicht nach `~/backups/` vor jedem Lauf).
- **Verifiziert (03.09.):** alle 54.544 Records mit exakt 118 Feldern (0 Verlust), NAP-Endpoint
  90/90 Requests fehlerfrei (~0,36 s/req), ~30.678 eindeutige Lokationen (Vollzug ≈ 3 h,
  inkrementell danach Minuten), Snapshots #7/#8 unangetastet, alte Tabellen unverändert.
  Echte Multi-NAP-Lokation gefunden (Lokation 1798726, 2 NAPs).
- **NAP-Vollzug erledigt (03.09., ~3,1 h):** 30.611/30.628 Lokationen ok → **27.870 NAPs in
  `netzanschlusspunkte`**. Datenqualität: Spannungsebene + Regelzone 100 % gefüllt,
  Messlokation 51 %, **479 Multi-NAP-Lokationen**. 17 Fehler = MaStR-Datenfehler („Keine
  Lokation" vom BNetzA-System, je 1 Wind-Einheit betroffen, retry-verifiziert, protokolliert
  in `nap_fetch_log`). 3.404 Lokationen haben 0 NAPs (Register-leer, normal).
  Cron-Design (Punkt 5): EIN Cronjob triggert alle drei Stränge (Wind, PV, NAP) —
  Details in `docs/update.md` § Pipeline 2.0.
- **HTML-Export (Punkt 9):** bleibt vorläufig unverändert (19 Kernfelder); Kernfeld-Anpassung
  für spätere Versionen MUSS explizit mit dem Nutzer besprochen werden.
- **Stand V11c (03.09., abgenommen):** F2 Spannungsebenen-Filter (V10) ✅, F1 NAP-Suche (V11) ✅,
  Performance-Fix Lazy-Popup (V11b, applyFilters 24,2 s → 0,68 s) ✅, Datumsfilter-Fix
  Epoch-Strings (V11c) ✅ — alle browser-verifiziert, Revisionen in iterations/, Single-File
  38,7 MB. Nächste AP: F3 (NAP-Gruppenansicht), danach F4+F6 (Betroffenheitsanalyse).
- **Stand V12 (03.09., wartet auf Freigabe):** F3 NAP-Gruppenansicht umgesetzt —
  Toggle „⚡ NAP-Gruppen" (opt-in, localStorage), 6.258 Gruppen-Badges auf der Karte,
  NAP-Panel mit allen Anlagen je Anschlusspunkt (Chunk-Rendering, Multi-NAP-Unterstützung,
  Betreiber-Warnung), F1-Suche öffnet bei aktivem Toggle dasselbe Panel. Revision:
  iterations/V12_NAPGruppenansicht.html. Danach: F4+F6 (Betroffenheitsanalyse).
- **Stand V13 (03.09., wartet auf Freigabe):** F4+F6 Betroffenheitsanalyse umgesetzt —
  neuer Statistik-Tab „⚠ Betroffenheit": Referenz (Anlage/Betreiber/NAP) suchen, Match-Modi
  (NAP-Gleichheit + Radius 2–20 km), Zeitfenster (letztes/alle Updates), Modi
  „neu registriert"/„neu in Betrieb", Leistungs-Betroffenheit (+MW neu/entfernt vs. Bestand
  am Knoten), Ereignisliste NEU/ENTFERNT klickbar auf Karte. Indikations-Hinweis im UI.
  Analyse < 1 ms (BBox-Vorfilter). Revision: iterations/V13_Betroffenheit.html.
  **Alle Features F1–F6 aus der Roadmap sind damit umgesetzt.** Offen: Punkt 9
  (HTML-Kernfeld-Auswahl) mit User besprechen.
- **Stand V13b (04.09., nach User-Feedback):** Live-Suggest im Betroffenheits-Tab wie
  Hauptsuche (ab 2 Zeichen, 250 ms Debounce). Revision: iterations/V13b_BetroffenheitLiveSuche.html.
- **Stand V13c (04.09., nach User-Feedback):** Anlagennamen-Suche gefixt (Feld heißt `n`,
  nicht `name` — Namen wurden nie gematcht); Betreiber max 8 / Anlagen max 12 Treffer.
  Revision: iterations/V13c_AnlagennameLiveSuche.html.
- **Stand V14 (04.09., wartet auf Freigabe):** Portfolio-Suche im Betroffenheits-Tab —
  Betreiber werden über Namenskerne zu Portfolios gruppiert (Rechtsformen/Branchen-Wörter/
  Nummern normalisiert); ein Eintrag prüft ALLE Invest-Gesellschaften gleichzeitig. Summary
  zeigt „Betroffene Gesellschaften X von N". Beispiel ABO Energy: 30 Gesellschaften /
  65 Anlagen in einer Analyse. Revision: iterations/V14_PortfolioSuche.html.
- **Stand V15 (04.09., wartet auf Freigabe):** Revisionspaket Betroffenheits-Tab —
  (1) **Betreibergruppen (Brand-Ebene):** Portfolios werden zusätzlich über das Markenwort
  gebildet (ENERPARC 212 Ges, CEE 60 Ges, ANUMAR 220 …), fixt „Betroffene Gesellschaften
  leer" (ENERPARC) und „kein CEE-Gesamtportfolio"; Klapptext nennt die betroffenen
  Gesellschaften namentlich. (2) **„🗺️ Anzeigen"-Button:** filtert die Karte auf die
  Analyse-Treffer + zoomt hin; Reset via „Alle anzeigen"/Filterwechsel. (3) **Farbringe:**
  gestrichelter Bernstein-Kreis mit gewähltem Suchradius um jede Referenz-Anlage
  (Dedupe, max 50). (4) **Beschreibungs-Klapptext** zur Prüfmethode (NAP-Gleichheit ODER
  Haversine-Umkreis). Revision: iterations/V15_BetroffenheitRevision.html.
- **Stand V16 (04.09., wartet auf Freigabe):** Revisionspaket 2 Betroffenheits-Tab —
  (1) Suchreihenfolge: Betreibergruppe → Portfolio → Betreiber → NAP → Anlagen. (2) ✕-Button
  leert das Suchfeld. (3) **Vermischungs-Fix:** Folge-Suchen mit 0 Treffern räumen Ringe/
  Anzeigen-Filter der Vor-Suche auf. (4) Ringe NUR um tatsächlich betroffene Referenz-Anlagen
  (vorher alle bis 50). (5) „Anzeigen" zeigt Bestands- + Neue Anlagen zusammen. (6)
  Vergleichstabelle Bestand↔Neu (Betreiber + Asset mit Deeplink je Zeile). Revision:
  iterations/V16_BetroffenheitRevision2.html.
- **Stand V17 (04.09., wartet auf Freigabe):** Revisionspaket 3 Betroffenheits-Tab —
  (1) „Betroffene Gesellschaften" gefixt: zählt jetzt die Portfolio-Gesellschaften über
  betroffene Bestandsanlagen UND NEU-Assets (vorher nur Neu-Betreiber → teils „0 von N");
  Berechnung nach der Bestands-Ermittlung (vorher: Wert der Vor-Analyse). (2) Ring-Geometrie
  mathematisch verifiziert (Haversine-Nachrechnung: 20 km → max 19,8 km; 5 km → max 2,9 km)
  — korrekt. (3) Erklär-Klapptext erweitert: NAP-ODER-Radius-Verfahren, geplante Anlagen
  ohne NAP → Geolokation, Grenzen (Luftlinie ≠ Netztopologie, Falsch-Positive). (4) Fix:
  Syntaxfehler aus V16-Patch (Karte hing bei „Lade Daten…"). Revision:
  iterations/V17_BetroffenheitRevision3.html.
- **Stand V18 (04.09., wartet auf Freigabe):** Revisionspaket 4 Betroffenheits-Tab —
  (1) Trefferliste unter der Vergleichstabelle entfernt (Tabelle ist alleinige Ergebnis-
  darstellung). (2) Neue Spalte „MW" vor Match: Anschlussleistung des Neu-Assets
  (PV → MWp, Wind → MW). (3) Radius-Slider erweitert auf 2–50 km, Default 20 km;
  Erklärtexte angepasst. (4) Bug gefixt: Ring-Tooltip „Suchradius N km" fing Maus-Events
  ab („Suchradius"-Popup statt Assetname) → Ringe jetzt `interactive: false` ohne Tooltip.
  Revision: iterations/V18_BetroffenheitRevision4.html.
- **Stand V19 (04.09., wartet auf Freigabe):** Revisionspaket 5 Betroffenheits-Tab —
  3 Bugs im „Anzeigen"-Modus gefixt: (1) Anzeigen-Modus ersetzt jetzt alle Filter
  (vorher Schnittmenge → Assets verschwanden bei aktivem Typ-Filter). (2) Clustering
  im Anzeigen-Modus aus → betroffene Bestandsanlagen nicht mehr in Cluster-Bubbles
  versteckt (Ringe wirken „leer"). (3) „Alle anzeigen" stellt Karte wieder her
  (applyFilters-Nachlauf; vorher blieben 21 Anzeigen-Marker stehen). Datensimulation:
  jeder Ring-Zentrum hat reale Bestands-Unit, jede Neuanlage im Bestand — kein
  Datenfehler. Revision: iterations/V19_BetroffenheitRevision5.html.
  **V19 Status: von User freigegeben (04.09.) → auf main + gh-pages deployed, LIVE.**
- **Stand V20 (04.09., wartet auf Freigabe):** Revisionspaket 6 (Laptop-Review, 7 Punkte) —
  (1) Popup-Datum gefixt (war roher `/Date(…)`-String → „MM.JJJJ"). (2) Wind/PV-Legende +
  Datenstand aus der Topbar (überlagerte Buttons) ins Hinweise-Panel verlagert. (3)
  Statistik-Panel 700→820 px + kompaktere Tabs → alle 8 Tabs ohne horizontales Scrollen.
  (4) Vergleichstabelle: neue schmale Typ-Spalte 🆕/🗑️; ENTFERNT-Assets erscheinen jetzt
  überhaupt (vorher nur NEU-Events). (5) Zubau-Charts: Wert-Labels senkrecht (Balken +
  Linien-Charts, beide Modi), PAD_T erhöht. (6) Gestrichelte Trendlinie entfernt.
  (7) Wind/PV-Label-Überlappung in Linien-Charts getrennt (L/R-Positionierung).
  Revision: iterations/V20_BetroffenheitRevision6.html.
- **ROADMAP (`docs/ROADMAP.md`, 03.09.):** User-Feature-Wünsche F1–F6 dokumentiert mit
  verifizierter Umsetzbarkeit: F1 NAP-Suche, F2 Spannungsebenen-Filter, F3 NAP-Gruppenansicht
  (opt-in), F4+F6 Betroffenheits-Match (neue + entfernte Anlagen vs. Betreiber/NAP),
  F5 Status-Filter (Katalog verifiziert: 4 Werte — In Planung/In Betrieb/Vorüb. stillgelegt/
  Endg. stillgelegt; „In Bau" existiert nicht; Nicht-InBetrieb-Volumen: 12.547 Anlagen).
  Umsetzung je Punkt nur nach User-Freigabe.

- **V11 — NAP-Suche (2026-09-03, F1, klickbare HTML zur Freigabe):**
  Suchfeld findet jetzt **Netzanschlusspunkte**: grüne „⚡ NAP"-Treffer-Blöcke (NAP-Nr.,
  Netzbetreiber, Spannungsebene, Regelzone, Anzahl Anlagen) über den Anlagen-Treffern.
  Ranking: SAN exakt > Präfix > enthält > Netzbetreiber-Name. Klick → alle Anlagen der
  Lokation auf der Karte + Zoom (Großparks bis 219 Anlagen). Popup: „NAP" + „NAP-
  Netzbetreiber" (Multi-NAPs kommagetrennt). Quelle: neuer NAP-Index (27.078 NAPs mit
  sichtbaren Anlagen, 3 MB; hostbar: assets/nap_index.json lazy, Single-File: eingebettet,
  38,7 MB). Anlagen-seitig neues Feld `lid` (lokation_id). NAPs ohne georef In-Betrieb-
 Anlage (792) sind bewusst nicht suchbar. Revision: iterations/V11_NAPSuche.html.
 - **V11b — Performance- + NAP-Vorschlags-Fix (2026-09-03, nach User-Feedback):**
 Beide User-Bugs behoben: (1) Langsamkeit — Popups wurden für ALLE 53.400 Marker
 vorgeneriert (17,7 s pro Filterwechsel!); jetzt Lazy-Popup beim Klick → applyFilters
 24,2 s → 0,68 s, Suchfeld-Löschen 28,4 s → 0,49 s. Zusätzlich Cluster-Quirk gefixt:
 marker.openPopup() zeigte bei Cluster-Markern leere Popups → map.openPopup() mit
 setLatLng. (2) NAP-Vorschläge bei beliebigen Texten — Netzbetreiber-Match now erst
 ab 5 Zeichen (SAN-Nummern ab 2). Revision: iterations/V11b_PerformanceFix.html.
 - **V11c — Datumsfilter-Fix (2026-09-03, nach User-Feedback):** Filter Registrierung/
 Inbetriebnahme lieferten 0 Treffer — reg/inb sind `/Date(...)`-Epochen-Strings, Filter
 schnitten `substring(0,4)` → `'/Dat'`. Fix: zentrale Normalisierer dateYear()/dateMonth()
 mit Cache, eingesetzt an beiden Filterstellen (applyFilters + showAllUnits-Duplikat),
 Tabellen-Sortierung und Zubau-Chart. Verifiziert: inb 2023 → 2.566, reg 2019 → 16.747,
 Zubau-Chart korrekt, Performance unverändert schnell (477 ms).
 Revision: iterations/V11c_DatumsfilterFix.html.
 - **V10 — Spannungsebenen-Filter (2026-09-03, F2, klickbare HTML zur Freigabe):**
  Toolbar-Dropdown „Spannungsebene" (Mittelspannung, Hochspannung, Höchstspannung,
  Niederspannung (Hausanschluss), 3 Umspannebenen, „ohne Angabe"); Quelle: NAP-Join
  (53.025/53.533 In-Betrieb georef = 99,05 % Abdeckung). Multi-NAP-Lokationen (173,
  z. B. MS+NS) matchen, wenn EINE der Ebenen gewählt. Popup-Zeile „Spannungsebene",
  Statistik-Tab „Spannungsebenen" (Balken, folgt aktivem Filter), Tabellen-Spalte „Ebene"
  (Kürzel MS/NS/HS/HöS, Volltext im Tooltip). Export: neues Feld `se` (Pipe-getrennt),
  meta.spannungsebenen. Revision: iterations/V10_SpannungsebenenFilter.html.
- **V9c — Tabellen-Deep-Links final (2026-09-03, AS-BUILT, von User abgenommen):**
  Übersichtstabelle „Alle Anlagen anzeigen": **Betreiber = externer NorthData-Link**
  (neuer Tab, identischer Slug wie im Popup — '＆'→'&' etc.), **Koordinaten = interner
  Deep-Link** (Karte zoomt via zoomToShowLayer + Popup öffnet), **MaStR-Nr.-Spalte entfernt**
  (funktionslos, Info bleibt im Anlagen-Popup). Sortierbare Betreiber-Spalte weiter aktiv.
  Header: # · Name · Typ · Art · MW · Bundesland · Landkreis · Gemeinde · Registriert ·
  Inbetriebnahme · Betreiber ↗ · Koordinaten. Revision: iterations/V9c_Tabelle_NorthData_MaStRWeg.html.
- **V9b — Tabellen-Filter-Fix (2026-09-03):** Status-Filter greift jetzt auch in der
  Tabellen-Ansicht (war zuvor nur auf der Karte aktiv); Registrierungs-Spalte parst
  /Date(...)-Epochen-Strings; Inbetriebnahme-Jahr-Dropdown bereinigt.
- **V9 — Status-Filter (2026-09-03, F5):** Neue Toolbar-Sektion
  „Status" mit **4 Checkboxen (Mehrfachauswahl)**: In Planung (31), In Betrieb (35, Default ✓),
  Vorübergehend stillgelegt (37), Endgültig stillgelegt (38). Marker-Stile: In Betrieb gefüllt
  (Wind blau/PV orange), In Planung gestrichelter Umriss, Vorüb. stillgelegt mit Kreuz, Endg.
  stillgelegt grau. Badge zählt aktive Filter-Kombination. Datenbasis: fetch_v2 `--extended-status`
  (separate Dateien `*_status{31,37,38}.json`, Bestand unangetastet), import_v2 UPSERT mit
  Statuswechsel-Erkennung, export_app liest ALLE Status aus einheiten_raw (V1-Tabelle nur noch
  Legacy) → 65.659 georef Anlagen: 53.405 In Betrieb / 9.273 In Planung / 66 Vorüb. stillg. /
  2.915 Endg. stillg. Browser-Tests: 10 Filter-Kombis, Badge == erwartete Mathematik,
  0 JS-Fehler, Bug-Fix: 0 gewählte Status = 0 Anlagen (zunächst falsch 65.659).
  **Nicht gepusht** (Regel 4) — wartet auf User-Freigabe der HTML.

## Was das Projekt ist
Interaktive, offline-fähige HTML-Karte aller **Wind- (≥100 kW) und PV-Anlagen (≥0,5 MWp)**
in Betrieb**, aus dem Marktstammdatenregister (MaStR, BNetzA). Klickbare Single-File + hostbare Version.

## Features
- **Karte:** Leaflet + MarkerCluster, Filter nach Typ (Wind/PV), Bundesland, **Art des Assets**
  (Freiflächen-/Gebäude-/Sonstige Solaranlage, Windkraft an Land/auf See) und **Leistung (MW)** in
  festen Größenklassen `[von, bis)` (0.1–0.5 … 150–200, 200+), Detail-Popups.
- **Anlagen-Anzahl-Badge (Filter):** Sobald ein **Art-, Bundesland- oder Leistungs-**Filter gesetzt ist,
  zeigt ein blauer Badge `Anzahl: <n>`. Logik (Var. A): die Zahl zählt immer die **tatsächlich sichtbaren**
  Anlagen (alle gesetzten Filter inkl. Wind/PV), konsistent mit den Marker-Clustern. Ohne Filter versteckt.
  Format: Tausendertrennung (`de-DE`).
- **Größenklassen-Skala (feste Staffel, Nutzer-Vorgabe + Kritis-Recherche):**
  `0.1–0.5 · 0.5–1 · 1–2 · 2–5 · 5–10 · 10–30 · 30–60 · 60–100 · 100–104 · 104–150 · 150+`
  (immer `>= von && < bis`, in MW/MWp). **Kritis-Schwelle:** Erzeugungsanlagen sind erst **ab 104 MW**
  installierter Nettonennleistung kritisrelevant (BSI-KritisV Anhang 1, Kat. 1.1.1). Daher ist NUR die
  Klasse ab `104` Kritis (`104–150`, `150+`); die Klasse `100–104` ist **kein** Kritis.
- **Suche mit Autocomplete:** Anlagen-, Park-, Gemeinde- **und Betreibername** (akzent-/case-unabhängig).
- **⛁ Betreiber-Suche:** Suchtext im Betreibernamen → ein Klick filtert **alle** Anlagen aller
  gematchten Betreiber (deutschlandweit, Fit-Bounds). Beispiel: „CEE" → 60 Betreiber/184 Anlagen.
- **Popup-Deeplinks:** Anlagen-Popup enthält „Koordinaten" (Dezimalgrad) → öffnet **Google Maps**
  an der Anlage (Deeplink `maps?api=1&query=lat,lon`); „Betreiber" → öffnet **NorthData**-Firmenprofil
  (Deeplink `northdata.de/<Firmenname-Slug>`; MaStR-typischer Vollbreite-Ampersand ＆ wird auf `&` normalisiert).
- **Statistik-Panel:** Betreiber-Tabelle (Filter/Top-N/Sortierung, Klick → Karte; **ohne** Technik-Badge/Emoji),
  Hersteller-Tabelle (nur Wind, +%Anteil-Spalte, **identische CSS-Formatierung wie Betreiber** — Schrift/Farbe/
  Kopfzeilen/Hover/Sortierpfeile, **ohne** Badge), **Größenklassen-Diagramme** mit Toggle **Wind / PV / Wind + PV**
  (gemeinsames Diagramm beider Technologien), Hersteller-Verteilungs-Donut-Chart (interaktiv, Canvas).

## Build (Ein-Befehl)
```bash
cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map
bash scripts/build.sh          # fetch → import → export → bundle (erzeugt dist/ + Single-File)
```
> Wichtig: `bash scripts/build.sh` (NICHT `python3` — build.sh ist ein Bash-Skript).

## Pipeline & Dateien
| Schritt | Datei | Zweck |
|---------|-------|-------|
| Fetch | `scripts/fetch_mastr.py` | MaStR-API (Wind ≥100 kW, PV ≥0,5 MWp) → `data/raw/*.json` |
| Import | `scripts/import_mastr.py` | Normalisierung (kW↔MW) + SQLite `data/mastr.db` |
| Export | `scripts/export_app.py` | `dist/assets/*.json` (nur georeferenziert) + Statistik (inkl. `groessenklassen.gesamt`) |
| Klassen-Rebuild | `scripts/rebuild_groessen.py` | DB-freies Rebuild der Größenklassen in `statistiken.json` (falls `mastr.db` fehlt, identische Logik) |
| Bundle | `scripts/bundle_singlefile.py` | `dist/index_singlefile.html` (eingebettete Daten) |
| App | `src/index.html` | Leaflet-Karte + Suche + Statistik-Panel + Impressum-Modal |

## Wichtige technische Details
- **Einheiten-Normalisierung:** Wind gemischt (kW/MW); Heuristik `>80 → kW`, sonst MW. PV immer kWp `/1000`.
- **Geolokation:** Nur Anlagen mit vorhandenen Koordinaten werden gezeichnet (kein Geocoding).
- **Statistik (gesamt):** `gesamt.wind_anzahl`/`pv_anzahl` = Direktzählung aus SQLite (Bugfix).
  `herstellbar_wind` = Summe der Hersteller.
- **Größenklassen (Staffel):** Feste 11-Klassen-Skala `0.1–0.5 … 100–104 · 104–150 · 150+`, einheitlich
  für Wind, PV und das gemeinsame Diagramm („Wind + PV"); definiert in `export_app.py` (`_staffel()`).
  **Alle Klassen werden immer gelistet** (auch leere), damit Kritis-Schwellen-Klassen sichtbar sind.
  Das Feld `kritis: true/false` markiert Kritis-relevante Klassen. **Kritis gilt erst ab 104 MW**
  (BSI-KritisV Kat. 1.1.1): nur `104–150` und `150+` tragen `kritis:true`; `100–104` ist **kein** Kritis.
  Die Karten-Statistik (`dist/assets/statistiken.json`) enthält den Schlüssel `groessenklassen.gesamt`
  für das gemeinsame Diagramm (zusätzlich zu `wind`/`pv`).
- **Kritis-Klassen:** Im Diagramm 🔴 rot markiert (`bar-fill.kritis`), mit `KRITIS`-Badge im Label +
  Tooltip-Hinweis. Leere Kritis-Klassen bei Wind (104+ real leer) bleiben sichtbar.
- **Gesamt-Diagramm („Wind + PV"):** zeigt pro Klasse **zwei Balken** (Wind blau, PV orange) nebeneinander
  mit getrennten Werten im Tooltip (Wind/PV Anlagen + Leistung), damit beide Technologien sichtbar sind.
- **Größen-Filter in der Toolbar:** HTML `<select id="filter-gr">` mit den 11 Größen-Klassen als
  `value="von,bis"` (z. B. `"0.5,1"`, `"104,150"`, `"150,1e9"`). `applyFilters()` parst
  `Number.parseFloat`, filtert `u.mw >= von && u.mw < bis`. Der Badge (`#art-count`) wird aktiviert
  bei `art || bl || gr`.
- **Rechtliches:** Quellenvermerk DL-De-BY-2.0 + Impressum (§5 DDG) fest in der App (Modal).
- **`data/`-Ist-Stand:** `data/raw/ + data/mastr.db` sind gitignored und aktuell **nicht vorhanden**;
  `fetch_mastr.py` legt sie beim nächsten vollständigen Update automatisch neu an.
- **rebuild_groessen.py:** Temporäres Hilfsskript (DB-frei) zur Neuberechnung der Größenklassen in
  `dist/assets/statistiken.json` aus `einheiten.json`, für den Fall, dass die SQLite-DB fehlt.
  Dieselbe Logik wie `export_app.py::build_statistiken()`.

## Offene Punkte / nächste Schritte (Vorschlag)
- [x] **DSGVO-Update (2026-08-31, Revision v2, deployed):** unpkg-CDN entfernt
      (Leaflet/MarkerCluster inline aus `src/vendor/`), OSM-Kacheln nur nach 2-Klick-Consent
      (localStorage `pvw_tiles_consent`), Datenschutz-Modal komplett überarbeitet (Drittland USA/UK,
      DPF, OSMF/UK-AD, TDDDG §25, HmbBfDI, Widerspruch, Deeplinks, Stand 31.08.2026), Meta
      `referrer`/`robots`. Details + Revisionen: `~/Projects/Domain_Hosting/ingenieur-tools.de/DSGVO/`.
- [x] **Fix Erstladen-ohne-Daten (2026-08-31, V3, as-built):** Beim ersten Besuch (ohne gesetzten Consent)
      lud die hostbare Karte keine Daten ("Lade Daten…" blieb stehen, keine Marker). **Root-Cause:**
      `L.map('map', { zoomControl:true })` ohne `maxZoom` → Leaflet warf die Promise-Rejection
      *"Map has no maxZoom specified"*, die den `await`-Datenblock (`fetch`) in der async `init()` abbrechen
      ließ, bevor er startete. **Fix:** `maxZoom:18` explizit auf der Map gesetzt + Datenladen robust
      (sequenzielle `fetchJson`-Helfer statt `Promise.all`, je Asset einzeln, `statistiken.json` optional,
      Zähler-Fallback aus den Daten). Verifiziert: Erstladen → 53.482 Einheiten, 53 Marker, 44 Cluster,
      0 JS-Fehler; Consent-Klick lädt 18 Kacheln. Revision `index_v3` / `index_singlefile_v3`.
- [x] **Alle Revisionen committet** (Betreiber-Suche, Hersteller-Formatierung, Badge-Removal, Deeplinks,
      Art-Filter, Anlagen-Anzahl-Badge, Größen-Filter + Leistungsklassen, Kritis-Markierung, Gesamt-Diagramm,
      Pipeline + Doku). Working tree sauber (Stand nach Commit dieses Dokuments).
- [x] `docs/statistik.md`, `docs/datenmodell.md`, `docs/update.md`, `docs/architektur.md` auf neue
      PV/Wind-Zahlen, Badge und Staffeln konsistent.
- [ ] **Performance:** Single-File ist auf ~25 MB gewachsen — optional hostbare Version nutzen,
      Daten-CDN, oder GeoJSON-Minify. Bei `file://`-Laden beachten (einmal war eine leere Seite transient).
- [ ] **Domain/HTTPS-Rest:** Portal + Sun-HTTPS warten auf Let's Encrypt (Rate-Limit, 7-Tage-Fenster).
      Watchdog `b950b901245e` (alle 30 Min, alle Hosts) meldet automatisch bei Erfolg. Karte + Galton
      haben `https_enforced=true` (01.09.).
- [x] **GitHub-Publishing** umgesetzt: Karten-Repo öffentlich auf GitHub + GitHub Pages live.
- [x] **V4 — Bundesländer-Tab mit Pie-Charts (2026-09-01, lokal, nicht gepusht):** Neuer Statistik-
      Reiter „Bundesländer" mit interaktivem Donut-Chart (Canvas, keine Bibliothek). Drei Modi via
      Toggle: **Wind** (17 Bundesländer, 31.114 Anlagen, Top: Niedersachsen 6.301), **PV** (16 BL,
      22.363 Anlagen, Top: Bayern 5.850), **Wind + PV** (17 BL, 53.477 Anlagen, Top: Niedersachsen 7.956).
      Measure-Toggle: Anlagen ⇄ Leistung (MW). Klick auf Pie-Segment oder Legende → Karte filtert
      auf Bundesland (Fit-Bounds + Suchfeld-Label). Summary-Box: Tech, Bundesländer-Anzahl, Anlagen,
      Gesamtleistung, Top-Bundesland. 16-Farben-Palette (`BL_COLORS`). Verifiziert: 0 JS-Fehler,
      53.482 Anlagen geladen, Canvas gefunden, alle drei Modi + Measure-Toggle getestet.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V4_Bundeslaender-PieChart.html`.
      **Push-Freigabe vom User ausstehend.**
- [x] **V4 — Update-Historie-Tab (2026-09-01, lokal, nicht gepusht):** Neuer Statistik-Reiter
      „Update-Historie" mit Revisions-Tracker. Vergleicht Datenstände zwischen Updates und zeigt
      Veränderungen über die Zeit. **Erster echter Delta-Test:** 29.08.→01.09. = +19 Anlagen
      (Wind +3/+15 MW, PV +16/+96 MW), 1 entfernt, 7 Bundesländer verändert (Top: Schleswig-Holstein +5 PV).
      **Features:** (1) Delta-Summary-Karten (Wind/PV/Gesamt neu, MW neu, Gesamt-Δ), (2) Verlauf-Tabelle
      mit allen Snapshots (Datum, Wind/PV/Gesamt Anzahlen+MW, Δ Neu/Δ MW), (3) Bundesländer-Veränderung
      je Update (Wind/PV/MW pro Bundesland), (4) Mini-Zeitleiste (Balken der Gesamtanzahl pro Snapshot).
      **Pipeline:** `snapshot.py` (neu) — SQLite-Schema (`snapshots`+`snapshot_einheiten`), `save_snapshot()`,
      `compute_delta()`, `build_historie()`. `import_mastr.py` — sichert alten Stand vor Rebuild, neuen
      Stand nach Import, berechnet Delta. `export_app.py` — generiert `historie.json`. `bundle_singlefile.py`
      — bettet `window.__PVWIND_HISTORIE__` ein. **Cronjob-Plan:** 1. & 15. des Monats (`0 3 1,15 * *`).
      Verifiziert: 53.500 Anlagen, 2 Snapshots, 0 JS-Fehler, alle UI-Elemente getestet.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V4b — Asset-Detail-Ansicht (2026-09-01):** Klickbare Verlauf-Zeilen
      in der Update-Historie öffnen ein Detail-Overlay mit 4 Tabs: **Neu: Wind**, **Neu: PV**,
      **Entfernt: Wind**, **Entfernt: PV**. Jeder Tab zeigt eine Tabelle aller hinzugefügten/entfernten
      Assets mit vollen Daten: Name, MW, Bundesland, Gemeinde, Inbetriebnahme, **Betreiber (NorthData-Deeplink)**,
      MaStR-Nr., **Koordinaten (Google-Maps-Deeplink)**. Auto-Tab-Wechsel zum ersten Tab mit Inhalt.
      Escape schließt das Overlay. `snapshot.py` erweitert: `snapshot_einheiten` speichert jetzt alle
      Asset-Felder (26 Spalten), `compute_delta()` liefert `added_assets`/`removed_assets` als volle
      Asset-Dicts. Historie-JSON wuchs von 5,3 KB auf 18,8 KB (19 Assets × volle Daten).
      Verifiziert: 19 added (3 Wind + 16 PV), 1 removed (Wind), 32 Deeplinks in PV-Tabelle,
      0 JS-Fehler, Overlay öffnet/schließt korrekt.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V4c — Formatierung (2026-09-01):** (1) Bundesländer-Veränderung als
      professionelle Tabelle mit 6 Spalten (Bundesland | Wind Δ | PV Δ | Wind MW Δ | PV MW Δ | Gesamt MW Δ),
      farbcodiert (grün=+, rot=−, grau=—), Spaltenüberschriften in Caps, sortiert nach absoluter
      Veränderung. (2) Hinweis-Text unter „Daten-Verlauf": „💡 Klicke auf eine Zeile mit Δ-Wert, um die
      detaillierte Auflistung aller hinzugefügten und entfernten Wind- und PV-Anlagen zu sehen".
      Verifiziert: 7 Bundesländer-Zeilen, 6 Spalten, Klick-Overlay funktioniert, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V5 — Responsive Design (2026-09-01, LIVE):** 3 Breakpoints via `@media`-Queries.
      **PC (≥1024px):** Stats-Panel 700px breit (vorher 440px) — kein horizontaler Scroll mehr
      bei Statistik-Tabellen. **Tablet (768–1023px):** Stats-Panel 560px. **Mobile (<768px):**
      Stats-Panel 100vw Vollbild, Topbar vollbreit, Toolbar horizontal scrollbar, Modals/Overlay
      vollbreit. Betreiber-/Hersteller-Tabellen: `max-width` für Namensspalte 200→280px.
      Verifiziert: Panel 700px, Tabellen 649px kein horizontaler Scroll, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V5c — Three Fixes (2026-09-01, LIVE):** (1) Datenverlauf-Tabelle: `font-size:12px`,
      `min-width:560px`, `white-space:nowrap` — lesbar wie Bundesländer-Tabelle, horizontaler
      Scroll nur wenn Panel <560px. (2) Bundesländer-Pie: Canvas 220→280px, auf Mobile
      `flex-direction:column` (Chart über Legende, max 320px) — Legende voll sichtbar auf
      Smartphone. (3) Topbar: Meta-Legende + Statistik-Button **nebeneinander** (vorher
      untereinander) — Höhe 31px statt ~50px. "Anlagen" entfernt aus Pie-Legende.
      Verifiziert: Canvas 280px, kein horizontaler Scroll, Topbar 31px, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V6 — Art-Verteilungs-Pie + Sortierungs-Fixes (2026-09-01, LIVE):** Donut-Pie-Charts unter
      den Größenklassen-Balkendiagrammen zeigen die Verteilung nach Anlagentyp (unabhängig der
      Leistungsklasse). **Wind:** Windkraft an Land (29.343/94,3%) vs. Windkraft auf See (1.773/5,7%)
      — umschaltbar Anzahlen/Leistung (79.196 MW vs. 10.969 MW). **PV:** Freiflächensolaranlage
      (11.721/52,4%), Gebäudesolaranlage (10.629/47,5%), Sonstige Solaranlage (34/0,2%) — umschaltbar
      Anzahlen/Leistung (45.092/9.598/40 MW). Canvas 240px Donut mit Loch, Prozent-Labels in Segmenten,
      Legende rechts, Responsive (Mobile untereinander). Weitere Fixes: (5) Hinweistext Update-Historie
      gekürzt ("NorthData/Google-Maps-Links" entfernt), (6) Hersteller-Sortierung auf Anzahl/desc
      geändert (vorher Summe MW), (7) Betreiber bleibt Summe MW/desc.
      Verifiziert: Alle 4 Pie-Kombinationen, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (01.09.2026).**
- [x] **V7 — Jahres-Filter nach Registrierungsdatum (2026-09-02):** Neuer Filter
      "Registrierung" (Dropdown) in der Toolbar unten links. Filtert nach `registrierungsdatum`
      (MaStR-Feld, Format YYYY-MM-DD, 0 NULL-Werte, Bereich 2019–2026). Neues JSON-Feld `"reg"` pro
      Anlage (`export_app.py` erweitert — `registrierungsdatum` zum SELECT + build_units hinzugefügt).
      Dropdown mit 8 Optionen (2019–2026), kombinierbar mit allen anderen Filtern.
      Verifiziert: 2019 → 16.771, 2026 → 2.454, 2019+Wind → 11.578, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7_JahresFilter.html`.
- [x] **V7b — Monats-Filter + Alle-Anlagen-Tabelle (2026-09-02):** (1) Neuer Filter
      "Registrierungsmonat" (Dropdown 1–12, Jan–Dez), kombinierbar mit Jahres-Filter und allen anderen.
      Filtert nach `registrierungsdatum.substring(5,7)` (Monatsteil). (2) "📋 Alle Anlagen anzeigen" Button
      in der Toolbar — erscheint automatisch bei aktivem Filter. Klick öffnet ein Vollbild-Overlay mit
      professioneller Tabelle aller gefilterten Anlagen (12 Spalten: #, Name, Typ, Art, MW, Bundesland,
      Landkreis, Gemeinde, Registriert, Inbetriebnahme, Betreiber, MaStR-Nr.). Chunk-Rendering (500
      Zeilen/Frame via `requestAnimationFrame`) verhindert Blockierung bei großen Mengen — getestet mit
      998 Anlagen. MW farbcodiert (Wind blau, PV orange). Sticky Header, Hover-Highlight, Escape/✕/Klick
      schließen. Responsive (Mobile: Vollbild).
      Verifiziert: 2020+März → 1.236, nur Januar → 5.816, 998 Zeilen gerendert, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7b_MonatFilter_AlleAnlagen.html`.
- [x] **V7c — Sortierbare Tabellen-Header (2026-09-02):** Klick auf jeden Spalten-Header
      in der Alle-Anlagen-Tabelle sortiert die Tabelle. Erster Klick = aufsteigend (▲), zweiter = absteigend (▼),
      Klick auf andere Spalte wechselt Sortierspalte. Sortierbar: alle 12 Spalten. Zahlen (MW) numerisch,
      Text alphabetisch (`localeCompare('de-DE')`), Datum als String (YYYY-MM-DD = chronologisch korrekt).
      Nach Sortierung: Chunk-Rendering für flüssiges Neu-Aufbauen. Header-Hover-Effekt (blau).
      Verifiziert: MW asc 0,3→6,8, MW desc 15→5,56, Name asc alphabetisch, Reg asc 2026-01-02→2026-06-23,
      ▲/▼ korrekt, 0 JS-Fehler.
      Datei: `~/hermes_human-share/PV-Wind-Karte_V7c_SortierbareTabelle.html`.
      **Gepusht auf main + gh-pages (02.09.2026).**
- [x] **V8 — Zubau-Tab mit 6 Charts (2026-09-02, LIVE):** Neuer 6. Statistik-Tab "Zubau" unter
      "Update-Historie". Toggle Anlagen/Leistung (MW). Summary-Box: Gesamt/Wind/PV/ØJahr/Zeitraum.
      6 Charts: (1) Gestapeltes Balkendiagramm Wind+PV, (2) PV einzeln mit Trendlinie,
      (3) Wind einzeln mit Trendlinie, (4) Bundesländer-Heatmap (18 BL × 8 Jahre, sqrt-skaliert,
      Rot→Gelb→Grün), (5) Zubauraten YoY-Wachstum (Liniendiagramm), (6) Wachstum gegenüber
      kumuliertem Bestand (Liniendiagramm, Jahreszubau als % des bisherigen Bestands).
      Daten aus `allUnits.reg` (registrierungsdatum), keine Backend-Änderung.
      Verifiziert: 53.500 Anlagen / 144.894 MW gesamt, 6 Charts, Heatmap-Farben, Toggle, 0 JS-Fehler.
      **Gepusht auf main + gh-pages (02.09.2026).**
- [x] **V8b — Zubau-Tab Anpassungen (2026-09-02, LIVE):** (1) Heatmap-Farben: Rot→Gelb→Grün
      (grün=hoch, rot=niedrig), sqrt-Skala gegen Outlier. (2) Neues Chart 6: Wachstum gegenüber
      kumuliertem Bestand (Jahreszubau als % des bisherigen Bestands). (3) Heatmap MW-Werte ganzzahlig.
      **Gepusht auf main + gh-pages (02.09.2026).**
- [x] **V8c — Inbetriebnahme-Filter (2026-09-02, LIVE):** Zwei weitere Dropdowns in der Toolbar:
      Inbetriebnahme Jahr (1983–2026, dynamisch generiert) + Monat (1–12). Analog zu Registrierungs-
      Filtern, kombinierbar mit allen anderen. `inb`-Feld bereits im JSON (YYYY-MM-DD, 0 NULL).
      Verifiziert: Inb 2010 → 1.826, Inb 2010+Jun → 641, Reg 2020+Inb 2010 → 878.
- [x] **V8d — Zweite Heatmap Inbetriebnahme (2026-09-02):** Heatmap für Inbetriebnahmedatum unter
      der Registrierungs-Heatmap. 18 BL × 41 Jahre (1983–2026), gleiche sqrt-Farbskala.
      (In V8e durch Sub-Tabs ersetzt.)
- [x] **V8e — Zubau-Sub-Tabs (2026-09-02, LIVE):** Zubau-Tab komplett umgebaut mit zwei Sub-Tabs:
      "Registrierungsdatum" (2019–2026) und "Inbetriebnahmedatum" (1983–2026). Beide Sub-Tabs
      identisch aufgebaut mit 6 Charts (Stacked Bar, PV/Wind einzeln, Heatmap, Raten, Kumuliert).
      `renderZubau(dateField)` universell, alle Charts aus einem Feld. Doppelte Heatmap entfernt.
      Chart-Helferfunktionen ausgelagert (drawStackedBar, drawSingleBar, drawTrendLine, drawRateChart,
      drawCumChart, renderZubauHeatmap).
- [x] **V8f — Senkrechte X-Achsen-Labels (2026-09-02):** Jahreszahlen in allen Bar/Rate/Cumulative-Charts
      senkrecht (−90° rotiert). Canvas 260→280px, PAD_B 30→44px. (In V8g weiter optimiert.)
- [x] **V8g — Werte außerhalb + volle Zahlen + X-Achse tiefer (2026-09-02, LIVE):** (1) Werte horizontal
      oberhalb der Balken (nicht innen/senkrecht), `textBaseline:bottom`. (2) `fmtY()` zeigt volle Zahlen
      mit de-DE Tausendertrennzeichen (kein k/M). (3) X-Achsen-Labels +14px tiefer, Canvas 290px, PAD_B 50px.
      Klare Trennung Diagramm ↔ Achsenbeschriftung.
      **Gepusht auf main + gh-pages (02.09.2026).**
- [x] **V8h — Wind-Bruttoleistung-Korrektur (2026-09-02):** Die MaStR-API liefert Wind-Bruttoleistungen
      inkonsistent (teils kW, teils MW). Die alte Heuristik (`>80→kW`) hatte eine Lücke: Werte 15–80 wurden
      als MW interpretiert, obwohl es bei Kleinwindanlagen (15–80 kW) kW-Werte sind.
      Korrektur: `to_mw()` in `import_mastr.py` mehrstufig überarbeitet — Werte 15–80 als kW erkannt
      (außer V236-15MW mit Typbezeichnung). 220 Anlagen korrigiert, fielen danach unter 100-kW-Schwelle
      und wurden gefiltert. Wind: 31.147→30.996, max MW 80→15. Älteste Wind-Anlage jetzt HSW 250 (1988, 0,25 MW).
- [x] **V8i — Disclaimer-Panel + Mobile-Fix (2026-09-02):** Hover/Tap-Disclaimer oben links (ℹ-Symbol).
      6 Absätze: Datenquelle & Qualität (BNetzA bestätigt ~50% geprüft), eigene Bereinigung, Leistungsschwellen
      (Wind ≥100 kW, PV ≥0,5 MWp), Auslandsanlagen, Statistik-Verzerrung, Hobbyprojekt ohne Gewähr.
      `position:fixed`, z-index 1200/1201. Mobile: Trigger unterhalb Suchfeld (top:78px), Panel kompakter
      (max 400px, 12px font). Bug-Fix: fehlendes `</style>` hatte CSS-Block verschmolzen → Consent-Dialog
      erschien beim Scrollen neu.
- [x] **V8j — QA-20-Punkte-Test + 3 Fixes (2026-09-03, lokal ungepushed):** Systematischer Testablauf
      (Build/Struktur, Consent, Disclaimer, Filter, Suche, Statistik, Daten, Performance, A11y, DSGVO,
      Deploy-Parität). Gefunden & gefixt in `src/index.html`:
      (1) überzähliges `</script>` nach markercluster-Block (Zeile ~756, inert aber wartungsfeindlich) entfernt;
      (2) Disclaimer-Trigger überlappte Leaflet-Zoom-Control (beide top:10px) → Trigger top:86px,
      Panel top:122px (Desktop) / Trigger top:96px, Panel top:130px (Mobile);
      (3) Regressionstest des V8i-Style-Bugs: alle 5 `<style>`/2×`<script>` balanciert, keine doppelten IDs.
      Verifiziert: Filter zählen korrekt (10–30 MW = 978: 819 PV + 159 Wind), V8h max Wind 15 MW,
      Suche + Vorschläge ok, alle 6 Statistik-Tabs rendern (handgeschriebenes Canvas, keine Chart.js),
      Impressum/Datenschutz-Modal open/close/ESC, nur OSM-Kacheln als externe Requests, LIVE=LOKAL
      byte-identisch (53.380).

## Verifikation: Filter + Anlagen-Anzahl-Badge (per Browser-Konsole, reproduzierbar)
Sobald die App geladen ist (`allUnits` befüllt), im Devtools-Konsolen-`window`-Kontext:
```js
const set=(type,bl,art,gr)=>{document.getElementById('filter-type').value=type;
 document.getElementById('filter-bl').value=bl;document.getElementById('filter-art').value=art;
 document.getElementById('filter-gr').value=gr||'';
 applyFilters();const e=document.getElementById('art-count');
 return {text:e.textContent,hidden:e.hidden};};
set('','','Freiflächensolaranlage','');      // → {text:"Anzahl: 11.721", hidden:false}   (V8j)
set('','Bayern','','');                      // → {text:"Anzahl: 1.188", hidden:false}   (V8j, Wind-Anteil Bayern)
set('','Bayern','Freiflächensolaranlage','');// → {text:"Anzahl: 4.396", hidden:false}   (hist. 53.500-Wert)
set('pv','','','104,150');                   // → {text:"Anzahl: 2", hidden:false}   (PV 104–150 MW)
set('wind','','','0.5,1');                   // → {text:"Anzahl: 4.079", hidden:false}   (hist. 53.500-Wert)
set('','','','');                            // → hidden:true
```
Referenzwerte (53.380-Datensatz, V8j-Test 2026-09-03): Wind gesamt 30.996, Bayern-Wind 1.188,
Freiflächen-PV 11.721, Größenklasse 10–30 MW = 978 (819 PV + 159 Wind), Inb-Jahr 1988 = 2
(älteste: HSW 250, 0,25 MW). Max Wind-MW = 15,0 (V8h). Die Zahl muss
stets `allUnits.filter(...)` für die gerade aktiven (Art, BL, Gr, Typ-)Filter entsprechen.
Die Größenklassen in `_stats.groessenklassen` haben `wind`/`pv`/`gesamt` mit je **11 Einträgen**;
Kritis-Klassen (`kritis:true`) sind nur `104–150` und `150+`.
Historische Referenzwerte des 53.500-Datensatzes (vor V8h): Bayern 7.042, Bayern+Freifläche 4.396,
PV 104–150 = 2, Wind 0.5–1 = 4.079, Summen Wind 31.116 · PV 22.384 · Gesamt 53.500.

## Besondere Hinweise für neue Sessions
- **Kein JSON/HTML-Rohcode in Telegram-Chat**; klickbare Datei per `MEDIA:` oder send_telegram_file senden.
- **Ergebnis-Kommunikation:** deutsch, kurze Alarm-Nachrichten bei Fehlern, hart prüfen (kein Halluzinieren),
  Änderungsliste mit Quellen.
- **GitHub-Publishing** (umsgesetzt): Repo `pv-wind-map` (und `ingenieur-tools-portal`) sind öffentlich auf
  GitHub, `main` ist das Quell-Repo, `gh-pages`-Branch deployt die Site. Keine Secrets im Repo.
- **Andere LLMs prüfen Ergebnisse gegengegen** — gemeldete Bugs ernst nehmen, verifizieren, fixen.

## ⚠️ Wichtige Regeln (unveränderlich)

### 1. Snapshots — niemals löschen, überschreiben oder verändern
Die in `data/mastr.db` gespeicherten Snapshots (Tabellen `snapshots` + `snapshot_einheiten`)
sind die **historische Datenbasis** des Projekts. Sie dienen dem Revisions-Tracker
(Update-Historie-Tab in der HTML-App) und bauen über Monate/Jahre eine vollständige
Veränderungshistorie auf.

- **Snapshots dürfen niemals gelöscht werden** — auch nicht alte oder scheinbar irrelevante.
- **Snapshots dürfen niemals überschrieben oder verändert werden** — jeder Snapshot ist
  ein unveränderlicher Punkt-in-Zeit-Datensatz.
- **Neue Snapshots werden nur angefügt** (`INSERT`, niemals `UPDATE`/`DELETE` auf bestehende).
- **`data/mastr.db` wird nicht auf GitHub gepusht** (gitignored, 64 MB) — die DB bleibt lokal.
- Bei Verlust der DB (z. B. SD-Karte defekt) ist die Historie unwiederherstellbar.
  `historie.json` (auf gh-pages, ~19 KB) enthält die aggregierten Deltas, aber nicht die
  vollen Asset-Daten — diese leben nur in der SQLite-DB.

### 2. Iterationen — alle speichern, niemals löschen
Jeder klickbare HTML-Iterationsschritt, der während der Entwicklung erstellt wird, muss im
Ordner `iterations/` gespeichert werden (`V<Version>_<Kurzbeschreibung>.html`).

- **Jede Iteration muss gespeichert werden** — auch fehlerhafte oder verworfene.
- **Dateien dürfen niemals gelöscht oder überschrieben werden.**
- Der Ordner ist gitignored (Dateien ~25 MB), bleibt also lokal.
- Übersicht: `iterations/README.md` (wird committet, enthält Versions-Tabelle).
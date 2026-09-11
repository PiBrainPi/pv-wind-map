# Projektstand (Handover) — PV & Wind Karte (MaStR)

> **Dieses Dokument dient als Einstieg für jede neue Agenten-/Arbeitssession.**
> Stand: 2026-09-11 (**V40 — EEG-Donut entfernt + 2-Spalten-Diagramme + DEPLOY; zuvor V39/V38/V37/V36**) · Repo: `/home/claw_01_rasbpi5_1/Projects/pv-wind-map`

## Aktueller Stand (2026-09-11, **V40 — deployt auf GitHub Pages (User-Freigabe erteilt)**)

**Code-Stand:** V40 (lokal UND live; V35.1→V40 Deploy am 11.09. via `scripts/deploy_ghpages.sh`)
**V40 (20-Punkte-Plan `2026-09-11_V40_EEGDonut_Entfernt_Deploy_20-Punkte-Plan.md`):**
- **User-AP1:** Chart „EEG-Registrierung" **komplett entfernt** (Semantik-Falle V39:
  MaStR bildet Vergütungsweg nicht ab — Details `fehlerbehebung.md` F-EEG-1).
  „Wachstum nach Inbetriebnahmejahr" + „Technologie-Verteilung" jetzt **nebeneinander**
  (flex, Wachstum flex-basis 480px, Stack bei schmalem Viewport). Measure-Toggle
  (Anlagen/MW) + Tech-Filter (Alle/Wind/PV) wirken auf beide verbleibenden Charts.
- **User-AP3:** Explizite Freigabe erteilt → Commit + Push main + Deploy gh-pages live.
**V39 (20-Punkte-Plan `2026-09-11_V39_EEGSemantik_Fix_20-Punkte-Plan.md`):**
- **User-Meldung:** CEE-Mitarbeiter: PV-Assets nach Leistung überwiegend NICHT EEG-vergütet,
  Diagramm zeige aber 100 % „mit EEG" → Bug-Verdacht.
- **Audit-Ergebnis (kein Daten-Bug, Semantik):** Diagramm wertet `EegInbetriebnahmeDatum`
  = „EEG-Anlage registriert?" aus. MaStR-Registrierung ist für alle ortsfesten Anlagen
  Pflicht — unabhängig vom Zahlungsanspruch (MaStR-Webhilfe). Kein Feld im MaStR bildet
  Vermarktungsweg/PPA ab. CEE: 184 Anlagen/827 MW, 100 % EEG-registriert (korrekt).
  PPA-Geschäfte laufen ÜBER registrierte EEG-Anlagen → erscheinen unter „mit EEG".
- **Fix (UI):** Chart-Untertitel „EEG-Anlage registriert: ja/nein", Erklärtext weist auf
  PPA-Direktvermarktung + nicht abgebildeten Vergütungsweg hin. Details: `fehlerbehebung.md`
  F-EEG-1. Revision `iterations/V39_EEGSemantik_Praezisierung.html`.
**V38 (20-Punkte-Plan `2026-09-11_V38_BetreiberDiagramme_TechFilter_PanelBreite_20-Punkte-Plan.md`):**
- **User-AP1:** Tab „Betreiber" → Diagramme: neben dem Measure-Toggle (Anlagen/MW) jetzt ein
  **Technologie-Umschalter Alle / Wind / PV**. Im Wind-/PV-Modus fließen nur Anlagen der gewählten
  Technologie in alle Charts ein; der EEG-Donut zeigt dann nur 2 Segmente (mit/ohne EEG) der
  gewählten Technologie — eindeutig erkennbar (Sub-Labels „— nur Windanlagen 🌬️" / „— nur PV-Anlagen ☀️",
  Note mit „TECHNOLOGIE-FILTER: …"). Kombinierte Ansicht („Alle") = bisheriges Verhalten (4 Segmente).
  Hintergrund: 4-Segment-Donut trennte Wind/PV×EEG für User nicht sauber auf den ersten Blick.
- **User-AP2:** `#stats-panel` Desktop 984 → **1063 px** (+8 %, Off-Canvas-Offset −1024 → −1103);
  Tablet (560) + Mobil (100vw) unverändert.
- Revision `iterations/V38_BetreiberDiagramme_TechFilter_PanelBreite.html` + human-share-Kopie.

**V37 (50-Punkte-Plan `2026-09-11_V37_TypenNormalisierung_Doku_50-Punkte-Plan.md`):**
- **User-AP1:** MaStR-Typenbezeichnungen sind inkonsistent (E40/E-40/E 40/e40 …). Recherche: 752 Typ-Gruppen mit mehreren Schreibweisen auf Karten-Basis, 9.741 betroffene Records.
- **Regel (Majority-Vote, User-Vorgabe):** häufigste Schreibweise = korrekt; Tie-Break kürzeste/dann alphabetisch. Mapping: `scripts/build_typ_normalisierung.py` → `data/typ_normalisierung.json` (1.547 Mappings inkl. Ganz-Bestand-Nachlauf, Report-CSV nebenbei).
- **Pipeline-Regel:** `import_mastr.py::normalize_typ()` (Legacy-Import, vor to_mw — 15-MW-Ausnahme sieht normalisierten Typ) + `export_app.py` (Wind-only, vor to_mw). to_mw-Diff durch Normalisierung: 0 von 43.478 (verifiziert).
- **Einmalige DB-Bereinigung:** `scripts/fix_typenbezeichnung.py` — raw_json 9.742 + 258 = **10.000 Records**, Legacy `einheiten` 7.368 + 37 = **7.405**; Backup `data/backups/mastr.db.backup_20260911_110745`; Rescan danach 0 Dubletten-Gruppen. **Idempotent.**
- **Pitfall (dokumentiert in fix-Skript-Docstring):** Karten-Basis-Scan (Geolok+≥0,1 MW) übersieht Kleinwind ohne Geolok → 1. Lauf ließ 82 Rest-Gruppen; `--all-bestand`-Nachlauf schloss sie (258 Records); Mapping-Datei dann mit Karten-Basis-Mappings gemerged (Rekonstruktion aus Backup, 0 Konflikte). ⚠️ Mapping-JSON enthält jetzt 1.547 Einträge (Karten-Basis ∪ Ganz-Bestand) — NICHT erneut mit `--all-bestand` überschreiben, sonst sind nur noch die Rest-Mappings drin.
- **Neuer Datenstand im Export:** 65.708 Anlagen (31.005 Wind / 22.421 PV) — Delta-Import von Samstag 06:10 ist eingeflossen; Infobar entsprechend.
- **Typ-Tab-Effekt:** E-40 jetzt 628 Anlagen als EINE Zeile (vorher 290+215+122+1 getrennt); Klick-Filter (selectTyp) trifft alle Varianten.
- **Revision:** `iterations/V37_TypenNormalisierung.html` (+ human-share). Kein Commit/Push ohne User-Freigabe.

## Aktueller Stand (2026-09-11 vormittag, **V36 — Betroffenheit: Zeitraum-Option**)

**Code-Stand:** V36 (lokal, **noch nicht gepusht/committed**; online/Basis: main `da9dc9f`, gh-pages `4d1a17c` = V35.1-Deploy)
**V36 (50-Punkte-Plan `2026-09-11_V36_Zeitraum_Betroffenheit_50-Punkte-Plan.md`):**
- **AP1 Zeitraum-Option im Betroffenheits-Tab:** „2 · Optionen" → Zeitfenster bekommt 3. Option **„Zeitraum (von–bis)"** (`#bff-fenster` value `range`) + Datums-Zeile `#bff-von`/`#bff-bis` (nur bei range sichtbar, Toggle in initBetroffen onchange).
- **Semantik (User-Entscheid 10.09., clarify):** Zeitraum = Inbetriebnahmedatum (`inb`)/Registrierungsdatum (`reg`) der Bestands-Anlagen — NICHT die Update-Deltas (die reichen nur bis 01.09.2026; User-Beispiel 01.01.2023 wäre dort leer). Modus-Feld (both/reg/inb) regelt, welches Datum zählt. Kandidaten direkt aus `allUnits` (Match-/Render-Pfad NAP/Radius unverändert wiederverwendet); ENTFERNT-Events entfallen im range-Modus bewusst (dokumentiert im Erklärtext „3 · Zeitraum-Modus").
- **Validierung:** leere Felder / von>bis → Statuszeilen-Warnung, kein Scan; Statuszeile: „N Treffer · X Kandidaten im Zeitraum geprüft · Y ms".
- **Verifikation (Multi-File 8805 + Singlefile file://, je 0 JS-Errors):** Toggle ✓, Validierung ✓; User-Beispiel 1 (01.01.–01.03.2023, Ref. Solarpark Döllen GmbH): 467 Kandidaten (JS-Gegenrechnung nBoth=467 identisch), 1 Treffer (SEE996415574024, PV 15,87 MW, NAP-Match, inb 01.03.2023) == unabhängiger Gegencheck; Popup per echtem Klick ✓ (V33.1-Regel, Plain-Layer-Pfad); Anzeigen-Modus ✓. Beispiel 2 (01.01.–05.09.2026): 5.027 Kandidaten, 14 Treffer/236,1 MW. Modus-Filter: inb 9/2.255, reg 14/4.987. Regression: last (1 Treffer/185 Assets) + all (1/205) unverändert, 11 Tabs ok, AP2-Reset + Idempotenz ✓, Infobar 31011/22402 ✓. Visuelle Bestätigung Dropdown+Datumsfelder ✓.
- Revision: `iterations/V36_Zeitraum_Betroffenheit.html` (+ human-share). **Kein Commit/Push ohne User-Freigabe.**

## Aktueller Stand (2026-09-10 Abend, **Pipeline: Delta-Fetch + Umlaut-Fix F-Fetch-1**)

**⚠️ KRITISCHER API-BEFUND (10.09., live verifiziert):** MaStR hat den JSON-Endpoint geändert —
der Filter-Column heißt jetzt `Energieträger` (MIT Umlaut); die alte Schreibweise
`Energietraeger` wird STILL ignoriert (Total = 9.435.237 Gesamtbestand statt ~32k Wind).
Letzter korrekter Lauf mit alter Syntax: 06.09. → **der ursprüngliche Sonntags-Cron (13.09.)
wäre ausgerudert.** Fix in `fetch_v2.py` (F-Fetch-1, Details fehlerbehebung.md).

**Pipeline 2.0 = Delta-Modus (10.09., 30-Punkte-Plan `2026-09-10_Pipeline2_UmlautFix_DeltaFetch_30-Punkte-Plan.md`):**
- `fetch_v2.py --delta`: nur Records mit `Letzte Aktualisierung > letzter Lauf` (Operator
  `~gt~`, Datum TT.MM.JJJJ; State `data/raw_v2/fetch_state.json`). Erstlauf 06.09.→10.09.:
  **Wind 105 + PV 160 Delta-Records statt 55k Vollabruf (~0,5 %)**; ohne `--delta` = Vollabruf (Rückfalloption).
- `scripts/merge_delta.py` (NEU): Delta-Dateien (`data/raw_v2/delta/`) per UPSERT je
  MaStR-Nummer in die Basis-JSONs mergen + Statuswechsel-Bereinigung (Nummer nur im
  Strang des aktuellen Status). Perf-Fix: O(n) statt O(n²) — 2,5 h → 21 s.
- Sicherheitsnetz: je Strang API-Gesamttotal vs. Basis+Delta (Toleranz 5 %) → bei
  Abweichung automatischer Vollabruf-Fallback. **Quartalsweise 1× Vollabruf PFLICHT**
  (Merkposten User-Freigabe 10.09.): einmal pro Quartal `pipeline2_update.sh` manuell mit
  Vollabruf laufen lassen (`python3 scripts/fetch_v2.py --extended-status` OHNE `--delta`,
  dann merge/import wie gehabt) — nur der Vollabgleich findet gelöschte Register-Einträge,
  die in keinem Delta erscheinen. Nächster Quartals-Vollabruf: ~Anfang Dezember 2026.
- `pipeline2_update.sh` nutzt jetzt: fetch `--delta` → merge → import → NAP → import.
  **Cron-Schedule seit 10.09. (User-Freigabe): SAMSTAGS 06:10** (vorher sonntags 18:00).
- Verifikation: Konsistenz nach Merge 0 Duplikate / 0 Status-Mismatches (67.176 Records);
  2. Delta-Lauf direkt danach = 0 Records (idempotent); import_v2 mit Backup
  (mastr_20260910_225009.db, 546,7 MB): einheiten_raw 67.183, georef 53.413 unverändert.
- DB-Backups VOR allen lokalen DB-Schreibvorgängen (Deploy-Regel) eingehalten.

## Aktueller Stand (2026-09-10, **V35/V35.1 — Betreiber-Diagramme, Filter-Reset-Ursprungszustand, Betroffenheits-Legende**)

**Code-Stand:** V35 (lokal, **noch nicht gepusht**; online/Basis: main `d8dd8e4`, gh-pages `15c2058` = V29.1-Deploy)
**Kern-Basis (unverändert):** 31.011 Wind · 22.402 PV = **53.413** In-Betrieb georef · Karte 65.663

**V35 (10.09., 50-Punkte-Plan `2026-09-10_V35_BetreiberCharts_Reset_Legende_50-Punkte-Plan.md`):**
- **AP1 Betreiber-Diagramme:** Tab „Betreiber" → Button **„📈 Diagramme"** neben dem Suchfeld (nur ab 2 Zeichen sichtbar). Chart-Block: (1) gestapeltes Wachstums-Balkendiagramm nach **Inbetriebnahmejahr** (Wind blau/PV orange, Toggle Anlagen/Leistung MW), (2) Donut **Technologie-%** (Wind/PV), (3) Donut **EEG-Registrierung** (Wind mit/ohne, PV mit/ohne) + Erklärsatz. Scope: Einzelbetreiber ODER Gruppe/Portfolio (Brand/Kern-Match wie die Tabelle). **Datenbasis:** neuer Export-Feld `eeg` (`EegInbetriebnahmeDatum` vorhanden = 1; PV 95,1 % / Wind 80,8 %). User-Freigabe-Definition 10.09.: „Mit/Ohne EEG-Registrierung" (MaStR hat keinen direkten Vergütungs-Status).
- **AP2 Filter-Reset = Ursprungszustand:** „🗑️ Filter löschen" beendet jetzt ZUSÄTZLICH den BFF-Anzeigen-Modus (`_bffResetAnalysis`), entfernt Ringe/rote entfernte-Marker/NAP-Fokus-Kreis (`__napFocusCircle`), schließt Stats- + NAP-Panel, leert Suche + Popup, setzt Karte auf Default-View `[51.5, 10.0]` z6, dann alle Filter auf Default. Idempotent (Doppel-Klick getestet).
- **AP3 Betroffenheits-Legende:** Beide „ℹ️ Wie funktioniert…?"-Blöcke um Abschnitt „Karten-Symbole & Farben" erweitert: grüner gestrichelter Ring (Neubau), roter gestrichelter Ring (nur Abmeldungen), roter gefüllter Punkt (entfernte Anlage), blau/orange Punkte (Wind/PV), gestrichelter Umriss (in Planung), grauer Punkt + Kreuz (stillgelegt), blauer Kreis (NAP-Fokus) + Hinweis auf AP2-Reset.
- **Nebenfix:** `export_app.py` — DB wurde vor dem Historie-Schreiben geschlossen → „Historie übersprungen (Cannot operate on a closed database)". Jetzt `db.close()` in `finally` → Historie wieder regulär (3 Snapshots, Δ 06.09. +125,54 MW korrekt).
- **Kosmetik:** Donut bei nur 1 Segment ohne weiße Trennlinie (100-%-Donut).
- **Verifikation (Singlefile, file://, 0 JS-Errors):** AP1 ENERPARC 522 Anlagen/3.217,5 MW == Tabelle, EEG 94,1/5,9 %, Einzelbetreiber „stadtwerke bielefeld" 7 Wind → 100 %-Donuts; wpd 243 (236 Wind/7 PV) → 2 Segmente + weiße Trennlinie + %-Labels; AP2 14 Assertions grün (Layer weg, View default, Filter default, Infobar korrekt); AP3 Legende 8/8 Checks + Sichtprüfung; Regression: Bayern-PV-Badge 5.862 ✓, alle 11 Tabs rendern ✓, Zubau-Chart ✓.
- Revision: `iterations/V35_BetreiberCharts_Reset_Legende.html` (+ human-share). **Deploy/Push nur nach User-Freigabe.**

**V35.1 (10.09., 20-Punkte-Plan `2026-09-10_V35-1_Donuts_MeasureToggle_20-Punkte-Plan.md`):**
Donuts „Technologie-Verteilung" + „EEG-Registrierung" jetzt ebenfalls über den Toggle **Anlagen ⇄ Leistung (MW)** steuerbar (User-Wunsch): 4 MW-Akkus (eegW_mw/noEegW_mw/eegP_mw/noEegP_mw) in `renderBetreiberDiagramme()`, Donut-Labels mit Einheit („Wind (MW)" / „PV (MWp)"), Untertitel dynamisch (`#bc-tech-sub`/`#bc-eeg-sub`). Verifiziert: ENERPARC MW-Modus PV 3.217,514 MWp == Header-Summe; wpd Wind-MW 140,12+1.266,82 = 1.406,94 == erwarteter Wind-MW-Summe; Rück-Toggle auf Anlagen korrekt; Pixel-Check alle 3 Canvases gezeichnet; Infobar unverändert. Revision: `iterations/V35-1_Donuts_MeasureToggle.html` (+ human-share).

## Aktueller Stand (2026-09-09, **V34 UX-Runde 2 abgeschlossen**)

## Aktueller Stand (2026-09-09, **V33 UX-Runde — lokal fertig, Deploy pending**)

**Code-Stand:** V33 (lokal, **noch nicht gepusht**; online/Basis: main `d8dd8e4`, gh-pages `15c2058` = V29.1-Deploy)
**Kern-Basis:** 31.011 Wind · 22.402 PV = **53.413** In-Betrieb georef · Karte 65.663
**V33 (UX-Runde, 09.09., 20-Punkte-Plan):** WP1 LK-Scrollbalken kontraststark (14 px, sticky
Name-Spalte bestätigt) · WP2 Statistik-Panel z-index 1800 über Topbar (User-Wunsch: Panel
komplett sichtbar; ESC/✕/Toggle schließen) · WP3 Betroffenheit: Ringe nach Treffer-Art
(**grün** = Neubau, **rot** = nur Abmeldungen) + Ring-Legende im Summary + entfernte Assets
als rote Marker im Anzeigen-Modus (Root-Cause „leere Ringe": ENTFERNT-Treffer sind korrekt,
aber nicht sichtbar — 9 NAPs nur-entfernt, entfernt-Assets nie in allUnits) · WP4 Singlefile
ab `file://` lädt **CARTO basemaps** statt OSM (OSMF-Referer-Pflicht 03/2026 → „403r Access
blocked"; Consent-Text dynamisch mit CARTO-Hinweis). Details: `fehlerbehebung.md` F-V33-1…4.
**V33.1 (09.09., spät):** BFF-Anzeigen-Modus: `_bindLazyPopup` im Plain-Layer-Pfad nachgebunden
(V32-WP4-Lücke — Klick auf Bestands-Anlage war tot). Revision: `iterations/V33-1_Popup_Hotfix.html`.
Finale Revision V33: `iterations/V33_UX_Runde.html` (+ human-share).

**V34 (09.09., spät, 20-Punkte-Plan „UX-Runde 2"):**
- **WP1** LK-Tab: Scrollbalken JETZT OBERHALB der Tabelle (synthetischer Scroller
  `#landkreis-scroll-bar`, bidirektional per JS synchronisiert, Loop-Schutz
  `_lkSyncing`); Tabelle selbst ohne sichtbaren Balken (`scrollbar-width:none`).
- **WP2** Popup-Re-Open-Bug gefixt: Root-Cause = Doppel-Dispatch (`_lazyPopup` +
  Leaflet-`_openPopup` von `bindPopup` toggelten gegeneinander). Fix: KEIN
  `marker.bindPopup()` mehr — eigenes `L.popup` pro Marker, Toggle im eigenen Handler,
  Re-Open nach Kartenklick jederzeit möglich. NAP-Link (V21.4) übernommen.
- **WP3** Statistik-Panel 20 % breiter: 820 → **984 px** (right:-1024 px); Tablet/Mobil
  unverändert.
Finale Revision: `iterations/V34_UX_Runde2.html` (+ human-share).

**Code-Stand:** V32.1 (lokal, **noch nicht gepusht**; online/Basis: main `d8dd8e4`, gh-pages `15c2058` = V29.1-Deploy)
**Kern-Basis:** 31.011 Wind · 22.402 PV = **53.413** In-Betrieb georef (Infobar)
**Karte gesamt:** 65.663 Anlagen (Wind 42.006 · PV 23.657)
**V32 (Bugfixrunde, 08.09.):** WP1 NAP-Ranking-Einbettung + NAP-Karten-Klick · WP2 LK-Scroll
· WP3 Snapshot-7/8-MW-Migration (Δ +125,54 MW statt −8.410,85) · WP4 BFF-Clustering-Fix
· WP5 NB-Filter-Listener · WP6 Doku. Details unten.
**V32.1 (Hotfix, 09.09.):** Singlefile-TDZ — keine Marker + Statistik-Button tot beim direkten
Öffnen der Singlefile. Root-Cause + Fix + Verifikation: unten „V32.1".
Finale Revision: `iterations/V32-1_Singlefile_Hotfix.html` (+ human-share).
**Wichtig:** Infobar-Zahlen älterer Doku-Abschnitte sind historische Stände — ab V30 gelten
ausschließlich 31.011/22.402/53.413/65.663. **Verifikationsregel ab V32.1:** Änderungen müssen
IMMER auch im Singlefile (`dist/index_singlefile.html`) browser-verifiziert werden — der
Multi-File-Build maskiert TDZ-/Sync-Fehler durch await.

## Aktueller Stand (2026-09-06 Abend, **V27 = Daten-Update LIVE** — Code V26, Daten 06.09. 18:59)

**LIVE:** https://wind-pv-map.ingenieur-tools.de (**V26-Code + Datenstand 2026-09-06 18:59**) · **Code-Stand:** V26 (main `f842c9a`, gh-pages `5e94114`) · **Single-File:** 42,4 MB
**Daten-Update (06.09., außer der Planung auf User-Wunsch):** Pipeline 2.0 (Wind/PV 118 Felder
inkl. F5-Status-Flag + NAP inkrementell, 28 neue NAPs → 27.898; 17 MaStR-Datenfehler =
unverändert datenseitig) + `build.sh` (Snapshot-Delta: **52 neu [+142,6 MW Wind / +108,4 MWp
PV], 133 entfernt**, Kern-Bestand 53.424 In-Betrieb georef). Karte jetzt **65.676 Anlagen**
(Wind 42.008 · PV 23.668; Infobar 31.010 Wind · 22.409 PV im In-Betrieb-Kern).
Verifiziert: Landkreis-Tab 377 LKs · 51.640 Assets · 27.338 NAPs; Geo-Suche „dithmarschen"
✓; „rwe" 126 Betreiber ✓; Größenklassen Park-Modus Max-Cluster 958,65 MW ✓; V26-Scrollbar ✓.
Revision: iterations/V27_Datenstand_2026-09-06.html.
**V27b (06.09. spät abend, User-Befund kW/MW):** Snapshot-Delta hatte 133 Wind-Abgänge,
davon 107 alte Klein-WKA (TW80 = 80 kW, als „80 MW" geführt). Ursache: MaStR meldet
Kleinwindräder teils in kW ohne Einheiten-Kennzeichnung; to_mw-Heuristik (v<15 ⇒ „bereits
MW") ließ sie durch. **Fix (beide Pfade):** Physik-Check in `to_mw` — eine echte ≥1,5-MW-WEA
hat RD ≥ 60 m (empirisch: 25.151 Anlagen, MIN exakt 60,0) ⇒ RD < 60 & ≥1,5 MW = kW-Falsch-
angabe → /1000 (→ <100 kW → gefiltert). `export_app` übergibt RD jetzt an to_mw (fehlte!).
Karten-Pfad hatte nur 2 aktive Fälle (V117/N163 mit falschem RD im MaStR, echte MW) — raus.
776 ungeorefte Kleinwind-Fälle (EasyWind 6 kW etc.) betrafen die Karte nie. PV unberührt
(kWp→/1000 eindeutig; Top 162 MWp = real). Nachher: Wind 42.006 (−2), MW-Summe unverändert
plausibel (~82 GW In-Betrieb real). Revision: iterations/V27b_KW_MW_Fix.html.
**V29/V29.1 (06.09. spät, 3 Pakete):** Paket 1 LK-Tab: Hinweistext „← Tabelle ist horizontal
scrollbar →" entfernt, stattdessen dauerhaft sichtbarer Scrollbalken UNTER der Tabelle
(Webkit+Firefox-Styling). NAP-Tab-Klick → Karte zeigt NUR NAP-⚡-Marker + zugehörige Anlagen
(renderMarkers-Analogie zum Hersteller-Tab; vorher openNapPanel). KRITIS-Rahmen/-Badge/-Legende
entfernt (User: einheitliche Klassenformatierung). Größen-Klick auf In-Betrieb-Basis (bs35) —
vorher flossen Planungsprojekte ein (4 statt 2 bei 104–150). Historie-Dedup beim Load
(Duplikate 01.09./06.09. mit leerem Delta = 5 tote Zeilen; je Datum gewinnt Snapshot mit
Delta-Inhalt) — Betroffenheit „letztes Update" funktioniert damit wieder (58 Treffer enova).
Paket 2: main 55c42af + 729e068 gepusht, Deploy OK, Live HTTP 200 (0 kritis-glow/hint-Refs).
Paket 3 Artikel as-built: `Artikel/artikel_20260906_v29.md` (65.674 Anlagen, 42.006 Wind,
enerparc 3.218 MW, NAP 30.948 Lokationen/27.898 NAPs, enova-Abb. 8 auf 58-Treffer-Stand,
Projektentwicklung-Abschnitt an exakter Position, LK/Gemeinde-Such-Hinweis, HSE raus) +
`screenshots_v29/` (9 neue Playwright-Shots vom Live-Stand) +
`LinkedIn_Artikel_Vorschau_20260906_v29.html` (build_vorschau_v29.py). Kopien in human-share.
**V28 (06.09. Nacht, 4 Arbeitspakete User):** ① LK-Tabelle übergelaufen auf PC — Root-Cause
`#stats-body` Flex-Item ohne `min-width:0` (wuchs auf Inhaltsbreite 1.024 px) → Fix + Scroll-
Container max-width:100 %, verifiziert (Container 769 px, Tabelle 1.024 px, scrollbar). ② Neuer
Statistik-Tab **„NAP"** (zwischen Landkreis & Spannungsebenen): Ranking 27.130 NAPs nach
angeschlossener Leistung — neue `build_nap_ranking()` in export_app.py → `nap_ranking.json`
(to_mw-normalisiert, BL-Mehrheitskonsens, Gesellschaften DISTINCT, lat/lon-Mittel; Top: SP WINI
648 MW, UW Bertikow 548 MW/51 Ges. ✓). Tabelle sortierbar (Default MW desc), Suchfeld mit
Live-Suggest (Bundesländer ZUERST, dann NAP-Namen), NAP-Klick → openNapPanel (Gruppenansicht
+ Karte-FlyTo), BL-Klick → Bundesland-Filter der Hauptseite. ③ Spannungsebenen-Bug bestätigt:
`computeSpannungData()` nutzte `_lastFiltered` → mit Karten-Filter „nur 100 MW". Fix: immer
allUnits mit bs===35 (In Betrieb), filter-unabhängig + neue Angabe „X Assets" je Ebene.
④ Toolbar-Button **„🗑️ Filter löschen"** (rot): setzt alle 11 Filter auf Default, nur st-35
„In Betrieb" gecheckt, Suche+Gemeinde-Optionen+Badge zurück, applyFilters(). Verifiziert:
Bayern+5-10MW+St31+Suche → Reset → alles Default, Infobar 31.010/22.409.
**Achtung Pitfall:** Patch-Skript ohne `open().write()` endet still (p4a schrieb HTML nicht →
Button fehlte im DOM trotz JS-Bindung; erst Browser-DOM-Diagnose (querySelectorAll len 0 bei
innerHTML.includes true) entlarvte fehlendes Element). Revision: iterations/V28_NAP_Tab_SpannungsFix_FilterReset.html.
gh-pages `…` Deploy OK, Live-Check nap_ranking.json 200. main `2481411`.
**Cron:** Pipeline-Intervall User-Wunsch → **sonntags 18:00** (Job 79229dc1690d, vorher
1./15. 03:00). Nächster Lauf: 13.09. 18:00.
**V25 (06.09.):** **Bugfix „Alle Anlagen anzeigen"** — V23-Regression: Geo-Filter (LK/Gemeinde)
fehlten in `showAllUnits()` → ReferenceError, Overlay öffnete nie. Jetzt: LK+Gemeinde gelesen
und gefiltert (Test: SH+Dithmarschen = 923 Anlagen, Meta korrekt). **Mobile:** Landkreis-Tab
horizontal scrollbar (Touch-Wischen, Hinweis unter der Tabelle), Header vollständig lesbar
(375-px-Test: Tabelle 1.024 px, alle 9 Header FULL); PC unverändert Fixed-Layout ohne Scroll.
Such-Placeholder: „Suche Anlage… z.B. Solarpark Döllen GmbH".
**LIVE-Deploy:** 06.09.2026 (V22+V23+V24 gemeinsam, User-Freigabe erteilt) · **main:** `7172681` · **gh-pages:** `1b9c85a`
## V30 (08.09.2026) — F-02 Design-Entscheidung

**User-Entscheidung:** Karten-Klicks (Betreiber/Gruppe, Hersteller, Geo-Suche BL/LK/Gemeinde,
NAP/Lokation, Bundesland) zeigen **bewusst alle Betriebs-Status**. Ausnahme: Größenklassen-Klick
bleibt In-Betrieb (bs35), konsistent zur Chart-Basis. Kein Code-Fix; dokumentiert in
`BUGS_ZU_ERLEDIGEN_2026-09-08.md` (F-02 geschlossen).

## V30 Fixrunde (08.09.2026) — F-04 Zahlendrift (Variante B: strikte Abgrenzung)

**User-Entscheidung 08.09.2026: Variante B** — Abgrenzung konsequent strikt durchsetzen:
**Wind ≥ 0,1 MW (>= 100 kW), PV ≥ 0,5 MWp (>= 500 kWp).** Die 11 PV-Grenzfälle mit
499,92 kWp (fetch-Filter `gt~499.9` hatte sie durchgelassen) sind **entfernt**.

**Neue konsistente Basis (alle Zahlen aus identischem Export):**
- **In-Betrieb-Kern (Infobar): 31.011 Wind · 22.402 PV = 53.413** (vorher 31.010/22.409 = 53.419, Drift behoben)
- Karte gesamt: **65.663 Anlagen** (Wind 42.006 · PV 23.657 inkl. Planung/stillgelegt)
- Legacy-V1-Tabelle war STALE (fehlte 1 Wind-Neuzugang SEE944775195571, enthielt 7 PV-Grenzfälle unter der eigenen Abgrenzung) — `meta.counts` zählt jetzt aus dem Export selbst, nie wieder Drift

**Fix-Umsetzung:**
1. `scripts/fetch_mastr.py` + `fetch_v2.py`: PV-Fetch-Filter `gt~499.9` → `ge~500` (strikt)
2. `export_app.py`: Abgrenzungs-Sicherheitsnetz nach `build_units` (PV ≥ 0,5 MWp / Wind ≥ 0,1 MW nach to_mw; 11 Einheiten verworfen)
3. `export_app.py`: `meta.counts` aus `units` (nur bs 35) statt Legacy-V1-Tabelle — Infobar-Semantik unverändert (nur In-Betrieb)
4. Legacy-Projektstand-Zahlen (65.676/42.008/23.668, 53.424) sind historisch; neue Kopfzahlen nach diesem Stand: 65.663 gesamt / 31.011 Wind / 22.402 PV (Infobar) / 53.413 Kern

**V24 (06.09.):** Landkreis-Tab-Header mit Leistungseinheiten („Leistung PV **(MWp)**",
„Leistung Wind **(MW)**"); Statistik-Panel **ohne horizontales Scrollen** — alle 9 Tabs
und alle Tab-Inhalte passen in die 805-px-Panel-Breite (Landkreis-Tabelle via
`table-layout:fixed` + feste Spaltenverhältnisse, Spannungs-Zeilen flex-wrap).
**V22 (06.09.):** Größenklassen-Basis-Umschalter „Einzelanlagen / Parks aggregiert"
(Döllen-Splittungs-Problem — Kritis-Sichtbarkeit 5 → 52 Objekte). Export liefert
`statistiken.json → groessen_cluster`, UI-Revision `iterations/V22_GroessenCluster.html`,
browser-verifiziert (12 Kombis, F5-Regression ok). **LIVE seit 06.09.** (Deploy mit V23+V24).
Details: `docs/ROADMAP.md` § V22.
**V23 (06.09., Arbeitspakete 1–8, Plan: `.hermes/plans/2026-09-06_V23-GeoEbene_30-Punkte-Plan.md`):**
1)–3) Geo-Suche (Landkreis/Gemeinde/Bundesland) unter Betreiber-Block; 4) Stats-Tab
„Landkreis" (9 Spalten: Assets P/W kombiniert + PV + Wind, NAP-Anzahl + NAP-MW;
analog Hersteller; NAP-Join über numerische LokationId: 377 LKs · 51.722 Assets ·
27.313 NAPs); 5) Größenklassen-Balken-Klick → Karte (gesamt-Modus: Wind-/PV-Abschnitte
einzeln klickbar; Cluster-Basis prüft Park-MW); 6)–7) Filter „Landkreis" + „Gemeinde"
(zwischen Bundesland und Art, kontextuell BL→LK→Gemeinde, kombinierbar); 8) Leistungs-
filter-Basis „Park (aggregiert)" als Default — zersplitterte Parks über Park-Gesamtleistung
(Döllen: 150+ = 1.603 Anlagen inkl. aller 13 Döllen-EH; Einzel-Modus: 3). Export: `pk`/
`pkmw` in einheiten.json + `landkreise`/`gemeinden` in statistiken.json (updatefähig,
läuft in jedem build.sh). Revision: iterations/V23_GeoEbene.html (42,3 MB). Browser-
verifiziert (Suche/Filter/Tab/Balken-Klick/Döllen-Kontrollfall + F5-Regression ok).
**LIVE seit 06.09.** (Deploy mit V22+V24).
CDN-Hinweis: max-age=600 → bis 10 min nach Deploy kann Cache den Altstand zeigen
(Cache-Buster-Query `?v…=1` umgeht das).

### V21 im Überblick (04.09., 6 Revisionspakete, alle browser-verifiziert)
- **V21.0 Betreiber-Tab:** Live-Suggest (ab 2 Zeichen, 250 ms Debounce, Gruppen 👥 /
  Portfolios 📁 zuerst, klickbar), Tabellen-Filter über Gruppen/Portfolios (kein
  substring-False-Positive mehr — 'rwe'-Bug), Gruppen-Klick = alle Anlagen der Gruppe.
- **V21.1–V21.3 Deeplink-Saga (User-Korrekturen):** ↗-Spalte → Name-Link → Korrrektur:
  KEIN North-Data im Betreiber-Tab; Klick auf Betreiber/Gruppe/Portfolio = Anlagen auf
  der Karte. Zahlformat „Summe MW"/„Ø MW" = exakt 1 Nachkommastelle (de-DE).
- **V21.4 Popup + Sortierung:** Popup-Datum TT.MM.JJJJ (`_parseMaStrDate` parst Tag,
  `dateFullFmt`), NAP im Popup klickbar → alle Anlagen am selben NAP (selectNAP,
  String-Vergleich-Fix; 219-Anlagen-Test), Spannungsebene bestätigt vorhanden.
  Sortier-Fix „Alle Anlagen anzeigen": Inbetriebnahme-Spalte numerisch (y*100+m)
  statt String (alter Bug: '201910' < '20192' lexikalisch).
- **V21.5 Asset-Name-Klick:** Tabelle „Alle Anlagen anzeigen", Spalte Name klickbar →
  Karte zoomt + Popup, alle gefilterten Marker bleiben (6.243-Marker-Test).
- **V21.6 Chart-Labels:** Zubau-Liniencharts (kumulativ + Raten) — senkrechte
  y-Wert-Labels stehen ÜBER dem Datenpunkt (negativ: darunter), kein Overlap mehr.

### Offene Punkte / nächste Themen (für nahtlose Weiterarbeit)
- **Stand 06.09. (V25 LIVE):** V25 = „Alle Anlagen anzeigen"-Bugfix (V23-Regression, Geo-Filter
  in showAllUnits ergänzt) + Landkreis-Tab mobil scrollbar (Header voll) + Such-Placeholder.
  Keine offenen Arbeitspakete — nächste Themen hier ergänzen.
- **Stand 06.09. (V24 LIVE):** V22+V23+V24 sind deployed (main `7172681`, gh-pages `1b9c85a`).
  V24 = Header-Einheiten im Landkreis-Tab (PV (MWp) / Wind (MW)) + Statistik-Panel ohne
  horizontales Scrollen (alle 9 Tabs verifiziert `scrollWidth ≤ clientWidth`). Keine
  offenen Arbeitspakete — nächste Themen hier ergänzen.
- **V23 (2026-09-06):** Geo-Ebene (Arbeitspakete 1–8) — Geo-Suche (BL/LK/Gemeinde
  unter Betreiber-Block), Geo-Filter (Landkreis zwischen BL/Art + Gemeinde; kontextuell),
  Stats-Tab „Landkreis" (9 Spalten + NAPs, analog Hersteller, Default MW desc),
  Größenklassen-Balken-Klick → Karte (gesamt-Modus: Klick-Position → Wind/PV),
  Leistungsfilter-Basis „Park (aggregiert)" als Default (`pk`/`pkmw`; Döllen 150+ =
  1.603 inkl. 13 EH vs. Einzel = 3). Plan: `.hermes/plans/2026-09-06_V23-GeoEbene_30-Punkte-Plan.md`,
  Revision: iterations/V23_GeoEbene.html. Status: implementiert + browser-verifiziert
  (inkl. F5-Regression), **LIVE seit 06.09. (mit V22+V24 gemeinsam).**
- **V22 (2026-09-06):** Größenklassen-Cluster-Basis „Parks aggregiert" —
  Splittungs-bereinigte Verteilung (Döllen-Problem). Export liefert `groessen_cluster`
  (wind/pv/gesamt), UI hat Basis-Umschalter im Größen-Tab. Revision:
  iterations/V22_GroessenCluster.html. Status: implementiert + browser-verifiziert,
  **LIVE seit 06.09.** (Deploy mit V23+V24).
- **Punkt 9 (alt):** HTML-Kernfeld-Auswahl — NUR mit User besprechen, nicht selbst decidieren.
- **NAP-Korrelation (User-Interesse):** Anlagen ↔ Netzanschlusspunkt via LokationId für
  künftige Karten-Features (Grundlage existiert: napByLid, 479 Multi-NAP-Lokationen).
- Revisionsdateien V21: iterations/V21_BetreiberTabRevision1–4, V21_PopupNAP_Sortierung,
  V21_AssetNameKlick, V21_ChartLabelsUeberPunkten (+ Kopien in ~/hermes_human-share/).
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
  **V21 Status: von User freigegeben (04.09. Abend) → auf main (d1096b4) + gh-pages
  (48da2ae) deployed, LIVE. Live-Verifikation: Index 433.686 Byte identisch lokal/live,
  V21.6-Marker + tbl-name + „Gruppe oder Portfolio filtern…" in Live-Datei, Placeholder
  im Live-JS bestätigt. (Hinweis: CDN max-age=600 — erste 10 min nach Deploy kann der
  alte Stand aus dem Cache kommen; Cache-Buster-Query umgeht das.)**
  Deploy-Skript-Vorlage: /tmp/deploy_ghpages_v20.sh (Worktree-Methode, CNAME bleibt;
  **jetzt fest im Repo: scripts/deploy_ghpages.sh** — pfadunabhängige Commit-Message,
  permanente Methode für alle künftigen Releases).
- **Stand V21 (04.09., wartet auf Freigabe):** Betreiber-Tab-Paket (3 Wünsche) —
  (1) North-Data-Deeplink-Spalte „↗" pro Zeile (neuer Tab, Zeilen-Klick bleibt Karte).
  (2) Filter findet jetzt auch Betreibergruppen/Portfolios (Gruppen-Zeilen oben).
  (3) Live-Suggest unter dem Filter (ab 2 Zeichen, 250 ms, Gruppen zuerst, Enter/Escape
  schließt) + `selectBetreiberGruppe()` (alle Anlagen aller Gesellschaften → fitBounds).
  Zwei Erstwurf-Bugs browser-gefangen und gefixt (Substring-False-Positive, Cache-Timing).
  Revision: iterations/V21_BetreiberTabRevision1.html.
  **V21.1 (04.09., User-Korrektur):** separate ↗-Spalte komplett entfernt; der
  **Betreiber-Name selbst** (Einzel + Gruppen/Portfolios) ist jetzt der North-Data-Deeplink
  in der Spalte „Betreiber". Tabelle wieder 4 Spalten. Revision:
  iterations/V21_BetreiberTabRevision2.html.
  **V21.2 (04.09., User-Feinschliff):** Deeplink pro Zeile verifiziert (50/50 inkl. Gruppen);
  „Summe MW" und „Ø MW" jetzt mit genau 1 Nachkommastelle. Revision:
  iterations/V21_BetreiberTabRevision3.html.
  **V21.3 (04.09., User-Korrektur):** KEIN North-Data-Link im Betreiber-Tab mehr —
  Klick auf Betreiber/Portfolio/Gruppe zeigt die Anlagen auf der Karte. Revision:
  iterations/V21_BetreiberTabRevision4.html.
  **V21.4 (04.09.):** Popup-Datum TT.MM.JJJJ (Tag wird jetzt mitgeparst), NAP im Popup
  klickbar → alle Anlagen am selben NAP auf der Karte (219-Anlagen-Test ok), Sortier-Fix
  Inbetriebnahme-Spalte (numerisch statt String — Oktober-sortierte-vor-Februar-Bug).
  Revision: iterations/V21_PopupNAP_Sortierung.html.
  **V21.5 (04.09.):** Asset-Name in „Alle Anlagen anzeigen"-Tabelle klickbar → Karte +
  Popup, alle gefilterten Marker bleiben (6.243-Marker-Test ok). Revision:
  iterations/V21_AssetNameKlick.html.
  **V21.6 (04.09.):** Chart-Labels in den 2 Zubau-Liniencharts (kumulativ + Raten) stehen
  jetzt ÜBER den Datenpunkten statt auf ihnen (negativ: darunter); senkrechte Ausrichtung
  bleibt. Revision: iterations/V21_ChartLabelsUeberPunkten.html.
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
| Export | `scripts/export_app.py` | `dist/assets/*.json` (nur georeferenziert) + Statistik (`groessenklassen` je wind/pv/gesamt **+ V22: `groessen_cluster`**) |
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
  für das gemeinsame Diagramm (zusätzlich zu `wind`/`pv`) — und **seit V22** `groessen_cluster`
  (wind/pv/gesamt) mit der Park-Cluster-Verteilung (Schlüssel: Energieträger + Betreiber + Parkname;
  Splittungen wie Solarpark Döllen = 13 EH → 1 Park 154,8 MW; Details `docs/ROADMAP.md` § V22).
- **Kritis-Klassen:** Im Diagramm 🔴 rot markiert (`bar-fill.kritis`), mit `KRITIS`-Badge im Label +
  Tooltip-Hinweis. Leere Kritis-Klassen bei Wind (104+ real leer) bleiben sichtbar.
- **Gesamt-Diagramm („Wind + PV"):** zeigt pro Klasse **zwei Balken** (Wind blau, PV orange) nebeneinander
  mit getrennten Werten im Tooltip (Wind/PV Anlagen + Leistung), damit beide Technologien sichtbar sind.
- **Größen-Filter in der Toolbar:** HTML `<select id="filter-gr">` mit den 11 Größen-Klassen als
  `value="von,bis"` (z. B. `"0.5,1"`, `"104,150"`, `"150,1e9"`). `applyFilters()` parst
  `Number.parseFloat`, filtert `u.mw >= von && u.mw < bis`. Der Badge (`#art-count`) wird aktiviert
  bei `art || bl || gr`.
- **Rechtliches:** Quellenvermerk DL-De-BY-2.0 + Impressum (§5 DDG) fest in der App (Modal).
- **`data/`-Ist-Stand:** `data/raw/ + data/mastr.db` sind gitignored und **im Working-Tree
  vorhanden** (Stand 04.09.2026, Backup `~/backups/mastr.db.2026-09-04.bak`, 419 MB);
  `fetch_mastr.py` legt sie bei einem vollständigen Update automatisch neu an.
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
- [ ] **Performance:** Single-File ist auf ~38,7 MB gewachsen — optional hostbare Version nutzen,
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

## V30 Final (08.09.2026, Abend) — Fixrunde abgeschlossen

Alle 8 Audit-Findings abgearbeitet:
- F-01 Overlay-Dual-State: showAllUnits liest filter-se (inkl. __ohne__), Leistungsfilter auf Park-Basis — 10.751 bei HS+Overlay
- F-02 Klick-Quellen-Status: BY DESIGN (alle Status sichtbar), geschlossen
- F-03 Snapshot-Dedup: save_snapshot mit Datum+Kennzahlen-Dedup; historie.json 8→3 Einträge; DB bereinigt
- F-04 Abgrenzung strikt (Variante B): Fetch ge~500, Export-Sicherheitsnetz; Basis 31.011 Wind · 22.402 PV = 53.413; Karte 65.663
- F-05 Overlay-Datum: dateFullFmt statt ISO — „31.01.2019 / 29.01.2019"
- F-06 Historie-Hinweis: „sonntags 18:00" statt „1. & 15. des Monats"
- F-07 Freeze: Beobachtungspunkt (nicht reprodizierbar, Kern 11 ms) — docs/F07_ABSCHLUSS_2026-09-08.md
- F-08 Doku: 9→10 Tabs (statistik.md, architektur.md, README.md)

Verifikation (finaler Build, ?v30final=1): Infobar 31011/22402 ✓, F-01 53.413 ✓,
F-05 DE-Datum ✓, F-06 Hinweistext ✓, 10 Tabs ✓, 0 JS-Errors ✓.
Geänderte Dateien: src/index.html, scripts/{fetch_mastr,fetch_v2,export_app,snapshot}.py,
README.md, docs/{PROJEKTSTAND,statistik,architektur}.md + BUGS_ZU_ERLEDIGEN_2026-09-08.md (neu).
Iterations: V30_F01_DualStateFix, V30_F05_DatumOverlay, V30_F06_HistorieHinweistext,
V30_F04_AbgrenzungStrikt, V30_F03_SnapshotDedup, V30_FINAL_Fixrunde (jeweils + human-share).

### V30 Doku-Sync (08.09. Abend)

Bestands-Doku gegen den Build-Status geprüft und angepasst:
- `README.md`: Daten-Tabelle auf V30-IST (65.663 / 53.413; Wind 42.006, PV 23.657)
- `docs/datenmodell.md`: Kennzahlen-Tabelle + Infobar-Absatz + Legacy-V1-Hinweis aktualisiert
- `docs/statistik.md`: Kopf V30, Hersteller-Basis 30.847 (61 Hersteller), LK-Basis 377 · 51.634 Assets · 125.552,1 MW · 27.338 NAPs, Wind max 15 MW (300-MW-Falscheintrag Südwind korrekt per V27b-Physik-Check als 0,3 MW)
- `docs/update.md`: V30-Snapshot-Dedup ergänzt; Cron-Beispiel auf sonntags 18:00
- `docs/architektur.md`: Fetch-Filter gt~499.9 → ge~500
- `scripts/fetch_mastr.py`: Header-Doku ge~500
- **F-04-Nachzieh-Fix:** Legacy-V1-Tabelle `einheiten` gesynced (11 Grenzfälle raus, 5 fehlende Einheiten aus RAW nachgefügt, SEE944775195571 auf 0,3 MW korrigiert) → `statistiken.json` jetzt konsistent: gesamt 53.413, Wind 31.011, PV 22.402, Wind max 15 MW, LK 51.634 Assets
- Verifikation: Browser ?v30doc=1 — Infobar 31011/22402 ✓, LK-Zähler „377 Landkreise · 51.634 Assets / 125.552,1 MW · 27.338 NAPs" ✓, 0 JS-Errors ✓
- Rebuild: iterations/V30_FINAL_Fixrunde.html + human-share aktualisiert

## V32 (08.09.2026, spät) — Bugfixrunde (50-Punkte-Plan): 5 Bugs + Doku

### WP1: NAP-Ranking im Singlefile + NAP-Klick → Karte
- **Bug:** `bundle_singlefile.py` bettete `nap_index.json` ein, aber NICHT `nap_ranking.json`
  → Singlefile: "NAP-Ranking nicht geladen — bitte Seite neu laden." (Multi-File-Build war ok).
- **Fix 1:** bundle_singlefile.py: `nap_ranking.json` als 6. Einbettung (`window.__PVWIND_NAP_RANKING__`).
- **Fix 2:** `focusNAPOnMap()`: Klick auf NAP-Zeile im Statistik-Tab "NAP" rendert jetzt
  **nur die Anlagen dieses NAPs** auf der Karte (selectHersteller-Muster: renderMarkers(grp.units)
  + fitBounds + Suchfeld-Label "NAP: <name> (N Anlagen)") + NAP-Panel öffnet. Fallback ohne
  nap_index-Gruppe: bisheriges Circle-Overlay.

### WP2: Landkreis-Tabelle horizontal scrollbar
- `#landkreis-scroll`: `overflow-x:auto` → `overflow-x:scroll` (Balken immer sichtbar),
  Name-Spalte sticky (`position:sticky; left:0`), damit sie beim Scrollen lesbar bleibt.

### WP3: Snapshot-7/8-MW-Korrektur (kW/MW-Verwechslung im Historie-Delta)
- **Bug:** Snapshots 7 (29.08.) + 8 (01.09.) enthielten die VOR dem V27b-Physik-Check
  importierten Wind-Leistungen: 120 Wind-Einträge mit kW-Falschangabe (z. B. E-18/20
  = 80 kW als "80 MW"), zusammen 8.545 MW zu viel pro Snapshot. Das Delta 01.09→06.09
  zeigte deshalb in "Entfernt: Wind" Werte wie 80 MW für Kleinstanlagen.
- **Fix:** `scripts/fix_snapshot_mw.py` (Migration): Wind-MW in snapshot_einheiten der
  Snapshots 7+8 mit to_mw-Heuristik neu berechnet (240 Einträge, Δ −17.072,8 MW),
  snapshots.wind_mw/gesamt_mw + bundeslaender_json neu abgeleitet, Delta via
  compute_delta neu berechnet, historie.json neu exportiert.
- **Ist jetzt:** Delta 01.09→06.09: wind_diff_mw **+125,54 MW** (vorher −8.410,85),
  removed wind ohne einzigen >15-MW-Ausreißer.
- **Neu:** `docs/wind_typen_leistungen.md` — Referenzliste 3.922 Wind-Typen
  (Hersteller; Typ; Anlagenleistung in MW; Anzahl) für künftige Korrekturen.

### WP4: Betroffenheit "Anzeigen" — NEU-Asset war unsichtbar
- **Bug:** `clusterGroup.disableClustering()` wurde aufgerufen, existiert aber nicht
  (Leaflet.markercluster hat keine solche API) → im Anzeigen-Modus blieb Clustering
  aktiv; Bestand+NEU am selben NAP verschmolzen in einem Cluster-Bubble.
- **Fix:** renderMarkers: im BFF-Anzeigen-Modus Rendering in einfachen `L.layerGroup`
  (clustering-frei) statt clusterGroup; Rückkehr zum Normal-Modus reaktiviert clusterGroup.
  Marker-Bau in `_buildUnitMarker(u)` + Lazy-Popup in `_bindLazyPopup(m, u)` extrahiert.

### WP5: Netzbetreiber-Filter reagierte nicht
- **Bug:** `filter-nb` hatte keinen `change`-Listener (V31-Nachlässigkeit; der
  Verifikationstest dispatchete programmatisch, daher unentdeckt).
- **Fix:** `addEventListener('change', applyFilters)` ergänzt.

### Build/Verifikation
- node --check über alle Inline-Script-Blöcke: OK.
- Browser-Verifikation: siehe Chat-Report vom 08.09.

## V31 (08.09.2026, Abend) — Netzbetreiber-Filter + Typ-Tab

### WP1: Netzbetreiber-Filter (Hauptseite)
- Neuer Filter `filter-nb` zwischen **Gemeinde** und **Art** (V31-Position).
- Optionen: 698 Netzbetreiber (Name ohne SNB-Klammer-Suffix, SNB-Nr im title-Attribut) + **„Keine Angabe"** (`__ohne__`) für 3.401 Anlagen ohne NB-Angabe (alle Status 31/38 — erscheinen nur mit aktivierten Status-Filtern).
- Verkabelung: `populateFilterNb()` (Daten-Load-Init), `applyFilters()` + `showAllUnits()` (Overlay == Karte, F-01-Muster), `resetFilters()` (IDs-Liste).
- NB-Match: exakter Vollstring ODER Name vor Klammer-Suffix; 0 NB-Namen mit mehreren SNB (verifiziert).
- Verifikation: Avacon = 5.184 Anlagen; Avacon + LK Celle = 35; „Keine Angabe" (alle Status) = 3.401 ✓; Reset räumt nb mit auf ✓.

### WP2: Statistik-Tab „Typ" (nach Hersteller)
- Neuer Tab `data-tab="typ"` mit Tabelle: **Hersteller; Typ; Leistung (MW); Anzahl; Anteil; Summe MW** — strikt 6 Spalten (User-Entscheid).
- Basis: alle Wind-Einheiten im Export (**42.006**, alle Status — Karten-Datenbestand). 4.950 (Hersteller, Typ)-Kombinationen; „Keine Angabe" für fehlende herst/typ.
- Default-Sortierung: **Leistung absteigend** (User-Anforderung); alle Header sortierbar; Top-N (10/50/100/Alle) + Textfilter (Typ oder Hersteller).
- Klick auf Zeile → `selectTyp(herst, typ)`: renderMarkers + fitBounds + Suchfeld-Label „Typ: … — … (N Anlagen)" + Stats-Panel schließt.
- Verifikation: Default erste Zeile Vestas V236-15MW (15 MW, 51 Anlagen); Σ Anzahl über „Alle" = 42.006 ✓; E-70 E4/ENERCON = 931 Anlagen = Klick-Marker ✓; 0 JS-Errors ✓.

### Files
- `src/index.html` (+HTML-Select/Section, +CSS #typ-table, +populateFilterNb/renderTyp/selectTyp, _statsState.typTop/typFilter/typSortKey/typSortDir)
- `iterations/V31_NetzbetreiberTyp.html` + human-share-Kopie (42.425.978 Bytes)
- Plan: `.hermes/plans/2026-09-08_V31_NetzbetreiberTyp_30-Punkte-Plan.md`

## V32.1 (09.09.2026) — Hotfix Singlefile-TDZ

- **Bug:** Singlefile zeigte keine Anlagen beim Öffnen (erst nach Filter-Toggle); Statistik-Button tot.
- **Root-Cause:** TDZ — `init()` läuft im Singlefile synchron (eingebettete Daten); `renderMarkers`
  las `_bffShowActive` vor dessen Deklaration → ReferenceError → catch → Abbruch vor
  `renderMarkers`/`initStats`. Multi-File nicht betroffen (await maskiert).
- **Fix:** BFF-State-Deklarationen vor `init()` verschoben. Vorgänger (08.09., nach User-Meldung):
  Topbar z-index 1700 + Statistik-Button-Toggle.
- **Verifikation (Singlefile, Browser):** Marker sofort (46 Cluster), 0 JS-Fehler, Stats-Panel
  öffnet/schließt via Button, NAP-Klick „SP WINI" → 8 Marker clustering-frei, NB-Filter Avacon
  5.184/53.413, NAP-Ranking 27.130, Historie-Δ +251 MW ok.

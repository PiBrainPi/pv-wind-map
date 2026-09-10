# V35 — 50-Punkte-Plan: Betreiber-Diagramme · Filter-Reset komplett · Betroffenheits-Legende

> **Datum:** 2026-09-10 · **Basis:** V34 (lokal, ungepusht) · **Repo:** ~/Projects/pv-wind-map
> **User-Freigabe:** Umsetzung ok, **KEIN Push nach GitHub** ohne explizite Freigabe.
> **EEG-Definition (User bestätigt):** „Mit/Ohne EEG-Registrierung" via `EegInbetriebnahmeDatum`-Existenz.

## A. Recherche (Punkte 1–12)
1. [x] Betreiber-Tab Struktur gelesen (`renderBetreiber`, L4135; Gruppen/Einzel-Logik, Suggest, `_bffGrpCache`).
2. [x] Datenmodell `einheiten.json` verifiziert: 65.663 Units; Felder t/art/mw/reg/inb/ab/bs — **kein EEG-Feld im Export**.
3. [x] MaStR-Rohdaten (118 Felder, `einheiten_raw.raw_json`) geprüft: `EegInbetriebnahmeDatum` existiert → PV 95,1 % / Wind 81,2 % mit EEG-Registrierung.
4. [x] Export-Pfad verifiziert: `SELECT_RAW_EXTRA` (Spalten 0–33) + `build_units` (Spaltenindizes) — Erweiterung um Spalte 33 `eeg` identifiziert.
5. [x] `resetFilters()` gelesen (L3142): setzt 12 Filter-IDs, Basis, Status, Suche, Badge — **rückt NICHT den BFF-/NAP-Fokus-Zustand auf**.
6. [x] BFF-State verifiziert: `_bffShowActive/_bffShowSet` (Plain-Layer), `_bffRadiusLayer` (Ringe), `_bffRemovedLayer` (rote Marker), `_bffResetAnalysis()` (L6141).
7. [x] NAP-Fokus: `_napFocusActive` + `window.__napFocusCircle` (blauer Kreis) — ebenfalls vom Reset betroffen.
8. [x] Karten-Init-View: `setView([51.5, 10.0], 6)` (L2328) — Ziel-Zustand für „Ursprungs-Ladezustand".
9. [x] Chart-Bausteine vorhanden: `drawStackedBar`/`drawSingleBar` (Zubau), Donut-Muster (Hersteller-Pie) — Wiederverwendung möglich.
10. [x] Erklärsatz „ℹ️ Wie funktioniert…?" lokalisiert (L2030–2039 + zweiter Details-Block L2071) — Legende fehlt dort.
11. [x] Bundle-Pfad verifiziert: `bundle_singlefile.py` bettet einheiten.json ein → EEG-Feld landet automatisch im Singlefile.
12. [x] Verifikationsregel V32.1: Änderungen MÜSSEN im Singlefile browser-verifiziert werden.

## B. Planung (Punkte 13–18)
13. [ ] **AP1 Export:** Spalte 33 `eeg` (0/1) in `SELECT_RAW_EXTRA` + `build_units` (Spaltenindizes) — Erweiterung um Spalte 33 `eeg` identifiziert.
5. [x] `resetFilters()` gelesen (L3142): setzt 12 Filter-IDs, Basis, Status, Suche, Badge — **rückt NICHT den BFF-/NAP-Fokus-Zustand auf**.
6. [x] BFF-State verifiziert: `_bffShowActive/_bffShowSet` (Plain-Layer), `_bffRadiusLayer` (Ringe), `_bffRemovedLayer` (rote Marker), `_bffResetAnalysis()` (L6141).
7. [x] NAP-Fokus: `_napFocusActive` + `window.__napFocusCircle` (blauer Kreis, L5108) — ebenfalls vom Reset betroffen.
8. [x] Karten-Init-View: `setView([51.5, 10.0], 6)` (L2328) — Ziel-Zustand für „Ursprungs-Ladezustand".
9. [x] Chart-Bausteine vorhanden: `drawStackedBar`/`drawSingleBar` (Zubau), Donut-Muster (Hersteller-Pie L4472) — Wiederverwendung möglich.
10. [x] Erklärsatz „ℹ️ Wie funktioniert…?" lokalisiert (L2030–2039 + zweiter Details-Block L2071) — Legende fehlt dort.
11. [x] `bundle_singlefile.py` bettet `einheiten.json` ein → EEG-Feld landet automatisch im Singlefile.
12. [x] Verifikationsregel V32.1: Änderungen MÜSSEN im Singlefile browser-verifiziert werden.

## B. Planung (Punkte 13–18)
13. [ ] **AP1 Export:** Spalte 33 `eeg` (0/1) in `SELECT_RAW_EXTRA` + `build_units` (neue Zuweisung bei `len(r) > 33`). Nur In-Betrieb- + alle Status.
14. [ ] **AP1 UI:** Button „📈 Diagramme" unter dem Betreiber-Suchfeld (sichtbar nur mit Suchtext); klappt Chart-Block unter der Tabelle auf. Scope = Einheiten des Suchtreffers (Einzelbetreiber ODER alle Ges. der Gruppe/Portfolios — gleiche Logik wie Suggest/Zeilen-Klick).
15. [ ] **AP1 Charts:** (a) Gestapeltes Balkendiagramm Zubau je Jahr (Inbetriebnahme, Wind blau/PV orange, Toggle Anlagen/Leistung MW); (b) Donut Technologie %; (c) Donut EEG mit/ohne je Wind;PV + Erklärsatz zur Definition. Canvas, kein Bibliotheks-Import (konsistent zur App).
16. [ ] **AP2 Reset:** `resetFilters()` erweitern — `_bffResetAnalysis()` + `_napFocusActive=false` + `window.__napFocusCircle` entfernen + NAP-Panel schließen + Karte `setView([51.5,10.0], 6)` + `applyFilters()` (bestehend). Reihenfolge: erst Exit-Modi, dann Filter.
17. [ ] **AP3 Legende:** Im „ℹ️ Wie funktioniert…?"-Details Block „Karten-Symbole & Farben": Marker-Styles je Status (F5), Ringfarben (grün=Neubau/rot=nur Abmeldung, gestrichelt), rote entfernte-Marker, NAP-⚡-Symbole.
18. [ ] **Build-Plan:** `python3 scripts/export_app.py` (regeneriert assets inkl. eeg, kopiert src→dist) + `python3 scripts/bundle_singlefile.py`. Kein fetch/import nötig (DB-Stand 06.09. unverändert). Iteration `iterations/V35_BetreiberCharts_Reset_Legende.html` + human-share-Kopie.

## C. Umsetzung (Punkte 19–38)
19. [ ] export_app.py: SELECT_RAW_EXTRA um Spalte 33 ergänzen (`json_extract(raw_json,'$.EegInbetriebnahmeDatum') IS NOT NULL`).
20. [ ] export_app.py: build_units — Spalten-Kommentar erweitern + `u["eeg"]=1` bei Spalte 33.
21. [ ] export_app.py ausführen → prüfen: eeg-Feld in einheiten.json, Infobar-Zahlen unverändert (31011/22402), 0 neue Felder-Fehler.
22. [ ] src/index.html: AP1 — Button `#betreiber-charts-btn` in stats-controls (nur mit Suchtext sichtbar).
23. [ ] src/index.html: `_betreiberScopeUnits(filterText)` — Unit-Scope (Gruppe via `_bffGrpCache` brand/kern-Sets + Einzel via norm-Match, dedupe).
24. [ ] src/index.html: `renderBetreiberDiagramme(units)` — 3 Charts (Canvas) + Summary-Zeile + Erklärnote EEG.
25. [ ] src/index.html: Toggle Anlagen/MW + Chart-Block schließen (Button wechselt Label ▲/▼).
26. [ ] src/index.html: AP2 — resetFilters erweitern (Reihenfolge: Exit BFF/NAP → Filter reset → View reset → applyFilters).
27. [ ] src/index.html: AP3 — Legenden-Block in beide Details-Erklärungen einfügen (Inline-Swatch-Divs wie Marker-HTML).
28. [ ] Syntax-Check: alle Inline-Script-Blöcke via node --check.
29. [ ] dist/index.html via export_app.py aktualisieren.
30. [ ] bundle_singlefile.py ausführen → dist/index_singlefile.html.
31. [ ] Singlefile browser öffnen (file://) — Smoke: Marker laden, 0 JS-Errors.
32. [ ] AP1-Verifikation: Suchtext (z.B. „ENERPARC") → Diagramme → Zahlen plausibel (Zubau-Summe == Anlagenzahl), Donut % == 100.
33. [ ] AP2-Verifikation: BFF-Analyse + „Anzeigen" → Filter löschen → Marker/Cluster zurück, Ringe/Marks weg, View [51.5,10] z6.
34. [ ] AP3-Verifikation: Erklärung zeigt Legende korrekt (Status-Marker, Ringe, entfernte Assets).
35. [ ] Regression: applyFilters Badge, Betreiber-Zeilen-Klick, Suggest, NAP-Tab, Zubau-Tab (F5-Regression).
36. [ ] Multi-File-Build (dist/index.html via http) ebenfalls checken (TDZ-Regel).
37. [ ] Revision speichern: iterations/V35_BetreiberCharts_Reset_Legende.html + ~/hermes_human-share/.
38. [ ] Doku as-built: docs/PROJEKTSTAND.md V35-Abschnitt, BUGS-Liste unverändert, kein Commit/Push.

## D. Überprüfung (Punkte 39–50)
39. [ ] Browser-Konsole: 0 Errors nach allen Aktionen.
40. [ ] Infobar unverändert: 31.011 Wind · 22.402 PV = 53.413 (Kern), Karte 65.663.
41. [ ] EEG-Donut Plausibilität: PV ≈95 % / Wind ≈81 % mit EEG (vs. Rohdaten-Scan 22.507/23.679 PV, 35.283/43.457 Wind).
42. [ ] AP1: Diagramm-Zahlen == Tabelle „Anzahl"/„Summe MW" des gewählten Treffers.
43. [ ] AP1: Diagramm reagiert auf Suche-Änderung (neuer Suchtext → Charts aktualisieren).
44. [ ] AP2: NAP-Fokus-Klick → Filter löschen → blauer NAP-Kreis weg, Karte default.
45. [ ] AP2: Doppel-Klick „Filter löschen" idempotent (keine Fehler, kein Layer-Leak).
46. [ ] AP2: mobile Breite (375 px) — Button/Charts im Panel brauchbar.
47. [ ] AP3: zweiter Details-Block (Optionen) ebenfalls aktualisiert.
48. [ ] Änderungsliste mit Quellen an User (deutsch, kurz).
49. [ ] Revision klickbar per MEDIA: im Chat liefern (kein HTML-Rohcode).
50. [ ] Abzeichnung: User-Freigabe → DANACH erst Push/Deploy (Regel 4).

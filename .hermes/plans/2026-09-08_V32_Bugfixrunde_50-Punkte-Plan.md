# V32 — 50-Punkte-Plan: 6 Arbeitspakete (Bugfixes + Doku-Finalisierung)

**Datum:** 08.09.2026 (Abend) · **Basis:** V31 (lokal, unverändert zu GitHub V29.1 + V30/V31-Änderungen im Working-Tree)
**HARTE REGEL:** Kein Push/Deploy/Settings-Änderung bei GitHub ohne explizite Freigabe. Revision lokal + HTML im Chat.

**Recherche-Ergebnisse (Phase A, abgeschlossen):**
- **WP1 (NAP-Ranking leer):** `bundle_singlefile.py` bettet `nap_index.json` (`__PVWIND_NAP__`) ein, aber NICHT `nap_ranking.json` (`__PVWIND_NAP_RANKING__`). Im Singlefile schlägt `fetch('assets/nap_ranking.json')` fehl (kein assets/-Ordner) → Hinweistext. Im Multi-File-Build (dist/index.html) funktioniert es. Klick-Logik `focusNAPOnMap()` existiert (öffnet NAP-Panel), blendet aber NICHT andere Anlagen aus (User will Analogie selectHersteller: nur NAP-Anlagen auf Karte).
- **WP2 (LK-Tabelle horizontal):** `#landkreis-scroll` hat bereits `overflow-x:auto`, `#landkreis-table` `width:max-content;min-width:900px`. CSS korrekt — Ursache der Nicht-Scrollbarkeit im Browser verifizieren (Vermutung: funktioniert, aber User sieht keinen sichtbaren Balken → Scrollbar-Styling/Position prüfen; ggf. `sticky` first column + sichtbarerer Balken).
- **WP3 (kW/MW im Historie-Delta):** Snapshots 7 (29.08.) + 8 (01.09.) enthalten UNKORRIGIERTE Wind-MW (vor V27b-Physik-Check): 120 Wind-Einträge >15 MW (= kW-Falschangaben, 8.545 MW zu viel). Snapshot 10 (06.09.) korrekt (81.754 MW). Delta 01.09→06.09 rechnet mit alten Werten → „Entfernt"-Liste/Bundesländer-Δ falsch. removed_assets-Elemente haben typ/rd/herst → serverseitige Korrektur via to_mw-Heuristik möglich. Frontend hat kein to_mw.
- **WP4 (Betroffenheit):** Alle 52 added_assets des letzten Deltas sind in allUnits, bs=35 (Aktiviert), mit Koordinaten — Daten ok. `_bffShowSet`-Filter bypassed andere Filter (V19-Fix vorhanden). ABER: `clusterGroup.disableClustering()` wird aufgerufen, existiert aber NICHT als Implementierung → Clustering bleibt im Anzeigen-Modus aktiv → Bestand+NEU am selben NAP verschmelzen in einem Cluster-Bubble (NEU-Asset unsichtbar). Das ist der Bug.
- **WP5 (NB-Filter tot):** `filter-nb` hat KEINEN change-Listener (alle anderen Filter haben `addEventListener('change', applyFilters)`). Mein V31-Browser-Test dispatchete programmatisch — daher grün. Echte User-Auswahl löst nichts aus. Einzeilen-Fix.
- **WP6:** Doku-Dateien: PROJEKTSTAND, README, architektur, statistik, datenmodell, update, hosting, DEPLOYMENT, fehlerbehebung, ROADMAP, F07-Abschluss. Wind-Typ-Referenzliste existiert noch nicht (WP3 erzeugt sie).

---

## PHASE B — PLANUNG

1. **WP1-Datenpfad:** bundle_singlefile.py: nap_ranking.json als 5. Einbettung (`window.__PVWIND_NAP_RANKING__`) — 27.130 Einträge ≈ 5 MB, akzeptabel (einheiten.json ist 42 MB). Guard in fetch-Zweig bleibt (Fallback bei fehlender Datei).
2. **WP1-Klick-Verhalten neu:** `focusNAPOnMap(r)` umbauen: nach lid-Auflösung via nap_index → `_buildNapGroups().get(lid)` → `renderMarkers(grp.units)` (NUR diese Anlagen) + fitBounds + Suchfeld-Label „NAP: <name> (N Anlagen)" + Stats schließen + NAP-Panel öffnen. Fallback (keine Gruppe): Circle-Overlay wie bisher.
3. **WP2-Lösung:** Scroll-Container prüfen; falls CSS ok: `#landkreis-scroll { overflow-x:auto; }` mit `min-height` für scrollbar Gutter + Scrollbalken sichtbarer stylen; Alternative: erste Spalte `position:sticky; left:0`. Im Browser verifizieren.
4. **WP3-Datenkorrektur (serverseitig, sauberste Lösung):** Migrations-Skript `scripts/fix_snapshot_mw.py`: Für Snapshots 7+8 alle Wind-Einheiten mit bruttoleistung_mw>15 → to_mw-Heuristik (typ+rd-basiert, aus import_mastr importiert) neu rechnen; snapshot_einheiten + wind_mw + bundeslaender_json updaten; Dedup-Auswirkung beachten. Danach Delta 01.09→06.09 neu berechnen + historie.json neu exportieren.
5. **WP3-Referenzliste:** `docs/wind_typen_leistungen.md` aus einheiten.json generieren (Hersteller; Typ; Anlagenleistung in MW — Modus/Pro Typ: konsolidierte MW je Typ aus Daten; wenn mehrere MW je Typ: häufigster Wert + Range). Zusätzlich in App? Nein — Daten kommen künftig korrekt aus Pipeline.
6. **WP3-App-Anzeige:** Nach DB-Korrektur zeigt das Frontend die korrigierten Werte automatisch (Delta kommt aus historie.json). Kein Frontend-Code nötig — außer: Historie-Kennzahlen (wind_mw je Snapshot) korrigiert.
7. **WP4-Fix:** `disableClustering()`/`enableClustering()` am clusterGroup implementieren: L.MarkerClusterGroup hat `disableClustering()` nativ (Leaflet.markercluster 1.5: ja, via `disableClustering()`) — prüfen; falls nicht: Option `disableClusteringAtZoom` umgehen → im Anzeigen-Modus Marker direkt in L.layerGroup statt clusterGroup rendern (renderMarkers-Schalter).
8. **WP5-Fix:** `document.getElementById('filter-nb').addEventListener('change', applyFilters);` nach filter-g-Zeile.
9. **WP6-Umfang:** PROJEKTSTAND V32-Block; README (Bugfixes); statistik.md (NAP-Klick-Verhalten); update.md (Snapshot-MW-Korrektur-Migration); datenmodell.md (wind_typen_leistungen.md referenzieren); fehlerbehebung.md (4 Bugs + Fixes); ROADMAP (Status).
10. **Build/Verify:** Standard-Kette, Browser-Tests je WP (Rezept: Consent → Warte-Loop → Cache-Busting ?v32=K).

## PHASE C — UMSETZUNG

### WP1 (Punkte 11–16)
11. `scripts/bundle_singlefile.py`: nap_ranking-Einbettung ergänzen (nach nap_index-Block).
12. `src/index.html` focusNAPOnMap(): Nur-NAP-Anlagen-Render (renderMarkers + fitBounds + Label).
13. NAP-Panel öffnen NACH Karten-Filter (Panel-Inhalt zeigt dieselben Anlagen).
14. Fallback ohne Gruppe: bisheriges Circle-Verhalten (kein Karten-Filter).
15. Guard-Test: ohne nap_ranking → Hinweis; mit → Tabelle.
16. Singlefile-Größe/Datenpfad verifizieren.

### WP2 (Punkte 17–19)
17. Scroll-Verhalten im Live-DOM diagnostizieren (getBoundingClientRect, computed styles).
18. CSS-Fix umsetzen (sichtbarer horizontaler Balken + ggf. sticky Name-Spalte).
19. Alle anderen Tab-Tabellen auf gleiches Muster prüfen (Typ/Betreiber/Hersteller — Konsistenz).

### WP3 (Punkte 20–28)
20. `scripts/fix_snapshot_mw.py` schreiben: to_mw-Import + Snapshot-7/8-Migration (Wind>15 MW → Heuristik).
21. Migration dry-run:.report (120 Einträge, alte/neue MW, Differenz).
22. Migration ausführen + DB verifizieren (Snapshot 7/8 ≈ 81,7k MW Wind).
23. bundeslaender_json beider Snapshots korrekt neu ableiten.
24. Delta 01.09→06.09 neu berechnen (compute_delta via snapshot.py importieren) + Snapshot-Delta-Konsistenz (wind_diff_mw ≈ -8.411 → neu ~+13 MW? verifizieren).
25. `python3 scripts/export_app.py` → neues historie.json.
26. `docs/wind_typen_leistungen.md` generieren (Header: Hersteller;Typ;Anlagenleistung in MW).
27. App-Verifikation: Historie-Tab → „Entfernt: Wind" zeigt korrigierte MW (E-18/20 = 0,08 MW statt 80).
28. Bundesländer-Veränderung zeigt korrigierte Δ-MW.

### WP4 (Punkte 29–33)
29. Leaflet.markercluster-API prüfen (disableClustering verfügbar?).
30. Fix: Anzeigen-Modus rendert ohne Clustering (layerGroup-Switch in renderMarkers ODER natives disableClustering).
31. Regression: Normal-Modus clustert weiter (V31-Basis).
32. Browser-Test: Betroffenheits-Analyse mit echtem NAP-Fall → Bestand+NEU beide sichtbar.
33. Ringe + fitBounds-Verhalten unverändert.

### WP5 (Punkte 34–35)
34. change-Listener für filter-nb ergänzen.
35. Browser-Test: echte change-Events (select-Auswahl) → Karte filtert; Overlay gleich; Reset ok.

### WP6 (Punkte 36–43)
36. PROJEKTSTAND.md V32-Block (alle 5 Bugfixes + Migration).
37. README.md: Feature-Beschreibungen anpassen (NAP-Klick-Verhalten, Snapshot-Korrektur).
38. statistik.md: NAP-Tab-Verhalten dokumentieren.
39. update.md: Migrations-Skript + Snapshot-7/8-Korrektur dokumentieren.
40. datenmodell.md: Referenz auf wind_typen_leistungen.md.
41. fehlerbehebung.md: 4 neue Bugs (F-NB-Listener, F-NAPRanking-Singlefile, F-SnapshotMW, F-BFF-Cluster) mit Ursache+Fix.
42. ROADMAP.md: V32-Status.
43. .hermes/plans V32-Plan ablegen (dieses Dokument).

## PHASE D — ÜBERPRÜFUNG (Punkte 44–50)

44. Build: cp src → dist + bundle_singlefile.py; Größen-Check.
45. Browser-Verifikation WP1: NAP-Tab lädt Tabelle (kein Fehlerhinweis); Klick auf NAP-Zeile → Karte zeigt NUR NAP-Anlagen; Panel öffnet; andere Filteranwendung hebt Kartenfilter auf (Reset).
46. Browser-Verifikation WP2: LK-Tabelle horizontal scrollbar; letzte Spalte lesbar.
47. Browser-Verifikation WP3: Historie → Entfernt-Wind MW-Werte plausibel (<3 MW); Δ MW plausibel; Bundesländer-Δ konsistent; wind_typen_leistungen.md im Chat-Report.
48. Browser-Verifikation WP4: Betroffenheit NAP-Testfall → Bestand + NEU sichtbar; Cluster aus im Anzeigen-Modus.
49. Browser-Verifikation WP5 + Regressionen: NB-Filter via echtes change-Event; Infobar 31.011/22.402; Typ-Tab; Hersteller-Klick; Historie 3 Snapshots; 0 JS-Errors.
50. Finalisierung: iterations/V32.html + human-share-Kopie; Git-Status-Report; Abschlussbericht im Chat (Änderungsliste mit Quellen); KEIN Push.

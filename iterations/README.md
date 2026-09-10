# Iterationen — PV & Wind Karte

In diesem Ordner werden **alle klickbaren HTML-Iterationsschritte** gespeichert,
die während der Entwicklung erstellt werden. Jede Datei ist eine vollständige,
einzelbare HTML-App (Single-File mit eingebetteten Daten, ~25 MB).

## Regeln

1. **Jede Iteration muss hier gespeichert werden** — keine Ausnahme.
   Dateiname: `V<Version>_<Kurzbeschreibung>.html` (z. B. `V6_ArtPieSortFixes.html`).
2. **Dateien dürfen niemals gelöscht oder überschrieben werden.**
   Auch veraltete oder fehlerhafte Iterationen bleiben als Historie erhalten.
3. **Neue Iterationen werden am Ende hinzugefügt** — die Liste wächst mit jeder Revision.
4. Dieser Ordner ist **lokal** (nicht auf GitHub gepusht, da die Dateien zu groß für Git sind).
   Die aktuelle Live-Version liegt immer auf `gh-pages` im GitHub-Repo.

## Übersicht (chronologisch)

| Version | Datum | Beschreibung |
|---|---|---|
| V4 | 2026-09-01 | Bundesländer-Tab (Donut), Update-Historie |
| V4b | 2026-09-01 | Asset-Detail-Ansicht (4 Tabs + Deeplinks) |
| V4c | 2026-09-01 | Formatierung BL-Tabelle + Click-Hint |
| V5 | 2026-09-01 | Responsive Design (3 Breakpoints) |
| V5b | 2026-09-01 | Tabellen-Format + Pie-Chart-Fix (intern, nicht freigegeben) |
| V5c | 2026-09-01 | Three Fixes (Tabelle, Pie, Topbar) |
| V6 | 2026-09-01 | Art-Verteilungs-Pie + Sortierungs-Fixes |
| V7 | 2026-09-02 | Jahres-Filter nach Registrierungsdatum |
| V7b | 2026-09-02 | Monats-Filter + Alle-Anlagen-Tabelle |
| V7c | 2026-09-02 | Sortierbare Tabellen-Header |
| V8 | 2026-09-02 | Zubau-Tab mit 6 Charts |
| V8b | 2026-09-02 | Heatmap-Farben Rot-Gelb-Grün + Chart 6 Kumuliert + MW ganzzahlig |
| V8c | 2026-09-02 | Inbetriebnahme-Filter (Jahr+Monat, 1983–2026) |
| V8d | 2026-09-02 | Zweite Heatmap Inbetriebnahme (in V8e ersetzt) |
| V8e | 2026-09-02 | Zubau-Sub-Tabs (Registrierung/Inbetriebnahme) |
| V8f | 2026-09-02 | Senkrechte X-Achsen-Labels |
| V8g | 2026-09-02 | Werte außerhalb + volle MW-Zahlen + X-Achse tiefer |
| V8h | 2026-09-02 | Wind-Bruttoleistung-Korrektur (to_mw mehrstufig, 220 Kleinwindanlagen entfernt) |
| V8i | 2026-09-02 | Disclaimer-Panel (Hover/Tap) + Mobile-Fix |
| V8j | 2026-09-03 | QA-20-Punkte-Test: stray `</script>` entfernt, Disclaimer-Trigger unter Zoom-Control (Desktop 86px/Mobile 96px) (aktuelle Version) |
| V9 | 2026-09-03 | Status-Filter (F5, 4 Checkboxen) + Marker-Stile je Status |
| V9b | 2026-09-03 | Tabellen-Filter-Fix + Registrierungs-Spalten-Parsing |
| V9c | 2026-09-03 | Tabellen-Deep-Links final (NorthData extern, Koordinaten intern) |
| V10 | 2026-09-03 | Spannungsebenen-Filter (F2) |
| V11/V11b/V11c | 2026-09-03 | NAP-Suche (F1) + Performance-Fix (Lazy-Popup) + Datumsfilter-Fix |
| V12 | 2026-09-03 | NAP-Gruppenansicht (F3) |
| V13–V20 | 2026-09-03/04 | Betroffenheits-Revisionen 1–6 |
| V21–V21.6 | 2026-09-04 | Betreiber-Tab-Paket + Popup-Datum + Sortier-Fix |
| V22–V25 | 2026-09-06 | Größenklassen-Cluster + Geo-Ebene + LK-Tab + LIVE-Deploy |
| V27/V27b | 2026-09-06 | Daten-Update + kW/MW-Physik-Check |
| V28/V29/V29.1 | 2026-09-06 | NAP-Ranking-Tab + Spannungs-Fix + Filter-Reset + Kritis-Entfernung |
| V30 | 2026-09-08 | F-01 bis F-08 Fixrunde (Abgrenzung strikt, Snapshot-Dedup …) |
| V31 | 2026-09-08 | Netzbetreiber-Filter + Typ-Tab |
| V32/V32.1 | 2026-09-08/09 | Bugfixrunde 5 WP + Singlefile-TDZ-Hotfix |
| V33/V33.1 | 2026-09-09 | UX-Runde (Ringe grün/rot, CARTO-Backup, Popup-Hotfix) |
| V34 | 2026-09-09 | UX-Runde 2 (LK-Scroller oben, Popup-Re-Open, Panel 984 px) |
| V35 | 2026-09-10 | Betreiber-Diagramme (Wachstum/Technologie/EEG) + Filter-Reset-Ursprungszustand + Betroffenheits-Legende (aktuelle Version) |

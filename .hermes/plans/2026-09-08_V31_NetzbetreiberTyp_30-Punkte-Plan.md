# V31 — 30-Punkte-Plan: Netzbetreiber-Filter (WP1) & Typ-Tab (WP2)

**Datum:** 08.09.2026 · **Basis:** V30-Fixrunde (lokal, unverändert zu GitHub-Stand V29.1 + V30-Änderungen im Working-Tree)
**HARTE REGEL:** Kein Push/Deploy ohne explizite User-Freigabe. Alle Änderungen lokal + revisionierte HTML im Chat.

**User-Entscheidungen vorab geklärt:**
- WP1: 3.401 Anlagen ohne Netzbetreiber → Eintrag **„Keine Angabe"** im Filter
- WP2: Strikt nur 6 Spalten (Hersteller; Typ; Leistung; Anzahl; Anteil; Summe MW) — kein Ø MW

---

## PHASE A — RECHERCHE (abgeschlossen)

1. **[ERLEDIGT] Filterleisten-Anatomie:** Toolbar-Reihenfolge Typ → BL → LK → Gemeinde → Art → Leistung → Jahr → Monat → Inb-Jahr → Inb-Monat → Status → Spannungsebene. Einfügepunkt Gemeinde→Art bestätigt (Zeile ~268755).
2. **[ERLEDIGT] Filter-Mechanik applyFilters():** Liest select-Werte, filtert allUnits schrittweise; Gemeinde `u.g`, Art `(u.art||'')===art`. NB-Feld = `u.nb` (Format „Name (SNB…)", keine Pipe-Multi-Fälle).
3. **[ERLEDIGT] showAllUnits() Overlay:** Liest dieselben Filter (V25/V30-F01-Pfad); NB-Filter muss hier analog ergänzt werden.
4. **[ERLEDIGT] Optionen-Befüllung:** populateFilterLk/G (kontextuell BL→LK→Gemeinde), populateFilterArt (Set aus allUnits, sortiert). Aufruf im Daten-Load-Block nach meta-Verarbeitung.
5. **[ERLEDIGT] resetFilters():** IDs-Liste + populateFilterG-Neuaufbau — NB-Filter muss in IDs-Liste + populate-Aufruf.
6. **[ERLEDIGT] Datenlage NB:** 65.663 Anlagen, 3.401 ohne `nb` (=5,2%), 698 eindeutige NB; NB-Feld = Netzanschluss-Betreiber mit MaStR-Nr in Klammern.
7. **[ERLEDIGT] Stats-Tab-Struktur:** stats-tabs Buttons (data-tab) + section-Tabs (id="tab-…"); Tab-Switch-Handler ruft renderX() je Tab.
8. **[ERLEDIGT] Hersteller-Tab als Vorlage:** renderHersteller() (Top-N/Filter/Sort/Hover/Klick→selectHersteller→renderMarkers+fitBounds), th data-key + sortier-Handler-Muster, CSS #hersteller-table.
9. **[ERLEDIGT] Datenlage Typ:** Wind 42.006 gesamt (Karte), 41.488 mit `typ` (518 ohne — unter „Keine Angabe"), 4.351 eindeutige Typen, Top: E-70 E4 (938). Hersteller separat via `herst` (41.541 mit Angabe).
10. **[ERLEDIGT] _statsState + Bindings:** State-Objekt erweitern (typTop/typFilter/typSortKey/typSortDir), Bindings-Muster von hersteller-top/-filter/-clear/table th kopieren.

## PHASE B — PLANUNG

11. **WP1 Datenmodell-Entscheid:** Filter-Optionen = NB-Name **ohne** SNB-Klammerteil (lesbarer; SNB-Nr bleibt im title-Attribut), „Keine Angabe" mit value `__ohne__` (Analogie filter-se). Gruppierung: gleicher NB-Name + verschiedene SNB → zusammenfassen (Fälle prüfen).
12. **WP1 Filterposition:** `<label>Netzbetreiber</label><select id="filter-nb">` exakt zwischen Gemeinde- und Art-Label.
13. **WP1 populateFilterNb():** Set aus allenUnits;NB parsen (Name vor letzter Klammer); kontextuell? Nein — NB ist bundesweit, kein BL/LK-Context nötig (einfaches Set, sortiert); „Keine Angabe" ans Ende.
14. **WP1 applyFilters-Erweiterung:** `const nb = …filter-nb…; if (nb === '__ohne__') filtered = filter(u => !u.nb); else if (nb) filtered = filter(u => (u.nb||'').startsWith(nb…))` — Match-Strategie exakt festlegen (Name-Präfix vs. exakter Vollstring).
15. **WP1 showAllUnits-Erweiterung:** identische NB-Logik (F-01-Muster: Overlay == Karte).
16. **WP1 resetFilters-Erweiterung:** 'filter-nb' in ids-Liste; populateFilterNb() beim Init + nach Reset (eigentlich statisch — Init reicht, Reset nur value='').

## PHASE C — UMSETZUNG

17. **[WP1] HTML:** Filter-Select zwischen Gemeinde/Art einfügen (Punkt 12).
18. **[WP1] JS populateFilterNb()** implementieren + im Daten-Load-Block aufrufen (Punkt 13/16).
19. **[WP1] JS applyFilters()** NB-Klausel (Punkt 14).
20. **[WP1] JS showAllUnits()** NB-Klausel (Punkt 15).
21. **[WP1] JS resetFilters()** 'filter-nb' ergänzen (Punkt 16).
22. **[WP2] HTML Tab-Button** `<button class="tab" data-tab="typ">Typ</button>` nach Hersteller + `<section id="tab-typ">` mit Tabelle (Header: Hersteller; Typ; Leistung; Anzahl; Anteil; Summe MW — „Leistung" = MW der Einzelanlage/typ. Klarstellung: Spalte „Leistung" = Nennleistung des Typs (MW), da Typ = Modell), Top-N-Select + Textfilter + Count-Zeile.
23. **[WP2] _statsState** erweitern: typTop:'50', typFilter:'', typSortKey:'mw', typSortDir:'desc' (Default: absteigend nach Leistung).
24. **[WP2] renderTyp():** Aggregation aus allUnits (nur t==='wind', Karte-Basis = alle Status gemäß F-02-Entscheid? NEIN — User: „alle Windkraftanlagen, die auf der Karte darstellbar sind" = Karten-Default = In-Betrieb bs35; präzisieren in Implementierung: Basis = alle Wind-Anlagen im Export **gemäß Status-Filter-Einstellung der Karte?** → Entscheid: Basis = alle Wind-Einheiten im Export (42.006), da Karte default nur bs35 zeigt, aber Tab konsistent mit Hersteller-Tab sein soll (dort auch alle bs35 aus Statistik-JSON). → FINAL: Basis = Wind bs35 georef (31.011) analog Hersteller-Tab-Datenbasis — beim Bau verifizieren gegen _stats.gesamt.wind_anzahl).
25. **[WP2] Typ-Aggregation:** Gruppe = (herst + typ); Leistung = u.mw je Anlage (Nennleistung); Anzahl; Anteil = anzahl / Gesamt-Wind-Basis; Summe MW = Σ mw. „Keine Angabe" für fehlenden Typ/Hersteller.
26. **[WP2] Sortierung/Filter/Top-N + th-Bindings** (Muster von Hersteller).
27. **[WP2] Klick auf Zeile → selectTyp(herst, typ):** alle Wind-Anlagen mit diesem (herst,typ) via renderMarkers + fitBounds + search-input-Label + closeStats (Analogie selectHersteller).
28. **[WP2] CSS:** #typ-table analog #hersteller-table (Kopie der CSS-Regeln mit neuer ID).
29. **[WP2] Tab-Switch-Handler:** `if (btn.dataset.tab === 'typ') renderTyp();` ergänzen.

## PHASE D — ÜBERPRÜFUNG

30. **Build:** cp src → dist, bundle_singlefile.py (42,4 MB), Server 8911, Browser `?v31=1`.
31. **WP1-Verifikation DOM:** a) Filter-Reihenfolge im DOM (Gemeinde→Netzbetreiber→Art); b) Optionen-Anzahl ≈ 699 (+„Keine Angabe"); c) NB wählen → Infobar-Markerzahl + Overlay „Alle Anlagen anzeigen" = identische Zahl; d) Kombi-Test NB + LK + Status; e) „Keine Angabe" → 3.401; f) Reset → alles leer.
32. **WP2-Verifikation DOM:** a) Tab „Typ" vorhanden (11 Tabs gesamt); b) Default-Sortierung Leistung desc; c) Header-Klick sortiert asc/desc; d) Top-N + Textfilter; e) Summen: Σ Anzahl = Basis-Wind, Σ Anteil ≈ 100%; f) Klick auf Typ-Zeile → Karte zeigt nur diesen Typ (Markerzahl = Tabellenanzahl), fitBounds, Suchfeld-Label.
33. **Regressions-Check:** Infobar 31.011/22.402; Hersteller-Tab unverändert; F-01-Overlay (HS+SE=10.751); Historie 3 Zeilen; 0 JS-Errors.
34. **Revision + Doku:** iterations/V31_NetzbetreiberTyp.html + human-share; PROJEKTSTAND-V31-Block; statistik.md (11 Tabs), README (Features), datenmodell (NB-Feld) — im Chat-Statusreport.

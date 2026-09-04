# ROADMAP — Feature-Wünsche & Umsetzbarkeit (laufendes Log)

> **Zweck:** Sammelpunkt für alle zukünftigen Implementierungswünsche (User-Braindumps).
> Jeder Wunsch wird hier erfasst, faktenbasiert bewertet und Schritt für Schritt umgesetzt.
> Erstellt: 2026-09-03 · Quelle: User-Braindump + Agent-Recherche (verifizierte Zahlen).
>
> ## 🔒 Arbeitsablauf je Feature (User-Vorgabe, 03.09. — BINDEND)
> 1. Pro Feature (Einzelschritt) wird ein **20-Punkte-Plan** erstellt mit den 4 Phasen
>    **Recherche → Planung → Umsetzung → Prüfung** (Prüfung: erfolgte Umsetzung gemäß
>    Planung/Research? Fehler?). Der Plan wird vor Beginn dokumentiert und während der
>    Umsetzung abgehakt.
> 2. Pro Feature wird die **Dokumentation aktualisiert UND geprüft** (welche bestehenden
>    Doku-Teile sind betroffen? angepasst oder als aktuell bestätigt).
> 3. **Nach jedem Einzelschritt** (F2, F5, F1 …): Finalisierung Umsetzung + Doku, dann
>    **klickbare HTML-Datei in den Chat** (MEDIA:).
> 4. **User-Freigabe der HTML-Datei** ist Gate zum nächsten Umsetzungsplan — ohne Freigabe
>    kein nächstes Feature.
> 5. **Jede HTML-Revision wird lokal gespeichert** (iterations/, niemals löschen — Regel 3
>    der GRUNDSATZENTSCHEIDUNG.md) + GitHub bleibt gesperrt ohne explizites „Ja" (Regel 4).

---

## Freigabe-Status (03.09.2., User-Braindump Nr. 2)

| Feature | Status | User-Entscheidung |
|---|---|---|
| F2 Spannungsebenen-Filter | ✅ FREIGEGEBEN | folgt Agent-Empfehlung, erster Schritt |
| F5 Status-Filter | ✅ FREIGEGEBEN | alle 4 Status-Werte (In Planung / In Betrieb / Vorüb. stillgelegt / Endg. stillgelegt), **Karte danach filterbar** |
| F1 NAP-Suche | ✅ FREIGEGEBEN | folgt Agent-Empfehlung |
| F4 Betroffenheitsanalyse | ⏳ KONKRETISIERT (s. u.), Umsetzung NACH F2/F5/F1 | 2 Modi + Radius + Leistung |
| F3 NAP-Gruppenansicht | ⏳ offen (Reihenfolge F2→F5→F1→F3→F4/F6) | |
| F6 Betroffenheit Entfernungen | ⏳ in F4 integriert (s. u.) | |

---

## F4 (KONKRETISIERT) — Betroffenheitsanalyse (User-Vision 03.09., Wortlaut eingearbeitet)

**Kernfrage des Users (als Betreiber):** *„Wenn der Datensatz geupdated wird (Cron), welche
der neu hinzugefügten ODER entfernten Assets betreffen MINE?"*

**Funktionsweise:**
1. **Basis-Referenz eingeben (3 Wege, alle in der Suche vorhanden):**
   eine konkrete Anlage ODER ein Betreiber (alle seine Anlagen) ODER ein Netzanschlusspunkt.
2. **Abgleich gegen die Update-Deltas** (neue + entfernte Assets aus dem Snapshot-Delta je
   Cron-Lauf). Ein **Match** wird ausgelöst bei:
   a) **NAP-Match:** Neuanlage/Entfernung am selben Netzanschlusspunkt, ODER
   b) **Umkreis-Match (Radius-Analyse):** Neuanlage/Entfernung innerhalb einer gewissen
      **Entfernung** zum Asset bzw. zu den Assets des Betreibers.
   **WARUM Radius zusätzlich?** (User-Begründung, übernommen): Die eigene Leitungstrasse
   kann an einem ANDEREN NAP verlaufen und durch Bauarbeiten der Neuanlage trotzdem
   beeinflusst werden → NAP-Match allein greift zu kurz.
3. **Radius-Eingabe durch den User:** Kilometerangabe **2–20 km** (Slider/Auswahl).
   Bei Betreiber-Suche: Radius gilt um jede Anlage des Betreibers (Union der Kreise).
4. **Modi (Agent-Empfehlung, von User bestätigt):** „neu registriert" vs. „neu in Betrieb"
   (Registrierung im Register ≠ reale Netzinbetriebnahme) + **Leistungsbetroffenheit**
   als Zusatzwert (z. B. „+45 MW am Knoten X, bestehend 120 MW").
5. **Benachrichtigung:** Match wird dem User gemeldet (Report), inkl. entfernter Assets
   (F6 komplett in F4 integriert — Ereignistypen: NEU / ENTFERNT).

**Technische Grundlagen (verifiziert):** Koordinaten je Einheit vorhanden (Haversine-Formel
für Radius-Match, 53.500 georef Anlagen); Delta-System liefert added/removed mit vollen
Asset-Dicts inkl. Koordinaten (V4b); NAP-Join 93,7 %.
**Konkretisierungen (User, 03.09.2.):**
- **Trigger: NICHT automatisch im Cron** — die Analyse läuft als **User-Funktion auf der
  HTML-Seite**: User wählt konkretes Asset ODER Netzanschlusspunkt ODER Betreiber aus
  (Suche) und startet die Analyse manuell.
- **Ausgabe: Telegram** (wie gewohnt) — klickbare HTML nach Fertigstellung im Chat.
- F4 wird nach F2/F5/F1 umgesetzt; Detail-Konzept (Datenfluss: Delta → Server-Berechnung →
  HTML-Interaktion) im 20-Punkte-Plan F4.

**Status: KONKRETISIERT — Umsetzung nach F2/F5/F1** 

### 📋 20-Punkte-Plan F4+F6 — Betroffenheitsanalyse (User-Funktion auf der HTML-Seite)

**Verifizierte Datenlage (03.09., vor Umsetzung):**
- `historie.json` liefert je Delta `added_assets`/`removed_assets` mit vollen Asset-Dicts
  (19 added / 1 removed im Testfenster 29.08.→01.09.), inkl. lat/lon, mw, ab (Betreiber),
  inb, m (MaStR-Nr). Koordinaten vollständig.
- NAP-Match: über `lid` (lokation_id) — in einheiten.json vorhanden (F1), in Snapshot-Assets
  NICHT → NAP-Match im Frontend über `lid`-Lookup der MaStR-Nr aus allUnits (Deckung
  snapshot ↔ einheiten.json prüfen).
- Umkreis-Match Performance (Pi5, live gemessen): Haversine 1 Neuanlage × 53.500 Bestand
  = 0,40 s → 19 Neuanlagen ≈ 8 s inline akzeptabel; mit lokalem Spatial-Grobfilter
  (Bounding-Box-Vorfilter) < 1 s.
- Modi: „neu registriert" (DatumLetzteAktualisierung ≈ Delta-Fenster) vs. „neu in Betrieb"
  (inb im Fenster) — beide aus den Delta-Assets filterbar.

| # | Phase | Punkt |
|---|---|---|
| 1 | Recherche | ✅ Datenlage verifiziert (oben) |
| 2 | Planung | UI-Konzept: Tab „Betroffenheit" im Statistik-Panel ODER eigener Dialog — Entscheidung: eigener Abschnitt im Statistik-Panel (neuer Tab), weil Suche/Filter dort schon vorhanden |
| 3 | Planung | Referenz-Wahl: Suchfeld (Anlage/Betreiber/NAP — nutzt bestehende Suchlogik) + Ergebnis-Liste „Referenz" |
| 4 | Planung | Match-Modi: Checkbox „NAP-Gleichheit" (immer an) + Radius-Slider 2–20 km (default 5) + Modi-Select „neu registriert"/„neu in Betrieb"/„beides" |
| 5 | Planung | Zeitfenster: Select letztes Delta / alle Deltas (Historie) |
| 6 | Umsetzung | Haversine + BBox-Vorfilter als JS-Funktion (`_haversine`, `_bboxPreFilter`) |
| 7 | Umsetzung | NAP-Match: lid-Vergleich via allUnits-Lookup (m → lid) |
| 8 | Umsetzung | Analyse-Kern: `runBetroffenheitsanalyse(ref, opts)` → Events {typ: NEU/ENTFERNT, asset, matchTyp: NAP/RADIUS, distKm, mw} |
| 9 | Umsetzung | Leistungs-Betroffenheit: Summe MW je Match-Gruppierung (am selben NAP / im Radius) + Bestands-MW am Ort |
| 10 | Umsetzung | UI: Ergebnisliste (Events sortiert nach Distanz/MW), Klick → Karte (flyTo + Popup), farbliche Trennung NEU/ENTFERNT |
| 11 | Umsetzung | Indikations-Hinweis („gleicher Anschlussknoten ≠ automatisch geteiltes Netz") im UI-Header, wie in Anmerkung 1 |
| 12 | Umsetzung | leeres Ergebnis: freundlicher Hinweis + Option Radius erhöhen |
| 13 | Prüfung | Test NAP-Match: Referenz = Anlage am NAP einer der 19 Neuanlagen |
| 14 | Prüfung | Test Radius: Referenz = Anlage nahe „PV Laaber 4" (7.99/49.32) mit 5 km → Treffer |
| 15 | Prüfung | Test Modi: „neu in Betrieb" (inb 2026-08-26 etc. im Fenster) vs. „neu registriert" |
| 16 | Prüfung | Test ENTFERNT: WP Buschmühlen (54.03/11.63) — Referenz in 20 km → Event ENTfernt |
| 17 | Prüfung | Regression: F5/F2/F1/F3/Datumsfilter/Performance |
| 18 | Doku | ROADMAP as-built + PROJEKTSTAND V13 |
| 19 | Lieferung | Revision iterations/V13_Betroffenheit.html + klickbare HTML im Chat |
| 20 | Freigabe | User-Prüfung → Gate |

**Status: UMGESETZT (03.09., alle 20 Punkte ✅) — wartet auf User-Freigabe**

**Umsetzung (V13, 03.09.):**
- UI: Neuer Statistik-Tab „⚠ Betroffenheit" mit Indikations-Hinweis (Anmerkung 1) im Kopf.
- Referenz-Wahl (Punkt 3): Suchfeld mit Trefferliste (NAP exakt/Präfix, Betreiber enthält,
  Anlage Name/MaStR-Nr), Auswahl → Bestätigungsbox, Analyse-Button entsprichtt erst dann.
- Optionen (Punkt 4/5): Zeitfenster „letztes Update"/„alle Updates", Modus „neu registriert +
  neu in Betrieb"/„nur registriert"/„nur in Betrieb" (inb-Filter: Assets ohne inb werden
  übersprungen), Radius-Slider 2–20 km (Default 5, deaktivierbar), NAP-Gleichheit immer aktiv.
- Analyse-Kern (Punkte 6–9): `_haversine` + BBox-Vorfilter; NAP-Match über lidByM-Lookup
  (m → lid aus allUnits, 53.915 Einträge); Leistungs-Betroffenheit: Summe NEU/ENTFERNT-MW
  + Bestands-MW am Referenz-Knoten; NAP-Kontext (SAN, NB, Ebene, Regelzone) im Summary.
- Ergebnisliste (Punkt 10): NAP-Match zuerst, dann Distanz; grün 🆕 NEU / rot 🗑️ ENTFERNT;
  Klick → Stats zu, Karte zoomt, Lazy-Popup.
- Leeres Ergebnis (Punkt 12): Hinweis mit Radius-Tipp.
- **Bug während Umsetzung (dokumentiert):** (1) `_historie` statt `historie` — Variable war
  anders benannt, ReferenceError im ersten Lauf. (2) initBetroffen mit _bffInitDone-Guard
  + addEventListener führte bei Re-Init zu veraltetem Handler-Zustand (Button onClick war
  null, Ergebnisliste updatete nicht) → Fix: idempotentes oninput/onclick/onkeydown ohne Guard.
- Performance (Punkt 16): Analyse 0 ms (BBox-Vorfilter), 20 Assets geprüft.

**Verifiziert (browser, frischer Load, echter Tab-Klick-Pfad):**
- Test A (Punkt 13/14, NAP+Radius): Referenz SEE991807581772 (tLa43) → 2 Treffer:
  tLa43 NAP-Match + tLa52 Umkreis 2 km, „+ 2 neu · 17,9 MW · Bestand am Knoten 8 MW" ✅
- Test B (Punkt 16, ENTFERNT): Referenz SEE965292104525 (WP Buschmühlen, die entfernte
  Anlage selbst, Radius 20) → 1 Treffer: 🗑️ ENTFERNT, NAP-Match, „− 1 entfernt · 2,5 MW ·
  Bestand am Knoten 28,1 MW · NAP-Kontext SAN953307809879, E.DIS Netz, Mittelspannung,
  50Hertz" ✅
- Test C (Punkt 15, Modi): „nur neu in Betrieb" → 3 Treffer (inb-Filter greift) ✅
- Zeilen-Klick → Karte + Popup ✅ · Regression: F5 9.273 ✅, F2 31.465 ✅, Datum 2.566 ✅,
  F1-NAP-Suche ✅, applyFilters 454 ms ✅

**Revision:** iterations/V13_Betroffenheit.html. Nicht gepusht (Regel 4).

**V13b (04.09., nach User-Feedback):** Betroffenheits-Suchfeld macht jetzt Live-Suggest
wie die Hauptsuche — ab 2 Zeichen suchen die ersten Treffer sofort (250 ms Debounce),
Enter + 🔍-Button funktionieren weiterhin. Verifiziert: „To" → 25 Treffer live, „Torn" →
5 Betreiber-Treffer, Klick wählt Referenz. Revision: iterations/V13b_BetroffenheitLiveSuche.html.

**V13c (04.09., nach User-Feedback):** Anlagennamen-Suche im Betroffenheits-Tab gefixt —
**Bug:** die Anlagen-Suche prüfte `u.name`, das Feld heißt aber `n` → Anlagennamen
wurden nie gefunden (nur MaStR-Nummern). Fix: `u.n`. Zusätzlich Betreiber-Treffer auf
8 gecappt, Anlagen auf 12 erhöht, damit Namen in der Liste sichtbar bleiben. Verifiziert:
„Ringleben" → 6 Anlagen-Treffer live, Klick → Referenz → Analyse 1 Treffer; Regression
„Torn" (12 Anlagen + 5 Betreiber), NAP-Suche, V13-Test A (2 Treffer) alle grün.
Revision: iterations/V13c_AnlagennameLiveSuche.html.

### V14 — Portfolio-Suche (Betreiber-Gruppe über Invest-Gesellschaften hinweg)

**User-Wunsch:** Große Betreiber (z. B. „Annapark") splitten sich in viele Invest-Gesellschaften
(„Annapark Solar 1 GmbH ＆ Co. KG", „Annapark Solar 2 GmbH" …). Bisher: jede Gesellschaft
einzeln suchen. Ziel: **portfolioweise Prüfung** — alle Betreiber, deren Name einen gemeinsamen
Kern enthält, in EINER Analyse.

**5-Punkte-Plan (User-Anforderung):**
1. **Recherche:** Betreiberfelder im Datensatz prüfen (Top-Betreiber, Namensmuster der
   Invest-Gesellschaften) ✅ erledigt — keine echte „Annapark"-Gruppe im Bestand (User-Beispiel),
   aber das Muster „X GmbH ＆ Co. KG / X 1 GmbH / X Solar 2 GmbH" ist überall vorhanden
   (z. B. BOREAS, ABO Energy, WP-Betreiber mit Dutzenden Projekt-Gesellschaften).
2. **Planung:** Neuer Referenz-Typ „Portfolio" im Betroffenheits-Tab:
   - Suchfeld: Eingabe eines Namenskerns → Live-Trefferliste zeigt **Portfolio-Gruppen**
     (Kern + Anzahl Gesellschaften + Anlagen).
   - Gruppenbildung (Frontend, beim ersten Treffer gecacht): alle Betreiber (`u.ab`) dedupliziert;
     Basis = Normalisierung (GmbH/UG/＆ Co. KG/Co. KG/KG/GbR/eG/SE/AG/mbH/Stiftung/…, Nummern,
     römische Ziffern, Ampel-Stopwörter entfernen); Kern = längster gemeinsamer Präfix bzw.
     Token-Cluster — pragmatisch: Gruppe = alle Betreiber, die mit dem eingegebenen Kern beginnen
     ODER ihn enthalten; Vorschlagsliste gruppiert die Betreiber-Vollnamen unter dem Kern.
   - Analyse: Portfolio-Referenz sammelt refLids + refPoints über ALLE Gruppen-Betreiber
     (gleicher Pfad wie `kind === 'betreiber'`, nur Set statt Einzelname).
   - Ergebnisliste bekommt Spalte **Betreiber-Gesellschaft** (schon da: `a.ab`), Summary zählt
     betroffene Gesellschaften.
3. **Umsetzung:** UI (Radio/Auswahltyp im Panel? → nein: Typ automatisch — Treffer zeigt
   „Portfolio (N Gesellschaften)" als eigenen Zeilentyp), bffSelectRef, Analyse-Kern,
   Summary-Erweiterung (Anzahl Gesellschaften betroffen), Ergebnis-Rendering unverändert.
4. **Prüfung:** Browser-Test mit realer Gruppe (z. B. „BOREAS" → Dutzend Gesellschaften):
   Live-Treffer, Referenz-Auswahl, Analyse über alle Gesellschaften, Regression V13-Tests.
5. **Doku as-built:** ROADMAP (V14-Abschnitt), PROJEKTSTAND (V14), Revision
   iterations/V14_PortfolioSuche.html + human-share. Kein Push (Regel 4).

**Status: UMGESETZT + GEPRÜFT (04.09., alle 5 Plan-Punkte ✅) — wartet auf User-Freigabe**

**Umsetzung (V14):**
- `_bffNormKern()`: Betreibername → Namenskern (Rechtsformen GmbH/KG/UG/GbR/eG/SE/AG/…,
  Branchen-Wörter PV/Wind/Solar/Energie/Projekt/Holding/…, röm. Ziffern, arabische Nummern
  entfernt; norm() = bestehende Umlaut/Casing-Normalisierung).
- `bffPortfolioGroups()`: gruppelt ALLE Betreiber nach identischem Kern (Cache beim ersten
  Aufruf, Gruppen ≥ 2 Gesellschaften); Suche matcht Kern ODER Vollnamen, Top 3 nach Größe.
- Live-Trefferliste: neuer Zeilentyp „👥 Portfolio „Kern" — N Betreiber-Gesellschaften,
  M Anlagen" (Tag: Portfolio), direkt unter den Einzelbetreibern.
- Analyse: `kind === 'portfolio'` sammelt refLids + refPoints über ALLE Gesellschaften;
  NAP-Match + Radius wie gehabt gegen dieses Set.
- Summary: zusätzliche Karte **„Betroffene Gesellschaften: X von N"** (gelb).

**Verifiziert (browser, frischer Load, echter Tab-Klick-Pfad):**
- „abo energy" → Portfolio „abo ＆ ." mit **30 Gesellschaften / 65 Anlagen** als Treffer ✅
- Analyse über dieses Portfolio: **3 Treffer · 22,8 MW · Bestand am Knoten 64,9 MW ·
  Betroffene Gesellschaften 1 von 30** — exakt der User-Use-Case (portfolioweite Prüfung
  ohne Einzelprüfung jeder Invest-Gesellschaft) ✅
- „boreas" → Portfolio (4 Gesellschaften, 15 Anlagen) + 7 Einzelbetreiber + Anlagen ✅
- Bug während Umsetzung: Set.some existiert nicht → `[...g.ges].some()` (dokumentiert)
- Regression: Einzelbetreiber tLa43 (2 Treffer @5 km) ✅ · ENTFERNT WP Buschmühlen
  (🗑️ @20 km) ✅ · Anlagenname Ringleben (6 Anlagen) ✅ · NAP-Suche ✅ ·
  Zeilen-Klick → Karte+Popup ✅ · Portfolio-Suche nach Cache-Aufbau 6 ms ✅

**Revision:** iterations/V14_PortfolioSuche.html. Nicht gepusht (Regel 4).

### V15 — Revisionspaket Betroffenheits-Tab (04.09., User-Feedback, 20-Punkte-Plan)

**User-Befunde:** (1) ENERPARC-Portfolio: Matches korrekt gelistet, aber Karte „Betroffene
Gesellschaften" leer/falsch. (2) CEE: kein Gesamt-Portfolio, nur Einzelparks. (3) Wunsch:
„Anzeigen"-Button nach Analyse → betroffene Assets auf der Karte filtern. (4) Wunsch: farbiger
Radius/Ring um betroffene Bestandsanlagen (visualisiert das Suchfeld). (5) Wunsch: Beschreibung
der Prüfmethode ergänzen (NAP-Gleichheit + Umkreis, wie genau?).

**Recherche (verifiziert in Daten):**
- Bug 1 (Karte „Betroffene Gesellschaften"): `gesBetroffen` zählt nur Assets, deren `a.ab`
  in `_bffRef.abs` ist — aber bei ENERPARC landeten die Treffer in ANDEREN Kern-Gruppen
  („enerparc tu", „enerparc eu") als die gewählte („enerparc", 143 Ges) → 0 von 143, obwohl
  4 ENERPARC-Neuanlagen da sind. Zwei-Ebenen-Problem: Kern-Gruppen sind zu fein.
- Bug 2 (CEE): Kern-Normalisierung lässt Parknamen stehen („CEE Windpark Schmölln" → Kern
  „cee schmoelln", „CEE PVF Eckolstädt" → „cee pvf eckolstaedt") → 60 Einzel-/Mini-Gruppen,
  keine Gesamt-CEE-Gruppe. Der Marken-Teil („CEE") ist das Verbindende, nicht der Kern.
- **Lösung für beide: Brand-Gruppierung als 2. Ebene** — Brand = erstes Wort des Kerns
  (validiert: ≥ 3 Zeichen, alphanumerisch, nicht generisch wie windpark/solarpark/stadtwerke,
  keine natürlichen Personen). Brand-Gruppe = alle Betreiber mit gleichem Brand:
  ENERPARC → 212 Ges (enthält alle 4 Delta-Gesellschaften ✅), CEE → 60 Ges, ANUMAR → 220,
  ABO → 71, UGE → 91, ENERTRAG → 91, wpd → 63 … 989 valide Brands ≥ 3 Ges.

**Planung (20 Punkte):**
1.  Datenmodell: `bffPortfolioGroups` erweitert — gibt Kern-Gruppen UND Brand-Gruppen zurück
    (Typ-Feld `grouping: 'brand'|'kern'`), Brand bevorzugt, max 4 Vorschläge.
2.  Brand-Validierung aus Recherche als `_bffBrandOf(kern)` (Stopwort-Liste generisch).
3.  Trefferliste: Brand-Zeile „👥 Betreibergruppe „ENERPARC" — 212 Gesellschaften, N Anlagen",
    Kern-Zeile bleibt (feiner) — User wählt Ebene.
4.  Bug-1-Fix Summary: „Betroffene Gesellschaften" zählt gegen die GEWÄHLTE Gruppe
    (Brand oder Kern), Gesellschaften der Gruppe = Set; Zählung über `a.ab ∈ abs` bleibt,
    aber `abs` ist jetzt bei Brand die Vereinigung → korrekte Zahlen.
5.  ZUSATZ (Verständlichkeit): Liste der betroffenen Gesellschaften im Summary-Klapptext
    (Details-Element), damit „1 von 212" nachvollziehbar wird.
6.  „Anzeigen"-Button (Punkt 3 User): neben „🔍 Analyse starten", disabled bis Analyse
    mit Treffern gelaufen.
7.  Anzeigen-Logik: setzt Kartenfilter auf die gematchten Assets (NEU+ENTFERNT der letzten
    Analyse) — Implementation über bestehenden Filter-Mechanismus (renderMarkers mit
    Subset, Filter-Reset-Button bleibt funktional).
8.  Marker der Analyse-Treffer visuell markieren (bereits durch Filter = nur diese sichtbar).
9.  Farbradius (Punkt 4 User): L.circle um jede REFERENZ-Anlage (refPoints), Radius =
    gewählter Umkreis, gestrichelte Linie + transparente Füllung; Farbe je nach Match-Typ.
10. Ring nur wenn Radius aktiv; NAP-Match-Referenz (lids ohne Punkte) → Kreise um die
    Anlagen der Gruppe mit Radius 0-Anzeige? → nein: NAP-Matches brauchen keinen Ring,
    Ring nur bei refPoints + radiusKm > 0.
11. Ringe in Layer-Group `_bffRadiusLayer`, Cleanup bei neuer Analyse/Tab-Close/Reset.
12. Tooltip auf Ring: „Suchradius 5 km um <Referenz>".
13. Beschreibungstext (Punkt 5 User): Panel-Kopf erweitern — Prüfmethode prägnant:
    NAP-Gleichheit (exakt gleicher Netzanschlusspunkt via lokation_id) ODER Umkreis
    (Haversine-Luftlinie um Koordinaten der Referenz-Anlagen), Bereich 2–20 km.
14. Textstellen: Panel-Intro + ( falls vorhanden) Info-Zeile über Analyse-Button.
15. Alles in src/index.html, kein Daten-Export nötig (alles Frontend).
16. Rebuild dist + bundle.
17. Prüfung Bug 1: ENERPARC-Brand-Referenz → Analyse → Karte „Betroffene Gesellschaften"
    zeigt korrekte Zahl (Erwartung: 3 von 212 bzw. alle Treffer-Gesellschaften).
18. Prüfung Bug 2: „cee" → Brand-Gruppe „CEE" (60 Ges) als Vorschlag; Analyse läuft über
    alle CEE-Gesellschaften.
19. Prüfung Neu: Anzeigen-Button filtert Karte auf Treffer; Ringe sichtbar mit Tooltip;
    Beschreibungstext korrekt; Regression V13/V14-Tests.
20. Doku as-built (ROADMAP V15 + PROJEKTSTAND), Revision iterations/V15 + human-share,
    kein Push.

**Status: UMGESETZT + GEPRÜFT (04.09., alle 20 Punkte ✅) — wartet auf User-Freigabe**

**Umsetzung (V15):**
- **Bug 1 (Betroffene Gesellschaften leer):** Root Cause zweistufig — (a) `Set.some` /
  defektes `split()` im Bundle-Kontext → Regex-Fix; (b) Kern-Gruppen zu fein: ENERPARC-
  Treffer hingen in anderen Kern-Gruppen („enerparc tu", „enerparc eu") als der gewählten.
  Lösung: **Brand-Ebene** — `_bffBrandOf()` extrahiert das erste Kern-Wort als Marke
  (Stopwort-Filter gegen generische Namen: windpark, solarpark, stadtwerke, firma …);
  `bffPortfolioGroups()` liefert jetzt Kern-Gruppen UND Brand-Gruppen (Betreibergruppe
  zuerst). Summary zählt gegen die gewählte Gruppe und zeigt die Namen der betroffenen
  Gesellschaften in einem Klapptext (`<details>`).
- **Bug 2 (CEE kein Gesamt-Portfolio):** Gleicher Fix — Brand „cee" vereint jetzt ALLE
  60 CEE-Gesellschaften (184 Anlagen); vorher nur 4, weil Einzel-Gesellschaften bei der
  Kern-Gruppenbildung (≥ 2 Ges) rausfielen. Brand-Bildung läuft jetzt über ALLE Betreiber.
- **Anzeigen-Button:** `bffShowOnMap()` — schließt Statistik, filtert die Karte per
  `_bffShowSet` auf die Analyse-Treffer (in `applyFilters()` integriert), zoomt auf
  Treffer+Referenz, Ringe bleiben sichtbar. Reset über „Alle anzeigen" (showAllUnits)
  oder jeden Filterwechsel.
- **Farbringe:** `_bffDrawRings()` — L.circle ( Bernstein #f59e0b, gestrichelt, 8 % Füllung)
  um jede Referenz-Anlage mit dem gewählten Suchradius, Tooltip „Suchradius X km".
  Dedupe der Referenzpunkte + Cap bei 50 Ringen (Portfolio-Performance).
- **Beschreibung:** Klapptext „Wie funktioniert die Betroffenheitsprüfung?" im Panel:
  NAP-Gleichheit (Lokations-ID, stärkstes Signal) ODER Umkreis (Haversine-Luftlinie),
  ODER-verknüpft, Ringe visualisieren das Suchfeld.

**Verifiziert (browser, frischer Load, echte User-Pfade):**
- ENERPARC: Betreibergruppe „enerparc" 212 Ges → Analyse: **14 Treffer · +13 neu 75,5 MW ·
  −1 entfernt 2,5 MW · Bestand 3.201 MW · 3 von 212 Gesellschaften** mit Namensliste
  (TU 18, TU 20, EU 1.7) ✅ — exakt der gemeldete Bug, behoben
- CEE: Betreibergruppe „cee" **60 Ges / 184 Anlagen** ✅ (war 4)
- Anzeigen-Button: 2 Marker sichtbar (tLa43+tLa52), Filter aktiv, Reset → alle Marker ✅
- Ringe: 1 Ring um Referenz (nach Dedupe), Tooltip ✅
- Regression: reg 2019 → 16.747 ✅ · SE Mittelspannung → 31.465 ✅ · F1-Suggest „tLa43" ✅

**Revision:** iterations/V15_BetroffenheitRevision.html. Nicht gepusht (Regel 4).

### V16 — Revisionspaket 2 Betroffenheits-Tab (04.09., User-Feedback, 20-Punkte-Plan)

**User-Befunde:** (1) Treffer-Reihenfolge im Suchfenster: erst Betreiber(gruppe), dann
Portfolio, dann einzelne Projektgesellschaften. (2) X-Button zum Löschen des Suchfelds.
(3) Karte zeigt viele Ringe OHNE Betroffenheit + die betroffene Bestandsanlage fehlt.
(4) Tabellarische Gegenüberstellung Bestand↔Neu mit Deeplinks. (5) Vermischungs-Verdacht
bei Folge-Suchen (ENERPARC → CEE).

**Recherche (Code-Review, verifiziert):**
- **Vermischung BESTÄTIGT (Bug):** `runBetroffenheitsanalyse` returnt bei „Keine Treffer"
  (Z. 5098) und bei „Referenz ohne Koordinaten" (Z. 5045) FRÜH — ohne `_bffLastEvents`,
  `_bffLastRefPoints`, Radius-Ringe, Anzeigen-Filter und bff-show-Button zurückzusetzen.
  Folge-Suche mit 0 Treffern lässt die Kreise der Vor-Suche stehen → exakt der User-Befund.
- **Ringe zu viel (Bug):** `_bffDrawRings` zeichnet um ALLE refPoints (alle Anlagen des
  Betreibers/Portfolios, Cap 50) — nicht nur um die betroffenen. → „viele Kreise ohne
  Betroffenheit".
- **Bestandsanlage fehlt (Bug):** `bffShowOnMap` baut `_bffShowSet` nur aus Event-Assets
  (NEU/ENTFERNT) — die betroffene Bestandsanlage (Referenz) ist nicht im Set, obwohl sie
  in allUnits wäre.
- **Reihenfolge:** aktuell NAP → Betreiber → Portfolio → Anlagen; gewünscht:
  Betreibergruppe → Portfolio → Einzel-Gesellschaften → NAP → Anlagen.

**Planung (20 Punkte):**
1. Recherche ✅ (oben).
2. Reihenfolge in `bffSearchRef`: brand → kern → einzelbetreiber → nap → anlagen.
3. X-Button im Suchfeld (HTML, ⓧ rechts).
4. X-Logik: Input leeren + Trefferliste leeren.
5. `_bffResetAnalysis()`: Ringe weg, _bffLast* null, bff-show disabled, Anzeigen-Filter aus.
6. Early-Returns der Analyse rufen Reset auf (0 Treffer, keine Koordinaten, keine Deltas).
7. Match-Tracking im Analyse-Kern: matchedRefKeys (Radius) + matchedNaplids (NAP).
8. Pro Event refKey/refLid merken (für Bestands-Zuordnung).
9. Ringe NUR um getroffene Referenzpunkte (matchedRefKeys).
10. Betroffene Bestandsanlagen ermitteln: Units an matchedRefKeys + Units an matchedNaplids.
11. Anzeigen-Set = Event-Assets + betroffene Bestandsanlagen → Karte zeigt beide.
12. Tabelle (4 Spalten): Bestands-Betreiber · Bestands-Asset (Deeplink) · Neuer Betreiber ·
    Neues Asset (Deeplink); kompakt, scrollbar.
13. Deeplink-Klick → closeStats + Karte + Popup (wie Ergebnis-Zeilen-Klick).
14. Rebuild dist + bundle.
15. Prüfung Reihenfolge: 'cee' → Betreibergruppe zuerst, dann Portfolio, dann Gesellschaften.
16. Prüfung X-Button leert Feld + Liste.
17. Prüfung ENERPARC: Ringe nur um betroffene Anlagen; Karte: Bestand + Neu sichtbar.
18. Prüfung Vermischung: ENERPARC (Treffer) → CEE (0 Treffer) → Ringe/Filter WEG.
19. Prüfung Tabelle + Deeplinks; Regression F1/F2/reg2019/SE.
20. Doku as-built + Revision iterations/V16 + human-share, kein Push.

**Status: UMGESETZT + GEPRÜFT (04.09., alle 20 Punkte ✅) — wartet auf User-Freigabe**

**Umsetzung (V16):**
- **Reihenfolge Suchfenster:** Betreibergruppe (Brand) → Portfolio (Kern) → einzelne
  Betreiber (max 8) → NAP → Anlagen (max 12).
- **✕-Button** neben dem Suchfeld: leert Input + Trefferliste (Analyse-Ergebnisse bleiben).
- **Vermischungs-Fix:** `_bffResetAnalysis()` — bei „Keine Treffer" und „Referenz ohne
  Koordinaten" werden Ringe entfernt, `_bffLast*` genullt, Anzeigen-Filter + Button
  zurückgesetzt. Folge-Suchen starten sauber.
- **Ringe nur um Betroffene:** Analyse merkt `matchedKeys` (Radius) / `matchedLids` (NAP);
  `_bffDrawRings` zeichnet nur noch um tatsächlich getroffene Referenz-Anlagen.
- **Bestandsanlage auf der Karte:** `_bffLastBestand` = Bestands-Units an getroffenen
  Punkten/NAPs; „Anzeigen" zeigt jetzt Bestand + Neu/Entfernt zusammen.
- **Vergleichstabelle:** Bestand·Betreiber | Bestand·Anlage (Deeplink) | Neu·Betreiber |
  Neu·Anlage (Deeplink) | Match (NAP/km). Deeplink → schließt Statistik, zoomt, öffnet Popup.

**Verifiziert (browser, frischer Load):**
- Reihenfolge 'cee': Portfolio(3) → Betreiber(3) ✅ · 'enerparc': Portfolio zuerst ✅
- ✕-Button: Feld leer, Liste leer ✅
- Vermischung: ENERPARC (6 Treffer, 1 Ring) → CEE 20 km (0 Treffer) → **0 Ringe,
  Anzeigen-Button disabled, Filter aus** ✅
- ENERPARC-Analyse: **7 Ringe (nur betroffene)** statt ~50, 11 Bestandsanlagen ermittelt,
  Tabelle mit 13 Zeilen + korrekten Spaltenköpfen ✅
- Deeplink „Tornesch 1.3": Statistik zu, Zoom 14, Popup offen ✅
- Anzeigen: 5 Marker (Bestand + Neu) ✅
- Regression: reg 2019 → 16.747 ✅ · SE MS → 31.465 ✅ · F1-Suche ✅

**Revision:** iterations/V16_BetroffenheitRevision2.html. Nicht gepusht (Regel 4).

### V17 — Revisionspaket 3 Betroffenheits-Tab (04.09., User-Feedback)

**User-Befunde:** (1) „Betroffene Gesellschaften" zeigt nach Analyse manchmal keine/
*falsche* Werte (ENERPARC). (2) Ringe auf der Karte vollständig verifizieren. (3)
Erklär-Klapptext erweitern: Indikation-Charakter, Radius-Messverfahren, geplante Anlagen
ohne NAP → Geolokationsprüfung, Grenzen.

**Recherche + 3 gefundene Bugs (alle verifiziert, alle behoben):**
- **Bug A (User-Befund 1):** Gesellschaften-Zählung lief NUR über die Betreiber der
  NEU-Events. Bei Radius-Matches sind viele Treffer aber Neuanlagen von FREMDBetreibern
  nahe Portfolio-Bestandsanlagen — die betroffene Partei ist die Portfolio-Gesellschaft
  (Bestand), nicht der Fremdbetreiber. Zusätzlich: der Block lief VOR der _bffLastBestand-
  Berechnung → nutzte den Wert der Vor-Analyse. Fix: Zählung NACH Bestands-Berechnung
  verschoben + Bestands-Gesellschaften einbezogen. ENERPARC: jetzt **10 von 212**
  (vorher 3, teils 0).
- **Bug B (eigener Fehler beim V16-Patch):** halbfertiges `const gesFns = () => {` im
  Bundle → SyntaxError im ganzen Script-Block → init() lief nicht (Karte hing bei
  „Lade Daten…"). Beim Testen entdeckt, Ursache im Patch-Verlauf. Fix: Fragment entfernt,
  beide Script-Blöcke per node new Function() auf Syntax geprüft (OK/OK).
- **Ring-Verifikation (User-Befund 2):** Geometrie mathematisch geprüft — jeder
  Radius-Match-Event liegt innerhalb des gemeldeten Radius um einen betroffenen
  Referenzpunkt (Haversine-Nachrechnung im Browser): 20 km → max 19,8 km ✅,
  5 km → max 2,9 km ✅; 7 Ringe (20 km) / 1 Ring (5 km) um echte Bestandsanlagen,
  11 Bestands-Units exakt an Ring-Punkten. Kein Fehler gefunden.

**Erklärtext (User-Befund 3):** Neuer Klapptext „ℹ️ Wie funktioniert die
Betroffenheitsprüfung?": (1) Prüfverfahren — NAP-Gleichheit ODER Haversine-Umkreis
(2–20 km), Ringe zeigen das Suchfeld. (2) Geplante Anlagen: häufig noch **ohne
Netzanschlusspunkt** → Geolokationsprüfung (Abstand zum Bestands-Asset) ist hier der
verlässliche Weg; NAP-Match greift nach erfolgtem Anschluss. (3) Grenzen: Luftlinie statt
Netztopologie, keine Leiterwege/Trafos/Knotenauslastung, Falsch-Positive bei großen
Radien möglich → Ergebnistabelle + Karte prüfen. Kopf-Hinweis „Indikation, keine
rechtsverbindliche Auskunft" bleibt erhalten.

**Verifiziert (browser, frischer Load):**
- Karte lädt (31.116 Wind · 22.384 PV), Syntax-Check beide Blöcke OK
- ENERPARC 20 km: 14 Treffer · **10 von 212 Gesellschaften** + Namensliste ✅
- Ring-Geometrie 20 km (max 19,8) und 5 km (max 2,9) korrekt ✅ · Tabelle vorhanden ✅
- Erklärtext: alle Kernpunkte enthalten ✅

**Revision:** iterations/V17_BetroffenheitRevision3.html. Nicht gepusht (Regel 4).

### V18 — Revisionspaket 4 Betroffenheits-Tab (04.09., User-Feedback)

**User-Wünsche:** (1) Liste unter der Vergleichstabelle entfernen. (2) Spalte „MW"
(Anschlussleistung des NEU-Assets) vor der Match-Spalte. (3) Radius-Slider 2–50 km,
Default 20 km. (4) Bug-Check: Popup „Suchradius 20 km" statt Asset-Name an einzelnen
Bestands-Assets.

**Umsetzung:**
- **(1) Liste entfernt:** Die Trefferliste unter der Tabelle (`#bff-results`) wird nicht
  mehr befüllt (leer). Die Tabelle im Summary ist die einzige Ergebnisdarstellung.
- **(2) MW-Spalte:** Neu zwischen „Neu · Anlage (Update)" und „Match" — zeigt die
  Leistung des Neu-Assets mit korrekter Einheit (PV → MWp, Wind → MW).
- **(3) Slider:** min 2 / max 50 / Default 20, Label synchron; Erklärtexte (2 Stellen)
  auf „2–50 km" aktualisiert.
- **(4) Bug bestätigt und behoben:** Die Radius-Ringe hatten einen Tooltip „Suchradius
  N km". Bei überlappenden Ringen/Hover fing der Ring das Maus-Event ab, statt des
  darunterliegenden Asset-Markers → User sah „Suchradius 20 km" statt Assetname. Fix:
  Ringe mit `interactive: false` (keine Events, reine Visualisierung). Tooltip entfernt —
  der Radius steht im Slider und im Erklärtext, Redundanz nicht nötig.

**Verifiziert (browser, frischer Load, ENERPARC-Portfolio):**
- Slider 2–50, Default 20, Label „20 km" ✅
- Tabelle: Kopfzeile inkl. MW vor Match; Zeilen zeigen z. B. „3,26 MWp", „10,22 MWp",
  „5,01 MWp" ✅ · Liste darunter leer ✅
- 20 km: 14 Treffer · 7 Ringe, alle `interactive: false`, keine Tooltips ✅
- 50 km: 17 Treffer · 8 Ringe · Geometrie max 49,6 km ✅ · Gesellschaften-Box 11 von 212 ✅
- Syntax-Check beide Script-Blöcke OK (Node new Function)

**Revision:** iterations/V18_BetroffenheitRevision4.html. Nicht gepusht (Regel 4).

### V19 — Revisionspaket 5 Betroffenheits-Tab (04.09., User-Bug-Meldungen, Detailprüfung)

**User-Befunde:** (1) Betroffene Bestandsanlage scheint im „Anzeigen"-Modus nicht immer
auf der Karte auf. (2) Vereinzelt Ring an unbetroffener Stelle ODER auslösende Neuanlage
fehlt. Bitte Detailprüfung + Testdurchläufe + autonome Patches.

**Recherche (Code + 3 Browser-Testdurchläufe + Python-Datensimulation) — 3 Bugs gefunden:**
- **Bug 1 (User-Befund 1):** „Anzeigen"-Modus bildete die SCHNITTMENGE mit aktiven
  Filtern (Typ/Status/…). Bei aktivem Wind-Filter verschwanden PV-Treffer aus dem
  mSet → betroffene Assets fehlten. Fix: Anzeigen-Modus ERSETZT alle Filter
  (`filtered = allUnits.filter(u => mSet.has(u.m) || mSet.has('lid:'+u.lid))`).
- **Bug 2 (User-Befund 1, Haupteinfluss):** Marker-CLUSTERING. Bei 21 Treffern auf
  Deutschland-Zoom fasst Leaflet.markercluster Nachbarn in Cluster-Bubbles zusammen —
  die betroffene Bestandsanlage „verschwindet" optisch im Cluster, der Ring steht
  „leer" da. Fix: Clustering im Anzeigen-Modus deaktiviert (Einzel-Marker),
  danach wieder an.
- **Bug 3 (User-Befund 1, Verlassen):** Nach Klick auf „📋 Alle Anlagen anzeigen"
  blieb die KARTE im Anzeigen-Stand (21 Marker statt ~53.400) — showAllUnits baute
  nur die Tabelle, ohne applyFilters nachzuziehen. Fix: applyFilters()-Nachlauf in
  showAllUnits, wenn der Anzeigen-Modus aktiv war.
- **Befund 2 (Ring ohne Anlage / Neuanlage fehlt) — KEIN Code-Bug:** Datensimulation
  bestätigte: Jeder Ring-Zentrum hat eine reale Bestands-Unit (Distanz 0 m), jede
  Neuanlage ist im Bestand vorhanden (0 ohne Unit). Die Ursache für die
  User-Wahrnehmung ist Bug 2 (Clustering versteckt die Marker). Verifiziert nach
  Fix: „ringeOhneMarker: []" in allen Testdurchläufen (ENERPARC 20 km/7 Ringe,
  CEE 50 km/5 Ringe, Tornesch, NAP-Referenz).

**Verifiziert (browser, frischer Load, kompletter User-Pfad):**
- ENERPARC 20 km mit AKTIVEM Wind-Filter: 21/21 Marker sichtbar (vorher: PV-Treffer fehlten) ✅
- Alle 7 Ringe haben einen Marker am Zentrum ✅ · CEE 50 km: 15/15, 5 Ringe ✅
- Tornesch-Einzelanlage: 5/5 Marker ✅ · NAP-Referenz ohne Treffer: Button disabled,
  Karte unverändert ✅
- „Alle anzeigen" nach Anzeigen-Modus: 53.405 Marker (volle Karte) ✅
- SEE991807581772 im NAP-Index nicht mehr vorhanden (Datenstand 01.09.) — kein Bug
- Syntax-Check beide Script-Blöcke OK (Node new Function)

**Revision:** iterations/V19_BetroffenheitRevision5.html. Nicht gepusht (Regel 4).

### Abschluss-Status V19 (04.09., Abend)

**User-Freigabe erteilt:** „Mir gefällt das jetzt richtig, richtig gut … Bitte push diesen
Status auf GitHub und stell ihn live."
→ main-Commit + gh-pages-Deploy (Worktree-Methode) + Pages-Verifizierung (served-SHA =
local-SHA, Daten-JSON live OK, HTTPS 200). Alle „Nicht gepusht (Regel 4)"-Hinweise
V11–V19 sind damit gegenstandslos — Freigabe lag vor, Push + Deploy erfolgten am 04.09.
Betroffenheits-Tab damit in allen Punkten (F4+F6 + alle Revisionen bis V19) abgeschlossen;
nächstes offenes Projektthema: Punkt 9 (HTML-Kernfeld-Auswahl) mit User.

### V20 — Revisionspaket 6 (04.09., User-Laptop-Review, 30-Punkte-Plan, 7 Punkte)

**User-Befunde (Brain-Dump) und Umsetzung:**
1. **Popup-Datum kaputt** („/Date(1548892800000)/" statt Datum) — buildPopup gab rohen
   MaStR-Epochen-String aus. Fix: `dateFullFmt()` (nutzt bestehenden `_parseMaStrDate`-
   Cache) → Anzeige „MM.JJJJ" (Tag liegt im Epochen-String, Parser liefert y/m).
   Verifiziert: PVA Zaacko I → „01.2019".
2. **Topbar-Überlappung:** Wind/PV-Legende + „Stand:" überlagerten hinter den Buttons
   NAP-Gruppen/Statistik. Fix: `#topbar-meta` entfernt; Legende + Datenstand als neue
   Sektion „Karte & Datenstand" im Hinweise-Panel (disclaimer-panel). IDs `data-stand`,
   `m-dot-wind/pv` unverändert → JS-Befüllung läuft weiter. CSS-Klassen globalisiert
   (vormals `#topbar-meta`-scoped), Mobile-Media-Query bereinigt.
3. **Statistik-Fenster zu schmal** (8 Tabs mit horizontalem Scroll): Panel 700→820 px,
   Tabs kompakter (font 13→11.5 px, padding 9→8/2 px, gap 4→2). Verifiziert:
   scrollWidth 805 = clientWidth 805 → alle 8 Tabs ohne Scroll sichtbar. Tablet/Mobile
   unverändert (Tabs scrollen dort).
4. **Tabelle ohne Typ-Kennzeichnung + ENTFERNT fehlten komplett:** `paarRows` wurde nur
   aus NEU-Events befüllt. Fix: alle Events; neue schmale 1. Spalte mit 🆕 (neu) /
   🗑️ (entfernt), title-Tooltip, 11 px. Verifiziert: ENERPARC → 14× 🆕;
   „WP Buschmühlen"-Referenz (das einzige entfernte Asset der Historie) → 🗑️-Zeile.
   Nebenbefund: Doppel-Deklaration `const paarRows` (V17-Verschiebe-Rest) → Syntax-
   Fehler im Bundle, durch Node-Check gefangen und behoben.
5. (User „Viertens/Sechstens" = 1 Punkt) **Zubau-Charts: Wert-Labels senkrecht** —
   drawStackedBar/drawSingleBar (Balken) + drawRateChart/drawCumChart (Linien) auf
   `rotate(-PI/2)` umgestellt; PAD_T 16→46, H 290→320 (Kopffreiraum). Vision-Check:
   Labels senkrecht, vollständig lesbar, beide Modi (Anlagen/Leistung), beide Sub-Tabs.
6. **Gestrichelte Trendlinie entfernt** (PV/Wind-Einzelcharts): drawTrendLine-Aufrufe
   entfernt (Funktion bleibt im Code), Untertitel „mit Trendlinie" → „Balkendiagramm".
   Vision-Check: keine gestrichelte Linie mehr.
7. **Label-Überlappung Wind/PV** (Vision-Befund nach 1. Build): In drawRL/drawCL
   Wind-Labels links (seite 'L'), PV-Labels rechts (seite 'R') der Datenpunkte →
   Vision-Check: getrennt und lesbar (Rest: 2020 identische Werte 100 %, unvermeidbar).

**Regression grün:** Hauptsuche (Vorschläge), 53.405 Marker, Betroffenheit ENERPARC
(14 Treffer, 21/21 Anzeigen-Marker, „Alle anzeigen" → volle Karte), Zubau-Render in
allen Modi. Syntax-Check beide Script-Blöcke OK (2 Builds).

**Revision:** iterations/V20_BetroffenheitRevision6.html. Nicht gepusht (Regel 4 —
Freigabe für V20 steht aus).

### Live-Gang V20 (04.09., User-Freigabe erteilt)

- main: `2c35f84` (V20 + Doku), gh-pages: `0fe70b2` (Worktree-Deploy, CNAME unangetastet)
- Verifikation: Pages `built` · Live-SHA = lokal (`30c1fcd2cca1b7b8…`) · 22 V20-Marker
  in der Live-Datei · meta.json live (Stand 2026-09-01) · Deployment-SHA = gh-pages-HEAD
- DEPLOYMENT.md V20-Abschnitt ergänzt; PROJEKTSTAND V20-Status auf „LIVE" gesetzt

Damit sind V11–V20 vollständig live. Offen für künftige Sessions:
**Punkt 9** (HTML-Kernfeld-Auswahl, NAP-Korrelation — gemeinsam mit User entscheiden);
Deploy-Skript liegt als Vorlage in /tmp (flüchtig!) — bei nächster Gelegenheit als
`scripts/deploy_ghpages.sh` ins Repo aufnehmen, damit die Methode nicht verloren geht.

---

## F1 — NAP in die Suche integrieren

**Wunsch:** Suche erweitern — nicht nur Anlagen & Betreiber, sondern auch **Netzanschlusspunkte**
suchen (NAP-MaStR-Nr. `SAN…`, Netzbetreiber, evtl. NAP-Bezeichnung).

**Datenbasis (verifiziert):** 27.870 NAPs in `netzanschlusspunkte` (nap_mastr_nummer, netzbetreiber,
spannungsebene, regelzone, messlokation) + Join über lokation_id zu den Anlagen.

**Umsetzbarkeit: ✅ SEHR GUT (mittel Aufwand)**
- Die Karte hat die NAP-Daten currently NICHT im Frontend (nur Server-DB). Zwei Wege:
  a) **NAP-Index ins Frontend-JSON** (`assets/nap_index.json`): kompakte Liste
     `{nap: "SAN…", nb: Netzbetreiber, se: Spannungsebene, rz: Regelzone, n: Anzahl Anlagen, ids: [Einheiten]}` — ~27.870 Einträge ≈ 2–4 MB, akzeptabel für hostbare Version, zu groß für Single-File → nur hostbare Variante.
  b) NAP nur in Server-Auswertungen (Python/SQL), nicht im Frontend.
- Empfehlung: (a) mit Such-Integration analog Betreiber-Block (بلauer „⚡ Netzanschlusspunkt"-Block
  über den Anlagen-Treffern, Klick → Filter auf alle Anlagen dieser Lokation + Zoom).
- **Erweiterungsidee des Agents:** Beim NAP-Treffer zusätzlich Spannungsebene + Regelzone
  im Vorschlagsblock anzeigen (Nutzwert hoch, Daten liegen vor).

**Status: GEPLANT — 20-Punkte-Plan erstellt 03.09. (nach F2-Abnahme), wartet auf Freigabe**

**Verifizierte Datenlage (03.09., Live-DB):**
- 27.870 NAPs; suchbare Felder: nap_mastr_nummer (100 %), netzbetreiber (100 %),
  spannungsebene, regelzone, bilanzierungsgebiet (je 100 %), messlokation (14.360),
  NAP-Bezeichnung (14.695).
- Join Anlage→NAP via lokation_id: **50.316 von 53.533 In-Betrieb georef (94,0 %)**.
- Verteilung Anlagen/Lokation: meist 1, bis zu 219 Anlagen auf EINER Lokation
  (Großparks) — Klick auf NAP-Treffer zeigt daher oft ganze Parks. Max 10 NAPs/Lokation.
- Größenprüfung NAP-Index: **~3,3 MB** (nap, nb, se, rz, n, lid) — als eingebettetes
  JS-String-Literal im Single-File machbar (34,7 → ~38 MB), plus +0,8 MB lokation_id
  in einheiten.json (Feld `lid` je Anlage).

**20-Punkte-Plan F1:**
1. Export: `export_app.py` um Feld `lid` (lokation_id) je Anlage erweitern (+0,8 MB).
2. Neues Skript `scripts/export_nap_index.py`: erzeugt `dist/assets/nap_index.json`
   (NUR NAPs mit ≥1 verknüpfter georef In-Betrieb-Anlage; Felder nap/nb/se/rz/n/lid).
3. `bundle_singlefile.py`: nap_index.json als eingebettetes `<script>`-Const einbetten
   (Single-File-fähig, GZip-komprimiert base64 falls Size kritisch — messen).
4. Frontend: NAP-Index beim Laden dekomprimieren/einlesen (lazy — erst nach Datenladen).
5. Suchlogik: Suchfeld-Treffer erweitern — NAP-MaStR-Nr. (exakt/Präfix), Netzbetreiber-
   Name (substring), NAP-Bezeichnung falls im Index. Ranking: exakt > Präfix > enthält.
6. Vorschlagsblock „⚡ Netzanschlusspunkt" über den Anlagen-Treffern (blau, wie Betreiber-
   Block): NAP-Nr., Netzbetreiber, Spannungsebene, Regelzone, Anzahl Anlagen.
7. Klick auf NAP-Treffer → Filter auf alle Anlagen mit dieser lokation_id (via `lid`)
   + Zoom auf Bounding-Box der Treffer + Badge-Update.
8. Statistik-Panel: NAP-Treffer-Zeile im Betreiber-Tab-ähnlichen Block (nur Info, kein
   neuer Tab — schlanke Umsetzung).
9. Popup-Erweiterung: NAP-MaStR-Nr. + Netzbetreiber des Anschlusses (falls lokation_id
   matcht, Multi-NAPs kommagetrennt).
10. „ohne NAP"-Anlagen: Popup zeigt „kein NAP zugeordnet" (Ehrlichkeit, 6 %quote).
11. Bundle + Größe-Check (Ziel: Single-File < 40 MB).
12. Browser-Test: Suche nach echter SAN-Nummer → Treffer-Block erscheint.
13. Browser-Test: Suche nach Netzbetreiber-Namen (z. B. „Avacon") → NAP-Treffer + Anlagen.
14. Browser-Test: Klick auf NAP-Treffer → Zoom + gefilterte Marker + Badge korrekt.
15. Browser-Test: NAP ohne verknüpfte Anlagen (13,7 %) → NICHT im Index (dokumentieren).
16. F-Regression: F5-Statusfilter, F2-Spannungsebenenfilter, F5b/c-Deep-Links, Tabelle.
17. Doku: PROJEKTSTAND (V11-Absatz) + ROADMAP (Umsetzung + Pitfalls).
18. Revision `iterations/V11_NAPSuche.html` + human-share-Kopie.
19. Klickbare HTML an User (MEDIA:) + Änderungsliste.
20. User-Freigabe als Gate → F1 abgenommen.

**Umsetzung (03.09., alle 20 Punkte ✅):**
- Export: `lid` (lokation_id) je Anlage (53.915/65.659); neues `scripts/export_nap_index.py`
  → `dist/assets/nap_index.json` (27.078 NAPs mit ≥1 georef In-Betrieb-Anlage, 3,0 MB;
  792 NAPs ohne sichtbare Anlage bewusst ausgeschlossen). bundle_singlefile.py bettet
  NAP-Index als `window.__PVWIND_NAP__` ein; hostbare Variante lädt lazy per fetch.
- Frontend: `searchNAP()` mit Ranking exakt > Präfix > enthält > Netzbetreiber (max 5
  Treffer, grüne „⚡ NAP"-Blöcke über den Betreiber-/Anlagen-Treffern); `selectNAP()`
  → alle Anlagen der lokation_id + fitBounds + Suchfeld-Label. Popup: Zeilen „NAP" +
  „NAP-Netzbetreiber" (Multi-NAPs kommagetrennt; „kein NAP zugeordnet" wenn leer).
- Single-File: 38,7 MB (< 40-MB-Ziel ✅).
- Browser-Tests (verifiziert): SAN929299871095 exakt → Block mit 219 Anlagen ✅;
  „Avacon" → 5 NAP-Treffer, Klick → 57 Anlagen + Zoom + Label ✅; Popup zeigt
  „NAP SAN929299871095" + „NAP-Netzbetreiber 50Hertz Transmission GmbH" ✅ (Achtung:
  openPopup nur nach zoomToShowLayer — Marker war im Cluster); hostbar-Log: nap_index.json
  wird geladen ✅. Regression: F5 Planung 9.273 (alle bs=31) ✅, F2 MS 31.465 (alle
  enthalten MS) ✅, Reset 53.405 ✅, Tabelle NorthData+Geo+13 Spalten ✅.
- Performance-Hinweis: applyFilters + Rerender ist auf Pi5 ~20–30 s — TestsSplitten
  (Timeout 30 s in browser_console); kein App-Bug, gleiche Dauer wie V10.
- Revision: iterations/V11_NAPSuche.html. Nicht gepusht (Regel 4).

### V11b — Performance- + NAP-Vorschlags-Fix (2026-09-03, nach User-Feedback)

**User-Meldung:** (1) Alles langsamer (Suche, Löschen, Marker-Anzeige). (2) NAP-Vorschläge
erscheinen bei beliebigen Suchtexten bis ~4–6 Zeichen.

**Diagnose (Live-Messungen, browser_console):**
- **Hauptübeltäter NICHT die 38,7 MB:** `renderMarkers()` rief `buildPopup()` für ALLE
  ~53.400 Marker auf → **17,7 s reine Popup-Generierung pro applyFilters** (gemessen:
  24,2 s gesamt). Popups sind unsichtbar, bis ein Marker angeklickt wird — Pure Verschwendung.
- **NAP-Bug:** `searchNAP()` matchte Netzbetreiber-Substring ab 2 Zeichen → „av" traf
  „Bav…"/„Avacon…", „müll" traf „Müll…", d. h. praktisch jeder Text produzierte NAP-Blöcke.
- Secondary: `clearSearch` = applyFilters = 28,4 s (gleiche Ursache).

**Fixes:**
1. **Lazy-Popup:** Popup wird erst beim Öffnen erzeugt (`m._lazyPopup`), nicht mehr
   vorgeneriert. applyFilters: **24,2 s → 0,68 s (35×)**, clearSearch: 28,4 s → 0,49 s (58×).
2. **Cluster-Quirk:** `marker.openPopup()` zeigt bei cluster-verwalteten Markern ein
   LEERES Popup (Inhalt wird nicht geupdated) → bewusst `map.openPopup(m.getPopup())`
   nach `setLatLng(m.getLatLng())` (sonst Leaflet-Exception „Cannot read lat of undefined").
   Alle Aufrufstellen umgestellt: Marker-Klick, Geo-Deep-Link (`zoomToShowLayer`),
   flyToUnit-Successor.
3. **NAP-Ranking:** Netzbetreiber-Substring-Match erst ab **5 Zeichen** („avaco" ✅,
   „av" → 0 Treffer). SAN-Nummern bleiben ab 2 Zeichen suchbar.

**Regression (browser-verifiziert):** F5 Planung 9.273 alle bs=31 ✅ · F2 MS 31.465 ✅ ·
Popup erster Klick MIT INHALT (NAP + Spannungsebene-Zeilen da) ✅ · „av" → 0 NAP,
„SAN929299871095" → 1 NAP ✅ · applyFilters 681 ms, clearSearch 494 ms ✅.

**Revision:** iterations/V11b_PerformanceFix.html. Nicht gepusht (Regel 4).

### V11c — Datumsfilter-Fix (2026-09-03, nach User-Feedback)

**User-Meldung:** Filter Registrierungsdatum/Inbetriebnahmedatum liefern 0 Anlagen.

**Ursache:** `reg`/`inb` sind MaStR-Epochen-Strings `/Date(1548892800000)/`. Die
Jahres-Dropdowns wurden mit dem F5-Fix normalisiert gebaut (Optionen „2019"…„2026"),
aber `applyFilters()` UND der Duplikat-Filterblock in `showAllUnits` schnitten
direkt `substring(0,4)` → `'/Dat'` — matchte nie. Fehlerklasse: Filter-Code-Duplikation
(dieselbe Logik an 2 Stellen, Fix nur an einer eingepflegt worden).

**Fix:**
1. Zentrale Normalisierer `dateYear(v)` / `dateMonth(v)` mit Map-Cache (`_dateCache`,
   Rohstring → {y, m}) — erkennt `/Date(...)`-Epochen UND ISO `YYYY-MM-DD`.
   Cache wichtig: sonst 65k Regex-Auswertungen pro Filterwechsel.
2. Beide Filterstellen (applyFilters + showAllUnits-Duplikat) nutzen die Helfer.
3. Tabellen-Sortierung reg/inb: sortiert jetzt über `dateYear+dateMonth` (vorher
   sortierte Epochen-Strings lexikalisch = falsche Reihenfolge).
4. Zubau-Chart (renderZubau): Jahre via `dateYear()` — vorher landete `'/Dat'` als Jahr
   im Chart.

**Verifiziert (browser):** inb-Jahr 2023 → 2.566 Anlagen, alle korrekt ✅ · inb 2023+03 →
201 ✅ · reg-Jahr 2019 → 16.747 ✅ · reg 2019+07 → 1.698 ✅ · Tabelle zeigt ISO-Daten ✅ ·
Zubau-Chart Jahre 2019–2024, kein '/Dat' ✅ · Regression: F5 (9.273) ✅, F2 (31.465) ✅,
applyFilters 477 ms ✅.

**Revision:** iterations/V11c_DatumsfilterFix.html. Nicht gepusht (Regel 4).

**Wunsch:** Neuer Karten-Filter: Anlagen nach **Spannungsebene ihres Netzanschlusspunkts** filtern.
(F2 — UMGESETZT + von User abgenommen, siehe unten.)

**Wunsch-Details F2 (historisch):**

**Datenbasis (verifiziert 03.09.):** 7 Ebenen, 100 % der 27.870 NAPs kategorisiert:
Mittelspannung 22.297 (80 %) · Niederspannung 2.002 · Hochspannung 1.868 · Umspann HS/MS 1.158 ·
Umspann MS/NS 370 · Höchstspannung 166 · Umspann HöS/HS 9.
**Korrelationsquote Einheit→NAP: 93,7 % (51.123 von 54.544 Einheiten; Wind 97,5 %, PV 88,4 %).**

**Umsetzbarkeit: ✅ SEHR GUT (klein-mittlerer Aufwand)**
- Vorgehen: beim Export ein `se`-Feld pro Einheit berechnen (Join lokation_id → NAP, 7 Werte);
  Einheiten ohne NAP bekommen `se: null` → Filter-Option „keine Angabe (Register)".
- Frontend: 8. Filter-Dropdown (7 Ebenen + „Alle" + „keine Angabe"), analog Bundesland-Filter.
- Achtung Datenpflege: Höchstspannung hat nur 166 NAPs, aber 3.596 Wind-Anlagen (Offshore-Cluster);
  Umspann HöS/HS hat 9 NAPs (Randgruppe, Leer-Feld trotzdem listen wie bei Kritis-Klassen).
- **Erweiterungsidee:** zusätzlich Regelzone (4 Werte: TenneT/50Hertz/Amprion/TransnetBW) als
  9. Filter — gleiches Muster, gleicher Export-Schritt, minimaler Zusatzaufwand.

**Status: UMSETZUNG FREIGEGEBEN (03.09., „bringe die Doku auf as-built und starte mit dem
nächsten Arbeitspaket") — UX-Variante a) Toggle „NAP-Cluster zeigen" + Variante b) NAP-Panel
im F1-Suchtreffer kombiniert; Details im 20-Punkte-Plan unten.**

### 📋 20-Punkte-Plan F3 — NAP-Gruppenansicht (opt-in)

| # | Phase | Punkt |
|---|---|---|
| 1 | Daten | Gruppen aus `lid` bauen: lokation_id → {Anlagen[], NAP-Daten, Summe MW} beim Laden (nur georef In-Betrieb, ~27k Gruppen) |
| 2 | Daten | Größen-Check: kein neues JSON nötig — Gruppen aus einheiten.json + nap_index.json zur Laufzeit ableiten |
| 3 | Export | prüfen, ob nap_index.json nb/rz/se je lid liefern kann (Multi-NAP: Pipe) |
| 4 | UI | Toggle „⚡ NAP-Gruppen" in Topbar (opt-in, localStorage, Default AUS) |
| 5 | UI | Bei AUS: keine Änderung am aktuellen Verhalten (Regression-sicher) |
| 6 | Kartenlogik | Bei AN: Marker derselben Lokation bekommen Gruppenring (divIcon-Erweiterung) ODER Gruppen-Overlay-Cluster |
| 7 | Kartenlogik | Klick auf Gruppe → NAP-Panel (rechts) mit NAP-Daten + Anlagenliste (Name, MW, Typ, Betreiber) |
| 8 | Panel | Anlagenliste klickbar → flyTo + Popup (nutzt Lazy-Popup-Pfad V11b) |
| 9 | Panel | Chunk-Rendering für Großgruppen (219 Anlagen — Muster V7b-Tabelle) |
| 10 | Panel | „Zoom auf Gruppe"-Button (fitBounds der Gruppenmarker) |
| 11 | F1-Verzahnung | NAP-Suchtreffer-Klick (V11) öffnet dasselbe Panel statt nur Zoom |
| 12 | Statistik | Panel-Kopf: NAP-Nr, Netzbetreiber, Ebene(n), Regelzone, X Anlagen, Y MW |
| 13 | Edge-Cases | Anlagen ohne lid/nid → keine Gruppe, Panel zeigt Hinweis |
| 14 | Edge-Cases | Multi-NAP-Lokationen (479): alle NAPs im Panel mit je Ebene/Betreiber |
| 15 | Performance | Gruppen-Index lazy beim ersten Toggle-Aktivieren bauen (nicht beim Laden) |
| 16 | Performance | applyFilters bleibt <1 s — Gruppenring nur auf sichtbare Marker (Zoom-Callback) |
| 17 | Test | Toggle an/aus, Gruppe klicken, 219er-Gruppe, Multi-NAP, Panel-Links |
| 18 | Test | Regression: F5/F2/F1-Suche/Datumsfilter/Tabelle/Deep-Links |
| 19 | Doku | ROADMAP as-built + PROJEKTSTAND V12 |
| 20 | Freigabe | klickbare HTML im Chat → User-Prüfung → Gate |

**Status: UMGESETZT (03.09., alle 20 Punkte ✅) — wartet auf User-Freigabe**

**Umsetzung (V12, 03.09.):**
- Toggle „⚡ NAP-Gruppen" in Topbar (grün aktiv, localStorage `pvw_nap_groups`, Default AUS,
  Punkt 4/5) — bei AUS exakt das bisherige Verhalten.
- Gruppen-Index lazy beim ersten Aktivieren gebaut (Punkt 15): lid → {units, naps[]};
  6.258 Gruppen-Badges (Gruppen ≥2 Anlagen) als eigener LayerGroup über der Karte (Punkt 6),
  grüne Badges mit Anlagenzahl, Klick → Panel.
- NAP-Panel rechts (Punkt 7): Titel (SAN bzw. „X Anschlusspunkte" bei Multi-NAP),
  Sub „N Anlagen · Y MW", NAP-Infos je Anschlusspunkt (SAN, Ebene, Regelzone, Netzbetreiber —
  Punkt 14: Multi-NAP-Lokationen listen ALLE NAPs, 470 Gruppen mit 2+ NAPs),
  ⚠-Warnung bei mehreren Betreibern am Anschlusspunkt (Punkt 12),
  Zoom-Button (fitBounds, Punkt 10), Anlagenliste sortiert nach MW absteigend mit
  Chunk-Rendering (40er-Blöcke, Punkt 9), Zeilen-Klick → flyTo + Lazy-Popup (Punkt 8).
- F1-Verzahnung (Punkt 11): NAP-Suchtreffer-Klick öffnet bei aktivem Toggle dasselbe Panel.
- Performance (Punkt 16): Panel-Öffnung 28 ms auch bei 219 Anlagen; applyFilters 401 ms
  unverändert; Badges-Layer unabhängig vom Marker-Filter.
- Größencheck (Punkt 2/3): kein neues JSON nötig — Gruppen zur Laufzeit aus
  einheiten.json + nap_index.json ableitbar (nap_index.json liefert nap/lid/nb/se/rz je Entry;
  Multi-NAPs = mehrere Entries je lid). Single-File bleibt 38,7 MB.

**Verifiziert (browser):** Toggle an/aus + localStorage ✅ · 6.258 Badges ✅ · 219er-Gruppe
(He Dreiht): Panel 28 ms, 219 Zeilen, 548 MW, 51 Betreiber-Warnung ✅ · Multi-NAP lid
4023449: „2 Anschlusspunkte", beide SANs gelistet ✅ · Zeilen-Klick → Popup MIT INHALT ✅ ·
F1-Klick → Panel ✅ · Regression F5 (9.273) / F2 (31.465) / Datum (2.566) / Deep-Links ✅ ·
applyFilters 401 ms ✅.

**Revision:** iterations/V12_NAPGruppenansicht.html. Nicht gepusht (Regel 4).

**Umsetzbarkeit: ✅ GUT (mittel Aufwand, UX entscheidet)**
- Datenlagen identisch F1/F2 (Join vorhanden, Multi-NAP-Lokationen: 479).
- Vorschlag UX (2 Varianten, bei Umsetzung abstimmen):
  a) **Toggle „NAP-Cluster zeigen":** Farbring/Icon um Anlagen-Marker derselben Lokation
     (Lokation-Gruppe), Klick auf Ring → Popup mit allen Assets des Knotens (Name, MW, Typ, Betreiber)
     + NAP-Daten (SAN-Nr, Spannungsebene, Regelzone, Netzbetreiber).
  b) **NAP-Panel:** Klick in Suche (F1) öffnet Panel „Anschlusspunkt SAN… — X Anlagen — Y MW"
     mit klickbarer Anlagenliste (fit-bounds).
- Opt-in wie gewünscht: Toggle in der Topbar, Zustand in localStorage, Default AUS.
- Offshore-Warnung: Cluster mit 219 Einheiten (He Dreiht) — Popup braucht Chunk-Rendering
  (Muster aus Alle-Anlagen-Tabelle V7b bereits vorhanden, wiederverwendbar).

**Status: GEPLANT — wartet auf Freigabe**

---

## F4 — Betroffenheits-Match: neue Anlagen vs. bestehende Anlagen/Betreiber (Zubau-Alarm)

**Wunsch:** Aus den abgerufenen Daten ein **Match** ermöglichen: neu hinzugekommene Anlagen
im Datensatz mit einem konkreten Asset oder Betreiber abgleichen — hat der Betreiber
„Betroffenheit", d. h. muss er sich den **Netzanschlusspunkt künftig teilen**?

**Datenbasis (verifiziert):** Snapshot-System vorhanden (Delta-Berechnung `added_assets` /
`removed_assets` mit vollen Asset-Dicts, getestet 29.08.→01.09. mit +19 Anlagen). NAP-Join 93,7 %.

**Umsetzbarkeit: ✅ GUT — KERNIDEE STIMMT, mit 2 technischen Anmerkungen**
- **Mechanik:** nach jedem Pipeline-Lauf (Cron existiert: 1./15.) existiert das Delta
  (neu/entfernt). Für jede neue Anlage: `lokation_id` → alle bestehenden Anlagen am selben
  NAP → Betreiber-Vergleich (eigener Betreiber = kein Match; fremder = potenzielle
  Betroffenheit). Ausgabe pro Betreiber: „N neue Anlagen an M Ihrer Anschlusspunkten".
- **Anmerkung 1 (fachlich wichtig):** Neuanlage am GLEICHEN NAP heißt nicht automatisch
  „Netz teilen" — ein NAP ist ein Netzknoten, hinter dem größere Netze hängen. Die
  Funktion liefert eine **Betroffenheits-INDIKATION** („gleicher Anschlussknoten"), keine
  rechtsverbindliche Auskunft. In der UI so kennzeichnen.
- **Anmerkung 2 (Datenlage):** Die Registrierung im MaStR erfolgt teils JAHRE nach realer
  Inbetriebnahme; „neu im Register" ≠ „neu ans Netz". Empfehlung: zwei Match-Modi —
  „neu registriert" (DatumLetzteAktualisierung/EinheitRegistrierungsdatum) und
  „neu in Betrieb" (InbetriebnahmeDatum im Fenster).
- **Erweiterungsidee des Agents (relevant für F4):** Zusätzlich **Leistungs-Betroffenheit**:
  Summe MW der Neuanlagen am NAP vs. bestehende MW am NAP („+45 MW an Knoten X, bestehend 120 MW")
  — das ist der Wert, der Netzbetreiber-Engpass-Diskussionen wirklich spiegelt.
  Daten liegen vollständig vor (bruttoleistung_mw je Einheit).

**Status: GEPLANT — wartet auf Freigabe (dann: Konzept-Detail mit UI-Skizze)**

---

## F5 — Filter nach Betriebs-Status (FREIGEGEBEN mit erweiterter Abruf-Logik)

**Wunsch (final, 03.09.):** Alle 4 Status-Werte — **In Planung / In Betrieb / Vorübergehend
stillgelegt / Endgültig stillgelegt** — werden abgerufen und die **Karte wird danach
filterbar** (User-Entscheidung: stillgelegte/planned Anlagen kommen auf die Karte).

**Fakten-Verifikation (03.09., live bei BNetzA abgefragt):**
- Der Status-Katalog der API hat GENAU 4 Werte (nicht „In Bau" — das gibt es im MaStR nicht):
  | ID | Status | Wind (≥100 kW) | PV (≥0,5 MWp) |
  |---|---|---|---|
  | 31 | **In Planung** | 8.193 | 1.189 |
  | 35 | **In Betrieb** | 32.155 | 22.389 | ← aktueller Datensatz
  | 37 | **Vorübergehend stillgelegt** | 88 | 15 |
  | 38 | **Endgültig stillgelegt** | 3.010 | 52 |
- Aktueller Datensatz enthält NUR „In Betrieb" (Wind-Filter in fetch fix auf 35).
- **⚠️ Konsequenz für F5:** Um In-Planung/Stillegungen zu zeigen, muss die **Abruf-Logik
  erweitert werden** (fetch_v2: Status-Filter entfernen bzw. alle 4 Status ziehen).
  Das vergrößert den Datensatz um ~12.500 Anlagen (8.193+1.189+88+15+3.010+52) →
  DB/Raw wachsen, Karte nur falls gewünscht. Einheiten in Planung haben oft noch
  keine Geokordinaten/keinen NAP.

**Umsetzbarkeit: ✅ GUT (klein-mittlerer Aufwand, Datenvolumen-Nachweis nötig)**
- Vorgehen: (1) fetch_v2 erweitern (Status-Liste 31/35/37/38 — kein breaking change, nur ADD),
  (2) import_v2: Status in `einheiten_raw` schon da (BetriebsStatusName), Kern-Export bekommt
  `st`-Feld, (3) Frontend-Filter „Status" mit 4 Optionen + „Alle", Default „In Betrieb"
  (Kompatibilität mit heutiger Karte).
- **Abstimmungspunkt mit User:** Sollen stillgelegte Anlagen auf die KARTE? (Meine Empfehlung:
  ja, mit ausgegrautem Marker — „Endgültig stillgelegt" ist für Auswertungen wertvoll,
  z. B. Repowering-Potenzial-Analyse: alte Standorte × moderne Turbinen.)
- **Erweiterungsidee:** Repowering-Report als separates Statistik-Tab (stillgelegt+Neubau
  am selben Standort/Cluster) — Recherche nötig, ob Standort-Identifikation zuverlässig
  möglich ist (Koordinaten-Nähe + Betreiber + Lokation).

**Status: FREIGEGEBEN (03.09.) — 20-Punkte-Plan siehe unten; Umsetzung als ERSTER Schritt**
(Reihenfolge-Änderung ggü. erster Empfehlung: F5 vor F2, weil der Datensatz-Fetch erweitert
werden muss — F2 profitiert vom erweiterten Datensatz im selben Zug.)

### 📋 20-Punkte-Plan F5 — Status-Filter (Mehrfachauswahl, Default „In Betrieb")

**User-Anforderungen (03.09.2., bindend):**
- 4 Status: In Planung (31), In Betrieb (35), Vorübergehend stillgelegt (37), Endgültig stillgelegt (38)
- Karte filterbar nach Status; **Default = nur „In Betrieb"** (wie bisher)
- **Nicht Einzel-Exclusive: Mehrfachauswahl** — Kombinierbarkeit mit allen bestehenden Filtern
- Abgleich der Entfernung: neue Anlagen kommen via fetch in den Datensatz (Δ ~12.547 Anlagen)
- Doku-Update + Doku-Prüfung; klickbare HTML hier in den Chat; Revision nach iterations/

| # | Phase | Punkt | Detail |
|---|---|---|---|
| 1 | Recherche | Status-Katalog | ✅ erledigt (4 Werte live verifiziert: 31/35/37/38) |
| 2 | Recherche | Volumen je Status | ✅ erledigt (Wind: 8193/32155/88/3010; PV: 1189/22389/15/52) |
| 3 | Recherche | API-Filterbarkeit pro Status | ✅ erledigt (Betriebs-Status~eq~<id> funktioniert je Wert) |
| 4 | Recherche | Feldbelegung Nicht-InBetrieb (Koordinaten? NAP?) | prüfen an Stichproben (In-Planung-Anlagen oft ohne Geo/NAP) |
| 5 | Planung | fetch_v2 erweitern | 4 separate Abrufe (31/37/38 zusätzlich, 35 bleibt) → data/raw_v2/{wind,pv}_status{31,37,38}.json ODER gemeinsame Liste; entscheidung: separate Dateien (leichteres Delta, kein Risiko für Bestandsdaten) |
| 6 | Planung | import_v2 erweitern | UPSERT von Zusatz-Status-Einheiten in einheiten_raw (mastr_nummer PK bleibt, energietraeger_id + betriebs_status_id als Felder schon da); KEIN Löschen bestehender Datensätze (Regel 1!) |
| 7 | Planung | Kern-Export (export_app) | Einheiten aller 4 Status exportieren, kompaktes Feld `st` (Betriebs-Status-ID); Karte muss 4 Status unterscheiden können |
| 8 | Planung | UI-Konzept Filter | Mehrfachauswahl-Muster: 4 Checkboxen (In Planung/In Betrieb/Vorüb. stillg./Endg. stillg.) in einem Filter-Block „Status"; Default: nur „In Betrieb" ✓; kombinierbar mit Typ/BL/Art/Leistung/… |
| 9 | Planung | Farb-/Marker-Konzept | In Betrieb: wie bisher; In Planung: gestrichelter Outline-Marker (z. B. blau); Vorüb. stillg.: orange; Endg. stillg.: grau — Legende im Disclaimer/Meta-Panel |
| 10 | Planung | Statistik-Integration | Zähler „Anzahl"-Badge: zählt nur aktive Status-Auswahl; Statistik-Tabs bleiben In-Betrieb-lastig? → Entscheidung: Tabs aggregieren über AKTIVE Filterauswahl (konsistent zur Karte) |
| 11 | Umsetzung | fetch_v2.py erweitern | Code + Test-Lauf gegen Live-API |
| 12 | Umsetzung | import_v2.py erweitern | Code + Test-Import (Ziel: 54.544 + ~12.547 Zusatz-Records UPSERT) |
| 13 | Umsetzung | export_app.py erweitern | `st`-Feld im einheiten.json + Status-Counter in meta.json |
| 14 | Umsetzung | src/index.html — UI | Filter-Block „Status" (4 Checkboxen), applyFilters() erweitert, Marker-Farben, Legende |
| 15 | Umsetzung | src/index.html — Logik | Default-Zustand (nur 35), Mehrfach-Kombis, Konsistenz Badge ↔ Marker-Count |
| 16 | Umsetzung | bundle_singlefile.py | prüfen: Status-Feld im Single-File automatisch dabei (Daten eingebettet) |
| 17 | Prüfung | Filter-Logik (Browser) | jede Kombination 4 Status × Typ/BL/Art: Badge-Zahl == Cluster-Count |
| 18 | Prüfung | Datenqualität | Volumen-Abgleich: DB-Records je Status == API-Total je Status; 0 Verlust bei In-Betrieb-Bestand (54.544 unverändert) |
| 19 | Prüfung | Doku-Update + Doku-Prüfung | PROJEKTSTAND, README (Filter-Liste), update.md, ROADMAP-Status; Kontrolle architektur.md/datenmodell.md/statistik.md auf Veraltet-Stellen |
| 20 | Prüfung | Revision sichern + Lieferung | klickbare HTML → iterations/V9_StatusFilter.html + MEDIA: in Chat; User-Freigabe = Gate zu F2 |

## F6 — Betroffenheit auch bei ENTFERNTEN Anlagen (F4-Erweiterung)

**Wunsch:** Der Betroffenheits-Abgleich (F4) soll auch **Entfernungen** abbilden —
neue UND entfernte Anlagen gegenüber bestehenden Anlagen/Betreiber.

**Datenbasis (verifiziert):** `compute_delta()` liefert bereits `removed_assets` mit vollen
Asset-Dicts (V4b-Test: 1 entfernte Wind-Anlage korrekt erkannt). Snapshots sind unveränderlich.

**Umsetzbarkeit: ✅ GUT — baut direkt auf F4 auf**
- Entfernte Anlage am NAP X mit Betreiber B → Betroffenheits-Event „Anlage weg vom Knoten"
  (betrifft denselben Betreiber-Kreis: eigene Anlage weg = Bestandsverlust; fremde Anlage weg =
  möglicherweise Kapazitätsfreigabe am Knoten — für Netzbetreiber-Diskussionen interessant).
- Vorschlag Datenmodell: Tabelle/Vier-Felder-Matrix pro (NAP, Betreiber, Event-Typ
  [neu/entfernt], MW) pro Update-Zyklus → „Betroffenheits-Feed" je Betreiber.
- **Wiederverwendungs-Hinweis:** Diese Struktur ist generisch — sie unterstützt später auch
  andere Event-Typen (Statuswechsel In Betrieb→Stillgelegt, Leistungsänderung) ohne Schema-Bruch.

**Status: GEPLANT — wartet auf Freigabe (Umsetzung nach/nit F4)**

---

## Umsetzungs-Reihenfolge (Empfehlung des Agents, freigabepflichtig)

1. **F2 Spannungsebenen-Filter** (+ optional Regelzone) — klein, hoher Nutzwert, Kern-Export-Erweiterung nötig (Punkt-9-Thema!)
2. **F5 Status-Filter** — benötigt fetch-Erweiterung (Datenvolumen +12.5k, Risiko gering), User-Entscheidung: stillgelegte auf Karte?
3. **F1 NAP-Suche** — mittlerer Aufwand, hostbare-Version-first (Single-File wird zu groß)
4. **F3 NAP-Gruppenansicht** — baut auf F1 auf (gleiche Datenstruktur)
5. **F4+F6 Betroffenheits-Match (neu + entfernt)** — größtes Feature, dafür vorhandenste Datenbasis; Konzept-Detail nach Freigabe

**Übergreifende Abhängigkeit:** F1–F3 brauchen NAP-Daten im Frontend → Kernfeld-Export-
Diskussion (Punkt 9, GRUNDSATZENTSCHEIDUNG.md) sollte VOR der Umsetzung stattfinden.
F4/F6 sind reine Server-Funktionen (Python/SQL) — könnten auch OHNE Frontend-Änderung
als Report laufen (z. B. als Teil des Cron-Reports oder eigenes HTML).

---

## Log

- **2026-09-03:** Roadmap angelegt (F1–F6 aus User-Braindump). Fakten verifiziert:
  Status-Katalog 4 Werte (kein „In Bau"), Nicht-InBetrieb-Volumen 12.547 Anlagen,
  NAP-Korrelation 93,7 %, Spannungsebenen 7, Multi-NAP 479.
- **2026-09-03 (Braindump 2):** User-Freigaben eingearbeitet: F5 (alle 4 Status, Karte
  filterbar), F2, F1 freigegeben; F4 zur **Betroffenheitsanalyse** konkretisiert
  (Trigger: Cron-Update → Match neuer/entfernter Assets vs. eigener Anlage/Betreiber/NAP;
  Match-Typen: NAP-Gleichheit ODER Umkreis **2–20 km** — Begründung Leitungstrasse an
  anderem NAP; Modi „neu registriert"/„neu in Betrieb" + Leistungsbetroffenheit; F6 in F4
  integriert). Arbeitsablauf-Vorgabe dokumentiert: je Feature 20-Punkte-Plan
  (Recherche→Planung→Umsetzung→Prüfung) + Doku-Update & Doku-Prüfung + klickbare HTML im
  Chat + User-Freigabe als Gate + jede HTML-Revision lokal in iterations/ sichern.
- **2026-09-03 (F5 UMGESETZT):** 20-Punkte-Plan abgearbeitet. Punkte 1–3 ✅ (Research),
  4 ✅ (Georef-Quote Zusatz-Status 70–99 %), 5–10 ✅ (Planung, Entscheidungen dokumentiert),
  11 ✅ fetch_v2 `--extended-status` (8 Dateien, Volumen exakt = API-Totals; 2 Call-Site-Bugs
  gefunden & behoben: fehlender status_id-Parameter bei Wind- und PV-Zusatz-Abrufen),
  12 ✅ import UPSERT mit BetriebsStatusId-Vergleich (67.116 Records, 0 Dubletten),
  13 ✅ Export: alle Status aus einheiten_raw, bs-Feld uniform, status_counts in meta.json
  (65.659: 53.405/9.273/66/2.915 — Differenzen vollständig aufgeklärt: 128+2 Wind <100 kW
  verworfen nach to_mw, konsistent zum Kern-Filter), 14–15 ✅ UI + Logik, 16 ✅ Bundle
  (33,5 MB), 17 ✅ 10 Browser-Kombis + Bug-Fix (0 gewählte Status → 0 Anlagen), 18 ✅
  Volumen-Abgleich, 19 ✅ PROJEKTSTAND/ROADMAP aktualisiert, README/update.md geprüft
  (Filter-Liste dort erst nach User-Freigabe finalisieren), 20 ✅ Revision gesichert
  (iterations/V9_StatusFilter.html) + HTML an User (MEDIA:). Nächster Schritt nach
  Freigabe: F2 Spannungsebenen-Filter.
- **2026-09-03 (F5b — User-Feedback):** Zwei Ergänzungen nach User-Review umgesetzt:
  (1) Tabellen-Übersicht „Alle Anlagen anzeigen" um **Betreiber-Deep-Link** (Klick →
  selectBetreiber, wie Statistik-Panel) und **Koordinaten-Spalte mit Deep-Link** (Klick →
  Karte zoomt via clusterGroup.zoomToShowLayer + öffnet Popup) erweitert.
  (2) User-Beobachtung „In-Planung-Anlagen mit Inbetriebnahmedatum" aufgeklärt:
  **KEIN MaStR-Datenfehler** — 0/9.273 In-Planung-Anlagen haben ein inb-Datum (raw verifiziert);
  Ursache war Bug #3: showAllUnits() wendete den Status-Filter nicht an → Tabelle zeigte
  In-Betrieb-Anlagen. Gefixt. Weitere Fixes: reg-Spalte zeigt jetzt geparste Daten statt
  /Date(...)-Rohstring (Bug #4), Inbetriebnahme-Jahres-Dropdown bereinigt (Bug #5,
  „/Dat"-Option), Marker-Lookup _unitMarkers statt Cluster-Iteration (Bug #6-Art).
  Revision: iterations/V9b_StatusFilter_DeepLinks.html. Alle Deep-Links browser-verifiziert
  (Popup öffnet, Betreiber-Suche greift, Tabelle filtert korrekt).
- **2026-09-03 (F5c — Tabelle final, AS-BUILT):** User-Feedback umgesetzt:
  (1) Tabellen-Spalte „Betreiber" ist jetzt **externer NorthData-Deep-Link** (target=_blank,
  gleicher Slug-Mechanismus wie im Popup: '＆'(U+FF06)→'&', Leerzeichen→'+', URL-encode;
  Live-Check: alle Test-URLs HTTP 200). Header zeigt „Betreiber ↗".
  (2) **MaStR-Nr.-Spalte entfernt** (war funktionslos; MaStR-Nr. bleibt im Popup der Anlage).
  (3) Koordinaten-Deep-Link (📍 → Karte zoomt + Popup) **beibehalten** wie zuvor.
  Sortierung Betreiber-Spalte getestet (th data-sort=ab, greift weiter). Popup-NorthData-Links
  unverändert intakt. Revision: iterations/V9c_Tabelle_NorthData_MaStRWeg.html.
  Tabellen-Header (As-Built): # | Name | Typ | Art | MW | Bundesland | Landkreis | Gemeinde |
  Registriert | Inbetriebnahme | Betreiber ↗ (NorthData, extern) | Koordinaten (📍, Karte+Popup).
  **Arbeitspaket F5 (Status-Filter + Tabellen-Deep-Links) von User abgenommen.**
- **2026-09-03 (F5-Pipeline-Härtung, nach User-Prüfauftrag):** Verifiziert, dass der
  Cronjob (79229dc1690d, 1./15. 03:00) die F5-Status-Daten korrekt aktualisiert.
  **Befund: Lücke gefunden & geschlossen** — `pipeline2_update.sh` rief `fetch_v2.py`
  OHNE `--extended-status` auf → die 6 Status-Dateien wären beim 15.09.-Lauf nicht
  aktualisiert worden (Status-Daten eingefroren). Fix: Flag im Skript (Pflicht, mit
  Begründungs-Kommentar) + erweiterter Report (F5-Status-Zähler je Lauf) + `update.md`
  (Warnblock Pflicht-Flag, Cron-Beispiel auf pipeline2_update.sh umgestellt, Schritt-1-
  Befehl mit Flag). Bash-Syntax geprüft, Report-SQL gegen Live-DB getestet
  (Planung 9.382 / Vorüb.stillg. 103 / Endg.stillg. 3.062).
  Bekannte Grenze (akzeptiert): Wind/PV-Abgang (Anlage registriert in DB, taucht in
  keinem der 4 Status-Feeds mehr auf) bleibt in einheiten_raw stehen — UPSERT ist
  additiv, es gibt keinen Status „nicht mehr gelistet". Auswirkung minimal (Anlage
  wäre in einem der 4 Status gelistet, da MaStR-Anlagen einen Status haben).

## F2 — Spannungsebenen-Filter (20-Punkte-Plan, 03.09., UMGESETZT + von User abgenommen: „Sehr gut, dann lass uns zum nächsten Arbeitspaket kommen")

**Verifizierte Datenlage (03.09., Live-DB):**
- 7 Spannungsebenen in `netzanschlusspunkte`: Mittelspannung 22.297 · Niederspannung 2.002 ·
  Hochspannung 1.868 · Umspann HS/MS 1.158 · Umspann MS/NS 370 · Höchstspannung 166 ·
  Umspann HöS/HS 9.
- Join-Quote AUSGEZEICHNET: **53.025 von 53.533** georef In-Betrieb-Anlagen (99,05 %) haben
  eine Spannungsebene — der NAP-Ausbau der letzten Wochen zahlt ein.
- Sonderfall: 173 Lokationen mit >1 VERSCHIEDENER Spannungsebene (z. B. Mittel- UND
  Niederspannung) → Anzeige als kombinierte Zuordnung, Filter matcht wenn EINE der
  Ebenen gewählt ist.
- 509 georef In-Betrieb-Anlagen ohne NAP → im Filter „ohne Angabe" zusammengefasst.

**Plan:**
1. ✅ Datenlage verifiziert (oben).
2. `export_app.py`: SELECT um LEFT JOIN auf `netzanschlusspunkte` erweitern
   (`GROUP_CONCAT(DISTINCT spannungsebene)` je Lokation) → neues Unit-Feld `se`.
3. Mehrfach-Ebenen (173 Lokationen): `se` enthält Pipe-getrennte Liste; UI matcht
   Teilmenge (Checkbox gewählt = Ebene in Liste enthalten).
4. `export_app.py` main(): `build_units` Mapping + `meta.json` um `spannungsebenen`-
   Verteilung erweitern (für Statistik-Tab).
5. Export-Lauf + Verifikation: 99 % Quote bestätigt, `se`-Feld sauber befüllt,
   Dateigröße im Rahmen (einheiten.json wächst moderat).
6. `src/index.html` Toolbar: Dropdown „Spannungsebene" (7 Ebenen + „ohne Angabe"),
   sortiert nach Häufigkeit, Titel-Tooltip mit Definitionen.
7. `applyFilters()`: `se`-Filter logik (enthält-Check bei Pipe-Listen, „ohne Angabe" = leeres `se`).
8. Kombinierbarkeit sicherstellen: Status + Typ + Art + BL + Leistung + Registrierung +
   Inbetriebnahme + Spannungsebene beliebig kombinierbar.
9. Statistik-Tab „Spannungsebenen": Verteilung (Balken/Pie, wie Bundesländer-Tab),
   folgt aktivem Filter.
10. Tabellen-Ansicht: Spalte „Ebene" (kurz: MS/NS/HS/ÜHS + Umspann-Kürzel), zwischen
    Gemeinde und Registriert — NUR wenn Tabelle damit nicht zu breit wird (sonst Tooltip).
11. Popup: Spannungsebene als Zeile ergänzen (nach Netzbetreiber).
12. `bundle_singlefile.py` → Single-File neu.
13. Browser-Tests: Dropdown vorhanden; Filter_MS → nur MS-Anlagen (Stichprobe gegen DB);
    Kombi MS+Status-In-Planung; Statistik-Tab folgt; Badge korrekt.
14. Edge-Cases: „ohne Angabe" wählbar → nur die 509; Pipe-Multi-Ebene wird von beiden
    Ebenen-Filtern erfasst; Sortierung der Tabelle mit neuer Spalte.
15. F5-Regression: Status-Checkboxen, Marker-Stile, Tabellen-Deep-Links (NorthData/Geo)
    weiterhin intakt.
16. Doku: PROJEKTSTAND (V10-Absatz), update.md (falls Export-Schema-Erwähnung nötig).
17. ROADMAP: Punkte abhaken, Befunde dokumentieren.
18. Revision nach `iterations/V10_SpannungsebenenFilter.html`.
19. Klickbare HTML an User (MEDIA:) + Änderungsliste.
20. User-Freigabe als Gate → danach Roadmap-Status F2 FREIGEGEBEN.

**Umsetzung (03.09., alle 20 Punkte ✅):**
- Export: `SELECT_RAW_EXTRA` um korrelierte Subquery erweitert (Pitfall: SQLite erlaubt
  `GROUP_CONCAT(DISTINCT x, sep)` NICHT → DISTINCT in innerer Subquery). Neues Feld `se`
  (Pipe-getrennt bei Multi-NAPs) + `meta.spannungsebenen` (Multi-Ebenen je 1x gezählt).
- Export-Ergebnis: 65.659 Anlagen, 50.450 mit `se`, Verteilung MS 31.580 / HS 10.862 /
  HöS 2.475 / NS 1.226 / Umspann-HS-MS 4.233 / Umspann-MS-NS 353 / Umspann-HöS-HS 81 /
  ohne Angabe 15.209 (v. a. In-Planung + stillgelegt — In-Betrieb-Quote ohne NAP nur ~1 %).
- UI: Dropdown „Spannungsebene" (8 Optionen inkl. „ohne Angabe" = `__ohne__`), applyFilters
  mit enthält-Logik für Pipe-Listen, Badge/hasFilter um seActive erweitert, Popup-Zeile
  „Spannungsebene", Statistik-Tab „Spannungsebenen" (Balken, folgt _lastFiltered),
  Tabellen-Spalte „Ebene" mit Kürzeln (MS/NS/HS/HöS/Umspann …, Volltext im Tooltip).
- Browser-Tests (verifiziert): MS-Filter 31.465 (alle enthalten MS ✅), Kombi MS+Planung
  31.466 (korrekt: nur 1 In-Planung-Anlage hat MS), „ohne Angabe" 3.213 im Status-Default
  (alle ohne se ✅), HöS 2.473, Statistik-Tab 8 Balken + folgt Filter (HöS-Filter → 1 Balken
  „HöS · 2.473 · 100,0 % · 12.347 MW"), Popup zeigt „Höchstspannung", Tabellen-Ebene-Spalte
  „MS" + Kürzel, F5-Regression: NorthData-Link OK, Geo-Deep-Link OK (Popup öffnet), Header
  korrekt (13 Spalten).
- Test-Infra-Pitfall: zoomToShowLayer-Cluster-Animation kann Browser-Eval blockieren —
  Tests besser mit map.setView + openPopup fragmentieren.
- Revision: iterations/V10_SpannungsebenenFilter.html. Nicht gepusht (Regel 4).

# PLAN — Statistik-Modul: Betreiber-Auswertung & Größenklassen

> Stand: 2026-08-29 · Entwurf zur Freigabe
> Ziel: Auf der Karten-HTML-Seite Statistiken anzeigen — (1) welcher Betreiber wie viele
> Anlagen & Summe MW hat, mit Filter/Sortierung/optimierter Tabelle; (2) Verteilung der
> Anlagengrößen ab 1 MW bis zur höchsten je im MaStR angegebenen MW-Größe, je Technologie.

## Datenbasis (verifiziert, aus `dist/assets/einheiten.json`)

- 36.175 georeferenzierte Anlagen: **26.586 Wind** (≥1 MW) + **9.589 PV** (≥1 MWp)
- **Betreiber**: Alle 36.175 haben ein Betreiber-Feld (`ab`); **14.141 eindeutige Betreiber**.
  - Top-Betreiber nach Anzahl: PROKON (257), RWE Wind Onshore & PV (222) …
  - Top-Betreiber nach Summe MW: Borkum Riffgrund 3 (959 MW), EnBW He Dreiht (765 MW) …
- **Größenklassen-Reichweiten**:
  - **PV**: min 1,0 MW → **max 162,26 MW** (1 großer Freiflächenpark). 1–2 MW dominant (3.588).
  - **Wind**: min 1,0 MW → **max 80 MW**. 2–3 MW dominant (10.051).
- WICHTIG (Datenqualität): Wind-max 80 MW ist ein einzelner stark ausgeprägter Wert;
  PV-max 162 MW ebenso. Klassen-Definition bezieht sich auf die realen Maxima.

---

## 20-Punkte-Plan

### Phase A — Fundament & Daten-Statistik (1–4)
1. **A1 · Betreiber-Feld verifizieren:** Betreibername (`ab`) als Grundlage bestätigen; ggf.
   `anlagenbetreiber`/`NB`-Fälle prüfen (natürliche Personen, „…GRb", Sonderzeichen  ＆).
2. **A2 · Statistische Aggregation per Datenbank:** SQL-Views in `mastr.db` anlegen (im
   `import_mastr.py` idempotent erzeugt):
   - `vw_betreiber` → Betreiber, Anzahl, Summe MW, durchschnittl. MW, min/max, je Technologie.
   - `vw_groesse` → je Technologie: Größenklasse, Anzahl, Summe MW, Anteil %.
3. **A3 · Aggregation in `export_app.py`:** Aus der SQLite-Auswertung ein kompaktes
   `dist/assets/statistiken.json` erzeugen (Schlüssel: betreiber[], groessenklassen{wind,pv}[],
   meta mit Gesamtzahlen & Maxima).
4. **A4 · Frontend-Schema:** Datenvertrag festlegen (Feldnamen, Typen, Reihenfolge), damit
   HTML/JS stabil dagegen bauen kann.

### Phase B — Betreiber-Tabelle (5–12)
5. **B1 · UI-Einstieg:** Button „Statistik" in der Top-Bar (oben rechts, neben Suche), der
   ein Overlay-/Seitenpanel öffnet.
6. **B2 · Tabellenlayout:** Reagible Tabelle mit Spalten
   **Betreiber | Anzahl | Summe MW | Ø MW**; Zeilenzahl mit Lazy-Rendering (bei 14 k Einträgen).
7. **B3 · Technologie-Filter:** Toggle/Select „Alle | Wind | PV", reduziert die Tabelle.
8. **B4 · Sortierung (User-Wunsch!):** Klick auf Spaltenkopf sortiert (Anzahl ↑↓, Summe MW ↑↓,
   Ø ↑↓, alphabetisch). Standard: Summe MW absteigend.
9. **B5 · Text-Filter Betreiber:** Eingabefeld über der Tabelle filtert Betreibernamen live
   (akzent-/case-unabhängig, wie die Karten-Suche).
10. **B6 · Pagination / Top-N:** Auswahl „Top 10 / 50 / 100 / alle" oder Scroll-Pagination, um 14 k Zeilen performant zu halten.
11. **B7 · Karten-Kopplung:** Klick auf eine Betreiber-Zeile → Karte zeigt nur die Anlagen
    dieses Betreibers (neuer Filter). Optional Grenze nicht überschreiten (Cluster).
12. **B8 · Export:** „CSV herunterladen" der aktuell gefilterten/ sortierten Tabelle.

### Phase C — Größenklassen-Verteilung (13–17)
13. **C1 · Klassen-Definition:** Automatische Klassen je Technologie von 1 MW bis zum realen
    Maximum (PV: bis 162 MW; Wind: bis 80 MW), sinnvoll gestaffelt:
    - Wind: 1–2, 2–3, 3–4, 4–5, 5–7, 7–10, 10–20, 20–50, 50–100 MW
    - PV: 1–2, 2–5, 5–10, 10–30, 30–60, 60–100, 100–200 MW
14. **C2 · Vertikale Balkendiagramme** (CSS/Canvas, kein externes Chart-Lib nötig —
    schlank & offline): je Technologie Anzahl je Klasse.
15. **C3 · Summen-MW-Balken:** Zusatzansicht „Anteil an Gesamtleistung je Klasse".
16. **C4 · Technologie-Toggle:** Umschalter Wind/PV/Both im Diagrammbereich.
17. **C5 · Hover/Tooltip:** Zeigt Klasse, Anzahl, Summe MW, Ø und Anteil % an.

### Phase D — Integration & Qualität (18–20)
18. **D1 · Design-Integration:** Panel/Overlay responsiv (Desktop-Sidebar rechts, Mobile
    Vollbild), Dark/Light-fähig, konsistent zur Karte.
19. **D2 · Performance & Verifikation:** 14 k Zeilen Tabelle beschleunigen (virtualization),
    Werte gegen SQLite-Checksummen prüfen; Cross-Check Top-Betreiber mit der DB-Ausgabe.
20. **D3 · Doku & Git:** `docs/statistik.md` (DE+EN) anlegen, PLAN aktualisieren,
    Build-Pipeline (fetch→import→export→bundle) erweitern, Commit.

---

## Offene Detailfragen (zu entscheiden)
- Panel: **Overlay/Sidebar** (empfohlen) vs. separates Tab.
- Sortierung initial: Summe MW (empfohlen) vs. Anzahl.
- Größenklassen: feste Staffel (empfohlen, s. o.) vs. dynamisch (equidistant/Legend).
- Betreibernamen bereinigen? (z. B. „natürliche Person (ABR…)" zusammenfassen) — ja, als Option.
- CSV-Export nötig? D8 ist optional → bestätigen.

> Hinweis: Der User-Wunsch nach **Filtern & Sortieren der Betreiber + tabellarischer
> Auflistung (Betreiber/Anzahl/Summe MW)** ist in A2, B2–B8 abgedeckt.
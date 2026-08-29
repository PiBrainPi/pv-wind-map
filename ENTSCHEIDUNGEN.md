# Entscheidungen (EVL) — PV & Wind Karte

> Status: laufend geführt. Neue Entscheidungen anhängen, nie löschen.
> Format: Datum · Entscheidung · Begründung · Status

## Gefällte Entscheidungen

1. **Geolokation (2026-08-29):** Nur Anlagen mit **vorhandenen Koordinaten** im MaStR werden gezeichnet. **Kein** Geocoding fehlender Koordinaten.
   - Begründung: Geocoding von ~100k+ Adressen (MaStR liefert bei vielen PV-Anlagen keine Koordinaten) wäre teuer, langsam und datenschutzsensibel. Bewusste Abgrenzung auf präzise, vorhandene Daten.

2. **Leistungsgrenze (2026-08-29):** Nur **Bruttoleistung ≥ 1 MW (Wind)** bzw. **≥ 1 MWp (PV)**.
   - Begründung: Reduziert die Datenmenge massiv (von ~3,7 Mio. auf deutliche weniger Einträge), fokussiert auf relevante Assets, verringert Clustering-/Performance-Aufwand. Kleinere Dach-PV bewusst ausgeschlossen.

3. **Haltung / Repo (2026-08-29):** Nur **lokal**; Git-Repo lokal. Hosting wird **vorbereitet** (Doku, Hostbarkeit), aber nicht live geschaltet; ggf. später. Zweisprachige Doku (DE + EN).
   - Begründung: User möchte zunächst lokalableieren und hosten später entscheiden.

4. **Update-Rhythmus (2026-08-29):** **Manuell** auslösbar; Pipeline so gebaut, dass daraus **jederzeit ein Cronjob** entstehen kann.
   - Begründung: Volle Kontrolle erstmal; Automatisierung als Option vorbereitet (Skript als Einstiegsbefehl ohne Interaktion).

5. **Kartentechnologie (2026-08-29):** **Leaflet + MarkerCluster** gewählt (statt PMTiles).
   - Begründung: Datenvolumen ~36 k Punkte ist für Leaflet + Clustering ideal beherrschbar;
     hostbar als statische Site; Single-File möglich. Kein Vektortiling nötig für V1.

## Wichtige Daten-Erkenntnisse (aus Umsetzung)

6. **MaStR-Einheiten inkonsistent:** PV-Bruttoleistung in **kWp**; Wind **gemischt**
   (kW für moderne/große Anlagen wie V236-15MW=15000, aber auch alte wie V47=660;
   wenige in MW). → Import normalisiert auf **MW** mit Heuristik `>80 → kW`.
   (siehe docs/datenmodell.md). Erst festgestellt, nachdem erste Summen absurd waren
   (Wind „avg 2556 MW"); mit korrekter Normalisierung avg ≈ 3.4 MW.
6. **Filter-Operator:** Für Zahlenfilter funktioniert nur `~gt~` zuverlässig
   (`~gte~`/`~ge~`/`>=` schlagen fehl). Feldnamen lokalisiert (Umlaute).
7. **PV-Datenmenge:** MaStR enthält ~6,4 Mio. PV-Einträge (davon ~4,85 Mio. Dachanlagen).
   Die ≥1-MWp-Grenze reduziert auf ~10,5 k in Betrieb — entscheidend für das Design
   (sonst wären Download & Karte unpraktikabel).

Die zuvor offenen Detailfragen (Clustering-Strategie, MaStR-Quelle, schlanke
Remote-Feldliste) sind alle in den Entscheidungen 4–7 bzw. in docs/ dokumentiert.

## Statistik-Modul — Entscheidungen (2026-08-29)

8. **Panel-Typ:** Overlay-**Sidebar rechts** (statt separatem Tab/Karte) — öffnet per
   „📊 Statistik"-Button in der Top-Bar; Overlay verdunkelt die Karte.
   - Begründung: klare Fokustrennung (Karte ↔ Statistik), schlank, responsiv.

9. **Größenklassen:** **feste Staffel** je Technologie (Wind: 1–2…50–100 MW; PV: 1–2…100–200 MW)
   bis zum realen Maximum (Wind 80 MW, PV 162 MW). Keine dynamische/equidistante Skala.
   - Begründung: einfacher, konsistenter und aussagekräftiger für die Zielnutzung.

10. **CSV-Export:** **bewusst NICHT umgesetzt** — vom User explizit abgelehnt (Punkt B8 entfällt).

11. **Betreiber-Kopplung:** Klick auf eine Betreiber-Zeile filtert die Karte auf dessen Anlagen
    (bei mehreren Anlagen Fit-Bounds, bei einer Fly-to + Popup).

## Wichtige Daten-Erkenntnis (Statistik)

- **14.141 eindeutige Betreiber** über 36.175 georeferenzierte Anlagen. Top nach Leistung:
  Borkum Riffgrund 3 (≈959 MW), EnBW He Dreiht (≈765 MW); nach Anzahl: PROKON (257 Anlagen).
- Statistik-Aggregation erfolgt in `export_app.py` aus SQLite (nur `geolokation=1`,
  konsistent zur Karte) → `dist/assets/statistiken.json`.
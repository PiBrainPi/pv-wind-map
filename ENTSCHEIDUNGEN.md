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

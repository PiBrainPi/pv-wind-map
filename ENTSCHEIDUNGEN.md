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

## Verbleibende Detailfragen (während Umsetzung)

- Skalierung/Data-Menge der hostbaren App: Clustering-Strategie (Leaflet vs. PMTiles) — Entscheidung in Phase C (Schritt 12).
- Exakte MaStR-Quelle (JSON-Endpunkt vs. XML-Komplettdownload) — Entscheidung in Schritt 4 nach Größen-/Strukturvergleich.
- Remote-Feldliste für Frontend minimal halten (nur Kartendaten + Popup).
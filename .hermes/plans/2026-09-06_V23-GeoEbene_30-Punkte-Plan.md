# V23 „Geo-Ebene" — 30-Punkte-Umsetzungsplan (Aufgabenpakete 1–8)

**Datum:** 06.09.2026 · **Projekt:** ~/Projects/pv-wind-map (V21 live, V22 wartet auf Freigabe)
**User-Entscheidung (Paket 8):** Variante A — alle Einheiten eines zersplitterten Parks erscheinen
als Marker, die Filterprüfung läuft über die Park-Summe (Döllen: 13 EH → Park 154,8 MW → „150+").

---

## Recherche (Punkte 1–6) — ABGESCHLOSSEN

| # | Recherche-Ergebnis |
|---|---|
| 1 | Such-Suggest `showSuggest()` (src/index.html ~L3045): Reihenfolge aktuell NAP → Betreiber → Assets. Geo-Blöcke (BL/LK/Gemeinde) kommen **unter Betreiber, über Assets**. Klick-Pfad analog `selectBetreiberSearch()` (L3013): renderMarkers + fitBounds + Suchfeld-Label + closeStats. |
| 2 | Filterleiste `#toolbar` (L1944): Typ → Bundesland → Art → Leistung. Neue Reihenfolge: Bundesland → **Landkreis** → **Gemeinde** → Art → Leistung. Befüllung nach Vorbild `populateFilterBl()` (L2335, Set + sort). `applyFilters()` (L2690) filtert auf `u.lk`/`u.g` exakt; `hasFilter` (L2760) erweitern. |
| 3 | Datenqualität: 377 Landkreise, 6.473 Gemeinden (Export-Basis). **164 Gemeindenamen mehrfach** über (BL,LK)-Kombis → Gemeinde-Filter kontextabhängig: Optionen folgen dem gewählten Landkreis (sonst alle, mit BL-Zusatz bei Mehrfachnamen). 4 LK-Namen in mehreren BL (z. B. Höxter) → Landkreis-Option mit BL-Klarnamen-Zusatz bei Kollision, Filterwert bleibt LK-Name (Marker identisch). |
| 4 | NAP-Tab „Landkreis": `netzanschlusspunkte` hat `nettoengpassleistung_mw` (41 % NULL, 16.476 gefüllt, Ø 4.717 MW — Offshore-Höchstspannung). Join über `lokation_id` → nur NAPs mit ≥1 georef Anlage im Landkreis zählen; Gesamtleistung NAP = SUM(Nettoengpassleistung) der zugeordneten NAPs (NULL als 0, dokumentiert). NAP-Index-Export `export_nap_index.py` (27078 NAPs, Felder nap/lid/nb/se/rz/n) **muss um „n LK/Gemeinde-Bezug" erweitert werden**? Nein — Statistik-Tab rechnet serverseitig in export_app.py (lokation_id → LK via einheiten-Join), kein neues Frontend-Asset nötig. |
| 5 | V22-Cluster-Logik `export_app.py` L234–271: `_park_key()` + `_cluster_rows()` vorhanden. Für Paket 8 wird ein **unit→cluster-Mapping** benötigt (`pk` = Park-Schlüssel, `pkmw` = Park-Summe je Einheit), damit das Frontend ohne zweite Datenquelle filtern kann. Cluster-Schlüssel identisch zu V22 (ET + Betreiber + Parkname). |
| 6 | Größen-Balken (L3890–3949): `bar-row` mit `data-tip` JSON (Klasse, von/bis indirekt über Label „104–150 MW"); Klick-Handler bisher nur Tooltip (L3944–3949). Für Paket 5: `data-von`/`data-bis`/`data-tech`-Attribute am Row rendern, Klick → `selectGroessenKlasse(von, bis, tech)` → renderMarkers + fitBounds + Label + closeStats. Im gesamt-Modus entscheidet die Klick-Position (linker Balken=Wind, rechter=PV, Zeile=beide). |

**Zahlen-Grundlage:** Export-Basis 53.500 georef (alle Status, einheiten-Tabelle). Döllen = 13 EH
(7,4–31,4 MW) = 154,8 MW. NAPs: 27.870 gesamt, 27.078 im Frontend-Index.

---

## Planung (Punkte 7–10)

| # | Planung |
|---|---|
| 7 | **Paket A (Datenbasis, export_app.py):** (a) `groessen_cluster` bleibt; zusätzlich `landkreise`-Statistik: `{lk, n_ges, mw_ges, n_pv, mw_pv, n_wind, mw_wind, n_nap, mw_nap}` — Einheiten aus `einheiten` (georef, alle Status), NAPs via `lokation_id`-Join, sortiert nach mw_ges desc. (b) `gemeinden`-Statistik analog (mit `b`+`lk`-Kontextfeld). (c) unit→Park-Mapping: im `build_units()` die V22-Schlüssel `_park_key` je Einheit berechnen und als `pk` (Park-Schlüssel-Hash) + `pkmw` (Park-Summe MW) ins einheiten.json — **nur bei Mehrglieder-Parks** (n≥2, sonst keine Felder → Dateigröße ~konstant). Updatefähigkeit: alles in export_app.py → jeder `build.sh`-Lauf frisch. |
| 8 | **Paket B (Suche):** neue `searchGeo(q)` → Treffer-Buckets {bundesland, landkreis, gemeinde} (Label + count, norm-Matching). showSuggest rendert nach Betreiber-Block: ① NAP ② Betreiber ③ **Geo (BL/LK/Gemeinde, je max 2 Zeilen)** ④ Assets. Klick → `selectGeo(typ, name)`: Marker + fitBounds + Label (`Landkreis: X (n Anlagen)`). |
| 9 | **Paket C (Filter):** 2 neue `<select>` zwischen Bundesland und Art: `filter-lk`, `filter-g`. Befüllung: LK = alle (sortiert); Gemeinde abhängig vom gewählten LK (ohne LK-Wahl: alle Gemeinden, mehrfach vergebene Namen erhalten Zusatz „(BL)"). applyFilters: `lk`/`g` exakt + kombinierbar; `hasFilter` + Tabelle-Meta (showAllUnits parts) erweitern; Änderung von BL setzt Gemeinde-Optionen neu (LK-Liste folgt BL analog). |
| 10 | **Paket D (Tab Landkreis):** neuer Stats-Tab nach „Bundesländer"; Tabelle analog Hersteller (identisches CSS `#hersteller-table`, Sortierung per Header-Klick, Default mw_ges desc): Spalten Landkreis · Assets (P/W) · Leistung (P/W) · Assets PV · Leistung PV · Assets Wind · Leistung Wind · NAP · NAP-MW. Zeilen-Klick → selectGeo('lk'). Summary-Zeile gesamt. |
| 11 | **Paket E (Balken-Klick):** bar-row erhält `data-von/bis/tech`; Klick → `selectGroessenKlasse(von,bis,tech)`: Filter `u.mw>=von&&u.mw<bis` (+Tech wenn nicht gesamt), Marker + fitBounds + Suchfeld-Label („Größenklasse 104–150 MW · Wind (n Anlagen)") + closeStats. Gesamt-Modus: Klick auf Wind-Balkenabschnitt → nur Wind; PV-Balkenabschnitt → nur PV; Klick auf Zeilen-Label → beide. Beim „Parks aggregiert"-Modus: Klick filtert nach **Cluster-Größe** (pkmw zwischen von/bis) — konsistent zur angezeigten Verteilung. |
| 12 | **Paket F (Leistungsfilter):** applyFilters-Leistungszweig: Basis-Variante „Park" = `u.pkmw >= von && u.pkmw < bis` (alle EH des Parks bleiben sichtbar); Variante „Einzelanlage" = bisheriges Verhalten (u.mw). Neuer kleiner Toggle im Toolbar-Label („Leistung: Einzelanlage/Park"), Default: **Park** (User-Wunsch: Filter soll echte Anlagenkgröße prüfen). filter-lk/g/werte kombinierbar. |

---

## Umsetzung (Punkte 11–24) — Reihenfolge

| # | Schritt | Datei |
|---|---|---|
| 11 | export_app.py: `_park_key` auf Modulebene heben, `build_units` erweitert (pk/pkmw bei n≥2) | scripts/export_app.py |
| 12 | export_app.py: `build_statistiken` um `landkreise` + `gemeinden` (mit NAP-Join) erweitern | scripts/export_app.py |
| 13 | Export laufen lassen + Zahlen prüfen (Döllen: pkmw=154,8; LK Dithmarschen NAP-Summe plausibel) | — |
| 14 | Suche: `searchGeo` + `selectGeo` + showSuggest-Erweiterung + CSS (sug-geo) | src/index.html |
| 15 | Filter: HTML `filter-lk`/`filter-g`, populate-Logik (BL-kontextuell), applyFilters + hasFilter + Tabelle-Meta | src/index.html |
| 16 | Stats-Tab „Landkreis": HTML-Sektion + renderLandkreise() + Sortierung + Zeilen-Klick | src/index.html |
| 17 | Balken-Klick: data-Attribute + selectGroessenKlasse + Gesamt-Modus-Split | src/index.html |
| 18 | Leistungsfilter: Park/Einzelanlage-Toggle + pkmw-Filterpfad | src/index.html |
| 19 | bundle_singlefile + cp dist/index.html | — |
| 20 | Browser-Verifikation Paket B/C (Suche „Dithmarschen", Filter-Kombis) | — |
| 21 | Browser-Verifikation Paket D (Tabelle + Sortierung + Klick) | — |
| 22 | Browser-Verifikation Paket E (Klick 104–150 Wind/ges./Park-Modus) | — |
| 23 | Browser-Verifikation Paket F (Filter 150+ → Döllen 13 Marker; Park-Toggle) | — |
| 24 | F5-Regression: V21/V22-Funktionen (Betreiber-Suggest, NAP, Status-Filter, Cluster-Basis) | — |

## Überprüfung (Punkte 25–30)

| # | Prüfkriterium | Erwartung |
|---|---|---|
| 25 | Export: statistiken.json enthält landkreise (377), gemeinden (~6.473), Felder vollständig | JSON ok, Döllen-Kontrollwerte korrekt |
| 26 | Suche „dithmarschen" → 1 Geo-Treffer über Betreiber-Block; Klick → Marker + Label | ~2.000 Anlagen sichtbar |
| 27 | Filter-LK/Gemeinde: Werte-Sets, Kombi BL+LK+G, Badge zählt | Anzahl-Badge korrekt |
| 28 | Balken-Klick 104–150: gesamt-Modus Wind-Klick → nur Wind-Marker; „Parks aggregiert" → Cluster-Filter | Markerzahl = Klassen-anzahl |
| 29 | Leistungsfilter 150+ (Park-Modus): 13 Döllen-Marker sichtbar; Einzelanlage-Modus: alt-Verhalten | Döllen korrekt |
| 30 | F5-Regression + 0 JS-Fehler + Revision V23 + human-share + Doku (PROJEKTSTAND/ROADMAP/README/statistik.md) | klickbare HTML im Chat |

**Risiken/Offen:** einheiten.json wächst leicht (pk/pkmw nur bei Multi-Parks); Gemeinde-Auswahl ohne
LK-Kontext = lange Liste (→ Kontextabhängigkeit); NAP-MW = NAP-Kapazität ≠ Anlagen-Leistung
(Begriffsunterschied im Tab-Titel dokumentieren: „NAP-MW = Nettoengpassleistung der zugeordneten NAPs").

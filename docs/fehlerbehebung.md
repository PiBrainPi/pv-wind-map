# Fehlerbehebung (Troubleshooting) — PV & Wind Karte

> Stand: 2026-09-09 (V32.1)

## Bekannte Fehlerbilder & Lösungen

### 0. „Alle Anlagen anzeigen"-Klick tut nichts (BEHOBEN in V25)
**Fehlerbild:** Filter aktiv, Button erscheint, Klick → sichtbar keine Reaktion.
**Ursache (V23-Regression):** `showAllUnits()` las die V23-Geo-Filter (Landkreis/Gemeinde)
nicht — die Meta-Zeile referenzierte `lk`, bevor es definiert war → `ReferenceError:
lk is not defined` → Funktion brach ab, bevor das Overlay geöffnet wurde.
**Lösung (V25):** Geo-Filter in `showAllUnits()` einlesen und anwenden (u.lk / u.g).
**Lektion:** Neue Filter IMMER in beiden Funktionen ergänzen: `applyFilters()` UND
`showAllUnits()` (gleiche Filterlogik, zwei Stellen — Browsers-Konsole via F12 zeigt
den ReferenceError sofort).

### 1. „Fehler beim Laden: Failed to fetch" (hostbare Version)
**Ursache:** Die hostbare `dist/index.html` lädt ihre Daten per `fetch()` aus
`assets/*.json`. Ab `file://` ist fetch() wegen CORS gesperrt.
**Lösung:** Die **Single-File** `dist/index_singlefile.html` verwenden (Daten eingebettet,
funktioniert ab `file://`), ODER die Dateien über einen HTTP-Server ausliefern:
```bash
cd ~/Projects/pv-wind-map/dist && python3 -m http.server 8080
# dann http://localhost:8080
```

### 2. Karte zeigt keine Rasterkacheln (grauer Hintergrund)
**Ursache:** OpenStreetMap-Kacheln können nicht geladen werden (offline / geblockt).
**Lösung:** Internetverbindung prüfen. Kacheln kommen von `{s}.tile.openstreetmap.org`.
Alternativer Hintergrundkarten-Dienst wäre konfigurierbar (z. B. Carto).

### 3. Markierungen/Cluster fehlen, obwohl App lädt
**Möglichkeit A — Filter aktiv:** Prüfe den Typ-Filter („Wind"/„PV"), den Bundesland-Filter
und den Art-Filter (z. B. „Gebäudesolaranlage"). Auf „Alle" zurücksetzen.
**Möglichkeit B — veraltete Daten:** Datenstand oben rechts in der Suchleiste prüfen („Stand: YYYY-MM-DD"). Update laufen lassen
(siehe `docs/update.md`).
**Möglichkeit C — falsches Datenmodell nach manueller Änderung:** Erneut exportieren:
`python3 scripts/export_app.py` und `python3 scripts/bundle_singlefile.py`.

### 4. Zahlen im Footer stimmen nicht mit DB überein
**Ursache:** `dist/assets/` oder die Single-File sind älter als die DB.
**Lösung:** Export + Bundle neu erzeugen. Der `metadaten.stand`-Wert zeigt den letzten
Import.

### 5. `python3 scripts/import_mastr.py` meldet „UNIQUE constraint failed: metadaten.key"
**Ursache:** Alte Zeilen in `metadaten` beim Rebuild. Durch `INSERT OR REPLACE` behoben —
also einfach erneut ausführen. Falls persistent: `data/mastr.db` löschen und neu importieren.

### 6. Merkwürdige Leistungswerte (z. B. Anlage mit 15000 MW)
**Ursache:** MaStR-Einheiten-Konvention (kW vs. MW), siehe `docs/datenmodell.md`.
**Lösung:** Der Import normalisiert bereits korrekt (Wert > 80 → kW). Nach einem
vollständigen Re-Import (`fetch` → `import`) sind die Werte in MW konsistent.
Einzelwerte von 100/95 MW sind veraltete/korrekte große Offshore (V236-15MW) bzw.
kW-Kleinstanlagen.

### 7. API-Abfrage scheitert (fetch_mastr.py)
**Ursache:** MaStR kurzzeitig nicht erreichbar, Rate-Limit, o. ä.
**Lösung:** Skript hat eingebaute Retries (5 Versuche, exponentielle Wartezeit).
Erneut ausführen. Dauert das Problem an, ist das MaStR (marktstammdatenregister.de)
ggf. in Wartung — später erneut versuchen.

### 8. Dubletten oder fehlende Anlagen
**Hinweis:** Die DB nutzt `MaStRNummer` als UNIQUE-Schlüssel (`INSERT OR REPLACE`).
Ein Re-Import ist ein Voll-Rebuild (DELETE + INSERT). Dubletten durch den
Behörden-Datensatz selbst sind möglich (wenige) und werden 1:1 übernommen.

---

## Troubleshooting (EN)

1. **"Failed to fetch"** — hostable `index.html` loads data via fetch() → needs an HTTP
   server (not file://). Use the single-file version or run `python3 -m http.server 8080` in `dist/`.
2. **No tiles (grey map)** — OpenStreetMap unreachable; check internet.
3. **Missing markers** — check filters, data freshness (footer), re-export.
4. **Footer counts don't match DB** — re-run export + bundle.
5. **UNIQUE constraint metadaten.key** — re-run import (now uses INSERT OR REPLACE); else delete mastr.db and re-import.
6. **Odd capacity values** — kW vs MW unit convention (see datenmodell.md). Re-import normalizes.
7. **MaStR API failing** — built-in retries; retry later if MaStR is in maintenance.
8. **Duplicates/missing** — MaStRNummer is unique; full rebuild on re-import.

## V32-Bugfixrunde (08.09.2026)

### F-V32-1: „NAP-Ranking nicht geladen" im Singlefile
- **Ursache:** `bundle_singlefile.py` bettete `nap_index.json` ein, nicht aber
  `nap_ranking.json`. Im Singlefile existiert kein `assets/`-Ordner → optioneller Fetch
  schlug fehl → `window.__PVWIND_NAP_RANKING__ = null` → Hinweistext im NAP-Tab.
- **Fix:** nap_ranking.json wird jetzt als 6. Datenblock eingebettet
  (`window.__PVWIND_NAP_RANKING__`).

### F-V32-2: Betroffenheit „Anzeigen" — neues Asset unsichtbar
- **Ursache:** `clusterGroup.disableClustering()` wurde aufgerufen, existiert aber in
  Leaflet.markercluster nicht (stiller No-op) → im Anzeigen-Modus blieb Clustering aktiv,
  Bestand + NEU-Anlage am selben NAP verschmolzen in einem Cluster-Bubble.
- **Fix:** Anzeigen-Modus rendert in einfacher `L.layerGroup` (clustering-frei);
  Marker-Bau (`_buildUnitMarker`) und Lazy-Popup (`_bindLazyPopup`) dafür extrahiert.

### F-V32-3: Historie-Delta mit kW/MW-Falschangaben (Entfernt: Wind 80 MW)
- **Ursache:** Snapshots 7+8 (29.08./01.09.) speicherten Wind-Leistungen VOR dem
  V27b-Physik-Check — 120 Einträge mit kW-als-MW (8.545 MW zu viel je Snapshot).
  compute_delta rechnete mit diesen Alt-Werten.
- **Fix:** Migration `scripts/fix_snapshot_mw.py` (to_mw-Heuristik auf snapshot_einheiten),
  Snapshots + Bundesländer-JSON + Delta + historie.json neu. Referenzliste:
  `docs/wind_typen_leistungen.md` (3.922 Typen).

### F-V32-4: Netzbetreiber-Filter reagierte nicht
- **Ursache:** `filter-nb` bekam in V31 keinen `change`-Listener (Verifikationstest
  nutzte programmatisches dispatchEvent → Bug unentdeckt).
- **Fix:** Listener ergänzt. **Lessonn learned:** Filter-Tests müssen echte
  change-Events (nutzergesteuert) verwenden.

### F-V32.1-1 (09.09.): Singlefile lädt keine Marker + Statistik-Button tot

**Symptom:** Beim Öffnen der Singlefile-Datei keine Anlagen auf der Karte (erst nach Filter
setzen+entfernen); „📊 Statistik"-Button reagierte nicht. Multi-File-Build war nicht betroffen.

**Ursache (TDZ):** `init()` läuft im Singlefile **synchron** durch (Daten eingebettet, kein
`await fetch()` vor `renderMarkers`). `renderMarkers()`/`applyFilters()` lesen
`_bffShowActive`/`_bffShowSet` — deklariert erst in der BFF-Sektion **nach** dem
`init()`-Aufruf → `ReferenceError: Cannot access '_bffShowActive' before initialization`
(TDZ). Der `catch` in `init()` showed „Fehler beim Laden", `renderMarkers` und `initStats()`
wurden nie erreicht → keine Marker, kein Button-Listener. Im Multi-File masked das
`await fetchJson()` (Event-Loop führt restliches Script inkl. Deklaration vorher aus) den Bug.

**Fix:** Deklarationen `let _bffShowActive/_bffShowSet/_bffLastMatchedLids/_bffLastBestand`
an den Scriptanfang (vor `init()`) verschoben. Plus Vorgänger-Fix: Topbar `z-index:1700`
(über Panel 1600) + Statistik-Button als Toggle.

**Lektion:** Jede in `renderMarkers`/`applyFilters` referenzierte `let/const`-Variable muss
vor `init()` deklariert sein — oder `init()` wird erst nach vollständiger Script-Ausführung
gerufen. Prüfskript: `/tmp/v321_check_tdz_rest.py` (erwartet: `[]`).

### Verifikationsregel (ab V32.1 verbindlich)
Jeder Build wird in **beiden** Varianten geprüft: Multi-File (`dist/index.html` via
http.server) **und** Singlefile (`dist/index_singlefile.html`). Der Singlefile-Synchronlauf
(macht TDZ-Fehler sichtbar statt sie durch await zu maskieren) und die Daten-Einbettungen
(z. B. nap_ranking) unterscheiden sich systematisch vom Multi-File — siehe F-V32.1-1 und F-V32-1.

### F-V33-1…4 (09.09., UX-Runde)
**F-V33-1 LK-Tabelle:** Scrollbalken auf 14 px + stärkeren Kontrast (#475569 auf #cbd5e1);
Verifikation: Container 769 px, Tabelle 1.024 px, scrollLeft-Test OK, Name-Spalte sticky.
**F-V33-2 Statistik-Panel verdeckte Topbar:** Panel `z-index` 1600 → **1800** (über Topbar 1700);
ESC schließt Panel mit. Toggle-Verhalten des Buttons bleibt (öffnet; wenn verdeckt, schließen
via ✕ oder ESC).
**F-V33-3 „Leere" Betroffenheits-Ringe:** KEIN false positive — Ringe markieren auch
NUR-ENTFERNT-Treffer (entfernte Assets sind nicht in allUnits → nie als Marker sichtbar).
Fix: Ring-Farben (grün = Neubau im Umkreis, rot = nur Abmeldungen), Ring-Legende im Summary,
entfernte Assets als rote CircleMarker mit Popup im Anzeigen-Modus (`_bffRemovedLayer`).
**F-V33-4 Singlefile „403r Access blocked":** OSMF-Tile-Policy (03/2026) verlangt HTTP-Referer;
ab `file://` sendet kein Browser einen → Kachel-Block. Fix: Singlefile erkennt `file:` und
lädt **CARTO basemaps** (`{s}.basemaps.cartocdn.com/rastertiles/voyager`, Subdomains abcd,
Attribution © OpenStreetMap contributors © CARTO). Online (http/https) bleibt OSM direkt.
Consent-Text (`#tc-text`) wird bei file:// dynamisch auf CARTO umgestellt (IP an CARTO/USA).

### F-V33.1-1 (09.09., spät): BFF-Anzeigen-Modus — kein Anlagen-Popup
**Symptom (User):** Nach der V33-Umstellung öffnete ein Klick auf eine Bestands-Anlage im
Betroffenheit-Anzeigen-Modus kein Anlagen-Popup mehr.
**Root-Cause:** V32-WP4-Reparatur: Der Plain-Layer-Pfad in `renderMarkers()` baute Marker
via `_buildUnitMarker(u)`, rief aber `_bindLazyPopup(m, u)` NICHT (war nur im Cluster-Pfad
vorhanden). Die Marker hatten keinen Klick-Handler → Popup tot.
**Fix (V33.1):** `_bindLazyPopup` auch im Plain-Pfad binden.
**Verifikation:** Normalmodus-Klick → Popup ✓ · BFF-Anzeigen-Modus → Bestands-Popup ✓
+ 6 rote removed-Marker ✓ · 0 JS-Fehler.

### F-V34-1…3 (09.09., UX-Runde 2)
**F-V34-1 LK-Scrollbalken oben (User-Wunsch):** Vorbild V33 hatte den Balken UNTER der
Tabelle. Neu: synthetischer Balken `#landkreis-scroll-bar` (16 px) OBERHALB, JS-Sync
beidseitig (`_lkSyncing`-Flag gegen Event-Loops), Innenfläche = Tabelle · clientWidth-Verhältnis;
Tabelle ohne eigenen Balken (`scrollbar-width:none`, `::-webkit-scrollbar{display:none}`).
Pitfall: Der Bar-Div braucht immer ein Kind-`<div>` (width wird von `stretch()` gesetzt).
**F-V34-2 Popup-Re-Open (User-Befund: „erneuter Klick öffnet nicht mehr"):**
Root-Cause (Browser-Forensik): `m.bindPopup()` registriert Leaflets `_openPopup` (Toggle!)
am selben `click`-Event wie `_lazyPopup` → Doppel-Dispatch; Leaflet schloss das von
`_lazyPopup` geöffnete Popup sofort wieder. Fix: `_bindLazyPopup` ohne `bindPopup` —
eigenes `L.popup` (maxWidth 420), Toggle im Marker-Handler, `openOn(map)` (Cluster-Quirk
gelöst), NAP-Link-Delegation (V21.4) auf `contentupdate` übernommen. Verifiziert:
Klick→Popup, Kartenklick→zu, Re-Klick→Popup (Plain UND Cluster UND BFF-Anzeigen-Modus).
**F-V34-3 Statistik-Panel +20 %:** width 820→984 px, right:-860→-1024 px.

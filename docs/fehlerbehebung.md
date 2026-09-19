# Fehlerbehebung (Troubleshooting) — PV & Wind Karte

> Stand: 2026-09-11 (V39: F-EEG-1 EEG-Semantik · V37: F-TYP-1 Typen-Dubletten)

## Bekannte Fehlerbilder & Lösungen

### F-EEG-1. EEG-Donut wurde als „Vergütungsstatus" missverstanden (KLARGESTELLT 11.09.2026, V39)
**Fehlerbild:** User (Betreiber-Mitarbeiter, CEE) meldete: „PV-Assets sind nach Leistung
überwiegend NICHT EEG-vergütet, aber das Diagramm zeigt 100 % mit EEG — da muss ein Bug sein."
**Ursache (kein Daten-Bug, sondern Semantik):** Das Diagramm wertet das MaStR-Feld
`EegInbetriebnahmeDatum` aus = **„ist eine EEG-Anlage registriert?"** — nicht „erhält die
Anlage EEG-Vergütung?". Fasst man beides zusammen, entsteht der falsche Eindruck.
**Harte Prüfung (11.09., DB-Audit):**
- MaStR-Registrierung ist für ALLE ortsfesten Erzeugungsanlagen Pflicht — **unabhängig
  davon, ob ein Zahlungsanspruch nach EEG/KWKG besteht** (MaStR-Webhilfe,
  marktstammdatenregister.de, abgerufen 11.09.2026).
- Die Datenbasis enthält 6 EEG-Felder: `EegInbetriebnahmeDatum`, `EegInstallierteLeistung`,
  `EegAnlageMastrNummer`, `EegAnlageRegistrierungsdatum`, `EegAnlagenschluessel`,
  `EegZuschlag`. **Kein einziges Feld bildet den Vermarktungs-/Vergütungsweg ab**
  (kein PPA-Feld, keine Direktvermarktungsart, kein „freier Strommarkt"-Flag).
- CEE-Audit: 184 Anlagen / 827 MW (33 PV / 356 MW + 151 Wind / 471 MW) — **100 % mit
  registrierter EEG-Anlage** (Datum + EegMastrNummer je Einheit). Das MaStR bestätigt also
  korrekt, was drinsteht; es kann nur nicht sagen, wie vermarktet wird.
- PPA-/Strompreisgeschäfte laufen i. d. R. **über** eine registrierte EEG-Anlage
  (Direktvermarktung statt Einspeisevergütung) → erscheinen zwingend unter „mit EEG".
- Einziger verwertbarer Hinweis: `EegZuschlag` (Ausschreibungs-ID) — bundesweit nur bei
  26,5 % Wind-/40,0 % PV-Leistung gesetzt; Ausschreibungsanlagen vermarkten i. d. R.
  anders als Fixed-EEG, aber das Feld sagt nichts über den aktuellen Vergütungsweg.
**Lösung (V39):** UI präzisiert — Chart-Untertitel „**EEG-Anlage registriert: ja/nein**
(MaStR-Feld EegInbetriebnahmeDatum)", Erklärtext im Diagramm weist ausdrücklich darauf hin,
dass PPA-/Strompreisgeschäfte unter „mit EEG" laufen und der Vergütungsweg im MaStR NICHT
abgebildet ist. **Fazit: Kein Bug in der Datenverarbeitung — das MaStR kann die Frage
„EEG-vergütet ja/nein?" strukturell nicht beantworten.** Für echte Vergütungswege wären
Netzbetreiber-Abrechnungsdaten oder Marktstammdaten+Netzentgelt-Daten nötig.

### F-CACHE-1. Online-Version wirkt älter als lokal — Browser-Cache (KLARGESTELLT 11.09.2026, V41)
**Fehlerbild:** User meldet: Tab „⚠ Betroffenheit" in der **online** Version enthält die
Zeitraum-Erweiterung (V36) nicht — lokal jedoch schon.
**Analyse (11.09., V41):**
- `https://wind-pv-map.ingenieur-tools.de/` und `https://pibrainpi.github.io/pv-wind-map/`
  lieferten **byte-identisch** diesel HTML wie lokal (md5 `4c952ab0df`, 514.105 Bytes,
  gleicher ETag `6aa3dd09-7df89`, Last-Modified 11.09. 10:50 GMT). Die Zeitraum-Option
  (`<option value="range">`) war **live vorhanden** — es gab technisch keinen Stand-Unterschied.
- **Root Cause 1 — Browser-Cache:** GitHub Pages sendet `Cache-Control: max-age=600`
  (10 min CDN-Cache), aber der Browser des Users hatte die Seite evtl. aus einer älteren
  Session noch im Cache (Tab-Wiederherstellung, Heuristik-Cache ohne beachtetes
  Cache-Control bei Rückkehr zur offenen Seite). → Der User sah eine alte Version,
  ohne dass der Server sie auslieferte. Lösung: **Hartes Neuladen** (Strg+Umschalt+R /
  Cmd+Shift+R) bzw. Cache leeren.
- **Root Cause 2 — Verwirrung um URL:** Die Karte lebt auf der **Subdomain**
  `https://wind-pv-map.ingenieur-tools.de/`. Pfade wie `ingenieur-tools.de/pv-wind-map`
  liefern **404**; `ingenieur-tools.de` **ohne www** zeigt das bekannte
  SSL-Fallback-Zertifikat (Hostname-Mismatch, altes LE-Rate-Limit-Thema). Wer über
  falsche Pfade oder ohne www zugreift, sieht garantiert nicht die aktuelle Version.
**Lösung (V41):**
1. **Build-Stempel in der Infobar** — „PV & Wind Karte – … · Build V41 (11.09.2026)".
   Der User sieht SOFORT, welche Version geladen ist (Cache-Indikator).
2. Prozessregel: Nach jedem Deploy hart neuladen; bei Versions-Diskrepanz zuerst
   Build-Stempel prüfen, dann Cache leeren.
3. Doku: HANDOVER/README verweisen ausdrücklich auf die Subdomain-URL.

### F-TYP-1. Typ-Tab zersplittert durch inkonsistente Typenbezeichnungen (BEHOBEN 11.09.2026, V37)
**Fehlerbild:** Im Statistik-Tab „Typ" tauchen dieselben Anlagentypen mehrfach auf
(z. B. „E-40" 290×, „E40" 215×, „E 40" 122×) — die Kumulation (Anzahl/MW) ist dadurch
falsch aufgeteilt. User-Meldung 11.09. (Beispiele E-40/E40, E-80/E80).
**Ursache:** Das MaStR liefert `Typenbezeichnung` frei-textlich; Varianten mit/ohne
Bindestrich/Leerzeichen/Großkleinabwandlungen werden als verschiedene Typen gezählt.
**Umfang (recherchiert 11.09.):** 752 Typ-Gruppen mit mehreren Schreibweisen auf
Karten-Basis (1.547 Varianten-Mappings, 9.741 betroffene Records); inkl. Ganz-Bestand
(Kleinwind ohne Geolokation) +258 Records in 82 weiteren Gruppen.
**Lösung (als Pipeline-Regel, nicht Daten-Flick):**
1. `scripts/build_typ_normalisierung.py` erzeugt per **Majority-Vote** (häufigste
   Schreibweise = korrekt, Tie-Break kürzeste/dann alphabetisch) die Tabelle
   `data/typ_normalisierung.json` + Report-CSV. Wichtig: `--all-bestand`-Lauf
   überschreibt die JSON nur mit Rest-Mappings — Merge beachten (s. Docstring).
2. Regel in `import_mastr.py::normalize_typ()` (Legacy-Import) und `export_app.py`
   (Wind-only, vor to_mw) — künftige Delta-UPSERTS werden automatisch normalisiert.
   to_mw bleibt unverändert (0 Differenzen, 15-MW-Ausnahme intakt).
3. Einmalige DB-Bereinigung: `scripts/fix_typenbezeichnung.py` (idempotent, DB-Backup
   automatisch in `data/backups/`, Rescan-Check eingebaut).
**Abgrenzung:** Normale Daten-Korrekturen (Anlagenwerte) übernimmt MaStR via Delta-UPSERT;
die Typ-Normalisierung ist eine PRAESENTATIONS-Regel und läuft in jedem Export mit.

### F-Fetch-1. MaStR-API ignoriert Filternamen ohne Umlaut (BEHOBEN 10.09.2026)
**Fehlerbild:** `fetch_v2.py` meldete beim Probe-Request Total = 9.435.237 (Gesamtbestand
aller Erzeugungseinheiten) statt ~32k Wind-Anlagen. Ein Voll-Lauf hätte zigtausend Seiten
gezogen. Die API meldet KEINEN Fehler — der Filter wird still ignoriert.
**Ursache:** MaStR hat den JSON-Endpoint umbenannt/verhalten geändert: Der Filter-Column
heißt jetzt **`Energieträger`** (mit Umlaut). Die bisherige Schreibweise `Energietraeger`
(ohne Umlaut) wirkte nicht mehr. Letzter korrekter Lauf mit alter Schreibweise: 06.09.2026.
**Diagnose:** Offizielle Filter-Column-Namen via
`GET /MaStR/Einheit/EinheitJson/GetFilterColumnsErweiterteOeffentlicheEinheitStromerzeugung`
(85 Columns, Liste ist die Wahrheit). Probe-Request mit pageSize=1: `Total` muss plausibel
klein sein (~32k Wind / ~23k PV) — 9.435.237 = Filter wirkungslos.
**Lösung:** `build_filter()` nutzt jetzt `Energieträger~eq~<id>`. Zusätzlich geändert:
PV-Leistungsklausel `~ge~500` → `~gt~499.9` (`ge` in Kombination mit weiteren Klauseln
lieferte Error=true; `gt` ist verifiziert ok).
**Lektion:** Nach jedem MaStR-Endpoint-Kontakt die Totals gegen die lokalen Counts
prüfen (Sicherheitsnetz macht das je Lauf automatisch).

### F-Fetch-2. Delta-Fetch: Datum-Filter-Syntax (ERARBEITET 10.09.2026)
Der Column **`Letzte Aktualisierung`** (Type date) erlaubt Delta-Abfragen:
`~and~Letzte Aktualisierung~gt~TT.MM.JJJJ` (de-DE-Datum!). Verifiziert:
- `gt~06.09.2026` → ok (Total ändert sich korrekt)
- `ge~…` / `gte~…` / ISO-Datum (2026-09-07) → **Error=true**
Delta-Lauf 06.09.→10.09.: Wind 105, PV 160 Records (statt 32k/23k = ~0,5 % Volumen).

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

### F-V35-1 (10.09.): export_app.py — „Historie: übersprungen (Cannot operate on a closed database)"
**Symptom:** Beim Export-Run erschien die Meldung „Historie: übersprungen"; die
Update-Historie bekam keinen neuen Snapshot-Eintrag.
**Root-Cause:** `main()` schloss die SQLite-Verbindung (`db.close()`) direkt nach dem
Statistik-Build — das Historie-Schreiben kam danach und lief in den geschlossenen Handle.
**Fix:** `db.close()` entfernt, Statistik + Historie teilen sich die Verbindung; Schließen
jetzt in `finally` mit Exception-Guard.
**Verifikation:** Export-Run schreibt Historie wieder (3 Snapshots, Δ 06.09. +125,54 MW
korrekt in `dist/assets/historie.json`).


## F-HIST-SNAP-MERGE (12.09.2026, V44/AP4) — doppelter Snapshot 06.09 in der Daten-Verlauf

**Symptom:** Tabelle "Daten-Verlauf" zeigte 06.09. zweimal (unterschiedliche Zahlen: 53.419 vs 53.413).
**Ursache:** Snapshot #10 entstand vormittags am 06.09. (Legacy-Import, vor V37/V42-Korrektur);
#15 wurde am 12.09. von sync_legacy.py als "Alter Stand"-Sicherung mit Datum 06.09 angelegt (korrigiert).
**Fix:** `scripts/fix_snapshot_merge_0906.py` — #15 bleibt als DER 06.09-Eintrag, #10 + Referenzen
gelöscht (User-Entscheid). Idempotent; Backup-Pflicht; build_historie rechnet Deltas neu.
**Prävention:** sync_legacy.py nutzt save_snapshot() mit V30-Dedup (identische Zahlen → kein Duplikat);
bei unterschiedlichen Zahlen am selben Tag greift der Dedup bewusst NICHT (echte Kennzahlen-Änderung).

## F-COMBO-UMLAUT (12.09.2026, V44/AP3) — Combo-Suche: Umlaut-Terme matchen nicht

**Symptom:** Landkreis-Suche „börde+havelland" fand nur Havelland (stummer 0-Treffer für Börde).
**Ursache:** matchesCombo erhielt `r.lk.toLowerCase()` statt `norm(r.lk)` — parseComboQuery normiert
Terme via norm() (ä→a), aber rohe toLowerCase()-Namen behalten Umlaute → 'börde' enthält 'borde' NICHT.
**Fix:** In renderLandkreise() wird jetzt `norm(r.lk)` übergeben. Regel: Combo-Match-Input IMMER
normiert übergeben (die 3 anderen Tabs nutzten bereits norm()).


## F-HIST-NICEMAX (12.09.2026, V45) — ReferenceError: niceMax is not defined

**Symptom:** renderHistorieCharts warf ReferenceError → Charts leer (html_len 0).
**Ursache:** Beim V45-Refactor von buildChart (Skala minLeft+step) wurde die niceMax-Definition
aus dem Function-Body entfernt, obwohl sie für die rechte Delta-Achse weiterhin gebraucht wird.
**Fix:** niceMax wieder in renderHistorieCharts definieren. **Prävention:** Bei Refactor
innerhalb einer Funktion `node --check` (fängt ReferenceError NICHT!) reicht nicht — immer
Browser-Smoke-Test (Rendern + JS-Errors abfangen) nach jedem Build.

## F-MOBIL-TOGGLE-UNSICHTBAR (12.09.2026, V44→V45) — Toggle-Button verschwand beim Einklappen

**Symptom (User-Meldung):** Auf dem Smartphone war nach dem Ausblenden des Filter-Panels der
Toggle-Button nicht mehr auffindbar — Funktion unbenutzbar.
**Root-Cause:** #toolbar-toggle hing `position:absolute; bottom:48px` im Karten-Container;
beim Einklappen rutschte der Kartenausschnitt/die Attribution darüber, Button außer Sichtweite.
**Fix (V45):** `position:fixed; bottom:10px; z-index:1250` (Bottom-Bar, immer sichtbar) +
Filter-Panel mobil als Overlay (`position:fixed; bottom:52px; max-height:62vh; scroll`).
**Prävention:** Mobile-Fixes immer im echten Mobile-Viewport testen (nicht nur Desktop-Emulation).


## F-MOBIL-KASKADE (12.09.2026, V46) — Mobil-Toggle auf Smartphone komplett unsichtbar (V44+V45)

**Symptom (User, 2× gemeldet):** „Ich sehe gar keine Filter auf meinem Smartphone und auch keinen
Toggle-Button." — Nach V44 (absolute-Positionierung) UND nochmal nach V45 (fixed Bottom-Bar)!
**Root-Cause (erst V46 gefunden):** CSS-Kaskade, NICHT Positionierung. Der Mobile-Media-Block
(≤767px) stand im Stylesheet VOR den Basis-Regeln `#toolbar-toggle { display:none }` und
`#toolbar { position:absolute }`. Media Queries erhöhen die Spezifität NICHT (0,1,0 == 0,1,0) →
die später im Quelltext stehende Basis-Regel gewinnt AUF ALLEN GERÄTEN. Der fixed-Button war also
technisch da — aber auf display:none. V45s Browser-Test verpasste es: Desktop-Viewport +
CSSOM-Regel-Existenz-Check, aber keine Kaskaden-/Spezifitäts-Prüfung.
**Fix (V46):** Mobile-Regeln mit body-Präfix im Media-Block (`body #toolbar-toggle`,
`body #toolbar`, `body.toolbar-hidden #toolbar`) → Spezifität 0,1,1 > 0,1,0, unabhängig von der
Quelltext-Reihenfolge. Beweis: CSSOM-Zeiger auf die body-Präfix-Regeln im 767er-Media-Block
(Multi UND Singlefile) + computed-style-Simulation (fixed/inline-block) + Desktop bleibt none.
**Prävention (dauerhaft):** Bei JEDEM Media-Query-Override: Spezifität gegen die zu überschreibende
Basis-Regel prüfen. Wenn Basis-Regel und Override denselben Selektor haben, entweder (a) body-
Präfix im Override ODER (b) Media-Block ans ENDE des Stylesheets verschieben. Ein „Regel existiert
im CSSOM"-Check allein reicht NICHT — die Kaskade entscheidet, nicht die Existenz.


## F-STICKY-CONTEXT (12.09.2026, V47) — Sticky-Table-Header stickt nicht

**Symptom:** Landkreis-Header blieb beim vertikalen Scrollen nicht stehen (Betreiber/Hersteller/Typ
taten es, obwohl identisches CSS).
**Root-Cause:** `position:sticky` wirkt nur innerhalb des NÄCHSTEN Scroll-Containers.
`#landkreis-scroll` hatte `overflow-x:scroll` (V32 horizontal) — das macht den Container zum
Clip-Context, aber OHNE eigene Höhe scrollt er nicht vertikal → der Header stickt ins Leere.
Betreiber/Hersteller/Typ scrollen dagegen im #stats-body → dort funktioniert top-sticky.
**Fix:** `#landkreis-scroll { overflow-y:auto; max-height:calc(100vh - 300px); }` (NAP-Muster
#nap-table-wrap). first-child z-index 3→4 (link-sticky V32 + top-sticky kombinieren).
**Prävention:** Vor sticky top:0 prüfen: WELCHER Container scrollt vertikal? Hat er eine
begrenzte Höhe? Sticky braucht Scroll-Context mit begrenzter Höhe unmittelbar über der Tabelle.


## F-TDZ-GLOBALS (13.09.2026, V48) — Neue globale let-Variablen VOR aller Nutzung deklarieren

**Kontext:** V48/AP5 führte `_lastStatsRows` als globales `let` ein. Erste Deklaration stand in
der Helfer-Sektion (~Zeile 5600), erste NUTZUNG aber in renderBetreiber (~4400) — die
Renderfunktionen laufen je nach Reihenfolge/Tab VOR der Deklaration → ReferenceError (TDZ).
Bekanntes Muster im Projekt (siehe V32.1-Fix-Kommentar bei Zeile ~2413): Der Singlefile ruft
init() SYNCHRON mit eingebetteten Daten — alles was init/renderXXX lesen muss, muss VOR dem
Script-Teil deklariert sein, der init() aufruft.
**Fix:** Deklaration zu den anderen globalen States (~2417) verschoben.
**Prävention:** Neue globale Variablen, die in Renderfunktionen gelesen werden, IMMER im
State-Block oben (~Zeile 2410–2420) deklarieren — nie in Funktionsnähe.


## F-COMBO-DIAGRAMME (13.09.2026, V50) — Operator-Queries in abgeleiteten Auswertungen durchreichen

**Symptom:** Betreiber-Tab, 📈-Diagramme zeigten bei kombinierten Suchen („rwe/vestas")
„Keine Treffer für den Suchtext", obwohl die Tabelle korrekt filterte.
**Root-Cause:** `_betreiberScopeUnits()` (V35) matchte mit `norm(u.ab).includes(nf)` über den
ROHEN Suchstring — Operatoren sind keine Literalbestandteile von Betreibernamen → 0 Treffer.
Die Tabelle nutzte seit V44/AP3 `parseComboQuery` + `matchesCombo`; der Diagramm-Scope war
bei der V44-Combo-Einführung nicht mitgepflegt worden.
**Fix:** V50/AP1 — Scope-Funktion prüft zuerst `parseComboQuery(rawQ)`; bei Combo-Query
tabellenidentisches `matchesCombo(norm(u.ab), combo)`, Gruppen-Pfad entfällt sinnvollerweise
(Operatoren sind keine Namensteile). Einfach-Queries/Gruppen unverändert (Regression grün).
**Prävention:** Wann immer ein neuer Matching-Mechanismus (Operatoren, Normalisierung) in
eine Tabellen-Renderfunktion eingebaut wird, ALLE davon abgeleiteten Auswertungen
(Diagramme, Map-Button, Exporte) auf den gleichen Mechanismus prüfen — am besten über eine
gemeinsame Helper-Funktion statt kopiertem Match-Code.

### F-LADEPROGRESS-1. „LIVE lädt keinerlei Daten, funktioniert nichts" (BEHOBEN 19.09.2026, V51.2)
**Fehlerbild:** User rief die LIVE-Karte auf — „es laden keinerlei Daten der Assets und es
funktioniert einfach nichts." Infobar hing auf „Lade Daten…".
**Diagnose (15 Headless-Chromium-Läufe):** Kein Code-Bug, kein Deploy-Fehler. Alle Assets
HTTP 200 + SHA-identisch mit lokal; einheiten.json (39,2 MB, gzip 5,3 MB) vollständig
ladbar; nach Wartezeit 65.819 Units + 46 Cluster im DOM. **Root-Cause: Kein Lade-Feedback**
— bei schwacher Anbindung (1,5 Mbit: 48 s · 0,5 Mbit: 93 s · 0,25 Mbit: 183 s gemessen,
CDP-Throttling) stand die Infobar minutenlang nur auf „Lade Daten…" → Abbruch im Warteraum.
**Fix (V51.2):** (1) Progress-fähiger Fetch via ReadableStream — Infobar zeigt „Lade
Daten… N MB / M MB (P %)", nach der gzip-Grenze „wird entpackt…"; (2) Slim-Export
(lat/lon 5 Dezimalen ≈ 1,1 m, mw 4 Dezimalen, leere Felder weg, kompakte Separatoren)
→ 39,2 → 34,7 MB; (3) 1 automatischer Retry nach 3 s bei Netzfehler.
**Pitfall (live erwischt):** GitHub Pages sendet Content-Length = **gzip-Größe** (~15 % des
Originals), ReadableStream-`received` zählt bereits dekomprimierte Bytes → naive
Prozent-Rechnung läuft auf 500 %+ hoch. Fix: Prozent nur solange received ≤ total,
danach „wird entpackt…"-Anzeige. **Prävention:** Lade-UX immer mit throttled Netz testen
(CDP `Network.emulateNetworkConditions`), nicht nur mit schneller lokaler Leitung — der
Bug war auf der schnellen Dev-Leitung unsichtbar (2 s Ladezeit, Progress nie sichtbar).

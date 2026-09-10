# V34 — 20-Punkte-Plan: Scrollbar oben (WP1), Popup-Re-Open-Bug (WP2), Panel 20 % breiter (WP3), Doku (WP4)

**Datum:** 09.09.2026 · **Basis:** V33.1 · **User-Auftrag:** 3 Arbeitspakete + Doku-Update,
20-Punkte-Plan (Recherche → Planung → Umsetzung → Überprüfung), revisionierte klickbare HTML
im Chat, **KEIN autonomer Push** (nur nach expliziter Freigabe).

## A · Recherche (P1–P6)
- **P1 (WP1):** LK-Scrollbalken V33: `#landkreis-scroll` (overflow-x:scroll, 14 px Balken,
  Kontrast #475569/#cbd5e1, sticky Name-Spalte) — Container liegt UNTER dem Hinweistext.
  Verifiziert 769 px vs. 1.024 px Tabellenbreite.
- **P2 (WP2-Repro im Browser):** DOM-Klick auf Bestands-Marker: `click`-Event feuert am
  Marker, aber Popup geht nicht auf → **Doppel-Dispatch**: `_lazyPopup` (App) und
  Leaflet-`_openPopup` (von `bindPopup`) laufen BEIDE. Leaflet togglet: offen→close.
  Mischbetrieb `marker.bindPopup()` + `map.openPopup(m.getPopup())` erzeugt Race-Zustände
  (`map._popup` stale, `_source`-Verschiebung). Einzelteile verifiziert: `map.openPopup(pop)`
  öffnet ✓, `mk.openPopup(latlng)` öffnet ✓, aber Kette aus beiden + Toggle = Klick tot.
- **P3 (WP2-Historie):** V21.4/V32-Kommentare im Lazy-Pfad dokumentieren die Cluster-Quirks
  („leeres Popup bei marker.openPopup bei cluster-verwalteten Markern" → deshalb
  map.openPopup). Fix muss beide Fälle (Cluster + Plain) sauber lösen.
- **P4 (WP3):** `#stats-panel`: width 820 px / right:-860 px (Desktop), Tablet 560 px,
  mobil 100 vw. 20 % breiter: 820→984 px, right-Offset muss mitziehen (860→1024).
- **P5:** Topbar 320 px, Panel z-Index 1800 (V33) — breiteres Panel überdeckt Topbar weiter,
  das ist gewollt (V33 WP2).
- **P6:** Leaflet-Quellanalyse: `bindPopup` registriert `click→_openPopup` am Marker;
  `_openPopup` ist ein Toggle (hasLayer → closePopup).

## B · Planung (P7–P9)
- **P7 (WP2-Fix-Design):** Ein einziger Klick-Handler pro Marker. Kein `marker.bindPopup()`
  mehr im Lazy-Pfad (damit Leaflet-_openPopup nie registriert wird). Stattdessen:
  eigenes `L.popup({maxWidth: 420})` beim ersten Klick bauen (Content = buildPopup(u)),
  `_lazyPopup` togglet selbst: offen → close, zu → setLatLng + openOn(map). Cluster-Quirk
  bleibt gelöst (map.openPopup-Äquivalent via popup.openOn(map), kein marker.openPopup).
- **P8 (WP1-Design):** Scroll-Container `#landkreis-scroll` per CSS `position:sticky;
  bottom:0` fixieren geht nicht (Balken würde in Tabelle rutschen). Stattdessen DOM-Umzug:
  `#landkreis-scroll` (nur der Scrollbalken-Träger) bleibt, aber die Tabelle erhält
  `margin-bottom:-Xpx`-Trick nein — **sauber:** Scrollbalken-Element `#landkreis-scroll`
  wird ein LEERER Container (height:16px, overflow-x:scroll) OBERHALB der Tabelle, der per
  JS `scrollLeft` mit der Tabelle synchronisiert; Tabelle bekommt eigenen versteckten
  Balken (scrollbar-width:none). → Klassisches „synthetic scrollbar above table"-Pattern.
- **P9 (WP3-Design):** width 820→984 px, right:-860→-1024 px; `.stats-body`/Tabellenbreiten
  prüfen (landkreis-scroll passt sich an); Tablet/Mobil-Queries unverändert.

## C · Umsetzung (P10–P16)
- **P10 (WP1):** DOM: leeren `#landkreis-scroll-bar`-Div oberhalb der Tabelle einfügen +
  CSS (16 px, gleiche Farben wie bisher, `overflow-x:scroll`); Tabelle: eigener Balken via
  `scrollbar-width:none` + `::-webkit-scrollbar{display:none}`; JS-Sync (scroll-Event
  bidirektional, synchron bei render/init).
- **P11 (WP2):** `_bindLazyPopup` umschreiben: kein `bindPopup` → eigenes `L.popup`
  (closeButton, autoClose:false damit Kartenklick NICHT Leaflet-intern kollidiert? —
  NEIN: autoClose:true lassen, Kartenklick schließt via Leaflet preclick; Toggle nur bei
  Marker-Klick) + Re-Open jederzeit möglich (Zustand `pop._map` prüfen).
- **P12 (WP2):** NAP-Link-Handler (V21.4 contentupdate-Delegation) in den neuen
  Popup-Erzeugungspfad übernehmen (kein Funktionsverlust).
- **P13 (WP3):** CSS width/right anpassen + Kommentar.
- **P14:** Rebuild Multi+Single, JS-Syntaxcheck (node --check der Inline-Blöcke).
- **P15:** Smoke-Test Singlefile (Marker rendern, kein Fehler beim Laden — TDZ-Regel).
- **P16:** Kopien: `iterations/V34_UX_Runde2.html` + human-share.

## D · Überprüfung (P17–P20)
- **P17 (WP1):** Browser: Scrollbalken OBERHALB der Tabelle sichtbar, Scroll-Sync läuft
  (scrollLeft-Test), unterhalb KEIN Balken mehr, letzte Spalte erreichbar.
- **P18 (WP2):** User-Szenario exakt: Klick → Popup ✓ · Kartenklick → zu ✓ · erneuter
  Klick auf dasselbe Asset → Popup WIEDER da ✓ · mehrfach wiederholt ✓ · auch im
  BFF-Anzeigen-Modus (Plain-Layer) ✓ · NAP-Link im Popup funktioniert ✓.
- **P19 (WP3 + Regression):** Panelbreite ~984 px (getBoundingClientRect), Panel deckt
  Topbar (V33-Verhalten bleibt), LK-Scroll im breiteren Panel, NB-Filter, Historie-Δ.
- **P20 (WP4):** Doku as-built (PROJEKTSTAND, fehlerbehebung F-V34-…, architektur) +
  Lieferung revisionierter HTML im Chat. Kein Push.

**Risiken/Pitfalls:**
- WP1-Sync-Loop-Gefahr (scroll-Events gegenseitig triggern) → Flag `._syncing`.
- WP2: `autoClose:true` + eigener Toggle kann Doppel-Close auslösen → Toggle nur im
  Marker-Handler, Kartenklick macht nur Leaflet-Close (kein eigener map-Listener).
- WP3: 984 px + max-width:94vw — auf kleinen Screens greift weiter max-width.

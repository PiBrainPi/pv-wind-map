# V32.1 — 20-Punkte-Prüfplan: Singlefile-Marker initial nicht sichtbar + Statistik-Button

**Datum:** 09.09.2026 · **Anlass:** User-Meldung: Beim Öffnen der Singlefile-Datei werden Anlagen
erst nach Filter setzen+entfernen angezeigt; „Statistik"-Button weiterhin ohne Reaktion.
**Bisheriger Blind Spot:** Alle bisherigen Browser-Tests liefen gegen `dist/index.html` (Multi-File,
http.server) — die **Singlefile** wurde nie im Browser verifiziert. Der User öffnet aber die Singlefile
(doppelt geklickt, ggf. sogar via `file://`).

## Phase A — Reproduktion (Singlefile, echte Öffn-Situation)

1. HTTP-Server auf `dist/` starten; `index_singlefile.html` mit Cache-Busting öffnen.
2. Consent akzeptieren, auf Daten-Load warten (`Wind ·` in Infobar).
3. **Ist-Check Marker:** `.marker-cluster`-Anzahl sofort nach Load zählen (Bug: 0 erwartet).
4. Konsolen-/JS-Fehler einsammeln (`window.__auditErrors`, uncaught exceptions).
5. Daten-Embedding prüfen: `typeof window.__PVWIND_DATA__`, Länge, `__PVWIND_META__`, `__PVWIND_STATS__`, `__PVWIND_NAP_RANKING__`.
6. `_lastFiltered`-Länge prüfen (wurde `renderMarkers()` initial überhaupt mit Daten gerufen?).
7. `clusterGroup.getLayers().length` vs. DOM — Layer da, aber nicht gerendert?
8. `file://`-Kontext replizieren (Browser-Navigation auf `file://…index_singlefile.html`) — localStorage/Consent-Verhalten dort prüfen.
9. **Statistik-Button im Singlefile:** Klick → Reaktion? Bei offenem Panel `elementFromPoint` auf Button-Position (welches Element fängt den Klick?).
10. `tile-consent`/`tile-hint`-Overlays: z-index + Geometrie — verdecken sie Topbar/Buttons dauerhaft?

## Phase B — Ursachenanalyse

11. `bundle_singlefile.py`-Reihenfolge prüfen: liegen Data-Embeds **vor** dem Haupt-Script? Ist init() an DOMContentLoaded gebunden oder immediate?
12. `init()`-Initialpfad: `renderMarkers(einheiten)`-Aufruf analysieren (volle 65.673-Liste inkl. koordinatenloser Einheiten?) vs. `applyFilters()` (53.413 bs35 mit Koordinaten).
13. Root-Cause(s) fixieren und dokumentieren (Marker-Bug + Button-Bug, jeweils Singlefile-Kontext).

## Phase C — Patch (autonom)

14. `src/index.html` patchen: Initial-Render robust machen (nach Datenload `applyFilters()`-äquivalent mit gefilterter bs35-Menge statt Rohliste; bzw. Root-Cause-Fix).
15. Statistik-Button:falls singlefile-spezifische Überlappung/Overlay-Ursache → Overlay-/z-index-/Handler-Fix.
16. Falls `bundle_singlefile.py`-Reihenfolge schuld: Bundle-Script korrigieren.
17. Rebuild: `cp src/index.html dist/index.html && python3 scripts/bundle_singlefile.py`.

## Phase D — Verifikation (Singlefile!)

18. Browser-Check Singlefile: Marker **ohne** Filter-Interaktion sofort sichtbar; Statistik-Button öffnet UND schließt; 0 JS-Fehler.
19. Regressionen: NAP-Ranking im Singlefile geladen (27.130 NAPs), NAP-Klick → Kartenfokus, NB-Filter (Avacon 5.184), BFF-Anzeigen-Modus, LK-Scroll.
20. Kopien nach `iterations/` + `~/hermes_human-share/`, revisionierte Datei im Chat liefern (kein Push).

**Status:** Umsetzung läuft (autonom gemäß Freigabe).

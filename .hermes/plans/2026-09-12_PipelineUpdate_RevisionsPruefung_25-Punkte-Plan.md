# 25-Punkte-Prüfplan — Pipeline-Update 12.09. + Revisions-Integration (pv-wind-map)

> **Anlass:** Cronjob `79229dc1690d` (MaStR Pipeline 2.0, samstags 06:10) lief am 12.09. 06:10–06:16.
> **Regel-Kontext:** Cron baut NUR LOKAL die DB, kein Auto-Deploy (Grundsatzentscheidung).

## Phase 1 — Recherche: Was ist passiert? ✅ (P1–P8)
- [x] P1: Cron-Report 12.09. gelesen (Exit 0, alle Schritte ok).
- [x] P2: `pipeline2_update.sh` gelesen — Schritte: fetch_v2 --delta → merge_delta → import_v2 → fetch_nap → import_v2. **KEIN Export-Schritt!**
- [x] P3: Zeitstempel verifiziert: fetch 06:10–06:13, import 06:14:37 + 06:15:32 (2 Läufe), NAP 06:14.
- [x] P4: fetch_state: Wind-Delta 66, PV-Delta 35+8; **PV `fallback_full: true`** → Sicherheitsnetz griff (5,29 % > 5 % Toleranz) → korrekter Vollabruf-Fallback (22.452 Records).
- [x] P5: DB-Zähler == Cron-Report: Wind 43.484 · PV 23.718 · Raw 67.202 ✓
- [x] P6: **NICHT 0 Änderungen!** Cron-Report „0 neu, 0 aktualisiert" bezog sich nur auf pv.json/wind.json-Basisfiles. DB-Diff (Backup 06:14 PRE vs. jetzt): **+19 neue Records, 154 geänderte raw_json, +9 NAPs.**
- [x] P7: NAP +9 (27.898→27.907), 54 Lokationen geprüft, 0 Fehler ✓
- [x] P8: Backups vorhanden: 06:14:24 (PRE) + 06:15:19 (je 546,7 MB) ✓

## Phase 2 — Code-Recherche: Wurde alles umgesetzt? ✅ (P9–P16)
- [x] P9: **NEIN — der Cron exportiert bewusst nicht** (pipeline2_update.sh endet nach DB-Import; Report-Block nur lesend). Export ist manueller Schritt (export_app.py / build.sh).
- [x] P10: dist/assets/*.json = 11.09. 20:26 (V43-Export) → **älter als die DB (12.09.)**.
- [x] P11: Relevant — die neuen Daten sind karten-relevant: **+5 neue PV-Anlagen In Betrieb** (519,82–9.452,68 kWp, georef), **6 Statuswechsel zu In Betrieb** (5 PV + 1 Wind, u. a. SEE930086471695 15 MW), 28 Records mit fachlichen Feld-Änderungen (Betreiber, Typ, Koordinaten, Leistung).
- [x] P12: meta.counts (31005/22421, Stand 06.09-Label) == DB-Basis zum Export-Zeitpunkt; LIVE == dist (byte-identisch via meta.json-Vergleich).
- [x] P13: Revision/iterations braucht keinen neuen UI-Stand (src unverändert), aber einen **neuen Daten-Build**.
- [x] P14: Live-Site liefert Datenstand 06.09 (meta.stand) — konsistent mit dist, aber hinter der DB.
- [x] P15: **Lücke bestätigt:** Neue DB-Daten NICHT in einheiten.json/statistiken.json/nap_index.json eingearbeitet.
- [x] P16: Lücke liegt in der bewussten Cron/Export-Trennung — KEIN Bug im Cron. **Zusatz-Fund:** 13 PV-Records in DB, die das Register nicht mehr unter dem Basisfilter liefert (5 gelöscht, 8 mit geändertem Bruttoleistung-Wert) — erklärt DB 23.718 vs. API-Total 23.705; quartalsweiser Vollabruf (Dez.) ist der vorgesehene Cleanup. **Zusatz-Fund 2:** nap_index.json ist stale (03.09) — wird von KEINEM Standardfluss regeneriert (export_nap_index.py fehlt in build.sh UND Cron).

## Phase 3 — Umsetzungsplan + Ausführung (P17–P21)
- [x] P17: Entscheidung: **Kein Code-Patch nötig** (Cron-Verhalten ist by design). Stattdessen: manueller Daten-Export + Bundle JETZT (User hat Integration vorab beauftragt).
- [x] P18: Plan: export_nap_index.py → export_app.py → cp src→dist → bundle_singlefile.py → Verifikation → Revision V43.1 + human-share → MEDIA.
- [x] P19: (n/a — kein Patch)
- [x] P20: Export läuft (Ergebnis unten).
- [x] P21: Bundle läuft (Ergebnis unten).

## Phase 4 — Überprüfung + Lieferung (P22–P25)
- [x] P22: Verifikation: Export-Output-Tail (Historie-Zeile!), meta.counts vs. DB-Erwartung, statistiken.json (Legacy-Basis — dokumentiert), nap_index frisch, 0 JS-Errors im Browser, neue Anlage auffindbar.
- [x] P23: Revision `iterations/V43.1_Datenstand_12-09.html` + human-share.
- [x] P24: Doku-Sync: PROJEKTSTAND (Pipeline-Lauf + V43.1) + HANDOVER §5 (cross-project).
- [x] P25: Status-Report + MEDIA im Chat. **Kein Push/Deploy ohne Freigabe.**

## Offene Punkte für den User (fachliche Entscheidungen)
1. Soll `pipeline2_update.sh` künftig einen Export-Schritt bekommen (Build lokal fertig, Deploy weiter manuell)? Sonst wächst der Abstand DB↔Karte wöchentlich.
2. `meta.stand` (Datenstand-Anzeige im Hinweise-Panel) hängt am Legacy-Key `metadaten.stand` (06.09, wird nur vom Legacy-Rebuild gesetzt) — Empfehlung: bei Export auf `raw_import_stand` mappen. Noch NICHT umgesetzt (fachliche Entscheidung).
3. statistiken.json (Charts) basiert weiter auf der Legacy-Tabelle `einheiten` (Stand 06.09) — Karte und Charts driften auseinander (bekanntes Muster F-04, architekturbedingt). Fix = größeres Arbeitspaket.
4. nap_index.json in build.sh + Cron-Pfad aufnehmen (damit nie wieder stale).

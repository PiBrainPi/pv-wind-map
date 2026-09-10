# Fix-Pläne V30 — 10-Punkte-Pläne je Finding (F-01 … F-08)

> **Datum:** 2026-09-08 · **Basis:** `BUGS_ZU_ERLEDIGEN_2026-09-08.md` · Basis-Stand V29.1
> **Vorgehen:** ID für ID, Reihenfolge: F-01 → F-05 → F-06 → F-08 → F-04 → F-02 → F-03 → F-07.
> Nach jeder ID: kurzer Statusreport im Chat; nächste ID erst nach User-Freigabe.
> Am Ende: revisionierte klickbare HTML (V30) im Chat. **Kein Push/Deploy ohne Freigabe.**
> Phasen je Plan: R = Recherche · P = Planung · U = Umsetzung · T = Test/Prüfung

---

## F-01 — Overlay: Spannungsfilter + Leistungsbasis (Dual-State)

1. **R:** Exakte Code-Stellen extrahieren: `showAllUnits()` gr-Block + fehlender se-Block; `applyFilters()` als Referenz (se-Block, grBasis-Block) wörtlich auslesen.
2. **R:** Prüfen, ob im Overlay-HTML (`all-units-*`) bereits Meta-Badge-Struktur für Filterhinweise existiert.
3. **P:** Patch-Spezifik: se-Filter 1:1 spiegeln; gr-Filter auf `(usePark ? (u.pkmw ?? u.mw) : u.mw)` umstellen (grBasis-Element-Read wie in applyFilters, mit Fallback 'park').
4. **P:** Repro-Fälle definieren: (a) se=Hochspannung → Overlay-Meta == Kartenbasis; (b) gr=100–150 → Overlay-Zeilen == Karten-Marker-Logik (Park-Basis).
5. **U:** Atomares Patch-Skript (asserts auf alte Texte, EIN write), beide Änderungen in einem Lauf.
6. **U:** Anker-Grep-Verifikation: `filter-se` in showAllUnits UND pkmw-Fallback in showAllUnits zählen (jeder Anker ≥1, HTML/JS getrennt).
7. **U:** `cp src/index.html dist/index.html` + `bundle_singlefile.py`.
8. **T:** Browser-Verifikation lokal (Cache-Buster): Fall (a) und (b) mit DOM-Messung (Meta-Text, Zeilenzahl).
9. **T:** JS-Error-Wächter über beide Repro-Läufe (muss leer bleiben) + F5-Regression.
10. **T:** Revision `iterations/V30_F01_DualStateFix.html` + human-share-Kopie; Eintrag in BUGS-Datei (Status: gefixt/verifiziert).

## F-05 — Overlay: TT.MM.JJJJ

1. **R:** `dateFullFmt()` + `_parseMaStrDate()` Semantik bestätigen (leere/Fehlwerte → „—").
2. **R:** Alle Datumsspalten im Overlay identifizieren (reg, inb) + eventuelle weitere ISO-Stellen (hist-detail?).
3. **P:** Ersetzen beider ISO-Wandlungen in `_renderTableRows()` durch `dateFullFmt(u.reg) || '\u2014'` / `dateFullFmt(u.inb) || '\u2014'`.
4. **P:** Edge-Cases: `/Date(-…)/` (negativ), fehlendes Datum, `null` — Verhalten festlegen („—").
5. **U:** Atomares Patch-Skript mit asserts (genau 2 Ersetzungen).
6. **U:** Anker-Grep: `dateFullFmt(u.reg)`/`dateFullFmt(u.inb)` in `_renderTableRows` vorhanden, alte ISO-Zeilen weg.
7. **U:** Build (cp + bundle).
8. **T:** Browser: Overlay öffnen, erste Zeile → Datum als TT.MM.JJJJ messen (DOM-Text-Assert).
9. **T:** Popup-Datum unverändert TT.MM.JJJJ (Regression), kein JS-Error.
10. **T:** Revision `V30_F05_DatumOverlay.html` + human-share + BUGS-Status.

## F-06 — Historie-Hinweistext

1. **R:** Exakte Textstelle in src/index.html lokalisieren („1. & 15. des Monats").
2. **R:** Andere Vorkommen falscher Rhythmus-Angaben greppen (docs, UI, Artikel).
3. **P:** Neuer Text: „Beim nächsten Daten-Update (sonntags 18:00) …" — Länge ähnlich, kein Layout-Impact.
4. **P:** Entscheidung dokumentieren (Cron 79229dc1690d, sonntags 18:00).
5. **U:** Atomarer Patch (1 Ersetzung, assert).
6. **U:** Grep: alter Text 0×, neuer Text 1× in src+dist.
7. **U:** Build (cp + bundle).
8. **T:** DOM-Assert: Text im leeren Historie-Zustand korrekt (Tab leeren via JS-Check der Funktion).
9. **T:** JS-Error-Wächter + Tab-Wechsel-Regression.
10. **T:** Revision + human-share + BUGS-Status.

## F-08 — Tab-Zählung Doku (10 Tabs)

1. **R:** Alle Doku-Stellen mit „9 Tabs"/„9 Tabs" greppen (PROJEKTSTAND, ROADMAP, statistik.md, README, Skill).
2. **R:** Tatsächliche Zählung DOM-verifizieren (10) und als Referenz dokumentieren.
3. **P:** Liste der zu ändernden Zeilen je Datei.
4. **P:** Zukunftssicher: Zählung als „10 Tabs (V28: NAP-Ranking)" ausdrücken.
5. **U:** Doku-Edits (patch je Datei).
6. **U:** Grep-Verifikation: „9 Tabs" 0× in Doku; „10 Tabs" konsistent.
7. **U:** Kein Build nötig (nur Doku) — aber src-Änderungen der Runde unberührt lassen.
8. **T:** Gegenprobe: DOM-Count == Doku-Angabe.
9. **T:** BUGS-Datei-Status für F-08 aktualisieren.
10. **T:** Statusreport (Doku-only, kein Commit ohne Freigabe).

## F-04 — Zahlendrift (0,4999-MWp-Grenzfälle + Doku-Kopf)

1. **R:** Alle 11 PV-0,4999 + 1 Wind-Grenzfall in DB einsehen (Namen, MW, Status).
2. **P:** ⚠ User-Entscheid: Grenzfälle IN die Abgrenzung (>=0,495 gerundet) oder RAUS (auch aus einheiten.json)? → clarify vor Umsetzung.
3. **P:** Auswirkung auf Zahlen je Variante rechnen (53.424 vs 53.419 etc., Doku-Zahlen ableiten).
4. **P:** Fix-Ort Pipeline (`export_app.py` build_units-Grenze) + Meta-Counts aus EINEM Zähler.
5. **U:** export_app.py anpassen (eine Quelle für Infobar/Meta/JSON).
6. **U:** Re-Export (Build), Assets + Single-File neu.
7. **T:** JSON-Count == Meta-Count == Infobar (DOM-Assert), Döllen-Regression.
8. **T:** PROJEKTSTAND-Kopf + statistik.md Zahlen as-built anpassen (nach T-Ergebnis).
9. **T:** Artikel-Fact-Check-Notiz: Zahlen geändert → Artikel-V30-Hinweis (User-Pflicht).
10. **T:** Revision `V30_F04_*.html` + human-share + BUGS-Status.

## F-02 — bs35-Gate an 6 Klick-Quellen ⚠ braucht User-Entscheid VOR Umsetzung

1. **R:** ⚠ Frage an User: sollen Betreiber-/Hersteller-/LK-/NAP-Klicks nur In-Betrieb zeigen? (Optionen: nur bs35 / alle Status + Badge „+X Planung" / Status quo + nur Doku.)
2. **R:** Je Klick-Quelle die Datenlage (Wie viele bs31/38/37 treffer je Beispiel) bereits dokumentiert (RWE 726/558).
3. **P:** Variante A (Gate überall): 6 Filterstellen um `if ((u.bs||35)!==35) return false;` erweitern, konsistent mit V29-Größenklick.
4. **P:** Variante B (Badge): zusätzlich UI-Badge im Kartenlabel „+X weitere (Planung…)" — Aufwand höher.
5. **U:** Patch je Quelle (atomar, asserts) — erst nach User-Wahl.
6. **U:** Anker-Grep je Quelle (6 Gates).
7. **U:** Build (cp + bundle).
8. **T:** Browser je Quelle: rwe → 558 (A) bzw. 726+Badge (B); Größen-Klick-Regression (104–150 = 2).
9. **T:** JS-Errors leer; F5-Regression.
10. **T:** Revision + human-share + BUGS-Status.

## F-03 — snapshot.py Duplikate (Pipeline)

1. **R:** snapshot.py Append-Logik lesen; historie.json-Erzeugung + bestehende Duplikate inventarisieren.
2. **R:** Prüfen, ob Rebuilds im Cron-Kontext Duplikate erzeugen (Sonntags-Lauf, V29-Befund).
3. **P:** Fix: vor Append nach `datum` suchen → überschreiben statt anhängen (UPSERT-Semantik).
4. **P:** Bestehende historie.json NICHT löschen (Regel 1) — Frontend-Dedup bleibt Sicherheitsnetz.
5. **U:** snapshot.py patchen (asserts).
6. **U:** DB-Backup vor Test-Lauf (`~/backups/mastr.db.<date>.preF03.bak`).
7. **U:** Test-Lauf snapshot.py lokal → historie.json erneut prüfen (kein neues Duplikat).
8. **T:** Diff historie.json vor/nach: nur Snapshot-Aktualisierung, keine Datenverluste (Regel 1).
9. **T:** Frontend: Historie-Tab + Betroffenheit „letztes Update" unverändert funktional.
10. **T:** BUGS-Status; Doku update.md § Pipeline um UPSERT-Verhalten ergänzen.

## F-07 — Freeze Betroffenheits-Tab (beobachten)

1. **R:** Kein Repro (2 ms in Lauf 2) — kein Code-Fix ohne Repro (Systematik-Regel).
2. **P:** Beobachtungsplan: bei jeder künftigen Runde Betroffenheits-Klick mit Timing messen (performance.now()).
3. **P:** Long-Task-Diagnose-Snippet vorbereiten (PerformanceObserver) für den Repro-Fall.
4. **U:** Keine Code-Änderung in V30.
5. **U:** Timing-Messung in dieser Fix-Runde einmal ausführen (Baseline dokumentieren).
6. **T:** Baseline-Ergebnis in BUGS-Datei notieren (2 ms, kein Error).
7. **T:** Falls Freeze in 3 Runden nicht mehr auftritt → als Einzalfall schließen (mit User abstimmen).
8. **T:** Bei Auftreten: Repro-Schritte + Long-Task-Trace in BUGS-Datei, dann Fix-Runde.
9. **T:** Kein Build, keine Revision für F-07.
10. **T:** Status „beobachten" in BUGS-Datei + Statusreport.

---

## Sammel-Abschluss nach allen IDs
- Revision `iterations/V30_FixRunde1_<Thema>.html` + Kopie human-share
- Klickbare HTML im Chat (MEDIA:)
- Doku as-built gesamt (PROJEKTSTAND, ROADMAP, statistik.md, ENTSCHEIDUNGEN, BUGS-Datei-Status je ID)
- Commit/Deploy NUR nach expliziter User-Freigabe
# V35.1 — 20-Punkte-Plan: Donuts measure-steuerbar (Anlagen ⇄ Leistung MW)

> Datum 2026-09-10 · Basis V35 · Kein Push ohne User-Freigabe.

## A. Recherche (1–5)
1. [x] `renderBetreiberDiagramme()`: Zählvariablen windN/pvN + eegW/noEegW/eegP/noEegP (Anzahlen) — MW-Summen fehlen für die EEG-Gruppen.
2. [x] Donut-Aufrufe: `_bcDrawDonut('bc-tech', [Wind, PV])` / `_bcDrawDonut('bc-eeg', [4 Segmente])` — val ausschließlich Anzahl.
3. [x] Toggle-Handler existiert (`.mbtn[data-bcmeasure]`) → ruft `renderBetreiberDiagramme()` neu auf; isMW-Flag wird aktuell nur vom Balkenchart genutzt.
4. [x] Untertitel der Donuts sind statisch („Anteil Wind / PV (Anlagen)") — müssen bei MW dynamisch werden.
5. [x] Header nutzt Konvention „MW" (Wind) / „MWp" (PV) — Donut-Legende entsprechend.

## B. Planung (6–9)
6. [ ] Zähl-Schleife um 4 MW-Akkus erweitern: eegW_mw, noEegW_mw, eegP_mw, noEegP_mw.
7. [ ] Donut-vals bei isMW: tech=[windMW, pvMW], eeg=[4 MW-Gruppen]; Legende-Einheit MW (Wind) / MWp (PV).
8. [ ] Untertitel-IDs (bc-tech-sub, bc-eeg-sub) + dynamischer Text (Anlagen/MW) im Render.
9. [ ] Keine Export-/Datenänderung — reines UI-Feature in src/index.html.

## C. Umsetzung (10–15)
10. [ ] Patch Zähl-Schleife (4 neue Variablen).
11. [ ] Patch Donut-Aufrufe (val je Modus + Labels mit Einheit).
12. [ ] Patch Untertitel dynamisch.
13. [ ] node --check über Inline-Scripts.
14. [ ] dist/index.html + Singlefile neu bauen.
15. [ ] Revision speichern (iterations/V35-1_Donuts_MeasureToggle.html + human-share).

## D. Überprüfung (16–20)
16. [ ] Browser: ENERPARC (nur PV) — beide Donuts wechseln Anzahl ⇄ MW korrekt (MW-Summe == Header 3.217,5).
17. [ ] Browser: gemischter Betreiber (wpd 236 Wind/7 PV) — Donut-Anteile je Modus plausibel.
18. [ ] %Labels + Legende aktualisieren sich je Modus; weiße Trennlinie nur bei ≥2 Segmenten.
19. [ ] Regression: Balkenchart weiter steuerbar, AP2-Reset unangetastet, 0 JS-Errors, Infobar 31011/22402.
20. [ ] MEDIA-Lieferung + Änderungsliste; kein Push.

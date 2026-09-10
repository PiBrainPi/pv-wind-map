# 100-Punkte-Prüfplan — PV & Wind Karte (MaStR) Gesamtprüfung

> **Datum:** 2026-09-08 · **Basis:** GitHub-Live-Stand V29.1 (main `d8dd8e4`, gh-pages `15c2058`,
> src/index.html == gh-pages index.html, SHA-verifiziert) · **Zweck:** Bug-Detektion VOR
> Weiterarbeit. **KEINE Patches in dieser Runde** — nur Findings.
> **Grundregeln aktiv:** kein Push/Deploy ohne explizite User-Freigabe; Revisionen/Findings
> lokal + in den Chat.

## Ziel
Sicherstellen, dass die V29.1-Basis bugfrei, strukturiert und skalierbar weiterverarbeitbar ist.
Ergebnis: `BUGS_ZU_ERLEDIGEN_2026-09-08.md` im Repo-Root mit allen Findings (detailliert,
priorisiert, mit Repro/Wiederholbarkeit + Einschätzung behebbar ja/nein).

---

## Phase 1 — Recherche & Zerlegung: Was ist in der Datei/dem Projekt? (P1–P20)

1. Repo-Inventur: alle Dateien/Ordner mit Größen (README, src, dist, scripts, docs, data, iterations).
2. Git-Integrität: main/gh-pages SHAs, sauberer Working Tree, Tag-Situation.
3. Architektur-Karte: Pipeline (fetch_v2/fetch_nap/import_v2) → DB (mastr.db) → Export (export_app.py) → Assets (dist/assets/*.json) → Bundle (bundle_singlefile.py) → Deploy (deploy_ghpages.sh).
4. Zerlegung src/index.html: Sektionen HTML / CSS / JS zählen und gliedern (Zeilenbereiche).
5. JS-Funktionsinventar: alle Function-Definitionen listen (Namen, Zeile).
6. DOM-Inventar: alle relevanten IDs/Klassen (Filter, Tabs, Buttons, Panels).
7. Event-Handler-Inventar: addEventListener-Liste — jedes Element wired?
8. Daten-Assets: einheiten.json, statistiken.json, nap_index.json, nap_ranking.json, historie.json, meta.json — Existenz, Größe, Schema-Stichprobe.
9. Script-Inventar scripts/: Zweck jedes Skripts, Aufrufreihenfolge, Cron-Anbindung.
10. Doku-Inventar: PROJEKTSTAND, ROADMAP, ENTSCHEIDUNGEN, statistik.md, datenmodell.md, update.md, DEPLOYMENT — welche „Stand"-Zeilen tragen sie.
11. Iterations-/Revisionshelfer: iterations/ vollständig? human-share-Spiegel aktuell?
12. Abhängigkeiten: Leaflet/CDN-Versionen, externe Calls (Tiles, Overpass, Nominatim?) inventarisieren.
13. Konstanten-Doppelung: Zahlen/Limits (Debounce, Radien, Versionsmarker) an wie vielen Stellen gepflegt?
14. localStorage-Schlüssel inventarisieren (Namenskonflikte, V29.1-Leftovers).
15. Feature-Flags/Toggles: welche opt-in Zustände existieren (NAP-Gruppen, Größen-Basis …)?

## Phase 2 — Statische Code-Analyse (P16–P45)

16. JS-Syntax: extrahiertes <script> via node --check (0 Fehler = Pflicht).
17. Python-Syntax: py_compile über alle scripts/*.py.
18. Undefinierte Referenzen: grep-Anker je Feature — HTML-Element UND JS-Handler getrennt zählen (V28-Lektion).
19. Dual-State-Prüfung: applyFilters() vs showAllUnits() Filter-Variablen diffen (V23/V25-Regressionklasse).
20. bs35-Gates: alle Karten-Klick-Quellen prüfen — wo fehlt `(u.bs||35)!==35` (V29-Pitfall)?
21. Historie-Dedup: Load-Stelle prüfen (Dedup by datum, Delta-Sieg) + Betroffenheits-`slice(-1)`-Kette.
22. NAP-Join-Keys: nur LokationId (numerisch) joins — keine lokation_nr-Fallen.
23. to_mw-Heuristik: RD<60 & ≥1,5 MW → /1000 in beiden Pfaden (V27b) korrekt?
24. Park-Key-Konsistenz: pk/pkmw nur n≥2-Cluster; Frontend-Fallback `u.pkmw ?? u.mw` überall wo aggregiert wird?
25. Null/undefined-Risiken: alle `?.`-losen Property-Zugriffe auf optional gelieferte Felder.
26. Duplicate IDs im HTML (href="#…"/id-Kollisionen).
27. CSS-Media-Queries: Mobile-Regeln (≤767px) vollständig + ohne Leerzeichen-Falle.
28. Tab-Layer: 9+2 Statistik-Tabs (inkl. NAP-Ranking, Betroffenheit) — Render/Count-Pfad je Tab.
29. Tote Wege: Funktionen/Buttons ohne Aufrufer (Refactoring-Reste aus gelöschten Revisionen).
30. Konsolen-Noise: console.log/error-Reste, bewusste vs. versehentliche Ausgaben.
31. Performance-Hebel: applyFilters-Komplexität, Marker-Rendering, Chunk-Grenzen.
32. Escaping: User-Input (Suche) → HTML-Injection-Punkte (innerHTML mit ungefiltertem Input).
33. Zahlenformatierung: TT.MM.JJJJ, MW/MWp, tausender-Trennzeichen konsistent (V21-Standard).
34. localStorage-Fehlertoleranz: private mode / Quota-Fehler abgefangen?
35. Event-Listener-Leaks: bei Re-Render doppelt registrierte Handler?
36. Race-Conditions: Init-Reihenfolge (Daten-Load → UI-Wiring → Consent → Infobar).
37. Error-Handling Datenload: fetch/JSON-Parse-Fehler sichtbar für User?
38. Konstanten-Drift: 9-Tab-Zählung, Assets-Zahlen, Versionsmarker in UI vs. Doku.
39. Skalierbarkeit: Datenwachstum (+Xk Anlagen/Monat) — Chunk-Größen, JSON-Splitting, Single-File-42MB-Grenze (GitHub 100 MB).
40. Datenschutz-Check: keine externen Tracker; Impressum/Datenschutz-Modal-Inhalte aktuell (§5 DDG).
41. Secrets-Scan: Tokens/Keys/URLs mit Credentials im Repo? (Muss 0 Treffer sein.)
42. .gitignore-Abdeckung: data/-Unterordner einzeln gedeckt; keine großen Blobs getrackt.
43. Deploy-Skript: Worktree-Muster, CNAME-Erhalt, dist-only-Wache — Logik-Review.
44. Cron-Pipeline: build.sh/fetch-Kette sonntags 18:00 — Backup-Pflicht, UPSERT-Schlüssel, Fehlerpfade.
45. Backup-Lage: ~/backups/mastr.db.* aktuell? Vor weiterer Arbeit Backup-Stand dokumentieren.

## Phase 3 — Datenintegrität (P46–P65)

46. DB-Kernzahlen: einheiten (In-Betrieb georef) vs. einheiten_raw vs. Karte-Infobar.
47. Asset-Konsistenz: einheiten.json Count == Infobar-Zahl == statistiken.json Summen.
48. nap_ranking.json: 27.130 NAPs; Top-Werte (SP WINI 648 MW) nachrechnen aus DB.
49. nap_index.json: 479 Multi-NAP-Lokationen repräsentiert?
50. historie.json: 0 Doppel-Datums-Snapshots nach Dedup-Load; letztes Snapshot-Delta non-empty.
51. Statistik-Tabs gegen DB: 377 LKs, 51.640 Assets, Spannungsebenen, Größenklassen (Einzel vs. Park).
52. Stichprobe Anlagen: Solarpark Döllen 13 EH → 154,77 MW (pkmw); TW80-kW-Fälle = 0 in Karte.
53. Geo-Plausibilität: LK-Zuordnung (dithmarschen), BL-Mehrheitskonsens im NAP-Ranking.
54. F5-Status-Flag: alle 4 Status im Raw, nur bs35 im Kern — Grenzfälle (geplant in Betrieb?)
55. Negative/Null-MW: Anlagen mit mw<=0 — wie viele, wo gefiltert?
56. Duplikate: MaStR-Doppelmeldungen ( gleiche Einheit 2×) — DB-seitig gededupt?
57. Datum-Formate: Einheitlich ISO im Backend, DE im UI?
58. Meta.json: Versionsmarker/Datenstand == live kommuniziertem Stand.
59. Asset-Schema-Stabilität: neue Felder rückwärtskompatibel (alte Revisionen laden neue Assets)?
60. JSON-Größen/Grenzen: kein Asset nähert sich GitHub-Grenzen; Load-Zeit lokal messen.
61. Import-Idempotenz: import_v2-UPSERT-Schlüssel verhindert Rebuild-Duplikate wirklich?
62. Snapshot-Kette: snapshots-Tabelle #1–#8 unangetastet (Regel: nichts löschen).
63. NAP-Inkrement: 28 neue NAPs (06.09.) — nap_fetch_log konsistent, keine Lücken.
64. 17 MaStR-Datenfehler: dokumentiert & protokolliert — keine stillen Ausfälle neuer Art.
65. Datenstand-Doku: „06.09. 18:59" überall identisch (UI, meta, PROJEKTSTAND).

## Phase 4 — Funktionale Browser-Verifikation (P66–P90)

66. Boot: lokal (Cache-Buster!) laden, Consent akzeptieren, Infobar-Zahlen (31.010/22.409) pollen.
67. JS-Error-Wächter: window-error-Listener VOR allen Klicks — muss leer bleiben.
68. Suche: Anlagenname („Döllen"), Betreiber („rwe" = 126), Geo („dithmarschen").
69. Alle 11 Filter einzeln + Kombination → Badge/Infobar-Konsistenz.
70. „🗑️ Filter löschen": Reset auf Default (nur st-35), Suche/Gemeinde/Badge zurück.
71. „Alle Anlagen anzeigen": Overlay öffnet, Zeilenzahl == Badge (V25-Regression).
72. Statistik-Panel: alle 9 Tabs rendern, kein horizontales Overflow PC (scrollWidth≤clientWidth).
73. Tab-Klicks: Hersteller→Karte, Größenklasse→Karte (bs35-Gate aktiv: 104–150 = 2), LK→Karte.
74. NAP-Ranking-Tab: Sortierung, Such-Suggest (BL zuerst), Klick → Karte nur NAP-⚡+Anlagen.
75. NAP-Gruppenansicht (opt-in): Badges, Panel, Multi-NAP-Unterstützung.
76. Betroffenheits-Tab: Referenz-Suche (enova = 58), Modi, Zeitfenster, 🗺️ Anzeigen.
77. Popup-Konsistenz: TT.MM.JJJJ, NAP-Klick im Popup → alle Anlagen am NAP.
78. Größen-Toggle „gesamt": Klick-Position → Wind/PV korrekt.
79. Historie/Betroffenheit „letztes Update": non-empty Delta wirksam (58 enova).
80. Mobile-Layout: 375px-Force-Test, LK-Tabelle scrollbar, alle Header lesbar.
81. Performance: applyFilters-Zeit, Boot-Zeit bis Infobar, Popup-Latenz (Lazy-Popup <1s).
82. localStorage-Pfade: Toggle-Zustände persistieren + Fehlerfallback.
83. Konsolen-Check: keine Errors/Warnungen während Standard-Journey.
84. Impressum/Datenschutz-Modal: öffnen, Inhalte, Footer-Links.
85. F5-Regression: Reload nach Filter-Aktionen, kein State-Verlust-Bug (bekanntes Element-null-Muster dokumentieren statt „fixen").

## Phase 5 — Struktur, Skalierbarkeit, Prozess (P91–P100)

86. Single-File-Architektur: Grenzen dokumentieren (42,4 MB; Editierbarkeit; Merge-Konflikte) — Empfehlung für V30+ ohne Verhalten ändern.
87. Code-Organisation: Sektion-Marker in src/index.html (Find-Marken für künftige Patches) — wo fehlen sie?
88. Patch-Disziplin: Checkliste „atomare Patch-Skripte + Anker-Grep" als Standard für jede künftige Runde verankern (Process-Finding).
89. Doku-Sync: alle „Stand"-Zeilen-Dateien gelistet (grep-Liste als Pflicht-Anhang künftiger Runden).
90. Repo-Hygiene: git ls-files data/ — außer dist-Assets nichts getrackt (Pflicht-Null).
91. Skalierungsplan Daten: Pipeline-Intervall sonntags 18:00 — Wachstumsprognose + Asset-Splitting-Schwelle.
92. Test-Deckung: Browser-Verifikations-Rezepte als wiederholbares Skript-Set? Lücke dokumentieren.
93. Deployment-Sicherheit: deploy_ghpages.sh Dry-Run-Analyse (kein echtes Deploy in dieser Runde!).
94. Rollback-Pfad: iterations/ + gh-pages-Historie als Rollback — rekonstruierbar aus Single-File (Pitfall 6) verifizieren.
95. Lizenz/Branding: MIT, Impressum Fabian Bussenius, keine E-Mail/PiBrain in UI? (User-Regel Public.)
96. Artikel-Basis: faktische Zahlen V29 (65.674 etc.) gegen aktuellen Stand — Drift dokumentieren.
97._EXTERN: live URL smoke-check (nur Lesen, Cache-Buster) — Abgleich lokal vs. live SHA-Diff.
98. Findings-Datei anlegen: BUGS_ZU_ERLEDIGEN_2026-09-08.md (Repo-Root) — Struktur: ID, Schwere (Kritisch/Hoch/Mittel/Niedrig/Kosmetik), Ort, Befund, Repro, Auswirkung, Behebbar (Ja/Nein), Vorschlag (NICHT umsetzen).
99. Priorisierung: P0 = Daten falsch/Klick tot; P1 = Funktion beeinträchtigt; P2 = Robustheit; P3 = Kosmetik/Doku.
100. Abschlussbericht: Kurzübersicht im Chat (Bug-Liste + Ja/Nein) — KEINE Patches, KEIN Push.

---

## Nicht-Ziele dieser Runde
- Kein Patchen, kein Push, kein Deploy, keine Settings-Änderungen.
- Keine Datenlöschung (Regel 1), keine History-Bereinigung.

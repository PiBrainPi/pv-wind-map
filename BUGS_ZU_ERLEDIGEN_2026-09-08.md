# 🐞 BUGS ZU ERLEDIGEN — Prüfbericht 2026-09-08

> **Datei-Stand:** 2026-09-08 · **Geprüfte Basis:** GitHub-Live-Stand V29.1
> (main `d8dd8e4`, gh-pages `15c2058`; `src/index.html` byte-identisch mit gh-pages
> `index.html`, SHA-verifiziert; `dist/index_singlefile.html` identisch mit
> `GH_Online_Stand_Index.html` im human-share)
> **Datenstand:** 2026-09-06 18:59 · 65.674 Anlagen (einheiten.json: 65.674),
> 27.898 NAPs, 27.130 NAPs im Ranking
>
> **Prüfplan:** `.hermes/plans/2026-09-08_100-Punkte-Pruefplan.md` (100 Punkte,
> 5 Phasen: Zerlegung / statische Analyse / Datenintegrität / Browser-Verifikation /
> Struktur & Skalierbarkeit)
>
> **Status dieser Datei:** NUR Detektion. **Es wurde NICHTS gepatcht, gepusht oder deployed.**
> Jeder Bug ist mit Repro-Weg dokumentiert, damit die Fix-Runde direkt starten kann.
>
> **Priorisierung:** P0 = Daten falsch / Klick tot · P1 = Funktion beeinträchtigt ·
> P2 = Robustheit / Konsistenz · P3 = Kosmetik / Doku

---

## Findings-Übersicht

| ID | Schwere | Prio | Kurzbeschreibung | Behebbar |
|---|---|---|---|---|
| F-01 | 🔴 Hoch | P1 | Dual-State-Lücke: Overlay ignoriert Spannungsfilter + nutzt falsche Leistungsbasis | Ja |
| F-02 | 🟠 Mittel | P1* | bs35-Gate fehlt bei 6 Karten-Klick-Quellen (Planung fließt ein) | Ja — nach User-Klärung |
| F-03 | 🟠 Mittel | P2 | historie.json: Snapshot-Duplikate wachsen weiter (Pipeline-seitig) | Ja |
| F-04 | 🟠 Mittel | P2 | Zahlendrift: JSON 53.424 vs. Infobar/Meta 53.419; Doku-Drift 65.674 vs. 65.676 | Ja |
| F-05 | 🟡 Niedrig | P2 | Overlay-Tabelle zeigt ISO-Datum statt TT.MM.JJJJ | Ja |
| F-06 | 🟡 Niedrig | P2 | Historie-Hinweistext „1. & 15. des Monats" veraltet (Pipeline: sonntags 18:00) | Ja |
| F-07 | 🟡 Niedrig | P2 | Einmaliger Main-Thread-Freeze >30 s nach Betroffenheits-Tab-Klick | Wahrscheinlich |
| F-08 | ⚪ Kosmetik | P3 | Tab-Zählung driftet: UI 10 Tabs, Doku „9 Tabs" | Ja |

\* F-02 braucht eine fachliche Entscheidung des Users, bevor gefixt wird (s. Detail).

---

## F-01 — Overlay „Alle Anlagen anzeigen": Spannungsfilter ignoriert, Leistungsbasis falsch

- **Schwere:** Hoch (P1)
- **Ort:** `src/index.html`, JS-Block 2, Funktion `showAllUnits()` (@ ~20336)
  vs. Referenz `applyFilters()` (@ ~31271)
- **Pitfall-Klasse:** Dual-State (bekannt aus V23/V25 — Filterlogik existiert zweimal)

### Befund (statisch verifiziert)
`applyFilters()` liest und wendet an: `filter-se` (Spannungsebene), `filter-gr-basis`
(Park/Einzel-Umschalter mit `u.pkmw ?? u.mw`), Status-Checkboxen, Typ, BL, LK,
Gemeinde, Art, Größenbereich, Jahr, Monat, Inb-Jahr, Inb-Monat.

`showAllUnits()` liest an: Typ, BL, LK, Gemeinde, Art, Größenbereich, Jahr, Monat,
Inb-Jahr, Inb-Monat, Status. **Fehlt:**
1. **`filter-se` (Spannungsebene) wird im Overlay gar nicht gelesen** — Overlay zeigt
   Anlagen, die die Karte (mit gesetztalem Spannungsfilter) nicht zeigt.
2. **Leistungsfilter nutzt immer `u.mw`:**
   ```js
   filtered = filtered.filter(u => u.mw != null && u.mw >= von && u.mw < bis);
   ```
   `applyFilters()` nutzt dagegen die V23-Paket-8-Basis:
   ```js
   const v = usePark ? (u.pkmw ?? u.mw) : u.mw;
   ```
   D.h. bei Default-Basis „Park (aggregiert)" liefert Karte und Overlay bei
   identischem Leistungsfilter unterschiedliche Ergebnismengen (Döllen-Splittungs-
   Problem: Karte zeigt den ganzen Park ab Park-MW, Overlay nur Einzel-Units ≥ MW).

### Repro
1. App laden, Consent akzeptieren, Daten warten (Infobar 31.010/22.409).
2. Statistik-Tab irrelevant — Hauptseite: Spannungsfilter „Hochspannung" setzen.
3. Karte: entsprechend weniger Marker. Klick auf „Alle Anlagen anzeigen":
   Overlay-Metadaten zählen weiter ALLE Anlagen (Spannungsfilter ohne Wirkung).
4. Leistungsfilter z. B. 100–150 MW: Karte (Park-Basis) zeigt komplette Parks,
   Overlay listet nur die Einzel-Units in diesem MW-Fenster.

### Auswirkung
V25-Fix (Geo-Filter in showAllUnits) war unvollständig — die V23-Regressionklasse
ist nur zur Hälfte geschlossen. User sieht widersprüchliche Zahlen Karte vs. Overlay.

### Fix-Ansatz (NICHT umgesetzt, nur Vorschlag)
Gemeinsame Filter-Builder-Funktion `buildFilteredUnits(context)` extrahieren und in
BEIDEN Funktionen verwenden (befreit dauerhaft aus der Dual-State-Falle). Alternativ
Minimal-Patch: se-Filter + grBasis-Logik 1:1 in `showAllUnits()` spiegeln + Klick-Repro.

---

## F-02 — bs35-Gate fehlt bei 6 Karten-Klick-Quellen (Planung fließt ein)

- **Schwere:** Mittel (P1*) — *braucht zuerst User-Entscheid
- **Ort:** `src/index.html`, JS-Block 2, mehrere `renderMarkers(...)`-Aufrufstellen

### Befund (statisch + Daten verifiziert)
Das V29-Pitfall-Muster „Karten-Auswahl muss `(u.bs||35)!==35` als Gate setzen, sonst
zeigt die Karte mehr Assets als das Chart" ist NUR beim Größenklassen-Klick umgesetzt
(1 Vorkommen). **Ohne Gate:**

| Klick-Quelle | Filter | Gate? |
|---|---|---|
| Größenklassen-Balken | `(u.bs||35)!==35` + tech + MW-Fenster | ✅ V29 |
| Betreiber-Klick (Einzeltreffer) | `u.ab === name` | ❌ |
| Betreiber-Klick (Multi/Set) | `u.ab && abs.has(u.ab)` | ❌ |
| Hersteller-Klick | `(u.herst||'').trim() === name` | ❌ |
| LK/Gemeinde-Klick (Stats/Suggest) | `u.g === hit.name` | ❌ |
| NAP-Klick (Stats + Popup 🔍) | `u.lid === e.lid` | ❌ |
| Einzelmarker-Fokus | `x.m === u.m` | ❌ |

### Datenlage (einheiten.json, 65.674 Rows)
- bs35: 53.424 (31.011 Wind / 22.413 PV) · bs31 Planung: 9.264 · bs38: 2.921 · bs37: 65
- bs≠35 mit mw ≥ 30: **26 Einheiten**, größte: „PVA Schafhöfen Anlagenteil 2" 200,0 MW (Planung!)
- Beispiel RWE: 726 Treffer gesamt, davon **165 Planungs-Einheiten = 1.073,6 MW** —
  Betreiber-Klick „rwe" zeichnet also auch nicht-in-betrieb Gigawatt-Projekte auf die Karte.

### Warum User-Entscheid nötig
Es ist möglich, dass die Karte bei Klicks bewusst ALLE Status zeigen soll (Planung
sichtbar machen = Feature, nicht Bug). Das widerspricht aber dem V29-Befund
(„104–150 MW gesamt = 4 statt 2" wurde als Bug gefixt) und der Chart-Konsistenz.
**Vorschlag:** Gate überall setzen UND optional Badge „+X Planung" anzeigen —
Entscheidung offen.

### Repro
1. Statistik → Betreiber → „rwe" suchen → Klick → Karte zeichnet 726 Marker
   (Infobar-Basis wäre 558).
2. Größenklassen-Klick dagegen: 104–150 MW = 2 (Gate aktiv) — dieselbe Logik fehlt
   bei den übrigen Klicks.

---


> **✅ ENTSCHEIDUNG 08.09.2026 (User): BY DESIGN — kein Bug, kein Fix.**
> Klick-Quellen (Betreiber, Betreibergruppe, Hersteller, LK/Gemeinde/BL via Geo-Suche,
> NAP inkl. Gruppen, Bundesland) zeigen **bewusst ALLE Betriebs-Status** (In-Betrieb +
> Planung + stillgelegt). Größenklassen-Klick bleibt als dokumentierte Ausnahme auf
> In-Betrieb (bs35), weil er die Zahlen des Balkendiagramms (statistiken.json, bs35-Basis)
> abbildet — Klick und Chart müssen dort identisch sein.
> Implikation für Analysen: Betreiber-Ranking im Statistik-Tab basiert auf In-Betrieb,
> ein Klick kann daher MEHR Anlagen zeigen als die Tabellenzeile angibt — verhält sich
> wie dokumentiert, kein Fehler.

## F-03 — historie.json: Snapshot-Duplikate wachsen weiter

- **Schwere:** Mittel (P2)
- **Ort:** `dist/assets/historie.json` (erzeugt von `scripts/snapshot.py`), Frontend-Load

### Befund (Daten verifiziert)
```
2026-08-29  delta leer
2026-09-01  delta non-empty   ← gewinnt
2026-09-01  delta leer
2026-09-06  delta non-empty   ← gewinnt
2026-09-06  delta leer        (4×)
```
2× 2026-09-01, 5× 2026-09-06. `snapshot.py` hängt bei jedem Build denselben Datum-
Snapshot erneut an. Das Frontend-Dedup (V29, gewinnt je Datum den Snapshot mit
Delta-Inhalt) funktioniert **verifiziert** (Betroffenheit „letztes Update": 58 Treffer
enova ✓) — aber:
- die Datei wächst jede Runde um tote Zeilen,
- der V29-Fix sitzt im Frontend (Symptom), nicht in der Pipeline (Ursache),
- Cross-Tab-Risiko: alles, was `deltas.slice(-1)` oder Listenende liest, ist
  fragil, falls die Dedup-Reihenfolge kippt.

### Fix-Ansatz (Vorschlag, NICHT umgesetzt)
`snapshot.py`: vor Anhängen prüfen, ob Snapshot mit gleichem `datum` existiert →
überschreiben statt append. Bestehende historie.json NICHT löschen (Regel 1) —
Frontend-Dedup bleibt als Sicherheitsnetz.

---

## F-04 — Zahlendrift: JSON 53.424 vs. Infobar/Meta 53.419; Doku 65.674 vs. 65.676

- **Schwere:** Mittel (P2)
- **Ort:** `scripts/export_app.py` (Abgrenzungslogik), `dist/assets/meta.json`,
  Infobar, PROJEKTSTAND, Zubau-Tab

### Befund (Daten verifiziert)
- `einheiten.json`: 65.674 Rows, davon bs35 = **53.424** (31.011 Wind / 22.413 PV)
- `meta.json` counts: Wind 31.010 · PV 22.409 = **53.419** (= Infobar-Anzeige)
- **Differenz: 5** — Ursache lokalisiert:
  - **11 PV-Einheiten mit mw = 0,4999 MWp** (499,92 kWp, knapp unter der
    Abgrenzung „PV ≥ 0,5 MWp"). Die Export-Abgrenzung filtert sie aus Infobar/Meta
    heraus, belässt sie aber in einheiten.json (bs35). Beispiel: „Pilotenstr. -
    499,92 kWp - 2015" (SEE915108634456).
  - 1 Wind-Fall analog (0,1-MW-Grenze).
- Konsequenz: Filter „Alle Status" + Karte kann 53.424 In-Betrieb-Anlagen zeigen,
  Infobar sagt 53.419 — 5 Einheiten sind je nach Blickwinkel sichtbar/unsichtbar.
- **Doku-Drift:** PROJEKTSTAND schreibt „65.676 Anlagen (Wind 42.008 · PV 23.668)",
  Zubau-Tab + einheiten.json real: **65.674 / 42.006 / 23.668**. Artikel V29 nutzt
  65.674 (korrekt), PROJEKTSTAND-Kopf driftet.

### Fix-Ansatz (Vorschlag)
Entscheiden: Grenzfälle (0,4999) konsequent IN die Abgrenzung (>= 0,495 gerundet)
oder konsequent RAUS (auch aus einheiten.json). Danach Infobar/Meta/JSON aus EINEM
Zähler generieren und PROJEKTSTAND-Kopf synchronisieren. Artikel-Fact-Check-Pflicht
bleibt bestehen.

---

## F-05 — Overlay-Tabelle: ISO-Datum statt TT.MM.JJJJ

- **Schwere:** Niedrig (P2)
- **Ort:** `src/index.html`, JS-Block 2, `_renderTableRows()` (Overlay „Alle Anlagen")

### Befund (statisch + DOM verifiziert)
`_renderTableRows()` formatiert `u.reg`/`u.inb` selbst:
```js
if (regStr.startsWith('/Date(')) { ... regStr = new Date(...).toISOString().substring(0,10); }
```
→ Spalten zeigen `2019-01-31`. Das Anlagen-Popup nutzt dagegen `dateFullFmt()`
(TT.MM.JJJJ, V20-Fix-Kommentar „war roher '/Date(…)'-String" — im Popup korrekt,
in der Tabelle wurde derselbe Fix nie angewendet). DOM-Beleg: erste Overlay-Zeile
„PVA Zaacko IPVGebäudesolaranlage0,57Brandenburg…**2019-01-31**…".

### Auswirkung
UI-Inkonsistenz; V21-Standard „Popup TT.MM.JJJJ" ist im Overlay nicht umgesetzt.

### Fix-Ansatz (Vorschlag)
In `_renderTableRows()` beide ISO-Wandlungen durch `dateFullFmt(u.reg)` /
`dateFullFmt(u.inb)` ersetzen (Helper existiert bereits).

---

## F-06 — Historie-Hinweistext nennt falschen Pipeline-Rhythmus

- **Schwere:** Niedrig (P2)
- **Ort:** `src/index.html`, Tab „Update-Historie" (`#tab-historie`)

### Befund (DOM verifiziert)
Tab-Text: *„Noch keine Update-Historie vorhanden. Beim nächsten Daten-Update
**(1. & 15. des Monats)** wird hier die Veränderung angezeigt."*
Tatsächlicher Cron (User-Entscheid 06.09., Job `79229dc1690d`): **sonntags 18:00**.
DOM: Hinweis unsichtbar, sobald Daten da sind — aber bei leerem Zustand
(erstes Laden nach künftigen Änderungen) irreführend.

### Fix-Ansatz (Vorschlag)
Text auf „sonntags 18:00" (oder dynamisch ohne Rhythmusangabe) ändern.
Nice-to-have: denselben Text-Check in jede Doku-Runde aufnehmen.

---

## F-07 — Einmaliger Main-Thread-Freeze nach Betroffenheits-Tab-Klick

**Status: GESCHLOSSEN als Beobachtungspunkt** (Diagnose 08.09.: Analyse-Kern 11 ms, kein Freeze reproduzierbar — Details in docs/F07_ABSCHLUSS_2026-09-08.md)

- **Schwere:** Niedrig (P2, Robustheit)
- **Ort:** `src/index.html`, Betroffenheits-Tab-Render; Repro unsicher

### Befund (Browser, Audit-Lauf 1)
Erster Klick auf Tab „⚠ Betroffenheit" blockierte den Main-Thread **> 30 s**
(3 aufeinanderfolgende Console-Evals timeouts; `1+1` antwortete nicht mehr).
Nur Re-Navigate rettete die Session. **Audit-Lauf 2 (frische Session):** gleicher
Klick = **2 ms**, kein Freeze, Analyse enova: 58 Treffer / 185 Assets / 10 ms.
Kein window-error. Cache-Warmer/First-Render-Kandidat, aber nicht reproduziert —
echtes Nutzer-Risiko nicht belegbar.

### Fix-Ansatz (Vorschlag)
Beobachten. Falls reprod.: Klick-Handler des Tabs profilieren (Long-Task-API),
verdächtig wäre der erste vollständige Render des 11,7-kB-Tab-HTML + Suggest-Wiring.
Kein Blind-Patch ohne Repro (Systematik-Regel).

---

## F-08 — Tab-Zählung driftet: UI 10 Tabs, Doku „9 Tabs"

- **Schwere:** Kosmetik (P3)
- **Ort:** `src/index.html` (Statistik-Panel) vs. `docs/*`, Skill-Notizen

### Befund
DOM: Tabs = `betreiber, hersteller, groesse, bundesland, landkreis, nap, spannung,
historie, zubau, betroffen` = **10**. Skill/PROJEKTSTAND-Notizen schreiben teils
„Statistik-Panel = 9 Tabs (seit V23 Landkreis)". Mit V28 („NAP"-Tab) sind es 10.
Bekannte Fehlerklasse („8-Tabs"-Drift) — Pflicht-Grep über alle „Stand"-Zeilen
bei jeder Runde existiert, wurde aber beim NAP-Tab-Einbau nicht für die Zählung
ausgeführt.

### Fix-Ansatz (Vorschlag)
Doku-Stellen auf „10 Tabs" synchronisieren; Zählung künftig per grep-Verifikation
(`document.querySelectorAll('#stats-tabs .tab').length`) in die Runden-Checkliste.

---

## ✅ Verifiziert sauber (Negativ-Befunde, Auszug)

| Prüfpunkt | Ergebnis |
|---|---|
| JS-Syntax (node --check, App-Block 186 kB) | OK |
| Python-Syntax 15/15 Skripte (py_compile) | OK |
| JS-Runtime-Fehler komplette Browser-Journey (Suche, 11 Filter, alle Tabs, Overlay, NAP-Gruppen, Analyse, Reset) | 0 Errors |
| Duplicate HTML-IDs (183 IDs) | 0 |
| User-Input-Escaping (esc() an 101 Stellen; 2 innerHTML mit ${} — beide harmlos/konstant bzw. escaped) | OK |
| console.log-Reste | 0 |
| Döllen-Referenzfall | 13 EH → 154,77 MW ✓ |
| V27b kW/MW-Fix | 0 Wind ≥100 MW; 15–80-MW-Zone = echte 15-MW-WEA (RD 236 m) ✓ |
| V25-Overlay-Fix | Overlay öffnet, 1.500 Zeilen gechunkt, Meta korrekt ✓ |
| NAP-Ranking | 27.130 NAPs; Top: SP WINI 648 MW ✓; Suche „Bertikow" → 2 NAPs ✓ |
| Betroffenheit enova | 58 Treffer · 185 Assets · 10 ms; 18/79 Gesellschaften ✓ |
| Historie-Delta | „Update: 2026-09-01 → 2026-09-06 · 133 entfernt" sichtbar ✓ |
| Infobar | 31.010 Wind · 22.409 PV ✓ |
| Geo-Suche „dithmarschen" | Treffer ✓ |
| Filter-Reset-Button | vorhanden, rot, Reset → 31.010/22.409 ✓ |
| Alle 10 Tabs PC-Breite | scrollWidth ≤ clientWidth (805/805), 0 geclippte ths ✓ |
| NAP-Gruppen-Toggle | aktiviert, kein Fehler ✓ |
| Impressum/Datenschutz | Modal öffnet; § 5 DDG; Fabian Bussenius; MaStR-Datenlizenz ✓ |
| Repo-Hygiene | `git ls-files data/` = 0 ✓; .gitignore deckt data/nap/, raw_v2/, iterations/ ✓ |
| Secrets-Scan (Skripte, src) | keine Tokens/Keys gefunden ✓ |
| localStorage-Keys | nur `pvw_nap_groups`, `pvw_tiles_consent` — keine Leftovers ✓ |
| Deploy-Skript | Worktree-Muster, CNAME-Erhalt, dist-only-Wache (Review, kein Dry-Run nötig) ✓ |
| Meta/Live-Konsistenz | meta.stand 2026-09-06T19:40:57 == kommuniziertem Datenstand ✓ |

---

## Empfohlene Fix-Reihenfolge für V30 (Vorschlag, keine Umsetzung in dieser Runde)

1. **F-01** (Dual-State: se-Filter + grBasis ins Overlay) — funktionale Konsistenz
2. **F-05** (ISO → TT.MM.JJJJ im Overlay) — Quick Win, Helper vorhanden
3. **F-06** (Historie-Hinweistext) — Quick Win
4. **F-08** (Tab-Zählung Doku) — Quick Win, mit Runden-Grep
5. **F-04** (Zahlendrift 0,4999 + PROJEKTSTAND-Kopf) — nach User-Entscheid Grenzfall
6. **F-02** (bs35-Gate 6 Klick-Quellen) — NACH User-Klärung „Karte zeigt Planung?"
7. **F-03** (snapshot.py Dedup) — Pipeline-Runde, mit DB-Backup
8. **F-07** (Freeze) — nur beobachten; Fix erst bei Repro

## Grundregeln (Bestätigung)
- Kein Push, kein Deploy, keine Settings-Änderung ohne explizite User-Freigabe ✓
- Nichts gelöscht (auch keine Daten/Revisionen) ✓
- Diese Datei dokumentiert NUR Befunde; kein Patch wurde angewendet ✓

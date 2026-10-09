# 100-Punkte-Plan V59 — SEO-Basics für wind-pv-map.de

> **Anlass:** Betreiber-Auftrag „SEO-Grundlagen für wind-pv-map.de" (09.10.2026).
> Ziel: robots.txt, sitemap.xml, SEO-Basics (Title/Description/Canonical/lang/OG)
> auf jeder indexierbaren Seite, Impressum + Datenschutz als echte Seiten.
> **Nichts geht live vor expliziter Freigabe des Betreibers** (Auftrag + Regel 4).
> Kein Push, kein Deploy, kein Preview-Promote vor Freigabe.

---

## A. Recherche (Punkte 1–25) — Ist-Stand, belegt

**1–2. Repo/Framework/Deploy:** `~/Projects/pv-wind-map`, Branch `main` (lokal, GitHub =
Archiv). **Kein Framework** — statisches HTML: `src/index.html` (Karte, 7.704 Zeilen),
`src/impressum.html`. Build: `scripts/build_all.sh` (export_nap_index → export_app →
cp src→dist → bundle_singlefile). Deploy: `scripts/deploy_vercel.sh` = CLI-Deploy des
Ordners `dist/` → Production `wind-pv-map.de` (`.vercel/project.json`:
`prj_FBJzyKt2HI34a072uu2BhF3k8JRD`). Kein Next.js/Vite/Router.

**3. Vorhandene SEO-Artefakte:** keine `robots.txt`, keine `sitemap.xml` (Repo + live
404, Punkt 7 belegt). Meta-Tags Ist-Stand:
- Startseite: `<title>PV & Wind Karte – MaStR Deutschland</title>`,
  `lang="de"` ✓, `<meta name="robots" content="index, follow">` ✓ —
  **aber:** keine Meta-Description, kein Canonical, keine OG-Tags, kein `<h1>`,
  kein JSON-LD.
- `impressum.html`: Title vorhanden, keine Description/Canonical/OG.

**4. Auslieferungsweg:** Vercel-CLI-Ordner-Deploy ohne `vercel.json` → statische Dateien
im Deploy-Ordner werden unter der Root-URL ausgeliefert. Muster für diesen Stack:
Dateien direkt in `dist/` (Quellen in `src/`, Kopie via build_all.sh). Kein
`robots.ts`/`sitemap.ts` (gäbe es nur bei Next.js).

**5. Routen (Dateisystem):** `/` (index.html) · `/impressum.html` ·
`/index_singlefile.html` (Doppel der Startseite, primär für `file://` gedacht) ·
`/assets/*.json` (6 Daten-Assets, maschinell) · `/Artikel/Release/` (noindex,
 separat, nicht Teil dieser App). Keine Router-Tabelle, keine Rewrites.
Kartenansichten ohne eigene URL → keine Sitemap-URL (Punkt 22/30).

**6. Live-Ist (rohes HTML):** Title vorhanden; Description/Canonical/OG/JSON-LD fehlen
komplett (0 Treffer). Impressum/Datenschutz sind **Modals per `href="#"`**:
`#impressum-link`, `#datenschutz-footer-link`, `#datenschutz-link`,
`#datenschutz-consent-link` (Z. 1673, 2330, 2358). Statische Textblöcke
indexierbar (Punkt 10/11): Disclaimer-Panel (Datenquelle/Qualität, Schwellen
Wind ≥ 100 kW / PV ≥ 0,5 MWp, Hobbyprojekt, Bereinigung), Footer-Attributionszeile
(Lizenz DL-DE-BY-2.0 + Impressum/Datenschutz-Links), OSM-2-Klick-Consent-Text.

**7. Live-Checks (belegt 09.10.2026):** `/robots.txt` → 404 (text/plain),
`/sitemap.xml` → 404 (text/plain), unbekannter Pfad → 404 (text/plain,
`NOT_FOUND`). **Wichtig: kein SPA-Fallback** — Rewrites auf index.html existieren
nicht → SEO-Dateien werden nie von HTML verschluckt (Punkt 19/20/49/85 erfüllt,
ohne vercel.json).

**8. Redirect-Kette (live):** `http://` → 308 `https://` ✓ · `www.` → 308 Apex ✓ ·
trailing slash auf .html-Dateien → 200 ohne Redirect (keine Kette > 1 Hop).
Kanonische Domain (Punkt 18): **`https://wind-pv-map.de`** (Apex, ohne www) —
Begründung: Haupt-URL laut Doku/Deploy-Skript; www leitet schon korrekt weiter;
Alt-URL stillgelegt.

**9. Zweite Domain:** `wind-pv-map.ingenieur-tools.de` → live **DNS 000/NXDOMAIN**
(verifiziert 09.10.) — stillgelegt seit 20.09.2026 (DEPLOYMENT.md). **Kein
Duplicate-Content-Risiko mehr.** Historie im Bericht; keine Aktion nötig.
GitHub-Pages-Archiv (`pibrainpi.github.io/pv-wind-map/`) bleibt als Notfall-Rückfallebene
bewusst bestehen (Projektentscheidung V52.2) — Canonical auf Apex verhindert
Einordnung als Quelle.

**12. Verarbeitungen im Code (für Datenschutz-Seite, alles belegt):**
Vercel-Server-Logs (Hosting) · OSM-Kacheln 2-Klick (Einwilligung) ·
localStorage: `pvw_tiles_consent`, `pvw_nap_groups`, `pvw_toolbar_hidden`,
`pvw_analytics_consent` (4 Keys, DS-Modal § 6 nennt 3 + Analytics-Key) ·
Vercel Web Analytics **opt-in only** (Script-Injektion erst nach Klick, Z. 7654 ff.) ·
externe Links Google Maps/NorthData. **Keine Cookies, kein Tracking sonst.**

**13–15. Impressum:** `src/impressum.html` (live V52-Stand, korrekt nach
Hans-Dampf-Fix): Name, Anschrift (Jüthornstraße 50, 22043 Hamburg), E-Mail,
Datenquelle/Lizenz, Hosting. **Fehlende Pflichtfelder: keine** — Vertretungsberechtigte
und Registerangaben entfallen bei Einzelperson; USt-IdNr. nicht vorhanden
(nicht-geschäftsmäßig). Liste an Betreiber im Bericht.
Rechtliche Einordnung (Hinweis, kein Rechtsrat): nicht-kommerzielles Hobbyprojekt
ohne Werbung fällt oft nicht unter § 5 DDG; Impressumsseite wird auf Betreiber-Wunsch
trotzdem angeboten (besteht seit V52).

**16. Lizenznennung:** Footer-Zeile der Startseite (dauerhaft sichtbar) + Impressum §
Datenquelle & Lizenz → govdata.de/dl-de/by-2-0. Bleibt erhalten.

**17. Wettbewerber-Kontrast (nicht kopiert):** wind-map.de / windturbinemap.com
ranken über statischen Erklärungstext. Auf wind-pv-map.de fehlt im ersten HTML:
ein zusammenfassender Erklärungssatz + ein `<h1>` — beide werden ergänzt
(Punkt 38), eingebettet in das bestehende Disclaimer-Panel (aufklappbar, verdeckt
nichts, kein versteckter Text).

**21. Preview-Deployments:** es gibt keine automatische Pipeline; Previews entstehen
nur manuell (`npx vercel` ohne --prod) und sind nach Freigabe-Workflow nicht
geplant. Vercel setzt für Preview-URLs automatisch `X-Robots-Tag: noindex`
(Standardverhalten). Prüfpunkt in Phase D (Punkt 87) dokumentiert.

**22. Query-Parameter:** 0 Treffer auf `location.search`/`URLSearchParams` —
Karte nutzt keine Parameter-URLs → keine Parameter in der Sitemap.

**23. Suchbegriffe aus dem tatsächlichen Angebot:** Windkraftanlagen,
Photovoltaik, Marktstammdatenregister, MaStR, Deutschland, Karte,
Netzanschlusspunkt. **Nicht** versprochen werden: Kleinanlagen unter den
Schwellen, Ertragsprognosen, Echtzeitdaten.

**25. Nutzer-Fragen:** keine — kanonische Domain ist entscheidbar (Punkt 18),
Pflichtangaben vollständig (Punkt 15). Betreiber-Freigabe vor Deploy bleibt
ohnehin Pflicht (Regel 4).

---

## B. Planung (Punkte 26–45)

**26. Auslieferungsweg:** statische Dateien — Quellen `src/robots.txt` +
`src/sitemap.xml`, Kopie nach `dist/` via `build_all.sh` (Zeilen wie für
index/impressum.html). Kein vercel.json (kein Fallback, der greifen müsste).

**27–28. robots.txt (final):**
```
User-agent: *
Allow: /
Disallow: /index_singlefile.html

Sitemap: https://wind-pv-map.de/sitemap.xml
```
Begründungen: Kein Crawl-delay. `/assets` **bewusst nicht** gesperrt (Punkt 27).
`/index_singlefile.html` gesperrt, weil es ein 1:1-Doppel der Startseite mit
eingebetteten 30-MB-Daten ist (Crawler-Falle, Duplicate) — ergänzt durch
`noindex`-Meta in der Singlefile selbst (Doppelschutz: Disallow hält Crawler
fern, noindex deckt verlinkte Fundstellen ab). Keine weiteren Disallows —
alle Inhalte sind öffentlich gedacht.

**29–30. sitemap.xml:** 3 URLs, ohne lastmod (Plan: nur echtes Datum — das
statische Datum würde monatlich veralten; verzichtbar):
- `https://wind-pv-map.de/`
- `https://wind-pv-map.de/impressum.html`
- `https://wind-pv-map.de/datenschutz.html`

**31–33. Titles/Descriptions (final):**
- Startseite:
  Title: `PV- & Windkarte Deutschland – Anlagen aus dem MaStR` (51 Zeichen)
  Description: `Interaktive Karte aller Windkraftanlagen (≥ 100 kW) und Photovoltaikanlagen (≥ 0,5 MWp) aus dem Marktstammdatenregister (MaStR) der Bundesnetzagentur – mit Statistiken, Anlagenliste und Netzanschlusspunkt-Auswertung.`
- impressum.html:
  Title: `Impressum · PV- & Windkarte Deutschland (MaStR)`
  Description: `Impressum der PV- & Windkarte Deutschland: Betreiber, Kontakt und rechtliche Angaben zum nicht-kommerziellen Kartenprojekt auf Basis des Marktstammdatenregisters.`
- datenschutz.html:
  Title: `Datenschutzerklärung · PV- & Windkarte Deutschland (MaStR)`
  Description: `Datenschutzerklärung der PV- & Windkarte Deutschland: Hosting-Logdaten (Vercel), 2-Klick-Kartendaten (OpenStreetMap), lokale Speicherung und optionale Besuchsstatistik.`

**34–37. Meta-Basics:** Canonical auf allen 3 Seiten auf die kanonische
Apex-URL (absolut). `lang="de"` bereits gesetzt. OG: `og:title`, `og:description`,
`og:url`, `og:type=website`, `og:locale=de_DE` — **kein og:image** (kein echtes
Bild vorhanden, nichts erfinden). JSON-LD: `WebSite` (Name, URL, inLanguage de,
Beschreibung) auf der Startseite — keine erfundene Organization, kein Rating.

**38. Einführungstext:** Das bestehende Disclaimer-Panel bekommt als ersten Block
`<h1>PV- & Windkarte Deutschland</h1>` + einen Lead-Absatz (was gezeigt wird,
Quelle MaStR, Schwellen, nicht-kommerziell, Lizenz). Panel ist aufklappbar
(Hover/Klick) → Text ist ohne JavaScript im HTML (Crawler liest ihn), verdeckt
die Karte nicht, ist kein versteckter Text (Accordions sind legitimes UI).
Footer-Lizenzzeile bleibt sichtbar (Punkt 61).

**39–41. Echte Seiten:** Impressum = bestehende `impressum.html` (Abweichung vom
Vorschlag `/impressum` begründet: Route existiert live seit V52, kein Rewrite
nötig, kleinster Diff). Datenschutz = **neue `datenschutz.html`** im Stil der
Impressum-Seite, Inhalt = der live freigegebene DS-Modal-Text (V54-Stand) in
Seitenform — ausschließlich belegte Verarbeitungen (siehe Punkt 12).
Die Einwilligungs-UI (Vercel Analytics Toggle) zieht auf die Datenschutzseite
(identischer localStorage-Key `pvw_analytics_consent`, gleiche Inject-Logik) —
kein Funktionsverlust beim Umbau der Links. Der DS-Modal-Code bleibt im Projekt
bestehen (Löschverbot Regel 1), wird aber von keinem Link mehr geöffnet.

**42–43. Preview/Freigabe:** kein Preview nötig; Freigabe-Workflow = dieser
Bericht + Diff an den Betreiber, Warten auf „Ja", erst dann Deploy (Phase D).
Kein Push, kein Deploy vor Freigabe.

**44. Prüfung:** vor Freigabe gegen lokalen Build (HTTP-Server auf dist/,
Content-Type/Status-Rohchecks + Playwright-Karten-Check gegen Regression);
nach Freigabe dieselben Checks gegen Produktion (Punkte 78–86).

**45. Betroffene Dateien:**
| Datei | Änderung |
|---|---|
| `src/robots.txt` | NEU |
| `src/sitemap.xml` | NEU |
| `src/datenschutz.html` | NEU (echte Datenschutzseite inkl. Analytics-Toggle) |
| `src/impressum.html` | + Description/Canonical/OG/JSON-LD entfällt (kein JSON-LD), Link auf datenschutz.html |
| `src/index.html` | + Description/Canonical/OG/JSON-LD/h1+Intro im Panel, #-Links → echte Routen |
| `scripts/build_all.sh` | + Kopieren der 3 Seiten + robots/sitemap nach dist/ |
| `scripts/bundle_singlefile.py` | + noindex-Meta in der Singlefile |
| `docs/PROJEKTSTAND.md` u. a. | Doku as-built (nach Umsetzung) |

---
(Weiter: Phase C — Ausführung, wird nach Umsetzung mit Belegen ergänzt.)

---

## C. Ausführung (Punkte 46–75) — ERLEDIGT, lokal belegt

**46.** Kein Feature-Branch: Projekt arbeitet auf `main` (Historie aller V-Revisions
ebenso); Deploy ist ohnehin erst nach Freigabe — Risiko identisch, da nichts
gepusht/deployt wird. Commit `07da90c` (lokal, nicht gepusht).
**47–48.** `src/robots.txt` + `src/sitemap.xml` gesetzt (Inhalte s. Planung).
**49.** Kein SPA-Fallback vorhanden (live 404 bewiesen) — Build-Output-Test:
lokal via http.server auf dist/: robots 200 text/plain, sitemap 200 application/xml,
unbekannter Pfad 404. Kein HTML-Schlucken möglich.
**50–54.** lang="de" stand bereits; Title/Description/Canonical/OG/JSON-LD auf
Startseite; eigene Titles + Metas auf impressum.html + datenschutz.html (Belege
im Roh-HTML von dist/, s. D).
**55.** Intro-Text steht als statisches HTML im Disclaimer-Panel (Zeilen ~1670 ff.).
**56–57.** impressum.html erweitert (Metas, Link auf datenschutz.html); datenschutz.html
neu gebaut aus dem belegten DS-Modal-Stand.
**58.** Alle 4 `#`-Links umgebogen: Footer (`#impressum-link` → impressum.html,
`#datenschutz-footer-link` → datenschutz.html), Impressum-Modal-Querverweis
(`#datenschutz-link` → datenschutz.html), OSM-Consent (`#datenschutz-consent-link`
→ datenschutz.html). JS-Handler (preventDefault + Modal-Öffnung) entfernt;
Modals bleiben unangerufen im HTML (Regel 1).
**59.** Zweite Domain: stillgelegt (DNS 000, live verifiziert) — keine Aktion,
nur Bericht.
**60.** Preview: nicht Teil dieses Workflows; Vercel sendet für Previews
standardmäßig `X-Robots-Tag: noindex`. Kein manueller Preview-Deploy geplant.
**61.** Lizenzzeile im Footer unverändert sichtbar; Intro-Text nennt Lizenz zusätzlich.
**62.** Keine weiteren Features umgesetzt.
**63.** Keine Secrets/Tokens in den Dateien (geprüft: robots/sitemap/Plan-Doku frei).
**64.** Diff-Selbstprüfung: 4 geänderte Dateien, 61+/37−; einzige unbeabsichtigte
Änderung gefunden + gefixt: fehlendes `}` nach Modal-Handler-Entfernung
(SyntaxError) — node --check je Script-Block + Verify 17/17 nach Fix.
**65.** Build läuft: `bash scripts/build_all.sh` grün (Singlefile 47,5 MB).
**66.** Roh-HTML-Checks: Title/Description/Canonical/h1/Intro im dist/index.html
bestätigt (grep-Belege).
**67.** robots: 200 text/plain · sitemap: 200 application/xml (lokaler Server).
**68.** Sitemap: urlset + 3 loc, absolute https, 0 Duplikate.
**69.** Alle 3 loc-URLs lokal abgerufen: 200/200/200.
**70.** Karte regressionstestet: verify_app.js 17/17 beide Builds (Marker, Infobar,
11 Tabs, Historie-SVGs, Heatmap); Klickpfad Footer→Impressum→Karte im
Funktionscheck 9/9.
**71.** Bericht aktualisiert (dieses Dokument) + PROJEKTSTAND V59-Abschnitt.
**72.** Commit `07da90c` lokal ("V59: SEO-Basics …"), **NICHT gepusht**.
**73–74.** Kein Push → keine Preview. Kein Schritt Richtung Produktion ausgeführt.
**75.** Übergabe an Betreiber: dieser Bericht + Diff (`git show 07da90c`) +
klickbare Revision `iterations/V59_SEO_Basics_robots_sitemap.html` (human-share).
**WARTET AUF FREIGABE.**

## D. Prüfung nach Freigabe (76–92) — OFFEN, nach User-Freigabe
(78–86 gegen Produktion: Status/Content-Type robots+sitemap, jede loc 200,
Roh-HTML-Checks, Redirect-Kette, 404-Verhalten, Karten-Check, Preview-noindex,
Diff-Vergleich. Wird nach Freigabe ausgeführt und hier dokumentiert.)

## E. Abschluss (93–100) — OFFEN, nach Phase D

## Fehlende Impressumsfelder (Punkt 15/97)
**Keine Lücken:** Name, Anschrift (Jüthornstraße 50, 22043 Hamburg), E-Mail
(fabibuss@web.de) vollständig und belegt. Vertretungsberechtigte/Register: entfallen
bei Einzelperson. USt-IdNr.: nicht vorhanden — nicht zu erfinden (§ 5 DDG-Prüfung
steht im Recherchebericht, Hinweis ohne Rechtsrat).

## Zweite Domain (Punkt 9/96)
`wind-pv-map.ingenieur-tools.de` ist seit 20.09.2026 stillgelegt (DNS 000/NXDOMAIN,
09.10. verifiziert) — **kein Duplicate-Content-Risiko**. Das GitHub-Pages-Archiv
(`pibrainpi.github.io/pv-wind-map/`) bleibt bewusst als Notfall-Rückfallebene
bestehen (Projektentscheidung V52.2); Canonicals auf `https://wind-pv-map.de`
verhindern eine Fehleinordnung. Kein Redirect nötig, keine Aktion.

## Search Console (Punkt 91/95, Folgeauftrag)
Nach Freigabe kann der Betreiber selbst einreichen:
- Sitemap: `https://wind-pv-map.de/sitemap.xml` (Google Search Console + Bing Webmaster)
- Robots: `https://wind-pv-map.de/robots.txt` (Prüf-URL beider Tools)

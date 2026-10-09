# 25-Punkte-Verifikationsplan V59 — Vollüberprüfung SEO-Basics

> **Zweck:** Unabhängige End-to-End-Verifikation aller V59-Änderungen (Recherche/Plan/
> Ausführung bereits belegt in `docs/SEO_V59_100PUNKTE_PLAN.md`). Jeder Punkt wird
> frisch ausgeführt und mit echtem Beleg abgehakt — kein Verweis auf frühere Läufe.
> Stand: 2026-10-09 · Basis: Commit `8f6f63f` (main, lokal)

## A. Quellen-Konsistenz (1–6)

1. ⬜ src/ und dist/ byte-identisch für alle 5 geänderten/neuen HTML/TXT/XML-Dateien
2. ⬜ Git-Status clean (nur bekannte untracked v55_reshots*.py) · 2 V59-Commits vorhanden
3. ⬜ Keine Secrets/Keys in robots.txt, sitemap.xml, datenschutz.html, Plandokumentation

## B. robots.txt (7–10)

4. ⬜ Inhalt exakt wie geplant (User-agent */ Allow / Disallow /index_singlefile.html / Sitemap)
5. ⬜ Kein Crawl-Delay, /assets NICHT gesperrt, keine weiteren Disallows
6. ⬜ Sitemap-Verweis ist absolute URL auf kanonische Domain
7. ⬜ Content-Type text/plain beim Ausliefern (lokaler Server)

## C. sitemap.xml (11–14)

8. ⬜ Wohlgeformtes XML (Parser), urlset-Namespace sitemaps.org
9. ⬜ Genau 3 loc, alle absolut https://wind-pv-map.de/…, 0 Duplikate, keine Parameter-URLs
10. ⬜ Alle 3 URLs antworten lokal 200
11. ⬜ Content-Type XML beim Ausliefern

## D. Meta-Tags Roh-HTML (15–20)

12. ⬜ Startseite: Title (≤60 Z.), Description, Canonical → https://wind-pv-map.de/, lang="de"
13. ⬜ Startseite: OG (title/description/url/type/locale, KEIN og:image), JSON-LD WebSite parsebar
14. ⬜ impressum.html: eigener Title + Description + Canonical (auf impressum.html) + OG
15. ⬜ datenschutz.html: eigener Title + Description + Canonical (auf datenschutz.html) + OG
16. ⬜ Kein Modal-Öffner mehr: 0× href="#" für Impressum/Datenschutz in index.html
17. ⬜ h1 + "Über diese Karte"-Intro im Roh-HTML (ohne JS lesbar), Impressum-Link im Intro

## E. Funktionalität (21–25)

18. ⬜ verify_app.js index.html 17/17, 0 JS-Errors (frischer Lauf)
19. ⬜ verify_app.js index_singlefile.html 17/17 + noindex-Meta im Build-Output
20. ⬜ Footer-Klick Impressum → impressum.html (echte Navigation, kein Modal)
21. ⬜ Footer-Klick Datenschutz → datenschutz.html (echte Navigation, kein Modal)
22. ⬜ Analytics-Toggle auf datenschutz.html: Statuswechsel AUS⇄AN + localStorage-Key korrekt
23. ⬜ Consent-Link (OSM-Panel) → datenschutz.html
24. ⬜ JSON-LD validiert gegen JSON.parse + Pflichtfelder (name/url/description/inLanguage)
25. ⬜ Doku-Konsistenz: PROJEKTSTAND V59-Abschnitt = Ist-Befund, Plandoku Phase C belegt

## Ergebnis — ALLE 25 PUNKTE ✅ (verifiziert 09.10.2026, frische Läufe)

**A. Quellen-Konsistenz**
1. ✅ src==dist byte-identisch für index/impressum/datenschutz.html + robots.txt + sitemap.xml (diff -q je Datei)
2. ✅ git status clean (nur bekannte v55_reshots*.py untracked) · V59-Commits `07da90c` + `8f6f63f` auf main
3. ✅ Secrets-Scan: 0 echte Treffer (1 Selbstreferenz des Plans „keine Secrets" = Dokumentation)

**B. robots.txt**
4. ✅ Inhalt exakt: `User-agent: *` / `Allow: /` / `Disallow: /index_singlefile.html` / `Sitemap: https://wind-pv-map.de/sitemap.xml`
5. ✅ Kein Crawl-Delay · /assets nicht gesperrt · keine weiteren Disallows
6. ✅ Sitemap-Verweis absolut auf kanonische Domain
7. ✅ HTTP 200, Content-Type `text/plain` (lokaler Server auf dist/, Port 8768)

**C. sitemap.xml**
8. ✅ Wohlgeformtes XML (ElementTree-Parse), Namespace sitemaps.org/0.9
9. ✅ Genau 3 loc, alle absolut `https://wind-pv-map.de/…`, 0 Duplikate, 0 Parameter/Anker
10. ✅ Alle 3 loc-URLs antworten 200 (/, /impressum.html, /datenschutz.html)
11. ✅ HTTP 200, Content-Type `application/xml`

**D. Meta-Tags Roh-HTML**
12. ✅ Title 57 Zeichen „PV- & Windkarte Deutschland – Anlagen aus dem MaStR" · Description · Canonical `https://wind-pv-map.de/` · `lang="de"`
13. ✅ OG 5 Properties (title/description/url/type/locale), og:image = 0 (nichts erfunden) · JSON-LD WebSite
14. ✅ Impressum: eigener Title/Description/Canonical (→ impressum.html)/OG (3 og-Tags)
15. ✅ Datenschutz: eigener Title/Description/Canonical (→ datenschutz.html)/OG (3 og-Tags)
16. ✅ 0 Impressum/Datenschutz-`#`-Links (verbleibende 3 `href="#"` = Leaflet-Vendor + NAP-/Betroffenheits-Deep-Links mit JS-Handlern, nicht relevant)
17. ✅ h1 + „Über diese Karte"-Intro im Roh-HTML, Impressum+Datenschutz-Links im Intro

**E. Funktionalität (frische Läufe)**
18. ✅ verify_app.js index.html: **17/17 grün, 0 JS-Errors**
19. ✅ verify_app.js index_singlefile.html: **17/17 grün** + `noindex, nofollow` im Build-Output
20. ✅ Footer-Klick Impressum → echte Navigation zu impressum.html (Title geprüft)
21. ✅ Footer-Klick Datenschutz → echte Navigation zu datenschutz.html (Title geprüft)
22. ✅ Analytics-Toggle: vorhanden, Status AUS→AN wechselnd, Key `pvw_analytics_consent`
23. ✅ OSM-Consent-Link → datenschutz.html
24. ✅ JSON-LD parsebar, Pflichtfelder name/url/description/inLanguage=de alle gesetzt
25. ✅ PROJEKTSTAND V59-Abschnitt (2 Fundstellen) + Plandoku Phase C (belegt) konsistent

**Fazit:** 25/25 ✅ — 0 Befunde, 0 Regressionen. V59 ist freigabefähig.
Nur der Test-Server (Port 8768) war zwischenzeitlich falsch gerootet (Repo-Root statt
dist/) und lieferte Schein-404s — nach Neustart mit CWD=dist alle Checks grün; kein
Produkt-Bug. Deploy + Push stehen AUS (Regel 4 + Auftrag Punkt 76).

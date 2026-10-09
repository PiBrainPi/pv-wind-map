# 25-Punkte-Plan V60 — og:image Social-Preview implementieren

**Status:** PLAN — wartet auf Bild des Betreibers (Upload im nächsten Prompt)
**Projekt:** wind-pv-map.de · Vorbereitung: 09.10.2026 · Ausführung: sobald Bild da
**Kontext:** V59.1 live. og:image ist der letzte offene SEO-Punkt (bewusst in V59 weggelassen, um nichts zu erfinden).

---

## A. Recherche (Punkte 1–7) — nach Bild-Upload

1. Bild annehmen, format prüfen (per `file` + `identify`): JPEG vs. PNG, Farbe, Transparenz
2. Dimensionen messen (Ziel laut Open-Graph-Standard: 1200×630 px, Verhältnis 1.91:1)
3. Dateigröße prüfen (Ziel < 300 KB, ideal < 150 KB für schnelle Social-Previews)
4. Recherche Social-Previews-Crawler-Verhalten (Facebook, WhatsApp, X, LinkedIn, Telegram): welche Größe, welche Formats akzeptiert, Caching-Verhalten (neu crawlen erzwingen möglich?)
5. Entscheiden: Original belassen vs. ableiten (z. B. mit ImageMagick exakt 1200×630 croppen/resizen, ggf. Hintergrund füllen)
6. Speicherort fixieren: `src/og-image.jpg` (FQN vor Deployment in `dist/`)
7. Festlegen: og:image NUR auf Startseite oder auch Impressum/Datenschutz? → Entscheidung: **alle 3 Seiten bekommen og:image** (gleiches Bild, ok, da Projekt-Branding)

## B. Planung der Umsetzung (Punkte 8–12)

8. Meta-Tags definieren (Startseite):
   - `<meta property="og:image" content="https://wind-pv-map.de/og-image.jpg">`
   - `<meta property="og:image:width" content="1200">`
   - `<meta property="og:image:height" content="630">`
   - `<meta property="og:image:type" content="image/jpeg">`
   - `<meta property="og:image:alt" content="...">` (Alt-Text, beschreibend)
   - ggf. Twitter-Card `summary_large_image` + `twitter:image` (dann auf allen 3 Seiten)
9. Einbau-Punkte fixieren: in `src/index.html` + `src/datenschutz.html` + `src/impressum.html` (im `<head>` nach den bestehenden og:*-Tags)
10. Build-Chain prüfen: `scripts/build_all.sh` kopiert ohnehin src→dist, og-image.jpg muss in die Kopierliste **falls nicht schon** `cp -a src/*.jpg` greift — prüfen
11. Sitemap prüfen: og:image-Datei NICHT in sitemap aufnehmen (Sitemap = nur Seiten, nicht Assets) — Verifikationspunkt einplanen
12. robots.txt prüfen: og-image.jpg darf NICHT disallowed sein (aktuell: nur /index_singlefile.html disallowed — passt, nichts zu tun)

## C. Umsetzung (Punkte 13–18)

13. Bild verarbeiten (falls nötig): exakt 1200×630, optimiert, als `src/og-image.jpg` ablegen
14. Meta-Tags einbauen in alle 3 HTML-Dateien (gleicher Block, jeweils unter den bestehenden og:*-Zeilen)
15. `scripts/build_all.sh` prüfen/anpassen, dass og-image.jpg nach dist/ kommt
16. Build ausführen: `scripts/build_all.sh`
17. Lokale Verifikation: `diff -q src/og-image.jpg dist/og-image.jpg` (identisch), Metas in dist/*.html drin, 0 Regressionen im HTML
18. `scripts/verify_app.js` laufen lassen (17/17 erwartet, 0 JS-Errors) + `verify_update.sh` falls vorhanden

## D. Test / Verifikation (Punkte 19–25)

19. Lokal: OG-Tags per grep/HTML-Parser auf allen 3 Seiten prüfen (vollständig, korrekte URL, korrekte width/height/type)
20. Lokal: og-image.jpg HTTP 200 + Content-Type image/jpeg (lokal via python http.server)
21. Deploy NUR nach expliziter Freigabe des Betreibers (V59-Workflow: kein Push/Deploy ohne OK)
22. Live-Checks nach Deploy:
    - `curl -I https://wind-pv-map.de/og-image.jpg` → 200, image/jpeg
    - og:image-Tags live auf allen 3 Seiten vorhanden
    - Dateigröße live < 300 KB
23. Social-Preview-Test: WhatsApp-Link-Vorschau prüfen (Fabi testet), ggf. Facebook Sharing Debugger (https://developers.facebook.com/tools/debug/) + Twitter Card Validator — Betreiber macht das, ich liefere die Links
24. Sitemap/robots final prüfen (kein og-image drin / nicht disallowed)
25. As-built-Doku: PROJEKTSTAND.md (V60-Eintrag: og:image live), SEO-Plan (offener og:image-Punkt schließen), ggf. iterations/-Eintrag; Commit + Push nur nach Freigabe

---

## Vorbereitet (warte auf Bild)

- Bildformat/Größe wird beim Upload geprüft
- Meta-Tag-Block ist definiert (Punkt 8)
- Speicherort festgelegt: `src/og-image.jpg` → dist/
- Alle 3 Seiten bekommen og:image (Startseite + Impressum + Datenschutz)
- Twitter-Card ergänzt, wenn wir eine wollen (muss dann Betreiber-OK — Standard ja, summary_large_image)
- og:image.alt-Text entstehe ich erst, wenn Bild da ist (beschreibe den Bildinhalt)

---

## Nächster Schritt

**Fabi:** Bild hochladen (im nächsten Prompt anfügen) → ich prüfe Format/Größe, handle alle 25 Punkte ab, melde mich vor Deploy mit Statusrückmeldung.

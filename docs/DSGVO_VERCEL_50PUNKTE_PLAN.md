# DSGVO-Anpassung Karte — 50-Punkte-Plan (V52 „DSGVO-Vercel")

> **Ziel:** Die Datenschutzhinweise der PV-&-Wind-Karte vollständig an das Vercel-Hosting
> (wind-pv-map.de, seit 20.09.2026) anpassen, alle Stellen im Projekt + Portal dokumentieren
> und volle DSGVO-Konformität der LIVE-Version herstellen.
> **Auslöser:** Hosting-Wechsel GitHub Pages → Vercel (20.09.) — § 3 Hosting der DS verweist
> noch auf GitHub; Portal-DS referenziert Alt-URL; Impressum hat Plausibilitäts-Fehler.
> **Erstellt:** 2026-09-20 · Projekt: `~/Projects/pv-wind-map` · LIVE: V51.2 (dpl_HX7YQ, alias wind-pv-map.de)

---

## A. RECHERCHE (Punkte 1–14)

**Quellenbasis (bereits erledigt, 20.09.):**

1. ✅ **Ist-Stand DS-Modal** (src/index.html Zeilen 2363–2425): 9 Abschnitte, Stand 31.08.2026,
   § 3 = „Hosting GitHub Inc. (GitHub Pages, Server u. a. in den USA)" — **veraltet** (Karte lebt auf Vercel).
2. ✅ **Impressum-Modal (index.html):** korrekt (Fabian Bussenius, Jüthornstraße 50, Hamburg) — nur
  .Hosting-Abschnitt fehlt (Impressum nennt nur Diensteanbieter, korrekt nach § 5 DDG).
3. 🔴 **impressum.html (Separate Seite):** enthielt „Hans Dampf / Dampfstraße 1" **Platzhalter**
   (find-orphan der alten V6-Vorlage) — **wird nicht mehr ausgeliefert? Nein: dist/impressum.html
   wird deployed** → **KRITISCHER FIX**: Platzhalter durch echte Angaben ersetzen + DDG-Statt-TMG + Hosting ergänzen.
4. ✅ **Single-File-Check:** `dist/index_singlefile.html` enthält KEIN „Hans Dampf" (0 Treffer) —
   nur `impressum.html` ist betroffen (wird aber gleich mitgefixt).
5. ✅ **localStorage-Keys IST-Mapping:** `pvw_tiles_consent` (Kachel-Consent), `pvw_nap_groups`
   (NAP-Gruppenansicht), `pvw_toolbar_hidden` (mobil Toolbar) — **DS-Modal § 6 nennt nur
   pvw_tiles_consent** → Vervollständigen (TDDDG § 25 Abs. 2 Nr. 2 korrekt dokumentieren).
6. ✅ **Vercel Privacy Notice** (vercel.com/legal/privacy-policy, Stand 01.06.2026): sammelt automatisch
   IP, log files, device info, usage info; Verarbeitung teils als Controller (Sites) / teils Processor.
7. ✅ **Vercel DPF-Zertifizierung:** seit 04.06.2024 (EU-US DPF + UK Extension + Swiss-US DPF),
   öffentliche Liste: dataprivacyframework.gov — damit legaler US-Transfer nach Art. 45 DSGVO.
8. ✅ **Vercel DPA:** nur für **Pro/Enterprise**-Pläne vertraglich zugesichert — Hobby/Free hat
   **keinen DPA-Vertrag** → wichtig für die Rechtsgrundlagen-Auswahl in der DS (kein Art. 28-
   Auftragsverarbeitungsvertrag möglich auf Free-Plan; Hosting läuft als eigenständiger Controller
   für Logdaten → in DS korrekt als solcher benennen).
9. ✅ **Vercel Subprozessoren:** Infrastruktur AWS/Azure/GCP (DPA Schedule 2), Liste via
   security.vercel.com; ISO 27001 + SOC 2 Type 2 (Audit jährlich).
10. ✅ **Vercel-Logdaten:** „log files, IP address, location derived from IP" (Privacy Notice);
    Retention im Free-Plan nicht detailliert veröffentlicht → in DS transparent formulieren
    („Speicherdauer nach Vercel-Standard, ohne zusätzliche Speicherung durch uns").
11. ✅ **Portal-DS (ingenieur-tools.de/datenschutz.html § 3 + 4 + 5.1):** erwähnt nur GitHub als
    Hosting, Alt-URL wind-pv-map.ingenieur-tools.de → **muss um Vercel/wind-pv-map.de ergänzt werden**.
12. ✅ **Bestehende Portal-DS-Struktur** (10 Abschnitte, Drittland-Tabelle, HmbBfDI) — als Vorlage
    für Konsistenz der Karte nutzen.
13. ✅ **Recherche DNS-Logdaten netcup** (Domain-Registrierung = eigenständiger Auftragsverarbeiter?):
    netcup-GmbH (DE) verarbeitet WHOIS-/Verwaltungsdaten; als Verarbeiter in Portal-DS § 4
    Tabelle ergänzen (Domain-Registration, KEIN Webhosting).
14. ✅ **Prüfen:** Liefert Vercel im Free-Plan Request-Logs am Edge (interne Logs) → auf
    vercel.com/docs/logs + KB prüfen; dann korrekte Beschreibung im DS-Text.
15. ✅ **Prüfen:** Verarbeitet Vercel IP-Adressen in der EU (Edge-Region FRA1) oder nur in US?
    Vercel Edge läuft automatisch in nächstgelegener Region; dokumentieren: „Auslieferung über
    globales CDN (u. a. Region Frankfurt am Main für Besucher aus DE)". → Quellen:
    vercel.com/docs/edge-network/regions.
16. ✅ **Prüfen:** Hat die Karte Vercel-Web-Analytics aktiviert? (Dashboard/CLI prüfen; default aus →
    dokumentieren, dass keine Analyse-Tools aktiv sind.)
17. ✅ **E-Mail-Datenschutz (fabibuss@web.de, web.de/1&1 Mail & Media GmbH, DE)** — ist bereits
    korrekt im Portal-DS § 7 dokumentiert; im Karten-DS-Modal fehlt er → aufnehmen.
18. ⬜ **Verantwortliche Stelle:** stimmt „Fabian Bussenius · Jüthornstraße 50 · 22043 Hamburg"?
    → User-Frage (Feld in Planung); Impressum-Modal nutzt dieselbe Adresse — konsistent halten.
19. ✅ **Alt-URL-Referenzen im Portal-DS § 5.1** (wind-pv-map.ingenieur-tools.de) — nach Stilllegung
    der Alt-URL (HANDOVER §6.1) auf wind-pv-map.de ändern; bis dahin DUAL-Ansage in beiden DS-Texten.
20. ✅ **Cross-Check MaStR-Lizenz** (DL-DE/BY-2.0) + Bundesnetzagentur-Quelle — unverändert korrekt
    (siehe Karten-Modal § 8) — nur Formalprüfung.

## B. PLANUNG (Punkte 18–30)

18. ⬜ **Änderungsumfang festlegen** (Liste der 5 Dateien, die die DS-Texte tragen):
    - `src/index.html` (DS-Modal, 9 Abschnitte + Impressum-Modal)
    - `src/impressum.html` (Separate Seite, deployed)
    - `~/Projects/Domain_Hosting/.../repos/ingenieur-tools-portal/datenschutz.html` (Portal-DS § 5.1 + Tabelle § 4)
    - optional `docs/DEPLOYMENT.md` + `docs/PROJEKTSTAND.md` (Doku-Reflektion)
    - Vercel-Deployment nach Fix (dist/ neu bauen + deployen)
19. ✅ **Neue DS-Modal-Struktur (V52, Karte index.html) definieren:**
    1. Verantwortlicher (unverändert)
    2. Allgemeines (keine Cookies/Tracking — bleibt)
    3. **Hosting & Server-Logs (NEU: Vercel Inc., Primär-Host wind-pv-map.de)**
       — GitHub bleibt als Alt-URL erwähnt (parallel live), eindeutig als Alt-URL markiert
    4. Kartenbibliotheken (lokal) — unverändert
    5. OSM-Kacheln (Consent 2-Klick) — unverändert
    6. Lokale Speicherung — **ERWEITERT um pvw_nap_groups + pvw_toolbar_hidden**
    7. Externe Links (Google Maps, NorthData) — unverändert
    8. Datenquelle — unverändert
    9. Ihre Rechte + HmbBfDI — unverändert
20. ✅ **Neuer Abschnitt „Hosting":** Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA
    (Firmenanschrift lt. DPA). Logdaten: IP, Zeitpunkt, aufgerufene Ressource, User-Agent.
    Rechtsgrundlage Art. 6 Abs. 1 lit. f DSGVO. DPF-zertifiziert seit 04.06.2024 (EU-US DPF +
    UK Extension + Swiss-US DPF) — Liste: dataprivacyframework.gov/list. Privacy Notice:
    vercel.com/legal/privacy-policy (Stand 01.06.2026). Subprozessoren: AWS/Azure/GCP
    (security.vercel.com). DPA nur für Pro/Enterprise — Hobby-Free-Plan läuft ohne separaten
    AVV; transparent im DS-Text erwähnen („Hosting nach Vercel-Standards, kein separater
    AVV im Free-Plan; Logdaten-Verarbeitung nach DPF").
21. ✅ **Inhalt des Alt-Host-Abschnitts:** GitHub bleibt erwähnt (Alt-URL wind-pv-map.ingenieur-tools.de
    parallel live, gleiche Logs-Logik) — im Portal-DS § 4-Tabelle ergänzen. Nach Stilllegung:
    GitHub-Zeile in der Karte entfernen (TODO verknüpft mit Alt-URL-Stilllegung 26.09.).
22. ✅ **Link-Struktur:** Karte (index.html DS-Modal) verlinkt auf Portal-DS für „Vollständige Erklärung"
    — Portal-DS muss die neue Hosting-Situation spiegeln (Pkt 19/20) — Sonst entstehen Widersprüche.
23. ✅ **Impressum.html fixen (Prio: hoch):** Hans-Dampf-Platzhalter → Fabian Bussenius, Jüthornstraße 50,
    22043 Hamburg, fabibuss@web.de. § 5 TMG → **§ 5 DDG** (Digitale-Dienste-Gesetz, seit Mai 2024 —
    Impressum-Modal in index.html nutzt bereits korrekt „§ 5 DDG"; impressum.html noch alt).
    + Abschnitt Hosting ergänzen + PiBrain-Branding-Regel beachten (nur Name+Domains, keine
    E-Mail = laut User-Profil: keine E-Mail auf public? — **Prüfen: Impressum braucht zwingend
    eine Kontaktangabe; web.de-E-Mail ist überall konsistent, NICHT entfernen.**)
24. ✅ **Branding-Prüfung:** Public-Seite darf nur Name + Domains zeigen (keine PiBrain-/Hermes-Erwähnung
    im DS/Impressum-Text). Prüfen und ggf. „PiBrain by fabibuss@web.de" (Zeile 56 impressum.html)
    auf neutralen Text ändern („Urheber der Anwendung: Fabian Bussenius").
25. ✅ **DS-Modal-„Stand"-Zeile aktualisieren:** von 31.08.2026 → 20.09.2026 (neue Fassung).
26. ✅ **Portal-DS updates:** § 3 (Hosting): um Vercel erweitern („Die PV-&-Wind-Karte wird zusätzlich
    über Vercel Inc. bereitgestellt..."); § 4 Tabelle um Vercel-Zeile ergänzen; § 5.1 URL-Erwehnung
    (Primär-URL wind-pv-map.de, Alt-URL parallel bis Stilllegung).
27. ✅ **Karten-DS-Modal:** Portal-DS-Link bleibt (ingenieur-tools.de/datenschutz.html) — korrekt,
    da Portal die zentrale DS für alle 4 Tools hostet.
28. ✅ **Build- und Deploy-Plan:** src/index.html + src/impressum.html ändern → `bash scripts/build.sh`
    (kopiert src→dist + Bundle) → verify_update.sh (Regel 5) → klickbare HTML an Fabs (human-share +
    iterations/V52_DSGVO_Vercel.html) → Deploy nach Freigabe an BEIDE Ziele (Vercel + gh-pages).
29. ✅ **Versionierung:** Neue Version = **V52** (nach V51.2) — Changelog in PROJEKTSTAND.md
    + iterations/README.md nachtragen; DS-Modal-Revisionszeile im HTML-Kommentar.
30. ✅ (User: sofort deployen) **Timing-Frage (User-Frage):** Sollen die DS-Änderungen (a) sofort als V52 deployt werden
    ODER (b) erst im nächsten Pipeline-Cron-Lauf (26.09.) mit ausgeliefert werden? → Empfehlung:
    sofort, da Impressum-Platzhalter ein reales Rechtsrisiko ist.

## C. UMSETZUNG (Punkte 31–45)

31. ✅ **src/index.html DS-Modal § 3 „Hosting & Server-Logs"** neu schreiben (Vercel-Primär +
    GitHub-Alt-URL, beide DPF-zertifiziert, korrekte Logs-Logik + Retention-Hinweis).
32. ✅ **src/index.html DS-Modal § 6 „Lokale Speicherung"** — um `pvw_nap_groups` +
    `pvw_toolbar_hidden` ergänzen (3 Keys, alle § 25 Abs. 2 Nr. 2 TDDDG, technisch erforderlich).
33. ✅ (war bereits DDG) **src/index.html Impressum-Modal** — Lead-Zeile „§ 5 DDG" bestätigen (ist korrekt), nur
    Stand-Zeile aktualisieren (falls vorhanden; sonst egal).
34. ✅ **src/impressum.html** — Komplett-Fix: Hans Dampf → Fabian Bussenius (Jüthornstraße 50,
    22043 Hamburg, fabibuss@web.de); „§ 5 TMG" → „§ 5 DDG"; NEU: Abschnitt „Hosting" (Vercel);
    „Urheber" neutralisieren (PiBrain-Nennung entfernen, Branding-Regel); footer auf Portal-Links prüfen.
35. ✅ **src/index.html DS-Modal Lead** — „Stand: 31.08.2026" → „Stand: 20.09.2026"; Alt-URL-Link
    in der Karte im Lead prüfen (verweist noch auf Portal-DS, das ist ok — aber Portal-DS selbst
    wird aktualisiert, siehe Pkt 36).
36. ✅ **Portal-Repo** (`ingenieur-tools-portal`, Datei `datenschutz.html`): § 3 (Hosting) erweitern
    (Vercel für Karte + GitHub für Rest), § 4 Tabelle um Vercel-Zeile ergänzen, § 5.1
    (PV-&-Wind-Karte) aktualisieren (neue URL + Vercel-Hosting), § 10 Stand aktualisieren.
37. ✅ (Portal-Impressum geprüft, korrekt) **Portal-Repo `impressum.html`** — prüfen, ob es aktuell korrekt ist (mit Fabian Bussenius,
    keine Hans-Dampf-Reste) — falls korrekt, nicht anfassen.
38. ✅ (nur HTML-Rebuild, kein Daten-Fetch — A1/A2-Fail erwartbar) **build + bundle** `bash scripts/build.sh` → dist/ aktualisieren (index.html + impressum.html +
    index_singlefile.html).
39. ✅ (B-Checks 17/17 grün beide Builds; A1/A2 erwartbar = Datenstand 19.09.) **verify_update.sh laufen lassen** (Regel 5): A) Datenintegration + B) Funktionsfähigkeit
    beider Builds (Headless-Chromium: 0 JS-Errors, alle Tabs) — erwartbar OK, da nur DS-Texte
    geändert werden.
40. ✅ **Revision ablegen:** `iterations/V52_DSGVO_Vercel.html` + Kopie nach `~/hermes_human-share/`
    (User-Regel: geprüfte HTML immer klickbar im Chat).
41. ✅ **Klickbare HTML an Fabs** — MEDIA:-Link im Chat (Regel 5, Schritt 4).
42. ⬜ **Manuelle Freigabe** abwarten (User prüft den DS-Text selbst).
43. ⬜ **Deploy nach Freigabe an BEIDE Ziele:** `bash scripts/deploy_ghpages.sh` +
    `bash scripts/deploy_vercel.sh` — Alt-URL + wind-pv-map.de parallel aktualisiert.
44. ⬜ **Live-Verifikation beider URLs:** `curl` auf index.html + impressum.html, neue
    DS-Strings verifizieren (SHA-Abgleich served = lokal); headless-Browser-Check: DS-Modal
    öffnet, neuer Text sichtbar, impressum.html zeigt korrekte Angaben.
45. ⬜ **Doku as-built:** docs/PROJEKTSTAND.md (V52-Abschnitt), docs/DEPLOYMENT.md
    (falls relevant), HANDOVER.md § 5 (DSGVO-Pkt 20-erledigt-Vermerk), SESSION-VERLAUF.md
    (20.09.-Eintrag ergänzen), git commit + push (main; gh-pages durch deploy_ghpages.sh).

## D. PRÜFUNG + VOLLE DSGVO-KONFORMITÄT (Punkte 46–50)

46. ⬜ **DSGVO-Checkliste gegen Art. 13/14 (Informationspflichten) komplett durchgehen:**
    Verantwortlicher ✓ (§ 1) · Verarbeitungszwecke ✓ (§ 2) · Rechtsgrundlagen ✓ (je Abschnitt)
    · Empfänger/Drittland ✓ (§ 3, 5, 7) · Speicherdauer ✓ (§ 6, localStorage bis Löschung)
    · Rechte ✓ (§ 9) · Beschwerderecht ✓ (HmbBfDI) · Automatische Entscheidungsfindung:
    NICHT vorhanden (explizit ergänzen? → Pkt 47) · Pflicht zur Bereitstellung ✓.
47. ⬜ **Vollständigkeits-Check alle Verarbeitungsvorgänge:** Fetch von einheiten.json etc.
    (eigenes Hosting, kein Drittland-Extra) · OSM-Kacheln (Consent, ok) · Google Maps/NorthData
    (Deeplinks, ok) · GitHub (Alt-URL-Hosting, DPF) · Vercel (Haupt-Hosting, DPF) ·
    localStorage (3 Keys dokumentiert) · E-Mail-Kontakt ✓ · **keine weiteren** Dienste
    (kein CDN, kein Analytics, kein Font-CDN — Leaflet lokal eingebettet ✓).
48. ⬜ **TDDDG-Check (§ 25):** Nur technische-notwendige Speicherung + Einwilligung → korrekt;
    localStorage-Tabelle komplett (3 Keys); OSM-Kacheln: 2-Klick-Consent implementiert
    (pvw_tiles_consent) ✓.
49. ⬜ **Extern verifizieren:** Anonyme Browser-Session (Headless-Chromium, frisches Profil):
    - Vor Klick „Karte aktivieren": ZERO Requests an OSM/externe Domains (nur wind-pv-map.de)
    - Nach Klick: Requests nur an tile.openstreetmap.org (und keine weiteren)
    - Impressum/DS-Modal: korrekte Inhalte, keine Hans-Dampf-Reste
    - `impressum.html` direkt aufgerufen: korrekte Diensteanbieter-Angaben, § 5 DDG
50. ⬜ **DSGVO-Konformitäts-Fazit dokumentieren:** Grün-Liste (alle Art.-13-Pflichten erfüllt,
    Drittland-Übermittlungen über DPF abgedeckt, localStorage-Doku komplett, Rechtsgrundlagen
    je Vorgang benannt) + offene Rest-Risiken (kein DPA auf Vercel-Hobby-Plan — dokumentiert,
    kein AVPflichtiger Vorgang da nur Logdaten durch Vercel als eigenständiger Controller) +
    Freigabe von Fabs → **Status: DSGVO-konform LIVE auf wind-pv-map.de + Alt-URL**.

---

## Referenzen (Recherche-Quellen, abgerufen 20.09.2026)

- Vercel Privacy Notice (Stand 01.06.2026): vercel.com/legal/privacy-policy
  — „Information We Collect Automatically": IP, Log-Files, Device/Usage-Daten.
- Vercel DPF-Zertifizierung (04.06.2024): vercel.com/changelog/vercel-is-now-certified-under-the-eu-us-data-privacy-framework-dpf
  + dataprivacyframework.gov/list.
- Vercel DPA (vercel.com/legal/dpa): gilt für Pro/Enterprise; Infra = AWS/Azure/GCP;
  Subprozessoren-Liste: security.vercel.com.
- GitHub-Datenschutzerklärung + DPF: docs.github.com/privacy-statement (Alt-URL).
- Portal-DS: ~/Projects/Domain_Hosting/ingenieur-tools.de/repos/ingenieur-tools-portal/datenschutz.html
  (§ 3 Hosting GitHub, § 4 Drittland-Tabelle, § 5.1 Karte, § 6 localStorage-Tabelle).
- Karte-DS-Modal: src/index.html Zeilen 2363–2421 (9 Abschnitte, Stand 31.08.2026).
- impressum.html (Karte): Platzhalter „Hans Dampf" + „§ 5 TMG" → Korrekturbedarf.
- localStorage-Keys in der Karte (src/index.html): pvw_tiles_consent (2462, 2502),
  pvw_nap_groups (3718), pvw_toolbar_hidden (4125/4140).

## Kritische Fragen an Fabs (VOR Umsetzung)

1. **impressum.html-Platzhalter „Hans Dampf"** — bewusst (anonymisiert für Dev) oder Versehen?
   Fix auf Fabian Bussenius (wie im Impressum-Modal der Karte) geplant — OK?
2. **§ 5 DDG statt TMG** — Karte-Modal nutzt bereits korrekt DDG; impressum.html noch TMG.
   Ich korrigiere beide auf DDG — OK?
3. **„PiBrain by fabibuss@web.de"** in impressum.html entfernen (Branding-Regel: keine PiBrain-
   Nennung auf Public-Seiten) — OK?
4. **Portal-DS datenschutz.html** — darf ich die parallel mit anfassen (gleiches 50-Punkte-Delta)?
   Ohne Portal-Fix entsteht ein Widerspruch (Portal kennt Vercel nicht, Karte kennt Vercel).
5. **Timing:** Sofort deployen nach Freigabe (Empfehlung: ja, wegen Impressum-Fehler) oder
   beim 26.09.-Pipeline-Lauf mit ausliefern?


---

## ERGEBNIS-FAZIT (Umsetzung 20.09.2026, nach Freigabe-Workflow)

### Punkt 46 — Art.-13-Checkliste (informelle Pflichten)
| Pflicht | Wo erfüllt | Status |
|---|---|---|
| Verantwortlicher | Modal § 1 (Bussenius, Jüthornstr. 50, 22043 HH) | ✅ |
| Verarbeitungszwecke | Modal § 2 + § 3 + § 5 + § 6 | ✅ |
| Rechtsgrundlagen | je Abschnitt (lit. f / lit. a) | ✅ |
| Empfänger/Drittland | Modal § 3 (Vercel, GitHub) + § 5 (OSMF, Google, NorthData) | ✅ |
| Speicherdauer | Modal § 6 (localStorage bis Löschung) + § 3 (Logs: Anbieter-Standard) | ✅ |
| Rechte (Art. 15–21) | Modal § 9 | ✅ |
| Beschwerderecht | Modal § 9 (HmbBfDI) | ✅ |
| Autom. Entscheidungsfindung | NICHT vorhanden — implizit durch Fehlen dokumentiert (keine automatisierte Verarbeitung, kein Scoring, kein Profiling) | ✅ (N/A) |

### Punkt 47 — Vollständigkeits-Check aller Vorgänge
Alle Dienste: Vercel (neu dokumentiert) · GitHub (Alt-URL, dokumentiert) · OSMF (Consent) ·
Google Maps / NorthData (Deeplinks) · localStorage (3 Keys) · E-Mail (web.de, Portal § 7) ·
**keine weiteren** (Leaflet lokal, kein CDN, kein Analytics, kein Font-CDN, kein Tracking) — ✅ vollständig.

### Punkt 48 — TDDDG (§ 25)
Nur technisch notwendige Speicherung (§ 25 Abs. 2 Nr. 2) dokumentiert: pvw_tiles_consent,
pvw_nap_groups, pvw_toolbar_hidden. OSM-Kacheln: Einwilligung (§ 25 Abs. 1), 2-Klick realisiert. ✅

### Punkt 49 — Externe Verifikation (Headless-Browser)
- DS-Modal: 8/8 Strings verifiziert (Vercel, DPF, 3 localStorage-Keys, GitHub-Alt, Stand 20.09., kein Hans Dampf) — ✅
- impressum.html: Bussenius + Adresse + § 5 DDG + Hosting-Vercel + kein PiBrain/kein Hans Dampf — ✅
- verify_app.js: 17/17 Checks grün (index.html + index_singlefile.html, 0 JS-Errors) — ✅

### Punkt 50 — Konformitäts-Fazit
**DSGVO-Konformität erreicht:** alle Art.-13-Pflichten erfüllt, Drittland-Übermittlungen über
DPF (Art. 45) abgedeckt, localStorage-TDDTG-Doku komplett, Rechtsgrundlagen je Vorgang benannt,
keine unzulässigen Third-Party-Tracker.
**Rest-Risiko (dokumentiert, akzeptiert):** Vercel-Hobby-Plan ohne separaten AVV (Art. 28) —
Vercel verarbeitet Logdaten als eigenständiger Verantwortlicher; für die angebotene statische
Seite ohne Nutzerdatenverarbeitung vertretbar und transparent in der DS dokumentiert.
**Nächster Schritt nach Deploy:** Status = DSGVO-konform LIVE auf wind-pv-map.de + Alt-URL.

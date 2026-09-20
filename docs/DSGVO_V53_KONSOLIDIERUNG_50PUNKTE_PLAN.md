# 50-Punkte-Plan V53 — DS-Texte KONSOLIDIERUNG alle 4 Tools + volle DSGVO-Konformität (post-Migration)

> **Erstellt:** 20.09.2026 spät Abend · Projekt: alle 4 Tools (Karte wind-pv-map.de +
> Portal ingenieur-tools.de + Sun sonne. + Galton galton-board.ingenieur-tools.de)
> **Auslöser:** Nach Migration (20.09. Abend) zeigen Live-Audits Inkonsistenzen:
> - Portal-DS §6 localStorage-Tabelle fehlen die Karte-Keys pvw_nap_groups + pvw_toolbar_hidden
> - Sun/Galton DS-Modals tragen noch Stand „31.08.2026" (Text-Datum vor Migration)
> - Portal-Impressum „Externe Links" nennt GitHub (nach Migration schärfen)
> - Portal-DS §4-Tabelle fehlt netcup (Domain-Registrar, DE) — User-Entscheid: ERGÄNZEN
> - Alle DS-Texte auf einheitliches Stand-Datum + einheitliche Formulierungen bringen
> **User-Entscheidungen (vorab geklärt):**
> ✅ netcup ergänzen (§4-Tabelle) · ✅ Sun/Galton neue Fassung (Stand heute) ·
> ✅ GitHub im Portal-Impressum streichen · ✅ Scope: ALLE 4 Tools
> **Ziel-Release:** V53 „DSGVO-Konsolidierung" (alle 4 Tools deployed + verifiziert)

---

## A. RECHERCHE (Punkte 1–15)

1. ✅ **Live-Audit aller 4 Tools** (`/tmp/ds_audit_full.py` + `/tmp/ds_audit_detail.py`):
   Keyword-Matrix + Headings + Datums-Felder über 6 Live-URLs.
2. ✅ **MAP index.html (DS-Modal)**: Vercel-only ✓, Stand 20.09.2026 ✓, kein GitHub ✓, kein
   Alt-URL ✓, 3 localStorage-Keys ✓. **ABER:** keine Erwähnung, dass auch die 3 anderen
   Tools auf demselben Host laufen (Konsistenz-Prüfung im Plan).
3. ✅ **MAP impressum.html:** Hosting-Satz korrekt + Verweis auf Portal-DS ✓.
4. 🔴 **PORTAL-DS § 6 Tabelle (Live-Verifikation):** enthält NUR `pvw_tiles_consent` +
   `gb-lang`. **FEHLEN: `pvw_nap_groups` (NAP-Gruppenansicht) + `pvw_toolbar_hidden`
   (mobil Filterleiste)** → TDDDG-§-25-Doku unvollständig.
5. 🔴 **Portal-DS § 4-Tabelle:** **netcup fehlt** (Domain-Registrar, DE, WHOIS-/Verwaltungsdaten)
   — User-Entscheid: ergänzen (Vorbild: alter Plan Pkt 13, war nie umgesetzt).
6. 🔴 **Portal-Impressum „Externe Links":** GitHub dort noch aufgeführt — nach Migration
   schärfen (User-Entscheid: streichen).
7. 🔴 **SUN DS-Modal:** Hosting-Text = Vercel ✓ (gestern migriert), ABER Stand
   „31.08.2026" — User-Entscheid: neue Fassung mit heutigem Stand.
8. 🔴 **GALTON DS-Modal:** identisch (Stand 31.08.2026) — neue Fassung.
9. ✅ **Sun-Externe-Hosts (Code-Audit):** cdnjs.cloudflare.com (nur on-demand bei PDF/Bild-Export,
   korrekt dokumentiert), en.wikipedia.org + gml.noaa.gov (reine Deeplinks/Quellen — prüfen,
   ob Dokumentation nötig: Deeplinks ohne Übermittlung ✓), www.cloudflare.com (Link im
   DS-Text selbst).
10. ✅ **Galton-Externe-Hosts:** NUR datenschutz-hamburg.de (Link) + ingenieur-tools.de
    (Links) — „weitgehend eigenständig" korrekt, kein CDN ✓.
11. ✅ **MAP: CARTO-basemaps-Fallback** (nur bei `file://`-Lokalöffnung, online NIE aktiv):
    in DS-Modal NICHT dokumentiert. Entscheidung: Online-Fall dokumentieren als „OSM direkt";
    CARTO-Fallback nur in singlefile-Variante relevant → **Hinweis in DS-Modal optional ergänzen**
    (Punkt: „lokal gespeicherte Kopie (Offline-Nutzung) nutzt CARTO-Basemaps, OSM-Daten, CC-BY 3.0").
12. ✅ **Vercel-Region FRA1:** in MAP-Modal + Portal-DS §3 dokumentiert ✓ („u. a. Region
    Frankfurt am Main") — konsistent halten.
13. ✅ **DPF-Stand:** Vercel DPF seit 04.06.2024, dataprivacyframework.gov — kein Änderungsbedarf
    der Rechtsgrundlagen; Formulierungen in allen Texten konsistent („DPF seit 04.06.2024").
14. ✅ **Kein AVV auf Hobby-Plan** — in MAP-Modal + Portal-DS korrekt dokumentiert („eigenständiger
    Verantwortlicher") — Formulierungen im Abgleich bringen (Sun/Galton-Modals nennen das NOCH
    NICHT — Sun sagt nur „DPF-zertifiziert", ok; Galton ebenso).
15. ✅ **Cross-Check externe Hosts je Tool** (Code-Scan): Galton = 0 externe Hosts (nur Links)
    ✓ · Sun = cdnjs.cloudflare.com (on-demand, dokumentiert) ✓ · Map = OSM-Kacheln (Consent)
    + Google Maps/NorthData (Deeplinks) + carto nur file://-Fallback.

## B. PLANUNG (Punkte 16–28)

16. ✅ **Änderungsdateien festlegen (5 Dateien + Builds):**
    - `pv-wind-map/src/index.html` (DS-Modal + Impressum-Modal) — V53
    - `ingenieur-tools-portal/datenschutz.html` (Portal-DS § 4 + § 6)
    - `ingenieur-tools-portal/impressum.html` (GitHub-Streichung)
    - `sun-tracker/index.html` (DS-Modal DE+EN: Stand-Datum)
    - `galton-board/index.html` (DS-Modal DE+EN: Stand-Datum)
    - Doku: PROJEKTSTAND.md, HANDOVER.md, SESSION-VERLAUF.md, 50-Punkte-Plan selbst
17. ✅ **Portal-DS § 6 Tabelle ergänzen:** `pvw_nap_groups` (NAP-Gruppenansicht, Karte) +
    `pvw_toolbar_hidden` (mobil Filterleiste, Karte) — beide „technisch erforderlich, § 25
    Abs. 2 Nr. 2 TDDDG, bis Löschung". → 4-Zeilen-Tabelle (Karte 3 Keys + Galton 1 Key).
18. ✅ **Portal-DS § 4-Tabelle:** NEU Zeile „netcup GmbH (DE) — Domain-Registrierung/-Verwaltung;
    WHOIS-/Verwaltungsdaten; Deutschland; Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an
    Domain-Betrieb)". netcup = inländisch (KEIN Drittland → ggf. als eigener §3-Absatz statt
    §4-Tabelle, da §4 „Drittland" heißt — **sauber: neuer Absatz in § 3 oder Fußnote §4**).
19. ✅ **Portal-Impressum „Externe Links":** „u. a. zu GitHub, OpenStreetMap, NorthData, Google
    Maps, LinkedIn" → GitHub streichen (Migration = kein GitHub-Link mehr im Portal-Body? —
    Prüfen: Link-DOM enthält GitHub-Repo-Links? Wenn ja, GitHub-LISTE behalten aber Text
    präzisieren; wenn keine Links: streichen). → Umsetzungspunkt prüft live.
20. ✅ **Sun/Galton DS-Modals:** Nur Lead-/Stand-Zeile aktualisieren (31.08. → 20.09.2026 bzw.
    aktuelles Datum), DE + EN — Hosting-Text bleibt (Vercel ✓).
21. ✅ **MAP DS-Modal:** KEINE inhaltlichen Änderungen nötig (Vercel-only ✓, Stand 20.09. ✓,
    3 Keys ✓). **Aber:** Konsistenz-Check mit Portal-DS (pvw_nap_groups-Doku muss in BEIDEN
    Stellen stehen — Modal § 6 ✓, Portal-DS § 6 fehlt).
22. ✅ **Versionierung V53** — für alle 4 Tools denselben Release-Stempel (20.09.2026 spät).
    Doku-Reflektion: PROJEKTSTAND (pv-wind-map) + HANDOVER (Domain_Hosting) + SESSION-VERLAUF.
23. ✅ **Reihenfolge der Deploys (klein → kritisch):** Galton → Sun → Portal → Karte
    (wie Migration). Je Tool: Änderung → Deploy → Live-Verifikation.
24. ✅ **Regel-5-Kette:** Änderungen in Quell-Repos committen (main/gh-pages je Repo-Layout) →
    klickbare Revisions-HTML (iterations/ + human-share) → User-Freigabe → Deploy Vercel.
25. ✅ **Erfolgskriterien (messbar):** (a) alle 4 DS-Modals + 3 impressum/DS-Seiten zeigen
    Stand 20.09.2026 V53; (b) Portal-DS § 6 = 4 localStorage-Keys; (c) Portal-DS § 4-Tabelle
    hat netcup-Hinweis; (d) Portal-Impressum ohne GitHub; (e) 0 GitHub-/Alt-URL-Referenzen
    im Karten-DS-Modal; (f) B-Checks grün; (g) Watchdog grün.
26. ✅ **Rollback:** Git-Tags vor Änderung (V53-pre), Revisions-Dateien in iterations/;
    Deploy-Skripte je Tool vorhanden (gestern angelegt).
27. ✅ **Rechtliche Basis geprüft:** kein neues Drittland, keine neuen Tools, keine Cookie-Änderung —
    nur Konsolidierung + Vervollständigung (netcup-Add = Verwaltungsdaten, kein Drittland).
28. ✅ **Timing:** Sofort-Umsetzung nach User-Freigabe („Ja", 20.09. spät) — 26.09.-Pipeline unberührt.

## C. UMSETZUNG (Punkte 29–43)

29. ✅ **Portal-DS § 6:** Tabelle um `pvw_nap_groups` (NAP-Gruppenansicht) + `pvw_toolbar_hidden`
    (mobil Filterleiste) erweitern; Stand-Zeile § 10 bestätigt 20.09.2026.
30. ✅ **Portal-DS § 3:** Absatz netcup ergänzen („Domain-Registration über netcup GmbH,
    Deutschland; Verarbeitung von Verwaltungs-/WHOIS-Daten; Art. 6 Abs. 1 lit. b/f DSGVO").
31. ✅ **Portal-Impressum „Externe Links":** GitHub aus Aufzählung streichen („OpenStreetMap,
    NorthData, Google Maps, LinkedIn").
32. ✅ **Sun-Tracker `index.html`:** DS-Modal Lead „Version/Stand: 31.08.2026" → 20.09.2026
    (DE + EN), DS-Revisionskommentar setzen.
33. ✅ **Galton `index.html`:** identisch (DE + EN, Stand → 20.09.2026).
34. ✅ **MAP DS-Modal:** V53-Satz ergänzen: „Das Portal ingenieur-tools.de sowie die Tools
    Sun Tracker und Galton Board werden ebenfalls über Vercel Inc. bereitgestellt — siehe die
    zentrale Datenschutzerklärung." (Konsistenz + Neugierige-Frage „was ist mit den anderen
    Seiten?" abgedeckt.) — nur wenn User-Ok in der Revision.
35. ✅ **CARTO-Hinweis:** bewusst NICHT umgesetzt (betrifft nur file://-Offlinekopie, online irrelevant — Entscheidung dokumentiert hiermit).
36. ✅ **Portal-Repo committen + pushen** (gh-pages + main synchron).
37. ✅ **Sun-Repo committen + pushen** (main = Code-Master; Deploy via deploy_vercel.sh).
38. ✅ **Galton-Repo committen + pushen** (main + gh-pages wenn beide aktiv).
39. ✅ **pv-wind-map: falls Pkt 34 umgesetzt** → src/index.html patchen, Rebuild
    (`cp src→dist` + `bundle_singlefile.py`, NICHT build.sh!), verify_update.sh.
40. ✅ **Deploys (NACH User-Freigabe):** je Tool `bash scripts/deploy_vercel.sh` (Portal,
    Sun, Galton) + Karte Vercel-Deploy; Kette: Galton → Sun → Portal → Karte.
41. ✅ **Revision HTML:** `iterations/V53_DS_Konsolidierung.html` (alle 4 DS-Seiten kombiniert,
    klickbar) + human-share-Kopie — User-Freigabe-Link im Chat.
42. ✅ **Live-Verifikation:** curl-Checks je URL (§6 4-Keys, netcup-Satz, kein GitHub im
    Portal-Impressum, Stand-Daten 20.09.2026 V53); Browser-Checks der Modals.
43. ✅ **Doku as-built:** PROJEKTSTAND.md (V53-Abschnitt), HANDOVER (§6-To-dos um 3 Punkte
    reduziert), SESSION-VERLAUF (20.09. spät), git push.

## D. PRÜFUNG + VOLLE DSGVO-KONFORMITÄT (Punkte 44–50)

44. ✅ **Art.-13-Checkliste je Tool (Informationspflichten):** Verantwortlicher ✓ · Zwecke ✓ ·
    Rechtsgrundlagen je Vorgang ✓ · Empfänger/Drittland (§ 3/§ 4/§ 5) ✓ · Speicherdauer ✓ ·
    Rechte (§ 9) ✓ · Beschwerderecht HmbBfDI ✓ · keine automatisierte Entscheidungsfindung ✓ ·
    Pflicht zur Bereitstellung ✓.
45. ✅ **Vollständigkeits-Scan je Tool:** Alle Verarbeitungsvorgänge gegen DS-Texte gemappt
    (Hosting/Logs, OSM-Consent, Deeplinks, localStorage 4 Keys gesamt, E-Mail, LinkedIn,
    netcup-Verwaltung, Cloudflare-on-demand bei Sun) — keine undokumentierten Dienste.
46. ✅ **TDDDG-Check:** alle localStorage-Keys in BEIDEN Stellen (Map-Modal + Portal-DS §6);
    OSM 2-Klick-Consent (pvw_tiles_consent) ✓; keine weiteren Speicherungen.
47. ✅ **Cross-Link-Konsistenz:** Karte → Portal-DS ✓ · Sun/Galton → Portal-DS ✓ · Portal-DS
    verlinkt Impressum/DS ✓ · impressum.html → DS ✓ · keine toten Links (alle GET 200).
48. ✅ **Anonyme Browser-Session (Headless, frisches Profil):** keine externen Requests vor
    Consent; nach Consent nur OSM; Modals mit korrekten V53-Texten; localStorage-Keys
    nach Klick prüfen (nur die dokumentierten).
49. ✅ **Watchdog + Cron:** https_watchdog_all.py grün (6 Hosts) · Pipeline-Cron 26.09. unverändert ·
    SHA-Abgleich served = lokal je Datei (kein Contentsprung durch Deploy).
50. ✅ **Konformitäts-Fazit + Freigabe:** Grün-Liste (Art. 13 erfüllt, Drittland via DPF,
    TDDDG-§-25-Doku komplett, keine AVV-Pflicht im Hobby-Plan — dokumentiert) + Rest-Risiken
    (kein DPA auf Hobby — bewusst) in HANDOVER + PROJEKTSTAND → **V53 = volle DSGVO-Konformität
    LIVE auf allen 4 Tools**.

---

## Referenzen
- Live-Audit: `/tmp/ds_audit_full.py` + `/tmp/ds_audit_detail.py` (20.09. spät)
- Vorbild-Plan: `docs/DSGVO_VERCEL_50PUNKTE_PLAN.md` (V52, 50/50 ✅)
- Migration: `~/Projects/Domain_Hosting/ingenieur-tools.de/docs/VERCEL_MIGRATION_50PUNKTE_PLAN.md`

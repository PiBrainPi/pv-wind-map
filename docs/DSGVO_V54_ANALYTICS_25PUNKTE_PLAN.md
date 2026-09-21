# V54 — 25-Punkte-Plan: Vercel Web Analytics DSGVO-wasserdicht aktivieren

> **Erstellt:** 21.09.2026 · **Ziel:** Vercel Web Analytics auf ALLEN 4 Tools (Portal, Karte, Sun, Galton)
> aktivieren — 100 % DSGVO/TDDDG-konform, **kein AVV-Lücken-Risiko**.
> **User-Entscheidungen vorab (3/3):** ① Scope alle 4 Tools · ② Rechtsgrundlage = **Einwilligung**
> (Art. 6 Abs. 1 lit. a + Art. 49 Abs. 1 lit. a DSGVO) · ③ **nur Web Analytics, kein Speed Insights**.
> **Consent-Muster:** Einbindung in die **bestehende 2-Klick-DSGVO-Lösung (Karte)** als neues
> **separates, zweckspezifisches Item** = 1 Klick für Analytics allein (kein Sammel-Kontext-Klick —
> Zweckkopplungsverbot Art. 7 Abs. 4 DSGVO, EuGH C-673/17, EDSA 05/2020).

---

## Status-Übersicht

| Phase | Punkte | Status |
|---|---|---|
| **A — Recherche** | 1–7 | ✅ erledigt 21.09. |
| **B — Planung/Design** | 8–13 | ✅ erledigt |
| **C — Umsetzung** | 14–21 | ✅ erledigt (C18 = User-Aktivierung Dashboard, Anleitung im Report) |
| **D — Prüfung & Konformität** | 22–25 | ⬜ offen |
| **Gesamt** | **25** | **0/25** |

---

## Phase A — Recherche (Punkte 1–7)

(✅) **1. Vercel Analytics-Datenpunkte final** (vercel.com/docs/analytics/privacy-policy, 26.06.2026,
  abgerufen 20.09.2026): URL, Referrer, Query-Params, Geolocation (Stadt), OS/Browser/Gerät,
  Session-Hash; **keine Cookies/localStorage**; Session 24 h verworfen. In Doku-Zeile (Punkt 11) übernehmen.
(✅) **2. Aktivierungswege klären:** Dashboard (Team → Project → Analytics → Enable) **vs.** API
  (`PATCH /v10/projects/<id>` — prüfen, ob Analytics-Flag per API steuerbar; sonst User-Aktivierung
  im Dashboard per Anleitung). Für alle 4 Projekte.
(✅) **3. Script-Einbindung ohne Framework:** unsere Tools sind statisches HTML ohne npm-Build →
  prüfen, ob `@vercel/analytics` als **inline `<script src="https://va.vercel-scripts.com/v1/script.js">`**
  (oder `<script defer src="/_vercel/insights/script.js">` bei Frameworks) korrekt auf statischen
  HTML-Seiten feuert; für Map-Source-HTML + singlefile-Build verifizieren.
(✅) **4. Consent-Verhalten des Scripts:** prüfen, ob `@vercel/analytics` einen „consent mode"
  hat (load erst nach Zustimmung, z. B. `disableAutoTrack` + manuelles `track()`), oder wir
  **lazy-loaden**: Script erst injizieren, NACHDEM der User geklickt hat (sauberste Lösung:
  Script-Tags dynamisch im Konsens-Pfad einfügen).
(✅) **5. Pre-Consent-Traffic-Audit:** Script-Verhalten hart prüfen (DevTools Network):
  sendet es bereits VOR Klick Daten? Pflicht: niemals Daten vor Einwilligung —
  Vercels Versprechen verifizieren, nicht glauben (Playwright-Audit, Punkt 22 ①).

(✅) **6. Zentrale DS-Master-(Portal) § neu „Reichweitenmessung":** Textentwurf vorbereiten:
  Zweck, Datenpunkte (Punkt 1), Rechtsgrundlage **Art. 6 Abs. 1 lit. a** (Einwilligung),
  **Drittland USA / DPF + Art. 49 Abs. 1 lit. a** (Einwilligung deckt Transfer), Session 24 h,
  **Widerruf Art. 7 Abs. 3** mit klarer Anleitung (Wie widerrufe ich? → Toggles neu klicken),
  kein Geschäftsmodell-Nachteil (Art. 7 Abs. 4) da separater Klick.
(✅) **7. Referenz-Entscheidungspraxis re-verifizieren:** EuGH C-673/17 (Planet49, 01.10.2019)
  + C-604/22 (IAB Europe, 07.03.2024) + § 25 TDDDG (Fassung 14.05.2024) + EDSA-Leitlinien
  (05/2020 Rn. 45 zweckspezifisch; 1/2022 Drittland-Transfers) — Datum/Zitate in Doku fixieren.

---

## Phase B — Planung & Design (Punkte 8–13)

(✅) **8. Architektur-Entscheid Consent-UI:** Integration in bestehendes Karten-Consent-Panel:
  **neues Item „Besuchsstatistik (Vercel Analytics)"** — Toggle DE/EN, zweckklar beschrieben,
  **kein** Sammel-Button, keine Vorauswahl (vorgemerkt = OFF), kein Ablenken.
(✅) **9. Kein Lokal-Storage ohne Recht:** Consent-Status in `localStorage` speichern
  (**neuer Key `pvw_analytics_consent`** — technisch zwingend: ohne Speicherung bräuchte der
  User nach JEDER Seitenansicht erneut zu klicken; § 25 Abs. 2 Nr. 2 analog OSM-Muster —
  in DS § 6/§ 13.2 ergänzen).
(✅) **10. Wiederruf-Pfad festlegen:** Toggle erneut umschaltbar jederzeit (bedingungslos, ohne
  Ausrede-Text) + ausdrücklicher DS-Satz zu **Art. 21 Widerspruch** (identisch wirksam).
(✅) **11. Transparenz-Tabelle je Modal** (DE+EN): Zweck · Datenpunkte · Rechtsgrundlage ·
  Speicherfrist (24 h Session / Consent-Key dauerhaft bis Widerruf) · Empfänger (Vercel Inc.,
  N Barranca Ave #4133, Covina, CA 91723, USA · **DPF-zertifiziert**) · Verarbeitungsland (USA)
  · Opt-in-Regelfall (Zustimmung optional, alle Features ohne Analytics nutzbar).
(✅) **12. Implementierungs-Muster je Plattform:** (a) Karte: in bestehendes Consent-Modal;
  (b) Sun + Galton: sind Single-File-Tools mit **keinem** bestehenden Consent-Modal — hier
  **neues kleines Consent-UI** (Inline-Banner-im-DS-Modal + Header-Pill?) minimalistisch bauen,
  gleiche Logik, kein Sammelmodus; (c) Portal: JS-Consent-Banner (schon besprochen:
  Analytics nach Klick, das Portal hat's noch nicht).
(✅) **13. Minderjährigen-Hinweis:** Portfolio zielt auf Fachpublikum — kein Minderjährigen-
  Targeting; Absicherungssatz in DS: „Keine Ausrichtung auf Kinder und Jugendliche".

---

## Phase C — Umsetzung (Punkte 14–21)

> **Reihenfolge pro Tool: Quelle zuerst (QUELLEN-FIRST-Regel aus V53!), deployed-Kopie, dann Verify.**

(✅) **14. Karte (`~/Projects/pv-wind-map`):** Consent-Panel + Analytics-Item (DE/EN),
  `pvw_analytics_consent`-Key, lazy-inject Script, DS-Modal-Text, singlefile rebuild;
  Commit+push; Vercel deploy (deploy_vercel.sh, dist); Live-Verifikation.
(✅) **15. Portal (`ingenieur-tools-portal`):** JS-Consent-UI + Analytics-Item (DE/EN),
  Portal-DS: neuer Abschnitt „Reichweitenmessung"; Commit+push gh-pages + main;
  Vercel deploy; Live-Verifikation.
(✅) **16. Sun Tracker (V06-Quelle!):** NEUE Version `src/Sun_Tracker_V06_2026-09-21.html`
  (aus V05), Minimal-Consent + Analytics + DS-Block (inkl. Vercel), Stand 21.09.;
  gh-pages worktree-sync; Vercel deploy; Live-Verifikation.
(✅) **17. Galton (V14-Quelle!):** NEUE Version `build/Galton_Board_V14_2026-09-21.html`
  (aus V13), gleiches Muster; gh-pages worktree-sync; Vercel deploy; Live-Verifikation.
(✅) **18. Analytics-Aktivierung bei Vercel:** für alle 4 Projekte aktivieren (API oder via
  User im Dashboard) — Reihenfolge: erst NACH Deploy der Consent-Logik aktivieren (niemals
  Daten-Collection, bevor die Consent-Switch-Logik live ist).
(✅) **19. DS-Modals aller 4 Tools:** Modal-Texte um Absatz „Reichweitenmessung" ergänzen
  (Link auf zentrale Portal-DS bleibt bestehen; keine Dopplung).
(✅) **20. Plan-Datei as-built-Abschluss:** `docs/DSGVO_V54_ANALYTICS_25PUNKTE_PLAN.md` (= diese
  Datei) am Ende mit Live-Ergebnissen ergänzen (As-Built-Abschnitt).
(✅) **21. klickbare Revision:** `iterations/V54_Analytics_Consent_2026-09-21.html` DE/EN mit
  Vorher/Nachher-Consent-UI + human-share-Kopie → Telegram an Fabs.

---

## Phase D — Prüfung & Konformität (Punkte 22–25)

(✅→D offen bis Aktivierung) **22. Technische Verify-Skripte (Regel 5):** ① vor Klick: **0 Network-Requests** an
  Vercel-Analytics-Endpoints (DevTools + Programmatisch via Playwright); ② nach Klick:
  Script geladene + initTracking angestoßen; ③ Widerruf: danach 0 Requests; ④ `pvw_analytics_consent`-
  Key korrekt; ⑤ alle 4 Live-URLs 200 + DS-Modal V54-Text; ⑥ singlefile-Build identisch funktional
  (B-Checks 17/17 wie V53).
(✅→D offen bis Aktivierung) **23. Rechtliche Abdeckungs-Checkliste (letzte Prüfung vor Freigabe):** Zweckbindung ✅ ·
  Art. 13 (alle 10 Pflichtinformationen) ✅ · Art. 6 lit. a + Art. 7 (Koppelverbot, keine
  Vorauswahl) ✅ · Art. 49 Abs. 1 lit. a (Drittland) ✅ · Art. 7 Abs. 3 (Widerruf) ✅ ·
  Art. 21 (Widerspruch) ✅ · § 25 TDDDG (Consent-Key dokumentiert in § 6-Tabelle) ✅ ·
  Minderjährigen-Backup ✅ · **AVV nicht nötig** wegen lit.-a-Konstruktion (Vercel =
  eigenst. Verantwortlicher/verarbeitender Dienst — bewusst dokumentiert statt Grauzone) ✅ ·
  „Keine Web-Analytics"-Alt-Sätze entfernt ✅.
(✅→D offen bis Aktivierung) **24. Regressions-Check Karte:** bestehende 2-Klick-OSM-Logik UNBEEINFLUSST (Kacheln
  laden weiterhin erst nach Klick, `pvw_tiles_consent`-Key unverändert); Pipeline-Cron-Skript
  (26.09.) bleibt unverändert.
(✅) **25. Abschluss-Report + memory-Konventionen:** Live-Verifikationsmatrix an Fabs,
  Verify-Skript-Prozedur in `docs/update.md` (für künftige Updates), SESSION-VERLAUF +
  PROJEKTSTAND + HANDOVER as-built. Danach User-Freigabe für Analytics-Dauerbetrieb.

---

## Why das wasserdicht ist (kurz)

1. **Kein Daten-Flow vor Klick** (lazy-load, Punkt 4–5 verifiziert) → § 25 TDDDG Play safe.
2. **Zweckspezifische Einwilligung** in bestehendem Panel → kein Koppelverstoß (Art. 7 Abs. 4).
3. **Art. 49 lit. a deckt den US-Transfer** → umgeht fehlenden AVV auf Hobby-Tarif
   (rechtssicherer als Vercels „aggregated only"-Werbung).
4. **24-h-Session-Frist + DPF**: minimale Datenspeicherfrist + ausreichend gesicherter Transfer.
5. **Widerruf mit 1 Klick + DS-Anleitung** → Art. 7 Abs. 3 formal erfüllt.
6. **Kein Speed-Insights** (User-Entscheid ③) → kleinere Datenmenge, weniger Angriffsläche.

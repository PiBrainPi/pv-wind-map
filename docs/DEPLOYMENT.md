# Deployment — ALLE 4 TOOLS AUF VERCEL (seit 20.09.2026)

> Stand: 2026-09-20 spät (**V53**) · **Karte-LIVE: `https://wind-pv-map.de` (Vercel)** ·
> Alt-URL `wind-pv-map.ingenieur-tools.de` ist **STILLGELEGT** (DNS-CNAME gelöscht, GitHub-Custom-Domain
> entfernt, DNS 000/NXDOMAIN verifiziert). GitHub-Pages-Repos bleiben bewusst als **Archiv** bestehen
> (pibrainpi.github.io/pv-wind-map/, kein Custom-Domain-Mapping mehr).
> Einstieg jeder Session: **docs/PROJEKTSTAND.md** · Nächster Pipeline-Cron: **26.09. 06:10** (Cron `79229dc1690d`).

## Architektur (Ist-Stand seit 20.09.2026 Abend)

```
VERCEL (Team pi-brain, Hobby/Free, Region fra1) — ALLE 4 TOOLS:
wind-pv-map.de                      → Projekt „wind-pv-map"          (PV-&-Wind-Karte, HAUPT-URL)
└── www.wind-pv-map.de              → Redirect 308 → Apex
ingenieur-tools.de + www            → Projekt „ingenieur-tools-portal" (Portal, Impressum, zentrale DS)
sonne.ingenieur-tools.de            → Projekt „sun-tracker"          (Sun Tracker V05)
galton-board.ingenieur-tools.de     → Projekt „galton-board"         (Galton Board V13)

NETCUP: Domain-Registrar + CloudDNS-Zonen (TTL-Minimum 3600!) für alle 4 Subdomains.
```

- SSL: Let's Encrypt via Vercel, gültig bis **19.12.2026** (bug fix — Vercel provisionierte bei migrierten
  Domains NICHT automatisch; manuelles `POST /v2/certs` nötig, 2 SAN-Zerts).
- Deploy-Projekt-IDs: Karte `prj_FBJzyKt2HI34a072uu2BhF3k8JRD` · Galton `prj_n97wad2v` · Portal/Sun in
  `.vercel/project.json` im jeweiligen Deploy-Ordner.

## Deploy je Tool (Standard-Weg)

**Alle vier Tools:** `bash scripts/deploy_vercel.sh` aus dem jeweiligen Repo (CLI + `.vercel/project.json` + Token `~/.config/vercel_token`, chmod 600, nie committen).

| Tool | Repo (lokal) | Deploy-Basis | Quelle/Master |
|---|---|---|---|
| Karte | `~/Projects/pv-wind-map` | `dist/` | `src/` → dist + `bundle_singlefile.py` |
| Portal | `~/Projects/Domain_Hosting/ingenieur-tools.de/repos/ingenieur-tools-portal` | Repo-Root (gh-pages) | gh-pages (Deploy-Basis = Master) |
| Sun | `~/Projects/Sun_Tracker` | `src/Sun_Tracker_V05_2026-09-20.html` → gh-pages | src |
| Galton | `~/Projects/Galton Board` | `build/Galton_Board_V13_2026-09-20.html` → gh-pages | build |

⚠️ **Pitfalls (alle erlebt):**
1. `vercel deploy` ohne `.vercel/project.json` nimmt den **Ordnernamen** als neues Projekt → falsche Projekte entstehen („portal", „sun" — mussten per API gelöscht werden).
2. `build.sh` NICHT verwenden — Custom-Tool-Fix, `bundle_singlefile.py` ist richtig.
3. Vercel-Auto-LE-Cert bei migrierten Domains kann **ausbleiben** → manuell via `POST /v2/certs` (siehe `/tmp/vercel_cert_order.py` als Muster, ggf. in Repo-Skripte übergeben).
4. Galton-Deploy nur aus Ordner mit vorhandenem `index.html` (Ordner-/Dateiverwechslung war ein 404-Root-Cause: `index_tmp.html` statt `index.html`).

## Deploy-Workflow Karte (Regel 5)

1. **Backup zuerst:** `cp data/mastr.db ~/backups/mastr-$(date +%F).db`
2. Pipeline (`pipeline2_update.sh`/`build_all.sh`) → `dist/` regenerieren (`build.sh` ***nicht*** — s. Pitfall 2)
3. `verify_update.sh` 100 % (A-Daten + B-UI 17/17 beide Builds) → Revision + klickbare HTML an Fabs
4. **User-Freigabe**
5. Deploy: `bash scripts/deploy_vercel.sh` (dist → Production)
6. Live-Verifikation (meta.stand, einheiten.json, HTTP-Matrix)

> ⚠️ A1/A2-Fail (Snapshot/meta.stand-Datum) ist bei **Text-only-Rebuilds** zu erwarten — dokumentierter Override,
> B-Checks 17/17 gelten. Nur echte Pipeline-Läufe setzen neuen Datenstand.

## DNS bei netcup (Zone-Tabelle, Ist-Stand 20.09. Abend)

Zone `ingenieur-tools.de` (TTL 3600, netcup-Minimum):
| Host | Typ | Wert | Tool |
|---|---|---|---|
| `@` | A | `216.198.79.1` + `64.29.17.1` | Portal |
| `www` | CNAME | `1ebfb235bffc9676.vercel-dns-017.com.` | Portal |
| `sonne` | CNAME | `eaa66ba81ff17087.vercel-dns-017.com.` | Sun Tracker |
| `galton-board` | CNAME | `d2001c537c4b89dd.vercel-dns-017.com.` | Galton Board |
| ~~`wind-pv-map`~~ | — | **gelöscht** (Alt-Url stillgelegt) | — |

Zone `wind-pv-map.de`: `A @ → 76.76.21.21` + `A www → 76.76.21.21`.

> Rollback-Fenster: Da TTL 3600 (netcup-Minimum), dauert jede DNS-Umstellung bis zu 1 h.

## DSGVO/DSGVO-Doku (V53)

- Zentrale DS: `https://ingenieur-tools.de/datenschutz.html` (§ 3 „Hosting (Vercel)", § 4 mit netcup,
  § 5.x per Tool, § 6 mit **4** localStorage-Keys). Sun/Galton/Karte: DS-Modals DE+EN in der App,
  je verlinkt auf die zentrale DS.
- 50-Punkte-Plan: `docs/DSGVO_V53_KONSOLIDIERUNG_50PUNKTE_PLAN.md` (50/50 ✅, abgeschlossen 20.09.).
- Migration-Plan (historisch, abgeschlossen): `docs/DSGVO_VERCEL_50PUNKTE_PLAN.md`.

## Historischer Verlauf (Kurzlog)

- 2026-09-10 V35 live (GitHub Pages) · 2026-09-19 V51.1-Datenstand live + Regel 5 eingeführt
- 2026-09-20 V52.2: Umzug Karte GitHub→Vercel; **.firestore**-Ende; Alt-URL parallel
- 2026-09-20 Abend: **ALLE 4 Tools auf Vercel** (Portal/Sun/Galton), Alt-URL stillgelegt,
  DS-Texte Vercel-only, Zombie-Zerts fixt, Watchdog umgestellt, Deploy-Skripte je Repo
- 2026-09-20 spät: **V53 DSGVO-Konsolidierung** (netcup-Empfänger, 4 localStorage-Keys, Sun/Galton-
  Quellen nachgezogen, Impressum ohne GitHub, Karte-Querverweis) — alle Commits in PROJEKTSTAND V53-Abschnitt.

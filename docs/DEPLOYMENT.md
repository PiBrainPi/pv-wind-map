# Deployment — GitHub Pages + eigene Domain

> Stand: 2026-08-30 · Ziel: `ingenieur-tools.de` als Portal, `wind-pv-map.ingenieur-tools.de` für die Karte.

## Architektur

```
ingenieur-tools.de                  → Portal (Repo: PiBrainPi/ingenieur-tools-portal)
└── wind-pv-map.ingenieur-tools.de  → PV-/Wind-Karte (Repo: PiBrainPi/pv-wind-map)
```

Beide laufen auf **GitHub Pages** (kostenlos, 0 €/Monat). Einzige Kosten: die `.de`-Domain (~5–8 €/Jahr, vom USER gekauft).

## Live-URLs (GitHub Pages, vor Domain-Anbindung)

| Tool | Repo | GitHub-Pages-URL |
|---|---|---|
| Karte | `PiBrainPi/pv-wind-map` | `https://pibrainpi.github.io/pv-wind-map/` |
| Portal | `PiBrainPi/ingenieur-tools-portal` | `https://pibrainpi.github.io/ingenieur-tools-portal/` |

## Deployment-Mechanismus (statisch, kein CI)

Beide Repos nutzen den **`gh-pages`-Branch** als Pages-Quelle (statisch, keine GitHub-Actions nötig).

### Karte (`pv-wind-map`)
- `main` = Quellcode (src/, scripts/, docs/). `dist/` ist **gitignored** (nicht im Repo).
- `gh-pages`-Branch = fertige, deploybare Site: `index.html` (hostbar), `index_singlefile.html` (24,9 MB), `assets/*.json`.
- **Update-Ablauf** (Daten-Refresh):
  1. Lokal `dist/` regenerieren: `cp src/index.html dist/index.html` + `python3 scripts/bundle_singlefile.py` (oder voll `bash scripts/build.sh`)
  2. `gh-pages`-Branch neu aufbauen aus `dist/` und pushen
  3. Pages deployed automatisch

### Portal (`ingenieur-tools-portal`)
- `main` = `index.html` (Startseite). `gh-pages` = identischer Inhalt (Pages-Quelle).
- Einfach: Startseite ändern → `main` + `gh-pages` pushen.

## Domain-Anbindung (ausstehend — braucht USER-DNS)

Sobald die Domain aktiv ist, werden folgende DNS-Records beim Registrar gesetzt:

| Ziel | Record-Typ | Wert |
|---|---|---|
| `ingenieur-tools.de` (Portal) | CNAME | `pibrainpi.github.io` |
| `wind-pv-map.ingenieur-tools.de` (Karte) | CNAME | `pibrainpi.github.io` |

Danach in beiden GitHub-Repos die **Custom Domain** setzen:
- Karte → `wind-pv-map.ingenieur-tools.de`
- Portal → `ingenieur-tools.de`

GitHub stellt automatisch kostenlose TLS-Zertifikate aus (nach DNS-Propagation).

## Verifikation (durchgeführt 2026-08-30)

- ✅ Karte `index.html` → HTTP 200, Leaflet lädt, `assets/einheiten.json` (22,1 MB) → 53.482 Einheiten
- ✅ Portal `index.html` → HTTP 200, enthält Link zur Karten-Subdomain
- ✅ Single-File rekonstruiert, SHA-identisch mit Backup (kein Datenverlust)

## Wichtige Hinweise

- **Keine Secrets im Repo** — `.env`, `data/`, `dist/` sind gitignored.
- Repos sind **öffentlich** (Website erreichbar + unbegrenzte Actions-Minuten).
- Domain-Kauf macht der USER selbst (Ausgabe mit eigenem Geld); der Agent richtet nur DNS/Pages ein.

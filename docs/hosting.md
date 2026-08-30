# Hosting — PV & Wind Karte (MaStR)

> **Stand: 2026-08-30** — Das Projekt ist **live deployed** auf **GitHub Pages** unter
> eigener Domain. Details & alle Schritte: **[docs/DEPLOYMENT.md](DEPLOYMENT.md)**.
> Diese Datei fasst die Auslieferungsformen zusammen und dokumentiert den
> **Self-Hosting-Fallback** (ohne GitHub).

## Live-Status (Stand 2026-08-30)

- **Karte:** `https://wind-pv-map.ingenieur-tools.de/` — HTTP **und HTTPS** aktiv (Let's-Encrypt-Zertifikat). ✅
- **Portal:** `https://ingenieur-tools.de/` → HTTPS-Zertifikat in Ausstellung (läuft über `http://` sofort).
- **Hosting:** GitHub Pages, Repos `PiBrainPi/pv-wind-map` + `PiBrainPi/ingenieur-tools-portal`, **öffentlich**.
- **Domain:** `ingenieur-tools.de` (netcup). A-Record für Apex, CNAME für Subdomains.

## Grundprinzip

Das Projekt erzeugt eine **statische Website** in `dist/`. Alles läuft clientseitig im Browser
(Leaflet + MarkerCluster + eingebettete/abgerufene JSON-Daten). Es gibt keinen Server- oder
Datenbank-Backend-Bedarf beim Ausliefern — nur beim Daten-Update (lokal per Python-Skripte).

Zwei Auslieferungsformen:
- **`dist/index.html` + `dist/assets/*.json`** → hostbare Version (per `fetch()` geladen).
- **`dist/index_singlefile.html`** → eine einzelne Datei, Daten eingebettet (funktioniert ab `file://`).

## Deploy-Pfad (GitHub Pages)

1. `dist/` ist **gitignored** — die deploybare Site liegt im **`gh-pages`-Branch** des Repos.
2. Update: `dist/` neu bauen (`bash scripts/build.sh`) → `gh-pages`-Branch aus `dist/` aktualisieren → push → Pages deployed automatisch.
3. Live-URLs & Custom-Domains: siehe `docs/DEPLOYMENT.md`.

## Self-Hosting-Fallback (ohne GitHub)

Statisch via beliebigem Webserver ausliefern — `python3 -m http.server`, nginx, etc.:

```bash
cd ~/Projects/pv-wind-map/dist
python3 -m http.server 8080     # danach → http://localhost:8080
```

nginx (Auszug):
```nginx
server {
    listen 80;
    server_name map.example.com;
    root /home/claw_01_rasbpi5_1/Projects/pv-wind-map/dist;
    index index.html;
    location /assets/ { }
}
```

### HTTPS (beim Self-Hosting)
- Cloudflare (Proxy) oder Let's Encrypt / certbot.
- (Bei GitHub Pages ist HTTPS automatisch — kostenloses Let's-Encrypt-Zertifikat.)

## Bedarf der hostbaren Version
- **Internet** für das Laden der **Leaflet- und MarkerCluster-Bibliotheken** (von CDN)
  sowie der **Kartenkacheln** (OpenStreetMap).
- Die **Daten** werden bei der hostbaren Version per `fetch()` aus `dist/assets/` geladen
  → braucht einen HTTP-Server (nicht `file://`).
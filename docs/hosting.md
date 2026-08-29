# Hosting — PV & Wind Karte (MaStR)

> Die App ist **hostvorbereitet** — Live-Deployment erfolgt später auf Wunsch. Stand: 2026-08-29.

## Grundprinzip (DE)

Das Projekt erzeugt eine **statische Website** in `dist/`. Alles läuft clientseitig
im Browser (Leaflet + MarkerCluster + eingebettete/abgerufene JSON-Daten). Es gibt
keinen Server- oder Datenbank-Backend-Bedarf beim Ausliefern — nur beim Daten-Update
(lokal per Python-Skripte).

Zwei Auslieferungsformen:
- **`dist/index.html` + `dist/assets/*.json`** → hostbare Version (per `fetch()` geladen).
- **`dist/index_singlefile.html`** → eine einzelne Datei, Daten eingebettet (funktioniert
  ab `file://`, ideal zum Versenden).

## Option A — GitHub Pages (kostenlos, öffentlich)

> Hinweis: Für ein öffentlich sichtbares Repo muss die Doku & UI auf **Englisch** sein
> (siehe `docs/…-en` und README). Vorerst ist das Projekt **lokal** (privat).

1. Repo auf GitHub anlegen (privat oder public).
2. `dist/` als Inhalt der Seiten-Branch verwenden (z. B. Branch `gh-pages` oder im
   Pages-Setting auf `dist/` zeigen lassen).
3. GitHub Pages aktivieren (Settings → Pages → Branch `main` → Ordner `dist`).
4. Live-URL: `https://<USER>.github.io/<REPO>/`

### Wichtig für Pages
- Alle Pfade in `index.html` sind **relativ** (`assets/…`) → funktioniert im Unterordner-Pfad.
- Daten liegen unter `dist/assets/`. Die hostbare `index.html` lädt sie per `fetch()`.

## Option B — Eigener Server / Pi5 / Cloudflare

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

### HTTPS (empfohlen)
- Cloudflare (Proxy) oder Let's Encrypt / certbot.

## Bedarf der hostbaren Version
- **Internet** für das Laden der **Leaflet- und MarkerCluster-Bibliotheken** (von CDN)
  sowie der **Kartenkacheln** (OpenStreetMap).
- Die **Daten** werden bei der hostbaren Version per `fetch()` aus `dist/assets/` geladen
  → braucht einen HTTP-Server (nicht `file://`).

---

## Hosting (EN)

The app is **hosting-ready** — live deployment happens later on request.

Two delivery forms:
- `dist/index.html` + `dist/assets/*.json` → hostable (loads data via fetch()).
- `dist/index_singlefile.html` → single file, data embedded (works from file://).

### Option A — GitHub Pages
Push `dist/` to a Pages-enabled branch. Paths are relative, so subpath URLs work.
Live URL: `https://<USER>.github.io/<REPO>/`.

### Option B — Own server / Pi5 / Cloudflare
Serve `dist/` statically:
```bash
cd ~/Projects/pv-wind-map/dist && python3 -m http.server 8080
```

### Runtime requirements
- Internet for Leaflet/MarkerCluster (CDN) and OpenStreetMap tiles.
- Hostable version needs an HTTP server to fetch() the data.
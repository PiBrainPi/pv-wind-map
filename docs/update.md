# Update — PV & Wind Karte (MaStR)

> Manuell auslösbar, cronjob-fähig. Stand: 2026-08-29.

## Update ausführen (DE)

Die komplette Pipeline ist nicht-interaktiv und kann als ein Befehl laufen:

```bash
cd ~/Projects/pv-wind-map
bash scripts/build.sh   # fetch → import → export → bundle (ein Schritt, erzeugt auch Single-File)
```

Der vollständige Weg in Einzelschritten (falls du Zwischenschritte prüfen willst):

```bash
cd ~/Projects/pv-wind-map

# 1. Daten aus dem MaStR neu laden (aktualisiert data/raw/*.json)
python3 scripts/fetch_mastr.py

# 2. In SQLite importieren (Normalisierung + ≥1-MW-Filter, überschreibt mastr.db)
python3 scripts/import_mastr.py

# 3. Für die Karte exportieren (nur Anlagen mit Geolokation → dist/assets/)
python3 scripts/export_app.py

# 4. Hostbare App auffrischen + eigenständige Einzel-Datei erzeugen
cp src/index.html dist/index.html
python3 scripts/bundle_singlefile.py
```

### Als Cronjob (automatisch)

Das Skript ist nicht-interaktiv, d. h. es kann direkt als Cronjob laufen.
**Wichtig (Pi5):** In einem Cron-Kontext kein `execute_code` nutzen — nur reine
Shell/Python. Beispiel-Crontab (monatlich, 3. Tag, 02:00):

```cron
0 2 3 * * cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map && \
  bash scripts/build.sh >> /tmp/pvwind_update.log 2>&1
```

Danach optional die neue `dist/index_singlefile.html` verteilen (z. B. in den
Austauschordner `~/hermes_human-share/`).

### Was bei einem Update passiert

- `fetch_mastr.py`: lädt Wind- und PV-Anlagen neu vom MaStR (Status „In Betrieb",
  ≥ 100 kW / ≥ 0,5 MWp).
- `import_mastr.py`: **leert** die Tabelle `einheiten` neu und baut sie wieder auf
  (einfach & robust für V0). Der `update_log` protokolliert Zählerstand.
- `export_app.py`: schreibt `dist/assets/einheiten.json` + `meta.json` + **`statistiken.json`** (Betreiber, Größenklassen).
- `bundle_singlefile.py`: erzeugt `dist/index_singlefile.html` (Daten + Statistik eingebettet).

> **Wichtig (Hosting):** Nach einem Daten-Update müssen geänderte `dist/assets/*.json` auch
> auf die **Live-Website** übertragen werden — der `gh-pages`-Branch des Repos enthält die
> deploybare Site. Ablauf: `dist/` neu bauen → `gh-pages`-Branch aus `dist/` aktualisieren →
> push → GitHub-Pages deployed automatisch. Details siehe `docs/DEPLOYMENT.md`.

### Verifikation nach Update

1. `python3 scripts/export_app.py` zeigt die Zähler (Wind/PV, Geolokation).
2. App öffnen und prüfen, dass „Stand:" im Footer neu ist.
3. Optional: ein paar bekannte Anlagen (MaStR-Nr.) in der Karte gegenprüfen.

---

## Update (EN)

The whole pipeline is non-interactive and can run as one command:

```bash
cd ~/Projects/pv-wind-map
bash scripts/build.sh   # fetch → import → export → bundle (single command, includes single-file)
```

Or step by step:

```bash
cd ~/Projects/pv-wind-map
python3 scripts/fetch_mastr.py
python3 scripts/import_mastr.py
python3 scripts/export_app.py
cp src/index.html dist/index.html
python3 scripts/bundle_singlefile.py
```

Or as a crontab job (monthly, 3rd, 02:00):

```cron
0 2 3 * * cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map && bash scripts/build.sh >> /tmp/pvwind_update.log 2>&1
```

Note (Pi5): in cron contexts do not use `execute_code`; use plain shell/Python.
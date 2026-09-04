# Update — PV & Wind Karte (MaStR)

> Manuell auslösbar, cronjob-fähig. Stand: 2026-09-03 (Pipeline 2.0 inkl. Netzanschlusspunkte).

## Update ausführen (DE)

Die komplette Pipeline ist nicht-interaktiv und kann als ein Befehl laufen:

```bash
cd ~/Projects/pv-wind-map
bash scripts/build.sh   # fetch → import → export → bundle (ein Schritt, erzeugt auch Single-File)
```

### Pipeline 2.0 — vollständige Datenhaltung (Regel 2 der Grundsatzentscheidung)

Seit 2026-09-03 werden zusätzlich zu den Kernfeldern **alle 118 API-Felder** und die
**Netzanschlusspunkte (NAP)** vorgehalten. Der Ein-Befehl für die Server-Datenbasis:

```bash
cd ~/Projects/pv-wind-map
python3 scripts/fetch_v2.py --extended-status   # 1. Alle 118 Felder → data/raw_v2/ + F5-Status 31/37/38 (separate Dateien; alte raw/ unangetastet)
python3 scripts/import_v2.py       # 2. Schema 2.0: einheiten_raw (UPSERT inkrementell) + Backup nach ~/backups/
python3 scripts/fetch_nap.py       # 3. NAP je Lokation (Cache: nur neue/geänderte, resumable)
python3 scripts/import_v2.py       # 4. NAP-JSONL in netzanschlusspunkte-Tabelle importieren
```

> **⚠️ F5-Pflicht-Flag `--extended-status` (seit 03.09., nicht optional):**
> Ohne das Flag werden die 6 Status-Dateien `{wind,pv}_status{31,37,38}.json`
> NICHT aktualisiert — `import_v2.py` liest sie aber trotzdem ein. Die Status-Filter-Daten
> der Karte (In Planung / stillgelegt) würden auf altem Stand einfrieren. Cron & alle
> manuellen Läufe MÜSSEN daher `pipeline2_update.sh` nutzen (das Flag enthält) oder
> fetch_v2 mit dem Flag aufrufen. Status-Wechsel einer Anlage (z. B. In Planung → In Betrieb)
> kommen zuverlässig an: Der UPSERT erkennt abweichende BetriebsStatusId, auch bei
> gleichem Aktualisierungsdatum.

**Kurzantwort zur Cron-Frage: Ja — alle drei Datenstränge (Wind, PV, NAP) werden von
einem einzigen Cronjob getriggert.** Der NAP-Schritt braucht keine eigene Behandlung im
Cron: `fetch_nap.py` nutzt den Cache (`nap_fetch_log`), d. h. der erste Lauf dauert ~3 h
(erledigt, 27.870 NAPs liegen vor), jeder folgende Lauf holt nur noch neue/veränderte
Lokationen (Minuten statt Stunden). Empfohlener Cronjob (Punkt 5, 10-Punkte-Plan):

```cron
0 3 1,15 * * cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map && \
  bash scripts/pipeline2_update.sh >> /tmp/pvwind_pipeline2.log 2>&1
```

> Der Cronjob führt `pipeline2_update.sh` aus — das Skript enthält das Pflicht-Flag
> `--extended-status` (F5) und den kompakten Telegram-Report inkl. Status-Zählern.

> Hinweis: `build.sh` (Karte) und Pipeline 2.0 (Server-Datenbasis) sind getrennt.
> Für einen kombinierten Lauf beides hintereinander ausführen. Daten-Updates ändern
> die Karte NICHT automatisch — der HTML-Export (Punkt 9) bleibt bis zur geplanten
> Kernfeld-Besprechung mit dem Nutzer unverändert.

Der vollständige Weg in Einzelschritten (falls du Zwischenschritte prüfen willst):

```bash
cd ~/Projects/pv-wind-map

# 1. Daten aus dem MaStR neu laden (aktualisiert data/raw/*.json)
python3 scripts/fetch_mastr.py

# 2. In SQLite importieren (Normalisierung + ≥100-kW-Wind / ≥0,5-MWp-PV-Filter, überschreibt mastr.db)
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
Shell/Python. Beispiel-Crontab (**1. & 15. des Monats, 03:00 Uhr**):

```cron
0 3 1,15 * * cd /home/claw_01_rasbpi5_1/Projects/pv-wind-map && \
  bash scripts/build.sh >> /tmp/pvwind_update.log 2>&1
```

Danach optional die neue `dist/index_singlefile.html` verteilen (z. B. in den
Austauschordner `~/hermes_human-share/`).

### Was bei einem Update passiert

- `fetch_mastr.py`: lädt Wind- und PV-Anlagen neu vom MaStR (Status „In Betrieb",
  ≥ 100 kW / ≥ 0,5 MWp).
- `import_mastr.py`: **leert** die Tabelle `einheiten` neu und baut sie wieder auf
  (einfach & robust für V0). Der `update_log` protokolliert Zählerstand.
  **V4 (Snapshot-System):** Vor dem Rebuild wird der alte Datenstand als Snapshot gesichert
  (`snapshot.py` → `snapshots` + `snapshot_einheiten` mit 26 Asset-Feldern). Nach dem Import
  wird der neue Stand als weiterer Snapshot gespeichert und das Delta berechnet
  (neue/entfernte Anlagen, Bundesländer-Veränderung).
- `export_app.py`: schreibt `dist/assets/einheiten.json` + `meta.json` + **`statistiken.json`**
  (Betreiber, Größenklassen) + **`historie.json`** (alle Snapshots + Deltas).
- `bundle_singlefile.py`: erzeugt `dist/index_singlefile.html` (Daten + Statistik + Historie eingebettet).
- `fetch_v2.py --extended-status` + `import_v2.py`: Pipeline 2.0 — alle 118 Felder 1:1 in `einheiten_raw`
  (UPSERT, inkrementell via `DatumLetzteAktualisierung` + BetriebsStatus-Wechsel-Erkennung),
  DB-Backup-Pflicht nach `~/backups/`. **F5:** Zusatz-Status 31/37/38 in separaten Dateien
  `{wind,pv}_status{31,37,38}.json` — Flag ist Pflicht (siehe Warnung oben), sonst frieren
  die Status-Filter der Karte ein.
- `fetch_nap.py`: **Netzanschlusspunkte** je Lokation → `data/nap/*.jsonl` + Cache
  `nap_fetch_log` (resumable, inkrementell). Abfrage je Lokation:
  `/MaStR/Einheit/Json/NetzanschlusspunkteKendoList/{lokationId}` (verifiziert 03.09.).
  `import_v2.py` (2. Aufruf) befüllt die Tabelle `netzanschlusspunkte` (27.870 NAPs, Stand 03.09.).


> **Wichtig (Hosting):** Nach einem Daten-Update müssen geänderte `dist/assets/*.json` auch
> auf die **Live-Website** übertragen werden — der `gh-pages`-Branch des Repos enthält die
> deploybare Site. Ablauf: `dist/` neu bauen → `gh-pages`-Branch aus `dist/` aktualisieren →
> push → GitHub-Pages deployed automatisch. Details siehe `docs/DEPLOYMENT.md`.
> Auch **Code-Änderungen an `src/index.html`** (z. B. neue Filter/UI) gehören mit `cp
> src/index.html dist/index.html` in den Deploy übernommen, bevor man `bundle_singlefile.py`
> und den `gh-pages`-Push ausführt.

> **Hinweis `data/` (Ist-Stand):** `data/raw/` und `data/mastr.db` sind **gitignored** und im
> Working-Tree aktuell (2026-09-01) **vorhanden** (Stand 01.09.2026, 53.500 georeferenzierte
> Anlagen). Sie werden vom `fetch_mastr.py` automatisch neu angelegt/überschrieben.
> Die zuletzt exportierten Karten-Daten liegen fertig in `dist/assets/*.json` bzw. in der
> Single-File; für eine reine UI-/Code-Revision (ohne Daten-Refresh) genügt Schritt 4
> (`cp` + bundle). Für den Revisions-Tracker (Update-Historie) muss mindestens `import_mastr.py`
> laufen, um den Snapshot zu sichern und das Delta zu berechnen.

### Verifikation nach Update

1. `python3 scripts/export_app.py` zeigt die Zähler (Wind/PV, Geolokation).
2. App öffnen und prüfen, dass „Stand:" oben rechts in der Suchleiste neu ist (auf den Tag gekürzt).
3. Optional: ein paar bekannte Anlagen (MaStR-Nr.) in der Karte gegenprüfen.

### ⚠️ Snapshot-Regel (unveränderlich)

Die in `data/mastr.db` gespeicherten Snapshots sind die historische Datenbasis des Projekts.

- **Snapshots dürfen niemals gelöscht, überschrieben oder verändert werden.**
- Jeder Snapshot ist ein unveränderlicher Punkt-in-Zeit-Datensatz.
- Neue Snapshots werden nur angefügt (`INSERT`, niemals `UPDATE`/`DELETE`).
- `data/mastr.db` wird nicht auf GitHub gepusht (gitignored).
- Die Historie wächst über Monate/Jahre und ist bei Verlust der DB unwiederherstellbar.

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
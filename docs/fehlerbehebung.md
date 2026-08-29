# Fehlerbehebung (Troubleshooting) — PV & Wind Karte

> Stand: 2026-08-29

## Bekannte Fehlerbilder & Lösungen

### 1. „Fehler beim Laden: Failed to fetch" (hostbare Version)
**Ursache:** Die hostbare `dist/index.html` lädt ihre Daten per `fetch()` aus
`assets/*.json`. Ab `file://` ist fetch() wegen CORS gesperrt.
**Lösung:** Die **Single-File** `dist/index_singlefile.html` verwenden (Daten eingebettet,
funktioniert ab `file://`), ODER die Dateien über einen HTTP-Server ausliefern:
```bash
cd ~/Projects/pv-wind-map/dist && python3 -m http.server 8080
# dann http://localhost:8080
```

### 2. Karte zeigt keine Rasterkacheln (grauer Hintergrund)
**Ursache:** OpenStreetMap-Kacheln können nicht geladen werden (offline / geblockt).
**Lösung:** Internetverbindung prüfen. Kacheln kommen von `{s}.tile.openstreetmap.org`.
Alternativer Hintergrundkarten-Dienst wäre konfigurierbar (z. B. Carto).

### 3. Markierungen/Cluster fehlen, obwohl App lädt
**Möglichkeit A — Filter aktiv:** Prüfe den Typ-Filter („Wind"/„PV") und den
Bundesland-Filter. Auf „Alle" zurücksetzen.
**Möglichkeit B — veraltete Daten:** Datenstand im Footer prüfen. Update laufen lassen
(siehe `docs/update.md`).
**Möglichkeit C — falsches Datenmodell nach manueller Änderung:** Erneut exportieren:
`python3 scripts/export_app.py` und `python3 scripts/bundle_singlefile.py`.

### 4. Zahlen im Footer stimmen nicht mit DB überein
**Ursache:** `dist/assets/` oder die Single-File sind älter als die DB.
**Lösung:** Export + Bundle neu erzeugen. Der `metadaten.stand`-Wert zeigt den letzten
Import.

### 5. `python3 scripts/import_mastr.py` meldet „UNIQUE constraint failed: metadaten.key"
**Ursache:** Alte Zeilen in `metadaten` beim Rebuild. Durch `INSERT OR REPLACE` behoben —
also einfach erneut ausführen. Falls persistent: `data/mastr.db` löschen und neu importieren.

### 6. Merkwürdige Leistungswerte (z. B. Anlage mit 15000 MW)
**Ursache:** MaStR-Einheiten-Konvention (kW vs. MW), siehe `docs/datenmodell.md`.
**Lösung:** Der Import normalisiert bereits korrekt (Wert > 80 → kW). Nach einem
vollständigen Re-Import (`fetch` → `import`) sind die Werte in MW konsistent.
Einzelwerte von 100/95 MW sind veraltete/korrekte große Offshore (V236-15MW) bzw.
kW-Kleinstanlagen.

### 7. API-Abfrage scheitert (fetch_mastr.py)
**Ursache:** MaStR kurzzeitig nicht erreichbar, Rate-Limit, o. ä.
**Lösung:** Skript hat eingebaute Retries (5 Versuche, exponentielle Wartezeit).
Erneut ausführen. Dauert das Problem an, ist das MaStR (marktstammdatenregister.de)
ggf. in Wartung — später erneut versuchen.

### 8. Dubletten oder fehlende Anlagen
**Hinweis:** Die DB nutzt `MaStRNummer` als UNIQUE-Schlüssel (`INSERT OR REPLACE`).
Ein Re-Import ist ein Voll-Rebuild (DELETE + INSERT). Dubletten durch den
Behörden-Datensatz selbst sind möglich (wenige) und werden 1:1 übernommen.

---

## Troubleshooting (EN)

1. **"Failed to fetch"** — hostable `index.html` loads data via fetch() → needs an HTTP
   server (not file://). Use the single-file version or run `python3 -m http.server 8080` in `dist/`.
2. **No tiles (grey map)** — OpenStreetMap unreachable; check internet.
3. **Missing markers** — check filters, data freshness (footer), re-export.
4. **Footer counts don't match DB** — re-run export + bundle.
5. **UNIQUE constraint metadaten.key** — re-run import (now uses INSERT OR REPLACE); else delete mastr.db and re-import.
6. **Odd capacity values** — kW vs MW unit convention (see datenmodell.md). Re-import normalizes.
7. **MaStR API failing** — built-in retries; retry later if MaStR is in maintenance.
8. **Duplicates/missing** — MaStRNummer is unique; full rebuild on re-import.
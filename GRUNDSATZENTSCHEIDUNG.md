# Grundsatzentscheidung — PV & Wind Karte (MaStR-Pipeline)

> Geltungsbereich: gesamtes Projekt `~/Projects/pv-wind-map/` (Datenpipeline, DB, Export, Deploy).
> Beschlossen: 2026-09-03 · Status: Regeln 1 + 2 final, Daten-Umfang von Nutzer final zu bestätigen.

## Regel 1 — Löschverbot (oberste Regel, unveränderlich)

**Es darf nichts aus diesem Projekt gelöscht werden, ohne explizite Zustimmung des Users.**

- Betroffen: Dateien, Ordner, Datenbanken, Snapshots, Iterationen, Raw-JSONs, Backups — alles.
- Das schließt ausdrücklich "Aufräum"-Aktionen bei Deploy, Build oder Skript-Läufen ein
  (Vorfälle vom 03.09. dokumentiert in `docs/PROJEKTSTAND.md`).
- Deploy-/Cleanup-Skripte dürfen **nur** Artefakte neu erzeugen (überschreiben), niemals
  bestehende Datenbestände entfernen. Ausnahme `rm` nur nach expliziter User-Freigabe.
- Vor jedem Deploy: Backup der DB nach `~/backups/` (Pflicht, kein Fallback).
- Snapshots in `data/mastr.db` (`snapshots`, `snapshot_einheiten`) sind bereits per
  PROJEKTSTAND.md geschützt — diese Regel gilt zusätzlich und allgemeiner für ALLES.

## Regel 2 — Vollständige Datenhaltung (100 %-Ziel)

**Alle im Marktstammdatenregister (MaStR) vorhandenen Daten zu Wind und PV werden auf den
Server (Pi5) geladen und dauerhaft vorgehalten** — auch Felder, die die Karte aktuell nicht
zeigt —, damit sie später für Auswertungen zur Verfügung stehen.

- **Grenzen (fix, laut Nutzer):** Wind ≥ 100 kW (Energieträger 2497), PV ≥ 0,5 MWp
  (Energieträger 2495). Keine Ausweitung auf kleinere Anlagen (Datenmengen-Vermeidung).
- **Netzanschlusspunkte (NAP):** werden **zukünftig mitgezogen**. Verifizierter Abrufweg
  (2026-09-03, live getestet): je Lokation
  `GET /MaStR/Einheit/Json/NetzanschlusspunkteKendoList/{lokationId}?lokationId={lokationId}`
  → liefert u. a. NAP-MaStR-Nr (SAN…), Messlokation, Spannungsebene, Regelzone,
  Bilanzierungsgebiet, Netzbetreiber, Nettoengpassleistung, Anschlusspunktkapazität.
- **Feldabdeckung:** die Einheiten-Datensätze haben **118 Felder**; Ziel ist 100 % Erfassung
  der Rohdatensätze 1:1 (Raw-JSON in der DB), plus normalisierte Kernfelder für die App.
- Der finale Feldkatalog wird vom Nutzer nach Sichtung der Feldübersicht bestätigt
  (Übersicht siehe unten / Chat vom 03.09.). Diese Bestätigung ergänzt hier.

## Regel 3 — HTML-Iterationen (Schutz)

**Keine alte bzw. iterierte HTML-Version darf gelöscht werden** — weder in `iterations/`
noch in `~/hermes_human-share/` oder sonstwo im Projekt. Gilt auch für fehlerhafte oder
verworfene Versionen (deckungsgleich mit PROJEKTSTAND.md § Iterationen).

## Regel 4 — GitHub (Freigabe-Pflicht)

**Ohne explizite Zustimmung des Users darf im Projekt NICHTS auf GitHub passieren:**
- kein `git push` (weder `main` noch `gh-pages` noch andere Branches)
- keine Repo-Settings-Änderungen (Pages, Visibility, Branch-Protection, Webhooks, …)
- keine Issues/PRs/Releases erstellen oder verändern
- Workflow: Agent fragt → User muss **explizit „Ja"** sagen → erst dann ausführen.
  Fragen sind ausdrücklich erlaubt und erwünscht; stillschweigendes Handeln nie.

## Datenübersicht (118 Einheiten-Felder, gruppiert — Stand: Live-Check 03.09.)

Bereits importiert (31): siehe `scripts/import_mastr.py` (`INSERT_COLS`).
Neu hinzu kommen (87), gruppiert:

- **Förderung/EEG:** EegAnlageMastrNummer, EegAnlageRegistrierungsdatum, EegAnlagenschluessel,
  EegInstallierteLeistung, EegZuschlag, Zuschlagsnummern, KwkAnlageMastrNummer,
  KwkAnlageRegistrierungsdatum, KwkAnlageInbetriebnahmedatum, KwkAnlageElektrischeLeistung,
  KwkZuschlag, HatFlexibilitaetspraemie, VollTeilEinspeisung(+Bezeichnung),
  MieterstromAngemeldet, IsBuergerenergie
- **Leistung/Technik:** Nettonennleistung, ThermischeNutzleistung, NutzbareSpeicherkapazitaet,
  TechnologieStromerzeugung(+Id), Typ, HauptbrennstoffId+Namen, BiomasseArt(+Bezeichnung),
  Batterietechnologie, Stromspeichertechnologie(+Bezeichnung), IsEinheitNotstromaggregat,
  Leistungsbegrenzung, WasserkraftErtuechtigung, KraftwerkName, KraftwerkBlockName
- **Wind-spezifisch:** WindClusterNordseeId, WindClusterOstseeId, Pilotwindanlage, Prototypanlage
- **PV-spezifisch:** HauptneigungswinkelSolarmodule(+Bezeichnung), NutzungsbereichGebSA(+Bezeichnung),
  InAnspruchgenommeneFlaeche, VorherigeNutzungsartDerFlaecheBezeichnung,
  VorherigerNutzungsartenBereichDerFlaecheBezeichnung
- **Genehmigung:** AktenzeichenGenehmigung, Genehmigungbehoerde, GenehmigungsMastrNummer,
  GenehmigungRegistrierungsdatum, GeplantesInbetriebsnahmeDatum
- **Zeit/Status-Detail:** EndgueltigeStilllegungDatum, InbetriebnahmeDatumAmAktuellenOrt,
  IsAnonymisiert, IsNBPruefungAbgeschlossen, MigrationseinheitMastrNummer,
  SpeicherEinheitMastrNummer, Gruppierungsobjekte(+Ids)
- **Adresse/Flur (Erweiterung):** Hausnummer, Gemarkung, Flurstueck, Gemeindeschluessel,
  BundeslandId, LandId, StandortAnonymisiert, SpannungsebenenId
- **IDs (technisch):** Id, AnlagenbetreiberId, AnlagenbetreiberMaStRNummer,
  AnlagenbetreiberMaskedName, AnlagenbetreiberPersonenArt, NetzbetreiberId,
  NetzbetreiberMaStRNummer, NetzbetreiberMaskedNamen, NetzbetreiberPersonenArt,
  BetriebsStatusId, SystemStatusId

Hinweise: Masked*-Felder sind datenschutz-relevant (NUR Server, nie Export). `Regelzone` ist an
der Einheit meist None (liegt am NAP). NAP-Felder kommen zusätzlich pro Lokation dazu.

## Umsetzung (Pipeline-Überarbeitung)

10-Punkte-Plan, Freigabe durch User 2026-09-03:

1. **Feldkatalog (FREIGEGEBEN):** alle 118 Einheiten-Felder + NAP-Felder → Server (Pi5).
   HTML-Export bekommt später NUR das Nötigste (Auswahl bei zukünftiger Version).
2. **NAP-Erreichbarkeit (FREIGEGEBEN):** live testen, "wir schauen einfach, wie es läuft".
3. **DB-Schema 2.0 (FREIGEGEBEN):** `einheiten_raw` (118 Felder 1:1) + `netzanschlusspunkte`
   + bestehende Tabellen (`einheiten`, Snapshots) unangetastet.
4. **Inkrementelle Update-Strategie (FREIGEGEBEN):** nur geänderte Einheiten via
   `DatumLetzteAktualisierung`, NAP nur für neue/veränderte Lokationen.
5. **Cron-Design (FREIGEGEBEN, nach QA):** monatlicher Update-Cron + Telegram-Watchdog.
6. **fetch_v2.py (FREIGEGEBEN):** komplette Records speichern, kein Feld-Wegwurf.
7. **import_v2.py (FREIGEGEBEN):** Schema 2.0, Snapshot-Logik nur anfügen, DB-Backup nach
   `~/backups/` vor jedem Lauf (Pflicht).
8. **fetch_nap.py (FREIGEGEBEN):** NAP pro Lokation + Cache gegen Re-Läufe.
9. **export_app.py (FREIGEGEBEN, vorläufig unverändert):** Karte bleibt wie sie ist
   (19 Kernfelder). **VERMERK: In späteren Versionen müssen die Kernfelder für den
   HTML-Export explizit mit dem Nutzer besprochen werden** (nur das Nötigste exportieren,
   Entscheidung steht noch aus).
10. **QA-Protokoll (FREIGEGEBEN):** Feldabgleich 118/118 + NAP-Count vs. Web, Stichproben
    (DB vs. Web-UI), Historie-Intaktheit, danach Cron + 2 beobachtete Testläufe.

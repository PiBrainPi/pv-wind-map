"""V32 (WP3): Snapshot-7/8-Migration — Wind-MW-Korrektur via to_mw-Heuristik.

Bug 08.09.: Snapshots 7 (2026-08-29) + 8 (2026-09-01) enthalten die VOR dem
V27b-Physik-Check importierten Wind-Leistungen (120 Einträge mit kW-Falschangabe,
z. B. E-18/20 = 80 kW als "80 MW"). Das Delta 01.09→06.09 und damit die
Historie-Anzeige (Entfernt-Liste, Δ MW, Bundesländer-Δ) rechnete mit falschen Werten.

Fix: bruttoleistung_mw aller Wind-Einträge (energietraeger_id=2497) in
snapshot_einheiten der Snapshots 7+8 mit der to_mw-Heuristik (import_mastr)
neu berechnen; snapshots.wind_mw/gesamt_mw + bundeslaender_json neu ableiten.
"""
import sqlite3, json, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_mastr import to_mw

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mastr.db')
WIND_ET = 2497


def migrate(dry_run=True):
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    total_fixed = 0
    total_delta_mw = 0.0

    for sid in (7, 8):
        rows = db.execute(
            "SELECT mastr_nummer, bruttoleistung_mw, typenbezeichnung, rotordurchmesser_m, nabenhoehe_m "
            "FROM snapshot_einheiten WHERE snapshot_id=? AND energietraeger_id=?", (sid, WIND_ET)
        ).fetchall()
        fixes = []
        for r in rows:
            old_mw = r['bruttoleistung_mw']
            # to_mw erwartet ein Dict mit Bruttoleistung/Typenbezeichnung/Rotordurchmesser/Nabenhöhe
            fake = {
                'Bruttoleistung': old_mw,       # bereits MW-normiert aus Alt-Import — Heuristik erneut anwenden
                'Typenbezeichnung': r['typenbezeichnung'],
                'Rotordurchmesser': r['rotordurchmesser_m'],
                'Nabenhöhe': r['nabenhoehe_m'],
            }
            # ACHTUNG: to_mw rechnet PV /1000 — hier nur Wind (et 2497), also kW/MW-Heuristik.
            new_mw = to_mw(fake, WIND_ET)
            if new_mw is None:
                new_mw = old_mw
            if abs((new_mw or 0) - (old_mw or 0)) > 0.005:
                fixes.append((r['mastr_nummer'], old_mw, new_mw))

        print(f"Snapshot {sid}: {len(rows)} Wind-Einträge, {len(fixes)} Korrekturen, "
              f"Δ-MW = {sum(n - o for _, o, n in fixes):.1f}")

        if dry_run:
            for m, o, nw in fixes[:10]:
                print(f"  {m}: {o} → {nw} MW")
            continue

        for m, o, nw in fixes:
            db.execute("UPDATE snapshot_einheiten SET bruttoleistung_mw=? WHERE snapshot_id=? AND mastr_nummer=?",
                       (nw, sid, m))
        total_fixed += len(fixes)
        total_delta_mw += sum(n - o for _, o, n in fixes)

        # Snapshots-Kennzahlen neu ableiten
        wind_anzahl, wind_mw = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM snapshot_einheiten "
            "WHERE snapshot_id=? AND energietraeger_id=?", (sid, WIND_ET)).fetchone()
        gesamt_anzahl, gesamt_mw = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM snapshot_einheiten WHERE snapshot_id=?",
            (sid,)).fetchone()
        pv_anzahl, pv_mw = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) FROM snapshot_einheiten "
            "WHERE snapshot_id=? AND energietraeger_id=?", (sid, 2495)).fetchone()

        # bundeslaender_json neu
        bl_rows = db.execute(
            "SELECT bundesland, energietraeger_id, COUNT(*), COALESCE(SUM(bruttoleistung_mw),0) "
            "FROM snapshot_einheiten WHERE snapshot_id=? GROUP BY bundesland, energietraeger_id", (sid,)).fetchall()
        bl = {}
        for r in bl_rows:
            name = r[0] or 'Unbekannt'
            d = bl.setdefault(name, {'wind': 0, 'pv': 0, 'wind_mw': 0.0, 'pv_mw': 0.0})
            if r[1] == WIND_ET:
                d['wind'] = r[2]; d['wind_mw'] = round(r[3], 2)
            else:
                d['pv'] = r[2]; d['pv_mw'] = round(r[3], 2)
        db.execute(
            "UPDATE snapshots SET wind_anzahl=?, wind_mw=?, pv_anzahl=?, pv_mw=?, "
            "gesamt_anzahl=?, gesamt_mw=?, bundeslaender_json=? WHERE id=?",
            (wind_anzahl, round(wind_mw, 2), pv_anzahl, round(pv_mw, 2),
             gesamt_anzahl, round(gesamt_mw, 2), json.dumps(bl, ensure_ascii=False), sid))
        print(f"Snapshot {sid} aktualisiert: Wind {wind_anzahl} / {wind_mw:.1f} MW")

    if not dry_run:
        db.commit()
        print(f"\nGESAMT: {total_fixed} Einträge korrigiert, Δ {total_delta_mw:.1f} MW")
    db.close()


if __name__ == '__main__':
    dry = '--apply' not in sys.argv
    migrate(dry_run=dry)

#!/usr/bin/env python3
"""Punkt 19: MaStR-Betreiberdaten — Analyse natürlicher Personen."""
import json, re, sys
from pathlib import Path

data = json.load(open('/home/claw_01_rasbpi5_1/Projects/pv-wind-map/dist/assets/einheiten.json', encoding='utf-8'))
print('Gesamt-Einheiten:', len(data))

betreiber = {}
for e in data:
    ab = e.get('ab', '')
    if ab:
        betreiber[ab] = betreiber.get(ab, 0) + 1

print('Anzahl eindeutige Betreiber:', len(betreiber))

# Rechtsform-/Firmen-Endungen -> eher juristische Personen
rechtsform = re.compile(r'(GmbH|m\.b\.H|Haftungsgesellschaft|KG|AG|SE|e\.G|UG|GbR|OHG|Gbr|LLC|Inc|Ltd|L\.P|Co\.|Corp|Foundation|GmbH & Co|PartG|e\.K|E\.K|Company|& Co\. KG|S\.A\.|Sarl|B\.V\.)', re.I)
jur = {k: v for k, v in betreiber.items() if rechtsform.search(k)}
nat = {k: v for k, v in betreiber.items() if not rechtsform.search(k)}

print('Mit Rechtsform-Hinweis (jur. Pers.):', len(jur), 'Anlagen:', sum(jur.values()))
print('Ohne Rechtsform-Hinweis (pot. nat. Pers.):', len(nat), 'Anlagen:', sum(nat.values()))
print('Anteil ohne Rechtsform an Gesamt-Anlagen: {:.1f}%'.format(100 * sum(nat.values()) / len(data)))

# Heuristik: ohne Rechtsform UND kein Firmen-/Stadtwerk-Hinweis -> Einzelperson
firmenwort = re.compile(r'(Energie|Solar|Wind|Park|Betrieb|GmbH|GmbH|Gmbh|Spv|Kraftwerk|Anlagen|Projekt|entwick|Investment|Verwaltung|Gewerbe|GbR|OHG|Landwirt|Freif|Pflege|Herr|Frau|Privat|Familie|Konzern|Group|Holding|Gmbh)', re.I)
stark_nat = {k: v for k, v in nat.items() if not firmenwort.search(k)}
print('STARK pot. natürliche Personen (kein Firmen/Energie-Wort):', len(stark_nat), 'Anlagen:', sum(stark_nat.values()))
print()
print('--- Beispiele pot. natürlicher Personen (Name-Muster, Vorname+Nachname):')
print('A) "ohne Rechtsform, ohne Firmenwort" – Stichprobe:')
for k in list(stark_nat.keys())[:20]:
    print('  *', repr(k), '->', stark_nat[k])
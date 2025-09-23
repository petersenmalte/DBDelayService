#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_xml(filename):
    # alles bis zum ersten <timetable> abschneiden
    with open(filename, 'rb') as f:
        raw = f.read().decode('utf-8', errors='ignore')
    idx = raw.find('<timetable')
    xml = raw[idx:]
    return ET.fromstring(xml)

def parse_timestamp(ts):
    # ts im Format YYMMDDHHMM → datetime (Jahr 20YY)
    return datetime.strptime(ts, "%y%m%d%H%M")

root = parse_xml('timetable.xml')

delays = []
for s in root.findall('s'):
    # nehme dp (departure) oder ar (arrival), je nachdem, was vorhanden ist
    ev = s.find('dp') or s.find('ar')
    if ev is None or 'pt' not in ev.attrib or 'ct' not in ev.attrib:
        continue

    pt = parse_timestamp(ev.get('pt'))
    ct = parse_timestamp(ev.get('ct'))
    delay = int((ct - pt).total_seconds() // 60)
    if delay < 60:
        continue

    # Gleis
    platform = ev.get('l') or ev.get('pp') or '–'

    # Metadaten aus <tl>
    tl = s.find('tl')
    category  = tl.get('c')
    number    = tl.get('n')
    direction = tl.get('f')    # z.B. 'F' oder 'N'
    origin    = tl.get('o')    # EVA-Code des Ursprungsbahnhofs

    # Streckenverlauf
    route_elem = s.find('ar') or s.find('dp')
    if route_elem is not None and 'cpth' in route_elem.attrib:
        stops = route_elem.get('cpth').split('|')
        start = stops[0] if stops else '–'
        end   = stops[-1] if stops else '–'
        route = ' → '.join(stops)
    else:
        start = end = route = '–'

    delays.append({
        'Kategorie':   category,
        'Nummer':      number,
        'Geplant':     pt.strftime("%d.%m.%Y %H:%M"),
        'Aktuell':     ct.strftime("%d.%m.%Y %H:%M"),
        'Verspätung':  f"{delay} min",
        'Gleis':       platform,
        'Richtung':    direction,
        'Ursprung EVA':origin,
        'Startbahnhof':start,
        'Zielbahnhof': end,
        'Route':       route,
    })

# Ausgabe als Tabelle
from tabulate import tabulate
print(tabulate(delays,
               headers="keys",
               tablefmt="github",
               colalign=("center",)*len(delays[0])))

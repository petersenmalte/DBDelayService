import requests
from datetime import datetime, timedelta

# 1) Deinen API-Key hier einfügen
API_KEY = "4c6cd2e5a2affda817b8e13123067f65"

# 2) Endpunkt für Abfahrten an einem Bahnhof (z.B. Berlin Hbf)
STATION = "8002549"  # DB-MIDX für Berlin Hbf
from datetime import datetime
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
URL = f"https://apis.deutschebahn.com/freeplan/v1/departureBoard/{STATION}?date={now}"
resp = requests.get(
    URL,
    headers={
        "Accept": "application/json",
        "DB-Client-Id": "4c6cd2e5a2affda817b8e13123067f65",
        "DB-Api-Key":    "370854dd922d0dc161285a05ccc67b0e"
    }
)
resp.raise_for_status()
data = resp.json()

# 4) Aktuelle Zeit
now = datetime.utcnow()

# 5) Filter: Verspätung ≥ 60 Minuten
late_trains = []
for ev in data:
    # 'delay' ist in Minuten
    delay = ev.get("delay") or 0
    if delay >= 60:
        late_trains.append({
            "train":      ev.get("name"),
            "direction":  ev.get("direction"),
            "scheduled":  ev.get("scheduledTime"),
            "expected":   ev.get("plannedTime"),
            "delay_min":  delay
        })

# 6) Ausgabe
print(f"Züge mit ≥ 60 Min Verspätung in {STATION}:")
for t in late_trains:
    sched = datetime.fromisoformat(t["scheduled"].replace("Z","+00:00"))
    exp   = datetime.fromisoformat(t["expected"].replace("Z","+00:00"))
    print(f"- {t['train']} nach {t['direction']}: "
          f"plan {sched.time()} → {exp.time()} (+{t['delay_min']} min)")
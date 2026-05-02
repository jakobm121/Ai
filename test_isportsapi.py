import os
import requests
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

API_KEY = os.getenv("ISPORTS_API_KEY")
URL = "http://api.isportsapi.com/sport/football/livescores"

res = requests.get(URL, params={"api_key": API_KEY}, timeout=25)
data = res.json().get("data", [])

statuses = Counter()
leagues = Counter()

for m in data:
    statuses[m.get("status")] += 1
    leagues[m.get("leagueName")] += 1

print("TOTAL MATCHES:", len(data))
print("STATUS COUNTS:", statuses.most_common())
print("TOP LEAGUES:", leagues.most_common(20))

print("\nSAMPLE TIMES:")
for m in data[:10]:
    ts = m.get("matchTime")
    dt = datetime.fromtimestamp(ts, ZoneInfo("Europe/Ljubljana")) if ts else None
    print(m.get("leagueName"), m.get("homeName"), "-", m.get("awayName"), "status=", m.get("status"), "time=", dt)

import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

API_KEY = os.getenv("ISPORTS_API_KEY")
BASE = "http://api.isportsapi.com"

def call(path, params):
    params = params.copy()
    params["api_key"] = API_KEY
    r = requests.get(BASE + path, params=params, timeout=25)
    print("\nPATH:", path)
    print("PARAMS:", {k:v for k,v in params.items() if k != "api_key"})
    print("STATUS:", r.status_code)
    print("PREVIEW:", r.text[:1200])
    try:
        data = r.json()
        print("KEYS:", list(data.keys()) if isinstance(data, dict) else type(data).__name__)
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            print("DATA LEN:", len(data["data"]))
            if data["data"] and isinstance(data["data"][0], dict):
                print("FIRST KEYS:", list(data["data"][0].keys()))
        elif isinstance(data, dict) and isinstance(data.get("data"), dict):
            print("DATA KEYS:", list(data["data"].keys()))
    except Exception:
        pass

def main():
    if not API_KEY:
        raise RuntimeError("Missing ISPORTS_API_KEY")

    today = datetime.now(ZoneInfo("Europe/Ljubljana")).strftime("%Y-%m-%d")

    tests = [
        ("/sport/football/schedule", {"date": today}),
        ("/sport/football/schedule", {"leagueID": "11157"}),
        ("/sport/football/league/basic", {}),
        ("/sport/football/team", {"leagueId": "11157"}),
    ]

    for path, params in tests:
        call(path, params)

if __name__ == "__main__":
    main()

import os
import requests
import json

API_KEY = os.getenv("ISPORTS_API_KEY")
BASE = "http://api.isportsapi.com"

def get(path, params=None):
    params = params or {}
    params["api_key"] = API_KEY
    r = requests.get(BASE + path, params=params, timeout=25)
    print("STATUS", path, r.status_code)
    data = r.json()
    return data

def main():
    odds = get("/sport/football/odds/main")
    data = odds.get("data", {})

    print("\nTOP LEVEL KEYS:", list(data.keys()))

    for key in ["europeOdds", "overUnder", "handicap", "overUnderHalf", "handicapHalf"]:
        rows = data.get(key, [])
        print("\n" + "=" * 80)
        print(key, "count:", len(rows))
        print("=" * 80)

        for row in rows[:10]:
            print(row)
            parts = str(row).split(",")
            print("parts len:", len(parts))
            for i, p in enumerate(parts):
                print(i, "=", p)
            print("-" * 40)

if __name__ == "__main__":
    main()

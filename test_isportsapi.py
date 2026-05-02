import os
import requests
import json

API_KEY = os.getenv("ISPORTS_API_KEY")

BASE_URLS = [
    "http://api.isportsapi.com",
    "http://api2.isportsapi.com",
]

PATHS = [
    "/sport/football/odds",
    "/sport/football/odds/main",
    "/sport/football/odds/list",
    "/sport/football/match/odds",
    "/sport/football/bookmaker",
    "/sport/football/schedule",
    "/sport/football/fixtures",
    "/sport/football/matches",
    "/sport/football/standings",
    "/sport/football/team",
]

def main():
    if not API_KEY:
        raise RuntimeError("Missing ISPORTS_API_KEY")

    for base in BASE_URLS:
        print("\n" + "=" * 80)
        print("BASE:", base)
        print("=" * 80)

        for path in PATHS:
            url = base + path
            try:
                res = requests.get(url, params={"api_key": API_KEY}, timeout=15)
                print("\nPATH:", path)
                print("STATUS:", res.status_code)
                print("PREVIEW:", res.text[:300])

                try:
                    data = res.json()
                    if isinstance(data, dict):
                        print("KEYS:", list(data.keys()))
                        if "data" in data:
                            if isinstance(data["data"], list):
                                print("DATA LIST LEN:", len(data["data"]))
                                if data["data"] and isinstance(data["data"][0], dict):
                                    print("FIRST KEYS:", list(data["data"][0].keys()))
                            elif isinstance(data["data"], dict):
                                print("DATA DICT KEYS:", list(data["data"].keys()))
                    elif isinstance(data, list):
                        print("LIST LEN:", len(data))
                except Exception:
                    pass

            except Exception as e:
                print("ERROR:", path, e)

if __name__ == "__main__":
    main()

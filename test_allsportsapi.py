import json
import requests

RAPIDAPI_KEY = "PASTE_YOUR_RAPIDAPI_KEY_HERE"

HOST = "free-api-live-football-data.p.rapidapi.com"
URL = "https://free-api-live-football-data.p.rapidapi.com/football-players-search"

def main():
    if RAPIDAPI_KEY == "7b08a67045mshf14f43b059212bfp17e1eajsnb9a13dec679a'":
        raise RuntimeError("Vstavi RapidAPI key v RAPIDAPI_KEY.")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    params = {
        "search": "m"
    }

    print("=" * 60)
    print("TESTING FREE LIVE FOOTBALL DATA")
    print("=" * 60)

    res = requests.get(URL, headers=headers, params=params, timeout=20)

    print("STATUS:", res.status_code)
    print("CONTENT-TYPE:", res.headers.get("content-type"))
    print("RATE LIMIT:", res.headers.get("x-ratelimit-requests-limit"))
    print("RATE REMAINING:", res.headers.get("x-ratelimit-requests-remaining"))

    print("\nRAW PREVIEW:")
    print(res.text[:1000])

    try:
        data = res.json()
    except Exception:
        print("Response is not JSON.")
        raise

    print("\nJSON PREVIEW:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:8000])

    print("\nSTRUCTURE:")
    if isinstance(data, dict):
        print("Top-level keys:", list(data.keys()))
        for key, value in data.items():
            if isinstance(value, list):
                print(f"{key}: list, {len(value)} items")
                if value and isinstance(value[0], dict):
                    print("First item keys:", list(value[0].keys()))
            elif isinstance(value, dict):
                print(f"{key}: dict keys:", list(value.keys()))
            else:
                print(f"{key}: {type(value).__name__} = {value}")
    elif isinstance(data, list):
        print("Top-level list:", len(data))
        if data and isinstance(data[0], dict):
            print("First item keys:", list(data[0].keys()))

    if res.status_code != 200:
        raise RuntimeError(f"API test failed with status {res.status_code}")

if __name__ == "__main__":
    main()

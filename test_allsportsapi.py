import json
import requests

# TEMP TEST ONLY:
# Tukaj začasno prilepi svoj RapidAPI key.
# Če bo API uporaben, ga kasneje premakneš v GitHub Secret.
RAPIDAPI_KEY = "PASTE_YOUR_RAPIDAPI_KEY_HERE"

HOST = "allsportsapi2.p.rapidapi.com"
URL = "https://allsportsapi2.p.rapidapi.com/api/tournament/17/season/76986/statistics/info"


def main():
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "7b08a67045mshf14f43b059212bfp17e1eajsnb9a13dec679a'":
        raise RuntimeError("Vstavi RapidAPI key v RAPIDAPI_KEY.")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    print("=" * 60)
    print("TESTING ALLSPORTSAPI2")
    print("=" * 60)
    print("URL:", URL)

    try:
        res = requests.get(URL, headers=headers, timeout=20)
    except Exception as e:
        print("REQUEST ERROR:", e)
        raise

    print("\n" + "=" * 60)
    print("RESPONSE INFO")
    print("=" * 60)
    print("STATUS:", res.status_code)
    print("CONTENT-TYPE:", res.headers.get("content-type"))
    print("RATE LIMIT:", res.headers.get("x-ratelimit-requests-limit"))
    print("RATE REMAINING:", res.headers.get("x-ratelimit-requests-remaining"))
    print("RATE RESET:", res.headers.get("x-ratelimit-requests-reset"))

    print("\n" + "=" * 60)
    print("RAW PREVIEW")
    print("=" * 60)
    print(res.text[:1000])

    print("\n" + "=" * 60)
    print("JSON PREVIEW")
    print("=" * 60)

    try:
        data = res.json()
    except Exception:
        print("Response is not JSON.")
        raise RuntimeError("AllSportsAPI2 response is not JSON.")

    print(json.dumps(data, indent=2, ensure_ascii=False)[:8000])

    print("\n" + "=" * 60)
    print("BASIC STRUCTURE CHECK")
    print("=" * 60)

    if isinstance(data, dict):
        print("Top-level type: dict")
        print("Top-level keys:", list(data.keys()))

        for key, value in data.items():
            if isinstance(value, list):
                print(f"- {key}: list with {len(value)} items")
                if value:
                    print(f"  first item type: {type(value[0]).__name__}")
                    if isinstance(value[0], dict):
                        print(f"  first item keys: {list(value[0].keys())}")
            elif isinstance(value, dict):
                print(f"- {key}: dict with keys {list(value.keys())}")
            else:
                print(f"- {key}: {type(value).__name__} = {value}")

    elif isinstance(data, list):
        print("Top-level type: list")
        print("Items:", len(data))
        if data:
            print("First item type:", type(data[0]).__name__)
            if isinstance(data[0], dict):
                print("First item keys:", list(data[0].keys()))
    else:
        print("Top-level type:", type(data).__name__)

    if res.status_code != 200:
        raise RuntimeError(f"AllSportsAPI2 test failed with status {res.status_code}")

    print("\nTEST DONE: API returned status 200.")


if __name__ == "__main__":
    main()

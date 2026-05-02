import os
import json
import requests

ISPORTS_API_KEY = os.getenv("ISPORTS_API_KEY")

BASE_URLS = [
    "http://api.isportsapi.com",
    "http://api2.isportsapi.com",
]

ENDPOINT = "/sport/football/livescores"


def print_structure(data, prefix=""):
    if isinstance(data, dict):
        print(f"{prefix}dict keys: {list(data.keys())}")

        for key, value in list(data.items())[:10]:
            if isinstance(value, list):
                print(f"{prefix}- {key}: list len={len(value)}")
                if value:
                    print(f"{prefix}  first item type: {type(value[0]).__name__}")
                    if isinstance(value[0], dict):
                        print(f"{prefix}  first item keys: {list(value[0].keys())}")
            elif isinstance(value, dict):
                print(f"{prefix}- {key}: dict keys={list(value.keys())}")
            else:
                print(f"{prefix}- {key}: {type(value).__name__} = {value}")

    elif isinstance(data, list):
        print(f"{prefix}list len={len(data)}")
        if data:
            print(f"{prefix}first item type: {type(data[0]).__name__}")
            if isinstance(data[0], dict):
                print(f"{prefix}first item keys: {list(data[0].keys())}")
    else:
        print(f"{prefix}{type(data).__name__}: {data}")


def test_url(base_url):
    url = f"{base_url}{ENDPOINT}"

    params = {
        "api_key": ISPORTS_API_KEY,
    }

    print("\n" + "=" * 70)
    print("TEST URL")
    print("=" * 70)
    print(url)

    res = requests.get(url, params=params, timeout=25)

    print("\nSTATUS:", res.status_code)
    print("CONTENT-TYPE:", res.headers.get("content-type"))
    print("RAW PREVIEW:")
    print(res.text[:1500])

    try:
        data = res.json()
    except Exception:
        print("NON-JSON RESPONSE")
        return False

    print("\nJSON PREVIEW:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:6000])

    print("\nSTRUCTURE:")
    print_structure(data)

    return res.status_code == 200


def main():
    if not ISPORTS_API_KEY:
        raise RuntimeError("Missing ISPORTS_API_KEY environment variable.")

    print("Starting iSportsAPI football test...")

    success = False

    for base_url in BASE_URLS:
        try:
            ok = test_url(base_url)
            if ok:
                success = True
                break
        except Exception as e:
            print(f"ERROR testing {base_url}: {e}")

    if not success:
        raise RuntimeError("iSportsAPI test failed on both base URLs.")

    print("\nTEST DONE: iSportsAPI returned status 200.")


if __name__ == "__main__":
    main()

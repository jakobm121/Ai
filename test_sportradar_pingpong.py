import os
import sys
import json
import requests

API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()

TEST_URLS = [
    "https://api.sportradar.com/tabletennis/trial/v2/en/schedules/live/timelines_delta.json",
    "https://api.sportradar.com/tabletennis/production/v2/en/schedules/live/timelines_delta.json",
]

TIMEOUT = 25


def print_block(title, value):
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    print(value)


def try_request(url: str, api_key: str) -> bool:
    headers = {
        "accept": "application/json",
        "x-api-key": api_key,
    }

    print_block("TEST URL", url)

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except Exception as exc:
        print_block("REQUEST ERROR", str(exc))
        return False

    print_block("STATUS CODE", response.status_code)
    print_block("CONTENT-TYPE", response.headers.get("content-type", "unknown"))

    text_preview = response.text[:2000] if response.text else ""
    print_block("RESPONSE PREVIEW", text_preview or "[empty response]")

    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict):
                print_block("JSON KEYS", list(data.keys()))
            elif isinstance(data, list):
                print_block("JSON TYPE", f"list ({len(data)} items)")
            else:
                print_block("JSON TYPE", type(data).__name__)
        except Exception:
            print_block("JSON PARSE", "Response was not valid JSON")
        return True

    return False


def main():
    if not API_KEY:
        print("ERROR: Missing SPORTRADAR_API_KEY environment variable.")
        sys.exit(1)

    print("Starting Sportradar Table Tennis API test...")

    success = False
    for url in TEST_URLS:
        ok = try_request(url, API_KEY)
        if ok:
            success = True

    print("\n" + "=" * 60)
    if success:
        print("RESULT: SUCCESS - Your key appears to work for Sportradar Table Tennis.")
        sys.exit(0)
    else:
        print("RESULT: FAILED - No successful Table Tennis response.")
        print("Most likely reasons:")
        print("- Table Tennis API is not enabled on your key/application")
        print("- trial/production access level does not match your account")
        print("- endpoint access is restricted")
        sys.exit(1)


if __name__ == "__main__":
    main()

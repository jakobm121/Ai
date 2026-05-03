import os
import json
import time
from datetime import datetime, timezone

import requests


PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")

BASE_URL = "https://api.pandascore.co"
OUTPUT_FILE = "pandascore_test_output.json"

REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_CALLS = 1.2

# Lahko kasneje spremeniš na lol, dota2, valorant ...
TEST_SPORTS = [
    "csgo",
    "lol",
    "dota2",
    "valorant",
]

ENDPOINTS_TO_TEST = [
    "/status",
    "/matches/upcoming",
    "/matches/running",
    "/matches/past",
    "/tournaments/upcoming",
    "/leagues",
    "/teams",
    "/players",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def mask_key(value):
    if not value:
        return "MISSING"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {
            "_raw_text": response.text[:2000],
        }


def make_headers():
    if not PANDASCORE_API_KEY:
        raise RuntimeError("Missing PANDASCORE_API_KEY environment variable.")

    return {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}",
        "Accept": "application/json",
    }


def api_get(path, params=None):
    url = BASE_URL + path

    print("=" * 100)
    print(f"GET {url}")
    print(f"PARAMS: {params or {}}")

    try:
        response = requests.get(
            url,
            headers=make_headers(),
            params=params or {},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as e:
        print(f"REQUEST ERROR: {e}")
        return {
            "path": path,
            "params": params or {},
            "ok": False,
            "request_error": str(e),
        }

    data = safe_json(response)

    print(f"STATUS: {response.status_code}")
    print(f"HEADERS RATE LIMIT:")
    print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
    print(f"  X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}")
    print(f"  X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset')}")

    preview = json.dumps(data, ensure_ascii=False)[:1800]
    print(f"PREVIEW: {preview}")

    inspect_payload(data)

    return {
        "path": path,
        "params": params or {},
        "status_code": response.status_code,
        "ok": response.ok,
        "headers": {
            "x_ratelimit_limit": response.headers.get("X-RateLimit-Limit"),
            "x_ratelimit_remaining": response.headers.get("X-RateLimit-Remaining"),
            "x_ratelimit_reset": response.headers.get("X-RateLimit-Reset"),
        },
        "data": data,
    }


def inspect_payload(data):
    print("-" * 100)
    print("INSPECT")

    if isinstance(data, list):
        print(f"TYPE: list")
        print(f"LEN: {len(data)}")

        if data:
            first = data[0]
            if isinstance(first, dict):
                print(f"FIRST KEYS: {list(first.keys())}")

                interesting = {
                    "id": first.get("id"),
                    "name": first.get("name"),
                    "slug": first.get("slug"),
                    "status": first.get("status"),
                    "begin_at": first.get("begin_at"),
                    "end_at": first.get("end_at"),
                    "scheduled_at": first.get("scheduled_at"),
                    "winner_id": first.get("winner_id"),
                    "videogame": first.get("videogame"),
                    "league": first.get("league"),
                    "serie": first.get("serie"),
                    "tournament": first.get("tournament"),
                    "opponents": first.get("opponents"),
                    "results": first.get("results"),
                    "games": first.get("games"),
                }

                compact = {
                    k: v for k, v in interesting.items()
                    if v is not None
                }

                print("FIRST COMPACT:")
                print(json.dumps(compact, indent=2, ensure_ascii=False)[:2500])
            else:
                print(f"FIRST ITEM: {first}")

        return

    if isinstance(data, dict):
        print("TYPE: dict")
        print(f"KEYS: {list(data.keys())}")

        if "error" in data:
            print(f"ERROR: {data.get('error')}")
        if "errors" in data:
            print(f"ERRORS: {data.get('errors')}")
        if "message" in data:
            print(f"MESSAGE: {data.get('message')}")

        print("DICT PREVIEW:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2500])
        return

    print(f"TYPE: {type(data).__name__}")
    print(str(data)[:1000])


def save_output(results):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")


def test_global_endpoints(results):
    print("\n")
    print("#" * 100)
    print("GLOBAL ENDPOINT TEST")
    print("#" * 100)

    for path in ENDPOINTS_TO_TEST:
        result = api_get(path, {"per_page": 5})
        results["global"].append(result)
        time.sleep(SLEEP_BETWEEN_CALLS)


def test_sport_endpoints(results):
    print("\n")
    print("#" * 100)
    print("SPORT-SPECIFIC ENDPOINT TEST")
    print("#" * 100)

    for sport in TEST_SPORTS:
        print("\n")
        print("=" * 100)
        print(f"SPORT: {sport}")
        print("=" * 100)

        sport_results = []

        paths = [
            f"/{sport}/matches/upcoming",
            f"/{sport}/matches/running",
            f"/{sport}/matches/past",
            f"/{sport}/tournaments/upcoming",
            f"/{sport}/leagues",
            f"/{sport}/teams",
        ]

        for path in paths:
            result = api_get(path, {"per_page": 5})
            sport_results.append(result)
            time.sleep(SLEEP_BETWEEN_CALLS)

        results["sports"][sport] = sport_results


def find_best_match_samples(results):
    print("\n")
    print("#" * 100)
    print("MATCH SAMPLE SUMMARY")
    print("#" * 100)

    samples = []

    def scan_payload(source_name, payload):
        data = payload.get("data")

        if not isinstance(data, list):
            return

        for item in data[:5]:
            if not isinstance(item, dict):
                continue

            if "opponents" not in item:
                continue

            opponents = item.get("opponents") or []

            teams = []
            for opp in opponents:
                opponent = opp.get("opponent") if isinstance(opp, dict) else None
                if isinstance(opponent, dict):
                    teams.append({
                        "id": opponent.get("id"),
                        "name": opponent.get("name"),
                        "slug": opponent.get("slug"),
                    })

            samples.append({
                "source": source_name,
                "match_id": item.get("id"),
                "name": item.get("name"),
                "status": item.get("status"),
                "begin_at": item.get("begin_at"),
                "scheduled_at": item.get("scheduled_at"),
                "winner_id": item.get("winner_id"),
                "videogame": item.get("videogame", {}).get("name") if isinstance(item.get("videogame"), dict) else item.get("videogame"),
                "league": item.get("league", {}).get("name") if isinstance(item.get("league"), dict) else item.get("league"),
                "serie": item.get("serie", {}).get("full_name") if isinstance(item.get("serie"), dict) else item.get("serie"),
                "tournament": item.get("tournament", {}).get("name") if isinstance(item.get("tournament"), dict) else item.get("tournament"),
                "teams": teams,
                "results": item.get("results"),
                "games_count": len(item.get("games") or []),
            })

    for payload in results.get("global", []):
        scan_payload(payload.get("path", "global"), payload)

    for sport, payloads in results.get("sports", {}).items():
        for payload in payloads:
            scan_payload(f"{sport}:{payload.get('path')}", payload)

    results["samples"] = samples[:30]

    print(f"SAMPLES FOUND: {len(samples)}")
    for sample in samples[:10]:
        print("-" * 100)
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:2500])


def main():
    print("PandaScore API Test")
    print(f"GENERATED_AT: {now_iso()}")
    print(f"PANDASCORE_API_KEY: {mask_key(PANDASCORE_API_KEY)}")
    print(f"BASE_URL: {BASE_URL}")
    print(f"OUTPUT_FILE: {OUTPUT_FILE}")

    if not PANDASCORE_API_KEY:
        raise RuntimeError("Missing PANDASCORE_API_KEY environment variable.")

    results = {
        "generated_at": now_iso(),
        "base_url": BASE_URL,
        "api_key_present": bool(PANDASCORE_API_KEY),
        "global": [],
        "sports": {},
        "samples": [],
    }

    test_global_endpoints(results)
    test_sport_endpoints(results)
    find_best_match_samples(results)

    save_output(results)

    print("\n")
    print("=" * 100)
    print("DONE")
    print(f"Saved: {OUTPUT_FILE}")
    print("=" * 100)


if __name__ == "__main__":
    main()

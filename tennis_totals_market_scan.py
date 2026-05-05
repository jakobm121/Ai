import os
import json
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
OUT_FILE = f"{DATA_DIR}/tennis_totals_market_scan.json"

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35

DAYS_AHEAD = 2
MAX_MATCHES_TO_SCAN = 80


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_json(path, data):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def api_call(params, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing API_KEY environment variable.")

    params = params.copy()
    params["APIkey"] = API_KEY

    for attempt in range(retries):
        res = requests.get(
            BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if res.status_code in {429, 500, 502, 503, 504}:
            wait = 3 * (attempt + 1)
            print(f"API retry {res.status_code}, sleeping {wait}s")
            time.sleep(wait)
            continue

        if res.status_code >= 400:
            raise RuntimeError(f"HTTP {res.status_code}: {res.text[:400]}")

        return res.json()

    raise RuntimeError("API failed after retries")


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def fetch_fixtures_for_date(date_value):
    date_s = date_value.strftime("%Y-%m-%d")

    data = api_call({
        "method": "get_fixtures",
        "date_start": date_s,
        "date_stop": date_s,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        print(f"Fixtures error {date_s}: {data}")
        return []

    result = data.get("result") or []
    return result if isinstance(result, list) else []


def fetch_odds(event_key):
    data = api_call({
        "method": "get_odds",
        "event_key": event_key,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return {}

    result = data.get("result") or {}
    return result.get(str(event_key)) or result.get(int(event_key)) or {}


def is_pregame(match):
    status = str(match.get("event_status") or "").lower()
    live = str(match.get("event_live") or "0")

    if live == "1":
        return False

    if status in {"finished", "cancelled", "postponed", "retired", "walkover"}:
        return False

    return True


def looks_like_total_market(market_name):
    n = str(market_name or "").lower()

    keywords = [
        "over/under",
        "over under",
        "total",
        "games",
        "match games",
    ]

    return any(k in n for k in keywords)


def summarize_market(market_data):
    """
    Return compact preview, because full odds blob can be huge.
    """
    if not isinstance(market_data, dict):
        return market_data

    preview = {}
    count = 0

    for outcome, books in market_data.items():
        if count >= 12:
            preview["..."] = "truncated"
            break

        if isinstance(books, dict):
            preview[outcome] = {
                "bookmakers": len(books),
                "sample": dict(list(books.items())[:5]),
            }
        else:
            preview[outcome] = books

        count += 1

    return preview


def main():
    start = today_local()

    fixtures = []

    for i in range(DAYS_AHEAD):
        date_value = start + timedelta(days=i)
        daily = fetch_fixtures_for_date(date_value)
        print(f"FIXTURES {date_value}: {len(daily)}")
        fixtures.extend(daily)

    fixtures = [m for m in fixtures if is_pregame(m)]

    print(f"PREGAME FIXTURES: {len(fixtures)}")

    scanned = 0
    with_odds = 0
    market_counter = Counter()
    total_market_counter = Counter()
    examples = []
    all_market_names_by_match = []

    for match in fixtures:
        if scanned >= MAX_MATCHES_TO_SCAN:
            break

        event_key = match.get("event_key")

        if not event_key:
            continue

        scanned += 1

        name = f"{match.get('event_first_player')} - {match.get('event_second_player')}"
        tournament = match.get("tournament_name") or ""
        event_type = match.get("event_type_type") or ""

        print(f"SCAN {scanned}/{MAX_MATCHES_TO_SCAN}: {name} | {event_key}")

        try:
            odds_blob = fetch_odds(event_key)

            if not odds_blob:
                all_market_names_by_match.append({
                    "event_key": event_key,
                    "match": name,
                    "has_odds": False,
                    "markets": [],
                })
                continue

            with_odds += 1

            market_names = list(odds_blob.keys())

            for market_name in market_names:
                market_counter[market_name] += 1

                if looks_like_total_market(market_name):
                    total_market_counter[market_name] += 1

            total_markets = {
                market_name: summarize_market(odds_blob.get(market_name))
                for market_name in market_names
                if looks_like_total_market(market_name)
            }

            all_market_names_by_match.append({
                "event_key": event_key,
                "match": name,
                "tournament": tournament,
                "event_type": event_type,
                "has_odds": True,
                "markets": market_names,
                "total_like_markets": list(total_markets.keys()),
            })

            if total_markets and len(examples) < 12:
                examples.append({
                    "event_key": event_key,
                    "match": name,
                    "tournament": tournament,
                    "event_type": event_type,
                    "total_like_markets": total_markets,
                })

        except Exception as e:
            print(f"ERROR {event_key}: {e}")
            all_market_names_by_match.append({
                "event_key": event_key,
                "match": name,
                "error": str(e),
            })

    payload = {
        "generated_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),
        "days_ahead": DAYS_AHEAD,
        "max_matches_to_scan": MAX_MATCHES_TO_SCAN,
        "fixtures_total": len(fixtures),
        "scanned": scanned,
        "with_odds": with_odds,
        "market_names_top": market_counter.most_common(80),
        "total_like_market_names": total_market_counter.most_common(80),
        "examples": examples,
        "matches": all_market_names_by_match,
    }

    save_json(OUT_FILE, payload)

    print("")
    print("TENNIS TOTALS MARKET SCAN DONE")
    print(f"Scanned: {scanned}")
    print(f"With odds: {with_odds}")
    print(f"Total-like markets found: {len(total_market_counter)}")
    print(f"Saved: {OUT_FILE}")

    print("")
    print("TOP TOTAL-LIKE MARKETS:")
    for name, count in total_market_counter.most_common(30):
        print(f"{count}x | {name}")


if __name__ == "__main__":
    main()

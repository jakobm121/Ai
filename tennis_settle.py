import os
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_results.json")
SETTLE_DEBUG_FILE = os.path.join(DATA_DIR, "tennis_settle_debug.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


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


def fetch_fixture(event_key):
    data = api_call({
        "method": "get_fixtures",
        "event_key": event_key,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return None

    result = data.get("result")

    if isinstance(result, list) and result:
        return result[0]

    if isinstance(result, dict):
        return result

    return None


def final_score(match):
    scores = match.get("scores") or []

    if not scores:
        return match.get("event_final_result") or ""

    parts = []

    for s in scores:
        a = s.get("score_first")
        b = s.get("score_second")

        if a is not None and b is not None:
            parts.append(f"{a}-{b}")

    return ", ".join(parts) if parts else (match.get("event_final_result") or "")


def settle_pick(pick, match):
    status = str(match.get("event_status") or "").lower()

    if status != "finished":
        return False

    winner = match.get("event_winner")

    if winner not in {"First Player", "Second Player"}:
        return False

    pick_side = pick.get("market_side")

    if pick_side == "Home":
        pick_winner_label = "First Player"
    elif pick_side == "Away":
        pick_winner_label = "Second Player"
    else:
        return False

    won = winner == pick_winner_label

    stake = float(pick.get("stake") or 1)
    odds = float(pick.get("odds") or 0)

    if won:
        profit = stake * (odds - 1)
        result = "win"
    else:
        profit = -stake
        result = "loss"

    pick["result"] = result
    pick["profit"] = round(profit, 4)
    pick["settled_at"] = datetime.now(ZoneInfo(TZ_NAME)).isoformat()
    pick["settled_status"] = match.get("event_status")
    pick["event_winner"] = winner
    pick["final_score"] = final_score(match)

    return True


def main():
    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    pending = [
        p for p in results
        if isinstance(p, dict)
        and str(p.get("result") or "pending").lower() == "pending"
    ]

    print(f"PENDING PICKS: {len(pending)}")

    updated = 0
    still_pending = 0
    not_found = 0
    errors = []

    for pick in pending:
        event_key = pick.get("event_key") or pick.get("fixture_id")
        match_name = pick.get("match", "Unknown match")

        if not event_key:
            print(f"MISSING EVENT KEY - KEEP PENDING: {match_name}")
            still_pending += 1
            continue

        try:
            match = fetch_fixture(event_key)

            if not match:
                print(f"NO MATCH FOUND - KEEP PENDING: {match_name} | event_key={event_key}")
                not_found += 1
                still_pending += 1
                continue

            status = match.get("event_status")
            score = match.get("event_final_result") or final_score(match)

            print(f"CHECK {match_name} | status={status} | score={score or '-'}")

            changed = settle_pick(pick, match)

            if changed:
                updated += 1
                print(f"SETTLED {match_name}: {pick['result']} | profit={pick.get('profit')} | {pick.get('final_score')}")
            else:
                still_pending += 1

        except Exception as e:
            print(f"SETTLE ERROR - KEEP PENDING: {match_name} | {e}")
            errors.append({
                "event_key": event_key,
                "match": match_name,
                "error": str(e),
            })
            still_pending += 1

    save_json(RESULTS_FILE, results)

    debug_payload = {
        "generated_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),
        "pending_checked": len(pending),
        "updated": updated,
        "still_pending": still_pending,
        "not_found": not_found,
        "errors": errors,
    }

    save_json(SETTLE_DEBUG_FILE, debug_payload)

    print(
        f"TENNIS SETTLE DONE: updated={updated} "
        f"still_pending={still_pending} "
        f"not_found={not_found} "
        f"errors={len(errors)}"
    )


if __name__ == "__main__":
    main()

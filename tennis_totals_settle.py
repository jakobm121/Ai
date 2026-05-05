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
RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results.json"
DEBUG_FILE = f"{DATA_DIR}/tennis_totals_settle_debug.json"

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.30


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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


def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def api_call(params, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing API_KEY environment variable.")

    params = params.copy()
    params["APIkey"] = API_KEY

    for attempt in range(retries):
        res = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)

        if res.status_code in {429, 500, 502, 503, 504}:
            wait = 3 * (attempt + 1)
            print(f"API retry {res.status_code}, sleeping {wait}s")
            time.sleep(wait)
            continue

        if res.status_code >= 400:
            raise RuntimeError(f"HTTP {res.status_code}: {res.text[:400]}")

        return res.json()

    raise RuntimeError("API failed after retries")


def fetch_fixture_by_event_key(event_key):
    data = api_call({
        "method": "get_fixtures",
        "event_key": event_key,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return None

    result = data.get("result") or []

    if isinstance(result, list) and result:
        return result[0]

    if isinstance(result, dict):
        return result

    return None


def parse_scores(scores):
    parsed = []

    if not isinstance(scores, list):
        return parsed

    for s in scores:
        try:
            a = int(str(s.get("score_first")).strip())
            b = int(str(s.get("score_second")).strip())
            parsed.append((a, b))
        except Exception:
            continue

    return parsed


def total_games(scores):
    return sum(a + b for a, b in parse_scores(scores))


def final_score_string(scores):
    parsed = parse_scores(scores)
    return ", ".join(f"{a}-{b}" for a, b in parsed)


def is_bad_terminal_status(status):
    s = str(status or "").lower().strip()
    bad = {
        "cancelled",
        "canceled",
        "postponed",
        "retired",
        "walkover",
        "abandoned",
        "interrupted",
        "suspended",
    }
    return s in bad


def settle_pick(pick, fixture):
    status_raw = fixture.get("event_status")
    status = str(status_raw or "").lower().strip()

    if is_bad_terminal_status(status):
        return False, "bad_terminal_status"

    if status != "finished":
        return False, "not_finished"

    scores = fixture.get("scores") or []
    parsed = parse_scores(scores)

    if not parsed:
        return False, "no_scores"

    total = total_games(scores)
    line = safe_float(pick.get("line"))
    side = str(pick.get("side") or "").lower()

    if side not in {"over", "under"}:
        return False, "bad_side"

    stake = safe_float(pick.get("stake"))
    odds = safe_float(pick.get("odds"))

    if total == line:
        result = "push"
        profit = 0.0
    elif side == "over":
        win = total > line
        result = "win" if win else "loss"
        profit = stake * (odds - 1) if win else -stake
    else:
        win = total < line
        result = "win" if win else "loss"
        profit = stake * (odds - 1) if win else -stake

    pick["result"] = result
    pick["profit"] = round(profit, 3)
    pick["settled_at"] = now_iso()
    pick["settled_status"] = status_raw
    pick["event_winner"] = fixture.get("event_winner")
    pick["final_score"] = final_score_string(scores)
    pick["total_games"] = total

    return True, "settled"


def main():
    ensure_dirs()

    results = load_json(RESULTS_FILE, [])
    if not isinstance(results, list):
        results = []

    pending = [
        x for x in results
        if isinstance(x, dict) and str(x.get("result") or "pending").lower() == "pending"
    ]

    debug = {
        "generated_at": now_iso(),
        "pending_before": len(pending),
        "updated": 0,
        "still_pending": 0,
        "not_found": 0,
        "errors": [],
        "items": [],
    }

    print(f"PENDING TOTALS PICKS: {len(pending)}")

    for pick in pending:
        event_key = pick.get("event_key")
        match_name = pick.get("match")

        if not event_key:
            debug["errors"].append({"pick_id": pick.get("pick_id"), "error": "missing_event_key"})
            continue

        try:
            fixture = fetch_fixture_by_event_key(event_key)

            if not fixture:
                debug["not_found"] += 1
                debug["items"].append({
                    "event_key": event_key,
                    "match": match_name,
                    "status": "not_found",
                })
                print(f"NO MATCH FOUND: {match_name} | event_key={event_key}")
                continue

            changed, reason = settle_pick(pick, fixture)

            if changed:
                debug["updated"] += 1
                print(
                    f"SETTLED: {match_name} | {pick.get('bet')} | "
                    f"{pick.get('result')} | total={pick.get('total_games')} | profit={pick.get('profit')}"
                )
            else:
                debug["still_pending"] += 1
                print(f"PENDING: {match_name} | reason={reason} | status={fixture.get('event_status')}")

            debug["items"].append({
                "event_key": event_key,
                "pick_id": pick.get("pick_id"),
                "match": match_name,
                "bet": pick.get("bet"),
                "side": pick.get("side"),
                "line": pick.get("line"),
                "status": reason,
                "api_status": fixture.get("event_status"),
                "result": pick.get("result"),
                "total_games": pick.get("total_games"),
                "final_score": pick.get("final_score"),
                "profit": pick.get("profit"),
            })

        except Exception as e:
            debug["errors"].append({
                "event_key": event_key,
                "match": match_name,
                "error": str(e),
            })
            print(f"ERROR {event_key} {match_name}: {e}")

    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)

    print("")
    print(
        f"TENNIS TOTALS SETTLE DONE: "
        f"updated={debug['updated']} still_pending={debug['still_pending']} "
        f"not_found={debug['not_found']} errors={len(debug['errors'])}"
    )


if __name__ == "__main__":
    main()

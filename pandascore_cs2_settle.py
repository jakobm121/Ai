import os
import json
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
BASE_URL = "https://api.pandascore.co"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "cs2_results.json")
SETTLE_SNAPSHOT_FILE = os.path.join(DATA_DIR, "cs2_settle_snapshot.json")
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.8
DEBUG = True

PAST_PAGES = 5
PAST_PER_PAGE = 100
RUNNING_PER_PAGE = 100

FINAL_STATUSES = {"finished", "canceled"}
VOID_STATUSES = {"canceled", "postponed"}


def debug(msg):
    if DEBUG:
        print(msg)


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


def headers():
    if not PANDASCORE_API_KEY:
        raise RuntimeError("Missing PANDASCORE_API_KEY environment variable.")
    return {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}",
        "Accept": "application/json",
    }


def api_get(path, params=None, retries=3):
    url = BASE_URL + path
    params = params.copy() if params else {}
    for attempt in range(retries):
        res = requests.get(url, headers=headers(), params=params, timeout=REQUEST_TIMEOUT)
        if res.status_code in {429, 500, 502, 503, 504}:
            wait = (attempt + 1) * 3
            debug(f"API RETRY {res.status_code} {path} sleep={wait}s")
            time.sleep(wait)
            continue
        if res.status_code >= 400:
            raise RuntimeError(f"HTTP {res.status_code} {path}: {res.text[:500]}")
        return res.json()
    raise RuntimeError(f"API failed after retries: {path} {params}")


def get_results_map(match):
    out = {}
    for item in match.get("results") or []:
        team_id = item.get("team_id")
        if team_id is not None:
            try:
                out[int(team_id)] = int(item.get("score") or 0)
            except Exception:
                out[int(team_id)] = 0
    return out


def fetch_running_and_past():
    matches = []
    running = api_get("/csgo/matches/running", {"per_page": RUNNING_PER_PAGE})
    if isinstance(running, list):
        matches.extend(running)
    time.sleep(API_SLEEP_SECONDS)

    for page in range(1, PAST_PAGES + 1):
        past = api_get("/csgo/matches/past", {"per_page": PAST_PER_PAGE, "page": page, "sort": "-begin_at"})
        if not isinstance(past, list) or not past:
            break
        matches.extend(past)
        time.sleep(API_SLEEP_SECONDS)

    save_json(SETTLE_SNAPSHOT_FILE, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches,
    })
    return matches


def settle_item(item, match):
    status = str(match.get("status") or "").lower()
    winner_id = match.get("winner_id")
    pick_team_id = item.get("pick_team_id")

    debug(f"CHECK {item.get('match')} | {item.get('bet')} | status={status} winner_id={winner_id}")

    if status in VOID_STATUSES:
        return "storno"
    if status != "finished":
        return "pending"
    if winner_id is None or pick_team_id is None:
        return "pending"

    try:
        return "win" if int(winner_id) == int(pick_team_id) else "loss"
    except Exception:
        return "pending"


def main():
    ensure_dirs()
    history = load_json(RESULTS_FILE, [])
    if not isinstance(history, list):
        history = []

    pending = [x for x in history if isinstance(x, dict) and x.get("result") == "pending"]
    debug(f"PENDING PICKS: {len(pending)}")
    if not pending:
        save_json(RESULTS_FILE, history)
        print("CS2 SETTLE DONE: no pending picks.")
        return

    matches = fetch_running_and_past()
    by_id = {str(m.get("id")): m for m in matches if isinstance(m, dict) and m.get("id") is not None}

    updated = 0
    still_pending = 0
    not_found = 0
    tz = ZoneInfo(TZ_NAME)

    for item in history:
        if not isinstance(item, dict) or item.get("result") != "pending":
            continue
        match_id = str(item.get("match_id") or item.get("fixture_id") or "")
        match = by_id.get(match_id)
        if not match:
            not_found += 1
            debug(f"NO MATCH FOUND: {item.get('match')} | match_id={match_id}")
            continue

        new_result = settle_item(item, match)
        if new_result == "pending":
            still_pending += 1
            continue

        results_map = get_results_map(match)
        pick_team_id = item.get("pick_team_id")
        opponent_team_id = item.get("opponent_team_id")
        final_score = ""
        try:
            final_score = f"{results_map.get(int(pick_team_id), 0)}:{results_map.get(int(opponent_team_id), 0)}"
        except Exception:
            final_score = json.dumps(results_map, ensure_ascii=False)

        item["result"] = new_result
        item["settled_at"] = datetime.now(tz).isoformat()
        item["settled_status"] = match.get("status")
        item["winner_id"] = match.get("winner_id")
        item["final_score"] = final_score
        updated += 1
        debug(f"SETTLED {item.get('match')} | {item.get('bet')} | {final_score} -> {new_result}")

    save_json(RESULTS_FILE, history)
    print(f"CS2 SETTLE DONE: updated={updated} still_pending={still_pending} not_found={not_found}")


if __name__ == "__main__":
    main()

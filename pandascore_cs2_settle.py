import os
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
BASE_URL = "https://api.pandascore.co"

TZ_NAME = "Europe/Ljubljana"

RESULTS_FILE = "data/cs2_results.json"
PREDICTIONS_FILE = "data/cs2_predictions.json"

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.4


def headers():
    if not PANDASCORE_API_KEY:
        raise RuntimeError("Missing PANDASCORE_API_KEY environment variable.")

    return {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}",
        "Accept": "application/json",
    }


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def api_get(path, params=None):
    url = BASE_URL + path

    res = requests.get(
        url,
        headers=headers(),
        params=params or {},
        timeout=REQUEST_TIMEOUT,
    )

    if res.status_code == 404:
        return None

    if res.status_code == 429:
        print("RATE LIMIT sleep 5s")
        time.sleep(5)
        res = requests.get(
            url,
            headers=headers(),
            params=params or {},
            timeout=REQUEST_TIMEOUT,
        )

    if res.status_code >= 400:
        print(f"API ERROR {res.status_code} {path}: {res.text[:300]}")
        return None

    return res.json()


def get_match_by_id(match_id):
    match_id = str(match_id)

    endpoints = [
        f"/matches/{match_id}",
        f"/csgo/matches/{match_id}",
    ]

    for endpoint in endpoints:
        data = api_get(endpoint)
        time.sleep(API_SLEEP_SECONDS)

        if isinstance(data, dict) and str(data.get("id")) == match_id:
            return data

    return None


def get_results_map(match):
    out = {}

    for item in match.get("results") or []:
        team_id = item.get("team_id")
        score = item.get("score")

        if team_id is not None:
            try:
                out[int(team_id)] = int(score or 0)
            except Exception:
                out[int(team_id)] = 0

    return out


def final_score_for_pick(match):
    results = get_results_map(match)

    if not results:
        return ""

    scores = list(results.values())

    if len(scores) >= 2:
        return f"{scores[0]}:{scores[1]}"

    return ""


def settle_pick(pick, match):
    status = str(match.get("status") or "").lower()
    winner_id = match.get("winner_id")

    if status != "finished":
        return False

    if winner_id is None:
        return False

    pick_team_id = pick.get("pick_team_id")

    if pick_team_id is None:
        return False

    try:
        pick_team_id = int(pick_team_id)
        winner_id = int(winner_id)
    except Exception:
        return False

    pick["result"] = "win" if pick_team_id == winner_id else "loss"
    pick["settled_at"] = datetime.now(ZoneInfo(TZ_NAME)).isoformat()
    pick["settled_status"] = status
    pick["winner_id"] = winner_id
    pick["final_score"] = final_score_for_pick(match)

    return True


def main():
    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    pending = [
        p for p in results
        if isinstance(p, dict) and str(p.get("result") or "pending").lower() == "pending"
    ]

    print(f"PENDING PICKS: {len(pending)}")

    updated = 0
    still_pending = 0
    not_found = 0

    for pick in pending:
        match_id = pick.get("match_id") or pick.get("fixture_id")
        match_name = pick.get("match", "Unknown match")

        if not match_id:
            print(f"MISSING MATCH ID: {match_name}")
            still_pending += 1
            continue

        match = get_match_by_id(match_id)

        if not match:
            print(f"NO MATCH FOUND - KEEP PENDING: {match_name} | match_id={match_id}")
            not_found += 1
            still_pending += 1
            continue

        status = str(match.get("status") or "").lower()
        score = final_score_for_pick(match)

        print(f"CHECK {match_name} | status={status} | score={score or '-'}")

        changed = settle_pick(pick, match)

        if changed:
            updated += 1
            print(f"SETTLED {match_name}: {pick['result']} | {pick.get('final_score', '-')}")
        else:
            still_pending += 1

    save_json(RESULTS_FILE, results)

    print(
        f"CS2 SETTLE DONE: updated={updated} "
        f"still_pending={still_pending} "
        f"not_found={not_found}"
    )


if __name__ == "__main__":
    main()

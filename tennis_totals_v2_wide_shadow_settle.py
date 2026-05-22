import os
import json
import time
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

PREDICTIONS_FILE = Path("data/tennis_totals_v2_wide_shadow_predictions.json")
RESULTS_FILE = Path("data/tennis_totals_v2_wide_shadow_results.json")
DEBUG_FILE = Path("data/tennis_totals_v2_wide_shadow_settle_debug.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35
MAX_API_ERRORS = 15


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def safe_int(v, default=0):
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default


def api_call(params, retries=4):
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


def normalize_fixture_result(result, event_key):
    if isinstance(result, list):
        for item in result:
            if str(item.get("event_key")) == str(event_key):
                return item
        return result[0] if result else None

    if isinstance(result, dict):
        if str(result.get("event_key")) == str(event_key):
            return result

        by_str = result.get(str(event_key))
        if isinstance(by_str, dict):
            return by_str

        by_int = result.get(safe_int(event_key))
        if isinstance(by_int, dict):
            return by_int

        for item in result.values():
            if isinstance(item, dict) and str(item.get("event_key")) == str(event_key):
                return item

    return None


def fetch_fixture_by_event_key(event_key):
    data = api_call({
        "method": "get_fixtures",
        "event_key": event_key,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return None

    return normalize_fixture_result(data.get("result"), event_key)


def fetch_fixture_by_date(event_key, date_s):
    if not date_s:
        return None

    data = api_call({
        "method": "get_fixtures",
        "date_start": date_s,
        "date_stop": date_s,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return None

    return normalize_fixture_result(data.get("result"), event_key)


def fetch_fixture(pick):
    event_key = pick.get("event_key") or pick.get("fixture_id")
    if not event_key:
        return None

    fixture = fetch_fixture_by_event_key(event_key)
    if fixture:
        return fixture

    return fetch_fixture_by_date(event_key, pick.get("date"))


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


def total_games_from_fixture(fixture):
    scores = parse_scores(fixture.get("scores"))
    return sum(a + b for a, b in scores), scores


def final_score_string(scores):
    if not scores:
        return ""
    return " ".join(f"{a}-{b}" for a, b in scores)


def settle_pick(pick, fixture):
    status = str(fixture.get("event_status") or "").strip().lower()

    if status in {"cancelled", "postponed", "walkover", "retired", "interrupted", "abandoned"}:
        pick["result"] = "void"
        pick["settled_at"] = now_iso()
        pick["settle_status"] = status
        pick["total_games"] = None
        pick["final_score"] = str(fixture.get("event_final_result") or "")
        pick["profit"] = 0.0
        pick["return_units"] = 0.0
        return pick

    if status != "finished":
        return pick

    total_games, scores = total_games_from_fixture(fixture)

    if not scores or total_games <= 0:
        pick["settle_note"] = "finished_but_no_valid_scores"
        return pick

    side = str(pick.get("side") or "").lower()
    line = safe_float(pick.get("line"))
    odds = safe_float(pick.get("odds"))
    stake = safe_float(pick.get("stake"), 1.0)

    if side not in {"over", "under"} or line <= 0 or odds <= 1:
        pick["settle_note"] = "invalid_pick_data"
        return pick

    if side == "over":
        if total_games > line:
            result = "won"
        elif total_games < line:
            result = "lost"
        else:
            result = "push"
    else:
        if total_games < line:
            result = "won"
        elif total_games > line:
            result = "lost"
        else:
            result = "push"

    if result == "won":
        profit = stake * (odds - 1)
        return_units = stake * odds
    elif result == "lost":
        profit = -stake
        return_units = 0.0
    else:
        profit = 0.0
        return_units = stake

    pick["result"] = result
    pick["settled_at"] = now_iso()
    pick["settle_status"] = status
    pick["total_games"] = total_games
    pick["final_score"] = final_score_string(scores)
    pick["profit"] = round(profit, 4)
    pick["return_units"] = round(return_units, 4)

    return pick


def merge_predictions_into_results(results, prediction_payload):
    existing_by_id = {
        x.get("pick_id"): x
        for x in results
        if isinstance(x, dict) and x.get("pick_id")
    }

    picks = prediction_payload.get("picks", []) if isinstance(prediction_payload, dict) else []

    for pick in picks:
        if not isinstance(pick, dict) or not pick.get("pick_id"):
            continue

        old = existing_by_id.get(pick["pick_id"])

        if old:
            # Če je že settled, ne povozi rezultata z novim pending pickom.
            if str(old.get("result") or "pending").lower() != "pending":
                continue

            merged = old.copy()
            merged.update(pick)
            existing_by_id[pick["pick_id"]] = merged
        else:
            existing_by_id[pick["pick_id"]] = pick

    return list(existing_by_id.values())


def update_prediction_payload(prediction_payload, settled_by_id):
    if not isinstance(prediction_payload, dict):
        return prediction_payload

    picks = prediction_payload.get("picks", [])
    if not isinstance(picks, list):
        return prediction_payload

    updated_picks = []
    for pick in picks:
        if not isinstance(pick, dict):
            updated_picks.append(pick)
            continue

        settled = settled_by_id.get(pick.get("pick_id"))
        if settled:
            pick = settled

        updated_picks.append(pick)

    prediction_payload["picks"] = updated_picks
    prediction_payload["last_settled_at"] = now_iso()

    settled_count = sum(
        1 for p in updated_picks
        if str(p.get("result") or "pending").lower() in {"won", "lost", "push", "void"}
    )
    pending_count = sum(
        1 for p in updated_picks
        if str(p.get("result") or "pending").lower() == "pending"
    )

    prediction_payload.setdefault("summary", {})
    prediction_payload["summary"]["settled_picks"] = settled_count
    prediction_payload["summary"]["pending_picks"] = pending_count

    return prediction_payload


def main():
    prediction_payload = load_json(PREDICTIONS_FILE, {})
    old_results = load_json(RESULTS_FILE, [])

    if not isinstance(old_results, list):
        old_results = []

    results = merge_predictions_into_results(old_results, prediction_payload)

    debug = {
        "started_at": now_iso(),
        "predictions_file": str(PREDICTIONS_FILE),
        "results_file": str(RESULTS_FILE),
        "total_rows_before": len(results),
        "checked": 0,
        "settled_now": 0,
        "already_settled": 0,
        "still_pending": 0,
        "void_now": 0,
        "errors": [],
    }

    updated = []

    for pick in results:
        if not isinstance(pick, dict):
            continue

        current_result = str(pick.get("result") or "pending").lower()

        if current_result != "pending":
            debug["already_settled"] += 1
            updated.append(pick)
            continue

        event_key = pick.get("event_key") or pick.get("fixture_id")

        if not event_key:
            pick["settle_note"] = "missing_event_key"
            updated.append(pick)
            continue

        try:
            debug["checked"] += 1

            fixture = fetch_fixture(pick)

            if not fixture:
                pick["settle_note"] = "fixture_not_found"
                debug["still_pending"] += 1
                updated.append(pick)
                continue

            before = str(pick.get("result") or "pending").lower()
            pick = settle_pick(pick, fixture)
            after = str(pick.get("result") or "pending").lower()

            if before == "pending" and after in {"won", "lost", "push"}:
                debug["settled_now"] += 1
            elif before == "pending" and after == "void":
                debug["void_now"] += 1
            elif after == "pending":
                debug["still_pending"] += 1

            updated.append(pick)

        except Exception as e:
            debug["errors"].append({
                "event_key": event_key,
                "match": pick.get("match"),
                "error": str(e),
            })
            updated.append(pick)

            if len(debug["errors"]) >= MAX_API_ERRORS:
                break

    updated.sort(key=lambda x: (
        x.get("date") or "",
        x.get("time") or "",
        x.get("match") or "",
    ))

    settled_by_id = {
        x.get("pick_id"): x
        for x in updated
        if isinstance(x, dict) and x.get("pick_id")
    }

    prediction_payload = update_prediction_payload(prediction_payload, settled_by_id)

    total_staked = sum(
        safe_float(p.get("stake"))
        for p in updated
        if str(p.get("result") or "").lower() in {"won", "lost", "push"}
    )

    total_profit = sum(
        safe_float(p.get("profit"))
        for p in updated
        if str(p.get("result") or "").lower() in {"won", "lost", "push"}
    )

    won = sum(1 for p in updated if str(p.get("result") or "").lower() == "won")
    lost = sum(1 for p in updated if str(p.get("result") or "").lower() == "lost")
    push = sum(1 for p in updated if str(p.get("result") or "").lower() == "push")
    void = sum(1 for p in updated if str(p.get("result") or "").lower() == "void")
    pending = sum(1 for p in updated if str(p.get("result") or "pending").lower() == "pending")

    roi = round((total_profit / total_staked) * 100, 2) if total_staked > 0 else 0.0

    debug["finished_at"] = now_iso()
    debug["total_rows_after"] = len(updated)
    debug["summary"] = {
        "won": won,
        "lost": lost,
        "push": push,
        "void": void,
        "pending": pending,
        "total_staked": round(total_staked, 4),
        "total_profit": round(total_profit, 4),
        "roi_percent": roi,
    }

    save_json(RESULTS_FILE, updated)
    save_json(PREDICTIONS_FILE, prediction_payload)
    save_json(DEBUG_FILE, debug)

    print("")
    print("TENNIS TOTALS V2 WIDE SHADOW SETTLE DONE")
    print(f"Checked pending: {debug['checked']}")
    print(f"Settled now: {debug['settled_now']}")
    print(f"Void now: {debug['void_now']}")
    print(f"Still pending: {debug['still_pending']}")
    print(f"Already settled: {debug['already_settled']}")
    print(f"W/L/P/V: {won}/{lost}/{push}/{void}")
    print(f"Pending: {pending}")
    print(f"Profit: {round(total_profit, 4)}u")
    print(f"ROI: {roi}%")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {DEBUG_FILE}")

    if debug["errors"]:
        print(f"Errors: {len(debug['errors'])}")


if __name__ == "__main__":
    main()

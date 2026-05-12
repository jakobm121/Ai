import os
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_results.json")
SETTLE_DEBUG_FILE = os.path.join(DATA_DIR, "tennis_settle_debug.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35

FINISHED_STATUSES = {"finished"}
VOID_STATUSES = {
    "cancelled",
    "canceled",
    "retired",
    "walkover",
    "wo",
    "abandoned",
}
KEEP_PENDING_STATUSES = {
    "",
    "not started",
    "started",
    "inprogress",
    "in progress",
    "live",
    "suspended",
    "interrupted",
    "postponed",
}


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


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def normalize_status(value):
    return str(value or "").strip().lower()


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        text = str(value).strip()
        if "." in text:
            text = text.split(".", 1)[0]
        return int(text)
    except Exception:
        return default


def api_call(params, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing TENNIS_API_KEY or API_KEY environment variable.")

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


def score_value(score_row, keys):
    for key in keys:
        value = score_row.get(key)
        parsed = safe_int(value, None)
        if parsed is not None:
            return parsed
    return None


def tiebreak_value(score_row):
    """
    API providers do not always use the same field names for tie-breaks.
    This checks the common variants and returns the loser points if available.
    """
    possible_keys = [
        "score_tb",
        "score_tie_break",
        "score_tiebreak",
        "tie_break",
        "tiebreak",
        "tb",
        "score_first_tie_break",
        "score_second_tie_break",
        "score_first_tb",
        "score_second_tb",
        "tie_break_first",
        "tie_break_second",
        "tb_first",
        "tb_second",
    ]

    for key in possible_keys:
        value = score_row.get(key)
        parsed = safe_int(value, None)
        if parsed is not None:
            return parsed

    return None


def final_score(match):
    """
    Returns final score with tie-breaks when available.

    Example:
    7-6(4), 6-4
    6-7(5), 6-3, 6-2
    """
    scores = match.get("scores") or []

    if not scores:
        return match.get("event_final_result") or ""

    parts = []

    for score_row in scores:
        if not isinstance(score_row, dict):
            continue

        a = score_value(score_row, ["score_first", "first_score", "home_score"])
        b = score_value(score_row, ["score_second", "second_score", "away_score"])

        if a is None or b is None:
            continue

        part = f"{a}-{b}"

        # Tie-break is only relevant on 7-6 / 6-7 sets.
        if {a, b} == {6, 7}:
            tb = tiebreak_value(score_row)
            if tb is not None:
                part = f"{part}({tb})"

        parts.append(part)

    return ", ".join(parts) if parts else (match.get("event_final_result") or "")


def pick_winner_label_from_side(pick):
    pick_side = pick.get("market_side")

    if pick_side == "Home":
        return "First Player"

    if pick_side == "Away":
        return "Second Player"

    return None


def settle_as_void(pick, match, reason):
    pick["result"] = "void"
    pick["profit"] = 0.0
    pick["settled_at"] = now_iso()
    pick["settled_status"] = match.get("event_status")
    pick["settle_reason"] = reason
    pick["event_winner"] = match.get("event_winner")
    pick["final_score"] = final_score(match)

    return True, reason


def settle_pick(pick, match):
    status = normalize_status(match.get("event_status"))

    if status in VOID_STATUSES:
        return settle_as_void(pick, match, f"void_status:{status}")

    if status not in FINISHED_STATUSES:
        return False, f"keep_pending_status:{status or 'unknown'}"

    winner = match.get("event_winner")

    if winner not in {"First Player", "Second Player"}:
        return False, "missing_or_invalid_event_winner"

    pick_winner_label = pick_winner_label_from_side(pick)

    if not pick_winner_label:
        return False, "missing_or_invalid_market_side"

    won = winner == pick_winner_label

    stake = safe_float(pick.get("stake"), 1.0)
    odds = safe_float(pick.get("odds"), 0.0)

    if won:
        profit = stake * (odds - 1)
        result = "win"
    else:
        profit = -stake
        result = "loss"

    pick["result"] = result
    pick["profit"] = round(profit, 4)
    pick["settled_at"] = now_iso()
    pick["settled_status"] = match.get("event_status")
    pick["settle_reason"] = "finished_with_winner"
    pick["event_winner"] = winner
    pick["final_score"] = final_score(match)

    return True, "settled"


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
    checked = []

    for pick in pending:
        event_key = pick.get("event_key") or pick.get("fixture_id")
        match_name = pick.get("match", "Unknown match")

        if not event_key:
            print(f"MISSING EVENT KEY - KEEP PENDING: {match_name}")
            still_pending += 1
            checked.append({
                "match": match_name,
                "event_key": event_key,
                "status": None,
                "changed": False,
                "reason": "missing_event_key",
            })
            continue

        try:
            match = fetch_fixture(event_key)

            if not match:
                print(f"NO MATCH FOUND - KEEP PENDING: {match_name} | event_key={event_key}")
                not_found += 1
                still_pending += 1
                checked.append({
                    "match": match_name,
                    "event_key": event_key,
                    "status": None,
                    "changed": False,
                    "reason": "match_not_found",
                })
                continue

            status = match.get("event_status")
            score = match.get("event_final_result") or final_score(match)

            print(f"CHECK {match_name} | status={status} | score={score or '-'}")

            changed, reason = settle_pick(pick, match)

            checked.append({
                "match": match_name,
                "event_key": event_key,
                "status": status,
                "winner": match.get("event_winner"),
                "score": score,
                "changed": changed,
                "reason": reason,
            })

            if changed:
                updated += 1
                print(
                    f"SETTLED {match_name}: {pick.get('result')} "
                    f"| profit={pick.get('profit')} "
                    f"| {pick.get('final_score')}"
                )
            else:
                still_pending += 1
                print(f"KEEP PENDING {match_name}: {reason}")

        except Exception as e:
            print(f"SETTLE ERROR - KEEP PENDING: {match_name} | {e}")
            errors.append({
                "event_key": event_key,
                "match": match_name,
                "error": str(e),
            })
            checked.append({
                "match": match_name,
                "event_key": event_key,
                "changed": False,
                "reason": f"error:{e}",
            })
            still_pending += 1

    save_json(RESULTS_FILE, results)

    debug_payload = {
        "generated_at": now_iso(),
        "pending_checked": len(pending),
        "updated": updated,
        "still_pending": still_pending,
        "not_found": not_found,
        "errors": errors,
        "checked": checked,
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

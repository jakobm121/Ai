import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_results.json")
AUDIT_DEBUG_FILE = os.path.join(DATA_DIR, "tennis_audit_repair_debug.json")

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

SETTLED_RESULTS = {"win", "loss", "void", "push"}


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


def normalize_result(value):
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


def expected_result_and_profit(pick, match):
    status = normalize_status(match.get("event_status"))

    if status in VOID_STATUSES:
        return "void", 0.0, f"void_status:{status}"

    if status not in FINISHED_STATUSES:
        return None, None, f"not_finished:{status or 'unknown'}"

    winner = match.get("event_winner")

    if winner not in {"First Player", "Second Player"}:
        return None, None, "missing_or_invalid_event_winner"

    pick_winner_label = pick_winner_label_from_side(pick)

    if not pick_winner_label:
        return None, None, "missing_or_invalid_market_side"

    stake = safe_float(pick.get("stake"), 1.0)
    odds = safe_float(pick.get("odds"), 0.0)

    if winner == pick_winner_label:
        return "win", round(stake * (odds - 1), 4), "finished_with_winner"

    return "loss", round(-stake, 4), "finished_with_winner"


def needs_audit(pick):
    if not isinstance(pick, dict):
        return False

    event_key = pick.get("event_key") or pick.get("fixture_id")

    if not event_key:
        return False

    result = normalize_result(pick.get("result") or "pending")

    if result == "pending":
        return True

    if result in SETTLED_RESULTS:
        if not pick.get("final_score") and result in {"win", "loss"}:
            return True

        if pick.get("profit") is None:
            return True

        if not pick.get("settled_at"):
            return True

    return False


def apply_repair(pick, match):
    expected_result, expected_profit, reason = expected_result_and_profit(pick, match)

    if expected_result is None:
        return False, reason

    old_payload = {
        "result": pick.get("result"),
        "profit": pick.get("profit"),
        "settled_at": pick.get("settled_at"),
        "settled_status": pick.get("settled_status"),
        "event_winner": pick.get("event_winner"),
        "final_score": pick.get("final_score"),
    }

    pick["result"] = expected_result
    pick["profit"] = expected_profit
    pick["settled_at"] = pick.get("settled_at") or now_iso()
    pick["settled_status"] = match.get("event_status")
    pick["settle_reason"] = reason
    pick["event_winner"] = match.get("event_winner")
    pick["final_score"] = final_score(match)

    new_payload = {
        "result": pick.get("result"),
        "profit": pick.get("profit"),
        "settled_at": pick.get("settled_at"),
        "settled_status": pick.get("settled_status"),
        "event_winner": pick.get("event_winner"),
        "final_score": pick.get("final_score"),
    }

    return old_payload != new_payload, reason


def main():
    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    candidates = [p for p in results if needs_audit(p)]

    print(f"AUDIT CANDIDATES: {len(candidates)}")

    checked = 0
    repaired = 0
    still_pending = 0
    not_found = 0
    errors = []
    details = []

    for pick in candidates:
        event_key = pick.get("event_key") or pick.get("fixture_id")
        match_name = pick.get("match", "Unknown match")

        try:
            match = fetch_fixture(event_key)

            if not match:
                not_found += 1
                still_pending += 1
                details.append({
                    "match": match_name,
                    "event_key": event_key,
                    "changed": False,
                    "reason": "match_not_found",
                })
                print(f"NO MATCH FOUND: {match_name} | {event_key}")
                continue

            checked += 1

            changed, reason = apply_repair(pick, match)

            details.append({
                "match": match_name,
                "event_key": event_key,
                "status": match.get("event_status"),
                "winner": match.get("event_winner"),
                "score": final_score(match),
                "changed": changed,
                "reason": reason,
                "result": pick.get("result"),
                "profit": pick.get("profit"),
            })

            if changed:
                repaired += 1
                print(
                    f"REPAIRED {match_name}: {pick.get('result')} "
                    f"| profit={pick.get('profit')} "
                    f"| {pick.get('final_score')}"
                )
            else:
                if normalize_result(pick.get("result")) == "pending":
                    still_pending += 1
                print(f"NO CHANGE {match_name}: {reason}")

        except Exception as e:
            errors.append({
                "event_key": event_key,
                "match": match_name,
                "error": str(e),
            })
            still_pending += 1
            print(f"AUDIT ERROR: {match_name} | {e}")

    save_json(RESULTS_FILE, results)

    debug_payload = {
        "generated_at": now_iso(),
        "candidates": len(candidates),
        "checked": checked,
        "repaired": repaired,
        "still_pending": still_pending,
        "not_found": not_found,
        "errors": errors,
        "details": details,
    }

    save_json(AUDIT_DEBUG_FILE, debug_payload)

    print(
        f"TENNIS AUDIT REPAIR DONE: candidates={len(candidates)} "
        f"checked={checked} "
        f"repaired={repaired} "
        f"still_pending={still_pending} "
        f"not_found={not_found} "
        f"errors={len(errors)}"
    )


if __name__ == "__main__":
    main()

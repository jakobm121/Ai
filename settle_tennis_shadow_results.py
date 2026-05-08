import os
import json
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


# =========================
# CONFIG
# =========================

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"

# SHADOW FILES — main ostane nedotaknjen
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_shadow_results.json")
PREDICTIONS_FILE = os.path.join(DATA_DIR, "tennis_shadow_predictions.json")
DEBUG_FILE = os.path.join(DATA_DIR, "tennis_shadow_settle_debug.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35


# =========================
# HELPERS
# =========================

def debug(msg):
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


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        text = str(value).strip()
        if "." in text:
            text = text.split(".", 1)[0]
        return int(text)
    except Exception:
        return default


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def api_call(params, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing TENNIS_API_KEY or API_KEY environment variable.")

    params = params.copy()
    params["APIkey"] = API_KEY

    for attempt in range(retries):
        try:
            res = requests.get(
                BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if res.status_code in {429, 500, 502, 503, 504}:
                wait = 3 * (attempt + 1)
                debug(f"API retry {res.status_code}, sleeping {wait}s")
                time.sleep(wait)
                continue

            if res.status_code >= 400:
                raise RuntimeError(f"HTTP {res.status_code}: {res.text[:400]}")

            return res.json()

        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 * (attempt + 1)
            debug(f"API exception {e}, sleeping {wait}s")
            time.sleep(wait)

    raise RuntimeError("API failed after retries")


# =========================
# API FETCH
# =========================

def fetch_fixtures_for_date(date_s):
    data = api_call({
        "method": "get_fixtures",
        "date_start": date_s,
        "date_stop": date_s,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        debug(f"Fixtures error for {date_s}: {data}")
        return []

    result = data.get("result") or []
    return result if isinstance(result, list) else []


def collect_needed_dates(pending_picks):
    dates = set()

    for pick in pending_picks:
        d = pick.get("date")
        if d:
            dates.add(d)

    # Safety: dodamo še včeraj/danes/jutri, če API ali timezone zamuja
    today = today_local()
    for offset in [-1, 0, 1]:
        dates.add((today + timedelta(days=offset)).strftime("%Y-%m-%d"))

    return sorted(dates)


def fetch_fixtures_by_needed_dates(pending_picks):
    fixtures_by_event = {}

    for date_s in collect_needed_dates(pending_picks):
        debug(f"Fetching fixtures for {date_s}")
        fixtures = fetch_fixtures_for_date(date_s)

        for match in fixtures:
            event_key = match.get("event_key")
            if event_key is not None:
                fixtures_by_event[str(event_key)] = match

    return fixtures_by_event


# =========================
# SETTLEMENT LOGIC
# =========================

def is_finished(match):
    status = str(match.get("event_status") or "").lower()
    winner = match.get("event_winner")

    if status != "finished":
        return False

    if winner not in {"First Player", "Second Player"}:
        return False

    return True


def pick_won(pick, match):
    event_winner = match.get("event_winner")
    side = str(pick.get("side") or "").lower()

    if side == "home":
        return event_winner == "First Player"

    if side == "away":
        return event_winner == "Second Player"

    # fallback, če side manjka
    market_side = str(pick.get("market_side") or "").lower()

    if market_side == "home":
        return event_winner == "First Player"

    if market_side == "away":
        return event_winner == "Second Player"

    return False


def format_final_score(match):
    scores = match.get("scores") or []

    if not isinstance(scores, list) or not scores:
        return ""

    parts = []

    for s in scores:
        a = s.get("score_first")
        b = s.get("score_second")

        if a is None or b is None:
            continue

        parts.append(f"{a}-{b}")

    return ", ".join(parts)


def settle_pick(pick, match):
    won = pick_won(pick, match)

    stake = safe_float(pick.get("stake"), 1.0)
    odds = safe_float(pick.get("odds"), 0.0)

    if won:
        profit = stake * (odds - 1)
        result = "win"
    else:
        profit = -stake
        result = "loss"

    updated = pick.copy()
    updated["result"] = result
    updated["profit"] = round(profit, 4)
    updated["settled_at"] = datetime.now(ZoneInfo(TZ_NAME)).isoformat()
    updated["settled_status"] = match.get("event_status")
    updated["event_winner"] = match.get("event_winner")
    updated["final_score"] = format_final_score(match)

    return updated


def update_predictions_file(settled_results):
    """
    Ni nujno, ampak lepo je:
    current shadow predictions dobi isti result, če je pick med trenutnimi picki.
    """
    payload = load_json(PREDICTIONS_FILE, {})

    if not isinstance(payload, dict):
        return

    picks = payload.get("picks") or payload.get("current_picks") or []

    if not isinstance(picks, list):
        return

    settled_by_id = {
        p.get("pick_id"): p
        for p in settled_results
        if isinstance(p, dict) and p.get("pick_id")
    }

    changed = False
    new_picks = []

    for pick in picks:
        pick_id = pick.get("pick_id")

        if pick_id in settled_by_id:
            new_picks.append(settled_by_id[pick_id])
            changed = True
        else:
            new_picks.append(pick)

    if "picks" in payload:
        payload["picks"] = new_picks

    if "current_picks" in payload:
        payload["current_picks"] = new_picks

    if changed:
        payload["settled_updated_at"] = datetime.now(ZoneInfo(TZ_NAME)).isoformat()
        save_json(PREDICTIONS_FILE, payload)


def settle_results():
    ensure_dirs()

    history = load_json(RESULTS_FILE, [])

    if not isinstance(history, list):
        history = []

    pending = [
        p for p in history
        if isinstance(p, dict) and str(p.get("result") or "pending").lower() == "pending"
    ]

    debug(f"Pending picks: {len(pending)}")

    if not pending:
        save_json(DEBUG_FILE, {
            "settled_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),
            "pending": 0,
            "settled": 0,
            "missing": 0,
            "message": "No pending picks."
        })
        return {
            "pending": 0,
            "settled": 0,
            "missing": 0,
        }

    fixtures_by_event = fetch_fixtures_by_needed_dates(pending)

    settled_count = 0
    missing_count = 0
    not_finished_count = 0
    settled_ids = set()

    new_history = []

    for pick in history:
        if not isinstance(pick, dict):
            new_history.append(pick)
            continue

        if str(pick.get("result") or "pending").lower() != "pending":
            new_history.append(pick)
            continue

        event_key = str(pick.get("event_key") or pick.get("fixture_id") or "")
        match = fixtures_by_event.get(event_key)

        if not match:
            missing_count += 1
            new_history.append(pick)
            continue

        if not is_finished(match):
            not_finished_count += 1
            new_history.append(pick)
            continue

        settled_pick = settle_pick(pick, match)
        new_history.append(settled_pick)

        settled_ids.add(settled_pick.get("pick_id"))
        settled_count += 1

        debug(
            f"SETTLED {settled_pick.get('match')} | "
            f"{settled_pick.get('bet')} | "
            f"{settled_pick.get('result')} | "
            f"{settled_pick.get('final_score')}"
        )

    save_json(RESULTS_FILE, new_history)

    settled_results = [
        p for p in new_history
        if isinstance(p, dict) and p.get("pick_id") in settled_ids
    ]

    update_predictions_file(settled_results)

    debug_payload = {
        "settled_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),
        "results_file": RESULTS_FILE,
        "predictions_file": PREDICTIONS_FILE,
        "pending_before": len(pending),
        "settled": settled_count,
        "missing": missing_count,
        "not_finished": not_finished_count,
    }

    save_json(DEBUG_FILE, debug_payload)

    return debug_payload


def main():
    payload = settle_results()

    print("")
    print("TENNIS SHADOW SETTLE DONE")
    print(f"Pending before: {payload.get('pending_before', payload.get('pending'))}")
    print(f"Settled: {payload.get('settled')}")
    print(f"Missing: {payload.get('missing')}")
    print(f"Not finished: {payload.get('not_finished', 0)}")
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()

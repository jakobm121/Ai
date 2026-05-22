import os
import re
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

# Pomembno: s tem preveri tudi že settlane picke in popravi napačne.
CHECK_ALREADY_SETTLED = True

SETTLED_RESULTS = {"won", "lost", "push", "void"}
BAD_STATUSES = {
    "cancelled",
    "postponed",
    "walkover",
    "retired",
    "interrupted",
    "abandoned",
    "withdrawn",
}


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


def normalize_result(value):
    r = str(value or "pending").strip().lower()
    if r == "win":
        return "won"
    if r == "loss":
        return "lost"
    if r in {"won", "lost", "push", "void", "pending", "pending_review"}:
        return r
    return "pending"


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
            if isinstance(item, dict) and str(item.get("event_key")) == str(event_key):
                return item
        return result[0] if result and isinstance(result[0], dict) else None

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


def parse_score_number(value):
    """
    API-Tennis pri tie-breakih zna vrniti:
      7.6
      6.4
      7.10
      6.8

    Za total games rabimo samo glavni score seta:
      7.6  -> 7
      6.4  -> 6
      7.10 -> 7

    Nikoli ne smemo delati int(float("6.4")), ker je namen decimalke tie-break info.
    """
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace(",", ".")

    if "." in text:
        text = text.split(".", 1)[0]

    text = re.sub(r"[^\d-]", "", text)

    if text in {"", "-"}:
        return None

    try:
        return int(text)
    except Exception:
        return None


def parse_set_pair_from_text(value):
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    # Primeri:
    # 7-6
    # 7-6(5)
    # 7 - 6
    # 7.6-6.4
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)", text)
    if not m:
        return None

    a = parse_score_number(m.group(1))
    b = parse_score_number(m.group(2))

    if a is None or b is None:
        return None

    return a, b


def parse_scores(scores):
    parsed = []

    if not isinstance(scores, list):
        return parsed

    for s in scores:
        if isinstance(s, dict):
            first = s.get("score_first")
            second = s.get("score_second")

            if first is not None and second is not None:
                a = parse_score_number(first)
                b = parse_score_number(second)
                if a is not None and b is not None:
                    parsed.append((a, b))
                    continue

            # Fallback, če API kdaj vrne score v enem string field-u.
            for key in (
                "score",
                "result",
                "set_score",
                "event_score",
                "score_set",
                "games",
                "value",
            ):
                pair = parse_set_pair_from_text(s.get(key))
                if pair:
                    parsed.append(pair)
                    break
        else:
            pair = parse_set_pair_from_text(s)
            if pair:
                parsed.append(pair)

    return parsed


def parse_scores_from_fixture(fixture):
    scores = fixture.get("scores") or []
    parsed = parse_scores(scores)

    if parsed:
        return parsed

    # Fallback iz fixture-level stringov.
    for key in (
        "event_final_result",
        "event_game_result",
        "event_result",
        "event_score",
        "final_score",
        "score",
    ):
        value = fixture.get(key)
        if not value:
            continue

        pairs = re.findall(r"(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)", str(value))
        if pairs:
            out = []
            for a_raw, b_raw in pairs:
                a = parse_score_number(a_raw)
                b = parse_score_number(b_raw)
                if a is not None and b is not None:
                    out.append((a, b))
            if out:
                return out

    return []


def final_score_string(scores):
    if not scores:
        return ""
    return " ".join(f"{a}-{b}" for a, b in scores)


def raw_scores_for_debug(fixture):
    raw = fixture.get("scores")
    if raw is None:
        return None
    try:
        return json.loads(json.dumps(raw, ensure_ascii=False))
    except Exception:
        return str(raw)


def looks_like_completed_best_of_3(scores):
    """
    Normalen completed tennis match mora imeti vsaj 2 seta.
    1 set pri status=finished je sumljiv API zapis ali nedokončan score.
    """
    if not scores:
        return False

    if len(scores) < 2:
        return False

    first_sets = 0
    second_sets = 0

    for a, b in scores:
        if a > b:
            first_sets += 1
        elif b > a:
            second_sets += 1

    return first_sets >= 2 or second_sets >= 2


def total_games_from_fixture(fixture):
    scores = parse_scores_from_fixture(fixture)
    return sum(a + b for a, b in scores), scores


def calculate_pick_result(side, line, total_games):
    side = str(side or "").lower()

    if side == "over":
        if total_games > line:
            return "won"
        if total_games < line:
            return "lost"
        return "push"

    if side == "under":
        if total_games < line:
            return "won"
        if total_games > line:
            return "lost"
        return "push"

    return "pending_review"


def apply_profit(pick, result):
    stake = safe_float(pick.get("stake"), 1.0)
    odds = safe_float(pick.get("odds"))

    if result == "won":
        profit = stake * (odds - 1)
        return_units = stake * odds
    elif result == "lost":
        profit = -stake
        return_units = 0.0
    elif result == "push":
        profit = 0.0
        return_units = stake
    elif result == "void":
        profit = 0.0
        return_units = 0.0
    else:
        profit = 0.0
        return_units = 0.0

    pick["profit"] = round(profit, 4)
    pick["return_units"] = round(return_units, 4)

    return pick


def settle_pick(pick, fixture, recheck=False):
    before_result = normalize_result(pick.get("result"))
    before_total = pick.get("total_games")
    before_score = pick.get("final_score")
    before_profit = pick.get("profit")

    status = str(fixture.get("event_status") or "").strip().lower()

    pick["settle_checked_at"] = now_iso()
    pick["settle_status"] = status
    pick["scores_raw"] = raw_scores_for_debug(fixture)

    if status in BAD_STATUSES:
        pick["result"] = "void"
        pick["settled_at"] = now_iso()
        pick["total_games"] = None
        pick["final_score"] = str(fixture.get("event_final_result") or "")
        pick["settle_note"] = f"void_status_{status}"
        apply_profit(pick, "void")
    elif status != "finished":
        # Če še ni končano, ne spreminjaj že settlanega v pending, razen če je recheck našel čuden status.
        if before_result in SETTLED_RESULTS and recheck:
            pick["settle_note"] = f"recheck_status_not_finished_{status}"
        else:
            pick["result"] = "pending"
            pick["settle_note"] = f"not_finished_{status or 'unknown'}"
        return pick
    else:
        total_games, scores = total_games_from_fixture(fixture)

        pick["total_games"] = total_games if scores else None
        pick["final_score"] = final_score_string(scores)

        if not scores or total_games <= 0:
            pick["result"] = "pending_review"
            pick["settle_note"] = "finished_but_no_valid_scores"
            pick["settle_needs_review"] = True
            apply_profit(pick, "pending_review")
            return pick

        if not looks_like_completed_best_of_3(scores):
            pick["result"] = "pending_review"
            pick["settle_note"] = "finished_but_incomplete_score_less_than_2_sets"
            pick["settle_needs_review"] = True
            apply_profit(pick, "pending_review")
            return pick

        side = str(pick.get("side") or "").lower()
        line = safe_float(pick.get("line"))
        odds = safe_float(pick.get("odds"))

        if side not in {"over", "under"} or line <= 0 or odds <= 1:
            pick["result"] = "pending_review"
            pick["settle_note"] = "invalid_pick_data"
            pick["settle_needs_review"] = True
            apply_profit(pick, "pending_review")
            return pick

        result = calculate_pick_result(side, line, total_games)

        pick["result"] = result
        pick["settled_at"] = now_iso()
        pick["settle_note"] = "settled_ok"
        pick["settle_needs_review"] = False
        apply_profit(pick, result)

    after_result = normalize_result(pick.get("result"))

    if recheck and (
        before_result != after_result
        or before_total != pick.get("total_games")
        or before_score != pick.get("final_score")
        or safe_float(before_profit, None) != safe_float(pick.get("profit"), None)
    ):
        pick.setdefault("settle_audit", [])
        pick["settle_audit"].append({
            "checked_at": now_iso(),
            "before": {
                "result": before_result,
                "total_games": before_total,
                "final_score": before_score,
                "profit": before_profit,
            },
            "after": {
                "result": pick.get("result"),
                "total_games": pick.get("total_games"),
                "final_score": pick.get("final_score"),
                "profit": pick.get("profit"),
            },
            "reason": "rechecked_and_corrected",
        })

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
            old_result = normalize_result(old.get("result"))

            # Če je star že settled, ne povozimo z novim pending pickom.
            # Recheck ga bo kasneje preveril preko API-ja.
            if old_result in SETTLED_RESULTS or old_result == "pending_review":
                merged = pick.copy()
                merged.update(old)
                existing_by_id[pick["pick_id"]] = merged
            else:
                merged = old.copy()
                merged.update(pick)
                existing_by_id[pick["pick_id"]] = merged
        else:
            pick["result"] = normalize_result(pick.get("result"))
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

    won = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "won")
    lost = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "lost")
    push = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "push")
    void = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "void")
    pending = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "pending")
    pending_review = sum(1 for p in updated_picks if normalize_result(p.get("result")) == "pending_review")

    settled_for_roi = [
        p for p in updated_picks
        if normalize_result(p.get("result")) in {"won", "lost", "push"}
    ]

    total_staked = sum(safe_float(p.get("stake")) for p in settled_for_roi)
    total_profit = sum(safe_float(p.get("profit")) for p in settled_for_roi)
    roi = round((total_profit / total_staked) * 100, 2) if total_staked > 0 else 0.0

    prediction_payload.setdefault("summary", {})
    prediction_payload["summary"].update({
        "settled_picks": won + lost + push + void,
        "pending_picks": pending,
        "pending_review": pending_review,
        "won": won,
        "lost": lost,
        "push": push,
        "void": void,
        "total_staked": round(total_staked, 4),
        "total_profit": round(total_profit, 4),
        "roi_percent": roi,
    })

    return prediction_payload


def calculate_global_summary(rows):
    won = sum(1 for p in rows if normalize_result(p.get("result")) == "won")
    lost = sum(1 for p in rows if normalize_result(p.get("result")) == "lost")
    push = sum(1 for p in rows if normalize_result(p.get("result")) == "push")
    void = sum(1 for p in rows if normalize_result(p.get("result")) == "void")
    pending = sum(1 for p in rows if normalize_result(p.get("result")) == "pending")
    pending_review = sum(1 for p in rows if normalize_result(p.get("result")) == "pending_review")

    roi_rows = [
        p for p in rows
        if normalize_result(p.get("result")) in {"won", "lost", "push"}
    ]

    total_staked = sum(safe_float(p.get("stake")) for p in roi_rows)
    total_profit = sum(safe_float(p.get("profit")) for p in roi_rows)
    roi = round((total_profit / total_staked) * 100, 2) if total_staked > 0 else 0.0

    return {
        "won": won,
        "lost": lost,
        "push": push,
        "void": void,
        "pending": pending,
        "pending_review": pending_review,
        "total_staked": round(total_staked, 4),
        "total_profit": round(total_profit, 4),
        "roi_percent": roi,
    }


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
        "check_already_settled": CHECK_ALREADY_SETTLED,
        "total_rows_before": len(results),
        "checked": 0,
        "settled_now": 0,
        "void_now": 0,
        "already_settled_skipped": 0,
        "already_settled_checked": 0,
        "corrected_on_recheck": 0,
        "pending_review_now": 0,
        "still_pending": 0,
        "errors": [],
    }

    updated = []

    for pick in results:
        if not isinstance(pick, dict):
            continue

        current_result = normalize_result(pick.get("result"))
        event_key = pick.get("event_key") or pick.get("fixture_id")

        if not event_key:
            pick["settle_note"] = "missing_event_key"
            updated.append(pick)
            continue

        if current_result in SETTLED_RESULTS and not CHECK_ALREADY_SETTLED:
            debug["already_settled_skipped"] += 1
            updated.append(pick)
            continue

        try:
            debug["checked"] += 1

            if current_result in SETTLED_RESULTS:
                debug["already_settled_checked"] += 1

            fixture = fetch_fixture(pick)

            if not fixture:
                if current_result in SETTLED_RESULTS:
                    pick["settle_note"] = "recheck_fixture_not_found_keep_old_result"
                else:
                    pick["settle_note"] = "fixture_not_found"
                    debug["still_pending"] += 1
                updated.append(pick)
                continue

            before_result = normalize_result(pick.get("result"))
            before_total = pick.get("total_games")
            before_score = pick.get("final_score")
            before_profit = pick.get("profit")

            pick = settle_pick(
                pick,
                fixture,
                recheck=before_result in SETTLED_RESULTS or before_result == "pending_review",
            )

            after_result = normalize_result(pick.get("result"))

            if before_result == "pending" and after_result in {"won", "lost", "push"}:
                debug["settled_now"] += 1
            elif before_result == "pending" and after_result == "void":
                debug["void_now"] += 1
            elif after_result == "pending":
                debug["still_pending"] += 1
            elif after_result == "pending_review":
                debug["pending_review_now"] += 1

            if before_result in SETTLED_RESULTS and (
                before_result != after_result
                or before_total != pick.get("total_games")
                or before_score != pick.get("final_score")
                or safe_float(before_profit, None) != safe_float(pick.get("profit"), None)
            ):
                debug["corrected_on_recheck"] += 1

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

    debug["finished_at"] = now_iso()
    debug["total_rows_after"] = len(updated)
    debug["summary"] = calculate_global_summary(updated)

    save_json(RESULTS_FILE, updated)
    save_json(PREDICTIONS_FILE, prediction_payload)
    save_json(DEBUG_FILE, debug)

    s = debug["summary"]

    print("")
    print("TENNIS TOTALS V2 WIDE SHADOW SETTLE DONE")
    print(f"Checked: {debug['checked']}")
    print(f"Settled now: {debug['settled_now']}")
    print(f"Void now: {debug['void_now']}")
    print(f"Pending review now: {debug['pending_review_now']}")
    print(f"Still pending: {debug['still_pending']}")
    print(f"Already settled checked: {debug['already_settled_checked']}")
    print(f"Corrected on recheck: {debug['corrected_on_recheck']}")
    print(f"W/L/P/V: {s['won']}/{s['lost']}/{s['push']}/{s['void']}")
    print(f"Pending: {s['pending']}")
    print(f"Pending review: {s['pending_review']}")
    print(f"Profit: {s['total_profit']}u")
    print(f"ROI: {s['roi_percent']}%")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {DEBUG_FILE}")

    if debug["errors"]:
        print(f"Errors: {len(debug['errors'])}")


if __name__ == "__main__":
    main()

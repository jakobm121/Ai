import json
import os
import sys
import time
import math
import requests
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo


# Allow import from ratings/ when script is run from repo root.
sys.path.append(os.path.dirname(__file__))

try:
    from elo_lookup import get_elo_signal
except Exception as e:
    raise RuntimeError(
        "Cannot import ratings/elo_lookup.py. "
        "Run this script from repo root, or check that elo_lookup.py exists."
    ) from e


TZ_NAME = "Europe/Ljubljana"

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TARGET_DAYS_BACK = int(os.getenv("TARGET_DAYS_BACK", "5"))
FORM_DAYS_BACK = int(os.getenv("FORM_DAYS_BACK", "45"))
FORM_LAST_N_1 = int(os.getenv("FORM_LAST_N_1", "5"))
FORM_LAST_N_2 = int(os.getenv("FORM_LAST_N_2", "10"))

REQUEST_SLEEP_SECONDS = float(os.getenv("REQUEST_SLEEP_SECONDS", "0.35"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "35"))

MIN_ABS_COMBINED_SCORE = float(os.getenv("MIN_ABS_COMBINED_SCORE", "0.00"))

OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest.json"
OUTPUT_MISSING_FILE = "ratings/elo_form_market_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest.md"


def now_local():
    return datetime.now(ZoneInfo(TZ_NAME))


def today_local_date():
    return now_local().date()


def now_iso():
    return now_local().isoformat()


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        if value == "":
            return default
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value in {"-", "—", "null", "None"}:
                return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(float(str(value).strip()))
    except Exception:
        return default


def clean_text(value):
    return str(value or "").strip()


def norm_name(value):
    return " ".join(clean_text(value).lower().replace(".", "").split())


def parse_date(value):
    if not value:
        return None

    value = str(value).strip()

    for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(value[:10], fmt).date()
        except Exception:
            pass

    try:
        return datetime.fromisoformat(value[:10]).date()
    except Exception:
        return None


def daterange(date_start, date_stop):
    if isinstance(date_start, str):
        start = datetime.fromisoformat(date_start).date()
    else:
        start = date_start

    if isinstance(date_stop, str):
        stop = datetime.fromisoformat(date_stop).date()
    else:
        stop = date_stop

    current = start
    while current <= stop:
        yield current.isoformat()
        current += timedelta(days=1)


def api_result_list(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in ["result", "results", "data", "fixtures", "odds"]:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    return []


def fetch_api(method, params=None, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing env var TENNIS_API_KEY or API_KEY")

    params = dict(params or {})
    params["method"] = method
    params["APIkey"] = API_KEY

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                success = data.get("success")
                if success == 0 or success is False:
                    msg = data.get("error") or data.get("message") or data
                    raise RuntimeError(f"API returned error: {msg}")

            return data

        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(1.5 * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def collect_fixtures(date_start, date_stop):
    rows = []

    for d in daterange(date_start, date_stop):
        print(f"Fetching fixtures: {d}")

        try:
            data = fetch_api("get_fixtures", {
                "date_start": d,
                "date_stop": d,
            })

            day_rows = api_result_list(data)
            rows.extend(day_rows)

            print(f"  fixtures: {len(day_rows)}")
            time.sleep(REQUEST_SLEEP_SECONDS)

        except Exception as e:
            print(f"WARNING: get_fixtures failed for {d}, skipping day: {e}")
            continue

    return rows


def collect_odds(date_start, date_stop):
    rows = []

    for d in daterange(date_start, date_stop):
        print(f"Fetching odds: {d}")

        try:
            data = fetch_api("get_odds", {
                "date_start": d,
                "date_stop": d,
            })

            day_rows = api_result_list(data)
            rows.extend(day_rows)

            print(f"  odds rows: {len(day_rows)}")
            time.sleep(REQUEST_SLEEP_SECONDS)

        except Exception as e:
            print(f"WARNING: get_odds failed for {d}, skipping day: {e}")
            continue

    return rows


def fixture_event_key(row):
    return clean_text(
        row.get("event_key")
        or row.get("id")
        or row.get("fixture_id")
        or row.get("match_id")
    )


def fixture_date(row):
    return parse_date(
        row.get("event_date")
        or row.get("date")
        or row.get("match_date")
        or row.get("fixture_date")
    )


def fixture_time(row):
    return clean_text(
        row.get("event_time")
        or row.get("time")
        or row.get("match_time")
    )


def first_player_name(row):
    return clean_text(
        row.get("event_first_player")
        or row.get("first_player")
        or row.get("first_player_name")
        or row.get("home_team")
        or row.get("player1")
        or row.get("player_1")
    )


def second_player_name(row):
    return clean_text(
        row.get("event_second_player")
        or row.get("second_player")
        or row.get("second_player_name")
        or row.get("away_team")
        or row.get("player2")
        or row.get("player_2")
    )


def infer_tour(row):
    raw_values = [
        row.get("event_type_type"),
        row.get("event_type"),
        row.get("tour_level"),
        row.get("league_name"),
        row.get("tournament_name"),
        row.get("tournament_key"),
    ]

    text = " ".join(clean_text(x).lower() for x in raw_values if x)

    if "wta" in text or "women" in text:
        return "wta"

    if "atp" in text or "men" in text:
        return "atp"

    if "challenger" in text:
        return "challenger"

    if "itf" in text:
        return "itf"

    return None


def infer_surface(row):
    value = (
        row.get("event_surface")
        or row.get("surface")
        or row.get("court_surface")
        or row.get("court")
    )

    if not value:
        return None

    value = clean_text(value).lower()

    if "hard" in value:
        return "hard"
    if "clay" in value:
        return "clay"
    if "grass" in value:
        return "grass"
    if "carpet" in value:
        return "carpet"

    return value


def final_result_text(row):
    return clean_text(
        row.get("event_final_result")
        or row.get("final_result")
        or row.get("score")
        or row.get("result")
    )


def is_finished_fixture(row):
    status = clean_text(
        row.get("event_status")
        or row.get("status")
        or row.get("match_status")
    ).lower()

    if status in {"finished", "after penalties", "ended", "complete", "completed", "ft"}:
        return True

    if final_result_text(row):
        return True

    return False


def winner_side_from_fixture(row):
    winner = clean_text(
        row.get("event_winner")
        or row.get("winner")
        or row.get("match_winner")
    )

    first = first_player_name(row)
    second = second_player_name(row)

    winner_norm = norm_name(winner)

    if winner_norm:
        if winner_norm in {"first player", "first_player", "player 1", "player1", "1", "home"}:
            return "first"

        if winner_norm in {"second player", "second_player", "player 2", "player2", "2", "away"}:
            return "second"

        if first and winner_norm == norm_name(first):
            return "first"

        if second and winner_norm == norm_name(second):
            return "second"

    fp_result = safe_int(
        row.get("event_first_player_result")
        or row.get("first_player_result")
        or row.get("home_result")
    )
    sp_result = safe_int(
        row.get("event_second_player_result")
        or row.get("second_player_result")
        or row.get("away_result")
    )

    if fp_result is not None and sp_result is not None and fp_result != sp_result:
        return "first" if fp_result > sp_result else "second"

    score = final_result_text(row)

    if score:
        parts = score.replace("–", "-").replace(":", "-").split("-")
        if len(parts) >= 2:
            a = safe_int(parts[0])
            b = safe_int(parts[1])
            if a is not None and b is not None and a != b:
                return "first" if a > b else "second"

    scores = row.get("scores")
    if isinstance(scores, list):
        first_sets = 0
        second_sets = 0

        for s in scores:
            if not isinstance(s, dict):
                continue

            a = safe_int(
                s.get("score_first")
                or s.get("first_score")
                or s.get("home_score")
                or s.get("score_home")
            )
            b = safe_int(
                s.get("score_second")
                or s.get("second_score")
                or s.get("away_score")
                or s.get("score_away")
            )

            if a is None or b is None or a == b:
                continue

            if a > b:
                first_sets += 1
            else:
                second_sets += 1

        if first_sets != second_sets:
            return "first" if first_sets > second_sets else "second"

    return None


def odds_event_key(row):
    return clean_text(
        row.get("event_key")
        or row.get("id")
        or row.get("fixture_id")
        or row.get("match_id")
    )


def looks_like_odd(value):
    x = safe_float(value)
    return x is not None and 1.01 <= x <= 30.0


def extract_odds_candidates_from_flat_dict(row):
    first = []
    second = []

    first_key_words = [
        "odd_1",
        "odds_1",
        "home",
        "first",
        "player1",
        "player_1",
        "one",
    ]

    second_key_words = [
        "odd_2",
        "odds_2",
        "away",
        "second",
        "player2",
        "player_2",
        "two",
    ]

    for key, value in row.items():
        if isinstance(value, (dict, list)):
            continue

        if not looks_like_odd(value):
            continue

        k = str(key).lower()

        if any(word in k for word in first_key_words):
            first.append(safe_float(value))

        if any(word in k for word in second_key_words):
            second.append(safe_float(value))

    return first, second


def walk_nested_odds(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_nested_odds(value)

    elif isinstance(obj, list):
        for item in obj:
            yield from walk_nested_odds(item)


def extract_odds_candidates_nested(row):
    first = []
    second = []

    for item in walk_nested_odds(row):
        if not isinstance(item, dict):
            continue

        name = clean_text(
            item.get("odd_name")
            or item.get("name")
            or item.get("label")
            or item.get("selection")
            or item.get("handicap")
        ).lower()

        value = (
            item.get("odd_value")
            or item.get("value")
            or item.get("odd")
            or item.get("price")
            or item.get("decimal")
        )

        if not looks_like_odd(value):
            continue

        odd = safe_float(value)

        if name in {"1", "home", "first", "first player", "player 1", "player1"}:
            first.append(odd)
        elif name in {"2", "away", "second", "second player", "player 2", "player2"}:
            second.append(odd)

    return first, second


def extract_match_winner_odds(row):
    first_a, second_a = extract_odds_candidates_from_flat_dict(row)
    first_b, second_b = extract_odds_candidates_nested(row)

    first = first_a + first_b
    second = second_a + second_b

    if not first or not second:
        return None

    return {
        "first_odds": max(first),
        "second_odds": max(second),
        "first_odds_all": sorted(set(round(x, 3) for x in first)),
        "second_odds_all": sorted(set(round(x, 3) for x in second)),
    }


def build_odds_index(odds_rows):
    by_event_key = {}

    for row in odds_rows:
        if not isinstance(row, dict):
            continue

        key = odds_event_key(row)
        odds = extract_match_winner_odds(row)

        if not key or not odds:
            continue

        current = by_event_key.get(key)

        if current is None:
            by_event_key[key] = odds
            continue

        current["first_odds"] = max(current["first_odds"], odds["first_odds"])
        current["second_odds"] = max(current["second_odds"], odds["second_odds"])
        current["first_odds_all"] = sorted(set(current["first_odds_all"] + odds["first_odds_all"]))
        current["second_odds_all"] = sorted(set(current["second_odds_all"] + odds["second_odds_all"]))

    return by_event_key


def player_fixture_result(row, player_name):
    first = first_player_name(row)
    second = second_player_name(row)

    if not first or not second:
        return None

    p = norm_name(player_name)

    if p not in {norm_name(first), norm_name(second)}:
        return None

    winner = winner_side_from_fixture(row)

    if winner not in {"first", "second"}:
        return None

    is_first = p == norm_name(first)

    if is_first and winner == "first":
        return "win"
    if is_first and winner == "second":
        return "loss"
    if not is_first and winner == "second":
        return "win"
    if not is_first and winner == "first":
        return "loss"

    return None


def build_player_history(fixtures):
    history = {}

    for row in fixtures:
        if not isinstance(row, dict):
            continue

        d = fixture_date(row)
        if not d:
            continue

        first = first_player_name(row)
        second = second_player_name(row)

        if not first or not second:
            continue

        winner = winner_side_from_fixture(row)

        if winner not in {"first", "second"}:
            continue

        for player in [first, second]:
            result = player_fixture_result(row, player)
            if result not in {"win", "loss"}:
                continue

            key = norm_name(player)

            history.setdefault(key, []).append({
                "date": d.isoformat(),
                "player": player,
                "opponent": second if norm_name(player) == norm_name(first) else first,
                "result": result,
                "event_key": fixture_event_key(row),
                "tour": infer_tour(row),
                "surface": infer_surface(row),
            })

    for key in history:
        history[key].sort(key=lambda x: x["date"], reverse=True)

    return history


def form_for_player(history, player, before_date, n):
    key = norm_name(player)
    rows = history.get(key, [])

    selected = []

    for r in rows:
        d = parse_date(r.get("date"))
        if not d:
            continue

        if d >= before_date:
            continue

        selected.append(r)

        if len(selected) >= n:
            break

    wins = sum(1 for r in selected if r.get("result") == "win")
    losses = sum(1 for r in selected if r.get("result") == "loss")
    total = wins + losses
    win_rate = wins / total if total else None

    return {
        "n": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate * 100, 2) if win_rate is not None else None,
        "raw_win_rate": win_rate,
    }


def cap(value, low, high):
    return max(low, min(high, value))


def elo_score(signal):
    overall = safe_float(signal.get("overall_elo_diff"))
    surface = safe_float(signal.get("surface_elo_diff"))

    if overall is None and surface is None:
        return None

    if surface is not None and overall is not None:
        raw = 0.65 * surface + 0.35 * overall
    elif surface is not None:
        raw = surface
    else:
        raw = overall

    return cap(raw / 250.0, -1.0, 1.0)


def form_score(first_form_5, second_form_5, first_form_10, second_form_10):
    values = []

    if first_form_5["raw_win_rate"] is not None and second_form_5["raw_win_rate"] is not None:
        values.append(0.65 * (first_form_5["raw_win_rate"] - second_form_5["raw_win_rate"]))

    if first_form_10["raw_win_rate"] is not None and second_form_10["raw_win_rate"] is not None:
        values.append(0.35 * (first_form_10["raw_win_rate"] - second_form_10["raw_win_rate"]))

    if not values:
        return 0.0

    return cap(sum(values), -1.0, 1.0)


def combined_score(elo_s, form_s):
    if elo_s is None:
        return None

    return 0.75 * elo_s + 0.25 * form_s


def prediction_from_score(score):
    if score is None:
        return None

    if abs(score) < MIN_ABS_COMBINED_SCORE:
        return None

    return "first" if score > 0 else "second"


def profit_for_pick(pick_side, winner_side, first_odds, second_odds):
    if pick_side not in {"first", "second"}:
        return None

    odds = first_odds if pick_side == "first" else second_odds

    if not odds:
        return None

    if winner_side == pick_side:
        return round(odds - 1.0, 3)

    return -1.0


def odds_bucket(odds):
    if odds is None:
        return "unknown"
    if odds < 1.40:
        return "<1.40"
    if odds < 1.60:
        return "1.40-1.59"
    if odds < 1.80:
        return "1.60-1.79"
    if odds < 2.00:
        return "1.80-1.99"
    if odds < 2.50:
        return "2.00-2.49"
    if odds < 3.00:
        return "2.50-2.99"
    return "3.00+"


def score_bucket(score):
    if score is None:
        return "unknown"

    abs_score = abs(score)

    if abs_score < 0.10:
        return "0.00-0.10"
    if abs_score < 0.20:
        return "0.10-0.20"
    if abs_score < 0.35:
        return "0.20-0.35"
    if abs_score < 0.50:
        return "0.35-0.50"
    return "0.50+"


def elo_diff_bucket(value):
    if value is None:
        return "unknown"

    v = abs(value)

    if v < 30:
        return "0-30"
    if v < 70:
        return "30-70"
    if v < 120:
        return "70-120"
    if v < 180:
        return "120-180"
    if v < 220:
        return "180-220"
    return "220+"


def empty_stats():
    return {
        "n": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0,
        "stake": 0.0,
        "avg_odds_sum": 0.0,
        "avg_combined_score_sum": 0.0,
        "avg_abs_overall_elo_diff_sum": 0.0,
        "avg_abs_surface_elo_diff_sum": 0.0,
    }


def add_stat(stats, key, row):
    stats.setdefault(key, empty_stats())
    s = stats[key]

    result = row.get("result")
    profit = safe_float(row.get("profit"), 0.0)
    odds = safe_float(row.get("odds"), 0.0)
    combined = safe_float(row.get("combined_score"), 0.0)

    overall_diff = row.get("elo", {}).get("overall_elo_diff")
    surface_diff = row.get("elo", {}).get("surface_elo_diff")

    s["n"] += 1
    s["stake"] += 1.0
    s["profit"] += profit
    s["avg_odds_sum"] += odds
    s["avg_combined_score_sum"] += abs(combined)

    if overall_diff is not None:
        s["avg_abs_overall_elo_diff_sum"] += abs(overall_diff)

    if surface_diff is not None:
        s["avg_abs_surface_elo_diff_sum"] += abs(surface_diff)

    if result == "win":
        s["wins"] += 1
    elif result == "loss":
        s["losses"] += 1


def finalize_stats(stats):
    out = {}

    for key, s in sorted(stats.items(), key=lambda kv: kv[0]):
        n = s["n"]
        wins = s["wins"]
        losses = s["losses"]
        stake = s["stake"]
        profit = s["profit"]

        graded = wins + losses

        out[key] = {
            "n": n,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / graded * 100, 2) if graded else 0.0,
            "profit": round(profit, 3),
            "stake": round(stake, 3),
            "roi": round(profit / stake * 100, 2) if stake else 0.0,
            "avg_odds": round(s["avg_odds_sum"] / n, 3) if n else 0.0,
            "avg_abs_combined_score": round(s["avg_combined_score_sum"] / n, 3) if n else 0.0,
            "avg_abs_overall_elo_diff": round(s["avg_abs_overall_elo_diff_sum"] / n, 2) if n else 0.0,
            "avg_abs_surface_elo_diff": round(s["avg_abs_surface_elo_diff_sum"] / n, 2) if n else 0.0,
        }

    return out


def analyse_rows(rows):
    stats = {}

    for row in rows:
        add_stat(stats, "overall", row)
        add_stat(stats, f"tour:{row.get('tour') or 'unknown'}", row)
        add_stat(stats, f"surface:{row.get('surface') or 'unknown'}", row)
        add_stat(stats, f"pick_side:{row.get('pick_side')}", row)
        add_stat(stats, f"odds:{odds_bucket(row.get('odds'))}", row)
        add_stat(stats, f"score:{score_bucket(row.get('combined_score'))}", row)

        overall_diff = row.get("elo", {}).get("overall_elo_diff")
        surface_diff = row.get("elo", {}).get("surface_elo_diff")

        add_stat(stats, f"overall_elo_diff:{elo_diff_bucket(overall_diff)}", row)
        add_stat(stats, f"surface_elo_diff:{elo_diff_bucket(surface_diff)}", row)

    return finalize_stats(stats)


def collect_rows():
    target_stop = today_local_date()
    target_start = target_stop - timedelta(days=TARGET_DAYS_BACK)

    form_start = target_start - timedelta(days=FORM_DAYS_BACK)
    form_stop = target_stop

    print(f"Fetching fixtures for form: {form_start} -> {form_stop}")
    all_fixtures = collect_fixtures(form_start, form_stop)

    print(f"Fetching odds for target window: {target_start} -> {target_stop}")
    odds_rows = collect_odds(target_start, target_stop)

    odds_index = build_odds_index(odds_rows)
    history = build_player_history(all_fixtures)

    rows = []
    missing = []

    for fixture in all_fixtures:
        if not isinstance(fixture, dict):
            continue

        d = fixture_date(fixture)
        if not d:
            continue

        if d < target_start or d > target_stop:
            continue

        if not is_finished_fixture(fixture):
            continue

        event_key = fixture_event_key(fixture)
        first = first_player_name(fixture)
        second = second_player_name(fixture)

        if not event_key or not first or not second:
            missing.append({
                "reason": "missing_event_key_or_players",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
                "raw": fixture,
            })
            continue

        winner = winner_side_from_fixture(fixture)

        if winner not in {"first", "second"}:
            missing.append({
                "reason": "missing_winner",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
                "score": final_result_text(fixture),
            })
            continue

        odds = odds_index.get(event_key)

        if not odds:
            missing.append({
                "reason": "missing_match_winner_odds",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
            })
            continue

        tour = infer_tour(fixture)
        surface = infer_surface(fixture)

        signal = get_elo_signal(
            first,
            second,
            surface=surface,
            tour=tour,
        )

        if not signal.get("matched"):
            missing.append({
                "reason": "elo_not_matched",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
                "tour": tour,
                "surface": surface,
                "first_matched": signal.get("player", {}).get("matched"),
                "second_matched": signal.get("opponent", {}).get("matched"),
                "first_method": signal.get("player", {}).get("match_method"),
                "second_method": signal.get("opponent", {}).get("match_method"),
            })
            continue

        first_form_5 = form_for_player(history, first, d, FORM_LAST_N_1)
        second_form_5 = form_for_player(history, second, d, FORM_LAST_N_1)
        first_form_10 = form_for_player(history, first, d, FORM_LAST_N_2)
        second_form_10 = form_for_player(history, second, d, FORM_LAST_N_2)

        e_score = elo_score(signal)
        f_score = form_score(first_form_5, second_form_5, first_form_10, second_form_10)
        c_score = combined_score(e_score, f_score)

        pick_side = prediction_from_score(c_score)

        if pick_side not in {"first", "second"}:
            missing.append({
                "reason": "no_prediction_after_score_filter",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
                "elo_score": e_score,
                "form_score": f_score,
                "combined_score": c_score,
            })
            continue

        pick_player = first if pick_side == "first" else second
        pick_odds = odds["first_odds"] if pick_side == "first" else odds["second_odds"]
        profit = profit_for_pick(pick_side, winner, odds["first_odds"], odds["second_odds"])

        if profit is None:
            missing.append({
                "reason": "missing_pick_odds",
                "event_key": event_key,
                "date": d.isoformat(),
                "first": first,
                "second": second,
                "pick_side": pick_side,
            })
            continue

        result = "win" if pick_side == winner else "loss"

        rows.append({
            "date": d.isoformat(),
            "time": fixture_time(fixture),
            "event_key": event_key,
            "match": f"{first} - {second}",
            "first_player": first,
            "second_player": second,
            "tour": tour,
            "surface": surface,
            "winner_side": winner,
            "winner_player": first if winner == "first" else second,
            "pick_side": pick_side,
            "pick": pick_player,
            "odds": round(pick_odds, 3),
            "first_odds": round(odds["first_odds"], 3),
            "second_odds": round(odds["second_odds"], 3),
            "result": result,
            "profit": round(profit, 3),
            "stake": 1.0,
            "elo_score": round(e_score, 4) if e_score is not None else None,
            "form_score": round(f_score, 4) if f_score is not None else None,
            "combined_score": round(c_score, 4) if c_score is not None else None,
            "elo": {
                "matched": signal.get("matched"),
                "overall_elo_diff": signal.get("overall_elo_diff"),
                "surface_elo_diff": signal.get("surface_elo_diff"),
                "first_matched_name": signal.get("player", {}).get("matched_name"),
                "second_matched_name": signal.get("opponent", {}).get("matched_name"),
                "first_method": signal.get("player", {}).get("match_method"),
                "second_method": signal.get("opponent", {}).get("match_method"),
            },
            "form": {
                "first_last_5": first_form_5,
                "second_last_5": second_form_5,
                "first_last_10": first_form_10,
                "second_last_10": second_form_10,
            },
        })

    meta = {
        "target_start": target_start.isoformat(),
        "target_stop": target_stop.isoformat(),
        "form_start": form_start.isoformat(),
        "form_stop": form_stop.isoformat(),
        "fixtures_collected": len(all_fixtures),
        "odds_rows_collected": len(odds_rows),
        "odds_events_indexed": len(odds_index),
        "rows": len(rows),
        "missing": len(missing),
    }

    return rows, missing, meta


def build_table(report):
    lines = []

    lines.append("# ELO + form + market backtest")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Window: {report['meta']['target_start']} -> {report['meta']['target_stop']}")
    lines.append(f"Form window: {report['meta']['form_start']} -> {report['meta']['form_stop']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Fixtures collected: {report['meta']['fixtures_collected']}")
    lines.append(f"- Odds rows collected: {report['meta']['odds_rows_collected']}")
    lines.append(f"- Odds events indexed: {report['meta']['odds_events_indexed']}")
    lines.append(f"- Backtest rows: {report['meta']['rows']}")
    lines.append(f"- Missing/skipped: {report['meta']['missing']}")
    lines.append("")

    overall = report["stats"].get("overall", {})

    if overall:
        lines.append("## Overall")
        lines.append("")
        lines.append("| N | W-L | WR | Profit | ROI | Avg odds | Avg score | Avg overall ELO diff | Avg surface ELO diff |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        lines.append(
            f"| {overall.get('n', 0)} | {overall.get('wins', 0)}-{overall.get('losses', 0)} | "
            f"{overall.get('win_rate', 0)}% | {overall.get('profit', 0)}u | "
            f"{overall.get('roi', 0)}% | {overall.get('avg_odds', 0)} | "
            f"{overall.get('avg_abs_combined_score', 0)} | "
            f"{overall.get('avg_abs_overall_elo_diff', 0)} | "
            f"{overall.get('avg_abs_surface_elo_diff', 0)} |"
        )
        lines.append("")

    lines.append("## Buckets")
    lines.append("")
    lines.append("| Bucket | N | W-L | WR | Profit | ROI | Avg odds | Avg score |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, s in report["stats"].items():
        if key == "overall":
            continue

        lines.append(
            f"| {key} | {s['n']} | {s['wins']}-{s['losses']} | {s['win_rate']}% | "
            f"{s['profit']}u | {s['roi']}% | {s['avg_odds']} | {s['avg_abs_combined_score']} |"
        )

    lines.append("")
    lines.append("## Picks")
    lines.append("")
    lines.append("| Date | Match | Pick | Odds | Result | Profit | Score | ELO diff | Surface diff |")
    lines.append("|---|---|---|---:|---|---:|---:|---:|---:|")

    for r in report["rows"][:250]:
        elo = r.get("elo", {})
        lines.append(
            f"| {r.get('date')} | {r.get('match')} | {r.get('pick')} | {r.get('odds')} | "
            f"{r.get('result')} | {r.get('profit')} | {r.get('combined_score')} | "
            f"{elo.get('overall_elo_diff')} | {elo.get('surface_elo_diff')} |"
        )

    return "\n".join(lines)


def main():
    rows, missing, meta = collect_rows()
    stats = analyse_rows(rows)

    report = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "api": "api-tennis",
        "settings": {
            "target_days_back": TARGET_DAYS_BACK,
            "form_days_back": FORM_DAYS_BACK,
            "form_last_n_1": FORM_LAST_N_1,
            "form_last_n_2": FORM_LAST_N_2,
            "min_abs_combined_score": MIN_ABS_COMBINED_SCORE,
            "combined_score_formula": "0.75 * elo_score + 0.25 * form_score",
            "elo_score_formula": "surface/overall weighted diff capped by 250",
        },
        "meta": meta,
        "stats": stats,
        "rows": rows,
    }

    missing_report = {
        "generated_at": report["generated_at"],
        "meta": meta,
        "missing": missing,
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_MISSING_FILE, missing_report)
    save_text(OUTPUT_TABLE_FILE, build_table(report))

    print("")
    print("ELO + FORM + MARKET BACKTEST DONE")
    print(f"Rows:      {len(rows)}")
    print(f"Missing:   {len(missing)}")
    print(f"Report:    {OUTPUT_REPORT_FILE}")
    print(f"Missing:   {OUTPUT_MISSING_FILE}")
    print(f"Table:     {OUTPUT_TABLE_FILE}")
    print("")

    overall = stats.get("overall", {})
    print("Overall:")
    print(overall)
    print("")


if __name__ == "__main__":
    main()

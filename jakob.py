import os
import json
import time
import math
import hashlib
import re
from statistics import median
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"

PREDICTIONS_FILE = f"{DATA_DIR}/jakob_predictions.json"
RESULTS_FILE = f"{DATA_DIR}/jakob_results.json"
DEBUG_FILE = f"{DATA_DIR}/jakob_debug.json"
RANKED_FILE = f"{DATA_DIR}/jakob_ranked_candidates.json"
PLAY_FILE = f"{DATA_DIR}/jakob_play_picks.json"

MODEL_VERSION = "jakob_tennis_totals_profile_v2"
MODEL_NAME = "Jakob Tennis Totals Profile Model v2"
MARKET_NAME = "Over/Under by Games in Match"

DAYS_AHEAD = 1
MAX_FIXTURES = 650
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.30

MAX_PICKS = 20
MAX_RANKED_SAVE = 300

MAX_OVER_PICKS = 8
MAX_UNDER_PICKS = 18

MIN_RECENT_MATCHES_EACH = 6
MIN_BOOKMAKERS = 3
MIN_EDGE = 0.055
MIN_CONFIDENCE = 68.0

ODDS_MIN = 1.65
ODDS_MAX = 2.20

MODEL_PROB_MIN = 0.43
MODEL_PROB_MAX = 0.62

MAIN_LINES_MIN = 18.5
MAIN_LINES_MAX = 24.5

MIN_JAKOB_SCORE_FOR_FINAL = 70.0
MAX_UNDER_18_5_FINAL = 3
MAX_LOW_UNDER_FINAL = 12


JAKOB_FORMULA = {
    "w_confidence": 15.319894178503324,
    "w_quality": 14.049749201315652,
    "w_edge": 14.77458595147632,
    "w_abs_margin": 9.47908583098798,
    "w_bookmakers": 7.551207891650762,
    "w_market_gap": 24.22852983564232,
    "w_avg_three": 9.005132468013311,
    "w_avg_close": -3.87639699678569,
    "w_min_recent": 8.024444469152819,
    "p_h2h": 0.4342811456501652,
    "p_strength_gap_high": -0.4403355549604271,
    "p_strength_gap_low": 0.46041939402701537,
    "p_odds_high": 1.2905056111699116,
    "p_low_line_under": 3.668771925125693,
    "p_qualification": 7.3848412819228795,
    "b_over": -2.269957818592272,
    "b_under": 0.8695297448767523,
}


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


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


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


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


def fetch_fixtures_for_date(date_value):
    date_s = date_value.strftime("%Y-%m-%d")
    data = api_call({
        "method": "get_fixtures",
        "date_start": date_s,
        "date_stop": date_s,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return []

    result = data.get("result") or []
    return result if isinstance(result, list) else []


def fetch_odds(event_key):
    data = api_call({
        "method": "get_odds",
        "event_key": event_key,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return {}

    result = data.get("result") or {}
    return result.get(str(event_key)) or result.get(int(event_key)) or {}


def fetch_h2h(first_player_key, second_player_key):
    data = api_call({
        "method": "get_H2H",
        "first_player_key": first_player_key,
        "second_player_key": second_player_key,
    })
    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return {}

    return data.get("result") or {}


def is_pregame(match):
    status = str(match.get("event_status") or "").lower()
    live = str(match.get("event_live") or "0")

    if live == "1":
        return False

    bad_statuses = {
        "finished",
        "cancelled",
        "postponed",
        "retired",
        "walkover",
        "interrupted",
    }

    if status in bad_statuses:
        return False

    return True


def is_singles(match):
    event_type = str(match.get("event_type_type") or "").lower()
    p1 = str(match.get("event_first_player") or "")
    p2 = str(match.get("event_second_player") or "")

    if "/" in p1 or "/" in p2:
        return False

    if "doubles" in event_type:
        return False

    return "singles" in event_type


def tour_level(event_type):
    e = str(event_type or "").lower()

    if "atp" in e:
        return "atp"
    if "wta" in e:
        return "wta"
    if "challenger" in e:
        return "challenger"
    if "itf" in e:
        return "itf"

    return "unknown"


def gender_from_event_type(event_type):
    e = str(event_type or "").lower()

    if "women" in e or "wta" in e:
        return "women"
    if "men" in e or "atp" in e:
        return "men"

    return "unknown"


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


def total_games_from_scores(scores):
    parsed = parse_scores(scores)
    return sum(a + b for a, b in parsed)


def sets_count(scores):
    return len(parse_scores(scores))


def close_sets_count(scores):
    count = 0

    for a, b in parse_scores(scores):
        if max(a, b) >= 6 and abs(a - b) <= 2:
            count += 1

    return count


def match_winner_side(match):
    winner = str(match.get("event_winner") or "").lower()

    if "first" in winner:
        return "first"
    if "second" in winner:
        return "second"

    final_result = str(match.get("event_final_result") or "")
    parts = final_result.replace(" ", "").split("-")

    if len(parts) == 2:
        try:
            a, b = int(parts[0]), int(parts[1])
            if a > b:
                return "first"
            if b > a:
                return "second"
        except Exception:
            pass

    return None


def player_won(match, player_key):
    player_key = safe_int(player_key)
    first = safe_int(match.get("first_player_key"))
    second = safe_int(match.get("second_player_key"))
    winner = match_winner_side(match)

    if winner == "first" and first == player_key:
        return True
    if winner == "second" and second == player_key:
        return True
    if winner in {"first", "second"}:
        return False

    return None


def game_diff_for_player(match, player_key):
    player_key = safe_int(player_key)
    first = safe_int(match.get("first_player_key"))
    second = safe_int(match.get("second_player_key"))

    diff = 0

    for a, b in parse_scores(match.get("scores")):
        diff += a - b

    if second == player_key:
        diff *= -1

    if first != player_key and second != player_key:
        return 0

    return diff


def set_diff_for_player(match, player_key):
    player_key = safe_int(player_key)
    first = safe_int(match.get("first_player_key"))
    second = safe_int(match.get("second_player_key"))

    diff = 0

    for a, b in parse_scores(match.get("scores")):
        if a > b:
            diff += 1
        elif b > a:
            diff -= 1

    if second == player_key:
        diff *= -1

    if first != player_key and second != player_key:
        return 0

    return diff


def clean_finished_matches(matches):
    out = []

    for m in matches or []:
        if str(m.get("event_status") or "").lower() != "finished":
            continue

        parsed = parse_scores(m.get("scores"))

        if not parsed:
            continue

        if len(parsed) < 2 or len(parsed) > 3:
            continue

        total = sum(a + b for a, b in parsed)

        if total < 12 or total > 39:
            continue

        bad_set = False

        for a, b in parsed:
            if a < 0 or b < 0:
                bad_set = True
            if max(a, b) > 13:
                bad_set = True

        if bad_set:
            continue

        out.append(m)

    return out


def form_totals(matches, player_key):
    matches = clean_finished_matches(matches)

    matches = sorted(
        matches,
        key=lambda x: (x.get("event_date") or "", x.get("event_time") or ""),
        reverse=True,
    )

    recent = matches[:20]

    def window_stats(n):
        arr = recent[:n]

        if not arr:
            return {
                "matches": 0,
                "avg_total_games": 0.0,
                "median_total_games": 0.0,
                "over_21_5_rate": 0.0,
                "over_22_5_rate": 0.0,
                "three_set_rate": 0.0,
                "straight_set_rate": 0.0,
                "close_set_rate": 0.0,
                "avg_set_diff": 0.0,
                "avg_game_diff": 0.0,
                "win_rate": 0.0,
            }

        totals = [total_games_from_scores(m.get("scores")) for m in arr]
        three_sets = [1 if sets_count(m.get("scores")) >= 3 else 0 for m in arr]
        close_sets = [
            close_sets_count(m.get("scores")) / max(1, sets_count(m.get("scores")))
            for m in arr
        ]
        wins = [1 if player_won(m, player_key) is True else 0 for m in arr]
        set_diffs = [set_diff_for_player(m, player_key) for m in arr]
        game_diffs = [game_diff_for_player(m, player_key) for m in arr]

        return {
            "matches": len(arr),
            "avg_total_games": round(sum(totals) / len(totals), 2),
            "median_total_games": round(median(totals), 2),
            "over_21_5_rate": round(sum(1 for x in totals if x > 21.5) / len(totals), 4),
            "over_22_5_rate": round(sum(1 for x in totals if x > 22.5) / len(totals), 4),
            "three_set_rate": round(sum(three_sets) / len(three_sets), 4),
            "straight_set_rate": round(1 - (sum(three_sets) / len(three_sets)), 4),
            "close_set_rate": round(sum(close_sets) / len(close_sets), 4),
            "avg_set_diff": round(sum(set_diffs) / len(set_diffs), 3),
            "avg_game_diff": round(sum(game_diffs) / len(game_diffs), 3),
            "win_rate": round(sum(wins) / len(wins), 4),
        }

    return {
        "last_5": window_stats(5),
        "last_10": window_stats(10),
        "last_20": window_stats(20),
    }


def player_strength_score(form):
    l10 = form.get("last_10", {})

    win_rate = safe_float(l10.get("win_rate"))
    game_diff = safe_float(l10.get("avg_game_diff"))
    set_diff = safe_float(l10.get("avg_set_diff"))

    score = 50
    score += (win_rate - 0.5) * 45
    score += clamp(game_diff, -6, 6) * 3
    score += clamp(set_diff, -1.8, 1.8) * 7

    return round(clamp(score, 1, 99), 2)


def extract_home_away_odds(odds_blob):
    market = odds_blob.get("Home/Away")

    if not isinstance(market, dict):
        return None

    home_books = market.get("Home") or {}
    away_books = market.get("Away") or {}

    if not isinstance(home_books, dict) or not isinstance(away_books, dict):
        return None

    home_odds = [safe_float(v) for v in home_books.values() if safe_float(v) > 1]
    away_odds = [safe_float(v) for v in away_books.values() if safe_float(v) > 1]

    if not home_odds or not away_odds:
        return None

    h = median(home_odds)
    a = median(away_odds)

    return {
        "home_median_odds": round(h, 3),
        "away_median_odds": round(a, 3),
        "home_implied": round(1 / h, 4),
        "away_implied": round(1 / a, 4),
        "market_gap": round(abs((1 / h) - (1 / a)), 4),
        "market_favorite_side": "home" if h < a else "away",
    }


def normalize_line_key(v):
    n = safe_float(v, None)

    if n is None:
        return None

    return f"{n:.1f}"


def extract_line_from_text(text):
    s = str(text or "")
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)", s)

    if not m:
        return None

    return safe_float(m.group(1).replace(",", "."), None)


def normalize_side_from_text(text):
    s = str(text or "").lower()

    if "over" in s:
        return "over"
    if "under" in s:
        return "under"

    return None


def collect_books_from_any_shape(obj):
    out = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            odd = safe_float(v, None)

            if odd is not None and odd > 1:
                out[str(k)] = odd
                continue

            if isinstance(v, dict):
                bookmaker = (
                    v.get("bookmaker")
                    or v.get("bookmaker_name")
                    or v.get("bookmaker_key")
                    or k
                )

                odd_val = (
                    v.get("odd")
                    or v.get("odds")
                    or v.get("value")
                    or v.get("price")
                )

                odd = safe_float(odd_val, None)

                if bookmaker and odd is not None and odd > 1:
                    out[str(bookmaker)] = odd

    elif isinstance(obj, list):
        for item in obj:
            if not isinstance(item, dict):
                continue

            bookmaker = (
                item.get("bookmaker")
                or item.get("bookmaker_name")
                or item.get("bookmaker_key")
                or item.get("name")
            )

            odd_val = (
                item.get("odd")
                or item.get("odds")
                or item.get("value")
                or item.get("price")
            )

            odd = safe_float(odd_val, None)

            if bookmaker and odd is not None and odd > 1:
                out[str(bookmaker)] = odd

    return out


def parse_totals_market(odds_blob):
    market = odds_blob.get(MARKET_NAME)

    if not isinstance(market, dict):
        return []

    by_line = {}

    def add_side_books(line, side, books):
        line_key = normalize_line_key(line)

        if not line_key or side not in {"over", "under"}:
            return

        line_float = safe_float(line_key, None)

        if line_float is None:
            return

        if not (MAIN_LINES_MIN <= line_float <= MAIN_LINES_MAX):
            return

        clean_books = {
            str(book): safe_float(odd)
            for book, odd in (books or {}).items()
            if safe_float(odd) > 1
        }

        if not clean_books:
            return

        by_line.setdefault(line_key, {"line": line_float, "over": {}, "under": {}})
        by_line[line_key][side].update(clean_books)

    over_key = f"{MARKET_NAME} Over"
    under_key = f"{MARKET_NAME} Under"

    over_data = market.get(over_key)
    under_data = market.get(under_key)

    if isinstance(over_data, dict):
        for line_s, over_books in over_data.items():
            add_side_books(line_s, "over", collect_books_from_any_shape(over_books))

    if isinstance(under_data, dict):
        for line_s, under_books in under_data.items():
            add_side_books(line_s, "under", collect_books_from_any_shape(under_books))

    for side_key in ["Over", "Under", "over", "under"]:
        data = market.get(side_key)
        side = normalize_side_from_text(side_key)

        if isinstance(data, dict) and side:
            for line_s, books in data.items():
                add_side_books(line_s, side, collect_books_from_any_shape(books))

    for key, value in market.items():
        side = normalize_side_from_text(key)
        line = extract_line_from_text(key)

        if side and line is not None:
            add_side_books(line, side, collect_books_from_any_shape(value))

    for key, value in market.items():
        line = extract_line_from_text(key)

        if line is None or not isinstance(value, dict):
            continue

        for sub_key, sub_value in value.items():
            side = normalize_side_from_text(sub_key)

            if side:
                add_side_books(line, side, collect_books_from_any_shape(sub_value))

    candidates = []

    for line_key, item in by_line.items():
        over_odds_values = item.get("over") or {}
        under_odds_values = item.get("under") or {}

        shared_books = sorted(set(over_odds_values) & set(under_odds_values))
        books_used = len(shared_books)

        if books_used < MIN_BOOKMAKERS:
            continue

        over_shared = [
            over_odds_values[b]
            for b in shared_books
            if over_odds_values[b] > 1
        ]

        under_shared = [
            under_odds_values[b]
            for b in shared_books
            if under_odds_values[b] > 1
        ]

        if not over_shared or not under_shared:
            continue

        over_best_book = max(shared_books, key=lambda b: over_odds_values[b])
        under_best_book = max(shared_books, key=lambda b: under_odds_values[b])

        candidates.append({
            "line": item["line"],
            "bookmakers_used": books_used,
            "over": {
                "best_odds": round(over_odds_values[over_best_book], 3),
                "best_bookmaker": over_best_book,
                "median_odds": round(median(over_shared), 3),
            },
            "under": {
                "best_odds": round(under_odds_values[under_best_book], 3),
                "best_bookmaker": under_best_book,
                "median_odds": round(median(under_shared), 3),
            },
        })

    candidates.sort(key=lambda x: safe_float(x.get("line")))
    return candidates


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def expected_total_games(player_form, opponent_form, h2h_matches, market_info):
    p5 = player_form["last_5"]
    p10 = player_form["last_10"]
    o5 = opponent_form["last_5"]
    o10 = opponent_form["last_10"]

    p10_total = safe_float(p10.get("median_total_games")) * 0.65 + safe_float(p10.get("avg_total_games")) * 0.35
    o10_total = safe_float(o10.get("median_total_games")) * 0.65 + safe_float(o10.get("avg_total_games")) * 0.35

    p5_total = safe_float(p5.get("median_total_games")) * 0.60 + safe_float(p5.get("avg_total_games")) * 0.40
    o5_total = safe_float(o5.get("median_total_games")) * 0.60 + safe_float(o5.get("avg_total_games")) * 0.40

    avg_recent = (
        p10_total * 0.34
        + o10_total * 0.34
        + p5_total * 0.16
        + o5_total * 0.16
    )

    three_set_rate = (
        safe_float(p10.get("three_set_rate"))
        + safe_float(o10.get("three_set_rate"))
    ) / 2

    close_set_rate = (
        safe_float(p10.get("close_set_rate"))
        + safe_float(o10.get("close_set_rate"))
    ) / 2

    p_strength = player_strength_score(player_form)
    o_strength = player_strength_score(opponent_form)
    strength_gap = abs(p_strength - o_strength)

    exp = avg_recent

    exp += (three_set_rate - 0.28) * 4.2
    exp += (close_set_rate - 0.36) * 2.8

    if strength_gap >= 30:
        exp -= 2.0
    elif strength_gap >= 22:
        exp -= 1.25
    elif strength_gap <= 8:
        exp += 1.0

    if market_info:
        gap = safe_float(market_info.get("market_gap"))

        if gap >= 0.55:
            exp -= 2.8
        elif gap >= 0.40:
            exp -= 2.2
        elif gap >= 0.26:
            exp -= 1.6
        elif gap >= 0.18:
            exp -= 1.0
        elif gap <= 0.08:
            exp += 0.8

    h2h_finished = clean_finished_matches(h2h_matches)

    if h2h_finished:
        h2h_totals = [
            total_games_from_scores(m.get("scores"))
            for m in h2h_finished[:5]
        ]

        h2h_avg = sum(h2h_totals) / len(h2h_totals)
        exp = exp * 0.85 + h2h_avg * 0.15

    return round(clamp(exp, 16.5, 29.5), 2)


def model_probability(expected_games, line, side):
    diff = expected_games - line

    p_over = sigmoid(diff / 2.9)
    p_over = clamp(p_over, MODEL_PROB_MIN, MODEL_PROB_MAX)

    if side == "over":
        return round(p_over, 4)

    return round(1 - p_over, 4)


def confidence_score(expected_games, line, model_prob, bookmakers_used, odds):
    margin = abs(expected_games - line)

    c = 50
    c += clamp(margin / 3.0, 0, 1) * 22
    c += clamp((model_prob - 0.5) / 0.12, 0, 1) * 16
    c += clamp(bookmakers_used / 10, 0, 1) * 8

    if 1.72 <= odds <= 2.05:
        c += 4
    elif 1.65 <= odds <= 2.15:
        c += 2

    return round(clamp(c, 1, 96), 1)


def quality_score(confidence, edge, bookmakers_used, odds, matches_min, margin):
    q = 0

    q += clamp(confidence / 90, 0, 1) * 30
    q += clamp(edge / 0.11, 0, 1) * 30
    q += clamp(bookmakers_used / 10, 0, 1) * 14
    q += clamp(matches_min / 14, 0, 1) * 12
    q += clamp(margin / 3.0, 0, 1) * 9

    if 1.72 <= odds <= 2.05:
        q += 5
    elif 1.65 <= odds <= 2.20:
        q += 3

    return round(clamp(q, 1, 99), 1)


def pick_id_for(event_key, side, line):
    raw = f"{MODEL_VERSION}:{event_key}:{side}:{line}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def rank_tier_for_rank(rank):
    if rank <= 50:
        return "elite", 0.75
    if rank <= 100:
        return "premium", 0.50
    return "value", 0.25


def market_gap_profile_value(side, line, market_gap):
    side = str(side or "").lower()
    line = safe_float(line)
    market_gap = safe_float(market_gap)

    if side == "under":
        if market_gap <= 0:
            return 0.0

        if market_gap <= 0.35:
            return market_gap / 0.35 * 0.55

        if market_gap <= 0.65:
            return 0.55 + ((market_gap - 0.35) / 0.30) * 0.35

        if market_gap <= 0.78:
            return 0.90 + ((market_gap - 0.65) / 0.13) * 0.08

        if line <= 19.5:
            return 0.82

        return 0.95

    if side == "over":
        if market_gap <= 0.08:
            return 1.0
        if market_gap <= 0.20:
            return 0.75
        if market_gap <= 0.35:
            return 0.45
        if market_gap <= 0.55:
            return 0.20
        return 0.05

    return clamp(market_gap / 0.80, 0, 1)


def jakob_profile_score(pick):
    f = JAKOB_FORMULA

    confidence = safe_float(pick.get("confidence"))
    quality = safe_float(pick.get("quality_score"))
    edge = safe_float(pick.get("edge"))
    margin = abs(safe_float(pick.get("expected_margin")))
    bookmakers = safe_float(pick.get("bookmakers_used"))
    odds = safe_float(pick.get("odds"))
    side = str(pick.get("side") or "").lower()
    line = safe_float(pick.get("line"))

    market_gap = safe_float((pick.get("market_info") or {}).get("market_gap"))

    first_form = pick.get("first_form") or {}
    second_form = pick.get("second_form") or {}

    f10 = first_form.get("last_10") or {}
    s10 = second_form.get("last_10") or {}

    avg_three = (
        safe_float(f10.get("three_set_rate"))
        + safe_float(s10.get("three_set_rate"))
    ) / 2

    avg_close = (
        safe_float(f10.get("close_set_rate"))
        + safe_float(s10.get("close_set_rate"))
    ) / 2

    min_recent = min(
        safe_int(f10.get("matches")),
        safe_int(s10.get("matches")),
    )

    strength_gap = abs(
        safe_float(pick.get("first_strength_score"))
        - safe_float(pick.get("second_strength_score"))
    )

    h2h_matches = safe_int(pick.get("h2h_matches"))
    qualification = bool(pick.get("qualification"))

    market_value = market_gap_profile_value(side, line, market_gap)

    score = 0.0

    score += f["w_confidence"] * clamp(confidence / 96.0, 0, 1)
    score += f["w_quality"] * clamp(quality / 99.0, 0, 1)
    score += f["w_edge"] * clamp(edge / 0.16, 0, 1)
    score += f["w_abs_margin"] * clamp(margin / 5.0, 0, 1)
    score += f["w_bookmakers"] * clamp(bookmakers / 10.0, 0, 1)
    score += f["w_market_gap"] * market_value
    score += f["w_avg_three"] * clamp(avg_three / 0.60, 0, 1)
    score += f["w_avg_close"] * clamp(avg_close / 0.80, 0, 1)
    score += f["w_min_recent"] * clamp(min_recent / 20.0, 0, 1)

    if h2h_matches > 0:
        score += f["p_h2h"]

    if strength_gap >= 22:
        score += f["p_strength_gap_high"]

    if strength_gap <= 8:
        score += f["p_strength_gap_low"]

    if odds >= 2.05:
        score += f["p_odds_high"]

    if side == "under" and line <= 20.5:
        score += f["p_low_line_under"]

    if qualification:
        score += f["p_qualification"]

    if side == "over":
        score += f["b_over"]

    if side == "under":
        score += f["b_under"]

    # Popravek v2:
    # Market gap za UNDER je dober, ampak ne sme slepo zmagati.
    # Over pri velikem favoritu dobi kazen.
    if side == "under":
        if line <= 18.5 and margin < 1.75:
            score -= 4.0

        if line <= 19.5 and margin < 1.25:
            score -= 2.5

        if line <= 19.5 and market_gap < 0.25:
            score -= 2.0

        if market_gap >= 0.78 and line <= 19.5:
            score -= 1.5

        if 0.35 <= market_gap <= 0.70:
            score += 1.25

    if side == "over":
        if market_gap >= 0.55:
            score -= 5.0
        elif market_gap >= 0.40:
            score -= 3.0
        elif market_gap <= 0.10:
            score += 1.5

        if line <= 20.5 and margin < 2.0:
            score -= 2.0

    # Guardrails proti fake lepim številkam.
    if edge > 0.155:
        score -= 2.0

    if bookmakers < 5:
        score -= 2.0

    if odds > 2.18:
        score -= 1.0

    if min_recent < 8:
        score -= 1.0

    if confidence < 72:
        score -= 1.0

    return round(score, 8)


def build_reasoning(pick):
    return (
        f"{pick['bet']} selected in {pick['match']} at line {pick['line']:.1f}. "
        f"Jakob profile score: {pick['jakob_score']:.2f}. "
        f"Model expected total games: {pick['expected_total_games']:.2f}; "
        f"market line: {pick['line']:.1f}. "
        f"Model probability {pick['model_prob'] * 100:.1f}% versus implied "
        f"{pick['implied_prob'] * 100:.1f}% from best odds {pick['odds']:.2f}. "
        f"Edge: {pick['edge'] * 100:+.1f}%. "
        f"Bookmakers used: {pick['bookmakers_used']}. "
        f"Confidence: {pick['confidence']:.1f}. "
        f"Quality: {pick['quality_score']:.1f}."
    )


def make_play_pick(pick):
    market_info = pick.get("market_info") or {}

    return {
        "rank": pick.get("rank"),
        "tier": pick.get("rank_tier"),
        "stake": pick.get("stake"),
        "date": pick.get("date"),
        "time": pick.get("time"),
        "match": pick.get("match"),
        "pick": pick.get("bet"),
        "side": pick.get("side"),
        "line": pick.get("line"),
        "odds": pick.get("odds"),
        "bookmaker": pick.get("best_bookmaker"),
        "tournament": pick.get("tournament"),
        "event_type": pick.get("event_type"),
        "jakob_score": pick.get("jakob_score"),
        "confidence": pick.get("confidence"),
        "quality_score": pick.get("quality_score"),
        "edge_percent": round(safe_float(pick.get("edge")) * 100, 2),
        "model_prob_percent": round(safe_float(pick.get("model_prob")) * 100, 2),
        "implied_prob_percent": round(safe_float(pick.get("implied_prob")) * 100, 2),
        "expected_total_games": pick.get("expected_total_games"),
        "expected_margin": pick.get("expected_margin"),
        "bookmakers_used": pick.get("bookmakers_used"),
        "market_gap": market_info.get("market_gap"),
        "strength_gap": pick.get("strength_gap"),
        "h2h_matches": pick.get("h2h_matches"),
        "reasoning": pick.get("reasoning"),
    }


def main():
    ensure_dirs()

    old_results = load_json(RESULTS_FILE, [])

    if not isinstance(old_results, list):
        old_results = []

    existing_by_id = {
        x.get("pick_id"): x
        for x in old_results
        if isinstance(x, dict) and x.get("pick_id")
    }

    fixtures = []
    start = today_local()

    for i in range(DAYS_AHEAD):
        day = start + timedelta(days=i)
        daily = fetch_fixtures_for_date(day)
        print(f"FIXTURES {day}: {len(daily)}")
        fixtures.extend(daily)

    fixtures = fixtures[:MAX_FIXTURES]

    candidates = []

    debug = {
        "generated_at": now_iso(),
        "model": MODEL_NAME,
        "fixtures_total": len(fixtures),
        "scanned": 0,
        "skipped": [],
        "candidates_raw": 0,
        "ranked_candidates": 0,
        "final_picks": 0,
        "errors": [],
        "formula": JAKOB_FORMULA,
        "notes": {
            "v2": "Market gap is direction-aware. Under gets capped bonus. Over gets high-gap penalty.",
            "play_file": PLAY_FILE,
        },
    }

    h2h_cache = {}

    for match in fixtures:
        event_key = match.get("event_key")
        name = f"{match.get('event_first_player')} - {match.get('event_second_player')}"

        if not event_key:
            continue

        if not is_pregame(match):
            debug["skipped"].append({
                "event_key": event_key,
                "match": name,
                "reason": "not_pregame",
            })
            continue

        if not is_singles(match):
            debug["skipped"].append({
                "event_key": event_key,
                "match": name,
                "reason": "not_singles",
            })
            continue

        first_key = match.get("first_player_key")
        second_key = match.get("second_player_key")

        if not first_key or not second_key:
            debug["skipped"].append({
                "event_key": event_key,
                "match": name,
                "reason": "missing_player_key",
            })
            continue

        try:
            debug["scanned"] += 1

            odds_blob = fetch_odds(event_key)

            if not odds_blob:
                debug["skipped"].append({
                    "event_key": event_key,
                    "match": name,
                    "reason": "no_odds",
                })
                continue

            totals_lines = parse_totals_market(odds_blob)

            if not totals_lines:
                market_preview = None

                try:
                    m = odds_blob.get(MARKET_NAME) if isinstance(odds_blob, dict) else None
                    market_preview = json.dumps(m, ensure_ascii=False)[:2500] if m is not None else None
                except Exception:
                    market_preview = str(odds_blob.get(MARKET_NAME))[:2500] if isinstance(odds_blob, dict) else None

                debug["skipped"].append({
                    "event_key": event_key,
                    "match": name,
                    "reason": "no_totals_market",
                    "available_markets": list(odds_blob.keys())[:30] if isinstance(odds_blob, dict) else [],
                    "totals_market_preview": market_preview,
                })
                continue

            cache_key = (first_key, second_key)

            if cache_key not in h2h_cache:
                h2h_cache[cache_key] = fetch_h2h(first_key, second_key)

            h2h = h2h_cache[cache_key]

            first_results = h2h.get("firstPlayerResults") or []
            second_results = h2h.get("secondPlayerResults") or []
            h2h_matches = h2h.get("H2H") or []

            first_form = form_totals(first_results, first_key)
            second_form = form_totals(second_results, second_key)

            first_n = safe_int(first_form["last_10"].get("matches"))
            second_n = safe_int(second_form["last_10"].get("matches"))
            matches_min = min(first_n, second_n)

            if matches_min < MIN_RECENT_MATCHES_EACH:
                debug["skipped"].append({
                    "event_key": event_key,
                    "match": name,
                    "reason": "not_enough_recent_matches",
                    "first_matches": first_n,
                    "second_matches": second_n,
                })
                continue

            market_info = extract_home_away_odds(odds_blob)

            exp_games = expected_total_games(
                first_form,
                second_form,
                h2h_matches,
                market_info,
            )

            first_strength = player_strength_score(first_form)
            second_strength = player_strength_score(second_form)

            for line_info in totals_lines:
                line = safe_float(line_info.get("line"))
                bookmakers_used = safe_int(line_info.get("bookmakers_used"))

                for side in ["over", "under"]:
                    side_info = line_info.get(side) or {}

                    odds = safe_float(side_info.get("best_odds"))
                    median_odds = safe_float(side_info.get("median_odds"))
                    bookmaker = side_info.get("best_bookmaker") or "unknown"

                    if odds < ODDS_MIN or odds > ODDS_MAX:
                        continue

                    model_prob = model_probability(exp_games, line, side)
                    implied_prob = 1 / odds
                    edge = model_prob - implied_prob
                    margin = abs(exp_games - line)

                    if market_info:
                        market_gap = safe_float(market_info.get("market_gap"))

                        if side == "over" and line <= 19.5 and market_gap >= 0.55:
                            continue

                    if edge < MIN_EDGE:
                        continue

                    confidence = confidence_score(
                        exp_games,
                        line,
                        model_prob,
                        bookmakers_used,
                        odds,
                    )

                    if confidence < MIN_CONFIDENCE:
                        continue

                    quality = quality_score(
                        confidence,
                        edge,
                        bookmakers_used,
                        odds,
                        matches_min,
                        margin,
                    )

                    pick = {
                        "pick_id": pick_id_for(event_key, side, line),
                        "event_key": event_key,
                        "fixture_id": event_key,
                        "sport": "tennis",
                        "model_version": MODEL_VERSION,
                        "model_name": MODEL_NAME,
                        "date": match.get("event_date"),
                        "time": match.get("event_time"),
                        "match": name,
                        "bet": f"{side.upper()} {line:.1f} games",
                        "bucket": "total_games",
                        "side": side,
                        "market": MARKET_NAME,
                        "line": line,
                        "first_player_key": safe_int(first_key),
                        "second_player_key": safe_int(second_key),
                        "first_player_name": match.get("event_first_player"),
                        "second_player_name": match.get("event_second_player"),
                        "tournament": match.get("tournament_name"),
                        "tournament_key": match.get("tournament_key"),
                        "round": match.get("tournament_round"),
                        "event_type": match.get("event_type_type"),
                        "qualification": str(match.get("event_qualification") or "").lower() == "true",
                        "tour_level": tour_level(match.get("event_type_type")),
                        "gender": gender_from_event_type(match.get("event_type_type")),
                        "odds": round(odds, 3),
                        "best_bookmaker": bookmaker,
                        "market_median_odds": round(median_odds, 3),
                        "bookmakers_used": bookmakers_used,
                        "model_prob": model_prob,
                        "implied_prob": round(implied_prob, 4),
                        "edge": round(edge, 4),
                        "expected_total_games": exp_games,
                        "expected_margin": round(exp_games - line, 3),
                        "confidence": confidence,
                        "quality_score": quality,
                        "market_info": market_info,
                        "first_form": first_form,
                        "second_form": second_form,
                        "first_strength_score": first_strength,
                        "second_strength_score": second_strength,
                        "strength_gap": round(abs(first_strength - second_strength), 3),
                        "h2h_matches": len(clean_finished_matches(h2h_matches)),
                        "result": "pending",
                        "created_at": now_iso(),
                    }

                    pick["jakob_score"] = jakob_profile_score(pick)
                    candidates.append(pick)

        except Exception as e:
            debug["errors"].append({
                "event_key": event_key,
                "match": name,
                "error": str(e),
            })
            print(f"ERROR {event_key} {name}: {e}")

    debug["candidates_raw"] = len(candidates)

    candidates.sort(
        key=lambda x: (
            safe_float(x.get("jakob_score")),
            safe_float(x.get("quality_score")),
            safe_float(x.get("edge")),
            safe_float(x.get("confidence")),
        ),
        reverse=True,
    )

    ranked = []
    used_ranked_events = set()

    for pick in candidates:
        if pick["event_key"] in used_ranked_events:
            continue

        rank = len(ranked) + 1
        tier, stake = rank_tier_for_rank(rank)

        pick["rank"] = rank
        pick["rank_tier"] = tier
        pick["stake"] = stake
        pick["stake_label"] = tier
        pick["reasoning"] = build_reasoning(pick)

        ranked.append(pick)
        used_ranked_events.add(pick["event_key"])

        if len(ranked) >= MAX_RANKED_SAVE:
            break

    debug["ranked_candidates"] = len(ranked)

    final = []
    over_count = 0
    under_count = 0
    under_18_5_count = 0
    low_under_count = 0

    for pick in ranked:
        score = safe_float(pick.get("jakob_score"))
        side = str(pick.get("side") or "").lower()
        line = safe_float(pick.get("line"))

        if score < MIN_JAKOB_SCORE_FOR_FINAL:
            continue

        if side == "over":
            if over_count >= MAX_OVER_PICKS:
                continue
            over_count += 1

        if side == "under":
            if under_count >= MAX_UNDER_PICKS:
                continue

            if line <= 18.5:
                if under_18_5_count >= MAX_UNDER_18_5_FINAL:
                    continue
                under_18_5_count += 1

            if line <= 20.5:
                if low_under_count >= MAX_LOW_UNDER_FINAL:
                    continue
                low_under_count += 1

            under_count += 1

        final.append(pick)

        if len(final) >= MAX_PICKS:
            break

    debug["final_picks"] = len(final)

    for pick in final:
        old = existing_by_id.get(pick["pick_id"])

        if old and str(old.get("result") or "pending").lower() != "pending":
            continue

        existing_by_id[pick["pick_id"]] = pick

    results = list(existing_by_id.values())
    results.sort(key=lambda x: (x.get("date") or "", x.get("time") or "", x.get("match") or ""))

    play_picks = [make_play_pick(p) for p in final]

    payload = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "stake_mode": "rank_tier_profile",
        "market": MARKET_NAME,
        "formula": JAKOB_FORMULA,
        "filters": {
            "days_ahead": DAYS_AHEAD,
            "max_fixtures": MAX_FIXTURES,
            "max_picks": MAX_PICKS,
            "max_ranked_save": MAX_RANKED_SAVE,
            "max_over_picks": MAX_OVER_PICKS,
            "max_under_picks": MAX_UNDER_PICKS,
            "max_under_18_5_final": MAX_UNDER_18_5_FINAL,
            "max_low_under_final": MAX_LOW_UNDER_FINAL,
            "min_jakob_score_for_final": MIN_JAKOB_SCORE_FOR_FINAL,
            "min_recent_matches_each": MIN_RECENT_MATCHES_EACH,
            "min_bookmakers": MIN_BOOKMAKERS,
            "min_edge": MIN_EDGE,
            "min_confidence": MIN_CONFIDENCE,
            "odds_min": ODDS_MIN,
            "odds_max": ODDS_MAX,
            "main_lines_min": MAIN_LINES_MIN,
            "main_lines_max": MAIN_LINES_MAX,
            "model_prob_min": MODEL_PROB_MIN,
            "model_prob_max": MODEL_PROB_MAX,
        },
        "summary": {
            "fixtures_checked": len(fixtures),
            "candidates_raw": len(candidates),
            "ranked_candidates": len(ranked),
            "final_picks": len(final),
            "errors": len(debug["errors"]),
        },
        "picks": final,
    }

    ranked_payload = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "formula": JAKOB_FORMULA,
        "summary": {
            "fixtures_checked": len(fixtures),
            "candidates_raw": len(candidates),
            "ranked_candidates": len(ranked),
        },
        "ranked_candidates": ranked,
    }

    play_payload = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "summary": {
            "final_picks": len(play_picks),
            "over_picks": sum(1 for p in play_picks if p.get("side") == "over"),
            "under_picks": sum(1 for p in play_picks if p.get("side") == "under"),
        },
        "picks_to_play": play_picks,
    }

    save_json(PREDICTIONS_FILE, payload)
    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)
    save_json(RANKED_FILE, ranked_payload)
    save_json(PLAY_FILE, play_payload)

    print("")
    print(
        f"JAKOB DONE: "
        f"candidates={len(candidates)} "
        f"ranked={len(ranked)} "
        f"final={len(final)} "
        f"results_total={len(results)}"
    )
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {DEBUG_FILE}")
    print(f"Saved {RANKED_FILE}")
    print(f"Saved {PLAY_FILE}")


if __name__ == "__main__":
    main()

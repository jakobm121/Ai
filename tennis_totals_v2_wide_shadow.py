import os
import json
import time
import math
import hashlib
from statistics import median
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_v2_wide_shadow_predictions.json"
RESULTS_FILE = f"{DATA_DIR}/tennis_totals_v2_wide_shadow_results.json"
DEBUG_FILE = f"{DATA_DIR}/tennis_totals_v2_wide_shadow_debug.json"
SNAPSHOT_FILE = f"{DATA_DIR}/tennis_totals_v2_wide_shadow_market_snapshots.json"

MODEL_VERSION = "ai77_tennis_totals_v2_wide_shadow"
MODEL_NAME = "AI77 Tennis Totals V2 Wide Shadow"
MARKET_NAME = "Over/Under by Games in Match"

DAYS_AHEAD = 1
MAX_FIXTURES = 650
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35

MAX_PICKS = 30
MAX_OVER_PICKS = 15
MAX_UNDER_PICKS = 15

MIN_RECENT_MATCHES_EACH = 6
MIN_BOOKMAKERS = 5
MIN_EDGE = 0.045
MIN_CONFIDENCE = 64.0

ODDS_MIN = 1.60
ODDS_MAX = 2.35

MODEL_PROB_MIN = 0.42
MODEL_PROB_MAX = 0.64

MAIN_LINES_MIN = 18.5
MAIN_LINES_MAX = 24.5

MAX_API_ERRORS_TO_SAVE = 12
MIN_FIXTURES_TO_SAVE = 50


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

    bad_statuses = {"finished", "cancelled", "postponed", "retired", "walkover", "interrupted"}
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
    return sum(a + b for a, b in parse_scores(scores))


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
    matches = sorted(matches, key=lambda x: (x.get("event_date") or "", x.get("event_time") or ""), reverse=True)
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
        close_sets = [close_sets_count(m.get("scores")) / max(1, sets_count(m.get("scores"))) for m in arr]
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


def extract_set_betting_info(odds_blob):
    possible_keys = [
        "Correct Score",
        "Set Betting",
        "Correct Set Score",
        "Set Score",
    ]

    market = None
    market_name = None
    for key in possible_keys:
        if isinstance(odds_blob.get(key), dict):
            market = odds_blob.get(key)
            market_name = key
            break

    if not isinstance(market, dict):
        return None

    straight_odds = []
    three_set_odds = []

    for outcome, books in market.items():
        outcome_s = str(outcome).lower().replace(" ", "")
        if not isinstance(books, dict):
            continue

        odds_values = [safe_float(v) for v in books.values() if safe_float(v) > 1]
        if not odds_values:
            continue

        med = median(odds_values)
        if any(x in outcome_s for x in ["2:0", "0:2", "2-0", "0-2", "20", "02"]):
            straight_odds.append(med)
        if any(x in outcome_s for x in ["2:1", "1:2", "2-1", "1-2", "21", "12"]):
            three_set_odds.append(med)

    if not straight_odds and not three_set_odds:
        return None

    straight_prob = sum((1 / x) for x in straight_odds) / len(straight_odds) if straight_odds else None
    three_set_prob = sum((1 / x) for x in three_set_odds) / len(three_set_odds) if three_set_odds else None

    return {
        "market_name": market_name,
        "straight_sets_median_odds": round(median(straight_odds), 3) if straight_odds else None,
        "three_sets_median_odds": round(median(three_set_odds), 3) if three_set_odds else None,
        "straight_sets_implied": round(straight_prob, 4) if straight_prob is not None else None,
        "three_sets_implied": round(three_set_prob, 4) if three_set_prob is not None else None,
        "straight_books": len(straight_odds),
        "three_set_books": len(three_set_odds),
    }


def parse_totals_market(odds_blob):
    market = odds_blob.get(MARKET_NAME)
    if not isinstance(market, dict):
        return []

    over_key = f"{MARKET_NAME} Over"
    under_key = f"{MARKET_NAME} Under"

    over_data = market.get(over_key) or {}
    under_data = market.get(under_key) or {}

    if not isinstance(over_data, dict) or not isinstance(under_data, dict):
        return []

    candidates = []

    for line_s, over_books in over_data.items():
        if line_s not in under_data:
            continue

        line = safe_float(line_s, None)
        if line is None:
            continue

        if not (MAIN_LINES_MIN <= line <= MAIN_LINES_MAX):
            continue

        under_books = under_data.get(line_s) or {}

        if not isinstance(over_books, dict) or not isinstance(under_books, dict):
            continue

        over_odds_values = {k: safe_float(v) for k, v in over_books.items() if safe_float(v) > 1}
        under_odds_values = {k: safe_float(v) for k, v in under_books.items() if safe_float(v) > 1}

        shared_books = sorted(set(over_odds_values) & set(under_odds_values))
        books_used = len(shared_books)

        if books_used < MIN_BOOKMAKERS:
            continue

        over_shared = [over_odds_values[b] for b in shared_books]
        under_shared = [under_odds_values[b] for b in shared_books]

        over_best_book = max(shared_books, key=lambda b: over_odds_values[b])
        under_best_book = max(shared_books, key=lambda b: under_odds_values[b])

        candidates.append({
            "line": line,
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
            }
        })

    return candidates


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def set_betting_adjustment(set_betting_info):
    if not set_betting_info:
        return 0.0

    straight_p = safe_float(set_betting_info.get("straight_sets_implied"), None)
    three_p = safe_float(set_betting_info.get("three_sets_implied"), None)

    if straight_p is None or three_p is None:
        return 0.0

    diff = three_p - straight_p

    if diff >= 0.12:
        return 1.05
    if diff >= 0.08:
        return 0.75
    if diff >= 0.04:
        return 0.40

    if diff <= -0.22:
        return -1.05
    if diff <= -0.16:
        return -0.75
    if diff <= -0.10:
        return -0.40

    return 0.0


def surface_proxy_adjustment(match):
    # API-Tennis pogosto nima čistega surface polja na fixtureju.
    # Zato je to previden proxy iz tournament/type stringa.
    text = " ".join(str(match.get(k) or "") for k in [
        "tournament_name", "event_type_type", "tournament_round"
    ]).lower()

    if "grass" in text:
        return 0.45, "grass_proxy"
    if "clay" in text or "roland" in text or "monte carlo" in text or "madrid" in text or "rome" in text:
        return -0.25, "clay_proxy"
    if "hard" in text or "indoor" in text:
        return 0.15, "hard_proxy"

    return 0.0, "unknown"


def expected_total_games(player_form, opponent_form, h2h_matches, market_info, set_betting_info=None, surface_adj=0.0):
    p5 = player_form["last_5"]
    p10 = player_form["last_10"]
    o5 = opponent_form["last_5"]
    o10 = opponent_form["last_10"]

    p10_total = safe_float(p10.get("median_total_games")) * 0.65 + safe_float(p10.get("avg_total_games")) * 0.35
    o10_total = safe_float(o10.get("median_total_games")) * 0.65 + safe_float(o10.get("avg_total_games")) * 0.35
    p5_total = safe_float(p5.get("median_total_games")) * 0.60 + safe_float(p5.get("avg_total_games")) * 0.40
    o5_total = safe_float(o5.get("median_total_games")) * 0.60 + safe_float(o5.get("avg_total_games")) * 0.40

    avg_recent = (
        p10_total * 0.34 +
        o10_total * 0.34 +
        p5_total * 0.16 +
        o5_total * 0.16
    )

    three_set_rate = (safe_float(p10.get("three_set_rate")) + safe_float(o10.get("three_set_rate"))) / 2
    close_set_rate = (safe_float(p10.get("close_set_rate")) + safe_float(o10.get("close_set_rate"))) / 2

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

    exp += set_betting_adjustment(set_betting_info)
    exp += surface_adj

    h2h_finished = clean_finished_matches(h2h_matches)
    if h2h_finished:
        h2h_totals = [total_games_from_scores(m.get("scores")) for m in h2h_finished[:5]]
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


def confidence_score(expected_games, line, model_prob, bookmakers_used, odds, set_betting_info=None, side=""):
    margin = abs(expected_games - line)
    c = 50
    c += clamp(margin / 3.0, 0, 1) * 22
    c += clamp((model_prob - 0.5) / 0.14, 0, 1) * 16
    c += clamp(bookmakers_used / 10, 0, 1) * 8

    if 1.72 <= odds <= 2.05:
        c += 4
    elif 1.60 <= odds <= 2.20:
        c += 2

    if set_betting_info:
        adj = set_betting_adjustment(set_betting_info)
        if side == "over" and adj > 0:
            c += min(4, adj * 3)
        if side == "under" and adj < 0:
            c += min(4, abs(adj) * 3)

    return round(clamp(c, 1, 97), 1)


def quality_score(confidence, edge, bookmakers_used, odds, matches_min, margin, module_score=0.0):
    q = 0
    q += clamp(confidence / 90, 0, 1) * 30
    q += clamp(edge / 0.11, 0, 1) * 30
    q += clamp(bookmakers_used / 10, 0, 1) * 14
    q += clamp(matches_min / 14, 0, 1) * 12
    q += clamp(margin / 3.0, 0, 1) * 9
    q += clamp(module_score, -6, 6)

    if 1.72 <= odds <= 2.05:
        q += 5
    elif 1.60 <= odds <= 2.20:
        q += 3

    return round(clamp(q, 1, 99), 1)


def special_module_score(side, line, expected_margin, first_form, second_form, market_info, set_betting_info):
    p10 = first_form.get("last_10", {})
    o10 = second_form.get("last_10", {})
    avg_three = (safe_float(p10.get("three_set_rate")) + safe_float(o10.get("three_set_rate"))) / 2
    avg_close = (safe_float(p10.get("close_set_rate")) + safe_float(o10.get("close_set_rate"))) / 2
    gap = safe_float((market_info or {}).get("market_gap"), None)
    set_adj = set_betting_adjustment(set_betting_info)

    score = 0.0

    if side == "over":
        if gap is not None and gap <= 0.12:
            score += 2.0
        if avg_three >= 0.36:
            score += 1.5
        if avg_close >= 0.42:
            score += 1.5
        if line <= 21.5:
            score += 1.0
        if set_adj > 0:
            score += min(2.0, set_adj * 1.5)
        if gap is not None and gap >= 0.35:
            score -= 3.0

    if side == "under":
        if gap is not None and gap >= 0.26:
            score += 2.0
        if avg_three <= 0.24:
            score += 1.2
        if avg_close <= 0.32:
            score += 1.2
        if expected_margin <= -2.5:
            score += 1.5
        if set_adj < 0:
            score += min(2.0, abs(set_adj) * 1.5)

    return round(clamp(score, -5, 6), 2)


def stake_from_quality(quality, edge, side, module_score):
    if quality >= 90 and edge >= 0.095:
        return 1.0, "Top Rated"
    if quality >= 82 and edge >= 0.07:
        return 0.75, "Strong"
    if quality >= 72:
        return 0.5, "Standard"
    if quality >= 66 and module_score >= 3.0:
        return 0.5, "Module Value"
    return 0.25, "Small Value"


def pick_id_for(event_key, side, line):
    raw = f"{MODEL_VERSION}:{event_key}:{side}:{line}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_reasoning(pick):
    return (
        f"{pick['bet']} selected in {pick['match']} at line {pick['line']}. "
        f"Shadow expected total games: {pick['expected_total_games']:.2f}; market line: {pick['line']:.1f}. "
        f"Model probability {pick['model_prob'] * 100:.1f}% versus implied {pick['implied_prob'] * 100:.1f}% "
        f"from best odds {pick['odds']:.2f}. Edge: {pick['edge'] * 100:+.1f}%. "
        f"Bookmakers used: {pick['bookmakers_used']}. Confidence: {pick['confidence']:.1f}. "
        f"Module score: {pick.get('module_score', 0)}."
    )


def record_market_snapshot(snapshot):
    old = load_json(SNAPSHOT_FILE, [])
    if not isinstance(old, list):
        old = []
    old.append(snapshot)
    old = old[-2000:]
    save_json(SNAPSHOT_FILE, old)


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
        "fixtures_total": len(fixtures),
        "scanned": 0,
        "skipped": [],
        "candidates_raw": 0,
        "errors": [],
        "shadow_modules": {
            "set_betting_signal": True,
            "surface_proxy": True,
            "over_rescue_filter": True,
            "under_blowout_filter": True,
            "market_snapshots": True,
        },
    }

    h2h_cache = {}
    snapshots = []

    for match in fixtures:
        event_key = match.get("event_key")
        name = f"{match.get('event_first_player')} - {match.get('event_second_player')}"

        if not event_key:
            continue

        if not is_pregame(match):
            debug["skipped"].append({"event_key": event_key, "match": name, "reason": "not_pregame"})
            continue

        if not is_singles(match):
            debug["skipped"].append({"event_key": event_key, "match": name, "reason": "not_singles"})
            continue

        first_key = match.get("first_player_key")
        second_key = match.get("second_player_key")

        if not first_key or not second_key:
            debug["skipped"].append({"event_key": event_key, "match": name, "reason": "missing_player_key"})
            continue

        try:
            debug["scanned"] += 1

            odds_blob = fetch_odds(event_key)
            if not odds_blob:
                debug["skipped"].append({"event_key": event_key, "match": name, "reason": "no_odds"})
                continue

            totals_lines = parse_totals_market(odds_blob)
            if not totals_lines:
                debug["skipped"].append({"event_key": event_key, "match": name, "reason": "no_totals_market"})
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
            set_betting_info = extract_set_betting_info(odds_blob)
            surface_adj, surface_proxy = surface_proxy_adjustment(match)

            exp_games = expected_total_games(
                first_form,
                second_form,
                h2h_matches,
                market_info,
                set_betting_info=set_betting_info,
                surface_adj=surface_adj,
            )

            snapshots.append({
                "created_at": now_iso(),
                "event_key": event_key,
                "match": name,
                "date": match.get("event_date"),
                "time": match.get("event_time"),
                "market_info": market_info,
                "set_betting_info": set_betting_info,
                "surface_proxy": surface_proxy,
                "surface_adj": surface_adj,
                "lines": totals_lines,
            })

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
                    expected_margin = round(exp_games - line, 3)
                    margin = abs(expected_margin)

                    if edge < MIN_EDGE:
                        continue

                    module_score = special_module_score(
                        side,
                        line,
                        expected_margin,
                        first_form,
                        second_form,
                        market_info,
                        set_betting_info,
                    )

                    # Shadow is wide, but not reckless.
                    if side == "over" and module_score < -2.0:
                        continue

                    confidence = confidence_score(
                        exp_games,
                        line,
                        model_prob,
                        bookmakers_used,
                        odds,
                        set_betting_info=set_betting_info,
                        side=side,
                    )

                    if confidence < MIN_CONFIDENCE and module_score < 3.0:
                        continue

                    quality = quality_score(
                        confidence,
                        edge,
                        bookmakers_used,
                        odds,
                        matches_min,
                        margin,
                        module_score=module_score,
                    )
                    stake, stake_label = stake_from_quality(quality, edge, side, module_score)

                    pick = {
                        "pick_id": pick_id_for(event_key, side, line),
                        "event_key": event_key,
                        "fixture_id": event_key,
                        "sport": "tennis",
                        "model_version": MODEL_VERSION,
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
                        "expected_margin": expected_margin,
                        "confidence": confidence,
                        "quality_score": quality,
                        "stake": stake,
                        "stake_label": stake_label,
                        "market_info": market_info,
                        "set_betting_info": set_betting_info,
                        "set_betting_adjustment": set_betting_adjustment(set_betting_info),
                        "surface_proxy": surface_proxy,
                        "surface_adjustment": surface_adj,
                        "module_score": module_score,
                        "first_form": first_form,
                        "second_form": second_form,
                        "first_strength_score": player_strength_score(first_form),
                        "second_strength_score": player_strength_score(second_form),
                        "h2h_matches": len(clean_finished_matches(h2h_matches)),
                        "result": "pending",
                        "created_at": now_iso(),
                    }

                    pick["reasoning"] = build_reasoning(pick)
                    candidates.append(pick)

        except Exception as e:
            debug["errors"].append({"event_key": event_key, "match": name, "error": str(e)})
            print(f"ERROR {event_key} {name}: {e}")

    debug["candidates_raw"] = len(candidates)

    candidates.sort(
        key=lambda x: (
            safe_float(x.get("quality_score")),
            safe_float(x.get("module_score")),
            safe_float(x.get("edge")),
            safe_float(x.get("confidence")),
        ),
        reverse=True,
    )

    final = []
    over_count = 0
    under_count = 0
    used_events = set()

    for pick in candidates:
        if pick["event_key"] in used_events:
            continue

        if pick["side"] == "over":
            if over_count >= MAX_OVER_PICKS:
                continue
            over_count += 1

        if pick["side"] == "under":
            if under_count >= MAX_UNDER_PICKS:
                continue
            under_count += 1

        final.append(pick)
        used_events.add(pick["event_key"])

        if len(final) >= MAX_PICKS:
            break

    for pick in final:
        old = existing_by_id.get(pick["pick_id"])
        if old and str(old.get("result") or "pending").lower() != "pending":
            continue
        existing_by_id[pick["pick_id"]] = pick

    results = list(existing_by_id.values())
    results.sort(key=lambda x: (x.get("date") or "", x.get("time") or "", x.get("match") or ""))

    payload = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": MODEL_NAME,
        "stake_mode": "v2_wide_shadow_quality_plus_modules",
        "market": MARKET_NAME,
        "filters": {
            "days_ahead": DAYS_AHEAD,
            "max_picks": MAX_PICKS,
            "max_over_picks": MAX_OVER_PICKS,
            "max_under_picks": MAX_UNDER_PICKS,
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
        "modules": debug["shadow_modules"],
        "summary": {
            "fixtures_checked": len(fixtures),
            "candidates_raw": len(candidates),
            "final_picks": len(final),
            "errors": len(debug["errors"]),
            "over_final": sum(1 for p in final if p.get("side") == "over"),
            "under_final": sum(1 for p in final if p.get("side") == "under"),
        },
        "picks": final,
    }

    if len(fixtures) < MIN_FIXTURES_TO_SAVE:
        raise RuntimeError(f"Safety stop: only {len(fixtures)} fixtures. Refusing to overwrite shadow output.")

    if len(debug["errors"]) > MAX_API_ERRORS_TO_SAVE:
        raise RuntimeError(f"Safety stop: too many API errors ({len(debug['errors'])}). Refusing to overwrite shadow output.")

    save_json(PREDICTIONS_FILE, payload)
    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)

    for s in snapshots:
        record_market_snapshot(s)

    print("")
    print(f"TENNIS TOTALS V2 WIDE SHADOW DONE: candidates={len(candidates)} final={len(final)} results_total={len(results)}")
    print(f"Over final: {sum(1 for p in final if p.get('side') == 'over')}")
    print(f"Under final: {sum(1 for p in final if p.get('side') == 'under')}")
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {DEBUG_FILE}")


if __name__ == "__main__":
    main()

import os
import json
import time
import math
import hashlib
from statistics import median, mean
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


# ============================================================
# AI77 TENNIS TOTALS V2 WIDE SHADOW
# ============================================================
# Namen:
# - Eksperimentalna "wide" mašina za tennis total games.
# - Bere iste osnovne API podatke kot V1.
# - Doda market features iz:
#   1) Over/Under by Games in Match
#   2) Total - Home / Total - Away
#   3) Asian Handicap (Games)
#   4) Over/Under 2.5 sets
#   5) Number of sets
#   6) 1st set totals
#   7) 2nd set totals
# - Ne blokira agresivno linij.
# - Shrani prediction, results in debug ločeno od V1.
#
# Pomembno:
# - To je SHADOW model. Najprej ga pusti teči vsaj 100-200 pickov.
# - Ne mešaj rezultatov z V1 datotekami.
# ============================================================


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"

PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_predictions_v2_wide_shadow.json"
RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results_v2_wide_shadow.json"
DEBUG_FILE = f"{DATA_DIR}/tennis_totals_debug_v2_wide_shadow.json"
CANDIDATES_FILE = f"{DATA_DIR}/tennis_totals_candidates_v2_wide_shadow.json"

MODEL_VERSION = "ai77_tennis_totals_v2_wide_shadow"
MODEL_NAME = "AI77 Tennis Totals V2 Wide Shadow"

MATCH_TOTAL_MARKET = "Over/Under by Games in Match"
SETS_OU_MARKET = "Over/Under"
PLAYER_TOTAL_HOME_MARKET = "Total - Home"
PLAYER_TOTAL_AWAY_MARKET = "Total - Away"
HANDICAP_GAMES_MARKET = "Asian Handicap (Games)"
FIRST_SET_TOTAL_MARKET = "Over/Under (1st Set)"
SECOND_SET_TOTAL_MARKET = "Over/Under by Games (2nd Set)"
NUMBER_OF_SETS_MARKET = "Number of sets"

DAYS_AHEAD = 1
MAX_FIXTURES = 650
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.30

MAX_PICKS = 24
MAX_OVER_PICKS = 12
MAX_UNDER_PICKS = 14

MIN_RECENT_MATCHES_EACH = 5
MIN_BOOKMAKERS_MATCH_TOTAL = 3
MIN_EDGE = 0.035
MIN_CONFIDENCE = 58.0
MIN_QUALITY = 54.0

ODDS_MIN = 1.55
ODDS_MAX = 2.35

MODEL_PROB_MIN = 0.39
MODEL_PROB_MAX = 0.66

MAIN_LINES_MIN = 18.5
MAIN_LINES_MAX = 24.5

# Hard safety samo za res ekstremne stvari.
EXTREME_LINE_MIN = 17.5
EXTREME_LINE_MAX = 25.5


# ============================================================
# BASIC HELPERS
# ============================================================

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
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def safe_int(v, default=0):
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def round_or_none(v, ndigits=3):
    if v is None:
        return None
    try:
        return round(float(v), ndigits)
    except Exception:
        return None


def avg(values, default=None):
    arr = [safe_float(x, None) for x in values]
    arr = [x for x in arr if x is not None]
    if not arr:
        return default
    return sum(arr) / len(arr)


def med(values, default=None):
    arr = [safe_float(x, None) for x in values]
    arr = [x for x in arr if x is not None]
    if not arr:
        return default
    return median(arr)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# ============================================================
# API
# ============================================================

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


# ============================================================
# FIXTURE FILTERS
# ============================================================

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


# ============================================================
# SCORE / FORM
# ============================================================

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

        # Normal best-of-3 singles only.
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
                "over_19_5_rate": 0.0,
                "over_20_5_rate": 0.0,
                "over_21_5_rate": 0.0,
                "over_22_5_rate": 0.0,
                "over_23_5_rate": 0.0,
                "under_21_5_rate": 0.0,
                "under_22_5_rate": 0.0,
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
            "over_19_5_rate": round(sum(1 for x in totals if x > 19.5) / len(totals), 4),
            "over_20_5_rate": round(sum(1 for x in totals if x > 20.5) / len(totals), 4),
            "over_21_5_rate": round(sum(1 for x in totals if x > 21.5) / len(totals), 4),
            "over_22_5_rate": round(sum(1 for x in totals if x > 22.5) / len(totals), 4),
            "over_23_5_rate": round(sum(1 for x in totals if x > 23.5) / len(totals), 4),
            "under_21_5_rate": round(sum(1 for x in totals if x < 21.5) / len(totals), 4),
            "under_22_5_rate": round(sum(1 for x in totals if x < 22.5) / len(totals), 4),
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


# ============================================================
# ODDS / MARKET PARSING
# ============================================================

def collect_side_books(market_dict, possible_side_keys):
    out = {}
    if not isinstance(market_dict, dict):
        return out

    for key in possible_side_keys:
        side_data = market_dict.get(key)
        if isinstance(side_data, dict):
            # Structure A: line -> bookmaker -> odds
            # Structure B: bookmaker -> odds
            for k, v in side_data.items():
                if isinstance(v, dict):
                    line = str(k)
                    if line not in out:
                        out[line] = {}
                    for book, odd in v.items():
                        fv = safe_float(odd, None)
                        if fv and fv > 1:
                            out[line][book] = fv
                else:
                    # no line
                    line = "__no_line__"
                    if line not in out:
                        out[line] = {}
                    fv = safe_float(v, None)
                    if fv and fv > 1:
                        out[line][k] = fv
    return out


def normalize_ou_market(odds_blob, market_name):
    market = odds_blob.get(market_name)
    if not isinstance(market, dict):
        return {}

    over_keys = [
        f"{market_name} Over",
        "Over",
        "Total Over",
    ]
    under_keys = [
        f"{market_name} Under",
        "Under",
        "Total Under",
    ]

    over_by_line = collect_side_books(market, over_keys)
    under_by_line = collect_side_books(market, under_keys)

    lines = sorted(set(over_by_line) & set(under_by_line), key=lambda x: safe_float(x, 9999))
    out = {}

    for line_s in lines:
        if line_s == "__no_line__":
            continue
        line = safe_float(line_s, None)
        if line is None:
            continue

        over_books = over_by_line.get(line_s) or {}
        under_books = under_by_line.get(line_s) or {}
        shared = sorted(set(over_books) & set(under_books))

        if not shared:
            continue

        over_vals = [over_books[b] for b in shared]
        under_vals = [under_books[b] for b in shared]

        over_med = median(over_vals)
        under_med = median(under_vals)
        no_vig = no_vig_prob(over_med, under_med)

        out[float(line)] = {
            "line": float(line),
            "shared_books": shared,
            "bookmakers_used": len(shared),
            "over": {
                "best_odds": round(max(over_vals), 3),
                "best_bookmaker": max(shared, key=lambda b: over_books[b]),
                "median_odds": round(over_med, 3),
                "avg_odds": round(mean(over_vals), 3),
                "min_odds": round(min(over_vals), 3),
                "max_odds": round(max(over_vals), 3),
            },
            "under": {
                "best_odds": round(max(under_vals), 3),
                "best_bookmaker": max(shared, key=lambda b: under_books[b]),
                "median_odds": round(under_med, 3),
                "avg_odds": round(mean(under_vals), 3),
                "min_odds": round(min(under_vals), 3),
                "max_odds": round(max(under_vals), 3),
            },
            "market_no_vig": no_vig,
            "spread": {
                "over_range": round(max(over_vals) - min(over_vals), 3),
                "under_range": round(max(under_vals) - min(under_vals), 3),
            },
        }

    return out


def no_vig_prob(over_odds, under_odds):
    over_odds = safe_float(over_odds, None)
    under_odds = safe_float(under_odds, None)
    if not over_odds or not under_odds or over_odds <= 1 or under_odds <= 1:
        return None

    p_over_raw = 1 / over_odds
    p_under_raw = 1 / under_odds
    total = p_over_raw + p_under_raw
    if total <= 0:
        return None

    return {
        "over": round(p_over_raw / total, 4),
        "under": round(p_under_raw / total, 4),
        "margin": round(total - 1, 4),
    }


def market_center_from_ou_lines(lines_dict):
    # Estimate where no-vig over probability crosses 50%.
    if not lines_dict:
        return None

    points = []
    for line, info in lines_dict.items():
        nv = info.get("market_no_vig") or {}
        p_over = safe_float(nv.get("over"), None)
        if p_over is not None:
            points.append((safe_float(line), p_over))

    points.sort()
    if not points:
        return None

    # If exact near 0.5
    closest = min(points, key=lambda x: abs(x[1] - 0.5))

    # Linear interpolation around 0.5
    for i in range(len(points) - 1):
        l1, p1 = points[i]
        l2, p2 = points[i + 1]
        if (p1 - 0.5) == 0:
            return round(l1, 3)
        if (p1 - 0.5) * (p2 - 0.5) <= 0 and p1 != p2:
            t = (0.5 - p1) / (p2 - p1)
            center = l1 + t * (l2 - l1)
            return round(center, 3)

    return round(closest[0], 3)


def parse_match_total_candidates(odds_blob):
    lines = normalize_ou_market(odds_blob, MATCH_TOTAL_MARKET)
    candidates = []

    for line, info in lines.items():
        if not (EXTREME_LINE_MIN <= line <= EXTREME_LINE_MAX):
            continue
        if not (MAIN_LINES_MIN <= line <= MAIN_LINES_MAX):
            continue
        if safe_int(info.get("bookmakers_used")) < MIN_BOOKMAKERS_MATCH_TOTAL:
            continue
        candidates.append(info)

    return sorted(candidates, key=lambda x: safe_float(x.get("line")))


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


def extract_sets_market_features(odds_blob):
    # In API sample "Over/Under" is often 2.5 sets, not games.
    lines = normalize_ou_market(odds_blob, SETS_OU_MARKET)
    info = lines.get(2.5)

    out = {
        "three_set_prob_no_vig": None,
        "straight_sets_prob_no_vig": None,
        "sets_ou_books": 0,
        "sets_ou_over_2_5_median": None,
        "sets_ou_under_2_5_median": None,
    }

    if info:
        nv = info.get("market_no_vig") or {}
        out.update({
            "three_set_prob_no_vig": nv.get("over"),
            "straight_sets_prob_no_vig": nv.get("under"),
            "sets_ou_books": info.get("bookmakers_used"),
            "sets_ou_over_2_5_median": (info.get("over") or {}).get("median_odds"),
            "sets_ou_under_2_5_median": (info.get("under") or {}).get("median_odds"),
        })

    # Number of sets market can be shaped differently; keep raw availability.
    num_sets = odds_blob.get(NUMBER_OF_SETS_MARKET)
    out["number_of_sets_available"] = isinstance(num_sets, dict)
    return out


def extract_player_total_features(odds_blob):
    home_lines = normalize_ou_market(odds_blob, PLAYER_TOTAL_HOME_MARKET)
    away_lines = normalize_ou_market(odds_blob, PLAYER_TOTAL_AWAY_MARKET)

    home_center = market_center_from_ou_lines(home_lines)
    away_center = market_center_from_ou_lines(away_lines)

    out = {
        "home_total_center": home_center,
        "away_total_center": away_center,
        "player_total_sum_center": None,
        "player_total_diff_center": None,
        "home_total_lines_count": len(home_lines),
        "away_total_lines_count": len(away_lines),
    }

    if home_center is not None and away_center is not None:
        out["player_total_sum_center"] = round(home_center + away_center, 3)
        out["player_total_diff_center"] = round(home_center - away_center, 3)

    return out


def extract_set_total_features(odds_blob):
    first_lines = normalize_ou_market(odds_blob, FIRST_SET_TOTAL_MARKET)
    second_lines = normalize_ou_market(odds_blob, SECOND_SET_TOTAL_MARKET)

    first_center = market_center_from_ou_lines(first_lines)
    second_center = market_center_from_ou_lines(second_lines)

    out = {
        "first_set_total_center": first_center,
        "second_set_total_center": second_center,
        "set_total_sum_2_sets": None,
        "first_set_lines_count": len(first_lines),
        "second_set_lines_count": len(second_lines),
    }

    if first_center is not None and second_center is not None:
        out["set_total_sum_2_sets"] = round(first_center + second_center, 3)

    return out


def extract_handicap_features(odds_blob):
    market = odds_blob.get(HANDICAP_GAMES_MARKET)
    if not isinstance(market, dict):
        return {
            "handicap_available": False,
            "handicap_center": None,
            "handicap_abs_center": None,
            "handicap_books": 0,
            "blowout_risk_market": False,
            "close_match_market": None,
        }

    home_keys = [f"{HANDICAP_GAMES_MARKET} Home", "Home"]
    away_keys = [f"{HANDICAP_GAMES_MARKET} Away", "Away"]

    home_by_line = collect_side_books(market, home_keys)
    away_by_line = collect_side_books(market, away_keys)

    points = []
    max_books = 0

    # Lines are from home perspective. We estimate where home handicap is fair.
    for line_s, home_books in home_by_line.items():
        if line_s == "__no_line__":
            continue
        line = safe_float(line_s, None)
        if line is None:
            continue

        # Opposite line may be same string in this API sample, not mirrored.
        away_books = away_by_line.get(line_s) or {}
        shared = sorted(set(home_books) & set(away_books))
        if not shared:
            continue

        h_med = median([home_books[b] for b in shared])
        a_med = median([away_books[b] for b in shared])
        nv = no_vig_prob(h_med, a_med)
        if not nv:
            continue

        max_books = max(max_books, len(shared))
        points.append((line, nv["over"]))  # "home cover" no-vig

    center = None
    if points:
        points.sort()
        closest = min(points, key=lambda x: abs(x[1] - 0.5))
        center = closest[0]

        for i in range(len(points) - 1):
            l1, p1 = points[i]
            l2, p2 = points[i + 1]
            if (p1 - 0.5) * (p2 - 0.5) <= 0 and p1 != p2:
                t = (0.5 - p1) / (p2 - p1)
                center = l1 + t * (l2 - l1)
                break

    abs_center = abs(center) if center is not None else None

    return {
        "handicap_available": True,
        "handicap_center": round_or_none(center, 3),
        "handicap_abs_center": round_or_none(abs_center, 3),
        "handicap_books": max_books,
        "blowout_risk_market": bool(abs_center is not None and abs_center >= 4.75),
        "close_match_market": bool(abs_center is not None and abs_center <= 2.0),
    }


def build_market_features_v2(odds_blob):
    match_lines = normalize_ou_market(odds_blob, MATCH_TOTAL_MARKET)
    match_center = market_center_from_ou_lines(match_lines)

    sets_features = extract_sets_market_features(odds_blob)
    player_total_features = extract_player_total_features(odds_blob)
    set_total_features = extract_set_total_features(odds_blob)
    handicap_features = extract_handicap_features(odds_blob)
    moneyline = extract_home_away_odds(odds_blob)

    out = {
        "match_total_center": match_center,
        "match_total_lines_count": len(match_lines),
        "moneyline": moneyline,
    }
    out.update(sets_features)
    out.update(player_total_features)
    out.update(set_total_features)
    out.update(handicap_features)

    # Derived confirmations against match total center.
    pts = safe_float(out.get("player_total_sum_center"), None)
    if pts is not None and match_center is not None:
        out["player_total_vs_match_center"] = round(pts - match_center, 3)
    else:
        out["player_total_vs_match_center"] = None

    sts = safe_float(out.get("set_total_sum_2_sets"), None)
    if sts is not None and match_center is not None:
        # Two sets sum below match center is normal because 3-set probability adds extra.
        out["two_set_sum_vs_match_center"] = round(sts - match_center, 3)
    else:
        out["two_set_sum_vs_match_center"] = None

    return out


# ============================================================
# EXPECTED TOTAL MODEL
# ============================================================

def base_expected_total_games(player_form, opponent_form, h2h_matches, market_info):
    p5 = player_form["last_5"]
    p10 = player_form["last_10"]
    p20 = player_form["last_20"]
    o5 = opponent_form["last_5"]
    o10 = opponent_form["last_10"]
    o20 = opponent_form["last_20"]

    def mix_total(w):
        return safe_float(w.get("median_total_games")) * 0.62 + safe_float(w.get("avg_total_games")) * 0.38

    avg_recent = (
        mix_total(p10) * 0.27 +
        mix_total(o10) * 0.27 +
        mix_total(p5) * 0.16 +
        mix_total(o5) * 0.16 +
        mix_total(p20) * 0.07 +
        mix_total(o20) * 0.07
    )

    three_set_rate = (safe_float(p10.get("three_set_rate")) + safe_float(o10.get("three_set_rate"))) / 2
    close_set_rate = (safe_float(p10.get("close_set_rate")) + safe_float(o10.get("close_set_rate"))) / 2

    p_strength = player_strength_score(player_form)
    o_strength = player_strength_score(opponent_form)
    strength_gap = abs(p_strength - o_strength)

    exp = avg_recent
    exp += (three_set_rate - 0.28) * 4.0
    exp += (close_set_rate - 0.36) * 2.6

    if strength_gap >= 34:
        exp -= 2.35
    elif strength_gap >= 28:
        exp -= 1.85
    elif strength_gap >= 22:
        exp -= 1.15
    elif strength_gap <= 7:
        exp += 0.95

    if market_info:
        gap = safe_float(market_info.get("market_gap"))

        if gap >= 0.60:
            exp -= 2.65
        elif gap >= 0.48:
            exp -= 2.15
        elif gap >= 0.36:
            exp -= 1.65
        elif gap >= 0.24:
            exp -= 0.95
        elif gap <= 0.08:
            exp += 0.65

    h2h_finished = clean_finished_matches(h2h_matches)
    if h2h_finished:
        h2h_totals = [total_games_from_scores(m.get("scores")) for m in h2h_finished[:5]]
        h2h_avg = sum(h2h_totals) / len(h2h_totals)
        exp = exp * 0.86 + h2h_avg * 0.14

    return round(clamp(exp, 16.0, 30.0), 2)


def market_adjusted_expected_games(base_exp, market_features):
    exp = safe_float(base_exp)

    match_center = safe_float(market_features.get("match_total_center"), None)
    player_sum = safe_float(market_features.get("player_total_sum_center"), None)
    three_prob = safe_float(market_features.get("three_set_prob_no_vig"), None)
    first_center = safe_float(market_features.get("first_set_total_center"), None)
    second_center = safe_float(market_features.get("second_set_total_center"), None)
    handicap_abs = safe_float(market_features.get("handicap_abs_center"), None)

    # Market center is useful but should not dominate the model.
    if match_center is not None:
        exp = exp * 0.78 + match_center * 0.22

    # Player totals are an independent confirmation.
    if player_sum is not None:
        exp = exp * 0.84 + player_sum * 0.16

    # Three-set market direct adjustment.
    if three_prob is not None:
        exp += (three_prob - 0.30) * 3.7

    # Set totals: if both first and second set are high, support over.
    if first_center is not None and second_center is not None:
        two_set_sum = first_center + second_center
        if two_set_sum >= 19.4:
            exp += 0.45
        elif two_set_sum <= 18.4:
            exp -= 0.35

    # Handicap center / dominance.
    if handicap_abs is not None:
        if handicap_abs >= 5.5:
            exp -= 1.25
        elif handicap_abs >= 4.5:
            exp -= 0.85
        elif handicap_abs <= 1.5:
            exp += 0.55

    return round(clamp(exp, 16.0, 30.0), 2)


def model_probability(expected_games, line, side, market_features=None):
    diff = expected_games - line

    # Wider scale for high lines and uncertain markets.
    scale = 2.85
    if line >= 22.5:
        scale = 3.10
    elif line <= 19.5:
        scale = 2.75

    p_over = sigmoid(diff / scale)

    # Small market-aware correction from 3-set probability.
    if market_features:
        three_prob = safe_float(market_features.get("three_set_prob_no_vig"), None)
        if three_prob is not None:
            p_over += (three_prob - 0.30) * 0.09

        handicap_abs = safe_float(market_features.get("handicap_abs_center"), None)
        if handicap_abs is not None and handicap_abs >= 5.0:
            p_over -= 0.035

    p_over = clamp(p_over, MODEL_PROB_MIN, MODEL_PROB_MAX)

    if side == "over":
        return round(p_over, 4)

    return round(1 - p_over, 4)


# ============================================================
# SIGNALS / PROFILES / SCORING
# ============================================================

def build_signals(side, line, expected_games, base_expected_games_value, market_features, first_form, second_form):
    margin = expected_games - line
    abs_margin = abs(margin)

    player_vs = safe_float(market_features.get("player_total_vs_match_center"), None)
    three_prob = safe_float(market_features.get("three_set_prob_no_vig"), None)
    handicap_abs = safe_float(market_features.get("handicap_abs_center"), None)
    match_center = safe_float(market_features.get("match_total_center"), None)
    first_set_center = safe_float(market_features.get("first_set_total_center"), None)
    second_set_center = safe_float(market_features.get("second_set_total_center"), None)

    p10 = first_form.get("last_10", {})
    o10 = second_form.get("last_10", {})

    form_over_21_5 = (safe_float(p10.get("over_21_5_rate")) + safe_float(o10.get("over_21_5_rate"))) / 2
    form_over_22_5 = (safe_float(p10.get("over_22_5_rate")) + safe_float(o10.get("over_22_5_rate"))) / 2
    form_three = (safe_float(p10.get("three_set_rate")) + safe_float(o10.get("three_set_rate"))) / 2
    form_close = (safe_float(p10.get("close_set_rate")) + safe_float(o10.get("close_set_rate"))) / 2

    signals = {
        "model_vs_line_games": round(margin, 3),
        "base_model_vs_line_games": round(base_expected_games_value - line, 3),
        "abs_model_margin": round(abs_margin, 3),
        "match_center_vs_line": round_or_none(match_center - line if match_center is not None else None, 3),
        "player_totals_confirm": False,
        "set_totals_confirm": False,
        "three_set_support": False,
        "form_total_support": False,
        "close_match_support": False,
        "blowout_risk": False,
        "market_curve_support": False,
        "wide_disagreement": False,
    }

    if player_vs is not None:
        if side == "over":
            signals["player_totals_confirm"] = player_vs >= 0.25
        else:
            signals["player_totals_confirm"] = player_vs <= -0.25

    if first_set_center is not None and second_set_center is not None:
        two_set_sum = first_set_center + second_set_center
        if side == "over":
            signals["set_totals_confirm"] = two_set_sum >= 19.2
        else:
            signals["set_totals_confirm"] = two_set_sum <= 18.8

    if three_prob is not None:
        if side == "over":
            signals["three_set_support"] = three_prob >= 0.31
        else:
            signals["three_set_support"] = three_prob <= 0.285

    if side == "over":
        if line <= 20.5:
            signals["form_total_support"] = form_over_21_5 >= 0.42
        elif line <= 21.5:
            signals["form_total_support"] = form_over_21_5 >= 0.46
        else:
            signals["form_total_support"] = form_over_22_5 >= 0.42
    else:
        if line >= 22.5:
            signals["form_total_support"] = form_over_22_5 <= 0.48
        else:
            signals["form_total_support"] = form_over_21_5 <= 0.52

    signals["close_match_support"] = bool((handicap_abs is not None and handicap_abs <= 2.0) or form_close >= 0.39)
    signals["blowout_risk"] = bool(handicap_abs is not None and handicap_abs >= 4.75)

    if match_center is not None:
        if side == "over":
            signals["market_curve_support"] = match_center >= line - 0.10
        else:
            signals["market_curve_support"] = match_center <= line + 0.10

    # Wide disagreement means model and market-derived features disagree.
    if match_center is not None:
        signals["wide_disagreement"] = abs(expected_games - match_center) >= 2.0

    signals["form_over_21_5_rate_avg"] = round(form_over_21_5, 4)
    signals["form_over_22_5_rate_avg"] = round(form_over_22_5, 4)
    signals["form_three_set_rate_avg"] = round(form_three, 4)
    signals["form_close_set_rate_avg"] = round(form_close, 4)

    return signals


def assign_profile(side, line, signals, market_features):
    three_prob = safe_float(market_features.get("three_set_prob_no_vig"), None)
    handicap_abs = safe_float(market_features.get("handicap_abs_center"), None)

    if side == "under":
        if signals.get("blowout_risk") and signals.get("player_totals_confirm"):
            return "UNDER_DOMINANT_FAV_PLAYER_TOTAL_CONFIRM"
        if signals.get("blowout_risk"):
            return "UNDER_DOMINANT_FAV"
        if signals.get("three_set_support") and signals.get("set_totals_confirm"):
            return "UNDER_LOW_THREE_SET_SET_CONFIRM"
        if signals.get("player_totals_confirm") and signals.get("market_curve_support"):
            return "UNDER_PLAYER_TOTAL_MARKET_CURVE_CONFIRM"
        if line >= 22.5 and signals.get("form_total_support"):
            return "UNDER_HIGH_LINE_FORM_SUPPORT"
        return "UNDER_GENERAL_VALUE"

    if side == "over":
        if line <= 20.5 and signals.get("market_curve_support"):
            return "OVER_LOW_LINE_VALUE"
        if signals.get("close_match_support") and signals.get("three_set_support"):
            return "OVER_CLOSE_MATCH_THREE_SET_SUPPORT"
        if signals.get("set_totals_confirm") and signals.get("player_totals_confirm"):
            return "OVER_SET_AND_PLAYER_TOTAL_CONFIRM"
        if line >= 22.5 and signals.get("three_set_support") and signals.get("form_total_support"):
            return "OVER_HIGH_LINE_SPECIAL"
        if line == 20.5:
            return "OVER_20_5_CORE"
        return "OVER_GENERAL_VALUE"

    return "UNKNOWN"


def confidence_score(side, expected_games, line, model_prob, bookmakers_used, odds, signals, market_features):
    margin = abs(expected_games - line)

    c = 42
    c += clamp(margin / 3.2, 0, 1) * 18
    c += clamp((model_prob - 0.5) / 0.14, 0, 1) * 14
    c += clamp(bookmakers_used / 10, 0, 1) * 8

    if 1.70 <= odds <= 2.08:
        c += 5
    elif 1.55 <= odds <= 2.25:
        c += 2

    confirmations = [
        signals.get("player_totals_confirm"),
        signals.get("set_totals_confirm"),
        signals.get("three_set_support"),
        signals.get("form_total_support"),
        signals.get("market_curve_support"),
    ]
    c += sum(1 for x in confirmations if x) * 3.2

    if side == "over" and signals.get("blowout_risk"):
        c -= 6
    if side == "under" and signals.get("close_match_support") and not signals.get("three_set_support"):
        c -= 2

    if signals.get("wide_disagreement"):
        c -= 3

    return round(clamp(c, 1, 96), 1)


def quality_score(side, confidence, edge, bookmakers_used, odds, matches_min, margin, signals):
    q = 0
    q += clamp(confidence / 90, 0, 1) * 28
    q += clamp(edge / 0.105, 0, 1) * 24
    q += clamp(bookmakers_used / 10, 0, 1) * 12
    q += clamp(matches_min / 14, 0, 1) * 11
    q += clamp(margin / 3.2, 0, 1) * 9

    confirmations = [
        signals.get("player_totals_confirm"),
        signals.get("set_totals_confirm"),
        signals.get("three_set_support"),
        signals.get("form_total_support"),
        signals.get("market_curve_support"),
    ]
    q += sum(1 for x in confirmations if x) * 4

    if 1.70 <= odds <= 2.08:
        q += 5
    elif 1.55 <= odds <= 2.35:
        q += 2.5

    if side == "over" and signals.get("blowout_risk"):
        q -= 8

    if signals.get("wide_disagreement"):
        q -= 4

    return round(clamp(q, 1, 99), 1)


def stake_from_quality(quality, edge, profile, side, line):
    # Shadow model naj ostane bolj previden.
    if quality >= 88 and edge >= 0.09:
        return 0.75, "Shadow Top"
    if quality >= 80 and edge >= 0.07:
        return 0.50, "Shadow Strong"
    if quality >= 68 and edge >= 0.05:
        return 0.35, "Shadow Standard"
    return 0.25, "Shadow Small"


def pick_id_for(event_key, side, line):
    raw = f"{MODEL_VERSION}:{event_key}:{side}:{line}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_reasoning(pick):
    mf = pick.get("market_features_v2") or {}
    signals = pick.get("signals") or {}

    extras = []
    if mf.get("match_total_center") is not None:
        extras.append(f"market center {mf.get('match_total_center')}")
    if mf.get("player_total_sum_center") is not None:
        extras.append(f"player-total sum {mf.get('player_total_sum_center')}")
    if mf.get("three_set_prob_no_vig") is not None:
        extras.append(f"3-set no-vig {mf.get('three_set_prob_no_vig') * 100:.1f}%")
    if mf.get("handicap_abs_center") is not None:
        extras.append(f"handicap abs {mf.get('handicap_abs_center')}")

    signal_txt = ", ".join([k for k, v in signals.items() if isinstance(v, bool) and v])
    extra_txt = "; ".join(extras)

    return (
        f"{pick['bet']} selected in {pick['match']} at line {pick['line']}. "
        f"V2 expected total games: {pick['expected_total_games']:.2f}; base model {pick['base_expected_total_games']:.2f}. "
        f"Model probability {pick['model_prob'] * 100:.1f}% versus implied {pick['implied_prob'] * 100:.1f}% "
        f"from best odds {pick['odds']:.2f}. Edge {pick['edge'] * 100:+.1f}%. "
        f"Profile: {pick['v2_profile']}. "
        f"{'Market features: ' + extra_txt + '. ' if extra_txt else ''}"
        f"{'Active signals: ' + signal_txt + '. ' if signal_txt else ''}"
        f"Bookmakers used: {pick['bookmakers_used']}. Confidence {pick['confidence']:.1f}, quality {pick['quality_score']:.1f}."
    )


# ============================================================
# MAIN
# ============================================================

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
        "model_version": MODEL_VERSION,
        "fixtures_total": len(fixtures),
        "scanned": 0,
        "with_odds": 0,
        "with_match_total_market": 0,
        "skipped": [],
        "candidates_raw": 0,
        "final_picks": 0,
        "errors": [],
        "market_feature_coverage": {
            "match_total_center": 0,
            "player_total_sum_center": 0,
            "three_set_prob_no_vig": 0,
            "handicap_abs_center": 0,
            "first_set_total_center": 0,
            "second_set_total_center": 0,
        },
    }

    h2h_cache = {}

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

            debug["with_odds"] += 1

            totals_lines = parse_match_total_candidates(odds_blob)
            if not totals_lines:
                debug["skipped"].append({"event_key": event_key, "match": name, "reason": "no_match_total_candidates"})
                continue

            debug["with_match_total_market"] += 1

            market_features = build_market_features_v2(odds_blob)
            for k in debug["market_feature_coverage"].keys():
                if market_features.get(k) is not None:
                    debug["market_feature_coverage"][k] += 1

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
            base_exp_games = base_expected_total_games(first_form, second_form, h2h_matches, market_info)
            exp_games = market_adjusted_expected_games(base_exp_games, market_features)

            for line_info in totals_lines:
                line = safe_float(line_info.get("line"))
                bookmakers_used = safe_int(line_info.get("bookmakers_used"))

                for side in ["over", "under"]:
                    side_info = line_info.get(side) or {}
                    odds = safe_float(side_info.get("best_odds"))
                    median_odds = safe_float(side_info.get("median_odds"))
                    avg_odds = safe_float(side_info.get("avg_odds"))
                    bookmaker = side_info.get("best_bookmaker") or "unknown"

                    if odds < ODDS_MIN or odds > ODDS_MAX:
                        continue

                    model_prob = model_probability(exp_games, line, side, market_features)
                    implied_prob = 1 / odds
                    edge = model_prob - implied_prob
                    margin_abs = abs(exp_games - line)

                    if edge < MIN_EDGE:
                        continue

                    signals = build_signals(side, line, exp_games, base_exp_games, market_features, first_form, second_form)
                    profile = assign_profile(side, line, signals, market_features)

                    confidence = confidence_score(side, exp_games, line, model_prob, bookmakers_used, odds, signals, market_features)
                    if confidence < MIN_CONFIDENCE:
                        continue

                    quality = quality_score(side, confidence, edge, bookmakers_used, odds, matches_min, margin_abs, signals)
                    if quality < MIN_QUALITY:
                        continue

                    # Soft safety for over high line without confirmations.
                    if side == "over" and line >= 22.5:
                        needed = sum(1 for k in ["three_set_support", "set_totals_confirm", "player_totals_confirm", "form_total_support"] if signals.get(k))
                        if needed < 2:
                            continue

                    # Soft safety for over against obvious blowout.
                    if side == "over" and signals.get("blowout_risk") and not signals.get("three_set_support"):
                        continue

                    stake, stake_label = stake_from_quality(quality, edge, profile, side, line)

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
                        "market": MATCH_TOTAL_MARKET,
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
                        "market_avg_odds": round(avg_odds, 3),
                        "bookmakers_used": bookmakers_used,
                        "match_total_market_no_vig": line_info.get("market_no_vig"),
                        "model_prob": model_prob,
                        "implied_prob": round(implied_prob, 4),
                        "edge": round(edge, 4),
                        "base_expected_total_games": base_exp_games,
                        "expected_total_games": exp_games,
                        "expected_margin": round(exp_games - line, 3),
                        "confidence": confidence,
                        "quality_score": quality,
                        "stake": stake,
                        "stake_label": stake_label,
                        "v2_profile": profile,
                        "market_features_v2": market_features,
                        "signals": signals,
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
            safe_float(x.get("edge")),
            safe_float(x.get("confidence")),
            safe_float(x.get("bookmakers_used")),
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
        "model_version": MODEL_VERSION,
        "stake_mode": "quality_based_shadow",
        "market": MATCH_TOTAL_MARKET,
        "filters": {
            "days_ahead": DAYS_AHEAD,
            "max_picks": MAX_PICKS,
            "max_over_picks": MAX_OVER_PICKS,
            "max_under_picks": MAX_UNDER_PICKS,
            "min_recent_matches_each": MIN_RECENT_MATCHES_EACH,
            "min_bookmakers_match_total": MIN_BOOKMAKERS_MATCH_TOTAL,
            "min_edge": MIN_EDGE,
            "min_confidence": MIN_CONFIDENCE,
            "min_quality": MIN_QUALITY,
            "odds_min": ODDS_MIN,
            "odds_max": ODDS_MAX,
            "main_lines_min": MAIN_LINES_MIN,
            "main_lines_max": MAIN_LINES_MAX,
            "model_prob_min": MODEL_PROB_MIN,
            "model_prob_max": MODEL_PROB_MAX,
        },
        "summary": {
            "fixtures_checked": len(fixtures),
            "scanned": debug["scanned"],
            "with_odds": debug["with_odds"],
            "with_match_total_market": debug["with_match_total_market"],
            "candidates_raw": len(candidates),
            "final_picks": len(final),
            "errors": len(debug["errors"]),
            "market_feature_coverage": debug["market_feature_coverage"],
        },
        "picks": final,
    }

    candidates_payload = {
        "generated_at": now_iso(),
        "model_version": MODEL_VERSION,
        "count": len(candidates),
        "candidates": candidates,
    }

    debug["final_picks"] = len(final)

    save_json(PREDICTIONS_FILE, payload)
    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)
    save_json(CANDIDATES_FILE, candidates_payload)

    print("")
    print(f"TENNIS TOTALS V2 WIDE SHADOW DONE: candidates={len(candidates)} final={len(final)} results_total={len(results)}")
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {DEBUG_FILE}")
    print(f"Saved {CANDIDATES_FILE}")


if __name__ == "__main__":
    main()

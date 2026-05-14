import os
import re
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

MODEL_VERSION = "ai77_tennis_totals_v2_wide_shadow"
MODEL_NAME = "AI77 Tennis Totals V2 Wide Shadow"
MARKET_NAME = "Over/Under by Games in Match"

PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_predictions_v2_wide_shadow.json"
RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results_v2_wide_shadow.json"
DEBUG_FILE = f"{DATA_DIR}/tennis_totals_debug_v2_wide_shadow.json"
CANDIDATES_FILE = f"{DATA_DIR}/tennis_totals_candidates_v2_wide_shadow.json"

DAYS_AHEAD = int(os.getenv("DAYS_AHEAD", "2"))
MAX_FIXTURES = int(os.getenv("MAX_FIXTURES", "900"))
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = float(os.getenv("API_SLEEP_SECONDS", "0.30"))

MAX_PICKS = int(os.getenv("MAX_PICKS", "30"))
MAX_OVER_PICKS = int(os.getenv("MAX_OVER_PICKS", "18"))
MAX_UNDER_PICKS = int(os.getenv("MAX_UNDER_PICKS", "18"))

MIN_RECENT_MATCHES_EACH = int(os.getenv("MIN_RECENT_MATCHES_EACH", "4"))

# Za prvi test naj bo 2. Ko boš videl, da kandidati prihajajo, lahko dvigneš na 3/4/5.
MIN_BOOKMAKERS = int(os.getenv("MIN_BOOKMAKERS", "2"))

MIN_EDGE = float(os.getenv("MIN_EDGE", "0.025"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "55.0"))

ODDS_MIN = float(os.getenv("ODDS_MIN", "1.45"))
ODDS_MAX = float(os.getenv("ODDS_MAX", "2.60"))

MODEL_PROB_MIN = 0.38
MODEL_PROB_MAX = 0.68

MAIN_LINES_MIN = float(os.getenv("MAIN_LINES_MIN", "16.5"))
MAIN_LINES_MAX = float(os.getenv("MAIN_LINES_MAX", "27.5"))


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
    status = str(match.get("event_status") or "").lower().strip()
    live = str(match.get("event_live") or "0").strip()

    if live == "1":
        return False

    bad_statuses = {
        "finished",
        "cancelled",
        "postponed",
        "retired",
        "walkover",
        "interrupted",
        "abandoned",
        "suspended",
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

    if "singles" in event_type:
        return True

    # API včasih ne napiše lepo singles, zato pustimo solo imena skozi.
    return True


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
            a = int(parts[0])
            b = int(parts[1])

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

    if first != player_key and second != player_key:
        return 0

    diff = 0

    for a, b in parse_scores(match.get("scores")):
        diff += a - b

    if second == player_key:
        diff *= -1

    return diff


def set_diff_for_player(match, player_key):
    player_key = safe_int(player_key)

    first = safe_int(match.get("first_player_key"))
    second = safe_int(match.get("second_player_key"))

    if first != player_key and second != player_key:
        return 0

    diff = 0

    for a, b in parse_scores(match.get("scores")):
        if a > b:
            diff += 1
        elif b > a:
            diff -= 1

    if second == player_key:
        diff *= -1

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

    recent = matches[:25]

    def window_stats(n):
        arr = recent[:n]

        if not arr:
            return {
                "matches": 0,
                "avg_total_games": 0.0,
                "median_total_games": 0.0,
                "over_20_5_rate": 0.0,
                "over_21_5_rate": 0.0,
                "over_22_5_rate": 0.0,
                "over_23_5_rate": 0.0,
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
            "over_20_5_rate": round(sum(1 for x in totals if x > 20.5) / len(totals), 4),
            "over_21_5_rate": round(sum(1 for x in totals if x > 21.5) / len(totals), 4),
            "over_22_5_rate": round(sum(1 for x in totals if x > 22.5) / len(totals), 4),
            "over_23_5_rate": round(sum(1 for x in totals if x > 23.5) / len(totals), 4),
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


def _line_from_text(text):
    text = str(text or "")
    hits = re.findall(r"(?<!\d)(\d{1,2}(?:\.5|\.0)?)(?!\d)", text)

    for h in hits:
        line = safe_float(h, None)

        if line is None:
            continue

        if MAIN_LINES_MIN <= line <= MAIN_LINES_MAX:
            return line

    return None


def _side_from_text(text):
    t = str(text or "").lower()

    if "over" in t:
        return "over"

    if "under" in t:
        return "under"

    return None


def _looks_like_line(text):
    line = safe_float(text, None)

    if line is None:
        return False

    return MAIN_LINES_MIN <= line <= MAIN_LINES_MAX


def _bookmaker_from_path(path):
    cleaned = []

    for p in path:
        s = str(p or "").strip()
        low = s.lower()

        if not s:
            continue

        if _looks_like_line(s):
            continue

        if "over" in low or "under" in low:
            continue

        if "games in match" in low:
            continue

        if low in {
            "over/under",
            "over/under by games in match",
            "match total",
            "total",
            "line",
            "odds",
            "value",
        }:
            continue

        cleaned.append(s)

    if cleaned:
        return cleaned[-1]

    return "unknown"


def _walk_totals_market(obj, path, rows):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_totals_market(v, path + [k], rows)
        return

    if isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_totals_market(v, path + [str(i)], rows)
        return

    odds = safe_float(obj, None)

    if odds is None or odds <= 1:
        return

    joined = " ".join(str(x) for x in path)

    side = _side_from_text(joined)
    line = _line_from_text(joined)

    if side not in {"over", "under"}:
        return

    if line is None:
        return

    bookmaker = _bookmaker_from_path(path)

    rows.append({
        "side": side,
        "line": line,
        "bookmaker": bookmaker,
        "odds": odds,
        "path": path,
    })


def parse_totals_market(odds_blob):
    """
    Robust parser za API-Tennis totals.

    Podpira več struktur:
    1) market["Over/Under by Games in Match Over"]["22.5"]["Book"] = 1.90
    2) market["Over"]["22.5"]["Book"] = 1.90
    3) market["22.5"]["Over"]["Book"] = 1.90
    4) market["Book"]["Over"]["22.5"] = 1.90
    5) market["Over 22.5"]["Book"] = 1.90
    """

    market = odds_blob.get(MARKET_NAME)

    if not isinstance(market, dict):
        return []

    rows = []
    _walk_totals_market(market, [MARKET_NAME], rows)

    grouped = {}

    for row in rows:
        side = row["side"]
        line = row["line"]
        bookmaker = row["bookmaker"]
        odds = row["odds"]

        if not (MAIN_LINES_MIN <= line <= MAIN_LINES_MAX):
            continue

        key = line

        if key not in grouped:
            grouped[key] = {
                "over": {},
                "under": {},
                "raw_rows": [],
            }

        old = grouped[key][side].get(bookmaker)

        if old is None or odds > old:
            grouped[key][side][bookmaker] = odds

        grouped[key]["raw_rows"].append(row)

    candidates = []

    for line, data in grouped.items():
        over_books = data.get("over") or {}
        under_books = data.get("under") or {}

        if not over_books or not under_books:
            continue

        shared_books = sorted(set(over_books) & set(under_books))

        if shared_books:
            over_values = [over_books[b] for b in shared_books]
            under_values = [under_books[b] for b in shared_books]
            books_used = len(shared_books)
        else:
            over_values = list(over_books.values())
            under_values = list(under_books.values())
            books_used = min(len(over_values), len(under_values))

        if books_used < MIN_BOOKMAKERS:
            continue

        over_best_book = max(over_books, key=lambda b: over_books[b])
        under_best_book = max(under_books, key=lambda b: under_books[b])

        candidates.append({
            "line": float(line),
            "bookmakers_used": books_used,
            "over": {
                "best_odds": round(over_books[over_best_book], 3),
                "best_bookmaker": over_best_book,
                "median_odds": round(median(over_values), 3),
            },
            "under": {
                "best_odds": round(under_books[under_best_book], 3),
                "best_bookmaker": under_best_book,
                "median_odds": round(median(under_values), 3),
            },
            "parser_rows_found": len(data.get("raw_rows") or []),
        })

    candidates.sort(key=lambda x: x["line"])

    return candidates


def extract_number_of_sets_market(odds_blob):
    market = odds_blob.get("Number of sets")

    if not isinstance(market, dict):
        return None

    flat = []

    def walk(obj, path):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, path + [k])
            return

        odds = safe_float(obj, None)

        if odds is None or odds <= 1:
            return

        joined = " ".join(str(x).lower() for x in path)

        flat.append((joined, odds))

    walk(market, ["Number of sets"])

    three_odds = []
    two_odds = []

    for label, odds in flat:
        if "3" in label:
            three_odds.append(odds)
        elif "2" in label:
            two_odds.append(odds)

    if not three_odds or not two_odds:
        return None

    o2 = median(two_odds)
    o3 = median(three_odds)

    p2_raw = 1 / o2
    p3_raw = 1 / o3
    total = p2_raw + p3_raw

    if total <= 0:
        return None

    return {
        "two_sets_median_odds": round(o2, 3),
        "three_sets_median_odds": round(o3, 3),
        "two_set_prob_no_vig": round(p2_raw / total, 4),
        "three_set_prob_no_vig": round(p3_raw / total, 4),
    }


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def expected_total_games(player_form, opponent_form, h2h_matches, market_info, sets_market):
    p5 = player_form["last_5"]
    p10 = player_form["last_10"]
    o5 = opponent_form["last_5"]
    o10 = opponent_form["last_10"]

    p10_total = safe_float(p10.get("median_total_games")) * 0.65 + safe_float(p10.get("avg_total_games")) * 0.35
    o10_total = safe_float(o10.get("median_total_games")) * 0.65 + safe_float(o10.get("avg_total_games")) * 0.35

    p5_total = safe_float(p5.get("median_total_games")) * 0.60 + safe_float(p5.get("avg_total_games")) * 0.40
    o5_total = safe_float(o5.get("median_total_games")) * 0.60 + safe_float(o5.get("avg_total_games")) * 0.40

    avg_recent = (
        p10_total * 0.32 +
        o10_total * 0.32 +
        p5_total * 0.18 +
        o5_total * 0.18
    )

    three_set_rate = (
        safe_float(p10.get("three_set_rate")) +
        safe_float(o10.get("three_set_rate"))
    ) / 2

    close_set_rate = (
        safe_float(p10.get("close_set_rate")) +
        safe_float(o10.get("close_set_rate"))
    ) / 2

    p_strength = player_strength_score(player_form)
    o_strength = player_strength_score(opponent_form)
    strength_gap = abs(p_strength - o_strength)

    exp = avg_recent

    exp += (three_set_rate - 0.28) * 4.4
    exp += (close_set_rate - 0.36) * 2.9

    if strength_gap >= 32:
        exp -= 2.2
    elif strength_gap >= 24:
        exp -= 1.45
    elif strength_gap >= 17:
        exp -= 0.75
    elif strength_gap <= 8:
        exp += 1.0

    if market_info:
        gap = safe_float(market_info.get("market_gap"))

        if gap >= 0.55:
            exp -= 2.7
        elif gap >= 0.40:
            exp -= 2.0
        elif gap >= 0.26:
            exp -= 1.4
        elif gap >= 0.18:
            exp -= 0.8
        elif gap <= 0.08:
            exp += 0.8

    if sets_market:
        three_prob = safe_float(sets_market.get("three_set_prob_no_vig"))

        if three_prob:
            exp += (three_prob - 0.30) * 5.5

    h2h_finished = clean_finished_matches(h2h_matches)

    if h2h_finished:
        h2h_finished = sorted(
            h2h_finished,
            key=lambda x: (x.get("event_date") or "", x.get("event_time") or ""),
            reverse=True,
        )

        h2h_totals = [total_games_from_scores(m.get("scores")) for m in h2h_finished[:5]]
        h2h_avg = sum(h2h_totals) / len(h2h_totals)

        exp = exp * 0.86 + h2h_avg * 0.14

    return round(clamp(exp, 15.5, 30.5), 2)


def model_probability(expected_games, line, side):
    diff = expected_games - line

    p_over = sigmoid(diff / 3.05)
    p_over = clamp(p_over, MODEL_PROB_MIN, MODEL_PROB_MAX)

    if side == "over":
        return round(p_over, 4)

    return round(1 - p_over, 4)


def confidence_score(expected_games, line, model_prob, bookmakers_used, odds):
    margin = abs(expected_games - line)

    c = 48
    c += clamp(margin / 3.2, 0, 1) * 22
    c += clamp((model_prob - 0.5) / 0.14, 0, 1) * 15
    c += clamp(bookmakers_used / 8, 0, 1) * 8

    if 1.70 <= odds <= 2.10:
        c += 5
    elif 1.55 <= odds <= 2.35:
        c += 3

    return round(clamp(c, 1, 96), 1)


def quality_score(confidence, edge, bookmakers_used, odds, matches_min, margin):
    q = 0
    q += clamp(confidence / 88, 0, 1) * 30
    q += clamp(edge / 0.10, 0, 1) * 30
    q += clamp(bookmakers_used / 8, 0, 1) * 14
    q += clamp(matches_min / 12, 0, 1) * 12
    q += clamp(margin / 3.2, 0, 1) * 9

    if 1.70 <= odds <= 2.10:
        q += 5
    elif 1.55 <= odds <= 2.35:
        q += 3

    return round(clamp(q, 1, 99), 1)


def stake_from_quality(quality, edge):
    if quality >= 88 and edge >= 0.09:
        return 1.0, "Top Rated"

    if quality >= 80 and edge >= 0.07:
        return 0.75, "Strong"

    if quality >= 68:
        return 0.5, "Standard"

    return 0.25, "Small Value"


def pick_id_for(event_key, side, line):
    raw = f"{MODEL_VERSION}:{event_key}:{side}:{line}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_reasoning(pick):
    return (
        f"{pick['bet']} selected in {pick['match']} at line {pick['line']}. "
        f"Expected total games: {pick['expected_total_games']:.2f}; market line: {pick['line']:.1f}. "
        f"Model probability {pick['model_prob'] * 100:.1f}% versus implied {pick['implied_prob'] * 100:.1f}% "
        f"from best odds {pick['odds']:.2f}. Edge: {pick['edge'] * 100:+.1f}%. "
        f"Bookmakers used: {pick['bookmakers_used']}. Confidence: {pick['confidence']:.1f}. "
        f"Quality: {pick['quality_score']:.1f}."
    )


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
            "number_of_sets": 0,
            "home_away": 0,
        },
        "market_probe": None,
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

            debug["with_odds"] += 1

            markets = list(odds_blob.keys())

            if debug["market_probe"] is None:
                debug["market_probe"] = {
                    "event_key": event_key,
                    "match": name,
                    "markets": markets,
                }

            if isinstance(odds_blob.get(MARKET_NAME), dict):
                debug["with_match_total_market"] += 1

            totals_lines = parse_totals_market(odds_blob)

            if not totals_lines:
                debug["skipped"].append({
                    "event_key": event_key,
                    "match": name,
                    "reason": "no_match_total_candidates",
                    "markets": markets,
                })
                continue

            debug["market_feature_coverage"]["match_total_center"] += 1

            market_info = extract_home_away_odds(odds_blob)

            if market_info:
                debug["market_feature_coverage"]["home_away"] += 1

            sets_market = extract_number_of_sets_market(odds_blob)

            if sets_market:
                debug["market_feature_coverage"]["number_of_sets"] += 1

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
                    "markets": markets,
                })
                continue

            exp_games = expected_total_games(
                first_form,
                second_form,
                h2h_matches,
                market_info,
                sets_market,
            )

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

                        if side == "under" and line >= 24.5 and market_gap <= 0.06:
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

                    stake, stake_label = stake_from_quality(quality, edge)

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
                        "stake": stake,
                        "stake_label": stake_label,
                        "market_info": market_info,
                        "sets_market": sets_market,
                        "line_parser_info": {
                            "parser_rows_found": line_info.get("parser_rows_found"),
                        },
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
            debug["errors"].append({
                "event_key": event_key,
                "match": name,
                "error": str(e),
            })

            print(f"ERROR {event_key} {name}: {e}")

    debug["candidates_raw"] = len(candidates)

    candidates.sort(
        key=lambda x: (
            safe_float(x.get("quality_score")),
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

    results.sort(
        key=lambda x: (
            x.get("date") or "",
            x.get("time") or "",
            x.get("match") or "",
        )
    )

    debug["final_picks"] = len(final)

    payload = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "stake_mode": "quality_based",
        "market": MARKET_NAME,
        "filters": {
            "days_ahead": DAYS_AHEAD,
            "max_fixtures": MAX_FIXTURES,
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
        "summary": {
            "fixtures_checked": len(fixtures),
            "scanned": debug["scanned"],
            "with_odds": debug["with_odds"],
            "with_match_total_market": debug["with_match_total_market"],
            "candidates_raw": len(candidates),
            "final_picks": len(final),
            "errors": len(debug["errors"]),
        },
        "picks": final,
    }

    save_json(PREDICTIONS_FILE, payload)
    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)
    save_json(CANDIDATES_FILE, candidates)

    print("")
    print(f"TENNIS TOTALS V2 WIDE SHADOW DONE: candidates={len(candidates)} final={len(final)} results_total={len(results)}")
    print(f"Saved {PREDICTIONS_FILE}")
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {DEBUG_FILE}")
    print(f"Saved {CANDIDATES_FILE}")


if __name__ == "__main__":
    main()

import os
import json
import math
import time
import statistics
import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

import requests


# =========================
# CONFIG
# =========================

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
PREDICTIONS_FILE = os.path.join(DATA_DIR, "tennis_predictions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_results.json")
DEBUG_FILE = os.path.join(DATA_DIR, "tennis_debug.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35

# Dates to scan
DAYS_AHEAD = 2

# Pick limits
MAX_PICKS = 5

# Strict filters
MIN_RECENT_MATCHES_EACH = 6
MIN_BOOKMAKERS = 5
MIN_EDGE = 0.065
MIN_CONFIDENCE = 72.0

ODDS_MIN = 1.60
ODDS_MAX = 2.85

# Avoid low-quality / unstable contexts if needed
SKIP_LIVE = True
SKIP_FINISHED = True

# Model probability cap
MODEL_PROB_MIN = 0.40
MODEL_PROB_MAX = 0.66

# Odds sanity
MAX_BEST_TO_MEDIAN_GAP = 0.18  # 18% max difference from median


# =========================
# HELPERS
# =========================

def debug(msg):
    print(msg)


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_json(path, data):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def safe_float(value, default=None):
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


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def median(values):
    vals = [safe_float(v) for v in values]
    vals = [v for v in vals if v is not None and v > 1.0]

    if not vals:
        return None

    return float(statistics.median(vals))


def avg(values, default=0.0):
    vals = [v for v in values if isinstance(v, (int, float))]
    if not vals:
        return default
    return sum(vals) / len(vals)


def pct(part, total):
    if not total:
        return 0.0
    return part / total


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def build_pick_id(event_key, side, player_key, odds=None):
    raw = f"tennis_value_v1|{event_key}|{side}|{player_key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def parse_match_date_time(match):
    date_s = match.get("event_date")
    time_s = match.get("event_time") or "00:00"

    try:
        dt = datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=ZoneInfo(TZ_NAME))
    except Exception:
        return None


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

            data = res.json()
            return data

        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 * (attempt + 1)
            debug(f"API exception {e}, sleeping {wait}s")
            time.sleep(wait)

    raise RuntimeError("API failed after retries")


# =========================
# API FETCHERS
# =========================

def fetch_fixtures_for_date(date_value):
    date_s = date_value.strftime("%Y-%m-%d")

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

    if not isinstance(result, list):
        return []

    debug(f"FIXTURES {date_s}: {len(result)}")
    return result


def fetch_all_fixtures():
    start = today_local()
    out = []

    for i in range(DAYS_AHEAD):
        date_value = start + timedelta(days=i)
        out.extend(fetch_fixtures_for_date(date_value))

    return out


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


# =========================
# ODDS PARSING
# =========================

def parse_home_away_odds(odds_blob):
    market = odds_blob.get("Home/Away")

    if not isinstance(market, dict):
        return None

    home = market.get("Home") or {}
    away = market.get("Away") or {}

    if not isinstance(home, dict) or not isinstance(away, dict):
        return None

    home_odds = []
    away_odds = []

    for book, odd in home.items():
        value = safe_float(odd)
        if value and value > 1:
            home_odds.append({
                "bookmaker": book,
                "odds": value,
            })

    for book, odd in away.items():
        value = safe_float(odd)
        if value and value > 1:
            away_odds.append({
                "bookmaker": book,
                "odds": value,
            })

    if not home_odds or not away_odds:
        return None

    home_values = [x["odds"] for x in home_odds]
    away_values = [x["odds"] for x in away_odds]

    home_best = max(home_odds, key=lambda x: x["odds"])
    away_best = max(away_odds, key=lambda x: x["odds"])

    home_median = median(home_values)
    away_median = median(away_values)

    common_books = set(x["bookmaker"] for x in home_odds) & set(x["bookmaker"] for x in away_odds)

    return {
        "home": {
            "best_odds": home_best["odds"],
            "best_bookmaker": home_best["bookmaker"],
            "median_odds": home_median,
            "bookmakers": len(home_odds),
            "raw": home_odds,
        },
        "away": {
            "best_odds": away_best["odds"],
            "best_bookmaker": away_best["bookmaker"],
            "median_odds": away_median,
            "bookmakers": len(away_odds),
            "raw": away_odds,
        },
        "bookmakers_used": min(len(home_odds), len(away_odds), len(common_books) if common_books else 999),
    }


def odds_are_sane(best_odds, median_odds):
    if not best_odds or not median_odds:
        return False

    gap = (best_odds - median_odds) / median_odds

    if gap > MAX_BEST_TO_MEDIAN_GAP:
        return False

    return True


# =========================
# RESULT / FORM PARSING
# =========================

def get_match_winner_side(match, player_key):
    winner = match.get("event_winner")

    first_key = safe_int(match.get("first_player_key"))
    second_key = safe_int(match.get("second_player_key"))
    player_key = safe_int(player_key)

    if winner == "First Player":
        winner_key = first_key
    elif winner == "Second Player":
        winner_key = second_key
    else:
        return None

    return winner_key == player_key


def parse_final_sets(match, player_key):
    """
    Returns:
    sets_for, sets_against, games_for, games_against
    """
    first_key = safe_int(match.get("first_player_key"))
    second_key = safe_int(match.get("second_player_key"))
    player_key = safe_int(player_key)

    scores = match.get("scores") or []

    sets_for = 0
    sets_against = 0
    games_for = 0
    games_against = 0

    for s in scores:
        a = safe_int(s.get("score_first"))
        b = safe_int(s.get("score_second"))

        if player_key == first_key:
            gf, ga = a, b
        elif player_key == second_key:
            gf, ga = b, a
        else:
            continue

        games_for += gf
        games_against += ga

        if gf > ga:
            sets_for += 1
        elif ga > gf:
            sets_against += 1

    return sets_for, sets_against, games_for, games_against


def normalize_player_results(raw_results, player_key, current_event_key=None):
    rows = []

    if not isinstance(raw_results, list):
        return rows

    for match in raw_results:
        if str(match.get("event_status") or "").lower() != "finished":
            continue

        if current_event_key and str(match.get("event_key")) == str(current_event_key):
            continue

        won = get_match_winner_side(match, player_key)
        if won is None:
            continue

        sets_for, sets_against, games_for, games_against = parse_final_sets(match, player_key)

        if sets_for + sets_against <= 0:
            continue

        date_s = match.get("event_date") or ""

        rows.append({
            "event_key": match.get("event_key"),
            "date": date_s,
            "won": bool(won),
            "sets_for": sets_for,
            "sets_against": sets_against,
            "set_diff": sets_for - sets_against,
            "games_for": games_for,
            "games_against": games_against,
            "game_diff": games_for - games_against,
            "straight_win": bool(won and sets_against == 0),
            "straight_loss": bool((not won) and sets_for == 0),
            "close_loss": bool((not won) and sets_for > 0),
            "event_type_type": match.get("event_type_type") or "",
            "tournament_name": match.get("tournament_name") or "",
            "event_qualification": str(match.get("event_qualification") or "").lower() == "true",
        })

    rows.sort(key=lambda x: x.get("date") or "", reverse=True)
    return rows


def h2h_score(h2h_rows, first_player_key, second_player_key):
    if not isinstance(h2h_rows, list) or not h2h_rows:
        return {
            "matches": 0,
            "first_wins": 0,
            "second_wins": 0,
            "first_score": 0.0,
            "second_score": 0.0,
        }

    first_wins = 0
    second_wins = 0
    usable = 0

    for match in h2h_rows:
        if str(match.get("event_status") or "").lower() != "finished":
            continue

        winner = match.get("event_winner")
        first_key = safe_int(match.get("first_player_key"))
        second_key = safe_int(match.get("second_player_key"))

        if winner == "First Player":
            winner_key = first_key
        elif winner == "Second Player":
            winner_key = second_key
        else:
            continue

        if winner_key == safe_int(first_player_key):
            first_wins += 1
            usable += 1
        elif winner_key == safe_int(second_player_key):
            second_wins += 1
            usable += 1

    if usable == 0:
        return {
            "matches": 0,
            "first_wins": 0,
            "second_wins": 0,
            "first_score": 0.0,
            "second_score": 0.0,
        }

    first_rate = first_wins / usable
    second_rate = second_wins / usable

    # Keep H2H small; tennis H2H can be stale/noisy.
    return {
        "matches": usable,
        "first_wins": first_wins,
        "second_wins": second_wins,
        "first_score": round((first_rate - 0.5) * 6, 3),
        "second_score": round((second_rate - 0.5) * 6, 3),
    }


def form_summary(rows):
    total = len(rows)

    if total == 0:
        return {
            "matches": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "set_diff_avg": 0,
            "game_diff_avg": 0,
            "straight_win_rate": 0,
            "straight_loss_rate": 0,
            "close_loss_rate": 0,
            "fatigue_matches_7d": 0,
            "fatigue_matches_3d": 0,
        }

    wins = sum(1 for r in rows if r["won"])
    losses = total - wins

    today = today_local()

    fatigue_7d = 0
    fatigue_3d = 0

    for r in rows:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            days_ago = (today - d).days
            if 0 <= days_ago <= 7:
                fatigue_7d += 1
            if 0 <= days_ago <= 3:
                fatigue_3d += 1
        except Exception:
            pass

    return {
        "matches": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / total, 4),
        "set_diff_avg": round(avg([r["set_diff"] for r in rows]), 4),
        "game_diff_avg": round(avg([r["game_diff"] for r in rows]), 4),
        "straight_win_rate": round(pct(sum(1 for r in rows if r["straight_win"]), total), 4),
        "straight_loss_rate": round(pct(sum(1 for r in rows if r["straight_loss"]), total), 4),
        "close_loss_rate": round(pct(sum(1 for r in rows if r["close_loss"]), total), 4),
        "fatigue_matches_7d": fatigue_7d,
        "fatigue_matches_3d": fatigue_3d,
    }


def player_strength(rows, h2h_adj=0.0):
    """
    Weighted player strength from recent matches.
    Designed conservative, not overconfident.
    """
    last_5 = rows[:5]
    last_10 = rows[:10]
    last_20 = rows[:20]

    s5 = form_summary(last_5)
    s10 = form_summary(last_10)
    s20 = form_summary(last_20)

    score = 50.0

    # Win rate
    score += (s5["win_rate"] - 0.5) * 22
    score += (s10["win_rate"] - 0.5) * 18
    score += (s20["win_rate"] - 0.5) * 10

    # Set dominance
    score += clamp(s10["set_diff_avg"], -1.5, 1.5) * 6

    # Game dominance
    score += clamp(s10["game_diff_avg"] / 5.0, -1.5, 1.5) * 5

    # Straight sets quality
    score += s10["straight_win_rate"] * 5
    score -= s10["straight_loss_rate"] * 6

    # Close losses are better than heavy losses
    score += s10["close_loss_rate"] * 2

    # Fatigue penalty
    score -= clamp(s10["fatigue_matches_3d"] - 1, 0, 4) * 1.8
    score -= clamp(s10["fatigue_matches_7d"] - 3, 0, 6) * 0.8

    # H2H small adjustment
    score += h2h_adj

    return {
        "score": round(clamp(score, 20, 80), 3),
        "last_5": s5,
        "last_10": s10,
        "last_20": s20,
    }


def probability_from_scores(score_a, score_b):
    diff = score_a - score_b

    # Conservative logistic.
    raw = 1 / (1 + math.exp(-(diff / 13.5)))

    return clamp(raw, MODEL_PROB_MIN, MODEL_PROB_MAX)


def confidence_score(model_prob, score_diff, edge, bookmakers_used, matches_min, odds, best_median_gap):
    conf = 45.0

    conf += clamp(abs(model_prob - 0.5) / 0.20, 0, 1) * 18
    conf += clamp(abs(score_diff) / 18, 0, 1) * 14
    conf += clamp(edge / 0.12, 0, 1) * 18
    conf += clamp(bookmakers_used / 10, 0, 1) * 9
    conf += clamp(matches_min / 14, 0, 1) * 8

    if 1.70 <= odds <= 2.35:
        conf += 5
    elif 1.55 <= odds <= 2.75:
        conf += 3

    # Penalize outlier best price
    conf -= clamp(best_median_gap / MAX_BEST_TO_MEDIAN_GAP, 0, 1) * 5

    return round(clamp(conf, 1, 88), 1)


def quality_score(confidence, edge, bookmakers_used, odds, matches_min):
    q = 0.0

    q += clamp(confidence / 100, 0, 1) * 35
    q += clamp(edge / 0.14, 0, 1) * 35
    q += clamp(bookmakers_used / 10, 0, 1) * 15
    q += clamp(matches_min / 14, 0, 1) * 10

    if 1.70 <= odds <= 2.40:
        q += 5
    elif 1.55 <= odds <= 2.80:
        q += 3

    return round(clamp(q, 1, 99), 1)


# =========================
# CANDIDATE BUILDING
# =========================

def is_match_eligible(match):
    status = str(match.get("event_status") or "").lower()

    if SKIP_FINISHED and status == "finished":
        return False

    if SKIP_LIVE and str(match.get("event_live") or "0") == "1":
        return False

    if status in {"finished", "cancelled", "postponed", "retired", "walkover"}:
        return False

    if not match.get("event_key"):
        return False

    if not match.get("first_player_key") or not match.get("second_player_key"):
        return False

    if not match.get("event_first_player") or not match.get("event_second_player"):
        return False

    return True


def tournament_context(match):
    event_type = str(match.get("event_type_type") or "")
    tournament_name = str(match.get("tournament_name") or "")
    round_name = str(match.get("tournament_round") or "")
    qualification = str(match.get("event_qualification") or "").lower() == "true"

    text = f"{event_type} {tournament_name} {round_name}".lower()

    if "women" in text or "wta" in text:
        tour_gender = "women"
    elif "men" in text or "atp" in text:
        tour_gender = "men"
    else:
        tour_gender = "unknown"

    if "itf" in text:
        level = "itf"
    elif "challenger" in text:
        level = "challenger"
    elif "atp" in text:
        level = "atp"
    elif "wta" in text:
        level = "wta"
    else:
        level = "other"

    return {
        "gender": tour_gender,
        "level": level,
        "qualification": qualification,
    }


def build_candidate(match):
    event_key = match.get("event_key")
    first_key = safe_int(match.get("first_player_key"))
    second_key = safe_int(match.get("second_player_key"))

    first_name = match.get("event_first_player")
    second_name = match.get("event_second_player")

    odds_blob = fetch_odds(event_key)
    parsed_odds = parse_home_away_odds(odds_blob)

    if not parsed_odds:
        return []

    bookmakers_used = parsed_odds["bookmakers_used"]

    if bookmakers_used < MIN_BOOKMAKERS:
        return []

    h2h = fetch_h2h(first_key, second_key)

    first_results_raw = h2h.get("firstPlayerResults") or []
    second_results_raw = h2h.get("secondPlayerResults") or []
    h2h_rows = h2h.get("H2H") or []

    first_rows = normalize_player_results(first_results_raw, first_key, current_event_key=event_key)
    second_rows = normalize_player_results(second_results_raw, second_key, current_event_key=event_key)

    if len(first_rows) < MIN_RECENT_MATCHES_EACH or len(second_rows) < MIN_RECENT_MATCHES_EACH:
        debug(f"SKIP low history {first_name} - {second_name}: {len(first_rows)} / {len(second_rows)}")
        return []

    h2h_data = h2h_score(h2h_rows, first_key, second_key)

    first_strength = player_strength(first_rows, h2h_adj=h2h_data["first_score"])
    second_strength = player_strength(second_rows, h2h_adj=h2h_data["second_score"])

    prob_first = probability_from_scores(first_strength["score"], second_strength["score"])
    prob_second = 1.0 - prob_first

    context = tournament_context(match)

    dt = parse_match_date_time(match)

    candidates = []

    sides = [
        {
            "side": "home",
            "market_side": "Home",
            "player_key": first_key,
            "player_name": first_name,
            "opponent_key": second_key,
            "opponent_name": second_name,
            "model_prob": prob_first,
            "player_strength": first_strength,
            "opponent_strength": second_strength,
            "score_diff": first_strength["score"] - second_strength["score"],
            "odds_data": parsed_odds["home"],
        },
        {
            "side": "away",
            "market_side": "Away",
            "player_key": second_key,
            "player_name": second_name,
            "opponent_key": first_key,
            "opponent_name": first_name,
            "model_prob": prob_second,
            "player_strength": second_strength,
            "opponent_strength": first_strength,
            "score_diff": second_strength["score"] - first_strength["score"],
            "odds_data": parsed_odds["away"],
        },
    ]

    for side in sides:
        odds = safe_float(side["odds_data"]["best_odds"])
        median_odds = safe_float(side["odds_data"]["median_odds"])

        if odds is None or median_odds is None:
            continue

        if odds < ODDS_MIN or odds > ODDS_MAX:
            continue

        if not odds_are_sane(odds, median_odds):
            continue

        implied_prob = 1 / odds
        edge = side["model_prob"] - implied_prob

        if edge < MIN_EDGE:
            continue

        best_median_gap = (odds - median_odds) / median_odds if median_odds else 0

        matches_min = min(
            side["player_strength"]["last_20"]["matches"],
            side["opponent_strength"]["last_20"]["matches"],
        )

        confidence = confidence_score(
            model_prob=side["model_prob"],
            score_diff=side["score_diff"],
            edge=edge,
            bookmakers_used=bookmakers_used,
            matches_min=matches_min,
            odds=odds,
            best_median_gap=best_median_gap,
        )

        if confidence < MIN_CONFIDENCE:
            continue

        quality = quality_score(
            confidence=confidence,
            edge=edge,
            bookmakers_used=bookmakers_used,
            odds=odds,
            matches_min=matches_min,
        )

        favorite_type = "favorite" if odds < 2.0 else "underdog"

        pick = {
            "pick_id": build_pick_id(event_key, side["side"], side["player_key"], odds),
            "event_key": event_key,
            "fixture_id": event_key,
            "sport": "tennis",
            "model_version": "ai77_tennis_value_v1",
            "date": dt.strftime("%Y-%m-%d") if dt else match.get("event_date"),
            "time": dt.strftime("%H:%M") if dt else match.get("event_time"),
            "match": f"{first_name} - {second_name}",
            "bet": side["player_name"],
            "bucket": "match_winner",
            "side": side["side"],
            "market_side": side["market_side"],
            "player_key": side["player_key"],
            "player_name": side["player_name"],
            "opponent_key": side["opponent_key"],
            "opponent_name": side["opponent_name"],
            "tournament": match.get("tournament_name") or "",
            "tournament_key": match.get("tournament_key"),
            "round": match.get("tournament_round") or "",
            "event_type": match.get("event_type_type") or "",
            "qualification": context["qualification"],
            "tour_level": context["level"],
            "gender": context["gender"],

            "odds": round(odds, 2),
            "best_bookmaker": side["odds_data"]["best_bookmaker"],
            "market_median_odds": round(median_odds, 2),
            "bookmakers_used": bookmakers_used,
            "best_to_median_gap": round(best_median_gap, 4),

            "model_prob": round(side["model_prob"], 4),
            "implied_prob": round(implied_prob, 4),
            "edge": round(edge, 4),

            "player_score": side["player_strength"]["score"],
            "opponent_score": side["opponent_strength"]["score"],
            "score_diff": round(side["score_diff"], 3),

            "confidence": confidence,
            "quality_score": quality,
            "stake": stake_from_quality(quality, edge, odds),
            "stake_label": stake_label_from_quality(quality),

            "favorite_type": favorite_type,
            "h2h": h2h_data,
            "player_form": side["player_strength"],
            "opponent_form": side["opponent_strength"],

            "result": "pending",
            "created_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),

            "reasoning": build_reasoning(
                player=side["player_name"],
                opponent=side["opponent_name"],
                tournament=match.get("tournament_name") or "",
                odds=odds,
                median_odds=median_odds,
                model_prob=side["model_prob"],
                implied_prob=implied_prob,
                edge=edge,
                confidence=confidence,
                player_strength=side["player_strength"],
                opponent_strength=side["opponent_strength"],
                bookmakers_used=bookmakers_used,
                favorite_type=favorite_type,
            ),
        }

        candidates.append(pick)

    return candidates


def stake_from_quality(quality, edge, odds):
    if quality >= 92 and edge >= 0.11 and 1.65 <= odds <= 2.70:
        return 1.5
    if quality >= 84 and edge >= 0.08:
        return 1.25
    if quality >= 74:
        return 1.0
    return 0.75


def stake_label_from_quality(quality):
    if quality >= 92:
        return "Top Rated"
    if quality >= 84:
        return "Strong"
    if quality >= 74:
        return "Standard"
    return "Small Value"


def build_reasoning(
    player,
    opponent,
    tournament,
    odds,
    median_odds,
    model_prob,
    implied_prob,
    edge,
    confidence,
    player_strength,
    opponent_strength,
    bookmakers_used,
    favorite_type,
):
    p10 = player_strength["last_10"]
    o10 = opponent_strength["last_10"]

    return (
        f"{player} is selected against {opponent} in {tournament}. "
        f"The model prices {player} at {model_prob * 100:.1f}% versus an implied probability of "
        f"{implied_prob * 100:.1f}% from best odds {odds:.2f}. "
        f"Market median is {median_odds:.2f} across {bookmakers_used} bookmakers, leaving an estimated edge of "
        f"+{edge * 100:.1f}%. "
        f"Recent-form profile: {player} last-10 win rate {p10['win_rate'] * 100:.1f}%, "
        f"avg set diff {p10['set_diff_avg']:+.2f}, avg game diff {p10['game_diff_avg']:+.2f}; "
        f"{opponent} last-10 win rate {o10['win_rate'] * 100:.1f}%, "
        f"avg set diff {o10['set_diff_avg']:+.2f}, avg game diff {o10['game_diff_avg']:+.2f}. "
        f"Pick type: {favorite_type}. Confidence score: {confidence:.1f}."
    )


# =========================
# HISTORY APPEND
# =========================

def append_unique_history(predictions):
    history = load_json(RESULTS_FILE, [])

    if not isinstance(history, list):
        history = []

    by_id = {
        item.get("pick_id"): idx
        for idx, item in enumerate(history)
        if isinstance(item, dict) and item.get("pick_id")
    }

    added = 0
    updated_pending = 0

    for pick in predictions:
        pick_id = pick.get("pick_id")

        if not pick_id:
            continue

        if pick_id not in by_id:
            history.append(pick.copy())
            by_id[pick_id] = len(history) - 1
            added += 1
        else:
            idx = by_id[pick_id]
            old = history[idx]

            # Only refresh pending picks. Never overwrite settled history.
            if str(old.get("result") or "pending").lower() == "pending":
                new_pick = pick.copy()

                if old.get("created_at"):
                    new_pick["created_at"] = old.get("created_at")

                history[idx] = new_pick
                updated_pending += 1

    save_json(RESULTS_FILE, history)

    debug(f"HISTORY added={added} updated_pending={updated_pending} total={len(history)}")


# =========================
# MAIN
# =========================

def build_predictions():
    ensure_dirs()

    now = datetime.now(ZoneInfo(TZ_NAME))
    fixtures = fetch_all_fixtures()

    debug_items = []
    candidates = []

    checked = 0
    skipped_ineligible = 0
    errors = 0

    for match in fixtures:
        checked += 1

        try:
            if not is_match_eligible(match):
                skipped_ineligible += 1
                continue

            match_name = f"{match.get('event_first_player')} - {match.get('event_second_player')}"
            debug(f"CHECK {match_name} | event_key={match.get('event_key')}")

            built = build_candidate(match)

            if built:
                debug(f"CANDIDATES {match_name}: {len(built)}")
                candidates.extend(built)

        except Exception as e:
            errors += 1
            debug(f"ERROR match={match.get('event_key')} {match.get('event_first_player')} - {match.get('event_second_player')}: {e}")
            debug_items.append({
                "event_key": match.get("event_key"),
                "match": f"{match.get('event_first_player')} - {match.get('event_second_player')}",
                "error": str(e),
            })

    # One pick per match max: choose higher quality side
    best_by_event = {}

    for pick in candidates:
        event_key = str(pick["event_key"])
        old = best_by_event.get(event_key)

        if not old:
            best_by_event[event_key] = pick
            continue

        if (
            pick["quality_score"],
            pick["confidence"],
            pick["edge"],
            pick["bookmakers_used"],
        ) > (
            old["quality_score"],
            old["confidence"],
            old["edge"],
            old["bookmakers_used"],
        ):
            best_by_event[event_key] = pick

    final = list(best_by_event.values())

    final.sort(
        key=lambda x: (
            x["quality_score"],
            x["confidence"],
            x["edge"],
            x["bookmakers_used"],
        ),
        reverse=True,
    )

    final = final[:MAX_PICKS]
    final.sort(key=lambda x: (x["date"], x["time"]))

    payload = {
        "generated_at": now.isoformat(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": "AI77 Tennis Value Model v1",
        "stake_mode": "quality_based",
        "market": "Home/Away Match Winner",
        "filters": {
            "min_recent_matches_each": MIN_RECENT_MATCHES_EACH,
            "min_bookmakers": MIN_BOOKMAKERS,
            "min_edge": MIN_EDGE,
            "min_confidence": MIN_CONFIDENCE,
            "odds_min": ODDS_MIN,
            "odds_max": ODDS_MAX,
            "max_picks": MAX_PICKS,
            "days_ahead": DAYS_AHEAD,
        },
        "summary": {
            "fixtures_checked": checked,
            "candidates_raw": len(candidates),
            "final_picks": len(final),
            "skipped_ineligible": skipped_ineligible,
            "errors": errors,
        },
        "picks": final,
    }

    save_json(PREDICTIONS_FILE, payload)
    append_unique_history(final)

    save_json(DEBUG_FILE, {
        "generated_at": now.isoformat(),
        "summary": payload["summary"],
        "errors": debug_items,
    })

    return payload


def main():
    payload = build_predictions()

    print("")
    print("TENNIS PREDICTIONS DONE")
    print(f"Fixtures checked: {payload['summary']['fixtures_checked']}")
    print(f"Raw candidates: {payload['summary']['candidates_raw']}")
    print(f"Final picks: {payload['summary']['final_picks']}")
    print(f"Saved: {PREDICTIONS_FILE}")

    for pick in payload["picks"]:
        print(
            f"{pick['date']} {pick['time']} | {pick['match']} | "
            f"{pick['bet']} @ {pick['odds']} | edge={pick['edge']} | "
            f"conf={pick['confidence']} | {pick['stake_label']}"
        )


if __name__ == "__main__":
    main()

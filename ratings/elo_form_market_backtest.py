import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

import requests


# ============================================================
# CONFIG
# ============================================================

TZ_NAME = "Europe/Ljubljana"
TZ = ZoneInfo(TZ_NAME)

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

BACKTEST_DAYS_BACK = int(os.getenv("BACKTEST_DAYS_BACK", "5"))
FORM_DAYS_BACK = int(os.getenv("FORM_DAYS_BACK", "45"))
MIN_ELO_DIFF = float(os.getenv("MIN_ELO_DIFF", "60"))

BOOKMAKER = os.getenv("BOOKMAKER", "").strip().lower()
REQUEST_SLEEP = float(os.getenv("REQUEST_SLEEP", "0.15"))

OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest_report.json"
OUTPUT_ROWS_FILE = "ratings/elo_form_market_backtest_rows.json"
OUTPUT_MISSING_FILE = "ratings/elo_form_market_backtest_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest_table.md"

SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    from elo_lookup import get_elo_signal
except Exception as e:
    raise RuntimeError(f"Cannot import ratings/elo_lookup.py: {e}")


# ============================================================
# BASIC HELPERS
# ============================================================

def now_local():
    return datetime.now(TZ)


def today_local():
    return now_local().date()


def now_iso():
    return now_local().isoformat()


def ymd(d):
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)


def daterange(start_date, stop_date):
    d = start_date
    while d <= stop_date:
        yield d
        d += timedelta(days=1)


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
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "":
                return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def norm_name(name):
    return " ".join(str(name or "").strip().lower().split())


def clean_name(name):
    return " ".join(str(name or "").strip().split())


def pct(x):
    return round(x * 100, 2)


def round2(x):
    try:
        return round(float(x), 2)
    except Exception:
        return x


# ============================================================
# API TENNIS
# ============================================================

def fetch_api(method, params=None, retries=3, sleep_base=1.2):
    if not API_KEY:
        raise RuntimeError("Missing env var TENNIS_API_KEY or API_KEY")

    params = dict(params or {})
    params["method"] = method
    params["APIkey"] = API_KEY

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE_URL, params=params, timeout=45)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict):
                success = data.get("success")
                if success == 0 and data.get("error"):
                    last_error = data.get("error")
                    time.sleep(sleep_base * attempt)
                    continue

            return data

        except Exception as e:
            last_error = e
            time.sleep(sleep_base * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def api_result_list(payload):
    if not isinstance(payload, dict):
        return []

    result = payload.get("result")

    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        return list(result.values())

    return []


def api_result_dict(payload):
    if not isinstance(payload, dict):
        return {}

    result = payload.get("result")

    if isinstance(result, dict):
        return result

    return {}


def collect_fixtures(start_date, stop_date):
    fixtures = []

    for d in daterange(start_date, stop_date):
        ds = ymd(d)
        print(f"Fetching fixtures: {ds}")

        try:
            data = fetch_api("get_fixtures", {
                "date_start": ds,
                "date_stop": ds,
            })
            rows = api_result_list(data)
            print(f"  fixtures: {len(rows)}")
            fixtures.extend(rows)

        except Exception as e:
            print(f"  fixtures failed: {e}")

        time.sleep(REQUEST_SLEEP)

    return fixtures


def fetch_match_odds(match_key):
    if not match_key:
        return {}

    try:
        data = fetch_api("get_odds", {
            "match_key": match_key,
        })

        result = api_result_dict(data)

        # API Tennis get_odds response:
        # result = { "159923": { "Home/Away": { "Home": {...}, "Away": {...} } } }
        match_odds = (
            result.get(str(match_key))
            or result.get(match_key)
            or {}
        )

        return match_odds if isinstance(match_odds, dict) else {}

    except Exception as e:
        return {"_error": str(e)}


# ============================================================
# FIXTURE PARSING
# ============================================================

def parse_match_dt(fx):
    date_str = (
        fx.get("event_date")
        or fx.get("date")
        or fx.get("match_date")
        or ""
    )

    time_str = (
        fx.get("event_time")
        or fx.get("time")
        or fx.get("match_time")
        or "00:00"
    )

    raw = f"{date_str} {time_str}".strip()

    for fmt in [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=TZ)
        except Exception:
            pass

    return None


def get_match_key(fx):
    return (
        fx.get("event_key")
        or fx.get("match_key")
        or fx.get("id")
        or fx.get("fixture_key")
    )


def get_first_player(fx):
    return clean_name(
        fx.get("event_first_player")
        or fx.get("first_player")
        or fx.get("home_player")
        or fx.get("player_home")
        or fx.get("player1")
    )


def get_second_player(fx):
    return clean_name(
        fx.get("event_second_player")
        or fx.get("second_player")
        or fx.get("away_player")
        or fx.get("player_away")
        or fx.get("player2")
    )


def get_surface(fx):
    raw = (
        fx.get("event_surface")
        or fx.get("surface")
        or fx.get("court_surface")
        or fx.get("tournament_surface")
        or ""
    )

    raw_l = str(raw).strip().lower()

    if not raw_l:
        return None

    if "clay" in raw_l:
        return "clay"
    if "hard" in raw_l:
        return "hard"
    if "grass" in raw_l:
        return "grass"
    if "indoor" in raw_l:
        return "indoor"

    return raw_l


def infer_tour(fx):
    fields = [
        fx.get("event_type_type"),
        fx.get("event_type"),
        fx.get("tournament_name"),
        fx.get("league_name"),
        fx.get("event_name"),
    ]

    text = " ".join(str(x or "") for x in fields).lower()

    if "wta" in text or "women" in text or "women's" in text:
        return "wta"

    if "atp" in text or "men" in text or "men's" in text:
        return "atp"

    if "challenger" in text:
        return "challenger"

    if "itf" in text:
        return "itf"

    return None


def get_tournament(fx):
    return clean_name(
        fx.get("tournament_name")
        or fx.get("event_type_type")
        or fx.get("league_name")
        or fx.get("event_name")
        or ""
    )


def get_status(fx):
    return str(
        fx.get("event_status")
        or fx.get("status")
        or fx.get("match_status")
        or ""
    ).strip().lower()


def is_finished(fx):
    status = get_status(fx)

    if status in {"finished", "finished after retirement", "retired", "walkover", "ended"}:
        return True

    if fx.get("event_final_result"):
        return True

    if fx.get("event_winner") or fx.get("event_winner_key"):
        return True

    return False


def get_winner_name(fx):
    first = get_first_player(fx)
    second = get_second_player(fx)

    winner_raw = (
        fx.get("event_winner")
        or fx.get("winner")
        or fx.get("match_winner")
        or ""
    )

    winner_key = (
        fx.get("event_winner_key")
        or fx.get("winner_key")
        or ""
    )

    first_key = str(fx.get("first_player_key") or fx.get("event_first_player_key") or "")
    second_key = str(fx.get("second_player_key") or fx.get("event_second_player_key") or "")

    wr = str(winner_raw or "").strip()
    wrl = wr.lower()

    if winner_key and first_key and str(winner_key) == str(first_key):
        return first

    if winner_key and second_key and str(winner_key) == str(second_key):
        return second

    first_norm = norm_name(first)
    second_norm = norm_name(second)
    winner_norm = norm_name(wr)

    if not winner_norm:
        return None

    if winner_norm in {"first player", "first", "home", "1", "player 1", "player1"}:
        return first

    if winner_norm in {"second player", "second", "away", "2", "player 2", "player2"}:
        return second

    if winner_norm == first_norm:
        return first

    if winner_norm == second_norm:
        return second

    if first_norm and first_norm in winner_norm:
        return first

    if second_norm and second_norm in winner_norm:
        return second

    if winner_norm and winner_norm in first_norm:
        return first

    if winner_norm and winner_norm in second_norm:
        return second

    return None


# ============================================================
# ODDS PARSING
# ============================================================

def extract_home_away_odds(match_odds):
    if not isinstance(match_odds, dict):
        return None

    if match_odds.get("_error"):
        return None

    market = (
        match_odds.get("Home/Away")
        or match_odds.get("home/away")
        or match_odds.get("Home Away")
        or match_odds.get("Match Winner")
        or match_odds.get("Winner")
    )

    if not isinstance(market, dict):
        # Sometimes markets can be nested with slightly different names.
        for k, v in match_odds.items():
            if isinstance(k, str) and k.strip().lower() in {
                "home/away",
                "home away",
                "match winner",
                "winner",
                "moneyline",
            }:
                market = v
                break

    if not isinstance(market, dict):
        return None

    home_books = (
        market.get("Home")
        or market.get("home")
        or market.get("1")
        or market.get("First")
        or market.get("first")
    )

    away_books = (
        market.get("Away")
        or market.get("away")
        or market.get("2")
        or market.get("Second")
        or market.get("second")
    )

    if not isinstance(home_books, dict) or not isinstance(away_books, dict):
        return None

    home_odd, home_book = choose_odd(home_books)
    away_odd, away_book = choose_odd(away_books)

    if not home_odd or not away_odd:
        return None

    return {
        "home_odd": home_odd,
        "away_odd": away_odd,
        "home_bookmaker": home_book,
        "away_bookmaker": away_book,
    }


def choose_odd(book_odds):
    if not isinstance(book_odds, dict):
        return None, None

    parsed = []

    for book, odd in book_odds.items():
        o = safe_float(odd)
        if o and o > 1.01:
            parsed.append((str(book).strip(), o))

    if not parsed:
        return None, None

    if BOOKMAKER:
        for book, odd in parsed:
            if book.lower() == BOOKMAKER:
                return odd, book

    # Best available odd.
    parsed.sort(key=lambda x: x[1], reverse=True)
    return parsed[0][1], parsed[0][0]


# ============================================================
# FORM
# ============================================================

def build_player_history(fixtures):
    history = defaultdict(list)

    for fx in fixtures:
        if not is_finished(fx):
            continue

        dt = parse_match_dt(fx)
        if not dt:
            continue

        first = get_first_player(fx)
        second = get_second_player(fx)
        winner = get_winner_name(fx)

        if not first or not second or not winner:
            continue

        first_norm = norm_name(first)
        second_norm = norm_name(second)
        winner_norm = norm_name(winner)

        first_win = winner_norm == first_norm
        second_win = winner_norm == second_norm

        if not first_win and not second_win:
            continue

        base = {
            "date": dt.isoformat(),
            "match_key": get_match_key(fx),
            "tournament": get_tournament(fx),
            "surface": get_surface(fx),
            "tour": infer_tour(fx),
        }

        history[first_norm].append({
            **base,
            "player": first,
            "opponent": second,
            "result": "win" if first_win else "loss",
        })

        history[second_norm].append({
            **base,
            "player": second,
            "opponent": first,
            "result": "win" if second_win else "loss",
        })

    for p in history:
        history[p].sort(key=lambda r: r["date"])

    return history


def player_form(history, player, before_dt, n):
    p = norm_name(player)
    rows = history.get(p, [])

    before_iso = before_dt.isoformat() if before_dt else "9999"

    past = [r for r in rows if r.get("date") < before_iso]
    last = past[-n:]

    wins = sum(1 for r in last if r.get("result") == "win")
    losses = sum(1 for r in last if r.get("result") == "loss")
    total = wins + losses

    return {
        "n": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / total * 100, 2) if total else None,
    }


def form_diff(fa, fb):
    if fa.get("win_rate") is None or fb.get("win_rate") is None:
        return None
    return round(fa["win_rate"] - fb["win_rate"], 2)


# ============================================================
# PICK LOGIC
# ============================================================

def get_elo_for_match(first, second, surface, tour):
    signal = get_elo_signal(
        first,
        second,
        surface=surface,
        tour=tour,
    )

    if not signal.get("matched"):
        return signal

    overall_diff = signal.get("overall_elo_diff")
    surface_diff = signal.get("surface_elo_diff")

    signal["abs_overall_elo_diff"] = abs(overall_diff) if overall_diff is not None else None
    signal["abs_surface_elo_diff"] = abs(surface_diff) if surface_diff is not None else None

    return signal


def choose_pick(first, second, odds, elo_signal, form_first_5, form_second_5, form_first_10, form_second_10):
    if not elo_signal.get("matched"):
        return None

    elo_diff = elo_signal.get("overall_elo_diff")
    if elo_diff is None:
        return None

    abs_elo = abs(elo_diff)

    if abs_elo < MIN_ELO_DIFF:
        return None

    if elo_diff > 0:
        pick_player = first
        opponent = second
        pick_side = "home"
        pick_odd = odds["home_odd"]
        opponent_odd = odds["away_odd"]
        form5_diff = form_diff(form_first_5, form_second_5)
        form10_diff = form_diff(form_first_10, form_second_10)
    else:
        pick_player = second
        opponent = first
        pick_side = "away"
        pick_odd = odds["away_odd"]
        opponent_odd = odds["home_odd"]
        form5_diff = form_diff(form_second_5, form_first_5)
        form10_diff = form_diff(form_second_10, form_first_10)

    form5_component = form5_diff if form5_diff is not None else 0.0
    form10_component = form10_diff if form10_diff is not None else 0.0

    # Form je samo dodatni signal za analizo, ne zavrže picka.
    # Combined score pomaga kasneje videti, če je kombinacija močnejša.
    combined_score = abs_elo + (form5_component * 0.50) + (form10_component * 0.25)

    market_implied = round(100 / pick_odd, 2) if pick_odd else None

    return {
        "pick_player": pick_player,
        "opponent": opponent,
        "pick_side": pick_side,
        "odds": pick_odd,
        "opponent_odds": opponent_odd,
        "abs_elo_diff": round2(abs_elo),
        "elo_side": "first" if elo_diff > 0 else "second",
        "form5_diff": form5_diff,
        "form10_diff": form10_diff,
        "combined_score": round2(combined_score),
        "market_implied_pct": market_implied,
    }


def settle_pick(pick_player, winner_name, odds):
    if not pick_player or not winner_name or not odds:
        return {
            "result": "unknown",
            "profit": 0.0,
            "stake": 0.0,
        }

    is_win = norm_name(pick_player) == norm_name(winner_name)

    if is_win:
        return {
            "result": "win",
            "profit": round2(odds - 1.0),
            "stake": 1.0,
        }

    return {
        "result": "loss",
        "profit": -1.0,
        "stake": 1.0,
    }


# ============================================================
# STATS
# ============================================================

def empty_stats():
    return {
        "rows": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0,
        "stake": 0.0,
        "avg_odds_sum": 0.0,
        "avg_elo_sum": 0.0,
        "avg_combined_sum": 0.0,
    }


def add_stat(stats, key, row):
    if key not in stats:
        stats[key] = empty_stats()

    s = stats[key]
    result = row.get("result")
    profit = safe_float(row.get("profit"), 0.0)
    stake = safe_float(row.get("stake"), 0.0)
    odds = safe_float(row.get("odds"), 0.0)
    elo = safe_float(row.get("abs_elo_diff"), 0.0)
    combined = safe_float(row.get("combined_score"), 0.0)

    s["rows"] += 1
    s["profit"] += profit
    s["stake"] += stake
    s["avg_odds_sum"] += odds
    s["avg_elo_sum"] += elo
    s["avg_combined_sum"] += combined

    if result == "win":
        s["wins"] += 1
    elif result == "loss":
        s["losses"] += 1


def finalize_stats(stats):
    out = {}

    for key, s in stats.items():
        rows = s["rows"]
        wins = s["wins"]
        losses = s["losses"]
        graded = wins + losses
        stake = s["stake"]
        profit = s["profit"]

        out[key] = {
            "rows": rows,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / graded * 100, 2) if graded else 0.0,
            "profit": round2(profit),
            "stake": round2(stake),
            "roi": round(profit / stake * 100, 2) if stake else 0.0,
            "avg_odds": round(s["avg_odds_sum"] / rows, 3) if rows else 0.0,
            "avg_abs_elo_diff": round(s["avg_elo_sum"] / rows, 2) if rows else 0.0,
            "avg_combined_score": round(s["avg_combined_sum"] / rows, 2) if rows else 0.0,
        }

    return out


def elo_bucket(abs_elo):
    x = safe_float(abs_elo, 0.0)

    if x < 60:
        return "<60"
    if x < 90:
        return "60-90"
    if x < 120:
        return "90-120"
    if x < 150:
        return "120-150"
    if x < 180:
        return "150-180"
    if x < 220:
        return "180-220"
    return "220+"


def odds_bucket(odds):
    x = safe_float(odds, 0.0)

    if x < 1.40:
        return "<1.40"
    if x < 1.60:
        return "1.40-1.60"
    if x < 1.80:
        return "1.60-1.80"
    if x < 2.00:
        return "1.80-2.00"
    if x < 2.30:
        return "2.00-2.30"
    if x < 2.70:
        return "2.30-2.70"
    return "2.70+"


def form_bucket(v):
    if v is None:
        return "unknown"

    x = safe_float(v, 0.0)

    if x >= 30:
        return "+30 or more"
    if x >= 15:
        return "+15 to +30"
    if x >= 0:
        return "0 to +15"
    if x >= -15:
        return "-15 to 0"
    if x >= -30:
        return "-30 to -15"
    return "-30 or less"


# ============================================================
# MAIN COLLECTOR
# ============================================================

def collect_rows():
    target_stop = today_local()
    target_start = target_stop - timedelta(days=BACKTEST_DAYS_BACK)

    form_start = target_start - timedelta(days=FORM_DAYS_BACK)
    form_stop = target_stop

    print(f"Fetching fixtures for form: {ymd(form_start)} -> {ymd(form_stop)}")
    all_fixtures = collect_fixtures(form_start, form_stop)

    history = build_player_history(all_fixtures)

    target_fixtures = []
    for fx in all_fixtures:
        dt = parse_match_dt(fx)
        if not dt:
            continue
        if target_start <= dt.date() <= target_stop:
            target_fixtures.append(fx)

    print(f"Target fixtures: {len(target_fixtures)}")

    rows = []
    missing = []

    for i, fx in enumerate(target_fixtures, start=1):
        match_key = get_match_key(fx)
        dt = parse_match_dt(fx)
        first = get_first_player(fx)
        second = get_second_player(fx)
        winner = get_winner_name(fx)
        surface = get_surface(fx)
        tour = infer_tour(fx)
        tournament = get_tournament(fx)

        if not is_finished(fx):
            continue

        if not match_key or not first or not second or not winner:
            missing.append({
                "reason": "missing_basic_match_data",
                "match_key": match_key,
                "date": dt.isoformat() if dt else None,
                "first_player": first,
                "second_player": second,
                "winner": winner,
                "raw_status": get_status(fx),
            })
            continue

        print(f"Fetching odds: {i}/{len(target_fixtures)} match_key={match_key}")

        match_odds = fetch_match_odds(match_key)
        odds = extract_home_away_odds(match_odds)

        if not odds:
            missing.append({
                "reason": "missing_home_away_odds",
                "match_key": match_key,
                "date": dt.isoformat() if dt else None,
                "match": f"{first} - {second}",
                "raw_odds_keys": list(match_odds.keys()) if isinstance(match_odds, dict) else None,
                "odds_error": match_odds.get("_error") if isinstance(match_odds, dict) else None,
            })
            time.sleep(REQUEST_SLEEP)
            continue

        elo_signal = get_elo_for_match(first, second, surface, tour)

        if not elo_signal.get("matched"):
            missing.append({
                "reason": "elo_not_matched",
                "match_key": match_key,
                "date": dt.isoformat() if dt else None,
                "match": f"{first} - {second}",
                "first_player": first,
                "second_player": second,
                "tour": tour,
                "surface": surface,
                "first_matched": elo_signal.get("player", {}).get("matched"),
                "second_matched": elo_signal.get("opponent", {}).get("matched"),
                "first_method": elo_signal.get("player", {}).get("match_method"),
                "second_method": elo_signal.get("opponent", {}).get("match_method"),
            })
            time.sleep(REQUEST_SLEEP)
            continue

        form_first_5 = player_form(history, first, dt, 5)
        form_second_5 = player_form(history, second, dt, 5)
        form_first_10 = player_form(history, first, dt, 10)
        form_second_10 = player_form(history, second, dt, 10)

        pick = choose_pick(
            first,
            second,
            odds,
            elo_signal,
            form_first_5,
            form_second_5,
            form_first_10,
            form_second_10,
        )

        if not pick:
            missing.append({
                "reason": "no_pick_min_elo_filter",
                "match_key": match_key,
                "date": dt.isoformat() if dt else None,
                "match": f"{first} - {second}",
                "overall_elo_diff": elo_signal.get("overall_elo_diff"),
                "abs_overall_elo_diff": elo_signal.get("abs_overall_elo_diff"),
                "min_elo_diff": MIN_ELO_DIFF,
            })
            time.sleep(REQUEST_SLEEP)
            continue

        settlement = settle_pick(pick["pick_player"], winner, pick["odds"])

        row = {
            "generated_at": now_iso(),
            "match_key": match_key,
            "date": dt.date().isoformat() if dt else None,
            "time": dt.strftime("%H:%M") if dt else None,
            "datetime": dt.isoformat() if dt else None,
            "tournament": tournament,
            "tour": tour,
            "surface": surface,
            "match": f"{first} - {second}",
            "first_player": first,
            "second_player": second,
            "winner": winner,

            "pick": pick["pick_player"],
            "opponent": pick["opponent"],
            "pick_side": pick["pick_side"],
            "odds": pick["odds"],
            "opponent_odds": pick["opponent_odds"],
            "home_odd": odds["home_odd"],
            "away_odd": odds["away_odd"],
            "home_bookmaker": odds["home_bookmaker"],
            "away_bookmaker": odds["away_bookmaker"],

            "result": settlement["result"],
            "profit": settlement["profit"],
            "stake": settlement["stake"],

            "overall_elo_diff_first_minus_second": round2(elo_signal.get("overall_elo_diff")),
            "surface_elo_diff_first_minus_second": round2(elo_signal.get("surface_elo_diff")),
            "abs_elo_diff": pick["abs_elo_diff"],
            "elo_side": pick["elo_side"],

            "first_form_5": form_first_5,
            "second_form_5": form_second_5,
            "first_form_10": form_first_10,
            "second_form_10": form_second_10,
            "form5_diff_for_pick": pick["form5_diff"],
            "form10_diff_for_pick": pick["form10_diff"],

            "combined_score": pick["combined_score"],
            "market_implied_pct": pick["market_implied_pct"],
            "min_elo_diff": MIN_ELO_DIFF,
        }

        rows.append(row)
        time.sleep(REQUEST_SLEEP)

    meta = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "api": "api-tennis.com",
        "target_start": ymd(target_start),
        "target_stop": ymd(target_stop),
        "backtest_days_back": BACKTEST_DAYS_BACK,
        "form_start": ymd(form_start),
        "form_stop": ymd(form_stop),
        "form_days_back": FORM_DAYS_BACK,
        "min_elo_diff": MIN_ELO_DIFF,
        "bookmaker": BOOKMAKER or "best_available",
        "all_fixtures": len(all_fixtures),
        "target_fixtures": len(target_fixtures),
        "rows": len(rows),
        "missing": len(missing),
    }

    return rows, missing, meta


def build_report(rows, missing, meta):
    stats = {}

    for row in rows:
        add_stat(stats, "overall", row)

        add_stat(stats, f"tour:{row.get('tour') or 'unknown'}", row)
        add_stat(stats, f"surface:{row.get('surface') or 'unknown'}", row)
        add_stat(stats, f"elo_bucket:{elo_bucket(row.get('abs_elo_diff'))}", row)
        add_stat(stats, f"odds_bucket:{odds_bucket(row.get('odds'))}", row)
        add_stat(stats, f"form5_pick_edge:{form_bucket(row.get('form5_diff_for_pick'))}", row)
        add_stat(stats, f"form10_pick_edge:{form_bucket(row.get('form10_diff_for_pick'))}", row)

        if safe_float(row.get("form5_diff_for_pick"), 0.0) >= 0:
            add_stat(stats, "elo_and_form5_agree", row)
        else:
            add_stat(stats, "elo_and_form5_disagree", row)

        if safe_float(row.get("form10_diff_for_pick"), 0.0) >= 0:
            add_stat(stats, "elo_and_form10_agree", row)
        else:
            add_stat(stats, "elo_and_form10_disagree", row)

    finalized = finalize_stats(stats)

    top_rows = sorted(
        rows,
        key=lambda r: (
            safe_float(r.get("combined_score"), 0.0),
            safe_float(r.get("abs_elo_diff"), 0.0),
        ),
        reverse=True,
    )[:50]

    return {
        "generated_at": now_iso(),
        "meta": meta,
        "summary": finalized,
        "top_rows_sample": top_rows,
        "missing_count": len(missing),
    }


def build_table(report):
    lines = []

    meta = report["meta"]
    summary = report["summary"]

    lines.append("# ELO + Form + Market Backtest")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Meta")
    lines.append("")
    lines.append(f"- Target window: {meta['target_start']} -> {meta['target_stop']}")
    lines.append(f"- Backtest days back: {meta['backtest_days_back']}")
    lines.append(f"- Form window: {meta['form_start']} -> {meta['form_stop']}")
    lines.append(f"- Form days back: {meta['form_days_back']}")
    lines.append(f"- Min ELO diff: {meta['min_elo_diff']}")
    lines.append(f"- Bookmaker: {meta['bookmaker']}")
    lines.append(f"- Target fixtures: {meta['target_fixtures']}")
    lines.append(f"- Pick rows: {meta['rows']}")
    lines.append(f"- Missing/skipped: {meta['missing']}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Bucket | Rows | W-L | WR | Profit | Stake | ROI | Avg odds | Avg ELO diff | Avg combined |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    preferred_order = [
        "overall",
        "elo_and_form5_agree",
        "elo_and_form5_disagree",
        "elo_and_form10_agree",
        "elo_and_form10_disagree",
    ]

    keys = []
    for k in preferred_order:
        if k in summary:
            keys.append(k)

    for k in sorted(summary.keys()):
        if k not in keys:
            keys.append(k)

    for key in keys:
        s = summary[key]
        lines.append(
            f"| {key} | {s['rows']} | {s['wins']}-{s['losses']} | "
            f"{s['win_rate']}% | {s['profit']}u | {s['stake']}u | "
            f"{s['roi']}% | {s['avg_odds']} | {s['avg_abs_elo_diff']} | {s['avg_combined_score']} |"
        )

    lines.append("")
    lines.append("## Top rows sample")
    lines.append("")
    lines.append("| Date | Match | Pick | Odds | Result | Profit | ELO diff | F5 diff | F10 diff | Combined |")
    lines.append("|---|---|---|---:|---|---:|---:|---:|---:|---:|")

    for row in report.get("top_rows_sample", [])[:25]:
        lines.append(
            f"| {row.get('date')} | {row.get('match')} | {row.get('pick')} | "
            f"{row.get('odds')} | {row.get('result')} | {row.get('profit')} | "
            f"{row.get('abs_elo_diff')} | {row.get('form5_diff_for_pick')} | "
            f"{row.get('form10_diff_for_pick')} | {row.get('combined_score')} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    rows, missing, meta = collect_rows()
    report = build_report(rows, missing, meta)
    table = build_table(report)

    missing_payload = {
        "generated_at": now_iso(),
        "meta": meta,
        "missing": missing,
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_ROWS_FILE, rows)
    save_json(OUTPUT_MISSING_FILE, missing_payload)
    save_text(OUTPUT_TABLE_FILE, table)

    print("")
    print("ELO + FORM + MARKET BACKTEST DONE")
    print(f"Rows:      {len(rows)}")
    print(f"Missing:   {len(missing)}")
    print(f"Report:    {OUTPUT_REPORT_FILE}")
    print(f"Rows file: {OUTPUT_ROWS_FILE}")
    print(f"Missing:   {OUTPUT_MISSING_FILE}")
    print(f"Table:     {OUTPUT_TABLE_FILE}")
    print("")

    overall = report["summary"].get("overall", {})
    print("Overall:")
    print(json.dumps(overall, indent=2, ensure_ascii=False))
    print("")


if __name__ == "__main__":
    main()

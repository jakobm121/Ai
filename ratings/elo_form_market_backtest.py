import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


# Repo import support
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATINGS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(RATINGS_DIR)
sys.path.append(ROOT_DIR)

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"
BASE_URL = "https://api.api-tennis.com/tennis/"

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")

BACKTEST_DAYS_BACK = int(os.getenv("BACKTEST_DAYS_BACK", "5"))
MIN_ELO_DIFF = float(os.getenv("MIN_ELO_DIFF", "60"))
MIN_ODDS = float(os.getenv("MIN_ODDS", "1.90"))
MAX_ODDS = float(os.getenv("MAX_ODDS", "2.70"))

OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest_report.json"
OUTPUT_ROWS_FILE = "ratings/elo_form_market_backtest_rows.json"
OUTPUT_MISSING_FILE = "ratings/elo_form_market_backtest_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest_table.md"


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)


def norm_text(value):
    return str(value or "").strip()


def norm_lower(value):
    return norm_text(value).lower()


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
        if value is None:
            return default
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return default
        return int(float(value))
    except Exception:
        return default


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def api_result(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in ["result", "data", "fixtures", "odds"]:
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]

    return []


def fetch_api(method, params=None, retries=3, sleep_seconds=0.6):
    if not API_KEY:
        raise RuntimeError("Missing env var TENNIS_API_KEY or API_KEY")

    params = dict(params or {})
    params["method"] = method
    params["APIkey"] = API_KEY

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=40)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                # API-Tennis sometimes returns success=0 with result/message.
                success = data.get("success")
                if str(success) == "0":
                    msg = data.get("message") or data.get("result") or data
                    last_error = RuntimeError(f"API success=0 for {method}: {msg}")
                    time.sleep(sleep_seconds)
                    continue

            return data

        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(sleep_seconds * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def collect_fixtures(start_date, end_date):
    fixtures = []

    print(f"Fetching fixtures: {start_date} -> {end_date}")

    for d in daterange(start_date, end_date):
        date_str = d.isoformat()
        print(f"Fetching fixtures: {date_str}")

        try:
            data = fetch_api(
                "get_fixtures",
                {
                    "date_start": date_str,
                    "date_stop": date_str,
                },
                retries=3,
            )
            rows = api_result(data)
            print(f"  fixtures: {len(rows)}")
            fixtures.extend(rows)

        except Exception as e:
            print(f"  fixtures error: {e}")

    return fixtures


def walk_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_dicts(item)


def fixture_key(row):
    for key in [
        "event_key",
        "match_key",
        "fixture_key",
        "id",
        "event_id",
        "match_id",
    ]:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()

    return None


def fixture_date(row):
    for key in ["event_date", "date", "match_date"]:
        value = row.get(key)
        if value:
            return str(value)

    return None


def fixture_time(row):
    for key in ["event_time", "time", "match_time"]:
        value = row.get(key)
        if value:
            return str(value)

    return None


def player_names(row):
    first = (
        row.get("event_first_player")
        or row.get("first_player")
        or row.get("player_1")
        or row.get("home_player")
        or row.get("home_team")
        or row.get("event_home_team")
    )

    second = (
        row.get("event_second_player")
        or row.get("second_player")
        or row.get("player_2")
        or row.get("away_player")
        or row.get("away_team")
        or row.get("event_away_team")
    )

    return norm_text(first), norm_text(second)


def event_name(row):
    for key in ["event_name", "match_name", "match", "name"]:
        value = row.get(key)
        if value:
            return str(value)

    first, second = player_names(row)
    if first and second:
        return f"{first} vs {second}"

    return ""


def infer_tour(row):
    blob = " ".join(
        norm_lower(row.get(k))
        for k in [
            "event_type_type",
            "event_type",
            "event_type_key",
            "league_name",
            "tournament_name",
            "event_name",
            "country_name",
        ]
    )

    if "wta" in blob or "women" in blob or "woman" in blob:
        return "wta"

    if "atp" in blob or "men" in blob:
        return "atp"

    if "challenger" in blob:
        return "challenger"

    if "itf" in blob:
        return "itf"

    return None


def infer_surface(row):
    for key in [
        "event_surface",
        "surface",
        "court_surface",
        "court",
        "event_court_surface",
    ]:
        value = row.get(key)
        if value:
            return norm_text(value)

    return None


def fixture_status(row):
    for key in ["event_status", "status", "match_status"]:
        value = row.get(key)
        if value:
            return norm_text(value)

    return ""


def is_finished(row):
    status = norm_lower(fixture_status(row))

    if not status:
        # Some API rows have final result but no status.
        return bool(row.get("event_final_result") or row.get("final_result"))

    finished_words = [
        "finished",
        "after penalties",
        "after penalty",
        "retired",
        "walkover",
        "wo",
        "cancelled",
        "canceled",
    ]

    return any(w in status for w in finished_words)


def winner_side(row):
    """
    Returns:
      1 = first player won
      2 = second player won
      None = unknown/not graded
    """

    first, second = player_names(row)
    first_l = norm_lower(first)
    second_l = norm_lower(second)

    for key in [
        "event_winner",
        "winner",
        "match_winner",
        "event_winner_name",
        "winner_name",
    ]:
        value = row.get(key)
        if value is None:
            continue

        text = norm_lower(value)

        if not text:
            continue

        if text in {"first player", "first", "player 1", "1", "home", "home team"}:
            return 1

        if text in {"second player", "second", "player 2", "2", "away", "away team"}:
            return 2

        if first_l and text == first_l:
            return 1

        if second_l and text == second_l:
            return 2

        if first_l and first_l in text and second_l not in text:
            return 1

        if second_l and second_l in text and first_l not in text:
            return 2

    final_result = norm_text(row.get("event_final_result") or row.get("final_result"))
    if final_result:
        parsed = winner_from_score(final_result)
        if parsed in {1, 2}:
            return parsed

    return None


def winner_from_score(score):
    """
    Very simple tennis score parser.
    Examples:
      2 - 0
      0 - 2
      6-4 7-6
      4-6 6-3 6-2
    """

    s = norm_text(score)
    if not s:
        return None

    # Direct sets score like "2 - 0"
    compact = s.replace(" ", "")
    for sep in ["-", ":"]:
        parts = compact.split(sep)
        if len(parts) == 2:
            a = safe_int(parts[0])
            b = safe_int(parts[1])
            if a is not None and b is not None and 0 <= a <= 5 and 0 <= b <= 5 and a != b:
                return 1 if a > b else 2

    # Game score by sets.
    tokens = s.replace(",", " ").replace(";", " ").split()
    p1_sets = 0
    p2_sets = 0

    for token in tokens:
        token = token.strip()
        if "-" not in token and ":" not in token:
            continue

        sep = "-" if "-" in token else ":"
        parts = token.split(sep)
        if len(parts) != 2:
            continue

        a = safe_int(parts[0])
        b = safe_int(parts[1])

        if a is None or b is None:
            continue

        if a == b:
            continue

        if a > b:
            p1_sets += 1
        else:
            p2_sets += 1

    if p1_sets > p2_sets:
        return 1

    if p2_sets > p1_sets:
        return 2

    return None


def fetch_odds_for_match(event_key):
    """
    API-Tennis get_odds expects event_key.
    """

    try:
        data = fetch_api("get_odds", {"event_key": event_key}, retries=2, sleep_seconds=0.4)
        return data
    except Exception as e:
        print(f"  odds error for event_key={event_key}: {e}")
        return []


def is_match_winner_context(d):
    blob = " ".join(norm_lower(v) for v in d.values() if isinstance(v, (str, int, float)))

    bad_words = [
        "total",
        "totals",
        "games",
        "set ",
        "1st set",
        "2nd set",
        "handicap",
        "spread",
        "correct score",
        "over",
        "under",
    ]

    good_words = [
        "match winner",
        "winner",
        "moneyline",
        "to win",
        "home/away",
        "home away",
        "full time result",
    ]

    if any(bad in blob for bad in bad_words):
        return False

    if any(good in blob for good in good_words):
        return True

    # API-Tennis often gives only odd_1/odd_2 for match winner inside event odds.
    return True


def extract_odds_pair(odds_payload):
    """
    Returns best available pair:
      p1_odds, p2_odds

    Robust for different API-Tennis shapes:
      odd_1 / odd_2
      home_odd / away_odd
      value/name + odd/price
    """

    p1_prices = []
    p2_prices = []

    for d in walk_dicts(odds_payload):
        if not isinstance(d, dict):
            continue

        lowered = {str(k).lower().strip(): k for k in d.keys()}

        if not is_match_winner_context(d):
            continue

        # Most important API-Tennis shape.
        if "odd_1" in lowered and "odd_2" in lowered:
            p1 = safe_float(d.get(lowered["odd_1"]))
            p2 = safe_float(d.get(lowered["odd_2"]))

            if p1 is not None and 1.01 <= p1 <= 20:
                p1_prices.append(p1)

            if p2 is not None and 1.01 <= p2 <= 20:
                p2_prices.append(p2)

            continue

        # Alternative pair keys.
        pair_key_sets = [
            ("home_odd", "away_odd"),
            ("odd_home", "odd_away"),
            ("player_1_odd", "player_2_odd"),
            ("first_odd", "second_odd"),
            ("price_1", "price_2"),
            ("coef_1", "coef_2"),
            ("coefficient_1", "coefficient_2"),
            ("home", "away"),
            ("1", "2"),
        ]

        for k1, k2 in pair_key_sets:
            if k1 in lowered and k2 in lowered:
                p1 = safe_float(d.get(lowered[k1]))
                p2 = safe_float(d.get(lowered[k2]))

                if p1 is not None and 1.01 <= p1 <= 20:
                    p1_prices.append(p1)

                if p2 is not None and 1.01 <= p2 <= 20:
                    p2_prices.append(p2)

        # Label + price shape.
        label = norm_lower(
            d.get("value")
            or d.get("name")
            or d.get("label")
            or d.get("odd_name")
            or d.get("bet_name")
            or d.get("selection")
            or d.get("selection_name")
        )

        price = safe_float(
            d.get("odd")
            or d.get("price")
            or d.get("coefficient")
            or d.get("value_odd")
            or d.get("bookmaker_odd")
        )

        if price is not None and 1.01 <= price <= 20:
            if label in {"home", "1", "player 1", "first player", "first", "p1"}:
                p1_prices.append(price)
            elif label in {"away", "2", "player 2", "second player", "second", "p2"}:
                p2_prices.append(price)

    if not p1_prices or not p2_prices:
        return None, None

    return max(p1_prices), max(p2_prices)


def elo_diff_bucket(abs_diff):
    if abs_diff is None:
        return "unknown"

    bins = [
        (0, 60),
        (60, 80),
        (80, 100),
        (100, 120),
        (120, 150),
        (150, 180),
        (180, 220),
        (220, 99999),
    ]

    for lo, hi in bins:
        if lo <= abs_diff < hi:
            if hi >= 99999:
                return f"{lo}+"
            return f"{lo}-{hi}"

    return "unknown"


def odds_bucket(odds):
    if odds is None:
        return "unknown"

    bins = [
        (1.90, 2.00),
        (2.00, 2.10),
        (2.10, 2.30),
        (2.30, 2.50),
        (2.50, 2.70),
    ]

    for lo, hi in bins:
        if lo <= odds < hi:
            return f"{lo:.2f}-{hi:.2f}"

    if odds == 2.70:
        return "2.50-2.70"

    return "outside"


def add_stat(stats, key, row):
    s = stats[key]

    if not s:
        s.update({
            "n": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0,
            "stake": 0.0,
            "odds_sum": 0.0,
            "elo_sum": 0.0,
        })

    s["n"] += 1
    s["stake"] += 1.0
    s["profit"] += row["profit"]
    s["odds_sum"] += row["odds"]
    s["elo_sum"] += row["abs_overall_elo_diff"]

    if row["result"] == "win":
        s["wins"] += 1
    else:
        s["losses"] += 1


def finalize_stat(s):
    n = s.get("n", 0)
    stake = s.get("stake", 0.0)
    wins = s.get("wins", 0)
    losses = s.get("losses", 0)
    profit = s.get("profit", 0.0)

    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / n * 100, 2) if n else 0.0,
        "profit": round(profit, 3),
        "stake": round(stake, 3),
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
        "avg_odds": round(s.get("odds_sum", 0.0) / n, 3) if n else 0.0,
        "avg_abs_overall_elo_diff": round(s.get("elo_sum", 0.0) / n, 2) if n else 0.0,
    }


def build_stats(rows):
    raw = defaultdict(dict)

    for row in rows:
        add_stat(raw, "overall", row)
        add_stat(raw, f"tour:{row.get('tour') or 'unknown'}", row)
        add_stat(raw, f"elo_diff:{elo_diff_bucket(row.get('abs_overall_elo_diff'))}", row)
        add_stat(raw, f"odds:{odds_bucket(row.get('odds'))}", row)
        add_stat(raw, f"picked_side:{row.get('picked_side')}", row)

    return {key: finalize_stat(value) for key, value in raw.items()}


def build_table(report):
    lines = []

    lines.append("# ELO-only market backtest")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Settings")
    lines.append("")
    lines.append(f"- Days back: {report['settings']['days_back']}")
    lines.append(f"- Min ELO diff: {report['settings']['min_elo_diff']}")
    lines.append(f"- Odds range: {report['settings']['min_odds']} - {report['settings']['max_odds']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Fixtures fetched: {report['meta']['fixtures_fetched']}")
    lines.append(f"- ELO candidates: {report['meta']['elo_candidates']}")
    lines.append(f"- Final rows: {report['meta']['final_rows']}")
    lines.append(f"- Missing/skipped: {report['meta']['missing_rows']}")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    lines.append("| Bucket | N | W-L | WR | Profit | ROI | Avg odds | Avg ELO diff |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, s in report["stats"].items():
        lines.append(
            f"| {key} | {s['n']} | {s['wins']}-{s['losses']} | "
            f"{s['win_rate']}% | {s['profit']}u | {s['roi']}% | "
            f"{s['avg_odds']} | {s['avg_abs_overall_elo_diff']} |"
        )

    lines.append("")
    lines.append("## First 50 picks")
    lines.append("")
    lines.append("| Date | Match | Pick | Odds | Result | Profit | ELO diff |")
    lines.append("|---|---|---|---:|---|---:|---:|")

    for row in report["sample_rows"]:
        lines.append(
            f"| {row.get('date') or ''} | {row.get('match') or ''} | "
            f"{row.get('pick') or ''} | {row.get('odds') or ''} | "
            f"{row.get('result') or ''} | {row.get('profit') or ''} | "
            f"{row.get('overall_elo_diff') or ''} |"
        )

    lines.append("")

    return "\n".join(lines)


def collect_rows():
    end_date = today_local()
    start_date = end_date - timedelta(days=BACKTEST_DAYS_BACK)

    fixtures = collect_fixtures(start_date, end_date)

    rows = []
    missing = []

    seen = set()
    target_fixtures = []

    for f in fixtures:
        if not isinstance(f, dict):
            continue

        key = fixture_key(f)
        if not key or key in seen:
            continue

        seen.add(key)

        first, second = player_names(f)
        if not first or not second:
            missing.append({
                "event_key": key,
                "reason": "missing_player_names",
                "raw_match": event_name(f),
            })
            continue

        if not is_finished(f):
            missing.append({
                "event_key": key,
                "date": fixture_date(f),
                "match": event_name(f),
                "reason": "not_finished",
                "status": fixture_status(f),
            })
            continue

        winner = winner_side(f)
        if winner not in {1, 2}:
            missing.append({
                "event_key": key,
                "date": fixture_date(f),
                "match": event_name(f),
                "reason": "winner_unknown",
                "status": fixture_status(f),
                "final_result": f.get("event_final_result") or f.get("final_result"),
                "event_winner": f.get("event_winner") or f.get("winner"),
            })
            continue

        tour = infer_tour(f)
        surface = infer_surface(f)

        signal = get_elo_signal(first, second, surface=surface, tour=tour)

        if not signal.get("matched"):
            missing.append({
                "event_key": key,
                "date": fixture_date(f),
                "match": event_name(f),
                "reason": "elo_unmatched",
                "first": first,
                "second": second,
                "first_matched": signal.get("player", {}).get("matched"),
                "second_matched": signal.get("opponent", {}).get("matched"),
                "first_method": signal.get("player", {}).get("match_method"),
                "second_method": signal.get("opponent", {}).get("match_method"),
            })
            continue

        overall_diff = signal.get("overall_elo_diff")
        if overall_diff is None:
            missing.append({
                "event_key": key,
                "date": fixture_date(f),
                "match": event_name(f),
                "reason": "elo_diff_missing",
            })
            continue

        overall_diff = float(overall_diff)
        abs_diff = abs(overall_diff)

        if abs_diff < MIN_ELO_DIFF:
            continue

        target_fixtures.append({
            "fixture": f,
            "event_key": key,
            "first": first,
            "second": second,
            "winner": winner,
            "tour": tour,
            "surface": surface,
            "overall_elo_diff": overall_diff,
            "abs_overall_elo_diff": abs_diff,
            "surface_elo_diff": signal.get("surface_elo_diff"),
            "first_matched_name": signal.get("player", {}).get("matched_name"),
            "second_matched_name": signal.get("opponent", {}).get("matched_name"),
        })

    print(f"Target fixtures after ELO filter: {len(target_fixtures)}")

    for idx, item in enumerate(target_fixtures, start=1):
        event_key = item["event_key"]

        if idx <= 10 or idx % 25 == 0 or idx == len(target_fixtures):
            print(f"Fetching odds: {idx}/{len(target_fixtures)} event_key={event_key}")

        odds_payload = fetch_odds_for_match(event_key)
        p1_odds, p2_odds = extract_odds_pair(odds_payload)

        if p1_odds is None or p2_odds is None:
            missing.append({
                "event_key": event_key,
                "date": fixture_date(item["fixture"]),
                "match": event_name(item["fixture"]),
                "reason": "odds_pair_missing",
                "overall_elo_diff": item["overall_elo_diff"],
                "abs_overall_elo_diff": item["abs_overall_elo_diff"],
            })
            continue

        if item["overall_elo_diff"] > 0:
            picked_side = 1
            pick_name = item["first"]
            odds = p1_odds
        else:
            picked_side = 2
            pick_name = item["second"]
            odds = p2_odds

        if odds < MIN_ODDS or odds > MAX_ODDS:
            missing.append({
                "event_key": event_key,
                "date": fixture_date(item["fixture"]),
                "match": event_name(item["fixture"]),
                "reason": "odds_outside_range",
                "pick": pick_name,
                "odds": odds,
                "p1_odds": p1_odds,
                "p2_odds": p2_odds,
                "overall_elo_diff": item["overall_elo_diff"],
                "abs_overall_elo_diff": item["abs_overall_elo_diff"],
            })
            continue

        result = "win" if picked_side == item["winner"] else "loss"
        profit = round(odds - 1.0, 3) if result == "win" else -1.0

        row = {
            "event_key": event_key,
            "date": fixture_date(item["fixture"]),
            "time": fixture_time(item["fixture"]),
            "match": event_name(item["fixture"]),
            "first_player": item["first"],
            "second_player": item["second"],
            "pick": pick_name,
            "picked_side": picked_side,
            "winner_side": item["winner"],
            "result": result,
            "odds": round(odds, 3),
            "p1_odds": round(p1_odds, 3),
            "p2_odds": round(p2_odds, 3),
            "stake": 1.0,
            "profit": profit,
            "tour": item["tour"],
            "surface": item["surface"],
            "overall_elo_diff": round(item["overall_elo_diff"], 3),
            "abs_overall_elo_diff": round(item["abs_overall_elo_diff"], 3),
            "surface_elo_diff": item["surface_elo_diff"],
            "first_matched_name": item["first_matched_name"],
            "second_matched_name": item["second_matched_name"],
        }

        rows.append(row)

    meta = {
        "fixtures_fetched": len(fixtures),
        "unique_fixtures": len(seen),
        "elo_candidates": len(target_fixtures),
        "final_rows": len(rows),
        "missing_rows": len(missing),
    }

    return rows, missing, meta


def main():
    rows, missing, meta = collect_rows()
    stats = build_stats(rows)

    report = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "settings": {
            "days_back": BACKTEST_DAYS_BACK,
            "min_elo_diff": MIN_ELO_DIFF,
            "min_odds": MIN_ODDS,
            "max_odds": MAX_ODDS,
            "api": "api-tennis",
            "source": BASE_URL,
        },
        "meta": meta,
        "stats": stats,
        "sample_rows": rows[:50],
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_ROWS_FILE, rows)
    save_json(OUTPUT_MISSING_FILE, {
        "generated_at": report["generated_at"],
        "meta": meta,
        "missing": missing,
    })
    save_text(OUTPUT_TABLE_FILE, build_table(report))

    print("")
    print("ELO-ONLY MARKET BACKTEST DONE")
    print(f"Rows:      {len(rows)}")
    print(f"Missing:   {len(missing)}")
    print(f"Report:    {OUTPUT_REPORT_FILE}")
    print(f"Rows file: {OUTPUT_ROWS_FILE}")
    print(f"Missing:   {OUTPUT_MISSING_FILE}")
    print(f"Table:     {OUTPUT_TABLE_FILE}")
    print("")
    print("Overall:")
    print(stats.get("overall", {}))
    print("")


if __name__ == "__main__":
    main()

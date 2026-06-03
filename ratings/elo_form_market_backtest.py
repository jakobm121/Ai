import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import requests

# Import iz ratings/
sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"
BASE_URL = "https://api.api-tennis.com/tennis/"

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")

BACKTEST_DAYS_BACK = int(os.getenv("BACKTEST_DAYS_BACK", "5"))
MIN_ELO_DIFF = float(os.getenv("MIN_ELO_DIFF", "60"))
MIN_ODDS = float(os.getenv("MIN_ODDS", "1.90"))
MAX_ODDS = float(os.getenv("MAX_ODDS", "2.70"))
REQUEST_SLEEP = float(os.getenv("REQUEST_SLEEP", "0.03"))

OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest_report.json"
OUTPUT_ROWS_FILE = "ratings/elo_form_market_backtest_rows.json"
OUTPUT_MISSING_FILE = "ratings/elo_form_market_backtest_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest_table.md"


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def date_range(start_date, end_date):
    d = start_date
    while d <= end_date:
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
            if not value:
                return default
        return float(value)
    except Exception:
        return default


def norm(value):
    return str(value or "").strip()


def norm_lower(value):
    return norm(value).lower()


def fetch_api(method, params=None, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing env var TENNIS_API_KEY or API_KEY")

    params = dict(params or {})
    params["method"] = method
    params["APIkey"] = API_KEY

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE_URL, params=params, timeout=35)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict):
                result = data.get("result")
                if result is None:
                    result = data.get("data")
                if result is None:
                    result = []
                return result

            if isinstance(data, list):
                return data

            return []
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(1.5 * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def collect_fixtures(start_date, end_date):
    out = []

    for d in date_range(start_date, end_date):
        ds = d.isoformat()
        print(f"Fetching fixtures: {ds}")

        try:
            rows = fetch_api("get_fixtures", {
                "date_start": ds,
                "date_stop": ds,
            })
        except Exception as e:
            print(f"  fixtures error: {e}")
            rows = []

        if not isinstance(rows, list):
            rows = []

        print(f"  fixtures: {len(rows)}")
        out.extend(rows)
        time.sleep(REQUEST_SLEEP)

    return out


def fixture_key(row):
    return (
        row.get("event_key")
        or row.get("match_key")
        or row.get("id")
        or row.get("fixture_key")
    )


def first_player(row):
    return (
        row.get("event_first_player")
        or row.get("first_player")
        or row.get("first_player_name")
        or row.get("player_1")
        or row.get("home_player")
    )


def second_player(row):
    return (
        row.get("event_second_player")
        or row.get("second_player")
        or row.get("second_player_name")
        or row.get("player_2")
        or row.get("away_player")
    )


def infer_surface(row):
    raw = " ".join([
        norm(row.get("event_surface")),
        norm(row.get("surface")),
        norm(row.get("court_surface")),
        norm(row.get("tournament_surface")),
        norm(row.get("tournament_name")),
        norm(row.get("event_type")),
    ]).lower()

    if "clay" in raw:
        return "clay"
    if "hard" in raw:
        return "hard"
    if "grass" in raw:
        return "grass"
    if "carpet" in raw:
        return "carpet"

    return None


def infer_tour(row):
    raw = " ".join([
        norm(row.get("event_type")),
        norm(row.get("tournament_name")),
        norm(row.get("league_name")),
        norm(row.get("event_league")),
        norm(row.get("tournament_type")),
    ]).lower()

    if "wta" in raw or "women" in raw:
        return "wta"
    if "atp" in raw or "men" in raw:
        return "atp"
    if "challenger" in raw:
        return "challenger"
    if "itf" in raw:
        return "itf"

    return None


def is_singles(row):
    raw = " ".join([
        norm(row.get("event_type")),
        norm(row.get("tournament_name")),
    ]).lower()

    if "doubles" in raw or "double" in raw:
        return False

    p1 = first_player(row)
    p2 = second_player(row)

    if not p1 or not p2:
        return False

    # doubles pogosto vsebujejo "/" ali "+"
    if "/" in p1 or "/" in p2 or " / " in p1 or " / " in p2:
        return False

    return True


def parse_winner_side(row):
    p1 = norm(first_player(row))
    p2 = norm(second_player(row))

    winner = (
        row.get("event_winner")
        or row.get("winner")
        or row.get("match_winner")
        or row.get("event_winner_player")
    )

    w = norm(winner)
    wl = w.lower()

    if not w:
        return None

    if wl in {"first player", "first_player", "player 1", "player_1", "1", "home"}:
        return "p1"

    if wl in {"second player", "second_player", "player 2", "player_2", "2", "away"}:
        return "p2"

    if p1 and wl == p1.lower():
        return "p1"

    if p2 and wl == p2.lower():
        return "p2"

    if p1 and p1.lower() in wl:
        return "p1"

    if p2 and p2.lower() in wl:
        return "p2"

    return None


def is_finished(row):
    status = norm_lower(row.get("event_status") or row.get("status") or row.get("match_status"))
    final_result = norm(row.get("event_final_result") or row.get("final_result"))

    if parse_winner_side(row):
        return True

    if status in {"finished", "ended", "final", "complete", "completed"}:
        return True

    if final_result:
        return True

    return False


def flatten_dicts(obj):
    found = []

    if isinstance(obj, dict):
        found.append(obj)
        for v in obj.values():
            found.extend(flatten_dicts(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(flatten_dicts(item))

    return found


def market_looks_match_winner(d):
    text = " ".join(str(v) for v in d.values() if isinstance(v, (str, int, float))).lower()

    bad_markets = [
        "total",
        "over",
        "under",
        "set",
        "handicap",
        "spread",
        "correct score",
        "games",
        "aces",
    ]

    good_markets = [
        "winner",
        "match winner",
        "match_winner",
        "home/away",
        "home away",
        "to win",
        "1x2",
        "moneyline",
    ]

    if any(bad in text for bad in bad_markets):
        return False

    if any(good in text for good in good_markets):
        return True

    # API-Tennis včasih vrne samo odd_1 / odd_2 brez market imena.
    keys = {str(k).lower() for k in d.keys()}
    if ("odd_1" in keys and "odd_2" in keys) or ("home_odd" in keys and "away_odd" in keys):
        return True

    return False


P1_ODD_KEYS = {
    "odd_1", "odd1", "odd_home", "home_odd", "home", "player_1_odd",
    "first_odd", "odd_first", "odd_first_player", "event_odd_1",
    "price_1", "coef_1", "coefficient_1",
}

P2_ODD_KEYS = {
    "odd_2", "odd2", "odd_away", "away_odd", "away", "player_2_odd",
    "second_odd", "odd_second", "odd_second_player", "event_odd_2",
    "price_2", "coef_2", "coefficient_2",
}


def extract_odds_pair(odds_payload):
    p1_prices = []
    p2_prices = []

    for d in flatten_dicts(odds_payload):
        if not isinstance(d, dict):
            continue

        if not market_looks_match_winner(d):
            continue

        for k, v in d.items():
            lk = str(k).lower().strip()
            price = safe_float(v)

            if price is None:
                continue

            if price < 1.01 or price > 20:
                continue

            if lk in P1_ODD_KEYS:
                p1_prices.append(price)
            elif lk in P2_ODD_KEYS:
                p2_prices.append(price)

    if not p1_prices or not p2_prices:
        return None, None

    # vzamemo najboljšo dosegljivo kvoto iz vrnjenih bookmakerjev
    return max(p1_prices), max(p2_prices)


def fetch_odds_for_match(match_key):
    # api-tennis endpoint za odds po match_key
    try:
        return fetch_api("get_odds", {"match_key": match_key}, retries=2)
    except Exception:
        return []


def odds_bucket(odds):
    if odds is None:
        return "unknown"

    if odds < 1.90:
        return "<1.90"
    if odds < 2.00:
        return "1.90-2.00"
    if odds < 2.20:
        return "2.00-2.20"
    if odds < 2.50:
        return "2.20-2.50"
    if odds <= 2.70:
        return "2.50-2.70"

    return ">2.70"


def elo_bucket(abs_diff):
    if abs_diff < 60:
        return "<60"
    if abs_diff < 80:
        return "60-80"
    if abs_diff < 100:
        return "80-100"
    if abs_diff < 120:
        return "100-120"
    if abs_diff < 150:
        return "120-150"
    if abs_diff < 180:
        return "150-180"
    if abs_diff < 220:
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
        "avg_abs_elo_sum": 0.0,
    }


def update_stats(stats, key, row):
    s = stats[key]
    s["n"] += 1
    s["stake"] += 1.0
    s["profit"] += row["profit"]
    s["avg_odds_sum"] += row["odds"]
    s["avg_abs_elo_sum"] += row["abs_overall_elo_diff"]

    if row["result"] == "win":
        s["wins"] += 1
    else:
        s["losses"] += 1


def finalize_stats(stats):
    out = {}

    for key, s in stats.items():
        n = s["n"]
        stake = s["stake"]
        profit = s["profit"]
        wins = s["wins"]

        out[key] = {
            "n": n,
            "wins": s["wins"],
            "losses": s["losses"],
            "win_rate": round(wins / n * 100, 2) if n else 0.0,
            "profit": round(profit, 3),
            "stake": round(stake, 3),
            "roi": round(profit / stake * 100, 2) if stake else 0.0,
            "avg_odds": round(s["avg_odds_sum"] / n, 3) if n else 0.0,
            "avg_abs_overall_elo_diff": round(s["avg_abs_elo_sum"] / n, 2) if n else 0.0,
        }

    return out


def collect_rows():
    end_date = today_local()
    start_date = end_date - timedelta(days=BACKTEST_DAYS_BACK)

    print(f"Fetching fixtures: {start_date} -> {end_date}")

    fixtures = collect_fixtures(start_date, end_date)

    rows = []
    missing = []
    counters = defaultdict(int)

    target_fixtures = []

    for f in fixtures:
        counters["fixtures_total"] += 1

        if not isinstance(f, dict):
            counters["bad_fixture_object"] += 1
            continue

        if not is_singles(f):
            counters["not_singles"] += 1
            continue

        if not is_finished(f):
            counters["not_finished"] += 1
            continue

        winner_side = parse_winner_side(f)
        if not winner_side:
            counters["missing_winner"] += 1
            continue

        key = fixture_key(f)
        if not key:
            counters["missing_match_key"] += 1
            continue

        p1 = first_player(f)
        p2 = second_player(f)

        if not p1 or not p2:
            counters["missing_players"] += 1
            continue

        tour = infer_tour(f)
        surface = infer_surface(f)

        signal = get_elo_signal(p1, p2, surface=surface, tour=tour)

        if not signal.get("matched"):
            counters["elo_unmatched"] += 1
            missing.append({
                "reason": "elo_unmatched",
                "date": f.get("event_date"),
                "match_key": key,
                "player_1": p1,
                "player_2": p2,
                "tour": tour,
                "surface": surface,
                "player_1_matched": signal.get("player", {}).get("matched"),
                "player_2_matched": signal.get("opponent", {}).get("matched"),
                "player_1_method": signal.get("player", {}).get("match_method"),
                "player_2_method": signal.get("opponent", {}).get("match_method"),
            })
            continue

        diff = signal.get("overall_elo_diff")
        if diff is None:
            counters["elo_diff_missing"] += 1
            continue

        abs_diff = abs(float(diff))

        if abs_diff < MIN_ELO_DIFF:
            counters["elo_diff_too_low"] += 1
            continue

        pick_side = "p1" if diff > 0 else "p2"
        pick_name = p1 if pick_side == "p1" else p2

        target_fixtures.append({
            "fixture": f,
            "match_key": key,
            "player_1": p1,
            "player_2": p2,
            "pick_side": pick_side,
            "pick_name": pick_name,
            "winner_side": winner_side,
            "tour": tour,
            "surface": surface,
            "overall_elo_diff": round(float(diff), 2),
            "abs_overall_elo_diff": round(abs_diff, 2),
            "player_1_elo": signal.get("player", {}).get("overall_elo"),
            "player_2_elo": signal.get("opponent", {}).get("overall_elo"),
            "player_1_matched_name": signal.get("player", {}).get("matched_name"),
            "player_2_matched_name": signal.get("opponent", {}).get("matched_name"),
        })

    print(f"Target fixtures after ELO filter: {len(target_fixtures)}")

    for i, item in enumerate(target_fixtures, start=1):
        key = item["match_key"]

        if i <= 10 or i % 25 == 0:
            print(f"Fetching odds: {i}/{len(target_fixtures)} match_key={key}")

        odds_payload = fetch_odds_for_match(key)
        p1_odds, p2_odds = extract_odds_pair(odds_payload)

        if p1_odds is None or p2_odds is None:
            counters["odds_missing"] += 1
            missing.append({
                "reason": "odds_missing",
                "date": item["fixture"].get("event_date"),
                "match_key": key,
                "player_1": item["player_1"],
                "player_2": item["player_2"],
                "pick": item["pick_name"],
                "overall_elo_diff": item["overall_elo_diff"],
            })
            time.sleep(REQUEST_SLEEP)
            continue

        pick_odds = p1_odds if item["pick_side"] == "p1" else p2_odds

        if pick_odds < MIN_ODDS or pick_odds > MAX_ODDS:
            counters["odds_out_of_range"] += 1
            time.sleep(REQUEST_SLEEP)
            continue

        result = "win" if item["pick_side"] == item["winner_side"] else "loss"
        profit = round(pick_odds - 1.0, 3) if result == "win" else -1.0

        row = {
            "date": item["fixture"].get("event_date"),
            "time": item["fixture"].get("event_time"),
            "match_key": key,
            "match": f"{item['player_1']} vs {item['player_2']}",
            "player_1": item["player_1"],
            "player_2": item["player_2"],
            "pick": item["pick_name"],
            "pick_side": item["pick_side"],
            "winner_side": item["winner_side"],
            "result": result,
            "odds": round(pick_odds, 3),
            "player_1_odds": round(p1_odds, 3),
            "player_2_odds": round(p2_odds, 3),
            "stake": 1.0,
            "profit": profit,
            "tour": item["tour"],
            "surface": item["surface"],
            "overall_elo_diff": item["overall_elo_diff"],
            "abs_overall_elo_diff": item["abs_overall_elo_diff"],
            "elo_bucket": elo_bucket(item["abs_overall_elo_diff"]),
            "odds_bucket": odds_bucket(pick_odds),
            "player_1_elo": item["player_1_elo"],
            "player_2_elo": item["player_2_elo"],
            "player_1_matched_name": item["player_1_matched_name"],
            "player_2_matched_name": item["player_2_matched_name"],
            "rule": f"ELO-only: higher overall ELO, abs diff >= {MIN_ELO_DIFF}, odds {MIN_ODDS}-{MAX_ODDS}",
        }

        rows.append(row)
        counters["picks"] += 1
        time.sleep(REQUEST_SLEEP)

    meta = {
        "fixtures_total": counters["fixtures_total"],
        "not_singles": counters["not_singles"],
        "not_finished": counters["not_finished"],
        "missing_winner": counters["missing_winner"],
        "missing_match_key": counters["missing_match_key"],
        "missing_players": counters["missing_players"],
        "elo_unmatched": counters["elo_unmatched"],
        "elo_diff_missing": counters["elo_diff_missing"],
        "elo_diff_too_low": counters["elo_diff_too_low"],
        "elo_candidates": len(target_fixtures),
        "odds_checked": len(target_fixtures),
        "odds_missing": counters["odds_missing"],
        "odds_out_of_range": counters["odds_out_of_range"],
        "picks": len(rows),
    }

    return rows, missing, meta


def build_report(rows, missing, meta):
    stats = defaultdict(empty_stats)

    for row in rows:
        update_stats(stats, "overall", row)
        update_stats(stats, f"tour:{row.get('tour') or 'unknown'}", row)
        update_stats(stats, f"surface:{row.get('surface') or 'unknown'}", row)
        update_stats(stats, f"elo:{row.get('elo_bucket')}", row)
        update_stats(stats, f"odds:{row.get('odds_bucket')}", row)

    report = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "mode": "elo_only_market_backtest",
        "settings": {
            "backtest_days_back": BACKTEST_DAYS_BACK,
            "min_elo_diff": MIN_ELO_DIFF,
            "min_odds": MIN_ODDS,
            "max_odds": MAX_ODDS,
            "stake": "1u flat",
        },
        "meta": meta,
        "overall": finalize_stats({"overall": stats["overall"]}).get("overall", {}),
        "stats": finalize_stats(stats),
        "rows_count": len(rows),
        "missing_count": len(missing),
    }

    return report


def build_table(report, rows):
    lines = []
    lines.append("# ELO-only market backtest")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Settings")
    lines.append("")
    lines.append(f"- Days back: {report['settings']['backtest_days_back']}")
    lines.append(f"- Min ELO diff: {report['settings']['min_elo_diff']}")
    lines.append(f"- Odds range: {report['settings']['min_odds']} - {report['settings']['max_odds']}")
    lines.append(f"- Stake: {report['settings']['stake']}")
    lines.append("")
    lines.append("## Funnel")
    lines.append("")
    lines.append("| Step | Count |")
    lines.append("|---|---:|")

    for k, v in report["meta"].items():
        lines.append(f"| {k} | {v} |")

    lines.append("")
    lines.append("## Stats")
    lines.append("")
    lines.append("| Bucket | N | W-L | WR | Profit | ROI | Avg odds | Avg abs ELO diff |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, s in report["stats"].items():
        lines.append(
            f"| {key} | {s['n']} | {s['wins']}-{s['losses']} | "
            f"{s['win_rate']}% | {s['profit']}u | {s['roi']}% | "
            f"{s['avg_odds']} | {s['avg_abs_overall_elo_diff']} |"
        )

    lines.append("")
    lines.append("## Picks")
    lines.append("")
    lines.append("| Date | Match | Pick | Odds | ELO diff | Result | Profit |")
    lines.append("|---|---|---|---:|---:|---:|---:|")

    for r in rows[:300]:
        lines.append(
            f"| {r.get('date')} | {r.get('match')} | {r.get('pick')} | "
            f"{r.get('odds')} | {r.get('abs_overall_elo_diff')} | "
            f"{r.get('result')} | {r.get('profit')} |"
        )

    return "\n".join(lines)


def main():
    rows, missing, meta = collect_rows()
    report = build_report(rows, missing, meta)

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_ROWS_FILE, rows)
    save_json(OUTPUT_MISSING_FILE, {
        "generated_at": report["generated_at"],
        "missing": missing,
        "meta": meta,
    })
    save_text(OUTPUT_TABLE_FILE, build_table(report, rows))

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
    print(report.get("overall", {}))
    print("")


if __name__ == "__main__":
    main()

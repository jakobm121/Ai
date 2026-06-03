import json
import os
import sys
import time
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import requests


# Allow imports when run from repo root.
sys.path.append(os.path.dirname(__file__))

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
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default

        if isinstance(value, str):
            value = value.strip().replace(",", ".")

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


def norm(value):
    return str(value or "").strip()


def lower(value):
    return norm(value).lower()


def fetch_api(method, params=None, retries=3, sleep_seconds=0.8):
    if not API_KEY:
        raise RuntimeError("Missing TENNIS_API_KEY or API_KEY env var")

    query = {
        "method": method,
        "APIkey": API_KEY,
    }

    if params:
        query.update(params)

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(BASE_URL, params=query, timeout=40)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and str(data.get("success")) == "0":
                # API sometimes returns success 0 with empty result for odds.
                return data

            return data

        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(sleep_seconds * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def api_result_to_list(data):
    if not isinstance(data, dict):
        return []

    result = data.get("result")

    if isinstance(result, list):
        return [x for x in result if isinstance(x, dict)]

    if isinstance(result, dict):
        return [x for x in result.values() if isinstance(x, dict)]

    return []


def get_first(row, keys, default=None):
    for key in keys:
        value = row.get(key)
        if value not in [None, ""]:
            return value

    return default


def get_event_key(row):
    return get_first(row, [
        "event_key",
        "match_key",
        "fixture_key",
        "id",
    ])


def get_first_player(row):
    return get_first(row, [
        "event_first_player",
        "first_player",
        "player_1",
        "player1",
        "home_team",
        "event_home_team",
    ])


def get_second_player(row):
    return get_first(row, [
        "event_second_player",
        "second_player",
        "player_2",
        "player2",
        "away_team",
        "event_away_team",
    ])


def get_event_date(row):
    return get_first(row, [
        "event_date",
        "date",
        "match_date",
    ])


def get_event_time(row):
    return get_first(row, [
        "event_time",
        "time",
        "match_time",
    ])


def infer_surface(row):
    value = get_first(row, [
        "event_surface",
        "surface",
        "court_surface",
        "court",
    ])

    if not value:
        return None

    text = lower(value)

    if "clay" in text:
        return "clay"
    if "hard" in text:
        return "hard"
    if "grass" in text:
        return "grass"
    if "indoor" in text:
        return "indoor"

    return norm(value)


def infer_tour(row):
    event_type = lower(get_first(row, [
        "event_type_type",
        "event_type",
        "type",
        "event_name",
        "league_name",
        "tournament_name",
    ], ""))

    if "wta" in event_type or "women" in event_type or "woman" in event_type:
        return "wta"

    if "atp" in event_type or "men" in event_type:
        return "atp"

    return None


def is_finished(row):
    status = lower(get_first(row, [
        "event_status",
        "status",
        "match_status",
    ], ""))

    if status in {
        "finished",
        "finish",
        "ended",
        "completed",
        "final",
        "after penalties",
        "retired",
        "walkover",
    }:
        return True

    final_result = norm(get_first(row, [
        "event_final_result",
        "final_result",
        "result",
    ], ""))

    if final_result and "-" in final_result:
        return True

    winner = get_first(row, [
        "event_winner",
        "winner",
        "event_winner_player",
    ])

    return bool(winner)


def parse_final_result(row):
    """
    Returns:
      1 if first player won
      2 if second player won
      None if unknown
    """

    winner = norm(get_first(row, [
        "event_winner",
        "winner",
        "event_winner_player",
    ], ""))

    first = norm(get_first_player(row))
    second = norm(get_second_player(row))

    if winner:
        if winner == "First Player" or winner == "1":
            return 1
        if winner == "Second Player" or winner == "2":
            return 2

        if first and lower(winner) == lower(first):
            return 1
        if second and lower(winner) == lower(second):
            return 2

    final_result = norm(get_first(row, [
        "event_final_result",
        "final_result",
        "result",
    ], ""))

    if not final_result or "-" not in final_result:
        return None

    cleaned = (
        final_result
        .replace(" ", "")
        .replace("–", "-")
        .replace("—", "-")
        .replace(":", "-")
    )

    parts = cleaned.split("-")

    if len(parts) < 2:
        return None

    a = safe_int(parts[0])
    b = safe_int(parts[1])

    if a is None or b is None:
        return None

    if a > b:
        return 1
    if b > a:
        return 2

    return None


def fetch_fixtures_for_day(day):
    day_s = day.isoformat()

    data = fetch_api(
        "get_fixtures",
        {
            "date_start": day_s,
            "date_stop": day_s,
        },
        retries=3,
        sleep_seconds=0.8,
    )

    return api_result_to_list(data)


def collect_fixtures(start_date, end_date):
    fixtures = []

    print(f"Fetching fixtures: {start_date} -> {end_date}")

    for day in daterange(start_date, end_date):
        print(f"Fetching fixtures: {day}")

        try:
            rows = fetch_fixtures_for_day(day)
            print(f"  fixtures: {len(rows)}")
            fixtures.extend(rows)
        except Exception as e:
            print(f"  fixtures error: {e}")

    return fixtures


def best_price(bookmaker_dict):
    if not isinstance(bookmaker_dict, dict):
        return None

    prices = []

    for value in bookmaker_dict.values():
        price = safe_float(value)

        if price is not None and 1.01 <= price <= 100:
            prices.append(price)

    if not prices:
        return None

    return max(prices)


def extract_odds_pair(odds_payload, match_key=None):
    """
    API-Tennis get_odds usually returns:

    {
      "success": 1,
      "result": {
        "159923": {
          "Home/Away": {
            "Home": {
              "bet365": "2.50"
            },
            "Away": {
              "bet365": "1.50"
            }
          }
        }
      }
    }

    Returns:
      first_player_odds, second_player_odds
    """

    if not isinstance(odds_payload, dict):
        return None, None

    result = odds_payload.get("result")

    if not isinstance(result, dict):
        return None, None

    match_data = None

    if match_key is not None and str(match_key) in result:
        match_data = result.get(str(match_key))

    if match_data is None:
        for value in result.values():
            if isinstance(value, dict):
                match_data = value
                break

    if not isinstance(match_data, dict):
        return None, None

    home_away = None

    for key, value in match_data.items():
        k = lower(key)

        if k in {
            "home/away",
            "home away",
            "match winner",
            "winner",
            "moneyline",
            "2 way",
            "2way",
        }:
            home_away = value
            break

    if home_away is None:
        # Fallback: sometimes market can be first nested dict that has Home/Away.
        for value in match_data.values():
            if isinstance(value, dict):
                keys = {lower(k) for k in value.keys()}
                if {"home", "away"}.issubset(keys) or {"1", "2"}.issubset(keys):
                    home_away = value
                    break

    if not isinstance(home_away, dict):
        return None, None

    home = None
    away = None

    for key, value in home_away.items():
        k = lower(key)

        if k in {"home", "1", "first", "first player", "player 1"}:
            home = value

        if k in {"away", "2", "second", "second player", "player 2"}:
            away = value

    p1 = best_price(home)
    p2 = best_price(away)

    return p1, p2


def fetch_odds_for_match(match_key):
    try:
        return fetch_api(
            "get_odds",
            {"match_key": match_key},
            retries=2,
            sleep_seconds=0.5,
        )
    except Exception as e:
        print(f"  odds error for match_key={match_key}: {e}")
        return {}


def is_odds_allowed(odds):
    if odds is None:
        return False

    return MIN_ODDS <= odds <= MAX_ODDS


def build_pick_from_fixture(row):
    event_key = get_event_key(row)
    first = get_first_player(row)
    second = get_second_player(row)

    if not event_key:
        return None, {
            "reason": "missing_event_key",
            "raw": row,
        }

    if not first or not second:
        return None, {
            "reason": "missing_players",
            "event_key": event_key,
            "raw": row,
        }

    if not is_finished(row):
        return None, {
            "reason": "not_finished",
            "event_key": event_key,
            "match": f"{first} - {second}",
        }

    winner_side = parse_final_result(row)

    if winner_side not in {1, 2}:
        return None, {
            "reason": "winner_unknown",
            "event_key": event_key,
            "match": f"{first} - {second}",
            "final_result": get_first(row, ["event_final_result", "final_result", "result"]),
            "winner": get_first(row, ["event_winner", "winner", "event_winner_player"]),
        }

    tour = infer_tour(row)
    surface = infer_surface(row)

    signal = get_elo_signal(
        first,
        second,
        surface=surface,
        tour=tour,
    )

    if not signal.get("matched"):
        return None, {
            "reason": "elo_unmatched",
            "event_key": event_key,
            "match": f"{first} - {second}",
            "first": first,
            "second": second,
            "tour": tour,
            "surface": surface,
            "first_matched": signal.get("player", {}).get("matched"),
            "second_matched": signal.get("opponent", {}).get("matched"),
            "first_method": signal.get("player", {}).get("match_method"),
            "second_method": signal.get("opponent", {}).get("match_method"),
        }

    overall_diff = signal.get("overall_elo_diff")
    surface_diff = signal.get("surface_elo_diff")

    if overall_diff is None:
        return None, {
            "reason": "elo_diff_missing",
            "event_key": event_key,
            "match": f"{first} - {second}",
        }

    abs_overall_diff = abs(float(overall_diff))

    if abs_overall_diff < MIN_ELO_DIFF:
        return None, {
            "reason": "elo_diff_too_low",
            "event_key": event_key,
            "match": f"{first} - {second}",
            "abs_overall_elo_diff": round(abs_overall_diff, 2),
        }

    if overall_diff > 0:
        pick_side = 1
        pick_player = first
        opponent = second
    else:
        pick_side = 2
        pick_player = second
        opponent = first

    return {
        "event_key": str(event_key),
        "date": get_event_date(row),
        "time": get_event_time(row),
        "match": f"{first} - {second}",
        "first_player": first,
        "second_player": second,
        "pick": pick_player,
        "opponent": opponent,
        "pick_side": pick_side,
        "winner_side": winner_side,
        "result": "win" if pick_side == winner_side else "loss",
        "tour": tour,
        "surface": surface,
        "final_result": get_first(row, ["event_final_result", "final_result", "result"]),
        "overall_elo_diff": round(float(overall_diff), 3),
        "surface_elo_diff": round(float(surface_diff), 3) if surface_diff is not None else None,
        "abs_overall_elo_diff": round(abs_overall_diff, 3),
        "abs_surface_elo_diff": round(abs(float(surface_diff)), 3) if surface_diff is not None else None,
        "elo_first": signal.get("player", {}).get("overall_elo"),
        "elo_second": signal.get("opponent", {}).get("overall_elo"),
        "matched_first": signal.get("player", {}).get("matched_name"),
        "matched_second": signal.get("opponent", {}).get("matched_name"),
    }, None


def enrich_pick_with_odds(pick):
    event_key = pick["event_key"]

    odds_payload = fetch_odds_for_match(event_key)
    p1_odds, p2_odds = extract_odds_pair(odds_payload, match_key=event_key)

    pick["first_player_odds"] = p1_odds
    pick["second_player_odds"] = p2_odds

    pick_odds = p1_odds if pick["pick_side"] == 1 else p2_odds
    pick["odds"] = pick_odds

    if not is_odds_allowed(pick_odds):
        return None, {
            "reason": "odds_missing_or_out_of_range",
            "event_key": event_key,
            "match": pick["match"],
            "pick": pick["pick"],
            "pick_side": pick["pick_side"],
            "first_player_odds": p1_odds,
            "second_player_odds": p2_odds,
            "min_odds": MIN_ODDS,
            "max_odds": MAX_ODDS,
        }

    if pick["result"] == "win":
        profit = pick_odds - 1.0
    else:
        profit = -1.0

    pick["stake"] = 1.0
    pick["profit"] = round(profit, 4)

    return pick, None


def empty_stats():
    return {
        "n": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0.0,
        "profit": 0.0,
        "stake": 0.0,
        "roi": 0.0,
        "avg_odds": 0.0,
        "avg_abs_overall_elo_diff": 0.0,
    }


def summarize(rows):
    if not rows:
        return empty_stats()

    n = len(rows)
    wins = sum(1 for r in rows if r.get("result") == "win")
    losses = sum(1 for r in rows if r.get("result") == "loss")
    profit = sum(safe_float(r.get("profit"), 0.0) or 0.0 for r in rows)
    stake = sum(safe_float(r.get("stake"), 0.0) or 0.0 for r in rows)

    odds_values = [safe_float(r.get("odds")) for r in rows if safe_float(r.get("odds")) is not None]
    diff_values = [
        safe_float(r.get("abs_overall_elo_diff"))
        for r in rows
        if safe_float(r.get("abs_overall_elo_diff")) is not None
    ]

    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / n * 100, 2) if n else 0.0,
        "profit": round(profit, 4),
        "stake": round(stake, 4),
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
        "avg_odds": round(sum(odds_values) / len(odds_values), 3) if odds_values else 0.0,
        "avg_abs_overall_elo_diff": round(sum(diff_values) / len(diff_values), 2) if diff_values else 0.0,
    }


def bucket_elo(diff):
    diff = safe_float(diff)

    if diff is None:
        return "unknown"

    if diff < 80:
        return "60-80"
    if diff < 100:
        return "80-100"
    if diff < 120:
        return "100-120"
    if diff < 150:
        return "120-150"
    if diff < 180:
        return "150-180"
    if diff < 220:
        return "180-220"

    return "220+"


def bucket_odds(odds):
    odds = safe_float(odds)

    if odds is None:
        return "unknown"

    if odds < 2.00:
        return "1.90-2.00"
    if odds < 2.20:
        return "2.00-2.20"
    if odds < 2.40:
        return "2.20-2.40"

    return "2.40-2.70"


def summarize_by(rows, key_func):
    buckets = {}

    for row in rows:
        key = key_func(row)
        buckets.setdefault(key, []).append(row)

    return {
        key: summarize(value)
        for key, value in sorted(buckets.items(), key=lambda x: str(x[0]))
    }


def build_report(rows, missing, meta):
    return {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "api-tennis",
        "strategy": "elo_only_market_backtest",
        "settings": {
            "backtest_days_back": BACKTEST_DAYS_BACK,
            "min_elo_diff": MIN_ELO_DIFF,
            "min_odds": MIN_ODDS,
            "max_odds": MAX_ODDS,
        },
        "meta": meta,
        "overall": summarize(rows),
        "by_elo_bucket": summarize_by(rows, lambda r: bucket_elo(r.get("abs_overall_elo_diff"))),
        "by_odds_bucket": summarize_by(rows, lambda r: bucket_odds(r.get("odds"))),
        "by_tour": summarize_by(rows, lambda r: r.get("tour") or "unknown"),
        "by_surface": summarize_by(rows, lambda r: r.get("surface") or "unknown"),
        "missing_summary": summarize_missing(missing),
    }


def summarize_missing(missing):
    out = {}

    for item in missing:
        reason = item.get("reason") or "unknown"
        out[reason] = out.get(reason, 0) + 1

    return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))


def build_table(report):
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
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| N | W-L | WR | Profit | Stake | ROI | Avg odds | Avg abs ELO diff |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")

    s = report["overall"]
    lines.append(
        f"| {s['n']} | {s['wins']}-{s['losses']} | {s['win_rate']}% | "
        f"{s['profit']}u | {s['stake']}u | {s['roi']}% | "
        f"{s['avg_odds']} | {s['avg_abs_overall_elo_diff']} |"
    )

    for section, title in [
        ("by_elo_bucket", "By ELO bucket"),
        ("by_odds_bucket", "By odds bucket"),
        ("by_tour", "By tour"),
        ("by_surface", "By surface"),
    ]:
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Bucket | N | W-L | WR | Profit | ROI | Avg odds |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")

        for key, b in report.get(section, {}).items():
            lines.append(
                f"| {key} | {b['n']} | {b['wins']}-{b['losses']} | "
                f"{b['win_rate']}% | {b['profit']}u | {b['roi']}% | {b['avg_odds']} |"
            )

    lines.append("")
    lines.append("## Missing summary")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|---|---:|")

    for reason, count in report.get("missing_summary", {}).items():
        lines.append(f"| {reason} | {count} |")

    return "\n".join(lines)


def collect_rows():
    end_date = today_local()
    start_date = end_date - timedelta(days=BACKTEST_DAYS_BACK)

    fixtures = collect_fixtures(start_date, end_date)

    missing = []
    elo_candidates = []

    for fixture in fixtures:
        pick, miss = build_pick_from_fixture(fixture)

        if pick:
            elo_candidates.append(pick)
        elif miss:
            missing.append(miss)

    print(f"Target fixtures after ELO filter: {len(elo_candidates)}")

    rows = []

    total = len(elo_candidates)

    for index, pick in enumerate(elo_candidates, start=1):
        if index <= 10 or index % 25 == 0 or index == total:
            print(f"Fetching odds: {index}/{total} match_key={pick['event_key']}")

        enriched, miss = enrich_pick_with_odds(pick)

        if enriched:
            rows.append(enriched)
        elif miss:
            missing.append(miss)

        time.sleep(0.12)

    meta = {
        "fixtures_total": len(fixtures),
        "elo_candidates": len(elo_candidates),
        "rows": len(rows),
        "missing": len(missing),
        "date_start": start_date.isoformat(),
        "date_end": end_date.isoformat(),
    }

    return rows, missing, meta


def main():
    rows, missing, meta = collect_rows()
    report = build_report(rows, missing, meta)

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_ROWS_FILE, rows)
    save_json(OUTPUT_MISSING_FILE, {
        "generated_at": report["generated_at"],
        "settings": report["settings"],
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
    print(report["overall"])
    print("")


if __name__ == "__main__":
    main()

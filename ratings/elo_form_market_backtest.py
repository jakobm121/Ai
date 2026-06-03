import json
import os
import sys
import math
import time
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict, deque

sys.path.append(os.path.dirname(__file__))

try:
    from elo_lookup import get_elo_signal
except Exception as e:
    raise RuntimeError(f"Cannot import ratings/elo_lookup.py: {e}")


TZ_NAME = "Europe/Ljubljana"
TZ = ZoneInfo(TZ_NAME)

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

DAYS_BACK = int(os.getenv("BACKTEST_DAYS_BACK", "5"))
FORM_DAYS_BACK = int(os.getenv("FORM_DAYS_BACK", "45"))
MIN_ELO_DIFF = float(os.getenv("MIN_ELO_DIFF", "60"))

OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest_report.json"
OUTPUT_ROWS_FILE = "ratings/elo_form_market_backtest_rows.json"
OUTPUT_MISSING_FILE = "ratings/elo_form_market_backtest_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest_table.md"


def now_local():
    return datetime.now(TZ)


def now_iso():
    return now_local().isoformat()


def today_str():
    return now_local().date().isoformat()


def date_str(days_ago):
    return (now_local().date() - timedelta(days=days_ago)).isoformat()


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
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def clean_name(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def fetch_api(method, params=None, retries=3, sleep_seconds=1.2):
    if not API_KEY:
        raise RuntimeError("Missing env var TENNIS_API_KEY or API_KEY")

    query = {
        "method": method,
        "APIkey": API_KEY,
    }

    if params:
        query.update(params)

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE_URL, params=query, timeout=40)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict) and str(data.get("success")) == "0":
                err = data.get("error") or data.get("message") or data
                raise RuntimeError(f"API-Tennis error for {method}: {err}")

            return data

        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(sleep_seconds * attempt)

    raise RuntimeError(f"API request failed for {method}: {last_error}")


def api_result_list(data):
    if isinstance(data, dict):
        value = data.get("result")
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]

    if isinstance(data, list):
        return data

    return []


def get_value(row, keys, default=None):
    for key in keys:
        if isinstance(row, dict) and row.get(key) not in [None, ""]:
            return row.get(key)
    return default


def extract_event_key(row):
    return str(get_value(row, [
        "event_key",
        "fixture_key",
        "match_key",
        "id",
        "event_id",
    ], "") or "").strip()


def extract_date(row):
    return get_value(row, [
        "event_date",
        "date",
        "match_date",
        "fixture_date",
    ])


def extract_time(row):
    return get_value(row, [
        "event_time",
        "time",
        "match_time",
        "fixture_time",
    ])


def extract_players(row):
    p1 = clean_name(get_value(row, [
        "event_first_player",
        "first_player",
        "player1",
        "home_player",
        "home_team",
        "player_home",
    ]))

    p2 = clean_name(get_value(row, [
        "event_second_player",
        "second_player",
        "player2",
        "away_player",
        "away_team",
        "player_away",
    ]))

    return p1, p2


def infer_tour(row):
    text = " ".join(str(get_value(row, [k], "")) for k in [
        "event_type_type",
        "event_type",
        "league_name",
        "tournament_name",
        "event_name",
    ]).lower()

    if "wta" in text or "women" in text:
        return "wta"

    if "atp" in text or "men" in text:
        return "atp"

    return None


def infer_surface(row):
    surface = get_value(row, [
        "surface",
        "event_surface",
        "court_surface",
        "court",
    ])

    if surface:
        return str(surface).lower()

    return None


def is_singles(row):
    text = " ".join(str(get_value(row, [k], "")) for k in [
        "event_type_type",
        "event_type",
        "league_name",
        "event_name",
        "tournament_name",
    ]).lower()

    if "double" in text or "doubles" in text:
        return False

    p1, p2 = extract_players(row)
    if not p1 or not p2:
        return False

    if "/" in p1 or "/" in p2:
        return False

    return True


def extract_winner_name(row):
    winner = clean_name(get_value(row, [
        "event_winner",
        "winner",
        "match_winner",
        "winner_name",
    ]))

    p1, p2 = extract_players(row)

    if winner in {"First Player", "first_player", "1", "Home", "home"}:
        return p1

    if winner in {"Second Player", "second_player", "2", "Away", "away"}:
        return p2

    if winner:
        return winner

    return None


def is_finished(row):
    status = str(get_value(row, [
        "event_status",
        "status",
        "match_status",
        "fixture_status",
    ], "") or "").lower()

    if any(x in status for x in ["finished", "final", "ended", "complete", "completed"]):
        return True

    winner = extract_winner_name(row)
    return bool(winner)


def collect_fixtures(date_start, date_stop):
    data = fetch_api("get_fixtures", {
        "date_start": date_start,
        "date_stop": date_stop,
    })
    return api_result_list(data)


def collect_odds(date_start, date_stop):
    # API-Tennis accounti nimajo vedno odds endpointa. Zato je to robustno:
    # če endpoint ni dostopen, backtest še vedno dela brez market odds.
    try:
        data = fetch_api("get_odds", {
            "date_start": date_start,
            "date_stop": date_stop,
        })
        return api_result_list(data)
    except Exception as e:
        print(f"WARNING: get_odds failed, continuing without odds: {e}")
        return []


def flatten_numbers(obj):
    out = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).lower()
            if key in {"1", "2", "home", "away", "first", "second", "player1", "player2"}:
                num = safe_float(v)
                if num and 1.01 <= num <= 20:
                    out.append((key, num))
            out.extend(flatten_numbers(v))

    elif isinstance(obj, list):
        for item in obj:
            out.extend(flatten_numbers(item))

    return out


def extract_moneyline_odds(row):
    # Poskus 1: pogosta API-Tennis oblika
    p1_candidates = [
        "odd_1",
        "odds_1",
        "home_odd",
        "first_odd",
        "player1_odd",
        "event_odd_1",
    ]
    p2_candidates = [
        "odd_2",
        "odds_2",
        "away_odd",
        "second_odd",
        "player2_odd",
        "event_odd_2",
    ]

    p1 = safe_float(get_value(row, p1_candidates))
    p2 = safe_float(get_value(row, p2_candidates))

    if p1 and p2 and 1.01 <= p1 <= 20 and 1.01 <= p2 <= 20:
        return p1, p2

    # Poskus 2: rekurzivno iz strukture
    nums = flatten_numbers(row)
    one = [v for k, v in nums if k in {"1", "home", "first", "player1"}]
    two = [v for k, v in nums if k in {"2", "away", "second", "player2"}]

    if one and two:
        return one[0], two[0]

    return None, None


def build_odds_map(odds_rows):
    odds_map = {}

    for row in odds_rows:
        if not isinstance(row, dict):
            continue

        key = extract_event_key(row)
        if not key:
            continue

        p1_odd, p2_odd = extract_moneyline_odds(row)

        if p1_odd and p2_odd:
            odds_map[key] = {
                "p1_odd": p1_odd,
                "p2_odd": p2_odd,
                "raw": row,
            }

    return odds_map


def match_name(a, b):
    if not a or not b:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


def calculate_form_maps(all_fixtures):
    completed = []

    for row in all_fixtures:
        if not isinstance(row, dict):
            continue
        if not is_singles(row):
            continue
        if not is_finished(row):
            continue

        p1, p2 = extract_players(row)
        winner = extract_winner_name(row)
        d = extract_date(row)

        if not p1 or not p2 or not winner or not d:
            continue

        completed.append({
            "date": str(d),
            "p1": p1,
            "p2": p2,
            "winner": winner,
        })

    completed.sort(key=lambda x: x["date"])

    history = defaultdict(list)

    for m in completed:
        p1 = m["p1"]
        p2 = m["p2"]
        winner = m["winner"]

        p1_win = match_name(winner, p1)
        p2_win = match_name(winner, p2)

        if p1_win or p2_win:
            history[p1.lower()].append({
                "date": m["date"],
                "opponent": p2,
                "win": p1_win,
            })
            history[p2.lower()].append({
                "date": m["date"],
                "opponent": p1,
                "win": p2_win,
            })

    return history


def form_before(history, player, match_date, n):
    if not player or not match_date:
        return {
            "n": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
        }

    rows = [
        x for x in history.get(player.lower(), [])
        if str(x.get("date")) < str(match_date)
    ]

    rows = rows[-n:]
    wins = sum(1 for x in rows if x.get("win"))
    losses = sum(1 for x in rows if not x.get("win"))
    total = wins + losses

    return {
        "n": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / total * 100, 2) if total else 0.0,
    }


def form_edge(f1, f2):
    return round((f1.get("win_rate", 0.0) - f2.get("win_rate", 0.0)), 2)


def pick_from_elo_form(signal, p1, p2, f1_5, f2_5, f1_10, f2_10):
    if not signal.get("matched"):
        return None

    overall_diff = safe_float(signal.get("overall_elo_diff"))
    surface_diff = safe_float(signal.get("surface_elo_diff"))

    chosen_diff = surface_diff if surface_diff is not None else overall_diff

    if chosen_diff is None:
        return None

    abs_diff = abs(chosen_diff)

    if abs_diff < MIN_ELO_DIFF:
        return None

    elo_pick = p1 if chosen_diff > 0 else p2

    edge5 = form_edge(f1_5, f2_5)
    edge10 = form_edge(f1_10, f2_10)

    form_score = edge5 * 0.65 + edge10 * 0.35

    if elo_pick == p2:
        form_score *= -1

    confidence = abs_diff + form_score

    return {
        "pick": elo_pick,
        "elo_pick": elo_pick,
        "elo_diff_used": round(chosen_diff, 2),
        "abs_elo_diff_used": round(abs_diff, 2),
        "overall_elo_diff": signal.get("overall_elo_diff"),
        "surface_elo_diff": signal.get("surface_elo_diff"),
        "form_edge_5": edge5,
        "form_edge_10": edge10,
        "form_score_for_pick": round(form_score, 2),
        "confidence": round(confidence, 2),
    }


def result_for_pick(pick, winner):
    if not pick or not winner:
        return None
    return "win" if match_name(pick, winner) else "loss"


def profit_for_pick(result, odds):
    if result == "win":
        return round(odds - 1, 4)
    if result == "loss":
        return -1.0
    return 0.0


def summarize(rows):
    settled = [r for r in rows if r.get("result") in {"win", "loss"}]
    wins = sum(1 for r in settled if r.get("result") == "win")
    losses = sum(1 for r in settled if r.get("result") == "loss")
    stake = sum(safe_float(r.get("stake"), 0.0) or 0.0 for r in settled)
    profit = sum(safe_float(r.get("profit"), 0.0) or 0.0 for r in settled)

    with_odds = [r for r in settled if r.get("odds")]

    return {
        "n": len(settled),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(settled) * 100, 2) if settled else 0.0,
        "stake": round(stake, 4),
        "profit": round(profit, 4),
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
        "with_odds": len(with_odds),
        "avg_odds": round(sum(r["odds"] for r in with_odds) / len(with_odds), 3) if with_odds else 0.0,
    }


def bucket_summary(rows, key_fn):
    buckets = defaultdict(list)

    for row in rows:
        key = key_fn(row)
        buckets[key].append(row)

    return {
        str(key): summarize(value)
        for key, value in sorted(buckets.items(), key=lambda x: str(x[0]))
    }


def collect_rows():
    target_start = date_str(DAYS_BACK)
    target_stop = today_str()

    form_start = date_str(FORM_DAYS_BACK)
    form_stop = today_str()

    print(f"Fetching fixtures for form: {form_start} -> {form_stop}")
    all_fixtures = collect_fixtures(form_start, form_stop)

    print(f"Fetching odds: {target_start} -> {target_stop}")
    odds_rows = collect_odds(target_start, target_stop)
    odds_map = build_odds_map(odds_rows)

    history = calculate_form_maps(all_fixtures)

    rows = []
    missing = []

    for row in all_fixtures:
        if not isinstance(row, dict):
            continue

        match_date = extract_date(row)

        if not match_date:
            continue

        if not (target_start <= str(match_date) <= target_stop):
            continue

        if not is_singles(row):
            continue

        if not is_finished(row):
            continue

        p1, p2 = extract_players(row)
        winner = extract_winner_name(row)

        if not p1 or not p2 or not winner:
            continue

        event_key = extract_event_key(row)
        tour = infer_tour(row)
        surface = infer_surface(row)

        signal = get_elo_signal(
            p1,
            p2,
            surface=surface,
            tour=tour,
        )

        if not signal.get("matched"):
            missing.append({
                "date": match_date,
                "event_key": event_key,
                "match": f"{p1} vs {p2}",
                "p1": p1,
                "p2": p2,
                "tour": tour,
                "surface": surface,
                "p1_matched": signal.get("player", {}).get("matched"),
                "p2_matched": signal.get("opponent", {}).get("matched"),
                "p1_method": signal.get("player", {}).get("match_method"),
                "p2_method": signal.get("opponent", {}).get("match_method"),
            })
            continue

        f1_5 = form_before(history, p1, match_date, 5)
        f2_5 = form_before(history, p2, match_date, 5)
        f1_10 = form_before(history, p1, match_date, 10)
        f2_10 = form_before(history, p2, match_date, 10)

        pick_data = pick_from_elo_form(signal, p1, p2, f1_5, f2_5, f1_10, f2_10)

        if not pick_data:
            continue

        result = result_for_pick(pick_data["pick"], winner)

        odds_info = odds_map.get(event_key, {})
        p1_odd = odds_info.get("p1_odd")
        p2_odd = odds_info.get("p2_odd")

        odds = None
        if match_name(pick_data["pick"], p1):
            odds = p1_odd
        elif match_name(pick_data["pick"], p2):
            odds = p2_odd

        stake = 1.0 if odds else 0.0
        profit = profit_for_pick(result, odds) if odds else 0.0

        rows.append({
            "date": match_date,
            "time": extract_time(row),
            "event_key": event_key,
            "tour": tour,
            "surface": surface,
            "match": f"{p1} vs {p2}",
            "player_1": p1,
            "player_2": p2,
            "winner": winner,
            "pick": pick_data["pick"],
            "result": result,
            "odds": odds,
            "stake": stake,
            "profit": profit,
            "p1_odd": p1_odd,
            "p2_odd": p2_odd,
            "elo": {
                "overall_elo_diff": pick_data["overall_elo_diff"],
                "surface_elo_diff": pick_data["surface_elo_diff"],
                "elo_diff_used": pick_data["elo_diff_used"],
                "abs_elo_diff_used": pick_data["abs_elo_diff_used"],
                "p1_matched_name": signal.get("player", {}).get("matched_name"),
                "p2_matched_name": signal.get("opponent", {}).get("matched_name"),
            },
            "form": {
                "p1_last5": f1_5,
                "p2_last5": f2_5,
                "p1_last10": f1_10,
                "p2_last10": f2_10,
                "form_edge_5": pick_data["form_edge_5"],
                "form_edge_10": pick_data["form_edge_10"],
                "form_score_for_pick": pick_data["form_score_for_pick"],
            },
            "confidence": pick_data["confidence"],
        })

    meta = {
        "target_start": target_start,
        "target_stop": target_stop,
        "form_start": form_start,
        "form_stop": form_stop,
        "fixtures_loaded": len(all_fixtures),
        "odds_rows_loaded": len(odds_rows),
        "odds_matched_events": len(odds_map),
        "min_elo_diff": MIN_ELO_DIFF,
    }

    return rows, missing, meta


def confidence_bucket(row):
    c = safe_float(row.get("confidence"), 0.0) or 0.0

    if c < 80:
        return "<80"
    if c < 120:
        return "80-120"
    if c < 160:
        return "120-160"
    if c < 220:
        return "160-220"
    return "220+"


def elo_bucket(row):
    d = safe_float(row.get("elo", {}).get("abs_elo_diff_used"), 0.0) or 0.0

    if d < 80:
        return "60-80"
    if d < 120:
        return "80-120"
    if d < 160:
        return "120-160"
    if d < 220:
        return "160-220"
    return "220+"


def build_table(report, rows):
    lines = []

    lines.append("# ELO + form market backtest")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    s = report["summary"]["overall"]
    lines.append(f"- Picks: {s['n']}")
    lines.append(f"- W-L: {s['wins']}-{s['losses']}")
    lines.append(f"- WR: {s['win_rate']}%")
    lines.append(f"- With odds: {s['with_odds']}")
    lines.append(f"- Profit: {s['profit']}u")
    lines.append(f"- ROI: {s['roi']}%")
    lines.append(f"- Avg odds: {s['avg_odds']}")
    lines.append("")
    lines.append("## By tour")
    lines.append("")
    lines.append("| Tour | N | W-L | WR | With odds | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, b in report["summary"]["by_tour"].items():
        lines.append(f"| {key} | {b['n']} | {b['wins']}-{b['losses']} | {b['win_rate']}% | {b['with_odds']} | {b['profit']}u | {b['roi']}% | {b['avg_odds']} |")

    lines.append("")
    lines.append("## By ELO bucket")
    lines.append("")
    lines.append("| ELO diff | N | W-L | WR | With odds | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, b in report["summary"]["by_elo_bucket"].items():
        lines.append(f"| {key} | {b['n']} | {b['wins']}-{b['losses']} | {b['win_rate']}% | {b['with_odds']} | {b['profit']}u | {b['roi']}% | {b['avg_odds']} |")

    lines.append("")
    lines.append("## By confidence bucket")
    lines.append("")
    lines.append("| Confidence | N | W-L | WR | With odds | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for key, b in report["summary"]["by_confidence_bucket"].items():
        lines.append(f"| {key} | {b['n']} | {b['wins']}-{b['losses']} | {b['win_rate']}% | {b['with_odds']} | {b['profit']}u | {b['roi']}% | {b['avg_odds']} |")

    lines.append("")
    lines.append("## Picks")
    lines.append("")
    lines.append("| Date | Match | Pick | Winner | Result | Odds | ELO diff | Conf |")
    lines.append("|---|---|---|---|---|---:|---:|---:|")

    for r in rows[:200]:
        lines.append(
            f"| {r.get('date')} | {r.get('match')} | {r.get('pick')} | {r.get('winner')} | "
            f"{r.get('result')} | {r.get('odds') or ''} | "
            f"{r.get('elo', {}).get('elo_diff_used')} | {r.get('confidence')} |"
        )

    return "\n".join(lines)


def main():
    rows, missing, meta = collect_rows()

    rows.sort(key=lambda r: (str(r.get("date")), str(r.get("time") or ""), str(r.get("match"))))

    report = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "api-tennis",
        "meta": meta,
        "summary": {
            "overall": summarize(rows),
            "by_tour": bucket_summary(rows, lambda r: r.get("tour") or "unknown"),
            "by_elo_bucket": bucket_summary(rows, elo_bucket),
            "by_confidence_bucket": bucket_summary(rows, confidence_bucket),
        },
        "missing_count": len(missing),
    }

    save_json(OUTPUT_ROWS_FILE, rows)
    save_json(OUTPUT_MISSING_FILE, {
        "generated_at": report["generated_at"],
        "missing": missing,
    })
    save_json(OUTPUT_REPORT_FILE, report)
    save_text(OUTPUT_TABLE_FILE, build_table(report, rows))

    print("")
    print("ELO + FORM MARKET BACKTEST DONE")
    print(f"Rows:       {len(rows)}")
    print(f"Missing:    {len(missing)}")
    print(f"Report:     {OUTPUT_REPORT_FILE}")
    print(f"Rows file:  {OUTPUT_ROWS_FILE}")
    print(f"Missing:    {OUTPUT_MISSING_FILE}")
    print(f"Table:      {OUTPUT_TABLE_FILE}")
    print("")
    print(json.dumps(report["summary"]["overall"], indent=2, ensure_ascii=False))
    print("")


if __name__ == "__main__":
    main()

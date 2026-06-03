#!/usr/bin/env python3
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.append(os.path.dirname(__file__))
from elo_lookup import get_elo_signal

TZ_NAME = "Europe/Ljubljana"
OUTPUT_MATCHES_FILE = "data/elo_form_market_backtest_matches.json"
OUTPUT_REPORT_FILE = "ratings/elo_form_market_backtest_report.json"
OUTPUT_TABLE_FILE = "ratings/elo_form_market_backtest_table.md"

ODDS_API_KEY_ENV = "ODDS_API_KEY"
ODDS_API_BASE_URL = os.getenv("ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4")
SPORT_KEYS = [x.strip() for x in os.getenv("TENNIS_SPORT_KEYS", "tennis_atp,tennis_wta").split(",") if x.strip()]
REGIONS = os.getenv("ODDS_REGIONS", "eu")
MARKETS = os.getenv("ODDS_MARKETS", "h2h")
ODDS_FORMAT = os.getenv("ODDS_FORMAT", "decimal")
BOOKMAKERS = os.getenv("ODDS_BOOKMAKERS", "")
TARGET_DAYS_BACK = int(os.getenv("ELO_FORM_TARGET_DAYS_BACK", "5"))
FORM_DAYS_BACK = int(os.getenv("ELO_FORM_HISTORY_DAYS_BACK", "120"))
REQUEST_SLEEP_SECONDS = float(os.getenv("ODDS_REQUEST_SLEEP_SECONDS", "0.25"))
ELO_CONFIRM_THRESHOLD = float(os.getenv("ELO_CONFIRM_THRESHOLD", "50"))
FORM5_CONFIRM_THRESHOLD = float(os.getenv("FORM5_CONFIRM_THRESHOLD", "0.10"))
FORM10_CONFIRM_THRESHOLD = float(os.getenv("FORM10_CONFIRM_THRESHOLD", "0.10"))


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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


def normalize_name(value):
    return " ".join(str(value or "").strip().split())


def infer_tour_from_sport_key(sport_key):
    sport_key = str(sport_key or "").lower()
    if "wta" in sport_key:
        return "wta"
    if "atp" in sport_key:
        return "atp"
    return None


def event_datetime(event):
    raw = event.get("commence_time") or event.get("completed_at") or event.get("last_update")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def is_event_in_window(event, start_utc, end_utc):
    dt = event_datetime(event)
    return bool(dt and start_utc <= dt <= end_utc)


def fetch_api(path, params):
    api_key = os.getenv(ODDS_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"Missing env var {ODDS_API_KEY_ENV}")
    params = dict(params)
    params["apiKey"] = api_key
    url = f"{ODDS_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "elo-form-market-backtest/1.0"})
    with urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_completed_winner(score_event):
    if not score_event.get("completed"):
        return None
    parsed = []
    for item in score_event.get("scores") or []:
        name = normalize_name(item.get("name"))
        score = safe_float(item.get("score"))
        if name and score is not None:
            parsed.append((name, score))
    if len(parsed) < 2:
        return None
    parsed = sorted(parsed, key=lambda x: x[1], reverse=True)
    if parsed[0][1] == parsed[1][1]:
        return None
    return parsed[0][0]


def collect_scores(days_back):
    end_utc = datetime.now(timezone.utc)
    start_utc = end_utc - timedelta(days=days_back)
    out = []
    for sport_key in SPORT_KEYS:
        data = fetch_api(f"sports/{sport_key}/scores", {"daysFrom": days_back, "dateFormat": "iso"})
        time.sleep(REQUEST_SLEEP_SECONDS)
        for ev in data:
            if not is_event_in_window(ev, start_utc, end_utc):
                continue
            home = normalize_name(ev.get("home_team"))
            away = normalize_name(ev.get("away_team"))
            winner = get_completed_winner(ev)
            dt = event_datetime(ev)
            if not home or not away or not winner or not dt:
                continue
            out.append({
                "id": ev.get("id"),
                "sport_key": sport_key,
                "tour": infer_tour_from_sport_key(sport_key),
                "commence_time": ev.get("commence_time"),
                "timestamp": dt.timestamp(),
                "home_team": home,
                "away_team": away,
                "winner": winner,
                "raw_score": ev.get("scores"),
            })
    return sorted(out, key=lambda x: x["timestamp"])


def collect_odds_for_event(sport_key, event_id):
    params = {"regions": REGIONS, "markets": MARKETS, "oddsFormat": ODDS_FORMAT, "dateFormat": "iso"}
    if BOOKMAKERS:
        params["bookmakers"] = BOOKMAKERS
    return fetch_api(f"sports/{sport_key}/events/{event_id}/odds", params)


def extract_best_h2h_odds(odds_event):
    best = {}
    for bookmaker in odds_event.get("bookmakers") or []:
        for market in bookmaker.get("markets") or []:
            if market.get("key") != "h2h":
                continue
            for outcome in market.get("outcomes") or []:
                name = normalize_name(outcome.get("name"))
                price = safe_float(outcome.get("price"))
                if not name or price is None:
                    continue
                if best.get(name) is None or price > best[name]:
                    best[name] = price
    return best


def profit_for_odds(odds, won, stake=1.0):
    if odds is None:
        return 0.0
    return round((odds - 1.0) * stake, 6) if won else -stake


def odds_bucket(odds):
    if odds is None:
        return "unknown"
    if odds < 1.40:
        return "<1.40"
    if odds < 1.80:
        return "1.40-1.80"
    if odds < 2.20:
        return "1.80-2.20"
    return "2.20+"


def build_history_index(score_events):
    history = {}
    for ev in score_events:
        p1, p2, winner = ev["home_team"], ev["away_team"], ev["winner"]
        for player, opponent in [(p1, p2), (p2, p1)]:
            history.setdefault(player.lower(), []).append({
                "timestamp": ev["timestamp"],
                "date": ev["commence_time"],
                "opponent": opponent,
                "won": player == winner,
                "tour": ev.get("tour"),
                "event_id": ev.get("id"),
            })
    for key in history:
        history[key].sort(key=lambda x: x["timestamp"])
    return history


def player_form(history, player, before_ts, n):
    rows = [r for r in history.get(player.lower(), []) if r["timestamp"] < before_ts][-n:]
    if not rows:
        return {"n": 0, "wins": 0, "losses": 0, "win_rate": None}
    wins = sum(1 for r in rows if r["won"])
    return {"n": len(rows), "wins": wins, "losses": len(rows) - wins, "win_rate": round(wins / len(rows), 4)}


def diff_or_none(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 4)


def choose_pick_by_elo_and_form(p1, p2, signal, form1_5, form2_5, form1_10, form2_10):
    overall_diff = signal.get("overall_elo_diff")
    if overall_diff is None:
        return None
    if overall_diff >= ELO_CONFIRM_THRESHOLD:
        pick = p1
        f5 = diff_or_none(form1_5["win_rate"], form2_5["win_rate"])
        f10 = diff_or_none(form1_10["win_rate"], form2_10["win_rate"])
    elif overall_diff <= -ELO_CONFIRM_THRESHOLD:
        pick = p2
        f5 = diff_or_none(form2_5["win_rate"], form1_5["win_rate"])
        f10 = diff_or_none(form2_10["win_rate"], form1_10["win_rate"])
    else:
        return {"status": "rejected", "reason": "elo_diff_too_small", "elo_pick": None, "elo_diff_abs": abs(overall_diff), "form5_diff": None, "form10_diff": None}
    f5_ok = f5 is not None and f5 >= FORM5_CONFIRM_THRESHOLD
    f10_ok = f10 is not None and f10 >= FORM10_CONFIRM_THRESHOLD
    if f5_ok and f10_ok:
        reason = "elo_plus_form5_plus_form10"
    elif f5_ok:
        reason = "elo_plus_form5"
    elif f10_ok:
        reason = "elo_plus_form10"
    else:
        reason = "form_not_confirming"
    return {"status": "confirmed" if (f5_ok or f10_ok) else "rejected", "reason": reason, "elo_pick": pick, "elo_diff_abs": abs(overall_diff), "form5_diff": f5, "form10_diff": f10}


def collect_rows():
    all_scores = collect_scores(FORM_DAYS_BACK)
    history = build_history_index(all_scores)
    end_utc = datetime.now(timezone.utc)
    start_utc = end_utc - timedelta(days=TARGET_DAYS_BACK)
    target_events = [ev for ev in all_scores if is_event_in_window(ev, start_utc, end_utc)]
    rows, missing = [], []
    for ev in target_events:
        p1, p2 = ev["home_team"], ev["away_team"]
        try:
            odds_event = collect_odds_for_event(ev["sport_key"], ev["id"])
            time.sleep(REQUEST_SLEEP_SECONDS)
            odds = extract_best_h2h_odds(odds_event)
        except Exception as exc:
            odds = {}
            missing.append({"event_id": ev.get("id"), "match": f"{p1} - {p2}", "reason": f"odds_fetch_failed: {exc}"})
        signal = get_elo_signal(p1, p2, surface=None, tour=ev.get("tour"))
        if not signal.get("matched"):
            missing.append({"event_id": ev.get("id"), "match": f"{p1} - {p2}", "reason": "elo_not_matched", "p1_matched": signal.get("player", {}).get("matched"), "p2_matched": signal.get("opponent", {}).get("matched")})
            continue
        form1_5 = player_form(history, p1, ev["timestamp"], 5)
        form2_5 = player_form(history, p2, ev["timestamp"], 5)
        form1_10 = player_form(history, p1, ev["timestamp"], 10)
        form2_10 = player_form(history, p2, ev["timestamp"], 10)
        decision = choose_pick_by_elo_and_form(p1, p2, signal, form1_5, form2_5, form1_10, form2_10)
        if not decision or decision["status"] != "confirmed":
            continue
        pick = decision["elo_pick"]
        pick_odds = odds.get(pick)
        won = pick == ev["winner"]
        rows.append({
            "date": ev["commence_time"], "event_id": ev.get("id"), "sport_key": ev.get("sport_key"), "tour": ev.get("tour"),
            "match": f"{p1} - {p2}", "player_1": p1, "player_2": p2, "winner": ev["winner"], "pick": pick,
            "result": "win" if won else "loss", "odds": pick_odds, "stake": 1.0 if pick_odds else 0.0,
            "profit": profit_for_odds(pick_odds, won, 1.0) if pick_odds else 0.0, "odds_bucket": odds_bucket(pick_odds),
            "elo": {"overall_elo_diff": signal.get("overall_elo_diff"), "surface_elo_diff": signal.get("surface_elo_diff"), "abs_overall_elo_diff": abs(signal.get("overall_elo_diff")) if signal.get("overall_elo_diff") is not None else None, "abs_surface_elo_diff": abs(signal.get("surface_elo_diff")) if signal.get("surface_elo_diff") is not None else None, "player_1_matched_name": signal.get("player", {}).get("matched_name"), "player_2_matched_name": signal.get("opponent", {}).get("matched_name")},
            "form": {"player_1_last5": form1_5, "player_2_last5": form2_5, "player_1_last10": form1_10, "player_2_last10": form2_10, "pick_form5_edge": decision["form5_diff"], "pick_form10_edge": decision["form10_diff"]},
            "decision": {"status": decision["status"], "reason": decision["reason"], "elo_diff_abs": decision["elo_diff_abs"], "thresholds": {"elo": ELO_CONFIRM_THRESHOLD, "form5": FORM5_CONFIRM_THRESHOLD, "form10": FORM10_CONFIRM_THRESHOLD}},
        })
    return rows, missing, {"all_score_events": len(all_scores), "target_events": len(target_events)}


def empty_stats():
    return {"n": 0, "wins": 0, "losses": 0, "stake": 0.0, "profit": 0.0, "avg_odds_sum": 0.0, "avg_odds_n": 0}


def add_row(stats, key, row):
    s = stats.setdefault(key, empty_stats())
    stake = safe_float(row.get("stake"), 0.0) or 0.0
    profit = safe_float(row.get("profit"), 0.0) or 0.0
    odds = safe_float(row.get("odds"))
    s["n"] += 1
    s["stake"] += stake
    s["profit"] += profit
    if row.get("result") == "win":
        s["wins"] += 1
    elif row.get("result") == "loss":
        s["losses"] += 1
    if odds is not None:
        s["avg_odds_sum"] += odds
        s["avg_odds_n"] += 1


def finalize_stats(stats):
    out = {}
    for key, s in stats.items():
        graded = s["wins"] + s["losses"]
        stake = s["stake"]
        out[key] = {"n": s["n"], "wins": s["wins"], "losses": s["losses"], "win_rate": round(s["wins"] / graded * 100, 2) if graded else 0.0, "profit": round(s["profit"], 3), "stake": round(stake, 3), "roi": round(s["profit"] / stake * 100, 2) if stake else 0.0, "avg_odds": round(s["avg_odds_sum"] / s["avg_odds_n"], 3) if s["avg_odds_n"] else 0.0}
    return out


def build_report(rows, missing, meta):
    stats = {}
    for row in rows:
        add_row(stats, "overall", row)
        add_row(stats, f"tour:{row.get('tour') or 'unknown'}", row)
        add_row(stats, f"reason:{row.get('decision', {}).get('reason') or 'unknown'}", row)
        add_row(stats, f"odds:{row.get('odds_bucket') or 'unknown'}", row)
        abs_elo = row.get("elo", {}).get("abs_overall_elo_diff")
        if abs_elo is not None:
            b = "0-70" if abs_elo < 70 else "70-120" if abs_elo < 120 else "120-180" if abs_elo < 180 else "180+"
            add_row(stats, f"elo:{b}", row)
    return {"generated_at": now_iso(), "timezone": TZ_NAME, "source": {"api_base_url": ODDS_API_BASE_URL, "sport_keys": SPORT_KEYS, "target_days_back": TARGET_DAYS_BACK, "form_days_back": FORM_DAYS_BACK, "regions": REGIONS, "markets": MARKETS, "bookmakers": BOOKMAKERS or "all"}, "thresholds": {"elo_confirm_threshold": ELO_CONFIRM_THRESHOLD, "form5_confirm_threshold": FORM5_CONFIRM_THRESHOLD, "form10_confirm_threshold": FORM10_CONFIRM_THRESHOLD}, "meta": meta, "stats": finalize_stats(stats), "rows": rows, "missing": missing}


def build_table(report):
    lines = ["# ELO + form market backtest", "", f"Generated: {report['generated_at']}", "", f"Target days back: {report['source']['target_days_back']}", f"Form history days back: {report['source']['form_days_back']}", "", "## Stats", "", "| Bucket | N | W-L | WR | Profit | Stake | ROI | Avg odds |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, s in report["stats"].items():
        lines.append(f"| {key} | {s['n']} | {s['wins']}-{s['losses']} | {s['win_rate']}% | {s['profit']}u | {s['stake']}u | {s['roi']}% | {s['avg_odds']} |")
    lines += ["", "## Confirmed picks", "", "| Date | Tour | Match | Pick | Odds | Result | Profit | Reason | ELO diff | F5 edge | F10 edge |", "|---|---|---|---|---:|---|---:|---|---:|---:|---:|"]
    for row in report["rows"][:200]:
        lines.append(f"| {row.get('date')} | {row.get('tour')} | {row.get('match')} | {row.get('pick')} | {row.get('odds') or ''} | {row.get('result')} | {row.get('profit')} | {row.get('decision', {}).get('reason')} | {round(row.get('elo', {}).get('abs_overall_elo_diff') or 0, 1)} | {row.get('form', {}).get('pick_form5_edge')} | {row.get('form', {}).get('pick_form10_edge')} |")
    lines += ["", f"Missing / skipped notes: {len(report.get('missing') or [])}", ""]
    return "\n".join(lines)


def main():
    rows, missing, meta = collect_rows()
    report = build_report(rows, missing, meta)
    save_json(OUTPUT_MATCHES_FILE, rows)
    save_json(OUTPUT_REPORT_FILE, report)
    save_text(OUTPUT_TABLE_FILE, build_table(report))
    print("\nELO + FORM MARKET BACKTEST DONE")
    print(f"Confirmed picks: {len(rows)}")
    print(f"Matches:         {OUTPUT_MATCHES_FILE}")
    print(f"Report:          {OUTPUT_REPORT_FILE}")
    print(f"Table:           {OUTPUT_TABLE_FILE}\n")
    print("Overall:")
    print(report["stats"].get("overall", {}))


if __name__ == "__main__":
    main()

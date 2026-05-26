import os
import json
import time
import re
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"

TZ_NAME = "Europe/Ljubljana"
DATA_DIR = "data"

RESULTS_FILE = f"{DATA_DIR}/jakob_results.json"
DEBUG_FILE = f"{DATA_DIR}/jakob_settle_debug.json"

SUMMARY_FILE = f"{DATA_DIR}/jakob_settle_summary.json"
TABLE_FILE = f"{DATA_DIR}/jakob_settle_table.csv"
REPORT_FILE = f"{DATA_DIR}/jakob_settle_report.md"

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.30


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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


def save_csv(path, rows):
    ensure_dirs()

    fieldnames = [
        "date",
        "time",
        "rank",
        "match",
        "pick",
        "side",
        "line",
        "odds",
        "bookmaker",
        "result",
        "total_games",
        "final_score",
        "profit",
        "stake",
        "jakob_score",
        "confidence",
        "quality_score",
        "edge_percent",
        "market_gap",
        "tournament",
        "event_type",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def save_text(path, text):
    ensure_dirs()

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


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


def fetch_fixture_by_event_key(event_key):
    data = api_call({
        "method": "get_fixtures",
        "event_key": event_key,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        return None

    result = data.get("result") or []

    if isinstance(result, list) and result:
        return result[0]

    if isinstance(result, dict):
        return result

    return None


def parse_set_pair_from_text(value):
    """
    Supports:
      6-7
      7-6(5)
      6 - 7
      10-8

    Tie-break number in parentheses is ignored.
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    match = re.search(r"(\d+)\s*-\s*(\d+)", text)

    if not match:
        return None

    return int(match.group(1)), int(match.group(2))


def parse_score_number(value):
    """
    API-Tennis sometimes returns tie-break set scores like:
      6.5 / 7.7
      6.8 / 7.10
      7.8 / 6.6

    For totals we only need games:
      6.5  -> 6
      7.10 -> 7
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if "." in text:
        text = text.split(".", 1)[0]

    try:
        return int(text)
    except Exception:
        return None


def parse_scores(scores):
    """
    Robust parser for API 'scores' array.

    Handles:
      {"score_first": "6", "score_second": "7"}
      {"score_first": "6.5", "score_second": "7.7"}
      {"score": "7-6(5)"}
    """
    parsed = []

    if not isinstance(scores, list):
        return parsed

    for s in scores:
        if not isinstance(s, dict):
            pair = parse_set_pair_from_text(s)

            if pair:
                parsed.append(pair)

            continue

        first = s.get("score_first")
        second = s.get("score_second")

        if first is not None and second is not None:
            a = parse_score_number(first)
            b = parse_score_number(second)

            if a is not None and b is not None:
                parsed.append((a, b))
                continue

        for key in (
            "score",
            "result",
            "set_score",
            "event_score",
            "score_set",
            "games",
            "value",
        ):
            pair = parse_set_pair_from_text(s.get(key))

            if pair:
                parsed.append(pair)
                break

    return parsed


def parse_scores_from_fixture(fixture):
    """
    First tries fixture['scores'].
    Then falls back to fixture-level result/score strings if API returns score there.
    """
    scores = fixture.get("scores") or []
    parsed = parse_scores(scores)

    if parsed:
        return parsed

    for key in (
        "event_final_result",
        "event_game_result",
        "event_result",
        "event_score",
        "final_score",
        "score",
    ):
        value = fixture.get(key)

        if not value:
            continue

        pairs = re.findall(r"(\d+)\s*-\s*(\d+)", str(value))

        if pairs:
            return [(int(a), int(b)) for a, b in pairs]

    return []


def total_games_from_parsed(parsed):
    return sum(a + b for a, b in parsed)


def final_score_string_from_parsed(parsed):
    return ", ".join(f"{a}-{b}" for a, b in parsed)


def is_bad_terminal_status(status):
    s = str(status or "").lower().strip()

    compact = (
        s.replace(" ", "")
         .replace("-", "")
         .replace("/", "")
         .replace(".", "")
    )

    bad = {
        "cancelled",
        "canceled",
        "postponed",
        "retired",
        "walkover",
        "wo",
        "abandoned",
        "interrupted",
        "suspended",
    }

    return s in bad or compact in bad


def compact_fixture_debug(fixture):
    """
    Saves score-related parts of the API fixture into debug file.
    """
    if not isinstance(fixture, dict):
        return fixture

    score_related = {}

    for key, value in fixture.items():
        lk = str(key).lower()

        if (
            "score" in lk
            or "result" in lk
            or "set" in lk
            or "point" in lk
            or "winner" in lk
            or "status" in lk
        ):
            score_related[key] = value

    return score_related


def settle_pick(pick, fixture):
    status_raw = fixture.get("event_status")
    status = str(status_raw or "").lower().strip()

    if is_bad_terminal_status(status):
        pick["result"] = "void"
        pick["profit"] = 0.0
        pick["settled_at"] = now_iso()
        pick["settled_status"] = status_raw
        pick["event_winner"] = fixture.get("event_winner")
        pick["final_score"] = None
        pick["total_games"] = None

        return True, "void_bad_terminal_status"

    if status != "finished":
        return False, "not_finished"

    parsed = parse_scores_from_fixture(fixture)

    if not parsed:
        return False, "no_scores"

    # Safety:
    # Finished tennis match with only one parsed set is unsafe for totals.
    # Usually incomplete API data or retirement-like score.
    if len(parsed) < 2:
        return False, "incomplete_score_sets"

    total = total_games_from_parsed(parsed)

    line = safe_float(pick.get("line"))
    side = str(pick.get("side") or "").lower()

    if side not in {"over", "under"}:
        return False, "bad_side"

    stake = safe_float(pick.get("stake"), 1.0)

    if stake <= 0:
        stake = 1.0

    odds = safe_float(pick.get("odds"))

    if total == line:
        result = "push"
        profit = 0.0
    elif side == "over":
        win = total > line
        result = "win" if win else "loss"
        profit = stake * (odds - 1) if win else -stake
    else:
        win = total < line
        result = "win" if win else "loss"
        profit = stake * (odds - 1) if win else -stake

    pick["result"] = result
    pick["profit"] = round(profit, 3)
    pick["settled_at"] = now_iso()
    pick["settled_status"] = status_raw
    pick["event_winner"] = fixture.get("event_winner")
    pick["final_score"] = final_score_string_from_parsed(parsed)
    pick["total_games"] = total

    return True, "settled"


def result_emoji(result):
    r = str(result or "").lower()

    if r == "win":
        return "✅"
    if r == "loss":
        return "❌"
    if r == "push":
        return "➖"
    if r == "void":
        return "⚪"

    return "⏳"


def format_profit(value):
    v = safe_float(value)

    if v > 0:
        return f"+{v:.2f}u"
    if v < 0:
        return f"{v:.2f}u"

    return "0.00u"


def make_table_row(pick):
    market_info = pick.get("market_info") or {}

    return {
        "date": pick.get("date"),
        "time": pick.get("time"),
        "rank": pick.get("rank"),
        "match": pick.get("match"),
        "pick": pick.get("bet"),
        "side": pick.get("side"),
        "line": pick.get("line"),
        "odds": pick.get("odds"),
        "bookmaker": pick.get("best_bookmaker"),
        "result": pick.get("result"),
        "total_games": pick.get("total_games"),
        "final_score": pick.get("final_score"),
        "profit": pick.get("profit"),
        "stake": pick.get("stake"),
        "jakob_score": pick.get("jakob_score"),
        "confidence": pick.get("confidence"),
        "quality_score": pick.get("quality_score"),
        "edge_percent": round(safe_float(pick.get("edge")) * 100, 2),
        "market_gap": market_info.get("market_gap"),
        "tournament": pick.get("tournament"),
        "event_type": pick.get("event_type"),
    }


def summarize_subset(items):
    wins = [x for x in items if str(x.get("result") or "").lower() == "win"]
    losses = [x for x in items if str(x.get("result") or "").lower() == "loss"]
    pushes = [x for x in items if str(x.get("result") or "").lower() == "push"]
    voids = [x for x in items if str(x.get("result") or "").lower() == "void"]

    graded = wins + losses

    stake = sum(safe_float(x.get("stake"), 1.0) for x in graded)
    profit = sum(safe_float(x.get("profit")) for x in items)

    return {
        "bets": len(items),
        "graded": len(graded),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "voids": len(voids),
        "stake": round(stake, 3),
        "profit": round(profit, 3),
        "win_rate_percent": round((len(wins) / len(graded) * 100), 2) if graded else 0.0,
        "roi_percent": round((profit / stake * 100), 2) if stake else 0.0,
    }


def build_summary(results):
    settled = [
        x for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "").lower() in {"win", "loss", "push", "void"}
    ]

    pending = [
        x for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "pending").lower() == "pending"
    ]

    today = datetime.now(ZoneInfo(TZ_NAME)).date().isoformat()

    settled_today = [
        x for x in settled
        if str(x.get("settled_at") or "").startswith(today)
    ]

    over = [
        x for x in settled
        if str(x.get("side") or "").lower() == "over"
    ]

    under = [
        x for x in settled
        if str(x.get("side") or "").lower() == "under"
    ]

    score_70_plus = [
        x for x in settled
        if safe_float(x.get("jakob_score")) >= 70
    ]

    score_72_plus = [
        x for x in settled
        if safe_float(x.get("jakob_score")) >= 72
    ]

    odds_210_or_less = [
        x for x in settled
        if safe_float(x.get("odds")) <= 2.10
    ]

    score_70_odds_210 = [
        x for x in settled
        if safe_float(x.get("jakob_score")) >= 70
        and safe_float(x.get("odds")) <= 2.10
    ]

    return {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "results_file": RESULTS_FILE,
        "pending": len(pending),
        "all_settled": summarize_subset(settled),
        "settled_today": summarize_subset(settled_today),
        "over": summarize_subset(over),
        "under": summarize_subset(under),
        "score_70_plus": summarize_subset(score_70_plus),
        "score_72_plus": summarize_subset(score_72_plus),
        "odds_210_or_less": summarize_subset(odds_210_or_less),
        "score_70_plus_and_odds_210_or_less": summarize_subset(score_70_odds_210),
    }


def markdown_summary_table(title, summary):
    return (
        f"### {title}\n\n"
        "| Bets | Wins | Losses | Push | Void | Winrate | Profit | ROI |\n"
        "|---:|---:|---:|---:|---:|---:|---:|---:|\n"
        f"| {summary['bets']} | {summary['wins']} | {summary['losses']} | "
        f"{summary['pushes']} | {summary['voids']} | "
        f"{summary['win_rate_percent']:.2f}% | "
        f"{format_profit(summary['profit'])} | "
        f"{summary['roi_percent']:.2f}% |\n\n"
    )


def build_markdown_report(results, summary_payload):
    settled = [
        x for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "").lower() in {"win", "loss", "push", "void"}
    ]

    # Newest settled first, then date/time.
    settled.sort(
        key=lambda x: (
            str(x.get("settled_at") or ""),
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            safe_int(x.get("rank"), 999999),
        ),
        reverse=True,
    )

    recent = settled[:80]

    out = []
    out.append("# Jakob Tennis Totals Settled Report\n\n")
    out.append(f"Generated: `{summary_payload['generated_at']}`\n\n")
    out.append(f"Pending picks: **{summary_payload['pending']}**\n\n")

    out.append(markdown_summary_table("All settled", summary_payload["all_settled"]))
    out.append(markdown_summary_table("Settled today", summary_payload["settled_today"]))
    out.append(markdown_summary_table("Score ≥ 70", summary_payload["score_70_plus"]))
    out.append(markdown_summary_table("Score ≥ 72", summary_payload["score_72_plus"]))
    out.append(markdown_summary_table("Score ≥ 70 + Odds ≤ 2.10", summary_payload["score_70_plus_and_odds_210_or_less"]))
    out.append(markdown_summary_table("Over", summary_payload["over"]))
    out.append(markdown_summary_table("Under", summary_payload["under"]))

    out.append("## Recent settled picks\n\n")
    out.append(
        "| Date | Time | Rank | Match | Pick | Odds | Result | Score | Total | Final score | Profit |\n"
    )
    out.append(
        "|---|---|---:|---|---|---:|---|---:|---:|---|---:|\n"
    )

    for pick in recent:
        result = str(pick.get("result") or "")
        emoji = result_emoji(result)
        profit = format_profit(pick.get("profit"))
        score = safe_float(pick.get("jakob_score"))

        out.append(
            f"| {pick.get('date') or ''} "
            f"| {pick.get('time') or ''} "
            f"| {pick.get('rank') or ''} "
            f"| {pick.get('match') or ''} "
            f"| {pick.get('bet') or ''} "
            f"| {safe_float(pick.get('odds')):.2f} "
            f"| {emoji} {result} "
            f"| {score:.2f} "
            f"| {pick.get('total_games') if pick.get('total_games') is not None else ''} "
            f"| {pick.get('final_score') or ''} "
            f"| {profit} |\n"
        )

    out.append("\n")
    return "".join(out)


def main():
    ensure_dirs()

    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    pending = [
        x for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "pending").lower() == "pending"
    ]

    debug = {
        "generated_at": now_iso(),
        "results_file": RESULTS_FILE,
        "pending_before": len(pending),
        "updated": 0,
        "still_pending": 0,
        "not_found": 0,
        "errors": [],
        "items": [],
    }

    print(f"PENDING JAKOB PICKS: {len(pending)}")

    for pick in pending:
        event_key = pick.get("event_key")
        match_name = pick.get("match")

        if not event_key:
            debug["errors"].append({
                "pick_id": pick.get("pick_id"),
                "match": match_name,
                "error": "missing_event_key",
            })
            continue

        try:
            fixture = fetch_fixture_by_event_key(event_key)

            if not fixture:
                debug["not_found"] += 1
                debug["items"].append({
                    "event_key": event_key,
                    "pick_id": pick.get("pick_id"),
                    "match": match_name,
                    "status": "not_found",
                })
                print(f"NO MATCH FOUND: {match_name} | event_key={event_key}")
                continue

            changed, reason = settle_pick(pick, fixture)

            if changed:
                debug["updated"] += 1
                print(
                    f"SETTLED: {match_name} | {pick.get('bet')} | "
                    f"{pick.get('result')} | total={pick.get('total_games')} | "
                    f"profit={pick.get('profit')}"
                )
            else:
                debug["still_pending"] += 1
                print(
                    f"PENDING: {match_name} | reason={reason} | "
                    f"status={fixture.get('event_status')}"
                )

            debug["items"].append({
                "event_key": event_key,
                "pick_id": pick.get("pick_id"),
                "match": match_name,
                "bet": pick.get("bet"),
                "side": pick.get("side"),
                "line": pick.get("line"),
                "odds": pick.get("odds"),
                "stake": pick.get("stake"),
                "jakob_score": pick.get("jakob_score"),
                "rank": pick.get("rank"),
                "rank_tier": pick.get("rank_tier"),
                "status": reason,
                "api_status": fixture.get("event_status"),
                "result": pick.get("result"),
                "total_games": pick.get("total_games"),
                "final_score": pick.get("final_score"),
                "profit": pick.get("profit"),
                "raw_scores": fixture.get("scores"),
                "score_debug": compact_fixture_debug(fixture),
            })

        except Exception as e:
            debug["errors"].append({
                "event_key": event_key,
                "match": match_name,
                "error": str(e),
            })
            print(f"ERROR {event_key} {match_name}: {e}")

    remaining_pending = [
        x for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "pending").lower() == "pending"
    ]

    debug["pending_after"] = len(remaining_pending)

    summary_payload = build_summary(results)
    table_rows = [
        make_table_row(x)
        for x in results
        if isinstance(x, dict)
        and str(x.get("result") or "").lower() in {"win", "loss", "push", "void"}
    ]

    table_rows.sort(
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            safe_int(x.get("rank"), 999999),
        ),
        reverse=True,
    )

    report_md = build_markdown_report(results, summary_payload)

    debug["summary_after_settle"] = summary_payload

    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)
    save_json(SUMMARY_FILE, summary_payload)
    save_csv(TABLE_FILE, table_rows)
    save_text(REPORT_FILE, report_md)

    print("")
    print(
        f"JAKOB SETTLE DONE: "
        f"updated={debug['updated']} "
        f"still_pending={debug['still_pending']} "
        f"not_found={debug['not_found']} "
        f"errors={len(debug['errors'])}"
    )
    print(f"Saved {RESULTS_FILE}")
    print(f"Saved {DEBUG_FILE}")
    print(f"Saved {SUMMARY_FILE}")
    print(f"Saved {TABLE_FILE}")
    print(f"Saved {REPORT_FILE}")


if __name__ == "__main__":
    main()

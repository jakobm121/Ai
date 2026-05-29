import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

TZ_NAME = "Europe/Ljubljana"
DATA_DIR = os.getenv("DATA_DIR", "data")
LUCIJA_DIR = os.getenv("LUCIJA_DIR", f"{DATA_DIR}/lucija")
SOURCE_FILE = os.getenv("TENNIS_TOTALS_RESULTS_FILE", f"{DATA_DIR}/tennis_totals_results.json")

REPORT_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_report.md"
SUMMARY_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_summary.json"
PICKS_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_picks.json"
BLOCKED_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_blocked_from_v1.json"
DEBUG_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_debug.json"

FLAT_STAKE = 1.0

RULES_V1 = {
    "avg_close_set_max": 0.55,
    "avg_close_set_min": 0.20,
    "avg_three_set_min": 0.15,
    "confidence_min": 80,
    "h2h_max": 0,
    "market_gap_min": 0.25,
    "quality_min": 72,
    "strength_gap_max": 30,
}

RULES_V2 = {
    "side": "under",
    "line_min": 20.0,
    "line_max": 21.5,
    "odds_min": 1.95,
    "odds_max": 2.20,
    "confidence_min": 83,
    "quality_min": 76,
    "market_gap_min": 0.25,
    "strength_gap_max": 30,
    "h2h_max": 0,
    "avg_three_set_max": 0.35,
    "avg_close_set_max": 0.50,
}


def ensure_dirs():
    os.makedirs(LUCIJA_DIR, exist_ok=True)


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


def save_text(path, text):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def safe_float(v, default=None):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def safe_int(v, default=None):
    try:
        if v is None or v == "":
            return default
        return int(float(v))
    except Exception:
        return default


def norm(v):
    return str(v or "").strip().lower()


def normalize_result(v):
    r = norm(v)
    if r in {"win", "won", "w"}:
        return "win"
    if r in {"loss", "lost", "lose", "l"}:
        return "loss"
    if r in {"push", "void", "cancelled", "canceled"}:
        return "push"
    if r in {"pending", ""}:
        return "pending"
    return r


def is_settled(p):
    return normalize_result(p.get("result")) in {"win", "loss", "push"}


def get_nested(d, path, default=None):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
        if cur is None:
            return default
    return cur


def avg_two(a, b, default=0.0):
    a = safe_float(a, default)
    b = safe_float(b, default)
    return round((a + b) / 2, 4)


def strength_gap(p):
    direct = safe_float(p.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)
    first = safe_float(p.get("first_strength_score"), None)
    second = safe_float(p.get("second_strength_score"), None)
    if first is not None and second is not None:
        return round(abs(first - second), 4)
    return None


def metrics(p):
    first_three = get_nested(p, "first_form.last_10.three_set_rate", 0)
    second_three = get_nested(p, "second_form.last_10.three_set_rate", 0)
    first_close = get_nested(p, "first_form.last_10.close_set_rate", 0)
    second_close = get_nested(p, "second_form.last_10.close_set_rate", 0)

    return {
        "side": norm(p.get("side")),
        "line": safe_float(p.get("line"), None),
        "odds": safe_float(p.get("odds"), None),
        "confidence": safe_float(p.get("confidence"), None),
        "quality_score": safe_float(p.get("quality_score"), None),
        "edge": safe_float(p.get("edge"), None),
        "bookmakers_used": safe_int(p.get("bookmakers_used"), None),
        "market_gap": safe_float(get_nested(p, "market_info.market_gap", None), None),
        "market_favorite_side": norm(get_nested(p, "market_info.market_favorite_side", "")) or None,
        "strength_gap": strength_gap(p),
        "h2h_matches": safe_int(p.get("h2h_matches"), 0),
        "avg_three_set": avg_two(first_three, second_three),
        "avg_close_set": avg_two(first_close, second_close),
        "tour_level": norm(p.get("tour_level")) or None,
        "gender": norm(p.get("gender")) or None,
    }


def ge(v, t):
    return v is not None and v >= t


def le(v, t):
    return v is not None and v <= t


def passes_v1(p):
    m = metrics(p)
    checks = {
        "avg_three_set_min": ge(m["avg_three_set"], RULES_V1["avg_three_set_min"]),
        "avg_close_set_min": ge(m["avg_close_set"], RULES_V1["avg_close_set_min"]),
        "avg_close_set_max": le(m["avg_close_set"], RULES_V1["avg_close_set_max"]),
        "confidence_min": ge(m["confidence"], RULES_V1["confidence_min"]),
        "quality_min": ge(m["quality_score"], RULES_V1["quality_min"]),
        "market_gap_min": ge(m["market_gap"], RULES_V1["market_gap_min"]),
        "strength_gap_max": le(m["strength_gap"], RULES_V1["strength_gap_max"]),
        "h2h_max": le(m["h2h_matches"], RULES_V1["h2h_max"]),
    }
    return all(checks.values()), m, checks


def passes_v2(p):
    m = metrics(p)
    checks = {
        "side_under": m["side"] == RULES_V2["side"],
        "line_min": ge(m["line"], RULES_V2["line_min"]),
        "line_max": le(m["line"], RULES_V2["line_max"]),
        "odds_min": ge(m["odds"], RULES_V2["odds_min"]),
        "odds_max": le(m["odds"], RULES_V2["odds_max"]),
        "confidence_min": ge(m["confidence"], RULES_V2["confidence_min"]),
        "quality_min": ge(m["quality_score"], RULES_V2["quality_min"]),
        "market_gap_min": ge(m["market_gap"], RULES_V2["market_gap_min"]),
        "strength_gap_max": le(m["strength_gap"], RULES_V2["strength_gap_max"]),
        "h2h_max": le(m["h2h_matches"], RULES_V2["h2h_max"]),
        "avg_three_set_max": le(m["avg_three_set"], RULES_V2["avg_three_set_max"]),
        "avg_close_set_max": le(m["avg_close_set"], RULES_V2["avg_close_set_max"]),
    }
    return all(checks.values()), m, checks


def profit(p):
    result = normalize_result(p.get("result"))
    odds = safe_float(p.get("odds"), None)
    if result == "win":
        return round((odds or 1.0) - 1.0, 4)
    if result == "loss":
        return -1.0
    return 0.0


def max_drawdown(profits):
    bankroll = 0.0
    peak = 0.0
    max_dd = 0.0
    for x in profits:
        bankroll += x
        peak = max(peak, bankroll)
        max_dd = min(max_dd, bankroll - peak)
    return round(max_dd, 4)


def longest_streak(results, target):
    best = 0
    cur = 0
    for r in results:
        if r == target:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def evaluate(picks):
    settled = [p for p in picks if is_settled(p)]
    wins = [p for p in settled if normalize_result(p.get("result")) == "win"]
    losses = [p for p in settled if normalize_result(p.get("result")) == "loss"]
    pushes = [p for p in settled if normalize_result(p.get("result")) == "push"]
    profits = [profit(p) for p in settled]
    stake = len(settled) * FLAT_STAKE
    total_profit = round(sum(profits), 4)
    roi = round((total_profit / stake) * 100, 2) if stake else 0.0
    winrate = round(len(wins) / max(1, len(wins) + len(losses)) * 100, 2)
    odds = [safe_float(p.get("odds"), None) for p in settled]
    odds = [x for x in odds if x is not None]
    results = [normalize_result(p.get("result")) for p in settled]
    return {
        "picks": len(picks),
        "settled": len(settled),
        "pending": len([p for p in picks if not is_settled(p)]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "winrate": winrate,
        "profit": total_profit,
        "roi": roi,
        "avg_odds": round(sum(odds) / len(odds), 4) if odds else 0.0,
        "max_drawdown": max_drawdown(profits),
        "longest_win_streak": longest_streak(results, "win"),
        "longest_loss_streak": longest_streak(results, "loss"),
    }


def split_train_test(picks, test_ratio=0.25):
    ordered = sorted(picks, key=lambda p: (str(p.get("date") or ""), str(p.get("time") or ""), str(p.get("fixture_id") or p.get("event_key") or "")))
    if len(ordered) < 4:
        return ordered, []
    cut = int(len(ordered) * (1 - test_ratio))
    cut = max(1, min(cut, len(ordered) - 1))
    return ordered[:cut], ordered[cut:]


def bucket(value, cuts):
    v = safe_float(value, None)
    if v is None:
        return "unknown"
    prev = None
    for cut in cuts:
        if v <= cut:
            return f"<= {cut}" if prev is None else f"{prev} - {cut}"
        prev = cut
    return f"> {cuts[-1]}"


def add_buckets(p):
    x = dict(p)
    m = metrics(p)
    x["_line_bucket"] = bucket(m["line"], [18.5, 19.5, 20.5, 21.5, 22.5])
    x["_odds_bucket"] = bucket(m["odds"], [1.80, 1.95, 2.05, 2.20, 2.50])
    x["_confidence_bucket"] = bucket(m["confidence"], [80, 83, 86, 89, 92])
    x["_quality_bucket"] = bucket(m["quality_score"], [72, 76, 80, 84, 88])
    x["_market_gap_bucket"] = bucket(m["market_gap"], [0.20, 0.25, 0.35, 0.45, 0.60])
    x["_strength_gap_bucket"] = bucket(m["strength_gap"], [5, 10, 15, 20, 25, 30])
    x["_avg_three_set_bucket"] = bucket(m["avg_three_set"], [0.15, 0.20, 0.25, 0.30, 0.35, 0.45])
    x["_avg_close_set_bucket"] = bucket(m["avg_close_set"], [0.20, 0.30, 0.40, 0.50, 0.60])
    return x


def group_stats(picks, field):
    groups = defaultdict(list)
    for p in picks:
        value = p.get(field)
        if value is None or value == "":
            value = "unknown"
        groups[str(value)].append(p)
    rows = []
    for key, items in groups.items():
        rows.append({"group": key, **evaluate(items)})
    rows.sort(key=lambda r: (r["profit"], r["roi"], r["settled"]), reverse=True)
    return rows


def public_pick(p, model):
    x = dict(p)
    ok, m, checks = passes_v2(p) if model == "v2" else passes_v1(p)
    x["lucija_backtest_model"] = model
    x["lucija_backtest_metrics"] = m
    x["lucija_backtest_checks"] = checks
    x["profit_flat"] = profit(p)
    return x


def make_report(generated_at, raw, settled, v1, v2, blocked, summary):
    lines = []
    lines.append("# Lucija v2 Backtest Report")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: `{SOURCE_FILE}`")
    lines.append(f"- Source picks loaded: **{len(raw)}**")
    lines.append(f"- Settled picks available: **{len(settled)}**")
    lines.append("")
    lines.append("## Rules")
    lines.append("")
    lines.append("### Lucija v1")
    lines.append("```json")
    lines.append(json.dumps(RULES_V1, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("### Lucija v2")
    lines.append("```json")
    lines.append(json.dumps(RULES_V2, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Main comparison")
    lines.append("")
    lines.append("| Model | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key, label in [("baseline", "All settled totals"), ("v1", "Lucija v1"), ("v2", "Lucija v2"), ("blocked_from_v1", "Blocked from v1 by v2")]:
        s = summary[key]
        lines.append(f"| {label} | {s['picks']} | {s['settled']} | {s['pending']} | {s['wins']} | {s['losses']} | {s['pushes']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {s['avg_odds']} | {s['max_drawdown']}u |")
    lines.append("")
    lines.append("## Train / test")
    lines.append("")
    lines.append("| Model | Split | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for model in ["v1", "v2"]:
        for split in ["train_75", "test_25"]:
            s = summary[f"{model}_{split}"]
            lines.append(f"| {model.upper()} | {split} | {s['settled']} | {s['wins']} | {s['losses']} | {s['winrate']}% | {s['profit']}u | {s['roi']}% | {s['avg_odds']} | {s['max_drawdown']}u |")
    lines.append("")
    lines.append("## V2 selected picks")
    lines.append("")
    lines.append("| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |")
    lines.append("|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for p in v2[:100]:
        m = metrics(p)
        lines.append(f"| {p.get('date','')} | {p.get('match','')} | {p.get('bet','')} | {p.get('odds','')} | {normalize_result(p.get('result'))} | {profit(p)} | {m.get('line')} | {m.get('avg_three_set')} | {m.get('avg_close_set')} | {m.get('market_gap')} | {m.get('strength_gap')} |")
    lines.append("")
    lines.append("## Blocked from v1 by v2")
    lines.append("")
    lines.append("| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Quality | Conf |")
    lines.append("|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for p in blocked[:100]:
        m = metrics(p)
        lines.append(f"| {p.get('date','')} | {p.get('match','')} | {p.get('bet','')} | {p.get('odds','')} | {normalize_result(p.get('result'))} | {profit(p)} | {m.get('line')} | {m.get('avg_three_set')} | {m.get('avg_close_set')} | {m.get('quality_score')} | {m.get('confidence')} |")
    lines.append("")
    lines.append("## V2 breakdowns")
    lines.append("")
    for title, rows in summary["v2_breakdowns"].items():
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for r in rows[:25]:
            lines.append(f"| {r['group']} | {r['settled']} | {r['wins']} | {r['losses']} | {r['winrate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} |")
        lines.append("")
    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append(f"- `{SUMMARY_FILE}`")
    lines.append(f"- `{PICKS_FILE}`")
    lines.append(f"- `{BLOCKED_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ensure_dirs()
    generated_at = now_iso()
    raw = load_json(SOURCE_FILE, [])
    if not isinstance(raw, list):
        raw = []
    settled = [p for p in raw if isinstance(p, dict) and is_settled(p)]

    v1 = []
    v2 = []
    rejected = []
    for p in raw:
        if not isinstance(p, dict):
            continue
        ok1, m1, c1 = passes_v1(p)
        ok2, m2, c2 = passes_v2(p)
        if ok1:
            v1.append(p)
        if ok2:
            v2.append(p)
        if not ok2:
            rejected.append({
                "pick_id": p.get("pick_id"),
                "date": p.get("date"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "result": p.get("result"),
                "metrics": m2,
                "checks": c2,
                "failed": [k for k, v in c2.items() if not v],
            })

    def key(p):
        return str(p.get("pick_id") or p.get("source_pick_id") or p.get("fixture_id") or p.get("event_key"))

    v2_keys = {key(p) for p in v2}
    blocked = [p for p in v1 if key(p) not in v2_keys]

    v1_train, v1_test = split_train_test(v1)
    v2_train, v2_test = split_train_test(v2)
    v2_bucketed = [add_buckets(p) for p in v2]

    summary = {
        "generated_at": generated_at,
        "source_file": SOURCE_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "rules_v1": RULES_V1,
        "rules_v2": RULES_V2,
        "baseline": evaluate(settled),
        "v1": evaluate(v1),
        "v2": evaluate(v2),
        "blocked_from_v1": evaluate(blocked),
        "v1_train_75": evaluate(v1_train),
        "v1_test_25": evaluate(v1_test),
        "v2_train_75": evaluate(v2_train),
        "v2_test_25": evaluate(v2_test),
        "v2_breakdowns": {
            "By tour level": group_stats(v2_bucketed, "tour_level"),
            "By gender": group_stats(v2_bucketed, "gender"),
            "By line bucket": group_stats(v2_bucketed, "_line_bucket"),
            "By odds bucket": group_stats(v2_bucketed, "_odds_bucket"),
            "By confidence bucket": group_stats(v2_bucketed, "_confidence_bucket"),
            "By quality bucket": group_stats(v2_bucketed, "_quality_bucket"),
            "By market gap bucket": group_stats(v2_bucketed, "_market_gap_bucket"),
            "By strength gap bucket": group_stats(v2_bucketed, "_strength_gap_bucket"),
            "By avg three set bucket": group_stats(v2_bucketed, "_avg_three_set_bucket"),
            "By avg close set bucket": group_stats(v2_bucketed, "_avg_close_set_bucket"),
            "By bookmaker": group_stats(v2_bucketed, "best_bookmaker"),
            "By tournament": group_stats(v2_bucketed, "tournament"),
        },
    }

    debug = {
        "generated_at": generated_at,
        "source_file": SOURCE_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "v1_count": len(v1),
        "v2_count": len(v2),
        "blocked_from_v1_count": len(blocked),
        "rejected_v2_sample": rejected[:500],
    }

    save_json(SUMMARY_FILE, summary)
    save_json(PICKS_FILE, [public_pick(p, "v2") for p in v2])
    save_json(BLOCKED_FILE, [public_pick(p, "blocked_from_v1") for p in blocked])
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, make_report(generated_at, raw, settled, v1, v2, blocked, summary))

    print("")
    print("LUCIJA V2 BACKTEST DONE")
    print(f"source picks: {len(raw)}")
    print(f"settled picks: {len(settled)}")
    print(f"v1 picks: {len(v1)}")
    print(f"v2 picks: {len(v2)}")
    print(f"blocked from v1 by v2: {len(blocked)}")
    print("")
    print("V1:")
    print(summary["v1"])
    print("V2:")
    print(summary["v2"])
    print("Blocked:")
    print(summary["blocked_from_v1"])
    print("")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

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
PICKS_V1_FILE = f"{LUCIJA_DIR}/lucija_v1_backtest_picks.json"
PICKS_V2_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_picks.json"
PICKS_V3_FILE = f"{LUCIJA_DIR}/lucija_v3_over_backtest_picks.json"
DEBUG_FILE = f"{LUCIJA_DIR}/lucija_v2_backtest_debug.json"

FLAT_STAKE = 1.0

# Original Lucija v1.
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

# UNDER test.
# Ideja: za under hočemo manj 3-set in manj close-set potenciala.
RULES_V2 = {
    "side": "under",
    "avg_close_set_max": 0.40,
    "avg_three_set_max": 0.40,
    "confidence_min": 0,
    "h2h_min": 0,
    "market_gap_min": 0.25,
    "quality_min": 0,
    "strength_gap_max": 30,
}

# OVER test.
# Kontra logika: za over hočemo več close-set / 3-set potenciala.
# Market gap je pri overjih raje manjši, ker bolj izenačen match večkrat vleče total gor.
RULES_V3 = {
    "side": "over",
    "avg_close_set_min": 0.30,
    "avg_three_set_min": 0.25,
    "confidence_min": 0,
    "h2h_min": 0,
    "market_gap_max": 0.35,
    "quality_min": 0,
    "strength_gap_max": 35,
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


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def normalize_text(value):
    return str(value or "").strip().lower()


def normalize_result(value):
    r = normalize_text(value)

    if r in {"win", "won", "w"}:
        return "win"
    if r in {"loss", "lost", "lose", "l"}:
        return "loss"
    if r in {"push", "void", "cancelled", "canceled"}:
        return "push"
    if r in {"pending", ""}:
        return "pending"

    return r


def is_settled(pick):
    return normalize_result(pick.get("result")) in {"win", "loss", "push"}


def get_nested(data, path, default=None):
    cur = data

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


def strength_gap(pick):
    direct = safe_float(pick.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)

    first = safe_float(pick.get("first_strength_score"), None)
    second = safe_float(pick.get("second_strength_score"), None)

    if first is not None and second is not None:
        return round(abs(first - second), 4)

    return None


def lucija_metrics(pick):
    first_three = get_nested(pick, "first_form.last_10.three_set_rate", 0)
    second_three = get_nested(pick, "second_form.last_10.three_set_rate", 0)

    first_close = get_nested(pick, "first_form.last_10.close_set_rate", 0)
    second_close = get_nested(pick, "second_form.last_10.close_set_rate", 0)

    first_avg_total = get_nested(pick, "first_form.last_10.avg_total_games", None)
    second_avg_total = get_nested(pick, "second_form.last_10.avg_total_games", None)

    first_over_21_5 = get_nested(pick, "first_form.last_10.over_21_5_rate", 0)
    second_over_21_5 = get_nested(pick, "second_form.last_10.over_21_5_rate", 0)

    first_win_rate = get_nested(pick, "first_form.last_10.win_rate", None)
    second_win_rate = get_nested(pick, "second_form.last_10.win_rate", None)

    return {
        "side": normalize_text(pick.get("side")),
        "line": safe_float(pick.get("line"), None),
        "odds": safe_float(pick.get("odds"), None),
        "confidence": safe_float(pick.get("confidence"), None),
        "quality_score": safe_float(pick.get("quality_score"), None),
        "edge": safe_float(pick.get("edge"), None),
        "bookmakers_used": safe_int(pick.get("bookmakers_used"), None),
        "market_gap": safe_float(get_nested(pick, "market_info.market_gap", None), None),
        "market_favorite_side": normalize_text(get_nested(pick, "market_info.market_favorite_side", "")) or None,
        "strength_gap": strength_gap(pick),
        "h2h_matches": safe_int(pick.get("h2h_matches"), 0),
        "avg_three_set": avg_two(first_three, second_three),
        "avg_close_set": avg_two(first_close, second_close),
        "avg_total_games_players": avg_two(first_avg_total, second_avg_total, 0),
        "avg_over_21_5_rate": avg_two(first_over_21_5, second_over_21_5, 0),
        "avg_win_rate": avg_two(first_win_rate, second_win_rate, 0),
        "tour_level": normalize_text(pick.get("tour_level")) or None,
        "gender": normalize_text(pick.get("gender")) or None,
    }


def check_min(value, threshold):
    return value is not None and value >= threshold


def check_max(value, threshold):
    return value is not None and value <= threshold


def passes_rules(pick, rules):
    m = lucija_metrics(pick)
    checks = {}

    if "side" in rules and rules["side"] is not None:
        checks["side"] = m["side"] == normalize_text(rules["side"])

    if "line_min" in rules and rules["line_min"] is not None:
        checks["line_min"] = check_min(m["line"], rules["line_min"])

    if "line_max" in rules and rules["line_max"] is not None:
        checks["line_max"] = check_max(m["line"], rules["line_max"])

    if "odds_min" in rules and rules["odds_min"] is not None:
        checks["odds_min"] = check_min(m["odds"], rules["odds_min"])

    if "odds_max" in rules and rules["odds_max"] is not None:
        checks["odds_max"] = check_max(m["odds"], rules["odds_max"])

    if "confidence_min" in rules and rules["confidence_min"] is not None:
        checks["confidence_min"] = check_min(m["confidence"], rules["confidence_min"])

    if "confidence_max" in rules and rules["confidence_max"] is not None:
        checks["confidence_max"] = check_max(m["confidence"], rules["confidence_max"])

    if "quality_min" in rules and rules["quality_min"] is not None:
        checks["quality_min"] = check_min(m["quality_score"], rules["quality_min"])

    if "quality_max" in rules and rules["quality_max"] is not None:
        checks["quality_max"] = check_max(m["quality_score"], rules["quality_max"])

    if "edge_min" in rules and rules["edge_min"] is not None:
        checks["edge_min"] = check_min(m["edge"], rules["edge_min"])

    if "edge_max" in rules and rules["edge_max"] is not None:
        checks["edge_max"] = check_max(m["edge"], rules["edge_max"])

    if "bookmakers_min" in rules and rules["bookmakers_min"] is not None:
        checks["bookmakers_min"] = check_min(m["bookmakers_used"], rules["bookmakers_min"])

    if "bookmakers_max" in rules and rules["bookmakers_max"] is not None:
        checks["bookmakers_max"] = check_max(m["bookmakers_used"], rules["bookmakers_max"])

    if "market_gap_min" in rules and rules["market_gap_min"] is not None:
        checks["market_gap_min"] = check_min(m["market_gap"], rules["market_gap_min"])

    if "market_gap_max" in rules and rules["market_gap_max"] is not None:
        checks["market_gap_max"] = check_max(m["market_gap"], rules["market_gap_max"])

    if "strength_gap_min" in rules and rules["strength_gap_min"] is not None:
        checks["strength_gap_min"] = check_min(m["strength_gap"], rules["strength_gap_min"])

    if "strength_gap_max" in rules and rules["strength_gap_max"] is not None:
        checks["strength_gap_max"] = check_max(m["strength_gap"], rules["strength_gap_max"])

    if "h2h_min" in rules and rules["h2h_min"] is not None:
        checks["h2h_min"] = check_min(m["h2h_matches"], rules["h2h_min"])

    if "h2h_max" in rules and rules["h2h_max"] is not None:
        checks["h2h_max"] = check_max(m["h2h_matches"], rules["h2h_max"])

    if "avg_three_set_min" in rules and rules["avg_three_set_min"] is not None:
        checks["avg_three_set_min"] = check_min(m["avg_three_set"], rules["avg_three_set_min"])

    if "avg_three_set_max" in rules and rules["avg_three_set_max"] is not None:
        checks["avg_three_set_max"] = check_max(m["avg_three_set"], rules["avg_three_set_max"])

    if "avg_close_set_min" in rules and rules["avg_close_set_min"] is not None:
        checks["avg_close_set_min"] = check_min(m["avg_close_set"], rules["avg_close_set_min"])

    if "avg_close_set_max" in rules and rules["avg_close_set_max"] is not None:
        checks["avg_close_set_max"] = check_max(m["avg_close_set"], rules["avg_close_set_max"])

    if "avg_total_games_min" in rules and rules["avg_total_games_min"] is not None:
        checks["avg_total_games_min"] = check_min(m["avg_total_games_players"], rules["avg_total_games_min"])

    if "avg_total_games_max" in rules and rules["avg_total_games_max"] is not None:
        checks["avg_total_games_max"] = check_max(m["avg_total_games_players"], rules["avg_total_games_max"])

    if "avg_over_21_5_rate_min" in rules and rules["avg_over_21_5_rate_min"] is not None:
        checks["avg_over_21_5_rate_min"] = check_min(m["avg_over_21_5_rate"], rules["avg_over_21_5_rate_min"])

    if "avg_over_21_5_rate_max" in rules and rules["avg_over_21_5_rate_max"] is not None:
        checks["avg_over_21_5_rate_max"] = check_max(m["avg_over_21_5_rate"], rules["avg_over_21_5_rate_max"])

    return all(checks.values()), m, checks


def profit_for_pick(pick, stake=FLAT_STAKE):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), None)

    if result == "win":
        return round(stake * ((odds or 1.0) - 1.0), 4)
    if result == "loss":
        return round(-stake, 4)
    return 0.0


def max_drawdown(profits):
    bankroll = 0.0
    peak = 0.0
    max_dd = 0.0

    for p in profits:
        bankroll += p
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

    profits = [profit_for_pick(p) for p in settled]
    stake_sum = len(settled) * FLAT_STAKE
    profit = round(sum(profits), 4)
    roi = round((profit / stake_sum) * 100, 2) if stake_sum else 0.0
    winrate = round(len(wins) / max(1, len(wins) + len(losses)) * 100, 2)

    odds_values = [safe_float(p.get("odds"), None) for p in settled]
    odds_values = [x for x in odds_values if x is not None]

    result_seq = [normalize_result(p.get("result")) for p in settled]

    return {
        "picks": len(picks),
        "settled": len(settled),
        "pending": len([p for p in picks if not is_settled(p)]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "winrate": winrate,
        "profit": profit,
        "roi": roi,
        "avg_odds": round(sum(odds_values) / len(odds_values), 4) if odds_values else 0.0,
        "max_drawdown": max_drawdown(profits),
        "longest_win_streak": longest_streak(result_seq, "win"),
        "longest_loss_streak": longest_streak(result_seq, "loss"),
    }


def split_train_test(picks, ratio=0.25):
    ordered = sorted(
        picks,
        key=lambda p: (
            str(p.get("date") or ""),
            str(p.get("time") or ""),
            str(p.get("fixture_id") or p.get("event_key") or ""),
            str(p.get("pick_id") or ""),
        ),
    )

    if len(ordered) < 4:
        return ordered, []

    cut = int(len(ordered) * (1 - ratio))
    cut = max(1, min(cut, len(ordered) - 1))
    return ordered[:cut], ordered[cut:]


def bucket(value, cuts):
    v = safe_float(value, None)
    if v is None:
        return "unknown"

    previous = None
    for cut in cuts:
        if v <= cut:
            if previous is None:
                return f"<= {cut}"
            return f"{previous} - {cut}"
        previous = cut

    return f"> {cuts[-1]}"


def add_buckets(pick):
    p = dict(pick)
    m = lucija_metrics(pick)

    p["_side"] = m["side"]
    p["_line_bucket"] = bucket(m["line"], [18.5, 19.5, 20.5, 21.5, 22.5])
    p["_odds_bucket"] = bucket(m["odds"], [1.80, 1.95, 2.05, 2.20, 2.50])
    p["_confidence_bucket"] = bucket(m["confidence"], [80, 83, 86, 89, 92])
    p["_quality_bucket"] = bucket(m["quality_score"], [72, 76, 80, 84, 88])
    p["_market_gap_bucket"] = bucket(m["market_gap"], [0.20, 0.25, 0.35, 0.45, 0.60])
    p["_strength_gap_bucket"] = bucket(m["strength_gap"], [5, 10, 15, 20, 25, 30, 35])
    p["_avg_three_set_bucket"] = bucket(m["avg_three_set"], [0.15, 0.20, 0.25, 0.30, 0.35, 0.45])
    p["_avg_close_set_bucket"] = bucket(m["avg_close_set"], [0.20, 0.30, 0.35, 0.40, 0.50, 0.60])
    p["_avg_total_games_bucket"] = bucket(m["avg_total_games_players"], [18, 19, 20, 21, 22, 23])
    p["_avg_over_21_5_bucket"] = bucket(m["avg_over_21_5_rate"], [0.20, 0.30, 0.40, 0.50, 0.60])

    return p


def group_stats(picks, key):
    groups = defaultdict(list)

    for p in picks:
        value = p.get(key)
        if value is None or value == "":
            value = "unknown"

        groups[str(value)].append(p)

    rows = []
    for value, items in groups.items():
        rows.append({
            "group": value,
            **evaluate(items),
        })

    rows.sort(key=lambda x: (x["profit"], x["roi"], x["settled"]), reverse=True)
    return rows


def public_pick(pick, model_name, rules):
    p = dict(pick)
    ok, metrics, checks = passes_rules(pick, rules)

    p["lucija_backtest_model"] = model_name
    p["lucija_backtest_rules"] = rules
    p["lucija_backtest_metrics"] = metrics
    p["lucija_backtest_checks"] = checks
    p["profit_flat"] = profit_for_pick(p)

    return p


def table_row(label, stats):
    return (
        f"| {label} | {stats['picks']} | {stats['settled']} | {stats['pending']} | "
        f"{stats['wins']} | {stats['losses']} | {stats['pushes']} | "
        f"{stats['winrate']}% | {stats['profit']}u | {stats['roi']}% | "
        f"{stats['avg_odds']} | {stats['max_drawdown']}u |"
    )


def make_report(generated_at, raw, settled, model_picks, summary):
    lines = []

    lines.append("# Lucija Backtest Report")
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
    lines.append("### V1 original")
    lines.append("```json")
    lines.append(json.dumps(RULES_V1, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("### V2 under")
    lines.append("```json")
    lines.append(json.dumps(RULES_V2, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("### V3 over")
    lines.append("```json")
    lines.append(json.dumps(RULES_V3, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")

    lines.append("## Main comparison")
    lines.append("")
    lines.append("| Model | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(table_row("All settled totals", summary["baseline"]))
    lines.append(table_row("V1 original", summary["v1"]))
    lines.append(table_row("V2 under", summary["v2"]))
    lines.append(table_row("V3 over", summary["v3"]))
    lines.append("")

    lines.append("## Train / test")
    lines.append("")
    lines.append("| Model | Split | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for model in ["v1", "v2", "v3"]:
        for split in ["train_75", "test_25"]:
            s = summary[f"{model}_{split}"]
            lines.append(
                f"| {model.upper()} | {split} | {s['picks']} | {s['settled']} | "
                f"{s['wins']} | {s['losses']} | {s['winrate']}% | "
                f"{s['profit']}u | {s['roi']}% | {s['avg_odds']} | {s['max_drawdown']}u |"
            )
    lines.append("")

    for model_key, title in [("v1", "V1 original"), ("v2", "V2 under"), ("v3", "V3 over")]:
        picks = model_picks[model_key]

        lines.append(f"## {title} selected picks")
        lines.append("")
        lines.append("| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |")
        lines.append("|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|")

        for p in picks[:100]:
            m = lucija_metrics(p)
            lines.append(
                f"| {p.get('date','')} | {p.get('match','')} | {p.get('bet','')} | "
                f"{p.get('odds','')} | {normalize_result(p.get('result'))} | {profit_for_pick(p)} | "
                f"{m.get('line')} | {m.get('avg_three_set')} | {m.get('avg_close_set')} | "
                f"{m.get('market_gap')} | {m.get('strength_gap')} |"
            )
        lines.append("")

    for model_key, title in [("v2", "V2 under breakdowns"), ("v3", "V3 over breakdowns")]:
        lines.append(f"## {title}")
        lines.append("")

        for section, rows in summary[f"{model_key}_breakdowns"].items():
            lines.append(f"### {section}")
            lines.append("")
            lines.append("| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |")
            lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

            for r in rows[:30]:
                lines.append(
                    f"| {r['group']} | {r['picks']} | {r['settled']} | {r['wins']} | {r['losses']} | "
                    f"{r['winrate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} |"
                )
            lines.append("")

    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append(f"- `{SUMMARY_FILE}`")
    lines.append(f"- `{PICKS_V1_FILE}`")
    lines.append(f"- `{PICKS_V2_FILE}`")
    lines.append(f"- `{PICKS_V3_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append("")

    return "\n".join(lines)


def model_breakdowns(picks):
    bucketed = [add_buckets(p) for p in picks]

    return {
        "By side": group_stats(bucketed, "_side"),
        "By tour level": group_stats(bucketed, "tour_level"),
        "By gender": group_stats(bucketed, "gender"),
        "By line bucket": group_stats(bucketed, "_line_bucket"),
        "By odds bucket": group_stats(bucketed, "_odds_bucket"),
        "By confidence bucket": group_stats(bucketed, "_confidence_bucket"),
        "By quality bucket": group_stats(bucketed, "_quality_bucket"),
        "By market gap bucket": group_stats(bucketed, "_market_gap_bucket"),
        "By strength gap bucket": group_stats(bucketed, "_strength_gap_bucket"),
        "By avg three set bucket": group_stats(bucketed, "_avg_three_set_bucket"),
        "By avg close set bucket": group_stats(bucketed, "_avg_close_set_bucket"),
        "By avg total games bucket": group_stats(bucketed, "_avg_total_games_bucket"),
        "By avg over 21.5 rate bucket": group_stats(bucketed, "_avg_over_21_5_bucket"),
        "By bookmaker": group_stats(bucketed, "best_bookmaker"),
        "By tournament": group_stats(bucketed, "tournament"),
    }


def main():
    ensure_dirs()

    generated_at = now_iso()

    raw = load_json(SOURCE_FILE, [])
    if not isinstance(raw, list):
        raw = []

    settled = [p for p in raw if isinstance(p, dict) and is_settled(p)]

    v1_picks = []
    v2_picks = []
    v3_picks = []

    rejected_debug = []

    for pick in raw:
        if not isinstance(pick, dict):
            continue

        ok1, m1, c1 = passes_rules(pick, RULES_V1)
        ok2, m2, c2 = passes_rules(pick, RULES_V2)
        ok3, m3, c3 = passes_rules(pick, RULES_V3)

        if ok1:
            v1_picks.append(pick)
        if ok2:
            v2_picks.append(pick)
        if ok3:
            v3_picks.append(pick)

        rejected_debug.append({
            "pick_id": pick.get("pick_id"),
            "date": pick.get("date"),
            "match": pick.get("match"),
            "bet": pick.get("bet"),
            "side": pick.get("side"),
            "result": pick.get("result"),
            "v1_ok": ok1,
            "v2_ok": ok2,
            "v3_ok": ok3,
            "metrics": m2,
            "v1_failed": [k for k, v in c1.items() if not v],
            "v2_failed": [k for k, v in c2.items() if not v],
            "v3_failed": [k for k, v in c3.items() if not v],
        })

    v1_train, v1_test = split_train_test(v1_picks)
    v2_train, v2_test = split_train_test(v2_picks)
    v3_train, v3_test = split_train_test(v3_picks)

    summary = {
        "generated_at": generated_at,
        "source_file": SOURCE_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "rules_v1": RULES_V1,
        "rules_v2": RULES_V2,
        "rules_v3": RULES_V3,
        "baseline": evaluate(settled),
        "v1": evaluate(v1_picks),
        "v2": evaluate(v2_picks),
        "v3": evaluate(v3_picks),
        "v1_train_75": evaluate(v1_train),
        "v1_test_25": evaluate(v1_test),
        "v2_train_75": evaluate(v2_train),
        "v2_test_25": evaluate(v2_test),
        "v3_train_75": evaluate(v3_train),
        "v3_test_25": evaluate(v3_test),
        "v2_breakdowns": model_breakdowns(v2_picks),
        "v3_breakdowns": model_breakdowns(v3_picks),
    }

    model_picks = {
        "v1": v1_picks,
        "v2": v2_picks,
        "v3": v3_picks,
    }

    debug = {
        "generated_at": generated_at,
        "source_file": SOURCE_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "v1_count": len(v1_picks),
        "v2_count": len(v2_picks),
        "v3_count": len(v3_picks),
        "debug_sample": rejected_debug[:1000],
    }

    report = make_report(
        generated_at=generated_at,
        raw=raw,
        settled=settled,
        model_picks=model_picks,
        summary=summary,
    )

    save_json(SUMMARY_FILE, summary)
    save_json(PICKS_V1_FILE, [public_pick(p, "v1", RULES_V1) for p in v1_picks])
    save_json(PICKS_V2_FILE, [public_pick(p, "v2", RULES_V2) for p in v2_picks])
    save_json(PICKS_V3_FILE, [public_pick(p, "v3", RULES_V3) for p in v3_picks])
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, report)

    print("")
    print("LUCIJA BACKTEST DONE")
    print(f"source picks: {len(raw)}")
    print(f"settled picks: {len(settled)}")
    print(f"v1 picks: {len(v1_picks)}")
    print(f"v2 under picks: {len(v2_picks)}")
    print(f"v3 over picks: {len(v3_picks)}")
    print("")
    print("V1:")
    print(summary["v1"])
    print("V2 UNDER:")
    print(summary["v2"])
    print("V3 OVER:")
    print(summary["v3"])
    print("")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

import os
import json
import math
import itertools
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
LUCIJA_DIR = f"{DATA_DIR}/lucija"

SOURCE_FILE = f"{DATA_DIR}/tennis_totals_results.json"

SUMMARY_FILE = f"{LUCIJA_DIR}/lucija_formula_optimizer_150_summary.json"
REPORT_FILE = f"{LUCIJA_DIR}/lucija_formula_optimizer_150_report.md"
TOP_RULES_FILE = f"{LUCIJA_DIR}/lucija_formula_optimizer_150_top_rules.json"

MIN_PICKS_TARGET = 150
TOP_N_PER_MODE = 25

TRAIN_RATIO = 0.75

# Če je True, zahteva pozitiven test del.
REQUIRE_POSITIVE_TEST = True

# Če je True, zahteva vsaj 30 test pickov.
REQUIRE_MIN_TEST_PICKS = True
MIN_TEST_PICKS = 30


SEARCH_SPACE = {
    "side": [None, "under", "over"],

    "line_min": [18.5, 19.0, 19.5, 20.0, 20.5],
    "line_max": [20.5, 21.0, 21.5, 22.0, 22.5, 24.5],

    "odds_min": [1.65, 1.75, 1.85, 1.90, 1.95],
    "odds_max": [2.00, 2.05, 2.10, 2.15, 2.20],

    "market_gap_min": [0.00, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
    "market_gap_max": [0.35, 0.45, 0.55, 0.60, 0.70, 1.00],

    "avg_three_set_min": [0.00, 0.10, 0.15, 0.20, 0.25],
    "avg_three_set_max": [0.25, 0.30, 0.35, 0.40, 0.50, 1.00],

    "avg_close_set_min": [0.00, 0.15, 0.20, 0.25, 0.30],
    "avg_close_set_max": [0.30, 0.35, 0.38, 0.42, 0.50, 1.00],

    "quality_min": [68, 72, 76, 80, 84],
    "quality_max": [84, 88, 92, 99],

    "confidence_min": [68, 75, 80, 83, 86, 89],
    "confidence_max": [88, 92, 96, 99],

    "strength_gap_min": [0, 5, 8, 10, 15],
    "strength_gap_max": [20, 25, 30, 35, 50, 999],

    "h2h_max": [0, 1, 2, 999],

    "bookmakers_min": [3, 5, 6, 7],
}


MODES = {
    "BEST_OVERALL_MIN_150": {
        "side": None,
        "tour_levels": None,
    },
    "BEST_UNDER_MIN_150": {
        "side": "under",
        "tour_levels": None,
    },
    "BEST_OVER_MIN_150": {
        "side": "over",
        "tour_levels": None,
    },
    "BEST_ATP_WTA_MIN_150": {
        "side": None,
        "tour_levels": {"atp", "wta"},
    },
    "BEST_UNDER_ATP_WTA_MIN_150": {
        "side": "under",
        "tour_levels": {"atp", "wta"},
    },
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
        return data
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


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
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


def get_nested(data, keys, default=None):
    cur = data

    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)

    return cur if cur is not None else default


def avg_values(values, default=0.0):
    clean = []

    for v in values:
        if v is None or v == "":
            continue

        try:
            clean.append(float(v))
        except Exception:
            continue

    if not clean:
        return default

    return round(sum(clean) / len(clean), 4)


def calc_profit(pick, stake=1.0):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), 0.0)

    if result == "win":
        return round(stake * (odds - 1.0), 4)
    if result == "loss":
        return round(-stake, 4)

    return 0.0


def extract_market_gap(pick):
    direct = safe_float(pick.get("market_gap"), None)
    if direct is not None:
        return direct

    return safe_float(get_nested(pick, ["market_info", "market_gap"], 0.0), 0.0)


def extract_strength_gap(pick):
    direct = safe_float(pick.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)

    first_strength = safe_float(pick.get("first_strength_score"), None)
    second_strength = safe_float(pick.get("second_strength_score"), None)

    if first_strength is None or second_strength is None:
        return 999.0

    return abs(first_strength - second_strength)


def extract_avg_three_set(pick):
    direct = safe_float(pick.get("avg_three_set"), None)
    if direct is not None:
        return direct

    return avg_values([
        get_nested(pick, ["first_form", "last_10", "three_set_rate"], None),
        get_nested(pick, ["second_form", "last_10", "three_set_rate"], None),
    ])


def extract_avg_close_set(pick):
    direct = safe_float(pick.get("avg_close_set"), None)
    if direct is not None:
        return direct

    return avg_values([
        get_nested(pick, ["first_form", "last_10", "close_set_rate"], None),
        get_nested(pick, ["second_form", "last_10", "close_set_rate"], None),
    ])


def extract_avg_total_games(pick):
    direct = safe_float(pick.get("avg_total_games"), None)
    if direct is not None:
        return direct

    return avg_values([
        get_nested(pick, ["first_form", "last_10", "avg_total_games"], None),
        get_nested(pick, ["second_form", "last_10", "avg_total_games"], None),
    ])


def extract_avg_over_21_5_rate(pick):
    direct = safe_float(pick.get("avg_over_21_5_rate"), None)
    if direct is not None:
        return direct

    return avg_values([
        get_nested(pick, ["first_form", "last_10", "over_21_5_rate"], None),
        get_nested(pick, ["second_form", "last_10", "over_21_5_rate"], None),
    ])


def enrich_pick(pick):
    p = dict(pick)

    p["_result"] = normalize_result(p.get("result"))
    p["_profit"] = calc_profit(p, 1.0)

    p["_side"] = normalize_text(p.get("side"))
    p["_tour_level"] = normalize_text(p.get("tour_level"))
    p["_gender"] = normalize_text(p.get("gender"))

    p["_line"] = safe_float(p.get("line"), 0.0)
    p["_odds"] = safe_float(p.get("odds"), 0.0)
    p["_bookmakers"] = safe_int(p.get("bookmakers_used"), 0)

    p["_confidence"] = safe_float(p.get("confidence"), 0.0)
    p["_quality"] = safe_float(p.get("quality_score"), 0.0)
    p["_edge"] = safe_float(p.get("edge"), 0.0)

    p["_market_gap"] = extract_market_gap(p)
    p["_strength_gap"] = extract_strength_gap(p)
    p["_avg_three_set"] = extract_avg_three_set(p)
    p["_avg_close_set"] = extract_avg_close_set(p)
    p["_avg_total_games"] = extract_avg_total_games(p)
    p["_avg_over_21_5_rate"] = extract_avg_over_21_5_rate(p)

    p["_h2h"] = safe_int(p.get("h2h_matches"), 999)

    return p


def max_drawdown(profits):
    peak = 0.0
    equity = 0.0
    max_dd = 0.0

    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        dd = equity - peak
        max_dd = min(max_dd, dd)

    return round(max_dd, 4)


def streaks(picks):
    longest_win = 0
    longest_loss = 0
    cur_win = 0
    cur_loss = 0

    for p in picks:
        result = p.get("_result")

        if result == "win":
            cur_win += 1
            cur_loss = 0
        elif result == "loss":
            cur_loss += 1
            cur_win = 0
        else:
            cur_win = 0
            cur_loss = 0

        longest_win = max(longest_win, cur_win)
        longest_loss = max(longest_loss, cur_loss)

    return longest_win, longest_loss


def evaluate(picks):
    settled = [p for p in picks if p.get("_result") in {"win", "loss", "push"}]
    wins = [p for p in settled if p.get("_result") == "win"]
    losses = [p for p in settled if p.get("_result") == "loss"]
    pushes = [p for p in settled if p.get("_result") == "push"]

    profits = [safe_float(p.get("_profit"), 0.0) for p in settled]

    stake_sum = len(settled)
    profit = round(sum(profits), 4)
    roi = round((profit / stake_sum) * 100, 2) if stake_sum else 0.0
    winrate = round((len(wins) / max(1, len(wins) + len(losses))) * 100, 2)

    odds_values = [p.get("_odds") for p in settled if safe_float(p.get("_odds"), 0.0) > 1]
    avg_odds = round(sum(odds_values) / len(odds_values), 4) if odds_values else 0.0

    longest_win, longest_loss = streaks(settled)

    return {
        "picks": len(picks),
        "settled": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "winrate": winrate,
        "profit": profit,
        "roi": roi,
        "avg_odds": avg_odds,
        "max_drawdown": max_drawdown(profits),
        "longest_win_streak": longest_win,
        "longest_loss_streak": longest_loss,
    }


def split_train_test(picks):
    sorted_picks = sorted(
        picks,
        key=lambda p: (
            str(p.get("date") or ""),
            str(p.get("time") or ""),
            str(p.get("match") or ""),
            str(p.get("pick_id") or ""),
        )
    )

    split_idx = int(len(sorted_picks) * TRAIN_RATIO)

    return sorted_picks[:split_idx], sorted_picks[split_idx:]


def valid_range(min_value, max_value):
    return float(min_value) <= float(max_value)


def rule_passes(p, r):
    side = r.get("side")
    if side and p["_side"] != side:
        return False

    if p["_line"] < r["line_min"] or p["_line"] > r["line_max"]:
        return False

    if p["_odds"] < r["odds_min"] or p["_odds"] > r["odds_max"]:
        return False

    if p["_market_gap"] < r["market_gap_min"] or p["_market_gap"] > r["market_gap_max"]:
        return False

    if p["_avg_three_set"] < r["avg_three_set_min"] or p["_avg_three_set"] > r["avg_three_set_max"]:
        return False

    if p["_avg_close_set"] < r["avg_close_set_min"] or p["_avg_close_set"] > r["avg_close_set_max"]:
        return False

    if p["_quality"] < r["quality_min"] or p["_quality"] > r["quality_max"]:
        return False

    if p["_confidence"] < r["confidence_min"] or p["_confidence"] > r["confidence_max"]:
        return False

    if p["_strength_gap"] < r["strength_gap_min"] or p["_strength_gap"] > r["strength_gap_max"]:
        return False

    if p["_h2h"] > r["h2h_max"]:
        return False

    if p["_bookmakers"] < r["bookmakers_min"]:
        return False

    return True


def filter_picks(picks, rule, mode_config):
    tour_levels = mode_config.get("tour_levels")

    out = []

    for p in picks:
        if tour_levels and p["_tour_level"] not in tour_levels:
            continue

        if rule_passes(p, rule):
            out.append(p)

    return out


def score_rule(full_stats, train_stats, test_stats):
    profit = full_stats["profit"]
    roi = full_stats["roi"]
    test_profit = test_stats["profit"]
    test_roi = test_stats["roi"]
    max_dd = abs(full_stats["max_drawdown"])

    train_roi = train_stats["roi"]
    instability = abs(train_roi - test_roi)

    score = (
        profit * 1.0
        + roi * 0.25
        + test_profit * 1.5
        + test_roi * 0.35
        - max_dd * 1.25
        - instability * 0.65
    )

    return round(score, 4)


def build_rule_combinations(mode_config):
    forced_side = mode_config.get("side")

    side_values = [forced_side] if forced_side else SEARCH_SPACE["side"]

    for side in side_values:
        for line_min, line_max in itertools.product(SEARCH_SPACE["line_min"], SEARCH_SPACE["line_max"]):
            if not valid_range(line_min, line_max):
                continue

            for odds_min, odds_max in itertools.product(SEARCH_SPACE["odds_min"], SEARCH_SPACE["odds_max"]):
                if not valid_range(odds_min, odds_max):
                    continue

                for market_gap_min, market_gap_max in itertools.product(SEARCH_SPACE["market_gap_min"], SEARCH_SPACE["market_gap_max"]):
                    if not valid_range(market_gap_min, market_gap_max):
                        continue

                    for avg_three_set_min, avg_three_set_max in itertools.product(SEARCH_SPACE["avg_three_set_min"], SEARCH_SPACE["avg_three_set_max"]):
                        if not valid_range(avg_three_set_min, avg_three_set_max):
                            continue

                        for avg_close_set_min, avg_close_set_max in itertools.product(SEARCH_SPACE["avg_close_set_min"], SEARCH_SPACE["avg_close_set_max"]):
                            if not valid_range(avg_close_set_min, avg_close_set_max):
                                continue

                            for quality_min, quality_max in itertools.product(SEARCH_SPACE["quality_min"], SEARCH_SPACE["quality_max"]):
                                if not valid_range(quality_min, quality_max):
                                    continue

                                for confidence_min, confidence_max in itertools.product(SEARCH_SPACE["confidence_min"], SEARCH_SPACE["confidence_max"]):
                                    if not valid_range(confidence_min, confidence_max):
                                        continue

                                    for strength_gap_min, strength_gap_max in itertools.product(SEARCH_SPACE["strength_gap_min"], SEARCH_SPACE["strength_gap_max"]):
                                        if not valid_range(strength_gap_min, strength_gap_max):
                                            continue

                                        for h2h_max in SEARCH_SPACE["h2h_max"]:
                                            for bookmakers_min in SEARCH_SPACE["bookmakers_min"]:
                                                yield {
                                                    "side": side,
                                                    "line_min": line_min,
                                                    "line_max": line_max,
                                                    "odds_min": odds_min,
                                                    "odds_max": odds_max,
                                                    "market_gap_min": market_gap_min,
                                                    "market_gap_max": market_gap_max,
                                                    "avg_three_set_min": avg_three_set_min,
                                                    "avg_three_set_max": avg_three_set_max,
                                                    "avg_close_set_min": avg_close_set_min,
                                                    "avg_close_set_max": avg_close_set_max,
                                                    "quality_min": quality_min,
                                                    "quality_max": quality_max,
                                                    "confidence_min": confidence_min,
                                                    "confidence_max": confidence_max,
                                                    "strength_gap_min": strength_gap_min,
                                                    "strength_gap_max": strength_gap_max,
                                                    "h2h_max": h2h_max,
                                                    "bookmakers_min": bookmakers_min,
                                                }


def maybe_keep_top(results, item, limit):
    results.append(item)
    results.sort(key=lambda x: x["score"], reverse=True)

    if len(results) > limit:
        results.pop()

    return results


def optimize_mode(picks, mode_name, mode_config):
    top = []
    checked = 0
    passed_min_picks = 0
    passed_test_filter = 0

    for rule in build_rule_combinations(mode_config):
        checked += 1

        selected = filter_picks(picks, rule, mode_config)

        if len(selected) < MIN_PICKS_TARGET:
            continue

        passed_min_picks += 1

        train, test = split_train_test(selected)

        if REQUIRE_MIN_TEST_PICKS and len(test) < MIN_TEST_PICKS:
            continue

        full_stats = evaluate(selected)
        train_stats = evaluate(train)
        test_stats = evaluate(test)

        if REQUIRE_POSITIVE_TEST:
            if test_stats["profit"] <= 0 or test_stats["roi"] <= 0:
                continue

        passed_test_filter += 1

        score = score_rule(full_stats, train_stats, test_stats)

        item = {
            "mode": mode_name,
            "score": score,
            "rules": rule,
            "full": full_stats,
            "train": train_stats,
            "test": test_stats,
        }

        maybe_keep_top(top, item, TOP_N_PER_MODE)

    return {
        "mode": mode_name,
        "checked_rules": checked,
        "passed_min_picks": passed_min_picks,
        "passed_test_filter": passed_test_filter,
        "top": top,
    }


def bucket_value(value, buckets):
    for label, lo, hi in buckets:
        if value >= lo and value < hi:
            return label
    return "unknown"


def group_stats(picks, group_func):
    groups = {}

    for p in picks:
        key = group_func(p)
        groups.setdefault(str(key), []).append(p)

    out = []
    for key, items in sorted(groups.items(), key=lambda x: x[0]):
        s = evaluate(items)
        s["group"] = key
        out.append(s)

    out.sort(key=lambda x: x["profit"], reverse=True)
    return out


def breakdown_for_rule(picks, rule, mode_config):
    selected = filter_picks(picks, rule, mode_config)

    return {
        "by_side": group_stats(selected, lambda p: p["_side"]),
        "by_tour_level": group_stats(selected, lambda p: p["_tour_level"]),
        "by_gender": group_stats(selected, lambda p: p["_gender"]),
        "by_bookmaker": group_stats(selected, lambda p: p.get("best_bookmaker") or "unknown"),
        "by_line_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_line"],
                [
                    ("<=18.5", -999, 18.6),
                    ("18.5-19.5", 18.6, 19.6),
                    ("19.5-20.5", 19.6, 20.6),
                    ("20.5-21.5", 20.6, 21.6),
                    ("21.5-22.5", 21.6, 22.6),
                    (">22.5", 22.6, 999),
                ],
            ),
        ),
        "by_market_gap_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_market_gap"],
                [
                    ("<=0.20", -999, 0.2001),
                    ("0.20-0.25", 0.2001, 0.2501),
                    ("0.25-0.35", 0.2501, 0.3501),
                    ("0.35-0.45", 0.3501, 0.4501),
                    ("0.45-0.60", 0.4501, 0.6001),
                    (">0.60", 0.6001, 999),
                ],
            ),
        ),
        "by_avg_three_set_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_avg_three_set"],
                [
                    ("<=0.15", -999, 0.1501),
                    ("0.15-0.20", 0.1501, 0.2001),
                    ("0.20-0.25", 0.2001, 0.2501),
                    ("0.25-0.30", 0.2501, 0.3001),
                    ("0.30-0.35", 0.3001, 0.3501),
                    ("0.35-0.45", 0.3501, 0.4501),
                    (">0.45", 0.4501, 999),
                ],
            ),
        ),
        "by_avg_close_set_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_avg_close_set"],
                [
                    ("<=0.20", -999, 0.2001),
                    ("0.20-0.30", 0.2001, 0.3001),
                    ("0.30-0.35", 0.3001, 0.3501),
                    ("0.35-0.40", 0.3501, 0.4001),
                    ("0.40-0.50", 0.4001, 0.5001),
                    (">0.50", 0.5001, 999),
                ],
            ),
        ),
        "by_quality_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_quality"],
                [
                    ("<72", -999, 72),
                    ("72-76", 72, 76),
                    ("76-80", 76, 80),
                    ("80-84", 80, 84),
                    ("84-88", 84, 88),
                    ("88-92", 88, 92),
                    (">=92", 92, 999),
                ],
            ),
        ),
        "by_confidence_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_confidence"],
                [
                    ("<75", -999, 75),
                    ("75-80", 75, 80),
                    ("80-83", 80, 83),
                    ("83-86", 83, 86),
                    ("86-89", 86, 89),
                    ("89-92", 89, 92),
                    (">=92", 92, 999),
                ],
            ),
        ),
        "by_strength_gap_bucket": group_stats(
            selected,
            lambda p: bucket_value(
                p["_strength_gap"],
                [
                    ("<=5", -999, 5.0001),
                    ("5-10", 5.0001, 10.0001),
                    ("10-15", 10.0001, 15.0001),
                    ("15-20", 15.0001, 20.0001),
                    ("20-25", 20.0001, 25.0001),
                    ("25-30", 25.0001, 30.0001),
                    (">30", 30.0001, 999),
                ],
            ),
        ),
    }


def compact_stats(s):
    return (
        f"picks {s['picks']}, W-L-P {s['wins']}-{s['losses']}-{s['pushes']}, "
        f"WR {s['winrate']}%, profit {s['profit']}u, ROI {s['roi']}%, "
        f"avg odds {s['avg_odds']}, maxDD {s['max_drawdown']}u"
    )


def format_rules_md(rules):
    lines = []
    lines.append("```python")
    lines.append("RULES_OPTIMIZED_150 = {")
    for k, v in rules.items():
        if isinstance(v, str) or v is None:
            lines.append(f'    "{k}": {json.dumps(v)},')
        else:
            lines.append(f'    "{k}": {v},')
    lines.append("}")
    lines.append("```")
    return "\n".join(lines)


def stats_table(title, rows, max_rows=20):
    lines = []
    lines.append(f"### {title}")
    lines.append("")
    lines.append("| Group | Picks | W | L | P | WR % | Profit | ROI % | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for r in rows[:max_rows]:
        lines.append(
            f"| {r.get('group')} | "
            f"{r.get('picks')} | "
            f"{r.get('wins')} | "
            f"{r.get('losses')} | "
            f"{r.get('pushes')} | "
            f"{r.get('winrate')} | "
            f"{r.get('profit')} | "
            f"{r.get('roi')} | "
            f"{r.get('avg_odds')} | "
            f"{r.get('max_drawdown')} |"
        )

    lines.append("")
    return "\n".join(lines)


def build_report(summary, all_results):
    lines = []

    lines.append("# Lucija Formula Optimizer 150")
    lines.append("")
    lines.append(f"Generated: `{summary['generated_at']}`")
    lines.append("")
    lines.append(f"Source file: `{SOURCE_FILE}`")
    lines.append(f"Source settled picks: **{summary['settled_count']}**")
    lines.append(f"Minimum picks target: **{MIN_PICKS_TARGET}**")
    lines.append("")
    lines.append("Score formula:")
    lines.append("")
    lines.append("```text")
    lines.append("score = profit*1.0 + roi*0.25 + test_profit*1.5 + test_roi*0.35 - abs(max_drawdown)*1.25 - abs(train_roi-test_roi)*0.65")
    lines.append("```")
    lines.append("")

    for mode_name, result in all_results.items():
        lines.append(f"## {mode_name}")
        lines.append("")
        lines.append(f"Checked rules: **{result['checked_rules']}**")
        lines.append(f"Passed min picks: **{result['passed_min_picks']}**")
        lines.append(f"Passed test filter: **{result['passed_test_filter']}**")
        lines.append("")

        top = result.get("top") or []

        if not top:
            lines.append("No valid formula found.")
            lines.append("")
            continue

        best = top[0]

        lines.append(f"Best score: **{best['score']}**")
        lines.append("")
        lines.append("### Best rules")
        lines.append("")
        lines.append(format_rules_md(best["rules"]))
        lines.append("")
        lines.append("### Results")
        lines.append("")
        lines.append(f"- Full: {compact_stats(best['full'])}")
        lines.append(f"- Train: {compact_stats(best['train'])}")
        lines.append(f"- Test: {compact_stats(best['test'])}")
        lines.append("")

        lines.append("### Top formulas")
        lines.append("")
        lines.append("| Rank | Score | Picks | Profit | ROI % | Test picks | Test profit | Test ROI % | Max DD |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for idx, item in enumerate(top[:10], start=1):
            lines.append(
                f"| {idx} | "
                f"{item['score']} | "
                f"{item['full']['picks']} | "
                f"{item['full']['profit']} | "
                f"{item['full']['roi']} | "
                f"{item['test']['picks']} | "
                f"{item['test']['profit']} | "
                f"{item['test']['roi']} | "
                f"{item['full']['max_drawdown']} |"
            )

        lines.append("")

        breakdown = best.get("breakdown") or {}

        if breakdown:
            lines.append("## Best formula breakdown")
            lines.append("")
            lines.append(stats_table("By side", breakdown.get("by_side", [])))
            lines.append(stats_table("By tour level", breakdown.get("by_tour_level", [])))
            lines.append(stats_table("By gender", breakdown.get("by_gender", [])))
            lines.append(stats_table("By line bucket", breakdown.get("by_line_bucket", [])))
            lines.append(stats_table("By market gap bucket", breakdown.get("by_market_gap_bucket", [])))
            lines.append(stats_table("By avg three set bucket", breakdown.get("by_avg_three_set_bucket", [])))
            lines.append(stats_table("By avg close set bucket", breakdown.get("by_avg_close_set_bucket", [])))
            lines.append(stats_table("By quality bucket", breakdown.get("by_quality_bucket", [])))
            lines.append(stats_table("By confidence bucket", breakdown.get("by_confidence_bucket", [])))
            lines.append(stats_table("By strength gap bucket", breakdown.get("by_strength_gap_bucket", [])))
            lines.append(stats_table("By bookmaker", breakdown.get("by_bookmaker", [])))

    return "\n".join(lines)


def main():
    ensure_dirs()

    raw = load_json(SOURCE_FILE, [])

    if isinstance(raw, dict):
        source = raw.get("picks") or raw.get("results") or []
    elif isinstance(raw, list):
        source = raw
    else:
        source = []

    enriched = []
    for p in source:
        if not isinstance(p, dict):
            continue

        if not is_settled(p):
            continue

        ep = enrich_pick(p)

        if ep["_side"] not in {"under", "over"}:
            continue

        if ep["_odds"] <= 1:
            continue

        if ep["_line"] <= 0:
            continue

        enriched.append(ep)

    enriched.sort(
        key=lambda p: (
            str(p.get("date") or ""),
            str(p.get("time") or ""),
            str(p.get("match") or ""),
            str(p.get("pick_id") or ""),
        )
    )

    print("")
    print("LUCIJA FORMULA OPTIMIZER 150")
    print(f"Source loaded: {len(source)}")
    print(f"Settled usable: {len(enriched)}")
    print("")

    all_results = {}

    for mode_name, mode_config in MODES.items():
        print(f"Optimizing {mode_name}...")
        result = optimize_mode(enriched, mode_name, mode_config)

        if result.get("top"):
            best_rule = result["top"][0]["rules"]
            result["top"][0]["breakdown"] = breakdown_for_rule(enriched, best_rule, mode_config)

        all_results[mode_name] = result

        best = result["top"][0] if result.get("top") else None
        if best:
            print(
                f"  best score={best['score']} "
                f"picks={best['full']['picks']} "
                f"profit={best['full']['profit']} "
                f"roi={best['full']['roi']} "
                f"test_roi={best['test']['roi']}"
            )
        else:
            print("  no formula found")

    summary = {
        "generated_at": now_iso(),
        "source_file": SOURCE_FILE,
        "source_count": len(source),
        "settled_count": len(enriched),
        "min_picks_target": MIN_PICKS_TARGET,
        "train_ratio": TRAIN_RATIO,
        "require_positive_test": REQUIRE_POSITIVE_TEST,
        "require_min_test_picks": REQUIRE_MIN_TEST_PICKS,
        "min_test_picks": MIN_TEST_PICKS,
        "search_space": SEARCH_SPACE,
        "modes": MODES,
        "baseline": evaluate(enriched),
        "best": {},
    }

    top_rules = {
        "generated_at": summary["generated_at"],
        "source_file": SOURCE_FILE,
        "min_picks_target": MIN_PICKS_TARGET,
        "rules": {},
    }

    for mode_name, result in all_results.items():
        top = result.get("top") or []

        if top:
            summary["best"][mode_name] = top[0]
            top_rules["rules"][mode_name] = top[0]["rules"]
        else:
            summary["best"][mode_name] = None
            top_rules["rules"][mode_name] = None

    save_json(SUMMARY_FILE, summary)
    save_json(TOP_RULES_FILE, top_rules)

    report = build_report(summary, all_results)
    save_text(REPORT_FILE, report)

    print("")
    print("DONE")
    print(f"Summary: {SUMMARY_FILE}")
    print(f"Top rules: {TOP_RULES_FILE}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

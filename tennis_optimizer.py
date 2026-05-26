import os
import json
import math
import itertools
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
OUTPUT_DIR = "tennis_optimizer"

RESULTS_FILE = f"{DATA_DIR}/tennis_results.json"

REPORT_FILE = f"{OUTPUT_DIR}/tennis_optimizer_report.md"
BEST_RULES_FILE = f"{OUTPUT_DIR}/tennis_best_rules.json"
TABLE_FILE = f"{OUTPUT_DIR}/tennis_optimizer_table.json"
PICKS_FILE = f"{OUTPUT_DIR}/tennis_optimizer_picks.json"
DEBUG_FILE = f"{OUTPUT_DIR}/tennis_optimizer_debug.json"
SUMMARY_FILE = f"{OUTPUT_DIR}/tennis_optimizer_summary.json"

MIN_PICKS = int(os.getenv("MIN_PICKS", "100"))
TOP_N = int(os.getenv("TOP_N", "75"))

# Za GitHub Actions. Če želiš močnejši run:
# MAX_CANDIDATES=750000 MAX_RULES_PER_COMBO=7 python tennis_optimizer.py
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "250000"))
MAX_RULES_PER_COMBO = int(os.getenv("MAX_RULES_PER_COMBO", "6"))

FLAT_STAKE = 1.0

SCORE_WEIGHTS = {
    "profit": 1.00,
    "roi": 0.35,
    "winrate": 0.15,
    "avg_odds": 0.10,
    "drawdown_penalty": 0.60,
    "sample_bonus": 0.08,
}

RULE_GRID = {
    "confidence_min": [None, 50, 55, 60, 65, 70, 75, 80, 85],
    "quality_min": [None, 50, 55, 60, 65, 70, 72, 75, 80],
    "edge_min": [None, 0.00, 0.02, 0.04, 0.06, 0.08, 0.10],
    "odds_min": [None, 1.30, 1.45, 1.60, 1.75, 1.90, 2.05],
    "odds_max": [None, 1.70, 1.90, 2.10, 2.30, 2.60, 3.00],
    "market_gap_min": [None, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40],
    "market_gap_max": [None, 0.25, 0.35, 0.50, 0.70],
    "strength_gap_min": [None, 3, 5, 8, 10, 15, 20, 30],
    "strength_gap_max": [None, 10, 15, 20, 30, 40, 60],
    "h2h_max": [None, 0, 1, 2, 3],
    "bookmakers_min": [None, 2, 3, 4, 5, 6, 8],
    "rank_max": [None, 10, 20, 30, 50, 100],
}

CATEGORICAL_RULES = {
    "side": [None, "home", "away"],
    "gender": [None, "men", "women"],
    "tour_level": [None, "atp", "wta", "challenger", "itf"],
    "qualification": [None, True, False],
}


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, type(default)):
            return data

        return default

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


def get_nested(data, path, default=None):
    cur = data

    for part in path.split("."):
        if not isinstance(cur, dict):
            return default

        if part not in cur:
            return default

        cur = cur[part]

    return cur


def normalize_result(value):
    result = str(value or "").strip().lower()

    if result in {"won", "win", "w"}:
        return "win"

    if result in {"lost", "loss", "lose", "l"}:
        return "loss"

    if result in {"push", "void", "cancelled", "canceled"}:
        return "push"

    if result == "pending":
        return "pending"

    return result


def is_settled(pick):
    return normalize_result(pick.get("result")) in {"win", "loss", "push"}


def side_value(pick):
    raw = str(
        pick.get("side")
        or pick.get("pick")
        or pick.get("selection")
        or ""
    ).strip().lower()

    if raw in {"home", "first", "1", "first_player", "player1", "player_1"}:
        return "home"

    if raw in {"away", "second", "2", "second_player", "player2", "player_2"}:
        return "away"

    bet = str(pick.get("bet") or "").lower()
    first = str(pick.get("first_player_name") or "").lower()
    second = str(pick.get("second_player_name") or "").lower()

    if first and first in bet:
        return "home"

    if second and second in bet:
        return "away"

    return raw or None


def pick_profit(pick, stake=FLAT_STAKE):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), None)

    if result == "win":
        if odds is None:
            return 0.0
        return stake * (odds - 1.0)

    if result == "loss":
        return -stake

    return 0.0


def max_drawdown(profits):
    bankroll = 0.0
    peak = 0.0
    max_dd = 0.0

    for profit in profits:
        bankroll += profit
        peak = max(peak, bankroll)
        drawdown = bankroll - peak
        max_dd = min(max_dd, drawdown)

    return round(max_dd, 4)


def longest_streak(results, target):
    best = 0
    current = 0

    for result in results:
        if result == target:
            current += 1
            best = max(best, current)
        else:
            current = 0

    return best


def extract_features(pick):
    market_info = pick.get("market_info")
    if not isinstance(market_info, dict):
        market_info = {}

    first_strength = safe_float(pick.get("first_strength_score"), None)
    second_strength = safe_float(pick.get("second_strength_score"), None)
    strength_gap = safe_float(pick.get("strength_gap"), None)

    if strength_gap is None and first_strength is not None and second_strength is not None:
        strength_gap = abs(first_strength - second_strength)

    market_gap = safe_float(market_info.get("market_gap"), None)

    if market_gap is None:
        home_implied = safe_float(market_info.get("home_implied"), None)
        away_implied = safe_float(market_info.get("away_implied"), None)

        if home_implied is not None and away_implied is not None:
            market_gap = abs(home_implied - away_implied)

    return {
        "confidence": safe_float(pick.get("confidence"), None),
        "quality": safe_float(pick.get("quality_score"), None),
        "edge": safe_float(pick.get("edge"), None),
        "odds": safe_float(pick.get("odds"), None),
        "model_prob": safe_float(pick.get("model_prob"), None),
        "implied_prob": safe_float(pick.get("implied_prob"), None),
        "bookmakers": safe_int(pick.get("bookmakers_used"), None),
        "rank": safe_int(pick.get("rank"), None),
        "market_gap": market_gap,
        "strength_gap": abs(strength_gap) if strength_gap is not None else None,
        "h2h": safe_int(pick.get("h2h_matches"), None),
        "side": side_value(pick),
        "gender": str(pick.get("gender") or "").lower() or None,
        "tour_level": str(pick.get("tour_level") or "").lower() or None,
        "qualification": pick.get("qualification") if isinstance(pick.get("qualification"), bool) else None,
    }


def enrich_pick(pick):
    enriched = dict(pick)
    enriched["_result_norm"] = normalize_result(pick.get("result"))
    enriched["_profit_flat"] = round(pick_profit(pick, FLAT_STAKE), 4)
    enriched["_features"] = extract_features(pick)

    return enriched


def valid_rule_combo(rule):
    odds_min = rule.get("odds_min")
    odds_max = rule.get("odds_max")

    if odds_min is not None and odds_max is not None and odds_min > odds_max:
        return False

    strength_gap_min = rule.get("strength_gap_min")
    strength_gap_max = rule.get("strength_gap_max")

    if strength_gap_min is not None and strength_gap_max is not None and strength_gap_min > strength_gap_max:
        return False

    market_gap_min = rule.get("market_gap_min")
    market_gap_max = rule.get("market_gap_max")

    if market_gap_min is not None and market_gap_max is not None and market_gap_min > market_gap_max:
        return False

    return True


def clean_rule(rule):
    return {
        key: value
        for key, value in rule.items()
        if value is not None
    }


def rule_complexity(rule):
    return len(clean_rule(rule))


def passes_rule(pick, rule):
    features = pick.get("_features", {})

    checks = [
        ("confidence_min", "confidence", ">="),
        ("quality_min", "quality", ">="),
        ("edge_min", "edge", ">="),
        ("odds_min", "odds", ">="),
        ("odds_max", "odds", "<="),
        ("market_gap_min", "market_gap", ">="),
        ("market_gap_max", "market_gap", "<="),
        ("strength_gap_min", "strength_gap", ">="),
        ("strength_gap_max", "strength_gap", "<="),
        ("h2h_max", "h2h", "<="),
        ("bookmakers_min", "bookmakers", ">="),
        ("rank_max", "rank", "<="),
    ]

    for rule_key, feature_key, operator in checks:
        threshold = rule.get(rule_key)

        if threshold is None:
            continue

        value = features.get(feature_key)

        if value is None:
            return False

        if operator == ">=" and value < threshold:
            return False

        if operator == "<=" and value > threshold:
            return False

    for key in CATEGORICAL_RULES:
        wanted = rule.get(key)

        if wanted is None:
            continue

        actual = features.get(key)

        if actual != wanted:
            return False

    return True


def evaluate_picks(picks):
    settled = [
        pick
        for pick in picks
        if pick.get("_result_norm") in {"win", "loss", "push"}
    ]

    wins = [
        pick
        for pick in settled
        if pick.get("_result_norm") == "win"
    ]

    losses = [
        pick
        for pick in settled
        if pick.get("_result_norm") == "loss"
    ]

    pushes = [
        pick
        for pick in settled
        if pick.get("_result_norm") == "push"
    ]

    profits = [
        safe_float(pick.get("_profit_flat"), 0.0)
        for pick in settled
    ]

    total_profit = round(sum(profits), 4)
    stake_sum = len(settled) * FLAT_STAKE

    roi = round((total_profit / stake_sum) * 100, 2) if stake_sum else 0.0

    decided = len(wins) + len(losses)
    winrate = round((len(wins) / decided) * 100, 2) if decided else 0.0

    odds_values = [
        safe_float(pick.get("odds"), None)
        for pick in settled
    ]
    odds_values = [
        value
        for value in odds_values
        if value is not None
    ]

    results = [
        pick.get("_result_norm")
        for pick in settled
    ]

    return {
        "picks": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "winrate": winrate,
        "profit": total_profit,
        "roi": roi,
        "avg_odds": round(sum(odds_values) / len(odds_values), 4) if odds_values else 0.0,
        "max_drawdown": max_drawdown(profits),
        "longest_win_streak": longest_streak(results, "win"),
        "longest_loss_streak": longest_streak(results, "loss"),
    }


def strategy_score(stats):
    if stats["picks"] < MIN_PICKS:
        return -999999

    sample_bonus = math.log(max(1, stats["picks"]))
    drawdown_abs = abs(stats["max_drawdown"])

    score = (
        stats["profit"] * SCORE_WEIGHTS["profit"]
        + stats["roi"] * SCORE_WEIGHTS["roi"]
        + stats["winrate"] * SCORE_WEIGHTS["winrate"]
        + stats["avg_odds"] * SCORE_WEIGHTS["avg_odds"]
        + sample_bonus * SCORE_WEIGHTS["sample_bonus"]
        - drawdown_abs * SCORE_WEIGHTS["drawdown_penalty"]
    )

    return round(score, 6)


def generate_rule_candidates():
    numeric_keys = list(RULE_GRID.keys())
    categorical_keys = list(CATEGORICAL_RULES.keys())

    numeric_blocks = [
        ["confidence_min", "quality_min", "edge_min"],
        ["odds_min", "odds_max"],
        ["market_gap_min", "market_gap_max"],
        ["strength_gap_min", "strength_gap_max"],
        ["h2h_max", "bookmakers_min", "rank_max"],
    ]

    base_rules = [{}]

    for block in numeric_blocks:
        new_rules = []
        values = [RULE_GRID[key] for key in block]

        for combo in itertools.product(*values):
            block_rule = {
                key: value
                for key, value in zip(block, combo)
            }

            if not valid_rule_combo(block_rule):
                continue

            for base_rule in base_rules:
                merged = dict(base_rule)
                merged.update(block_rule)

                if not valid_rule_combo(merged):
                    continue

                if rule_complexity(merged) <= MAX_RULES_PER_COMBO:
                    new_rules.append(merged)

        base_rules = new_rules

    all_rules = []
    categorical_values = [
        CATEGORICAL_RULES[key]
        for key in categorical_keys
    ]

    for base_rule in base_rules:
        for combo in itertools.product(*categorical_values):
            rule = dict(base_rule)

            for key, value in zip(categorical_keys, combo):
                rule[key] = value

            if not valid_rule_combo(rule):
                continue

            cleaned = clean_rule(rule)

            if rule_complexity(cleaned) > MAX_RULES_PER_COMBO:
                continue

            all_rules.append(cleaned)

            if len(all_rules) >= MAX_CANDIDATES:
                return deduplicate_rules(all_rules)

    return deduplicate_rules(all_rules)


def deduplicate_rules(rules):
    seen = set()
    unique = []

    for rule in rules:
        key = json.dumps(rule, sort_keys=True, ensure_ascii=False)

        if key in seen:
            continue

        seen.add(key)
        unique.append(rule)

    return unique


def split_train_test(picks, test_ratio=0.25):
    ordered = sorted(
        picks,
        key=lambda pick: (
            str(pick.get("date") or ""),
            str(pick.get("time") or ""),
            str(pick.get("created_at") or ""),
            str(pick.get("pick_id") or ""),
        )
    )

    if len(ordered) < 4:
        return ordered, []

    cut = int(len(ordered) * (1 - test_ratio))
    cut = max(1, min(cut, len(ordered) - 1))

    return ordered[:cut], ordered[cut:]


def breakdown(picks, field):
    groups = defaultdict(list)

    for pick in picks:
        if field.startswith("_features."):
            key = field.split(".", 1)[1]
            value = pick.get("_features", {}).get(key)
        else:
            value = get_nested(pick, field, None)

        if value is None or value == "":
            value = "unknown"

        groups[str(value)].append(pick)

    rows = []

    for group, items in groups.items():
        stats = evaluate_picks(items)
        rows.append({
            "group": group,
            **stats,
        })

    rows.sort(
        key=lambda row: (
            row["profit"],
            row["roi"],
            row["picks"],
        ),
        reverse=True,
    )

    return rows


def numeric_ranges(picks, feature_key):
    values = []

    for pick in picks:
        value = pick.get("_features", {}).get(feature_key)

        if isinstance(value, (int, float)):
            values.append(value)

    if not values:
        return None

    values = sorted(values)
    count = len(values)

    def quantile(percent):
        index = int(round((count - 1) * percent))
        return round(values[index], 4)

    return {
        "min": round(values[0], 4),
        "p25": quantile(0.25),
        "median": quantile(0.50),
        "p75": quantile(0.75),
        "max": round(values[-1], 4),
        "avg": round(sum(values) / count, 4),
    }


def format_rule(rule):
    if not rule:
        return "No filters"

    labels = {
        "confidence_min": "confidence ≥",
        "quality_min": "quality ≥",
        "edge_min": "edge ≥",
        "odds_min": "odds ≥",
        "odds_max": "odds ≤",
        "market_gap_min": "market gap ≥",
        "market_gap_max": "market gap ≤",
        "strength_gap_min": "strength gap ≥",
        "strength_gap_max": "strength gap ≤",
        "h2h_max": "h2h ≤",
        "bookmakers_min": "bookmakers ≥",
        "rank_max": "rank ≤",
        "side": "side =",
        "gender": "gender =",
        "tour_level": "tour =",
        "qualification": "qualification =",
    }

    parts = []

    for key, value in rule.items():
        label = labels.get(key, key)
        parts.append(f"{label} {value}")

    return "; ".join(parts)


def public_pick(pick):
    item = dict(pick)
    item.pop("_features", None)
    return item


def make_markdown_report(
    generated_at,
    source_count,
    settled_count,
    candidate_rules_tested,
    valid_rules_over_min_sample,
    all_stats,
    best,
    top_rows,
    best_picks,
    train_stats,
    test_stats,
    breakdowns,
    ranges,
):
    lines = []

    lines.append("# Tennis Home/Away Optimizer Report")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Source picks loaded: **{source_count}**")
    lines.append(f"- Settled picks used: **{settled_count}**")
    lines.append(f"- Candidate rules tested: **{candidate_rules_tested}**")
    lines.append(f"- Valid rules over minimum sample: **{valid_rules_over_min_sample}**")
    lines.append(f"- Minimum sample per valid strategy: **{MIN_PICKS} picks**")
    lines.append(f"- Max candidates limit: **{MAX_CANDIDATES}**")
    lines.append(f"- Max rules per combo: **{MAX_RULES_PER_COMBO}**")
    lines.append("")
    lines.append("## Whole database baseline")
    lines.append("")
    lines.append("| Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {all_stats['picks']} | {all_stats['wins']} | {all_stats['losses']} | {all_stats['pushes']} | "
        f"{all_stats['winrate']}% | {all_stats['profit']}u | {all_stats['roi']}% | "
        f"{all_stats['avg_odds']} | {all_stats['max_drawdown']}u |"
    )
    lines.append("")

    if not best:
        lines.append("## Best strategy")
        lines.append("")
        lines.append("No strategy passed the minimum sample requirement.")
        lines.append("")
        lines.append("Try lowering `MIN_PICKS`, for example:")
        lines.append("")
        lines.append("```bash")
        lines.append("MIN_PICKS=75 python tennis_optimizer.py")
        lines.append("```")
        lines.append("")
        return "\n".join(lines) + "\n"

    lines.append("## Best strategy found")
    lines.append("")
    lines.append(f"**Score:** {best['score']}")
    lines.append("")
    lines.append(f"**Rules:** {format_rule(best['rules'])}")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(best["rules"], indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("| Split | Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for name, stats in [
        ("Full", best["stats"]),
        ("Train 75%", train_stats),
        ("Test 25%", test_stats),
    ]:
        lines.append(
            f"| {name} | {stats['picks']} | {stats['wins']} | {stats['losses']} | {stats['pushes']} | "
            f"{stats['winrate']}% | {stats['profit']}u | {stats['roi']}% | "
            f"{stats['avg_odds']} | {stats['max_drawdown']}u |"
        )

    lines.append("")
    lines.append("## Recommended tactic")
    lines.append("")
    lines.append("Use this optimizer as a filter layer on top of the existing tennis home/away machine.")
    lines.append("")
    lines.append("Stake suggestion:")
    lines.append("")
    lines.append("- Report simulation uses **flat 1u**.")
    lines.append("- Live start suggestion: **0.5u flat** until at least 50 new forward-test picks.")
    lines.append("- After forward confirmation: **1u flat**, no martingale.")
    lines.append("")
    lines.append("Important: this is historical optimization. The main validation number is the **Test 25%** result and then forward tracking.")
    lines.append("")

    lines.append("## Top strategies")
    lines.append("")
    lines.append("| Rank | Score | Picks | Winrate | Profit | ROI | Avg odds | Max DD | Rules |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    for index, row in enumerate(top_rows[:25], start=1):
        stats = row["stats"]
        lines.append(
            f"| {index} | {row['score']} | {stats['picks']} | {stats['winrate']}% | "
            f"{stats['profit']}u | {stats['roi']}% | {stats['avg_odds']} | "
            f"{stats['max_drawdown']}u | {format_rule(row['rules'])} |"
        )

    lines.append("")
    lines.append("## Best strategy selected picks sample")
    lines.append("")
    lines.append("| Date | Match | Bet | Result | Odds | Profit |")
    lines.append("|---|---|---|---:|---:|---:|")

    for pick in best_picks[:50]:
        lines.append(
            f"| {pick.get('date', '')} {pick.get('time', '')} | "
            f"{pick.get('match', '')} | "
            f"{pick.get('bet') or pick.get('selection') or pick.get('side', '')} | "
            f"{pick.get('_result_norm')} | "
            f"{pick.get('odds', '')} | "
            f"{pick.get('_profit_flat')} |"
        )

    lines.append("")
    lines.append("## Feature ranges inside best strategy")
    lines.append("")
    lines.append("| Feature | Min | P25 | Median | P75 | Max | Avg |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for feature, data in ranges.items():
        if not data:
            continue

        lines.append(
            f"| {feature} | {data['min']} | {data['p25']} | {data['median']} | "
            f"{data['p75']} | {data['max']} | {data['avg']} |"
        )

    lines.append("")
    lines.append("## Breakdown of best strategy")
    lines.append("")

    for title, rows in breakdowns.items():
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")

        for row in rows[:15]:
            lines.append(
                f"| {row['group']} | {row['picks']} | {row['winrate']}% | "
                f"{row['profit']}u | {row['roi']}% | {row['avg_odds']} | "
                f"{row['max_drawdown']}u |"
            )

        lines.append("")

    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append(f"- `{BEST_RULES_FILE}`")
    lines.append(f"- `{TABLE_FILE}`")
    lines.append(f"- `{PICKS_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append(f"- `{SUMMARY_FILE}`")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    ensure_dirs()

    raw = load_json(RESULTS_FILE, [])

    if not isinstance(raw, list):
        raw = []

    enriched = [
        enrich_pick(pick)
        for pick in raw
        if isinstance(pick, dict)
    ]

    settled = [
        pick
        for pick in enriched
        if is_settled(pick)
    ]

    all_stats = evaluate_picks(settled)

    candidates = generate_rule_candidates()

    evaluated = []

    for rule in candidates:
        selected = [
            pick
            for pick in settled
            if passes_rule(pick, rule)
        ]

        if len(selected) < MIN_PICKS:
            continue

        stats = evaluate_picks(selected)
        score = strategy_score(stats)

        evaluated.append({
            "score": score,
            "rules": rule,
            "stats": stats,
        })

    evaluated.sort(
        key=lambda row: (
            row["score"],
            row["stats"]["profit"],
            row["stats"]["roi"],
            row["stats"]["picks"],
        ),
        reverse=True,
    )

    top_rows = evaluated[:TOP_N]
    best = top_rows[0] if top_rows else None

    best_picks = []
    train_stats = evaluate_picks([])
    test_stats = evaluate_picks([])
    breakdowns = {}
    ranges = {}

    if best:
        best_picks = [
            pick
            for pick in settled
            if passes_rule(pick, best["rules"])
        ]

        train_picks, test_picks = split_train_test(best_picks)

        train_stats = evaluate_picks(train_picks)
        test_stats = evaluate_picks(test_picks)

        breakdown_fields = {
            "By side": "_features.side",
            "By gender": "_features.gender",
            "By tour level": "_features.tour_level",
            "By qualification": "_features.qualification",
            "By bookmaker": "best_bookmaker",
            "By tournament": "tournament",
        }

        breakdowns = {
            title: breakdown(best_picks, field)
            for title, field in breakdown_fields.items()
        }

        for feature in [
            "confidence",
            "quality",
            "edge",
            "odds",
            "market_gap",
            "strength_gap",
            "bookmakers",
            "rank",
        ]:
            ranges[feature] = numeric_ranges(best_picks, feature)

    generated_at = now_iso()

    summary = {
        "generated_at": generated_at,
        "source_file": RESULTS_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "min_picks": MIN_PICKS,
        "max_candidates": MAX_CANDIDATES,
        "max_rules_per_combo": MAX_RULES_PER_COMBO,
        "candidate_rules_tested": len(candidates),
        "valid_rules_over_min_sample": len(evaluated),
        "baseline": all_stats,
        "best": best,
        "train_75_stats": train_stats,
        "test_25_stats": test_stats,
        "output_dir": OUTPUT_DIR,
    }

    debug = {
        "generated_at": generated_at,
        "candidate_rules_tested": len(candidates),
        "valid_rules_over_min_sample": len(evaluated),
        "min_picks": MIN_PICKS,
        "top_n": TOP_N,
        "max_candidates": MAX_CANDIDATES,
        "max_rules_per_combo": MAX_RULES_PER_COMBO,
        "flat_stake": FLAT_STAKE,
        "score_weights": SCORE_WEIGHTS,
        "rule_grid": RULE_GRID,
        "categorical_rules": CATEGORICAL_RULES,
        "source_count": len(raw),
        "settled_count": len(settled),
        "missing_or_pending_count": len(enriched) - len(settled),
    }

    save_json(SUMMARY_FILE, summary)
    save_json(BEST_RULES_FILE, best["rules"] if best else {})
    save_json(TABLE_FILE, top_rows)
    save_json(PICKS_FILE, [public_pick(pick) for pick in best_picks])
    save_json(DEBUG_FILE, debug)

    report = make_markdown_report(
        generated_at=generated_at,
        source_count=len(raw),
        settled_count=len(settled),
        candidate_rules_tested=len(candidates),
        valid_rules_over_min_sample=len(evaluated),
        all_stats=all_stats,
        best=best,
        top_rows=top_rows,
        best_picks=best_picks,
        train_stats=train_stats,
        test_stats=test_stats,
        breakdowns=breakdowns,
        ranges=ranges,
    )

    save_text(REPORT_FILE, report)

    print("")
    print("TENNIS OPTIMIZER DONE")
    print(f"source picks: {len(raw)}")
    print(f"settled picks: {len(settled)}")
    print(f"candidate rules tested: {len(candidates)}")
    print(f"valid rules over min sample: {len(evaluated)}")
    print(f"min picks: {MIN_PICKS}")
    print(f"max candidates: {MAX_CANDIDATES}")
    print(f"max rules per combo: {MAX_RULES_PER_COMBO}")

    if best:
        print("")
        print("BEST RULES:")
        print(json.dumps(best["rules"], indent=2, ensure_ascii=False))
        print("")
        print("FULL:")
        print(best["stats"])
        print("")
        print("TRAIN 75%:")
        print(train_stats)
        print("")
        print("TEST 25%:")
        print(test_stats)
    else:
        print("")
        print("No valid strategy found.")
        print("Try lowering MIN_PICKS, for example:")
        print("MIN_PICKS=75 python tennis_optimizer.py")

    print("")
    print(f"Report: {REPORT_FILE}")
    print("")


if __name__ == "__main__":
    main()

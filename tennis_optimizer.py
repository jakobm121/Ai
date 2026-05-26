import os
import json
import math
import itertools
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter

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

# Glavna zaščita pred overfitom.
# Če želiš bolj strogo, dvigni na 150 ali 200.
MIN_PICKS = int(os.getenv("MIN_PICKS", "100"))

# Koliko najboljših kombinacij shranimo v table/report.
TOP_N = int(os.getenv("TOP_N", "75"))

# Za stake simulacije.
FLAT_STAKE = 1.0

# Score uteži. Profit in ROI sta pomembna, ampak kaznujemo majhen sample in velik drawdown.
SCORE_WEIGHTS = {
    "profit": 1.00,
    "roi": 0.35,
    "winrate": 0.15,
    "avg_odds": 0.10,
    "drawdown_penalty": 0.60,
    "sample_bonus": 0.08,
}

# Pravila, ki jih optimizer testira.
# min = value >= threshold
# max = value <= threshold
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
    "side": [None, "home", "away", "first", "second"],
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


def get_nested(d, path, default=None):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def normalize_result(value):
    r = str(value or "").strip().lower()
    if r in {"won", "win", "w"}:
        return "win"
    if r in {"lost", "loss", "lose", "l"}:
        return "loss"
    if r in {"push", "void", "cancelled", "canceled"}:
        return r
    if r == "pending":
        return "pending"
    return r


def is_settled(pick):
    return normalize_result(pick.get("result")) in {"win", "loss", "push"}


def side_value(pick):
    raw = str(pick.get("side") or pick.get("pick") or pick.get("selection") or "").lower()
    if raw in {"home", "first", "1", "first_player"}:
        return "home"
    if raw in {"away", "second", "2", "second_player"}:
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

    for p in profits:
        bankroll += p
        peak = max(peak, bankroll)
        dd = bankroll - peak
        max_dd = min(max_dd, dd)

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


def extract_features(pick):
    market_info = pick.get("market_info") if isinstance(pick.get("market_info"), dict) else {}

    first_strength = safe_float(pick.get("first_strength_score"), None)
    second_strength = safe_float(pick.get("second_strength_score"), None)
    strength_gap = safe_float(pick.get("strength_gap"), None)

    if strength_gap is None and first_strength is not None and second_strength is not None:
        strength_gap = abs(first_strength - second_strength)

    side = side_value(pick)

    market_gap = safe_float(market_info.get("market_gap"), None)
    if market_gap is None:
        home = safe_float(market_info.get("home_implied"), None)
        away = safe_float(market_info.get("away_implied"), None)
        if home is not None and away is not None:
            market_gap = abs(home - away)

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
        "side": side,
        "gender": str(pick.get("gender") or "").lower() or None,
        "tour_level": str(pick.get("tour_level") or "").lower() or None,
        "qualification": pick.get("qualification") if isinstance(pick.get("qualification"), bool) else None,
    }


def enrich_pick(pick):
    p = dict(pick)
    p["_result_norm"] = normalize_result(pick.get("result"))
    p["_profit_flat"] = round(pick_profit(pick, FLAT_STAKE), 4)
    p["_features"] = extract_features(pick)
    return p


def valid_rule_combo(rule):
    odds_min = rule.get("odds_min")
    odds_max = rule.get("odds_max")
    if odds_min is not None and odds_max is not None and odds_min > odds_max:
        return False

    sg_min = rule.get("strength_gap_min")
    sg_max = rule.get("strength_gap_max")
    if sg_min is not None and sg_max is not None and sg_min > sg_max:
        return False

    gap_min = rule.get("market_gap_min")
    gap_max = rule.get("market_gap_max")
    if gap_min is not None and gap_max is not None and gap_min > gap_max:
        return False

    return True


def passes_rule(pick, rule):
    f = pick.get("_features", {})

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

    for rule_key, feature_key, op in checks:
        threshold = rule.get(rule_key)
        if threshold is None:
            continue

        value = f.get(feature_key)
        if value is None:
            return False

        if op == ">=" and value < threshold:
            return False
        if op == "<=" and value > threshold:
            return False

    for key in CATEGORICAL_RULES:
        wanted = rule.get(key)
        if wanted is None:
            continue

        actual = f.get(key)
        if key == "side":
            if wanted == "first":
                wanted = "home"
            if wanted == "second":
                wanted = "away"

        if actual != wanted:
            return False

    return True


def evaluate_picks(picks):
    settled = [p for p in picks if p.get("_result_norm") in {"win", "loss", "push"}]
    wins = [p for p in settled if p.get("_result_norm") == "win"]
    losses = [p for p in settled if p.get("_result_norm") == "loss"]
    pushes = [p for p in settled if p.get("_result_norm") == "push"]

    profits = [p.get("_profit_flat", 0.0) for p in settled]
    total_profit = round(sum(profits), 4)
    stake_sum = len(settled) * FLAT_STAKE
    roi = round((total_profit / stake_sum) * 100, 2) if stake_sum else 0.0
    winrate = round((len(wins) / max(1, len(wins) + len(losses))) * 100, 2)

    odds_values = [safe_float(p.get("odds"), None) for p in settled]
    odds_values = [x for x in odds_values if x is not None]

    results = [p.get("_result_norm") for p in settled]

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
    dd_abs = abs(stats["max_drawdown"])

    score = (
        stats["profit"] * SCORE_WEIGHTS["profit"]
        + stats["roi"] * SCORE_WEIGHTS["roi"]
        + stats["winrate"] * SCORE_WEIGHTS["winrate"]
        + stats["avg_odds"] * SCORE_WEIGHTS["avg_odds"]
        + sample_bonus * SCORE_WEIGHTS["sample_bonus"]
        - dd_abs * SCORE_WEIGHTS["drawdown_penalty"]
    )

    return round(score, 6)


def clean_rule(rule):
    return {k: v for k, v in rule.items() if v is not None}


def generate_rule_candidates():
    keys = list(RULE_GRID.keys())
    cat_keys = list(CATEGORICAL_RULES.keys())

    # 1) Najprej osnovne kombinacije numeric pravil.
    # Namenoma ne delamo vseh brutalno velikih kombinacij naenkrat, ampak pametno po segmentih,
    # da ne eksplodira število kombinacij.
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
        values = [RULE_GRID[k] for k in block]

        for combo in itertools.product(*values):
            block_rule = {k: v for k, v in zip(block, combo)}
            if not valid_rule_combo(block_rule):
                continue

            for base in base_rules:
                merged = dict(base)
                merged.update(block_rule)
                if valid_rule_combo(merged):
                    new_rules.append(merged)

        # Ohranimo tudi praznejše variante, ampak omejimo število.
        base_rules = new_rules

    # 2) Dodamo kategorične reze.
    all_rules = []

    cat_values = [CATEGORICAL_RULES[k] for k in cat_keys]
    for base in base_rules:
        for combo in itertools.product(*cat_values):
            rule = dict(base)
            rule.update({k: v for k, v in zip(cat_keys, combo)})

            if not valid_rule_combo(rule):
                continue

            cleaned = clean_rule(rule)

            # Ne dovolimo preveč kompleksnih pravil, ker je to pogosto overfit.
            if len(cleaned) <= 8:
                all_rules.append(cleaned)

    # Deduplicate
    seen = set()
    unique = []
    for r in all_rules:
        key = json.dumps(r, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def split_train_test(picks, test_ratio=0.25):
    ordered = sorted(
        picks,
        key=lambda p: (
            str(p.get("date") or ""),
            str(p.get("time") or ""),
            str(p.get("created_at") or ""),
            str(p.get("pick_id") or ""),
        )
    )

    if len(ordered) < 4:
        return ordered, []

    cut = int(len(ordered) * (1 - test_ratio))
    cut = max(1, min(cut, len(ordered) - 1))
    return ordered[:cut], ordered[cut:]


def breakdown(picks, field):
    groups = defaultdict(list)

    for p in picks:
        if field.startswith("_features."):
            key = field.split(".", 1)[1]
            value = p.get("_features", {}).get(key)
        else:
            value = get_nested(p, field, None)

        if value is None or value == "":
            value = "unknown"

        groups[str(value)].append(p)

    rows = []
    for key, items in groups.items():
        stats = evaluate_picks(items)
        rows.append({
            "group": key,
            **stats,
        })

    rows.sort(key=lambda x: (x["profit"], x["roi"], x["picks"]), reverse=True)
    return rows


def numeric_ranges(picks, feature_key):
    values = []
    for p in picks:
        v = p.get("_features", {}).get(feature_key)
        if isinstance(v, (int, float)):
            values.append(v)

    if not values:
        return None

    values = sorted(values)
    n = len(values)

    def q(percent):
        idx = int(round((n - 1) * percent))
        return round(values[idx], 4)

    return {
        "min": round(values[0], 4),
        "p25": q(0.25),
        "median": q(0.50),
        "p75": q(0.75),
        "max": round(values[-1], 4),
        "avg": round(sum(values) / n, 4),
    }


def format_rule(rule):
    if not rule:
        return "No filters"

    parts = []
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

    for k, v in rule.items():
        parts.append(f"{labels.get(k, k)} {v}")

    return "; ".join(parts)


def make_markdown_report(
    generated_at,
    source_count,
    settled_count,
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
    lines.append(f"- Minimum sample per valid strategy: **{MIN_PICKS} picks**")
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
        return "\n".join(lines) + "\n"

    lines.append("## Best strategy found")
    lines.append("")
    lines.append(f"**Score:** {best['score']}")
    lines.append("")
    lines.append(f"**Rules:** {format_rule(best['rules'])}")
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
    lines.append("Use this as a filter layer on top of the existing tennis home/away machine:")
    lines.append("")
    lines.append(f"```json\n{json.dumps(best['rules'], indent=2, ensure_ascii=False)}\n```")
    lines.append("")
    lines.append("Stake suggestion:")
    lines.append("")
    lines.append("- Base test in this report uses **flat 1u** per pick.")
    lines.append("- Conservative live version: **0.5u flat** until at least 50 new forward-test picks.")
    lines.append("- Aggressive only after forward confirmation: **1u flat**, no martingale.")
    lines.append("")
    lines.append("Risk warning: this optimizer is historical. The important number is the **Test 25%** and then forward tracking, not only the full-sample result.")
    lines.append("")

    lines.append("## Top strategies")
    lines.append("")
    lines.append("| Rank | Score | Picks | Winrate | Profit | ROI | Max DD | Rules |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---|")
    for i, row in enumerate(top_rows[:25], start=1):
        s = row["stats"]
        lines.append(
            f"| {i} | {row['score']} | {s['picks']} | {s['winrate']}% | "
            f"{s['profit']}u | {s['roi']}% | {s['max_drawdown']}u | {format_rule(row['rules'])} |"
        )
    lines.append("")

    lines.append("## Best strategy selected picks sample")
    lines.append("")
    lines.append("| Date | Match | Bet | Result | Odds | Profit |")
    lines.append("|---|---|---|---:|---:|---:|")
    for p in best_picks[:40]:
        lines.append(
            f"| {p.get('date','')} {p.get('time','')} | {p.get('match','')} | {p.get('bet') or p.get('selection') or p.get('side','')} | "
            f"{p.get('_result_norm')} | {p.get('odds','')} | {p.get('_profit_flat')} |"
        )
    lines.append("")

    lines.append("## Feature ranges inside best strategy")
    lines.append("")
    lines.append("| Feature | Min | P25 | Median | P75 | Max | Avg |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for feature, data in ranges.items():
        if data:
            lines.append(
                f"| {feature} | {data['min']} | {data['p25']} | {data['median']} | {data['p75']} | {data['max']} | {data['avg']} |"
            )
    lines.append("")

    lines.append("## Breakdown of best strategy")
    lines.append("")
    for title, rows in breakdowns.items():
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for r in rows[:15]:
            lines.append(
                f"| {r['group']} | {r['picks']} | {r['winrate']}% | {r['profit']}u | "
                f"{r['roi']}% | {r['avg_odds']} | {r['max_drawdown']}u |"
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

    enriched = [enrich_pick(p) for p in raw if isinstance(p, dict)]
    settled = [p for p in enriched if is_settled(p)]

    all_stats = evaluate_picks(settled)

    candidates = generate_rule_candidates()

    evaluated = []
    for rule in candidates:
        selected = [p for p in settled if passes_rule(p, rule)]
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
        key=lambda x: (
            x["score"],
            x["stats"]["profit"],
            x["stats"]["roi"],
            x["stats"]["picks"],
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
        best_picks = [p for p in settled if passes_rule(p, best["rules"])]
        train, test = split_train_test(best_picks)
        train_stats = evaluate_picks(train)
        test_stats = evaluate_picks(test)

        breakdown_fields = {
            "By side": "_features.side",
            "By gender": "_features.gender",
            "By tour level": "_features.tour_level",
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

    # Za JSON output odstranimo interne težke feature objekte iz pickov, ampak pustimo profit/result.
    def public_pick(p):
        x = dict(p)
        x.pop("_features", None)
        return x

    summary = {
        "generated_at": generated_at,
        "source_file": RESULTS_FILE,
        "source_count": len(raw),
        "settled_count": len(settled),
        "min_picks": MIN_PICKS,
        "baseline": all_stats,
        "best": best,
        "train_75_stats": train_stats,
        "test_25_stats": test_stats,
        "output_dir": OUTPUT_DIR,
    }

    save_json(SUMMARY_FILE, summary)
    save_json(BEST_RULES_FILE, best["rules"] if best else {})
    save_json(TABLE_FILE, top_rows)
    save_json(PICKS_FILE, [public_pick(p) for p in best_picks])

    debug = {
        "generated_at": generated_at,
        "candidate_rules_tested": len(candidates),
        "valid_rules_over_min_sample": len(evaluated),
        "min_picks": MIN_PICKS,
        "score_weights": SCORE_WEIGHTS,
        "rule_grid": RULE_GRID,
        "categorical_rules": CATEGORICAL_RULES,
        "missing_or_pending_count": len(enriched) - len(settled),
    }
    save_json(DEBUG_FILE, debug)

    report = make_markdown_report(
        generated_at=generated_at,
        source_count=len(raw),
        settled_count=len(settled),
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

    if best:
        print("")
        print("BEST RULES:")
        print(json.dumps(best["rules"], indent=2, ensure_ascii=False))
        print("")
        print("FULL:")
        print(best["stats"])
        print("TRAIN 75%:")
        print(train_stats)
        print("TEST 25%:")
        print(test_stats)
    else:
        print("No valid strategy found. Try lowering MIN_PICKS.")

    print("")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

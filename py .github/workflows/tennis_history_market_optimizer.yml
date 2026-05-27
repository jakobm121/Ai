import os
import json
import math
import itertools
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter

TZ_NAME = "Europe/Ljubljana"

PROBE_DIR = os.getenv("PROBE_DIR", "jure_probe")
DATASET_FILE = os.getenv("DATASET_FILE", f"{PROBE_DIR}/history_betting_dataset.json")

OUTPUT_DIR = os.getenv("HISTORY_OPTIMIZER_DIR", PROBE_DIR)

REPORT_FILE = f"{OUTPUT_DIR}/history_market_optimizer_report.md"
BEST_RULES_FILE = f"{OUTPUT_DIR}/history_market_best_rules.json"
TABLE_FILE = f"{OUTPUT_DIR}/history_market_optimizer_table.json"
PICKS_FILE = f"{OUTPUT_DIR}/history_market_optimizer_picks.json"
SUMMARY_FILE = f"{OUTPUT_DIR}/history_market_optimizer_summary.json"
DEBUG_FILE = f"{OUTPUT_DIR}/history_market_optimizer_debug.json"

MIN_ROWS = int(os.getenv("MIN_ROWS", "30"))
TOP_N = int(os.getenv("TOP_N", "100"))

FLAT_STAKE = 1.0

# Scoring: profit + ROI + winrate, with penalties for drawdown and tiny samples.
SCORE_WEIGHTS = {
    "profit": 1.00,
    "roi": 0.35,
    "winrate": 0.12,
    "avg_odds": 0.08,
    "drawdown_penalty": 0.45,
    "sample_bonus": 0.10,
}

# Focused grid. Dataset is still small, so don't overfit too hard.
RULE_GRID = {
    "odds_min": [None, 1.30, 1.50, 1.70, 1.75, 1.85, 2.00, 2.25, 2.50, 3.00],
    "odds_max": [None, 1.80, 2.00, 2.20, 2.50, 3.00, 4.00, 6.00],
    "median_odds_min": [None, 1.50, 1.70, 1.85, 2.00, 2.25, 2.50],
    "median_odds_max": [None, 2.00, 2.25, 2.50, 3.00, 4.00, 6.00],
    "bookmakers_min": [None, 1, 2, 3, 4, 5],
    "total_games_min": [None, 16, 18, 20, 22, 24],
    "total_games_max": [None, 20, 22, 24, 26, 28],
}

CATEGORICAL_RULES = {
    "market": [
        None,
        "Home/Away",
        "Home/Away (1st Set)",
        "Home/Away (2nd Set)",
        "Odd/Even",
        "Odd/Even (1st Set)",
        "Set Betting",
        "Set / Match",
        "Number of sets",
    ],
    "selection": [
        None,
        "Home",
        "Away",
        "Odd",
        "Even",
        "2",
        "3",
        "2:0",
        "2:1",
        "0:2",
        "1:2",
        "1/1",
        "1/2",
        "2/1",
        "2/2",
    ],
    "tour_level": [None, "atp", "wta", "challenger", "itf"],
    "gender": [None, "men", "women"],
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
    return r


def is_settled(row):
    return normalize_result(row.get("result")) in {"win", "loss", "push"}


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


def profit_flat(row):
    result = normalize_result(row.get("result"))
    odds = safe_float(row.get("odds"), None)

    if result == "win":
        return round((odds or 1.0) - 1.0, 4)
    if result == "loss":
        return -1.0
    return 0.0


def enrich(row):
    r = dict(row)
    r["_result_norm"] = normalize_result(row.get("result"))
    r["_profit_flat"] = profit_flat(row)

    r["_features"] = {
        "market": row.get("market"),
        "selection": str(row.get("selection") or ""),
        "tour_level": normalize_text(row.get("tour_level")) or None,
        "gender": normalize_text(row.get("gender")) or None,
        "odds": safe_float(row.get("odds"), None),
        "median_odds": safe_float(row.get("median_odds"), None),
        "avg_odds": safe_float(row.get("avg_odds"), None),
        "bookmakers": safe_int(row.get("bookmakers_used"), None),
        "total_games": safe_float(row.get("total_games"), None),
        "set_count": safe_int(row.get("set_count"), None),
    }

    return r


def valid_rule(rule):
    pairs = [
        ("odds_min", "odds_max"),
        ("median_odds_min", "median_odds_max"),
        ("total_games_min", "total_games_max"),
    ]

    for lo, hi in pairs:
        a = rule.get(lo)
        b = rule.get(hi)
        if a is not None and b is not None and a > b:
            return False

    return True


def passes_rule(row, rule):
    f = row.get("_features", {})

    numeric_checks = [
        ("odds_min", "odds", ">="),
        ("odds_max", "odds", "<="),
        ("median_odds_min", "median_odds", ">="),
        ("median_odds_max", "median_odds", "<="),
        ("bookmakers_min", "bookmakers", ">="),
        ("total_games_min", "total_games", ">="),
        ("total_games_max", "total_games", "<="),
    ]

    for rule_key, feature_key, op in numeric_checks:
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

        if key in {"tour_level", "gender"}:
            if normalize_text(actual) != normalize_text(wanted):
                return False
        else:
            if str(actual) != str(wanted):
                return False

    return True


def evaluate(rows):
    settled = [r for r in rows if r.get("_result_norm") in {"win", "loss", "push"}]
    wins = [r for r in settled if r.get("_result_norm") == "win"]
    losses = [r for r in settled if r.get("_result_norm") == "loss"]
    pushes = [r for r in settled if r.get("_result_norm") == "push"]

    profits = [safe_float(r.get("_profit_flat"), 0.0) or 0.0 for r in settled]
    profit = round(sum(profits), 4)
    stake = len(settled) * FLAT_STAKE
    roi = round((profit / stake) * 100, 2) if stake else 0.0
    winrate = round((len(wins) / max(1, len(wins) + len(losses))) * 100, 2)

    odds_values = [safe_float(r.get("odds"), None) for r in settled]
    odds_values = [x for x in odds_values if x is not None]

    result_seq = [r.get("_result_norm") for r in settled]

    return {
        "rows": len(settled),
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


def score_strategy(stats):
    if stats["rows"] < MIN_ROWS:
        return -999999

    sample_bonus = math.log(max(1, stats["rows"]))
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


def generate_rules():
    keys = list(RULE_GRID.keys())
    cat_keys = list(CATEGORICAL_RULES.keys())

    # To avoid exploding combinations, build in logical blocks.
    numeric_blocks = [
        ["odds_min", "odds_max"],
        ["median_odds_min", "median_odds_max"],
        ["bookmakers_min"],
        ["total_games_min", "total_games_max"],
    ]

    base_rules = [{}]

    for block in numeric_blocks:
        new_rules = []

        for combo in itertools.product(*[RULE_GRID[k] for k in block]):
            block_rule = {k: v for k, v in zip(block, combo)}
            if not valid_rule(block_rule):
                continue

            for base in base_rules:
                merged = dict(base)
                merged.update(block_rule)
                if valid_rule(merged):
                    new_rules.append(merged)

        base_rules = new_rules

    all_rules = []
    for base in base_rules:
        for combo in itertools.product(*[CATEGORICAL_RULES[k] for k in cat_keys]):
            rule = dict(base)
            rule.update({k: v for k, v in zip(cat_keys, combo)})

            if not valid_rule(rule):
                continue

            cleaned = clean_rule(rule)

            # Guardrail: too many filters on small data is overfit.
            if len(cleaned) <= 6:
                all_rules.append(cleaned)

    # Deduplicate.
    seen = set()
    unique = []
    for r in all_rules:
        key = json.dumps(r, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    return unique


def split_train_test(rows, test_ratio=0.25):
    ordered = sorted(
        rows,
        key=lambda r: (
            str(r.get("date") or ""),
            str(r.get("time") or ""),
            str(r.get("event_key") or ""),
            str(r.get("market") or ""),
            str(r.get("selection") or ""),
        ),
    )

    if len(ordered) < 4:
        return ordered, []

    cut = int(len(ordered) * (1 - test_ratio))
    cut = max(1, min(cut, len(ordered) - 1))
    return ordered[:cut], ordered[cut:]


def grouped_breakdown(rows, field):
    groups = defaultdict(list)
    for r in rows:
        if field.startswith("_features."):
            key = field.split(".", 1)[1]
            value = r.get("_features", {}).get(key)
        else:
            value = r.get(field)

        if value is None or value == "":
            value = "unknown"

        groups[str(value)].append(r)

    out = []
    for value, items in groups.items():
        out.append({"group": value, **evaluate(items)})

    out.sort(key=lambda x: (x["profit"], x["roi"], x["rows"]), reverse=True)
    return out


def format_rule(rule):
    if not rule:
        return "No filters"

    labels = {
        "market": "market =",
        "selection": "selection =",
        "tour_level": "tour =",
        "gender": "gender =",
        "odds_min": "odds ≥",
        "odds_max": "odds ≤",
        "median_odds_min": "median odds ≥",
        "median_odds_max": "median odds ≤",
        "bookmakers_min": "bookmakers ≥",
        "total_games_min": "total games ≥",
        "total_games_max": "total games ≤",
    }

    return "; ".join([f"{labels.get(k, k)} {v}" for k, v in rule.items()])


def compact_row(row):
    x = dict(row)
    x.pop("_features", None)
    return x


def make_report(generated_at, source_rows, baseline, best, top_rows, best_rows, train_stats, test_stats, breakdowns):
    lines = []
    lines.append("# Historical Market Optimizer Report")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Dataset rows loaded: **{source_rows}**")
    lines.append(f"- Minimum rows per valid strategy: **{MIN_ROWS}**")
    lines.append(f"- Top strategies saved: **{TOP_N}**")
    lines.append("")
    lines.append("## Dataset baseline")
    lines.append("")
    lines.append("| Rows | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {baseline['rows']} | {baseline['wins']} | {baseline['losses']} | {baseline['pushes']} | "
        f"{baseline['winrate']}% | {baseline['profit']}u | {baseline['roi']}% | "
        f"{baseline['avg_odds']} | {baseline['max_drawdown']}u |"
    )
    lines.append("")

    if not best:
        lines.append("## Best strategy")
        lines.append("")
        lines.append("No strategy passed the minimum row requirement.")
        return "\n".join(lines) + "\n"

    lines.append("## Best strategy found")
    lines.append("")
    lines.append(f"**Score:** {best['score']}")
    lines.append("")
    lines.append(f"**Rules:** {format_rule(best['rules'])}")
    lines.append("")
    lines.append("| Split | Rows | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for name, stats in [
        ("Full", best["stats"]),
        ("Train 75%", train_stats),
        ("Test 25%", test_stats),
    ]:
        lines.append(
            f"| {name} | {stats['rows']} | {stats['wins']} | {stats['losses']} | {stats['pushes']} | "
            f"{stats['winrate']}% | {stats['profit']}u | {stats['roi']}% | "
            f"{stats['avg_odds']} | {stats['max_drawdown']}u |"
        )

    lines.append("")
    lines.append("## Recommended tactic")
    lines.append("")
    lines.append("Use this only as a historical hypothesis. The next step is forward tracking.")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(best["rules"], indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("Suggested live stake while testing: **0.25u–0.5u flat** until at least 50 new forward-test rows.")
    lines.append("")

    lines.append("## Top strategies")
    lines.append("")
    lines.append("| Rank | Score | Rows | Winrate | Profit | ROI | Avg odds | Max DD | Rules |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    for i, row in enumerate(top_rows[:50], start=1):
        s = row["stats"]
        lines.append(
            f"| {i} | {row['score']} | {s['rows']} | {s['winrate']}% | "
            f"{s['profit']}u | {s['roi']}% | {s['avg_odds']} | {s['max_drawdown']}u | "
            f"{format_rule(row['rules'])} |"
        )

    lines.append("")
    lines.append("## Best strategy row sample")
    lines.append("")
    lines.append("| Date | Match | Market | Selection | Odds | Result | Profit |")
    lines.append("|---|---|---|---|---:|---|---:|")
    for r in best_rows[:60]:
        lines.append(
            f"| {r.get('date','')} | {r.get('match','')} | {r.get('market','')} | "
            f"{r.get('selection','')} | {r.get('odds','')} | {r.get('_result_norm','')} | {r.get('_profit_flat','')} |"
        )

    lines.append("")
    lines.append("## Breakdowns for best strategy")
    lines.append("")
    for title, rows in breakdowns.items():
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Group | Rows | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for r in rows[:25]:
            lines.append(
                f"| {r['group']} | {r['rows']} | {r['winrate']}% | {r['profit']}u | "
                f"{r['roi']}% | {r['avg_odds']} | {r['max_drawdown']}u |"
            )
        lines.append("")

    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append(f"- `{BEST_RULES_FILE}`")
    lines.append(f"- `{TABLE_FILE}`")
    lines.append(f"- `{PICKS_FILE}`")
    lines.append(f"- `{SUMMARY_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    ensure_dirs()

    raw = load_json(DATASET_FILE, [])
    rows = [enrich(r) for r in raw if isinstance(r, dict) and is_settled(r)]

    baseline = evaluate(rows)
    candidates = generate_rules()

    evaluated = []
    for rule in candidates:
        selected = [r for r in rows if passes_rule(r, rule)]
        if len(selected) < MIN_ROWS:
            continue

        stats = evaluate(selected)
        score = score_strategy(stats)

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
            x["stats"]["rows"],
        ),
        reverse=True,
    )

    top_rows = evaluated[:TOP_N]
    best = top_rows[0] if top_rows else None

    best_rows = []
    train_stats = evaluate([])
    test_stats = evaluate([])
    breakdowns = {}

    if best:
        best_rows = [r for r in rows if passes_rule(r, best["rules"])]
        train, test = split_train_test(best_rows)
        train_stats = evaluate(train)
        test_stats = evaluate(test)

        breakdowns = {
            "By market": grouped_breakdown(best_rows, "market"),
            "By selection": grouped_breakdown(best_rows, "selection"),
            "By tour level": grouped_breakdown(best_rows, "tour_level"),
            "By gender": grouped_breakdown(best_rows, "gender"),
            "By bookmaker": grouped_breakdown(best_rows, "best_bookmaker"),
            "By tournament": grouped_breakdown(best_rows, "tournament"),
        }

    generated_at = now_iso()

    summary = {
        "generated_at": generated_at,
        "dataset_file": DATASET_FILE,
        "dataset_rows_loaded": len(raw),
        "settled_rows_used": len(rows),
        "min_rows": MIN_ROWS,
        "top_n": TOP_N,
        "baseline": baseline,
        "best": best,
        "train_75_stats": train_stats,
        "test_25_stats": test_stats,
        "output_dir": OUTPUT_DIR,
    }

    debug = {
        "generated_at": generated_at,
        "dataset_file": DATASET_FILE,
        "candidate_rules_tested": len(candidates),
        "valid_rules_over_min_rows": len(evaluated),
        "score_weights": SCORE_WEIGHTS,
        "rule_grid": RULE_GRID,
        "categorical_rules": CATEGORICAL_RULES,
        "min_rows": MIN_ROWS,
    }

    report = make_report(
        generated_at=generated_at,
        source_rows=len(raw),
        baseline=baseline,
        best=best,
        top_rows=top_rows,
        best_rows=best_rows,
        train_stats=train_stats,
        test_stats=test_stats,
        breakdowns=breakdowns,
    )

    save_json(SUMMARY_FILE, summary)
    save_json(BEST_RULES_FILE, best["rules"] if best else {})
    save_json(TABLE_FILE, top_rows)
    save_json(PICKS_FILE, [compact_row(r) for r in best_rows])
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, report)

    print("")
    print("HISTORY MARKET OPTIMIZER DONE")
    print(f"dataset rows loaded: {len(raw)}")
    print(f"settled rows used: {len(rows)}")
    print(f"candidate rules tested: {len(candidates)}")
    print(f"valid rules over min rows: {len(evaluated)}")

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
        print("No valid strategy found. Try lowering MIN_ROWS.")

    print("")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

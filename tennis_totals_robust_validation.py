import json
import math
from itertools import combinations
from pathlib import Path
from datetime import datetime

RESULTS_FILE = Path("data/tennis_totals_results.json")
OUT_FILE = Path("data/tennis_totals_robust_validation_report.json")

SETTLED = {"win", "loss"}

TRAIN_RATIO = 0.70
MIN_TEST_PICKS = 10

AUTO_MIN_TRAIN_PICKS = 40
AUTO_MIN_TEST_PICKS = 10
AUTO_RULE_SIZE_MIN = 3
AUTO_RULE_SIZE_MAX = 5

WALK_TRAIN_START = 120
WALK_TEST_SIZE = 40
WALK_STEP = 40


def fnum(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def sval(x):
    return str(x or "").strip().lower()


def result(p):
    return sval(p.get("result"))


def profit(p, stake=1.0):
    r = result(p)
    odds = fnum(p.get("odds"))

    if r == "win":
        return stake * (odds - 1)

    if r == "loss":
        return -stake

    return 0.0


def parse_dt(p):
    raw = f"{p.get('date', '')} {p.get('time', '')}".strip()

    for fmt in [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
    ]:
        try:
            return datetime.strptime(raw, fmt)
        except Exception:
            pass

    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return datetime.min


def key_time(p):
    dt = parse_dt(p)
    return (
        dt,
        str(p.get("date", "")),
        str(p.get("time", "")),
        str(p.get("match", "")),
    )


def dedupe(items):
    best = {}

    for p in items:
        k = (
            p.get("fixture_id") or p.get("event_key") or p.get("match"),
            sval(p.get("side")),
            fnum(p.get("line")),
        )

        old = best.get(k)

        if old is None:
            best[k] = p
            continue

        score_new = (
            fnum(p.get("quality_score")),
            fnum(p.get("confidence")),
            fnum(p.get("edge")),
            fnum(p.get("odds")),
        )
        score_old = (
            fnum(old.get("quality_score")),
            fnum(old.get("confidence")),
            fnum(old.get("edge")),
            fnum(old.get("odds")),
        )

        if score_new > score_old:
            best[k] = p

    return list(best.values())


def summarize_rows(rows, stake=1.0):
    rows = [p for p in rows if result(p) in SETTLED]

    wins = sum(1 for p in rows if result(p) == "win")
    losses = sum(1 for p in rows if result(p) == "loss")

    staked = len(rows) * stake
    prof = sum(profit(p, stake) for p in rows)

    bank = 0.0
    peak = 0.0
    dd = 0.0
    streak = 0
    max_streak = 0

    for p in sorted(rows, key=key_time):
        bank += profit(p, stake)
        peak = max(peak, bank)
        dd = max(dd, peak - bank)

        if result(p) == "loss":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return {
        "picks": len(rows),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(rows) * 100, 2) if rows else 0,
        "staked": round(staked, 2),
        "profit": round(prof, 2),
        "roi": round(prof / staked * 100, 2) if staked else 0,
        "avg_odds": round(sum(fnum(p.get("odds")) for p in rows) / len(rows), 3) if rows else 0,
        "max_drawdown_units": round(dd, 2),
        "longest_loss_streak": max_streak,
    }


def summarize_variable_stake(rows, stake_func):
    selected = []

    for p in rows:
        if result(p) not in SETTLED:
            continue

        stake, tier = stake_func(p)

        if stake <= 0:
            continue

        selected.append((p, stake, tier))

    wins = sum(1 for p, _, _ in selected if result(p) == "win")
    losses = sum(1 for p, _, _ in selected if result(p) == "loss")

    staked = sum(stake for _, stake, _ in selected)
    prof = sum(profit(p, stake) for p, stake, _ in selected)

    bank = 0.0
    peak = 0.0
    dd = 0.0
    streak = 0
    max_streak = 0

    for p, stake, _ in sorted(selected, key=lambda x: key_time(x[0])):
        bank += profit(p, stake)
        peak = max(peak, bank)
        dd = max(dd, peak - bank)

        if result(p) == "loss":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    by_tier = {}

    for tier in sorted(set(t for _, _, t in selected)):
        tier_rows = [(p, stake) for p, stake, t in selected if t == tier]

        tier_staked = sum(stake for _, stake in tier_rows)
        tier_profit = sum(profit(p, stake) for p, stake in tier_rows)
        tier_wins = sum(1 for p, _ in tier_rows if result(p) == "win")
        tier_losses = sum(1 for p, _ in tier_rows if result(p) == "loss")

        by_tier[tier] = {
            "picks": len(tier_rows),
            "wins": tier_wins,
            "losses": tier_losses,
            "win_rate": round(tier_wins / len(tier_rows) * 100, 2) if tier_rows else 0,
            "staked": round(tier_staked, 2),
            "profit": round(tier_profit, 2),
            "roi": round(tier_profit / tier_staked * 100, 2) if tier_staked else 0,
            "avg_odds": round(sum(fnum(p.get("odds")) for p, _ in tier_rows) / len(tier_rows), 3) if tier_rows else 0,
        }

    return {
        "picks": len(selected),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(selected) * 100, 2) if selected else 0,
        "staked": round(staked, 2),
        "profit": round(prof, 2),
        "roi": round(prof / staked * 100, 2) if staked else 0,
        "avg_odds": round(sum(fnum(p.get("odds")) for p, _, _ in selected) / len(selected), 3) if selected else 0,
        "max_drawdown_units": round(dd, 2),
        "longest_loss_streak": max_streak,
        "by_tier": by_tier,
    }


def is_premium(p):
    side = sval(p.get("side"))
    conf = fnum(p.get("confidence"))
    books = fnum(p.get("bookmakers_used"))
    label = p.get("stake_label")

    books_not_6_7 = not (6 <= books < 8)

    return (
        side == "under"
        and conf >= 82
        and books_not_6_7
        and label == "Strong"
    )


def is_volume_b(p):
    line = fnum(p.get("line"))
    conf = fnum(p.get("confidence"))
    label = p.get("stake_label")

    return (
        line == 20.5
        and conf >= 82
        and label != "Top Rated"
    )


def stake_premium_only(p):
    if is_premium(p):
        return 1.0, "Premium"

    return 0.0, "No Pick"


def stake_premium_plus_volume_b(p):
    if is_premium(p):
        return 1.0, "Premium"

    if is_volume_b(p):
        return 0.25, "Volume B"

    return 0.0, "No Pick"


def base_filters():
    return [
        ("under", lambda p: sval(p.get("side")) == "under"),
        ("over", lambda p: sval(p.get("side")) == "over"),

        ("line_18.5_20.5", lambda p: 18.5 <= fnum(p.get("line")) <= 20.5),
        ("line_20.5_22.5", lambda p: 20.5 <= fnum(p.get("line")) <= 22.5),
        ("line_max_20.5", lambda p: fnum(p.get("line")) <= 20.5),
        ("line_max_21.5", lambda p: fnum(p.get("line")) <= 21.5),
        ("line_exact_20.5", lambda p: fnum(p.get("line")) == 20.5),
        ("line_exact_21.5", lambda p: fnum(p.get("line")) == 21.5),
        ("line_exact_22.5", lambda p: fnum(p.get("line")) == 22.5),

        ("odds_1.70_1.84", lambda p: 1.70 <= fnum(p.get("odds")) < 1.85),
        ("odds_1.85_1.99", lambda p: 1.85 <= fnum(p.get("odds")) < 2.00),
        ("odds_2.00_2.20", lambda p: 2.00 <= fnum(p.get("odds")) <= 2.20),
        ("odds_1.85_2.20", lambda p: 1.85 <= fnum(p.get("odds")) <= 2.20),

        ("edge_under_6.5", lambda p: fnum(p.get("edge")) < 0.065),
        ("edge_6.5_9.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.10),
        ("edge_10_11.9", lambda p: 0.10 <= fnum(p.get("edge")) < 0.12),
        ("edge_under_12", lambda p: fnum(p.get("edge")) < 0.12),

        ("conf_74_plus", lambda p: fnum(p.get("confidence")) >= 74),
        ("conf_82_plus", lambda p: fnum(p.get("confidence")) >= 82),
        ("conf_82_87.9", lambda p: 82 <= fnum(p.get("confidence")) < 88),
        ("conf_88_plus", lambda p: fnum(p.get("confidence")) >= 88),
        ("conf_not_76_81.9", lambda p: not (76 <= fnum(p.get("confidence")) < 82)),

        ("q_55_plus", lambda p: fnum(p.get("quality_score")) >= 55),
        ("q_78_plus", lambda p: fnum(p.get("quality_score")) >= 78),
        ("q_82_plus", lambda p: fnum(p.get("quality_score")) >= 82),
        ("q_86_plus", lambda p: fnum(p.get("quality_score")) >= 86),

        ("margin_under_1", lambda p: fnum(p.get("expected_margin")) < 1.0),
        ("margin_1.0_plus", lambda p: fnum(p.get("expected_margin")) >= 1.0),
        ("margin_1.5_plus", lambda p: fnum(p.get("expected_margin")) >= 1.5),
        ("margin_2.0_plus", lambda p: fnum(p.get("expected_margin")) >= 2.0),

        ("books_lt6", lambda p: fnum(p.get("bookmakers_used")) < 6),
        ("books_6_7", lambda p: 6 <= fnum(p.get("bookmakers_used")) < 8),
        ("books_not_6_7", lambda p: not (6 <= fnum(p.get("bookmakers_used")) < 8)),
        ("books_8plus", lambda p: fnum(p.get("bookmakers_used")) >= 8),

        ("no_top_rated", lambda p: p.get("stake_label") != "Top Rated"),
        ("strong_only", lambda p: p.get("stake_label") == "Strong"),
        ("standard_or_strong", lambda p: p.get("stake_label") in {"Standard", "Strong"}),

        ("atp", lambda p: sval(p.get("tour_level")) == "atp"),
        ("wta", lambda p: sval(p.get("tour_level")) == "wta"),
        ("challenger", lambda p: sval(p.get("tour_level")) == "challenger"),
        ("itf", lambda p: sval(p.get("tour_level")) == "itf"),
    ]


def has_conflict(names):
    names = set(names)

    conflict_groups = [
        {"under", "over"},
        {"books_lt6", "books_6_7", "books_8plus"},
        {"strong_only", "no_top_rated"},
        {"atp", "wta", "challenger", "itf"},
    ]

    for group in conflict_groups:
        if len(names & group) > 1:
            return True

    if "books_6_7" in names and "books_not_6_7" in names:
        return True

    if "conf_88_plus" in names and "conf_82_87.9" in names:
        return True

    if "line_exact_22.5" in names and "line_max_21.5" in names:
        return True

    if "line_exact_21.5" in names and "line_max_20.5" in names:
        return True

    return False


def mask_from_rows(rows):
    mask = 0
    for i in range(len(rows)):
        mask |= 1 << i
    return mask


def summarize_mask(rows, mask):
    selected = [rows[i] for i in range(len(rows)) if mask & (1 << i)]
    return summarize_rows(selected, stake=1.0)


def robust_score(s):
    if s["picks"] <= 0:
        return -999999

    return round(
        s["profit"]
        + s["roi"] * 0.25
        - s["max_drawdown_units"] * 2.0
        - s["longest_loss_streak"] * 1.5
        + math.log(max(s["picks"], 1)) * 2.0,
        4,
    )


def build_filter_masks(rows):
    filters = []

    for name, fn in base_filters():
        mask = 0

        for i, p in enumerate(rows):
            if fn(p):
                mask |= 1 << i

        filters.append((name, mask))

    return filters


def find_best_rules(rows, train_mask, min_train_picks=AUTO_MIN_TRAIN_PICKS, limit=50):
    filters = build_filter_masks(rows)
    seen_picksets = {}
    candidates = []

    generated = 0
    skipped_conflict = 0

    for size in range(AUTO_RULE_SIZE_MIN, AUTO_RULE_SIZE_MAX + 1):
        for combo in combinations(filters, size):
            names = [x[0] for x in combo]

            if has_conflict(names):
                skipped_conflict += 1
                continue

            mask = mask_from_rows(rows)

            for _, fmask in combo:
                mask &= fmask

            generated += 1

            train_selected_mask = mask & train_mask
            picks = train_selected_mask.bit_count()

            if picks < min_train_picks:
                continue

            s_train = summarize_mask(rows, train_selected_mask)

            if s_train["profit"] <= 0:
                continue

            rule_name = "rule_" + "__".join(names)
            score = robust_score(s_train)

            pickset_key = train_selected_mask

            existing = seen_picksets.get(pickset_key)

            candidate = {
                "name": rule_name,
                "mask": mask,
                "train": s_train,
                "score": score,
            }

            if existing is None or score > existing["score"]:
                seen_picksets[pickset_key] = candidate

    candidates = list(seen_picksets.values())
    candidates.sort(
        key=lambda x: (
            x["score"],
            x["train"]["profit"],
            x["train"]["roi"],
            x["train"]["picks"],
        ),
        reverse=True,
    )

    clean = []

    for c in candidates[:limit]:
        clean.append(c)

    meta = {
        "generated": generated,
        "skipped_conflict": skipped_conflict,
        "unique_candidate_picksets": len(candidates),
    }

    return clean, meta


def evaluate_train_test(rows):
    n = len(rows)
    split = int(n * TRAIN_RATIO)

    train_mask = 0
    test_mask = 0

    for i in range(n):
        if i < split:
            train_mask |= 1 << i
        else:
            test_mask |= 1 << i

    best_rules, meta = find_best_rules(rows, train_mask, AUTO_MIN_TRAIN_PICKS, limit=25)

    evaluated = []

    for c in best_rules:
        test_selected_mask = c["mask"] & test_mask
        s_test = summarize_mask(rows, test_selected_mask)

        evaluated.append({
            "name": c["name"],
            "score": c["score"],
            "train": c["train"],
            "test": s_test,
            "passed_test": (
                s_test["picks"] >= AUTO_MIN_TEST_PICKS
                and s_test["profit"] > 0
                and s_test["roi"] > 0
            ),
        })

    return {
        "split_index": split,
        "train_rows": split,
        "test_rows": n - split,
        "meta": meta,
        "best_train_rule": evaluated[0] if evaluated else None,
        "top_train_rules_tested": evaluated,
        "passed_test_count": sum(1 for x in evaluated if x["passed_test"]),
    }


def evaluate_walk_forward(rows):
    n = len(rows)
    results = []

    train_end = WALK_TRAIN_START

    while train_end + WALK_TEST_SIZE <= n:
        train_mask = 0
        test_mask = 0

        for i in range(n):
            if i < train_end:
                train_mask |= 1 << i
            elif train_end <= i < train_end + WALK_TEST_SIZE:
                test_mask |= 1 << i

        best_rules, meta = find_best_rules(rows, train_mask, AUTO_MIN_TRAIN_PICKS, limit=1)

        if best_rules:
            best = best_rules[0]
            test_summary = summarize_mask(rows, best["mask"] & test_mask)

            results.append({
                "train_start_index": 0,
                "train_end_index": train_end,
                "test_start_index": train_end,
                "test_end_index": train_end + WALK_TEST_SIZE,
                "selected_rule": best["name"],
                "train": best["train"],
                "test": test_summary,
                "passed": (
                    test_summary["picks"] >= MIN_TEST_PICKS
                    and test_summary["profit"] > 0
                    and test_summary["roi"] > 0
                ),
                "meta": meta,
            })

        train_end += WALK_STEP

    all_test_rows = []

    for r in results:
        # To je samo agregat selected test pickov čez walk-forward okna.
        # Ker imamo samo summary, ne rekonstruiramo posameznih pickov tukaj.
        pass

    return {
        "windows": results,
        "windows_count": len(results),
        "passed_windows": sum(1 for x in results if x["passed"]),
    }


def evaluate_fixed_strategies(rows):
    n = len(rows)
    split = int(n * TRAIN_RATIO)

    train_rows = rows[:split]
    test_rows = rows[split:]

    strategies = {
        "premium_only": stake_premium_only,
        "premium_plus_volume_b_025": stake_premium_plus_volume_b,
    }

    report = {}

    for name, stake_func in strategies.items():
        report[name] = {
            "overall": summarize_variable_stake(rows, stake_func),
            "train_70": summarize_variable_stake(train_rows, stake_func),
            "test_30": summarize_variable_stake(test_rows, stake_func),
            "blocks": evaluate_blocks(rows, stake_func),
        }

    return report


def evaluate_blocks(rows, stake_func):
    blocks = {}

    # 4 časovni bloki po vrstnem redu tekem
    n = len(rows)
    q = max(1, n // 4)

    for idx in range(4):
        start = idx * q
        end = (idx + 1) * q if idx < 3 else n
        block_rows = rows[start:end]
        blocks[f"time_block_{idx + 1}"] = summarize_variable_stake(block_rows, stake_func)

    # meseci, če so datumi lepo parsani
    months = {}

    for p in rows:
        dt = parse_dt(p)

        if dt == datetime.min:
            key = "unknown_month"
        else:
            key = dt.strftime("%Y-%m")

        months.setdefault(key, []).append(p)

    blocks["by_month"] = {
        month: summarize_variable_stake(month_rows, stake_func)
        for month, month_rows in sorted(months.items())
    }

    return blocks


def main():
    raw_all = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))

    raw_settled = [p for p in raw_all if result(p) in SETTLED]
    rows = dedupe(raw_settled)
    rows = sorted(rows, key=key_time)

    fixed = evaluate_fixed_strategies(rows)
    train_test_auto = evaluate_train_test(rows)
    walk_forward = evaluate_walk_forward(rows)

    report = {
        "raw_results": len(raw_all),
        "settled_results": len(raw_settled),
        "deduped_settled_results": len(rows),
        "fixed_strategies": fixed,
        "train_test_auto": train_test_auto,
        "walk_forward_auto": walk_forward,
        "notes": {
            "premium_rule": "UNDER + confidence >= 82 + bookmakers_used not 6-7 + stake_label Strong",
            "volume_b_rule": "line == 20.5 + confidence >= 82 + stake_label != Top Rated",
            "removed": ["Volume A", "Value"],
            "production_preference": "Use only rules that survive test_30 and walk_forward, not only best backtest ROI.",
        },
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Saved:", OUT_FILE)
    print("Raw:", len(raw_all))
    print("Settled:", len(raw_settled))
    print("Deduped settled:", len(rows))

    print("\n=== FIXED: PREMIUM ONLY ===")
    print(json.dumps(fixed["premium_only"]["overall"], indent=2, ensure_ascii=False))
    print("\nTrain 70:")
    print(json.dumps(fixed["premium_only"]["train_70"], indent=2, ensure_ascii=False))
    print("\nTest 30:")
    print(json.dumps(fixed["premium_only"]["test_30"], indent=2, ensure_ascii=False))

    print("\n=== FIXED: PREMIUM + VOLUME B 0.25 ===")
    print(json.dumps(fixed["premium_plus_volume_b_025"]["overall"], indent=2, ensure_ascii=False))
    print("\nTrain 70:")
    print(json.dumps(fixed["premium_plus_volume_b_025"]["train_70"], indent=2, ensure_ascii=False))
    print("\nTest 30:")
    print(json.dumps(fixed["premium_plus_volume_b_025"]["test_30"], indent=2, ensure_ascii=False))

    print("\n=== AUTO TRAIN/TEST ===")
    print(json.dumps(train_test_auto["best_train_rule"], indent=2, ensure_ascii=False))
    print("Passed test count:", train_test_auto["passed_test_count"])

    print("\n=== WALK FORWARD ===")
    print("Windows:", walk_forward["windows_count"])
    print("Passed:", walk_forward["passed_windows"])
    print(json.dumps(walk_forward["windows"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

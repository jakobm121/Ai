import json
from itertools import combinations
from pathlib import Path

RESULTS_FILE = Path("data/tennis_totals_results.json")
OUT_FILE = Path("data/tennis_totals_vs_aib_optimizer_report.json")

BASELINE_ROI = 30.0
BASELINE_MIN_PICKS = 40
MIN_PICKS = 25

SETTLED = {"win", "loss"}


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


def key_time(p):
    return f"{p.get('date','')} {p.get('time','')} {p.get('match','')}"


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


def summarize(items, stake=1.0):
    rows = [p for p in items if result(p) in SETTLED]

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


def summarize_variable_stake(items, stake_func):
    rows = []

    for p in items:
        if result(p) not in SETTLED:
            continue

        stake, tier = stake_func(p)

        if stake <= 0:
            continue

        rows.append((p, stake, tier))

    wins = sum(1 for p, _, _ in rows if result(p) == "win")
    losses = sum(1 for p, _, _ in rows if result(p) == "loss")
    staked = sum(stake for _, stake, _ in rows)
    prof = sum(profit(p, stake) for p, stake, _ in rows)

    bank = 0.0
    peak = 0.0
    dd = 0.0
    streak = 0
    max_streak = 0

    for p, stake, _ in sorted(rows, key=lambda x: key_time(x[0])):
        bank += profit(p, stake)
        peak = max(peak, bank)
        dd = max(dd, peak - bank)

        if result(p) == "loss":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    by_tier = {}

    for tier in sorted(set(t for _, _, t in rows)):
        tier_rows = [(p, stake) for p, stake, t in rows if t == tier]
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
        "picks": len(rows),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(rows) * 100, 2) if rows else 0,
        "staked": round(staked, 2),
        "profit": round(prof, 2),
        "roi": round(prof / staked * 100, 2) if staked else 0,
        "avg_odds": round(sum(fnum(p.get("odds")) for p, _, _ in rows) / len(rows), 3) if rows else 0,
        "max_drawdown_units": round(dd, 2),
        "longest_loss_streak": max_streak,
        "by_tier": by_tier,
    }


def optimized_stake(p):
    side = sval(p.get("side"))
    line = fnum(p.get("line"))
    odds = fnum(p.get("odds"))
    conf = fnum(p.get("confidence"))
    edge = fnum(p.get("edge"))
    q = fnum(p.get("quality_score"))
    books = fnum(p.get("bookmakers_used"))
    label = p.get("stake_label")

    books_not_6_7 = not (6 <= books < 8)

    # Premium: najbolj stabilen balanced segment iz reporta.
    if side == "under" and conf >= 82 and books_not_6_7 and label == "Strong":
        return 1.0, "Premium"

    # Value: top ROI cluster, ampak nižji stake zaradi manjšega vzorca.
    if (
        side == "under"
        and 0.10 <= edge < 0.12
        and conf >= 82
        and books_not_6_7
    ):
        return 0.75, "Value"

    # Volume A: širši profitabilen cluster.
    if (
        line <= 21.5
        and 2.00 <= odds <= 2.20
        and conf >= 82
        and q >= 78
        and books_not_6_7
        and label != "Top Rated"
    ):
        return 0.5, "Volume A"

    # Volume B: več pickov, manj agresivno.
    if (
        line == 20.5
        and conf >= 82
        and label != "Top Rated"
    ):
        return 0.35, "Volume B"

    return 0.0, "No Pick"


def simulate(name, items, rule, stake=1.0):
    selected = [p for p in items if result(p) in SETTLED and rule(p)]
    selected = dedupe(selected)

    s = summarize(selected, stake=stake)
    s["name"] = name
    s["stake"] = stake

    return s


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


def build_rules():
    filters = base_filters()

    # Hitrejša verzija:
    # 42C3 + 42C4 = približno 123k kombinacij.
    # Prejšnja verzija 3-6 filtrov je šla čez 6M kombinacij.
    for size in range(3, 5):
        for combo in combinations(filters, size):
            names = [x[0] for x in combo]
            fns = [x[1] for x in combo]

            # Preskoči očitne konflikte, da ne testira praznih/neuporabnih pravil.
            if has_conflict(names):
                continue

            name = "rule_" + "__".join(names)

            def rule(p, fns=fns):
                return all(fn(p) for fn in fns)

            yield name, rule


def has_conflict(names):
    names = set(names)

    # Side conflict
    if "under" in names and "over" in names:
        return True

    # Tour conflict
    tours = {"atp", "wta", "challenger", "itf"}
    if len(names & tours) > 1:
        return True

    # Label conflict
    if "strong_only" in names and "no_top_rated" in names:
        # To ni nujno konflikt, ker Strong ni Top Rated.
        pass

    if "strong_only" in names and "standard_or_strong" in names:
        # Ni konflikt, ampak je redundantno.
        return True

    # Books conflict
    if "books_6_7" in names and "books_not_6_7" in names:
        return True

    if "books_lt6" in names and "books_8plus" in names:
        return True

    if "books_lt6" in names and "books_6_7" in names:
        return True

    if "books_8plus" in names and "books_6_7" in names:
        return True

    # Confidence conflict
    if "conf_88_plus" in names and "conf_82_87.9" in names:
        return True

    if "conf_82_87.9" in names and "conf_not_76_81.9" in names:
        # Ni konflikt, ker 82-87.9 je zunaj 76-81.9, ampak je redundantno.
        return True

    if "conf_88_plus" in names and "conf_not_76_81.9" in names:
        # Ni konflikt, ampak redundantno.
        return True

    # Edge conflict
    if "edge_under_6.5" in names and "edge_6.5_9.9" in names:
        return True

    if "edge_under_6.5" in names and "edge_10_11.9" in names:
        return True

    if "edge_6.5_9.9" in names and "edge_10_11.9" in names:
        return True

    if "edge_10_11.9" in names and "edge_under_12" in names:
        # Ni konflikt, ampak redundantno.
        return True

    # Odds conflict
    odds_groups = {
        "odds_1.70_1.84",
        "odds_1.85_1.99",
        "odds_2.00_2.20",
    }

    if len(names & odds_groups) > 1:
        return True

    if "odds_1.85_2.20" in names and ("odds_1.85_1.99" in names or "odds_2.00_2.20" in names):
        # Ni konflikt, ampak redundantno.
        return True

    if "odds_1.70_1.84" in names and "odds_1.85_2.20" in names:
        return True

    # Exact line conflicts
    exact_lines = {"line_exact_20.5", "line_exact_21.5", "line_exact_22.5"}
    if len(names & exact_lines) > 1:
        return True

    if "line_exact_22.5" in names and "line_max_21.5" in names:
        return True

    if "line_exact_22.5" in names and "line_max_20.5" in names:
        return True

    if "line_exact_21.5" in names and "line_max_20.5" in names:
        return True

    if "line_18.5_20.5" in names and "line_exact_21.5" in names:
        return True

    if "line_18.5_20.5" in names and "line_exact_22.5" in names:
        return True

    if "line_20.5_22.5" in names and "line_max_20.5" in names:
        # Presek je samo 20.5. Ni konflikt, ampak zelo ozko/redundantno.
        return True

    # Margin conflict
    if "margin_under_1" in names and "margin_1.0_plus" in names:
        return True

    if "margin_under_1" in names and "margin_1.5_plus" in names:
        return True

    if "margin_under_1" in names and "margin_2.0_plus" in names:
        return True

    return False


def main():
    raw_loaded = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    raw_settled = [p for p in raw_loaded if result(p) in SETTLED]
    raw = dedupe(raw_settled)

    tested = []
    better_than_aib = []

    rule_count = 0

    for name, rule in build_rules():
        rule_count += 1

        # Fixed stake testiramo samo z 1.0.
        # Pri 0.5/0.75/1.0 je ROI enak, samo profit in drawdown se linearno spremenita.
        s = simulate(name, raw, rule, stake=1.0)

        if s["picks"] < MIN_PICKS:
            continue

        tested.append(s)

        if s["roi"] > BASELINE_ROI and s["picks"] >= MIN_PICKS and s["profit"] > 0:
            better_than_aib.append(s)

    combined_optimized = summarize_variable_stake(raw, optimized_stake)
    combined_optimized["name"] = "combined_optimized_totals_staking"

    top_by_roi = sorted(
        tested,
        key=lambda x: (x["roi"], x["profit"], x["picks"]),
        reverse=True,
    )

    top_by_profit = sorted(
        tested,
        key=lambda x: (x["profit"], x["roi"], x["picks"]),
        reverse=True,
    )

    top_balanced = sorted(
        tested,
        key=lambda x: (
            x["profit"],
            x["roi"],
            -x["max_drawdown_units"],
            -x["longest_loss_streak"],
            x["picks"],
        ),
        reverse=True,
    )

    better = sorted(
        better_than_aib,
        key=lambda x: (x["roi"], x["profit"], x["picks"]),
        reverse=True,
    )

    # Posebej izpiši pravila z večjim volumnom.
    top_100_plus = [
        x for x in top_by_profit
        if x["picks"] >= 100
    ]

    top_150_plus = [
        x for x in top_by_profit
        if x["picks"] >= 150
    ]

    report = {
        "baseline": {
            "aib_roi": BASELINE_ROI,
            "baseline_min_picks": BASELINE_MIN_PICKS,
        },
        "raw_results": len(raw_loaded),
        "settled_results": len(raw_settled),
        "deduped_results": len(raw),
        "filters_used": len(base_filters()),
        "rules_generated_after_conflict_skip": rule_count,
        "tested_strategies": len(tested),
        "better_than_aib_count": len(better),
        "combined_optimized": combined_optimized,
        "better_than_aib": better[:100],
        "top_by_roi": top_by_roi[:100],
        "top_by_profit": top_by_profit[:100],
        "top_balanced": top_balanced[:100],
        "top_100_plus": top_100_plus[:100],
        "top_150_plus": top_150_plus[:100],
        "recommended": {
            "best_roi": top_by_roi[0] if top_by_roi else None,
            "best_profit": top_by_profit[0] if top_by_profit else None,
            "best_balanced": top_balanced[0] if top_balanced else None,
            "best_100_plus": top_100_plus[0] if top_100_plus else None,
            "best_150_plus": top_150_plus[0] if top_150_plus else None,
            "combined_optimized": combined_optimized,
        },
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Saved:", OUT_FILE)
    print("Raw:", len(raw_loaded))
    print("Settled:", len(raw_settled))
    print("Deduped:", len(raw))
    print("Filters:", len(base_filters()))
    print("Rules generated after conflict skip:", rule_count)
    print("Tested strategies:", len(tested))
    print("Better than AiB:", len(better))

    print("\nCombined optimized:")
    print(json.dumps(combined_optimized, indent=2, ensure_ascii=False))

    print("\nRecommended:")
    print(json.dumps(report["recommended"], indent=2, ensure_ascii=False))

    print("\nTop 150+ picks:")
    print(json.dumps(top_150_plus[:20], indent=2, ensure_ascii=False))

    print("\nTop by profit:")
    print(json.dumps(top_by_profit[:20], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

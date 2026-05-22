import json
from itertools import combinations
from pathlib import Path

RESULTS_FILE = Path("data/tennis_totals_results.json")
OUT_FILE = Path("data/tennis_totals_vs_aib_optimizer_report.json")

BASELINE_ROI = 30.0
BASELINE_MIN_PICKS = 40
MIN_PICKS = 25

SETTLED = {"win", "loss"}
STAKES = [0.5, 0.75, 1.0]

MIN_FILTERS = 3
MAX_FILTERS = 6


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
    return f"{p.get('date', '')} {p.get('time', '')} {p.get('match', '')}"


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


def build_filter_sets(items):
    filters = []

    def add(name, fn):
        idxs = {i for i, p in enumerate(items) if fn(p)}
        if len(idxs) >= MIN_PICKS:
            filters.append((name, idxs))

    add("under", lambda p: sval(p.get("side")) == "under")
    add("over", lambda p: sval(p.get("side")) == "over")

    for tour in ["atp", "wta", "challenger", "itf"]:
        add(tour, lambda p, tour=tour: sval(p.get("tour_level")) == tour)

    add("line_18.5_20.5", lambda p: 18.5 <= fnum(p.get("line")) <= 20.5)
    add("line_20.5_22.5", lambda p: 20.5 <= fnum(p.get("line")) <= 22.5)
    add("line_21.5_22.5", lambda p: 21.5 <= fnum(p.get("line")) <= 22.5)
    add("line_max_20.5", lambda p: fnum(p.get("line")) <= 20.5)
    add("line_max_21.5", lambda p: fnum(p.get("line")) <= 21.5)
    add("line_exact_20.5", lambda p: fnum(p.get("line")) == 20.5)
    add("line_exact_21.5", lambda p: fnum(p.get("line")) == 21.5)
    add("line_exact_22.5", lambda p: fnum(p.get("line")) == 22.5)

    add("odds_1.70_1.84", lambda p: 1.70 <= fnum(p.get("odds")) < 1.85)
    add("odds_1.85_1.99", lambda p: 1.85 <= fnum(p.get("odds")) < 2.00)
    add("odds_2.00_2.20", lambda p: 2.00 <= fnum(p.get("odds")) <= 2.20)
    add("odds_1.85_2.20", lambda p: 1.85 <= fnum(p.get("odds")) <= 2.20)
    add("odds_1.70_2.20", lambda p: 1.70 <= fnum(p.get("odds")) <= 2.20)

    add("edge_under_6.5", lambda p: fnum(p.get("edge")) < 0.065)
    add("edge_6.5_9.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.10)
    add("edge_10_11.9", lambda p: 0.10 <= fnum(p.get("edge")) < 0.12)
    add("edge_under_12", lambda p: fnum(p.get("edge")) < 0.12)
    add("edge_12plus", lambda p: fnum(p.get("edge")) >= 0.12)

    add("conf_74_plus", lambda p: fnum(p.get("confidence")) >= 74)
    add("conf_82_plus", lambda p: fnum(p.get("confidence")) >= 82)
    add("conf_82_87.9", lambda p: 82 <= fnum(p.get("confidence")) < 88)
    add("conf_86_plus", lambda p: fnum(p.get("confidence")) >= 86)
    add("conf_88_plus", lambda p: fnum(p.get("confidence")) >= 88)
    add("conf_not_76_81.9", lambda p: not (76 <= fnum(p.get("confidence")) < 82))

    add("q_55_plus", lambda p: fnum(p.get("quality_score")) >= 55)
    add("q_78_plus", lambda p: fnum(p.get("quality_score")) >= 78)
    add("q_82_plus", lambda p: fnum(p.get("quality_score")) >= 82)
    add("q_86_plus", lambda p: fnum(p.get("quality_score")) >= 86)

    add("margin_under_1", lambda p: fnum(p.get("expected_margin")) < 1.0)
    add("margin_1.0_plus", lambda p: fnum(p.get("expected_margin")) >= 1.0)
    add("margin_1.5_plus", lambda p: fnum(p.get("expected_margin")) >= 1.5)
    add("margin_2.0_plus", lambda p: fnum(p.get("expected_margin")) >= 2.0)
    add("margin_2.5_plus", lambda p: fnum(p.get("expected_margin")) >= 2.5)

    add("books_lt6", lambda p: fnum(p.get("bookmakers_used")) < 6)
    add("books_6_7", lambda p: 6 <= fnum(p.get("bookmakers_used")) < 8)
    add("books_not_6_7", lambda p: not (6 <= fnum(p.get("bookmakers_used")) < 8))
    add("books_8plus", lambda p: fnum(p.get("bookmakers_used")) >= 8)

    add("no_top_rated", lambda p: p.get("stake_label") != "Top Rated")
    add("strong_only", lambda p: p.get("stake_label") == "Strong")
    add("standard_or_strong", lambda p: p.get("stake_label") in {"Standard", "Strong"})

    return filters


def invalid_combo(names):
    groups = {
        "side": ["under", "over"],
        "tour": ["atp", "wta", "challenger", "itf"],
        "label": ["no_top_rated", "strong_only", "standard_or_strong"],
    }

    for values in groups.values():
        count = sum(1 for n in names if n in values)
        if count > 1:
            return True

    exact_lines = [n for n in names if n.startswith("line_exact_")]
    if len(exact_lines) > 1:
        return True

    exact_odds = [
        n for n in names
        if n.startswith("odds_")
    ]
    if len(exact_odds) > 1:
        return True

    edge_names = [n for n in names if n.startswith("edge_")]
    if len(edge_names) > 1:
        return True

    return False


def summarize_indexes(items, idxs, name, stake):
    selected = [items[i] for i in sorted(idxs)]
    s = summarize(selected, stake=stake)
    s["name"] = name
    s["stake"] = stake
    return s


def predefined(items):
    rules = []

    def add(name, fn):
        idxs = {i for i, p in enumerate(items) if fn(p)}
        rules.append((name, idxs))

    add(
        "aib_like_under_core",
        lambda p:
            sval(p.get("side")) == "under"
            and fnum(p.get("confidence")) >= 82
            and fnum(p.get("quality_score")) >= 55,
    )

    add(
        "under_atp_20.5_22.5",
        lambda p:
            sval(p.get("side")) == "under"
            and sval(p.get("tour_level")) == "atp"
            and 20.5 <= fnum(p.get("line")) <= 22.5,
    )

    add(
        "under_challenger_low_line",
        lambda p:
            sval(p.get("side")) == "under"
            and sval(p.get("tour_level")) == "challenger"
            and 18.5 <= fnum(p.get("line")) <= 20.5,
    )

    add(
        "over_wta_low_line",
        lambda p:
            sval(p.get("side")) == "over"
            and sval(p.get("tour_level")) == "wta"
            and 18.5 <= fnum(p.get("line")) <= 20.5,
    )

    add(
        "no_top_rated_under",
        lambda p:
            sval(p.get("side")) == "under"
            and p.get("stake_label") != "Top Rated",
    )

    out = []
    for name, idxs in rules:
        if len(idxs) < MIN_PICKS:
            continue
        for stake in STAKES:
            out.append(summarize_indexes(items, idxs, name, stake))

    return out


def main():
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"Missing {RESULTS_FILE}")

    raw = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    raw = [p for p in raw if result(p) in SETTLED]
    items = dedupe(raw)

    filters = build_filter_sets(items)

    tested = []
    better_than_aib = []

    seen = set()

    for r in range(MIN_FILTERS, MAX_FILTERS + 1):
        for combo in combinations(filters, r):
            names = [x[0] for x in combo]

            if invalid_combo(names):
                continue

            idxs = None
            for _, s in combo:
                idxs = set(s) if idxs is None else idxs & s

                if len(idxs) < MIN_PICKS:
                    break

            if not idxs or len(idxs) < MIN_PICKS:
                continue

            key = tuple(sorted(idxs))
            if key in seen:
                continue
            seen.add(key)

            name = "rule_" + "__".join(names)

            for stake in STAKES:
                summary = summarize_indexes(items, idxs, name, stake)
                tested.append(summary)

                if (
                    summary["roi"] > BASELINE_ROI
                    and summary["picks"] >= MIN_PICKS
                    and summary["profit"] > 0
                ):
                    better_than_aib.append(summary)

    tested.extend(predefined(items))

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

    better = sorted(
        better_than_aib,
        key=lambda x: (x["roi"], x["profit"], x["picks"]),
        reverse=True,
    )

    balanced_candidates = [
        x for x in tested
        if x["picks"] >= BASELINE_MIN_PICKS
        and x["profit"] > 0
        and x["roi"] > 0
        and x["max_drawdown_units"] <= 6
    ]

    top_balanced = sorted(
        balanced_candidates,
        key=lambda x: (
            x["roi"] * 0.45
            + x["profit"] * 1.8
            + min(x["picks"], 120) * 0.05
            - x["max_drawdown_units"] * 1.2
            - x["longest_loss_streak"] * 0.8
        ),
        reverse=True,
    )

    report = {
        "baseline": {
            "aib_roi": BASELINE_ROI,
            "baseline_min_picks": BASELINE_MIN_PICKS,
        },
        "raw_results": len(raw),
        "deduped_results": len(items),
        "filters_used": len(filters),
        "tested_strategies": len(tested),
        "better_than_aib_count": len(better),
        "better_than_aib": better[:100],
        "top_by_roi": top_by_roi[:100],
        "top_by_profit": top_by_profit[:100],
        "top_balanced": top_balanced[:100],
        "recommended": {
            "best_roi": top_by_roi[0] if top_by_roi else None,
            "best_profit": top_by_profit[0] if top_by_profit else None,
            "best_balanced": top_balanced[0] if top_balanced else None,
        },
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Saved:", OUT_FILE)
    print("Raw:", len(raw))
    print("Deduped:", len(items))
    print("Filters:", len(filters))
    print("Tested:", len(tested))
    print("Better than AiB:", len(better))

    print("\nRecommended:")
    print(json.dumps(report["recommended"], indent=2, ensure_ascii=False))

    print("\nTop better_than_aib:")
    print(json.dumps(better[:20], indent=2, ensure_ascii=False))

    print("\nTop by profit:")
    print(json.dumps(top_by_profit[:20], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

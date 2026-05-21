import json
from itertools import product
from pathlib import Path
from collections import defaultdict

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


def summarize(items, stake=1.0):
    rows = [p for p in items if result(p) in SETTLED]
    wins = sum(1 for p in rows if result(p) == "win")
    losses = sum(1 for p in rows if result(p) == "loss")
    staked = len(rows) * stake
    prof = sum(profit(p, stake) for p in rows)

    bank = 0
    peak = 0
    dd = 0
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


def simulate(name, items, rule, stake=1.0):
    selected = [p for p in items if result(p) in SETTLED and rule(p)]
    selected = dedupe(selected)
    s = summarize(selected, stake=stake)
    s["name"] = name
    s["stake"] = stake
    return s


def build_rules():
    sides = [
        ("any_side", lambda p: True),
        ("under", lambda p: sval(p.get("side")) == "under"),
        ("over", lambda p: sval(p.get("side")) == "over"),
    ]

    tours = [
        ("any_tour", lambda p: True),
        ("atp", lambda p: sval(p.get("tour_level")) == "atp"),
        ("wta", lambda p: sval(p.get("tour_level")) == "wta"),
        ("challenger", lambda p: sval(p.get("tour_level")) == "challenger"),
        ("itf", lambda p: sval(p.get("tour_level")) == "itf"),
    ]

    lines = [
        ("any_line", lambda p: True),
        ("line_18.5_20.5", lambda p: 18.5 <= fnum(p.get("line")) <= 20.5),
        ("line_20.5_22.5", lambda p: 20.5 <= fnum(p.get("line")) <= 22.5),
        ("line_21.5_22.5", lambda p: 21.5 <= fnum(p.get("line")) <= 22.5),
        ("line_max_20.5", lambda p: fnum(p.get("line")) <= 20.5),
        ("line_max_21.5", lambda p: fnum(p.get("line")) <= 21.5),
        ("line_exact_20.5", lambda p: fnum(p.get("line")) == 20.5),
        ("line_exact_21.5", lambda p: fnum(p.get("line")) == 21.5),
        ("line_exact_22.5", lambda p: fnum(p.get("line")) == 22.5),
    ]

    odds = [
        ("any_odds", lambda p: True),
        ("odds_1.70_1.84", lambda p: 1.70 <= fnum(p.get("odds")) < 1.85),
        ("odds_1.85_1.99", lambda p: 1.85 <= fnum(p.get("odds")) < 2.00),
        ("odds_2.00_2.20", lambda p: 2.00 <= fnum(p.get("odds")) <= 2.20),
        ("odds_1.85_2.20", lambda p: 1.85 <= fnum(p.get("odds")) <= 2.20),
    ]

    edges = [
        ("any_edge", lambda p: True),
        ("edge_under_6.5", lambda p: fnum(p.get("edge")) < 0.065),
        ("edge_6.5_9.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.10),
        ("edge_10_11.9", lambda p: 0.10 <= fnum(p.get("edge")) < 0.12),
        ("edge_under_12", lambda p: fnum(p.get("edge")) < 0.12),
        ("edge_no_12plus", lambda p: fnum(p.get("edge")) < 0.12),
    ]

    confs = [
        ("any_conf", lambda p: True),
        ("conf_74_plus", lambda p: fnum(p.get("confidence")) >= 74),
        ("conf_82_plus", lambda p: fnum(p.get("confidence")) >= 82),
        ("conf_82_87.9", lambda p: 82 <= fnum(p.get("confidence")) < 88),
        ("conf_88_plus", lambda p: fnum(p.get("confidence")) >= 88),
        ("conf_not_76_81.9", lambda p: not (76 <= fnum(p.get("confidence")) < 82)),
    ]

    qualities = [
        ("any_quality", lambda p: True),
        ("q_55_plus", lambda p: fnum(p.get("quality_score")) >= 55),
        ("q_78_plus", lambda p: fnum(p.get("quality_score")) >= 78),
        ("q_82_plus", lambda p: fnum(p.get("quality_score")) >= 82),
        ("q_86_plus", lambda p: fnum(p.get("quality_score")) >= 86),
    ]

    margins = [
        ("any_margin", lambda p: True),
        ("margin_under_1", lambda p: fnum(p.get("expected_margin")) < 1.0),
        ("margin_1.0_plus", lambda p: fnum(p.get("expected_margin")) >= 1.0),
        ("margin_1.5_plus", lambda p: fnum(p.get("expected_margin")) >= 1.5),
        ("margin_2.0_plus", lambda p: fnum(p.get("expected_margin")) >= 2.0),
        ("margin_2.5_plus", lambda p: fnum(p.get("expected_margin")) >= 2.5),
    ]

    books = [
        ("any_books", lambda p: True),
        ("books_lt6", lambda p: fnum(p.get("bookmakers_used")) < 6),
        ("books_6_7", lambda p: 6 <= fnum(p.get("bookmakers_used")) < 8),
        ("books_not_6_7", lambda p: not (6 <= fnum(p.get("bookmakers_used")) < 8)),
        ("books_8plus", lambda p: fnum(p.get("bookmakers_used")) >= 8),
    ]

    labels = [
        ("any_label", lambda p: True),
        ("no_top_rated", lambda p: p.get("stake_label") != "Top Rated"),
        ("strong_only", lambda p: p.get("stake_label") == "Strong"),
        ("standard_or_strong", lambda p: p.get("stake_label") in {"Standard", "Strong"}),
    ]

    for combo in product(sides, tours, lines, odds, edges, confs, qualities, margins, books, labels):
        names = [x[0] for x in combo]
        fns = [x[1] for x in combo]

        # skip totally generic
        useful = [n for n in names if not n.startswith("any_")]
        if len(useful) < 3:
            continue

        name = "rule_" + "__".join(useful)

        def rule(p, fns=fns):
            return all(fn(p) for fn in fns)

        yield name, rule


def main():
    raw = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    raw = [p for p in raw if result(p) in SETTLED]

    tested = []
    better_than_aib = []

    for name, rule in build_rules():
        for stake in [0.5, 0.75, 1.0]:
            s = simulate(name, raw, rule, stake=stake)

            if s["picks"] < MIN_PICKS:
                continue

            tested.append(s)

            if s["roi"] > BASELINE_ROI and s["picks"] >= MIN_PICKS and s["profit"] > 0:
                better_than_aib.append(s)

    top_by_roi = sorted(tested, key=lambda x: (x["roi"], x["profit"], x["picks"]), reverse=True)
    top_by_profit = sorted(tested, key=lambda x: (x["profit"], x["roi"], x["picks"]), reverse=True)
    better = sorted(better_than_aib, key=lambda x: (x["roi"], x["profit"], x["picks"]), reverse=True)

    report = {
        "baseline": {
            "aib_roi": BASELINE_ROI,
            "baseline_min_picks": BASELINE_MIN_PICKS,
        },
        "raw_results": len(raw),
        "tested_strategies": len(tested),
        "better_than_aib_count": len(better),
        "better_than_aib": better[:100],
        "top_by_roi": top_by_roi[:100],
        "top_by_profit": top_by_profit[:100],
    }

    OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Saved:", OUT_FILE)
    print("Tested:", len(tested))
    print("Better than AiB:", len(better))
    print("\nTop better_than_aib:")
    print(json.dumps(better[:20], indent=2, ensure_ascii=False))
    print("\nTop by profit:")
    print(json.dumps(top_by_profit[:20], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

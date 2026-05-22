import json
from itertools import product
from pathlib import Path

RESULTS_FILE = Path("data/tennis_results.json")
OUT_FILE = Path("data/tennis_strategy_optimizer_report.json")

SETTLED = {"win", "loss"}
MIN_PICKS = 12


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


def profit(p, stake):
    odds = fnum(p.get("odds"))
    if result(p) == "win":
        return stake * (odds - 1)
    if result(p) == "loss":
        return -stake
    return 0.0


def time_key(p):
    return f"{p.get('date','')} {p.get('time','')} {p.get('match','')}"


def dedupe(items):
    best = {}

    for p in items:
        key = (
            p.get("fixture_id") or p.get("event_key") or p.get("match"),
            p.get("bet") or p.get("pick") or p.get("selection"),
        )

        score = (
            fnum(p.get("quality_score")),
            fnum(p.get("confidence")),
            fnum(p.get("edge")),
            fnum(p.get("odds")),
        )

        if key not in best or score > best[key]["_score"]:
            x = dict(p)
            x["_score"] = score
            best[key] = x

    out = []
    for x in best.values():
        x.pop("_score", None)
        out.append(x)

    return out


def summarize(items, stake_fn):
    rows = []
    for p in items:
        stake, label = stake_fn(p)
        if stake <= 0:
            continue

        x = dict(p)
        x["_stake"] = stake
        x["_stake_label"] = label
        x["_profit"] = profit(p, stake)
        rows.append(x)

    rows = dedupe(rows)

    wins = sum(1 for p in rows if result(p) == "win")
    losses = sum(1 for p in rows if result(p) == "loss")
    staked = sum(p["_stake"] for p in rows)
    prof = sum(p["_profit"] for p in rows)

    bank = 0
    peak = 0
    max_dd = 0
    streak = 0
    max_streak = 0

    for p in sorted(rows, key=time_key):
        bank += p["_profit"]
        peak = max(peak, bank)
        max_dd = max(max_dd, peak - bank)

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
        "max_drawdown_units": round(max_dd, 2),
        "longest_loss_streak": max_streak,
    }


def fixed_stake(amount):
    def fn(p):
        if amount >= 1:
            return amount, "Top Rated"
        if amount >= 0.75:
            return amount, "Strong"
        return amount, "Standard"
    return fn


def calibrated_stake(p):
    odds = fnum(p.get("odds"))
    edge = fnum(p.get("edge"))
    conf = fnum(p.get("confidence"))
    tour = sval(p.get("tour_level"))
    fav = sval(p.get("favorite_type"))
    label = str(p.get("stake_label", ""))

    if tour == "challenger" and fav == "underdog" and 2.10 <= odds <= 2.39 and edge >= 0.12:
        return 1.0, "Top Rated"

    if tour == "wta" and fav == "favorite" and 1.70 <= odds <= 2.09 and label != "Top Rated":
        return 0.75, "Strong"

    if tour == "atp" and fav == "favorite" and 1.70 <= odds <= 2.09:
        return 0.75, "Strong"

    if tour == "itf" and fav == "favorite" and 1.70 <= odds < 1.90:
        return 0.5, "Standard"

    if conf >= 82 and 1.70 <= odds <= 2.09 and label != "Top Rated":
        return 0.5, "Standard"

    return 0.0, "No Pick"


def build_rules():
    sides = [
        ("any_fav", lambda p: True),
        ("favorite", lambda p: sval(p.get("favorite_type")) == "favorite"),
        ("underdog", lambda p: sval(p.get("favorite_type")) == "underdog"),
    ]

    tours = [
        ("any_tour", lambda p: True),
        ("atp", lambda p: sval(p.get("tour_level")) == "atp"),
        ("wta", lambda p: sval(p.get("tour_level")) == "wta"),
        ("challenger", lambda p: sval(p.get("tour_level")) == "challenger"),
        ("itf", lambda p: sval(p.get("tour_level")) == "itf"),
    ]

    odds_rules = [
        ("odds_1.70_1.89", lambda p: 1.70 <= fnum(p.get("odds")) < 1.90),
        ("odds_1.90_2.09", lambda p: 1.90 <= fnum(p.get("odds")) <= 2.09),
        ("odds_1.70_2.09", lambda p: 1.70 <= fnum(p.get("odds")) <= 2.09),
        ("odds_2.10_2.39", lambda p: 2.10 <= fnum(p.get("odds")) <= 2.39),
        ("odds_2.40_2.70", lambda p: 2.40 <= fnum(p.get("odds")) <= 2.70),
    ]

    edge_rules = [
        ("any_edge", lambda p: True),
        ("edge_6.5_7.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.08),
        ("edge_8_9.9", lambda p: 0.08 <= fnum(p.get("edge")) < 0.10),
        ("edge_10_11.9", lambda p: 0.10 <= fnum(p.get("edge")) < 0.12),
        ("edge_12plus", lambda p: fnum(p.get("edge")) >= 0.12),
        ("edge_under12", lambda p: fnum(p.get("edge")) < 0.12),
    ]

    conf_rules = [
        ("any_conf", lambda p: True),
        ("conf_82_85.9", lambda p: 82 <= fnum(p.get("confidence")) < 86),
        ("conf_86plus", lambda p: fnum(p.get("confidence")) >= 86),
        ("conf_under86", lambda p: fnum(p.get("confidence")) < 86),
    ]

    labels = [
        ("any_label", lambda p: True),
        ("no_top_rated", lambda p: str(p.get("stake_label", "")) != "Top Rated"),
        ("strong_only", lambda p: str(p.get("stake_label", "")) == "Strong"),
        ("standard_or_strong", lambda p: str(p.get("stake_label", "")) in {"Standard", "Strong"}),
    ]

    for combo in product(sides, tours, odds_rules, edge_rules, conf_rules, labels):
        names = [x[0] for x in combo]
        fns = [x[1] for x in combo]
        useful = [n for n in names if not n.startswith("any_")]

        if len(useful) < 3:
            continue

        name = "rule_" + "__".join(useful)

        def rule(p, fns=fns):
            return all(fn(p) for fn in fns)

        yield name, rule


def simulate(name, raw, rule, stake_fn):
    selected = [p for p in raw if result(p) in SETTLED and rule(p)]
    s = summarize(selected, stake_fn)
    s["name"] = name
    return s


def main():
    raw = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    raw = [p for p in raw if result(p) in SETTLED]

    baseline = summarize(raw, lambda p: (fnum(p.get("stake"), 1), str(p.get("stake_label", "Model"))))
    baseline["name"] = "raw_model_baseline"

    candidates = [baseline]

    predefined = [
        ("calibrated_moneyline_profile", lambda p: True, calibrated_stake),
        ("only_1.70_2.09_no_top_rated", lambda p: 1.70 <= fnum(p.get("odds")) <= 2.09 and str(p.get("stake_label", "")) != "Top Rated", fixed_stake(1.0)),
        ("challenger_dog_2.10_2.39_edge12", lambda p: sval(p.get("tour_level")) == "challenger" and sval(p.get("favorite_type")) == "underdog" and 2.10 <= fnum(p.get("odds")) <= 2.39 and fnum(p.get("edge")) >= 0.12, fixed_stake(1.0)),
        ("favorites_1.70_2.09", lambda p: sval(p.get("favorite_type")) == "favorite" and 1.70 <= fnum(p.get("odds")) <= 2.09, fixed_stake(0.75)),
    ]

    for name, rule, stake_fn in predefined:
        s = simulate(name, raw, rule, stake_fn)
        if s["picks"] >= MIN_PICKS:
            candidates.append(s)

    grid = []

    for name, rule in build_rules():
        for stake in [0.5, 0.75, 1.0]:
            s = simulate(name, raw, rule, fixed_stake(stake))
            if s["picks"] >= MIN_PICKS and s["profit"] > 0:
                s["stake"] = stake
                grid.append(s)

    top_by_roi = sorted(grid, key=lambda x: (x["roi"], x["profit"], x["picks"]), reverse=True)[:100]
    top_by_profit = sorted(grid, key=lambda x: (x["profit"], x["roi"], x["picks"]), reverse=True)[:100]
    balanced = sorted(
        grid,
        key=lambda x: (x["profit"] - x["max_drawdown_units"], x["roi"], x["picks"]),
        reverse=True,
    )[:100]

    report = {
        "raw_results": len(raw),
        "min_picks": MIN_PICKS,
        "baseline_and_predefined": sorted(candidates, key=lambda x: (x["roi"], x["profit"]), reverse=True),
        "top_by_roi": top_by_roi,
        "top_by_profit": top_by_profit,
        "top_balanced": balanced,
        "recommended": {
            "best_roi": top_by_roi[0] if top_by_roi else None,
            "best_profit": top_by_profit[0] if top_by_profit else None,
            "best_balanced": balanced[0] if balanced else None,
        },
    }

    OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Saved:", OUT_FILE)
    print(json.dumps(report["baseline_and_predefined"], indent=2, ensure_ascii=False))
    print("\nTop ROI:")
    print(json.dumps(top_by_roi[:20], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

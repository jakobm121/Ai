#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI77 Tennis Totals Rank Optimizer

Vzame zgodovinske picke iz tennis_totals_results.json, zgradi ranking formulo,
testira Top 50 / Top 100 / Top 150 in shrani report + best_formula.

Primer:
  python tennis_totals_rank_optimizer.py
  python tennis_totals_rank_optimizer.py --input data/tennis_totals_v2_wide_shadow_results.json --prefix wide_shadow_rank
"""

import argparse
import json
import random
from datetime import datetime, timezone, date
from pathlib import Path
from statistics import mean

WIN = {"win", "won", "w"}
LOSS = {"loss", "lost", "lose", "l"}
VOID = {"void", "push", "cancelled", "canceled", "refund"}
UNSETTLED = {"", "pending", "open", "unknown", "none", "null"}
TOP_CUTS = [50, 100, 150]
SAFE_STAKES = {"elite": 0.75, "premium": 0.50, "value": 0.25}
AGGR_STAKES = {"elite": 1.00, "premium": 0.75, "value": 0.50}


def fnum(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def sval(x):
    return str(x or "").strip().lower()


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def norm(v, lo, hi):
    if hi == lo:
        return 0.0
    return clamp((v - lo) / (hi - lo), 0.0, 1.0)


def nested_get(d, path, default=None):
    cur = d
    for part in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
    return cur if cur is not None else default


def result(p):
    return sval(p.get("result"))


def is_win(p):
    return result(p) in WIN


def is_loss(p):
    return result(p) in LOSS


def is_void(p):
    return result(p) in VOID


def is_settled(p):
    return is_win(p) or is_loss(p) or is_void(p)


def date_key(p):
    return (
        str(p.get("date") or ""),
        str(p.get("time") or ""),
        str(p.get("match") or ""),
        str(p.get("side") or ""),
        fnum(p.get("line")),
    )


def month_key(p):
    d = str(p.get("date") or "")
    return d[:7] if len(d) >= 7 else "unknown"


def week_key(p):
    d = str(p.get("date") or "")
    try:
        y, m, day = [int(x) for x in d[:10].split("-")]
        iso = date(y, m, day).isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    except Exception:
        return "unknown"


def profit_for_pick(p, stake):
    odds = fnum(p.get("odds"))
    if is_win(p):
        return stake * (odds - 1.0)
    if is_loss(p):
        return -stake
    return 0.0


def avg_pair(p, path):
    a = fnum(nested_get(p, ["first_form"] + path))
    b = fnum(nested_get(p, ["second_form"] + path))
    return (a + b) / 2.0


def min_pair(p, path):
    a = fnum(nested_get(p, ["first_form"] + path))
    b = fnum(nested_get(p, ["second_form"] + path))
    return min(a, b)


def extract_features(p):
    side = sval(p.get("side"))
    tour = sval(p.get("tour_level"))
    gender = sval(p.get("gender"))
    strength_gap = abs(fnum(p.get("first_strength_score")) - fnum(p.get("second_strength_score")))
    return {
        "edge": fnum(p.get("edge")),
        "confidence": fnum(p.get("confidence")),
        "quality": fnum(p.get("quality_score")),
        "odds": fnum(p.get("odds")),
        "line": fnum(p.get("line")),
        "bookmakers": fnum(p.get("bookmakers_used")),
        "expected_margin": fnum(p.get("expected_margin")),
        "abs_margin": abs(fnum(p.get("expected_margin"))),
        "market_gap": fnum(nested_get(p, ["market_info", "market_gap"])),
        "strength_gap": strength_gap,
        "h2h": fnum(p.get("h2h_matches")),
        "avg_three": avg_pair(p, ["last_10", "three_set_rate"]),
        "avg_close": avg_pair(p, ["last_10", "close_set_rate"]),
        "avg_over_21_5": avg_pair(p, ["last_10", "over_21_5_rate"]),
        "avg_total_games": avg_pair(p, ["last_10", "avg_total_games"]),
        "min_recent": min_pair(p, ["last_10", "matches"]),
        "side_over": 1.0 if side == "over" else 0.0,
        "side_under": 1.0 if side == "under" else 0.0,
        "tour_atp": 1.0 if tour == "atp" else 0.0,
        "tour_wta": 1.0 if tour == "wta" else 0.0,
        "tour_challenger": 1.0 if tour == "challenger" else 0.0,
        "tour_itf": 1.0 if tour == "itf" else 0.0,
        "gender_men": 1.0 if gender == "men" else 0.0,
        "gender_women": 1.0 if gender == "women" else 0.0,
        "qualification": 1.0 if bool(p.get("qualification")) else 0.0,
    }


def score_pick(f, formula):
    s = 0.0
    s += formula["w_confidence"] * norm(f["confidence"], 65, 95)
    s += formula["w_quality"] * norm(f["quality"], 60, 95)
    s += formula["w_edge"] * norm(f["edge"], 0.00, 0.16)
    s += formula["w_abs_margin"] * norm(f["abs_margin"], 0.0, 5.0)
    s += formula["w_bookmakers"] * norm(f["bookmakers"], 2, 10)
    s += formula["w_market_gap"] * norm(f["market_gap"], 0.0, 0.60)
    s += formula["w_avg_three"] * norm(f["avg_three"], 0.0, 0.70)
    s += formula["w_avg_close"] * norm(f["avg_close"], 0.0, 0.70)
    s += formula["w_min_recent"] * norm(f["min_recent"], 5, 14)
    s -= formula["p_h2h"] * norm(f["h2h"], 0, 5)
    s -= formula["p_strength_gap_high"] * norm(max(0.0, f["strength_gap"] - 30), 0, 35)
    s -= formula["p_odds_high"] * norm(max(0.0, f["odds"] - 2.15), 0, 0.45)
    s -= formula["p_low_line_under"] * (1.0 if f["side_under"] and f["line"] <= 19.5 else 0.0)
    s -= formula["p_qualification"] * f["qualification"]
    s += formula["b_over"] * f["side_over"]
    s += formula["b_under"] * f["side_under"]
    return round(s, 8)


def formula_space(samples=2500, seed=77):
    base = [
        {"w_confidence":22,"w_quality":22,"w_edge":16,"w_abs_margin":10,"w_bookmakers":7,"w_market_gap":12,"w_avg_three":5,"w_avg_close":4,"w_min_recent":4,"p_h2h":7,"p_strength_gap_high":7,"p_odds_high":5,"p_low_line_under":4,"p_qualification":3,"b_over":0,"b_under":0},
        {"w_confidence":28,"w_quality":18,"w_edge":12,"w_abs_margin":8,"w_bookmakers":6,"w_market_gap":14,"w_avg_three":5,"w_avg_close":5,"w_min_recent":4,"p_h2h":8,"p_strength_gap_high":8,"p_odds_high":4,"p_low_line_under":4,"p_qualification":3,"b_over":0,"b_under":1},
        {"w_confidence":18,"w_quality":26,"w_edge":16,"w_abs_margin":8,"w_bookmakers":8,"w_market_gap":12,"w_avg_three":5,"w_avg_close":5,"w_min_recent":4,"p_h2h":8,"p_strength_gap_high":8,"p_odds_high":5,"p_low_line_under":4,"p_qualification":3,"b_over":0,"b_under":1},
    ]
    rng = random.Random(seed)
    for _ in range(samples):
        f = {
            "w_confidence": rng.uniform(12, 34),
            "w_quality": rng.uniform(12, 34),
            "w_edge": rng.uniform(6, 24),
            "w_abs_margin": rng.uniform(2, 16),
            "w_bookmakers": rng.uniform(0, 12),
            "w_market_gap": rng.uniform(0, 20),
            "w_avg_three": rng.uniform(-4, 10),
            "w_avg_close": rng.uniform(-4, 10),
            "w_min_recent": rng.uniform(0, 8),
            "p_h2h": rng.uniform(0, 12),
            "p_strength_gap_high": rng.uniform(0, 12),
            "p_odds_high": rng.uniform(0, 10),
            "p_low_line_under": rng.uniform(0, 8),
            "p_qualification": rng.uniform(0, 8),
            "b_over": rng.uniform(-2, 2),
            "b_under": rng.uniform(-2, 2),
        }
        base.append({k: round(v, 5) for k, v in f.items()})
    return base


def rank_tier(rank, cuts=TOP_CUTS):
    if rank <= cuts[0]:
        return "elite"
    if rank <= cuts[1]:
        return "premium"
    if rank <= cuts[2]:
        return "value"
    return "reject"


def stake_for_rank(rank, cuts, stakes):
    tier = rank_tier(rank, cuts)
    return stakes.get(tier, 0.0)


def rank_rows(picks, formula):
    rows = []
    for p in picks:
        f = extract_features(p)
        rows.append({"score": score_pick(f, formula), "features": f, "pick": p})
    rows.sort(key=lambda r: (r["score"], fnum(r["pick"].get("confidence")), fnum(r["pick"].get("quality_score")), fnum(r["pick"].get("edge"))), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
        r["rank_tier"] = rank_tier(i)
    return rows


def summarize(rows, cuts, stakes, max_rank):
    selected = []
    for r in rows:
        if r["rank"] > max_rank:
            continue
        p = r["pick"]
        stake = 0.0 if is_void(p) else stake_for_rank(r["rank"], cuts, stakes)
        if stake <= 0 and not is_void(p):
            continue
        selected.append({**r, "stake": stake, "profit": profit_for_pick(p, stake)})

    settled = [x for x in selected if is_win(x["pick"]) or is_loss(x["pick"])]
    voids = [x for x in selected if is_void(x["pick"])]
    wins = sum(1 for x in settled if is_win(x["pick"]))
    losses = sum(1 for x in settled if is_loss(x["pick"]))
    staked = sum(x["stake"] for x in settled)
    prof = sum(x["profit"] for x in settled)

    bank = peak = 0.0
    max_dd = 0.0
    streak = longest = 0
    equity = []
    for x in sorted(settled, key=lambda y: date_key(y["pick"])):
        bank += x["profit"]
        peak = max(peak, bank)
        max_dd = min(max_dd, bank - peak)
        if is_loss(x["pick"]):
            streak += 1
            longest = max(longest, streak)
        elif is_win(x["pick"]):
            streak = 0
        equity.append(round(bank, 4))

    by_week, by_month, by_side = {}, {}, {}
    for x in settled:
        p = x["pick"]
        by_week[week_key(p)] = by_week.get(week_key(p), 0.0) + x["profit"]
        by_month[month_key(p)] = by_month.get(month_key(p), 0.0) + x["profit"]
        side = sval(p.get("side"))
        by_side[side] = by_side.get(side, 0.0) + x["profit"]

    weeks = list(by_week.values())
    months = list(by_month.values())

    by_tier = {}
    for tier in ["elite", "premium", "value"]:
        tr = [x for x in settled if x["rank_tier"] == tier]
        tw = sum(1 for x in tr if is_win(x["pick"]))
        tl = sum(1 for x in tr if is_loss(x["pick"]))
        ts = sum(x["stake"] for x in tr)
        tp = sum(x["profit"] for x in tr)
        by_tier[tier] = {
            "picks": len(tr), "wins": tw, "losses": tl,
            "winrate": round(tw / len(tr), 4) if tr else 0,
            "staked": round(ts, 4), "profit": round(tp, 4),
            "roi_on_actual_staked": round(tp / ts, 6) if ts else 0,
            "avg_odds": round(mean([fnum(x["pick"].get("odds")) for x in tr]), 4) if tr else 0,
        }

    return {
        "picks": len(settled) + len(voids),
        "settled_non_void": len(settled),
        "wins": wins, "losses": losses, "voids": len(voids),
        "winrate": round(wins / len(settled), 4) if settled else 0,
        "avg_odds": round(mean([fnum(x["pick"].get("odds")) for x in settled]), 4) if settled else 0,
        "avg_edge": round(mean([fnum(x["pick"].get("edge")) for x in settled]), 5) if settled else 0,
        "avg_confidence": round(mean([fnum(x["pick"].get("confidence")) for x in settled]), 3) if settled else 0,
        "avg_quality": round(mean([fnum(x["pick"].get("quality_score")) for x in settled]), 3) if settled else 0,
        "total_staked_units": round(staked, 4),
        "profit": round(prof, 4),
        "roi_on_actual_staked": round(prof / staked, 6) if staked else 0,
        "max_drawdown": round(max_dd, 4),
        "longest_losing_streak": longest,
        "profit_by_week": {k: round(v, 4) for k, v in sorted(by_week.items())},
        "profit_by_month": {k: round(v, 4) for k, v in sorted(by_month.items())},
        "profit_by_side": {k: round(v, 4) for k, v in sorted(by_side.items())},
        "weeks_positive_ratio": round(sum(1 for v in weeks if v > 0) / len(weeks), 4) if weeks else 0,
        "months_positive_ratio": round(sum(1 for v in months if v > 0) / len(months), 4) if months else 0,
        "equity_curve_last": equity[-10:],
        "by_tier": by_tier,
    }


def objective(summary_by_cut):
    score = 0.0
    for key, weight in [("top_50", 1.35), ("top_100", 1.05), ("top_150", 0.80)]:
        s = summary_by_cut[key]
        picks = fnum(s.get("settled_non_void"))
        roi = fnum(s.get("roi_on_actual_staked"))
        profit = fnum(s.get("profit"))
        dd = abs(fnum(s.get("max_drawdown")))
        wr = fnum(s.get("weeks_positive_ratio"))
        ls = fnum(s.get("longest_losing_streak"))
        score += weight * roi * 180
        score += weight * profit * 2.2
        score += weight * wr * 20
        score -= weight * dd * 1.5
        score -= weight * ls * 1.8
        if picks < 20:
            score -= 80
        elif picks < 35:
            score -= 30
    if fnum(summary_by_cut["top_150"].get("settled_non_void")) < 80:
        score -= 45
    return round(score, 6)


def evaluate(picks, formula, cuts, stakes):
    rows = rank_rows(picks, formula)
    summary_by_cut = {f"top_{cut}": summarize(rows, cuts, stakes, cut) for cut in cuts}
    return {"score": objective(summary_by_cut), "formula": formula, "summary_by_cut": summary_by_cut}


def load_picks(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("picks"), list):
        raw = raw["picks"]
    if not isinstance(raw, list):
        raise ValueError("Input mora biti list pickov ali objekt s ključem 'picks'.")
    settled, skipped = [], {"unsettled": 0, "bad_result": 0, "missing_odds": 0}
    for p in raw:
        if not isinstance(p, dict):
            continue
        r = result(p)
        if r in UNSETTLED:
            skipped["unsettled"] += 1
            continue
        if not is_settled(p):
            skipped["bad_result"] += 1
            continue
        if not is_void(p) and fnum(p.get("odds")) <= 1:
            skipped["missing_odds"] += 1
            continue
        settled.append(p)
    settled.sort(key=date_key)
    return settled, skipped


def write_md(report, path):
    best = report["best"]
    lines = [
        "# AI77 Tennis Totals Rank Optimizer Report", "",
        f"Generated UTC: `{report['generated_at_utc']}`",
        f"Input: `{report['input_file']}`",
        f"Settled picks used: **{report['settled_picks_used']}**", "",
        "## Best formula", "",
        f"Optimizer score: **{best['score']}**", "", "```json",
        json.dumps(best["formula"], indent=2, ensure_ascii=False), "```", "",
        "## Rank tier staking", "",
        "| Tier | Rank | Stake |", "|---|---:|---:|",
        f"| Elite | 1-{report['top_cuts'][0]} | {report['tier_stakes']['elite']}u |",
        f"| Premium | {report['top_cuts'][0]+1}-{report['top_cuts'][1]} | {report['tier_stakes']['premium']}u |",
        f"| Value | {report['top_cuts'][1]+1}-{report['top_cuts'][2]} | {report['tier_stakes']['value']}u |", "",
        "## Top cut performance", "",
        "| Cut | Picks | W-L-V | Winrate | Avg odds | Profit | ROI actual | Max DD | L streak | Weeks + |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cut in report["top_cuts"]:
        s = best["summary_by_cut"][f"top_{cut}"]
        lines.append(f"| Top {cut} | {s['picks']} | {s['wins']}-{s['losses']}-{s['voids']} | {s['winrate']*100:.2f}% | {s['avg_odds']:.3f} | {s['profit']:.2f}u | {s['roi_on_actual_staked']*100:.2f}% | {s['max_drawdown']:.2f}u | {s['longest_losing_streak']} | {s['weeks_positive_ratio']*100:.1f}% |")
    lines += ["", "## Tier breakdown for Top 150", "", "| Tier | Picks | W-L | Winrate | Profit | ROI actual | Avg odds |", "|---|---:|---:|---:|---:|---:|---:|"]
    by_tier = best["summary_by_cut"].get("top_150", {}).get("by_tier", {})
    for tier in ["elite", "premium", "value"]:
        s = by_tier.get(tier, {})
        lines.append(f"| {tier} | {s.get('picks',0)} | {s.get('wins',0)}-{s.get('losses',0)} | {fnum(s.get('winrate'))*100:.2f}% | {fnum(s.get('profit')):.2f}u | {fnum(s.get('roi_on_actual_staked'))*100:.2f}% | {fnum(s.get('avg_odds')):.3f} |")
    lines += ["", "## Notes", "", "- Ranking uporablja samo pred-tekma podatke.", "- Rezultat se uporablja samo za backtest.", "- Za uradno stran najprej testiraj ločeno 7–14 dni.", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/tennis_totals_results.json")
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--prefix", default="tennis_totals_rank")
    ap.add_argument("--samples", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=77)
    ap.add_argument("--staking", choices=["safe", "aggressive"], default="safe")
    args = ap.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stakes = SAFE_STAKES if args.staking == "safe" else AGGR_STAKES

    picks, skipped = load_picks(input_path)
    if len(picks) < 50:
        raise RuntimeError(f"Premalo settled pickov: {len(picks)}. Potrebujem vsaj 50.")

    best = None
    leaderboard = []
    for formula in formula_space(args.samples, args.seed):
        ev = evaluate(picks, formula, TOP_CUTS, stakes)
        leaderboard.append(ev)
        if best is None or ev["score"] > best["score"]:
            best = ev
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    ranked = rank_rows(picks, best["formula"])
    ranked_export = []
    for r in ranked[:TOP_CUTS[-1]]:
        p = r["pick"]
        stake = stake_for_rank(r["rank"], TOP_CUTS, stakes)
        ranked_export.append({
            "rank": r["rank"], "rank_tier": r["rank_tier"], "optimizer_score": r["score"],
            "stake": stake, "profit_backtest": round(profit_for_pick(p, stake), 4),
            "pick_id": p.get("pick_id"), "event_key": p.get("event_key"),
            "date": p.get("date"), "time": p.get("time"), "match": p.get("match"),
            "side": p.get("side"), "line": p.get("line"), "odds": p.get("odds"),
            "result": p.get("result"), "confidence": p.get("confidence"),
            "quality_score": p.get("quality_score"), "edge": p.get("edge"),
            "expected_margin": p.get("expected_margin"), "bookmakers_used": p.get("bookmakers_used"),
            "market_gap": nested_get(p, ["market_info", "market_gap"]),
            "strength_gap": abs(fnum(p.get("first_strength_score")) - fnum(p.get("second_strength_score"))),
            "h2h_matches": p.get("h2h_matches"),
        })

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(input_path),
        "settled_picks_used": len(picks),
        "skipped": skipped,
        "top_cuts": TOP_CUTS,
        "tier_stakes": stakes,
        "formula_candidates_tested": len(leaderboard),
        "best": best,
        "leaderboard_top_20": [{"rank": i+1, **x} for i, x in enumerate(leaderboard[:20])],
        "ranked_top_picks": ranked_export,
    }

    report_file = out_dir / f"{args.prefix}_optimizer_report.json"
    md_file = out_dir / f"{args.prefix}_optimizer_report.md"
    best_file = out_dir / f"{args.prefix}_best_formula.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    best_file.write_text(json.dumps({
        "generated_at_utc": report["generated_at_utc"],
        "input_file": report["input_file"],
        "top_cuts": TOP_CUTS,
        "tier_stakes": stakes,
        "formula": best["formula"],
        "summary_by_cut": best["summary_by_cut"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md(report, md_file)

    print("\nAI77 TENNIS TOTALS RANK OPTIMIZER DONE")
    print(f"Input settled picks: {len(picks)}")
    print(f"Formula candidates tested: {len(leaderboard)}")
    print(f"Best optimizer score: {best['score']}")
    for cut in TOP_CUTS:
        s = best["summary_by_cut"][f"top_{cut}"]
        print(f"Top {cut}: picks={s['picks']} W-L-V={s['wins']}-{s['losses']}-{s['voids']} profit={s['profit']}u ROI={round(s['roi_on_actual_staked']*100,2)}% DD={s['max_drawdown']}u")
    print(f"Saved {report_file}")
    print(f"Saved {md_file}")
    print(f"Saved {best_file}")


if __name__ == "__main__":
    main()

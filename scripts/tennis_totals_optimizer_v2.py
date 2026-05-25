import os
import json
import math
import random
import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from collections import defaultdict


DATA_DIR = "data"

INPUT_FILE = f"{DATA_DIR}/tennis_totals_results.json"

REPORT_FILE = f"{DATA_DIR}/tennis_totals_optimizer_v2_report.json"
TOP100_FILE = f"{DATA_DIR}/tennis_totals_ranked_top100.json"
TOP200_FILE = f"{DATA_DIR}/tennis_totals_ranked_top200.json"
TOP300_FILE = f"{DATA_DIR}/tennis_totals_ranked_top300.json"

OPTIMIZER_VERSION = "ai77_tennis_totals_optimizer_v2"

RANDOM_SEED = 77077

FORMULA_CANDIDATES = 40000
LEADERBOARD_KEEP = 300

TOP_CUTS = [100, 200, 300]

TIER_STAKES = {
    "elite": 0.75,     # top 1-100
    "premium": 0.50,   # top 101-200
    "value": 0.25,     # top 201-300
}

MIN_SETTLED_FOR_TEST = 80

VALID_WIN = {"win", "won"}
VALID_LOSS = {"loss", "lost"}
VALID_VOID = {"void", "push", "refund", "cancelled", "canceled"}


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def now_utc():
    return datetime.now(timezone.utc).isoformat()


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


def safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def safe_int(v, default=0):
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def normalize_result(v):
    r = str(v or "").strip().lower()

    if r in VALID_WIN:
        return "win"
    if r in VALID_LOSS:
        return "loss"
    if r in VALID_VOID:
        return "void"

    return "pending"


def get_market_gap(pick):
    market_info = pick.get("market_info") or {}
    return safe_float(market_info.get("market_gap"))


def get_strength_gap(pick):
    a = safe_float(pick.get("first_strength_score"))
    b = safe_float(pick.get("second_strength_score"))
    return abs(a - b)


def avg_player_stat(pick, key, window="last_10"):
    f1 = pick.get("first_form") or {}
    f2 = pick.get("second_form") or {}

    a = safe_float((f1.get(window) or {}).get(key))
    b = safe_float((f2.get(window) or {}).get(key))

    return (a + b) / 2


def min_recent_matches(pick):
    f1 = pick.get("first_form") or {}
    f2 = pick.get("second_form") or {}

    a = safe_int((f1.get("last_10") or {}).get("matches"))
    b = safe_int((f2.get("last_10") or {}).get("matches"))

    return min(a, b)


def settled_picks(raw):
    settled = []
    skipped = {
        "unsettled": 0,
        "bad_result": 0,
        "missing_odds": 0,
    }

    for p in raw:
        if not isinstance(p, dict):
            continue

        result = normalize_result(p.get("result"))

        if result == "pending":
            skipped["unsettled"] += 1
            continue

        odds = safe_float(p.get("odds"))
        if odds <= 1:
            skipped["missing_odds"] += 1
            continue

        q = deepcopy(p)
        q["result"] = result
        settled.append(q)

    return settled, skipped


def profit_for_pick(pick, stake):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"))

    if result == "win":
        return stake * (odds - 1)

    if result == "loss":
        return -stake

    return 0.0


def tier_for_rank(rank):
    if rank <= 100:
        return "elite"
    if rank <= 200:
        return "premium"
    return "value"


def stake_for_rank(rank):
    tier = tier_for_rank(rank)
    return TIER_STAKES[tier]


def max_drawdown(equity):
    peak = 0.0
    max_dd = 0.0

    for x in equity:
        peak = max(peak, x)
        dd = x - peak
        max_dd = min(max_dd, dd)

    return round(max_dd, 6)


def longest_losing_streak(picks):
    longest = 0
    current = 0

    for p in picks:
        result = normalize_result(p.get("result"))

        if result == "loss":
            current += 1
            longest = max(longest, current)
        elif result == "win":
            current = 0

    return longest


def week_key(date_s):
    try:
        d = datetime.fromisoformat(str(date_s)).date()
        iso = d.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    except Exception:
        return "unknown"


def month_key(date_s):
    try:
        d = datetime.fromisoformat(str(date_s)).date()
        return f"{d.year}-{d.month:02d}"
    except Exception:
        return "unknown"


def summarize_ranked(ranked, cut):
    selected = ranked[:cut]

    wins = 0
    losses = 0
    voids = 0
    staked = 0.0
    profit = 0.0

    equity = []
    running = 0.0

    profit_by_week = defaultdict(float)
    profit_by_month = defaultdict(float)
    profit_by_side = defaultdict(float)

    tier_stats = {
        "elite": {
            "picks": 0,
            "wins": 0,
            "losses": 0,
            "voids": 0,
            "staked": 0.0,
            "profit": 0.0,
            "odds_sum": 0.0,
        },
        "premium": {
            "picks": 0,
            "wins": 0,
            "losses": 0,
            "voids": 0,
            "staked": 0.0,
            "profit": 0.0,
            "odds_sum": 0.0,
        },
        "value": {
            "picks": 0,
            "wins": 0,
            "losses": 0,
            "voids": 0,
            "staked": 0.0,
            "profit": 0.0,
            "odds_sum": 0.0,
        },
    }

    odds_sum = 0.0
    edge_sum = 0.0
    confidence_sum = 0.0
    quality_sum = 0.0

    non_void_count = 0

    ordered = sorted(
        selected,
        key=lambda x: (
            x.get("date") or "",
            x.get("time") or "",
            x.get("match") or "",
            safe_int(x.get("rank")),
        ),
    )

    for p in ordered:
        rank = safe_int(p.get("rank"))
        stake = stake_for_rank(rank)
        result = normalize_result(p.get("result"))
        odds = safe_float(p.get("odds"))
        side = str(p.get("side") or "unknown").lower()

        tier = tier_for_rank(rank)
        tier_stats[tier]["picks"] += 1
        tier_stats[tier]["odds_sum"] += odds

        if result == "win":
            wins += 1
            non_void_count += 1
            staked += stake

            tier_stats[tier]["wins"] += 1
            tier_stats[tier]["staked"] += stake

        elif result == "loss":
            losses += 1
            non_void_count += 1
            staked += stake

            tier_stats[tier]["losses"] += 1
            tier_stats[tier]["staked"] += stake

        else:
            voids += 1
            tier_stats[tier]["voids"] += 1

        pick_profit = profit_for_pick(p, stake)
        profit += pick_profit
        running += pick_profit
        equity.append(round(running, 6))

        tier_stats[tier]["profit"] += pick_profit

        profit_by_week[week_key(p.get("date"))] += pick_profit
        profit_by_month[month_key(p.get("date"))] += pick_profit
        profit_by_side[side] += pick_profit

        odds_sum += odds
        edge_sum += safe_float(p.get("edge"))
        confidence_sum += safe_float(p.get("confidence"))
        quality_sum += safe_float(p.get("quality_score"))

    week_values = list(profit_by_week.values())
    month_values = list(profit_by_month.values())

    by_tier = {}

    for tier, s in tier_stats.items():
        tier_non_void = s["wins"] + s["losses"]
        tier_staked = s["staked"]

        by_tier[tier] = {
            "picks": s["picks"],
            "settled_non_void": tier_non_void,
            "wins": s["wins"],
            "losses": s["losses"],
            "voids": s["voids"],
            "winrate": round(s["wins"] / tier_non_void, 4) if tier_non_void else 0,
            "staked": round(tier_staked, 6),
            "profit": round(s["profit"], 6),
            "roi_on_actual_staked": round(s["profit"] / tier_staked, 6) if tier_staked else 0,
            "avg_odds": round(s["odds_sum"] / s["picks"], 4) if s["picks"] else 0,
        }

    return {
        "picks": len(selected),
        "settled_non_void": non_void_count,
        "wins": wins,
        "losses": losses,
        "voids": voids,
        "winrate": round(wins / non_void_count, 4) if non_void_count else 0,
        "avg_odds": round(odds_sum / len(selected), 4) if selected else 0,
        "avg_edge": round(edge_sum / len(selected), 5) if selected else 0,
        "avg_confidence": round(confidence_sum / len(selected), 4) if selected else 0,
        "avg_quality": round(quality_sum / len(selected), 4) if selected else 0,
        "total_staked_units": round(staked, 6),
        "profit": round(profit, 6),
        "roi_on_actual_staked": round(profit / staked, 6) if staked else 0,
        "max_drawdown": max_drawdown(equity),
        "longest_losing_streak": longest_losing_streak(ordered),
        "profit_by_week": {k: round(v, 6) for k, v in sorted(profit_by_week.items())},
        "profit_by_month": {k: round(v, 6) for k, v in sorted(profit_by_month.items())},
        "profit_by_side": {k: round(v, 6) for k, v in sorted(profit_by_side.items())},
        "weeks_positive_ratio": round(sum(1 for x in week_values if x > 0) / len(week_values), 4) if week_values else 0,
        "months_positive_ratio": round(sum(1 for x in month_values if x > 0) / len(month_values), 4) if month_values else 0,
        "equity_curve_last": equity[-10:],
        "by_tier": by_tier,
    }


def random_formula():
    return {
        "w_confidence": random.uniform(0, 35),
        "w_quality": random.uniform(0, 35),
        "w_edge": random.uniform(0, 35),
        "w_abs_margin": random.uniform(0, 18),
        "w_bookmakers": random.uniform(0, 14),
        "w_market_gap": random.uniform(-5, 25),
        "w_avg_three": random.uniform(-8, 12),
        "w_avg_close": random.uniform(-8, 10),
        "w_min_recent": random.uniform(0, 10),

        "p_h2h": random.uniform(0, 14),
        "p_strength_gap_high": random.uniform(-4, 14),
        "p_strength_gap_low": random.uniform(-4, 10),
        "p_odds_high": random.uniform(-3, 10),
        "p_low_line_under": random.uniform(-3, 8),
        "p_qualification": random.uniform(-5, 8),

        "b_over": random.uniform(-4, 4),
        "b_under": random.uniform(-4, 4),
    }


def formula_hash(formula):
    raw = json.dumps(formula, sort_keys=True)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def optimizer_score_pick(pick, formula):
    confidence = safe_float(pick.get("confidence"))
    quality = safe_float(pick.get("quality_score"))
    edge = safe_float(pick.get("edge"))
    abs_margin = abs(safe_float(pick.get("expected_margin")))
    bookmakers = safe_float(pick.get("bookmakers_used"))
    market_gap = get_market_gap(pick)

    avg_three = avg_player_stat(pick, "three_set_rate")
    avg_close = avg_player_stat(pick, "close_set_rate")
    min_recent = min_recent_matches(pick)

    h2h = safe_float(pick.get("h2h_matches"))
    strength_gap = get_strength_gap(pick)
    odds = safe_float(pick.get("odds"))
    line = safe_float(pick.get("line"))
    side = str(pick.get("side") or "").lower()
    qualification = bool(pick.get("qualification"))

    score = 0.0

    score += formula["w_confidence"] * (confidence / 100)
    score += formula["w_quality"] * (quality / 100)
    score += formula["w_edge"] * clamp(edge / 0.16, -1, 1)
    score += formula["w_abs_margin"] * clamp(abs_margin / 5.0, 0, 1)
    score += formula["w_bookmakers"] * clamp(bookmakers / 10.0, 0, 1)
    score += formula["w_market_gap"] * clamp(market_gap / 0.8, 0, 1)
    score += formula["w_avg_three"] * clamp(avg_three / 0.55, 0, 1)
    score += formula["w_avg_close"] * clamp(avg_close / 0.65, 0, 1)
    score += formula["w_min_recent"] * clamp(min_recent / 16.0, 0, 1)

    if h2h > 0:
        score += formula["p_h2h"]

    if strength_gap >= 25:
        score += formula["p_strength_gap_high"]

    if strength_gap <= 8:
        score += formula["p_strength_gap_low"]

    if odds >= 2.08:
        score += formula["p_odds_high"]

    if side == "under" and line <= 20.5:
        score += formula["p_low_line_under"]

    if qualification:
        score += formula["p_qualification"]

    if side == "over":
        score += formula["b_over"]

    if side == "under":
        score += formula["b_under"]

    return round(score, 8)


def rank_picks(picks, formula):
    ranked = []

    for p in picks:
        q = deepcopy(p)
        q["optimizer_score"] = optimizer_score_pick(q, formula)
        ranked.append(q)

    ranked.sort(
        key=lambda x: (
            safe_float(x.get("optimizer_score")),
            safe_float(x.get("quality_score")),
            safe_float(x.get("edge")),
            safe_float(x.get("confidence")),
        ),
        reverse=True,
    )

    for i, p in enumerate(ranked, start=1):
        p["rank"] = i
        p["rank_tier"] = tier_for_rank(i)
        p["stake"] = stake_for_rank(i)
        p["profit_backtest"] = round(profit_for_pick(p, p["stake"]), 6)

    return ranked


def score_cut(summary, cut):
    roi = safe_float(summary.get("roi_on_actual_staked"))
    winrate = safe_float(summary.get("winrate"))
    profit = safe_float(summary.get("profit"))
    max_dd = abs(safe_float(summary.get("max_drawdown")))
    lls = safe_float(summary.get("longest_losing_streak"))
    weeks_pos = safe_float(summary.get("weeks_positive_ratio"))
    non_void = safe_float(summary.get("settled_non_void"))

    score = 0.0

    score += roi * 260
    score += winrate * 70
    score += profit * 2.5
    score += weeks_pos * 25
    score -= max_dd * 4.5
    score -= lls * 2.2

    if non_void < cut * 0.82:
        score -= 100

    if roi < 0:
        score -= 80

    if winrate < 0.50:
        score -= 40

    return round(score, 6)


def global_formula_score(summary_by_cut):
    s100 = summary_by_cut["top_100"]
    s200 = summary_by_cut["top_200"]
    s300 = summary_by_cut["top_300"]

    score = 0.0

    score += score_cut(s100, 100) * 1.00
    score += score_cut(s200, 200) * 0.55
    score += score_cut(s300, 300) * 0.30

    if safe_float(s100.get("roi_on_actual_staked")) < 0.05:
        score -= 100

    if safe_float(s200.get("roi_on_actual_staked")) < 0:
        score -= 50

    if safe_float(s300.get("roi_on_actual_staked")) < -0.03:
        score -= 40

    return round(score, 6)


def compact_pick(p):
    return {
        "rank": p.get("rank"),
        "rank_tier": p.get("rank_tier"),
        "optimizer_score": p.get("optimizer_score"),
        "stake": p.get("stake"),
        "profit_backtest": p.get("profit_backtest"),

        "pick_id": p.get("pick_id"),
        "event_key": p.get("event_key"),
        "date": p.get("date"),
        "time": p.get("time"),
        "match": p.get("match"),
        "side": p.get("side"),
        "line": p.get("line"),
        "odds": p.get("odds"),
        "result": p.get("result"),

        "confidence": p.get("confidence"),
        "quality_score": p.get("quality_score"),
        "edge": p.get("edge"),
        "expected_margin": p.get("expected_margin"),
        "expected_total_games": p.get("expected_total_games"),
        "bookmakers_used": p.get("bookmakers_used"),

        "market_gap": get_market_gap(p),
        "strength_gap": get_strength_gap(p),
        "h2h_matches": p.get("h2h_matches"),
        "tournament": p.get("tournament"),
        "tour_level": p.get("tour_level"),
        "gender": p.get("gender"),
    }


def main():
    ensure_dirs()
    random.seed(RANDOM_SEED)

    raw = load_json(INPUT_FILE, [])
    if not isinstance(raw, list):
        raise RuntimeError(f"Input file must be a list: {INPUT_FILE}")

    picks, skipped = settled_picks(raw)

    if len(picks) < MIN_SETTLED_FOR_TEST:
        raise RuntimeError(f"Not enough settled picks. Found {len(picks)}, need {MIN_SETTLED_FOR_TEST}")

    leaderboard = []

    best_by_cut = {
        100: None,
        200: None,
        300: None,
    }

    for i in range(FORMULA_CANDIDATES):
        formula = random_formula()
        ranked = rank_picks(picks, formula)

        summary_by_cut = {}

        for cut in TOP_CUTS:
            summary_by_cut[f"top_{cut}"] = summarize_ranked(ranked, cut)

        global_score = global_formula_score(summary_by_cut)

        item = {
            "formula_id": formula_hash(formula),
            "score": global_score,
            "formula": formula,
            "summary_by_cut": summary_by_cut,
        }

        leaderboard.append(item)

        if len(leaderboard) > LEADERBOARD_KEEP * 4:
            leaderboard.sort(key=lambda x: safe_float(x.get("score")), reverse=True)
            leaderboard = leaderboard[:LEADERBOARD_KEEP]

        for cut in TOP_CUTS:
            cut_key = f"top_{cut}"
            cut_score = score_cut(summary_by_cut[cut_key], cut)

            candidate = {
                "cut": cut,
                "cut_score": cut_score,
                "formula_id": formula_hash(formula),
                "formula": formula,
                "summary": summary_by_cut[cut_key],
                "summary_by_cut": summary_by_cut,
                "ranked": ranked[:cut],
            }

            if best_by_cut[cut] is None or cut_score > best_by_cut[cut]["cut_score"]:
                best_by_cut[cut] = candidate

        if (i + 1) % 1000 == 0:
            print(f"tested={i + 1}/{FORMULA_CANDIDATES}")

    leaderboard.sort(key=lambda x: safe_float(x.get("score")), reverse=True)
    leaderboard = leaderboard[:LEADERBOARD_KEEP]

    best_outputs = {}

    for cut in TOP_CUTS:
        winner = best_by_cut[cut]
        ranked_compact = [compact_pick(p) for p in winner["ranked"]]

        best_outputs[f"top_{cut}"] = {
            "cut": cut,
            "cut_score": winner["cut_score"],
            "formula_id": winner["formula_id"],
            "formula": winner["formula"],
            "summary": winner["summary"],
            "summary_by_cut_for_same_formula": winner["summary_by_cut"],
            "ranked_picks": ranked_compact,
        }

        out_file = {
            100: TOP100_FILE,
            200: TOP200_FILE,
            300: TOP300_FILE,
        }[cut]

        save_json(out_file, {
            "generated_at_utc": now_utc(),
            "optimizer_version": OPTIMIZER_VERSION,
            "input_file": INPUT_FILE,
            "cut": cut,
            "formula_id": winner["formula_id"],
            "formula": winner["formula"],
            "summary": winner["summary"],
            "ranked_picks": ranked_compact,
        })

    report = {
        "generated_at_utc": now_utc(),
        "optimizer_version": OPTIMIZER_VERSION,
        "input_file": INPUT_FILE,
        "settled_picks_used": len(picks),
        "skipped": skipped,
        "formula_candidates_tested": FORMULA_CANDIDATES,
        "leaderboard_keep": LEADERBOARD_KEEP,
        "top_cuts": TOP_CUTS,
        "tier_stakes": TIER_STAKES,
        "best_by_cut": best_outputs,
        "leaderboard_top_300_formulas": [
            {
                "rank": idx,
                "formula_id": item["formula_id"],
                "score": item["score"],
                "formula": item["formula"],
                "summary_by_cut": item["summary_by_cut"],
            }
            for idx, item in enumerate(leaderboard, start=1)
        ],
    }

    save_json(REPORT_FILE, report)

    print("")
    print("TENNIS TOTALS OPTIMIZER V2 DONE")
    print(f"settled_picks_used={len(picks)}")
    print(f"formula_candidates_tested={FORMULA_CANDIDATES}")
    print(f"saved={REPORT_FILE}")
    print(f"saved={TOP100_FILE}")
    print(f"saved={TOP200_FILE}")
    print(f"saved={TOP300_FILE}")

    for cut in TOP_CUTS:
        b = best_by_cut[cut]
        s = b["summary"]
        print("")
        print(f"BEST TOP {cut}")
        print(f"cut_score={b['cut_score']}")
        print(f"picks={s['picks']} wins={s['wins']} losses={s['losses']} voids={s['voids']}")
        print(f"winrate={s['winrate']} roi={s['roi_on_actual_staked']} profit={s['profit']} dd={s['max_drawdown']}")


if __name__ == "__main__":
    main()

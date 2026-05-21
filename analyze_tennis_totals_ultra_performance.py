import json
from collections import defaultdict
from pathlib import Path

RESULTS_FILE = Path("data/tennis_totals_results.json")
OUT_FILE = Path("data/tennis_totals_ultra_performance_report.json")

SETTLED = {"win", "loss"}

def fnum(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def result(p):
    return str(p.get("result", "")).lower()

def profit(p):
    r = result(p)
    odds = fnum(p.get("odds"))
    stake = fnum(p.get("stake"), 1)
    if r == "win":
        return (odds - 1) * stake
    if r == "loss":
        return -stake
    return 0

def pick_key(p):
    return f"{p.get('date','')} {p.get('time','')} {p.get('match','')} {p.get('side','')} {p.get('line','')}"

def bucket_odds(p):
    o = fnum(p.get("odds"))
    if o < 1.70: return "<1.70"
    if o < 1.85: return "1.70-1.84"
    if o < 2.00: return "1.85-1.99"
    if o <= 2.20: return "2.00-2.20"
    return "2.20+"

def bucket_line(p):
    l = fnum(p.get("line"))
    if l <= 19.5: return "<=19.5"
    if l == 20.5: return "20.5"
    if l == 21.5: return "21.5"
    if l == 22.5: return "22.5"
    if l == 23.5: return "23.5"
    if l >= 24.5: return ">=24.5"
    return str(l)

def bucket_edge(p):
    e = fnum(p.get("edge"))
    if e < 0.065: return "<6.5%"
    if e < 0.08: return "6.5-7.9%"
    if e < 0.10: return "8-9.9%"
    if e < 0.12: return "10-11.9%"
    return "12%+"

def bucket_conf(p):
    c = fnum(p.get("confidence"))
    if c < 70: return "<70"
    if c < 76: return "70-75.9"
    if c < 82: return "76-81.9"
    if c < 88: return "82-87.9"
    return "88+"

def bucket_margin(p):
    m = fnum(p.get("expected_margin"))
    if m < 1.0: return "<1.0"
    if m < 1.5: return "1.0-1.49"
    if m < 2.0: return "1.5-1.99"
    if m < 2.5: return "2.0-2.49"
    if m < 3.0: return "2.5-2.99"
    return "3.0+"

def bucket_market_gap(p):
    g = fnum(p.get("market_gap"))
    if g < 0.08: return "<0.08"
    if g < 0.18: return "0.08-0.17"
    if g < 0.26: return "0.18-0.25"
    if g < 0.40: return "0.26-0.39"
    return "0.40+"

def bucket_books(p):
    b = fnum(p.get("bookmakers_used"))
    if b < 6: return "<6"
    if b < 8: return "6-7"
    if b < 10: return "8-9"
    return "10+"

def summarize(items):
    settled = [p for p in items if result(p) in SETTLED]
    wins = sum(1 for p in settled if result(p) == "win")
    losses = sum(1 for p in settled if result(p) == "loss")
    staked = sum(fnum(p.get("stake"), 1) for p in settled)
    prof = sum(profit(p) for p in settled)
    avg_odds = sum(fnum(p.get("odds")) for p in settled) / len(settled) if settled else 0

    return {
        "picks": len(settled),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(settled) * 100, 2) if settled else 0,
        "staked": round(staked, 2),
        "profit": round(prof, 2),
        "roi": round(prof / staked * 100, 2) if staked else 0,
        "avg_odds": round(avg_odds, 3),
    }

def max_drawdown(items):
    settled = sorted([p for p in items if result(p) in SETTLED], key=pick_key)
    bank = 0
    peak = 0
    dd = 0
    streak = 0
    max_streak = 0

    for p in settled:
        bank += profit(p)
        peak = max(peak, bank)
        dd = max(dd, peak - bank)

        if result(p) == "loss":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return {
        "max_drawdown_units": round(dd, 2),
        "longest_loss_streak": max_streak,
    }

def group_by(items, fn, min_picks=1):
    groups = defaultdict(list)
    for p in items:
        groups[str(fn(p))].append(p)

    out = {}
    for k, rows in groups.items():
        s = summarize(rows)
        if s["picks"] >= min_picks:
            s.update(max_drawdown(rows))
            out[k] = s

    return dict(sorted(out.items(), key=lambda x: x[1]["roi"], reverse=True))

def multi_cross(items, fields, min_picks=8):
    groups = defaultdict(list)

    for p in items:
        key = " | ".join(str(fn(p)) for fn in fields)
        groups[key].append(p)

    rows = []
    for key, vals in groups.items():
        s = summarize(vals)
        if s["picks"] >= min_picks:
            s.update(max_drawdown(vals))
            s["segment"] = key
            rows.append(s)

    return sorted(rows, key=lambda x: (x["roi"], x["profit"]), reverse=True)

def simulate(items, name, rule):
    rows = [p for p in items if result(p) in SETTLED and rule(p)]
    s = summarize(rows)
    s.update(max_drawdown(rows))
    s["name"] = name
    return s

def strategy_search(items, min_picks=10):
    tests = []

    sides = ["over", "under"]
    tours = ["atp", "wta", "challenger", "itf"]
    genders = ["men", "women"]

    line_rules = [
        ("line_low_18.5_20.5", lambda p: 18.5 <= fnum(p.get("line")) <= 20.5),
        ("line_mid_21.5_22.5", lambda p: 21.5 <= fnum(p.get("line")) <= 22.5),
        ("line_high_23.5_24.5", lambda p: 23.5 <= fnum(p.get("line")) <= 24.5),
        ("line_20.5_22.5", lambda p: 20.5 <= fnum(p.get("line")) <= 22.5),
    ]

    margin_rules = [
        ("margin_1.5_plus", lambda p: fnum(p.get("expected_margin")) >= 1.5),
        ("margin_2_plus", lambda p: fnum(p.get("expected_margin")) >= 2.0),
        ("margin_2.5_plus", lambda p: fnum(p.get("expected_margin")) >= 2.5),
    ]

    gap_rules = [
        ("gap_low_under_0.18", lambda p: fnum(p.get("market_gap")) < 0.18),
        ("gap_mid_0.18_0.39", lambda p: 0.18 <= fnum(p.get("market_gap")) < 0.40),
        ("gap_high_0.40_plus", lambda p: fnum(p.get("market_gap")) >= 0.40),
    ]

    edge_rules = [
        ("edge_6.5_9.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.10),
        ("edge_10_11.9", lambda p: 0.10 <= fnum(p.get("edge")) < 0.12),
        ("edge_12_plus", lambda p: fnum(p.get("edge")) >= 0.12),
    ]

    stake_rules = [
        ("no_top_rated", lambda p: p.get("stake_label") != "Top Rated"),
        ("strong_only", lambda p: p.get("stake_label") == "Strong"),
        ("standard_or_strong", lambda p: p.get("stake_label") in {"Standard", "Strong"}),
    ]

    for side in sides:
        tests.append((f"{side}_only", lambda p, side=side: str(p.get("side", "")).lower() == side))

        for tour in tours:
            base = f"{side}_{tour}"
            tests.append((base, lambda p, side=side, tour=tour:
                str(p.get("side", "")).lower() == side and str(p.get("tour_level", "")).lower() == tour
            ))

            for line_name, line_fn in line_rules:
                name = f"{base}_{line_name}"
                tests.append((name, lambda p, side=side, tour=tour, line_fn=line_fn:
                    str(p.get("side", "")).lower() == side
                    and str(p.get("tour_level", "")).lower() == tour
                    and line_fn(p)
                ))

                for margin_name, margin_fn in margin_rules:
                    tests.append((f"{name}_{margin_name}", lambda p, side=side, tour=tour, line_fn=line_fn, margin_fn=margin_fn:
                        str(p.get("side", "")).lower() == side
                        and str(p.get("tour_level", "")).lower() == tour
                        and line_fn(p)
                        and margin_fn(p)
                    ))

                for gap_name, gap_fn in gap_rules:
                    tests.append((f"{name}_{gap_name}", lambda p, side=side, tour=tour, line_fn=line_fn, gap_fn=gap_fn:
                        str(p.get("side", "")).lower() == side
                        and str(p.get("tour_level", "")).lower() == tour
                        and line_fn(p)
                        and gap_fn(p)
                    ))

                for edge_name, edge_fn in edge_rules:
                    tests.append((f"{name}_{edge_name}", lambda p, side=side, tour=tour, line_fn=line_fn, edge_fn=edge_fn:
                        str(p.get("side", "")).lower() == side
                        and str(p.get("tour_level", "")).lower() == tour
                        and line_fn(p)
                        and edge_fn(p)
                    ))

                for stake_name, stake_fn in stake_rules:
                    tests.append((f"{name}_{stake_name}", lambda p, side=side, tour=tour, line_fn=line_fn, stake_fn=stake_fn:
                        str(p.get("side", "")).lower() == side
                        and str(p.get("tour_level", "")).lower() == tour
                        and line_fn(p)
                        and stake_fn(p)
                    ))

        for gender in genders:
            tests.append((f"{side}_{gender}", lambda p, side=side, gender=gender:
                str(p.get("side", "")).lower() == side and str(p.get("gender", "")).lower() == gender
            ))

    results = []
    for name, rule in tests:
        s = simulate(items, name, rule)
        if s["picks"] >= min_picks:
            results.append(s)

    return sorted(results, key=lambda x: (x["roi"], x["profit"]), reverse=True)

def find_duplicates(items):
    same = defaultdict(list)
    match = defaultdict(list)

    for p in items:
        same[f"{p.get('date')} | {p.get('match')} | {p.get('side')} | {p.get('line')}"].append(p)
        match[f"{p.get('date')} | {p.get('match')}"].append(p)

    return {
        "same_match_same_side_line": [
            {"key": k, "count": len(v), "profit": round(sum(profit(x) for x in v), 2)}
            for k, v in same.items() if len(v) > 1
        ],
        "same_match_multiple_totals": [
            {"key": k, "count": len(v), "profit": round(sum(profit(x) for x in v), 2)}
            for k, v in match.items() if len(v) > 1
        ],
    }

def calibration(items):
    groups = defaultdict(list)

    for p in items:
        if result(p) not in SETTLED:
            continue
        prob = fnum(p.get("model_prob"))
        if prob <= 0:
            continue
        b = int((prob * 100) // 5 * 5)
        groups[f"{b}-{b+4}%"].append(p)

    out = {}
    for k, rows in groups.items():
        wins = sum(1 for p in rows if result(p) == "win")
        avg_prob = sum(fnum(p.get("model_prob")) for p in rows) / len(rows)
        actual = wins / len(rows)
        out[k] = {
            "picks": len(rows),
            "avg_model_prob": round(avg_prob * 100, 2),
            "actual_win_rate": round(actual * 100, 2),
            "gap": round((actual - avg_prob) * 100, 2),
        }

    return out

def main():
    items = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))

    report = {
        "overall": {**summarize(items), **max_drawdown(items)},

        "single_segments": {
            "by_side": group_by(items, lambda p: str(p.get("side", "unknown")).lower()),
            "by_line": group_by(items, bucket_line),
            "by_odds": group_by(items, bucket_odds),
            "by_edge": group_by(items, bucket_edge),
            "by_confidence": group_by(items, bucket_conf),
            "by_expected_margin": group_by(items, bucket_margin),
            "by_market_gap": group_by(items, bucket_market_gap),
            "by_bookmakers": group_by(items, bucket_books),
            "by_stake_label": group_by(items, lambda p: p.get("stake_label", "unknown")),
            "by_tour_level": group_by(items, lambda p: str(p.get("tour_level", "unknown")).lower()),
            "by_gender": group_by(items, lambda p: str(p.get("gender", "unknown")).lower()),
        },

        "multi_segments": {
            "side_x_line": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_line,
            ]),
            "side_x_margin": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_margin,
            ]),
            "side_x_market_gap": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_market_gap,
            ]),
            "tour_x_side_x_line": multi_cross(items, [
                lambda p: str(p.get("tour_level", "unknown")).lower(),
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_line,
            ]),
            "tour_x_side_x_margin": multi_cross(items, [
                lambda p: str(p.get("tour_level", "unknown")).lower(),
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_margin,
            ]),
            "side_x_line_x_margin": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_line,
                bucket_margin,
            ]),
            "side_x_line_x_gap": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_line,
                bucket_market_gap,
            ]),
            "side_x_edge_x_margin": multi_cross(items, [
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_edge,
                bucket_margin,
            ]),
            "stake_x_side_x_line": multi_cross(items, [
                lambda p: p.get("stake_label", "unknown"),
                lambda p: str(p.get("side", "unknown")).lower(),
                bucket_line,
            ]),
        },

        "strategy_search": strategy_search(items, min_picks=10),
        "calibration": calibration(items),
        "duplicates": find_duplicates(items),
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Totals ultra report saved:", OUT_FILE)
    print(json.dumps(report["overall"], indent=2, ensure_ascii=False))
    print("\nTop strategy search:")
    print(json.dumps(report["strategy_search"][:20], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

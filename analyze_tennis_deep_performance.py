import json
from collections import defaultdict
from pathlib import Path

RESULTS_FILE = Path("data/tennis_results.json")
OUT_FILE = Path("data/tennis_deep_performance_report.json")

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

def pick_date_key(p):
    return f"{p.get('date','')} {p.get('time','')} {p.get('match','')}"

def bucket_odds(p):
    o = fnum(p.get("odds"))
    if o < 1.70: return "<1.70"
    if o < 1.90: return "1.70-1.89"
    if o < 2.10: return "1.90-2.09"
    if o < 2.40: return "2.10-2.39"
    return "2.40+"

def bucket_edge(p):
    e = fnum(p.get("edge"))
    if e < 0.08: return "6.5-7.9%"
    if e < 0.10: return "8-9.9%"
    if e < 0.12: return "10-11.9%"
    return "12%+"

def bucket_conf(p):
    c = fnum(p.get("confidence"))
    if c < 74: return "<74"
    if c < 78: return "74-77.9"
    if c < 82: return "78-81.9"
    if c < 86: return "82-85.9"
    return "86+"

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
        "avg_odds": round(avg_odds, 3)
    }

def max_drawdown(items):
    settled = sorted(
        [p for p in items if result(p) in SETTLED],
        key=pick_date_key
    )
    bank = 0
    peak = 0
    dd = 0
    loss_streak = 0
    max_loss_streak = 0

    for p in settled:
        pr = profit(p)
        bank += pr
        peak = max(peak, bank)
        dd = max(dd, peak - bank)

        if result(p) == "loss":
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        else:
            loss_streak = 0

    return {
        "max_drawdown_units": round(dd, 2),
        "longest_loss_streak": max_loss_streak
    }

def group_by(items, name, fn, min_picks=1):
    groups = defaultdict(list)
    for p in items:
        groups[fn(p)].append(p)

    out = {}
    for k, rows in groups.items():
        s = summarize(rows)
        if s["picks"] >= min_picks:
            s.update(max_drawdown(rows))
            out[str(k)] = s

    return dict(sorted(out.items(), key=lambda x: x[1]["profit"], reverse=True))

def cross(items, name, f1, f2, min_picks=10):
    groups = defaultdict(list)
    for p in items:
        key = f"{f1(p)} | {f2(p)}"
        groups[key].append(p)

    rows = []
    for k, vals in groups.items():
        s = summarize(vals)
        if s["picks"] >= min_picks:
            s.update(max_drawdown(vals))
            s["segment"] = k
            rows.append(s)

    return sorted(rows, key=lambda x: x["roi"], reverse=True)

def find_duplicates(items):
    by_match_bet = defaultdict(list)
    by_match = defaultdict(list)

    for p in items:
        k1 = f"{p.get('date')} | {p.get('match')} | {p.get('bet')}"
        k2 = f"{p.get('date')} | {p.get('match')}"
        by_match_bet[k1].append(p)
        by_match[k2].append(p)

    return {
        "same_match_same_bet": [
            {"key": k, "count": len(v), "profit": round(sum(profit(x) for x in v), 2)}
            for k, v in by_match_bet.items()
            if len(v) > 1
        ],
        "same_match_multiple_picks": [
            {"key": k, "count": len(v), "profit": round(sum(profit(x) for x in v), 2)}
            for k, v in by_match.items()
            if len(v) > 1
        ]
    }

def simulate(items, name, rule):
    rows = [p for p in items if result(p) in SETTLED and rule(p)]
    s = summarize(rows)
    s.update(max_drawdown(rows))
    s["name"] = name
    return s

def what_if(items):
    tests = [
        ("odds_1.70_2.09", lambda p: 1.70 <= fnum(p.get("odds")) <= 2.09),
        ("odds_1.70_2.09_no_top_rated", lambda p: 1.70 <= fnum(p.get("odds")) <= 2.09 and p.get("stake_label") != "Top Rated"),
        ("no_top_rated", lambda p: p.get("stake_label") != "Top Rated"),
        ("no_edge_12_plus", lambda p: fnum(p.get("edge")) < 0.12),
        ("edge_6.5_11.9", lambda p: 0.065 <= fnum(p.get("edge")) < 0.12),
        ("challenger_only", lambda p: str(p.get("tour_level", "")).lower() == "challenger"),
        ("favorites_only", lambda p: str(p.get("favorite_type", "")).lower() == "favorite"),
        ("challenger_odds_1.70_2.09", lambda p: str(p.get("tour_level", "")).lower() == "challenger" and 1.70 <= fnum(p.get("odds")) <= 2.09),
        ("favorite_odds_1.70_2.09", lambda p: str(p.get("favorite_type", "")).lower() == "favorite" and 1.70 <= fnum(p.get("odds")) <= 2.09),
        ("gold_zone", lambda p:
            1.70 <= fnum(p.get("odds")) <= 2.09
            and 0.065 <= fnum(p.get("edge")) < 0.12
            and p.get("stake_label") != "Top Rated"
        ),
        ("brutal_conservative", lambda p:
            1.70 <= fnum(p.get("odds")) <= 2.09
            and 0.065 <= fnum(p.get("edge")) < 0.12
            and str(p.get("favorite_type", "")).lower() == "favorite"
            and p.get("stake_label") != "Top Rated"
        ),
    ]

    rows = [simulate(items, name, rule) for name, rule in tests]
    return sorted(rows, key=lambda x: x["roi"], reverse=True)

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
            "gap": round((actual - avg_prob) * 100, 2)
        }

    return out

def main():
    items = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))

    report = {
        "overall": {**summarize(items), **max_drawdown(items)},

        "single_segments": {
            "by_odds": group_by(items, "odds", bucket_odds),
            "by_edge": group_by(items, "edge", bucket_edge),
            "by_confidence": group_by(items, "confidence", bucket_conf),
            "by_stake_label": group_by(items, "stake", lambda p: p.get("stake_label", "unknown")),
            "by_tour_level": group_by(items, "tour", lambda p: str(p.get("tour_level", "unknown")).lower()),
            "by_gender": group_by(items, "gender", lambda p: str(p.get("gender", "unknown")).lower()),
            "by_favorite_type": group_by(items, "favorite", lambda p: str(p.get("favorite_type", "unknown")).lower()),
        },

        "cross_segments": {
            "odds_x_tour": cross(items, "odds_x_tour", bucket_odds, lambda p: str(p.get("tour_level", "unknown")).lower()),
            "odds_x_edge": cross(items, "odds_x_edge", bucket_odds, bucket_edge),
            "odds_x_confidence": cross(items, "odds_x_conf", bucket_odds, bucket_conf),
            "odds_x_favorite": cross(items, "odds_x_fav", bucket_odds, lambda p: str(p.get("favorite_type", "unknown")).lower()),
            "tour_x_favorite": cross(items, "tour_x_fav", lambda p: str(p.get("tour_level", "unknown")).lower(), lambda p: str(p.get("favorite_type", "unknown")).lower()),
            "stake_x_odds": cross(items, "stake_x_odds", lambda p: p.get("stake_label", "unknown"), bucket_odds),
            "confidence_x_edge": cross(items, "conf_x_edge", bucket_conf, bucket_edge),
        },

        "what_if": what_if(items),
        "calibration": calibration(items),
        "duplicates": find_duplicates(items)
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Deep report saved:", OUT_FILE)
    print(json.dumps(report["overall"], indent=2, ensure_ascii=False))
    print("\nTop what-if:")
    print(json.dumps(report["what_if"][:5], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

import json
from collections import defaultdict

RESULTS_FILE = "data/tennis_results.json"
REPORT_FILE = "data/tennis_performance_report.json"

def load_results():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def profit_for_pick(p):
    result = str(p.get("result", "")).lower()
    odds = float(p.get("odds") or 0)
    stake = float(p.get("stake") or 1)

    if result == "win":
        return (odds - 1) * stake
    if result == "loss":
        return -stake
    return 0

def bucket_odds(odds):
    odds = float(odds or 0)
    if odds < 1.70: return "1.60-1.69"
    if odds < 1.90: return "1.70-1.89"
    if odds < 2.10: return "1.90-2.09"
    if odds < 2.40: return "2.10-2.39"
    return "2.40+"

def bucket_confidence(conf):
    conf = float(conf or 0)
    if conf < 74: return "<74"
    if conf < 78: return "74-77.9"
    if conf < 82: return "78-81.9"
    if conf < 86: return "82-85.9"
    return "86+"

def bucket_edge(edge):
    edge = float(edge or 0)
    if edge < 0.08: return "6.5%-7.9%"
    if edge < 0.10: return "8%-9.9%"
    if edge < 0.12: return "10%-11.9%"
    return "12%+"

def summarize(items):
    settled = [p for p in items if str(p.get("result", "")).lower() in ["win", "loss"]]
    wins = sum(1 for p in settled if str(p.get("result")).lower() == "win")
    losses = sum(1 for p in settled if str(p.get("result")).lower() == "loss")
    staked = sum(float(p.get("stake") or 1) for p in settled)
    profit = sum(profit_for_pick(p) for p in settled)

    return {
        "picks": len(settled),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(settled) * 100, 2) if settled else 0,
        "staked": round(staked, 2),
        "profit": round(profit, 2),
        "roi": round(profit / staked * 100, 2) if staked else 0,
        "avg_odds": round(sum(float(p.get("odds") or 0) for p in settled) / len(settled), 3) if settled else 0
    }

def group_by(items, key_fn):
    groups = defaultdict(list)
    for p in items:
        groups[key_fn(p)].append(p)
    return {k: summarize(v) for k, v in sorted(groups.items())}

def calibration(items):
    buckets = defaultdict(list)

    for p in items:
        result = str(p.get("result", "")).lower()
        if result not in ["win", "loss"]:
            continue

        prob = float(p.get("model_prob") or 0)
        bucket = f"{int(prob * 100 // 5 * 5)}-{int(prob * 100 // 5 * 5 + 4)}%"
        buckets[bucket].append(p)

    out = {}
    for b, rows in sorted(buckets.items()):
        wins = sum(1 for p in rows if str(p.get("result")).lower() == "win")
        avg_prob = sum(float(p.get("model_prob") or 0) for p in rows) / len(rows)
        actual = wins / len(rows)
        out[b] = {
            "picks": len(rows),
            "avg_model_prob": round(avg_prob * 100, 2),
            "actual_win_rate": round(actual * 100, 2),
            "calibration_gap": round((actual - avg_prob) * 100, 2)
        }

    return out

def max_drawdown(items):
    settled = [
        p for p in items
        if str(p.get("result", "")).lower() in ["win", "loss"]
    ]

    settled.sort(key=lambda p: f"{p.get('date', '')} {p.get('time', '')}")

    bankroll = 0
    peak = 0
    max_dd = 0

    curve = []

    for p in settled:
        bankroll += profit_for_pick(p)
        peak = max(peak, bankroll)
        dd = peak - bankroll
        max_dd = max(max_dd, dd)

        curve.append({
            "date": p.get("date"),
            "match": p.get("match"),
            "profit": round(profit_for_pick(p), 2),
            "bankroll": round(bankroll, 2),
            "drawdown": round(dd, 2)
        })

    return {
        "max_drawdown_units": round(max_dd, 2),
        "equity_curve": curve
    }

def main():
    results = load_results()

    report = {
        "overall": summarize(results),
        "by_odds": group_by(results, lambda p: bucket_odds(p.get("odds"))),
        "by_confidence": group_by(results, lambda p: bucket_confidence(p.get("confidence"))),
        "by_edge": group_by(results, lambda p: bucket_edge(p.get("edge"))),
        "by_stake_label": group_by(results, lambda p: p.get("stake_label", "unknown")),
        "by_tour_level": group_by(results, lambda p: p.get("tour_level", "unknown")),
        "by_gender": group_by(results, lambda p: p.get("gender", "unknown")),
        "by_favorite_type": group_by(results, lambda p: p.get("favorite_type", "unknown")),
        "calibration": calibration(results),
        "drawdown": max_drawdown(results)
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report["overall"], indent=2, ensure_ascii=False))
    print(f"Saved report: {REPORT_FILE}")

if __name__ == "__main__":
    main()

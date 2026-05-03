import json
import os
from datetime import datetime
from collections import defaultdict

DATA_DIR = "data"
WEB_DIR = "web"
RESULTS_FILE = os.path.join(DATA_DIR, "cs2_results.json")
PREDICTIONS_FILE = os.path.join(DATA_DIR, "cs2_predictions.json")
WEB_DATA_FILE = os.path.join(WEB_DIR, "cs2_data.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def profit_for_pick(item):
    # No odds yet. Unit accuracy mode: win=+1, loss=-1, pending=0.
    if item.get("result") == "win":
        return 1.0
    if item.get("result") == "loss":
        return -1.0
    return 0.0


def group_stats(items, key_fn):
    groups = defaultdict(list)
    for item in items:
        if item.get("result") not in {"win", "loss"}:
            continue
        key = key_fn(item) or "Unknown"
        groups[str(key)].append(item)

    out = []
    for key, arr in groups.items():
        wins = sum(1 for x in arr if x.get("result") == "win")
        losses = sum(1 for x in arr if x.get("result") == "loss")
        picks = wins + losses
        profit = sum(profit_for_pick(x) for x in arr)
        hit = wins / picks * 100 if picks else 0
        roi = profit / picks * 100 if picks else 0
        out.append({
            "group": key,
            "picks": picks,
            "wins": wins,
            "losses": losses,
            "hit_rate": round(hit, 1),
            "profit_units": round(profit, 2),
            "roi": round(roi, 1),
        })
    out.sort(key=lambda x: (x["profit_units"], x["hit_rate"], x["picks"]), reverse=True)
    return out


def confidence_band(item):
    c = float(item.get("confidence") or 0)
    if c >= 85:
        return "Elite 85+"
    if c >= 75:
        return "High 75-84"
    if c >= 65:
        return "Medium 65-74"
    return "Low <65"


def main():
    os.makedirs(WEB_DIR, exist_ok=True)
    results = load_json(RESULTS_FILE, [])
    predictions = load_json(PREDICTIONS_FILE, {})
    if not isinstance(results, list):
        results = []

    settled = [x for x in results if isinstance(x, dict) and x.get("result") in {"win", "loss"}]
    pending = [x for x in results if isinstance(x, dict) and x.get("result") == "pending"]
    wins = sum(1 for x in settled if x.get("result") == "win")
    losses = sum(1 for x in settled if x.get("result") == "loss")
    profit = sum(profit_for_pick(x) for x in settled)
    picks = len(settled)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "mode": "prediction_accuracy_no_odds",
        "summary": {
            "settled_picks": picks,
            "pending_picks": len(pending),
            "wins": wins,
            "losses": losses,
            "hit_rate": round((wins / picks * 100) if picks else 0, 1),
            "profit_units_accuracy_mode": round(profit, 2),
            "roi_accuracy_mode": round((profit / picks * 100) if picks else 0, 1),
        },
        "predictions": predictions.get("picks", []) if isinstance(predictions, dict) else [],
        "results": results,
        "tables": {
            "by_confidence": group_stats(results, confidence_band),
            "by_tier": group_stats(results, lambda x: x.get("tier")),
            "by_league": group_stats(results, lambda x: x.get("league")),
            "by_best_of": group_stats(results, lambda x: f"BO{x.get('best_of')}"),
            "by_region": group_stats(results, lambda x: x.get("region")),
        },
    }

    with open(WEB_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Built {WEB_DATA_FILE}")


if __name__ == "__main__":
    main()

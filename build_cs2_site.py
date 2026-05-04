import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

DATA_DIR = "data"
WEB_DIR = "web"

PREDICTIONS_FILE = os.path.join(DATA_DIR, "cs2_predictions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "cs2_results.json")
SITE_DATA_FILE = os.path.join(WEB_DIR, "cs2_site_data.json")

TZ_NAME = "Europe/Ljubljana"


def load_json(path, default):
    if not os.path.exists(path):
        print(f"Missing file: {path}")
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return default


def save_json(path, data):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def pick_profit(pick):
    result = str(pick.get("result") or "pending").lower()

    if result == "win":
        return 1.0

    if result == "loss":
        return -1.0

    return 0.0


def settled_picks(results):
    return [
        p for p in results
        if isinstance(p, dict) and str(p.get("result") or "").lower() in {"win", "loss"}
    ]


def pending_picks(results):
    return [
        p for p in results
        if isinstance(p, dict) and str(p.get("result") or "pending").lower() == "pending"
    ]


def calc_summary(results):
    settled = settled_picks(results)
    pending = pending_picks(results)

    total = len(settled)
    wins = sum(1 for p in settled if str(p.get("result") or "").lower() == "win")
    losses = sum(1 for p in settled if str(p.get("result") or "").lower() == "loss")
    profit = sum(pick_profit(p) for p in settled)

    hit_rate = (wins / total * 100) if total else 0.0
    roi = (profit / total * 100) if total else 0.0

    return {
        "settled_picks": total,
        "pending_picks": len(pending),
        "wins": wins,
        "losses": losses,
        "profit": round(profit, 2),
        "hit_rate": round(hit_rate, 1),
        "roi": round(roi, 1),
    }


def confidence_band(confidence):
    try:
        conf = float(confidence or 0)
    except Exception:
        conf = 0

    if conf >= 80:
        return "High Confidence"
    if conf >= 65:
        return "Medium Confidence"
    return "Lower Confidence"


def group_stats(results, mode):
    groups = {}

    for pick in settled_picks(results):
        if mode == "confidence":
            key = confidence_band(pick.get("confidence"))
        elif mode == "best_of":
            key = f"BO{pick.get('best_of') or 'Unknown'}"
        elif mode == "tier":
            key = pick.get("tier") or "Unknown"
        else:
            key = "Unknown"

        if key not in groups:
            groups[key] = {
                "group": key,
                "picks": 0,
                "wins": 0,
                "losses": 0,
                "profit": 0.0,
            }

        groups[key]["picks"] += 1

        if str(pick.get("result") or "").lower() == "win":
            groups[key]["wins"] += 1
        else:
            groups[key]["losses"] += 1

        groups[key]["profit"] += pick_profit(pick)

    output = []

    for row in groups.values():
        picks = row["picks"]
        row["hit_rate"] = round((row["wins"] / picks * 100) if picks else 0, 1)
        row["roi"] = round((row["profit"] / picks * 100) if picks else 0, 1)
        row["profit"] = round(row["profit"], 2)
        output.append(row)

    output.sort(key=lambda x: (x["profit"], x["hit_rate"], x["picks"]), reverse=True)
    return output


def normalize_predictions(payload):
    if isinstance(payload, dict):
        picks = payload.get("picks", [])
        generated_at = payload.get("generated_at")
        model = payload.get("model") or "AI77 PandaScore CS2"
        note = payload.get("note") or ""
    elif isinstance(payload, list):
        picks = payload
        generated_at = None
        model = "AI77 PandaScore CS2"
        note = ""
    else:
        picks = []
        generated_at = None
        model = "AI77 PandaScore CS2"
        note = ""

    if not isinstance(picks, list):
        picks = []

    return picks, generated_at, model, note


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)

    print("Building CS2 site data...")
    print(f"Reading predictions from: {PREDICTIONS_FILE}")
    print(f"Reading results from: {RESULTS_FILE}")

    predictions_payload = load_json(PREDICTIONS_FILE, {})
    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    current_picks, generated_at, model, note = normalize_predictions(predictions_payload)

    now = datetime.now(ZoneInfo(TZ_NAME)).isoformat()

    site_data = {
        "generated_at": generated_at or now,
        "built_at": now,
        "timezone": TZ_NAME,
        "source": "PandaScore",
        "model": model,
        "note": note or "No betting odds are used. This page tracks prediction accuracy only.",
        "summary": calc_summary(results),
        "current_picks": current_picks,
        "results": results,
        "performance_by_confidence": group_stats(results, "confidence"),
        "performance_by_best_of": group_stats(results, "best_of"),
        "performance_by_tier": group_stats(results, "tier"),
    }

    save_json(SITE_DATA_FILE, site_data)

    print(f"Current picks: {len(current_picks)}")
    print(f"Results rows: {len(results)}")
    print(f"Saved {SITE_DATA_FILE}")
    print(f"Exists after save: {os.path.exists(SITE_DATA_FILE)}")


if __name__ == "__main__":
    main()

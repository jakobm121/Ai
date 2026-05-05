import os
import json
from datetime import datetime
from collections import defaultdict
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
WEB_DIR = "web"

PREDICTIONS_FILE = os.path.join(DATA_DIR, "tennis_predictions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "tennis_results.json")
SITE_DATA_FILE = os.path.join(WEB_DIR, "tennis_site_data.json")


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)


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


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def is_win(item):
    return str(item.get("result") or "").lower() == "win"


def is_loss(item):
    return str(item.get("result") or "").lower() == "loss"


def is_pending(item):
    return str(item.get("result") or "pending").lower() == "pending"


def is_settled(item):
    return is_win(item) or is_loss(item)


def odds_band(odds):
    odds = safe_float(odds)

    if odds < 1.60:
        return "< 1.60"
    if odds < 1.80:
        return "1.60 - 1.79"
    if odds < 2.00:
        return "1.80 - 1.99"
    if odds < 2.30:
        return "2.00 - 2.29"
    if odds < 2.70:
        return "2.30 - 2.69"
    return "2.70+"


def confidence_band(conf):
    conf = safe_float(conf)

    if conf >= 88:
        return "Elite 88+"
    if conf >= 82:
        return "Strong 82-87"
    if conf >= 76:
        return "Solid 76-81"
    if conf >= 72:
        return "Minimum 72-75"
    return "Below 72"


def edge_band(edge):
    edge = safe_float(edge)

    if edge >= 0.20:
        return "20%+"
    if edge >= 0.15:
        return "15% - 19.9%"
    if edge >= 0.10:
        return "10% - 14.9%"
    if edge >= 0.065:
        return "6.5% - 9.9%"
    return "< 6.5%"


def calc_group_stats(items):
    picks = len(items)
    settled = [x for x in items if is_settled(x)]
    pending = [x for x in items if is_pending(x)]
    wins = sum(1 for x in settled if is_win(x))
    losses = sum(1 for x in settled if is_loss(x))

    stake = sum(safe_float(x.get("stake"), 0) for x in settled)
    profit = sum(safe_float(x.get("profit"), 0) for x in settled)

    avg_odds_items = [safe_float(x.get("odds"), 0) for x in settled if safe_float(x.get("odds"), 0) > 0]
    avg_odds = sum(avg_odds_items) / len(avg_odds_items) if avg_odds_items else 0

    hit_rate = (wins / len(settled) * 100) if settled else 0
    roi = (profit / stake * 100) if stake else 0

    return {
        "picks": picks,
        "settled": len(settled),
        "pending": len(pending),
        "wins": wins,
        "losses": losses,
        "hit_rate": round(hit_rate, 1),
        "stake": round(stake, 2),
        "profit": round(profit, 2),
        "roi": round(roi, 1),
        "avg_odds": round(avg_odds, 2),
    }


def build_table(items, key_fn):
    groups = defaultdict(list)

    for item in items:
        group = key_fn(item)
        groups[group].append(item)

    rows = []

    for group, group_items in groups.items():
        stats = calc_group_stats(group_items)
        rows.append({
            "group": group,
            **stats,
        })

    rows.sort(
        key=lambda x: (
            x["settled"],
            x["profit"],
            x["picks"],
        ),
        reverse=True,
    )

    return rows


def build_daily_performance(items):
    groups = defaultdict(list)

    for item in items:
        date = item.get("date") or "Unknown"
        groups[date].append(item)

    rows = []

    for date, group_items in groups.items():
        stats = calc_group_stats(group_items)
        rows.append({
            "date": date,
            **stats,
        })

    rows.sort(key=lambda x: x["date"], reverse=True)
    return rows


def build_daily_by_type(items):
    groups = defaultdict(list)

    for item in items:
        date = item.get("date") or "Unknown"
        favorite_type = item.get("favorite_type") or "unknown"
        groups[(date, favorite_type)].append(item)

    rows = []

    for (date, favorite_type), group_items in groups.items():
        stats = calc_group_stats(group_items)
        rows.append({
            "date": date,
            "type": favorite_type,
            **stats,
        })

    rows.sort(key=lambda x: (x["date"], x["type"]), reverse=True)
    return rows


def get_current_picks(predictions_payload, results):
    current = predictions_payload.get("picks", [])

    if not isinstance(current, list):
        current = []

    # Merge latest result state from results file, because a prediction can already be settled.
    result_by_id = {
        item.get("pick_id"): item
        for item in results
        if isinstance(item, dict) and item.get("pick_id")
    }

    merged = []

    for pick in current:
        pick_id = pick.get("pick_id")
        if pick_id in result_by_id:
            merged.append(result_by_id[pick_id])
        else:
            merged.append(pick)

    merged.sort(key=lambda x: (x.get("date") or "", x.get("time") or ""))
    return merged


def build_site_data():
    ensure_dirs()

    predictions = load_json(PREDICTIONS_FILE, {})
    results = load_json(RESULTS_FILE, [])

    if not isinstance(predictions, dict):
        predictions = {}

    if not isinstance(results, list):
        results = []

    current_picks = get_current_picks(predictions, results)

    settled = [x for x in results if is_settled(x)]
    pending = [x for x in results if is_pending(x)]

    summary = calc_group_stats(results)

    payload = {
        "generated_at": datetime.now(ZoneInfo(TZ_NAME)).isoformat(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "model": predictions.get("model") or "AI77 Tennis Value Model",
        "market": predictions.get("market") or "Home/Away Match Winner",
        "filters": predictions.get("filters") or {},
        "predictions_summary": predictions.get("summary") or {},
        "summary": {
            **summary,
            "total_results": len(results),
            "settled_picks": len(settled),
            "pending_picks": len(pending),
        },
        "current_picks": current_picks,
        "results": results,
        "tables": {
            "daily_performance": build_daily_performance(results),
            "daily_by_type": build_daily_by_type(results),
            "by_favorite_type": build_table(results, lambda x: x.get("favorite_type") or "unknown"),
            "by_odds_band": build_table(results, lambda x: odds_band(x.get("odds"))),
            "by_confidence": build_table(results, lambda x: confidence_band(x.get("confidence"))),
            "by_edge": build_table(results, lambda x: edge_band(x.get("edge"))),
            "by_stake_label": build_table(results, lambda x: x.get("stake_label") or "Unknown"),
            "by_tour_level": build_table(results, lambda x: x.get("tour_level") or "unknown"),
            "by_gender": build_table(results, lambda x: x.get("gender") or "unknown"),
            "by_bookmaker": build_table(results, lambda x: x.get("best_bookmaker") or "unknown"),
        },
    }

    save_json(SITE_DATA_FILE, payload)

    print(f"Built tennis site data: {SITE_DATA_FILE}")
    print(f"Results: {len(results)} | settled={len(settled)} | pending={len(pending)}")


if __name__ == "__main__":
    build_site_data()

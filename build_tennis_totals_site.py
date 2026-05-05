import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
WEB_DIR = "web"

PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_predictions.json"
RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results.json"
OUTPUT_FILE = f"{WEB_DIR}/tennis_totals_site_data.json"


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    predictions = load_json(PREDICTIONS_FILE, {})
    results = load_json(RESULTS_FILE, [])

    if not isinstance(predictions, dict):
        predictions = {}

    if not isinstance(results, list):
        results = []

    payload = {
        "built_at": now_iso(),
        "timezone": TZ_NAME,
        "predictions": predictions,
        "results": results,
    }

    save_json(OUTPUT_FILE, payload)

    print(f"Built totals site data: {OUTPUT_FILE}")
    print(f"Predictions picks: {len((predictions.get('picks') or []))}")
    print(f"Results picks: {len(results)}")


if __name__ == "__main__":
    main()

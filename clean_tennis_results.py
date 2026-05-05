import json
import os
import shutil
from datetime import datetime

RESULTS_FILE = "data/tennis_totals_results.json"

REMOVE_PICK_IDS = {
    "05f7e73fe1f472dcf442d312bba6d1d4",
    "694932db8045896a98ee2dda5d09c19b",
    "f3edac972b81c64d1e42c88e158c6785",
    "3672a248ab050785a7b6f2b50146b1ab",
}


def main():
    if not os.path.exists(RESULTS_FILE):
        raise FileNotFoundError(f"Missing file: {RESULTS_FILE}")

    backup_file = f"{RESULTS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copyfile(RESULTS_FILE, backup_file)

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)

    if not isinstance(results, list):
        raise RuntimeError("tennis_results.json must be a JSON list")

    before = len(results)

    cleaned = [
        pick for pick in results
        if pick.get("pick_id") not in REMOVE_PICK_IDS
    ]

    after = len(cleaned)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Backup created: {backup_file}")
    print(f"Before: {before}")
    print(f"After: {after}")
    print(f"Removed: {before - after}")


if __name__ == "__main__":
    main()

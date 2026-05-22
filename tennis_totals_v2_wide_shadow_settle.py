import json
import subprocess
from pathlib import Path

PREDICTIONS_FILE = Path("data/tennis_totals_v2_wide_shadow_predictions.json")
RESULTS_FILE = Path("data/tennis_totals_v2_wide_shadow_results.json")

# Uporabi isti settle engine kot navadni totals.
# Ta wrapper samo začasno preusmeri V2 shadow file-e.
BASE_SETTLE_FILE = Path("tennis_totals_settle.py")


def main():
    if not BASE_SETTLE_FILE.exists():
        raise FileNotFoundError("Missing tennis_totals_settle.py")

    code = BASE_SETTLE_FILE.read_text(encoding="utf-8")

    code = code.replace(
        'Path("data/tennis_totals_predictions.json")',
        'Path("data/tennis_totals_v2_wide_shadow_predictions.json")',
    )
    code = code.replace(
        'Path("data/tennis_totals_results.json")',
        'Path("data/tennis_totals_v2_wide_shadow_results.json")',
    )
    code = code.replace(
        '"data/tennis_totals_predictions.json"',
        '"data/tennis_totals_v2_wide_shadow_predictions.json"',
    )
    code = code.replace(
        '"data/tennis_totals_results.json"',
        '"data/tennis_totals_v2_wide_shadow_results.json"',
    )

    temp_file = Path("_tmp_tennis_totals_v2_wide_shadow_settle_runner.py")
    temp_file.write_text(code, encoding="utf-8")

    try:
        subprocess.run(["python", str(temp_file)], check=True)
    finally:
        temp_file.unlink(missing_ok=True)

    if RESULTS_FILE.exists():
        data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        print(f"V2 wide shadow settled/results rows: {len(data) if isinstance(data, list) else 'unknown'}")


if __name__ == "__main__":
    main()

name: Settle Tennis First Set Picks

on:
  workflow_dispatch:
  schedule:
    - cron: "10 */2 * * *"

permissions:
  contents: write

concurrency:
  group: settle-tennis-first-set-picks
  cancel-in-progress: false

jobs:
  settle-tennis-first-set-picks:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Import and settle first-set picks
        env:
          API_KEY: ${{ secrets.API_KEY }}
          TZ_NAME: "Europe/Ljubljana"
          TENNIS_FIRST_SET_PICKS_URL: "https://raw.githubusercontent.com/jakobm121/Tennis-ELO/refs/heads/main/data/predictions/first_set_under_9_5_shadow.json"
          TENNIS_FIRST_SET_DEFAULT_STAKE: "1.0"
        run: python tennis_first_set_settle.py

      - name: Validate settlement
        run: |
          python - <<'PY'
          import json
          from pathlib import Path

          results_path = Path("data/tennis_first_set_results.json")
          debug_path = Path("data/tennis_first_set_settle_debug.json")

          for path in [results_path, debug_path]:
              if not path.exists():
                  raise SystemExit(f"Missing generated file: {path}")

          results = json.loads(
              results_path.read_text(encoding="utf-8")
          )

          debug = json.loads(
              debug_path.read_text(encoding="utf-8")
          )

          print("RESULTS:", len(results))
          print("PERFORMANCE:", debug.get("performance", {}))

          for item in results[-10:]:
              print({
                  "match": item.get("match"),
                  "side": item.get("side"),
                  "line": item.get("line"),
                  "odds": item.get("odds"),
                  "result": item.get("result"),
                  "first_set_score": item.get("first_set_score"),
                  "profit": item.get("profit"),
              })
          PY

      - name: Commit settlement outputs
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add data/tennis_first_set_results.json
          git add data/tennis_first_set_settle_debug.json

          if git diff --cached --quiet; then
            echo "No changes to commit."
            exit 0
          fi

          git commit -m "Settle tennis first set picks"
          git pull --rebase --autostash origin main
          git push origin HEAD:main

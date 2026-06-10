from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests


BASE_URL = "https://api.api-tennis.com/tennis/"
DEFAULT_OUTPUT = Path("data/tle/odds_backfill/tle_odds_backfill.json")
DEFAULT_REPORT = Path("data/tle/odds_backfill/tle_odds_backfill_report.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def date_range(start: date, stop: date):
    current = start
    while current <= stop:
        yield current
        current += timedelta(days=1)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_existing(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": 1,
            "created_at": now_iso(),
            "updated_at": None,
            "date_ranges": [],
            "odds_by_event_key": {},
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Invalid existing odds archive: {path}")

    payload.setdefault("schema_version", 1)
    payload.setdefault("date_ranges", [])
    payload.setdefault("odds_by_event_key", {})
    return payload


def api_get(api_key: str, params: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    request_params = {"APIkey": api_key, **params}
    response = requests.get(BASE_URL, params=request_params, timeout=timeout)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("API returned non-object JSON payload")

    return payload


def market_has_home_away(event_odds: Any) -> bool:
    if not isinstance(event_odds, dict):
        return False

    market = event_odds.get("Home/Away")
    if not isinstance(market, dict):
        return False

    return isinstance(market.get("Home"), dict) and isinstance(market.get("Away"), dict)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill zgodovinske API-Tennis kvote za Home/Away market "
            "po datumih in shrani odds archive za TLE ROI test."
        )
    )

    parser.add_argument("--from-date", required=True)
    parser.add_argument("--to-date", required=True)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Zamenjaj obstojeÄi odds archive namesto merge/update.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=float(os.getenv("API_SLEEP_SECONDS", "0.8")),
    )

    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY environment variable.")

    start = parse_date(args.from_date)
    stop = parse_date(args.to_date)
    if stop < start:
        raise RuntimeError("--to-date mora biti >= --from-date")

    output_path = Path(args.output)
    report_path = Path(args.report)

    if args.replace:
        archive = {
            "schema_version": 1,
            "created_at": now_iso(),
            "updated_at": None,
            "date_ranges": [],
            "odds_by_event_key": {},
        }
    else:
        archive = load_existing(output_path)

    counters = Counter()
    day_reports = []

    for day in date_range(start, stop):
        day_text = day.isoformat()
        counters["days_requested"] += 1

        payload = api_get(
            api_key,
            {
                "method": "get_odds",
                "date_start": day_text,
                "date_stop": day_text,
            },
        )

        success = payload.get("success")
        result = payload.get("result") or {}

        if not isinstance(result, dict):
            result = {}

        day_count = 0
        day_home_away_count = 0

        for event_key, event_odds in result.items():
            event_key_text = str(event_key)
            day_count += 1
            counters["events_with_any_odds"] += 1

            has_home_away = market_has_home_away(event_odds)
            if has_home_away:
                day_home_away_count += 1
                counters["events_with_home_away"] += 1
            else:
                counters["events_without_home_away"] += 1

            archive["odds_by_event_key"][event_key_text] = {
                "event_key": event_key_text,
                "odds_date": day_text,
                "fetched_at": now_iso(),
                "has_home_away": has_home_away,
                "markets": event_odds,
            }

        day_reports.append(
            {
                "date": day_text,
                "success": success,
                "events": day_count,
                "events_with_home_away": day_home_away_count,
            }
        )

        print(
            json.dumps(
                day_reports[-1],
                ensure_ascii=False,
            )
        )

        if args.sleep > 0:
            time.sleep(args.sleep)

    archive["updated_at"] = now_iso()
    archive["date_ranges"].append(
        {
            "from_date": args.from_date,
            "to_date": args.to_date,
            "fetched_at": archive["updated_at"],
            "replace": bool(args.replace),
        }
    )

    summary = {
        "from_date": args.from_date,
        "to_date": args.to_date,
        "archive_events_total": len(archive["odds_by_event_key"]),
        **dict(sorted(counters.items())),
    }

    report = {
        "generated_at": now_iso(),
        "summary": summary,
        "days": day_reports,
        "debug_url_pattern": (
            BASE_URL
            + "?"
            + urlencode(
                {
                    "method": "get_odds",
                    "APIkey": "***",
                    "date_start": args.from_date,
                    "date_stop": args.to_date,
                }
            )
        ),
    }

    save_json(output_path, archive)
    save_json(report_path, report)

    print("TLE ODDS BACKFILL DONE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


BASE_URL = "https://api.api-tennis.com/tennis/"
DEFAULT_OUTPUT = Path("data/tle/debug/odds_side_mapping_raw_debug.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def api_get(api_key: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(
        BASE_URL,
        params={"APIkey": api_key, **params},
        timeout=60,
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except Exception:
        return {
            "success": None,
            "raw_text": response.text[:5000],
            "url": response.url.replace(api_key, "***"),
        }

    if isinstance(payload, dict):
        payload["debug_url"] = response.url.replace(api_key, "***")

    return payload


def result_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result")

    if isinstance(result, list):
        return [
            item
            for item in result
            if isinstance(item, dict)
        ]

    if isinstance(result, dict):
        return [
            value
            for value in result.values()
            if isinstance(value, dict)
        ]

    return []


def first_fixture(payload: dict[str, Any], event_key: str) -> dict[str, Any] | None:
    for item in result_list(payload):
        if clean(item.get("event_key")) == str(event_key):
            return item

    rows = result_list(payload)
    return rows[0] if rows else None


def odds_for_event(payload: dict[str, Any], event_key: str) -> dict[str, Any] | None:
    result = payload.get("result")
    if not isinstance(result, dict):
        return None

    event_odds = result.get(str(event_key))
    if not isinstance(event_odds, dict):
        return None

    market = event_odds.get("Home/Away")
    if not isinstance(market, dict):
        return None

    return market


def summarize_fixture(fixture: dict[str, Any] | None) -> dict[str, Any]:
    if not fixture:
        return {}

    keys = [
        "event_key",
        "event_date",
        "event_time",
        "event_first_player",
        "first_player",
        "first_player_key",
        "event_second_player",
        "second_player",
        "second_player_key",
        "event_final_result",
        "event_game_result",
        "event_winner",
        "event_status",
        "event_type_type",
        "tournament_name",
        "tournament_key",
        "tournament_round",
        "event_qualification",
    ]

    out = {}
    for key in keys:
        if key in fixture:
            out[key] = fixture.get(key)

    # Include suspicious name/key fields that API may use.
    for key, value in fixture.items():
        key_text = str(key).lower()
        if (
            "player" in key_text
            or "winner" in key_text
            or "result" in key_text
            or "score" in key_text
            or "home" in key_text
            or "away" in key_text
        ):
            out.setdefault(key, value)

    return out


def summarize_home_away(market: dict[str, Any] | None) -> dict[str, Any]:
    if not market:
        return {}

    home = market.get("Home") if isinstance(market.get("Home"), dict) else {}
    away = market.get("Away") if isinstance(market.get("Away"), dict) else {}

    preferred_books = [
        "Pncl",
        "bet365",
        "Marathon",
        "1xBet",
        "Betano",
        "WilliamHill",
        "10Bet",
    ]

    return {
        "Home": {
            book: home.get(book)
            for book in preferred_books
            if book in home
        },
        "Away": {
            book: away.get(book)
            for book in preferred_books
            if book in away
        },
        "home_books_count": len(home),
        "away_books_count": len(away),
    }


def infer_winner_from_fixture(fixture: dict[str, Any] | None) -> dict[str, Any]:
    if not fixture:
        return {
            "winner_inference": "missing_fixture",
        }

    first = clean(
        fixture.get("event_first_player")
        or fixture.get("first_player")
        or fixture.get("player_1")
    )
    second = clean(
        fixture.get("event_second_player")
        or fixture.get("second_player")
        or fixture.get("player_2")
    )

    winner_raw = fixture.get("event_winner")

    first_key = clean(fixture.get("first_player_key"))
    second_key = clean(fixture.get("second_player_key"))

    # API-Tennis often stores event_winner as "First Player" / "Second Player"
    # or as a player key. We output all interpretations instead of guessing.
    possible = {
        "as_raw": winner_raw,
        "first_player": first,
        "second_player": second,
        "first_player_key": first_key,
        "second_player_key": second_key,
        "interpretations": {},
    }

    winner_text = clean(winner_raw).lower()

    if winner_text in {"first player", "first", "home", "1", first_key.lower()}:
        possible["interpretations"]["event_winner_as_first_player"] = first

    if winner_text in {"second player", "second", "away", "2", second_key.lower()}:
        possible["interpretations"]["event_winner_as_second_player"] = second

    if winner_text and first and winner_text == first.lower():
        possible["interpretations"]["event_winner_as_name"] = first

    if winner_text and second and winner_text == second.lower():
        possible["interpretations"]["event_winner_as_name"] = second

    return possible


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Raw debug za API-Tennis fixture + Home/Away odds mapping. "
            "To uporabi za direktno preverjanje ali Home pomeni first_player "
            "ali second_player in kaj pomeni event_winner."
        )
    )

    parser.add_argument(
        "--event-keys",
        required=True,
        help="Comma separated event keys, e.g. 12134273,12134279",
    )
    parser.add_argument(
        "--date",
        default="",
        help="Optional date YYYY-MM-DD. Äe je podan, get_odds uporabi ta datum.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
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

    event_keys = [
        item.strip()
        for item in args.event_keys.split(",")
        if item.strip()
    ]

    output = {
        "generated_at": now_iso(),
        "event_keys": event_keys,
        "date": args.date or None,
        "items": [],
    }

    for event_key in event_keys:
        fixture_payload = api_get(
            api_key,
            {
                "method": "get_fixtures",
                "event_key": event_key,
            },
        )

        fixture = first_fixture(fixture_payload, event_key)

        if args.date:
            odds_payload = api_get(
                api_key,
                {
                    "method": "get_odds",
                    "date_start": args.date,
                    "date_stop": args.date,
                },
            )
        else:
            # Some plans accept event_key on get_odds; if not, response will show it.
            odds_payload = api_get(
                api_key,
                {
                    "method": "get_odds",
                    "event_key": event_key,
                },
            )

        market = odds_for_event(odds_payload, event_key)

        item = {
            "event_key": event_key,
            "fixture_request": {
                "success": fixture_payload.get("success"),
                "debug_url": fixture_payload.get("debug_url"),
                "result_type": type(fixture_payload.get("result")).__name__,
                "result_count": len(result_list(fixture_payload)),
            },
            "fixture_summary": summarize_fixture(fixture),
            "winner_inference": infer_winner_from_fixture(fixture),
            "odds_request": {
                "success": odds_payload.get("success"),
                "debug_url": odds_payload.get("debug_url"),
                "result_type": type(odds_payload.get("result")).__name__,
                "result_count": (
                    len(odds_payload.get("result"))
                    if isinstance(odds_payload.get("result"), dict)
                    else None
                ),
            },
            "home_away_odds_summary": summarize_home_away(market),
            "manual_questions": [
                "Ali Home kvota ustreza event_first_player ali event_second_player?",
                "Ali event_winner pomeni first_player_key/second_player_key ali 1/2?",
                "Ali je event_final_result zapisan iz perspektive first_player?",
            ],
            "raw_fixture": fixture,
            "raw_home_away_market": market,
        }

        output["items"].append(item)

        print(json.dumps({
            "event_key": event_key,
            "fixture_summary": item["fixture_summary"],
            "winner_inference": item["winner_inference"],
            "home_away_odds_summary": item["home_away_odds_summary"],
        }, indent=2, ensure_ascii=False))

        if args.sleep > 0:
            time.sleep(args.sleep)

    save_json(Path(args.output), output)

    print("TLE RAW ODDS SIDE DEBUG DONE")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from tennis_odds_export import (
    API_SLEEP_SECONDS,
    TZ_NAME,
    api_call,
    gender_from_event_type,
    infer_best_of,
    infer_indoor,
    is_grand_slam,
    is_singles,
    normalize_surface,
    safe_int,
    tour_level,
)


SCHEMA_VERSION = 1
DEFAULT_OUTPUT = "data/tle/tle_api_results_backfill.json"
DEFAULT_REPORT = "data/tle/tle_api_results_backfill_report.json"

FINISHED_STATUSES = {
    "finished",
    "final",
    "completed",
    "complete",
    "ended",
}

REJECTED_STATUSES = {
    "cancelled",
    "canceled",
    "postponed",
    "interrupted",
    "abandoned",
    "walkover",
    "wo",
    "w/o",
    "retired",
}

TRUE_VALUES = {"1", "true", "yes", "y"}


def now_iso() -> str:
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Neveljaven datum {value!r}; uporabi YYYY-MM-DD."
        ) from exc


def date_range(start_date: date, end_date: date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalized_status(fixture: dict[str, Any]) -> str:
    return clean_text(fixture.get("event_status")).lower()


def is_finished(fixture: dict[str, Any]) -> bool:
    status = normalized_status(fixture)
    if status in FINISHED_STATUSES:
        return True

    # API vÄasih vrne prazen ali drugaÄen status, rezultat pa je Å¾e konÄen.
    final_result = clean_text(
        fixture.get("event_final_result")
        or fixture.get("final_result")
        or fixture.get("event_result")
    )
    winner = clean_text(
        fixture.get("event_winner")
        or fixture.get("winner")
    )
    return bool(final_result and winner and status not in REJECTED_STATUSES)


def is_rejected_result(fixture: dict[str, Any]) -> bool:
    status = normalized_status(fixture)
    text = " ".join(
        [
            status,
            clean_text(fixture.get("event_final_result")).lower(),
            clean_text(fixture.get("event_result")).lower(),
        ]
    )
    return any(marker in text for marker in REJECTED_STATUSES)


def qualification_flag(fixture: dict[str, Any]) -> bool:
    value = str(fixture.get("event_qualification") or "").strip().lower()
    if value in TRUE_VALUES:
        return True

    round_text = clean_text(fixture.get("tournament_round")).lower()
    event_type = clean_text(fixture.get("event_type_type")).lower()
    tournament = clean_text(fixture.get("tournament_name")).lower()
    blob = f"{round_text} {event_type} {tournament}"

    return any(
        marker in blob
        for marker in (
            "qualification",
            "qualifying",
            "qualifier",
            "q1",
            "q2",
            "q3",
        )
    )


def normalize_tle_level(fixture: dict[str, Any]) -> str:
    if qualification_flag(fixture):
        return "qualifying"

    event_type = fixture.get("event_type_type")
    tournament = fixture.get("tournament_name")
    raw_level = tour_level(event_type, tournament)

    if raw_level in {"grand_slam", "atp", "wta"}:
        return "main_tour"
    if raw_level == "challenger":
        return "challenger"
    if raw_level == "itf":
        return "itf"
    return "unknown"


def winner_side(fixture: dict[str, Any]) -> str | None:
    raw = clean_text(
        fixture.get("event_winner")
        or fixture.get("winner")
    ).lower()

    first_name = clean_text(fixture.get("event_first_player")).lower()
    second_name = clean_text(fixture.get("event_second_player")).lower()

    first_markers = {
        "first player",
        "first",
        "player 1",
        "player1",
        "home",
        "1",
    }
    second_markers = {
        "second player",
        "second",
        "player 2",
        "player2",
        "away",
        "2",
    }

    if raw in first_markers or (first_name and raw == first_name):
        return "player_1"
    if raw in second_markers or (second_name and raw == second_name):
        return "player_2"
    return None


def fetch_fixtures_for_date(day: date) -> list[dict[str, Any]]:
    day_text = day.isoformat()
    payload = api_call(
        {
            "method": "get_fixtures",
            "date_start": day_text,
            "date_stop": day_text,
        }
    )
    time.sleep(API_SLEEP_SECONDS)

    if payload.get("success") != 1:
        return []

    result = payload.get("result") or []
    return result if isinstance(result, list) else []


def build_record(fixture: dict[str, Any]) -> dict[str, Any]:
    tournament = fixture.get("tournament_name")
    event_type = fixture.get("event_type_type")
    gender = gender_from_event_type(event_type, tournament)
    surface = normalize_surface(fixture)
    level = normalize_tle_level(fixture)
    side = winner_side(fixture)

    player_1 = clean_text(fixture.get("event_first_player"))
    player_2 = clean_text(fixture.get("event_second_player"))

    winner_name = player_1 if side == "player_1" else player_2
    loser_name = player_2 if side == "player_1" else player_1

    return {
        "schema_version": SCHEMA_VERSION,
        "source": "API-Tennis",
        "event_key": safe_int(fixture.get("event_key")),
        "event_id": str(fixture.get("event_key") or ""),
        "date": clean_text(fixture.get("event_date")),
        "time": clean_text(fixture.get("event_time")),
        "timezone": TZ_NAME,
        "status": clean_text(fixture.get("event_status")),
        "gender": gender,
        "tour_level": level,
        "surface": surface,
        "qualification": qualification_flag(fixture),
        "is_grand_slam": is_grand_slam(tournament),
        "indoor": infer_indoor(fixture),
        "best_of": infer_best_of(fixture, gender, tournament),
        "event_type": clean_text(event_type),
        "tournament": clean_text(tournament),
        "tournament_key": safe_int(fixture.get("tournament_key")),
        "tournament_season": clean_text(
            fixture.get("tournament_season")
        ),
        "round": clean_text(fixture.get("tournament_round")),
        "player_1": player_1,
        "player_2": player_2,
        "first_player_key": safe_int(
            fixture.get("first_player_key")
        ),
        "second_player_key": safe_int(
            fixture.get("second_player_key")
        ),
        "winner_side": side,
        "winner": winner_name,
        "loser": loser_name,
        "final_result": clean_text(
            fixture.get("event_final_result")
            or fixture.get("final_result")
            or fixture.get("event_result")
        ),
        "scores": fixture.get("scores") or [],
        "raw_fixture": fixture,
    }


def load_existing_matches(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    matches = payload.get("matches") if isinstance(payload, dict) else None
    return matches if isinstance(matches, list) else []


def match_identity(match: dict[str, Any]) -> str:
    event_key = match.get("event_key")
    if event_key not in {None, ""}:
        return f"event:{event_key}"

    players = sorted(
        [
            clean_text(match.get("player_1")).lower(),
            clean_text(match.get("player_2")).lower(),
        ]
    )
    return "|".join(
        [
            clean_text(match.get("date")),
            clean_text(match.get("tournament")).lower(),
            *players,
        ]
    )


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")

    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    temporary.replace(path)


def summary_for(matches: list[dict[str, Any]]) -> dict[str, Any]:
    levels = Counter(match.get("tour_level") or "unknown" for match in matches)
    surfaces = Counter(match.get("surface") or "unknown" for match in matches)
    genders = Counter(match.get("gender") or "unknown" for match in matches)

    return {
        "matches_total": len(matches),
        "levels": dict(sorted(levels.items())),
        "surfaces": dict(sorted(surfaces.items())),
        "genders": dict(sorted(genders.items())),
        "level_unknown": levels.get("unknown", 0),
        "surface_unknown": surfaces.get("unknown", 0),
        "gender_unknown": genders.get("unknown", 0),
        "with_player_api_ids": sum(
            match.get("first_player_key") is not None
            and match.get("second_player_key") is not None
            for match in matches
        ),
    }


def main() -> None:
    local_today = datetime.now(ZoneInfo(TZ_NAME)).date()

    parser = argparse.ArgumentParser(
        description=(
            "Pobere zakljuÄene API-Tennis singles tekme za TLE backfill."
        )
    )
    parser.add_argument(
        "--from-date",
        type=parse_date,
        default=local_today - timedelta(days=14),
        help="ZaÄetni datum YYYY-MM-DD. Privzeto 14 dni nazaj.",
    )
    parser.add_argument(
        "--to-date",
        type=parse_date,
        default=local_today - timedelta(days=1),
        help="KonÄni datum YYYY-MM-DD. Privzeto vÄeraj.",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("TLE_RESULTS_OUTPUT", DEFAULT_OUTPUT),
    )
    parser.add_argument(
        "--report",
        default=os.getenv("TLE_RESULTS_REPORT", DEFAULT_REPORT),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Ne zdruÅ¾i z obstojeÄim arhivom, ampak ga zamenja.",
    )
    args = parser.parse_args()

    if args.from_date > args.to_date:
        parser.error("--from-date ne sme biti po --to-date.")

    output_path = Path(args.output)
    report_path = Path(args.report)

    existing = [] if args.replace else load_existing_matches(output_path)
    all_matches = {match_identity(match): match for match in existing}

    counters = Counter()
    skipped: list[dict[str, Any]] = []
    daily: list[dict[str, Any]] = []

    for day in date_range(args.from_date, args.to_date):
        fixtures = fetch_fixtures_for_date(day)
        day_added = 0
        day_finished_singles = 0

        counters["fixtures_total"] += len(fixtures)

        for fixture in fixtures:
            event_key = fixture.get("event_key")
            name = (
                f"{fixture.get('event_first_player')} - "
                f"{fixture.get('event_second_player')}"
            )

            if not is_singles(fixture):
                counters["skipped_not_singles"] += 1
                continue

            if is_rejected_result(fixture):
                counters["skipped_rejected_status"] += 1
                skipped.append(
                    {
                        "event_key": event_key,
                        "match": name,
                        "reason": "rejected_status",
                        "status": fixture.get("event_status"),
                    }
                )
                continue

            if not is_finished(fixture):
                counters["skipped_not_finished"] += 1
                continue

            day_finished_singles += 1
            record = build_record(fixture)

            if record["winner_side"] is None:
                counters["skipped_missing_winner"] += 1
                skipped.append(
                    {
                        "event_key": event_key,
                        "match": name,
                        "reason": "missing_or_unrecognized_winner",
                        "event_winner": fixture.get("event_winner"),
                        "status": fixture.get("event_status"),
                    }
                )
                continue

            if not record["final_result"]:
                counters["skipped_missing_result"] += 1
                skipped.append(
                    {
                        "event_key": event_key,
                        "match": name,
                        "reason": "missing_final_result",
                    }
                )
                continue

            identity = match_identity(record)
            if identity in all_matches:
                counters["duplicates"] += 1
                continue

            all_matches[identity] = record
            counters["added"] += 1
            day_added += 1

        daily.append(
            {
                "date": day.isoformat(),
                "fixtures": len(fixtures),
                "finished_singles": day_finished_singles,
                "added": day_added,
            }
        )
        print(
            f"{day}: fixtures={len(fixtures)} "
            f"finished_singles={day_finished_singles} added={day_added}"
        )

    matches = sorted(
        all_matches.values(),
        key=lambda item: (
            clean_text(item.get("date")),
            clean_text(item.get("time")),
            str(item.get("event_key") or ""),
        ),
    )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "requested_range": {
            "from_date": args.from_date.isoformat(),
            "to_date": args.to_date.isoformat(),
        },
        "summary": {
            **summary_for(matches),
            "existing_before_run": len(existing),
            "added_this_run": counters["added"],
            "duplicates_this_run": counters["duplicates"],
            "fixtures_seen_this_run": counters["fixtures_total"],
            "skipped_not_singles": counters["skipped_not_singles"],
            "skipped_not_finished": counters["skipped_not_finished"],
            "skipped_rejected_status": counters[
                "skipped_rejected_status"
            ],
            "skipped_missing_winner": counters[
                "skipped_missing_winner"
            ],
            "skipped_missing_result": counters[
                "skipped_missing_result"
            ],
        },
        "daily": daily,
        "matches": matches,
    }

    report = {
        "generated_at": payload["generated_at"],
        "requested_range": payload["requested_range"],
        "summary": payload["summary"],
        "daily": daily,
        "skipped_for_review": skipped,
        "unknown_level_matches": [
            match
            for match in matches
            if match.get("tour_level") == "unknown"
        ],
        "unknown_surface_matches": [
            match
            for match in matches
            if match.get("surface") == "unknown"
        ],
    }

    save_json(output_path, payload)
    save_json(report_path, report)

    print("")
    print("TLE RESULTS BACKFILL DONE")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter, defaultdict
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


SCHEMA_VERSION = 2

DEFAULT_OUTPUT = "data/tle/tle_api_results_backfill.json"
DEFAULT_REPORT = "data/tle/tle_api_results_backfill_report.json"
DEFAULT_METADATA = "data/tle/api_tournament_metadata.json"

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
    "walk over",
    "wo",
    "w/o",
    "retired",
}

REJECTED_RESULT_MARKERS = {
    "walkover",
    "walk over",
    "w/o",
    "retired",
    "cancelled",
    "canceled",
    "postponed",
    "interrupted",
    "abandoned",
}

TRUE_VALUES = {"1", "true", "yes", "y"}

VALID_LEVELS = {
    "main_tour",
    "challenger",
    "itf",
    "qualifying",
    "unknown",
}

VALID_SURFACES = {
    "hard",
    "clay",
    "grass",
    "carpet",
    "unknown",
}

VALID_GENDERS = {
    "men",
    "women",
    "unknown",
}


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


def lower_text(value: Any) -> str:
    return clean_text(value).lower()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ne morem prebrati JSON datoteke: {path}") from exc


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")

    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

        temporary.replace(path)
    except OSError as exc:
        if temporary.exists():
            temporary.unlink()
        raise RuntimeError(f"Ne morem zapisati datoteke: {path}") from exc


def normalized_status(fixture: dict[str, Any]) -> str:
    return lower_text(fixture.get("event_status"))


def result_text(fixture: dict[str, Any]) -> str:
    return clean_text(
        fixture.get("event_final_result")
        or fixture.get("final_result")
        or fixture.get("event_result")
    )


def is_finished(fixture: dict[str, Any]) -> bool:
    status = normalized_status(fixture)

    if status in FINISHED_STATUSES:
        return True

    winner = clean_text(
        fixture.get("event_winner")
        or fixture.get("winner")
    )

    return bool(
        result_text(fixture)
        and winner
        and not is_rejected_result(fixture)
    )


def is_rejected_result(fixture: dict[str, Any]) -> bool:
    status = normalized_status(fixture)

    # Status preverjamo kot celo vrednost. Ne uporabljamo substringa "wo",
    # ker bi ta napaÄno zadel besede kot "women".
    if status in REJECTED_STATUSES:
        return True

    result_blob = " ".join(
        [
            lower_text(fixture.get("event_final_result")),
            lower_text(fixture.get("event_result")),
        ]
    )

    return any(
        marker in result_blob
        for marker in REJECTED_RESULT_MARKERS
    )


def qualification_flag(fixture: dict[str, Any]) -> bool:
    raw = lower_text(fixture.get("event_qualification"))

    if raw in TRUE_VALUES:
        return True

    blob = " ".join(
        [
            lower_text(fixture.get("tournament_round")),
            lower_text(fixture.get("event_type_type")),
            lower_text(fixture.get("tournament_name")),
        ]
    )

    qualification_markers = (
        "qualification",
        "qualifying",
        "qualifier",
        " qual ",
        " q1",
        " q2",
        " q3",
    )

    return any(marker in f" {blob} " for marker in qualification_markers)


def normalize_tle_level(fixture: dict[str, Any]) -> str:
    if qualification_flag(fixture):
        return "qualifying"

    raw = tour_level(
        fixture.get("event_type_type"),
        fixture.get("tournament_name"),
    )

    if raw in {"grand_slam", "atp", "wta"}:
        return "main_tour"
    if raw == "challenger":
        return "challenger"
    if raw == "itf":
        return "itf"

    return "unknown"


def winner_side(fixture: dict[str, Any]) -> str | None:
    raw = lower_text(
        fixture.get("event_winner")
        or fixture.get("winner")
    )

    first_name = lower_text(fixture.get("event_first_player"))
    second_name = lower_text(fixture.get("event_second_player"))

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


def tournament_key_text(fixture: dict[str, Any]) -> str:
    key = safe_int(fixture.get("tournament_key"))
    return str(key) if key is not None else ""


def load_metadata(path: Path) -> dict[str, Any]:
    payload = load_json(path, {})

    if not isinstance(payload, dict):
        raise RuntimeError(
            f"Metadata mora biti JSON object: {path}"
        )

    tournaments = payload.get("tournaments")

    if tournaments is None:
        # Podpora tudi preprosti obliki:
        # {"123": {"surface": "clay", ...}}
        tournaments = {
            str(key): value
            for key, value in payload.items()
            if isinstance(value, dict)
        }

    if not isinstance(tournaments, dict):
        tournaments = {}

    return {
        "schema_version": payload.get("schema_version", 1),
        "updated_at": payload.get("updated_at"),
        "tournaments": tournaments,
    }


def metadata_value(
    metadata: dict[str, Any],
    fixture: dict[str, Any],
    field: str,
) -> str | None:
    key = tournament_key_text(fixture)

    if not key:
        return None

    entry = metadata.get("tournaments", {}).get(key)

    if not isinstance(entry, dict):
        return None

    value = lower_text(entry.get(field))

    allowed = {
        "surface": VALID_SURFACES,
        "gender": VALID_GENDERS,
        "tour_level": VALID_LEVELS,
    }.get(field)

    if not value or value == "unknown":
        return None

    if allowed is not None and value not in allowed:
        raise ValueError(
            f"Neveljaven metadata {field}={value!r} za tournament_key={key}"
        )

    return value


def resolve_surface(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[str, str]:
    override = metadata_value(metadata, fixture, "surface")

    if override:
        return override, "metadata"

    detected = normalize_surface(fixture)

    if detected in VALID_SURFACES - {"unknown"}:
        return detected, "fixture_or_fallback"

    return "unknown", "unknown"


def resolve_gender(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[str, str]:
    override = metadata_value(metadata, fixture, "gender")

    if override:
        return override, "metadata"

    detected = gender_from_event_type(
        fixture.get("event_type_type"),
        fixture.get("tournament_name"),
    )

    if detected in VALID_GENDERS - {"unknown"}:
        return detected, "event_type"

    return "unknown", "unknown"


def resolve_level(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[str, str]:
    # Qualifying ima vedno prednost pred roÄnim level overrideom.
    if qualification_flag(fixture):
        return "qualifying", "qualification"

    override = metadata_value(metadata, fixture, "tour_level")

    if override:
        return override, "metadata"

    detected = normalize_tle_level(fixture)

    if detected in VALID_LEVELS - {"unknown"}:
        return detected, "event_type"

    return "unknown", "unknown"


def fetch_fixtures_for_date(day: date) -> list[dict[str, Any]]:
    day_text = day.isoformat()

    payload = api_call(
        {
            "method": "get_fixtures",
            "date_start": day_text,
            "date_stop": day_text,
            "timezone": TZ_NAME,
        }
    )

    time.sleep(API_SLEEP_SECONDS)

    if payload.get("success") != 1:
        return []

    result = payload.get("result") or []
    return result if isinstance(result, list) else []


def fixture_metadata_debug(
    fixture: dict[str, Any],
) -> dict[str, Any]:
    markers = (
        "surface",
        "court",
        "ground",
        "floor",
        "indoor",
        "outdoor",
        "type",
        "tournament",
        "league",
        "round",
        "season",
        "qualification",
    )

    return {
        str(key): value
        for key, value in fixture.items()
        if any(marker in str(key).lower() for marker in markers)
    }


def build_record(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    tournament = clean_text(fixture.get("tournament_name"))
    event_type = clean_text(fixture.get("event_type_type"))

    gender, gender_source = resolve_gender(fixture, metadata)
    surface, surface_source = resolve_surface(fixture, metadata)
    level, level_source = resolve_level(fixture, metadata)

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
        "gender_source": gender_source,
        "tour_level": level,
        "tour_level_source": level_source,
        "surface": surface,
        "surface_source": surface_source,
        "qualification": qualification_flag(fixture),
        "is_grand_slam": is_grand_slam(tournament),
        "indoor": infer_indoor(fixture),
        "best_of": infer_best_of(fixture, gender, tournament),
        "event_type": event_type,
        "tournament": tournament,
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
        "final_result": result_text(fixture),
        "scores": fixture.get("scores") or [],
        "fixture_metadata_debug": fixture_metadata_debug(fixture),
        "raw_fixture": fixture,
    }


def load_existing_matches(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path, {})

    if not isinstance(payload, dict):
        return []

    matches = payload.get("matches")
    return matches if isinstance(matches, list) else []


def match_identity(match: dict[str, Any]) -> str:
    event_key = match.get("event_key")

    if event_key not in {None, ""}:
        return f"event:{event_key}"

    players = sorted(
        [
            lower_text(match.get("player_1")),
            lower_text(match.get("player_2")),
        ]
    )

    return "|".join(
        [
            clean_text(match.get("date")),
            lower_text(match.get("tournament")),
            *players,
        ]
    )


def summary_for(matches: list[dict[str, Any]]) -> dict[str, Any]:
    levels = Counter(
        match.get("tour_level") or "unknown"
        for match in matches
    )

    surfaces = Counter(
        match.get("surface") or "unknown"
        for match in matches
    )

    genders = Counter(
        match.get("gender") or "unknown"
        for match in matches
    )

    surface_sources = Counter(
        match.get("surface_source") or "unknown"
        for match in matches
    )

    gender_sources = Counter(
        match.get("gender_source") or "unknown"
        for match in matches
    )

    return {
        "matches_total": len(matches),
        "levels": dict(sorted(levels.items())),
        "surfaces": dict(sorted(surfaces.items())),
        "genders": dict(sorted(genders.items())),
        "surface_sources": dict(sorted(surface_sources.items())),
        "gender_sources": dict(sorted(gender_sources.items())),
        "level_unknown": levels.get("unknown", 0),
        "surface_unknown": surfaces.get("unknown", 0),
        "gender_unknown": genders.get("unknown", 0),
        "with_player_api_ids": sum(
            match.get("first_player_key") is not None
            and match.get("second_player_key") is not None
            for match in matches
        ),
    }


def tournament_summary(
    matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for match in matches:
        key = str(match.get("tournament_key") or "")
        grouped[key].append(match)

    rows: list[dict[str, Any]] = []

    for key, group in grouped.items():
        names = Counter(
            clean_text(match.get("tournament"))
            for match in group
        )

        event_types = Counter(
            clean_text(match.get("event_type"))
            for match in group
        )

        levels = Counter(
            match.get("tour_level") or "unknown"
            for match in group
        )

        surfaces = Counter(
            match.get("surface") or "unknown"
            for match in group
        )

        genders = Counter(
            match.get("gender") or "unknown"
            for match in group
        )

        row = {
            "tournament_key": safe_int(key),
            "tournament": names.most_common(1)[0][0] if names else "",
            "event_type": (
                event_types.most_common(1)[0][0]
                if event_types
                else ""
            ),
            "matches": len(group),
            "tour_levels": dict(levels),
            "surfaces": dict(surfaces),
            "genders": dict(genders),
            "needs_surface": surfaces.get("unknown", 0) > 0,
            "needs_gender": genders.get("unknown", 0) > 0,
            "sample_event_key": group[0].get("event_key"),
            "sample_metadata": group[0].get(
                "fixture_metadata_debug",
                {},
            ),
        }

        rows.append(row)

    return sorted(
        rows,
        key=lambda row: (
            not row["needs_surface"],
            not row["needs_gender"],
            -row["matches"],
            row["tournament"],
        ),
    )


def update_metadata_catalog(
    metadata: dict[str, Any],
    tournament_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    tournaments = dict(metadata.get("tournaments") or {})

    for row in tournament_rows:
        key = row.get("tournament_key")

        if key is None:
            continue

        key_text = str(key)
        old = tournaments.get(key_text)
        entry = dict(old) if isinstance(old, dict) else {}

        entry["name"] = row.get("tournament")
        entry["event_type"] = row.get("event_type")
        entry["matches_seen"] = row.get("matches")
        entry["last_seen_at"] = now_iso()

        level_counts = row.get("tour_levels") or {}
        known_levels = [
            value
            for value in level_counts
            if value != "unknown"
        ]
        if not entry.get("tour_level") and len(known_levels) == 1:
            entry["tour_level"] = known_levels[0]

        surface_counts = row.get("surfaces") or {}
        known_surfaces = [
            value
            for value in surface_counts
            if value != "unknown"
        ]
        if not entry.get("surface"):
            entry["surface"] = (
                known_surfaces[0]
                if len(known_surfaces) == 1
                else "unknown"
            )

        gender_counts = row.get("genders") or {}
        known_genders = [
            value
            for value in gender_counts
            if value != "unknown"
        ]
        if not entry.get("gender"):
            entry["gender"] = (
                known_genders[0]
                if len(known_genders) == 1
                else "unknown"
            )

        entry["needs_review"] = bool(
            entry.get("surface") in {None, "", "unknown"}
            or entry.get("gender") in {None, "", "unknown"}
        )

        tournaments[key_text] = entry

    return {
        "schema_version": 1,
        "updated_at": now_iso(),
        "instructions": {
            "surface": "Allowed: hard, clay, grass, carpet, unknown",
            "gender": "Allowed: men, women, unknown",
            "tour_level": (
                "Allowed: main_tour, challenger, itf, "
                "qualifying, unknown"
            ),
            "note": (
                "RoÄno popravi samo surface/gender/tour_level. "
                "Naslednji zagon backfilla bo te vrednosti uporabil."
            ),
        },
        "tournaments": dict(
            sorted(
                tournaments.items(),
                key=lambda item: (
                    not bool(item[1].get("needs_review")),
                    -int(item[1].get("matches_seen") or 0),
                    str(item[1].get("name") or ""),
                ),
            )
        ),
    }


def main() -> None:
    local_today = datetime.now(ZoneInfo(TZ_NAME)).date()

    parser = argparse.ArgumentParser(
        description=(
            "Pobere zakljuÄene API-Tennis singles tekme za TLE backfill "
            "in izdela tournament metadata katalog."
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
        "--metadata",
        default=os.getenv(
            "TLE_TOURNAMENT_METADATA",
            DEFAULT_METADATA,
        ),
    )

    parser.add_argument(
        "--replace",
        action="store_true",
        help="Zamenjaj obstojeÄi backfill arhiv.",
    )

    args = parser.parse_args()

    if args.from_date > args.to_date:
        parser.error("--from-date ne sme biti po --to-date.")

    output_path = Path(args.output)
    report_path = Path(args.report)
    metadata_path = Path(args.metadata)

    metadata = load_metadata(metadata_path)

    existing = (
        []
        if args.replace
        else load_existing_matches(output_path)
    )

    all_matches = {
        match_identity(match): match
        for match in existing
    }

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
            match_name = (
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
                        "match": match_name,
                        "reason": "rejected_status",
                        "status": fixture.get("event_status"),
                        "result": result_text(fixture),
                    }
                )
                continue

            if not is_finished(fixture):
                counters["skipped_not_finished"] += 1
                continue

            day_finished_singles += 1
            record = build_record(fixture, metadata)

            if record["winner_side"] is None:
                counters["skipped_missing_winner"] += 1
                skipped.append(
                    {
                        "event_key": event_key,
                        "match": match_name,
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
                        "match": match_name,
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
            f"finished_singles={day_finished_singles} "
            f"added={day_added}"
        )

    matches = sorted(
        all_matches.values(),
        key=lambda item: (
            clean_text(item.get("date")),
            clean_text(item.get("time")),
            str(item.get("event_key") or ""),
        ),
    )

    summary = {
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
    }

    tournaments = tournament_summary(matches)

    metadata_payload = update_metadata_catalog(
        metadata,
        tournaments,
    )

    unknown_surface_tournaments = [
        row
        for row in tournaments
        if row["needs_surface"]
    ]

    unknown_gender_tournaments = [
        row
        for row in tournaments
        if row["needs_gender"]
    ]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "requested_range": {
            "from_date": args.from_date.isoformat(),
            "to_date": args.to_date.isoformat(),
        },
        "settings": {
            "metadata_path": str(metadata_path),
            "replace": args.replace,
        },
        "summary": summary,
        "daily": daily,
        "matches": matches,
    }

    report = {
        "generated_at": payload["generated_at"],
        "requested_range": payload["requested_range"],
        "summary": summary,
        "daily": daily,
        "tournaments_total": len(tournaments),
        "tournaments": tournaments,
        "unknown_surface_tournaments": unknown_surface_tournaments,
        "unknown_gender_tournaments": unknown_gender_tournaments,
        "skipped_for_review": skipped,
    }

    save_json(output_path, payload)
    save_json(report_path, report)
    save_json(metadata_path, metadata_payload)

    print("")
    print("TLE RESULTS BACKFILL DONE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("")
    print(
        "Unknown-surface tournaments:",
        len(unknown_surface_tournaments),
    )
    print(
        "Unknown-gender tournaments:",
        len(unknown_gender_tournaments),
    )
    print(f"Output:   {output_path}")
    print(f"Report:   {report_path}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()

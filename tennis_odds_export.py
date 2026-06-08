import json
import os
import re
import time
from datetime import datetime, timedelta
from statistics import median
from typing import Any
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = os.getenv("TZ_NAME", "Europe/Ljubljana")
SCHEMA_VERSION = 2

DATA_DIR = os.getenv("TENNIS_ODDS_DATA_DIR", "data")
OUTPUT_FILE = os.getenv(
    "TENNIS_ODDS_OUTPUT_FILE",
    f"{DATA_DIR}/tennis_odds_today.json",
)
DEBUG_FILE = os.getenv(
    "TENNIS_ODDS_DEBUG_FILE",
    f"{DATA_DIR}/tennis_odds_export_debug.json",
)

DAYS_AHEAD = int(os.getenv("TENNIS_ODDS_DAYS_AHEAD", "1"))
MAX_FIXTURES = int(os.getenv("TENNIS_ODDS_MAX_FIXTURES", "650"))
REQUEST_TIMEOUT = int(os.getenv("TENNIS_ODDS_REQUEST_TIMEOUT", "30"))
API_SLEEP_SECONDS = float(os.getenv("TENNIS_ODDS_API_SLEEP_SECONDS", "0.30"))
SAVE_RAW_MARKETS = os.getenv("TENNIS_ODDS_SAVE_RAW_MARKETS", "1") == "1"
SAVE_RAW_FIXTURE = os.getenv("TENNIS_ODDS_SAVE_RAW_FIXTURE", "1") == "1"

BAD_STATUSES = {
    "finished",
    "cancelled",
    "canceled",
    "postponed",
    "retired",
    "walkover",
    "interrupted",
    "abandoned",
}


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def today_local():
    return datetime.now(ZoneInfo(TZ_NAME)).date()


def save_json(path: str, payload: Any) -> None:
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        number = float(str(value).replace(",", "."))
        return number
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def api_call(params: dict[str, Any], retries: int = 3) -> dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("Missing API_KEY environment variable.")

    request_params = dict(params)
    request_params["APIkey"] = API_KEY

    for attempt in range(retries):
        response = requests.get(
            BASE_URL,
            params=request_params,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code in {429, 500, 502, 503, 504}:
            wait_seconds = 3 * (attempt + 1)
            print(
                f"API retry {response.status_code}; "
                f"sleeping {wait_seconds}s"
            )
            time.sleep(wait_seconds)
            continue

        if response.status_code >= 400:
            raise RuntimeError(
                f"HTTP {response.status_code}: {response.text[:500]}"
            )

        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    raise RuntimeError("API request failed after retries.")


def fetch_fixtures_for_date(date_value) -> list[dict[str, Any]]:
    date_text = date_value.strftime("%Y-%m-%d")
    payload = api_call(
        {
            "method": "get_fixtures",
            "date_start": date_text,
            "date_stop": date_text,
        }
    )
    time.sleep(API_SLEEP_SECONDS)

    if payload.get("success") != 1:
        return []

    result = payload.get("result") or []
    return result if isinstance(result, list) else []


def fetch_odds(event_key: Any) -> dict[str, Any]:
    payload = api_call(
        {
            "method": "get_odds",
            "event_key": event_key,
        }
    )
    time.sleep(API_SLEEP_SECONDS)

    if payload.get("success") != 1:
        return {}

    result = payload.get("result") or {}

    if not isinstance(result, dict):
        return {}

    return (
        result.get(str(event_key))
        or result.get(safe_int(event_key))
        or {}
    )


def is_pregame(match: dict[str, Any]) -> bool:
    status = str(match.get("event_status") or "").strip().lower()
    live = str(match.get("event_live") or "0").strip()

    if live == "1":
        return False

    return status not in BAD_STATUSES


def is_singles(match: dict[str, Any]) -> bool:
    event_type = str(match.get("event_type_type") or "").lower()
    player_1 = str(match.get("event_first_player") or "")
    player_2 = str(match.get("event_second_player") or "")

    if "/" in player_1 or "/" in player_2:
        return False

    if "double" in event_type:
        return False

    return "single" in event_type


def normalize_player_key(name: Any) -> str:
    value = str(name or "").lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def text_blob(*values: Any) -> str:
    return " ".join(str(value or "") for value in values).lower()


def direct_fixture_values(
    fixture: dict[str, Any],
    markers: tuple[str, ...],
) -> list[Any]:
    values = []

    for key, value in fixture.items():
        lower = str(key).lower()

        if any(marker in lower for marker in markers):
            values.append(value)

    return values


def tour_level(event_type: Any, tournament: Any = None) -> str:
    value = text_blob(event_type, tournament)

    if "grand slam" in value:
        return "grand_slam"
    if any(name in value for name in (
        "australian open",
        "french open",
        "roland garros",
        "wimbledon",
        "us open",
        "u.s. open",
    )):
        return "grand_slam"
    if "challenger" in value:
        return "challenger"
    if "itf" in value:
        return "itf"
    if "wta" in value:
        return "wta"
    if "atp" in value:
        return "atp"
    if "junior" in value:
        return "junior"

    return "unknown"


def gender_from_event_type(event_type: Any, tournament: Any = None) -> str:
    value = text_blob(event_type, tournament)

    if any(marker in value for marker in (
        "women",
        "woman",
        "female",
        "wta",
        "Å¾enski",
        "zene",
    )):
        return "women"

    if any(marker in value for marker in (
        "men",
        "male",
        "atp",
        "muÅ¡ki",
        "muski",
    )):
        return "men"

    return "unknown"


SURFACE_ALIASES = {
    "clay": (
        "clay",
        "red clay",
        "green clay",
        "zemlja",
        "terre battue",
    ),
    "grass": (
        "grass",
        "trava",
        "lawn",
    ),
    "hard": (
        "hard",
        "hardcourt",
        "hard court",
        "cement",
        "acrylic",
    ),
    "carpet": (
        "carpet",
        "tepih",
    ),
}

# Stable tournament fallbacks for cases where API fixture metadata does not
# expose a dedicated surface field.
TOURNAMENT_KEY_SURFACES = {
    12571: "grass",  # London WTA
    3137: "clay",    # Bratislava Challenger
    13955: "clay",   # Cattolica Challenger
    2389: "clay",    # Lyon Challenger
    10890: "clay",   # San Miguel de Tucuman Challenger
    12576: "clay",   # M15 Messina
    13956: "clay",   # Modena Challenger Women
}

TOURNAMENT_SURFACE_FALLBACKS = {
    "australian open": "hard",
    "french open": "clay",
    "roland garros": "clay",
    "wimbledon": "grass",
    "us open": "hard",
    "u.s. open": "hard",
    "stuttgart": "grass",
    "s-hertogenbosch": "grass",
    "hertogenbosch": "grass",
    "ilkley": "grass",
    "queens club": "grass",
    "queen's club": "grass",
    "halle": "grass",
    "eastbourne": "grass",
    "nottingham": "grass",
    "berlin": "grass",
    "bad homburg": "grass",
}


def normalize_surface(fixture: dict[str, Any]) -> str:
    direct_values = direct_fixture_values(
        fixture,
        ("surface", "court", "ground", "floor"),
    )

    candidates = [
        *direct_values,
        fixture.get("event_type_type"),
        fixture.get("tournament_name"),
        fixture.get("tournament_season"),
        fixture.get("league_name"),
    ]
    value = text_blob(*candidates)

    for canonical, aliases in SURFACE_ALIASES.items():
        if any(alias in value for alias in aliases):
            return canonical

    tournament = text_blob(fixture.get("tournament_name"))

    for marker, surface in TOURNAMENT_SURFACE_FALLBACKS.items():
        if marker in tournament:
            return surface

    tournament_key = safe_int(fixture.get("tournament_key"))

    if tournament_key in TOURNAMENT_KEY_SURFACES:
        return TOURNAMENT_KEY_SURFACES[tournament_key]

    return "unknown"


def infer_indoor(fixture: dict[str, Any]) -> bool | None:
    values = direct_fixture_values(
        fixture,
        ("indoor", "outdoor", "court", "surface", "ground"),
    )
    value = text_blob(*values, fixture.get("event_type_type"))

    if "indoor" in value:
        return True

    if "outdoor" in value:
        return False

    return None


def is_grand_slam(tournament: Any) -> bool:
    value = text_blob(tournament)

    return any(name in value for name in (
        "australian open",
        "french open",
        "roland garros",
        "wimbledon",
        "us open",
        "u.s. open",
    ))


def infer_best_of(
    fixture: dict[str, Any],
    gender: str,
    tournament: Any,
) -> int:
    for key, value in fixture.items():
        lower = str(key).lower()

        if "best" in lower and ("set" in lower or "of" in lower):
            parsed = safe_int(value)

            if parsed in {3, 5}:
                return parsed

    if is_grand_slam(tournament) and gender == "men":
        return 5

    return 3


def fixture_metadata_debug(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        str(key): value
        for key, value in fixture.items()
        if any(
            marker in str(key).lower()
            for marker in (
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
                "best",
                "set",
            )
        )
    }


def collect_books(obj: Any) -> dict[str, float]:
    books: dict[str, float] = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            direct = safe_float(value)

            if direct is not None and direct > 1:
                books[str(key)] = round(direct, 4)
                continue

            if isinstance(value, dict):
                bookmaker = (
                    value.get("bookmaker")
                    or value.get("bookmaker_name")
                    or value.get("bookmaker_key")
                    or key
                )
                odd_value = (
                    value.get("odd")
                    or value.get("odds")
                    or value.get("value")
                    or value.get("price")
                )
                odd = safe_float(odd_value)

                if bookmaker and odd is not None and odd > 1:
                    books[str(bookmaker)] = round(odd, 4)

    elif isinstance(obj, list):
        for item in obj:
            if not isinstance(item, dict):
                continue

            bookmaker = (
                item.get("bookmaker")
                or item.get("bookmaker_name")
                or item.get("bookmaker_key")
                or item.get("name")
            )
            odd_value = (
                item.get("odd")
                or item.get("odds")
                or item.get("value")
                or item.get("price")
            )
            odd = safe_float(odd_value)

            if bookmaker and odd is not None and odd > 1:
                books[str(bookmaker)] = round(odd, 4)

    return books


def books_summary(books: dict[str, float]) -> dict[str, Any] | None:
    valid = {
        str(book): float(odd)
        for book, odd in books.items()
        if safe_float(odd) is not None and float(odd) > 1
    }

    if not valid:
        return None

    best_bookmaker = max(valid, key=valid.get)
    values = list(valid.values())

    return {
        "best_odds": round(valid[best_bookmaker], 4),
        "best_bookmaker": best_bookmaker,
        "median_odds": round(median(values), 4),
        "bookmakers_count": len(valid),
        "books": valid,
    }


def parse_match_winner(odds_blob: dict[str, Any]) -> dict[str, Any] | None:
    possible_names = [
        "Home/Away",
        "Match Winner",
        "Winner",
        "To Win Match",
    ]

    market = None
    market_name = ""

    for name in possible_names:
        candidate = odds_blob.get(name)
        if isinstance(candidate, dict):
            market = candidate
            market_name = name
            break

    if not isinstance(market, dict):
        return None

    home_raw = (
        market.get("Home")
        or market.get("Player 1")
        or market.get("First Player")
        or market.get("1")
    )
    away_raw = (
        market.get("Away")
        or market.get("Player 2")
        or market.get("Second Player")
        or market.get("2")
    )

    home = books_summary(collect_books(home_raw))
    away = books_summary(collect_books(away_raw))

    if not home or not away:
        return None

    raw_p1 = 1.0 / home["median_odds"]
    raw_p2 = 1.0 / away["median_odds"]
    total = raw_p1 + raw_p2

    p1_fair = raw_p1 / total if total else 0.5
    p2_fair = raw_p2 / total if total else 0.5

    return {
        "source_market": market_name,
        "player_1": home,
        "player_2": away,
        "de_vig": {
            "player_1_probability": round(p1_fair, 6),
            "player_2_probability": round(p2_fair, 6),
            "favorite_side": "player_1" if p1_fair >= p2_fair else "player_2",
            "favorite_probability": round(max(p1_fair, p2_fair), 6),
        },
    }


def extract_line(text: Any) -> float | None:
    value = str(text or "")

    # Remove ordinal numbers such as "1st" so they are not
    # incorrectly interpreted as a totals line of 1.0.
    value = re.sub(
        r"\b\d+(?:st|nd|rd|th)\b",
        "",
        value,
        flags=re.IGNORECASE,
    )

    match = re.search(
        r"(?<!\d)(\d{1,2}(?:[.,]\d+)?)(?!\d)",
        value,
    )

    if not match:
        return None

    return safe_float(match.group(1).replace(",", "."))


def side_from_text(text: Any) -> str | None:
    value = str(text or "").strip().lower()

    # Market labels can contain both words, for example:
    # "Over/Under (1st Set) Under".
    # The last occurrence is the actual selection.
    selections = re.findall(r"\b(over|under)\b", value)

    if selections:
        return selections[-1]

    if value in {"yes", "no"}:
        return value

    return None


def parse_over_under_market(
    market_name: str,
    market: Any,
) -> dict[str, Any]:
    by_line: dict[str, dict[str, Any]] = {}

    def add(line: float | None, side: str | None, obj: Any) -> None:
        if line is None or side not in {"over", "under"}:
            return

        books = collect_books(obj)
        summary = books_summary(books)

        if not summary:
            return

        line_key = f"{line:.1f}"
        by_line.setdefault(line_key, {"line": line})
        by_line[line_key][side] = summary

    if not isinstance(market, dict):
        return {}

    for key, value in market.items():
        key_side = side_from_text(key)
        key_line = extract_line(key)

        if key_side in {"over", "under"} and key_line is not None:
            add(key_line, key_side, value)

        if isinstance(value, dict):
            # Shape: Over -> line -> books
            if key_side in {"over", "under"}:
                for nested_key, nested_value in value.items():
                    nested_line = extract_line(nested_key)
                    add(nested_line, key_side, nested_value)

            # Shape: line -> Over/Under -> books
            if key_line is not None:
                for nested_key, nested_value in value.items():
                    nested_side = side_from_text(nested_key)
                    add(key_line, nested_side, nested_value)

            # Shape: market-name-over -> line -> books
            for nested_key, nested_value in value.items():
                nested_side = side_from_text(nested_key)
                nested_line = extract_line(nested_key)

                if nested_side in {"over", "under"} and nested_line is not None:
                    add(nested_line, nested_side, nested_value)

    completed = {
        line_key: item
        for line_key, item in by_line.items()
        if item.get("over") or item.get("under")
    }

    return {
        "source_market": market_name,
        "lines": completed,
    } if completed else {}


def parse_yes_no_market(
    market_name: str,
    market: Any,
) -> dict[str, Any]:
    if not isinstance(market, dict):
        return {}

    result: dict[str, Any] = {"source_market": market_name}

    for key, value in market.items():
        normalized = str(key or "").strip().lower()

        if normalized in {"yes", "no"}:
            summary = books_summary(collect_books(value))
            if summary:
                result[normalized] = summary

    return result if len(result) > 1 else {}


def classify_market(name: str) -> str:
    value = name.lower()

    if any(x in value for x in ["home/away", "match winner", "to win match"]):
        return "match_winner"

    if "first set" in value or "1st set" in value:
        if "tie" in value and "break" in value:
            return "first_set_tiebreak"
        if "total" in value or "over/under" in value or "games" in value:
            return "first_set_total_games"
        if "winner" in value:
            return "first_set_winner"

    if "tie" in value and "break" in value:
        return "match_tiebreak"

    if "total sets" in value or "sets total" in value:
        return "total_sets"

    if "over/under" in value and "games" in value:
        return "match_total_games"

    if "player" in value and "total" in value and "games" in value:
        return "player_total_games"

    if "game handicap" in value or "handicap by games" in value:
        return "game_handicap"

    if "set handicap" in value or "handicap by sets" in value:
        return "set_handicap"

    if "correct score" in value or "exact score" in value:
        return "correct_score"

    return "unmapped"


def normalize_markets(odds_blob: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "match_winner": parse_match_winner(odds_blob),
        "match_total_games": [],
        "first_set_total_games": [],
        "total_sets": [],
        "match_tiebreak": [],
        "first_set_tiebreak": [],
        "player_total_games": [],
        "game_handicap": [],
        "set_handicap": [],
        "correct_score": [],
        "first_set_winner": [],
        "unmapped": [],
    }

    for market_name, market_data in odds_blob.items():
        category = classify_market(str(market_name))

        if category == "match_winner":
            continue

        if category in {
            "match_total_games",
            "first_set_total_games",
            "total_sets",
            "player_total_games",
            "game_handicap",
            "set_handicap",
        }:
            parsed = parse_over_under_market(str(market_name), market_data)

        elif category in {"match_tiebreak", "first_set_tiebreak"}:
            parsed = parse_yes_no_market(str(market_name), market_data)

        else:
            parsed = {}

        if parsed:
            normalized[category].append(parsed)
        else:
            normalized["unmapped"].append(
                {
                    "market_name": str(market_name),
                    "classified_as": category,
                }
            )

    # Remove empty containers to keep output smaller.
    return {
        key: value
        for key, value in normalized.items()
        if value not in [None, [], {}]
    }


def match_record(
    fixture: dict[str, Any],
    odds_blob: dict[str, Any],
) -> dict[str, Any]:
    player_1 = fixture.get("event_first_player")
    player_2 = fixture.get("event_second_player")
    event_type = fixture.get("event_type_type")
    tournament = fixture.get("tournament_name")
    gender = gender_from_event_type(event_type, tournament)
    surface = normalize_surface(fixture)
    level = tour_level(event_type, tournament)

    record = {
        "schema_version": SCHEMA_VERSION,
        "event_key": fixture.get("event_key"),
        "event_id": str(fixture.get("event_key") or ""),
        "date": fixture.get("event_date"),
        "time": fixture.get("event_time"),
        "timezone": TZ_NAME,
        "status": fixture.get("event_status"),
        "live": str(fixture.get("event_live") or "0") == "1",
        "player_1": player_1,
        "player_2": player_2,
        "player_1_key": normalize_player_key(player_1),
        "player_2_key": normalize_player_key(player_2),
        "first_player_key": safe_int(fixture.get("first_player_key")),
        "second_player_key": safe_int(fixture.get("second_player_key")),
        "tournament": tournament,
        "tournament_key": fixture.get("tournament_key"),
        "tournament_season": fixture.get("tournament_season"),
        "round": fixture.get("tournament_round"),
        "event_type": event_type,
        "tour_level": level,
        "gender": gender,
        "surface": surface,
        "indoor": infer_indoor(fixture),
        "best_of": infer_best_of(fixture, gender, tournament),
        "is_grand_slam": is_grand_slam(tournament),
        "qualification": str(
            fixture.get("event_qualification") or ""
        ).lower() == "true",
        "available_markets": list(odds_blob.keys()),
        "markets": normalize_markets(odds_blob),
        "fixture_metadata_debug": fixture_metadata_debug(fixture),
    }

    if SAVE_RAW_FIXTURE:
        record["raw_fixture"] = fixture

    if SAVE_RAW_MARKETS:
        record["raw_markets"] = odds_blob

    return record


def main() -> None:
    ensure_dirs()

    fixtures: list[dict[str, Any]] = []
    start = today_local()

    for offset in range(DAYS_AHEAD):
        day = start + timedelta(days=offset)
        daily = fetch_fixtures_for_date(day)
        print(f"FIXTURES {day}: {len(daily)}")
        fixtures.extend(daily)

    fixtures = fixtures[:MAX_FIXTURES]

    matches: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for fixture in fixtures:
        event_key = fixture.get("event_key")
        match_name = (
            f"{fixture.get('event_first_player')} - "
            f"{fixture.get('event_second_player')}"
        )

        if not event_key:
            skipped.append(
                {"match": match_name, "reason": "missing_event_key"}
            )
            continue

        if not is_pregame(fixture):
            skipped.append(
                {
                    "event_key": event_key,
                    "match": match_name,
                    "reason": "not_pregame",
                }
            )
            continue

        if not is_singles(fixture):
            skipped.append(
                {
                    "event_key": event_key,
                    "match": match_name,
                    "reason": "not_singles",
                }
            )
            continue

        try:
            odds_blob = fetch_odds(event_key)

            if not odds_blob:
                skipped.append(
                    {
                        "event_key": event_key,
                        "match": match_name,
                        "reason": "no_odds",
                    }
                )
                continue

            record = match_record(fixture, odds_blob)
            matches.append(record)

            print(
                f"ODDS {event_key}: {match_name} "
                f"markets={len(record['available_markets'])}"
            )

        except Exception as exc:
            errors.append(
                {
                    "event_key": event_key,
                    "match": match_name,
                    "error": str(exc),
                }
            )
            print(f"ERROR {event_key} {match_name}: {exc}")

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source": "API-Tennis",
        "settings": {
            "days_ahead": DAYS_AHEAD,
            "max_fixtures": MAX_FIXTURES,
            "save_raw_markets": SAVE_RAW_MARKETS,
            "save_raw_fixture": SAVE_RAW_FIXTURE,
        },
        "summary": {
            "fixtures_total": len(fixtures),
            "matches_with_odds": len(matches),
            "skipped": len(skipped),
            "errors": len(errors),
            "first_set_total_matches": sum(
                bool(
                    (match.get("markets") or {}).get(
                        "first_set_total_games"
                    )
                )
                for match in matches
            ),
            "match_total_matches": sum(
                bool(
                    (match.get("markets") or {}).get(
                        "match_total_games"
                    )
                )
                for match in matches
            ),
            "with_surface": sum(
                match.get("surface") not in {"", "unknown", None}
                for match in matches
            ),
            "with_gender": sum(
                match.get("gender") not in {"", "unknown", None}
                for match in matches
            ),
            "with_best_of": sum(
                match.get("best_of") in {3, 5}
                for match in matches
            ),
            "tiebreak_market_matches": sum(
                bool(
                    (match.get("markets") or {}).get(
                        "match_tiebreak"
                    )
                    or (match.get("markets") or {}).get(
                        "first_set_tiebreak"
                    )
                )
                for match in matches
            ),
        },
        "matches": matches,
    }

    debug = {
        "generated_at": now_iso(),
        "summary": payload["summary"],
        "skipped": skipped,
        "errors": errors,
        "market_names": sorted(
            {
                market_name
                for match in matches
                for market_name in match.get("available_markets", [])
            }
        ),
    }

    save_json(OUTPUT_FILE, payload)
    save_json(DEBUG_FILE, debug)

    print("")
    print("TENNIS ODDS EXPORT DONE")
    print(payload["summary"])
    print(f"Output: {OUTPUT_FILE}")
    print(f"Debug:  {DEBUG_FILE}")
    print("")


if __name__ == "__main__":
    main()

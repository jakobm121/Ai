from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import re
import statistics
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests

from urllib.request import urlopen
from io import BytesIO
from zoneinfo import ZoneInfo

ROOT_DIR = Path(".")
API_BASE_URL = "https://api.api-tennis.com/tennis/"
TLE_RAW_BASE = "https://raw.githubusercontent.com/jakobm121/Tennis-ELO/refs/heads/main/"

DEFAULT_CANONICAL_MANIFEST = TLE_RAW_BASE + "data/tle/processed/canonical/tle_matches_manifest.json"
DEFAULT_API_PLAYER_MAPPING = TLE_RAW_BASE + "data/tle/mappings/api_player_to_sackmann.json"
DEFAULT_TOURNAMENT_METADATA = TLE_RAW_BASE + "data/tle/mappings/api_tournament_metadata.json"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data" / "tle" / "predictions"

DEFAULT_ELO = 1500.0
GLOBAL_K = 24.0
GLOBAL_SURFACE_K = 20.0
LEVEL_K = 24.0
LEVEL_SURFACE_K = 20.0

VALID_SURFACES = {"hard", "clay", "grass", "carpet"}
MAIN_TOUR_LEVELS = {"atp_wta", "grand_slam", "main_tour"}
SUPPORTED_SCAN_LEVELS = {"itf", "challenger", "atp_wta", "grand_slam"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalize_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def surname_initial_key(value: Any) -> str:
    tokens = normalize_name(value).split()
    if len(tokens) < 2:
        return ""
    return f"{tokens[-1]}|{tokens[0][:1]}"


def parse_date(value: Any) -> date | None:
    text = clean(value)
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 1.0:
        return None
    return number


def safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load_json(path_or_url: str | Path) -> Any:
    text = str(path_or_url)
    if text.startswith("http://") or text.startswith("https://"):
        with urlopen(text, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    path = Path(text)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_jsonl_gz(path_or_url: str | Path):
    text = str(path_or_url)
    if text.startswith("http://") or text.startswith("https://"):
        with urlopen(text, timeout=180) as response:
            data = response.read()
        handle = gzip.open(BytesIO(data), "rt", encoding="utf-8")
    else:
        path = Path(text)
        if not path.is_absolute():
            path = ROOT_DIR / path
        handle = gzip.open(path, "rt", encoding="utf-8")
    with handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def api_get(api_key: str, params: dict[str, Any], sleep_seconds: float = 0.0) -> dict[str, Any]:
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    response = requests.get(
        API_BASE_URL,
        params={"APIkey": api_key, **params},
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, dict):
        raise RuntimeError(f"API response is not object for params={params}")

    return payload


def result_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result")

    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]

    if isinstance(result, dict):
        return [item for item in result.values() if isinstance(item, dict)]

    return []


def event_key_text(value: Any) -> str:
    return clean(value)


def fixture_index(fixtures_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in result_list(fixtures_payload):
        key = event_key_text(row.get("event_key"))
        if key:
            out[key] = row
    return out


def odds_index(odds_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = odds_payload.get("result")
    if not isinstance(result, dict):
        return {}

    out = {}
    for event_key, markets in result.items():
        if isinstance(markets, dict):
            out[event_key_text(event_key)] = markets
    return out


def get_home_away_market(markets: dict[str, Any]) -> dict[str, Any] | None:
    market = markets.get("Home/Away")
    if not isinstance(market, dict):
        return None
    if not isinstance(market.get("Home"), dict):
        return None
    if not isinstance(market.get("Away"), dict):
        return None
    return market


def side_book_odds(market: dict[str, Any], side: str, min_odds: float, max_odds: float) -> dict[str, float]:
    raw = market.get(side) or {}
    if not isinstance(raw, dict):
        return {}
    out = {}
    for book, value in raw.items():
        odds = safe_float(value)
        if odds is not None and min_odds <= odds <= max_odds:
            out[clean(book)] = odds
    return out


def remove_outlier_pairs(pairs: list[tuple[str, float, float]], max_deviation: float) -> list[tuple[str, float, float]]:
    if len(pairs) < 3 or max_deviation <= 0:
        return pairs
    home_med = statistics.median([p[1] for p in pairs])
    away_med = statistics.median([p[2] for p in pairs])
    cleaned = []
    for book, home, away in pairs:
        home_dev = abs(home - home_med) / home_med if home_med else 0.0
        away_dev = abs(away - away_med) / away_med if away_med else 0.0
        if home_dev <= max_deviation and away_dev <= max_deviation:
            cleaned.append((book, home, away))
    return cleaned or pairs


def choose_pair_odds(
    market: dict[str, Any],
    bookmaker: str,
    fallback: str,
    min_odds: float,
    max_odds: float,
    min_overround: float,
    max_overround: float,
    max_book_deviation: float,
) -> tuple[float | None, float | None, str | None, dict[str, Any]]:
    home_books = side_book_odds(market, "Home", min_odds, max_odds)
    away_books = side_book_odds(market, "Away", min_odds, max_odds)
    common = sorted(set(home_books) & set(away_books))

    valid_pairs = []
    rejected_overround = 0
    for book in common:
        home = home_books[book]
        away = away_books[book]
        _, _, overround = devig_home_away(home, away)
        if min_overround <= overround <= max_overround:
            valid_pairs.append((book, home, away))
        else:
            rejected_overround += 1

    valid_pairs = remove_outlier_pairs(valid_pairs, max_book_deviation)

    if not valid_pairs:
        return None, None, None, {
            "book_pairs_total": len(common),
            "book_pairs_valid": 0,
            "book_pairs_rejected_overround": rejected_overround,
        }

    preferred = [p for p in valid_pairs if p[0] == bookmaker]
    if fallback == "bookmaker":
        if preferred:
            book, home, away = preferred[0]
            return home, away, bookmaker, {"book_pairs_valid": len(valid_pairs), "books_used": [book]}
        return None, None, None, {"book_pairs_valid": len(valid_pairs), "missing_bookmaker": bookmaker}

    if fallback == "clean_median":
        home = float(statistics.median([p[1] for p in valid_pairs]))
        away = float(statistics.median([p[2] for p in valid_pairs]))
        source = "clean_median"
    elif fallback == "best":
        home = max(p[1] for p in valid_pairs)
        away = max(p[2] for p in valid_pairs)
        source = "best_clean"
    elif fallback == "none":
        if preferred:
            book, home, away = preferred[0]
            source = bookmaker
        else:
            return None, None, None, {"book_pairs_valid": len(valid_pairs), "missing_bookmaker": bookmaker}
    else:
        home = float(sum(p[1] for p in valid_pairs) / len(valid_pairs))
        away = float(sum(p[2] for p in valid_pairs) / len(valid_pairs))
        source = "clean_average"

    return home, away, source, {
        "book_pairs_total": len(common),
        "book_pairs_valid": len(valid_pairs),
        "book_pairs_rejected_overround": rejected_overround,
        "books_used": [p[0] for p in valid_pairs],
        "home_book_odds": [round(p[1], 6) for p in valid_pairs],
        "away_book_odds": [round(p[2], 6) for p in valid_pairs],
    }

def devig_home_away(home_odds: float, away_odds: float) -> tuple[float, float, float]:
    raw_home = 1.0 / home_odds
    raw_away = 1.0 / away_odds
    total = raw_home + raw_away
    return raw_home / total, raw_away / total, total - 1.0


def infer_gender(fixture: dict[str, Any]) -> str:
    text = " ".join(
        clean(fixture.get(key))
        for key in ["event_type_type", "tournament_name", "tournament_round"]
    ).lower()

    if "women" in text or "wta" in text or "girls" in text:
        return "women"

    if "men" in text or "atp" in text or "boys" in text:
        return "men"

    return "unknown"


def normalize_level(level: Any) -> str:
    s = clean(level).lower().replace("-", "_").replace(" ", "_")
    if s in {"atp", "wta", "main", "main_tour"}:
        return "atp_wta"
    if s in {"grand_slam", "slam"}:
        return "grand_slam"
    if s in {"challenger", "atp_challenger"}:
        return "challenger"
    if s == "itf":
        return "itf"
    if "qual" in s:
        return "qualifying"
    return s


def is_qualification_fixture(fixture: dict[str, Any]) -> bool:
    # API tournament metadata can incorrectly label normal ATP/WTA/Challenger
    # quarter-finals as qualifying. For level selection, trust the live fixture
    # text first and only treat it as qualifying when the fixture itself says so.
    text = " ".join(
        clean(fixture.get(key))
        for key in ["tournament_name", "tournament_round", "event_name"]
    ).lower()
    return bool(re.search(r"\bqualif(?:ication|ying|iers?|y)?\b", text))


def infer_level(fixture: dict[str, Any], metadata: dict[str, Any]) -> str:
    event_type = clean(fixture.get("event_type_type")).lower()
    fixture_text = " ".join(
        clean(fixture.get(key))
        for key in ["tournament_name", "tournament_round", "event_name"]
    ).lower()

    if is_qualification_fixture(fixture):
        return "qualifying"

    # Live API event_type is more reliable than our tournament metadata for daily scans.
    # Metadata is still used as a fallback when event_type is missing/ambiguous.
    if "itf" in event_type:
        return "itf"
    if "challenger" in event_type:
        return "challenger"
    if "atp" in event_type or "wta" in event_type:
        return "atp_wta"

    if (
        "grand slam" in fixture_text
        or "australian open" in fixture_text
        or "roland garros" in fixture_text
        or "wimbledon" in fixture_text
        or "us open" in fixture_text
    ):
        return "grand_slam"

    tournament_key = clean(fixture.get("tournament_key"))
    if tournament_key:
        meta = metadata.get(tournament_key)
        if isinstance(meta, dict):
            level = normalize_level(meta.get("tour_level"))
            if level in {"atp_wta", "grand_slam", "challenger", "itf", "qualifying"}:
                return level

    text = f"{event_type} {fixture_text}"
    if "itf" in text:
        return "itf"
    if "challenger" in text:
        return "challenger"
    if "atp" in text or "wta" in text:
        return "atp_wta"

    return "unknown"


def infer_surface(fixture: dict[str, Any], metadata: dict[str, Any]) -> str:
    for key in ["surface", "event_surface", "court_surface"]:
        surface = clean(fixture.get(key)).lower()
        if surface in VALID_SURFACES:
            return surface

    tournament_key = clean(fixture.get("tournament_key"))
    if tournament_key:
        meta = metadata.get(tournament_key)
        if isinstance(meta, dict):
            surface = clean(meta.get("surface")).lower()
            if surface in VALID_SURFACES:
                return surface

    return "unknown"


def is_singles(fixture: dict[str, Any]) -> bool:
    text = clean(fixture.get("event_type_type")).lower()
    if "doubles" in text:
        return False
    # API Tennis tennis event types are usually "Atp Singles", "Wta Singles", ...
    return "singles" in text or not text


def player_identity_from_match(player: dict[str, Any], gender: str) -> tuple[str | None, str]:
    name = clean(player.get("name"))
    sackmann_id = player.get("sackmann_player_id")

    if sackmann_id not in {None, ""}:
        try:
            return f"{gender}:sackmann:{int(sackmann_id)}", name
        except (TypeError, ValueError):
            pass

    api_key = player.get("api_player_key")
    if api_key not in {None, ""}:
        try:
            return f"{gender}:api:{int(api_key)}", name
        except (TypeError, ValueError):
            pass

    if name:
        return f"{gender}:name:{normalize_name(name)}", name

    return None, ""


def iter_canonical_matches(manifest_path: Path):
    manifest = load_json(manifest_path)
    rows = []

    for item in manifest.get("year_files") or []:
        rel = item.get("path")
        if not rel:
            continue
        if str(manifest_path).startswith("http://") or str(manifest_path).startswith("https://"):
            source = TLE_RAW_BASE + rel
        else:
            path = Path(rel)
            if not path.is_absolute():
                path = ROOT_DIR / path
            if not path.exists():
                continue
            source = path
        for row in read_jsonl_gz(source):
            rows.append(row)

    rows.sort(key=lambda row: (clean(row.get("date")), clean(row.get("tle_match_id"))))
    yield from rows


def build_alias_indexes(manifest_path: Path) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, str]]:
    exact = defaultdict(set)
    surname_initial = defaultdict(set)
    display = {}

    for match in iter_canonical_matches(manifest_path):
        gender = clean(match.get("gender")).lower()
        if gender not in {"men", "women"}:
            continue

        for side in ("winner", "loser"):
            player = match.get(side) or {}
            if not isinstance(player, dict):
                continue

            key, name = player_identity_from_match(player, gender)
            if not key or not name:
                continue

            display.setdefault(key, name)

            norm = normalize_name(name)
            if norm:
                exact[f"{gender}|{norm}"].add(key)

            si = surname_initial_key(name)
            if si:
                surname_initial[f"{gender}|{si}"].add(key)

    return (
        {key: sorted(values) for key, values in exact.items()},
        {key: sorted(values) for key, values in surname_initial.items()},
        display,
    )


def load_api_player_mapping(path: str | Path) -> dict[str, dict[str, Any]]:
    if not str(path).startswith("http") and not Path(path).exists():
        return {}

    payload = load_json(path)
    players = payload.get("players") if isinstance(payload, dict) else None
    if not isinstance(players, dict):
        return {}

    return {str(key): value for key, value in players.items() if isinstance(value, dict)}


def resolve_player(
    api_key: int | None,
    name: str,
    gender: str,
    api_mapping: dict[str, dict[str, Any]],
    exact_index: dict[str, list[str]],
    surname_initial_index: dict[str, list[str]],
) -> tuple[str | None, str]:
    if gender not in {"men", "women"}:
        return None, "invalid_gender"

    if api_key is not None:
        mapped = api_mapping.get(str(api_key))
        if (
            isinstance(mapped, dict)
            and mapped.get("status") == "matched"
            and clean(mapped.get("gender")).lower() == gender
            and mapped.get("sackmann_player_id") not in {None, ""}
        ):
            try:
                return f"{gender}:sackmann:{int(mapped['sackmann_player_id'])}", "api_mapping"
            except (TypeError, ValueError):
                pass

    norm = normalize_name(name)
    if norm:
        candidates = exact_index.get(f"{gender}|{norm}", [])
        if len(candidates) == 1:
            return candidates[0], "exact_name"

    si = surname_initial_key(name)
    if si:
        candidates = surname_initial_index.get(f"{gender}|{si}", [])
        if len(candidates) == 1:
            return candidates[0], "unique_surname_initial"

    if api_key is not None:
        return f"{gender}:api:{api_key}", "api_key_unmapped"

    if norm:
        return f"{gender}:name:{norm}", "name_fallback"

    return None, "unresolved"


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))


def update_pair(winner_rating: float, loser_rating: float, k: float) -> tuple[float, float]:
    expected = expected_score(winner_rating, loser_rating)
    change = k * (1.0 - expected)
    return winner_rating + change, loser_rating - change


def new_surface_state() -> dict[str, Any]:
    return {"elo": DEFAULT_ELO, "matches": 0, "wins": 0}


def new_level_state() -> dict[str, Any]:
    return {"overall_elo": DEFAULT_ELO, "matches": 0, "wins": 0, "surfaces": {}}


def new_player_state(key: str, name: str, gender: str) -> dict[str, Any]:
    return {
        "player_key": key,
        "display_name": name,
        "gender": gender,
        "global": {"overall_elo": DEFAULT_ELO, "matches": 0, "wins": 0, "surfaces": {}},
        "levels": {},
    }


def ensure_player(players: dict[str, dict[str, Any]], key: str, name: str, gender: str) -> dict[str, Any]:
    if key not in players:
        players[key] = new_player_state(key, name, gender)
    return players[key]


def ensure_level(player: dict[str, Any], level: str) -> dict[str, Any]:
    if level not in player["levels"]:
        player["levels"][level] = new_level_state()
    return player["levels"][level]


def ensure_surface(container: dict[str, Any], surface: str) -> dict[str, Any]:
    if surface not in container["surfaces"]:
        container["surfaces"][surface] = new_surface_state()
    return container["surfaces"][surface]


def update_rating_layer(winner: dict[str, Any], loser: dict[str, Any], field: str, k: float) -> None:
    winner_new, loser_new = update_pair(float(winner[field]), float(loser[field]), k)
    winner[field] = winner_new
    loser[field] = loser_new


def update_state_for_match(match: dict[str, Any], players: dict[str, dict[str, Any]]) -> None:
    if not match.get("ready_for_tle"):
        return

    gender = clean(match.get("gender")).lower()
    level = clean(match.get("tour_level")).lower()
    surface = clean((match.get("tournament") or {}).get("surface")).lower()

    if gender not in {"men", "women"}:
        return

    winner_raw = match.get("winner") or {}
    loser_raw = match.get("loser") or {}
    if not isinstance(winner_raw, dict) or not isinstance(loser_raw, dict):
        return

    winner_key, winner_name = player_identity_from_match(winner_raw, gender)
    loser_key, loser_name = player_identity_from_match(loser_raw, gender)

    if not winner_key or not loser_key or winner_key == loser_key:
        return

    winner = ensure_player(players, winner_key, winner_name, gender)
    loser = ensure_player(players, loser_key, loser_name, gender)

    update_rating_layer(winner["global"], loser["global"], "overall_elo", GLOBAL_K)
    winner["global"]["matches"] += 1
    loser["global"]["matches"] += 1
    winner["global"]["wins"] += 1

    if surface in VALID_SURFACES:
        ws = ensure_surface(winner["global"], surface)
        ls = ensure_surface(loser["global"], surface)
        update_rating_layer(ws, ls, "elo", GLOBAL_SURFACE_K)
        ws["matches"] += 1
        ls["matches"] += 1
        ws["wins"] += 1

    wl = ensure_level(winner, level)
    ll = ensure_level(loser, level)
    update_rating_layer(wl, ll, "overall_elo", LEVEL_K)
    wl["matches"] += 1
    ll["matches"] += 1
    wl["wins"] += 1

    if surface in VALID_SURFACES:
        wls = ensure_surface(wl, surface)
        lls = ensure_surface(ll, surface)
        update_rating_layer(wls, lls, "elo", LEVEL_SURFACE_K)
        wls["matches"] += 1
        lls["matches"] += 1
        wls["wins"] += 1


def build_state_before_date(manifest_path: Path, scan_date: date) -> tuple[dict[str, dict[str, Any]], int]:
    players: dict[str, dict[str, Any]] = {}
    processed = 0

    for match in iter_canonical_matches(manifest_path):
        match_date = parse_date(match.get("date"))
        if match_date is None:
            continue
        if match_date >= scan_date:
            break
        update_state_for_match(match, players)
        processed += 1

    return players, processed


def get_level_state(player: dict[str, Any], level: str) -> dict[str, Any] | None:
    return player.get("levels", {}).get(level)


def get_level_surface_state(player: dict[str, Any], level: str, surface: str) -> dict[str, Any] | None:
    level_state = get_level_state(player, level)
    if not level_state:
        return None
    return level_state.get("surfaces", {}).get(surface)


def probability_for_home_away(
    home: dict[str, Any],
    away: dict[str, Any],
    level: str,
    surface: str,
    args: argparse.Namespace,
) -> tuple[float | None, str, dict[str, Any]]:
    """Return home win probability."""
    if level in MAIN_TOUR_LEVELS:
        model_level = "atp_wta"
        home_level = get_level_state(home, model_level)
        away_level = get_level_state(away, model_level)

        if not home_level or not away_level:
            return None, "main_tour_missing_level_rating", {}

        if home_level["matches"] < args.main_min_level_matches or away_level["matches"] < args.main_min_level_matches:
            return None, "main_tour_level_min_sample", {}

        if surface not in VALID_SURFACES:
            return None, "main_tour_unknown_surface", {}

        home_surface = get_level_surface_state(home, model_level, surface)
        away_surface = get_level_surface_state(away, model_level, surface)

        if not home_surface or not away_surface:
            return None, "main_tour_missing_surface_rating", {}

        if home_surface["matches"] < args.main_min_surface_matches or away_surface["matches"] < args.main_min_surface_matches:
            return None, "main_tour_surface_min_sample", {}

        p_level = expected_score(float(home_level["overall_elo"]), float(away_level["overall_elo"]))
        p_surface = expected_score(float(home_surface["elo"]), float(away_surface["elo"]))
        p = 0.80 * p_level + 0.20 * p_surface

        return p, "main_tour_80_level_20_surface", {
            "home_level_matches": home_level["matches"],
            "away_level_matches": away_level["matches"],
            "home_surface_matches": home_surface["matches"],
            "away_surface_matches": away_surface["matches"],
            "home_level_elo": round(float(home_level["overall_elo"]), 3),
            "away_level_elo": round(float(away_level["overall_elo"]), 3),
            "home_surface_elo": round(float(home_surface["elo"]), 3),
            "away_surface_elo": round(float(away_surface["elo"]), 3),
            "p_level": round(p_level, 6),
            "p_surface": round(p_surface, 6),
        }

    if level == "itf":
        home_level = get_level_state(home, "itf")
        away_level = get_level_state(away, "itf")

        if not home_level or not away_level:
            return None, "itf_missing_level_rating", {}

        if home_level["matches"] < args.itf_min_level_matches or away_level["matches"] < args.itf_min_level_matches:
            return None, "itf_level_min_sample", {}

        p = expected_score(float(home_level["overall_elo"]), float(away_level["overall_elo"]))
        return p, "itf_100_level_overall", {
            "home_level_matches": home_level["matches"],
            "away_level_matches": away_level["matches"],
            "home_level_elo": round(float(home_level["overall_elo"]), 3),
            "away_level_elo": round(float(away_level["overall_elo"]), 3),
        }

    if level == "challenger":
        home_level = get_level_state(home, "challenger")
        away_level = get_level_state(away, "challenger")

        if not home_level or not away_level:
            return None, "challenger_missing_level_rating", {}

        if home_level["matches"] < args.challenger_min_level_matches or away_level["matches"] < args.challenger_min_level_matches:
            return None, "challenger_level_min_sample", {}

        p = expected_score(float(home_level["overall_elo"]), float(away_level["overall_elo"]))
        return p, "challenger_100_level_overall", {
            "home_level_matches": home_level["matches"],
            "away_level_matches": away_level["matches"],
            "home_level_elo": round(float(home_level["overall_elo"]), 3),
            "away_level_elo": round(float(away_level["overall_elo"]), 3),
        }

    if level == "qualifying":
        return None, "qualifying_no_bet", {}

    return None, "unsupported_level", {}


def make_pick_row(
    fixture: dict[str, Any],
    level: str,
    gender: str,
    surface: str,
    side: str,
    probability: float,
    odds: float,
    book_probability: float,
    ev: float,
    edge: float,
    odds_source: str,
    model: str,
    model_details: dict[str, Any],
    home_name: str,
    away_name: str,
    home_key: str,
    away_key: str,
) -> dict[str, Any]:
    selection_name = home_name if side == "Home" else away_name
    opponent_name = away_name if side == "Home" else home_name

    return {
        "event_key": event_key_text(fixture.get("event_key")),
        "date": clean(fixture.get("event_date")),
        "time": clean(fixture.get("event_time")),
        "tournament": clean(fixture.get("tournament_name")),
        "tournament_key": clean(fixture.get("tournament_key")),
        "round": clean(fixture.get("tournament_round")),
        "event_type": clean(fixture.get("event_type_type")),
        "gender": gender,
        "tour_level": level,
        "surface": surface,
        "match": f"{home_name} - {away_name}",
        "selection": selection_name,
        "opponent": opponent_name,
        "selected_side": side,
        "selected_player_side": "player_1" if side == "Home" else "player_2",
        "home_player": home_name,
        "away_player": away_name,
        "home_tle_key": home_key,
        "away_tle_key": away_key,
        "odds": round(odds, 6),
        "odds_source": odds_source,
        "book_probability_devig": round(book_probability, 6),
        "tle_probability": round(probability, 6),
        "tle_edge": round(edge, 6),
        "tle_ev": round(ev, 6),
        "model": model,
        "model_details": model_details,
    }


def parse_fixture_datetime(fixture: dict[str, Any], timezone_name: str) -> datetime | None:
    d = clean(fixture.get("event_date") or fixture.get("date"))
    t = clean(fixture.get("event_time") or fixture.get("time"))
    if not d or not t:
        return None
    try:
        hhmm = t[:5]
        return datetime.fromisoformat(f"{d}T{hhmm}:00").replace(tzinfo=ZoneInfo(timezone_name))
    except Exception:
        return None


def minutes_until_start(fixture: dict[str, Any], timezone_name: str) -> float | None:
    dt = parse_fixture_datetime(fixture, timezone_name)
    if dt is None:
        return None
    now = datetime.now(ZoneInfo(timezone_name))
    return (dt - now).total_seconds() / 60.0


def pick_identity(pick: dict[str, Any]) -> str:
    return "|".join([
        clean(pick.get("event_key")),
        clean(pick.get("selected_player_side") or pick.get("selected_side")),
        normalize_name(pick.get("selection")),
    ])


def load_existing_predictions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows = payload.get("picks") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def merge_open_predictions(existing: list[dict[str, Any]], current: list[dict[str, Any]], generated_at: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in existing:
        status = clean(row.get("settlement_status") or "PENDING").upper()
        if status in {"WIN", "LOSS", "VOID"}:
            continue
        key = pick_identity(row)
        if not key:
            continue
        row = dict(row)
        row.setdefault("settlement_status", "PENDING")
        row.setdefault("first_seen_at", generated_at)
        row.setdefault("last_seen_at", row.get("first_seen_at"))
        row.setdefault("snapshot_count", 1)
        row.setdefault("first_odds", row.get("odds"))
        row.setdefault("first_tle_probability", row.get("tle_probability"))
        row.setdefault("first_book_probability_devig", row.get("book_probability_devig"))
        row.setdefault("first_tle_edge", row.get("tle_edge"))
        row.setdefault("first_tle_ev", row.get("tle_ev"))
        row["ledger_status"] = "not_in_latest_snapshot"
        merged[key] = row

    current_keys = set()
    for row in current:
        key = pick_identity(row)
        if not key:
            continue
        current_keys.add(key)
        if key not in merged:
            new = dict(row)
            new["settlement_status"] = "PENDING"
            new["first_seen_at"] = generated_at
            new["last_seen_at"] = generated_at
            new["snapshot_count"] = 1
            new["ledger_status"] = "active_in_latest_snapshot"
            new["first_odds"] = new.get("odds")
            new["first_tle_probability"] = new.get("tle_probability")
            new["first_book_probability_devig"] = new.get("book_probability_devig")
            new["first_tle_edge"] = new.get("tle_edge")
            new["first_tle_ev"] = new.get("tle_ev")
            new["latest_odds"] = new.get("odds")
            new["latest_tle_probability"] = new.get("tle_probability")
            new["latest_book_probability_devig"] = new.get("book_probability_devig")
            new["latest_tle_edge"] = new.get("tle_edge")
            new["latest_tle_ev"] = new.get("tle_ev")
            merged[key] = new
        else:
            old = merged[key]
            preserved = {k: old.get(k) for k in ["first_seen_at", "first_odds", "first_tle_probability", "first_book_probability_devig", "first_tle_edge", "first_tle_ev", "settlement_status"]}
            count = int(old.get("snapshot_count") or 1) + 1
            old.update(row)
            old.update(preserved)
            old["snapshot_count"] = count
            old["last_seen_at"] = generated_at
            old["ledger_status"] = "active_in_latest_snapshot"
            old["latest_odds"] = row.get("odds")
            old["latest_tle_probability"] = row.get("tle_probability")
            old["latest_book_probability_devig"] = row.get("book_probability_devig")
            old["latest_tle_edge"] = row.get("tle_edge")
            old["latest_tle_ev"] = row.get("tle_ev")
            merged[key] = old

    rows = list(merged.values())
    rows.sort(key=lambda r: (clean(r.get("date")), clean(r.get("time")), -float(r.get("first_tle_edge") or r.get("tle_edge") or 0)))
    return rows, {
        "existing_open_before_merge": len(existing),
        "current_snapshot_picks": len(current),
        "open_predictions_after_merge": len(rows),
        "active_in_latest_snapshot": sum(1 for r in rows if r.get("ledger_status") == "active_in_latest_snapshot"),
        "not_in_latest_snapshot": sum(1 for r in rows if r.get("ledger_status") == "not_in_latest_snapshot"),
    }


def format_pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return ""


def write_predictions_table(path: Path, picks: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# AI TLE Predictions",
        "",
        f"Generated: `{summary.get('generated_at')}`",
        f"Open predictions: `{len(picks)}`",
        "",
        "| # | Date | Time | Level | Match | Pick | Odds | TLE % | Book % | Edge | EV | Status |",
        "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for i, p in enumerate(picks, 1):
        lines.append("| " + " | ".join([
            str(i), clean(p.get("date")), clean(p.get("time")), clean(p.get("tour_level")),
            clean(p.get("match")).replace("|", "-"), clean(p.get("selection")).replace("|", "-"),
            clean(p.get("first_odds") or p.get("odds")), format_pct(p.get("first_tle_probability") or p.get("tle_probability")),
            format_pct(p.get("first_book_probability_devig") or p.get("book_probability_devig")),
            format_pct(p.get("first_tle_edge") or p.get("tle_edge")), format_pct(p.get("first_tle_ev") or p.get("tle_ev")),
            clean(p.get("settlement_status") or "PENDING"),
        ]) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Pure TLE scanner: fetches today's API-Tennis fixtures + Home/Away odds, "
            "computes TLE Elo probability, and writes picks with edge/EV."
        )
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Scan date YYYY-MM-DD")
    parser.add_argument("--duration", type=int, default=1, help="Number of days to scan")
    parser.add_argument("--bookmaker", default="Pncl")
    parser.add_argument("--fallback", choices=["none", "bookmaker", "clean_average", "clean_median", "best"], default="clean_average")
    parser.add_argument("--min-edge", type=float, default=0.03)
    parser.add_argument("--min-ev", type=float, default=0.0)
    parser.add_argument("--min-odds", type=float, default=1.20)
    parser.add_argument("--max-odds", type=float, default=8.0)
    parser.add_argument("--levels", default="challenger,itf,atp_wta,grand_slam", help="Comma separated levels to scan")
    parser.add_argument("--timezone", default="Europe/Ljubljana")
    parser.add_argument("--min-start-minutes", type=float, default=30.0)
    parser.add_argument("--min-overround", type=float, default=-0.03)
    parser.add_argument("--max-overround", type=float, default=0.18)
    parser.add_argument("--max-book-deviation", type=float, default=0.35)
    parser.add_argument("--min-book-pairs", type=int, default=3)
    parser.add_argument("--allowed-resolve-methods", default="api_mapping,exact_name")
    parser.add_argument("--canonical-manifest", default=str(DEFAULT_CANONICAL_MANIFEST))
    parser.add_argument("--api-player-mapping", default=str(DEFAULT_API_PLAYER_MAPPING))
    parser.add_argument("--tournament-metadata", default=str(DEFAULT_TOURNAMENT_METADATA))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--sleep", type=float, default=float(os.getenv("API_SLEEP_SECONDS", "0.8")))

    parser.add_argument("--main-min-level-matches", type=int, default=20)
    parser.add_argument("--main-min-surface-matches", type=int, default=10)
    parser.add_argument("--itf-min-level-matches", type=int, default=5)
    parser.add_argument("--challenger-min-level-matches", type=int, default=5)

    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY environment variable.")

    scan_start = date.fromisoformat(args.date)
    scan_end = date.fromordinal(scan_start.toordinal() + max(0, args.duration - 1))

    levels_to_scan = {
        clean(item).lower()
        for item in args.levels.split(",")
        if clean(item)
    }

    canonical_manifest = args.canonical_manifest

    api_mapping_path = args.api_player_mapping

    metadata_path = args.tournament_metadata

    metadata = {}
    try:
        metadata_payload = load_json(metadata_path)
        raw_meta = metadata_payload.get("tournaments") if isinstance(metadata_payload, dict) else None
        if isinstance(raw_meta, dict):
            metadata = {clean(key): value for key, value in raw_meta.items() if isinstance(value, dict)}
    except Exception:
        metadata = {}

    api_mapping = load_api_player_mapping(api_mapping_path)
    exact_index, surname_initial_index, _display = build_alias_indexes(canonical_manifest)
    players, historical_matches = build_state_before_date(canonical_manifest, scan_start)

    counters = Counter()
    all_scored = []
    picks = []

    current = scan_start
    while current <= scan_end:
        date_text = current.isoformat()

        fixtures_payload = api_get(
            api_key,
            {"method": "get_fixtures", "date_start": date_text, "date_stop": date_text},
            sleep_seconds=args.sleep,
        )
        odds_payload = api_get(
            api_key,
            {"method": "get_odds", "date_start": date_text, "date_stop": date_text},
            sleep_seconds=args.sleep,
        )

        fixtures = fixture_index(fixtures_payload)
        odds_by_event = odds_index(odds_payload)

        counters["api_fixture_events"] += len(fixtures)
        counters["api_odds_events"] += len(odds_by_event)

        for event_key, markets in odds_by_event.items():
            fixture = fixtures.get(event_key)
            if not fixture:
                counters["skipped_missing_fixture"] += 1
                continue

            counters["odds_events_with_fixture"] += 1

            if not is_singles(fixture):
                counters["skipped_not_singles"] += 1
                continue

            status = clean(fixture.get("event_status")).lower()
            if status in {"finished", "cancelled", "canceled", "postponed", "retired", "walkover"}:
                counters[f"skipped_status_{status or 'missing'}"] += 1
                continue

            gender = infer_gender(fixture)
            if gender not in {"men", "women"}:
                counters["skipped_gender_unknown"] += 1
                continue

            level = infer_level(fixture, metadata)
            if level not in levels_to_scan:
                counters[f"skipped_level_{level}"] += 1
                continue

            surface = infer_surface(fixture, metadata)

            market = get_home_away_market(markets)
            if not market:
                counters["skipped_missing_home_away_market"] += 1
                continue

            home_odds, away_odds, odds_source, odds_details = choose_pair_odds(market, args.bookmaker, args.fallback, args.min_odds, args.max_odds, args.min_overround, args.max_overround, args.max_book_deviation)
            if home_odds is None or away_odds is None or odds_source is None:
                counters["skipped_missing_pair_odds"] += 1
                continue

            if int(odds_details.get("book_pairs_valid") or 0) < args.min_book_pairs:
                counters["skipped_min_book_pairs"] += 1
                continue

            mins = minutes_until_start(fixture, args.timezone)
            if mins is None:
                counters["skipped_missing_start_time"] += 1
                continue
            if mins < args.min_start_minutes:
                counters["skipped_starts_too_soon"] += 1
                continue

            home_name = clean(fixture.get("event_first_player") or fixture.get("first_player"))
            away_name = clean(fixture.get("event_second_player") or fixture.get("second_player"))
            home_api_key = safe_int(fixture.get("first_player_key"))
            away_api_key = safe_int(fixture.get("second_player_key"))

            home_key, home_method = resolve_player(
                home_api_key,
                home_name,
                gender,
                api_mapping,
                exact_index,
                surname_initial_index,
            )
            away_key, away_method = resolve_player(
                away_api_key,
                away_name,
                gender,
                api_mapping,
                exact_index,
                surname_initial_index,
            )

            counters[f"home_resolve_{home_method}"] += 1
            counters[f"away_resolve_{away_method}"] += 1

            if not home_key or not away_key:
                counters["skipped_unresolved_player"] += 1
                continue

            if home_method not in allowed_resolve_methods or away_method not in allowed_resolve_methods:
                counters["skipped_unsafe_player_resolve"] += 1
                counters[f"skipped_unsafe_home_{home_method}"] += 1
                counters[f"skipped_unsafe_away_{away_method}"] += 1
                continue

            home_player = players.get(home_key)
            away_player = players.get(away_key)
            if not home_player or not away_player:
                counters["skipped_missing_player_history"] += 1
                continue

            home_prob, model, model_details = probability_for_home_away(
                home_player,
                away_player,
                level,
                surface,
                args,
            )

            if home_prob is None:
                counters[f"skipped_{model}"] += 1
                continue

            away_prob = 1.0 - home_prob
            book_home_prob, book_away_prob, overround = devig_home_away(home_odds, away_odds)

            candidates = [
                ("Home", home_name, home_prob, home_odds, book_home_prob),
                ("Away", away_name, away_prob, away_odds, book_away_prob),
            ]

            scored_any = False
            for side, _name, prob, odds, book_prob in candidates:
                ev = prob * odds - 1.0
                edge = prob - book_prob

                scored = make_pick_row(
                    fixture=fixture,
                    level=level,
                    gender=gender,
                    surface=surface,
                    side=side,
                    probability=prob,
                    odds=odds,
                    book_probability=book_prob,
                    ev=ev,
                    edge=edge,
                    odds_source=odds_source,
                    model=model,
                    model_details={
                        **model_details,
                        "home_resolve_method": home_method,
                        "away_resolve_method": away_method,
                        "home_odds": round(home_odds, 6),
                        "away_odds": round(away_odds, 6),
                        "overround": round(overround, 6),
                        "odds_details": odds_details,
                        "minutes_until_start": round(mins, 2),
                    },
                    home_name=home_name,
                    away_name=away_name,
                    home_key=home_key,
                    away_key=away_key,
                )
                all_scored.append(scored)
                scored_any = True

                if (
                    edge >= args.min_edge
                    and ev >= args.min_ev
                    and odds >= args.min_odds
                    and odds <= args.max_odds
                ):
                    picks.append(scored)
                    counters["picks"] += 1
                    counters[f"picks_level_{level}"] += 1
                    counters[f"picks_gender_{gender}"] += 1

            if scored_any:
                counters["scored_matches"] += 1
                counters[f"scored_level_{level}"] += 1

        current = date.fromordinal(current.toordinal() + 1)

    picks.sort(key=lambda row: (-row["tle_edge"], -row["tle_ev"], row["date"], row["time"], row["event_key"]))
    all_scored.sort(key=lambda row: (-row["tle_edge"], -row["tle_ev"], row["date"], row["time"], row["event_key"]))

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT_DIR / out_dir

    if args.duration == 1:
        stem = f"tle_scanner_picks_{scan_start.isoformat()}"
    else:
        stem = f"tle_scanner_picks_{scan_start.isoformat()}_{scan_end.isoformat()}"

    output_path = out_dir / f"{stem}.json"
    latest_path = out_dir / "ai_tle_predictions_latest.json"
    table_path = out_dir / "ai_tle_predictions_table.md"

    generated_at = now_iso()
    existing_open = load_existing_predictions(latest_path)
    open_picks, ledger_stats = merge_open_predictions(existing_open, picks, generated_at)

    summary = {
        "generated_at": generated_at,
        "scan_date_start": scan_start.isoformat(),
        "scan_date_end": scan_end.isoformat(),
        "settings": {
            "bookmaker": args.bookmaker,
            "fallback": args.fallback,
            "min_edge": args.min_edge,
            "min_ev": args.min_ev,
            "min_odds": args.min_odds,
            "max_odds": args.max_odds,
            "min_overround": args.min_overround,
            "max_overround": args.max_overround,
            "max_book_deviation": args.max_book_deviation,
            "min_book_pairs": args.min_book_pairs,
            "allowed_resolve_methods": sorted(allowed_resolve_methods),
            "min_start_minutes": args.min_start_minutes,
            "levels": sorted(levels_to_scan),
            "main_min_level_matches": args.main_min_level_matches,
            "main_min_surface_matches": args.main_min_surface_matches,
            "itf_min_level_matches": args.itf_min_level_matches,
            "challenger_min_level_matches": args.challenger_min_level_matches,
            "state_note": "TLE state uses Tennis-ELO canonical matches strictly before scan start date.",
            "historical_matches_loaded_before_scan_date": historical_matches,
        },
        "counters": dict(sorted(counters.items())),
        "current_snapshot_picks_count": len(picks),
        "open_predictions_count": len(open_picks),
        "scored_sides_count": len(all_scored),
        "ledger": ledger_stats,
        "level_counts": dict(Counter(row["tour_level"] for row in open_picks)),
        "gender_counts": dict(Counter(row["gender"] for row in open_picks)),
    }

    payload = {
        "schema_version": 1,
        "file_type": "ai_repo_tle_open_predictions",
        "summary": summary,
        "picks": open_picks,
        "current_snapshot_picks": picks,
        "all_scored_sides": all_scored,
    }

    save_json(output_path, payload)
    save_json(latest_path, payload)
    write_predictions_table(table_path, open_picks, summary)

    print("AI TLE SCANNER DONE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Output: {output_path}")
    print(f"Latest predictions: {latest_path}")
    print(f"Table: {table_path}")


if __name__ == "__main__":
    main()

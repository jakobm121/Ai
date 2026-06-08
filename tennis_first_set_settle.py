import json
import os
import re
import time
from datetime import datetime
from typing import Any
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
TZ_NAME = os.getenv("TZ_NAME", "Europe/Ljubljana")

DATA_DIR = os.getenv("TENNIS_FIRST_SET_DATA_DIR", "data")
PICKS_URL = os.getenv(
    "TENNIS_FIRST_SET_PICKS_URL",
    "https://raw.githubusercontent.com/jakobm121/Tennis-ELO/refs/heads/main/"
    "data/predictions/first_set_totals_shadow.json",
)
RESULTS_FILE = os.getenv(
    "TENNIS_FIRST_SET_RESULTS_FILE",
    f"{DATA_DIR}/tennis_first_set_results.json",
)
DEBUG_FILE = os.getenv(
    "TENNIS_FIRST_SET_DEBUG_FILE",
    f"{DATA_DIR}/tennis_first_set_settle_debug.json",
)

REQUEST_TIMEOUT = int(os.getenv("TENNIS_FIRST_SET_REQUEST_TIMEOUT", "30"))
API_SLEEP_SECONDS = float(
    os.getenv("TENNIS_FIRST_SET_API_SLEEP_SECONDS", "0.30")
)
DEFAULT_STAKE = float(os.getenv("TENNIS_FIRST_SET_DEFAULT_STAKE", "1.0"))

BAD_TERMINAL_STATUSES = {
    "cancelled",
    "canceled",
    "postponed",
    "retired",
    "walkover",
    "wo",
    "abandoned",
    "interrupted",
    "suspended",
}


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, type(default)) else default
    except Exception:
        return default


def save_json(path: str, payload: Any) -> None:
    ensure_dirs()

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def fetch_remote_json(url: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": "AI tennis first-set multi-market settle/2.0",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        payload = json.load(response)

    return payload if isinstance(payload, dict) else {}


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def clean_market_name(value: Any) -> str:
    market = str(value or "").strip().lower()

    if market in {
        "first_set_total_games",
        "1st set total games",
        "first set total games",
    }:
        return "first_set_total_games"

    return market or "first_set_total_games"


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


def fetch_fixture_by_event_key(event_key: Any) -> dict[str, Any] | None:
    payload = api_call(
        {
            "method": "get_fixtures",
            "event_key": event_key,
        }
    )
    time.sleep(API_SLEEP_SECONDS)

    if payload.get("success") != 1:
        return None

    result = payload.get("result") or []

    if isinstance(result, list) and result:
        return result[0] if isinstance(result[0], dict) else None

    if isinstance(result, dict):
        return result

    return None


def parse_set_pair_from_text(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    match = re.search(r"(\d+)\s*-\s*(\d+)", text)

    if not match:
        return None

    return int(match.group(1)), int(match.group(2))


def parse_score_number(value: Any) -> int | None:
    """
    API-Tennis can return tie-break sets as 6.5 / 7.7.
    Only the number before the dot is the game score.
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if "." in text:
        text = text.split(".", 1)[0]

    try:
        return int(text)
    except ValueError:
        return None


def parse_scores(scores: Any) -> list[tuple[int, int]]:
    parsed: list[tuple[int, int]] = []

    if not isinstance(scores, list):
        return parsed

    for item in scores:
        if not isinstance(item, dict):
            pair = parse_set_pair_from_text(item)
            if pair:
                parsed.append(pair)
            continue

        first = item.get("score_first")
        second = item.get("score_second")

        if first is not None and second is not None:
            a = parse_score_number(first)
            b = parse_score_number(second)

            if a is not None and b is not None:
                parsed.append((a, b))
                continue

        for key in (
            "score",
            "result",
            "set_score",
            "event_score",
            "score_set",
            "games",
            "value",
        ):
            pair = parse_set_pair_from_text(item.get(key))

            if pair:
                parsed.append(pair)
                break

    return parsed


def parse_scores_from_fixture(
    fixture: dict[str, Any],
) -> list[tuple[int, int]]:
    parsed = parse_scores(fixture.get("scores") or [])

    if parsed:
        return parsed

    for key in (
        "event_final_result",
        "event_game_result",
        "event_result",
        "event_score",
        "final_score",
        "score",
    ):
        value = fixture.get(key)

        if not value:
            continue

        pairs = re.findall(r"(\d+)\s*-\s*(\d+)", str(value))

        if pairs:
            return [(int(a), int(b)) for a, b in pairs]

    return []


def is_bad_terminal_status(status: Any) -> bool:
    value = str(status or "").lower().strip()
    compact = (
        value.replace(" ", "")
        .replace("-", "")
        .replace("/", "")
        .replace(".", "")
    )

    return value in BAD_TERMINAL_STATUSES or compact in BAD_TERMINAL_STATUSES


def compact_fixture_debug(fixture: Any) -> Any:
    if not isinstance(fixture, dict):
        return fixture

    score_related = {}

    for key, value in fixture.items():
        lower = str(key).lower()

        if any(
            marker in lower
            for marker in (
                "score",
                "result",
                "set",
                "winner",
                "status",
            )
        ):
            score_related[key] = value

    return score_related


def pick_id(pick: dict[str, Any]) -> str:
    existing = str(pick.get("pick_id") or "").strip()

    if existing:
        return existing

    event_key = str(pick.get("event_key") or "").strip()
    side = str(pick.get("side") or "under").strip().lower()
    line = safe_float(pick.get("line"), 9.5)
    strategy_id = str(pick.get("strategy_id") or "").strip()

    suffix = f"|{strategy_id}" if strategy_id else ""

    return f"{event_key}|first_set|{side}|{line:.1f}{suffix}"


def normalize_remote_pick(pick: dict[str, Any]) -> dict[str, Any]:
    line = safe_float(pick.get("line"), 9.5) or 9.5
    side = str(pick.get("side") or "under").lower().strip()
    odds = safe_float(
        pick.get("odds")
        or pick.get("under_odds")
        or pick.get("over_odds")
    )
    stake = safe_float(pick.get("stake"), DEFAULT_STAKE) or DEFAULT_STAKE

    normalized = dict(pick)
    normalized.update(
        {
            "pick_id": pick_id(pick),
            "market": clean_market_name(pick.get("market")),
            "side": side,
            "line": line,
            "odds": odds,
            "stake": stake,
            "result": str(pick.get("result") or "pending").lower(),
            "profit": safe_float(pick.get("profit"), 0.0) or 0.0,
            "imported_at": pick.get("imported_at") or now_iso(),
        }
    )

    return normalized


def sync_new_picks(
    existing: list[dict[str, Any]],
    remote_payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    remote = remote_payload.get("shadow_picks") or []

    if not isinstance(remote, list):
        remote = []

    by_id = {
        pick_id(item): item
        for item in existing
        if isinstance(item, dict)
    }
    order = [
        pick_id(item)
        for item in existing
        if isinstance(item, dict)
    ]

    added = 0

    for item in remote:
        if not isinstance(item, dict):
            continue

        normalized = normalize_remote_pick(item)
        key = normalized["pick_id"]

        if key not in by_id:
            by_id[key] = normalized
            order.append(key)
            added += 1
            continue

        # Preserve settlement fields, but refresh missing metadata.
        current = by_id[key]

        for field, value in normalized.items():
            if current.get(field) in (None, "", [], {}) and value not in (
                None,
                "",
                [],
                {},
            ):
                current[field] = value

    return [by_id[key] for key in order], added


def settle_pick(
    pick: dict[str, Any],
    fixture: dict[str, Any],
) -> tuple[bool, str]:
    status_raw = fixture.get("event_status")
    status = str(status_raw or "").lower().strip()

    if is_bad_terminal_status(status):
        pick.update(
            {
                "result": "void",
                "profit": 0.0,
                "settled_at": now_iso(),
                "settled_status": status_raw,
                "event_winner": fixture.get("event_winner"),
                "final_score": None,
                "first_set_score": None,
                "first_set_games": None,
            }
        )
        return True, "void_bad_terminal_status"

    if status != "finished":
        return False, "not_finished"

    parsed = parse_scores_from_fixture(fixture)

    if not parsed:
        return False, "no_scores"

    first_a, first_b = parsed[0]
    first_set_games = first_a + first_b

    line = safe_float(pick.get("line"))
    side = str(pick.get("side") or "").lower()
    stake = safe_float(pick.get("stake"), DEFAULT_STAKE) or DEFAULT_STAKE
    odds = safe_float(pick.get("odds"))

    if line is None:
        return False, "bad_line"

    if side not in {"over", "under"}:
        return False, "bad_side"

    if odds is None or odds <= 1:
        return False, "bad_odds"

    if first_set_games == line:
        result = "push"
        profit = 0.0
    elif side == "over":
        won = first_set_games > line
        result = "win" if won else "loss"
        profit = stake * (odds - 1) if won else -stake
    else:
        won = first_set_games < line
        result = "win" if won else "loss"
        profit = stake * (odds - 1) if won else -stake

    pick.update(
        {
            "result": result,
            "profit": round(profit, 3),
            "settled_at": now_iso(),
            "settled_status": status_raw,
            "event_winner": fixture.get("event_winner"),
            "final_score": ", ".join(
                f"{a}-{b}" for a, b in parsed
            ),
            "first_set_score": f"{first_a}-{first_b}",
            "first_set_games": first_set_games,
        }
    )

    return True, "settled"


def performance(results: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [
        item
        for item in results
        if str(item.get("result") or "").lower()
        in {"win", "loss", "push", "void"}
    ]
    graded = [
        item
        for item in settled
        if str(item.get("result") or "").lower()
        in {"win", "loss"}
    ]

    wins = sum(item.get("result") == "win" for item in settled)
    losses = sum(item.get("result") == "loss" for item in settled)
    pushes = sum(item.get("result") == "push" for item in settled)
    voids = sum(item.get("result") == "void" for item in settled)
    pending = sum(
        str(item.get("result") or "pending").lower() == "pending"
        for item in results
    )
    staked = sum(
        safe_float(item.get("stake"), 0.0) or 0.0
        for item in graded
    )
    profit = round(
        sum(safe_float(item.get("profit"), 0.0) or 0.0 for item in settled),
        3,
    )

    return {
        "total_picks": len(results),
        "pending": pending,
        "settled": len(settled),
        "graded": len(graded),
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "voids": voids,
        "hit_rate": round(wins / len(graded), 4) if graded else None,
        "total_staked": round(staked, 3),
        "profit": profit,
        "roi": round(profit / staked, 4) if staked else None,
    }


def main() -> None:
    ensure_dirs()

    remote_payload = fetch_remote_json(PICKS_URL)
    results = load_json(RESULTS_FILE, [])

    if not isinstance(results, list):
        results = []

    results, added = sync_new_picks(results, remote_payload)

    pending = [
        item
        for item in results
        if isinstance(item, dict)
        and str(item.get("result") or "pending").lower() == "pending"
    ]

    debug = {
        "generated_at": now_iso(),
        "source_picks_url": PICKS_URL,
        "remote_shadow_picks": len(
            remote_payload.get("shadow_picks") or []
        ),
        "added": added,
        "pending_before": len(pending),
        "updated": 0,
        "still_pending": 0,
        "not_found": 0,
        "errors": [],
        "items": [],
    }

    print(f"NEW FIRST-SET PICKS ADDED: {added}")
    print(f"PENDING FIRST-SET PICKS: {len(pending)}")

    for pick in pending:
        event_key = pick.get("event_key")
        match_name = pick.get("match")

        if not event_key:
            debug["errors"].append(
                {
                    "pick_id": pick.get("pick_id"),
                    "error": "missing_event_key",
                }
            )
            continue

        try:
            fixture = fetch_fixture_by_event_key(event_key)

            if not fixture:
                debug["not_found"] += 1
                debug["items"].append(
                    {
                        "event_key": event_key,
                        "pick_id": pick.get("pick_id"),
                        "match": match_name,
                        "status": "not_found",
                    }
                )
                print(
                    f"NO MATCH FOUND: {match_name} | "
                    f"event_key={event_key}"
                )
                continue

            changed, reason = settle_pick(pick, fixture)

            if changed:
                debug["updated"] += 1
                print(
                    f"SETTLED: {match_name} | "
                    f"{pick.get('side')} {pick.get('line')} | "
                    f"{pick.get('result')} | "
                    f"first_set={pick.get('first_set_score')} | "
                    f"profit={pick.get('profit')}"
                )
            else:
                debug["still_pending"] += 1
                print(
                    f"PENDING: {match_name} | reason={reason} | "
                    f"status={fixture.get('event_status')}"
                )

            debug["items"].append(
                {
                    "event_key": event_key,
                    "pick_id": pick.get("pick_id"),
                    "match": match_name,
                    "side": pick.get("side"),
                    "line": pick.get("line"),
                    "odds": pick.get("odds"),
                    "status": reason,
                    "api_status": fixture.get("event_status"),
                    "result": pick.get("result"),
                    "first_set_score": pick.get("first_set_score"),
                    "first_set_games": pick.get("first_set_games"),
                    "final_score": pick.get("final_score"),
                    "profit": pick.get("profit"),
                    "raw_scores": fixture.get("scores"),
                    "score_debug": compact_fixture_debug(fixture),
                }
            )

        except Exception as exc:
            debug["errors"].append(
                {
                    "event_key": event_key,
                    "match": match_name,
                    "error": str(exc),
                }
            )
            print(f"ERROR {event_key} {match_name}: {exc}")

    debug["performance"] = performance(results)

    save_json(RESULTS_FILE, results)
    save_json(DEBUG_FILE, debug)

    print("")
    print("TENNIS FIRST SET SETTLE DONE")
    print(
        {
            "added": added,
            "updated": debug["updated"],
            "still_pending": debug["still_pending"],
            "not_found": debug["not_found"],
            "errors": len(debug["errors"]),
        }
    )
    print("PERFORMANCE:", debug["performance"])
    print(f"Results: {RESULTS_FILE}")
    print(f"Debug:   {DEBUG_FILE}")
    print("")


if __name__ == "__main__":
    main()

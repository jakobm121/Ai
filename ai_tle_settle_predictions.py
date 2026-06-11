from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


DEFAULT_PICKS_PATH = Path("data") / "tle" / "predictions" / "ai_tle_predictions_latest.json"
DEFAULT_OUTPUT_DIR = Path("data") / "tle" / "settlement"
API_BASE_URL = "https://api.api-tennis.com/tennis/"


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


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def load_json_any(path_or_url: str | Path) -> Any:
    text = str(path_or_url)
    if text.startswith("http://") or text.startswith("https://"):
        response = requests.get(text, timeout=90)
        response.raise_for_status()
        return response.json()
    return json.loads(Path(text).read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def extract_picks(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("picks"), list):
        return [row for row in payload["picks"] if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    raise RuntimeError("Tennis-ELO predictions JSON has no list field 'picks'.")


def api_get_fixtures(api_key: str, date_start: str, date_stop: str, timezone_name: str = "Europe/Ljubljana") -> list[dict[str, Any]]:
    params = {
        "method": "get_fixtures",
        "APIkey": api_key,
        "date_start": date_start,
        "date_stop": date_stop,
        "timezone": timezone_name,
    }

    response = requests.get(API_BASE_URL, params=params, timeout=120)
    response.raise_for_status()
    payload = response.json()

    result = payload.get("result") if isinstance(payload, dict) else None
    if result is None:
        return []
    if isinstance(result, list):
        return [row for row in result if isinstance(row, dict)]
    if isinstance(result, dict):
        return [result]
    return []


def event_key(row: dict[str, Any]) -> str:
    return clean(row.get("event_key") or row.get("event_id") or row.get("id"))


def index_fixtures(fixtures: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index = {}
    for row in fixtures:
        key = event_key(row)
        if not key:
            continue

        old = index.get(key)
        if old is None or fixture_richness(row) >= fixture_richness(old):
            index[key] = row

    return index


def fixture_richness(row: dict[str, Any]) -> int:
    score = 0
    for key in [
        "event_winner",
        "event_status",
        "event_final_result",
        "event_first_player",
        "event_second_player",
        "event_date",
    ]:
        if clean(row.get(key)):
            score += 1
    return score


def status_text(fixture: dict[str, Any] | None) -> str:
    if not fixture:
        return ""
    return clean(
        fixture.get("event_status")
        or fixture.get("status")
        or fixture.get("match_status")
        or fixture.get("event_status_info")
    )


def is_void_status(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in [
            "cancel",
            "postpon",
            "abandon",
            "walkover",
            "w/o",
            "retired",
            "ret.",
            "void",
            "interrupted",
        ]
    )


def is_pending_status(text: str) -> bool:
    lowered = text.lower()
    if not lowered:
        return True
    return any(
        token in lowered
        for token in [
            "not started",
            "scheduled",
            "pending",
            "live",
            "in progress",
            "set",
            "game",
            "break",
        ]
    )


def winner_side_from_api_value(value: Any) -> str | None:
    text = clean(value).lower()
    text = text.replace("_", " ").replace("-", " ")

    if not text:
        return None

    if text in {"first player", "first", "home", "player 1", "player1", "p1", "1"}:
        return "player_1"

    if text in {"second player", "second", "away", "player 2", "player2", "p2", "2"}:
        return "player_2"

    if "first player" in text:
        return "player_1"

    if "second player" in text:
        return "player_2"

    return None


def winner_side_from_names(fixture: dict[str, Any], pick: dict[str, Any]) -> str | None:
    raw_winner = clean(fixture.get("event_winner") or fixture.get("winner"))
    winner_norm = normalize_name(raw_winner)

    if not winner_norm:
        return None

    first_names = [
        fixture.get("event_first_player"),
        fixture.get("first_player"),
        fixture.get("player_1"),
        pick.get("home_player"),
        pick.get("player_1"),
    ]

    second_names = [
        fixture.get("event_second_player"),
        fixture.get("second_player"),
        fixture.get("player_2"),
        pick.get("away_player"),
        pick.get("player_2"),
    ]

    for name in first_names:
        n = normalize_name(name)
        if n and (winner_norm == n or winner_norm in n or n in winner_norm):
            return "player_1"

    for name in second_names:
        n = normalize_name(name)
        if n and (winner_norm == n or winner_norm in n or n in winner_norm):
            return "player_2"

    selection_norm = normalize_name(pick.get("selection"))
    if selection_norm and (winner_norm == selection_norm or winner_norm in selection_norm or selection_norm in winner_norm):
        return clean(pick.get("selected_player_side")) or None

    return None


def winner_side(fixture: dict[str, Any], pick: dict[str, Any]) -> str | None:
    for key in ["event_winner", "winner", "winner_side", "event_winner_side"]:
        side = winner_side_from_api_value(fixture.get(key))
        if side:
            return side

    return winner_side_from_names(fixture, pick)


def final_score(fixture: dict[str, Any] | None) -> str:
    if not fixture:
        return ""
    return clean(
        fixture.get("event_final_result")
        or fixture.get("final_score")
        or fixture.get("event_result")
        or fixture.get("result")
    )


def settle_pick(pick: dict[str, Any], fixture: dict[str, Any] | None) -> dict[str, Any]:
    selected_side = clean(pick.get("selected_player_side"))
    odds = (
        safe_float(pick.get("first_odds"))
        or safe_float(pick.get("odds"))
        or safe_float(pick.get("latest_odds"))
    )

    if fixture is None:
        status = "PENDING"
        reason = "fixture_not_found"
        won = None
        profit = 0.0
        win_side = None
    else:
        api_status = status_text(fixture)

        if is_void_status(api_status):
            status = "VOID"
            reason = "void_status"
            won = None
            profit = 0.0
            win_side = None
        else:
            win_side = winner_side(fixture, pick)

            if win_side not in {"player_1", "player_2"}:
                if is_pending_status(api_status):
                    status = "PENDING"
                    reason = "not_finished"
                else:
                    status = "PENDING"
                    reason = "winner_not_resolved"
                won = None
                profit = 0.0
            elif selected_side not in {"player_1", "player_2"}:
                status = "PENDING"
                reason = "selected_side_not_resolved"
                won = None
                profit = 0.0
            elif odds is None or odds <= 1.0:
                status = "PENDING"
                reason = "invalid_odds"
                won = None
                profit = 0.0
            else:
                won = selected_side == win_side
                status = "WIN" if won else "LOSS"
                reason = "settled"
                profit = odds - 1.0 if won else -1.0

    return {
        **pick,
        "settlement_status": status,
        "settlement_reason": reason,
        "settlement_odds": odds,
        "stake": 1.0,
        "profit": round(profit, 6),
        "won": won,
        "winner_side": win_side,
        "api_event_status": status_text(fixture),
        "api_event_winner": clean((fixture or {}).get("event_winner") or (fixture or {}).get("winner")),
        "api_final_score": final_score(fixture),
        "api_first_player": clean((fixture or {}).get("event_first_player")),
        "api_second_player": clean((fixture or {}).get("event_second_player")),
        "api_event_date": clean((fixture or {}).get("event_date")),
        "api_event_time": clean((fixture or {}).get("event_time")),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row["settlement_status"] in {"WIN", "LOSS"}]
    wins = [row for row in settled if row["settlement_status"] == "WIN"]
    losses = [row for row in settled if row["settlement_status"] == "LOSS"]
    voids = [row for row in rows if row["settlement_status"] == "VOID"]
    pending = [row for row in rows if row["settlement_status"] == "PENDING"]

    staked = float(len(settled))
    profit = sum(float(row.get("profit") or 0.0) for row in settled)

    return {
        "total_picks": len(rows),
        "settled_bets": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "void": len(voids),
        "pending": len(pending),
        "staked": round(staked, 6),
        "profit": round(profit, 6),
        "roi": round(profit / staked, 6) if staked else None,
        "hit_rate": round(len(wins) / len(settled), 6) if settled else None,
        "avg_odds": round(
            sum(float(row.get("settlement_odds") or 0.0) for row in settled) / len(settled),
            6,
        ) if settled else None,
    }


def summarize_by(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = sorted({clean(row.get(field)) for row in rows if clean(row.get(field))})
    return {
        value: summarize([row for row in rows if clean(row.get(field)) == value])
        for value in values
    }


def pct(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return ""
    return f"{number * 100:.2f}%"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "date",
        "time",
        "tour_level",
        "gender",
        "surface",
        "match",
        "selection",
        "settlement_status",
        "settlement_odds",
        "profit",
        "tle_probability",
        "book_probability_devig",
        "tle_edge",
        "tle_ev",
        "event_key",
        "winner_side",
        "api_event_winner",
        "api_final_score",
        "api_event_status",
        "settlement_reason",
        "first_seen_at",
        "last_seen_at",
        "ledger_status",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})

    tmp.replace(path)


def write_md(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    overall = summary["overall"]

    lines = [
        "# TLE Scanner Settlement",
        "",
        f"Generated: `{summary.get('generated_at')}`",
        f"Source picks: `{summary.get('picks_source')}`",
        f"Settled bets: `{overall.get('settled_bets')}`",
        f"Pending: `{overall.get('pending')}`",
        f"Profit: `{overall.get('profit')}`",
        f"ROI: `{pct(overall.get('roi'))}`",
        f"Hit rate: `{pct(overall.get('hit_rate'))}`",
        "",
        "## By level",
        "",
        "| Level | Bets | W | L | Pending | Profit | ROI | Hit rate | Avg odds |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for level, item in summary.get("by_level", {}).items():
        lines.append(
            f"| {level} | {item.get('settled_bets')} | {item.get('wins')} | {item.get('losses')} | "
            f"{item.get('pending')} | {item.get('profit')} | {pct(item.get('roi'))} | "
            f"{pct(item.get('hit_rate'))} | {item.get('avg_odds')} |"
        )

    lines.extend(
        [
            "",
            "## Picks",
            "",
            "| Date | Time | Level | Match | Pick | Odds | Result | Profit | Edge | EV | Winner | Score | Reason |",
            "|---|---|---|---|---|---:|---|---:|---:|---:|---|---|---|",
        ]
    )

    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    clean(row.get("date")),
                    clean(row.get("time")),
                    clean(row.get("tour_level")),
                    clean(row.get("match")).replace("|", "-"),
                    clean(row.get("selection")).replace("|", "-"),
                    clean(row.get("settlement_odds")),
                    clean(row.get("settlement_status")),
                    clean(row.get("profit")),
                    pct(row.get("tle_edge")),
                    pct(row.get("tle_ev")),
                    clean(row.get("api_event_winner")).replace("|", "-"),
                    clean(row.get("api_final_score")).replace("|", "-"),
                    clean(row.get("settlement_reason")),
                ]
            )
            + " |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)


def date_label_from_rows(rows: list[dict[str, Any]]) -> str:
    dates = sorted({clean(row.get("date")) for row in rows if clean(row.get("date"))})
    if not dates:
        return "latest"
    if len(dates) == 1:
        return dates[0]
    return f"{dates[0]}_{dates[-1]}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Settle AI repo TLE open predictions. Keeps picks in predictions until WIN/LOSS/VOID."
    )
    parser.add_argument("--picks", default=str(DEFAULT_PICKS_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--timezone", default="Europe/Ljubljana")
    parser.add_argument("--api-sleep-seconds", type=float, default=0.0)
    args = parser.parse_args()

    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY environment variable.")

    picks_path = Path(args.picks)
    picks_payload = load_json_any(args.picks)
    picks = extract_picks(picks_payload)

    if not picks:
        raise RuntimeError("No Tennis-ELO picks found.")

    dates = sorted({clean(row.get("date")) for row in picks if clean(row.get("date"))})
    if not dates:
        raise RuntimeError("No pick dates found.")

    date_start = dates[0]
    date_stop = dates[-1]

    fixtures = api_get_fixtures(
        api_key=api_key,
        date_start=date_start,
        date_stop=date_stop,
        timezone_name=args.timezone,
    )

    if args.api_sleep_seconds > 0:
        time.sleep(args.api_sleep_seconds)

    fixtures_index = index_fixtures(fixtures)

    settled_rows = []
    counters = Counter()

    for pick in picks:
        key = clean(pick.get("event_key"))
        fixture = fixtures_index.get(key)
        settled = settle_pick(pick, fixture)
        settled_rows.append(settled)

        counters[f"status_{settled['settlement_status'].lower()}"] += 1
        counters[f"reason_{settled['settlement_reason']}"] += 1

    # Keep only unresolved picks in predictions; settled rows go to settlement history.
    still_open = [row for row in settled_rows if row.get("settlement_status") == "PENDING"]
    newly_closed = [row for row in settled_rows if row.get("settlement_status") in {"WIN", "LOSS", "VOID"}]

    history_path = Path(args.output_dir) / "ai_tle_settlement_history.json"
    old_history = []
    if history_path.exists():
        try:
            old_payload = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(old_payload, dict) and isinstance(old_payload.get("settled_picks"), list):
                old_history = [r for r in old_payload["settled_picks"] if isinstance(r, dict)]
        except Exception:
            old_history = []

    def row_key(row: dict[str, Any]) -> str:
        return "|".join([clean(row.get("event_key")), clean(row.get("selected_player_side")), normalize_name(row.get("selection"))])

    history_by_key = {row_key(r): r for r in old_history if row_key(r)}
    for r in newly_closed:
        history_by_key[row_key(r)] = r
    history_rows = sorted(history_by_key.values(), key=lambda r: (clean(r.get("date")), clean(r.get("time")), clean(r.get("event_key"))))

    open_predictions_payload = {
        "schema_version": 1,
        "file_type": "ai_repo_tle_open_predictions",
        "summary": {
            "generated_at": now_iso(),
            "open_predictions_count": len(still_open),
            "removed_settled_this_run": len(newly_closed),
        },
        "picks": still_open,
    }
    if not str(args.picks).startswith("http"):
        save_json(picks_path, open_predictions_payload)

    settled_rows.sort(
        key=lambda row: (
            clean(row.get("date")),
            clean(row.get("time")),
            clean(row.get("event_key")),
            clean(row.get("selection")),
        )
    )

    label = date_label_from_rows(settled_rows)
    out_dir = Path(args.output_dir)

    output_json = out_dir / f"tle_scanner_settlement_{label}.json"
    output_csv = out_dir / f"tle_scanner_settlement_{label}.csv"
    output_md = out_dir / f"tle_scanner_settlement_{label}.md"

    latest_json = out_dir / "tle_scanner_settlement_latest.json"
    latest_csv = out_dir / "tle_scanner_settlement_latest.csv"
    latest_md = out_dir / "tle_scanner_settlement_latest.md"

    raw_fixtures_path = out_dir / f"tle_scanner_settlement_raw_fixtures_{label}.json"
    raw_fixtures_latest = out_dir / "tle_scanner_settlement_raw_fixtures_latest.json"

    summary = {
        "generated_at": now_iso(),
        "picks_source": str(args.picks),
        "date_start": date_start,
        "date_stop": date_stop,
        "date_label": label,
        "api_fixtures_loaded": len(fixtures),
        "api_events_indexed": len(fixtures_index),
        "picks_loaded": len(picks),
        "counters": dict(sorted(counters.items())),
        "overall": summarize(settled_rows),
        "by_level": summarize_by(settled_rows, "tour_level"),
        "by_gender": summarize_by(settled_rows, "gender"),
        "by_status": summarize_by(settled_rows, "settlement_status"),
    }

    payload = {
        "schema_version": 1,
        "summary": summary,
        "settled_picks": settled_rows,
    }

    for path in [output_json, latest_json]:
        save_json(path, payload)

    for path in [output_csv, latest_csv]:
        write_csv(path, settled_rows)

    for path in [output_md, latest_md]:
        write_md(path, summary, settled_rows)

    history_payload = {
        "schema_version": 1,
        "summary": {
            "generated_at": summary["generated_at"],
            "total_settled_history": len(history_rows),
            "newly_closed_this_run": len(newly_closed),
            "open_remaining": len(still_open),
            "overall_history": summarize(history_rows),
            "by_level_history": summarize_by(history_rows, "tour_level"),
        },
        "settled_picks": history_rows,
    }
    save_json(history_path, history_payload)

    raw_payload = {
        "generated_at": summary["generated_at"],
        "date_start": date_start,
        "date_stop": date_stop,
        "fixtures": fixtures,
    }

    for path in [raw_fixtures_path, raw_fixtures_latest]:
        save_json(path, raw_payload)

    print("AI TLE PREDICTIONS SETTLEMENT DONE")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON: {output_json}")
    print(f"CSV: {output_csv}")
    print(f"MD: {output_md}")
    print(f"Latest JSON: {latest_json}")
    print(f"Latest CSV: {latest_csv}")
    print(f"Latest MD: {latest_md}")
    print(f"Raw fixtures: {raw_fixtures_path}")
    print(f"Updated open predictions: {args.picks}")
    print(f"Settlement history: {history_path}")


if __name__ == "__main__":
    main()

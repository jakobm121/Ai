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




def write_active_predictions_table(path: Path, picks: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# AI TLE Active Predictions",
        "",
        f"Generated: `{summary.get('generated_at')}`",
        f"Active predictions: `{len(picks)}`",
        f"Results ledger: `{summary.get('results_path')}`",
        "",
        "| # | Date | Time | Level | Match | Pick | Odds | TLE % | Book % | Edge | EV | Status |",
        "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for i, p in enumerate(picks, 1):
        odds = p.get("first_odds") or p.get("odds") or p.get("latest_odds")
        lines.append("| " + " | ".join([
            str(i),
            clean(p.get("date")),
            clean(p.get("time")),
            clean(p.get("tour_level")),
            clean(p.get("match")).replace("|", "-"),
            clean(p.get("selection")).replace("|", "-"),
            clean(odds),
            pct(p.get("first_tle_probability") or p.get("tle_probability")),
            pct(p.get("first_book_probability_devig") or p.get("book_probability_devig")),
            pct(p.get("first_tle_edge") or p.get("tle_edge")),
            pct(p.get("first_tle_ev") or p.get("tle_ev")),
            clean(p.get("settlement_status") or "PENDING"),
        ]) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_results_table(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    overall = summary.get("overall", {})
    lines = [
        "# AI TLE Results",
        "",
        f"Generated: `{summary.get('generated_at')}`",
        f"Total picks: `{overall.get('total_picks')}`",
        f"Settled bets: `{overall.get('settled_bets')}`",
        f"Pending: `{overall.get('pending')}`",
        f"Profit: `{overall.get('profit')}`",
        f"ROI: `{pct(overall.get('roi'))}`",
        f"Hit rate: `{pct(overall.get('hit_rate'))}`",
        "",
        "| # | Date | Time | Level | Match | Pick | Odds | Status | Profit | Edge | EV | Winner | Score | Reason |",
        "|---:|---|---|---|---|---|---:|---|---:|---:|---:|---|---|---|",
    ]
    for i, row in enumerate(rows, 1):
        status = clean(row.get("settlement_status") or "PENDING")
        profit = "" if status == "PENDING" else clean(row.get("profit"))
        odds = row.get("settlement_odds") or row.get("first_odds") or row.get("odds") or row.get("latest_odds")
        lines.append("| " + " | ".join([
            str(i),
            clean(row.get("date")),
            clean(row.get("time")),
            clean(row.get("tour_level")),
            clean(row.get("match")).replace("|", "-"),
            clean(row.get("selection")).replace("|", "-"),
            clean(odds),
            status,
            profit,
            pct(row.get("first_tle_edge") or row.get("tle_edge")),
            pct(row.get("first_tle_ev") or row.get("tle_ev")),
            clean(row.get("api_event_winner")).replace("|", "-"),
            clean(row.get("api_final_score")).replace("|", "-"),
            clean(row.get("settlement_reason")),
        ]) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)


def pick_key(row: dict[str, Any]) -> str:
    return "|".join([
        clean(row.get("event_key")),
        clean(row.get("selected_player_side") or row.get("selected_side")),
        normalize_name(row.get("selection")),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Settle AI TLE results ledger. Keeps active predictions open until settled."
    )
    parser.add_argument("--results", default="data/tle/predictions/ai_tle_results.json")
    parser.add_argument("--picks", default="", help="Deprecated alias; use --results")
    parser.add_argument("--predictions", default="data/tle/predictions/ai_tle_predictions_latest.json")
    parser.add_argument("--predictions-table", default="data/tle/predictions/ai_tle_predictions_table.md")
    parser.add_argument("--results-table", default="data/tle/predictions/ai_tle_results_table.md")
    parser.add_argument("--timezone", default="Europe/Ljubljana")
    parser.add_argument("--api-sleep-seconds", type=float, default=0.0)
    args = parser.parse_args()

    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY environment variable.")

    results_path = Path(args.picks or args.results)
    predictions_path = Path(args.predictions)
    predictions_table_path = Path(args.predictions_table)
    results_table_path = Path(args.results_table)

    results_payload = load_json_any(results_path)
    all_rows = extract_picks(results_payload)
    if not all_rows:
        raise RuntimeError("No AI TLE results picks found.")

    pending_rows = [r for r in all_rows if clean(r.get("settlement_status") or "PENDING").upper() == "PENDING"]
    dates = sorted({clean(row.get("date")) for row in pending_rows if clean(row.get("date"))})

    fixtures: list[dict[str, Any]] = []
    fixtures_index: dict[str, dict[str, Any]] = {}
    date_start = dates[0] if dates else ""
    date_stop = dates[-1] if dates else ""

    if dates:
        fixtures = api_get_fixtures(
            api_key=api_key,
            date_start=date_start,
            date_stop=date_stop,
            timezone_name=args.timezone,
        )
        if args.api_sleep_seconds > 0:
            time.sleep(args.api_sleep_seconds)
        fixtures_index = index_fixtures(fixtures)

    updated_by_key: dict[str, dict[str, Any]] = {}
    counters = Counter()
    generated_at = now_iso()

    for row in all_rows:
        status_before = clean(row.get("settlement_status") or "PENDING").upper()
        if status_before in {"WIN", "LOSS", "VOID"}:
            updated = dict(row)
            counters[f"status_{status_before.lower()}"] += 1
        else:
            fixture = fixtures_index.get(clean(row.get("event_key")))
            updated = settle_pick(row, fixture)
            status_after = clean(updated.get("settlement_status") or "PENDING").upper()
            if status_after in {"WIN", "LOSS", "VOID"}:
                updated["settled_at"] = generated_at
            counters[f"status_{status_after.lower()}"] += 1
            counters[f"reason_{updated.get('settlement_reason')}"] += 1
        key = pick_key(updated)
        if key:
            updated_by_key[key] = updated

    updated_rows = list(updated_by_key.values())
    updated_rows.sort(key=lambda r: (clean(r.get("date")), clean(r.get("time")), clean(r.get("event_key")), clean(r.get("selection"))))
    active_rows = [r for r in updated_rows if clean(r.get("settlement_status") or "PENDING").upper() == "PENDING"]
    active_rows.sort(key=lambda r: (clean(r.get("date")), clean(r.get("time")), -float(r.get("first_tle_edge") or r.get("tle_edge") or 0)))

    summary = {
        "generated_at": generated_at,
        "results_path": str(results_path),
        "predictions_path": str(predictions_path),
        "date_start": date_start,
        "date_stop": date_stop,
        "api_fixtures_loaded": len(fixtures),
        "api_events_indexed": len(fixtures_index),
        "results_loaded": len(all_rows),
        "results_total_after_settle": len(updated_rows),
        "active_predictions_after_settle": len(active_rows),
        "counters": dict(sorted(counters.items())),
        "overall": summarize(updated_rows),
        "by_level": summarize_by(updated_rows, "tour_level"),
        "by_gender": summarize_by(updated_rows, "gender"),
        "by_status": summarize_by(updated_rows, "settlement_status"),
        "files_written": [
            str(results_path),
            str(predictions_path),
            str(predictions_table_path),
            str(results_table_path),
        ],
    }

    new_results_payload = {
        "schema_version": 1,
        "file_type": "ai_tle_results_ledger",
        "summary": summary,
        "picks": updated_rows,
    }
    predictions_payload = {
        "schema_version": 1,
        "file_type": "ai_tle_open_predictions",
        "summary": summary,
        "picks": active_rows,
    }

    save_json(results_path, new_results_payload)
    save_json(predictions_path, predictions_payload)
    write_active_predictions_table(predictions_table_path, active_rows, summary)
    write_results_table(results_table_path, updated_rows, summary)

    print("AI TLE SETTLEMENT DONE")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Results ledger: {results_path}")
    print(f"Open predictions: {predictions_path}")
    print(f"Active table: {predictions_table_path}")
    print(f"Results table: {results_table_path}")


if __name__ == "__main__":
    main()

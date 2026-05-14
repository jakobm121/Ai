#!/usr/bin/env python3
"""
Audit raw tennis API payloads for AI77 totals model.

This script is read-only:
- does not change predictions
- does not change results
- does not call betting logic
- only inspects saved raw API JSON files

Usage:
    python scripts/audit_totals_api_payload.py
    python scripts/audit_totals_api_payload.py --input data/debug_api
    python scripts/audit_totals_api_payload.py --input data/debug_api/raw_response.json

Recommended flow:
    1. Save raw API responses from tennis_totals_predictions.py into data/debug_api/
    2. Run this script
    3. Check data/debug_api_schema_audit.json and .txt
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


DEFAULT_INPUT = Path("data/debug_api")
DEFAULT_JSON_OUT = Path("data/debug_api_schema_audit.json")
DEFAULT_TXT_OUT = Path("data/debug_api_schema_audit.txt")


KNOWN_USED_FIELDS = {
    # Match / pick basics
    "match_id",
    "id",
    "fixture_id",
    "home_player",
    "away_player",
    "player1",
    "player2",
    "first_player",
    "second_player",
    "tournament",
    "league",
    "tour",
    "tour_level",
    "gender",
    "start_time",
    "commence_time",

    # Totals market
    "line",
    "total_line",
    "market_line",
    "odds",
    "over_odds",
    "under_odds",
    "best_odds",
    "bookmaker",
    "bookmakers",
    "market_info",
    "market_gap",
    "market_median_odds",
    "bookmakers_used",

    # Model fields already visible in current results/audit
    "side",
    "pick",
    "confidence",
    "quality_score",
    "edge",
    "model_prob",
    "implied_prob",
    "expected_margin",
    "expected_total_games",
    "first_form",
    "second_form",
    "combined_three_set_rate",
    "combined_close_set_rate",
    "combined_over_21_5_rate",
    "strength_gap",
}


INTERESTING_KEYWORDS = [
    "surface",
    "court",
    "indoor",
    "outdoor",
    "venue",
    "round",
    "best_of",
    "rank",
    "ranking",
    "seed",
    "elo",
    "rating",
    "form",
    "last",
    "streak",
    "h2h",
    "head",
    "injury",
    "retired",
    "walkover",
    "withdraw",
    "status",
    "score",
    "sets",
    "games",
    "tiebreak",
    "tie_break",
    "odds",
    "price",
    "bookmaker",
    "opening",
    "closing",
    "movement",
    "line",
    "market",
    "prob",
    "probability",
    "weather",
]


def load_json_files(path: Path) -> List[Tuple[Path, Any]]:
    files: List[Path] = []

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted(path.glob("*.json"))
    else:
        raise FileNotFoundError(f"Input path not found: {path}")

    payloads: List[Tuple[Path, Any]] = []

    for file_path in files:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                payloads.append((file_path, json.load(f)))
        except Exception as exc:
            print(f"Skipping {file_path}: {exc}")

    return payloads


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def short_sample(value: Any, max_len: int = 120) -> Any:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)

    if len(text) > max_len:
        return text[:max_len] + "..."

    return value


def walk(
    obj: Any,
    prefix: str = "",
    depth: int = 0,
    max_array_items: int = 5,
) -> Iterable[Tuple[str, Any]]:
    """
    Yield flattened key paths and values.

    Lists are represented as [].
    Example:
        response[].bookmakers[].markets[].outcomes[].price
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            key = str(key)
            new_prefix = f"{prefix}.{key}" if prefix else key
            yield new_prefix, value
            yield from walk(value, new_prefix, depth + 1, max_array_items)

    elif isinstance(obj, list):
        list_prefix = f"{prefix}[]" if prefix else "[]"
        yield list_prefix, obj

        for item in obj[:max_array_items]:
            yield from walk(item, list_prefix, depth + 1, max_array_items)


def base_key(path: str) -> str:
    clean = path.replace("[]", "")
    return clean.split(".")[-1].lower()


def is_interesting(path: str) -> bool:
    low = path.lower()
    return any(keyword in low for keyword in INTERESTING_KEYWORDS)


def collect_schema(payloads: List[Tuple[Path, Any]]) -> Dict[str, Any]:
    path_counter: Counter[str] = Counter()
    type_counter: Dict[str, Counter[str]] = defaultdict(Counter)
    samples: Dict[str, List[Any]] = defaultdict(list)
    files_seen: Dict[str, Set[str]] = defaultdict(set)

    top_level_types = Counter()

    for file_path, payload in payloads:
        top_level_types[type_name(payload)] += 1

        for path, value in walk(payload):
            path_counter[path] += 1
            type_counter[path][type_name(value)] += 1
            files_seen[path].add(file_path.name)

            if len(samples[path]) < 5:
                sample = short_sample(value)
                if sample not in samples[path]:
                    samples[path].append(sample)

    all_paths = sorted(path_counter.keys())

    used_like = []
    interesting_unused = []
    all_interesting = []

    known_used_lower = {x.lower() for x in KNOWN_USED_FIELDS}

    for path in all_paths:
        bkey = base_key(path)
        record = {
            "path": path,
            "base_key": bkey,
            "count": path_counter[path],
            "types": dict(type_counter[path]),
            "files_seen": sorted(files_seen[path]),
            "samples": samples[path],
        }

        if bkey in known_used_lower or path.lower() in known_used_lower:
            used_like.append(record)

        if is_interesting(path):
            all_interesting.append(record)
            if bkey not in known_used_lower and path.lower() not in known_used_lower:
                interesting_unused.append(record)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": [str(p) for p, _ in payloads],
        "file_count": len(payloads),
        "top_level_types": dict(top_level_types),
        "total_unique_paths": len(all_paths),
        "all_paths": [
            {
                "path": path,
                "count": path_counter[path],
                "types": dict(type_counter[path]),
                "samples": samples[path],
            }
            for path in all_paths
        ],
        "used_like_paths": used_like,
        "interesting_paths": all_interesting,
        "interesting_unused_paths": interesting_unused,
        "recommendation_groups": build_recommendation_groups(interesting_unused),
    }


def build_recommendation_groups(records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {
        "surface_context": [],
        "player_strength": [],
        "player_form": [],
        "h2h_context": [],
        "market_depth_and_movement": [],
        "match_format_and_status": [],
        "score_result_validation": [],
        "other_interesting": [],
    }

    for record in records:
        path = record["path"]
        low = path.lower()

        if any(x in low for x in ["surface", "court", "indoor", "outdoor", "venue"]):
            groups["surface_context"].append(path)
        elif any(x in low for x in ["rank", "ranking", "seed", "elo", "rating"]):
            groups["player_strength"].append(path)
        elif any(x in low for x in ["form", "last", "streak", "games", "tiebreak", "tie_break"]):
            groups["player_form"].append(path)
        elif any(x in low for x in ["h2h", "head"]):
            groups["h2h_context"].append(path)
        elif any(x in low for x in ["odds", "price", "bookmaker", "opening", "closing", "movement", "market"]):
            groups["market_depth_and_movement"].append(path)
        elif any(x in low for x in ["round", "best_of", "status", "retired", "walkover", "withdraw"]):
            groups["match_format_and_status"].append(path)
        elif any(x in low for x in ["score", "sets"]):
            groups["score_result_validation"].append(path)
        else:
            groups["other_interesting"].append(path)

    return {key: sorted(set(values)) for key, values in groups.items() if values}


def write_outputs(schema: Dict[str, Any], json_out: Path, txt_out: Path) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    txt_out.parent.mkdir(parents=True, exist_ok=True)

    with json_out.open("w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    lines: List[str] = []
    lines.append("AI77 TENNIS API SCHEMA AUDIT")
    lines.append("=" * 40)
    lines.append(f"Generated: {schema['generated_at']}")
    lines.append(f"Files scanned: {schema['file_count']}")
    lines.append(f"Unique paths: {schema['total_unique_paths']}")
    lines.append("")

    lines.append("FILES")
    lines.append("-----")
    for file_name in schema["files_scanned"]:
        lines.append(f"- {file_name}")
    lines.append("")

    lines.append("RECOMMENDATION GROUPS")
    lines.append("---------------------")
    for group, paths in schema["recommendation_groups"].items():
        lines.append(f"\n{group}:")
        for path in paths[:80]:
            lines.append(f"  - {path}")
        if len(paths) > 80:
            lines.append(f"  ... +{len(paths) - 80} more")
    lines.append("")

    lines.append("USED-LIKE PATHS")
    lines.append("---------------")
    for rec in schema["used_like_paths"][:200]:
        lines.append(
            f"- {rec['path']} | types={rec['types']} | sample={rec['samples'][:2]}"
        )
    lines.append("")

    lines.append("INTERESTING UNUSED PATHS")
    lines.append("------------------------")
    for rec in schema["interesting_unused_paths"][:300]:
        lines.append(
            f"- {rec['path']} | types={rec['types']} | sample={rec['samples'][:2]}"
        )

    txt_out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--txt-out", type=Path, default=DEFAULT_TXT_OUT)
    args = parser.parse_args()

    payloads = load_json_files(args.input)

    if not payloads:
        raise RuntimeError(
            f"No JSON files found in {args.input}. "
            "First save raw API responses into data/debug_api/."
        )

    schema = collect_schema(payloads)
    write_outputs(schema, args.json_out, args.txt_out)

    print("API schema audit complete.")
    print(f"Files scanned: {schema['file_count']}")
    print(f"Unique paths: {schema['total_unique_paths']}")
    print(f"JSON output: {args.json_out}")
    print(f"TXT output: {args.txt_out}")


if __name__ == "__main__":
    main()

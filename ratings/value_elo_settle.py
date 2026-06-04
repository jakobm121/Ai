import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

# Inputs
ELO_PREDICTIONS_FILE = "data/tennis_value_elo_predictions.json"
VALUE_RESULTS_FILE = "data/tennis_results.json"
ELO_RESULTS_FILE = "data/tennis_value_elo_results.json"

# Outputs
OUTPUT_PREDICTIONS_TABLE_FILE = "ratings/value_elo_predictions_table.md"
OUTPUT_RESULTS_TABLE_FILE = "ratings/value_elo_results_table.md"
OUTPUT_REPORT_FILE = "ratings/value_elo_results_report.json"
OUTPUT_MISSING_FILE = "ratings/value_elo_settle_missing.json"


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rows_from_payload(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ["picks", "predictions", "results", "data"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value

    return []


def normalize(value):
    return str(value or "").strip().lower()


def normalize_result(value):
    return normalize(value)


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def is_settled(row):
    return normalize_result(row.get("result")) in {"win", "loss", "void", "push"}


def make_pick_key(row):
    existing = (
        row.get("pick_id")
        or row.get("id")
        or row.get("prediction_id")
        or row.get("match_id")
    )

    if existing:
        return str(existing)

    date = row.get("date") or ""
    match = row.get("match") or ""
    bet = row.get("bet") or row.get("player_name") or row.get("pick") or row.get("selection") or ""
    opponent = row.get("opponent_name") or row.get("opponent") or ""

    return "|".join([
        str(date).strip(),
        str(match).strip(),
        str(bet).strip(),
        str(opponent).strip(),
    ]).lower()


def compact_match_key(row):
    date = row.get("date") or ""
    match = row.get("match") or ""
    bet = row.get("bet") or row.get("player_name") or row.get("pick") or row.get("selection") or ""
    opponent = row.get("opponent_name") or row.get("opponent") or ""

    return "|".join([
        str(date).strip().lower(),
        str(match).strip().lower(),
        str(bet).strip().lower(),
        str(opponent).strip().lower(),
    ])


def build_value_results_maps(value_result_rows):
    by_pick_key = {}
    by_compact_key = {}

    for row in value_result_rows:
        if not isinstance(row, dict):
            continue

        if not is_settled(row):
            continue

        by_pick_key[make_pick_key(row)] = row
        by_compact_key[compact_match_key(row)] = row

    return by_pick_key, by_compact_key


def make_elo_result_row(prediction_row, settled_row, match_method):
    elo_filter = {
        "confirmed": True,
        "matched": True,
        "agrees_with_pick": True,
        "overall_elo_diff": prediction_row.get("elo_overall_diff"),
        "surface_elo_diff": prediction_row.get("elo_surface_diff"),
        "player_matched_name": prediction_row.get("elo_player_matched_name"),
        "opponent_matched_name": prediction_row.get("elo_opponent_matched_name"),
        "player_match_method": prediction_row.get("elo_player_match_method"),
        "opponent_match_method": prediction_row.get("elo_opponent_match_method"),
    }

    out = {
        **settled_row,
        "pick_id": make_pick_key(prediction_row),
        "elo_filter": elo_filter,
        "elo_settle": {
            "settled_at": now_iso(),
            "settle_match_method": match_method,
            "source_predictions_file": ELO_PREDICTIONS_FILE,
            "source_results_file": VALUE_RESULTS_FILE,
        },
    }

    # Če settled row nima česa, vzemi iz ELO predictiona.
    fallback_keys = [
        "date",
        "tour_level",
        "event_type",
        "match",
        "bet",
        "opponent",
        "odds",
        "stake",
        "edge",
        "value_score",
    ]

    for key in fallback_keys:
        if out.get(key) in [None, ""]:
            out[key] = prediction_row.get(key)

    return out


def merge_by_pick_id(existing_rows, new_rows):
    merged = {}

    for row in existing_rows:
        if isinstance(row, dict):
            merged[make_pick_key(row)] = row

    added = 0
    updated = 0

    for row in new_rows:
        if not isinstance(row, dict):
            continue

        key = make_pick_key(row)

        if key in merged:
            updated += 1
        else:
            added += 1

        merged[key] = row

    return list(merged.values()), added, updated


def calc_stats(rows):
    stats = {
        "rows": 0,
        "win_loss_rows": 0,
        "wins": 0,
        "losses": 0,
        "void_push": 0,
        "profit": 0.0,
        "stake": 0.0,
        "avg_odds": 0.0,
        "roi": 0.0,
        "win_rate": 0.0,
    }

    odds_sum = 0.0
    odds_count = 0

    for row in rows:
        if not isinstance(row, dict):
            continue

        stats["rows"] += 1

        result = normalize_result(row.get("result"))
        odds = safe_float(row.get("odds"), 0.0)

        if odds:
            odds_sum += odds
            odds_count += 1

        if result in {"void", "push"}:
            stats["void_push"] += 1

        if result in {"win", "loss"}:
            stats["win_loss_rows"] += 1

            profit = safe_float(row.get("profit"), 0.0)
            stake = safe_float(row.get("stake"), 1.0)

            stats["profit"] += profit
            stats["stake"] += stake

            if result == "win":
                stats["wins"] += 1
            else:
                stats["losses"] += 1

    if stats["win_loss_rows"]:
        stats["win_rate"] = round(stats["wins"] / stats["win_loss_rows"] * 100, 2)

    if stats["stake"]:
        stats["roi"] = round(stats["profit"] / stats["stake"] * 100, 2)

    if odds_count:
        stats["avg_odds"] = round(odds_sum / odds_count, 3)

    stats["profit"] = round(stats["profit"], 3)
    stats["stake"] = round(stats["stake"], 3)

    return stats


def bucket_stats(rows, key_func):
    buckets = {}

    for row in rows:
        key = key_func(row)
        buckets.setdefault(key, []).append(row)

    return {
        key: calc_stats(value)
        for key, value in sorted(buckets.items(), key=lambda x: str(x[0]))
    }


def settle_elo_predictions():
    predictions_payload = load_json(ELO_PREDICTIONS_FILE, [])
    prediction_rows = rows_from_payload(predictions_payload)

    value_results_payload = load_json(VALUE_RESULTS_FILE, [])
    value_result_rows = rows_from_payload(value_results_payload)

    existing_elo_results_payload = load_json(ELO_RESULTS_FILE, [])
    existing_elo_result_rows = rows_from_payload(existing_elo_results_payload)

    value_by_pick_key, value_by_compact_key = build_value_results_maps(value_result_rows)

    remaining_predictions = []
    settled_now = []
    missing = []

    for pred in prediction_rows:
        if not isinstance(pred, dict):
            continue

        pred_pick_key = make_pick_key(pred)
        pred_compact_key = compact_match_key(pred)

        settled_row = value_by_pick_key.get(pred_pick_key)
        match_method = "pick_key"

        if not settled_row:
            settled_row = value_by_compact_key.get(pred_compact_key)
            match_method = "compact_key"

        if settled_row and is_settled(settled_row):
            settled_now.append(
                make_elo_result_row(pred, settled_row, match_method)
            )
        else:
            remaining_predictions.append(pred)
            missing.append({
                "reason": "not_settled_in_value_results",
                "pick_id": pred_pick_key,
                "date": pred.get("date"),
                "match": pred.get("match"),
                "bet": pred.get("bet"),
                "opponent": pred.get("opponent"),
            })

    merged_results, added, updated = merge_by_pick_id(
        existing_elo_result_rows,
        settled_now,
    )

    predictions_output = {
        "generated_at": now_iso(),
        "source_file": (
            predictions_payload.get("source_file")
            if isinstance(predictions_payload, dict)
            else "data/tennis_predictions.json"
        ),
        "settle_source_file": VALUE_RESULTS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "settled_removed": len(settled_now),
        "total_saved_predictions": len(remaining_predictions),
        "picks": remaining_predictions,
    }

    results_output = {
        "generated_at": now_iso(),
        "source_predictions_file": ELO_PREDICTIONS_FILE,
        "source_results_file": VALUE_RESULTS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "settled_in_current_run": len(settled_now),
        "added": added,
        "updated": updated,
        "confirmed_settled_results": len(merged_results),
        "results": merged_results,
    }

    save_json(ELO_PREDICTIONS_FILE, predictions_output)
    save_json(ELO_RESULTS_FILE, results_output)

    return {
        "prediction_source_rows": len(prediction_rows),
        "value_result_source_rows": len(value_result_rows),
        "settled_now": len(settled_now),
        "remaining_predictions": len(remaining_predictions),
        "added": added,
        "updated": updated,
        "saved_total_results": len(merged_results),
        "missing": missing,
        "remaining_prediction_rows": remaining_predictions,
        "result_rows": merged_results,
        "settled_now_rows": settled_now,
    }


def build_predictions_table(predictions_rows):
    lines = []

    lines.append("# Value + ELO predictions")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append("## Open / saved ELO-confirmed value picks")
    lines.append("")
    lines.append("| Date | Tour | Match | Pick | Odds | Stake | Edge | ELO overall diff | ELO surface diff |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")

    for row in predictions_rows:
        lines.append(
            f"| {row.get('date') or ''} "
            f"| {row.get('tour_level') or ''} "
            f"| {row.get('match') or ''} "
            f"| {row.get('bet') or ''} "
            f"| {row.get('odds') or ''} "
            f"| {row.get('stake') or ''} "
            f"| {row.get('edge') or ''} "
            f"| {row.get('elo_overall_diff') or ''} "
            f"| {row.get('elo_surface_diff') or ''} |"
        )

    if not predictions_rows:
        lines.append("| - | - | - | No open ELO-confirmed picks | - | - | - | - | - |")

    return "\n".join(lines)


def build_results_table(result_rows):
    stats = calc_stats(result_rows)

    lines = []

    lines.append("# Value + ELO settled results")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append(
        f"Overall: **{stats['wins']}-{stats['losses']}**, "
        f"WR **{stats['win_rate']}%**, "
        f"Profit **{stats['profit']}u**, "
        f"ROI **{stats['roi']}%**, "
        f"Avg odds **{stats['avg_odds']}**"
    )
    lines.append("")
    lines.append("| Date | Tour | Match | Pick | Odds | Stake | Result | Profit | ELO overall diff | ELO surface diff |")
    lines.append("|---|---|---|---|---:|---:|---|---:|---:|---:|")

    for row in result_rows:
        elo = row.get("elo_filter", {})

        lines.append(
            f"| {row.get('date') or ''} "
            f"| {row.get('tour_level') or ''} "
            f"| {row.get('match') or ''} "
            f"| {row.get('bet') or row.get('player_name') or ''} "
            f"| {row.get('odds') or ''} "
            f"| {row.get('stake') or ''} "
            f"| {row.get('result') or ''} "
            f"| {row.get('profit') or ''} "
            f"| {elo.get('overall_elo_diff') or ''} "
            f"| {elo.get('surface_elo_diff') or ''} |"
        )

    return "\n".join(lines)


def build_report(info):
    rows = info["result_rows"]

    return {
        "generated_at": now_iso(),
        "source_files": {
            "elo_predictions": ELO_PREDICTIONS_FILE,
            "value_results": VALUE_RESULTS_FILE,
            "elo_results": ELO_RESULTS_FILE,
            "elo": "ratings/tennis_elo.json",
        },
        "settle": {
            "prediction_source_rows": info["prediction_source_rows"],
            "value_result_source_rows": info["value_result_source_rows"],
            "settled_now": info["settled_now"],
            "remaining_predictions": info["remaining_predictions"],
            "added": info["added"],
            "updated": info["updated"],
            "saved_total_results": info["saved_total_results"],
            "missing_unsettled": len(info["missing"]),
        },
        "results": {
            "overall": calc_stats(rows),
            "by_tour": bucket_stats(rows, lambda r: r.get("tour_level") or "unknown"),
            "by_event_type": bucket_stats(rows, lambda r: r.get("event_type") or "unknown"),
        },
    }


def main():
    info = settle_elo_predictions()
    report = build_report(info)

    missing = {
        "generated_at": now_iso(),
        "missing": info["missing"],
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_MISSING_FILE, missing)
    save_text(
        OUTPUT_PREDICTIONS_TABLE_FILE,
        build_predictions_table(info["remaining_prediction_rows"]),
    )
    save_text(
        OUTPUT_RESULTS_TABLE_FILE,
        build_results_table(info["result_rows"]),
    )

    print("")
    print("VALUE + ELO SETTLE DONE")
    print(f"ELO predictions:          {ELO_PREDICTIONS_FILE}")
    print(f"Value results source:     {VALUE_RESULTS_FILE}")
    print(f"ELO results:              {ELO_RESULTS_FILE}")
    print(f"Predictions table:        {OUTPUT_PREDICTIONS_TABLE_FILE}")
    print(f"Results table:            {OUTPUT_RESULTS_TABLE_FILE}")
    print(f"Report:                   {OUTPUT_REPORT_FILE}")
    print(f"Missing:                  {OUTPUT_MISSING_FILE}")
    print("")
    print("Settle:")
    print({
        "prediction_source_rows": info["prediction_source_rows"],
        "settled_now": info["settled_now"],
        "remaining_predictions": info["remaining_predictions"],
        "added": info["added"],
        "updated": info["updated"],
        "saved_total_results": info["saved_total_results"],
        "missing_unsettled": len(info["missing"]),
    })
    print("")
    print("Results overall:")
    print(report["results"]["overall"])
    print("")


if __name__ == "__main__":
    main()

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


# Run from repo root.
sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"

# Input: value machine predictions / results
VALUE_PREDICTIONS_FILE = "data/tennis_predictions.json"
VALUE_RESULTS_FILE = "data/tennis_results.json"

# Output: only ELO-confirmed value picks
ELO_PREDICTIONS_FILE = "data/tennis_value_elo_predictions.json"
ELO_RESULTS_FILE = "data/tennis_value_elo_results.json"

OUTPUT_TABLE_FILE = "ratings/value_elo_predictions_table.md"
OUTPUT_REPORT_FILE = "ratings/value_elo_results_report.json"
OUTPUT_MISSING_FILE = "ratings/value_elo_missing.json"


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


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def infer_tour(row):
    tour_level = normalize(row.get("tour_level"))
    gender = normalize(row.get("gender"))
    event_type = normalize(row.get("event_type"))

    if tour_level == "atp":
        return "atp"

    if tour_level == "wta":
        return "wta"

    if gender == "men":
        return "atp"

    if gender == "women":
        return "wta"

    if "men" in event_type and "women" not in event_type:
        return "atp"

    if "women" in event_type or "wta" in event_type:
        return "wta"

    if "atp" in event_type:
        return "atp"

    return None


def infer_surface(row):
    return row.get("surface") or row.get("court_surface") or None


def normalize_result(value):
    return normalize(value)


def is_settled(row):
    return normalize_result(row.get("result")) in {"win", "loss", "void", "push"}


def is_win_loss(row):
    return normalize_result(row.get("result")) in {"win", "loss"}


def make_pick_key(row):
    """
    Stabilen ID, da ne podvajamo pickov, tudi če workflow večkrat zaženeš.
    """
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
    bet = row.get("bet") or row.get("player_name") or ""
    opponent = row.get("opponent_name") or ""

    return "|".join([
        str(date).strip(),
        str(match).strip(),
        str(bet).strip(),
        str(opponent).strip(),
    ]).lower()


def get_player_and_opponent(row):
    player = (
        row.get("player_name")
        or row.get("bet")
        or row.get("pick")
        or row.get("selection")
    )

    opponent = row.get("opponent_name")

    return player, opponent


def compact_prediction_row(row, signal):
    """
    Pregleden prediction JSON brez preveč informacij.
    """
    return {
        "pick_id": make_pick_key(row),
        "created_at": row.get("created_at") or row.get("generated_at"),
        "date": row.get("date"),
        "tour_level": row.get("tour_level"),
        "event_type": row.get("event_type"),
        "match": row.get("match"),
        "bet": row.get("bet") or row.get("player_name"),
        "opponent": row.get("opponent_name"),
        "odds": row.get("odds"),
        "stake": row.get("stake"),
        "model_probability": row.get("model_probability") or row.get("probability"),
        "edge": row.get("edge"),
        "value_score": row.get("value_score"),
        "elo_confirmed": True,
        "elo_overall_diff": signal.get("overall_elo_diff"),
        "elo_surface_diff": signal.get("surface_elo_diff"),
    }


def rich_result_row(row, signal):
    """
    Results ima lahko več informacij, da lahko kasneje delamo statistiko.
    """
    return {
        **row,
        "pick_id": make_pick_key(row),
        "elo_filter": {
            "confirmed": True,
            "matched": signal.get("matched"),
            "agrees_with_pick": signal.get("agrees_with_pick"),
            "overall_elo_diff": signal.get("overall_elo_diff"),
            "surface_elo_diff": signal.get("surface_elo_diff"),
            "player_matched_name": signal.get("player", {}).get("matched_name"),
            "opponent_matched_name": signal.get("opponent", {}).get("matched_name"),
            "player_match_method": signal.get("player", {}).get("match_method"),
            "opponent_match_method": signal.get("opponent", {}).get("match_method"),
        },
    }


def elo_confirms_value_pick(row):
    player, opponent = get_player_and_opponent(row)

    if not player or not opponent:
        return False, None, {
            "reason": "missing_player_or_opponent",
            "row": row,
        }

    tour = infer_tour(row)
    surface = infer_surface(row)

    signal = get_elo_signal(
        player,
        opponent,
        surface=surface,
        tour=tour,
    )

    if not signal.get("matched"):
        return False, signal, {
            "reason": "elo_unmatched",
            "date": row.get("date"),
            "match": row.get("match"),
            "player": player,
            "opponent": opponent,
            "tour": tour,
            "surface": surface,
            "player_matched": signal.get("player", {}).get("matched"),
            "opponent_matched": signal.get("opponent", {}).get("matched"),
            "player_method": signal.get("player", {}).get("match_method"),
            "opponent_method": signal.get("opponent", {}).get("match_method"),
        }

    if signal.get("agrees_with_pick") is not True:
        return False, signal, None

    return True, signal, None


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


def filter_predictions():
    payload = load_json(VALUE_PREDICTIONS_FILE, [])
    rows = rows_from_payload(payload)

    existing_payload = load_json(ELO_PREDICTIONS_FILE, [])
    existing_rows = rows_from_payload(existing_payload)

    confirmed = []
    missing = []
    rejected = 0
    unmatched = 0

    for row in rows:
        if not isinstance(row, dict):
            continue

        ok, signal, missing_item = elo_confirms_value_pick(row)

        if ok:
            confirmed.append(compact_prediction_row(row, signal))
        else:
            rejected += 1

            if missing_item:
                unmatched += 1
                missing.append(missing_item)

    merged, added, updated = merge_by_pick_id(existing_rows, confirmed)

    output = {
        "generated_at": now_iso(),
        "source_file": VALUE_PREDICTIONS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "total_source_predictions": len(rows),
        "confirmed_in_current_run": len(confirmed),
        "added": added,
        "updated": updated,
        "total_saved_predictions": len(merged),
        "picks": merged,
    }

    save_json(ELO_PREDICTIONS_FILE, output)

    return {
        "source_rows": len(rows),
        "confirmed": len(confirmed),
        "rejected": rejected,
        "unmatched": unmatched,
        "added": added,
        "updated": updated,
        "saved_total": len(merged),
        "missing": missing,
        "rows": merged,
    }


def filter_results():
    payload = load_json(VALUE_RESULTS_FILE, [])
    rows = rows_from_payload(payload)

    existing_payload = load_json(ELO_RESULTS_FILE, [])
    existing_rows = rows_from_payload(existing_payload)

    confirmed_results = []
    missing = []
    rejected = 0
    unmatched = 0

    for row in rows:
        if not isinstance(row, dict):
            continue

        if not is_settled(row):
            continue

        ok, signal, missing_item = elo_confirms_value_pick(row)

        if ok:
            confirmed_results.append(rich_result_row(row, signal))
        else:
            rejected += 1

            if missing_item:
                unmatched += 1
                missing.append(missing_item)

    merged, added, updated = merge_by_pick_id(existing_rows, confirmed_results)

    output = {
        "generated_at": now_iso(),
        "source_file": VALUE_RESULTS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "confirmed_settled_results": len(merged),
        "results": merged,
    }

    save_json(ELO_RESULTS_FILE, output)

    return {
        "source_rows": len(rows),
        "confirmed": len(confirmed_results),
        "rejected": rejected,
        "unmatched": unmatched,
        "added": added,
        "updated": updated,
        "saved_total": len(merged),
        "missing": missing,
        "rows": merged,
    }


def calc_stats(rows):
    stats = {
        "rows": 0,
        "win_loss_rows": 0,
        "wins": 0,
        "losses": 0,
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


def build_report(prediction_info, result_info):
    rows = result_info["rows"]

    report = {
        "generated_at": now_iso(),
        "source_files": {
            "value_predictions": VALUE_PREDICTIONS_FILE,
            "value_results": VALUE_RESULTS_FILE,
            "elo_predictions": ELO_PREDICTIONS_FILE,
            "elo_results": ELO_RESULTS_FILE,
            "elo": "ratings/tennis_elo.json",
        },
        "predictions": {
            "source_rows": prediction_info["source_rows"],
            "confirmed_current_run": prediction_info["confirmed"],
            "added": prediction_info["added"],
            "updated": prediction_info["updated"],
            "saved_total": prediction_info["saved_total"],
            "unmatched": prediction_info["unmatched"],
        },
        "results": {
            "source_rows": result_info["source_rows"],
            "confirmed_current_run": result_info["confirmed"],
            "added": result_info["added"],
            "updated": result_info["updated"],
            "saved_total": result_info["saved_total"],
            "unmatched": result_info["unmatched"],
            "overall": calc_stats(rows),
            "by_tour": bucket_stats(rows, lambda r: r.get("tour_level") or "unknown"),
            "by_event_type": bucket_stats(rows, lambda r: r.get("event_type") or "unknown"),
        },
    }

    return report


def build_predictions_table(predictions_rows, result_rows):
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

    stats = calc_stats(result_rows)

    lines.append("")
    lines.append("## Settled ELO-confirmed value picks")
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


def main():
    prediction_info = filter_predictions()
    result_info = filter_results()

    report = build_report(prediction_info, result_info)

    missing = {
        "generated_at": now_iso(),
        "prediction_missing": prediction_info["missing"],
        "result_missing": result_info["missing"],
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_MISSING_FILE, missing)
    save_text(
        OUTPUT_TABLE_FILE,
        build_predictions_table(prediction_info["rows"], result_info["rows"]),
    )

    print("")
    print("VALUE + ELO FILTER DONE")
    print(f"Value predictions source: {VALUE_PREDICTIONS_FILE}")
    print(f"Value results source:     {VALUE_RESULTS_FILE}")
    print("")
    print(f"ELO predictions:          {ELO_PREDICTIONS_FILE}")
    print(f"ELO results:              {ELO_RESULTS_FILE}")
    print(f"Report:                   {OUTPUT_REPORT_FILE}")
    print(f"Table:                    {OUTPUT_TABLE_FILE}")
    print(f"Missing:                  {OUTPUT_MISSING_FILE}")
    print("")
    print("Predictions:")
    print({
        "source_rows": prediction_info["source_rows"],
        "confirmed": prediction_info["confirmed"],
        "added": prediction_info["added"],
        "updated": prediction_info["updated"],
        "saved_total": prediction_info["saved_total"],
        "unmatched": prediction_info["unmatched"],
    })
    print("")
    print("Results:")
    print(report["results"]["overall"])
    print("")


if __name__ == "__main__":
    main()

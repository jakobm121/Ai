import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


# Run from repo root.
sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"

# Input: value machine predictions only
VALUE_PREDICTIONS_FILE = "data/tennis_predictions.json"

# Output: only open ELO-confirmed value picks
ELO_PREDICTIONS_FILE = "data/tennis_value_elo_predictions.json"

OUTPUT_TABLE_FILE = "ratings/value_elo_predictions_table.md"
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
    opponent = row.get("opponent_name") or row.get("opponent") or ""

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

    opponent = row.get("opponent_name") or row.get("opponent")

    return player, opponent


def compact_prediction_row(row, signal):
    """
    Pregleden prediction JSON brez preveč informacij.
    To je active/open ELO pick.
    """
    return {
        "pick_id": make_pick_key(row),
        "created_at": row.get("created_at") or row.get("generated_at"),
        "date": row.get("date"),
        "tour_level": row.get("tour_level"),
        "event_type": row.get("event_type"),
        "match": row.get("match"),
        "bet": row.get("bet") or row.get("player_name"),
        "opponent": row.get("opponent_name") or row.get("opponent"),
        "odds": row.get("odds"),
        "stake": row.get("stake"),
        "model_probability": row.get("model_probability") or row.get("probability"),
        "edge": row.get("edge"),
        "value_score": row.get("value_score"),
        "elo_confirmed": True,
        "elo_overall_diff": signal.get("overall_elo_diff"),
        "elo_surface_diff": signal.get("surface_elo_diff"),
        "elo_player_matched_name": signal.get("player", {}).get("matched_name"),
        "elo_opponent_matched_name": signal.get("opponent", {}).get("matched_name"),
        "elo_player_match_method": signal.get("player", {}).get("match_method"),
        "elo_opponent_match_method": signal.get("opponent", {}).get("match_method"),
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


def main():
    prediction_info = filter_predictions()

    missing = {
        "generated_at": now_iso(),
        "prediction_missing": prediction_info["missing"],
    }

    save_json(OUTPUT_MISSING_FILE, missing)
    save_text(
        OUTPUT_TABLE_FILE,
        build_predictions_table(prediction_info["rows"]),
    )

    print("")
    print("VALUE + ELO FILTER DONE")
    print(f"Value predictions source: {VALUE_PREDICTIONS_FILE}")
    print("")
    print(f"ELO predictions:          {ELO_PREDICTIONS_FILE}")
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


if __name__ == "__main__":
    main()

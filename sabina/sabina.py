import csv
import json
import os
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

INPUT_FILE = "data/tennis_predictions.json"

SABINA_DIR = "sabina"
RESULTS_DIR = os.path.join(SABINA_DIR, "results")

OUTPUT_JSON = os.path.join(RESULTS_DIR, "sabina_predictions.json")
OUTPUT_CSV = os.path.join(RESULTS_DIR, "sabina_today.csv")
SABINA_HISTORY_FILE = os.path.join(RESULTS_DIR, "sabina_history.json")


# =========================
# SABINA FORMULA
# =========================

MIN_BEST_TO_MEDIAN_GAP = 0.06
MAX_OPPONENT_L5_GAME_DIFF = 1.5
MAX_ODDS = 2.60


def ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return default


def save_json(path, data):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def pick_identity(pick):
    fixture_id = pick.get("fixture_id") or pick.get("event_key") or ""
    side = pick.get("side") or pick.get("market_side") or ""
    player_key = pick.get("player_key") or pick.get("bet") or ""

    raw = f"sabina|{fixture_id}|{side}|{player_key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def read_picks_from_predictions(payload):
    """
    tennis_predictions.py saves:
    {
      "generated_at": "...",
      "picks": [...]
    }

    This also supports a raw list, just in case.
    """
    if isinstance(payload, dict):
        picks = payload.get("picks") or []
        meta = {
            "source_generated_at": payload.get("generated_at"),
            "source_model": payload.get("model"),
            "source_file": INPUT_FILE,
        }
        return picks, meta

    if isinstance(payload, list):
        return payload, {
            "source_generated_at": None,
            "source_model": None,
            "source_file": INPUT_FILE,
        }

    return [], {
        "source_generated_at": None,
        "source_model": None,
        "source_file": INPUT_FILE,
    }


def opponent_l5_game_diff(pick):
    return safe_float(
        (((pick.get("opponent_form") or {}).get("last_5") or {}).get("game_diff_avg")),
        default=999.0,
    )


def player_fatigue_7d(pick):
    return safe_int(
        (((pick.get("player_form") or {}).get("last_5") or {}).get("fatigue_matches_7d")),
        default=0,
    )


def is_sabina_play(pick):
    gap = safe_float(pick.get("best_to_median_gap"), 0.0)
    opp_gd = opponent_l5_game_diff(pick)
    odds = safe_float(pick.get("odds"), 999.0)

    if gap < MIN_BEST_TO_MEDIAN_GAP:
        return False

    if opp_gd > MAX_OPPONENT_L5_GAME_DIFF:
        return False

    if odds > MAX_ODDS:
        return False

    return True


def sabina_stake(pick):
    """
    No external config.
    Built-in stake logic.
    """
    stake = 0.75

    opp_gd = opponent_l5_game_diff(pick)
    fatigue_7d = player_fatigue_7d(pick)
    tour_level = str(pick.get("tour_level") or "").lower()

    if opp_gd <= 0.5:
        stake += 0.25

    if fatigue_7d >= 1:
        stake += 0.25

    if tour_level == "wta":
        stake -= 0.25

    stake = max(0.50, min(1.25, stake))
    return round(stake, 2)


def sabina_reason(pick):
    return (
        "Sabina PLAY: "
        f"best_to_median_gap={pick.get('best_to_median_gap')}, "
        f"opponent_l5_game_diff={opponent_l5_game_diff(pick)}, "
        f"odds={pick.get('odds')}. "
        "Formula: gap >= 0.06, opponent L5 game diff <= 1.5, odds <= 2.60."
    )


def enrich_pick(pick):
    out = dict(pick)

    out["sabina_pick_id"] = pick_identity(pick)
    out["sabina_model"] = "sabina_filter_v1"
    out["sabina_result"] = "pending"
    out["sabina_stake"] = sabina_stake(pick)
    out["sabina_reason"] = sabina_reason(pick)
    out["sabina_created_at"] = datetime.now(ZoneInfo(TZ_NAME)).isoformat()

    return out


def dedupe_picks(picks):
    """
    One Sabina pick per fixture.
    If duplicates exist, keep the better one by quality/confidence/edge/gap.
    """
    best = {}

    for pick in picks:
        fixture_id = str(pick.get("fixture_id") or pick.get("event_key") or pick_identity(pick))

        current = best.get(fixture_id)
        if current is None:
            best[fixture_id] = pick
            continue

        pick_rank = (
            safe_float(pick.get("quality_score"), 0.0),
            safe_float(pick.get("confidence"), 0.0),
            safe_float(pick.get("edge"), 0.0),
            safe_float(pick.get("best_to_median_gap"), 0.0),
        )

        current_rank = (
            safe_float(current.get("quality_score"), 0.0),
            safe_float(current.get("confidence"), 0.0),
            safe_float(current.get("edge"), 0.0),
            safe_float(current.get("best_to_median_gap"), 0.0),
        )

        if pick_rank > current_rank:
            best[fixture_id] = pick

    return list(best.values())


def write_csv(path, picks):
    ensure_dirs()

    fields = [
        "date",
        "time",
        "match",
        "bet",
        "odds",
        "best_bookmaker",
        "market_median_odds",
        "best_to_median_gap",
        "edge",
        "model_prob",
        "implied_prob",
        "confidence",
        "quality_score",
        "tour_level",
        "event_type",
        "favorite_type",
        "sabina_stake",
        "sabina_reason",
        "event_key",
        "fixture_id",
        "pick_id",
        "sabina_pick_id",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for pick in picks:
            writer.writerow({field: pick.get(field, "") for field in fields})


def append_sabina_history(picks):
    """
    Sabina keeps its own history in sabina/results/sabina_history.json.
    It does not overwrite settled Sabina records later.
    """
    history = load_json(SABINA_HISTORY_FILE, [])

    if not isinstance(history, list):
        history = []

    index = {}
    for i, item in enumerate(history):
        if isinstance(item, dict):
            key = item.get("sabina_pick_id") or item.get("pick_id")
            if key:
                index[key] = i

    added = 0
    updated_pending = 0

    for pick in picks:
        key = pick.get("sabina_pick_id") or pick.get("pick_id")
        if not key:
            continue

        if key not in index:
            history.append(dict(pick))
            index[key] = len(history) - 1
            added += 1
            continue

        old = history[index[key]]
        old_status = str(old.get("sabina_result") or old.get("result") or "pending").lower()

        if old_status == "pending":
            keep_created_at = old.get("sabina_created_at")
            new_pick = dict(pick)
            if keep_created_at:
                new_pick["sabina_created_at"] = keep_created_at

            history[index[key]] = new_pick
            updated_pending += 1

    save_json(SABINA_HISTORY_FILE, history)
    return added, updated_pending, len(history)


def main():
    ensure_dirs()

    payload = load_json(INPUT_FILE, {})
    picks, meta = read_picks_from_predictions(payload)

    if not picks:
        raise SystemExit(
            f"No picks found. Expected tennis value model output at: {INPUT_FILE}"
        )

    deduped = dedupe_picks(picks)

    sabina_picks = []
    for pick in deduped:
        if is_sabina_play(pick):
            sabina_picks.append(enrich_pick(pick))

    sabina_picks.sort(
        key=lambda p: (
            p.get("date") or "",
            p.get("time") or "",
            -safe_float(p.get("sabina_stake"), 0.0),
            -safe_float(p.get("quality_score"), 0.0),
        )
    )

    now = datetime.now(ZoneInfo(TZ_NAME)).isoformat()

    output = {
        "generated_at": now,
        "timezone": TZ_NAME,
        "model": "Sabina Filter v1",
        "source_file": INPUT_FILE,
        "source_generated_at": meta.get("source_generated_at"),
        "source_model": meta.get("source_model"),
        "formula": {
            "min_best_to_median_gap": MIN_BEST_TO_MEDIAN_GAP,
            "max_opponent_l5_game_diff": MAX_OPPONENT_L5_GAME_DIFF,
            "max_odds": MAX_ODDS,
        },
        "summary": {
            "input_picks": len(picks),
            "deduped_picks": len(deduped),
            "sabina_picks": len(sabina_picks),
        },
        "picks": sabina_picks,
    }

    save_json(OUTPUT_JSON, output)
    write_csv(OUTPUT_CSV, sabina_picks)

    added, updated_pending, total_history = append_sabina_history(sabina_picks)

    print("")
    print("SABINA DONE")
    print(f"Input file:       {INPUT_FILE}")
    print(f"Input picks:      {len(picks)}")
    print(f"Deduped picks:    {len(deduped)}")
    print(f"Sabina picks:     {len(sabina_picks)}")
    print(f"Saved JSON:       {OUTPUT_JSON}")
    print(f"Saved CSV:        {OUTPUT_CSV}")
    print(f"History:          {SABINA_HISTORY_FILE}")
    print(f"History added:    {added}")
    print(f"History updated:  {updated_pending}")
    print(f"History total:    {total_history}")
    print("")

    for pick in sabina_picks:
        print(
            f"{pick.get('date')} {pick.get('time')} | "
            f"{pick.get('match')} | "
            f"{pick.get('bet')} @ {pick.get('odds')} | "
            f"gap={pick.get('best_to_median_gap')} | "
            f"opp_l5_gd={opponent_l5_game_diff(pick)} | "
            f"stake={pick.get('sabina_stake')}"
        )


if __name__ == "__main__":
    main()

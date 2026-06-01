import csv
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

MAIN_RESULTS_FILE = "data/tennis_results.json"

SABINA_DIR = "sabina"
RESULTS_DIR = os.path.join(SABINA_DIR, "results")

SABINA_HISTORY_FILE = os.path.join(RESULTS_DIR, "sabina_history.json")
SABINA_PREDICTIONS_FILE = os.path.join(RESULTS_DIR, "sabina_predictions.json")

SETTLED_JSON = os.path.join(RESULTS_DIR, "sabina_settled.json")
SETTLED_CSV = os.path.join(RESULTS_DIR, "sabina_settled.csv")
PENDING_CSV = os.path.join(RESULTS_DIR, "sabina_pending.csv")


def ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def now_local_iso():
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
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def normalize_status(value):
    return str(value or "").strip().lower()


def is_settled_result(value):
    return normalize_status(value) in {"win", "loss", "void", "cancelled", "retired", "walkover"}


def load_sabina_history():
    history = load_json(SABINA_HISTORY_FILE, None)

    if isinstance(history, list):
        return history

    predictions = load_json(SABINA_PREDICTIONS_FILE, {})
    if isinstance(predictions, dict) and isinstance(predictions.get("picks"), list):
        return predictions["picks"]

    return []


def load_main_results():
    data = load_json(MAIN_RESULTS_FILE, [])

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if isinstance(data.get("picks"), list):
            return data["picks"]
        if isinstance(data.get("results"), list):
            return data["results"]

    return []


def make_result_indexes(main_results):
    by_fixture = {}
    by_event = {}
    by_pick = {}

    for r in main_results:
        if not isinstance(r, dict):
            continue

        result = normalize_status(r.get("result"))
        if result not in {"win", "loss", "void"}:
            continue

        fixture_id = str(r.get("fixture_id") or "").strip()
        event_key = str(r.get("event_key") or "").strip()
        pick_id = str(r.get("pick_id") or "").strip()

        if fixture_id:
            by_fixture[fixture_id] = r
        if event_key:
            by_event[event_key] = r
        if pick_id:
            by_pick[pick_id] = r

    return by_fixture, by_event, by_pick


def find_matching_result(pick, indexes):
    by_fixture, by_event, by_pick = indexes

    pick_id = str(pick.get("pick_id") or "").strip()
    fixture_id = str(pick.get("fixture_id") or "").strip()
    event_key = str(pick.get("event_key") or "").strip()

    if pick_id and pick_id in by_pick:
        return by_pick[pick_id]

    if fixture_id and fixture_id in by_fixture:
        return by_fixture[fixture_id]

    if event_key and event_key in by_event:
        return by_event[event_key]

    return None


def settle_profit_from_main_result(pick, main_result):
    """
    Main result profit uses original stake.
    Sabina uses sabina_stake, so calculate Sabina profit separately.
    """
    result = normalize_status(main_result.get("result"))
    odds = safe_float(pick.get("odds"), 0.0)
    stake = safe_float(pick.get("sabina_stake") or pick.get("stake"), 0.0)

    if result == "win":
        return round(stake * (odds - 1.0), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def settle_history_from_main_results(history, main_results):
    indexes = make_result_indexes(main_results)

    updated = []
    newly_settled = 0
    already_settled = 0
    still_pending = 0
    missing = 0

    for pick in history:
        if not isinstance(pick, dict):
            continue

        old_status = normalize_status(pick.get("sabina_result") or pick.get("result") or "pending")

        if old_status in {"win", "loss", "void"}:
            updated.append(pick)
            already_settled += 1
            continue

        main_result = find_matching_result(pick, indexes)

        if not main_result:
            pick2 = dict(pick)
            pick2["sabina_result"] = "pending"
            updated.append(pick2)
            still_pending += 1
            missing += 1
            continue

        result = normalize_status(main_result.get("result"))

        if result not in {"win", "loss", "void"}:
            pick2 = dict(pick)
            pick2["sabina_result"] = "pending"
            updated.append(pick2)
            still_pending += 1
            continue

        pick2 = dict(pick)
        pick2["sabina_result"] = result
        pick2["sabina_profit"] = settle_profit_from_main_result(pick2, main_result)
        pick2["settled_at"] = main_result.get("settled_at") or now_local_iso()
        pick2["settled_status"] = main_result.get("settled_status", "")
        pick2["event_winner"] = main_result.get("event_winner", "")
        pick2["final_score"] = main_result.get("final_score", "")

        if "total_games" in main_result:
            pick2["total_games"] = main_result.get("total_games")

        updated.append(pick2)
        newly_settled += 1

    return updated, {
        "newly_settled": newly_settled,
        "already_settled": already_settled,
        "still_pending": still_pending,
        "missing_in_main_results": missing,
    }


def stats(history):
    settled = [
        p for p in history
        if normalize_status(p.get("sabina_result")) in {"win", "loss"}
    ]

    wins = sum(1 for p in settled if normalize_status(p.get("sabina_result")) == "win")
    losses = sum(1 for p in settled if normalize_status(p.get("sabina_result")) == "loss")
    profit = sum(safe_float(p.get("sabina_profit"), 0.0) for p in settled)
    stake = sum(safe_float(p.get("sabina_stake") or p.get("stake"), 0.0) for p in settled)

    pending = sum(
        1 for p in history
        if normalize_status(p.get("sabina_result") or "pending") == "pending"
    )

    voids = sum(
        1 for p in history
        if normalize_status(p.get("sabina_result")) == "void"
    )

    roi = profit / stake if stake else 0.0
    wr = wins / len(settled) if settled else 0.0

    return {
        "total_history": len(history),
        "settled_bets": len(settled),
        "wins": wins,
        "losses": losses,
        "voids": voids,
        "pending": pending,
        "profit": round(profit, 4),
        "stake": round(stake, 4),
        "roi": round(roi, 4),
        "win_rate": round(wr, 4),
    }


def write_csv(path, picks):
    ensure_dirs()

    fields = [
        "date",
        "time",
        "match",
        "bet",
        "odds",
        "sabina_stake",
        "sabina_result",
        "sabina_profit",
        "settled_status",
        "event_winner",
        "final_score",
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
        "event_key",
        "fixture_id",
        "pick_id",
        "sabina_pick_id",
        "sabina_created_at",
        "settled_at",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for pick in picks:
            writer.writerow({field: pick.get(field, "") for field in fields})


def main():
    ensure_dirs()

    history = load_sabina_history()
    if not history:
        raise SystemExit(
            "No Sabina history found. Expected sabina/results/sabina_history.json "
            "or sabina/results/sabina_predictions.json"
        )

    main_results = load_main_results()
    if not main_results:
        raise SystemExit(f"No main results found at {MAIN_RESULTS_FILE}")

    updated_history, settle_summary = settle_history_from_main_results(history, main_results)
    summary = stats(updated_history)

    report = {
        "generated_at": now_local_iso(),
        "timezone": TZ_NAME,
        "source_history_file": SABINA_HISTORY_FILE,
        "source_main_results_file": MAIN_RESULTS_FILE,
        "settle_summary": settle_summary,
        "summary": summary,
        "picks": updated_history,
    }

    save_json(SABINA_HISTORY_FILE, updated_history)
    save_json(SETTLED_JSON, report)

    settled_rows = [
        p for p in updated_history
        if normalize_status(p.get("sabina_result")) in {"win", "loss", "void"}
    ]

    pending_rows = [
        p for p in updated_history
        if normalize_status(p.get("sabina_result") or "pending") == "pending"
    ]

    write_csv(SETTLED_CSV, settled_rows)
    write_csv(PENDING_CSV, pending_rows)

    print("")
    print("SABINA SETTLE DONE")
    print(f"Source main results: {MAIN_RESULTS_FILE}")
    print(f"History file:        {SABINA_HISTORY_FILE}")
    print(f"Settled JSON:        {SETTLED_JSON}")
    print(f"Settled CSV:         {SETTLED_CSV}")
    print(f"Pending CSV:         {PENDING_CSV}")
    print("")
    print(f"Newly settled:       {settle_summary['newly_settled']}")
    print(f"Already settled:     {settle_summary['already_settled']}")
    print(f"Still pending:       {settle_summary['still_pending']}")
    print(f"Missing in results:  {settle_summary['missing_in_main_results']}")
    print("")
    print(f"Total history:       {summary['total_history']}")
    print(f"Settled bets:        {summary['settled_bets']}")
    print(f"Wins/Losses:         {summary['wins']} / {summary['losses']}")
    print(f"Voids:               {summary['voids']}")
    print(f"Pending:             {summary['pending']}")
    print(f"Profit:              {summary['profit']:+.2f}u")
    print(f"Stake:               {summary['stake']:.2f}u")
    print(f"ROI:                 {summary['roi'] * 100:.1f}%")
    print(f"Win rate:            {summary['win_rate'] * 100:.1f}%")
    print("")


if __name__ == "__main__":
    main()

import csv
import json
import os
import time
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# =========================
# CONFIG
# =========================

API_KEY = os.getenv("TENNIS_API_KEY") or os.getenv("API_KEY")
BASE_URL = "https://api.api-tennis.com/tennis/"
REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.35

TZ_NAME = "Europe/Ljubljana"

SABINA_DIR = "sabina"
RESULTS_DIR = os.path.join(SABINA_DIR, "results")

SABINA_HISTORY_FILE = os.path.join(RESULTS_DIR, "sabina_history.json")
SABINA_PREDICTIONS_FILE = os.path.join(RESULTS_DIR, "sabina_predictions.json")

SETTLED_JSON = os.path.join(RESULTS_DIR, "sabina_settled.json")
SETTLED_CSV = os.path.join(RESULTS_DIR, "sabina_settled.csv")
PENDING_CSV = os.path.join(RESULTS_DIR, "sabina_pending.csv")


# =========================
# BASIC HELPERS
# =========================

def ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def now_local_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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


def safe_float(value, default=0.0):
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
        text = str(value).strip()
        if "." in text:
            text = text.split(".", 1)[0]
        return int(text)
    except Exception:
        return default


def normalize_status(value):
    return str(value or "").strip().lower()


def is_already_settled(pick):
    status = normalize_status(
        pick.get("sabina_result")
        or pick.get("result")
        or "pending"
    )
    return status in {"win", "loss", "void", "cancelled", "retired", "walkover"}


def get_pick_date(pick):
    date_s = pick.get("date")
    if not date_s:
        return None

    try:
        return datetime.strptime(date_s, "%Y-%m-%d").date()
    except Exception:
        return None


def final_score_from_match(match):
    """
    API-Tennis usually gives either event_final_result or scores.
    We support both.
    """
    direct = match.get("event_final_result") or match.get("event_result")
    if direct:
        return str(direct)

    scores = match.get("scores") or []
    parts = []

    if isinstance(scores, list):
        for s in scores:
            a = s.get("score_first")
            b = s.get("score_second")
            if a is None or b is None:
                continue
            parts.append(f"{a}-{b}")

    return ", ".join(parts)


# =========================
# API
# =========================

def api_call(params, retries=3):
    if not API_KEY:
        raise RuntimeError("Missing TENNIS_API_KEY or API_KEY secret/env variable.")

    params = params.copy()
    params["APIkey"] = API_KEY

    for attempt in range(retries):
        try:
            res = requests.get(
                BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if res.status_code in {429, 500, 502, 503, 504}:
                wait = 3 * (attempt + 1)
                print(f"API retry HTTP {res.status_code}, sleeping {wait}s")
                time.sleep(wait)
                continue

            if res.status_code >= 400:
                raise RuntimeError(f"HTTP {res.status_code}: {res.text[:400]}")

            return res.json()

        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 * (attempt + 1)
            print(f"API exception {e}, sleeping {wait}s")
            time.sleep(wait)

    raise RuntimeError("API failed after retries")


def fetch_fixtures_for_date(date_value):
    date_s = date_value.strftime("%Y-%m-%d")

    data = api_call({
        "method": "get_fixtures",
        "date_start": date_s,
        "date_stop": date_s,
    })

    time.sleep(API_SLEEP_SECONDS)

    if data.get("success") != 1:
        print(f"Fixtures error for {date_s}: {data}")
        return []

    result = data.get("result") or []
    if not isinstance(result, list):
        return []

    print(f"Fetched fixtures {date_s}: {len(result)}")
    return result


def fetch_fixtures_for_dates(dates):
    fixtures_by_event_key = {}

    for d in sorted(dates):
        for match in fetch_fixtures_for_date(d):
            event_key = str(match.get("event_key") or "")
            if event_key:
                fixtures_by_event_key[event_key] = match

    return fixtures_by_event_key


# =========================
# SETTLE LOGIC
# =========================

def winner_key_from_match(match):
    winner = match.get("event_winner")

    first_key = safe_int(match.get("first_player_key"))
    second_key = safe_int(match.get("second_player_key"))

    if winner == "First Player":
        return first_key

    if winner == "Second Player":
        return second_key

    return None


def settle_pick(pick, match):
    """
    Mutates and returns a settled/pending pick.
    """
    out = dict(pick)

    event_status = str(match.get("event_status") or "")
    status_norm = normalize_status(event_status)

    out["settled_status"] = event_status
    out["event_winner"] = match.get("event_winner")
    out["final_score"] = final_score_from_match(match)

    # Not done yet.
    if status_norm not in {
        "finished",
        "cancelled",
        "postponed",
        "retired",
        "walkover",
        "abandoned",
        "interrupted",
    }:
        out["sabina_result"] = "pending"
        return out

    stake = safe_float(out.get("sabina_stake") or out.get("stake"), 0.0)
    odds = safe_float(out.get("odds"), 0.0)

    # Void-like outcomes.
    if status_norm in {"cancelled", "postponed", "abandoned", "interrupted"}:
        out["sabina_result"] = "void"
        out["sabina_profit"] = 0.0
        out["settled_at"] = now_local_iso()
        return out

    winner_key = winner_key_from_match(match)
    player_key = safe_int(out.get("player_key"))

    if not winner_key or not player_key:
        out["sabina_result"] = "pending"
        return out

    if winner_key == player_key:
        out["sabina_result"] = "win"
        out["sabina_profit"] = round(stake * (odds - 1.0), 4)
    else:
        out["sabina_result"] = "loss"
        out["sabina_profit"] = round(-stake, 4)

    out["settled_at"] = now_local_iso()
    return out


def load_sabina_history():
    history = load_json(SABINA_HISTORY_FILE, None)

    if isinstance(history, list):
        return history

    # Fallback: if history does not exist yet, use latest Sabina predictions.
    predictions = load_json(SABINA_PREDICTIONS_FILE, {})
    if isinstance(predictions, dict) and isinstance(predictions.get("picks"), list):
        return predictions["picks"]

    return []


def dates_to_check_for_pending(history):
    dates = set()
    today = datetime.now(ZoneInfo(TZ_NAME)).date()

    for pick in history:
        if not isinstance(pick, dict):
            continue

        if is_already_settled(pick):
            continue

        d = get_pick_date(pick)
        if not d:
            continue

        # Check pick date plus next day, because tennis matches can finish after midnight.
        dates.add(d)
        dates.add(d + timedelta(days=1))

        # Also check today, useful when date parsing or timezone is slightly off.
        dates.add(today)

    return dates


def settle_history(history, fixtures_by_event_key):
    settled_history = []

    newly_settled = 0
    still_pending = 0
    already_settled = 0
    missing_fixture = 0

    for pick in history:
        if not isinstance(pick, dict):
            continue

        if is_already_settled(pick):
            settled_history.append(pick)
            already_settled += 1
            continue

        event_key = str(pick.get("event_key") or pick.get("fixture_id") or "")
        match = fixtures_by_event_key.get(event_key)

        if not match:
            settled_history.append(pick)
            missing_fixture += 1
            continue

        before = normalize_status(pick.get("sabina_result") or pick.get("result") or "pending")
        updated = settle_pick(pick, match)
        after = normalize_status(updated.get("sabina_result") or "pending")

        if before == "pending" and after in {"win", "loss", "void"}:
            newly_settled += 1

        if after == "pending":
            still_pending += 1

        settled_history.append(updated)

    return settled_history, {
        "newly_settled": newly_settled,
        "still_pending": still_pending,
        "already_settled": already_settled,
        "missing_fixture": missing_fixture,
    }


# =========================
# REPORTING
# =========================

def stats(history):
    settled = [
        p for p in history
        if normalize_status(p.get("sabina_result")) in {"win", "loss"}
    ]

    wins = sum(1 for p in settled if normalize_status(p.get("sabina_result")) == "win")
    losses = sum(1 for p in settled if normalize_status(p.get("sabina_result")) == "loss")
    profit = sum(safe_float(p.get("sabina_profit"), 0.0) for p in settled)
    stake = sum(safe_float(p.get("sabina_stake") or p.get("stake"), 0.0) for p in settled)

    roi = profit / stake if stake else 0.0
    wr = wins / len(settled) if settled else 0.0

    pending = sum(
        1 for p in history
        if normalize_status(p.get("sabina_result") or p.get("result") or "pending") == "pending"
    )

    voids = sum(
        1 for p in history
        if normalize_status(p.get("sabina_result")) == "void"
    )

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

    dates = dates_to_check_for_pending(history)

    if not dates:
        print("No pending Sabina picks to settle.")
        report = {
            "generated_at": now_local_iso(),
            "timezone": TZ_NAME,
            "summary": stats(history),
            "picks": history,
        }
        save_json(SETTLED_JSON, report)
        write_csv(SETTLED_CSV, history)
        write_csv(PENDING_CSV, [])
        return

    fixtures_by_event_key = fetch_fixtures_for_dates(dates)

    updated_history, settle_summary = settle_history(history, fixtures_by_event_key)

    summary = stats(updated_history)

    report = {
        "generated_at": now_local_iso(),
        "timezone": TZ_NAME,
        "source_history_file": SABINA_HISTORY_FILE,
        "settle_summary": settle_summary,
        "summary": summary,
        "picks": updated_history,
    }

    # Keep Sabina history updated in-place.
    save_json(SABINA_HISTORY_FILE, updated_history)

    # Also write clean reports.
    save_json(SETTLED_JSON, report)

    settled_rows = [
        p for p in updated_history
        if normalize_status(p.get("sabina_result")) in {"win", "loss", "void"}
    ]
    pending_rows = [
        p for p in updated_history
        if normalize_status(p.get("sabina_result") or p.get("result") or "pending") == "pending"
    ]

    write_csv(SETTLED_CSV, settled_rows)
    write_csv(PENDING_CSV, pending_rows)

    print("")
    print("SABINA SETTLE DONE")
    print(f"History file:      {SABINA_HISTORY_FILE}")
    print(f"Settled JSON:      {SETTLED_JSON}")
    print(f"Settled CSV:       {SETTLED_CSV}")
    print(f"Pending CSV:       {PENDING_CSV}")
    print("")
    print(f"Newly settled:     {settle_summary['newly_settled']}")
    print(f"Still pending:     {settle_summary['still_pending']}")
    print(f"Already settled:   {settle_summary['already_settled']}")
    print(f"Missing fixture:   {settle_summary['missing_fixture']}")
    print("")
    print(f"Total history:     {summary['total_history']}")
    print(f"Settled bets:      {summary['settled_bets']}")
    print(f"Wins/Losses:       {summary['wins']} / {summary['losses']}")
    print(f"Voids:             {summary['voids']}")
    print(f"Pending:           {summary['pending']}")
    print(f"Profit:            {summary['profit']:+.2f}u")
    print(f"Stake:             {summary['stake']:.2f}u")
    print(f"ROI:               {summary['roi'] * 100:.1f}%")
    print(f"Win rate:          {summary['win_rate'] * 100:.1f}%")
    print("")

    for pick in settled_rows[-20:]:
        print(
            f"{pick.get('date')} {pick.get('time')} | "
            f"{pick.get('match')} | "
            f"{pick.get('bet')} @ {pick.get('odds')} | "
            f"{pick.get('sabina_result')} | "
            f"{safe_float(pick.get('sabina_profit'), 0.0):+.2f}u | "
            f"{pick.get('final_score')}"
        )


if __name__ == "__main__":
    main()

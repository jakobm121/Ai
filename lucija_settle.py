import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
LUCIJA_DIR = f"{DATA_DIR}/lucija"

SOURCE_RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results.json"

LUCIJA_RESULTS_FILE = f"{LUCIJA_DIR}/lucija_results.json"
LUCIJA_PREDICTIONS_FILE = f"{LUCIJA_DIR}/lucija_predictions.json"
LUCIJA_SUMMARY_FILE = f"{LUCIJA_DIR}/lucija_summary.json"
LUCIJA_TABLE_FILE = f"{LUCIJA_DIR}/lucija_table.md"
LUCIJA_DEBUG_FILE = f"{LUCIJA_DIR}/lucija_settle_debug.json"

LUCIJA_FLAT_STAKE = 1.0


def ensure_dirs():
    os.makedirs(LUCIJA_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def save_json(path, data):
    ensure_dirs()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    ensure_dirs()

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def settled_result(value):
    return str(value or "").lower() in {"win", "loss", "push", "void"}


def pending_result(value):
    return str(value or "pending").lower() == "pending"


def source_key(pick):
    """
    Fallback key, če source_pick_id ne obstaja.
    """
    return "|".join([
        str(pick.get("event_key") or pick.get("fixture_id") or ""),
        str(pick.get("side") or "").lower(),
        str(pick.get("line") or ""),
        str(pick.get("market") or ""),
    ])


def build_source_indexes(source_results):
    by_pick_id = {}
    by_source_key = {}

    for pick in source_results:
        if not isinstance(pick, dict):
            continue

        pid = pick.get("pick_id")
        if pid:
            by_pick_id[pid] = pick

        skey = source_key(pick)
        if skey.strip("|"):
            by_source_key[skey] = pick

    return by_pick_id, by_source_key


def recalc_profit_for_lucija(lucija_pick, source_pick):
    result = str(source_pick.get("result") or "").lower()
    stake = safe_float(lucija_pick.get("stake"), LUCIJA_FLAT_STAKE)
    odds = safe_float(lucija_pick.get("odds"))

    if result == "win":
        return round(stake * (odds - 1), 3)

    if result == "loss":
        return round(-stake, 3)

    if result in {"push", "void"}:
        return 0.0

    return None


def copy_settle_fields(lucija_pick, source_pick):
    lucija_pick["result"] = source_pick.get("result")
    lucija_pick["profit"] = recalc_profit_for_lucija(lucija_pick, source_pick)

    for key in [
        "settled_at",
        "settled_status",
        "event_winner",
        "final_score",
        "total_games",
    ]:
        if key in source_pick:
            lucija_pick[key] = source_pick.get(key)

    lucija_pick["settled_from"] = SOURCE_RESULTS_FILE
    lucija_pick["settled_source_pick_id"] = source_pick.get("pick_id")
    lucija_pick["lucija_settled_at"] = now_iso()


def build_summary(results):
    settled = [
        x for x in results
        if isinstance(x, dict)
        and settled_result(x.get("result"))
    ]

    graded = [
        x for x in settled
        if str(x.get("result") or "").lower() in {"win", "loss", "push"}
    ]

    wins = sum(1 for x in graded if str(x.get("result") or "").lower() == "win")
    losses = sum(1 for x in graded if str(x.get("result") or "").lower() == "loss")
    pushes = sum(1 for x in graded if str(x.get("result") or "").lower() == "push")
    voids = sum(1 for x in settled if str(x.get("result") or "").lower() == "void")
    pending = sum(1 for x in results if pending_result(x.get("result")))

    profit = round(sum(safe_float(x.get("profit")) for x in settled), 3)

    risked = sum(
        safe_float(x.get("stake"), LUCIJA_FLAT_STAKE)
        for x in graded
        if str(x.get("result") or "").lower() in {"win", "loss"}
    )

    winrate = round((wins / (wins + losses)) * 100, 2) if wins + losses else 0.0
    roi = round((profit / risked) * 100, 2) if risked else 0.0

    return {
        "generated_at": now_iso(),
        "source_results_file": SOURCE_RESULTS_FILE,
        "lucija_results_file": LUCIJA_RESULTS_FILE,
        "total": len(results),
        "pending": pending,
        "settled": len(settled),
        "graded": len(graded),
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "voids": voids,
        "profit": profit,
        "risked": round(risked, 3),
        "winrate": winrate,
        "roi": roi,
    }


def build_table(results):
    summary = build_summary(results)

    lines = []
    lines.append("# Lucija results")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Picks: {summary['total']}")
    lines.append(f"- Pending: {summary['pending']}")
    lines.append(f"- Settled: {summary['settled']}")
    lines.append(f"- W/L/P/V: {summary['wins']}/{summary['losses']}/{summary['pushes']}/{summary['voids']}")
    lines.append(f"- Profit: {summary['profit']}u")
    lines.append(f"- ROI: {summary['roi']}%")
    lines.append(f"- Winrate: {summary['winrate']}%")
    lines.append("")
    lines.append("| Date | Time | Match | Bet | Odds | Stake | Result | Profit | Score | Total |")
    lines.append("|---|---:|---|---|---:|---:|---|---:|---|---:|")

    sorted_rows = sorted(
        results,
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
        )
    )

    for p in sorted_rows:
        lines.append(
            "| "
            f"{p.get('date', '')} | "
            f"{p.get('time', '')} | "
            f"{p.get('match', '')} | "
            f"{p.get('bet', '')} | "
            f"{safe_float(p.get('odds')):.2f} | "
            f"{safe_float(p.get('stake'), LUCIJA_FLAT_STAKE):.2f} | "
            f"{p.get('result', 'pending')} | "
            f"{safe_float(p.get('profit')):.3f} | "
            f"{p.get('final_score', '') or ''} | "
            f"{p.get('total_games', '') or ''} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    lucija_results = load_json(LUCIJA_RESULTS_FILE, [])
    source_results = load_json(SOURCE_RESULTS_FILE, [])

    if not isinstance(lucija_results, list):
        lucija_results = []

    if not isinstance(source_results, list):
        source_results = []

    by_pick_id, by_source_key = build_source_indexes(source_results)

    debug = {
        "generated_at": now_iso(),
        "source_results_file": SOURCE_RESULTS_FILE,
        "lucija_results_file": LUCIJA_RESULTS_FILE,
        "source_results_count": len(source_results),
        "lucija_results_count": len(lucija_results),
        "updated": 0,
        "still_pending": 0,
        "source_not_found": 0,
        "source_not_settled": 0,
        "items": [],
    }

    for lucija_pick in lucija_results:
        if not isinstance(lucija_pick, dict):
            continue

        if not pending_result(lucija_pick.get("result")):
            continue

        source_pick = None
        match_method = None

        source_pick_id = lucija_pick.get("source_pick_id")

        if source_pick_id and source_pick_id in by_pick_id:
            source_pick = by_pick_id[source_pick_id]
            match_method = "source_pick_id"

        if source_pick is None:
            skey = source_key(lucija_pick)
            if skey in by_source_key:
                source_pick = by_source_key[skey]
                match_method = "source_key"

        if source_pick is None:
            debug["source_not_found"] += 1
            debug["items"].append({
                "pick_id": lucija_pick.get("pick_id"),
                "match": lucija_pick.get("match"),
                "status": "source_not_found",
            })
            continue

        if not settled_result(source_pick.get("result")):
            debug["source_not_settled"] += 1
            debug["still_pending"] += 1
            debug["items"].append({
                "pick_id": lucija_pick.get("pick_id"),
                "source_pick_id": source_pick.get("pick_id"),
                "match": lucija_pick.get("match"),
                "status": "source_not_settled",
                "source_result": source_pick.get("result"),
                "match_method": match_method,
            })
            continue

        copy_settle_fields(lucija_pick, source_pick)
        debug["updated"] += 1

        debug["items"].append({
            "pick_id": lucija_pick.get("pick_id"),
            "source_pick_id": source_pick.get("pick_id"),
            "match": lucija_pick.get("match"),
            "status": "settled",
            "result": lucija_pick.get("result"),
            "profit": lucija_pick.get("profit"),
            "total_games": lucija_pick.get("total_games"),
            "final_score": lucija_pick.get("final_score"),
            "match_method": match_method,
        })

    active_predictions = [
        x for x in lucija_results
        if isinstance(x, dict)
        and pending_result(x.get("result"))
    ]

    summary = build_summary(lucija_results)
    table = build_table(lucija_results)

    save_json(LUCIJA_RESULTS_FILE, lucija_results)
    save_json(LUCIJA_PREDICTIONS_FILE, active_predictions)
    save_json(LUCIJA_SUMMARY_FILE, summary)
    save_json(LUCIJA_DEBUG_FILE, debug)
    save_text(LUCIJA_TABLE_FILE, table)

    print("")
    print("LUCIJA SETTLE FROM TENNIS TOTALS RESULTS DONE")
    print(f"Source results: {len(source_results)}")
    print(f"Lucija results: {len(lucija_results)}")
    print(f"Updated: {debug['updated']}")
    print(f"Source not settled: {debug['source_not_settled']}")
    print(f"Source not found: {debug['source_not_found']}")
    print(f"Pending left: {len(active_predictions)}")
    print(f"Profit: {summary['profit']}u")
    print(f"ROI: {summary['roi']}%")
    print(f"Winrate: {summary['winrate']}%")


if __name__ == "__main__":
    main()

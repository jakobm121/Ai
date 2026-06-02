import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
HANA_DIR = f"{DATA_DIR}/hana"

HANA_PREDICTIONS_FILE = f"{HANA_DIR}/hana_predictions.json"
HANA_RESULTS_FILE = f"{HANA_DIR}/hana_results.json"
HANA_SETTLE_SUMMARY_FILE = f"{HANA_DIR}/hana_settle_summary.json"
HANA_SETTLE_DEBUG_FILE = f"{HANA_DIR}/hana_settle_debug.json"
HANA_SETTLE_TABLE_FILE = f"{HANA_DIR}/hana_settle_table.md"

SOURCE_RESULTS = {
    "jakob": f"{DATA_DIR}/jakob_results.json",
    "tedi_main": f"{DATA_DIR}/tedi/tedi_results.json",
    "tedi_v2": f"{DATA_DIR}/tedi/tedi_results.json",
    "lucija": f"{DATA_DIR}/lucija/lucija_results.json",
}

FLAT_STAKE = 1.0


def ensure_dirs():
    os.makedirs(HANA_DIR, exist_ok=True)


def now_iso():
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


def normalize_result(value):
    r = str(value or "").strip().lower()

    if r in {"win", "won", "w"}:
        return "win"

    if r in {"loss", "lost", "lose", "l"}:
        return "loss"

    if r in {"push", "void", "cancelled", "canceled"}:
        return "push"

    if r in {"pending", "", "open"}:
        return "pending"

    return r


def is_settled(value):
    return normalize_result(value) in {"win", "loss", "push"}


def extract_hana_predictions(raw):
    if isinstance(raw, dict):
        picks = raw.get("picks", [])
        return picks if isinstance(picks, list) else []

    if isinstance(raw, list):
        return raw

    return []


def hana_key(item):
    return "|".join([
        str(item.get("event_key") or item.get("fixture_id") or ""),
        str(item.get("side") or "").strip().lower(),
        f"{safe_float(item.get('line'), 0.0):.1f}",
    ])


def source_fallback_key(item):
    return "|".join([
        str(item.get("event_key") or item.get("fixture_id") or ""),
        str(item.get("side") or "").strip().lower(),
        f"{safe_float(item.get('line'), 0.0):.1f}",
    ])


def load_source_indexes():
    indexes = {}
    debug = {}

    for machine, path in SOURCE_RESULTS.items():
        rows = load_json(path, [])

        if not isinstance(rows, list):
            rows = []

        by_pick_id = {}
        by_fallback = {}

        for row in rows:
            if not isinstance(row, dict):
                continue

            if not is_settled(row.get("result")):
                continue

            pid = str(row.get("pick_id") or "").strip()
            if pid:
                by_pick_id[pid] = row

            key = source_fallback_key(row)
            if key:
                by_fallback[key] = row

        indexes[machine] = {
            "path": path,
            "by_pick_id": by_pick_id,
            "by_fallback": by_fallback,
        }

        debug[machine] = {
            "file": path,
            "loaded_rows": len(rows),
            "settled_by_pick_id": len(by_pick_id),
            "settled_by_fallback": len(by_fallback),
        }

    return indexes, debug


def find_source_result(hana_pick, indexes):
    source_pick_ids = hana_pick.get("source_pick_ids") or {}

    # First try exact pick_id from Hana source_pick_ids.
    for machine, source_pick_id in source_pick_ids.items():
        machine_index = indexes.get(machine)
        if not machine_index:
            continue

        pid = str(source_pick_id or "").strip()
        if pid and pid in machine_index["by_pick_id"]:
            return machine, machine_index["by_pick_id"][pid], "source_pick_id"

    # Fallback: event_key + side + line.
    key = hana_key(hana_pick)

    for machine in ["jakob", "tedi_main", "tedi_v2", "lucija"]:
        machine_index = indexes.get(machine)
        if not machine_index:
            continue

        if key in machine_index["by_fallback"]:
            return machine, machine_index["by_fallback"][key], "fallback_key"

    return None, None, None


def profit_for_hana(hana_pick, result):
    odds = safe_float(hana_pick.get("best_odds") or hana_pick.get("odds"), 0.0)
    stake = safe_float(hana_pick.get("stake"), FLAT_STAKE)

    if result == "win":
        return round(stake * (odds - 1.0), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def merge_existing_results(existing_results, current_predictions):
    existing_by_key = {}

    for item in existing_results:
        if not isinstance(item, dict):
            continue
        existing_by_key[hana_key(item)] = item

    for item in current_predictions:
        key = hana_key(item)
        if key not in existing_by_key:
            new_item = dict(item)
            new_item["stake"] = FLAT_STAKE
            new_item["result"] = "pending"
            new_item["profit"] = None
            new_item["hana_created_at"] = item.get("generated_at") or now_iso()
            existing_by_key[key] = new_item
            continue

        old = existing_by_key[key]

        if is_settled(old.get("result")):
            continue

        created_at = old.get("hana_created_at") or item.get("generated_at") or now_iso()
        old.update(item)
        old["stake"] = safe_float(old.get("stake"), FLAT_STAKE)
        old["result"] = "pending"
        old["profit"] = None
        old["hana_created_at"] = created_at

    return list(existing_by_key.values())


def settle_hana_results(results, indexes):
    final = []
    settled_now = []
    already_settled = []
    still_pending = []
    debug_items = []

    for item in results:
        if not isinstance(item, dict):
            continue

        pick = dict(item)

        if is_settled(pick.get("result")):
            already_settled.append(pick)
            final.append(pick)
            continue

        machine, source, method = find_source_result(pick, indexes)

        if not source:
            still_pending.append(pick)
            final.append(pick)
            debug_items.append({
                "hub_key": pick.get("hub_key"),
                "match": pick.get("match"),
                "bet": pick.get("bet"),
                "source_pick_ids": pick.get("source_pick_ids"),
                "status": "missing_source_result",
            })
            continue

        result = normalize_result(source.get("result"))

        if result not in {"win", "loss", "push"}:
            still_pending.append(pick)
            final.append(pick)
            continue

        pick["result"] = result
        pick["profit"] = profit_for_hana(pick, result)
        pick["settled_at"] = source.get("settled_at") or now_iso()
        pick["settled_status"] = source.get("settled_status", "")
        pick["event_winner"] = source.get("event_winner", "")
        pick["final_score"] = source.get("final_score", "")
        pick["total_games"] = source.get("total_games")
        pick["hana_settled_from_machine"] = machine
        pick["hana_settled_from_file"] = indexes[machine]["path"]
        pick["hana_settle_match_method"] = method
        pick["hana_source_result_pick_id"] = source.get("pick_id")
        pick["hana_settled_at"] = now_iso()

        settled_now.append(pick)
        final.append(pick)

        debug_items.append({
            "hub_key": pick.get("hub_key"),
            "match": pick.get("match"),
            "bet": pick.get("bet"),
            "result": result,
            "profit": pick.get("profit"),
            "machine": machine,
            "method": method,
            "source_pick_id": source.get("pick_id"),
            "total_games": pick.get("total_games"),
            "final_score": pick.get("final_score"),
        })

    return final, settled_now, already_settled, still_pending, debug_items


def evaluate(items):
    settled = [x for x in items if is_settled(x.get("result"))]
    wins = [x for x in settled if normalize_result(x.get("result")) == "win"]
    losses = [x for x in settled if normalize_result(x.get("result")) == "loss"]
    pushes = [x for x in settled if normalize_result(x.get("result")) == "push"]

    stake = sum(safe_float(x.get("stake"), FLAT_STAKE) for x in settled)
    profit = round(sum(safe_float(x.get("profit"), 0.0) for x in settled), 4)

    graded = len(wins) + len(losses)

    return {
        "picks": len(items),
        "settled": len(settled),
        "pending": len([x for x in items if not is_settled(x.get("result"))]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "stake": round(stake, 4),
        "profit": profit,
        "winrate": round(len(wins) / graded * 100, 2) if graded else 0.0,
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
    }


def group_by_consensus(items):
    groups = {}

    for item in items:
        level = str(item.get("consensus_level") or "unknown")
        groups.setdefault(level, []).append(item)

    return {level: evaluate(rows) for level, rows in sorted(groups.items())}


def build_table(results, summary):
    lines = []
    lines.append("# Hana settled results")
    lines.append("")
    lines.append(f"Generated: {summary['generated_at']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    overall = summary["overall"]
    lines.append(
        f"| {overall['picks']} | {overall['settled']} | {overall['pending']} | "
        f"{overall['wins']} | {overall['losses']} | {overall['pushes']} | "
        f"{overall['winrate']}% | {overall['profit']}u | {overall['roi']}% |"
    )

    lines.append("")
    lines.append("## By consensus")
    lines.append("")
    lines.append("| Consensus | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for level, stats in summary["by_consensus"].items():
        lines.append(
            f"| {level} | {stats['picks']} | {stats['settled']} | {stats['pending']} | "
            f"{stats['wins']} | {stats['losses']} | {stats['pushes']} | "
            f"{stats['winrate']}% | {stats['profit']}u | {stats['roi']}% |"
        )

    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Date | Time | Consensus | Result | Profit | Match | Bet | Odds | Total games | Final score | Settled from |")
    lines.append("|---|---:|---|---|---:|---|---|---:|---:|---|---|")

    rows = sorted(
        results,
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
            str(x.get("side") or ""),
            safe_float(x.get("line"), 0.0),
        )
    )

    for p in rows:
        lines.append(
            "| "
            f"{p.get('date', '')} | "
            f"{p.get('time', '')} | "
            f"{p.get('consensus_level', '')} | "
            f"{normalize_result(p.get('result'))} | "
            f"{safe_float(p.get('profit'), 0.0):.2f} | "
            f"{p.get('match', '')} | "
            f"{p.get('bet', '')} | "
            f"{safe_float(p.get('best_odds') or p.get('odds'), 0.0):.2f} | "
            f"{p.get('total_games', '')} | "
            f"{p.get('final_score', '')} | "
            f"{p.get('hana_settled_from_machine', '')} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    raw_hana = load_json(HANA_PREDICTIONS_FILE, {})
    hana_predictions = extract_hana_predictions(raw_hana)

    existing_results = load_json(HANA_RESULTS_FILE, [])
    if not isinstance(existing_results, list):
        existing_results = []

    merged = merge_existing_results(existing_results, hana_predictions)

    indexes, source_debug = load_source_indexes()

    final_results, settled_now, already_settled, still_pending, debug_items = settle_hana_results(
        merged,
        indexes,
    )

    final_results.sort(
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
            str(x.get("side") or ""),
            safe_float(x.get("line"), 0.0),
        )
    )

    summary = {
        "generated_at": now_iso(),
        "hana_predictions_file": HANA_PREDICTIONS_FILE,
        "hana_results_file": HANA_RESULTS_FILE,
        "source_results": SOURCE_RESULTS,
        "predictions_loaded": len(hana_predictions),
        "existing_results_loaded": len(existing_results),
        "settled_now": len(settled_now),
        "already_settled": len(already_settled),
        "still_pending": len(still_pending),
        "overall": evaluate(final_results),
        "by_consensus": group_by_consensus(final_results),
    }

    debug = {
        "generated_at": summary["generated_at"],
        "source_debug": source_debug,
        "settled_items": debug_items,
        "settled_now": len(settled_now),
        "still_pending": len(still_pending),
    }

    save_json(HANA_RESULTS_FILE, final_results)
    save_json(HANA_SETTLE_SUMMARY_FILE, summary)
    save_json(HANA_SETTLE_DEBUG_FILE, debug)
    save_text(HANA_SETTLE_TABLE_FILE, build_table(final_results, summary))

    print("")
    print("HANA SETTLE DONE")
    print(f"Predictions loaded: {len(hana_predictions)}")
    print(f"Existing loaded:    {len(existing_results)}")
    print(f"Settled now:        {len(settled_now)}")
    print(f"Already settled:    {len(already_settled)}")
    print(f"Still pending:      {len(still_pending)}")
    print(f"Results file:       {HANA_RESULTS_FILE}")
    print(f"Summary file:       {HANA_SETTLE_SUMMARY_FILE}")
    print(f"Debug file:         {HANA_SETTLE_DEBUG_FILE}")
    print(f"Table file:         {HANA_SETTLE_TABLE_FILE}")
    print("")


if __name__ == "__main__":
    main()

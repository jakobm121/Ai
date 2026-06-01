import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
TEDI_DIR = f"{DATA_DIR}/tedi"

TEDI_RESULTS_FILE = f"{TEDI_DIR}/tedi_results.json"
TEDI_SUMMARY_FILE = f"{TEDI_DIR}/tedi_settle_summary.json"
TEDI_TABLE_FILE = f"{TEDI_DIR}/tedi_settle_table.md"
TEDI_DEBUG_FILE = f"{TEDI_DIR}/tedi_settle_debug.json"

SOURCE_TOTALS_RESULTS_FILE = f"{DATA_DIR}/tennis_totals_results.json"

FLAT_STAKE = 1.0


def ensure_dirs():
    os.makedirs(TEDI_DIR, exist_ok=True)


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


def normalize_text(value):
    return str(value or "").strip().lower()


def normalize_result(value):
    r = normalize_text(value)

    if r in {"win", "won", "w"}:
        return "win"
    if r in {"loss", "lost", "lose", "l"}:
        return "loss"
    if r in {"push", "void", "cancelled", "canceled"}:
        return "push"
    if r in {"pending", ""}:
        return "pending"

    return r


def is_settled(pick):
    return normalize_result(pick.get("result")) in {"win", "loss", "push"}


def profit_for_pick(pick, stake=None):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), 0.0)

    if stake is None:
        stake = safe_float(pick.get("stake"), FLAT_STAKE)

    if result == "win":
        return round(stake * (odds - 1.0), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def norm_line(value):
    return f"{safe_float(value, 0.0):.1f}"


def settle_key(pick):
    return "|".join([
        str(pick.get("event_key") or pick.get("fixture_id") or ""),
        normalize_text(pick.get("market")),
        normalize_text(pick.get("side")),
        norm_line(pick.get("line")),
    ])


def build_source_index(source_results):
    index = {}

    for item in source_results:
        if not isinstance(item, dict):
            continue

        if not is_settled(item):
            continue

        key = settle_key(item)
        index[key] = item

    return index


def settle_tedi_results(tedi_results, source_results):
    source_index = build_source_index(source_results)

    settled_now = []
    already_settled = []
    still_pending = []
    missing_source = []

    final = []

    for item in tedi_results:
        if not isinstance(item, dict):
            continue

        pick = dict(item)

        if is_settled(pick):
            already_settled.append(pick)
            final.append(pick)
            continue

        key = settle_key(pick)
        source = source_index.get(key)

        if not source:
            still_pending.append(pick)
            missing_source.append({
                "tedi_pick_id": pick.get("pick_id"),
                "source_pick_id": pick.get("source_pick_id"),
                "strategy": pick.get("tedi_strategy"),
                "match": pick.get("match"),
                "bet": pick.get("bet"),
                "key": key,
                "reason": "no_settled_source_match",
            })
            final.append(pick)
            continue

        source_result = normalize_result(source.get("result"))

        if source_result not in {"win", "loss", "push"}:
            still_pending.append(pick)
            final.append(pick)
            continue

        copy_fields = [
            "result",
            "settled_at",
            "settled_status",
            "event_winner",
            "final_score",
            "winner",
            "score",
            "total_games",
            "settled_from",
            "settled_source_pick_id",
        ]

        for field in copy_fields:
            if field in source:
                pick[field] = source[field]

        pick["result"] = source_result
        pick["profit"] = profit_for_pick(pick, safe_float(pick.get("stake"), FLAT_STAKE))
        pick["tedi_settled_from"] = SOURCE_TOTALS_RESULTS_FILE
        pick["tedi_settled_source_pick_id"] = source.get("pick_id")
        pick["tedi_settled_at"] = now_iso()

        settled_now.append(pick)
        final.append(pick)

    return final, settled_now, already_settled, still_pending, missing_source


def evaluate(picks):
    settled = [p for p in picks if is_settled(p)]
    wins = [p for p in settled if normalize_result(p.get("result")) == "win"]
    losses = [p for p in settled if normalize_result(p.get("result")) == "loss"]
    pushes = [p for p in settled if normalize_result(p.get("result")) == "push"]

    stake_sum = sum(safe_float(p.get("stake"), FLAT_STAKE) for p in settled)
    profit = round(sum(safe_float(p.get("profit"), 0.0) for p in settled), 4)

    winrate = round(len(wins) / max(1, len(wins) + len(losses)) * 100, 2)
    roi = round(profit / stake_sum * 100, 2) if stake_sum else 0.0

    return {
        "picks": len(picks),
        "settled": len(settled),
        "pending": len([p for p in picks if not is_settled(p)]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "stake_sum": round(stake_sum, 4),
        "profit": profit,
        "roi": roi,
        "winrate": winrate,
    }


def group_by_strategy(picks):
    groups = {}

    for p in picks:
        strategy = str(p.get("tedi_strategy") or "unknown")
        groups.setdefault(strategy, []).append(p)

    return {
        strategy: evaluate(items)
        for strategy, items in sorted(groups.items())
    }


def sort_key(pick):
    return (
        str(pick.get("date") or ""),
        str(pick.get("time") or ""),
        str(pick.get("match") or ""),
        str(pick.get("tedi_strategy") or ""),
    )


def build_table(results, summary):
    lines = []

    lines.append("# Tedi settled results")
    lines.append("")
    lines.append(f"Generated: {summary['generated_at']}")
    lines.append("")
    lines.append("## Summary by strategy")
    lines.append("")
    lines.append("| Strategy | Picks | Settled | Pending | W | L | P | Winrate | Profit | ROI |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for strategy, stats in summary["by_strategy"].items():
        lines.append(
            f"| {strategy} | "
            f"{stats['picks']} | "
            f"{stats['settled']} | "
            f"{stats['pending']} | "
            f"{stats['wins']} | "
            f"{stats['losses']} | "
            f"{stats['pushes']} | "
            f"{stats['winrate']}% | "
            f"{stats['profit']}u | "
            f"{stats['roi']}% |"
        )

    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Date | Time | Strategy | Result | Profit | Match | Bet | Odds | Total games | Final score |")
    lines.append("|---|---:|---|---|---:|---|---|---:|---:|---|")

    for p in sorted(results, key=sort_key):
        lines.append(
            "| "
            f"{p.get('date', '')} | "
            f"{p.get('time', '')} | "
            f"{p.get('tedi_strategy', '')} | "
            f"{normalize_result(p.get('result'))} | "
            f"{safe_float(p.get('profit'), 0.0):.2f} | "
            f"{p.get('match', '')} | "
            f"{p.get('bet', '')} | "
            f"{safe_float(p.get('odds'), 0.0):.2f} | "
            f"{p.get('total_games', '')} | "
            f"{p.get('final_score', '')} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    tedi_results = load_json(TEDI_RESULTS_FILE, [])
    source_results = load_json(SOURCE_TOTALS_RESULTS_FILE, [])

    if not isinstance(tedi_results, list):
        tedi_results = []

    if not isinstance(source_results, list):
        source_results = []

    final_results, settled_now, already_settled, still_pending, missing_source = settle_tedi_results(
        tedi_results=tedi_results,
        source_results=source_results,
    )

    final_results.sort(key=sort_key)

    summary = {
        "generated_at": now_iso(),
        "tedi_results_file": TEDI_RESULTS_FILE,
        "source_results_file": SOURCE_TOTALS_RESULTS_FILE,
        "tedi_results_loaded": len(tedi_results),
        "source_results_loaded": len(source_results),
        "settled_now": len(settled_now),
        "already_settled": len(already_settled),
        "still_pending": len(still_pending),
        "overall": evaluate(final_results),
        "by_strategy": group_by_strategy(final_results),
    }

    debug = {
        "generated_at": summary["generated_at"],
        "settled_now": [
            {
                "pick_id": p.get("pick_id"),
                "source_pick_id": p.get("source_pick_id"),
                "strategy": p.get("tedi_strategy"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "result": p.get("result"),
                "profit": p.get("profit"),
                "total_games": p.get("total_games"),
                "final_score": p.get("final_score"),
            }
            for p in settled_now
        ],
        "missing_source": missing_source[:1000],
    }

    save_json(TEDI_RESULTS_FILE, final_results)
    save_json(TEDI_SUMMARY_FILE, summary)
    save_json(TEDI_DEBUG_FILE, debug)
    save_text(TEDI_TABLE_FILE, build_table(final_results, summary))

    print("")
    print("TEDI SETTLE DONE")
    print(f"Tedi loaded: {len(tedi_results)}")
    print(f"Source loaded: {len(source_results)}")
    print(f"Settled now: {len(settled_now)}")
    print(f"Already settled: {len(already_settled)}")
    print(f"Still pending: {len(still_pending)}")
    print(f"Results file: {TEDI_RESULTS_FILE}")
    print(f"Summary file: {TEDI_SUMMARY_FILE}")
    print(f"Debug file: {TEDI_DEBUG_FILE}")
    print(f"Table file: {TEDI_TABLE_FILE}")


if __name__ == "__main__":
    main()

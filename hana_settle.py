import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
HANA_DIR = f"{DATA_DIR}/hana"

HANA_RESULTS_FILE = f"{HANA_DIR}/hana_results.json"
HANA_SUMMARY_FILE = f"{HANA_DIR}/hana_settle_summary.json"
HANA_DEBUG_FILE = f"{HANA_DIR}/hana_settle_debug.json"
HANA_TABLE_FILE = f"{HANA_DIR}/hana_settle_table.md"

SOURCE_RESULTS = {
    "jakob": f"{DATA_DIR}/jakob_results.json",
    "tedi": f"{DATA_DIR}/tedi/tedi_results.json",
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
            return json.load(f)
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


def is_settled(row):
    return normalize_result(row.get("result")) in {"win", "loss", "push"}


def extract_rows(raw):
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ["picks", "results", "data"]:
            value = raw.get(key)
            if isinstance(value, list):
                return value

    return []


def get_odds(row):
    return safe_float(
        row.get("best_odds")
        or row.get("odds")
        or row.get("price")
        or row.get("decimal_odds"),
        0.0,
    )


def get_line(row):
    return safe_float(row.get("line"), 0.0)


def get_side(row):
    return str(row.get("side") or "").strip().lower()


def get_event_key(row):
    return str(row.get("event_key") or row.get("fixture_id") or "").strip()


def hana_key(row):
    return "|".join([
        get_event_key(row),
        get_side(row),
        f"{get_line(row):.1f}",
    ])


def source_label(row):
    side = get_side(row).upper()
    line = get_line(row)
    if side in {"over", "under"}:
        return f"{side} {line:.1f}"
    return str(row.get("bet") or "")


def load_source_results():
    grouped = {}
    debug = {}

    for source_name, path in SOURCE_RESULTS.items():
        raw = load_json(path, [])
        rows = extract_rows(raw)

        settled_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue

            if not is_settled(row):
                continue

            key = hana_key(row)
            if not key or key.startswith("|"):
                continue

            settled_rows.append(row)
            grouped.setdefault(key, []).append({
                "source": source_name,
                "path": path,
                "row": row,
            })

        debug[source_name] = {
            "file": path,
            "loaded_rows": len(rows),
            "settled_rows": len(settled_rows),
        }

    return grouped, debug


def choose_best_row(source_items):
    """
    For Hana display we keep the row with best odds.
    """
    return max(
        source_items,
        key=lambda item: (
            get_odds(item["row"]),
            safe_float(item["row"].get("edge"), 0.0),
            safe_float(item["row"].get("quality_score"), 0.0),
        )
    )


def consensus_level(source_count):
    if source_count >= 3:
        return "triple"
    if source_count == 2:
        return "double"
    return "single"


def hana_profit(result, odds, stake=FLAT_STAKE):
    result = normalize_result(result)

    if result == "win":
        return round(stake * (odds - 1.0), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def build_hana_results(grouped):
    hana_results = []

    for key, source_items in grouped.items():
        best_item = choose_best_row(source_items)
        best = best_item["row"]

        sources = sorted({item["source"] for item in source_items})
        source_count = len(sources)

        result = normalize_result(best.get("result"))
        odds = get_odds(best)
        stake = FLAT_STAKE

        row = {
            "hana_key": key,
            "date": best.get("date", ""),
            "time": best.get("time", ""),
            "match": best.get("match", ""),
            "bet": source_label(best),
            "side": get_side(best),
            "line": get_line(best),
            "odds": odds,
            "stake": stake,
            "result": result,
            "profit": hana_profit(result, odds, stake),
            "consensus_level": consensus_level(source_count),
            "source_count": source_count,
            "sources": sources,
            "source_pick_ids": {
                item["source"]: item["row"].get("pick_id")
                for item in source_items
            },
            "source_results": {
                item["source"]: normalize_result(item["row"].get("result"))
                for item in source_items
            },
            "event_key": best.get("event_key"),
            "fixture_id": best.get("fixture_id"),
            "market": best.get("market", ""),
            "tour_level": best.get("tour_level", ""),
            "event_type": best.get("event_type", ""),
            "best_bookmaker": best.get("best_bookmaker", ""),
            "market_median_odds": best.get("market_median_odds", ""),
            "edge": best.get("edge", ""),
            "model_prob": best.get("model_prob", ""),
            "implied_prob": best.get("implied_prob", ""),
            "confidence": best.get("confidence", ""),
            "quality_score": best.get("quality_score", ""),
            "settled_at": best.get("settled_at", ""),
            "settled_status": best.get("settled_status", ""),
            "event_winner": best.get("event_winner", ""),
            "final_score": best.get("final_score", ""),
            "total_games": best.get("total_games", ""),
            "hana_built_at": now_iso(),
        }

        hana_results.append(row)

    hana_results.sort(
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
            str(x.get("side") or ""),
            safe_float(x.get("line"), 0.0),
        )
    )

    return hana_results


def evaluate(rows):
    settled = [r for r in rows if normalize_result(r.get("result")) in {"win", "loss", "push"}]
    graded = [r for r in settled if normalize_result(r.get("result")) in {"win", "loss"}]

    wins = [r for r in graded if normalize_result(r.get("result")) == "win"]
    losses = [r for r in graded if normalize_result(r.get("result")) == "loss"]
    pushes = [r for r in settled if normalize_result(r.get("result")) == "push"]

    stake = sum(safe_float(r.get("stake"), FLAT_STAKE) for r in graded)
    profit = round(sum(safe_float(r.get("profit"), 0.0) for r in settled), 4)

    return {
        "picks": len(rows),
        "settled": len(settled),
        "graded": len(graded),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "stake": round(stake, 4),
        "profit": profit,
        "win_rate": round(len(wins) / len(graded) * 100, 2) if graded else 0.0,
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
    }


def group_stats(rows, field):
    out = {}

    for row in rows:
        key = str(row.get(field) or "unknown")
        out.setdefault(key, []).append(row)

    return {
        key: evaluate(items)
        for key, items in sorted(out.items())
    }


def build_table(rows, summary):
    lines = []

    lines.append("# Hana settled results")
    lines.append("")
    lines.append(f"Generated: {summary['generated_at']}")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Picks | Settled | W | L | Push | Winrate | Profit | ROI |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")

    overall = summary["overall"]
    lines.append(
        f"| {overall['picks']} | {overall['settled']} | "
        f"{overall['wins']} | {overall['losses']} | {overall['pushes']} | "
        f"{overall['win_rate']}% | {overall['profit']}u | {overall['roi']}% |"
    )

    lines.append("")
    lines.append("## By consensus")
    lines.append("")
    lines.append("| Consensus | Picks | Settled | W | L | Push | Winrate | Profit | ROI |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for level, stats in summary["by_consensus"].items():
        lines.append(
            f"| {level} | {stats['picks']} | {stats['settled']} | "
            f"{stats['wins']} | {stats['losses']} | {stats['pushes']} | "
            f"{stats['win_rate']}% | {stats['profit']}u | {stats['roi']}% |"
        )

    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Date | Time | Consensus | Sources | Result | Profit | Match | Bet | Odds | Total games | Final score |")
    lines.append("|---|---:|---|---|---|---:|---|---|---:|---:|---|")

    for r in rows:
        lines.append(
            "| "
            f"{r.get('date', '')} | "
            f"{r.get('time', '')} | "
            f"{r.get('consensus_level', '')} | "
            f"{', '.join(r.get('sources') or [])} | "
            f"{r.get('result', '')} | "
            f"{safe_float(r.get('profit'), 0.0):.2f} | "
            f"{r.get('match', '')} | "
            f"{r.get('bet', '')} | "
            f"{safe_float(r.get('odds'), 0.0):.2f} | "
            f"{r.get('total_games', '')} | "
            f"{r.get('final_score', '')} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    grouped, source_debug = load_source_results()
    hana_results = build_hana_results(grouped)

    summary = {
        "generated_at": now_iso(),
        "description": "Hana settle built directly from settled results of Jakob, Tedi and Lucija.",
        "dedupe_key": "event_key + side + line",
        "source_results": SOURCE_RESULTS,
        "source_debug": source_debug,
        "unique_hana_picks": len(hana_results),
        "overall": evaluate(hana_results),
        "by_consensus": group_stats(hana_results, "consensus_level"),
        "by_side": group_stats(hana_results, "side"),
        "by_tour_level": group_stats(hana_results, "tour_level"),
    }

    debug = {
        "generated_at": summary["generated_at"],
        "source_debug": source_debug,
        "grouped_keys": len(grouped),
        "hana_results": len(hana_results),
    }

    save_json(HANA_RESULTS_FILE, hana_results)
    save_json(HANA_SUMMARY_FILE, summary)
    save_json(HANA_DEBUG_FILE, debug)
    save_text(HANA_TABLE_FILE, build_table(hana_results, summary))

    print("")
    print("HANA SETTLE FROM RESULTS DONE")
    print(f"Unique Hana picks: {len(hana_results)}")
    print(f"Results:           {HANA_RESULTS_FILE}")
    print(f"Summary:           {HANA_SUMMARY_FILE}")
    print(f"Debug:             {HANA_DEBUG_FILE}")
    print(f"Table:             {HANA_TABLE_FILE}")
    print("")
    print("Overall:")
    print(summary["overall"])
    print("")


if __name__ == "__main__":
    main()

import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
HANA_DIR = f"{DATA_DIR}/hana"

SOURCES = [
    {
        "machine": "jakob",
        "file": f"{DATA_DIR}/jakob_predictions.json",
        "path_type": "predictions",
    },
    {
        "machine": "tedi_main",
        "file": f"{DATA_DIR}/tedi/tedi_predictions.json",
        "path_type": "list",
    },
    {
        "machine": "tedi_v2",
        "file": f"{DATA_DIR}/tedi/tedi_v2_test_predictions.json",
        "path_type": "list",
    },
    {
        "machine": "lucija",
        "file": f"{DATA_DIR}/lucija/lucija_predictions.json",
        "path_type": "list",
    },
]

HANA_PREDICTIONS_FILE = f"{HANA_DIR}/hana_predictions.json"
HANA_TABLE_FILE = f"{HANA_DIR}/hana_table.md"
HANA_DEBUG_FILE = f"{HANA_DIR}/hana_debug.json"


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


def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def normalize_text(value):
    return str(value or "").strip().lower()


def normalize_line(value):
    return f"{safe_float(value, 0.0):.1f}"


def normalize_side(value):
    return normalize_text(value)


def extract_picks(raw):
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ["picks", "predictions", "data", "results", "ranked_candidates"]:
            value = raw.get(key)
            if isinstance(value, list):
                return value

    return []


def is_active_pick(pick):
    if not isinstance(pick, dict):
        return False

    result = normalize_text(pick.get("result"))

    if result not in {"", "pending", "open"}:
        return False

    if pick.get("settled_at"):
        return False

    if pick.get("final_score"):
        return False

    if pick.get("total_games") is not None:
        return False

    if not (pick.get("event_key") or pick.get("fixture_id") or pick.get("match")):
        return False

    if normalize_side(pick.get("side")) not in {"under", "over"}:
        return False

    if pick.get("line") is None:
        return False

    return True


def hub_key_for_pick(pick):
    event_key = pick.get("event_key") or pick.get("fixture_id")

    if event_key:
        base = str(event_key)
    else:
        base = "|".join([
            str(pick.get("date") or ""),
            str(pick.get("time") or ""),
            str(pick.get("match") or ""),
        ])

    return "|".join([
        base,
        normalize_side(pick.get("side")),
        normalize_line(pick.get("line")),
    ])


def consensus_level(machine_count):
    if machine_count >= 4:
        return "quad"
    if machine_count == 3:
        return "triple"
    if machine_count == 2:
        return "double"
    return "single"


def machine_priority(machine):
    priority = {
        "jakob": 1,
        "tedi_main": 2,
        "lucija": 3,
        "tedi_v2": 4,
    }
    return priority.get(machine, 99)


def best_value(items, field, default=None):
    values = []

    for item in items:
        value = item.get(field)
        if value is not None and value != "":
            values.append(value)

    if not values:
        return default

    return values[0]


def best_numeric(items, field, default=0.0):
    nums = []

    for item in items:
        value = safe_float(item.get(field), None)
        if value is not None:
            nums.append(value)

    if not nums:
        return default

    return max(nums)


def get_market_gap(pick):
    direct = safe_float(pick.get("market_gap"), None)
    if direct is not None:
        return direct

    market_info = pick.get("market_info") or {}
    if isinstance(market_info, dict):
        return safe_float(market_info.get("market_gap"), None)

    return None


def get_strength_gap(pick):
    direct = safe_float(pick.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)

    first = safe_float(pick.get("first_strength_score"), None)
    second = safe_float(pick.get("second_strength_score"), None)

    if first is None or second is None:
        return None

    return abs(first - second)


def get_avg_three_set(pick):
    metrics = pick.get("tedi_metrics") or pick.get("lucija_metrics") or {}
    if isinstance(metrics, dict):
        value = safe_float(metrics.get("avg_three_set"), None)
        if value is not None:
            return value

    first = (((pick.get("first_form") or {}).get("last_10") or {}).get("three_set_rate"))
    second = (((pick.get("second_form") or {}).get("last_10") or {}).get("three_set_rate"))

    values = [safe_float(x, None) for x in [first, second]]
    values = [x for x in values if x is not None]

    if not values:
        return None

    return round(sum(values) / len(values), 4)


def get_avg_close_set(pick):
    metrics = pick.get("tedi_metrics") or pick.get("lucija_metrics") or {}
    if isinstance(metrics, dict):
        value = safe_float(metrics.get("avg_close_set"), None)
        if value is not None:
            return value

    first = (((pick.get("first_form") or {}).get("last_10") or {}).get("close_set_rate"))
    second = (((pick.get("second_form") or {}).get("last_10") or {}).get("close_set_rate"))

    values = [safe_float(x, None) for x in [first, second]]
    values = [x for x in values if x is not None]

    if not values:
        return None

    return round(sum(values) / len(values), 4)


def normalize_pick_for_machine(pick, machine):
    out = dict(pick)
    out["_hana_machine"] = machine
    out["_hana_hub_key"] = hub_key_for_pick(pick)
    return out


def build_hub_item(hub_key, picks):
    picks_sorted = sorted(
        picks,
        key=lambda p: (
            machine_priority(p.get("_hana_machine")),
            -safe_float(p.get("quality_score"), 0),
            -safe_float(p.get("confidence"), 0),
            -safe_float(p.get("edge"), 0),
        ),
    )

    main = picks_sorted[0]
    machines = [p.get("_hana_machine") for p in picks_sorted]
    machines_unique = []

    for m in machines:
        if m and m not in machines_unique:
            machines_unique.append(m)

    machine_count = len(machines_unique)

    odds_by_machine = {}
    bookmaker_by_machine = {}
    confidence_by_machine = {}
    quality_by_machine = {}
    edge_by_machine = {}
    source_pick_ids = {}

    for p in picks_sorted:
        machine = p.get("_hana_machine")
        if not machine:
            continue

        odds_by_machine[machine] = p.get("odds")
        bookmaker_by_machine[machine] = p.get("best_bookmaker")
        confidence_by_machine[machine] = p.get("confidence")
        quality_by_machine[machine] = p.get("quality_score")
        edge_by_machine[machine] = p.get("edge")
        source_pick_ids[machine] = p.get("pick_id")

    best_odds = best_numeric(picks_sorted, "odds", 0.0)

    best_bookmaker = None
    for p in picks_sorted:
        if safe_float(p.get("odds"), 0.0) == best_odds:
            best_bookmaker = p.get("best_bookmaker")
            break

    return {
        "hub_key": hub_key,
        "generated_at": now_iso(),

        "event_key": main.get("event_key") or main.get("fixture_id"),
        "fixture_id": main.get("fixture_id") or main.get("event_key"),
        "date": main.get("date"),
        "time": main.get("time"),
        "match": main.get("match"),
        "bet": main.get("bet"),
        "bucket": main.get("bucket"),
        "side": normalize_side(main.get("side")),
        "market": main.get("market"),
        "line": safe_float(main.get("line"), 0.0),

        "best_odds": round(best_odds, 3),
        "best_bookmaker": best_bookmaker,
        "odds_by_machine": odds_by_machine,
        "bookmaker_by_machine": bookmaker_by_machine,

        "machines": machines_unique,
        "machine_count": machine_count,
        "consensus_level": consensus_level(machine_count),

        "confidence": best_numeric(picks_sorted, "confidence", 0.0),
        "quality_score": best_numeric(picks_sorted, "quality_score", 0.0),
        "edge": best_numeric(picks_sorted, "edge", 0.0),
        "confidence_by_machine": confidence_by_machine,
        "quality_by_machine": quality_by_machine,
        "edge_by_machine": edge_by_machine,

        "expected_total_games": main.get("expected_total_games"),
        "expected_margin": main.get("expected_margin"),
        "market_gap": get_market_gap(main),
        "strength_gap": get_strength_gap(main),
        "avg_three_set": get_avg_three_set(main),
        "avg_close_set": get_avg_close_set(main),

        "tour_level": main.get("tour_level"),
        "gender": main.get("gender"),
        "tournament": main.get("tournament"),
        "round": main.get("round"),
        "event_type": main.get("event_type"),

        "source_pick_ids": source_pick_ids,
        "source_picks": picks_sorted,
    }


def sort_hub_items(items):
    consensus_rank = {
        "quad": 4,
        "triple": 3,
        "double": 2,
        "single": 1,
    }

    return sorted(
        items,
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            -consensus_rank.get(x.get("consensus_level"), 0),
            str(x.get("match") or ""),
            str(x.get("side") or ""),
            safe_float(x.get("line"), 0.0),
        ),
    )


def machine_display(machines):
    names = {
        "jakob": "Jakob",
        "tedi_main": "Tedi",
        "tedi_v2": "Tedi V2",
        "lucija": "Lucija",
    }

    return " + ".join(names.get(m, m) for m in machines)


def build_table(items):
    lines = []

    lines.append("# Hana totals hub")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append("## Active unique picks")
    lines.append("")
    lines.append("| Date | Time | Match | Pick | Consensus | Machines | Best odds | Book | Conf | Quality | Edge | 3-set | Close | Gap | Strength |")
    lines.append("|---|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|")

    for item in items:
        lines.append(
            "| "
            f"{item.get('date', '')} | "
            f"{item.get('time', '')} | "
            f"{item.get('match', '')} | "
            f"{item.get('bet', '')} | "
            f"{item.get('consensus_level', '')} | "
            f"{machine_display(item.get('machines') or [])} | "
            f"{safe_float(item.get('best_odds'), 0.0):.2f} | "
            f"{item.get('best_bookmaker') or ''} | "
            f"{safe_float(item.get('confidence'), 0.0):.1f} | "
            f"{safe_float(item.get('quality_score'), 0.0):.1f} | "
            f"{safe_float(item.get('edge'), 0.0):.3f} | "
            f"{safe_float(item.get('avg_three_set'), 0.0):.3f} | "
            f"{safe_float(item.get('avg_close_set'), 0.0):.3f} | "
            f"{safe_float(item.get('market_gap'), 0.0):.3f} | "
            f"{safe_float(item.get('strength_gap'), 0.0):.2f} |"
        )

    lines.append("")
    lines.append("## Consensus summary")
    lines.append("")

    counts = {}
    for item in items:
        level = item.get("consensus_level") or "unknown"
        counts[level] = counts.get(level, 0) + 1

    lines.append("| Consensus | Count |")
    lines.append("|---|---:|")

    for level in ["quad", "triple", "double", "single", "unknown"]:
        if level in counts:
            lines.append(f"| {level} | {counts[level]} |")

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    grouped = {}
    debug_sources = []

    for source in SOURCES:
        machine = source["machine"]
        path = source["file"]

        raw = load_json(path, [])
        picks = extract_picks(raw)

        active = []
        rejected = 0

        for pick in picks:
            if not is_active_pick(pick):
                rejected += 1
                continue

            normalized = normalize_pick_for_machine(pick, machine)
            grouped.setdefault(normalized["_hana_hub_key"], []).append(normalized)
            active.append(normalized)

        debug_sources.append({
            "machine": machine,
            "file": path,
            "raw_picks": len(picks),
            "active_picks": len(active),
            "rejected_picks": rejected,
        })

    hub_items = []

    for hub_key, picks in grouped.items():
        hub_items.append(build_hub_item(hub_key, picks))

    hub_items = sort_hub_items(hub_items)

    debug = {
        "generated_at": now_iso(),
        "sources": debug_sources,
        "unique_hub_picks": len(hub_items),
        "raw_group_keys": len(grouped),
        "consensus_counts": {},
    }

    for item in hub_items:
        level = item.get("consensus_level") or "unknown"
        debug["consensus_counts"][level] = debug["consensus_counts"].get(level, 0) + 1

    payload = {
        "generated_at": now_iso(),
        "model": "Hana Totals Hub",
        "description": "Central overview of active totals picks from Jakob, Tedi, Tedi V2 and Lucija, deduped by event_key + side + line.",
        "dedupe_key": "event_key + side + line",
        "summary": {
            "unique_picks": len(hub_items),
            "consensus_counts": debug["consensus_counts"],
            "sources": debug_sources,
        },
        "picks": hub_items,
    }

    save_json(HANA_PREDICTIONS_FILE, payload)
    save_json(HANA_DEBUG_FILE, debug)
    save_text(HANA_TABLE_FILE, build_table(hub_items))

    print("")
    print("HANA DONE")
    print(f"Unique picks: {len(hub_items)}")
    print(f"Predictions file: {HANA_PREDICTIONS_FILE}")
    print(f"Table file: {HANA_TABLE_FILE}")
    print(f"Debug file: {HANA_DEBUG_FILE}")


if __name__ == "__main__":
    main()

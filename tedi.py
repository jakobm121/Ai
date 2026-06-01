import os
import json
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
TEDI_DIR = f"{DATA_DIR}/tedi"

SOURCE_PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_predictions.json"

TEDI_PREDICTIONS_FILE = f"{TEDI_DIR}/tedi_predictions.json"
TEDI_V2_TEST_FILE = f"{TEDI_DIR}/tedi_v2_test_predictions.json"
TEDI_RESULTS_FILE = f"{TEDI_DIR}/tedi_results.json"
TEDI_SUMMARY_FILE = f"{TEDI_DIR}/tedi_summary.json"
TEDI_TABLE_FILE = f"{TEDI_DIR}/tedi_table.md"
TEDI_DEBUG_FILE = f"{TEDI_DIR}/tedi_debug.json"

MODEL_VERSION = "tedi_v1"
MODEL_NAME = "Tedi Tennis Totals Filter v1"

FLAT_STAKE = 1.0


# Glavna Tedi formula iz min 150 backtesta.
TEDI_MAIN_RULES = {
    "side": "under",

    "line_min": 19.5,
    "line_max": 22.5,

    "avg_three_set_min": 0.15,
    "avg_three_set_max": 0.35,

    "strength_gap_min": 0,
    "strength_gap_max": 30,
}


# Testna V2 formula iz tvojega RULES_V2.
TEDI_V2_TEST_RULES = {
    "side": "under",

    "avg_close_set_max": 0.35,
    "avg_three_set_max": 0.35,

    "confidence_min": 80,
    "h2h_max": 0,
    "market_gap_min": 0.25,
    "quality_min": 72,
    "strength_gap_max": 30,
}


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


def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
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


def get_nested(data, keys, default=None):
    cur = data

    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)

    return cur if cur is not None else default


def avg_values(values, default=0.0):
    clean = []

    for value in values:
        if value is None or value == "":
            continue

        try:
            clean.append(float(value))
        except Exception:
            continue

    if not clean:
        return default

    return round(sum(clean) / len(clean), 4)


def extract_source_picks(raw_source):
    # Podpira obe obliki:
    # 1) [pick, pick, ...]
    # 2) {"generated_at": "...", "summary": {...}, "picks": [pick, pick, ...]}
    if isinstance(raw_source, dict):
        picks = raw_source.get("picks", [])
    elif isinstance(raw_source, list):
        picks = raw_source
    else:
        picks = []

    return picks if isinstance(picks, list) else []


def source_format(raw_source):
    if isinstance(raw_source, dict):
        return "dict_with_picks"
    if isinstance(raw_source, list):
        return "list"
    return type(raw_source).__name__


def calc_strength_gap(pick):
    direct = safe_float(pick.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)

    first_strength = safe_float(pick.get("first_strength_score"), None)
    second_strength = safe_float(pick.get("second_strength_score"), None)

    if first_strength is None or second_strength is None:
        return 999.0

    return abs(first_strength - second_strength)


def tedi_metrics(pick):
    first_three = get_nested(pick, ["first_form", "last_10", "three_set_rate"], None)
    second_three = get_nested(pick, ["second_form", "last_10", "three_set_rate"], None)

    first_close = get_nested(pick, ["first_form", "last_10", "close_set_rate"], None)
    second_close = get_nested(pick, ["second_form", "last_10", "close_set_rate"], None)

    first_total = get_nested(pick, ["first_form", "last_10", "avg_total_games"], None)
    second_total = get_nested(pick, ["second_form", "last_10", "avg_total_games"], None)

    first_over_21 = get_nested(pick, ["first_form", "last_10", "over_21_5_rate"], None)
    second_over_21 = get_nested(pick, ["second_form", "last_10", "over_21_5_rate"], None)

    avg_three_set = avg_values([first_three, second_three])
    avg_close_set = avg_values([first_close, second_close])
    avg_total_games = avg_values([first_total, second_total])
    avg_over_21_5_rate = avg_values([first_over_21, second_over_21])

    market_gap = safe_float(get_nested(pick, ["market_info", "market_gap"], 0.0), 0.0)

    return {
        "side": normalize_text(pick.get("side")),
        "line": round(safe_float(pick.get("line"), 0.0), 4),
        "odds": round(safe_float(pick.get("odds"), 0.0), 4),

        "avg_three_set": round(avg_three_set, 4),
        "avg_close_set": round(avg_close_set, 4),
        "avg_total_games": round(avg_total_games, 4),
        "avg_over_21_5_rate": round(avg_over_21_5_rate, 4),

        "market_gap": round(market_gap, 4),
        "confidence": round(safe_float(pick.get("confidence"), 0.0), 4),
        "quality_score": round(safe_float(pick.get("quality_score"), 0.0), 4),
        "edge": round(safe_float(pick.get("edge"), 0.0), 4),

        "strength_gap": round(calc_strength_gap(pick), 4),
        "h2h_matches": safe_int(pick.get("h2h_matches"), 999),
        "bookmakers_used": safe_int(pick.get("bookmakers_used"), 0),

        "tour_level": normalize_text(pick.get("tour_level")),
        "gender": normalize_text(pick.get("gender")),
    }


def check_main_rules(metrics):
    r = TEDI_MAIN_RULES

    checks = {
        "side": metrics["side"] == r["side"],

        "line_min": metrics["line"] >= r["line_min"],
        "line_max": metrics["line"] <= r["line_max"],

        "avg_three_set_min": metrics["avg_three_set"] >= r["avg_three_set_min"],
        "avg_three_set_max": metrics["avg_three_set"] <= r["avg_three_set_max"],

        "strength_gap_min": metrics["strength_gap"] >= r["strength_gap_min"],
        "strength_gap_max": metrics["strength_gap"] <= r["strength_gap_max"],
    }

    return all(checks.values()), checks


def check_v2_test_rules(metrics):
    r = TEDI_V2_TEST_RULES

    checks = {
        "side": metrics["side"] == r["side"],

        "avg_close_set_max": metrics["avg_close_set"] <= r["avg_close_set_max"],
        "avg_three_set_max": metrics["avg_three_set"] <= r["avg_three_set_max"],

        "confidence_min": metrics["confidence"] >= r["confidence_min"],
        "h2h_max": metrics["h2h_matches"] <= r["h2h_max"],
        "market_gap_min": metrics["market_gap"] >= r["market_gap_min"],
        "quality_min": metrics["quality_score"] >= r["quality_min"],
        "strength_gap_max": metrics["strength_gap"] <= r["strength_gap_max"],
    }

    return all(checks.values()), checks


def failed_checks(checks):
    return [key for key, passed in checks.items() if not passed]


def build_tedi_pick_id(source_pick, strategy):
    raw = "|".join([
        str(source_pick.get("event_key") or source_pick.get("fixture_id") or ""),
        str(source_pick.get("market") or ""),
        str(source_pick.get("side") or ""),
        str(source_pick.get("line") or ""),
        str(source_pick.get("odds") or ""),
        strategy,
        MODEL_VERSION,
    ])

    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def normalize_pick(source_pick, strategy, metrics, checks):
    pick = dict(source_pick)

    original_pick_id = pick.get("pick_id")

    pick["source_pick_id"] = original_pick_id
    pick["pick_id"] = build_tedi_pick_id(source_pick, strategy)

    pick["model_version"] = MODEL_VERSION
    pick["model_name"] = MODEL_NAME

    pick["tedi_strategy"] = strategy
    pick["tedi_rules"] = TEDI_MAIN_RULES if strategy == "tedi_main_150" else TEDI_V2_TEST_RULES
    pick["tedi_metrics"] = metrics
    pick["tedi_checks"] = checks

    pick["stake"] = FLAT_STAKE
    pick["stake_label"] = "flat"

    pick["result"] = "pending"
    pick["profit"] = None

    pick["created_at"] = now_iso()

    if strategy == "tedi_main_150":
        pick["reasoning"] = (
            f"Tedi selected {pick.get('bet')} in {pick.get('match')} using MAIN 150 rule: "
            f"side under, line {TEDI_MAIN_RULES['line_min']}–{TEDI_MAIN_RULES['line_max']}, "
            f"avg_three_set {TEDI_MAIN_RULES['avg_three_set_min']}–{TEDI_MAIN_RULES['avg_three_set_max']}, "
            f"strength_gap <= {TEDI_MAIN_RULES['strength_gap_max']}."
        )
    else:
        pick["reasoning"] = (
            f"Tedi V2 TEST selected {pick.get('bet')} in {pick.get('match')} using V2 test rule: "
            f"side under, avg_close_set <= {TEDI_V2_TEST_RULES['avg_close_set_max']}, "
            f"avg_three_set <= {TEDI_V2_TEST_RULES['avg_three_set_max']}, "
            f"confidence >= {TEDI_V2_TEST_RULES['confidence_min']}, "
            f"quality >= {TEDI_V2_TEST_RULES['quality_min']}, "
            f"market_gap >= {TEDI_V2_TEST_RULES['market_gap_min']}, "
            f"strength_gap <= {TEDI_V2_TEST_RULES['strength_gap_max']}, "
            f"h2h <= {TEDI_V2_TEST_RULES['h2h_max']}."
        )

    return pick


def unique_by_pick_id(picks):
    seen = set()
    out = []

    for pick in picks:
        if not isinstance(pick, dict):
            continue

        pid = pick.get("pick_id")
        if not pid or pid in seen:
            continue

        seen.add(pid)
        out.append(pick)

    return out


def result_key(pick):
    return "|".join([
        str(pick.get("event_key") or pick.get("fixture_id") or ""),
        str(pick.get("market") or ""),
        str(pick.get("side") or ""),
        str(pick.get("line") or ""),
        str(pick.get("tedi_strategy") or ""),
    ])


def merge_into_results(existing_results, new_predictions):
    existing_by_key = {}

    for item in existing_results:
        if not isinstance(item, dict):
            continue

        key = item.get("tedi_result_key") or result_key(item)
        item["tedi_result_key"] = key
        existing_by_key[key] = item

    for pick in new_predictions:
        key = result_key(pick)
        pick["tedi_result_key"] = key

        if key not in existing_by_key:
            existing_by_key[key] = dict(pick)
            continue

        old = existing_by_key[key]
        old_result = normalize_result(old.get("result"))

        # Če je star pick že settled, ga ne prepišemo s pending.
        if old_result in {"win", "loss", "push"}:
            continue

        created_at = old.get("created_at") or pick.get("created_at")
        old.update(pick)
        old["created_at"] = created_at

    return list(existing_by_key.values())


def count_by(picks, field):
    out = {}

    for p in picks:
        value = str(p.get(field) or "unknown").lower()
        out[value] = out.get(value, 0) + 1

    return out


def build_summary(source_count, raw_type, main_predictions, v2_predictions, rejected):
    return {
        "generated_at": now_iso(),
        "model_version": MODEL_VERSION,
        "model_name": MODEL_NAME,
        "source_file": SOURCE_PREDICTIONS_FILE,
        "source_format": raw_type,
        "source_picks": source_count,

        "main_strategy": "tedi_main_150",
        "main_rules": TEDI_MAIN_RULES,
        "main_picks": len(main_predictions),

        "v2_test_strategy": "tedi_v2_test",
        "v2_test_rules": TEDI_V2_TEST_RULES,
        "v2_test_picks": len(v2_predictions),

        "rejected_picks": len(rejected),
        "stake": FLAT_STAKE,

        "main_sides": count_by(main_predictions, "side"),
        "v2_test_sides": count_by(v2_predictions, "side"),
    }


def build_table(title, predictions):
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append("| Date | Time | Strategy | Match | Bet | Odds | Line | Conf | Quality | Gap | Strength | Avg 3-set | Avg close | Book |")
    lines.append("|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    sorted_picks = sorted(
        predictions,
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
            str(x.get("tedi_strategy") or ""),
        )
    )

    for p in sorted_picks:
        m = p.get("tedi_metrics") or {}

        lines.append(
            "| "
            f"{p.get('date', '')} | "
            f"{p.get('time', '')} | "
            f"{p.get('tedi_strategy', '')} | "
            f"{p.get('match', '')} | "
            f"{p.get('bet', '')} | "
            f"{safe_float(p.get('odds')):.2f} | "
            f"{safe_float(p.get('line')):.1f} | "
            f"{safe_float(m.get('confidence')):.1f} | "
            f"{safe_float(m.get('quality_score')):.1f} | "
            f"{safe_float(m.get('market_gap')):.3f} | "
            f"{safe_float(m.get('strength_gap')):.2f} | "
            f"{safe_float(m.get('avg_three_set')):.3f} | "
            f"{safe_float(m.get('avg_close_set')):.3f} | "
            f"{p.get('best_bookmaker', '')} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    raw_source = load_json(SOURCE_PREDICTIONS_FILE, [])
    raw_type = source_format(raw_source)
    source_predictions = extract_source_picks(raw_source)

    main_predictions = []
    v2_test_predictions = []
    rejected = []

    for source_pick in source_predictions:
        if not isinstance(source_pick, dict):
            continue

        metrics = tedi_metrics(source_pick)

        main_ok, main_checks = check_main_rules(metrics)
        v2_ok, v2_checks = check_v2_test_rules(metrics)

        if main_ok:
            main_predictions.append(
                normalize_pick(
                    source_pick=source_pick,
                    strategy="tedi_main_150",
                    metrics=metrics,
                    checks=main_checks,
                )
            )

        if v2_ok:
            v2_test_predictions.append(
                normalize_pick(
                    source_pick=source_pick,
                    strategy="tedi_v2_test",
                    metrics=metrics,
                    checks=v2_checks,
                )
            )

        if not main_ok and not v2_ok:
            rejected.append({
                "source_pick_id": source_pick.get("pick_id"),
                "match": source_pick.get("match"),
                "bet": source_pick.get("bet"),
                "date": source_pick.get("date"),
                "time": source_pick.get("time"),
                "odds": source_pick.get("odds"),
                "metrics": metrics,
                "main_failed": failed_checks(main_checks),
                "v2_failed": failed_checks(v2_checks),
            })

    main_predictions = unique_by_pick_id(main_predictions)
    v2_test_predictions = unique_by_pick_id(v2_test_predictions)

    existing_results = load_json(TEDI_RESULTS_FILE, [])
    if not isinstance(existing_results, list):
        existing_results = []

    merged_results = merge_into_results(existing_results, main_predictions + v2_test_predictions)

    summary = build_summary(
        source_count=len(source_predictions),
        raw_type=raw_type,
        main_predictions=main_predictions,
        v2_predictions=v2_test_predictions,
        rejected=rejected,
    )

    debug = {
        "generated_at": now_iso(),
        "source_file": SOURCE_PREDICTIONS_FILE,
        "source_format": raw_type,
        "source_picks": len(source_predictions),

        "main_picks": len(main_predictions),
        "v2_test_picks": len(v2_test_predictions),
        "rejected_picks": len(rejected),

        "main_rules": TEDI_MAIN_RULES,
        "v2_test_rules": TEDI_V2_TEST_RULES,

        "accepted_main": [
            {
                "pick_id": p.get("pick_id"),
                "source_pick_id": p.get("source_pick_id"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "metrics": p.get("tedi_metrics"),
            }
            for p in main_predictions
        ],

        "accepted_v2_test": [
            {
                "pick_id": p.get("pick_id"),
                "source_pick_id": p.get("source_pick_id"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "metrics": p.get("tedi_metrics"),
            }
            for p in v2_test_predictions
        ],

        "rejected": rejected[:1000],
    }

    table = build_table("Tedi active predictions", main_predictions + v2_test_predictions)

    save_json(TEDI_PREDICTIONS_FILE, main_predictions)
    save_json(TEDI_V2_TEST_FILE, v2_test_predictions)
    save_json(TEDI_RESULTS_FILE, merged_results)
    save_json(TEDI_SUMMARY_FILE, summary)
    save_json(TEDI_DEBUG_FILE, debug)
    save_text(TEDI_TABLE_FILE, table)

    print("")
    print("TEDI DONE")
    print(f"Source format: {raw_type}")
    print(f"Source picks: {len(source_predictions)}")
    print(f"Tedi main picks: {len(main_predictions)}")
    print(f"Tedi V2 test picks: {len(v2_test_predictions)}")
    print(f"Rejected picks: {len(rejected)}")
    print(f"Predictions file: {TEDI_PREDICTIONS_FILE}")
    print(f"V2 test file: {TEDI_V2_TEST_FILE}")
    print(f"Results file: {TEDI_RESULTS_FILE}")
    print(f"Summary file: {TEDI_SUMMARY_FILE}")
    print(f"Debug file: {TEDI_DEBUG_FILE}")
    print(f"Table file: {TEDI_TABLE_FILE}")


if __name__ == "__main__":
    main()

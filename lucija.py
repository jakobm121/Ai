import os
import json
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
LUCIJA_DIR = f"{DATA_DIR}/lucija"

SOURCE_PREDICTIONS_FILE = f"{DATA_DIR}/tennis_totals_predictions.json"

LUCIJA_PREDICTIONS_FILE = f"{LUCIJA_DIR}/lucija_predictions.json"
LUCIJA_RESULTS_FILE = f"{LUCIJA_DIR}/lucija_results.json"
LUCIJA_SUMMARY_FILE = f"{LUCIJA_DIR}/lucija_summary.json"
LUCIJA_TABLE_FILE = f"{LUCIJA_DIR}/lucija_table.md"
LUCIJA_DEBUG_FILE = f"{LUCIJA_DIR}/lucija_debug.json"

MODEL_VERSION = "lucija_v1"
MODEL_NAME = "Lucija Tennis Totals Filter v1"

# Best optimizer rule:
# score 313.7786
# Full: picks 72, winrate 74.29%, profit 35.69u, ROI 50.99%, max DD -2.0u
# Test: picks 19, profit 13.15u, ROI 69.21%
RULES = {
    "avg_close_set_max": 0.55,
    "avg_close_set_min": 0.20,
    "avg_three_set_min": 0.15,
    "confidence_min": 80,
    "h2h_max": 0,
    "market_gap_min": 0.25,
    "quality_min": 72,
    "strength_gap_max": 30,
}

FLAT_STAKE = 1.0


def ensure_dirs():
    os.makedirs(LUCIJA_DIR, exist_ok=True)


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


def build_lucija_pick_id(pick):
    raw = "|".join([
        str(pick.get("event_key") or pick.get("fixture_id") or ""),
        str(pick.get("market") or ""),
        str(pick.get("side") or ""),
        str(pick.get("line") or ""),
        str(pick.get("odds") or ""),
        MODEL_VERSION,
    ])
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def lucija_metrics(pick):
    # Lucija ne dela nove tennis logike.
    # Samo mapira obstoječe podatke iz tennis_totals_predictions.json
    # v imena, ki jih uporablja optimizer rule.
    three_values = [
        get_nested(pick, ["first_form", "last_10", "three_set_rate"], None),
        get_nested(pick, ["second_form", "last_10", "three_set_rate"], None),
    ]

    close_values = [
        get_nested(pick, ["first_form", "last_10", "close_set_rate"], None),
        get_nested(pick, ["second_form", "last_10", "close_set_rate"], None),
    ]

    avg_three_set = avg_values(three_values)
    avg_close_set = avg_values(close_values)

    market_gap = safe_float(get_nested(pick, ["market_info", "market_gap"], 0.0), 0.0)
    confidence = safe_float(pick.get("confidence"), 0.0)
    quality_score = safe_float(pick.get("quality_score"), 0.0)

    strength_gap = safe_float(pick.get("strength_gap"), None)
    if strength_gap is None:
        first_strength = safe_float(pick.get("first_strength_score"), None)
        second_strength = safe_float(pick.get("second_strength_score"), None)
        if first_strength is not None and second_strength is not None:
            strength_gap = abs(first_strength - second_strength)
        else:
            # Če ni podatka, pick ne sme skozi strength_gap <= 30.
            strength_gap = 999.0

    h2h_matches = safe_int(pick.get("h2h_matches"), 999)

    return {
        "avg_three_set": round(avg_three_set, 4),
        "avg_close_set": round(avg_close_set, 4),
        "market_gap": round(market_gap, 4),
        "confidence": round(confidence, 4),
        "quality_score": round(quality_score, 4),
        "strength_gap": round(abs(strength_gap), 4),
        "h2h_matches": h2h_matches,
    }


def passes_lucija_rules(pick):
    m = lucija_metrics(pick)
    checks = {
        "avg_three_set_min": m["avg_three_set"] >= RULES["avg_three_set_min"],
        "avg_close_set_min": m["avg_close_set"] >= RULES["avg_close_set_min"],
        "avg_close_set_max": m["avg_close_set"] <= RULES["avg_close_set_max"],
        "confidence_min": m["confidence"] >= RULES["confidence_min"],
        "quality_min": m["quality_score"] >= RULES["quality_min"],
        "market_gap_min": m["market_gap"] >= RULES["market_gap_min"],
        "strength_gap_max": m["strength_gap"] <= RULES["strength_gap_max"],
        "h2h_max": m["h2h_matches"] <= RULES["h2h_max"],
    }
    return all(checks.values()), m, checks


def normalize_pick(source_pick):
    ok, metrics, checks = passes_lucija_rules(source_pick)
    if not ok:
        return None, metrics, checks

    pick = dict(source_pick)
    original_pick_id = pick.get("pick_id")

    pick["source_pick_id"] = original_pick_id
    pick["pick_id"] = build_lucija_pick_id(pick)
    pick["model_version"] = MODEL_VERSION
    pick["model_name"] = MODEL_NAME
    pick["lucija_rules"] = RULES
    pick["lucija_metrics"] = metrics
    pick["lucija_checks"] = checks
    pick["stake"] = FLAT_STAKE
    pick["stake_label"] = "flat"

    # Lucija agregator samo naredi active picke. Settle naj dela ločena skripta.
    pick["result"] = "pending"
    pick["profit"] = None
    pick["created_at"] = now_iso()

    pick["reasoning"] = (
        f"Lucija selected {pick.get('bet')} in {pick.get('match')} "
        f"using optimizer rule: confidence >= {RULES['confidence_min']}, "
        f"quality >= {RULES['quality_min']}, market_gap >= {RULES['market_gap_min']}, "
        f"strength_gap <= {RULES['strength_gap_max']}, h2h <= {RULES['h2h_max']}, "
        f"avg_three_set >= {RULES['avg_three_set_min']}, "
        f"avg_close_set between {RULES['avg_close_set_min']} and {RULES['avg_close_set_max']}."
    )

    return pick, metrics, checks


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


def merge_into_results(existing_results, new_predictions):
    existing_by_id = {
        x.get("pick_id"): x
        for x in existing_results
        if isinstance(x, dict) and x.get("pick_id")
    }

    for pick in new_predictions:
        pid = pick.get("pick_id")
        if not pid:
            continue

        if pid not in existing_by_id:
            existing_results.append(dict(pick))
            continue

        # Če je obstoječi pick že settled, ga ne prepisujemo s pending.
        old = existing_by_id[pid]
        old_result = str(old.get("result") or "").lower()
        if old_result in {"win", "won", "loss", "lost", "push", "void"}:
            continue

        # Če še ni settled, lahko osvežimo odds/metadata, ampak ohranimo created_at.
        created_at = old.get("created_at") or pick.get("created_at")
        old.update(pick)
        old["created_at"] = created_at

    return unique_by_pick_id(existing_results)


def build_summary(predictions, source_count, raw_type, rejected_count):
    sides = {}
    for p in predictions:
        side = str(p.get("side") or "unknown").lower()
        sides[side] = sides.get(side, 0) + 1

    return {
        "generated_at": now_iso(),
        "model_version": MODEL_VERSION,
        "model_name": MODEL_NAME,
        "source_file": SOURCE_PREDICTIONS_FILE,
        "source_format": raw_type,
        "source_picks": source_count,
        "lucija_picks": len(predictions),
        "rejected_picks": rejected_count,
        "rules": RULES,
        "stake": FLAT_STAKE,
        "sides": sides,
    }


def build_table(predictions):
    lines = []
    lines.append("# Lucija active predictions")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append("")
    lines.append("| Date | Time | Match | Bet | Odds | Stake | Conf | Quality | Gap | Strength gap | H2H | Avg 3-set | Avg close | Book |")
    lines.append("|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    sorted_picks = sorted(
        predictions,
        key=lambda x: (
            str(x.get("date") or ""),
            str(x.get("time") or ""),
            str(x.get("match") or ""),
        )
    )

    for p in sorted_picks:
        m = p.get("lucija_metrics") or {}
        lines.append(
            "| "
            f"{p.get('date', '')} | "
            f"{p.get('time', '')} | "
            f"{p.get('match', '')} | "
            f"{p.get('bet', '')} | "
            f"{safe_float(p.get('odds')):.2f} | "
            f"{safe_float(p.get('stake')):.2f} | "
            f"{safe_float(p.get('confidence')):.1f} | "
            f"{safe_float(p.get('quality_score')):.1f} | "
            f"{safe_float(m.get('market_gap')):.3f} | "
            f"{safe_float(m.get('strength_gap')):.2f} | "
            f"{safe_int(m.get('h2h_matches'))} | "
            f"{safe_float(m.get('avg_three_set')):.3f} | "
            f"{safe_float(m.get('avg_close_set')):.3f} | "
            f"{p.get('best_bookmaker', '')} |"
        )

    lines.append("")
    return "\n".join(lines)


def failed_checks(checks):
    return [key for key, passed in checks.items() if not passed]


def main():
    ensure_dirs()

    raw_source = load_json(SOURCE_PREDICTIONS_FILE, [])
    source_predictions = extract_source_picks(raw_source)

    if isinstance(raw_source, dict):
        raw_type = "dict_with_picks"
    elif isinstance(raw_source, list):
        raw_type = "list"
    else:
        raw_type = type(raw_source).__name__

    lucija_predictions = []
    rejected = []

    for source_pick in source_predictions:
        if not isinstance(source_pick, dict):
            continue

        lucija_pick, metrics, checks = normalize_pick(source_pick)
        if lucija_pick:
            lucija_predictions.append(lucija_pick)
        else:
            rejected.append({
                "pick_id": source_pick.get("pick_id"),
                "match": source_pick.get("match"),
                "bet": source_pick.get("bet"),
                "date": source_pick.get("date"),
                "time": source_pick.get("time"),
                "odds": source_pick.get("odds"),
                "confidence": source_pick.get("confidence"),
                "quality_score": source_pick.get("quality_score"),
                "metrics": metrics,
                "checks": checks,
                "failed": failed_checks(checks),
            })

    lucija_predictions = unique_by_pick_id(lucija_predictions)

    existing_results = load_json(LUCIJA_RESULTS_FILE, [])
    if not isinstance(existing_results, list):
        existing_results = []

    merged_results = merge_into_results(existing_results, lucija_predictions)

    summary = build_summary(
        predictions=lucija_predictions,
        source_count=len(source_predictions),
        raw_type=raw_type,
        rejected_count=len(rejected),
    )
    table = build_table(lucija_predictions)

    debug = {
        "generated_at": now_iso(),
        "source_file": SOURCE_PREDICTIONS_FILE,
        "source_format": raw_type,
        "source_picks": len(source_predictions),
        "lucija_picks": len(lucija_predictions),
        "rejected_picks": len(rejected),
        "rules": RULES,
        "accepted": [
            {
                "pick_id": p.get("pick_id"),
                "source_pick_id": p.get("source_pick_id"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "odds": p.get("odds"),
                "metrics": p.get("lucija_metrics"),
            }
            for p in lucija_predictions
        ],
        "rejected": rejected,
    }

    save_json(LUCIJA_PREDICTIONS_FILE, lucija_predictions)
    save_json(LUCIJA_RESULTS_FILE, merged_results)
    save_json(LUCIJA_SUMMARY_FILE, summary)
    save_json(LUCIJA_DEBUG_FILE, debug)
    save_text(LUCIJA_TABLE_FILE, table)

    print("")
    print("LUCIJA DONE")
    print(f"Source format: {raw_type}")
    print(f"Source picks: {len(source_predictions)}")
    print(f"Lucija picks: {len(lucija_predictions)}")
    print(f"Rejected picks: {len(rejected)}")
    print(f"Predictions file: {LUCIJA_PREDICTIONS_FILE}")
    print(f"Results file: {LUCIJA_RESULTS_FILE}")
    print(f"Summary file: {LUCIJA_SUMMARY_FILE}")
    print(f"Debug file: {LUCIJA_DEBUG_FILE}")
    print(f"Table file: {LUCIJA_TABLE_FILE}")


if __name__ == "__main__":
    main()

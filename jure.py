import os
import json
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = os.getenv("DATA_DIR", "data")
OUTPUT_DIR = os.getenv("JURE_DIR", "jure")

PREDICTIONS_FILE = os.getenv("TENNIS_PREDICTIONS_FILE", f"{DATA_DIR}/tennis_predictions.json")
MAIN_RESULTS_FILE = os.getenv("TENNIS_RESULTS_FILE", f"{DATA_DIR}/tennis_results.json")

ACTIVE_FILE = f"{OUTPUT_DIR}/jure_predictions.json"
ACTIVE_MD_FILE = f"{OUTPUT_DIR}/jure_active.md"
RESULTS_FILE = f"{OUTPUT_DIR}/jure_results.json"
SUMMARY_FILE = f"{OUTPUT_DIR}/jure_summary.json"
DEBUG_FILE = f"{OUTPUT_DIR}/jure_debug.json"

# Taktika A = strožja taktika iz optimizerja.
TACTIC_A = {
    "tour_level": "challenger",
    "bookmakers_min": 6,
    "confidence_max": 88,
    "edge_max": 0.20,
}

# Taktika B = širša taktika iz optimizerja.
TACTIC_B = {
    "odds_min": 1.75,
    "quality_max": 90,
    "edge_max": 0.15,
}

STAKE_A = float(os.getenv("JURE_STAKE_A", "0.75"))
STAKE_B = float(os.getenv("JURE_STAKE_B", "0.50"))

# Če pick pade v A in B, ga obdržimo samo enkrat kot A+B s stake A.
TACTIC_PRIORITY = ["A+B", "A", "B"]


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


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


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
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


def is_settled(pick):
    return normalize_result(pick.get("result")) in {"win", "loss", "push"}


def side_value(pick):
    raw = normalize_text(pick.get("side") or pick.get("pick") or pick.get("selection"))
    if raw in {"home", "first", "1", "first_player", "player1"}:
        return "home"
    if raw in {"away", "second", "2", "second_player", "player2"}:
        return "away"

    bet = normalize_text(pick.get("bet"))
    first = normalize_text(pick.get("first_player_name"))
    second = normalize_text(pick.get("second_player_name"))
    if first and first in bet:
        return "home"
    if second and second in bet:
        return "away"
    return raw or None


def is_home_away_pick(pick):
    side = side_value(pick)
    if side not in {"home", "away"}:
        return False

    market = normalize_text(pick.get("market"))
    bet = normalize_text(pick.get("bet"))

    bad_words = [
        "over/under",
        "total",
        "games in match",
        "number of sets",
        "odd/even",
        "asian handicap",
        "correct score",
        "set betting",
    ]
    if any(w in market for w in bad_words):
        return False
    if bet.startswith("over ") or bet.startswith("under "):
        return False

    if not market:
        return True
    return "home/away" in market or market in {"winner", "match winner"}


def market_gap(pick):
    info = pick.get("market_info") if isinstance(pick.get("market_info"), dict) else {}
    gap = safe_float(info.get("market_gap"), None)
    if gap is not None:
        return gap
    home = safe_float(info.get("home_implied"), None)
    away = safe_float(info.get("away_implied"), None)
    if home is not None and away is not None:
        return abs(home - away)
    return None


def feature_value(pick, name):
    if name == "tour_level":
        return normalize_text(pick.get("tour_level")) or None
    if name == "gender":
        return normalize_text(pick.get("gender")) or None
    if name == "qualification":
        return pick.get("qualification") if isinstance(pick.get("qualification"), bool) else None
    if name == "bookmakers":
        return safe_int(pick.get("bookmakers_used"), None)
    if name == "confidence":
        return safe_float(pick.get("confidence"), None)
    if name == "quality":
        return safe_float(pick.get("quality_score"), None)
    if name == "edge":
        return safe_float(pick.get("edge"), None)
    if name == "odds":
        return safe_float(pick.get("odds"), None)
    if name == "market_gap":
        return market_gap(pick)
    if name == "strength_gap":
        return safe_float(pick.get("strength_gap"), None)
    if name == "h2h":
        return safe_int(pick.get("h2h_matches"), None)
    if name == "side":
        return side_value(pick)
    return None


def passes_tactic_a(pick):
    if feature_value(pick, "tour_level") != TACTIC_A["tour_level"]:
        return False
    bookmakers = feature_value(pick, "bookmakers")
    confidence = feature_value(pick, "confidence")
    edge = feature_value(pick, "edge")
    if bookmakers is None or bookmakers < TACTIC_A["bookmakers_min"]:
        return False
    if confidence is None or confidence > TACTIC_A["confidence_max"]:
        return False
    if edge is None or edge > TACTIC_A["edge_max"]:
        return False
    return True


def passes_tactic_b(pick):
    odds = feature_value(pick, "odds")
    quality = feature_value(pick, "quality")
    edge = feature_value(pick, "edge")
    if odds is None or odds < TACTIC_B["odds_min"]:
        return False
    if quality is None or quality > TACTIC_B["quality_max"]:
        return False
    if edge is None or edge > TACTIC_B["edge_max"]:
        return False
    return True


def tactic_label(pick):
    a = passes_tactic_a(pick)
    b = passes_tactic_b(pick)
    if a and b:
        return "A+B"
    if a:
        return "A"
    if b:
        return "B"
    return None


def stake_for_label(label):
    if label in {"A", "A+B"}:
        return STAKE_A
    if label == "B":
        return STAKE_B
    return 0.0


def profit_for_pick(pick, stake=None):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), None)
    if stake is None:
        stake = safe_float(pick.get("stake"), 0.0) or 0.0
    if result == "win":
        return round(stake * ((odds or 1.0) - 1.0), 4)
    if result == "loss":
        return round(-stake, 4)
    return 0.0


def selection_key(pick):
    fixture = pick.get("fixture_id") or pick.get("event_key") or pick.get("id") or pick.get("match") or ""
    side = side_value(pick) or normalize_text(pick.get("bet"))
    market = normalize_text(pick.get("market") or "home/away")
    raw = f"{fixture}|{market}|{side}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def result_match_key(pick):
    fixture = pick.get("fixture_id") or pick.get("event_key") or pick.get("id") or pick.get("match") or ""
    side = side_value(pick) or normalize_text(pick.get("bet"))
    return f"{fixture}|{side}"


def prepare_pick(pick, label):
    p = dict(pick)
    p["jure_key"] = selection_key(p)
    p["jure_result_key"] = result_match_key(p)
    p["jure_tactic"] = label
    p["stake"] = stake_for_label(label)
    p["stake_label"] = "Jure A" if label in {"A", "A+B"} else "Jure B"
    p["result"] = normalize_result(p.get("result")) if p.get("result") else "pending"
    p["profit"] = profit_for_pick(p, p["stake"]) if is_settled(p) else 0.0
    p["created_by"] = "jure.py"
    p["jure_created_at"] = p.get("jure_created_at") or now_iso()
    return p


def priority_index(label):
    try:
        return TACTIC_PRIORITY.index(label)
    except ValueError:
        return 99


def merge_unique(existing, incoming):
    by_key = {}
    for p in existing:
        if not isinstance(p, dict):
            continue
        key = p.get("jure_key") or selection_key(p)
        x = dict(p)
        x["jure_key"] = key
        x["jure_result_key"] = x.get("jure_result_key") or result_match_key(x)
        by_key[key] = x

    for p in incoming:
        key = p.get("jure_key") or selection_key(p)
        if key not in by_key:
            by_key[key] = p
            continue
        old = by_key[key]
        if is_settled(old) and not is_settled(p):
            continue
        old_label = old.get("jure_tactic")
        new_label = p.get("jure_tactic")
        if priority_index(new_label) < priority_index(old_label):
            merged = dict(old)
            merged.update(p)
            merged["jure_created_at"] = old.get("jure_created_at") or p.get("jure_created_at")
            by_key[key] = merged
    return list(by_key.values())


def settle_from_main_results(jure_picks, main_results):
    result_index = {}
    for r in main_results:
        if not isinstance(r, dict):
            continue
        if not is_home_away_pick(r):
            continue
        result_index[result_match_key(r)] = r

    settled = []
    still_pending = []
    for p in jure_picks:
        x = dict(p)
        key = x.get("jure_result_key") or result_match_key(x)
        main = result_index.get(key)
        if main and is_settled(main):
            for field in ["result", "settled_at", "settled_status", "event_winner", "final_score", "winner", "score"]:
                if field in main:
                    x[field] = main[field]
            x["result"] = normalize_result(x.get("result"))
            x["profit"] = profit_for_pick(x, safe_float(x.get("stake"), 0.0) or 0.0)
            x["jure_settled_from"] = MAIN_RESULTS_FILE
            x["jure_settled_at"] = x.get("jure_settled_at") or now_iso()
            settled.append(x)
        else:
            still_pending.append(x)
    return settled, still_pending


def sort_pick_key(p):
    return (str(p.get("date") or ""), str(p.get("time") or ""), str(p.get("match") or ""), str(p.get("jure_key") or ""))


def evaluate(picks):
    settled = [p for p in picks if is_settled(p)]
    wins = [p for p in settled if normalize_result(p.get("result")) == "win"]
    losses = [p for p in settled if normalize_result(p.get("result")) == "loss"]
    pushes = [p for p in settled if normalize_result(p.get("result")) == "push"]
    stake_sum = sum(safe_float(p.get("stake"), 0.0) or 0.0 for p in settled)
    profit = round(sum(safe_float(p.get("profit"), 0.0) or 0.0 for p in settled), 4)
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


def group_stats(picks, field):
    groups = {}
    for p in picks:
        value = p.get(field)
        if value is None or value == "":
            value = "unknown"
        groups.setdefault(str(value), []).append(p)
    return {key: evaluate(items) for key, items in sorted(groups.items())}


def make_active_md(active, summary):
    lines = []
    lines.append("# Jure active tennis picks")
    lines.append("")
    lines.append(f"Generated at: **{summary['generated_at']}**")
    lines.append("")
    lines.append(f"Active picks: **{len(active)}**")
    lines.append("")
    if not active:
        lines.append("No active Jure picks.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Date | Time | Tactic | Stake | Match | Bet | Odds | Book | Conf | Quality | Edge |")
    lines.append("|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|")
    for p in sorted(active, key=sort_pick_key):
        lines.append(
            f"| {p.get('date','')} | {p.get('time','')} | {p.get('jure_tactic','')} | "
            f"{p.get('stake','')} | {p.get('match','')} | {p.get('bet') or side_value(p) or ''} | "
            f"{p.get('odds','')} | {p.get('best_bookmaker','')} | {p.get('confidence','')} | "
            f"{p.get('quality_score','')} | {p.get('edge','')} |"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()
    predictions = load_json(PREDICTIONS_FILE, [])
    main_results = load_json(MAIN_RESULTS_FILE, [])
    previous_results = load_json(RESULTS_FILE, [])

    accepted = []
    rejected = []
    for pick in predictions:
        if not isinstance(pick, dict):
            continue
        reason = None
        if not is_home_away_pick(pick):
            reason = "not_home_away"
        else:
            label = tactic_label(pick)
            if label:
                accepted.append(prepare_pick(pick, label))
            else:
                reason = "failed_tactics"
        if reason:
            rejected.append({
                "reason": reason,
                "match": pick.get("match"),
                "bet": pick.get("bet"),
                "side": pick.get("side"),
                "market": pick.get("market"),
                "tour_level": pick.get("tour_level"),
                "bookmakers_used": pick.get("bookmakers_used"),
                "confidence": pick.get("confidence"),
                "quality_score": pick.get("quality_score"),
                "edge": pick.get("edge"),
                "odds": pick.get("odds"),
            })

    all_jure = merge_unique(previous_results, accepted)
    settled, pending = settle_from_main_results(all_jure, main_results)
    final_results = sorted(settled + pending, key=sort_pick_key)
    active = sorted([p for p in pending if not is_settled(p)], key=sort_pick_key)

    summary = {
        "generated_at": now_iso(),
        "predictions_file": PREDICTIONS_FILE,
        "main_results_file": MAIN_RESULTS_FILE,
        "output_dir": OUTPUT_DIR,
        "predictions_loaded": len(predictions),
        "accepted_from_current_predictions": len(accepted),
        "rejected_from_current_predictions": len(rejected),
        "active_count": len(active),
        "results_count": len(final_results),
        "settled_count": len(settled),
        "pending_count": len(pending),
        "tactic_a": TACTIC_A,
        "tactic_b": TACTIC_B,
        "stake_a": STAKE_A,
        "stake_b": STAKE_B,
        "overall": evaluate(final_results),
        "by_tactic": group_stats(final_results, "jure_tactic"),
    }

    debug = {
        "generated_at": summary["generated_at"],
        "accepted_keys": [p.get("jure_key") for p in accepted],
        "rejected": rejected[:500],
        "rejected_count": len(rejected),
        "dedupe_rule": "fixture/event + market + side",
        "settle_rule": "fixture/event + side matched against data/tennis_results.json",
    }

    save_json(ACTIVE_FILE, active)
    save_json(RESULTS_FILE, final_results)
    save_json(SUMMARY_FILE, summary)
    save_json(DEBUG_FILE, debug)
    save_text(ACTIVE_MD_FILE, make_active_md(active, summary))

    print("")
    print("JURE DONE")
    print(f"predictions loaded: {len(predictions)}")
    print(f"accepted current: {len(accepted)}")
    print(f"rejected current: {len(rejected)}")
    print(f"active picks: {len(active)}")
    print(f"all jure results: {len(final_results)}")
    print(f"settled: {len(settled)}")
    print(f"pending: {len(pending)}")
    print("")
    print(f"Active: {ACTIVE_FILE}")
    print(f"Results: {RESULTS_FILE}")
    print(f"Summary: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()

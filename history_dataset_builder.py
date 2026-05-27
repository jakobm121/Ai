import os
import json
import statistics
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter

TZ_NAME = "Europe/Ljubljana"

PROBE_DIR = os.getenv("PROBE_DIR", "jure_probe")

HISTORY_FILE = os.getenv("HISTORY_FILE", f"{PROBE_DIR}/history_raw_sample.json")
ODDS_FILE = os.getenv("ODDS_FILE", f"{PROBE_DIR}/odds_probe_raw.json")

DATASET_FILE = f"{PROBE_DIR}/history_betting_dataset.json"
SUMMARY_FILE = f"{PROBE_DIR}/history_betting_summary.json"
REPORT_FILE = f"{PROBE_DIR}/history_betting_report.md"
DEBUG_FILE = f"{PROBE_DIR}/history_betting_debug.json"

# Keep this focused first. We can add more markets after we validate the dataset.
SUPPORTED_MARKETS = {
    "Home/Away",
    "Home/Away (1st Set)",
    "Home/Away (2nd Set)",
    "Set Betting",
    "Set / Match",
    "Number of sets",
    "Odd/Even",
    "Odd/Even (1st Set)",
}

BOOKMAKER_PRIORITY = [
    "Pncl",
    "Pinnacle",
    "bet365",
    "Bet365",
    "Betfair",
    "Marathon",
    "1xBet",
    "BetVictor",
    "Unibet",
]


def ensure_dirs():
    os.makedirs(PROBE_DIR, exist_ok=True)


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


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def normalize_text(value):
    return str(value or "").strip().lower()


def get_history_items(raw_history):
    if isinstance(raw_history, dict):
        for key in ["items_sample", "items", "result", "response", "data"]:
            value = raw_history.get(key)
            if isinstance(value, list):
                return value

    if isinstance(raw_history, list):
        return raw_history

    return []


def get_odds_items(raw_odds):
    if isinstance(raw_odds, dict):
        for key in ["odds_items_sample", "odds_items", "items", "result", "response", "data"]:
            value = raw_odds.get(key)
            if isinstance(value, list):
                return value

    if isinstance(raw_odds, list):
        return raw_odds

    return []


def event_key(item):
    return str(
        item.get("event_key")
        or item.get("fixture_id")
        or item.get("id")
        or item.get("event_id")
        or item.get("_probe_event_key")
        or ""
    )


def player_names(match):
    first = (
        match.get("event_first_player")
        or match.get("first_player")
        or match.get("first_player_name")
        or match.get("home")
        or ""
    )

    second = (
        match.get("event_second_player")
        or match.get("second_player")
        or match.get("second_player_name")
        or match.get("away")
        or ""
    )

    return str(first), str(second)


def parse_set_score(value):
    if value is None:
        return None

    if isinstance(value, dict):
        a = safe_float(value.get("score_first") or value.get("home") or value.get("first"), None)
        b = safe_float(value.get("score_second") or value.get("away") or value.get("second"), None)
        if a is not None and b is not None:
            return int(a), int(b)
        return None

    text = str(value).strip()
    if not text or text in {"-", "None", "null"}:
        return None

    # Common forms: "6 - 4", "6-4", "7:6"
    for sep in [" - ", "-", ":"]:
        if sep in text:
            parts = [p.strip() for p in text.split(sep)]
            if len(parts) >= 2:
                a = safe_float(parts[0], None)
                b = safe_float(parts[1], None)
                if a is not None and b is not None:
                    return int(a), int(b)

    return None


def extract_sets(match):
    sets = []

    # API-Tennis usually gives event_first_set, event_second_set, ...
    for key in [
        "event_first_set",
        "event_second_set",
        "event_third_set",
        "event_fourth_set",
        "event_fifth_set",
    ]:
        parsed = parse_set_score(match.get(key))
        if parsed is not None:
            sets.append(parsed)

    if sets:
        return sets

    # Sometimes score data is inside scores[]
    scores = match.get("scores")
    if isinstance(scores, list):
        by_set = []
        for row in scores:
            if not isinstance(row, dict):
                continue

            parsed = parse_set_score(row)
            if parsed is None:
                a = safe_float(row.get("score_first"), None)
                b = safe_float(row.get("score_second"), None)
                if a is not None and b is not None:
                    parsed = (int(a), int(b))

            if parsed is not None:
                set_no = safe_float(row.get("score_set"), None)
                by_set.append((set_no if set_no is not None else len(by_set) + 1, parsed))

        by_set.sort(key=lambda x: x[0])
        return [p for _n, p in by_set]

    return []


def parse_match_set_score(match, sets):
    # Prefer actual set scores.
    first_sets = 0
    second_sets = 0

    for a, b in sets:
        if a > b:
            first_sets += 1
        elif b > a:
            second_sets += 1

    if first_sets or second_sets:
        return first_sets, second_sets

    # Fallback from final result, often "2 - 0" or "0 - 2".
    for key in ["event_final_result", "final_result", "score"]:
        parsed = parse_set_score(match.get(key))
        if parsed is not None:
            return parsed

    return None


def match_winner_side(match, sets):
    first_name, second_name = player_names(match)
    winner = str(match.get("event_winner") or match.get("winner") or "").strip()

    if winner:
        w_norm = normalize_text(winner)
        if w_norm in {"first", "home", "1", "player1", "player 1"}:
            return "Home"
        if w_norm in {"second", "away", "2", "player2", "player 2"}:
            return "Away"
        if first_name and normalize_text(first_name) in w_norm:
            return "Home"
        if second_name and normalize_text(second_name) in w_norm:
            return "Away"

    score = parse_match_set_score(match, sets)
    if score:
        a, b = score
        if a > b:
            return "Home"
        if b > a:
            return "Away"

    return None


def set_winner_side(sets, set_index):
    if len(sets) <= set_index:
        return None

    a, b = sets[set_index]
    if a > b:
        return "Home"
    if b > a:
        return "Away"

    return None


def total_games(sets):
    return sum(a + b for a, b in sets)


def selection_odds(selection_dict):
    if not isinstance(selection_dict, dict):
        return None

    odds_by_book = {}

    for book, raw_odds in selection_dict.items():
        odd = safe_float(raw_odds, None)
        if odd is not None and odd > 1.0:
            odds_by_book[str(book)] = odd

    if not odds_by_book:
        return None

    values = list(odds_by_book.values())

    # Best odds.
    best_bookmaker, best_odds = max(odds_by_book.items(), key=lambda kv: kv[1])

    # Preferred odds if available.
    preferred_bookmaker = None
    preferred_odds = None

    for book in BOOKMAKER_PRIORITY:
        if book in odds_by_book:
            preferred_bookmaker = book
            preferred_odds = odds_by_book[book]
            break

    if preferred_odds is None:
        preferred_bookmaker = best_bookmaker
        preferred_odds = best_odds

    return {
        "best_bookmaker": best_bookmaker,
        "best_odds": round(best_odds, 4),
        "preferred_bookmaker": preferred_bookmaker,
        "preferred_odds": round(preferred_odds, 4),
        "median_odds": round(statistics.median(values), 4),
        "avg_odds": round(sum(values) / len(values), 4),
        "bookmakers_used": len(values),
        "odds_by_bookmaker": odds_by_book,
    }


def result_for_selection(market, selection, match, sets):
    selection_raw = str(selection)
    selection_norm = normalize_text(selection)

    mw = match_winner_side(match, sets)
    set_score = parse_match_set_score(match, sets)
    game_total = total_games(sets) if sets else None

    if market == "Home/Away":
        if mw is None:
            return None
        return "win" if selection in {"Home", "Away"} and selection == mw else "loss"

    if market == "Home/Away (1st Set)":
        sw = set_winner_side(sets, 0)
        if sw is None:
            return None
        return "win" if selection in {"Home", "Away"} and selection == sw else "loss"

    if market == "Home/Away (2nd Set)":
        sw = set_winner_side(sets, 1)
        if sw is None:
            return None
        return "win" if selection in {"Home", "Away"} and selection == sw else "loss"

    if market == "Set Betting":
        if not set_score:
            return None
        actual = f"{set_score[0]}:{set_score[1]}"
        return "win" if selection_raw == actual else "loss"

    if market == "Set / Match":
        if mw is None:
            return None

        first_set_winner = set_winner_side(sets, 0)
        if first_set_winner is None:
            return None

        first_code = "1" if first_set_winner == "Home" else "2"
        match_code = "1" if mw == "Home" else "2"
        actual = f"{first_code}/{match_code}"
        return "win" if selection_raw == actual else "loss"

    if market == "Number of sets":
        if not set_score:
            return None

        set_count = set_score[0] + set_score[1]

        # Reliable numeric selections like "2" or "3".
        if selection_norm in {"2", "2 sets", "two"}:
            return "win" if set_count == 2 else "loss"
        if selection_norm in {"3", "3 sets", "three"}:
            return "win" if set_count == 3 else "loss"

        # Some API responses expose weird label "Away" for number of sets.
        # Do not guess. Keep as unknown so optimizer does not use leaked/wrong labels.
        return None

    if market == "Odd/Even":
        if game_total is None:
            return None

        actual = "Odd" if game_total % 2 == 1 else "Even"
        return "win" if selection in {"Odd", "Even"} and selection == actual else "loss"

    if market == "Odd/Even (1st Set)":
        if not sets:
            return None

        first_total = sets[0][0] + sets[0][1]
        actual = "Odd" if first_total % 2 == 1 else "Even"
        return "win" if selection in {"Odd", "Even"} and selection == actual else "loss"

    return None


def profit_flat(result, odds, stake=1.0):
    if result == "win":
        return round(stake * (odds - 1.0), 4)
    if result == "loss":
        return round(-stake, 4)
    return 0.0


def event_type_to_level(event_type):
    text = normalize_text(event_type)

    if "wta" in text:
        return "wta"
    if "atp" in text:
        return "atp"
    if "challenger" in text:
        return "challenger"
    if "itf" in text:
        return "itf"

    return None


def event_type_to_gender(event_type):
    text = normalize_text(event_type)

    if "women" in text or "wta" in text:
        return "women"
    if "men" in text or "atp" in text or "challenger" in text:
        return "men"

    return None


def build_dataset(history_items, odds_items):
    match_by_key = {}

    for match in history_items:
        if not isinstance(match, dict):
            continue

        key = event_key(match)
        if key:
            match_by_key[key] = match

    rows = []
    skipped = Counter()

    for odds_item in odds_items:
        if not isinstance(odds_item, dict):
            continue

        key = str(odds_item.get("_probe_event_key") or event_key(odds_item))
        match = match_by_key.get(key)

        if not match:
            skipped["missing_match"] += 1
            continue

        sets = extract_sets(match)
        set_score = parse_match_set_score(match, sets)
        mw = match_winner_side(match, sets)
        first_name, second_name = player_names(match)

        for market, market_data in odds_item.items():
            if market.startswith("_"):
                continue

            if market not in SUPPORTED_MARKETS:
                skipped[f"unsupported_market:{market}"] += 1
                continue

            if not isinstance(market_data, dict):
                skipped[f"bad_market_shape:{market}"] += 1
                continue

            for selection, selection_data in market_data.items():
                odds_meta = selection_odds(selection_data)
                if not odds_meta:
                    skipped[f"missing_odds:{market}"] += 1
                    continue

                result = result_for_selection(market, str(selection), match, sets)

                # Keep unknown result rows in debug? For dataset, skip them so optimizer cannot use uncertain labels.
                if result not in {"win", "loss"}:
                    skipped[f"unknown_result:{market}:{selection}"] += 1
                    continue

                odds = odds_meta["best_odds"]

                row = {
                    "event_key": key,
                    "date": match.get("event_date") or match.get("date"),
                    "time": match.get("event_time") or match.get("time"),
                    "match": f"{first_name} - {second_name}".strip(" -"),
                    "first_player_key": match.get("first_player_key"),
                    "second_player_key": match.get("second_player_key"),
                    "first_player": first_name,
                    "second_player": second_name,
                    "tournament": match.get("tournament_name") or match.get("tournament"),
                    "tournament_key": match.get("tournament_key"),
                    "round": match.get("tournament_round") or match.get("event_round"),
                    "event_type": match.get("event_type_type") or match.get("event_type"),
                    "tour_level": event_type_to_level(match.get("event_type_type") or match.get("event_type")),
                    "gender": event_type_to_gender(match.get("event_type_type") or match.get("event_type")),
                    "market": market,
                    "selection": str(selection),
                    "odds": odds,
                    "best_bookmaker": odds_meta["best_bookmaker"],
                    "median_odds": odds_meta["median_odds"],
                    "avg_odds": odds_meta["avg_odds"],
                    "bookmakers_used": odds_meta["bookmakers_used"],
                    "result": result,
                    "profit_flat": profit_flat(result, odds, 1.0),
                    "match_winner_side": mw,
                    "set_score": f"{set_score[0]}:{set_score[1]}" if set_score else None,
                    "set_count": (set_score[0] + set_score[1]) if set_score else None,
                    "total_games": total_games(sets) if sets else None,
                    "sets": [{"first": a, "second": b} for a, b in sets],
                    "source": "api-tennis historical odds + finished fixtures",
                }

                rows.append(row)

    return rows, skipped


def evaluate(rows):
    wins = [r for r in rows if r.get("result") == "win"]
    losses = [r for r in rows if r.get("result") == "loss"]
    profit = round(sum(float(r.get("profit_flat") or 0) for r in rows), 4)
    stake = len(rows)
    roi = round((profit / stake) * 100, 2) if stake else 0.0
    winrate = round((len(wins) / max(1, len(wins) + len(losses))) * 100, 2)

    odds_values = [safe_float(r.get("odds"), None) for r in rows]
    odds_values = [x for x in odds_values if x is not None]

    return {
        "rows": len(rows),
        "wins": len(wins),
        "losses": len(losses),
        "winrate": winrate,
        "profit_flat": profit,
        "roi": roi,
        "avg_odds": round(sum(odds_values) / len(odds_values), 4) if odds_values else 0.0,
    }


def grouped_stats(rows, key):
    groups = defaultdict(list)
    for r in rows:
        value = r.get(key)
        if value is None or value == "":
            value = "unknown"
        groups[str(value)].append(r)

    out = []
    for value, items in groups.items():
        out.append({
            "group": value,
            **evaluate(items),
        })

    out.sort(key=lambda x: (x["rows"], x["profit_flat"]), reverse=True)
    return out


def make_report(generated_at, history_count, odds_count, rows, skipped, summary):
    lines = []
    lines.append("# Historical Betting Dataset Report")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- History file: `{HISTORY_FILE}`")
    lines.append(f"- Odds file: `{ODDS_FILE}`")
    lines.append(f"- History matches loaded: **{history_count}**")
    lines.append(f"- Odds items loaded: **{odds_count}**")
    lines.append("")
    lines.append("## Dataset")
    lines.append("")
    lines.append(f"- Dataset rows: **{len(rows)}**")
    lines.append(f"- Supported markets: `{', '.join(sorted(SUPPORTED_MARKETS))}`")
    lines.append("")
    lines.append("## Overall flat baseline")
    lines.append("")
    base = summary["overall"]
    lines.append("| Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {base['rows']} | {base['wins']} | {base['losses']} | {base['winrate']}% | "
        f"{base['profit_flat']}u | {base['roi']}% | {base['avg_odds']} |"
    )
    lines.append("")
    lines.append("## By market")
    lines.append("")
    lines.append("| Market | Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for row in summary["by_market"]:
        lines.append(
            f"| {row['group']} | {row['rows']} | {row['wins']} | {row['losses']} | "
            f"{row['winrate']}% | {row['profit_flat']}u | {row['roi']}% | {row['avg_odds']} |"
        )

    lines.append("")
    lines.append("## By market + selection")
    lines.append("")
    lines.append("| Market / Selection | Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for row in summary["by_market_selection"][:80]:
        lines.append(
            f"| {row['group']} | {row['rows']} | {row['wins']} | {row['losses']} | "
            f"{row['winrate']}% | {row['profit_flat']}u | {row['roi']}% | {row['avg_odds']} |"
        )

    lines.append("")
    lines.append("## Skipped / unknown")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|---|---:|")
    for reason, count in skipped.most_common(80):
        lines.append(f"| `{reason}` | {count} |")

    lines.append("")
    lines.append("## Dataset sample")
    lines.append("")
    lines.append("| Date | Match | Market | Selection | Odds | Result | Profit | Final | Total games |")
    lines.append("|---|---|---|---|---:|---|---:|---|---:|")

    for r in rows[:50]:
        lines.append(
            f"| {r.get('date','')} | {r.get('match','')} | {r.get('market','')} | "
            f"{r.get('selection','')} | {r.get('odds','')} | {r.get('result','')} | "
            f"{r.get('profit_flat','')} | {r.get('set_score','')} | {r.get('total_games','')} |"
        )

    lines.append("")
    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{DATASET_FILE}`")
    lines.append(f"- `{SUMMARY_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append("")

    return "\n".join(lines)


def main():
    ensure_dirs()

    generated_at = now_iso()

    raw_history = load_json(HISTORY_FILE, {})
    raw_odds = load_json(ODDS_FILE, {})

    history_items = get_history_items(raw_history)
    odds_items = get_odds_items(raw_odds)

    rows, skipped = build_dataset(history_items, odds_items)

    # Stable sort.
    rows.sort(key=lambda r: (
        str(r.get("date") or ""),
        str(r.get("time") or ""),
        str(r.get("event_key") or ""),
        str(r.get("market") or ""),
        str(r.get("selection") or ""),
    ))

    for idx, row in enumerate(rows, start=1):
        row["dataset_id"] = f"hist_{idx:06d}"

    by_market_selection_rows = []
    for r in rows:
        x = dict(r)
        x["market_selection"] = f"{r.get('market')} / {r.get('selection')}"
        by_market_selection_rows.append(x)

    summary = {
        "generated_at": generated_at,
        "history_file": HISTORY_FILE,
        "odds_file": ODDS_FILE,
        "history_matches_loaded": len(history_items),
        "odds_items_loaded": len(odds_items),
        "dataset_rows": len(rows),
        "supported_markets": sorted(SUPPORTED_MARKETS),
        "overall": evaluate(rows),
        "by_market": grouped_stats(rows, "market"),
        "by_market_selection": grouped_stats(by_market_selection_rows, "market_selection"),
    }

    debug = {
        "generated_at": generated_at,
        "history_matches_loaded": len(history_items),
        "odds_items_loaded": len(odds_items),
        "dataset_rows": len(rows),
        "skipped": dict(skipped),
        "history_file": HISTORY_FILE,
        "odds_file": ODDS_FILE,
        "notes": [
            "Post-match statistics are not used as predictors here.",
            "This builder only turns historical odds + finished scores into labelled betting rows.",
            "Unknown result labels are skipped to avoid false optimizer signals.",
        ],
    }

    report = make_report(
        generated_at=generated_at,
        history_count=len(history_items),
        odds_count=len(odds_items),
        rows=rows,
        skipped=skipped,
        summary=summary,
    )

    save_json(DATASET_FILE, rows)
    save_json(SUMMARY_FILE, summary)
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, report)

    print("")
    print("HISTORY BETTING DATASET DONE")
    print(f"history matches loaded: {len(history_items)}")
    print(f"odds items loaded: {len(odds_items)}")
    print(f"dataset rows: {len(rows)}")
    print(f"supported markets: {', '.join(sorted(SUPPORTED_MARKETS))}")
    print("")
    print(f"Dataset: {DATASET_FILE}")
    print(f"Summary: {SUMMARY_FILE}")
    print(f"Report: {REPORT_FILE}")
    print(f"Debug: {DEBUG_FILE}")


if __name__ == "__main__":
    main()

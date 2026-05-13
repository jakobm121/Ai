import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Europe/Ljubljana")

DATA_DIR = Path("data")
RESULTS_FILE = DATA_DIR / "tennis_totals_results.json"
REPORT_FILE = DATA_DIR / "tennis_totals_alt_line_report.json"
SUMMARY_FILE = DATA_DIR / "tennis_totals_alt_line_summary.txt"

SETTLED_RESULTS = {"win", "loss", "push", "void"}


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return default

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["results", "picks", "data"]:
            if isinstance(data.get(key), list):
                return data[key]

    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def to_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def norm(value):
    return str(value or "").strip().lower()


def is_valid_total_pick(item):
    if not isinstance(item, dict):
        return False

    if norm(item.get("bucket")) != "total_games":
        return False

    if norm(item.get("side")) not in {"under", "over"}:
        return False

    if norm(item.get("result")) not in SETTLED_RESULTS:
        return False

    if norm(item.get("result")) in {"void", "push"}:
        return True

    if to_float(item.get("line"), None) is None:
        return False

    if to_float(item.get("odds"), None) is None:
        return False

    if to_float(item.get("total_games"), None) is None:
        return False

    return True


def stake_value(item):
    return to_float(
        item.get("public_stake")
        if item.get("public_stake") is not None
        else item.get("stake"),
        0.0,
    ) or 0.0


def profit_for_result(result, odds, stake):
    result = norm(result)

    if result in {"void", "push"}:
        return 0.0

    if result == "win":
        return round(stake * (odds - 1), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def original_result(item):
    return norm(item.get("result"))


def alt_line(item):
    side = norm(item.get("side"))
    line = to_float(item.get("line"), None)

    if line is None:
        return None

    if side == "under":
        return round(line - 1.0, 1)

    if side == "over":
        return round(line + 1.0, 1)

    return None


def alt_result(item):
    result = original_result(item)

    if result in {"void", "push"}:
        return result

    side = norm(item.get("side"))
    total_games = to_float(item.get("total_games"), None)
    new_line = alt_line(item)

    if total_games is None or new_line is None:
        return "unknown"

    if side == "under":
        return "win" if total_games < new_line else "loss"

    if side == "over":
        return "win" if total_games > new_line else "loss"

    return "unknown"


def stats(items, mode="original"):
    out = {
        "total_picks": 0,
        "settled_picks": 0,
        "wins": 0,
        "losses": 0,
        "pushes": 0,
        "voids": 0,
        "win_rate": 0,
        "profit": 0,
        "roi": 0,
        "total_staked": 0,
        "avg_odds": 0,
        "avg_stake": 0,
    }

    odds_values = []
    stake_values = []

    for item in items:
        if not is_valid_total_pick(item):
            continue

        odds = to_float(item.get("odds"), 0.0) or 0.0
        stake = stake_value(item)

        if mode == "alt":
            result = alt_result(item)
        else:
            result = original_result(item)

        if result not in SETTLED_RESULTS:
            continue

        out["total_picks"] += 1

        if odds:
            odds_values.append(odds)

        if result in {"win", "loss"}:
            out["settled_picks"] += 1
            out["total_staked"] += stake
            stake_values.append(stake)

            if result == "win":
                out["wins"] += 1
            else:
                out["losses"] += 1

            out["profit"] += profit_for_result(result, odds, stake)

        elif result == "push":
            out["pushes"] += 1

        elif result == "void":
            out["voids"] += 1

    settled = out["settled_picks"]
    staked = out["total_staked"]

    out["profit"] = round(out["profit"], 4)
    out["total_staked"] = round(out["total_staked"], 4)
    out["win_rate"] = round((out["wins"] / settled) * 100, 2) if settled else 0
    out["roi"] = round((out["profit"] / staked) * 100, 2) if staked else 0
    out["avg_odds"] = round(sum(odds_values) / len(odds_values), 3) if odds_values else 0
    out["avg_stake"] = round(sum(stake_values) / len(stake_values), 3) if stake_values else 0

    return out


def group_stats(items, key_func, mode):
    groups = {}

    for item in items:
        if not is_valid_total_pick(item):
            continue

        key = key_func(item)
        groups.setdefault(str(key), []).append(item)

    return {
        key: stats(value, mode=mode)
        for key, value in sorted(groups.items(), key=lambda x: str(x[0]))
    }


def changed_examples(items):
    changed = []

    for item in items:
        if not is_valid_total_pick(item):
            continue

        original = original_result(item)
        alt = alt_result(item)

        if original in {"win", "loss"} and alt in {"win", "loss"} and original != alt:
            changed.append({
                "date": item.get("date"),
                "time": item.get("time"),
                "match": item.get("match"),
                "side": item.get("side"),
                "original_line": item.get("line"),
                "alt_line": alt_line(item),
                "total_games": item.get("total_games"),
                "odds": item.get("odds"),
                "stake": stake_value(item),
                "original_result": original,
                "alt_result": alt,
                "original_profit": profit_for_result(original, to_float(item.get("odds"), 0), stake_value(item)),
                "alt_profit": profit_for_result(alt, to_float(item.get("odds"), 0), stake_value(item)),
            })

    return changed


def line_key(item):
    line = to_float(item.get("line"), None)
    return "unknown" if line is None else str(line)


def alt_line_key(item):
    line = alt_line(item)
    return "unknown" if line is None else str(line)


def build_report(raw):
    items = [x for x in raw if is_valid_total_pick(x)]

    original = stats(items, mode="original")
    alternate = stats(items, mode="alt")

    diff = {
        "profit_diff_alt_minus_original": round(alternate["profit"] - original["profit"], 4),
        "roi_diff_alt_minus_original": round(alternate["roi"] - original["roi"], 2),
        "wins_diff_alt_minus_original": alternate["wins"] - original["wins"],
        "losses_diff_alt_minus_original": alternate["losses"] - original["losses"],
        "settled_diff_alt_minus_original": alternate["settled_picks"] - original["settled_picks"],
    }

    changed = changed_examples(items)

    return {
        "generated_at": datetime.now(TZ).isoformat(),
        "source_file": str(RESULTS_FILE),
        "raw_rows": len(raw),
        "valid_total_picks": len(items),
        "method": {
            "under": "UNDER line is moved one game lower: 20.5 -> 19.5",
            "over": "OVER line is moved one game higher: 20.5 -> 21.5",
            "odds": "same odds used for comparison because historical alternate-line odds are not available",
            "stake": "same stake/public_stake used",
        },
        "original": original,
        "alternate_one_game_harder": alternate,
        "diff": diff,
        "changed_count": len(changed),
        "changed_examples": changed,
        "original_by_side": group_stats(items, lambda x: norm(x.get("side")) or "unknown", "original"),
        "alternate_by_side": group_stats(items, lambda x: norm(x.get("side")) or "unknown", "alt"),
        "original_by_line": group_stats(items, line_key, "original"),
        "alternate_by_original_line": group_stats(items, line_key, "alt"),
        "alternate_by_alt_line": group_stats(items, alt_line_key, "alt"),
        "original_by_stake_label": group_stats(
            items,
            lambda x: x.get("public_stake_label") or x.get("stake_label") or "unknown",
            "original",
        ),
        "alternate_by_stake_label": group_stats(
            items,
            lambda x: x.get("public_stake_label") or x.get("stake_label") or "unknown",
            "alt",
        ),
        "original_by_tour_level": group_stats(items, lambda x: x.get("tour_level") or "unknown", "original"),
        "alternate_by_tour_level": group_stats(items, lambda x: x.get("tour_level") or "unknown", "alt"),
    }


def make_summary(report):
    o = report["original"]
    a = report["alternate_one_game_harder"]
    d = report["diff"]

    lines = []
    lines.append("AI77 TOTALS ALT LINE REPORT")
    lines.append("=" * 40)
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Valid total picks: {report['valid_total_picks']}")
    lines.append("")
    lines.append("Original:")
    lines.append(
        f"  {o['wins']}-{o['losses']} | WR {o['win_rate']}% | "
        f"Profit {o['profit']}u | ROI {o['roi']}% | Staked {o['total_staked']}u"
    )
    lines.append("")
    lines.append("One game harder line:")
    lines.append(
        f"  {a['wins']}-{a['losses']} | WR {a['win_rate']}% | "
        f"Profit {a['profit']}u | ROI {a['roi']}% | Staked {a['total_staked']}u"
    )
    lines.append("")
    lines.append("Difference alt - original:")
    lines.append(
        f"  Profit {d['profit_diff_alt_minus_original']}u | "
        f"ROI {d['roi_diff_alt_minus_original']}pp | "
        f"Wins {d['wins_diff_alt_minus_original']} | "
        f"Losses {d['losses_diff_alt_minus_original']}"
    )
    lines.append("")
    lines.append(f"Changed win/loss picks: {report['changed_count']}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("  This is a pure line-sensitivity test.")
    lines.append("  It uses the same odds because historical odds for the alternate line are not available.")
    lines.append("  Real alternate-line odds would usually be different.")

    return "\n".join(lines) + "\n"


def main():
    raw = load_json(RESULTS_FILE, [])
    report = build_report(raw)

    save_json(REPORT_FILE, report)
    save_text(SUMMARY_FILE, make_summary(report))

    print(make_summary(report))
    print(f"Wrote report: {REPORT_FILE}")
    print(f"Wrote summary: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()

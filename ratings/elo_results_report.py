import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


# Allow import from ratings/ when script is run from repo root.
sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"

MATCH_RESULTS_FILE = "data/tennis_results.json"
TOTALS_RESULTS_FILE = "data/tennis_totals_results.json"

OUTPUT_REPORT_FILE = "ratings/elo_results_report.json"
OUTPUT_MISSING_FILE = "ratings/elo_results_missing.json"
OUTPUT_TABLE_FILE = "ratings/elo_results_table.md"


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
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def rows_from_payload(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ["picks", "results", "data"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value

    return []


def normalize_result(value):
    return str(value or "").strip().lower()


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def infer_tour(row):
    tour_level = str(row.get("tour_level") or "").lower()
    gender = str(row.get("gender") or "").lower()
    event_type = str(row.get("event_type") or "").lower()

    if tour_level == "atp":
        return "atp"

    if tour_level == "wta":
        return "wta"

    if gender == "men":
        return "atp"

    if gender == "women":
        return "wta"

    if "men" in event_type and "women" not in event_type:
        return "atp"

    if "women" in event_type or "wta" in event_type:
        return "wta"

    if "atp" in event_type:
        return "atp"

    return None


def infer_surface(row):
    # Trenutno tvoji JSON-i pogosto nimajo surface.
    # Če ga kasneje dodaš v prediction model, ga bo report avtomatsko pobral.
    return row.get("surface") or row.get("court_surface") or None


def is_settled(row):
    return normalize_result(row.get("result")) in {"win", "loss", "void", "push"}


def is_win_loss(row):
    return normalize_result(row.get("result")) in {"win", "loss"}


def add_bucket(stats, key):
    if key not in stats:
        stats[key] = {
            "rows": 0,
            "matched_rows": 0,
            "unmatched_rows": 0,
            "win_loss_rows": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0,
            "stake": 0.0,
            "elo_agree_rows": 0,
            "elo_disagree_rows": 0,
            "elo_agree_wins": 0,
            "elo_agree_losses": 0,
            "elo_disagree_wins": 0,
            "elo_disagree_losses": 0,
            "elo_agree_profit": 0.0,
            "elo_disagree_profit": 0.0,
        }


def finalize_stats(stats):
    out = {}

    for key, s in stats.items():
        rows = s["rows"]
        matched_rows = s["matched_rows"]
        win_loss_rows = s["win_loss_rows"]
        wins = s["wins"]
        stake = s["stake"]
        profit = s["profit"]

        agree_graded = s["elo_agree_wins"] + s["elo_agree_losses"]
        disagree_graded = s["elo_disagree_wins"] + s["elo_disagree_losses"]

        out[key] = dict(s)
        out[key]["match_rate"] = round(matched_rows / rows * 100, 2) if rows else 0.0
        out[key]["win_rate"] = round(wins / win_loss_rows * 100, 2) if win_loss_rows else 0.0
        out[key]["roi"] = round(profit / stake * 100, 2) if stake else 0.0

        out[key]["elo_agree_win_rate"] = (
            round(s["elo_agree_wins"] / agree_graded * 100, 2)
            if agree_graded
            else 0.0
        )
        out[key]["elo_disagree_win_rate"] = (
            round(s["elo_disagree_wins"] / disagree_graded * 100, 2)
            if disagree_graded
            else 0.0
        )

        out[key]["elo_agree_roi"] = (
            round(s["elo_agree_profit"] / s["elo_agree_rows"] * 100, 2)
            if s["elo_agree_rows"]
            else 0.0
        )
        out[key]["elo_disagree_roi"] = (
            round(s["elo_disagree_profit"] / s["elo_disagree_rows"] * 100, 2)
            if s["elo_disagree_rows"]
            else 0.0
        )

    return out


def update_stats(stats, key, row, signal, model_type):
    add_bucket(stats, key)
    s = stats[key]

    result = normalize_result(row.get("result"))
    profit = safe_float(row.get("profit"), 0.0)
    stake = safe_float(row.get("stake"), 1.0)

    s["rows"] += 1

    if signal.get("matched"):
        s["matched_rows"] += 1
    else:
        s["unmatched_rows"] += 1

    if result in {"win", "loss"}:
        s["win_loss_rows"] += 1
        s["profit"] += profit
        s["stake"] += stake

        if result == "win":
            s["wins"] += 1
        else:
            s["losses"] += 1

    agrees = signal.get("agrees_with_pick")

    if signal.get("matched") and agrees is not None and result in {"win", "loss"}:
        if agrees:
            s["elo_agree_rows"] += 1
            s["elo_agree_profit"] += profit

            if result == "win":
                s["elo_agree_wins"] += 1
            else:
                s["elo_agree_losses"] += 1
        else:
            s["elo_disagree_rows"] += 1
            s["elo_disagree_profit"] += profit

            if result == "win":
                s["elo_disagree_wins"] += 1
            else:
                s["elo_disagree_losses"] += 1


def analyse_match_winner(rows):
    stats = {}
    missing = []
    enriched_sample = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        if not is_settled(row):
            continue

        player = row.get("player_name") or row.get("bet")
        opponent = row.get("opponent_name")

        if not player or not opponent:
            continue

        tour = infer_tour(row)
        surface = infer_surface(row)

        signal = get_elo_signal(
            player,
            opponent,
            surface=surface,
            tour=tour,
        )

        if not signal.get("matched"):
            missing.append({
                "model_type": "match_winner",
                "date": row.get("date"),
                "match": row.get("match"),
                "player": player,
                "opponent": opponent,
                "tour": tour,
                "surface": surface,
                "player_matched": signal.get("player", {}).get("matched"),
                "opponent_matched": signal.get("opponent", {}).get("matched"),
                "player_method": signal.get("player", {}).get("match_method"),
                "opponent_method": signal.get("opponent", {}).get("match_method"),
            })

        update_stats(stats, "overall", row, signal, "match_winner")
        update_stats(stats, f"tour:{row.get('tour_level') or 'unknown'}", row, signal, "match_winner")
        update_stats(stats, f"event_type:{row.get('event_type') or 'unknown'}", row, signal, "match_winner")

        if len(enriched_sample) < 25:
            enriched_sample.append({
                "date": row.get("date"),
                "match": row.get("match"),
                "bet": row.get("bet"),
                "result": row.get("result"),
                "profit": row.get("profit"),
                "elo": {
                    "matched": signal.get("matched"),
                    "overall_elo_diff": signal.get("overall_elo_diff"),
                    "surface_elo_diff": signal.get("surface_elo_diff"),
                    "agrees_with_pick": signal.get("agrees_with_pick"),
                    "player_matched_name": signal.get("player", {}).get("matched_name"),
                    "opponent_matched_name": signal.get("opponent", {}).get("matched_name"),
                },
            })

    return {
        "stats": finalize_stats(stats),
        "missing": missing,
        "sample": enriched_sample,
    }


def analyse_totals(rows):
    stats = {}
    missing = []
    enriched_sample = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        if not is_settled(row):
            continue

        first = row.get("first_player_name")
        second = row.get("second_player_name")

        if not first or not second:
            continue

        tour = infer_tour(row)
        surface = infer_surface(row)

        signal = get_elo_signal(
            first,
            second,
            surface=surface,
            tour=tour,
        )

        # Pri totalsih "agrees_with_pick" ni pick-side agreement.
        # Tukaj pomeni samo: first player ima višji ELO od second.
        # Za totals bomo uporabljali abs diff in direction kasneje.
        if not signal.get("matched"):
            missing.append({
                "model_type": "totals",
                "date": row.get("date"),
                "match": row.get("match"),
                "first_player": first,
                "second_player": second,
                "tour": tour,
                "surface": surface,
                "first_matched": signal.get("player", {}).get("matched"),
                "second_matched": signal.get("opponent", {}).get("matched"),
                "first_method": signal.get("player", {}).get("match_method"),
                "second_method": signal.get("opponent", {}).get("match_method"),
            })

        update_stats(stats, "overall", row, signal, "totals")
        update_stats(stats, f"side:{row.get('side') or 'unknown'}", row, signal, "totals")
        update_stats(stats, f"tour:{row.get('tour_level') or 'unknown'}", row, signal, "totals")
        update_stats(stats, f"line:{row.get('line') or 'unknown'}", row, signal, "totals")

        if len(enriched_sample) < 25:
            enriched_sample.append({
                "date": row.get("date"),
                "match": row.get("match"),
                "bet": row.get("bet"),
                "side": row.get("side"),
                "line": row.get("line"),
                "result": row.get("result"),
                "profit": row.get("profit"),
                "elo": {
                    "matched": signal.get("matched"),
                    "overall_elo_diff": signal.get("overall_elo_diff"),
                    "surface_elo_diff": signal.get("surface_elo_diff"),
                    "abs_overall_elo_diff": (
                        abs(signal.get("overall_elo_diff"))
                        if signal.get("overall_elo_diff") is not None
                        else None
                    ),
                    "first_matched_name": signal.get("player", {}).get("matched_name"),
                    "second_matched_name": signal.get("opponent", {}).get("matched_name"),
                },
            })

    return {
        "stats": finalize_stats(stats),
        "missing": missing,
        "sample": enriched_sample,
    }


def build_table(report):
    lines = []

    lines.append("# ELO results report")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Match winner")
    lines.append("")
    lines.append("| Bucket | Rows | Matched | Match rate | W-L | WR | Profit | ROI | ELO agree WR | ELO disagree WR |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for key, s in report["match_winner"]["stats"].items():
        lines.append(
            f"| {key} | {s['rows']} | {s['matched_rows']} | {s['match_rate']}% | "
            f"{s['wins']}-{s['losses']} | {s['win_rate']}% | "
            f"{round(s['profit'], 2)}u | {s['roi']}% | "
            f"{s['elo_agree_win_rate']}% | {s['elo_disagree_win_rate']}% |"
        )

    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| Bucket | Rows | Matched | Match rate | W-L | WR | Profit | ROI | ELO first-higher WR | ELO first-lower WR |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for key, s in report["totals"]["stats"].items():
        lines.append(
            f"| {key} | {s['rows']} | {s['matched_rows']} | {s['match_rate']}% | "
            f"{s['wins']}-{s['losses']} | {s['win_rate']}% | "
            f"{round(s['profit'], 2)}u | {s['roi']}% | "
            f"{s['elo_agree_win_rate']}% | {s['elo_disagree_win_rate']}% |"
        )

    lines.append("")
    lines.append("## Missing summary")
    lines.append("")
    lines.append(f"- Match winner missing: {len(report['match_winner']['missing'])}")
    lines.append(f"- Totals missing: {len(report['totals']['missing'])}")
    lines.append("")

    return "\n".join(lines)


def main():
    match_payload = load_json(MATCH_RESULTS_FILE, [])
    totals_payload = load_json(TOTALS_RESULTS_FILE, [])

    match_rows = rows_from_payload(match_payload)
    totals_rows = rows_from_payload(totals_payload)

    match_report = analyse_match_winner(match_rows)
    totals_report = analyse_totals(totals_rows)

    report = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "source_files": {
            "match_winner_results": MATCH_RESULTS_FILE,
            "totals_results": TOTALS_RESULTS_FILE,
            "elo": "ratings/tennis_elo.json",
        },
        "match_winner": match_report,
        "totals": totals_report,
    }

    missing = {
        "generated_at": report["generated_at"],
        "match_winner_missing": match_report["missing"],
        "totals_missing": totals_report["missing"],
    }

    save_json(OUTPUT_REPORT_FILE, report)
    save_json(OUTPUT_MISSING_FILE, missing)
    save_text(OUTPUT_TABLE_FILE, build_table(report))

    print("")
    print("ELO RESULTS REPORT DONE")
    print(f"Match winner rows: {len(match_rows)}")
    print(f"Totals rows:       {len(totals_rows)}")
    print(f"Report:            {OUTPUT_REPORT_FILE}")
    print(f"Missing:           {OUTPUT_MISSING_FILE}")
    print(f"Table:             {OUTPUT_TABLE_FILE}")
    print("")

    mw_overall = report["match_winner"]["stats"].get("overall", {})
    totals_overall = report["totals"]["stats"].get("overall", {})

    print("Match winner overall:")
    print(mw_overall)
    print("")
    print("Totals overall:")
    print(totals_overall)
    print("")


if __name__ == "__main__":
    main()

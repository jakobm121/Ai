import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"

TOTALS_RESULTS_FILE = "data/tennis_totals_results.json"

OUTPUT_JSON = "ratings/elo_totals_scan.json"
OUTPUT_TABLE = "ratings/elo_totals_scan_table.md"


UNDER_THRESHOLDS = [30, 50, 70, 90, 100, 120, 150, 180, 200]
OVER_THRESHOLDS = [20, 30, 40, 50, 60, 70, 80, 100, 120]

MIN_SAMPLE = 10


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


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def normalize_result(value):
    return str(value or "").strip().lower()


def is_win_loss(row):
    return normalize_result(row.get("result")) in {"win", "loss"}


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

    if "women" in event_type or "wta" in event_type:
        return "wta"

    if "men" in event_type or "atp" in event_type:
        return "atp"

    return None


def infer_surface(row):
    return row.get("surface") or row.get("court_surface") or None


def enrich_rows(rows):
    enriched = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        if not is_win_loss(row):
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

        if not signal.get("matched"):
            continue

        overall_diff = signal.get("overall_elo_diff")
        surface_diff = signal.get("surface_elo_diff")

        if overall_diff is None:
            continue

        if surface_diff is None:
            surface_diff = overall_diff

        item = dict(row)
        item["_tour"] = str(row.get("tour_level") or "unknown").lower()
        item["_side"] = str(row.get("side") or "").lower()
        item["_line"] = safe_float(row.get("line"), 0.0)
        item["_result"] = normalize_result(row.get("result"))
        item["_profit"] = safe_float(row.get("profit"), 0.0)
        item["_stake"] = safe_float(row.get("stake"), 1.0)
        item["_overall_elo_diff"] = safe_float(overall_diff)
        item["_surface_elo_diff"] = safe_float(surface_diff)
        item["_abs_overall_elo_diff"] = abs(safe_float(overall_diff))
        item["_abs_surface_elo_diff"] = abs(safe_float(surface_diff))
        item["_first_elo_higher"] = safe_float(overall_diff) >= 0
        item["_first_surface_elo_higher"] = safe_float(surface_diff) >= 0

        enriched.append(item)

    return enriched


def evaluate(rows):
    wins = sum(1 for r in rows if r["_result"] == "win")
    losses = sum(1 for r in rows if r["_result"] == "loss")
    profit = sum(r["_profit"] for r in rows)
    stake = sum(r["_stake"] for r in rows)

    n = wins + losses

    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / n * 100, 2) if n else 0.0,
        "profit": round(profit, 4),
        "stake": round(stake, 4),
        "roi": round(profit / stake * 100, 2) if stake else 0.0,
        "avg_odds": round(
            sum(safe_float(r.get("odds") or r.get("best_odds"), 0.0) for r in rows) / n,
            3,
        ) if n else 0.0,
    }


def scan_under_large_gap(rows, diff_field, label):
    out = []

    base = [r for r in rows if r["_side"] == "under"]

    for threshold in UNDER_THRESHOLDS:
        selected = [
            r for r in base
            if safe_float(r.get(diff_field), 0.0) >= threshold
        ]

        stats = evaluate(selected)
        stats["rule"] = f"UNDER + {label} >= {threshold}"
        stats["threshold"] = threshold
        stats["side"] = "under"
        stats["diff_type"] = label

        if stats["n"] >= MIN_SAMPLE:
            out.append(stats)

    return out


def scan_over_small_gap(rows, diff_field, label):
    out = []

    base = [r for r in rows if r["_side"] == "over"]

    for threshold in OVER_THRESHOLDS:
        selected = [
            r for r in base
            if safe_float(r.get(diff_field), 999999.0) <= threshold
        ]

        stats = evaluate(selected)
        stats["rule"] = f"OVER + {label} <= {threshold}"
        stats["threshold"] = threshold
        stats["side"] = "over"
        stats["diff_type"] = label

        if stats["n"] >= MIN_SAMPLE:
            out.append(stats)

    return out


def scan_by_tour(rows):
    out = {}

    tours = sorted({r["_tour"] for r in rows})

    for tour in tours:
        tour_rows = [r for r in rows if r["_tour"] == tour]

        rules = []
        rules.extend(scan_under_large_gap(tour_rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
        rules.extend(scan_under_large_gap(tour_rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))
        rules.extend(scan_over_small_gap(tour_rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
        rules.extend(scan_over_small_gap(tour_rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))

        rules.sort(key=lambda x: (x["roi"], x["profit"], x["n"]), reverse=True)

        out[tour] = {
            "base": evaluate(tour_rows),
            "rules": rules,
            "top_rules": rules[:15],
        }

    return out


def scan_by_line(rows):
    out = {}

    lines = sorted({r["_line"] for r in rows})

    for line in lines:
        line_rows = [r for r in rows if r["_line"] == line]

        if len(line_rows) < MIN_SAMPLE:
            continue

        rules = []
        rules.extend(scan_under_large_gap(line_rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
        rules.extend(scan_under_large_gap(line_rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))
        rules.extend(scan_over_small_gap(line_rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
        rules.extend(scan_over_small_gap(line_rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))

        rules.sort(key=lambda x: (x["roi"], x["profit"], x["n"]), reverse=True)

        out[str(line)] = {
            "base": evaluate(line_rows),
            "rules": rules,
            "top_rules": rules[:10],
        }

    return out


def scan_direction(rows):
    groups = {
        "under_large_overall_100": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_overall_elo_diff"] >= 100
        ],
        "under_large_surface_100": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_surface_elo_diff"] >= 100
        ],
        "over_close_overall_50": [
            r for r in rows
            if r["_side"] == "over" and r["_abs_overall_elo_diff"] <= 50
        ],
        "over_close_surface_50": [
            r for r in rows
            if r["_side"] == "over" and r["_abs_surface_elo_diff"] <= 50
        ],
        "under_large_overall_120": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_overall_elo_diff"] >= 120
        ],
        "under_large_surface_120": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_surface_elo_diff"] >= 120
        ],
        "over_close_overall_70": [
            r for r in rows
            if r["_side"] == "over" and r["_abs_overall_elo_diff"] <= 70
        ],
        "over_close_surface_70": [
            r for r in rows
            if r["_side"] == "over" and r["_abs_surface_elo_diff"] <= 70
        ],
    }

    return {key: evaluate(value) for key, value in groups.items()}


def all_rules(rows):
    rules = []

    rules.extend(scan_under_large_gap(rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
    rules.extend(scan_under_large_gap(rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))
    rules.extend(scan_over_small_gap(rows, "_abs_overall_elo_diff", "abs_overall_elo_diff"))
    rules.extend(scan_over_small_gap(rows, "_abs_surface_elo_diff", "abs_surface_elo_diff"))

    rules.sort(key=lambda x: (x["roi"], x["profit"], x["n"]), reverse=True)

    return rules


def build_table(report):
    lines = []

    lines.append("# ELO totals scan")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Base")
    lines.append("")
    base = report["base"]
    lines.append("| N | W-L | WR | Profit | Stake | ROI | Avg odds |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {base['n']} | {base['wins']}-{base['losses']} | {base['win_rate']}% | "
        f"{base['profit']}u | {base['stake']}u | {base['roi']}% | {base['avg_odds']} |"
    )

    lines.append("")
    lines.append("## Top overall rules")
    lines.append("")
    lines.append("| Rule | N | W-L | WR | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for r in report["top_overall_rules"]:
        lines.append(
            f"| {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
            f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} |"
        )

    lines.append("")
    lines.append("## Simple theory checks")
    lines.append("")
    lines.append("| Rule | N | W-L | WR | Profit | ROI |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for key, r in report["theory_checks"].items():
        lines.append(
            f"| {key} | {r['n']} | {r['wins']}-{r['losses']} | "
            f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
        )

    lines.append("")
    lines.append("## Top by tour")
    lines.append("")

    for tour, block in report["by_tour"].items():
        lines.append(f"### {tour}")
        lines.append("")
        lines.append("| Rule | N | W-L | WR | Profit | ROI |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for r in block["top_rules"][:8]:
            lines.append(
                f"| {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
                f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
            )

        lines.append("")

    lines.append("")
    lines.append("## Top by line")
    lines.append("")

    for line, block in report["by_line"].items():
        lines.append(f"### Line {line}")
        lines.append("")
        lines.append("| Rule | N | W-L | WR | Profit | ROI |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for r in block["top_rules"][:5]:
            lines.append(
                f"| {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
                f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
            )

        lines.append("")

    return "\n".join(lines)


def main():
    payload = load_json(TOTALS_RESULTS_FILE, [])
    raw_rows = rows_from_payload(payload)

    enriched = enrich_rows(raw_rows)

    rules = all_rules(enriched)

    report = {
        "generated_at": now_iso(),
        "source_file": TOTALS_RESULTS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "raw_rows": len(raw_rows),
        "elo_matched_win_loss_rows": len(enriched),
        "min_sample": MIN_SAMPLE,
        "base": evaluate(enriched),
        "all_overall_rules": rules,
        "top_overall_rules": rules[:25],
        "theory_checks": scan_direction(enriched),
        "by_tour": scan_by_tour(enriched),
        "by_line": scan_by_line(enriched),
    }

    save_json(OUTPUT_JSON, report)
    save_text(OUTPUT_TABLE, build_table(report))

    print("")
    print("ELO TOTALS SCAN DONE")
    print(f"Raw rows:              {len(raw_rows)}")
    print(f"ELO matched W/L rows:  {len(enriched)}")
    print(f"Output JSON:           {OUTPUT_JSON}")
    print(f"Output table:          {OUTPUT_TABLE}")
    print("")

    print("BASE:")
    print(report["base"])
    print("")

    print("TOP OVERALL RULES:")
    for r in report["top_overall_rules"][:12]:
        print(
            f"{r['rule']} | N={r['n']} | {r['wins']}-{r['losses']} | "
            f"WR={r['win_rate']}% | Profit={r['profit']}u | ROI={r['roi']}%"
        )

    print("")
    print("THEORY CHECKS:")
    for key, r in report["theory_checks"].items():
        print(
            f"{key} | N={r['n']} | {r['wins']}-{r['losses']} | "
            f"WR={r['win_rate']}% | Profit={r['profit']}u | ROI={r['roi']}%"
        )
    print("")


if __name__ == "__main__":
    main()

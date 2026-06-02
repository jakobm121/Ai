import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


sys.path.append(os.path.dirname(__file__))

from elo_lookup import get_elo_signal


TZ_NAME = "Europe/Ljubljana"

TOTALS_RESULTS_FILE = "data/tennis_totals_results.json"

OUTPUT_JSON = "ratings/elo_totals_interval_scan.json"
OUTPUT_TABLE = "ratings/elo_totals_interval_scan_table.md"

MIN_SAMPLE = 5

INTERVALS = [
    (0, 20),
    (20, 30),
    (30, 40),
    (40, 50),
    (50, 70),
    (70, 90),
    (90, 100),
    (100, 120),
    (120, 150),
    (150, 180),
    (180, 220),
    (220, 9999),
]


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

    if tour_level == "challenger":
        return "challenger"

    if tour_level == "itf":
        return "itf"

    if gender == "men":
        return "atp"

    if gender == "women":
        return "wta"

    if "women" in event_type or "wta" in event_type:
        return "wta"

    if "men" in event_type or "atp" in event_type:
        return "atp"

    return "unknown"


def infer_surface(row):
    return row.get("surface") or row.get("court_surface") or None


def interval_label(lo, hi):
    if hi >= 9999:
        return f"{lo}+"
    return f"{lo}-{hi}"


def in_interval(value, lo, hi):
    value = safe_float(value)
    if hi >= 9999:
        return value >= lo
    return lo <= value < hi


def evaluate(rows):
    wins = sum(1 for r in rows if r["_result"] == "win")
    losses = sum(1 for r in rows if r["_result"] == "loss")
    profit = sum(r["_profit"] for r in rows)
    stake = sum(r["_stake"] for r in rows)

    n = wins + losses

    avg_abs_overall = (
        sum(r["_abs_overall_elo_diff"] for r in rows) / n
        if n
        else 0.0
    )
    avg_abs_surface = (
        sum(r["_abs_surface_elo_diff"] for r in rows) / n
        if n
        else 0.0
    )

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
        "avg_abs_overall_elo_diff": round(avg_abs_overall, 2),
        "avg_abs_surface_elo_diff": round(avg_abs_surface, 2),
    }


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
            tour=tour if tour in {"atp", "wta"} else None,
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
        item["_tour"] = tour
        item["_side"] = str(row.get("side") or "").lower()
        item["_line"] = safe_float(row.get("line"), 0.0)
        item["_result"] = normalize_result(row.get("result"))
        item["_profit"] = safe_float(row.get("profit"), 0.0)
        item["_stake"] = safe_float(row.get("stake"), 1.0)
        item["_overall_elo_diff"] = safe_float(overall_diff)
        item["_surface_elo_diff"] = safe_float(surface_diff)
        item["_abs_overall_elo_diff"] = abs(safe_float(overall_diff))
        item["_abs_surface_elo_diff"] = abs(safe_float(surface_diff))

        enriched.append(item)

    return enriched


def scan_intervals(rows, diff_field, diff_label, group_name):
    out = []

    for lo, hi in INTERVALS:
        selected = [
            r for r in rows
            if in_interval(r.get(diff_field), lo, hi)
        ]

        stats = evaluate(selected)
        stats["group"] = group_name
        stats["diff_type"] = diff_label
        stats["interval"] = interval_label(lo, hi)
        stats["lo"] = lo
        stats["hi"] = hi
        stats["rule"] = f"{group_name} + {diff_label} in {stats['interval']}"

        if stats["n"] >= MIN_SAMPLE:
            out.append(stats)

    return out


def scan_side_intervals(rows):
    out = {}

    for side in ["under", "over"]:
        side_rows = [r for r in rows if r["_side"] == side]

        rows_out = []
        rows_out.extend(
            scan_intervals(
                side_rows,
                "_abs_overall_elo_diff",
                "abs_overall_elo_diff",
                side.upper(),
            )
        )
        rows_out.extend(
            scan_intervals(
                side_rows,
                "_abs_surface_elo_diff",
                "abs_surface_elo_diff",
                side.upper(),
            )
        )

        out[side] = {
            "base": evaluate(side_rows),
            "intervals": rows_out,
            "top": sorted(
                rows_out,
                key=lambda x: (x["roi"], x["profit"], x["n"]),
                reverse=True,
            )[:20],
        }

    return out


def scan_by_tour(rows):
    out = {}

    for tour in sorted({r["_tour"] for r in rows}):
        tour_rows = [r for r in rows if r["_tour"] == tour]
        out[tour] = scan_side_intervals(tour_rows)

    return out


def scan_by_line(rows):
    out = {}

    for line in sorted({r["_line"] for r in rows}):
        line_rows = [r for r in rows if r["_line"] == line]

        if len(line_rows) < MIN_SAMPLE:
            continue

        out[str(line)] = scan_side_intervals(line_rows)

    return out


def scan_combo_summary(rows):
    combos = {
        "UNDER overall 120-150": [
            r for r in rows
            if r["_side"] == "under" and in_interval(r["_abs_overall_elo_diff"], 120, 150)
        ],
        "UNDER overall 150-180": [
            r for r in rows
            if r["_side"] == "under" and in_interval(r["_abs_overall_elo_diff"], 150, 180)
        ],
        "UNDER overall 180+": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_overall_elo_diff"] >= 180
        ],
        "UNDER surface 100-120": [
            r for r in rows
            if r["_side"] == "under" and in_interval(r["_abs_surface_elo_diff"], 100, 120)
        ],
        "UNDER surface 120-150": [
            r for r in rows
            if r["_side"] == "under" and in_interval(r["_abs_surface_elo_diff"], 120, 150)
        ],
        "UNDER surface 150+": [
            r for r in rows
            if r["_side"] == "under" and r["_abs_surface_elo_diff"] >= 150
        ],
        "OVER overall 40-70": [
            r for r in rows
            if r["_side"] == "over" and in_interval(r["_abs_overall_elo_diff"], 40, 70)
        ],
        "OVER overall 50-100": [
            r for r in rows
            if r["_side"] == "over" and 50 <= r["_abs_overall_elo_diff"] < 100
        ],
        "OVER overall 70-120": [
            r for r in rows
            if r["_side"] == "over" and 70 <= r["_abs_overall_elo_diff"] < 120
        ],
        "OVER surface 40-70": [
            r for r in rows
            if r["_side"] == "over" and in_interval(r["_abs_surface_elo_diff"], 40, 70)
        ],
        "OVER surface 50-100": [
            r for r in rows
            if r["_side"] == "over" and 50 <= r["_abs_surface_elo_diff"] < 100
        ],
        "OVER surface 70-120": [
            r for r in rows
            if r["_side"] == "over" and 70 <= r["_abs_surface_elo_diff"] < 120
        ],
    }

    return {key: evaluate(value) for key, value in combos.items()}


def build_table(report):
    lines = []

    lines.append("# ELO totals interval scan")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Base")
    lines.append("")
    b = report["base"]
    lines.append("| N | W-L | WR | Profit | Stake | ROI | Avg odds |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {b['n']} | {b['wins']}-{b['losses']} | {b['win_rate']}% | "
        f"{b['profit']}u | {b['stake']}u | {b['roi']}% | {b['avg_odds']} |"
    )

    lines.append("")
    lines.append("## Combo summary")
    lines.append("")
    lines.append("| Rule | N | W-L | WR | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for key, s in report["combo_summary"].items():
        lines.append(
            f"| {key} | {s['n']} | {s['wins']}-{s['losses']} | "
            f"{s['win_rate']}% | {s['profit']}u | {s['roi']}% | {s['avg_odds']} |"
        )

    lines.append("")
    lines.append("## Top overall intervals")
    lines.append("")
    lines.append("| Rule | N | W-L | WR | Profit | ROI | Avg odds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for r in report["top_overall"]:
        lines.append(
            f"| {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
            f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} |"
        )

    lines.append("")
    lines.append("## UNDER intervals")
    lines.append("")
    lines.append("| Diff | Interval | N | W-L | WR | Profit | ROI |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    for r in report["overall"]["under"]["intervals"]:
        lines.append(
            f"| {r['diff_type']} | {r['interval']} | {r['n']} | "
            f"{r['wins']}-{r['losses']} | {r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
        )

    lines.append("")
    lines.append("## OVER intervals")
    lines.append("")
    lines.append("| Diff | Interval | N | W-L | WR | Profit | ROI |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    for r in report["overall"]["over"]["intervals"]:
        lines.append(
            f"| {r['diff_type']} | {r['interval']} | {r['n']} | "
            f"{r['wins']}-{r['losses']} | {r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
        )

    lines.append("")
    lines.append("## Top by tour")
    lines.append("")

    for tour, block in report["by_tour"].items():
        lines.append(f"### {tour}")
        lines.append("")
        lines.append("| Side | Rule | N | W-L | WR | Profit | ROI |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")

        for side in ["under", "over"]:
            for r in block[side]["top"][:8]:
                lines.append(
                    f"| {side} | {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
                    f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
                )

        lines.append("")

    lines.append("")
    lines.append("## Top by line")
    lines.append("")

    for line, block in report["by_line"].items():
        lines.append(f"### Line {line}")
        lines.append("")
        lines.append("| Side | Rule | N | W-L | WR | Profit | ROI |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")

        for side in ["under", "over"]:
            for r in block[side]["top"][:6]:
                lines.append(
                    f"| {side} | {r['rule']} | {r['n']} | {r['wins']}-{r['losses']} | "
                    f"{r['win_rate']}% | {r['profit']}u | {r['roi']}% |"
                )

        lines.append("")

    return "\n".join(lines)


def main():
    payload = load_json(TOTALS_RESULTS_FILE, [])
    raw_rows = rows_from_payload(payload)

    enriched = enrich_rows(raw_rows)

    overall = scan_side_intervals(enriched)

    all_interval_rows = []
    for side in ["under", "over"]:
        all_interval_rows.extend(overall[side]["intervals"])

    top_overall = sorted(
        all_interval_rows,
        key=lambda x: (x["roi"], x["profit"], x["n"]),
        reverse=True,
    )[:30]

    report = {
        "generated_at": now_iso(),
        "source_file": TOTALS_RESULTS_FILE,
        "elo_file": "ratings/tennis_elo.json",
        "raw_rows": len(raw_rows),
        "elo_matched_win_loss_rows": len(enriched),
        "min_sample": MIN_SAMPLE,
        "intervals": [interval_label(lo, hi) for lo, hi in INTERVALS],
        "base": evaluate(enriched),
        "overall": overall,
        "top_overall": top_overall,
        "combo_summary": scan_combo_summary(enriched),
        "by_tour": scan_by_tour(enriched),
        "by_line": scan_by_line(enriched),
    }

    save_json(OUTPUT_JSON, report)
    save_text(OUTPUT_TABLE, build_table(report))

    print("")
    print("ELO TOTALS INTERVAL SCAN DONE")
    print(f"Raw rows:             {len(raw_rows)}")
    print(f"ELO matched W/L rows: {len(enriched)}")
    print(f"Output JSON:          {OUTPUT_JSON}")
    print(f"Output table:         {OUTPUT_TABLE}")
    print("")

    print("BASE:")
    print(report["base"])
    print("")

    print("COMBO SUMMARY:")
    for key, s in report["combo_summary"].items():
        print(
            f"{key} | N={s['n']} | {s['wins']}-{s['losses']} | "
            f"WR={s['win_rate']}% | Profit={s['profit']}u | ROI={s['roi']}%"
        )

    print("")
    print("TOP OVERALL INTERVALS:")
    for r in report["top_overall"][:15]:
        print(
            f"{r['rule']} | N={r['n']} | {r['wins']}-{r['losses']} | "
            f"WR={r['win_rate']}% | Profit={r['profit']}u | ROI={r['roi']}%"
        )

    print("")


if __name__ == "__main__":
    main()

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Europe/Ljubljana")

DATA_DIR = Path("data")
RESULTS_FILE = DATA_DIR / "tennis_totals_results.json"
REPORT_FILE = DATA_DIR / "tennis_totals_signal_calibration_report.json"
SUMMARY_FILE = DATA_DIR / "tennis_totals_signal_calibration_summary.txt"

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


def is_total_pick(item):
    return isinstance(item, dict) and norm(item.get("bucket")) == "total_games"


def is_settled(item):
    return norm(item.get("result")) in SETTLED_RESULTS


def is_win_loss(item):
    return norm(item.get("result")) in {"win", "loss"}


def stake_value(item):
    return to_float(
        item.get("public_stake")
        if item.get("public_stake") is not None
        else item.get("stake"),
        0.0,
    ) or 0.0


def profit_value(item):
    return to_float(
        item.get("public_profit")
        if item.get("public_profit") is not None
        else item.get("profit"),
        0.0,
    ) or 0.0


def calc_profit(item, stake=None):
    result = norm(item.get("result"))
    odds = to_float(item.get("odds"), 0.0) or 0.0

    if stake is None:
        stake = stake_value(item)

    if result in {"push", "void"}:
        return 0.0

    if result == "win":
        return round(stake * (odds - 1), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def stats(items, use_flat_stake=None):
    valid = [x for x in items if is_total_pick(x) and is_settled(x)]

    out = {
        "total_picks": len(valid),
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
        "avg_edge": 0,
        "avg_confidence": 0,
        "avg_quality": 0,
        "avg_expected_margin": 0,
        "avg_abs_expected_margin": 0,
        "avg_model_prob": 0,
        "avg_implied_prob": 0,
        "avg_total_games": 0,
        "avg_line": 0,
        "avg_cushion": 0,
        "avg_miss_distance": 0,
        "near_miss_losses": 0,
        "tight_wins": 0,
        "clean_wins": 0,
    }

    odds_values = []
    stake_values = []
    edge_values = []
    confidence_values = []
    quality_values = []
    expected_margin_values = []
    abs_expected_margin_values = []
    model_prob_values = []
    implied_prob_values = []
    total_games_values = []
    line_values = []
    cushion_values = []
    miss_values = []

    for item in valid:
        result = norm(item.get("result"))
        side = norm(item.get("side"))
        line = to_float(item.get("line"), None)
        total_games = to_float(item.get("total_games"), None)

        stake = float(use_flat_stake if use_flat_stake is not None else stake_value(item))

        odds = to_float(item.get("odds"), None)
        if odds is not None:
            odds_values.append(odds)

        if result in {"win", "loss"}:
            out["settled_picks"] += 1
            out["total_staked"] += stake
            stake_values.append(stake)

            if result == "win":
                out["wins"] += 1
            else:
                out["losses"] += 1

            out["profit"] += calc_profit(item, stake)

        elif result == "push":
            out["pushes"] += 1

        elif result == "void":
            out["voids"] += 1

        edge_values.append(to_float(item.get("edge"), 0.0) or 0.0)
        confidence_values.append(to_float(item.get("confidence"), 0.0) or 0.0)
        quality_values.append(to_float(item.get("quality_score"), 0.0) or 0.0)

        expected_margin = to_float(item.get("expected_margin"), None)
        if expected_margin is not None:
            expected_margin_values.append(expected_margin)
            abs_expected_margin_values.append(abs(expected_margin))

        model_prob = to_float(item.get("model_prob"), None)
        if model_prob is not None:
            model_prob_values.append(model_prob)

        implied_prob = to_float(item.get("implied_prob"), None)
        if implied_prob is not None:
            implied_prob_values.append(implied_prob)

        if total_games is not None:
            total_games_values.append(total_games)

        if line is not None:
            line_values.append(line)

        if result in {"win", "loss"} and line is not None and total_games is not None:
            if side == "under":
                distance = line - total_games
            elif side == "over":
                distance = total_games - line
            else:
                distance = None

            if distance is not None:
                if result == "win":
                    cushion_values.append(distance)

                    if distance <= 0.5:
                        out["tight_wins"] += 1

                    if distance >= 3.5:
                        out["clean_wins"] += 1

                if result == "loss":
                    miss = abs(distance)
                    miss_values.append(miss)

                    if miss <= 0.5:
                        out["near_miss_losses"] += 1

    settled = out["settled_picks"]
    staked = out["total_staked"]

    out["profit"] = round(out["profit"], 4)
    out["total_staked"] = round(staked, 4)
    out["win_rate"] = round((out["wins"] / settled) * 100, 2) if settled else 0
    out["roi"] = round((out["profit"] / staked) * 100, 2) if staked else 0

    out["avg_odds"] = avg(odds_values, 3)
    out["avg_stake"] = avg(stake_values, 3)
    out["avg_edge"] = avg(edge_values, 4)
    out["avg_confidence"] = avg(confidence_values, 2)
    out["avg_quality"] = avg(quality_values, 2)
    out["avg_expected_margin"] = avg(expected_margin_values, 3)
    out["avg_abs_expected_margin"] = avg(abs_expected_margin_values, 3)
    out["avg_model_prob"] = avg(model_prob_values, 4)
    out["avg_implied_prob"] = avg(implied_prob_values, 4)
    out["avg_total_games"] = avg(total_games_values, 2)
    out["avg_line"] = avg(line_values, 2)
    out["avg_cushion"] = avg(cushion_values, 3)
    out["avg_miss_distance"] = avg(miss_values, 3)

    return out


def avg(values, digits=3):
    values = [x for x in values if x is not None]

    if not values:
        return 0

    return round(sum(values) / len(values), digits)


def bucket_number(value, buckets):
    value = to_float(value, None)

    if value is None:
        return "unknown"

    for label, low, high in buckets:
        if value >= low and value < high:
            return label

    return f"{buckets[-1][2]}+"


def bucket_abs_number(value, buckets):
    value = to_float(value, None)

    if value is None:
        return "unknown"

    return bucket_number(abs(value), buckets)


def group_stats(items, key_func):
    groups = {}

    for item in items:
        if not is_total_pick(item) or not is_settled(item):
            continue

        key = key_func(item)
        groups.setdefault(str(key), []).append(item)

    return {
        key: stats(value)
        for key, value in sorted(groups.items(), key=lambda x: str(x[0]))
    }


def side_items(items, side):
    return [x for x in items if norm(x.get("side")) == side]


def line_key(item):
    line = to_float(item.get("line"), None)
    return "unknown" if line is None else str(line)


def result_margin_bucket(item):
    side = norm(item.get("side"))
    line = to_float(item.get("line"), None)
    total_games = to_float(item.get("total_games"), None)

    if line is None or total_games is None:
        return "unknown"

    if side == "under":
        distance = line - total_games
    elif side == "over":
        distance = total_games - line
    else:
        return "unknown"

    result = norm(item.get("result"))

    if result == "win":
        if distance <= 0.5:
            return "win_by_0.5"
        if distance <= 1.5:
            return "win_by_1.5"
        if distance <= 2.5:
            return "win_by_2.5"
        if distance <= 3.5:
            return "win_by_3.5"
        return "win_by_4+"

    if result == "loss":
        miss = abs(distance)
        if miss <= 0.5:
            return "loss_by_0.5"
        if miss <= 1.5:
            return "loss_by_1.5"
        if miss <= 2.5:
            return "loss_by_2.5"
        if miss <= 3.5:
            return "loss_by_3.5"
        return "loss_by_4+"

    return result


def predicted_vs_actual_error(item):
    expected_total = to_float(item.get("expected_total_games"), None)
    total_games = to_float(item.get("total_games"), None)

    if expected_total is None or total_games is None:
        return None

    return total_games - expected_total


def prediction_error_bucket(item):
    err = predicted_vs_actual_error(item)

    if err is None:
        return "unknown"

    abs_err = abs(err)

    if abs_err <= 1:
        return "0-1"
    if abs_err <= 2:
        return "1-2"
    if abs_err <= 3:
        return "2-3"
    if abs_err <= 5:
        return "3-5"
    return "5+"


def signal_quality_score(group):
    """
    Simple heuristic score for calibration:
    Higher means the bucket is more useful.
    """
    s = group
    settled = s.get("settled_picks", 0)
    roi = s.get("roi", 0)
    wr = s.get("win_rate", 0)

    if settled < 5:
        return -999

    return round((roi * 0.7) + ((wr - 50) * 1.2) + min(settled, 50) * 0.1, 2)


def rank_groups(grouped):
    rows = []

    for key, s in grouped.items():
        row = {
            "bucket": key,
            "score": signal_quality_score(s),
            **s,
        }
        rows.append(row)

    return sorted(rows, key=lambda x: (x["score"], x["profit"], x["settled_picks"]), reverse=True)


def make_profile(items, filter_func):
    return [x for x in items if filter_func(x)]


def under_margin_confidence_profile(item):
    side = norm(item.get("side"))
    confidence = to_float(item.get("confidence"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0
    line = to_float(item.get("line"), 0) or 0

    return (
        side == "under"
        and confidence >= 74
        and margin <= -1.5
        and line in {19.5, 20.5, 21.5, 22.5}
    )


def under_core_profile(item):
    side = norm(item.get("side"))
    confidence = to_float(item.get("confidence"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0
    line = to_float(item.get("line"), 0) or 0

    return (
        side == "under"
        and confidence >= 82
        and margin <= -2.0
        and line in {19.5, 20.5, 21.5}
    )


def under_sniper_profile(item):
    side = norm(item.get("side"))
    confidence = to_float(item.get("confidence"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0
    quality = to_float(item.get("quality_score"), 0) or 0
    line = to_float(item.get("line"), 0) or 0

    return (
        side == "under"
        and confidence >= 88
        and quality >= 78
        and margin <= -2.75
        and line in {19.5, 20.5, 21.5}
    )


def over_strict_profile(item):
    side = norm(item.get("side"))
    confidence = to_float(item.get("confidence"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0
    quality = to_float(item.get("quality_score"), 0) or 0
    edge = to_float(item.get("edge"), 0) or 0
    line = to_float(item.get("line"), 0) or 0

    return (
        side == "over"
        and confidence >= 90
        and quality >= 86
        and edge >= 0.10
        and margin >= 2.2
        and line <= 21.5
    )


def build_report(raw):
    items = [x for x in raw if is_total_pick(x) and is_settled(x)]
    under = side_items(items, "under")
    over = side_items(items, "over")

    confidence_buckets = [
        ("0-74", 0, 74),
        ("74-82", 74, 82),
        ("82-86", 82, 86),
        ("86-90", 86, 90),
        ("90+", 90, 999),
    ]

    quality_buckets = [
        ("0-65", 0, 65),
        ("65-74", 65, 74),
        ("74-78", 74, 78),
        ("78-82", 78, 82),
        ("82-86", 82, 86),
        ("86+", 86, 999),
    ]

    edge_buckets = [
        ("0-0.04", 0, 0.04),
        ("0.04-0.06", 0.04, 0.06),
        ("0.06-0.08", 0.06, 0.08),
        ("0.08-0.10", 0.08, 0.10),
        ("0.10-0.12", 0.10, 0.12),
        ("0.12+", 0.12, 999),
    ]

    abs_margin_buckets = [
        ("0-1", 0, 1),
        ("1-2", 1, 2),
        ("2-3", 2, 3),
        ("3-4", 3, 4),
        ("4+", 4, 999),
    ]

    odds_buckets = [
        ("1.70-1.90", 1.70, 1.90),
        ("1.90-2.00", 1.90, 2.00),
        ("2.00-2.10", 2.00, 2.10),
        ("2.10-2.20", 2.10, 2.20),
        ("2.20+", 2.20, 999),
    ]

    line_group = group_stats(items, line_key)
    side_group = group_stats(items, lambda x: norm(x.get("side")) or "unknown")

    report = {
        "generated_at": datetime.now(TZ).isoformat(),
        "source_file": str(RESULTS_FILE),
        "raw_rows": len(raw),
        "valid_total_rows": len(items),
        "overall": stats(items),
        "under_over": side_group,
        "by_line": line_group,
        "under": {
            "overall": stats(under),
            "by_line": group_stats(under, line_key),
            "by_confidence": group_stats(under, lambda x: bucket_number(x.get("confidence"), confidence_buckets)),
            "by_quality": group_stats(under, lambda x: bucket_number(x.get("quality_score"), quality_buckets)),
            "by_edge": group_stats(under, lambda x: bucket_number(x.get("edge"), edge_buckets)),
            "by_abs_expected_margin": group_stats(under, lambda x: bucket_abs_number(x.get("expected_margin"), abs_margin_buckets)),
            "by_odds": group_stats(under, lambda x: bucket_number(x.get("odds"), odds_buckets)),
            "by_tour_level": group_stats(under, lambda x: x.get("tour_level") or "unknown"),
            "by_gender": group_stats(under, lambda x: x.get("gender") or "unknown"),
            "by_bookmakers": group_stats(
                under,
                lambda x: bucket_number(x.get("bookmakers_used"), [
                    ("0-5", 0, 5),
                    ("5-6", 5, 6),
                    ("6-7", 6, 7),
                    ("7-8", 7, 8),
                    ("8+", 8, 999),
                ]),
            ),
            "by_result_margin": group_stats(under, result_margin_bucket),
            "by_prediction_error": group_stats(under, prediction_error_bucket),
        },
        "over": {
            "overall": stats(over),
            "by_line": group_stats(over, line_key),
            "by_confidence": group_stats(over, lambda x: bucket_number(x.get("confidence"), confidence_buckets)),
            "by_quality": group_stats(over, lambda x: bucket_number(x.get("quality_score"), quality_buckets)),
            "by_edge": group_stats(over, lambda x: bucket_number(x.get("edge"), edge_buckets)),
            "by_abs_expected_margin": group_stats(over, lambda x: bucket_abs_number(x.get("expected_margin"), abs_margin_buckets)),
            "by_odds": group_stats(over, lambda x: bucket_number(x.get("odds"), odds_buckets)),
            "by_tour_level": group_stats(over, lambda x: x.get("tour_level") or "unknown"),
            "by_gender": group_stats(over, lambda x: x.get("gender") or "unknown"),
            "by_result_margin": group_stats(over, result_margin_bucket),
            "by_prediction_error": group_stats(over, prediction_error_bucket),
        },
        "ranked_signals": {
            "under_confidence": rank_groups(group_stats(under, lambda x: bucket_number(x.get("confidence"), confidence_buckets))),
            "under_quality": rank_groups(group_stats(under, lambda x: bucket_number(x.get("quality_score"), quality_buckets))),
            "under_edge": rank_groups(group_stats(under, lambda x: bucket_number(x.get("edge"), edge_buckets))),
            "under_abs_expected_margin": rank_groups(group_stats(under, lambda x: bucket_abs_number(x.get("expected_margin"), abs_margin_buckets))),
            "under_line": rank_groups(group_stats(under, line_key)),
            "over_confidence": rank_groups(group_stats(over, lambda x: bucket_number(x.get("confidence"), confidence_buckets))),
            "over_quality": rank_groups(group_stats(over, lambda x: bucket_number(x.get("quality_score"), quality_buckets))),
            "over_edge": rank_groups(group_stats(over, lambda x: bucket_number(x.get("edge"), edge_buckets))),
            "over_abs_expected_margin": rank_groups(group_stats(over, lambda x: bucket_abs_number(x.get("expected_margin"), abs_margin_buckets))),
            "over_line": rank_groups(group_stats(over, line_key)),
        },
        "test_profiles": {
            "under_margin_confidence": {
                "description": "UNDER, confidence >= 74, expected_margin <= -1.5, line 19.5-22.5",
                "stats": stats(make_profile(items, under_margin_confidence_profile)),
            },
            "under_core": {
                "description": "UNDER, confidence >= 82, expected_margin <= -2.0, line 19.5-21.5",
                "stats": stats(make_profile(items, under_core_profile)),
            },
            "under_sniper": {
                "description": "UNDER, confidence >= 88, quality >= 78, expected_margin <= -2.75, line 19.5-21.5",
                "stats": stats(make_profile(items, under_sniper_profile)),
            },
            "over_strict": {
                "description": "OVER strict test, confidence >= 90, quality >= 86, edge >= 0.10, expected_margin >= 2.2, line <= 21.5",
                "stats": stats(make_profile(items, over_strict_profile)),
            },
        },
    }

    report["diagnostics"] = make_diagnostics(report)

    return report


def make_diagnostics(report):
    diagnostics = []

    under = report["under"]["overall"]
    over = report["over"]["overall"]

    diagnostics.append({
        "signal": "side",
        "finding": "UNDER vs OVER",
        "under_roi": under["roi"],
        "over_roi": over["roi"],
        "under_profit": under["profit"],
        "over_profit": over["profit"],
        "comment": "If UNDER ROI is much higher, model should be treated as under-first instead of symmetric totals model.",
    })

    under_conf = report["ranked_signals"]["under_confidence"]
    under_quality = report["ranked_signals"]["under_quality"]
    under_edge = report["ranked_signals"]["under_edge"]
    under_margin = report["ranked_signals"]["under_abs_expected_margin"]

    diagnostics.append({
        "signal": "confidence_under",
        "best_buckets": under_conf[:5],
        "comment": "Check whether higher confidence buckets actually improve WR/ROI.",
    })

    diagnostics.append({
        "signal": "quality_under",
        "best_buckets": under_quality[:5],
        "comment": "If high quality is not better than mid quality, quality_score is not well calibrated.",
    })

    diagnostics.append({
        "signal": "edge_under",
        "best_buckets": under_edge[:5],
        "comment": "If edge does not rank well, edge may mostly represent higher odds rather than true probability advantage.",
    })

    diagnostics.append({
        "signal": "expected_margin_under",
        "best_buckets": under_margin[:5],
        "comment": "Expected margin should ideally be one of the strongest signals.",
    })

    return diagnostics


def format_group(title, grouped):
    lines = []
    lines.append(title)
    lines.append("-" * len(title))

    for key, s in grouped.items():
        lines.append(
            f"{key}: {s['wins']}-{s['losses']} | "
            f"WR {s['win_rate']}% | "
            f"Profit {s['profit']}u | "
            f"ROI {s['roi']}% | "
            f"Picks {s['total_picks']} | "
            f"Avg koef {s['avg_odds']} | "
            f"Avg margin {s['avg_expected_margin']}"
        )

    lines.append("")
    return "\n".join(lines)


def make_summary(report):
    lines = []

    lines.append("AI77 TOTALS SIGNAL CALIBRATION REPORT")
    lines.append("=" * 48)
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Valid total rows: {report['valid_total_rows']}")
    lines.append("")

    o = report["overall"]
    lines.append("OVERALL")
    lines.append("-" * 7)
    lines.append(
        f"{o['wins']}-{o['losses']} | WR {o['win_rate']}% | "
        f"Profit {o['profit']}u | ROI {o['roi']}% | "
        f"Staked {o['total_staked']}u | Avg koef {o['avg_odds']}"
    )
    lines.append("")

    lines.append(format_group("UNDER / OVER", report["under_over"]))
    lines.append(format_group("BY LINE", report["by_line"]))

    lines.append(format_group("UNDER BY CONFIDENCE", report["under"]["by_confidence"]))
    lines.append(format_group("UNDER BY QUALITY", report["under"]["by_quality"]))
    lines.append(format_group("UNDER BY EDGE", report["under"]["by_edge"]))
    lines.append(format_group("UNDER BY ABS EXPECTED MARGIN", report["under"]["by_abs_expected_margin"]))
    lines.append(format_group("UNDER BY RESULT MARGIN", report["under"]["by_result_margin"]))
    lines.append(format_group("UNDER BY PREDICTION ERROR", report["under"]["by_prediction_error"]))

    lines.append(format_group("OVER BY CONFIDENCE", report["over"]["by_confidence"]))
    lines.append(format_group("OVER BY QUALITY", report["over"]["by_quality"]))
    lines.append(format_group("OVER BY EDGE", report["over"]["by_edge"]))
    lines.append(format_group("OVER BY ABS EXPECTED MARGIN", report["over"]["by_abs_expected_margin"]))

    lines.append("TEST PROFILES")
    lines.append("-" * 13)

    for name, payload in report["test_profiles"].items():
        s = payload["stats"]
        lines.append(f"{name}: {payload['description']}")
        lines.append(
            f"  {s['wins']}-{s['losses']} | WR {s['win_rate']}% | "
            f"Profit {s['profit']}u | ROI {s['roi']}% | "
            f"Picks {s['total_picks']} | Staked {s['total_staked']}u"
        )
        lines.append("")

    lines.append("TOP UNDER SIGNAL BUCKETS")
    lines.append("-" * 24)

    for signal_name in [
        "under_confidence",
        "under_quality",
        "under_edge",
        "under_abs_expected_margin",
        "under_line",
    ]:
        lines.append(signal_name + ":")
        for row in report["ranked_signals"][signal_name][:5]:
            lines.append(
                f"  {row['bucket']}: score {row['score']} | "
                f"{row['wins']}-{row['losses']} | "
                f"ROI {row['roi']}% | Profit {row['profit']}u | Picks {row['total_picks']}"
            )
        lines.append("")

    lines.append("NOTES")
    lines.append("-" * 5)
    lines.append("If confidence/quality/edge buckets do not improve as values rise, the signal is not well calibrated.")
    lines.append("Expected margin should be checked especially for UNDER. If stronger margin does not improve results, margin formula needs repair.")
    lines.append("Edge may be misleading if model_prob is nearly fixed and edge mostly tracks high odds.")
    lines.append("This report does not modify any result file.")

    return "\n".join(lines) + "\n"


def main():
    raw = load_json(RESULTS_FILE, [])
    report = build_report(raw)

    save_json(REPORT_FILE, report)
    summary = make_summary(report)
    save_text(SUMMARY_FILE, summary)

    print(summary)
    print(f"Wrote report: {REPORT_FILE}")
    print(f"Wrote summary: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()

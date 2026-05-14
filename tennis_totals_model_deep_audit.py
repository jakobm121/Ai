import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Europe/Ljubljana")

DATA_DIR = Path("data")
RESULTS_FILE = DATA_DIR / "tennis_totals_results.json"
REPORT_FILE = DATA_DIR / "tennis_totals_model_deep_audit.json"
SUMMARY_FILE = DATA_DIR / "tennis_totals_model_deep_audit_summary.txt"

SETTLED_RESULTS = {"win", "loss", "push", "void"}


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
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
        json.dump(data, f, ensure_ascii=False, indent=2)
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


def is_total(item):
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


def profit_from_item(item, stake=None):
    result = norm(item.get("result"))
    odds = to_float(item.get("odds"), 0.0) or 0.0

    if stake is None:
        stake = stake_value(item)

    if result in {"push", "void"}:
        return 0.0

    if result == "win":
        return stake * (odds - 1)

    if result == "loss":
        return -stake

    return 0.0


def avg(values, digits=3):
    values = [x for x in values if x is not None]

    if not values:
        return 0

    return round(sum(values) / len(values), digits)


def stats(items, flat_stake=None):
    rows = [x for x in items if is_total(x) and is_settled(x)]

    out = {
        "total_picks": len(rows),
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
        "avg_quality_score": 0,
        "avg_model_prob": 0,
        "avg_implied_prob": 0,
        "avg_expected_margin": 0,
        "avg_abs_expected_margin": 0,
        "avg_expected_total_games": 0,
        "avg_actual_total_games": 0,
        "avg_prediction_error": 0,
        "avg_abs_prediction_error": 0,
        "avg_market_gap": 0,
        "avg_strength_gap": 0,
        "avg_combined_three_set_rate": 0,
        "avg_combined_close_set_rate": 0,
        "avg_combined_over_21_5_rate": 0,
        "near_losses": 0,
        "clean_wins": 0,
        "big_miss_losses": 0,
    }

    odds_values = []
    stake_values = []
    edge_values = []
    confidence_values = []
    quality_values = []
    model_prob_values = []
    implied_prob_values = []
    expected_margin_values = []
    abs_expected_margin_values = []
    expected_total_values = []
    actual_total_values = []
    prediction_error_values = []
    abs_prediction_error_values = []
    market_gap_values = []
    strength_gap_values = []
    three_set_values = []
    close_set_values = []
    over_21_5_values = []

    for item in rows:
        result = norm(item.get("result"))
        side = norm(item.get("side"))
        line = to_float(item.get("line"), None)
        total_games = to_float(item.get("total_games"), None)
        expected_total = to_float(item.get("expected_total_games"), None)

        stake = float(flat_stake if flat_stake is not None else stake_value(item))
        profit = profit_from_item(item, stake)

        odds = to_float(item.get("odds"), None)
        if odds is not None:
            odds_values.append(odds)

        if result in {"win", "loss"}:
            out["settled_picks"] += 1
            out["total_staked"] += stake
            stake_values.append(stake)
            out["profit"] += profit

            if result == "win":
                out["wins"] += 1
            else:
                out["losses"] += 1

            if line is not None and total_games is not None:
                if side == "under":
                    distance = line - total_games
                elif side == "over":
                    distance = total_games - line
                else:
                    distance = None

                if distance is not None:
                    if result == "loss" and abs(distance) <= 1.5:
                        out["near_losses"] += 1
                    if result == "loss" and abs(distance) >= 5:
                        out["big_miss_losses"] += 1
                    if result == "win" and distance >= 3.5:
                        out["clean_wins"] += 1

        elif result == "push":
            out["pushes"] += 1

        elif result == "void":
            out["voids"] += 1

        edge_values.append(to_float(item.get("edge"), None))
        confidence_values.append(to_float(item.get("confidence"), None))
        quality_values.append(to_float(item.get("quality_score"), None))
        model_prob_values.append(to_float(item.get("model_prob"), None))
        implied_prob_values.append(to_float(item.get("implied_prob"), None))

        expected_margin = to_float(item.get("expected_margin"), None)
        if expected_margin is not None:
            expected_margin_values.append(expected_margin)
            abs_expected_margin_values.append(abs(expected_margin))

        if expected_total is not None:
            expected_total_values.append(expected_total)

        if total_games is not None:
            actual_total_values.append(total_games)

        if expected_total is not None and total_games is not None:
            err = total_games - expected_total
            prediction_error_values.append(err)
            abs_prediction_error_values.append(abs(err))

        market_info = item.get("market_info") or {}
        if isinstance(market_info, dict):
            market_gap_values.append(to_float(market_info.get("market_gap"), None))

        first_strength = to_float(item.get("first_strength_score"), None)
        second_strength = to_float(item.get("second_strength_score"), None)
        if first_strength is not None and second_strength is not None:
            strength_gap_values.append(abs(first_strength - second_strength))

        first_form = item.get("first_form") or {}
        second_form = item.get("second_form") or {}

        f10 = first_form.get("last_10") if isinstance(first_form, dict) else {}
        s10 = second_form.get("last_10") if isinstance(second_form, dict) else {}

        if isinstance(f10, dict) and isinstance(s10, dict):
            f_three = to_float(f10.get("three_set_rate"), None)
            s_three = to_float(s10.get("three_set_rate"), None)
            f_close = to_float(f10.get("close_set_rate"), None)
            s_close = to_float(s10.get("close_set_rate"), None)
            f_o21 = to_float(f10.get("over_21_5_rate"), None)
            s_o21 = to_float(s10.get("over_21_5_rate"), None)

            if f_three is not None and s_three is not None:
                three_set_values.append((f_three + s_three) / 2)

            if f_close is not None and s_close is not None:
                close_set_values.append((f_close + s_close) / 2)

            if f_o21 is not None and s_o21 is not None:
                over_21_5_values.append((f_o21 + s_o21) / 2)

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
    out["avg_quality_score"] = avg(quality_values, 2)
    out["avg_model_prob"] = avg(model_prob_values, 4)
    out["avg_implied_prob"] = avg(implied_prob_values, 4)
    out["avg_expected_margin"] = avg(expected_margin_values, 3)
    out["avg_abs_expected_margin"] = avg(abs_expected_margin_values, 3)
    out["avg_expected_total_games"] = avg(expected_total_values, 3)
    out["avg_actual_total_games"] = avg(actual_total_values, 3)
    out["avg_prediction_error"] = avg(prediction_error_values, 3)
    out["avg_abs_prediction_error"] = avg(abs_prediction_error_values, 3)
    out["avg_market_gap"] = avg(market_gap_values, 4)
    out["avg_strength_gap"] = avg(strength_gap_values, 3)
    out["avg_combined_three_set_rate"] = avg(three_set_values, 4)
    out["avg_combined_close_set_rate"] = avg(close_set_values, 4)
    out["avg_combined_over_21_5_rate"] = avg(over_21_5_values, 4)

    return out


def bucket_number(value, buckets):
    value = to_float(value, None)

    if value is None:
        return "unknown"

    for label, low, high in buckets:
        if value >= low and value < high:
            return label

    return f"{buckets[-1][2]}+"


def group_stats(items, key_func):
    groups = {}

    for item in items:
        if not is_total(item) or not is_settled(item):
            continue

        key = str(key_func(item))
        groups.setdefault(key, []).append(item)

    return {
        key: stats(value)
        for key, value in sorted(groups.items(), key=lambda x: str(x[0]))
    }


def line_key(item):
    line = to_float(item.get("line"), None)
    return "unknown" if line is None else str(line)


def side_key(item):
    return norm(item.get("side")) or "unknown"


def confidence_bucket(item):
    return bucket_number(
        item.get("confidence"),
        [
            ("0-74", 0, 74),
            ("74-82", 74, 82),
            ("82-86", 82, 86),
            ("86-90", 86, 90),
            ("90+", 90, 999),
        ],
    )


def quality_bucket(item):
    return bucket_number(
        item.get("quality_score"),
        [
            ("0-70", 0, 70),
            ("70-74", 70, 74),
            ("74-78", 74, 78),
            ("78-82", 78, 82),
            ("82-86", 82, 86),
            ("86+", 86, 999),
        ],
    )


def edge_bucket(item):
    return bucket_number(
        item.get("edge"),
        [
            ("0-0.04", 0, 0.04),
            ("0.04-0.06", 0.04, 0.06),
            ("0.06-0.08", 0.06, 0.08),
            ("0.08-0.10", 0.08, 0.10),
            ("0.10-0.12", 0.10, 0.12),
            ("0.12+", 0.12, 999),
        ],
    )


def abs_margin_bucket(item):
    margin = to_float(item.get("expected_margin"), None)

    if margin is None:
        return "unknown"

    return bucket_number(
        abs(margin),
        [
            ("0-1", 0, 1),
            ("1-2", 1, 2),
            ("2-3", 2, 3),
            ("3-4", 3, 4),
            ("4-5", 4, 5),
            ("5+", 5, 999),
        ],
    )


def market_gap_bucket(item):
    market_info = item.get("market_info") or {}
    gap = None

    if isinstance(market_info, dict):
        gap = to_float(market_info.get("market_gap"), None)

    return bucket_number(
        gap,
        [
            ("0-0.08", 0, 0.08),
            ("0.08-0.18", 0.08, 0.18),
            ("0.18-0.26", 0.18, 0.26),
            ("0.26-0.40", 0.26, 0.40),
            ("0.40-0.55", 0.40, 0.55),
            ("0.55+", 0.55, 999),
        ],
    )


def strength_gap_bucket(item):
    first_strength = to_float(item.get("first_strength_score"), None)
    second_strength = to_float(item.get("second_strength_score"), None)

    if first_strength is None or second_strength is None:
        return "unknown"

    return bucket_number(
        abs(first_strength - second_strength),
        [
            ("0-8", 0, 8),
            ("8-15", 8, 15),
            ("15-22", 15, 22),
            ("22-30", 22, 30),
            ("30+", 30, 999),
        ],
    )


def combined_form_value(item, field):
    first_form = item.get("first_form") or {}
    second_form = item.get("second_form") or {}

    f10 = first_form.get("last_10") if isinstance(first_form, dict) else {}
    s10 = second_form.get("last_10") if isinstance(second_form, dict) else {}

    if not isinstance(f10, dict) or not isinstance(s10, dict):
        return None

    a = to_float(f10.get(field), None)
    b = to_float(s10.get(field), None)

    if a is None or b is None:
        return None

    return (a + b) / 2


def combined_three_set_bucket(item):
    value = combined_form_value(item, "three_set_rate")

    return bucket_number(
        value,
        [
            ("0-0.20", 0, 0.20),
            ("0.20-0.30", 0.20, 0.30),
            ("0.30-0.40", 0.30, 0.40),
            ("0.40-0.50", 0.40, 0.50),
            ("0.50+", 0.50, 999),
        ],
    )


def combined_close_set_bucket(item):
    value = combined_form_value(item, "close_set_rate")

    return bucket_number(
        value,
        [
            ("0-0.25", 0, 0.25),
            ("0.25-0.35", 0.25, 0.35),
            ("0.35-0.45", 0.35, 0.45),
            ("0.45-0.55", 0.45, 0.55),
            ("0.55+", 0.55, 999),
        ],
    )


def combined_over_21_5_bucket(item):
    value = combined_form_value(item, "over_21_5_rate")

    return bucket_number(
        value,
        [
            ("0-0.30", 0, 0.30),
            ("0.30-0.40", 0.30, 0.40),
            ("0.40-0.50", 0.40, 0.50),
            ("0.50-0.60", 0.50, 0.60),
            ("0.60+", 0.60, 999),
        ],
    )


def prediction_error_bucket(item):
    expected = to_float(item.get("expected_total_games"), None)
    actual = to_float(item.get("total_games"), None)

    if expected is None or actual is None:
        return "unknown"

    err = actual - expected

    return bucket_number(
        abs(err),
        [
            ("0-1", 0, 1),
            ("1-2", 1, 2),
            ("2-3", 2, 3),
            ("3-5", 3, 5),
            ("5+", 5, 999),
        ],
    )


def simulated_profile_c_plus_stake(item):
    side = norm(item.get("side"))
    confidence = to_float(item.get("confidence"), 0) or 0
    quality = to_float(item.get("quality_score"), 0) or 0
    edge = to_float(item.get("edge"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0
    line = to_float(item.get("line"), 0) or 0

    if side == "under":
        if confidence < 82:
            return 0.0

        if confidence < 86:
            stake = 1.0
        elif confidence < 90:
            stake = 0.5
            if edge >= 0.10 and quality >= 82:
                stake = 0.75
        else:
            stake = 0.75
            if (edge >= 0.10 and quality >= 82) or quality >= 86:
                stake = 1.0

        if margin > -1.5:
            stake = min(stake, 0.5)

        if line == 18.5:
            stake = min(stake, 0.5)

        return stake

    if side == "over":
        stake = 0.5

        if (
            line <= 20.5
            and confidence >= 90
            and quality >= 82
            and margin >= 2.5
            and edge >= 0.08
        ):
            stake = 0.75

        return stake

    return 0.0


def stats_with_custom_stake(items, stake_func):
    rows = []

    for item in items:
        new_item = dict(item)
        stake = stake_func(item)

        if stake <= 0:
            continue

        new_item["stake"] = stake
        new_item["public_stake"] = stake
        new_item["profit"] = profit_from_item(item, stake)
        new_item["public_profit"] = new_item["profit"]

        rows.append(new_item)

    return stats(rows)


def profile_filters(item):
    side = norm(item.get("side"))
    line = to_float(item.get("line"), 0) or 0
    confidence = to_float(item.get("confidence"), 0) or 0
    quality = to_float(item.get("quality_score"), 0) or 0
    edge = to_float(item.get("edge"), 0) or 0
    margin = to_float(item.get("expected_margin"), 0) or 0

    return {
        "under_all": side == "under",
        "under_conf_82_plus": side == "under" and confidence >= 82,
        "under_profile_c_plus_publishable": simulated_profile_c_plus_stake(item) > 0 and side == "under",
        "under_edge_010_plus": side == "under" and edge >= 0.10,
        "under_quality_82_plus": side == "under" and quality >= 82,
        "under_line_19_5_20_5": side == "under" and line in {19.5, 20.5},
        "under_no_21_5": side == "under" and line != 21.5,
        "under_margin_2_3_or_4_plus": side == "under" and (2 <= abs(margin) < 3 or abs(margin) >= 4),
        "over_all": side == "over",
        "over_20_5_only": side == "over" and line == 20.5,
        "over_low_edge_only": side == "over" and edge >= 0.06 and edge < 0.10,
        "over_high_edge_danger": side == "over" and edge >= 0.10,
    }


def make_profiles(items):
    profile_rows = {}

    for item in items:
        if not is_total(item) or not is_settled(item):
            continue

        flags = profile_filters(item)

        for name, ok in flags.items():
            if ok:
                profile_rows.setdefault(name, []).append(item)

    out = {}

    for name, rows in profile_rows.items():
        out[name] = stats(rows)

    out["profile_c_plus_custom_stake"] = stats_with_custom_stake(
        items,
        simulated_profile_c_plus_stake,
    )

    return out


def build_report(raw):
    items = [x for x in raw if is_total(x) and is_settled(x)]
    under = [x for x in items if norm(x.get("side")) == "under"]
    over = [x for x in items if norm(x.get("side")) == "over"]

    report = {
        "generated_at": datetime.now(TZ).isoformat(),
        "source_file": str(RESULTS_FILE),
        "raw_rows": len(raw),
        "valid_total_rows": len(items),
        "overall": stats(items),
        "by_side": group_stats(items, side_key),
        "by_line": group_stats(items, line_key),
        "by_tour_level": group_stats(items, lambda x: x.get("tour_level") or "unknown"),
        "by_gender": group_stats(items, lambda x: x.get("gender") or "unknown"),
        "by_confidence": group_stats(items, confidence_bucket),
        "by_quality": group_stats(items, quality_bucket),
        "by_edge": group_stats(items, edge_bucket),
        "by_abs_expected_margin": group_stats(items, abs_margin_bucket),
        "by_market_gap": group_stats(items, market_gap_bucket),
        "by_strength_gap": group_stats(items, strength_gap_bucket),
        "by_combined_three_set_rate": group_stats(items, combined_three_set_bucket),
        "by_combined_close_set_rate": group_stats(items, combined_close_set_bucket),
        "by_combined_over_21_5_rate": group_stats(items, combined_over_21_5_bucket),
        "by_prediction_error": group_stats(items, prediction_error_bucket),
        "under": {
            "overall": stats(under),
            "by_line": group_stats(under, line_key),
            "by_confidence": group_stats(under, confidence_bucket),
            "by_quality": group_stats(under, quality_bucket),
            "by_edge": group_stats(under, edge_bucket),
            "by_abs_expected_margin": group_stats(under, abs_margin_bucket),
            "by_market_gap": group_stats(under, market_gap_bucket),
            "by_strength_gap": group_stats(under, strength_gap_bucket),
            "by_combined_three_set_rate": group_stats(under, combined_three_set_bucket),
            "by_combined_close_set_rate": group_stats(under, combined_close_set_bucket),
            "by_combined_over_21_5_rate": group_stats(under, combined_over_21_5_bucket),
            "by_prediction_error": group_stats(under, prediction_error_bucket),
        },
        "over": {
            "overall": stats(over),
            "by_line": group_stats(over, line_key),
            "by_confidence": group_stats(over, confidence_bucket),
            "by_quality": group_stats(over, quality_bucket),
            "by_edge": group_stats(over, edge_bucket),
            "by_abs_expected_margin": group_stats(over, abs_margin_bucket),
            "by_market_gap": group_stats(over, market_gap_bucket),
            "by_strength_gap": group_stats(over, strength_gap_bucket),
            "by_combined_three_set_rate": group_stats(over, combined_three_set_bucket),
            "by_combined_close_set_rate": group_stats(over, combined_close_set_bucket),
            "by_combined_over_21_5_rate": group_stats(over, combined_over_21_5_bucket),
            "by_prediction_error": group_stats(over, prediction_error_bucket),
        },
        "profiles": make_profiles(items),
    }

    report["recommendations"] = make_recommendations(report)

    return report


def group_lines(title, grouped):
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
            f"Avg odds {s['avg_odds']} | "
            f"Avg edge {s['avg_edge']} | "
            f"Avg margin {s['avg_expected_margin']}"
        )

    lines.append("")
    return "\n".join(lines)


def make_recommendations(report):
    recs = []

    under = report["under"]["overall"]
    over = report["over"]["overall"]

    if under["roi"] > over["roi"] + 15:
        recs.append({
            "priority": 1,
            "title": "Use under-first model",
            "reason": f"UNDER ROI {under['roi']}% vs OVER ROI {over['roi']}%.",
            "action": "Separate UNDER and OVER scoring/staking. Do not use one symmetric score.",
        })

    over_line = report["over"]["by_line"]
    over_20 = over_line.get("20.5")
    over_21 = over_line.get("21.5")
    over_22 = over_line.get("22.5")

    if over_20 and over_20["roi"] > 0:
        recs.append({
            "priority": 2,
            "title": "Keep only strong over 20.5 exposure",
            "reason": f"OVER 20.5 ROI {over_20['roi']}%.",
            "action": "Over 20.5 can stay. Cap over stake and avoid 1u.",
        })

    if over_21 and over_21["roi"] < 0:
        recs.append({
            "priority": 3,
            "title": "Reduce over 21.5",
            "reason": f"OVER 21.5 ROI {over_21['roi']}%.",
            "action": "Require stronger filters or remove from public.",
        })

    if over_22 and over_22["roi"] < 0:
        recs.append({
            "priority": 4,
            "title": "Remove or ultra-filter over 22.5",
            "reason": f"OVER 22.5 ROI {over_22['roi']}%.",
            "action": "Avoid public over 22.5 unless there is future proof.",
        })

    under_conf = report["under"]["by_confidence"]
    c_82_86 = under_conf.get("82-86")
    c_86_90 = under_conf.get("86-90")
    c_90 = under_conf.get("90+")

    if c_82_86 and c_86_90 and c_82_86["roi"] > c_86_90["roi"] + 20:
        recs.append({
            "priority": 5,
            "title": "Confidence is not linear",
            "reason": f"UNDER 82-86 ROI {c_82_86['roi']}%, UNDER 86-90 ROI {c_86_90['roi']}%.",
            "action": "Do not increase stake linearly with confidence. Keep Profile C+ style.",
        })

    under_edge = report["under"]["by_edge"]
    e_010 = under_edge.get("0.10-0.12")
    e_008 = under_edge.get("0.08-0.10")

    if e_010 and e_008 and e_010["roi"] > e_008["roi"] + 20:
        recs.append({
            "priority": 6,
            "title": "Use under edge >= 0.10 as boost",
            "reason": f"UNDER edge 0.10-0.12 ROI {e_010['roi']}%, edge 0.08-0.10 ROI {e_008['roi']}%.",
            "action": "Edge >= 0.10 should boost under stake, but not be universal filter.",
        })

    over_edge = report["over"]["by_edge"]
    oe_high = over_edge.get("0.12+")
    if oe_high and oe_high["roi"] < 0:
        recs.append({
            "priority": 7,
            "title": "Do not boost over high edge",
            "reason": f"OVER edge 0.12+ ROI {oe_high['roi']}%.",
            "action": "High over edge may mean market correctly doubts over. Cap or remove.",
        })

    return sorted(recs, key=lambda x: x["priority"])


def make_summary(report):
    lines = []

    lines.append("AI77 TENNIS TOTALS MODEL DEEP AUDIT")
    lines.append("=" * 44)
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Rows: {report['valid_total_rows']}")
    lines.append("")

    o = report["overall"]
    lines.append("OVERALL")
    lines.append("-" * 7)
    lines.append(
        f"{o['wins']}-{o['losses']} | WR {o['win_rate']}% | "
        f"Profit {o['profit']}u | ROI {o['roi']}% | "
        f"Staked {o['total_staked']}u | Avg odds {o['avg_odds']}"
    )
    lines.append("")

    lines.append(group_lines("BY SIDE", report["by_side"]))
    lines.append(group_lines("BY LINE", report["by_line"]))

    lines.append(group_lines("UNDER BY CONFIDENCE", report["under"]["by_confidence"]))
    lines.append(group_lines("UNDER BY QUALITY", report["under"]["by_quality"]))
    lines.append(group_lines("UNDER BY EDGE", report["under"]["by_edge"]))
    lines.append(group_lines("UNDER BY MARKET GAP", report["under"]["by_market_gap"]))
    lines.append(group_lines("UNDER BY STRENGTH GAP", report["under"]["by_strength_gap"]))
    lines.append(group_lines("UNDER BY THREE SET RATE", report["under"]["by_combined_three_set_rate"]))
    lines.append(group_lines("UNDER BY CLOSE SET RATE", report["under"]["by_combined_close_set_rate"]))
    lines.append(group_lines("UNDER BY OVER 21.5 FORM RATE", report["under"]["by_combined_over_21_5_rate"]))
    lines.append(group_lines("UNDER BY PREDICTION ERROR", report["under"]["by_prediction_error"]))

    lines.append(group_lines("OVER BY LINE", report["over"]["by_line"]))
    lines.append(group_lines("OVER BY EDGE", report["over"]["by_edge"]))
    lines.append(group_lines("OVER BY CONFIDENCE", report["over"]["by_confidence"]))
    lines.append(group_lines("OVER BY MARKET GAP", report["over"]["by_market_gap"]))
    lines.append(group_lines("OVER BY THREE SET RATE", report["over"]["by_combined_three_set_rate"]))

    lines.append("TEST PROFILES")
    lines.append("-" * 13)

    for name, s in report["profiles"].items():
        lines.append(
            f"{name}: {s['wins']}-{s['losses']} | "
            f"WR {s['win_rate']}% | Profit {s['profit']}u | "
            f"ROI {s['roi']}% | Picks {s['total_picks']} | "
            f"Staked {s['total_staked']}u"
        )

    lines.append("")
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 15)

    for rec in report["recommendations"]:
        lines.append(f"{rec['priority']}. {rec['title']}")
        lines.append(f"   Reason: {rec['reason']}")
        lines.append(f"   Action: {rec['action']}")

    lines.append("")
    lines.append("NOTES")
    lines.append("-" * 5)
    lines.append("This audit does not modify predictions or results.")
    lines.append("Use it to decide which parts of tennis_totals_predictions.py should be changed.")
    lines.append("Most important: check whether model features are predictive before changing live production.")

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

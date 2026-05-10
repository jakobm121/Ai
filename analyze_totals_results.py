import json
import re
from pathlib import Path
from collections import defaultdict


INPUT_FILE = Path("data/results_totals.json")
OUTPUT_DIR = Path("output")

AUDIT_FILE = OUTPUT_DIR / "totals_audit_report.json"
CLEAN_FILE = OUTPUT_DIR / "totals_clean_results.json"
STATS_FILE = OUTPUT_DIR / "totals_public_stats.json"


PUBLIC_FILTERS = {
    "sport": "tennis",
    "bucket": "total_games",
    "allowed_sides": ["under"],
    "min_odds": 1.95,
    "max_odds": 2.20,
    "min_bookmakers_used": 5,
    "min_confidence": 80.0,
    "min_quality_score": 80.0,
    "allowed_stake_labels": ["Strong", "Top Rated"],
    "allowed_lines": [18.5, 19.5, 20.5, 21.5, 22.5],
    "max_expected_margin": -2.0,
}


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_total_games(final_score):
    """
    Parses tennis score like:
    '6-3, 3-6, 4-6'
    '7-6, 7-5'
    '6-4, 6-4'

    Returns:
    {
      valid: bool,
      total_games: int | None,
      reason: str
    }
    """

    if not final_score or not isinstance(final_score, str):
        return {
            "valid": False,
            "total_games": None,
            "reason": "missing_score",
        }

    sets = [s.strip() for s in final_score.split(",") if s.strip()]

    if len(sets) < 2:
        return {
            "valid": False,
            "total_games": None,
            "reason": "incomplete_match_score",
        }

    total_games = 0
    valid_sets = 0

    for set_score in sets:
        nums = re.findall(r"\d+", set_score)

        if len(nums) < 2:
            return {
                "valid": False,
                "total_games": None,
                "reason": f"invalid_set_score:{set_score}",
            }

        games_a = int(nums[0])
        games_b = int(nums[1])

        total_games += games_a + games_b
        valid_sets += 1

    if valid_sets < 2:
        return {
            "valid": False,
            "total_games": None,
            "reason": "not_enough_completed_sets",
        }

    return {
        "valid": True,
        "total_games": total_games,
        "reason": "ok",
    }


def settle_pick(pick):
    score_data = parse_total_games(pick.get("final_score"))

    if not score_data["valid"]:
        return {
            "settlement_valid": False,
            "settlement_reason": score_data["reason"],
            "true_total_games": None,
            "true_result": "void",
            "true_profit": 0.0,
        }

    total_games = score_data["total_games"]

    side = str(pick.get("side", "")).lower()
    line = pick.get("line")
    odds = pick.get("odds")
    stake = pick.get("stake", 1)

    try:
        line = float(line)
        odds = float(odds)
        stake = float(stake)
    except (TypeError, ValueError):
        return {
            "settlement_valid": False,
            "settlement_reason": "invalid_line_odds_or_stake",
            "true_total_games": total_games,
            "true_result": "void",
            "true_profit": 0.0,
        }

    if side == "over":
        won = total_games > line
    elif side == "under":
        won = total_games < line
    else:
        return {
            "settlement_valid": False,
            "settlement_reason": "invalid_side",
            "true_total_games": total_games,
            "true_result": "void",
            "true_profit": 0.0,
        }

    if won:
        result = "win"
        profit = stake * (odds - 1)
    else:
        result = "loss"
        profit = -stake

    return {
        "settlement_valid": True,
        "settlement_reason": "ok",
        "true_total_games": total_games,
        "true_result": result,
        "true_profit": round(profit, 3),
    }


def audit_pick(pick):
    settlement = settle_pick(pick)
    issues = []

    old_total_games = pick.get("total_games")
    old_result = pick.get("result")
    old_profit = pick.get("profit")

    if not settlement["settlement_valid"]:
        issues.append(settlement["settlement_reason"])
    else:
        if old_total_games is not None and old_total_games != settlement["true_total_games"]:
            issues.append("total_games_mismatch")

        if old_result is not None and old_result != settlement["true_result"]:
            issues.append("result_mismatch")

        if old_profit is not None:
            try:
                if abs(float(old_profit) - settlement["true_profit"]) > 0.02:
                    issues.append("profit_mismatch")
            except (TypeError, ValueError):
                issues.append("profit_invalid")

    audited = dict(pick)
    audited["_audit"] = {
        "issues": issues,
        **settlement,
    }

    return audited


def passes_public_filter(pick):
    if pick.get("sport") != PUBLIC_FILTERS["sport"]:
        return False

    if pick.get("bucket") != PUBLIC_FILTERS["bucket"]:
        return False

    side = str(pick.get("side", "")).lower()
    if side not in PUBLIC_FILTERS["allowed_sides"]:
        return False

    try:
        odds = float(pick.get("odds"))
        bookmakers_used = int(pick.get("bookmakers_used", 0))
        confidence = float(pick.get("confidence", 0))
        quality_score = float(pick.get("quality_score", 0))
        line = float(pick.get("line"))
        expected_margin = float(pick.get("expected_margin", 999))
    except (TypeError, ValueError):
        return False

    if not (PUBLIC_FILTERS["min_odds"] <= odds <= PUBLIC_FILTERS["max_odds"]):
        return False

    if bookmakers_used < PUBLIC_FILTERS["min_bookmakers_used"]:
        return False

    if confidence < PUBLIC_FILTERS["min_confidence"]:
        return False

    if quality_score < PUBLIC_FILTERS["min_quality_score"]:
        return False

    if line not in PUBLIC_FILTERS["allowed_lines"]:
        return False

    if expected_margin > PUBLIC_FILTERS["max_expected_margin"]:
        return False

    if pick.get("stake_label") not in PUBLIC_FILTERS["allowed_stake_labels"]:
        return False

    return True


def deduplicate_by_fixture(picks):
    best = {}

    for pick in picks:
        fixture_id = pick.get("fixture_id") or pick.get("event_key") or pick.get("pick_id")

        current = best.get(fixture_id)

        if current is None:
            best[fixture_id] = pick
            continue

        pick_score = (
            float(pick.get("quality_score", 0)),
            float(pick.get("edge", 0)),
            float(pick.get("confidence", 0)),
            float(pick.get("odds", 0)),
        )

        current_score = (
            float(current.get("quality_score", 0)),
            float(current.get("edge", 0)),
            float(current.get("confidence", 0)),
            float(current.get("odds", 0)),
        )

        if pick_score > current_score:
            best[fixture_id] = pick

    return list(best.values())


def build_stats(picks):
    stats = {
        "total_picks": 0,
        "wins": 0,
        "losses": 0,
        "voids": 0,
        "profit": 0.0,
        "stake": 0.0,
        "roi": 0.0,
        "win_rate": 0.0,
        "average_odds": 0.0,
        "by_side": {},
        "by_line": {},
        "by_stake_label": {},
        "by_tour_level": {},
    }

    settled = []

    for pick in picks:
        audit = pick.get("_audit", {})
        result = audit.get("true_result")

        if result not in ["win", "loss"]:
            stats["voids"] += 1
            continue

        settled.append(pick)

    def calc_group(group_picks):
        total = len(group_picks)
        wins = sum(1 for p in group_picks if p["_audit"]["true_result"] == "win")
        losses = sum(1 for p in group_picks if p["_audit"]["true_result"] == "loss")
        profit = round(sum(float(p["_audit"]["true_profit"]) for p in group_picks), 3)
        stake = round(sum(float(p.get("stake", 0)) for p in group_picks), 3)
        avg_odds = round(sum(float(p.get("odds", 0)) for p in group_picks) / total, 3) if total else 0.0
        win_rate = round((wins / total) * 100, 2) if total else 0.0
        roi = round((profit / stake) * 100, 2) if stake else 0.0

        return {
            "total_picks": total,
            "wins": wins,
            "losses": losses,
            "profit": profit,
            "stake": stake,
            "roi": roi,
            "win_rate": win_rate,
            "average_odds": avg_odds,
        }

    overall = calc_group(settled)
    stats.update(overall)

    grouped = {
        "by_side": defaultdict(list),
        "by_line": defaultdict(list),
        "by_stake_label": defaultdict(list),
        "by_tour_level": defaultdict(list),
    }

    for pick in settled:
        grouped["by_side"][pick.get("side", "unknown")].append(pick)
        grouped["by_line"][str(pick.get("line", "unknown"))].append(pick)
        grouped["by_stake_label"][pick.get("stake_label", "unknown")].append(pick)
        grouped["by_tour_level"][pick.get("tour_level", "unknown")].append(pick)

    for group_name, group_data in grouped.items():
        stats[group_name] = {
            key: calc_group(value)
            for key, value in sorted(group_data.items())
        }

    return stats


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_picks = load_json(INPUT_FILE)

    audited_picks = [audit_pick(pick) for pick in raw_picks]

    clean_picks = []
    rejected_picks = []

    for pick in audited_picks:
        audit = pick["_audit"]

        if not audit["settlement_valid"]:
            rejected_picks.append(pick)
            continue

        if audit["true_result"] not in ["win", "loss"]:
            rejected_picks.append(pick)
            continue

        if not passes_public_filter(pick):
            rejected_picks.append(pick)
            continue

        clean_pick = dict(pick)
        clean_pick["total_games"] = audit["true_total_games"]
        clean_pick["result"] = audit["true_result"]
        clean_pick["profit"] = audit["true_profit"]

        clean_picks.append(clean_pick)

    clean_picks = deduplicate_by_fixture(clean_picks)
    stats = build_stats(clean_picks)

    audit_report = {
        "input_count": len(raw_picks),
        "audited_count": len(audited_picks),
        "public_clean_count": len(clean_picks),
        "rejected_count": len(rejected_picks),
        "issue_summary": {},
        "mismatch_examples": [],
    }

    issue_counter = defaultdict(int)

    for pick in audited_picks:
        for issue in pick["_audit"]["issues"]:
            issue_counter[issue] += 1

    audit_report["issue_summary"] = dict(sorted(issue_counter.items()))

    mismatch_examples = []
    for pick in audited_picks:
        issues = pick["_audit"]["issues"]
        if issues:
            mismatch_examples.append({
                "date": pick.get("date"),
                "time": pick.get("time"),
                "match": pick.get("match"),
                "bet": pick.get("bet"),
                "final_score": pick.get("final_score"),
                "old_total_games": pick.get("total_games"),
                "true_total_games": pick["_audit"].get("true_total_games"),
                "old_result": pick.get("result"),
                "true_result": pick["_audit"].get("true_result"),
                "old_profit": pick.get("profit"),
                "true_profit": pick["_audit"].get("true_profit"),
                "issues": issues,
            })

    audit_report["mismatch_examples"] = mismatch_examples[:50]

    save_json(AUDIT_FILE, audit_report)
    save_json(CLEAN_FILE, clean_picks)
    save_json(STATS_FILE, stats)

    print("Done.")
    print(f"Input picks: {len(raw_picks)}")
    print(f"Clean public picks: {len(clean_picks)}")
    print(f"Rejected picks: {len(rejected_picks)}")
    print(f"Audit file: {AUDIT_FILE}")
    print(f"Clean file: {CLEAN_FILE}")
    print(f"Stats file: {STATS_FILE}")


if __name__ == "__main__":
    main()

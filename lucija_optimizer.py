import os
import json
import itertools
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = os.getenv("DATA_DIR", "data")
LUCIJA_DIR = os.getenv("LUCIJA_DIR", f"{DATA_DIR}/lucija")

SOURCE_FILE = os.getenv("TENNIS_TOTALS_RESULTS_FILE", f"{DATA_DIR}/tennis_totals_results.json")

REPORT_FILE = f"{LUCIJA_DIR}/lucija_optimizer_report.md"
SUMMARY_FILE = f"{LUCIJA_DIR}/lucija_optimizer_summary.json"

BEST_UNDER_FILE = f"{LUCIJA_DIR}/lucija_optimizer_best_under.json"
BEST_OVER_FILE = f"{LUCIJA_DIR}/lucija_optimizer_best_over.json"

TOP_UNDER_FILE = f"{LUCIJA_DIR}/lucija_optimizer_top_under.json"
TOP_OVER_FILE = f"{LUCIJA_DIR}/lucija_optimizer_top_over.json"

V1_PICKS_FILE = f"{LUCIJA_DIR}/lucija_optimizer_v1_picks.json"
BEST_UNDER_PICKS_FILE = f"{LUCIJA_DIR}/lucija_optimizer_best_under_picks.json"
BEST_OVER_PICKS_FILE = f"{LUCIJA_DIR}/lucija_optimizer_best_over_picks.json"

DEBUG_FILE = f"{LUCIJA_DIR}/lucija_optimizer_debug.json"

MIN_PICKS = int(os.getenv("LUCIJA_OPT_MIN_PICKS", "80"))
MIN_SETTLED = int(os.getenv("LUCIJA_OPT_MIN_SETTLED", "80"))
MIN_TEST_PICKS = int(os.getenv("LUCIJA_OPT_MIN_TEST_PICKS", "20"))
TEST_RATIO = float(os.getenv("LUCIJA_OPT_TEST_RATIO", "0.25"))

TOP_N = int(os.getenv("LUCIJA_OPT_TOP_N", "30"))

# Trenutna Lucija V1
RULES_V1 = {
    "avg_close_set_max": 0.55,
    "avg_close_set_min": 0.20,
    "avg_three_set_min": 0.15,
    "confidence_min": 80,
    "h2h_max": 0,
    "market_gap_min": 0.25,
    "quality_min": 72,
    "strength_gap_max": 30,
}

# Kandidati za optimizer.
# None pomeni: tega pogoja ne uporabi.
SEARCH_SPACE_COMMON = {
    "confidence_min": [75, 78, 80, 83, 86],
    "confidence_max": [None, 88, 90, 92, 95],

    "quality_min": [70, 72, 75, 78, 80],
    "quality_max": [None, 84, 88, 90, 92],

    "market_gap_min": [None, 0.20, 0.25, 0.30, 0.35, 0.40],
    "market_gap_max": [None, 0.45, 0.50, 0.60, 0.70],

    "strength_gap_max": [None, 20, 25, 30, 35, 40],
    "h2h_max": [None, 0, 1],

    "avg_three_set_min": [None, 0.10, 0.15, 0.20, 0.25],
    "avg_three_set_max": [None, 0.30, 0.35, 0.40, 0.45, 0.50],

    "avg_close_set_min": [None, 0.20, 0.25, 0.30, 0.35],
    "avg_close_set_max": [None, 0.35, 0.40, 0.45, 0.50, 0.55],

    "line_min": [None, 18.5, 19.5, 20.5],
    "line_max": [None, 20.5, 21.5, 22.5, 23.5],

    "odds_min": [None, 1.70, 1.80, 1.90, 1.95],
    "odds_max": [None, 2.05, 2.15, 2.25],

    "bookmakers_min": [None, 3, 5, 6, 7],

    "tour_level_in": [
        None,
        ["atp", "wta"],
        ["atp"],
        ["wta"],
        ["challenger"],
        ["itf"],
        ["challenger", "itf"],
    ],

    "gender_in": [
        None,
        ["men"],
        ["women"],
    ],
}


def ensure_dirs():
    os.makedirs(LUCIJA_DIR, exist_ok=True)


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


def norm(value):
    return str(value or "").strip().lower()


def normalize_result(value):
    r = norm(value)

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


def get_nested(data, keys, default=None):
    cur = data

    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)

    return cur if cur is not None else default


def avg_values(values, default=None):
    nums = []

    for v in values:
        x = safe_float(v, None)
        if x is not None:
            nums.append(x)

    if not nums:
        return default

    return round(sum(nums) / len(nums), 4)


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


def strength_gap(pick):
    direct = safe_float(pick.get("strength_gap"), None)
    if direct is not None:
        return abs(direct)

    first = safe_float(pick.get("first_strength_score"), None)
    second = safe_float(pick.get("second_strength_score"), None)

    if first is not None and second is not None:
        return abs(first - second)

    return None


def calc_metrics(pick):
    first_l10_three = get_nested(pick, ["first_form", "last_10", "three_set_rate"], None)
    second_l10_three = get_nested(pick, ["second_form", "last_10", "three_set_rate"], None)

    first_l10_close = get_nested(pick, ["first_form", "last_10", "close_set_rate"], None)
    second_l10_close = get_nested(pick, ["second_form", "last_10", "close_set_rate"], None)

    first_l10_total = get_nested(pick, ["first_form", "last_10", "avg_total_games"], None)
    second_l10_total = get_nested(pick, ["second_form", "last_10", "avg_total_games"], None)

    first_l10_over_21 = get_nested(pick, ["first_form", "last_10", "over_21_5_rate"], None)
    second_l10_over_21 = get_nested(pick, ["second_form", "last_10", "over_21_5_rate"], None)

    return {
        "side": norm(pick.get("side")),
        "tour_level": norm(pick.get("tour_level")),
        "gender": norm(pick.get("gender")),
        "line": safe_float(pick.get("line"), None),
        "odds": safe_float(pick.get("odds"), None),
        "bookmakers": safe_int(pick.get("bookmakers_used"), None),
        "confidence": safe_float(pick.get("confidence"), None),
        "quality": safe_float(pick.get("quality_score"), None),
        "edge": safe_float(pick.get("edge"), None),
        "market_gap": market_gap(pick),
        "strength_gap": strength_gap(pick),
        "h2h": safe_int(pick.get("h2h_matches"), None),
        "avg_three_set": avg_values([first_l10_three, second_l10_three], None),
        "avg_close_set": avg_values([first_l10_close, second_l10_close], None),
        "avg_total_games": avg_values([first_l10_total, second_l10_total], None),
        "avg_over_21_5_rate": avg_values([first_l10_over_21, second_l10_over_21], None),
    }


def check_min(value, threshold):
    if threshold is None:
        return True
    if value is None:
        return False
    return value >= threshold


def check_max(value, threshold):
    if threshold is None:
        return True
    if value is None:
        return False
    return value <= threshold


def check_in(value, allowed):
    if allowed is None:
        return True
    if value is None:
        return False
    return value in allowed


def passes_rules(pick, rules):
    m = calc_metrics(pick)

    checks = {
        "side": True if rules.get("side") is None else m["side"] == rules.get("side"),

        "tour_level_in": check_in(m["tour_level"], rules.get("tour_level_in")),
        "gender_in": check_in(m["gender"], rules.get("gender_in")),

        "confidence_min": check_min(m["confidence"], rules.get("confidence_min")),
        "confidence_max": check_max(m["confidence"], rules.get("confidence_max")),

        "quality_min": check_min(m["quality"], rules.get("quality_min")),
        "quality_max": check_max(m["quality"], rules.get("quality_max")),

        "market_gap_min": check_min(m["market_gap"], rules.get("market_gap_min")),
        "market_gap_max": check_max(m["market_gap"], rules.get("market_gap_max")),

        "strength_gap_max": check_max(m["strength_gap"], rules.get("strength_gap_max")),
        "h2h_max": check_max(m["h2h"], rules.get("h2h_max")),

        "avg_three_set_min": check_min(m["avg_three_set"], rules.get("avg_three_set_min")),
        "avg_three_set_max": check_max(m["avg_three_set"], rules.get("avg_three_set_max")),

        "avg_close_set_min": check_min(m["avg_close_set"], rules.get("avg_close_set_min")),
        "avg_close_set_max": check_max(m["avg_close_set"], rules.get("avg_close_set_max")),

        "line_min": check_min(m["line"], rules.get("line_min")),
        "line_max": check_max(m["line"], rules.get("line_max")),

        "odds_min": check_min(m["odds"], rules.get("odds_min")),
        "odds_max": check_max(m["odds"], rules.get("odds_max")),

        "bookmakers_min": check_min(m["bookmakers"], rules.get("bookmakers_min")),
    }

    return all(checks.values()), m, checks


def profit_for_pick(pick, stake=1.0):
    result = normalize_result(pick.get("result"))
    odds = safe_float(pick.get("odds"), None)

    if result == "win":
        return round(stake * ((odds or 1.0) - 1.0), 4)

    if result == "loss":
        return round(-stake, 4)

    return 0.0


def max_drawdown_from_profits(profits):
    peak = 0.0
    balance = 0.0
    max_dd = 0.0

    for p in profits:
        balance += p
        if balance > peak:
            peak = balance
        dd = balance - peak
        if dd < max_dd:
            max_dd = dd

    return round(max_dd, 4)


def streaks(picks):
    longest_win = 0
    longest_loss = 0
    current_win = 0
    current_loss = 0

    for p in picks:
        result = normalize_result(p.get("result"))

        if result == "win":
            current_win += 1
            current_loss = 0
        elif result == "loss":
            current_loss += 1
            current_win = 0
        else:
            current_win = 0
            current_loss = 0

        longest_win = max(longest_win, current_win)
        longest_loss = max(longest_loss, current_loss)

    return longest_win, longest_loss


def sort_key(p):
    return (
        str(p.get("date") or ""),
        str(p.get("time") or ""),
        str(p.get("match") or ""),
        str(p.get("pick_id") or ""),
    )


def evaluate(picks):
    ordered = sorted(picks, key=sort_key)
    settled = [p for p in ordered if is_settled(p)]

    wins = [p for p in settled if normalize_result(p.get("result")) == "win"]
    losses = [p for p in settled if normalize_result(p.get("result")) == "loss"]
    pushes = [p for p in settled if normalize_result(p.get("result")) == "push"]

    profits = [profit_for_pick(p, 1.0) for p in settled]

    profit = round(sum(profits), 4)
    stake_sum = len(settled)
    roi = round(profit / stake_sum * 100, 2) if stake_sum else 0.0
    winrate = round(len(wins) / max(1, len(wins) + len(losses)) * 100, 2)

    odds_values = [safe_float(p.get("odds"), None) for p in settled]
    odds_values = [x for x in odds_values if x is not None]
    avg_odds = round(sum(odds_values) / len(odds_values), 4) if odds_values else 0.0

    longest_win, longest_loss = streaks(settled)

    return {
        "picks": len(ordered),
        "settled": len(settled),
        "pending": len([p for p in ordered if not is_settled(p)]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "winrate": winrate,
        "profit": profit,
        "roi": roi,
        "avg_odds": avg_odds,
        "max_drawdown": max_drawdown_from_profits(profits),
        "longest_win_streak": longest_win,
        "longest_loss_streak": longest_loss,
    }


def train_test_split(picks, test_ratio=TEST_RATIO):
    ordered = sorted(picks, key=sort_key)

    if not ordered:
        return [], []

    cut = int(len(ordered) * (1.0 - test_ratio))
    cut = max(1, min(cut, len(ordered) - 1))

    return ordered[:cut], ordered[cut:]


def score_strategy(full_stats, train_stats, test_stats):
    if full_stats["settled"] < MIN_SETTLED:
        return None

    if test_stats["settled"] < MIN_TEST_PICKS:
        return None

    if full_stats["picks"] < MIN_PICKS:
        return None

    if test_stats["roi"] <= 0:
        return None

    train_test_gap_penalty = abs(train_stats["roi"] - test_stats["roi"]) * 0.50
    drawdown_penalty = abs(full_stats["max_drawdown"]) * 1.50

    score = (
        test_stats["roi"] * 2.0
        + full_stats["roi"] * 1.0
        + full_stats["profit"] * 0.40
        - drawdown_penalty
        - train_test_gap_penalty
    )

    return round(score, 6)


def clean_rules(rules):
    out = {}

    for k, v in rules.items():
        if v is not None:
            out[k] = v

    return out


def generate_rule_combinations(side):
    keys = list(SEARCH_SPACE_COMMON.keys())
    values = [SEARCH_SPACE_COMMON[k] for k in keys]

    for combo in itertools.product(*values):
        rules = {"side": side}

        for k, v in zip(keys, combo):
            rules[k] = v

        # Skip nelogične kombinacije.
        if rules.get("confidence_min") is not None and rules.get("confidence_max") is not None:
            if rules["confidence_min"] > rules["confidence_max"]:
                continue

        if rules.get("quality_min") is not None and rules.get("quality_max") is not None:
            if rules["quality_min"] > rules["quality_max"]:
                continue

        if rules.get("market_gap_min") is not None and rules.get("market_gap_max") is not None:
            if rules["market_gap_min"] > rules["market_gap_max"]:
                continue

        if rules.get("avg_three_set_min") is not None and rules.get("avg_three_set_max") is not None:
            if rules["avg_three_set_min"] > rules["avg_three_set_max"]:
                continue

        if rules.get("avg_close_set_min") is not None and rules.get("avg_close_set_max") is not None:
            if rules["avg_close_set_min"] > rules["avg_close_set_max"]:
                continue

        if rules.get("line_min") is not None and rules.get("line_max") is not None:
            if rules["line_min"] > rules["line_max"]:
                continue

        if rules.get("odds_min") is not None and rules.get("odds_max") is not None:
            if rules["odds_min"] > rules["odds_max"]:
                continue

        yield clean_rules(rules)


def filter_picks(picks, rules):
    out = []

    for p in picks:
        if not isinstance(p, dict):
            continue

        ok, metrics, checks = passes_rules(p, rules)

        if ok:
            x = dict(p)
            x["lucija_optimizer_metrics"] = metrics
            x["lucija_optimizer_checks"] = checks
            x["lucija_optimizer_rules"] = rules
            x["lucija_optimizer_profit"] = profit_for_pick(x, 1.0)
            out.append(x)

    return sorted(out, key=sort_key)


def evaluate_rules(picks, rules):
    selected = filter_picks(picks, rules)
    train, test = train_test_split(selected, TEST_RATIO)

    full_stats = evaluate(selected)
    train_stats = evaluate(train)
    test_stats = evaluate(test)

    score = score_strategy(full_stats, train_stats, test_stats)

    if score is None:
        return None

    return {
        "score": score,
        "rules": rules,
        "stats": full_stats,
        "train_75_stats": train_stats,
        "test_25_stats": test_stats,
    }


def optimize_side(picks, side):
    top = []
    checked = 0
    valid = 0

    for rules in generate_rule_combinations(side):
        checked += 1

        result = evaluate_rules(picks, rules)

        if result is None:
            continue

        valid += 1
        top.append(result)

        top = sorted(top, key=lambda x: x["score"], reverse=True)[:TOP_N]

    return {
        "side": side,
        "checked_combinations": checked,
        "valid_combinations": valid,
        "top": top,
        "best": top[0] if top else None,
    }


def group_bucket(value, buckets):
    x = safe_float(value, None)

    if x is None:
        return "unknown"

    for label, low, high in buckets:
        if low is None and x <= high:
            return label
        if high is None and x > low:
            return label
        if low is not None and high is not None and low < x <= high:
            return label

    return "other"


def breakdown(picks, name):
    groups = {}

    for p in picks:
        m = calc_metrics(p)

        if name == "side":
            key = m["side"] or "unknown"
        elif name == "tour_level":
            key = m["tour_level"] or "unknown"
        elif name == "gender":
            key = m["gender"] or "unknown"
        elif name == "bookmaker":
            key = str(p.get("best_bookmaker") or "unknown")
        elif name == "tournament":
            key = str(p.get("tournament") or "unknown")
        elif name == "line":
            key = group_bucket(m["line"], [
                ("<= 18.5", None, 18.5),
                ("18.5 - 19.5", 18.5, 19.5),
                ("19.5 - 20.5", 19.5, 20.5),
                ("20.5 - 21.5", 20.5, 21.5),
                ("21.5 - 22.5", 21.5, 22.5),
                ("> 22.5", 22.5, None),
            ])
        elif name == "odds":
            key = group_bucket(m["odds"], [
                ("<= 1.80", None, 1.80),
                ("1.80 - 1.95", 1.80, 1.95),
                ("1.95 - 2.05", 1.95, 2.05),
                ("2.05 - 2.20", 2.05, 2.20),
                ("> 2.20", 2.20, None),
            ])
        elif name == "confidence":
            key = group_bucket(m["confidence"], [
                ("<= 80", None, 80),
                ("80 - 83", 80, 83),
                ("83 - 86", 83, 86),
                ("86 - 89", 86, 89),
                ("89 - 92", 89, 92),
                ("> 92", 92, None),
            ])
        elif name == "quality":
            key = group_bucket(m["quality"], [
                ("<= 72", None, 72),
                ("72 - 76", 72, 76),
                ("76 - 80", 76, 80),
                ("80 - 84", 80, 84),
                ("84 - 88", 84, 88),
                ("> 88", 88, None),
            ])
        elif name == "market_gap":
            key = group_bucket(m["market_gap"], [
                ("<= 0.20", None, 0.20),
                ("0.20 - 0.25", 0.20, 0.25),
                ("0.25 - 0.35", 0.25, 0.35),
                ("0.35 - 0.45", 0.35, 0.45),
                ("0.45 - 0.60", 0.45, 0.60),
                ("> 0.60", 0.60, None),
            ])
        elif name == "strength_gap":
            key = group_bucket(m["strength_gap"], [
                ("<= 5", None, 5),
                ("5 - 10", 5, 10),
                ("10 - 15", 10, 15),
                ("15 - 20", 15, 20),
                ("20 - 25", 20, 25),
                ("25 - 30", 25, 30),
                ("> 30", 30, None),
            ])
        elif name == "avg_three_set":
            key = group_bucket(m["avg_three_set"], [
                ("<= 0.15", None, 0.15),
                ("0.15 - 0.20", 0.15, 0.20),
                ("0.20 - 0.25", 0.20, 0.25),
                ("0.25 - 0.30", 0.25, 0.30),
                ("0.30 - 0.35", 0.30, 0.35),
                ("0.35 - 0.45", 0.35, 0.45),
                ("> 0.45", 0.45, None),
            ])
        elif name == "avg_close_set":
            key = group_bucket(m["avg_close_set"], [
                ("<= 0.20", None, 0.20),
                ("0.20 - 0.30", 0.20, 0.30),
                ("0.30 - 0.35", 0.30, 0.35),
                ("0.35 - 0.40", 0.35, 0.40),
                ("0.40 - 0.50", 0.40, 0.50),
                ("> 0.50", 0.50, None),
            ])
        elif name == "avg_total_games":
            key = group_bucket(m["avg_total_games"], [
                ("<= 18", None, 18),
                ("18 - 19", 18, 19),
                ("19 - 20", 19, 20),
                ("20 - 21", 20, 21),
                ("21 - 22", 21, 22),
                ("22 - 23", 22, 23),
                ("> 23", 23, None),
            ])
        else:
            key = "unknown"

        groups.setdefault(key, []).append(p)

    rows = []

    for key, items in groups.items():
        s = evaluate(items)
        row = {"group": key}
        row.update(s)
        rows.append(row)

    return sorted(rows, key=lambda x: (x["profit"], x["roi"], x["picks"]), reverse=True)


def build_breakdowns(picks):
    return {
        "By side": breakdown(picks, "side"),
        "By tour level": breakdown(picks, "tour_level"),
        "By gender": breakdown(picks, "gender"),
        "By line bucket": breakdown(picks, "line"),
        "By odds bucket": breakdown(picks, "odds"),
        "By confidence bucket": breakdown(picks, "confidence"),
        "By quality bucket": breakdown(picks, "quality"),
        "By market gap bucket": breakdown(picks, "market_gap"),
        "By strength gap bucket": breakdown(picks, "strength_gap"),
        "By avg three set bucket": breakdown(picks, "avg_three_set"),
        "By avg close set bucket": breakdown(picks, "avg_close_set"),
        "By avg total games bucket": breakdown(picks, "avg_total_games"),
        "By bookmaker": breakdown(picks, "bookmaker"),
        "By tournament": breakdown(picks, "tournament"),
    }


def stats_line(label, stats):
    return (
        f"| {label} | {stats.get('picks', 0)} | {stats.get('settled', 0)} | "
        f"{stats.get('wins', 0)} | {stats.get('losses', 0)} | {stats.get('pushes', 0)} | "
        f"{stats.get('winrate', 0)}% | {stats.get('profit', 0)}u | "
        f"{stats.get('roi', 0)}% | {stats.get('avg_odds', 0)} | "
        f"{stats.get('max_drawdown', 0)}u |"
    )


def rules_to_text(rules):
    return json.dumps(rules, indent=2, ensure_ascii=False)


def top_table(title, top):
    lines = []
    lines.append(f"## {title}")
    lines.append("")

    if not top:
        lines.append("No valid strategy found with current minimum requirements.")
        lines.append("")
        return lines

    lines.append("| Rank | Score | Picks | Test picks | ROI | Test ROI | Profit | Max DD | Rules |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    for i, item in enumerate(top[:TOP_N], start=1):
        rules_short = ", ".join([f"{k}={v}" for k, v in item["rules"].items()])
        lines.append(
            f"| {i} | {item['score']} | {item['stats']['picks']} | "
            f"{item['test_25_stats']['picks']} | {item['stats']['roi']}% | "
            f"{item['test_25_stats']['roi']}% | {item['stats']['profit']}u | "
            f"{item['stats']['max_drawdown']}u | `{rules_short}` |"
        )

    lines.append("")
    return lines


def breakdown_section(title, breakdowns):
    lines = []
    lines.append(f"## {title}")
    lines.append("")

    if not breakdowns:
        lines.append("No breakdowns.")
        lines.append("")
        return lines

    for name, rows in breakdowns.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| Group | Picks | W | L | P | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for r in rows[:30]:
            lines.append(
                f"| {r['group']} | {r['picks']} | {r['wins']} | {r['losses']} | {r['pushes']} | "
                f"{r['winrate']}% | {r['profit']}u | {r['roi']}% | {r['avg_odds']} | {r['max_drawdown']}u |"
            )

        lines.append("")

    return lines


def build_report(summary, v1_eval, under_result, over_result, under_breakdowns, over_breakdowns):
    lines = []

    lines.append("# Lucija Optimizer Report")
    lines.append("")
    lines.append(f"Generated: `{summary['generated_at']}`")
    lines.append("")
    lines.append(f"Source file: `{summary['source_file']}`")
    lines.append(f"Source count: **{summary['source_count']}**")
    lines.append(f"Settled count: **{summary['settled_count']}**")
    lines.append("")
    lines.append("Minimum optimizer requirements:")
    lines.append("")
    lines.append(f"- Minimum picks: **{MIN_PICKS}**")
    lines.append(f"- Minimum settled: **{MIN_SETTLED}**")
    lines.append(f"- Minimum test picks: **{MIN_TEST_PICKS}**")
    lines.append(f"- Test ratio: **{TEST_RATIO}**")
    lines.append("")

    lines.append("## Main Results")
    lines.append("")
    lines.append("| Strategy | Picks | Settled | W | L | P | Winrate | Profit | ROI | Avg odds | Max DD |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(stats_line("Baseline all settled", summary["baseline"]))
    lines.append(stats_line("V1 current Lucija", v1_eval["stats"]))

    if under_result["best"]:
        lines.append(stats_line("V2 best UNDER optimizer", under_result["best"]["stats"]))
    else:
        lines.append("| V2 best UNDER optimizer | 0 | 0 | 0 | 0 | 0 | 0% | 0u | 0% | 0 | 0u |")

    if over_result["best"]:
        lines.append(stats_line("V3 best OVER optimizer", over_result["best"]["stats"]))
    else:
        lines.append("| V3 best OVER optimizer | 0 | 0 | 0 | 0 | 0 | 0% | 0u | 0% | 0 | 0u |")

    lines.append("")

    lines.append("## V1 Current Lucija Rules")
    lines.append("")
    lines.append("```json")
    lines.append(rules_to_text(RULES_V1))
    lines.append("```")
    lines.append("")

    if under_result["best"]:
        lines.append("## Best UNDER Rules")
        lines.append("")
        lines.append("```json")
        lines.append(rules_to_text(under_result["best"]["rules"]))
        lines.append("```")
        lines.append("")
        lines.append("### Best UNDER Train/Test")
        lines.append("")
        lines.append("| Split | Picks | Settled | W | L | P | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        lines.append(stats_line("Full", under_result["best"]["stats"]))
        lines.append(stats_line("Train 75%", under_result["best"]["train_75_stats"]))
        lines.append(stats_line("Test 25%", under_result["best"]["test_25_stats"]))
        lines.append("")

    if over_result["best"]:
        lines.append("## Best OVER Rules")
        lines.append("")
        lines.append("```json")
        lines.append(rules_to_text(over_result["best"]["rules"]))
        lines.append("```")
        lines.append("")
        lines.append("### Best OVER Train/Test")
        lines.append("")
        lines.append("| Split | Picks | Settled | W | L | P | Winrate | Profit | ROI | Avg odds | Max DD |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        lines.append(stats_line("Full", over_result["best"]["stats"]))
        lines.append(stats_line("Train 75%", over_result["best"]["train_75_stats"]))
        lines.append(stats_line("Test 25%", over_result["best"]["test_25_stats"]))
        lines.append("")

    lines.extend(top_table("Top UNDER Strategies", under_result["top"]))
    lines.extend(top_table("Top OVER Strategies", over_result["top"]))

    lines.extend(breakdown_section("Best UNDER Breakdowns", under_breakdowns))
    lines.extend(breakdown_section("Best OVER Breakdowns", over_breakdowns))

    return "\n".join(lines)


def main():
    ensure_dirs()

    source = load_json(SOURCE_FILE, [])
    if not isinstance(source, list):
        source = []

    settled_source = [p for p in source if isinstance(p, dict) and is_settled(p)]

    baseline = evaluate(settled_source)

    v1_picks = filter_picks(source, RULES_V1)
    v1_train, v1_test = train_test_split(v1_picks, TEST_RATIO)
    v1_eval = {
        "rules": RULES_V1,
        "stats": evaluate(v1_picks),
        "train_75_stats": evaluate(v1_train),
        "test_25_stats": evaluate(v1_test),
    }

    print("")
    print("LUCIJA OPTIMIZER START")
    print(f"Source file: {SOURCE_FILE}")
    print(f"Source count: {len(source)}")
    print(f"Settled count: {len(settled_source)}")
    print(f"Minimum picks: {MIN_PICKS}")
    print("")

    print("Optimizing UNDER...")
    under_result = optimize_side(settled_source, "under")

    print("Optimizing OVER...")
    over_result = optimize_side(settled_source, "over")

    under_best_picks = []
    over_best_picks = []

    under_breakdowns = {}
    over_breakdowns = {}

    if under_result["best"]:
        under_best_picks = filter_picks(source, under_result["best"]["rules"])
        under_breakdowns = build_breakdowns(under_best_picks)

    if over_result["best"]:
        over_best_picks = filter_picks(source, over_result["best"]["rules"])
        over_breakdowns = build_breakdowns(over_best_picks)

    summary = {
        "generated_at": now_iso(),
        "source_file": SOURCE_FILE,
        "source_count": len(source),
        "settled_count": len(settled_source),
        "min_picks": MIN_PICKS,
        "min_settled": MIN_SETTLED,
        "min_test_picks": MIN_TEST_PICKS,
        "test_ratio": TEST_RATIO,
        "baseline": baseline,
        "v1_current_lucija": v1_eval,
        "v2_best_under": under_result["best"],
        "v3_best_over": over_result["best"],
        "under_checked_combinations": under_result["checked_combinations"],
        "under_valid_combinations": under_result["valid_combinations"],
        "over_checked_combinations": over_result["checked_combinations"],
        "over_valid_combinations": over_result["valid_combinations"],
    }

    report = build_report(
        summary=summary,
        v1_eval=v1_eval,
        under_result=under_result,
        over_result=over_result,
        under_breakdowns=under_breakdowns,
        over_breakdowns=over_breakdowns,
    )

    save_json(SUMMARY_FILE, summary)
    save_json(BEST_UNDER_FILE, under_result["best"] or {})
    save_json(BEST_OVER_FILE, over_result["best"] or {})
    save_json(TOP_UNDER_FILE, under_result["top"])
    save_json(TOP_OVER_FILE, over_result["top"])
    save_json(V1_PICKS_FILE, v1_picks)
    save_json(BEST_UNDER_PICKS_FILE, under_best_picks)
    save_json(BEST_OVER_PICKS_FILE, over_best_picks)
    save_json(DEBUG_FILE, {
        "generated_at": now_iso(),
        "source_file": SOURCE_FILE,
        "search_space_common": SEARCH_SPACE_COMMON,
        "rules_v1": RULES_V1,
        "min_picks": MIN_PICKS,
        "min_settled": MIN_SETTLED,
        "min_test_picks": MIN_TEST_PICKS,
        "test_ratio": TEST_RATIO,
        "note": "None means condition disabled.",
    })
    save_text(REPORT_FILE, report)

    print("")
    print("LUCIJA OPTIMIZER DONE")
    print(f"V1 picks: {v1_eval['stats']['picks']}, ROI: {v1_eval['stats']['roi']}%")

    if under_result["best"]:
        print(
            f"Best UNDER: picks {under_result['best']['stats']['picks']}, "
            f"ROI {under_result['best']['stats']['roi']}%, "
            f"test ROI {under_result['best']['test_25_stats']['roi']}%, "
            f"score {under_result['best']['score']}"
        )
    else:
        print("Best UNDER: no valid strategy found")

    if over_result["best"]:
        print(
            f"Best OVER: picks {over_result['best']['stats']['picks']}, "
            f"ROI {over_result['best']['stats']['roi']}%, "
            f"test ROI {over_result['best']['test_25_stats']['roi']}%, "
            f"score {over_result['best']['score']}"
        )
    else:
        print("Best OVER: no valid strategy found")

    print("")
    print(f"Report: {REPORT_FILE}")
    print(f"Summary: {SUMMARY_FILE}")
    print(f"Best under: {BEST_UNDER_FILE}")
    print(f"Best over: {BEST_OVER_FILE}")


if __name__ == "__main__":
    main()

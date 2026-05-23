#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI77 Tennis Totals Results Optimizer
-----------------------------------
Reads tennis_totals_results.json and searches many filter combinations to find
profitable, more stable rule sets and staking variants.

Usage examples:
  python optimize_tennis_totals_results.py --input data/tennis_totals_results.json --iterations 1000000
  python optimize_tennis_totals_results.py --input https://raw.githubusercontent.com/jakobm121/Ai/refs/heads/main/data/tennis_totals_results.json --iterations 500000 --min-full 25 --min-test 8

Outputs:
  data/tennis_totals_optimizer_report.json
  data/tennis_totals_best_rules.json
  data/tennis_totals_staking_comparison.json
  data/tennis_totals_calibration.json
  data/tennis_totals_optimizer_top_rules.csv
  data/tennis_totals_optimizer_report.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


SETTLED_WIN = {"win", "won", "w", "profit"}
SETTLED_LOSS = {"loss", "lost", "l"}
SETTLED_VOID = {"void", "push", "cancelled", "canceled", "refund", "no bet", "nobet"}

OUT_DIR_DEFAULT = "data"


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def safe_int(v: Any, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(float(v))
    except Exception:
        return default


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def parse_date(value: Any) -> str:
    s = str(value or "")[:10]
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s
    return "0000-00-00"


def month_key(date_s: str) -> str:
    return date_s[:7] if len(date_s) >= 7 else "unknown"


def week_key(date_s: str) -> str:
    try:
        d = datetime.strptime(date_s[:10], "%Y-%m-%d").date()
        iso = d.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    except Exception:
        return "unknown"


def load_json_any(path_or_url: str) -> Any:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        if requests is None:
            raise RuntimeError("requests package is missing. Install requests or use a local file.")
        res = requests.get(path_or_url, timeout=40)
        res.raise_for_status()
        return res.json()
    with open(path_or_url, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def nested_get(d: Dict[str, Any], path: str, default: Any = None) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur.get(part)
    return cur


def normalize_result(p: Dict[str, Any]) -> Optional[str]:
    r = str(p.get("result") or p.get("settled_result") or "").strip().lower()
    if r in SETTLED_WIN:
        return "win"
    if r in SETTLED_LOSS:
        return "loss"
    if r in SETTLED_VOID:
        return "void"
    # Fallback using explicit profit if settled result naming is different.
    if p.get("profit") is not None and str(p.get("settled_status") or "").lower() not in {"", "pending"}:
        pr = safe_float(p.get("profit"))
        if pr > 0:
            return "win"
        if pr < 0:
            return "loss"
        return "void"
    return None


def flat_profit(result: str, odds: float, stake: float = 1.0) -> float:
    if result == "win":
        return stake * (odds - 1.0)
    if result == "loss":
        return -stake
    return 0.0


def implied_break_even(odds: float) -> float:
    return 1.0 / odds if odds > 1.0 else 0.0


def kelly_fraction(model_prob: float, odds: float) -> float:
    b = odds - 1.0
    if b <= 0:
        return 0.0
    q = 1.0 - model_prob
    return max(0.0, ((b * model_prob) - q) / b)


def pct(x: float) -> float:
    return round(100.0 * x, 2)


@dataclass(frozen=True)
class Pick:
    idx: int
    pick_id: str
    date: str
    week: str
    month: str
    match: str
    result: str
    side: str
    odds: float
    line: float
    stake_original: float
    profit_original: float
    flat_profit_1u: float
    model_prob: float
    implied_prob: float
    edge: float
    confidence: float
    quality: float
    expected_total_games: float
    expected_margin: float
    abs_expected_margin: float
    bookmakers_used: int
    market_median_odds: float
    tour_level: str
    gender: str
    qualification: bool
    event_type: str
    tournament: str
    round_name: str
    best_bookmaker: str
    market_gap: float
    market_favorite_side: str
    first_strength: float
    second_strength: float
    strength_gap: float
    h2h_matches: int
    first_l5_avg_total: float
    second_l5_avg_total: float
    first_l10_avg_total: float
    second_l10_avg_total: float
    first_l10_median_total: float
    second_l10_median_total: float
    first_l10_three_set_rate: float
    second_l10_three_set_rate: float
    avg_l10_three_set_rate: float
    first_l10_close_set_rate: float
    second_l10_close_set_rate: float
    avg_l10_close_set_rate: float
    first_l10_over_21_5_rate: float
    second_l10_over_21_5_rate: float
    avg_l10_over_21_5_rate: float
    first_l10_matches: int
    second_l10_matches: int
    min_recent_matches: int
    total_games: float


def make_pick(raw: Dict[str, Any], idx: int) -> Optional[Pick]:
    result = normalize_result(raw)
    if result is None:
        return None
    odds = safe_float(raw.get("odds"), 0.0)
    if odds <= 1.0:
        return None
    side = str(raw.get("side") or "").strip().lower()
    if side not in {"over", "under"}:
        if "over" in str(raw.get("bet") or "").lower():
            side = "over"
        elif "under" in str(raw.get("bet") or "").lower():
            side = "under"
        else:
            return None

    date_s = parse_date(raw.get("date") or raw.get("created_at") or raw.get("settled_at"))
    stake_original = safe_float(raw.get("stake"), 1.0)
    profit_original = raw.get("profit")
    if profit_original is None:
        profit_original = flat_profit(result, odds, stake_original)
    profit_original = safe_float(profit_original, 0.0)

    first_strength = safe_float(raw.get("first_strength_score"))
    second_strength = safe_float(raw.get("second_strength_score"))

    f_l5_avg = safe_float(nested_get(raw, "first_form.last_5.avg_total_games"))
    s_l5_avg = safe_float(nested_get(raw, "second_form.last_5.avg_total_games"))
    f_l10_avg = safe_float(nested_get(raw, "first_form.last_10.avg_total_games"))
    s_l10_avg = safe_float(nested_get(raw, "second_form.last_10.avg_total_games"))
    f_l10_med = safe_float(nested_get(raw, "first_form.last_10.median_total_games"))
    s_l10_med = safe_float(nested_get(raw, "second_form.last_10.median_total_games"))
    f_l10_3 = safe_float(nested_get(raw, "first_form.last_10.three_set_rate"))
    s_l10_3 = safe_float(nested_get(raw, "second_form.last_10.three_set_rate"))
    f_l10_close = safe_float(nested_get(raw, "first_form.last_10.close_set_rate"))
    s_l10_close = safe_float(nested_get(raw, "second_form.last_10.close_set_rate"))
    f_l10_o215 = safe_float(nested_get(raw, "first_form.last_10.over_21_5_rate"))
    s_l10_o215 = safe_float(nested_get(raw, "second_form.last_10.over_21_5_rate"))
    f_l10_n = safe_int(nested_get(raw, "first_form.last_10.matches"))
    s_l10_n = safe_int(nested_get(raw, "second_form.last_10.matches"))

    return Pick(
        idx=idx,
        pick_id=str(raw.get("pick_id") or raw.get("event_key") or idx),
        date=date_s,
        week=week_key(date_s),
        month=month_key(date_s),
        match=str(raw.get("match") or ""),
        result=result,
        side=side,
        odds=odds,
        line=safe_float(raw.get("line")),
        stake_original=stake_original,
        profit_original=profit_original,
        flat_profit_1u=flat_profit(result, odds, 1.0),
        model_prob=safe_float(raw.get("model_prob")),
        implied_prob=safe_float(raw.get("implied_prob"), implied_break_even(odds)),
        edge=safe_float(raw.get("edge"), safe_float(raw.get("model_prob")) - implied_break_even(odds)),
        confidence=safe_float(raw.get("confidence")),
        quality=safe_float(raw.get("quality_score")),
        expected_total_games=safe_float(raw.get("expected_total_games")),
        expected_margin=safe_float(raw.get("expected_margin")),
        abs_expected_margin=abs(safe_float(raw.get("expected_margin"))),
        bookmakers_used=safe_int(raw.get("bookmakers_used")),
        market_median_odds=safe_float(raw.get("market_median_odds")),
        tour_level=str(raw.get("tour_level") or "unknown").lower(),
        gender=str(raw.get("gender") or "unknown").lower(),
        qualification=bool(raw.get("qualification")),
        event_type=str(raw.get("event_type") or "").lower(),
        tournament=str(raw.get("tournament") or ""),
        round_name=str(raw.get("round") or raw.get("round_name") or ""),
        best_bookmaker=str(raw.get("best_bookmaker") or "unknown"),
        market_gap=safe_float(nested_get(raw, "market_info.market_gap")),
        market_favorite_side=str(nested_get(raw, "market_info.market_favorite_side", "unknown") or "unknown").lower(),
        first_strength=first_strength,
        second_strength=second_strength,
        strength_gap=abs(first_strength - second_strength),
        h2h_matches=safe_int(raw.get("h2h_matches")),
        first_l5_avg_total=f_l5_avg,
        second_l5_avg_total=s_l5_avg,
        first_l10_avg_total=f_l10_avg,
        second_l10_avg_total=s_l10_avg,
        first_l10_median_total=f_l10_med,
        second_l10_median_total=s_l10_med,
        first_l10_three_set_rate=f_l10_3,
        second_l10_three_set_rate=s_l10_3,
        avg_l10_three_set_rate=(f_l10_3 + s_l10_3) / 2.0,
        first_l10_close_set_rate=f_l10_close,
        second_l10_close_set_rate=s_l10_close,
        avg_l10_close_set_rate=(f_l10_close + s_l10_close) / 2.0,
        first_l10_over_21_5_rate=f_l10_o215,
        second_l10_over_21_5_rate=s_l10_o215,
        avg_l10_over_21_5_rate=(f_l10_o215 + s_l10_o215) / 2.0,
        first_l10_matches=f_l10_n,
        second_l10_matches=s_l10_n,
        min_recent_matches=min(f_l10_n, s_l10_n) if f_l10_n and s_l10_n else 0,
        total_games=safe_float(raw.get("total_games")),
    )


@dataclass(frozen=True)
class Rule:
    side: str = "any"
    odds_min: Optional[float] = None
    odds_max: Optional[float] = None
    line_min: Optional[float] = None
    line_max: Optional[float] = None
    edge_min: Optional[float] = None
    edge_max: Optional[float] = None
    confidence_min: Optional[float] = None
    quality_min: Optional[float] = None
    expected_margin_min: Optional[float] = None
    expected_margin_max: Optional[float] = None
    abs_margin_min: Optional[float] = None
    bookmakers_min: Optional[int] = None
    market_gap_min: Optional[float] = None
    market_gap_max: Optional[float] = None
    strength_gap_min: Optional[float] = None
    strength_gap_max: Optional[float] = None
    h2h_min: Optional[int] = None
    h2h_max: Optional[int] = None
    min_recent_matches_min: Optional[int] = None
    avg_three_set_min: Optional[float] = None
    avg_three_set_max: Optional[float] = None
    avg_close_set_min: Optional[float] = None
    avg_close_set_max: Optional[float] = None
    avg_over_21_5_min: Optional[float] = None
    avg_over_21_5_max: Optional[float] = None
    tour_level: str = "any"
    gender: str = "any"
    qualification: str = "any"  # any / true / false
    market_favorite_side: str = "any"
    best_bookmaker: str = "any"

    def to_key(self) -> str:
        s = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.md5(s.encode("utf-8")).hexdigest()


def passes_rule(p: Pick, r: Rule) -> bool:
    if r.side != "any" and p.side != r.side:
        return False
    if r.tour_level != "any" and p.tour_level != r.tour_level:
        return False
    if r.gender != "any" and p.gender != r.gender:
        return False
    if r.qualification == "true" and not p.qualification:
        return False
    if r.qualification == "false" and p.qualification:
        return False
    if r.market_favorite_side != "any" and p.market_favorite_side != r.market_favorite_side:
        return False
    if r.best_bookmaker != "any" and p.best_bookmaker != r.best_bookmaker:
        return False

    checks = [
        (r.odds_min, p.odds, ">="), (r.odds_max, p.odds, "<="),
        (r.line_min, p.line, ">="), (r.line_max, p.line, "<="),
        (r.edge_min, p.edge, ">="), (r.edge_max, p.edge, "<="),
        (r.confidence_min, p.confidence, ">="), (r.quality_min, p.quality, ">="),
        (r.expected_margin_min, p.expected_margin, ">="), (r.expected_margin_max, p.expected_margin, "<="),
        (r.abs_margin_min, p.abs_expected_margin, ">="),
        (r.bookmakers_min, p.bookmakers_used, ">="),
        (r.market_gap_min, p.market_gap, ">="), (r.market_gap_max, p.market_gap, "<="),
        (r.strength_gap_min, p.strength_gap, ">="), (r.strength_gap_max, p.strength_gap, "<="),
        (r.h2h_min, p.h2h_matches, ">="), (r.h2h_max, p.h2h_matches, "<="),
        (r.min_recent_matches_min, p.min_recent_matches, ">="),
        (r.avg_three_set_min, p.avg_l10_three_set_rate, ">="), (r.avg_three_set_max, p.avg_l10_three_set_rate, "<="),
        (r.avg_close_set_min, p.avg_l10_close_set_rate, ">="), (r.avg_close_set_max, p.avg_l10_close_set_rate, "<="),
        (r.avg_over_21_5_min, p.avg_l10_over_21_5_rate, ">="), (r.avg_over_21_5_max, p.avg_l10_over_21_5_rate, "<="),
    ]
    for threshold, value, op in checks:
        if threshold is None:
            continue
        if op == ">=" and value < threshold:
            return False
        if op == "<=" and value > threshold:
            return False
    return True


def equity_curve(profits: Sequence[float]) -> List[float]:
    cur = 0.0
    out = []
    for pr in profits:
        cur += pr
        out.append(round(cur, 6))
    return out


def max_drawdown(curve: Sequence[float]) -> float:
    if not curve:
        return 0.0
    peak = 0.0
    max_dd = 0.0
    for x in curve:
        peak = max(peak, x)
        max_dd = min(max_dd, x - peak)
    return round(max_dd, 6)


def longest_losing_streak(picks: Sequence[Pick]) -> int:
    best = 0
    cur = 0
    for p in picks:
        if p.result == "loss":
            cur += 1
            best = max(best, cur)
        elif p.result == "win":
            cur = 0
    return best


def profit_by_key(picks: Sequence[Pick], key: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for p in picks:
        k = getattr(p, key)
        out[k] = out.get(k, 0.0) + p.flat_profit_1u
    return {k: round(v, 6) for k, v in sorted(out.items())}


def backtest_metrics(picks: Sequence[Pick], profit_attr: str = "flat_profit_1u") -> Dict[str, Any]:
    n = len(picks)
    if n == 0:
        return {
            "picks": 0, "wins": 0, "losses": 0, "voids": 0, "winrate": 0.0, "avg_odds": 0.0,
            "profit": 0.0, "roi": 0.0, "max_drawdown": 0.0, "longest_losing_streak": 0,
            "profit_by_month": {}, "profit_by_week": {}, "profit_by_side": {}, "months_positive_ratio": 0.0,
        }
    profits = [safe_float(getattr(p, profit_attr)) for p in picks]
    curve = equity_curve(profits)
    wins = sum(1 for p in picks if p.result == "win")
    losses = sum(1 for p in picks if p.result == "loss")
    voids = sum(1 for p in picks if p.result == "void")
    staked = sum(1.0 for p in picks if p.result != "void")
    profit = sum(profits)
    by_month = profit_by_key(picks, "month")
    pos_months = sum(1 for v in by_month.values() if v > 0)
    return {
        "picks": n,
        "wins": wins,
        "losses": losses,
        "voids": voids,
        "winrate": round(wins / max(1, wins + losses), 4),
        "avg_odds": round(sum(p.odds for p in picks) / n, 4),
        "avg_edge": round(sum(p.edge for p in picks) / n, 5),
        "avg_confidence": round(sum(p.confidence for p in picks) / n, 3),
        "avg_quality": round(sum(p.quality for p in picks) / n, 3),
        "profit": round(profit, 6),
        "roi": round(profit / max(1e-9, staked), 6),
        "max_drawdown": max_drawdown(curve),
        "longest_losing_streak": longest_losing_streak(picks),
        "profit_by_month": by_month,
        "profit_by_week": profit_by_key(picks, "week"),
        "profit_by_side": {"over": round(sum(p.flat_profit_1u for p in picks if p.side == "over"), 6),
                           "under": round(sum(p.flat_profit_1u for p in picks if p.side == "under"), 6)},
        "months_positive_ratio": round(pos_months / max(1, len(by_month)), 4),
        "equity_curve_last": curve[-10:],
    }


def split_train_test(picks: Sequence[Pick], train_ratio: float) -> Tuple[List[Pick], List[Pick]]:
    arr = sorted(picks, key=lambda p: (p.date, p.idx))
    cut = max(1, min(len(arr) - 1, int(len(arr) * train_ratio))) if len(arr) >= 2 else len(arr)
    return arr[:cut], arr[cut:]


def walk_forward_score(selected: Sequence[Pick], folds: int = 4) -> Dict[str, Any]:
    arr = sorted(selected, key=lambda p: (p.date, p.idx))
    n = len(arr)
    if n < folds * 4:
        return {"folds": 0, "positive_folds": 0, "positive_ratio": 0.0, "fold_roi": []}
    fold_size = max(1, n // folds)
    rois = []
    profits = []
    for i in range(folds):
        part = arr[i * fold_size:] if i == folds - 1 else arr[i * fold_size:(i + 1) * fold_size]
        m = backtest_metrics(part)
        rois.append(m["roi"])
        profits.append(m["profit"])
    pos = sum(1 for p in profits if p > 0)
    return {
        "folds": folds,
        "positive_folds": pos,
        "positive_ratio": round(pos / folds, 4),
        "fold_roi": [round(x, 6) for x in rois],
        "fold_profit": [round(x, 6) for x in profits],
    }


def rule_complexity(r: Rule) -> int:
    d = asdict(r)
    c = 0
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, str) and v == "any":
            continue
        c += 1
    return c


def score_rule(full: Dict[str, Any], train: Dict[str, Any], test: Dict[str, Any], wf: Dict[str, Any], complexity: int) -> float:
    # Scoring favors out-of-sample ROI/profit, sample size and stability; penalizes drawdown and complexity.
    full_roi = full["roi"]
    test_roi = test["roi"]
    full_profit = full["profit"]
    test_profit = test["profit"]
    n = full["picks"]
    dd = abs(full["max_drawdown"])
    size_bonus = min(20.0, math.log(max(1, n), 1.35))
    stability = 20.0 * full.get("months_positive_ratio", 0.0) + 15.0 * wf.get("positive_ratio", 0.0)
    roi_score = 180.0 * max(-0.20, min(0.50, full_roi)) + 240.0 * max(-0.20, min(0.50, test_roi))
    profit_score = 1.2 * full_profit + 2.0 * test_profit
    dd_penalty = 2.5 * dd
    complexity_penalty = 1.2 * complexity
    return round(roi_score + profit_score + size_bonus + stability - dd_penalty - complexity_penalty, 4)


def evaluate_rule(rule: Rule, all_picks: Sequence[Pick], train_pool: Sequence[Pick], test_pool: Sequence[Pick], min_full: int, min_test: int) -> Optional[Dict[str, Any]]:
    selected_full = [p for p in all_picks if passes_rule(p, rule)]
    if len(selected_full) < min_full:
        return None
    selected_test = [p for p in test_pool if passes_rule(p, rule)]
    if len(selected_test) < min_test:
        return None
    selected_train = [p for p in train_pool if passes_rule(p, rule)]
    full_m = backtest_metrics(selected_full)
    test_m = backtest_metrics(selected_test)
    train_m = backtest_metrics(selected_train)

    # Keep some negative test rules in report? No: for live use we reject overfit/negative OOS.
    if full_m["profit"] <= 0 or test_m["profit"] <= 0:
        return None
    if full_m["roi"] <= 0 or test_m["roi"] <= 0:
        return None

    wf = walk_forward_score(selected_full, folds=4)
    complexity = rule_complexity(rule)
    return {
        "rule_id": rule.to_key(),
        "score": score_rule(full_m, train_m, test_m, wf, complexity),
        "complexity": complexity,
        "rule": asdict(rule),
        "full": full_m,
        "train": train_m,
        "test": test_m,
        "walk_forward": wf,
        "example_matches": [p.match for p in selected_full[:8]],
    }


def uniq_sorted(values: Iterable[Any]) -> List[Any]:
    return sorted(set(v for v in values if v is not None and str(v) != ""))


def random_choice_or_any(rng: random.Random, values: Sequence[str], p_any: float = 0.65) -> str:
    if not values or rng.random() < p_any:
        return "any"
    return str(rng.choice(list(values)))


def random_range(rng: random.Random, low_values: Sequence[float], high_values: Sequence[float], p_none: float = 0.45) -> Tuple[Optional[float], Optional[float]]:
    lo = None if rng.random() < p_none else rng.choice(list(low_values))
    hi = None if rng.random() < p_none else rng.choice(list(high_values))
    if lo is not None and hi is not None and lo > hi:
        lo, hi = hi, lo
    return lo, hi


def generate_random_rule(rng: random.Random, domains: Dict[str, List[Any]]) -> Rule:
    side = random_choice_or_any(rng, ["over", "under"], p_any=0.35)

    odds_min, odds_max = random_range(rng, domains["odds_min"], domains["odds_max"], p_none=0.20)
    if odds_min is None and odds_max is None and rng.random() < 0.75:
        odds_min = rng.choice(domains["odds_min"])
        odds_max = rng.choice(domains["odds_max"])
        if odds_min > odds_max:
            odds_min, odds_max = odds_max, odds_min

    line_min, line_max = random_range(rng, domains["line_min"], domains["line_max"], p_none=0.55)

    edge_min = None if rng.random() < 0.18 else rng.choice(domains["edge_min"])
    edge_max = None if rng.random() < 0.92 else rng.choice(domains["edge_max"])
    if edge_min is not None and edge_max is not None and edge_min > edge_max:
        edge_min, edge_max = edge_max, edge_min

    expected_margin_min = None
    expected_margin_max = None
    abs_margin_min = None
    # Side-aware expected margin filters.
    if side == "over":
        expected_margin_min = None if rng.random() < 0.35 else rng.choice(domains["pos_margin_min"])
    elif side == "under":
        expected_margin_max = None if rng.random() < 0.35 else rng.choice(domains["neg_margin_max"])
    else:
        abs_margin_min = None if rng.random() < 0.45 else rng.choice(domains["abs_margin_min"])

    return Rule(
        side=side,
        odds_min=odds_min,
        odds_max=odds_max,
        line_min=line_min,
        line_max=line_max,
        edge_min=edge_min,
        edge_max=edge_max,
        confidence_min=None if rng.random() < 0.35 else rng.choice(domains["confidence_min"]),
        quality_min=None if rng.random() < 0.35 else rng.choice(domains["quality_min"]),
        expected_margin_min=expected_margin_min,
        expected_margin_max=expected_margin_max,
        abs_margin_min=abs_margin_min,
        bookmakers_min=None if rng.random() < 0.45 else rng.choice(domains["bookmakers_min"]),
        market_gap_min=None if rng.random() < 0.82 else rng.choice(domains["market_gap_min"]),
        market_gap_max=None if rng.random() < 0.55 else rng.choice(domains["market_gap_max"]),
        strength_gap_min=None if rng.random() < 0.78 else rng.choice(domains["strength_gap_min"]),
        strength_gap_max=None if rng.random() < 0.58 else rng.choice(domains["strength_gap_max"]),
        h2h_min=None if rng.random() < 0.82 else rng.choice(domains["h2h_min"]),
        h2h_max=None if rng.random() < 0.88 else rng.choice(domains["h2h_max"]),
        min_recent_matches_min=None if rng.random() < 0.68 else rng.choice(domains["recent_min"]),
        avg_three_set_min=None if rng.random() < 0.82 else rng.choice(domains["rate_min"]),
        avg_three_set_max=None if rng.random() < 0.82 else rng.choice(domains["rate_max"]),
        avg_close_set_min=None if rng.random() < 0.84 else rng.choice(domains["rate_min"]),
        avg_close_set_max=None if rng.random() < 0.84 else rng.choice(domains["rate_max"]),
        avg_over_21_5_min=None if rng.random() < 0.84 else rng.choice(domains["rate_min"]),
        avg_over_21_5_max=None if rng.random() < 0.84 else rng.choice(domains["rate_max"]),
        tour_level=random_choice_or_any(rng, domains["tour_level"], p_any=0.72),
        gender=random_choice_or_any(rng, domains["gender"], p_any=0.78),
        qualification=random_choice_or_any(rng, ["true", "false"], p_any=0.82),
        market_favorite_side=random_choice_or_any(rng, domains["market_favorite_side"], p_any=0.82),
        best_bookmaker=random_choice_or_any(rng, domains["best_bookmaker"], p_any=0.93),
    )


def generate_seed_rules(domains: Dict[str, List[Any]]) -> List[Rule]:
    rules: List[Rule] = []
    sides = ["any", "over", "under"]
    for side in sides:
        for edge in [None, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]:
            for q in [None, 60, 65, 70, 75, 80, 85]:
                for conf in [None, 60, 65, 70, 75, 80, 85]:
                    rules.append(Rule(side=side, edge_min=edge, quality_min=q, confidence_min=conf))
    for side in ["over", "under"]:
        for odds_min, odds_max in [(1.55, 2.20), (1.65, 2.20), (1.70, 2.15), (1.75, 2.10), (1.80, 2.20)]:
            for edge in [0.05, 0.06, 0.07, 0.08, 0.09]:
                for q in [60, 65, 70, 75, 80]:
                    rules.append(Rule(side=side, odds_min=odds_min, odds_max=odds_max, edge_min=edge, quality_min=q))
    for side in ["over", "under"]:
        for tl in domains["tour_level"]:
            rules.append(Rule(side=side, tour_level=tl))
            for edge in [0.05, 0.07, 0.09]:
                rules.append(Rule(side=side, tour_level=tl, edge_min=edge, quality_min=70))
    for side in ["over", "under"]:
        if side == "over":
            for m in [0.8, 1.2, 1.6, 2.0, 2.5, 3.0]:
                rules.append(Rule(side=side, expected_margin_min=m, edge_min=0.05, quality_min=65))
        else:
            for m in [-0.8, -1.2, -1.6, -2.0, -2.5, -3.0]:
                rules.append(Rule(side=side, expected_margin_max=m, edge_min=0.05, quality_min=65))
    return rules


def mutate_rule(rng: random.Random, r: Rule, domains: Dict[str, List[Any]]) -> Rule:
    d = asdict(r)
    fields = list(d.keys())
    for _ in range(rng.randint(1, 4)):
        f = rng.choice(fields)
        if f == "side":
            d[f] = random_choice_or_any(rng, ["over", "under"], p_any=0.25)
        elif f in {"tour_level", "gender", "market_favorite_side", "best_bookmaker"}:
            d[f] = random_choice_or_any(rng, domains.get(f, []), p_any=0.70 if f != "best_bookmaker" else 0.92)
        elif f == "qualification":
            d[f] = random_choice_or_any(rng, ["true", "false"], p_any=0.80)
        elif f in {"odds_min", "odds_max"}:
            d[f] = None if rng.random() < 0.25 else rng.choice(domains[f])
        elif f in {"line_min", "line_max"}:
            d[f] = None if rng.random() < 0.45 else rng.choice(domains[f])
        elif f in {"edge_min"}:
            d[f] = None if rng.random() < 0.10 else rng.choice(domains["edge_min"])
        elif f in {"edge_max"}:
            d[f] = None if rng.random() < 0.90 else rng.choice(domains["edge_max"])
        elif f in {"confidence_min"}:
            d[f] = None if rng.random() < 0.25 else rng.choice(domains["confidence_min"])
        elif f in {"quality_min"}:
            d[f] = None if rng.random() < 0.25 else rng.choice(domains["quality_min"])
        elif f == "expected_margin_min":
            d[f] = None if rng.random() < 0.40 else rng.choice(domains["pos_margin_min"])
        elif f == "expected_margin_max":
            d[f] = None if rng.random() < 0.40 else rng.choice(domains["neg_margin_max"])
        elif f == "abs_margin_min":
            d[f] = None if rng.random() < 0.40 else rng.choice(domains["abs_margin_min"])
        elif f == "bookmakers_min":
            d[f] = None if rng.random() < 0.45 else rng.choice(domains["bookmakers_min"])
        elif f in {"market_gap_min", "market_gap_max"}:
            d[f] = None if rng.random() < 0.60 else rng.choice(domains[f])
        elif f in {"strength_gap_min", "strength_gap_max"}:
            d[f] = None if rng.random() < 0.65 else rng.choice(domains[f])
        elif f in {"h2h_min", "h2h_max"}:
            d[f] = None if rng.random() < 0.75 else rng.choice(domains[f])
        elif f == "min_recent_matches_min":
            d[f] = None if rng.random() < 0.65 else rng.choice(domains["recent_min"])
        elif f.startswith("avg_"):
            key = "rate_min" if f.endswith("min") else "rate_max"
            d[f] = None if rng.random() < 0.82 else rng.choice(domains[key])

    # Fix invalid ranges.
    for a, b in [("odds_min", "odds_max"), ("line_min", "line_max"), ("edge_min", "edge_max"),
                 ("market_gap_min", "market_gap_max"), ("strength_gap_min", "strength_gap_max"),
                 ("h2h_min", "h2h_max"), ("avg_three_set_min", "avg_three_set_max"),
                 ("avg_close_set_min", "avg_close_set_max"), ("avg_over_21_5_min", "avg_over_21_5_max")]:
        if d.get(a) is not None and d.get(b) is not None and d[a] > d[b]:
            d[a], d[b] = d[b], d[a]
    return Rule(**d)


def build_domains(picks: Sequence[Pick]) -> Dict[str, List[Any]]:
    max_books = max([p.bookmakers_used for p in picks] or [1])
    return {
        "odds_min": [1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90, 1.95],
        "odds_max": [1.75, 1.80, 1.85, 1.90, 1.95, 2.00, 2.05, 2.10, 2.15, 2.20, 2.30, 2.40, 2.60],
        "line_min": [14.5, 16.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 27.5, 30.5, 34.5, 36.5, 38.5],
        "line_max": [18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 27.5, 30.5, 34.5, 36.5, 38.5, 41.5, 45.5, 52.5],
        "edge_min": [round(x, 3) for x in [0.00, 0.02, 0.03, 0.04, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.10, 0.11, 0.12, 0.14]],
        "edge_max": [round(x, 3) for x in [0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.20]],
        "confidence_min": [50, 55, 60, 62, 65, 68, 70, 72, 75, 78, 80, 82, 85, 88, 90, 94],
        "quality_min": [45, 50, 55, 60, 65, 68, 70, 72, 75, 78, 80, 82, 85, 88, 90],
        "pos_margin_min": [0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.3, 2.6, 3.0, 3.5, 4.0],
        "neg_margin_max": [-0.2, -0.5, -0.8, -1.0, -1.2, -1.5, -1.8, -2.0, -2.3, -2.6, -3.0, -3.5, -4.0],
        "abs_margin_min": [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.0, 2.3, 2.6, 3.0, 3.5, 4.0],
        "bookmakers_min": list(range(1, max(2, max_books) + 1)),
        "market_gap_min": [0.00, 0.04, 0.08, 0.12, 0.16, 0.20, 0.25, 0.30, 0.40, 0.50],
        "market_gap_max": [0.04, 0.08, 0.12, 0.16, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70],
        "strength_gap_min": [0, 4, 8, 12, 16, 20, 25, 30, 35, 40],
        "strength_gap_max": [4, 8, 12, 16, 20, 25, 30, 35, 40, 60, 100],
        "h2h_min": [0, 1, 2, 3, 4, 5],
        "h2h_max": [0, 1, 2, 3, 5, 10],
        "recent_min": [4, 5, 6, 7, 8, 9, 10, 12, 15],
        "rate_min": [0.0, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65],
        "rate_max": [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.75, 1.0],
        "tour_level": uniq_sorted(p.tour_level for p in picks),
        "gender": uniq_sorted(p.gender for p in picks),
        "market_favorite_side": uniq_sorted(p.market_favorite_side for p in picks),
        "best_bookmaker": uniq_sorted(p.best_bookmaker for p in picks),
    }


def top_insert(top: List[Dict[str, Any]], item: Dict[str, Any], top_n: int) -> None:
    top.append(item)
    top.sort(key=lambda x: x["score"], reverse=True)
    if len(top) > top_n:
        del top[top_n:]


def run_optimizer(picks: List[Pick], iterations: int, seed: int, min_full: int, min_test: int, top_n: int, train_ratio: float) -> Dict[str, Any]:
    rng = random.Random(seed)
    train_pool, test_pool = split_train_test(picks, train_ratio)
    domains = build_domains(picks)
    seen: set[str] = set()
    top: List[Dict[str, Any]] = []
    checked = 0
    valid = 0
    start = time.time()

    seed_rules = generate_seed_rules(domains)
    for rule in seed_rules:
        key = rule.to_key()
        if key in seen:
            continue
        seen.add(key)
        checked += 1
        ev = evaluate_rule(rule, picks, train_pool, test_pool, min_full, min_test)
        if ev:
            valid += 1
            top_insert(top, ev, top_n)

    # Random + genetic search. Every now and then mutate one of current best rules.
    for i in range(iterations):
        if top and rng.random() < 0.28:
            parent = Rule(**rng.choice(top[:min(len(top), 40)])["rule"])
            rule = mutate_rule(rng, parent, domains)
        else:
            rule = generate_random_rule(rng, domains)
        key = rule.to_key()
        if key in seen:
            continue
        seen.add(key)
        checked += 1
        ev = evaluate_rule(rule, picks, train_pool, test_pool, min_full, min_test)
        if ev:
            valid += 1
            top_insert(top, ev, top_n)
        if (i + 1) % 100000 == 0:
            elapsed = time.time() - start
            best_score = top[0]["score"] if top else 0
            print(f"searched={i+1:,} checked={checked:,} valid={valid:,} best_score={best_score:.2f} elapsed={elapsed:.1f}s", flush=True)

    return {
        "optimizer": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "iterations_requested": iterations,
            "rules_checked_unique": checked,
            "valid_rules": valid,
            "seed": seed,
            "min_full": min_full,
            "min_test": min_test,
            "train_ratio": train_ratio,
            "settled_picks": len(picks),
            "train_picks": len(train_pool),
            "test_picks": len(test_pool),
            "runtime_seconds": round(time.time() - start, 3),
        },
        "baseline": {
            "all_flat_1u": backtest_metrics(picks),
            "train_flat_1u": backtest_metrics(train_pool),
            "test_flat_1u": backtest_metrics(test_pool),
        },
        "top_rules": top,
    }


def stake_for_strategy(p: Pick, strategy: str) -> float:
    if strategy == "flat_0_5u":
        return 0.5
    if strategy == "flat_1u":
        return 1.0
    if strategy == "original":
        return clamp(p.stake_original, 0.0, 5.0)
    if strategy == "quality_ladder":
        if p.quality >= 88 and p.edge >= 0.09:
            return 1.0
        if p.quality >= 80 and p.edge >= 0.07:
            return 0.75
        if p.quality >= 70:
            return 0.5
        return 0.25
    if strategy == "edge_ladder":
        if p.edge >= 0.11:
            return 1.0
        if p.edge >= 0.09:
            return 0.75
        if p.edge >= 0.07:
            return 0.5
        return 0.25
    if strategy == "confidence_ladder":
        if p.confidence >= 88:
            return 1.0
        if p.confidence >= 80:
            return 0.75
        if p.confidence >= 72:
            return 0.5
        return 0.25
    if strategy == "hybrid_safe":
        s = 0.25
        if p.edge >= 0.06 and p.quality >= 68 and p.confidence >= 65:
            s = 0.5
        if p.edge >= 0.08 and p.quality >= 76 and p.confidence >= 72:
            s = 0.75
        if p.edge >= 0.10 and p.quality >= 84 and p.confidence >= 80:
            s = 1.0
        return s
    if strategy == "kelly_10pct_capped":
        return clamp(kelly_fraction(p.model_prob, p.odds) * 0.10 * 10.0, 0.0, 1.0)
    if strategy == "kelly_25pct_capped":
        return clamp(kelly_fraction(p.model_prob, p.odds) * 0.25 * 10.0, 0.0, 1.25)
    return 1.0


def metrics_for_strategy(picks: Sequence[Pick], strategy: str) -> Dict[str, Any]:
    class Temp:
        pass
    temp = []
    for p in picks:
        stake = stake_for_strategy(p, strategy)
        t = Temp()
        # copy only needed attrs
        t.result = p.result
        t.odds = p.odds
        t.month = p.month
        t.week = p.week
        t.side = p.side
        t.flat_profit_1u = flat_profit(p.result, p.odds, stake)
        temp.append(t)
    m = backtest_metrics(temp)  # type: ignore[arg-type]
    total_staked = sum(stake_for_strategy(p, strategy) for p in picks if p.result != "void")
    m["strategy"] = strategy
    m["total_staked_units"] = round(total_staked, 6)
    m["roi_on_actual_staked"] = round(m["profit"] / max(1e-9, total_staked), 6)
    m["avg_stake"] = round(total_staked / max(1, sum(1 for p in picks if p.result != "void")), 4)
    return m


def staking_comparison(picks: Sequence[Pick], top_rules: Sequence[Dict[str, Any]], top_k: int = 10) -> Dict[str, Any]:
    strategies = [
        "flat_0_5u", "flat_1u", "original", "quality_ladder", "edge_ladder",
        "confidence_ladder", "hybrid_safe", "kelly_10pct_capped", "kelly_25pct_capped",
    ]
    out: Dict[str, Any] = {"baseline_all_picks": {}, "by_top_rule": []}
    for st in strategies:
        out["baseline_all_picks"][st] = metrics_for_strategy(picks, st)
    for rule_item in top_rules[:top_k]:
        r = Rule(**rule_item["rule"])
        selected = [p for p in picks if passes_rule(p, r)]
        row = {"rule_id": rule_item["rule_id"], "score": rule_item["score"], "rule": rule_item["rule"], "strategies": {}}
        for st in strategies:
            row["strategies"][st] = metrics_for_strategy(selected, st)
        # choose best by profit with drawdown penalty
        best_name = max(strategies, key=lambda s: row["strategies"][s]["profit"] + row["strategies"][s]["max_drawdown"] * 0.5)
        row["recommended_strategy"] = best_name
        out["by_top_rule"].append(row)
    return out


def calibration_report(picks: Sequence[Pick]) -> Dict[str, Any]:
    def bucketize(name: str, values: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        rows = []
        for lo, hi in values:
            arr = [p for p in picks if lo <= safe_float(getattr(p, name)) < hi]
            m = backtest_metrics(arr)
            rows.append({"range": f"{lo:g}-{hi:g}", **m})
        return rows
    return {
        "model_prob": bucketize("model_prob", [(0.40, 0.50), (0.50, 0.52), (0.52, 0.54), (0.54, 0.56), (0.56, 0.58), (0.58, 0.60), (0.60, 0.63), (0.63, 1.00)]),
        "edge": bucketize("edge", [(-1, 0.03), (0.03, 0.05), (0.05, 0.07), (0.07, 0.09), (0.09, 0.11), (0.11, 0.14), (0.14, 1)]),
        "confidence": bucketize("confidence", [(0, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, 100)]),
        "quality": bucketize("quality", [(0, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, 100)]),
        "odds": bucketize("odds", [(1.0, 1.60), (1.60, 1.70), (1.70, 1.80), (1.80, 1.90), (1.90, 2.00), (2.00, 2.15), (2.15, 2.40), (2.40, 10.0)]),
    }


def breakdown_report(picks: Sequence[Pick]) -> Dict[str, Any]:
    groups = {
        "side": lambda p: p.side,
        "tour_level": lambda p: p.tour_level,
        "gender": lambda p: p.gender,
        "qualification": lambda p: str(p.qualification).lower(),
        "best_bookmaker": lambda p: p.best_bookmaker,
        "market_favorite_side": lambda p: p.market_favorite_side,
    }
    out: Dict[str, Any] = {}
    for name, fn in groups.items():
        bucket: Dict[str, List[Pick]] = {}
        for p in picks:
            bucket.setdefault(fn(p), []).append(p)
        out[name] = {k: backtest_metrics(v) for k, v in sorted(bucket.items())}
    return out


def write_csv(path: str, top_rules: Sequence[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fields = [
        "rank", "score", "picks", "winrate", "avg_odds", "profit", "roi", "max_drawdown",
        "test_picks", "test_profit", "test_roi", "positive_folds", "complexity", "rule_id", "rule_json",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, item in enumerate(top_rules, 1):
            w.writerow({
                "rank": i,
                "score": item["score"],
                "picks": item["full"]["picks"],
                "winrate": item["full"]["winrate"],
                "avg_odds": item["full"]["avg_odds"],
                "profit": item["full"]["profit"],
                "roi": item["full"]["roi"],
                "max_drawdown": item["full"]["max_drawdown"],
                "test_picks": item["test"]["picks"],
                "test_profit": item["test"]["profit"],
                "test_roi": item["test"]["roi"],
                "positive_folds": item["walk_forward"].get("positive_folds"),
                "complexity": item["complexity"],
                "rule_id": item["rule_id"],
                "rule_json": json.dumps(item["rule"], ensure_ascii=False, sort_keys=True),
            })


def write_markdown(path: str, report: Dict[str, Any], staking: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    b = report["baseline"]["all_flat_1u"]
    lines = []
    lines.append("# Tennis Totals Optimizer Report")
    lines.append("")
    lines.append(f"Generated: `{report['optimizer']['generated_at']}`")
    lines.append(f"Settled picks: **{report['optimizer']['settled_picks']}**")
    lines.append(f"Unique rules checked: **{report['optimizer']['rules_checked_unique']:,}**")
    lines.append("")
    lines.append("## Baseline flat 1u")
    lines.append(f"Picks: **{b['picks']}**, winrate: **{pct(b['winrate'])}%**, profit: **{b['profit']}u**, ROI: **{pct(b['roi'])}%**, max DD: **{b['max_drawdown']}u**")
    lines.append("")
    lines.append("## Top rules")
    for i, item in enumerate(report["top_rules"][:20], 1):
        f = item["full"]
        t = item["test"]
        rule = {k: v for k, v in item["rule"].items() if v is not None and v != "any"}
        lines.append(f"### #{i} score {item['score']}")
        lines.append(f"Full: picks **{f['picks']}**, winrate **{pct(f['winrate'])}%**, profit **{f['profit']}u**, ROI **{pct(f['roi'])}%**, max DD **{f['max_drawdown']}u**")
        lines.append(f"Test: picks **{t['picks']}**, profit **{t['profit']}u**, ROI **{pct(t['roi'])}%**")
        lines.append("```json")
        lines.append(json.dumps(rule, indent=2, ensure_ascii=False, sort_keys=True))
        lines.append("```")
    lines.append("")
    lines.append("## Recommended staking for top rules")
    for row in staking.get("by_top_rule", [])[:10]:
        st = row["recommended_strategy"]
        m = row["strategies"][st]
        lines.append(f"- `{row['rule_id'][:8]}`: **{st}** → profit {m['profit']}u, ROI on staked {pct(m['roi_on_actual_staked'])}%, max DD {m['max_drawdown']}u")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/tennis_totals_results.json", help="Local JSON path or raw GitHub URL")
    ap.add_argument("--out-dir", default=OUT_DIR_DEFAULT)
    ap.add_argument("--iterations", type=int, default=1_000_000, help="Random/genetic search iterations. Use 5000000 for deeper search.")
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--min-full", type=int, default=25, help="Minimum picks for a rule on full data")
    ap.add_argument("--min-test", type=int, default=8, help="Minimum picks for a rule on out-of-sample test data")
    ap.add_argument("--top-n", type=int, default=250)
    ap.add_argument("--train-ratio", type=float, default=0.70)
    args = ap.parse_args()

    raw = load_json_any(args.input)
    if not isinstance(raw, list):
        raise RuntimeError("Input JSON must be a list of picks.")

    picks = []
    for idx, item in enumerate(raw):
        if isinstance(item, dict):
            p = make_pick(item, idx)
            if p:
                picks.append(p)
    picks.sort(key=lambda p: (p.date, p.idx))

    if len(picks) < 20:
        print(f"WARNING: only {len(picks)} settled picks found. Optimization can overfit badly.", file=sys.stderr)

    print(f"Loaded settled picks: {len(picks)}")
    print(f"Running optimizer iterations={args.iterations:,}, min_full={args.min_full}, min_test={args.min_test}")

    report = run_optimizer(
        picks=picks,
        iterations=args.iterations,
        seed=args.seed,
        min_full=args.min_full,
        min_test=args.min_test,
        top_n=args.top_n,
        train_ratio=args.train_ratio,
    )
    calibration = calibration_report(picks)
    breakdown = breakdown_report(picks)
    staking = staking_comparison(picks, report["top_rules"], top_k=20)

    full_report = {
        **report,
        "breakdown": breakdown,
        "calibration": calibration,
    }

    out_dir = args.out_dir
    save_json(os.path.join(out_dir, "tennis_totals_optimizer_report.json"), full_report)
    save_json(os.path.join(out_dir, "tennis_totals_best_rules.json"), report["top_rules"])
    save_json(os.path.join(out_dir, "tennis_totals_staking_comparison.json"), staking)
    save_json(os.path.join(out_dir, "tennis_totals_calibration.json"), calibration)
    write_csv(os.path.join(out_dir, "tennis_totals_optimizer_top_rules.csv"), report["top_rules"])
    write_markdown(os.path.join(out_dir, "tennis_totals_optimizer_report.md"), report, staking)

    print("\nDONE")
    print(f"Baseline ROI: {pct(report['baseline']['all_flat_1u']['roi'])}% | profit {report['baseline']['all_flat_1u']['profit']}u")
    if report["top_rules"]:
        best = report["top_rules"][0]
        print("Best rule:")
        print(json.dumps({
            "score": best["score"],
            "full": {k: best["full"][k] for k in ["picks", "winrate", "profit", "roi", "max_drawdown"]},
            "test": {k: best["test"][k] for k in ["picks", "winrate", "profit", "roi", "max_drawdown"]},
            "rule": {k: v for k, v in best["rule"].items() if v is not None and v != "any"},
        }, indent=2, ensure_ascii=False))
    else:
        print("No stable profitable rules found. Try lowering --min-full / --min-test, but beware overfitting.")
    print(f"Saved reports to: {out_dir}")


if __name__ == "__main__":
    main()

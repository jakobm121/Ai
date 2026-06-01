#!/usr/bin/env python3
"""
sabina.py

Sabina = tennis pick filter / backtester for AI77 tennis model exports.

Default formula v1:
    PLAY if:
        best_to_median_gap >= 0.06
        opponent_form.last_5.game_diff_avg <= 1.5
        odds <= 2.60

Default stake v1:
    0.75u base
    +0.25u if opponent_form.last_5.game_diff_avg <= 0.5
    +0.25u if player_form.last_5.fatigue_matches_7d >= 1
    -0.25u if tour_level == "wta"
    clipped to [0.50u, 1.25u]

Usage:
    python sabina.py tennis_results.json.txt
    python sabina.py tennis_results.json.txt --export sabina_picks.csv
    python sabina.py tennis_results.json.txt --mode candidates
    python sabina.py tennis_results.json.txt --gap 0.06 --opp-gd 1.5 --max-odds 2.60
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

Pick = Dict[str, Any]


def get_nested(d: Pick, path: str, default: Any = None) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def as_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


def parse_dt(p: Pick) -> datetime:
    # Prefer created_at; fallback to date+time; fallback minimum date.
    for key in ("created_at", "settled_at"):
        raw = p.get(key)
        if raw:
            try:
                return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            except ValueError:
                pass
    raw_date = str(p.get("date", "1900-01-01"))
    raw_time = str(p.get("time", "00:00"))
    try:
        return datetime.fromisoformat(f"{raw_date}T{raw_time}")
    except ValueError:
        return datetime(1900, 1, 1)


def load_picks(path: str | Path) -> List[Pick]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of pick objects.")
    return [p for p in data if isinstance(p, dict)]


def dedupe_picks(picks: Iterable[Pick]) -> List[Pick]:
    """
    One bet per fixture/side/bucket.
    If duplicates exist, keep the latest created_at version because it usually has fresher odds/bookmaker data.
    """
    grouped: Dict[Tuple[Any, Any, Any], Pick] = {}
    for p in picks:
        key = (
            p.get("fixture_id") or p.get("event_key") or p.get("pick_id"),
            p.get("bucket", "match_winner"),
            p.get("side") or p.get("market_side") or p.get("bet"),
        )
        old = grouped.get(key)
        if old is None or parse_dt(p) >= parse_dt(old):
            grouped[key] = p
    return sorted(grouped.values(), key=parse_dt)


def is_settled(p: Pick) -> bool:
    return str(p.get("result", "")).lower() in {"win", "loss"}


def sabina_play(
    p: Pick,
    *,
    min_gap: float = 0.06,
    max_opp_l5_game_diff: float = 1.5,
    max_odds: float = 2.60,
    min_bookmakers: int = 0,
    block_qualification: bool = False,
    block_atp: bool = False,
) -> bool:
    gap = as_float(p.get("best_to_median_gap"))
    opp_gd = as_float(get_nested(p, "opponent_form.last_5.game_diff_avg"), default=999.0)
    odds = as_float(p.get("odds"), default=999.0)
    bookmakers = int(as_float(p.get("bookmakers_used"), default=0))
    tour = str(p.get("tour_level", "")).lower()
    qualification = bool(p.get("qualification", False))

    if gap < min_gap:
        return False
    if opp_gd > max_opp_l5_game_diff:
        return False
    if odds > max_odds:
        return False
    if bookmakers < min_bookmakers:
        return False
    if block_qualification and qualification:
        return False
    if block_atp and tour == "atp":
        return False
    return True


def sabina_stake(p: Pick) -> float:
    stake = 0.75

    opp_l5_gd = as_float(get_nested(p, "opponent_form.last_5.game_diff_avg"), default=999.0)
    player_fatigue_7d = as_float(get_nested(p, "player_form.last_5.fatigue_matches_7d"), default=0.0)
    tour = str(p.get("tour_level", "")).lower()

    if opp_l5_gd <= 0.5:
        stake += 0.25
    if player_fatigue_7d >= 1:
        stake += 0.25
    if tour == "wta":
        stake -= 0.25

    return max(0.50, min(stake, 1.25))


def profit_with_stake(p: Pick, stake: float) -> float:
    result = str(p.get("result", "")).lower()
    odds = as_float(p.get("odds"), default=0.0)
    if result == "win":
        return stake * max(0.0, odds - 1.0)
    if result == "loss":
        return -stake
    return 0.0


@dataclass
class Stats:
    n: int = 0
    wins: int = 0
    losses: int = 0
    stake: float = 0.0
    profit: float = 0.0
    avg_odds_sum: float = 0.0

    def add(self, p: Pick, stake: Optional[float] = None, use_original_profit: bool = False) -> None:
        result = str(p.get("result", "")).lower()
        if result not in {"win", "loss"}:
            return
        s = as_float(p.get("stake"), default=1.0) if stake is None else stake
        prof = as_float(p.get("profit"), default=profit_with_stake(p, s)) if use_original_profit else profit_with_stake(p, s)
        self.n += 1
        self.wins += int(result == "win")
        self.losses += int(result == "loss")
        self.stake += s
        self.profit += prof
        self.avg_odds_sum += as_float(p.get("odds"), default=0.0)

    @property
    def win_rate(self) -> float:
        return self.wins / self.n if self.n else 0.0

    @property
    def roi(self) -> float:
        return self.profit / self.stake if self.stake else 0.0

    @property
    def avg_odds(self) -> float:
        return self.avg_odds_sum / self.n if self.n else 0.0


def summarize(label: str, stats: Stats) -> str:
    return (
        f"{label:<22} "
        f"N={stats.n:>4}  "
        f"W={stats.wins:>4}  L={stats.losses:>4}  "
        f"WR={stats.win_rate*100:>6.1f}%  "
        f"Profit={stats.profit:>8.2f}u  "
        f"Stake={stats.stake:>8.2f}u  "
        f"ROI={stats.roi*100:>7.1f}%  "
        f"AvgOdds={stats.avg_odds:>5.2f}"
    )


def time_splits(picks: List[Pick], k: int = 3) -> List[List[Pick]]:
    ordered = sorted(picks, key=parse_dt)
    if not ordered:
        return [[] for _ in range(k)]
    splits: List[List[Pick]] = []
    n = len(ordered)
    for i in range(k):
        a = round(i * n / k)
        b = round((i + 1) * n / k)
        splits.append(ordered[a:b])
    return splits


def group_report(picks: List[Pick], field: str) -> List[Tuple[str, Stats]]:
    groups: Dict[str, Stats] = defaultdict(Stats)
    for p in picks:
        key = str(get_nested(p, field, p.get(field, "unknown")) or "unknown")
        groups[key].add(p, stake=sabina_stake(p))
    return sorted(groups.items(), key=lambda kv: kv[1].profit, reverse=True)


def export_csv(path: str | Path, picks: List[Pick]) -> None:
    fields = [
        "date", "time", "match", "bet", "odds", "sabina_stake", "sabina_profit",
        "result", "tour_level", "event_type", "best_bookmaker", "bookmakers_used",
        "best_to_median_gap", "edge", "model_prob", "implied_prob",
        "opponent_l5_game_diff", "player_l5_fatigue_7d", "score_diff", "quality_score",
        "fixture_id", "pick_id",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in picks:
            stake = sabina_stake(p)
            row = {
                "date": p.get("date"),
                "time": p.get("time"),
                "match": p.get("match"),
                "bet": p.get("bet"),
                "odds": p.get("odds"),
                "sabina_stake": stake,
                "sabina_profit": profit_with_stake(p, stake) if is_settled(p) else "",
                "result": p.get("result"),
                "tour_level": p.get("tour_level"),
                "event_type": p.get("event_type"),
                "best_bookmaker": p.get("best_bookmaker"),
                "bookmakers_used": p.get("bookmakers_used"),
                "best_to_median_gap": p.get("best_to_median_gap"),
                "edge": p.get("edge"),
                "model_prob": p.get("model_prob"),
                "implied_prob": p.get("implied_prob"),
                "opponent_l5_game_diff": get_nested(p, "opponent_form.last_5.game_diff_avg"),
                "player_l5_fatigue_7d": get_nested(p, "player_form.last_5.fatigue_matches_7d"),
                "score_diff": p.get("score_diff"),
                "quality_score": p.get("quality_score"),
                "fixture_id": p.get("fixture_id"),
                "pick_id": p.get("pick_id"),
            }
            writer.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sabina tennis value filter/backtester")
    ap.add_argument("input", help="Path to tennis_results JSON export")
    ap.add_argument("--export", help="Export Sabina-selected picks to CSV")
    ap.add_argument("--mode", choices=["settled", "candidates", "all"], default="settled",
                    help="settled=backtest win/loss only; candidates=unsettled/non-final picks; all=all selected")
    ap.add_argument("--gap", type=float, default=0.06, help="Minimum best_to_median_gap")
    ap.add_argument("--opp-gd", type=float, default=1.5, help="Max opponent last-5 game_diff_avg")
    ap.add_argument("--max-odds", type=float, default=2.60, help="Maximum odds")
    ap.add_argument("--min-bookmakers", type=int, default=0, help="Minimum bookmakers_used")
    ap.add_argument("--block-qualification", action="store_true", help="Block qualification matches")
    ap.add_argument("--block-atp", action="store_true", help="Block ATP tour_level")
    args = ap.parse_args()

    raw = load_picks(args.input)
    deduped = dedupe_picks(raw)
    selected_all = [
        p for p in deduped
        if sabina_play(
            p,
            min_gap=args.gap,
            max_opp_l5_game_diff=args.opp_gd,
            max_odds=args.max_odds,
            min_bookmakers=args.min_bookmakers,
            block_qualification=args.block_qualification,
            block_atp=args.block_atp,
        )
    ]

    if args.mode == "settled":
        selected = [p for p in selected_all if is_settled(p)]
    elif args.mode == "candidates":
        selected = [p for p in selected_all if not is_settled(p)]
    else:
        selected = selected_all

    print("Sabina v1")
    print("=" * 92)
    print(f"Input records:          {len(raw)}")
    print(f"Deduped records:        {len(deduped)}")
    print(f"Selected records:       {len(selected)}")
    print(f"Formula: gap >= {args.gap}, opponent L5 game diff <= {args.opp_gd}, odds <= {args.max_odds}")
    if args.min_bookmakers:
        print(f"Extra:   bookmakers_used >= {args.min_bookmakers}")
    if args.block_qualification:
        print("Extra:   qualification blocked")
    if args.block_atp:
        print("Extra:   ATP blocked")
    print("=" * 92)

    settled_selected = [p for p in selected if is_settled(p)]
    if settled_selected:
        original = Stats()
        sabina = Stats()
        for p in settled_selected:
            original.add(p, stake=as_float(p.get("stake"), default=1.0), use_original_profit=True)
            sabina.add(p, stake=sabina_stake(p), use_original_profit=False)
        print(summarize("Original staking", original))
        print(summarize("Sabina staking", sabina))
        print("\nTime stability, Sabina staking:")
        for i, split in enumerate(time_splits(settled_selected, 3), 1):
            st = Stats()
            for p in split:
                st.add(p, stake=sabina_stake(p))
            print(summarize(f"Split {i}/3", st))

        print("\nBy tour_level:")
        for key, st in group_report(settled_selected, "tour_level")[:12]:
            print(summarize(key[:22], st))

        print("\nBy event_type:")
        for key, st in group_report(settled_selected, "event_type")[:12]:
            print(summarize(key[:22], st))
    else:
        print("No settled selected picks in this mode. Use --mode settled for backtest or --mode all.")

    if args.export:
        export_csv(args.export, selected)
        print(f"\nExported: {args.export}")


if __name__ == "__main__":
    main()

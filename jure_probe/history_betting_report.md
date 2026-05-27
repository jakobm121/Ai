# Historical Betting Dataset Report

Generated at: **2026-05-28T01:18:50.644564+02:00**

## Inputs

- History file: `jure_probe/history_raw_sample.json`
- Odds file: `jure_probe/odds_probe_raw.json`
- History matches loaded: **300**
- Odds items loaded: **101**

## Dataset

- Dataset rows: **1031**
- Supported markets: `Home/Away, Home/Away (1st Set), Home/Away (2nd Set), Number of sets, Odd/Even, Odd/Even (1st Set), Set / Match, Set Betting`

## Overall flat baseline

| Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |
|---:|---:|---:|---:|---:|---:|---:|
| 1031 | 400 | 631 | 38.8% | -112.07u | -10.87% | 3.9514 |

## By market

| Market | Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Set Betting | 212 | 53 | 159 | 25.0% | -27.43u | -12.94% | 5.7916 |
| Set / Match | 212 | 53 | 159 | 25.0% | -45.17u | -21.31% | 6.726 |
| Odd/Even | 118 | 59 | 59 | 50.0% | -8.07u | -6.84% | 1.8691 |
| Odd/Even (1st Set) | 118 | 59 | 59 | 50.0% | -8.32u | -7.05% | 1.8762 |
| Home/Away (1st Set) | 106 | 53 | 53 | 50.0% | -3.03u | -2.86% | 2.4498 |
| Home/Away (2nd Set) | 106 | 53 | 53 | 50.0% | -7.02u | -6.62% | 2.3295 |
| Home/Away | 106 | 53 | 53 | 50.0% | -8.59u | -8.1% | 3.0282 |
| Number of sets | 53 | 17 | 36 | 32.08% | -4.44u | -8.38% | 2.8425 |

## By market + selection

| Market / Selection | Rows | Wins | Losses | Winrate | Profit flat | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Odd/Even / Even | 59 | 37 | 22 | 62.71% | 9.91u | 16.8% | 1.8702 |
| Odd/Even (1st Set) / Even | 59 | 36 | 23 | 61.02% | 5.77u | 9.78% | 1.8022 |
| Odd/Even (1st Set) / Odd | 59 | 23 | 36 | 38.98% | -14.09u | -23.88% | 1.9502 |
| Odd/Even / Odd | 59 | 22 | 37 | 37.29% | -17.98u | -30.47% | 1.868 |
| Home/Away (1st Set) / Away | 53 | 32 | 21 | 60.38% | 11.71u | 22.09% | 2.3545 |
| Home/Away / Away | 53 | 27 | 26 | 50.94% | -0.53u | -1.0% | 2.7898 |
| Home/Away (2nd Set) / Away | 53 | 27 | 26 | 50.94% | -1.48u | -2.79% | 2.2196 |
| Set Betting / 2:1 | 53 | 11 | 42 | 20.75% | -3.72u | -7.02% | 6.7085 |
| Set / Match / 2/2 | 53 | 25 | 28 | 47.17% | -4.38u | -8.26% | 3.3932 |
| Number of sets / 3 | 53 | 17 | 36 | 32.08% | -4.44u | -8.38% | 2.8425 |
| Home/Away (2nd Set) / Home | 53 | 26 | 27 | 49.06% | -5.54u | -10.45% | 2.4394 |
| Set Betting / 0:2 | 53 | 21 | 32 | 39.62% | -7.68u | -14.49% | 4.7198 |
| Set Betting / 2:0 | 53 | 15 | 38 | 28.3% | -7.68u | -14.49% | 5.5102 |
| Home/Away / Home | 53 | 26 | 27 | 49.06% | -8.06u | -15.21% | 3.2666 |
| Set / Match / 2/1 | 53 | 7 | 46 | 13.21% | -8.25u | -15.57% | 10.1151 |
| Set Betting / 1:2 | 53 | 6 | 47 | 11.32% | -8.35u | -15.75% | 6.2277 |
| Set / Match / 1/1 | 53 | 19 | 34 | 35.85% | -11.29u | -21.3% | 3.9353 |
| Home/Away (1st Set) / Home | 53 | 21 | 32 | 39.62% | -14.74u | -27.81% | 2.5451 |
| Set / Match / 1/2 | 53 | 2 | 51 | 3.77% | -21.25u | -40.09% | 9.4604 |

## Skipped / unknown

| Reason | Count |
|---|---:|
| `unsupported_market:Correct Score 1st Half` | 59 |
| `unknown_result:Number of sets:Away` | 59 |
| `unsupported_market:Away Team Total (1st Set)` | 59 |
| `unsupported_market:Home Team Total (1st Set)` | 59 |
| `unsupported_market:Correct Score 2nd Half` | 57 |
| `unsupported_market:Odd/Even (2nd Set)` | 57 |
| `unsupported_market:Away Team Total (2nd Set)` | 57 |
| `unsupported_market:Home Team Total (2nd Set)` | 57 |
| `unsupported_market:param` | 42 |
| `unsupported_market:msg` | 42 |
| `unsupported_market:cod` | 42 |
| `unsupported_market:Win at least one set (Player 1)` | 15 |
| `unsupported_market:Win at least one set (Player 2)` | 15 |
| `unknown_result:Home/Away:Home` | 6 |
| `unknown_result:Home/Away:Away` | 6 |
| `unknown_result:Home/Away (1st Set):Home` | 6 |
| `unknown_result:Home/Away (1st Set):Away` | 6 |
| `unknown_result:Set Betting:2:0` | 6 |
| `unknown_result:Set Betting:2:1` | 6 |
| `unknown_result:Set Betting:0:2` | 6 |
| `unknown_result:Set Betting:1:2` | 6 |
| `unknown_result:Set / Match:1/1` | 6 |
| `unknown_result:Set / Match:1/2` | 6 |
| `unknown_result:Set / Match:2/1` | 6 |
| `unknown_result:Set / Match:2/2` | 6 |
| `unknown_result:Home/Away (2nd Set):Home` | 6 |
| `unknown_result:Home/Away (2nd Set):Away` | 6 |
| `unknown_result:Number of sets:3` | 6 |

## Dataset sample

| Date | Match | Market | Selection | Odds | Result | Profit | Final | Total games |
|---|---|---|---|---:|---|---:|---|---:|
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away | Away | 2.43 | win | 1.43 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away | Home | 1.61 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away (1st Set) | Away | 2.3 | win | 1.3 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away (1st Set) | Home | 1.66 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away (2nd Set) | Away | 2.22 | win | 1.22 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Home/Away (2nd Set) | Home | 1.63 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Number of sets | 3 | 2.5 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Odd/Even | Even | 1.84 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Odd/Even | Odd | 1.84 | win | 0.84 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Odd/Even (1st Set) | Even | 1.83 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Odd/Even (1st Set) | Odd | 1.85 | win | 0.85 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set / Match | 1/1 | 1.94 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set / Match | 1/2 | 8.1 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set / Match | 2/1 | 6.25 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set / Match | 2/2 | 2.99 | win | 1.99 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set Betting | 0:2 | 3.75 | win | 2.75 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set Betting | 1:2 | 5.5 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set Betting | 2:0 | 2.38 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | D. Singh - L. Vithoontien | Set Betting | 2:1 | 4.5 | loss | -1.0 | 0:2 | 19 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away | Away | 1.93 | win | 0.93 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away | Home | 2.02 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away (1st Set) | Away | 1.88 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away (1st Set) | Home | 1.95 | win | 0.95 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away (2nd Set) | Away | 1.77 | win | 0.77 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Home/Away (2nd Set) | Home | 1.92 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Number of sets | 3 | 2.38 | win | 1.38 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Odd/Even | Even | 1.84 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Odd/Even | Odd | 1.84 | win | 0.84 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Odd/Even (1st Set) | Even | 1.8 | win | 0.8 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Odd/Even (1st Set) | Odd | 1.88 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set / Match | 1/1 | 2.51 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set / Match | 1/2 | 6.75 | win | 5.75 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set / Match | 2/1 | 7.2 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set / Match | 2/2 | 2.24 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set Betting | 0:2 | 3.0 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set Betting | 1:2 | 4.4 | win | 3.4 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set Betting | 2:0 | 3.08 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | K. Singh - W. K. Leong M. | Set Betting | 2:1 | 4.65 | loss | -1.0 | 1:2 | 29 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away | Away | 1.33 | win | 0.33 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away | Home | 3.84 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away (1st Set) | Away | 1.41 | win | 0.41 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away (1st Set) | Home | 3.14 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away (2nd Set) | Away | 1.38 | win | 0.38 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Home/Away (2nd Set) | Home | 2.94 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Number of sets | 3 | 2.62 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Odd/Even | Even | 1.84 | win | 0.84 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Odd/Even | Odd | 1.84 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Odd/Even (1st Set) | Even | 1.78 | win | 0.78 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Odd/Even (1st Set) | Odd | 1.9 | loss | -1.0 | 0:2 | 18 |
| 2026-05-19 | R. Matsuda - Y. Takahashi | Set / Match | 1/1 | 4.7 | loss | -1.0 | 0:2 | 18 |

## Files generated

- `jure_probe/history_betting_dataset.json`
- `jure_probe/history_betting_summary.json`
- `jure_probe/history_betting_debug.json`
- `jure_probe/history_betting_report.md`

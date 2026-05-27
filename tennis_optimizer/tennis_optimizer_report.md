# Tennis Home/Away Optimizer Report

Generated at: **2026-05-27T10:50:20.949961+02:00**

## Executive summary

- Source picks loaded: **463**
- Settled picks used: **437**
- Minimum sample: **100**
- Rules evaluated: **115095**
- Valid strategies: **24417**

## Whole database baseline

| Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 437 | 185 | 230 | 22 | 44.58% | -6.0u | -1.37% | 2.2501 | -14.26u |

## Best strategy found

**Score:** 52.783745

**Rules:** bookmakers ≤ 10; bookmakers ≥ 6; edge ≤ 0.15; odds ≥ 1.75; quality ≤ 90

| Split | Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full | 125 | 68 | 51 | 6 | 57.14% | 24.37u | 19.5% | 2.0968 | -4.55u |
| Train 75% | 93 | 49 | 41 | 3 | 54.44% | 10.75u | 11.56% | 2.0722 | -6.07u |
| Test 25% | 32 | 19 | 10 | 3 | 65.52% | 13.62u | 42.56% | 2.1684 | -2.0u |

## Recommended live tactic

### Base filter

```json
{
  "bookmakers_max": 10,
  "bookmakers_min": 6,
  "edge_max": 0.15,
  "odds_min": 1.75,
  "quality_max": 90
}
```

### Stake

- Forward test: **0.5u flat** until 50 new live picks.
- Confirmed mode: **1u flat** only after forward confirmation.
- No martingale.

### A-pick priority

| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---|---:|---:|---:|---:|---:|---:|
| side = home | 55 | 68.63% | 20.59u | 37.44% | 5.59u | 39.93% |
| odds ≥ 2.25 | 29 | 60.71% | 15.71u | 54.17% | 9.02u | 112.75% |
| edge ≤ 0.0799; edge ≥ 0.06 | 27 | 73.08% | 14.81u | 54.85% | 5.24u | 74.86% |
| bookmakers ≥ 8; side = home | 38 | 71.05% | 16.36u | 43.05% | 7.4u | 74.0% |
| tour = challenger | 45 | 65.91% | 17.22u | 38.27% | 7.91u | 65.92% |

### B-pick watchlist

| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---|---:|---:|---:|---:|---:|---:|
| gender = men; tour = challenger | 45 | 65.91% | 17.22u | 38.27% | 7.91u | 65.92% |
| qualification = False | 99 | 58.06% | 21.44u | 21.66% | 10.02u | 40.08% |
| odds ≥ 2.25; qualification = False | 24 | 60.87% | 13.29u | 55.38% | 5.52u | 92.0% |
| bookmakers ≥ 8 | 89 | 59.09% | 20.25u | 22.75% | 6.02u | 26.17% |
| bookmakers ≥ 8; qualification = False | 65 | 60.94% | 17.86u | 27.48% | 8.16u | 48.0% |

### Avoid / weak segments

| Reason | Group | Picks | Winrate | Profit | ROI |
|---|---|---:|---:|---:|---:|
| tournament | French Open | 12 | 41.67% | -1.78u | -14.83% |
| edge | 0.08-0.099 | 21 | 47.37% | -1.59u | -7.57% |
| tour | itf | 55 | 46.0% | -1.18u | -2.15% |
| confidence | 85-87.9 | 12 | 45.45% | -1.12u | -9.33% |
| quality | 80-84.9 | 35 | 47.06% | -0.87u | -2.49% |
| odds | 2.05-2.249 | 29 | 46.43% | -0.25u | -0.86% |

## Tactical add-on combinations inside best base

| Rank | Score | Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 38.5706 | side = home | 55 | 68.63% | 20.59u | 37.44% | 5.59u | 39.93% |
| 2 | 37.385594 | odds ≥ 2.25 | 29 | 60.71% | 15.71u | 54.17% | 9.02u | 112.75% |
| 3 | 37.358876 | edge ≤ 0.0799; edge ≥ 0.06 | 27 | 73.08% | 14.81u | 54.85% | 5.24u | 74.86% |
| 4 | 36.399138 | bookmakers ≥ 8; side = home | 38 | 71.05% | 16.36u | 43.05% | 7.4u | 74.0% |
| 5 | 35.353999 | tour = challenger | 45 | 65.91% | 17.22u | 38.27% | 7.91u | 65.92% |
| 6 | 35.353999 | gender = men; tour = challenger | 45 | 65.91% | 17.22u | 38.27% | 7.91u | 65.92% |
| 7 | 35.257268 | qualification = False | 99 | 58.06% | 21.44u | 21.66% | 10.02u | 40.08% |
| 8 | 34.830708 | odds ≥ 2.25; qualification = False | 24 | 60.87% | 13.29u | 55.38% | 5.52u | 92.0% |
| 9 | 32.926795 | bookmakers ≥ 8 | 89 | 59.09% | 20.25u | 22.75% | 6.02u | 26.17% |
| 10 | 32.606158 | bookmakers ≥ 8; qualification = False | 65 | 60.94% | 17.86u | 27.48% | 8.16u | 48.0% |
| 11 | 32.107156 | side = home; tour = challenger | 22 | 72.73% | 10.53u | 47.86% | 6.97u | 116.17% |
| 12 | 32.107156 | gender = men; side = home; tour = challenger | 22 | 72.73% | 10.53u | 47.86% | 6.97u | 116.17% |
| 13 | 31.940028 | qualification = False; tour = challenger | 36 | 65.71% | 13.46u | 37.39% | 9.68u | 107.56% |
| 14 | 31.940028 | gender = men; qualification = False; tour = challenger | 36 | 65.71% | 13.46u | 37.39% | 9.68u | 107.56% |
| 15 | 31.609022 | qualification = False; side = home | 47 | 65.12% | 15.26u | 32.47% | 5.72u | 47.67% |
| 16 | 31.312708 | edge ≤ 0.0799; edge ≥ 0.06; qualification = False | 24 | 69.57% | 11.54u | 48.08% | 4.34u | 72.33% |
| 17 | 31.309824 | bookmakers ≥ 8; edge ≥ 0.12; gender = men | 23 | 68.18% | 11.24u | 48.87% | 5.04u | 84.0% |
| 18 | 29.05368 | bookmakers ≥ 8; qualification = False; side = home | 30 | 66.67% | 11.03u | 36.77% | 7.48u | 93.5% |
| 19 | 28.959831 | bookmakers ≥ 8; gender = men; quality ≥ 85 | 28 | 66.67% | 11.18u | 39.93% | 4.27u | 61.0% |
| 20 | 28.302594 | bookmakers ≥ 8; edge ≥ 0.12 | 29 | 64.29% | 11.36u | 39.17% | 3.04u | 38.0% |
| 21 | 28.265876 | bookmakers ≥ 8; edge ≥ 0.12; quality ≥ 85 | 27 | 65.38% | 10.96u | 40.59% | 1.64u | 23.43% |
| 22 | 28.041138 | gender = men; side = home | 38 | 66.67% | 12.02u | 31.63% | 4.86u | 48.6% |
| 23 | 27.811302 | bookmakers ≥ 8; quality ≥ 85 | 35 | 64.71% | 12.14u | 34.69% | 2.27u | 25.22% |
| 24 | 27.658708 | bookmakers ≥ 8; gender = women; qualification = False | 24 | 66.67% | 10.62u | 44.25% | -1.05u | -17.5% |
| 25 | 27.295824 | bookmakers ≥ 8; qualification = False; quality ≥ 85 | 23 | 68.18% | 9.4u | 40.87% | 3.4u | 56.67% |
| 26 | 27.007708 | edge ≥ 0.12; gender = men; quality ≥ 85 | 24 | 65.22% | 9.74u | 40.58% | 2.64u | 44.0% |
| 27 | 26.276094 | edge ≤ 0.1199; edge ≥ 0.1; qualification = False | 29 | 65.52% | 10.3u | 35.52% | 3.54u | 44.25% |
| 28 | 26.195886 | gender = men | 87 | 56.63% | 14.42u | 16.57% | 10.95u | 49.77% |
| 29 | 25.988954 | bookmakers ≥ 8; tour = challenger | 34 | 63.64% | 10.57u | 31.09% | 6.05u | 67.22% |
| 30 | 25.988954 | bookmakers ≥ 8; gender = men; tour = challenger | 34 | 63.64% | 10.57u | 31.09% | 6.05u | 67.22% |

## Top global strategies

| Rank | Score | Picks | Winrate | Profit | ROI | Test profit | Test ROI | Max DD | Rules |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 52.783745 | 125 | 57.14% | 24.37u | 19.5% | 13.62u | 42.56% | -4.55u | bookmakers ≤ 10; bookmakers ≥ 6; edge ≤ 0.15; odds ≥ 1.75; quality ≤ 90 |
| 2 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 3 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≥ 50; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 4 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≥ 55; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 5 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≥ 60; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 6 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≥ 65; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 7 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≥ 70; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 8 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≤ 88; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 9 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≤ 90; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 10 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≤ 93; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 11 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; confidence ≤ 96; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 12 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90; quality ≥ 50 |
| 13 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90; quality ≥ 55 |
| 14 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90; quality ≥ 60 |
| 15 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; edge ≥ 0; odds ≥ 1.85; quality ≤ 90 |
| 16 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; edge ≥ 0.02; odds ≥ 1.85; quality ≤ 90 |
| 17 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; edge ≥ 0.04; odds ≥ 1.85; quality ≤ 90 |
| 18 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; edge ≥ 0.06; odds ≥ 1.85; quality ≤ 90 |
| 19 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; edge ≤ 0.15; odds ≤ 3.0; odds ≥ 1.85; quality ≤ 90 |
| 20 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; bookmakers ≥ 2; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 21 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; bookmakers ≥ 3; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 22 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; bookmakers ≥ 4; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 23 | 52.23321 | 108 | 57.28% | 24.78u | 22.94% | 11.49u | 42.56% | -6.23u | bookmakers ≤ 10; bookmakers ≥ 5; edge ≤ 0.15; odds ≥ 1.85; quality ≤ 90 |
| 24 | 52.224394 | 132 | 57.14% | 25.4u | 19.24% | 12.46u | 37.76% | -4.55u | bookmakers ≤ 10; edge ≤ 0.15; odds ≥ 1.75; quality ≤ 90 |
| 25 | 52.224394 | 132 | 57.14% | 25.4u | 19.24% | 12.46u | 37.76% | -4.55u | bookmakers ≤ 10; confidence ≥ 50; edge ≤ 0.15; odds ≥ 1.75; quality ≤ 90 |

## Feature ranges inside best strategy

| Feature | Min | P25 | Median | P75 | Max | Avg |
|---|---:|---:|---:|---:|---:|---:|
| confidence | 72.6 | 86.4 | 88.0 | 88.0 | 88.0 | 85.8792 |
| quality | 63.4 | 76.4 | 81.8 | 86.3 | 89.9 | 80.7496 |
| edge | 0.0652 | 0.0872 | 0.1083 | 0.1252 | 0.1483 | 0.1059 |
| odds | 1.75 | 1.88 | 2.01 | 2.2 | 2.85 | 2.0968 |
| bookmakers | 6 | 7 | 9 | 9 | 10 | 8.352 |

## Bucket analysis inside best strategy

### confidence

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 80-84.9 | 15 | 86.67% | 16.4u | 109.33% | 2.3973 | -2.0u |
| <75 | 4 | 100.0% | 5.67u | 141.75% | 2.4175 | 0.0u |
| 75-79.9 | 10 | 44.44% | 1.98u | 19.8% | 2.728 | -3.0u |
| 88-89.9 | 84 | 52.5% | 1.44u | 1.71% | 1.9576 | -7.62u |
| 85-87.9 | 12 | 45.45% | -1.12u | -9.33% | 2.0625 | -3.14u |

### quality

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| <72 | 17 | 75.0% | 10.99u | 64.65% | 2.2506 | -2.0u |
| 85+ | 40 | 60.53% | 10.04u | 25.1% | 2.0978 | -3.0u |
| 72-74.9 | 9 | 62.5% | 2.93u | 32.56% | 2.0778 | -2.07u |
| 75-79.9 | 24 | 52.17% | 1.28u | 5.33% | 2.0367 | -3.49u |
| 80-84.9 | 35 | 47.06% | -0.87u | -2.49% | 2.0671 | -4.96u |

### edge

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 0.06-0.079 | 27 | 73.08% | 14.81u | 54.85% | 2.1074 | -2.0u |
| 0.10-0.119 | 35 | 57.14% | 6.14u | 17.54% | 2.072 | -3.09u |
| 0.12+ | 42 | 51.28% | 5.01u | 11.93% | 2.1938 | -3.9u |
| 0.08-0.099 | 21 | 47.37% | -1.59u | -7.57% | 1.9305 | -3.48u |

### odds

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 2.25+ | 29 | 60.71% | 15.71u | 54.17% | 2.5531 | -4.0u |
| 1.75-1.899 | 35 | 62.5% | 4.78u | 13.66% | 1.832 | -2.55u |
| 1.90-2.049 | 32 | 58.06% | 4.13u | 12.91% | 1.9522 | -3.21u |
| 2.05-2.249 | 29 | 46.43% | -0.25u | -0.86% | 2.1197 | -6.28u |

### market_gap

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 125 | 57.14% | 24.37u | 19.5% | 2.0968 | -4.55u |

### strength_gap

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 125 | 57.14% | 24.37u | 19.5% | 2.0968 | -4.55u |

### bookmakers

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 8+ | 89 | 59.09% | 20.25u | 22.75% | 2.0837 | -4.25u |
| 6-7 | 36 | 51.61% | 4.12u | 11.44% | 2.1292 | -3.0u |

### rank

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 125 | 57.14% | 24.37u | 19.5% | 2.0968 | -4.55u |

## Categorical breakdown inside best strategy

### By side

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| home | 55 | 68.63% | 20.59u | 37.44% | 2.0005 | -2.0u |
| away | 70 | 48.53% | 3.78u | 5.4% | 2.1724 | -7.52u |

### By gender

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| men | 87 | 56.63% | 14.42u | 16.57% | 2.0887 | -6.33u |
| women | 38 | 58.33% | 9.95u | 26.18% | 2.1153 | -2.0u |

### By tour level

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| challenger | 45 | 65.91% | 17.22u | 38.27% | 2.0809 | -3.41u |
| wta | 12 | 75.0% | 7.15u | 59.58% | 2.1167 | -1.0u |
| atp | 13 | 53.85% | 1.18u | 9.08% | 2.1108 | -3.23u |
| itf | 55 | 46.0% | -1.18u | -2.15% | 2.1022 | -6.05u |

### By bookmaker

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Pncl | 57 | 56.6% | 8.42u | 14.77% | 2.0232 | -3.15u |
| bet365 | 21 | 60.0% | 5.93u | 28.24% | 2.1505 | -3.0u |
| Unibet | 21 | 61.9% | 5.85u | 27.86% | 2.1233 | -3.46u |
| Betfair | 14 | 57.14% | 5.52u | 39.43% | 2.405 | -3.0u |
| Betano | 6 | 66.67% | 1.72u | 28.67% | 1.9117 | -1.0u |
| Superbet | 1 | 0.0% | 0.0u | 0.0% | 1.87 | 0.0u |
| WilliamHill | 1 | 0.0% | -1.0u | -100.0% | 2.1 | -1.0u |
| 888Sport | 1 | 0.0% | -1.0u | -100.0% | 1.91 | -1.0u |
| Sbo | 3 | 33.33% | -1.07u | -35.67% | 2.0033 | -1.07u |

### By tournament

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Rome | 4 | 100.0% | 5.18u | 129.5% | 2.295 | 0.0u |
| Bengaluru 3 (India) - Qualification | 3 | 100.0% | 4.56u | 152.0% | 2.52 | 0.0u |
| Valencia | 8 | 75.0% | 4.38u | 54.75% | 2.0512 | -1.0u |
| Strasbourg | 4 | 100.0% | 3.96u | 99.0% | 1.99 | 0.0u |
| W100 Takasaki | 4 | 75.0% | 3.5u | 87.5% | 2.4375 | -1.0u |
| Wuxi | 3 | 100.0% | 3.18u | 106.0% | 2.06 | 0.0u |
| Little Rock | 3 | 100.0% | 2.75u | 91.67% | 1.9167 | 0.0u |
| W15 Tsaghkadzor | 2 | 100.0% | 1.85u | 92.5% | 1.925 | 0.0u |
| M25 Hurghada (Egypt) | 2 | 100.0% | 1.78u | 89.0% | 1.89 | 0.0u |
| W35 Andong | 1 | 100.0% | 1.75u | 175.0% | 2.75 | 0.0u |
| W15 Hurghada 4 (Egypt) | 1 | 100.0% | 1.63u | 163.0% | 2.63 | 0.0u |
| Kosice | 5 | 60.0% | 1.44u | 28.8% | 2.088 | -2.0u |
| M15 Litija | 2 | 100.0% | 1.4u | 70.0% | 2.205 | 0.0u |
| M25 Reggio Emilia | 1 | 100.0% | 1.25u | 125.0% | 2.25 | 0.0u |
| W15 Szentendre (Hungary) | 1 | 100.0% | 1.2u | 120.0% | 2.2 | 0.0u |
| Geneva | 1 | 100.0% | 1.12u | 112.0% | 2.12 | 0.0u |
| Chisinau | 1 | 100.0% | 1.12u | 112.0% | 2.12 | 0.0u |
| W15 Kursumlijska Banja | 1 | 100.0% | 1.1u | 110.0% | 2.1 | 0.0u |
| Cervia (Italy) - Qualification | 1 | 100.0% | 1.04u | 104.0% | 2.04 | 0.0u |
| M15 Kayseri | 1 | 100.0% | 0.9u | 90.0% | 1.9 | 0.0u |

## Files generated

- `tennis_optimizer/tennis_optimizer_report.md`
- `tennis_optimizer/tennis_best_rules.json`
- `tennis_optimizer/tennis_optimizer_table.json`
- `tennis_optimizer/tennis_optimizer_picks.json`
- `tennis_optimizer/tennis_optimizer_tactic.json`
- `tennis_optimizer/tennis_optimizer_debug.json`
- `tennis_optimizer/tennis_optimizer_summary.json`


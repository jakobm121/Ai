# Tennis Home/Away Optimizer Report

Generated at: **2026-05-27T07:40:38.256763+02:00**

## Executive summary

- Source picks loaded: **457**
- Settled picks used: **431**
- Minimum sample: **100**
- Rules evaluated: **114582**
- Valid strategies: **21515**

## Whole database baseline

| Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 431 | 183 | 226 | 22 | 44.74% | -4.33u | -1.0% | 2.2501 | -14.26u |

## Best strategy found

**Score:** 56.090118

**Rules:** bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; tour = challenger

| Split | Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full | 103 | 58 | 40 | 5 | 59.18% | 25.2u | 24.47% | 2.1274 | -5.0u |
| Train 75% | 77 | 40 | 32 | 5 | 55.56% | 12.43u | 16.14% | 2.1104 | -4.9u |
| Test 25% | 26 | 18 | 8 | 0 | 69.23% | 12.77u | 49.12% | 2.1777 | -2.0u |

## Recommended live tactic

### Base filter

```json
{
  "bookmakers_min": 6,
  "confidence_max": 88,
  "edge_max": 0.2,
  "tour_level": "challenger"
}
```

### Stake

- Forward test: **0.5u flat** until 50 new live picks.
- Confirmed mode: **1u flat** only after forward confirmation.
- No martingale.

### A-pick priority

| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---|---:|---:|---:|---:|---:|---:|
| gender = men | 91 | 60.47% | 23.69u | 26.03% | 9.24u | 40.17% |
| gender = men; tour = challenger | 91 | 60.47% | 23.69u | 26.03% | 9.24u | 40.17% |
| odds ≥ 2.25 | 34 | 59.38% | 14.76u | 43.41% | 6.53u | 72.56% |
| odds ≥ 2.25; tour = challenger | 34 | 59.38% | 14.76u | 43.41% | 6.53u | 72.56% |
| bookmakers ≤ 7.999; bookmakers ≥ 6 | 24 | 70.83% | 12.07u | 50.29% | 3.49u | 58.17% |

### B-pick watchlist

| Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---|---:|---:|---:|---:|---:|---:|
| tour = challenger | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% |
| qualification = False | 87 | 58.54% | 20.03u | 23.02% | 12.91u | 58.68% |
| qualification = False; tour = challenger | 87 | 58.54% | 20.03u | 23.02% | 12.91u | 58.68% |
| bookmakers ≤ 7.999; bookmakers ≥ 6; tour = challenger | 24 | 70.83% | 12.07u | 50.29% | 3.49u | 58.17% |
| edge ≥ 0.12; gender = men; quality ≥ 85 | 53 | 61.22% | 16.91u | 31.91% | 5.13u | 36.64% |

### Avoid / weak segments

| Reason | Group | Picks | Winrate | Profit | ROI |
|---|---|---:|---:|---:|---:|
| tournament | Francavilla | 9 | 33.33% | -2.63u | -29.22% |
| quality | 80-84.9 | 13 | 41.67% | -2.63u | -20.23% |
| tournament | Zagreb | 8 | 37.5% | -1.64u | -20.5% |
| edge | 0.08-0.099 | 8 | 50.0% | -0.58u | -7.25% |
| odds | 2.05-2.249 | 30 | 46.43% | -0.28u | -0.93% |
| tournament | Tunis | 11 | 44.44% | -0.11u | -1.0% |

## Tactical add-on combinations inside best base

| Rank | Score | Rules | Picks | Winrate | Profit | ROI | Test profit | Test ROI |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 40.400209 | tour = challenger | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% |
| 2 | 38.155129 | gender = men | 91 | 60.47% | 23.69u | 26.03% | 9.24u | 40.17% |
| 3 | 38.155129 | gender = men; tour = challenger | 91 | 60.47% | 23.69u | 26.03% | 9.24u | 40.17% |
| 4 | 34.827386 | qualification = False | 87 | 58.54% | 20.03u | 23.02% | 12.91u | 58.68% |
| 5 | 34.827386 | qualification = False; tour = challenger | 87 | 58.54% | 20.03u | 23.02% | 12.91u | 58.68% |
| 6 | 33.564954 | odds ≥ 2.25 | 34 | 59.38% | 14.76u | 43.41% | 6.53u | 72.56% |
| 7 | 33.564954 | odds ≥ 2.25; tour = challenger | 34 | 59.38% | 14.76u | 43.41% | 6.53u | 72.56% |
| 8 | 32.995708 | bookmakers ≤ 7.999; bookmakers ≥ 6 | 24 | 70.83% | 12.07u | 50.29% | 3.49u | 58.17% |
| 9 | 32.995708 | bookmakers ≤ 7.999; bookmakers ≥ 6; tour = challenger | 24 | 70.83% | 12.07u | 50.29% | 3.49u | 58.17% |
| 10 | 31.800544 | edge ≥ 0.12; gender = men; quality ≥ 85 | 53 | 61.22% | 16.91u | 31.91% | 5.13u | 36.64% |
| 11 | 31.212152 | gender = men; quality ≥ 85 | 60 | 60.71% | 17.25u | 28.75% | 5.97u | 39.8% |
| 12 | 31.212152 | gender = men; quality ≥ 85; tour = challenger | 60 | 60.71% | 17.25u | 28.75% | 5.97u | 39.8% |
| 13 | 31.13011 | gender = men; qualification = False | 76 | 59.15% | 17.52u | 23.05% | 9.38u | 49.37% |
| 14 | 31.13011 | gender = men; qualification = False; tour = challenger | 76 | 59.15% | 17.52u | 23.05% | 9.38u | 49.37% |
| 15 | 31.058902 | quality ≥ 85 | 71 | 58.21% | 17.74u | 24.99% | 7.46u | 41.44% |
| 16 | 31.058902 | quality ≥ 85; tour = challenger | 71 | 58.21% | 17.74u | 24.99% | 7.46u | 41.44% |
| 17 | 30.986332 | edge ≥ 0.12; quality ≥ 85 | 64 | 58.33% | 17.4u | 27.19% | 5.52u | 34.5% |
| 18 | 30.986332 | edge ≥ 0.12; quality ≥ 85; tour = challenger | 64 | 58.33% | 17.4u | 27.19% | 5.52u | 34.5% |
| 19 | 30.928178 | bookmakers ≤ 7.999; bookmakers ≥ 6; gender = men | 21 | 71.43% | 10.47u | 49.86% | 3.49u | 58.17% |
| 20 | 30.928178 | bookmakers ≤ 7.999; bookmakers ≥ 6; gender = men; tour = challenger | 21 | 71.43% | 10.47u | 49.86% | 3.49u | 58.17% |
| 21 | 30.649499 | gender = men; side = home | 45 | 65.91% | 13.88u | 30.84% | 10.93u | 91.08% |
| 22 | 30.649499 | gender = men; side = home; tour = challenger | 45 | 65.91% | 13.88u | 30.84% | 10.93u | 91.08% |
| 23 | 28.494831 | odds ≥ 2.25; side = away | 25 | 60.87% | 11.02u | 44.08% | 3.1u | 44.29% |
| 24 | 28.494831 | odds ≥ 2.25; side = away; tour = challenger | 25 | 60.87% | 11.02u | 44.08% | 3.1u | 44.29% |
| 25 | 28.372803 | side = home | 50 | 63.27% | 13.12u | 26.24% | 11.62u | 89.38% |
| 26 | 28.372803 | side = home; tour = challenger | 50 | 63.27% | 13.12u | 26.24% | 11.62u | 89.38% |
| 27 | 28.32568 | gender = men; odds ≥ 2.25 | 30 | 57.14% | 11.51u | 38.37% | 5.14u | 64.25% |
| 28 | 28.32568 | gender = men; odds ≥ 2.25; tour = challenger | 30 | 57.14% | 11.51u | 38.37% | 5.14u | 64.25% |
| 29 | 27.906331 | odds ≥ 2.25; qualification = False | 28 | 57.69% | 11.16u | 39.86% | 3.75u | 53.57% |
| 30 | 27.906331 | odds ≥ 2.25; qualification = False; tour = challenger | 28 | 57.69% | 11.16u | 39.86% | 3.75u | 53.57% |

## Top global strategies

| Rank | Score | Picks | Winrate | Profit | ROI | Test profit | Test ROI | Max DD | Rules |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; tour = challenger |
| 2 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; edge ≤ 0.2; tour = challenger |
| 3 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 93; edge ≤ 0.2; tour = challenger |
| 4 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; confidence ≥ 50; edge ≤ 0.2; tour = challenger |
| 5 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; confidence ≥ 55; edge ≤ 0.2; tour = challenger |
| 6 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; confidence ≥ 60; edge ≤ 0.2; tour = challenger |
| 7 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; confidence ≥ 65; edge ≤ 0.2; tour = challenger |
| 8 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; confidence ≥ 70; edge ≤ 0.2; tour = challenger |
| 9 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; quality ≥ 50; tour = challenger |
| 10 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; quality ≥ 55; tour = challenger |
| 11 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; quality ≥ 60; tour = challenger |
| 12 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; quality ≤ 93; tour = challenger |
| 13 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; edge ≥ 0; tour = challenger |
| 14 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; edge ≥ 0.02; tour = challenger |
| 15 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; edge ≥ 0.04; tour = challenger |
| 16 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; edge ≥ 0.06; tour = challenger |
| 17 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; odds ≥ 1.3; tour = challenger |
| 18 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; odds ≥ 1.45; tour = challenger |
| 19 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; odds ≥ 1.6; tour = challenger |
| 20 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 88; edge ≤ 0.2; odds ≤ 3.0; tour = challenger |
| 21 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; confidence ≥ 50; edge ≤ 0.2; tour = challenger |
| 22 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; confidence ≥ 55; edge ≤ 0.2; tour = challenger |
| 23 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; confidence ≥ 60; edge ≤ 0.2; tour = challenger |
| 24 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; confidence ≥ 65; edge ≤ 0.2; tour = challenger |
| 25 | 56.090118 | 103 | 59.18% | 25.2u | 24.47% | 12.77u | 49.12% | -5.0u | bookmakers ≥ 6; confidence ≤ 90; confidence ≥ 70; edge ≤ 0.2; tour = challenger |

## Feature ranges inside best strategy

| Feature | Min | P25 | Median | P75 | Max | Avg |
|---|---:|---:|---:|---:|---:|---:|
| confidence | 73.4 | 88.0 | 88.0 | 88.0 | 88.0 | 86.965 |
| quality | 63.7 | 84.1 | 87.5 | 90.9 | 92.9 | 85.6592 |
| edge | 0.0681 | 0.1072 | 0.1305 | 0.1575 | 0.2 | 0.1318 |
| odds | 1.69 | 1.91 | 2.1 | 2.3 | 2.8 | 2.1274 |
| bookmakers | 6 | 8 | 9 | 10 | 12 | 9.0 |

## Bucket analysis inside best strategy

### confidence

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 88-89.9 | 85 | 58.02% | 15.14u | 17.81% | 2.06 | -5.0u |
| 80-84.9 | 9 | 62.5% | 4.01u | 44.56% | 2.42 | -1.0u |
| 75-79.9 | 2 | 100.0% | 3.6u | 180.0% | 2.8 | 0.0u |
| <75 | 2 | 100.0% | 3.04u | 152.0% | 2.52 | 0.0u |
| 85-87.9 | 5 | 40.0% | -0.59u | -11.8% | 2.32 | -1.09u |

### quality

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 85+ | 71 | 58.21% | 17.74u | 24.99% | 2.1958 | -5.0u |
| <72 | 9 | 88.89% | 7.86u | 87.33% | 2.0844 | -1.0u |
| 72-74.9 | 3 | 66.67% | 1.73u | 57.67% | 2.1467 | -1.0u |
| 75-79.9 | 7 | 57.14% | 0.5u | 7.14% | 1.8914 | -2.0u |
| 80-84.9 | 13 | 41.67% | -2.63u | -20.23% | 1.9062 | -5.23u |

### edge

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 0.12+ | 66 | 56.45% | 15.4u | 23.33% | 2.2244 | -4.0u |
| 0.06-0.079 | 13 | 76.92% | 7.61u | 58.54% | 2.0077 | -1.0u |
| 0.10-0.119 | 16 | 60.0% | 2.77u | 17.31% | 1.9625 | -3.0u |
| 0.08-0.099 | 8 | 50.0% | -0.58u | -7.25% | 1.8513 | -3.0u |

### odds

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 2.25+ | 34 | 59.38% | 14.76u | 43.41% | 2.4332 | -2.0u |
| 1.90-2.049 | 16 | 75.0% | 7.58u | 47.38% | 1.9544 | -2.0u |
| 1.75-1.899 | 19 | 61.11% | 2.05u | 10.79% | 1.8158 | -2.16u |
| 1.60-1.749 | 4 | 75.0% | 1.09u | 27.25% | 1.7 | -1.0u |
| 2.05-2.249 | 30 | 46.43% | -0.28u | -0.93% | 2.1273 | -3.0u |

### market_gap

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 103 | 59.18% | 25.2u | 24.47% | 2.1274 | -5.0u |

### strength_gap

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 103 | 59.18% | 25.2u | 24.47% | 2.1274 | -5.0u |

### bookmakers

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 8+ | 79 | 55.41% | 13.13u | 16.62% | 2.1362 | -5.0u |
| 6-7 | 24 | 70.83% | 12.07u | 50.29% | 2.0983 | -1.07u |

### rank

| Bucket | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| unknown | 103 | 59.18% | 25.2u | 24.47% | 2.1274 | -5.0u |

## Categorical breakdown inside best strategy

### By side

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| home | 50 | 63.27% | 13.12u | 26.24% | 2.0064 | -5.72u |
| away | 53 | 55.1% | 12.08u | 22.79% | 2.2415 | -4.39u |

### By gender

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| men | 91 | 60.47% | 23.69u | 26.03% | 2.1179 | -5.0u |
| women | 12 | 50.0% | 1.51u | 12.58% | 2.1992 | -3.0u |

### By tour level

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| challenger | 103 | 59.18% | 25.2u | 24.47% | 2.1274 | -5.0u |

### By bookmaker

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Pncl | 42 | 60.53% | 9.98u | 23.76% | 2.129 | -4.21u |
| Unibet | 24 | 62.5% | 8.18u | 34.08% | 2.1129 | -3.0u |
| bet365 | 12 | 63.64% | 4.77u | 39.75% | 2.1875 | -3.0u |
| Betfair | 6 | 66.67% | 3.85u | 64.17% | 2.3583 | -1.0u |
| Betano | 12 | 58.33% | 1.22u | 10.17% | 1.925 | -3.0u |
| 888Sport | 1 | 100.0% | 1.1u | 110.0% | 2.1 | 0.0u |
| 10Bet | 1 | 0.0% | -1.0u | -100.0% | 2.2 | -1.0u |
| Sbo | 1 | 0.0% | -1.0u | -100.0% | 2.51 | -1.0u |
| WilliamHill | 4 | 25.0% | -1.9u | -47.5% | 2.17 | -3.0u |

### By tournament

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Bengaluru 3 (India) - Qualification | 5 | 100.0% | 7.05u | 141.0% | 2.41 | 0.0u |
| Valencia | 10 | 80.0% | 6.91u | 69.1% | 2.094 | -1.0u |
| Wuxi | 3 | 100.0% | 3.18u | 106.0% | 2.06 | 0.0u |
| Little Rock | 5 | 80.0% | 2.75u | 55.0% | 2.052 | -1.0u |
| Istanbul (Turkey) - Qualification | 10 | 60.0% | 2.37u | 23.7% | 2.124 | -2.0u |
| Brazzaville | 2 | 100.0% | 2.07u | 103.5% | 2.035 | 0.0u |
| Jiujiang (China) - Qualification | 3 | 66.67% | 1.9u | 63.33% | 2.35 | -1.0u |
| Kosice | 5 | 60.0% | 1.44u | 28.8% | 2.088 | -2.0u |
| Paris | 3 | 66.67% | 1.16u | 38.67% | 2.21 | -1.0u |
| Chisinau | 1 | 100.0% | 1.12u | 112.0% | 2.12 | 0.0u |
| Centurion (South Africa) - Qualification | 1 | 100.0% | 0.95u | 95.0% | 1.95 | 0.0u |
| Cervia (Italy) - Qualification | 3 | 66.67% | 0.95u | 31.67% | 2.1133 | -1.0u |
| Cordoba 2 | 5 | 66.67% | 0.65u | 13.0% | 2.086 | -1.0u |
| Bengaluru 2 | 2 | 50.0% | 0.5u | 25.0% | 2.275 | -1.0u |
| Oeiras 6 | 5 | 50.0% | 0.1u | 2.0% | 2.012 | -1.0u |
| Tunis | 11 | 44.44% | -0.11u | -1.0% | 2.2173 | -3.3u |
| Vicenza | 3 | 33.33% | -0.2u | -6.67% | 2.3367 | -1.0u |
| Bordeaux | 7 | 42.86% | -1.32u | -18.86% | 1.91 | -2.0u |
| Zagreb | 8 | 37.5% | -1.64u | -20.5% | 2.1088 | -4.0u |
| Parma | 2 | 0.0% | -2.0u | -100.0% | 2.065 | -2.0u |

## Files generated

- `tennis_optimizer/tennis_optimizer_report.md`
- `tennis_optimizer/tennis_best_rules.json`
- `tennis_optimizer/tennis_optimizer_table.json`
- `tennis_optimizer/tennis_optimizer_picks.json`
- `tennis_optimizer/tennis_optimizer_tactic.json`
- `tennis_optimizer/tennis_optimizer_debug.json`
- `tennis_optimizer/tennis_optimizer_summary.json`


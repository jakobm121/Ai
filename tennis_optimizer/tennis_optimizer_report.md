# Tennis Home/Away Optimizer Report

Generated at: **2026-05-27T01:41:48.662694+02:00**

## Executive summary

- Source picks loaded: **442**
- Settled picks used: **431**
- Minimum sample per valid strategy: **100 picks**
- Search mode: **beam search**
- Beam width: **350**
- Max rules per tactic: **6**

## Whole database baseline

| Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 431 | 183 | 226 | 22 | 44.74% | -4.33u | -1.0% | 2.2501 | -14.26u |

## Best strategy found

**Score:** 35.889873

**Rules:** tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75

| Split | Picks | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full | 121 | 62 | 52 | 7 | 54.39% | 23.13u | 19.12% | 2.2571 | -4.5u |
| Train 75% | 90 | 47 | 38 | 5 | 55.29% | 18.64u | 20.71% | 2.2292 | -4.65u |
| Test 25% | 31 | 15 | 14 | 2 | 51.72% | 4.49u | 14.48% | 2.3381 | -4.0u |

## Recommended tactic

Use this as a filter layer on top of the existing tennis home/away machine:

```json
{
  "tour_level": "challenger",
  "gender": "men",
  "bookmakers_min": 6,
  "odds_min": 1.75
}
```

Stake suggestion:

- Historical test uses **flat 1u**.
- Conservative forward test: **0.5u flat** for at least 50 new picks.
- No martingale.

Risk warning: this is historical optimization. The most important number is Test 25% and then forward tracking.

## Top strategies

| Rank | Score | Picks | Winrate | Profit | ROI | Max DD | Rules |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75 |
| 2 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50 |
| 3 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 55 |
| 4 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 60 |
| 5 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 65 |
| 6 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 70 |
| 7 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; quality ≥ 50 |
| 8 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; quality ≥ 55 |
| 9 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; quality ≥ 60 |
| 10 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; edge ≥ 0.0 |
| 11 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; edge ≥ 0.02 |
| 12 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; edge ≥ 0.04 |
| 13 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; edge ≥ 0.06 |
| 14 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; odds ≤ 3.0 |
| 15 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; quality ≥ 50 |
| 16 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; quality ≥ 55 |
| 17 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; quality ≥ 60 |
| 18 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; edge ≥ 0.0 |
| 19 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; edge ≥ 0.02 |
| 20 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; edge ≥ 0.04 |
| 21 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; edge ≥ 0.06 |
| 22 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 50; odds ≤ 3.0 |
| 23 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 55; quality ≥ 50 |
| 24 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 55; quality ≥ 55 |
| 25 | 35.889873 | 121 | 54.39% | 23.13u | 19.12% | -4.5u | tour = challenger; gender = men; bookmakers ≥ 6; odds ≥ 1.75; confidence ≥ 55; quality ≥ 60 |

## Best strategy selected picks sample

| Date | Match | Bet | Result | Odds | Profit |
|---|---|---|---:|---:|---:|
| 2026-05-05 07:30 | A. Bolt - F. Sun | F. Sun | win | 2.13 | 1.13 |
| 2026-05-05 11:00 | A. Barrena - A. Holmgren | A. Holmgren | win | 2.33 | 1.33 |
| 2026-05-05 10:30 | L. Castelnuovo - O. Milic | L. Castelnuovo | loss | 2.4 | -1.0 |
| 2026-05-05 11:00 | A. Barrena - A. Holmgren | A. Holmgren | win | 2.22 | 1.22 |
| 2026-05-05 11:25 | L. Castelnuovo - O. Milic | L. Castelnuovo | loss | 2.63 | -1.0 |
| 2026-05-05 12:35 | F. Gill - Z. Kolar | F. Gill | loss | 1.93 | -1.0 |
| 2026-05-05 20:00 | A. Guerrieri - C. H. Tseng | A. Guerrieri | loss | 1.85 | -1.0 |
| 2026-05-06 11:00 | J. C. Prado Angelo - B. Gadamauri | B. Gadamauri | loss | 2.23 | -1.0 |
| 2026-05-05 20:00 | M. Tobon - E. Ribeiro | M. Tobon | win | 2.5 | 1.5 |
| 2026-05-06 11:00 | J. C. Prado Angelo - B. Gadamauri | B. Gadamauri | loss | 2.28 | -1.0 |
| 2026-05-06 11:00 | J. C. Prado Angelo - B. Gadamauri | B. Gadamauri | loss | 2.28 | -1.0 |
| 2026-05-06 12:45 | A. Holmgren - G. Den Ouden | A. Holmgren | win | 2.25 | 1.25 |
| 2026-05-07 09:30 | M. Jones - A. Santillan | A. Santillan | win | 2.12 | 1.12 |
| 2026-05-07 18:00 | F. Ferreira Silva - C. H. Tseng | F. Ferreira Silva | loss | 2.1 | -1.0 |
| 2026-05-07 18:30 | M. Tobon - F. Mena | M. Tobon | win | 2.5 | 1.5 |
| 2026-05-08 16:10 | A. Holmgren - M. Schoenhaus | A. Holmgren | win | 1.82 | 0.82 |
| 2026-05-08 16:10 | I. Vasa - F. Ribero | F. Ribero | win | 2.25 | 1.25 |
| 2026-05-08 16:10 | F. Bax - M. Erhard | F. Bax | win | 1.82 | 0.82 |
| 2026-05-08 22:00 | M. Pucinelli de Almeida - M. Tobon | M. Tobon | loss | 2.83 | -1.0 |
| 2026-05-09 18:30 | M. Pucinelli de Almeida - F. Roncadelli | F. Roncadelli | win | 2.71 | 1.71 |
| 2026-05-10 10:00 | Y. Bu - S. Kwon | S. Kwon | win | 1.93 | 0.93 |
| 2026-05-10 16:15 | N. Gombos - T. Zink | T. Zink | win | 2.37 | 1.37 |
| 2026-05-11 16:30 | Dar. Blanch - J. Pinnington Jones | Dar. Blanch | loss | 1.78 | -1.0 |
| 2026-05-11 17:25 | M. Mrva - F. Cina | M. Mrva | loss | 2.44 | -1.0 |
| 2026-05-11 11:30 | F. Agamenone - A. Ghibaudo | A. Ghibaudo | loss | 2.48 | -1.0 |
| 2026-05-11 14:00 | R. Bertola - C. Sanchez Jover | C. Sanchez Jover | win | 2.54 | 1.54 |
| 2026-05-11 14:10 | N. Fatic - D. Kuzmanov | N. Fatic | win | 1.84 | 0.84 |
| 2026-05-11 14:30 | T. Boyer - A. Dougaz | A. Dougaz | push | 2.2 | 0.0 |
| 2026-05-11 14:30 | S. Nagal - P. Herbert | P. Herbert | loss | 2.05 | -1.0 |
| 2026-05-11 14:40 | J. Reis Da Silva - L. Pavlovic | J. Reis Da Silva | win | 2.23 | 1.23 |
| 2026-05-11 19:25 | B. Harris - P. Brunclik | P. Brunclik | win | 2.0 | 1.0 |
| 2026-05-12 12:00 | T. Pereira - G. Elias | T. Pereira | push | 1.8 | 0.0 |
| 2026-05-12 14:30 | R. Matsuda - C. Papa | C. Papa | win | 2.5 | 1.5 |
| 2026-05-13 17:55 | M. Dodig - A. Holmgren | M. Dodig | loss | 2.1 | -1.0 |
| 2026-05-12 14:30 | R. Hijikata - A. Vukic | R. Hijikata | loss | 1.76 | -1.0 |
| 2026-05-12 15:00 | G. I. Justo - L. J. Rodriguez | L. J. Rodriguez | push | 2.13 | 0.0 |
| 2026-05-12 16:00 | P. Carreno-Busta - F. Comesana | P. Carreno-Busta | win | 1.84 | 0.84 |
| 2026-05-12 23:00 | M. Pucinelli de Almeida - H. Casanova | H. Casanova | push | 2.55 | 0.0 |
| 2026-05-13 11:30 | N. Fatic - E. Moller | N. Fatic | loss | 2.5 | -1.0 |
| 2026-05-12 11:00 | I. Simakin - L. Lokoli | I. Simakin | loss | 2.5 | -1.0 |
| 2026-05-13 10:00 | T. Seyboth Wild - D. E. Galan | D. E. Galan | win | 2.15 | 1.15 |
| 2026-05-12 11:30 | R. Sakamoto - C. H. Tseng | R. Sakamoto | win | 2.05 | 1.05 |
| 2026-05-12 13:05 | C. Sanchez Jover - T. Daniel | T. Daniel | win | 2.3 | 1.3 |
| 2026-05-12 13:00 | J. J. Schwaerzler - F. Agamenone | F. Agamenone | loss | 2.85 | -1.0 |
| 2026-05-12 13:00 | G. Blancaneaux - S. Nagal | G. Blancaneaux | win | 2.38 | 1.38 |
| 2026-05-12 14:30 | L. Djere - G. Heide | G. Heide | loss | 2.38 | -1.0 |
| 2026-05-12 18:20 | Z. Kolar - Z. Zhang | Z. Kolar | win | 2.1 | 1.1 |
| 2026-05-13 11:30 | T. Monteiro - A. Andrade | T. Monteiro | loss | 1.8 | -1.0 |
| 2026-05-13 12:30 | S. Dostanic - C. Rodesch | S. Dostanic | loss | 2.75 | -1.0 |
| 2026-05-13 12:30 | O. Virtanen - G. Mpetshi Perricard | O. Virtanen | loss | 2.05 | -1.0 |

## Feature ranges inside best strategy

| Feature | Min | P25 | Median | P75 | Max | Avg |
|---|---:|---:|---:|---:|---:|---:|
| confidence | 73.4 | 88.0 | 88.0 | 88.0 | 88.0 | 87.119 |
| quality | 63.7 | 85.7 | 88.5 | 90.9 | 92.9 | 86.8099 |
| edge | 0.0681 | 0.1165 | 0.1483 | 0.2124 | 0.3091 | 0.1619 |
| odds | 1.75 | 2.0 | 2.25 | 2.5 | 2.85 | 2.2571 |
| bookmakers | 6 | 8 | 10 | 10 | 12 | 9.0826 |

## Breakdown of best strategy

### By side

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| home | 63 | 58.33% | 14.48u | 22.98% | 2.1911 | -4.0u |
| away | 58 | 50.0% | 8.65u | 14.91% | 2.3288 | -5.41u |

### By gender

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| men | 121 | 54.39% | 23.13u | 19.12% | 2.2571 | -4.5u |

### By tour level

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| challenger | 121 | 54.39% | 23.13u | 19.12% | 2.2571 | -4.5u |

### By bookmaker

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Pncl | 55 | 56.86% | 12.77u | 23.22% | 2.2745 | -3.0u |
| Unibet | 26 | 56.0% | 5.02u | 19.31% | 2.1877 | -2.0u |
| bet365 | 16 | 53.33% | 3.52u | 22.0% | 2.32 | -4.0u |
| Betano | 8 | 62.5% | 2.12u | 26.5% | 1.99 | -1.0u |
| Betfair | 8 | 50.0% | 1.85u | 23.12% | 2.41 | -2.0u |
| Sbo | 4 | 33.33% | -0.25u | -6.25% | 2.5325 | -2.0u |
| WilliamHill | 4 | 25.0% | -1.9u | -47.5% | 2.17 | -3.0u |

### By tournament

| Group | Picks | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Bengaluru 3 (India) - Qualification | 7 | 85.71% | 7.84u | 112.0% | 2.4514 | -1.0u |
| Bordeaux | 10 | 60.0% | 3.78u | 37.8% | 2.147 | -2.0u |
| Santos | 4 | 75.0% | 3.71u | 92.75% | 2.635 | -1.0u |
| Valencia | 14 | 57.14% | 2.91u | 20.79% | 2.2329 | -2.0u |
| Centurion (South Africa) - Qualification | 2 | 100.0% | 2.36u | 118.0% | 2.18 | 0.0u |
| Brazzaville | 2 | 100.0% | 2.07u | 103.5% | 2.035 | 0.0u |
| Little Rock | 8 | 66.67% | 1.75u | 21.88% | 2.2325 | -1.0u |
| Istanbul (Turkey) - Qualification | 5 | 60.0% | 1.23u | 24.6% | 2.194 | -2.0u |
| Wuxi | 5 | 60.0% | 1.18u | 23.6% | 2.242 | -2.0u |
| Chisinau | 1 | 100.0% | 1.12u | 112.0% | 2.12 | 0.0u |
| Cervia (Italy) - Qualification | 3 | 66.67% | 0.95u | 31.67% | 2.1133 | -1.0u |
| Tunis | 11 | 44.44% | 0.78u | 7.09% | 2.4018 | -4.0u |
| Cordoba 2 | 5 | 66.67% | 0.65u | 13.0% | 2.086 | -1.0u |
| Bengaluru 2 | 2 | 50.0% | 0.5u | 25.0% | 2.275 | -1.0u |
| Kosice | 7 | 42.86% | -0.56u | -8.0% | 2.2314 | -2.0u |

## Files generated

- `tennis_optimizer/tennis_optimizer_report.md`
- `tennis_optimizer/tennis_best_rules.json`
- `tennis_optimizer/tennis_optimizer_table.json`
- `tennis_optimizer/tennis_optimizer_picks.json`
- `tennis_optimizer/tennis_optimizer_debug.json`
- `tennis_optimizer/tennis_optimizer_summary.json`


# Lucija Backtest Report

Generated at: **2026-05-31T22:44:03.024027+02:00**

## Input

- Source file: `data/tennis_totals_results.json`
- Source picks loaded: **542**
- Settled picks available: **523**

## Rules

### V1 original
```json
{
  "avg_close_set_max": 0.55,
  "avg_close_set_min": 0.2,
  "avg_three_set_min": 0.15,
  "confidence_min": 80,
  "market_gap_min": 0.25,
  "quality_min": 72,
  "strength_gap_max": 30
}
```

### V2 under
```json
{
  "side": "under",
  "avg_close_set_max": 0.35,
  "avg_three_set_max": 0.35,
  "confidence_min": 80,
  "h2h_max": 0,
  "market_gap_min": 0.25,
  "quality_min": 72,
  "strength_gap_max": 30
}
```

### V3 over
```json
{
  "side": "over",
  "avg_close_set_min": 0.3,
  "avg_three_set_min": 0.35,
  "confidence_min": 0,
  "market_gap_max": 0.35,
  "quality_min": 0,
  "strength_gap_max": 35
}
```

## Main comparison

| Model | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All settled totals | 523 | 523 | 0 | 231 | 256 | 36 | 47.43% | -13.57u | -2.59% | 2.0576 | -44.03u |
| V1 original | 158 | 153 | 5 | 91 | 59 | 3 | 60.67% | 36.03u | 23.55% | 2.0512 | -7.92u |
| V2 under | 61 | 58 | 3 | 36 | 18 | 4 | 66.67% | 20.47u | 35.29% | 2.0759 | -5.0u |
| V3 over | 63 | 60 | 3 | 27 | 28 | 5 | 49.09% | -3.44u | -5.73% | 1.9395 | -10.59u |

## Train / test

| Model | Split | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | train_75 | 118 | 118 | 73 | 43 | 62.93% | 32.88u | 27.86% | 2.0404 | -5.7u |
| V1 | test_25 | 40 | 35 | 18 | 16 | 52.94% | 3.15u | 9.0% | 2.0877 | -3.0u |
| V2 | train_75 | 45 | 45 | 29 | 14 | 67.44% | 16.88u | 37.51% | 2.0689 | -5.0u |
| V2 | test_25 | 16 | 13 | 7 | 4 | 63.64% | 3.59u | 27.62% | 2.1 | -2.0u |
| V3 | train_75 | 47 | 47 | 19 | 23 | 45.24% | -5.56u | -11.83% | 1.9443 | -10.59u |
| V3 | test_25 | 16 | 13 | 8 | 5 | 61.54% | 2.12u | 16.31% | 1.9223 | -2.11u |

## V1 original selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | A. Bondar - Q. Zheng | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.45 | 0.3083 | 0.3695 | 26.1 |
| 2026-05-05 | L. Pigossi - L. Cortez Llorca | OVER 20.5 games | 1.87 | win | 0.87 | 20.5 | 0.35 | 0.4083 | 0.2585 | 18.9 |
| 2026-05-05 | M. Krumich - G. Piraino | OVER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.5786 | 0.3703 | 0.4572 | 17.69 |
| 2026-05-05 | A. Li - S. Zhang | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2167 | 0.3223 | 0.4751 | 18.35 |
| 2026-05-06 | T. Townsend - N. Brancaccio | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.254 | 0.2976 | 0.4895 | 23.58 |
| 2026-05-06 | N. Basiletti - A. Tomljanovic | OVER 20.5 games | 2.15 | win | 1.15 | 20.5 | 0.4778 | 0.4315 | 0.5697 | 0.17 |
| 2026-05-07 | D. Shapovalov - M. Navone | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.3333 | 0.4167 | 0.2791 | 26.89 |
| 2026-05-07 | H. Medjedovic - V. Royer | UNDER 21.5 games | 2.17 | win | 1.17 | 21.5 | 0.25 | 0.3021 | 0.4233 | 19.88 |
| 2026-05-08 | A. Tubello - P. Kudermetova | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4778 | 0.3417 | 0.3597 | 2.6 |
| 2026-05-08 | L. Pigossi - G. Maristany | OVER 20.5 games | 1.98 | loss | -1.0 | 20.5 | 0.45 | 0.4667 | 0.3893 | 23.7 |
| 2026-05-08 | D. Vekic - M. Ristic | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.2125 | 0.3542 | 0.4707 | 14.48 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 0.285 | 3.78 |
| 2026-05-08 | B. Van De Zandschulp - A. Kovacevic | UNDER 21.5 games | 2.14 | win | 1.14 | 21.5 | 0.1875 | 0.4062 | 0.5035 | 28.25 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 0.4802 | 16.45 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 0.5758 | 6.45 |
| 2026-05-09 | Q. Zheng - J. Ostapenko | OVER 20.5 games | 1.91 | win | 0.91 | 20.5 | 0.5 | 0.5167 | 0.336 | 6.4 |
| 2026-05-09 | D. Vekic - G. Maristany | UNDER 19.5 games | 2.13 | win | 1.13 | 19.5 | 0.15 | 0.4584 | 0.4767 | 14.6 |
| 2026-05-09 | G. Heide - A. Holmgren | UNDER 20.5 games | 2.03 | loss | -1.0 | 20.5 | 0.1736 | 0.4896 | 0.5504 | 18.32 |
| 2026-05-09 | O. Oliynykova - L. Noskova | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.325 | 0.3729 | 0.4835 | 23.12 |
| 2026-05-09 | T. M. Etcheverry - M. Bellucci | UNDER 21.5 games | 2.05 | loss | -1.0 | 21.5 | 0.3493 | 0.4828 | 0.4543 | 24.23 |
| 2026-05-09 | Q. Zheng - J. Ostapenko | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.5278 | 0.513 | 0.285 | 11.41 |
| 2026-05-09 | H. Medjedovic - J. Fonseca | UNDER 22.5 games | 1.99 | win | 0.99 | 22.5 | 0.2847 | 0.3947 | 0.2536 | 16.03 |
| 2026-05-09 | M. Pucinelli de Almeida - F. Roncadelli | UNDER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.4072 | 0.3571 | 0.299 | 26.51 |
| 2026-05-09 | B. Bencic - A. Kalinskaya | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.2222 | 0.3889 | 0.4148 | 21.78 |
| 2026-05-10 | E. Svitolina - H. Baptiste | UNDER 20.5 games | 2.13 | win | 1.13 | 20.5 | 0.2222 | 0.4166 | 0.3308 | 3.55 |
| 2026-05-10 | M. Keys - N. Bartunkova | OVER 20.5 games | 1.98 | win | 0.98 | 20.5 | 0.575 | 0.3084 | 0.4488 | 8.78 |
| 2026-05-10 | D. Vekic - M. Timofeeva | UNDER 20.5 games | 1.97 | win | 0.97 | 20.5 | 0.225 | 0.4146 | 0.3241 | 18.9 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 0.433 | 7.3 |
| 2026-05-11 | N. McDonald - D. Glinka | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.1736 | 0.3588 | 0.256 | 7.03 |
| 2026-05-11 | G. Den Ouden - D. Added | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.275 | 0.4416 | 0.4288 | 9.32 |
| 2026-05-11 | J. Pegula - A. Potapova | UNDER 21.5 games | 1.99 | win | 0.99 | 21.5 | 0.4222 | 0.3574 | 0.3053 | 12.17 |
| 2026-05-11 | P. Llamas Ruiz - D. Medvedev | OVER 20.5 games | 1.9 | win | 0.9 | 20.5 | 0.4732 | 0.3541 | 0.3695 | 16.14 |
| 2026-05-11 | L. Draxl - E. Nava | UNDER 20.5 games | 2.09 | loss | -1.0 | 20.5 | 0.2083 | 0.3646 | 0.4955 | 15.55 |
| 2026-05-12 | K. Birrell - K. Boulter | OVER 19.5 games | 1.83 | win | 0.83 | 19.5 | 0.4822 | 0.3215 | 0.4625 | 3.95 |
| 2026-05-12 | K. Khachanov - D. Prizmic | UNDER 22.5 games | 2.05 | win | 1.05 | 22.5 | 0.2083 | 0.4479 | 0.2806 | 25.88 |
| 2026-05-12 | C. Garin - L. Midon | OVER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.6072 | 0.4702 | 0.6423 | 2.04 |
| 2026-05-12 | L. Darderi - A. Zverev | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.2222 | 0.3148 | 0.594 | 22.0 |
| 2026-05-12 | S. De La Fuente - M. A. Dellien Velasco | UNDER 19.5 games | 2.1 | win | 1.1 | 19.5 | 0.2611 | 0.2028 | 0.4811 | 7.08 |
| 2026-05-12 | A. Rublev - N. Basilashvili | UNDER 21.5 games | 2.11 | loss | -1.0 | 21.5 | 0.1945 | 0.463 | 0.4966 | 8.06 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-12 | J. B. Torres - B. Fernandez | UNDER 19.5 games | 2.0 | loss | -1.0 | 19.5 | 0.2611 | 0.3491 | 0.6325 | 25.81 |
| 2026-05-13 | J. Pegula - I. Swiatek | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.3166 | 0.2703 | 0.3993 | 2.63 |
| 2026-05-13 | F. Urgesi - V. Golubic | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.3333 | 0.2408 | 0.5416 | 2.33 |
| 2026-05-13 | M. Berrettini - T. Daniel | UNDER 20.5 games | 1.98 | win | 0.98 | 20.5 | 0.325 | 0.4208 | 0.6752 | 19.12 |
| 2026-05-13 | E. Svitolina - E. Rybakina | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.1805 | 0.3599 | 0.3835 | 22.72 |
| 2026-05-13 | R. Jodar - L. Darderi | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.3611 | 0.2963 | 0.3546 | 24.51 |
| 2026-05-14 | J. Reis Da Silva - E. Moller | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.2625 | 0.2437 | 0.3466 | 26.38 |
| 2026-05-14 | A. Sasnovich - A. Blinkova | UNDER 20.5 games | 1.97 | loss | -1.0 | 20.5 | 0.2167 | 0.375 | 0.3089 | 16.57 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 0.5207 | 9.83 |
| 2026-05-14 | D. Dedura - L. Neumayer | UNDER 20.5 games | 2.12 | win | 1.12 | 20.5 | 0.2361 | 0.2291 | 0.2667 | 29.38 |
| 2026-05-14 | S. Cirstea - C. Gauff | OVER 20.5 games | 1.95 | loss | -1.0 | 20.5 | 0.4667 | 0.4083 | 0.3502 | 2.3 |
| 2026-05-14 | S. Bandecchi - J. Bouzas Maneiro | UNDER 19.5 games | 1.99 | loss | -1.0 | 19.5 | 0.2222 | 0.4074 | 0.6325 | 14.78 |
| 2026-05-15 | A. Tabilo - D. Lajovic | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.1825 | 0.4669 | 0.4936 | 13.17 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | R. Hijikata - T. Daniel | UNDER 21.5 games | 2.04 | loss | -1.0 | 21.5 | 0.275 | 0.3208 | 0.2507 | 27.28 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 0.3448 | 13.95 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 0.7922 | 18.7 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-17 | D. Dedura - F. Tiafoe | UNDER 20.5 games | 2.2 | win | 1.2 | 20.5 | 0.1984 | 0.3995 | 0.4357 | 1.02 |
| 2026-05-17 | L. Jeanjean - L. Fernandez | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.3541 | 0.3125 | 0.4974 | 12.67 |
| 2026-05-17 | T. Paul - E. Quinn | UNDER 21.5 games | 2.17 | win | 1.17 | 21.5 | 0.381 | 0.4365 | 0.4148 | 29.17 |
| 2026-05-17 | M. Kecmanovic - D. Vallejo | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.1667 | 0.4352 | 0.2991 | 24.56 |
| 2026-05-18 | S. Baez - A. Michelsen | UNDER 21.5 games | 2.11 | win | 1.11 | 21.5 | 0.2777 | 0.4074 | 0.2528 | 9.66 |
| 2026-05-18 | S. Shimabukuro - S. Sakellaridis | UNDER 21.5 games | 2.16 | loss | -1.0 | 21.5 | 0.1984 | 0.3717 | 0.4171 | 26.66 |
| 2026-05-18 | T. Atmane - T. M. Etcheverry | OVER 22.5 games | 1.93 | loss | -1.0 | 22.5 | 0.4028 | 0.5081 | 0.297 | 4.22 |
| 2026-05-18 | Y. Yuan - H. Dart | OVER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.55 | 0.2334 | 0.5697 | 3.4 |
| 2026-05-18 | D. Altmaier - R. Hijikata | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2143 | 0.3215 | 0.3966 | 8.72 |
| 2026-05-18 | N. Mejia - P. Llamas Ruiz | UNDER 19.5 games | 2.01 | loss | -1.0 | 19.5 | 0.25 | 0.2812 | 0.711 | 22.08 |
| 2026-05-19 | L. Darderi - R. A. Burruchaga | UNDER 21.5 games | 2.0 | loss | -1.0 | 21.5 | 0.3 | 0.425 | 0.2902 | 2.9 |
| 2026-05-19 | L. Midon - R. Carballes Baena | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.6507 | 0.3651 | 0.3248 | 22.39 |
| 2026-05-19 | Y. Kabbaj - B. Cengiz | OVER 20.5 games | 1.92 | win | 0.92 | 20.5 | 0.4166 | 0.4713 | 0.3308 | 21.23 |
| 2026-05-19 | L. Zaar - J. Bouzas Maneiro | UNDER 19.5 games | 2.06 | win | 1.06 | 19.5 | 0.3222 | 0.2815 | 0.4974 | 16.76 |
| 2026-05-19 | N. Honda - P. Sekulic | UNDER 20.5 games | 2.05 | push | 0.0 | 20.5 | 0.2143 | 0.2262 | 0.5649 | 19.56 |
| 2026-05-19 | B. Hassan - F. C. Jianu | UNDER 20.5 games | 2.03 | win | 1.03 | 20.5 | 0.3 | 0.3167 | 0.3106 | 23.6 |
| 2026-05-19 | L. Giustino - K. Jacquet | OVER 21.5 games | 2.04 | win | 1.04 | 21.5 | 0.6111 | 0.3611 | 0.4321 | 16.72 |
| 2026-05-19 | E. Ymer - A. Fery | UNDER 21.5 games | 2.05 | win | 1.05 | 21.5 | 0.3095 | 0.549 | 0.402 | 20.18 |
| 2026-05-19 | I. Burillo Escorihuela - V. Tomova | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2 | 0.3334 | 0.4698 | 17.1 |
| 2026-05-19 | P. Kudermetova - A. Koevermans | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.3333 | 0.4352 | 0.3254 | 27.11 |
| 2026-05-19 | T. Schoolkate - K. Coppejans | UNDER 21.5 games | 2.0 | loss | -1.0 | 21.5 | 0.1548 | 0.4385 | 0.402 | 14.24 |
| 2026-05-20 | T. Faurel - J. Clarke | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.2056 | 0.288 | 0.3868 | 21.45 |
| 2026-05-20 | L. Vithoontien - P. Bar Biryukov | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.2 | 0.425 | 0.5894 | 0.9 |
| 2026-05-20 | Y. Kabbaj - T. Maria | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.1875 | 0.3195 | 0.5597 | 26.91 |
| 2026-05-20 | M. Bassols - Ka. Pliskova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.3125 | 0.2292 | 0.5182 | 17.5 |
| 2026-05-20 | J. Tjen - C. Osorio | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.1611 | 0.2713 | 0.4865 | 8.84 |
| 2026-05-20 | N. Budkov Kjaer - T. Gentzsch | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2777 | 0.3334 | 0.4374 | 0.11 |
| 2026-05-20 | P. Kudermetova - V. Tomova | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.4125 | 0.3708 | 0.3254 | 26.22 |
| 2026-05-21 | I. Ivashka - A. Hernandez | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.15 | 0.3778 | 0.6325 | 11.99 |
| 2026-05-21 | J. De Jong - M. Zheng | OVER 20.5 games | 1.8 | win | 0.8 | 20.5 | 0.3403 | 0.5416 | 0.3456 | 7.89 |
| 2026-05-21 | P. Makk - D. Milanovic | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.2381 | 0.2738 | 0.4567 | 14.24 |
| 2026-05-21 | C. Osorio - P. Udvardy | UNDER 20.5 games | 1.97 | loss | -1.0 | 20.5 | 0.3333 | 0.3056 | 0.4127 | 27.01 |
| 2026-05-21 | A. Galarneau - F. Cina | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2222 | 0.5 | 0.5251 | 14.89 |
| 2026-05-21 | B. Gadamauri - P. Nesterov | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2361 | 0.4665 | 0.2711 | 1.27 |
| 2026-05-21 | D. Svrcina - T. Faurel | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.2222 | 0.3056 | 0.5697 | 28.89 |
| 2026-05-21 | A. Popyrin - C. Ruud | UNDER 21.5 games | 2.11 | win | 1.11 | 21.5 | 0.25 | 0.3959 | 0.4835 | 17.38 |
| 2026-05-21 | S. Zhang - E. Navarro | UNDER 20.5 games | 1.95 | loss | -1.0 | 20.5 | 0.2056 | 0.4232 | 0.4138 | 13.29 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 22.5 games | 2.06 | win | 1.06 | 22.5 | 0.4334 | 0.4213 | 0.3193 | 0.93 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 21.5 games | 1.8 | win | 0.8 | 21.5 | 0.4236 | 0.3739 | 0.3193 | 0.55 |
| 2026-05-22 | E. Nava - P. Martinez | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.2361 | 0.3692 | 0.402 | 9.61 |
| 2026-05-22 | C. Ruud - M. Navone | UNDER 20.5 games | 2.07 | win | 1.07 | 20.5 | 0.2222 | 0.463 | 0.5706 | 23.33 |

## V2 under selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | A. Li - S. Zhang | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2167 | 0.3223 | 0.4751 | 18.35 |
| 2026-05-06 | T. Townsend - N. Brancaccio | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.254 | 0.2976 | 0.4895 | 23.58 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 0.4802 | 16.45 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 0.5758 | 6.45 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 0.433 | 7.3 |
| 2026-05-12 | L. Darderi - A. Zverev | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.2222 | 0.3148 | 0.594 | 22.0 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-12 | J. B. Torres - B. Fernandez | UNDER 19.5 games | 2.0 | loss | -1.0 | 19.5 | 0.2611 | 0.3491 | 0.6325 | 25.81 |
| 2026-05-14 | J. Reis Da Silva - E. Moller | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.2625 | 0.2437 | 0.3466 | 26.38 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 0.5207 | 9.83 |
| 2026-05-14 | D. Dedura - L. Neumayer | UNDER 20.5 games | 2.12 | win | 1.12 | 20.5 | 0.2361 | 0.2291 | 0.2667 | 29.38 |
| 2026-05-14 | D. Dzumhur - J. Munar | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.125 | 0.3229 | 0.4074 | 4.38 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 0.7922 | 18.7 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-18 | D. Altmaier - R. Hijikata | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2143 | 0.3215 | 0.3966 | 8.72 |
| 2026-05-18 | N. Mejia - P. Llamas Ruiz | UNDER 19.5 games | 2.01 | loss | -1.0 | 19.5 | 0.25 | 0.2812 | 0.711 | 22.08 |
| 2026-05-19 | L. Zaar - J. Bouzas Maneiro | UNDER 19.5 games | 2.06 | win | 1.06 | 19.5 | 0.3222 | 0.2815 | 0.4974 | 16.76 |
| 2026-05-19 | N. Honda - P. Sekulic | UNDER 20.5 games | 2.05 | push | 0.0 | 20.5 | 0.2143 | 0.2262 | 0.5649 | 19.56 |
| 2026-05-19 | B. Hassan - F. C. Jianu | UNDER 20.5 games | 2.03 | win | 1.03 | 20.5 | 0.3 | 0.3167 | 0.3106 | 23.6 |
| 2026-05-20 | T. Faurel - J. Clarke | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.2056 | 0.288 | 0.3868 | 21.45 |
| 2026-05-20 | Y. Kabbaj - T. Maria | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.1875 | 0.3195 | 0.5597 | 26.91 |
| 2026-05-20 | M. Bassols - Ka. Pliskova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.3125 | 0.2292 | 0.5182 | 17.5 |
| 2026-05-20 | R. Collignon - C. Ruud | UNDER 21.5 games | 2.03 | win | 1.03 | 21.5 | 0.0556 | 0.3333 | 0.4205 | 11.84 |
| 2026-05-20 | N. Budkov Kjaer - T. Gentzsch | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2777 | 0.3334 | 0.4374 | 0.11 |
| 2026-05-21 | P. Makk - D. Milanovic | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.2381 | 0.2738 | 0.4567 | 14.24 |
| 2026-05-21 | D. Svrcina - T. Faurel | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.2222 | 0.3056 | 0.5697 | 28.89 |
| 2026-05-22 | A. Kovacevic - I. Buse | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.3055 | 0.3102 | 0.5238 | 27.17 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 21.5 games | 2.15 | loss | -1.0 | 21.5 | 0.1125 | 0.2521 | 0.3487 | 5.62 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 22.0 games | 2.05 | loss | -1.0 | 22.0 | 0.1125 | 0.2521 | 0.3466 | 5.62 |
| 2026-05-23 | G. Blancaneaux - C. Denolly | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.127 | 0.3359 | 0.4038 | 24.39 |
| 2026-05-23 | S. Giamichelle - G. Ribeiro de Almeida | UNDER 20.0 games | 2.11 | loss | -1.0 | 20.0 | 0.0714 | 0.2262 | 0.3375 | 24.72 |
| 2026-05-23 | S. Giamichelle - G. Ribeiro de Almeida | UNDER 19.5 games | 2.14 | loss | -1.0 | 19.5 | 0.0714 | 0.2262 | 0.3319 | 24.72 |
| 2026-05-23 | M. Alves - H. Hoeyeraal | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.1111 | 0.2778 | 0.4955 | 9.77 |
| 2026-05-23 | M. Alves - H. Hoeyeraal | UNDER 20.0 games | 2.11 | win | 1.11 | 20.0 | 0.1111 | 0.2778 | 0.4675 | 9.77 |
| 2026-05-24 | A. Azkara - P. Schoen | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.0625 | 0.3438 | 0.4408 | 17.87 |
| 2026-05-24 | N. Vukadin - M. Kasnikowski | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.1805 | 0.3067 | 0.5764 | 4.8 |
| 2026-05-24 | A. Kubareva - L. Petretic | UNDER 19.5 games | 2.02 | loss | -1.0 | 19.5 | 0.2 | 0.2666 | 0.4263 | 0.3 |
| 2026-05-24 | L. Vujovic - M. Mettraux | UNDER 19.5 games | 1.97 | loss | -1.0 | 19.5 | 0.25 | 0.2083 | 0.5191 | 19.4 |
| 2026-05-24 | S. Kraus - B. Bencic | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.2777 | 0.2871 | 0.5449 | 12.11 |
| 2026-05-25 | D. Kasatkina - Z. Sonmez | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2111 | 0.2296 | 0.3753 | 14.26 |
| 2026-05-25 | P. Zahraj - G. Hussey | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.2111 | 0.3361 | 0.3128 | 6.09 |
| 2026-05-26 | E. Navarro - J. Tjen | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.1611 | 0.2639 | 0.4534 | 7.3 |
| 2026-05-26 | E. Pridankina - O. Oliynykova | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2611 | 0.3398 | 0.2843 | 24.21 |
| 2026-05-26 | P. Sekulic - M. Krueger | UNDER 21.5 games | 2.18 | push | 0.0 | 21.5 | 0.259 | 0.2843 | 0.3432 | 22.1 |
| 2026-05-27 | C. McNally - B. Bencic | UNDER 20.0 games | 2.09 | win | 1.09 | 20.0 | 0.2056 | 0.1991 | 0.4935 | 3.09 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2222 | 0.3241 | 0.3308 | 25.68 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.0 games | 2.19 | win | 1.19 | 20.0 | 0.2222 | 0.3241 | 0.3341 | 25.68 |
| 2026-05-27 | F. Jones - M. Bouzkova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.1666 | 0.3175 | 0.5142 | 23.32 |
| 2026-05-28 | L. Wessels - V. Durasovic | UNDER 21.5 games | 2.14 | loss | -1.0 | 21.5 | 0.25 | 0.3166 | 0.3091 | 20.7 |
| 2026-05-28 | A. Kalinskaya - A. Korneeva | UNDER 20.5 games | 2.1 | loss | -1.0 | 20.5 | 0.1125 | 0.2646 | 0.3957 | 24.12 |
| 2026-05-28 | A. Li - D. Parry | UNDER 20.5 games | 2.04 | win | 1.04 | 20.5 | 0.2429 | 0.3393 | 0.4073 | 20.14 |
| 2026-05-29 | T. Daniel - M. Erhard | UNDER 21.0 games | 2.11 | loss | -1.0 | 21.0 | 0.1714 | 0.2536 | 0.2618 | 1.3 |
| 2026-05-30 | M. Homberg - K. Sultanov | UNDER 20.0 games | 2.11 | win | 1.11 | 20.0 | 0.1736 | 0.2755 | 0.3176 | 0.22 |
| 2026-05-30 | M. Fuele - N. Djosic | UNDER 19.5 games | 2.06 | push | 0.0 | 19.5 | 0.1111 | 0.3403 | 0.526 | 11.88 |
| 2026-05-30 | T. Sahtali - I. Almazan Valiente | UNDER 20.0 games | 2.12 | loss | -1.0 | 20.0 | 0.125 | 0.2535 | 0.2521 | 16.69 |
| 2026-05-30 | D. Shnaider - O. Oliynykova | UNDER 20.5 games | 1.99 | win | 0.99 | 20.5 | 0.3166 | 0.262 | 0.4414 | 6.69 |
| 2026-05-31 | A. Zantedeschi - V. Ivanov | UNDER 20.0 games | 2.04 | pending | 0.0 | 20.0 | 0.0556 | 0.2777 | 0.3098 | 26.67 |
| 2026-05-31 | N. Vukadin - D. Ajdukovic | UNDER 20.5 games | 2.1 | pending | 0.0 | 20.5 | 0.2 | 0.2167 | 0.2747 | 24.8 |
| 2026-05-31 | K. Sultanov - T. Chavez | UNDER 19.0 games | 2.04 | pending | 0.0 | 19.0 | 0.1736 | 0.2234 | 0.4906 | 28.6 |

## V3 over selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | S. Kenin - B. Andreescu | OVER 21.5 games | 1.92 | win | 0.92 | 21.5 | 0.5625 | 0.4375 | 0.1018 | 21.62 |
| 2026-05-05 | L. Pigossi - L. Cortez Llorca | OVER 20.5 games | 1.87 | win | 0.87 | 20.5 | 0.35 | 0.4083 | 0.2585 | 18.9 |
| 2026-05-05 | M. Landaluce - A. Pellegrino | OVER 22.5 games | 1.93 | win | 0.93 | 22.5 | 0.4028 | 0.4259 | 0.1666 | 2.12 |
| 2026-05-06 | S. Tsitsipas - T. Machac | OVER 22.5 games | 1.83 | win | 0.83 | 22.5 | 0.4 | 0.3334 | 0.1443 | 5.2 |
| 2026-05-06 | Y. Putintseva - T. Valentova | OVER 21.5 games | 1.95 | loss | -1.0 | 21.5 | 0.4018 | 0.4539 | 0.1288 | 9.17 |
| 2026-05-07 | C. Garin - J. M. Cerundolo | OVER 22.5 games | 1.9 | win | 0.9 | 22.5 | 0.4 | 0.4917 | 0.0518 | 13.3 |
| 2026-05-07 | L. Sonego - I. Buse | OVER 22.5 games | 1.94 | loss | -1.0 | 22.5 | 0.5238 | 0.4385 | 0.1995 | 7.1 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 0.285 | 3.78 |
| 2026-05-08 | I. Vasa - F. Ribero | OVER 21.5 games | 1.84 | win | 0.84 | 21.5 | 0.4375 | 0.423 | 0.1492 | 19.6 |
| 2026-05-08 | D. Prizmic - N. Djokovic | OVER 21.5 games | 1.83 | win | 0.83 | 21.5 | 0.3958 | 0.4236 | 0.2821 | 4.62 |
| 2026-05-09 | Q. Zheng - J. Ostapenko | OVER 20.5 games | 1.91 | win | 0.91 | 20.5 | 0.5 | 0.5167 | 0.336 | 6.4 |
| 2026-05-09 | Q. Zheng - J. Ostapenko | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.5278 | 0.513 | 0.285 | 11.41 |
| 2026-05-11 | A. Kalinskaya - J. Ostapenko | OVER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.3555 | 0.5685 | 0.1018 | 19.33 |
| 2026-05-11 | A. Fery - V. Sachko | OVER 22.5 games | 2.0 | loss | -1.0 | 22.5 | 0.4732 | 0.5416 | 0.0992 | 11.96 |
| 2026-05-12 | T. Monteiro - A. Andrade | OVER 21.5 games | 1.8 | push | 0.0 | 21.5 | 0.3889 | 0.4352 | 0.1645 | 21.56 |
| 2026-05-12 | S. Cirstea - J. Ostapenko | OVER 21.5 games | 1.9 | loss | -1.0 | 21.5 | 0.4643 | 0.4333 | 0.1479 | 0.08 |
| 2026-05-12 | T. Seyboth Wild - D. E. Galan | OVER 22.5 games | 2.04 | loss | -1.0 | 22.5 | 0.5715 | 0.5476 | 0.1226 | 16.0 |
| 2026-05-12 | F. Diaz Acosta - H. Dellien | OVER 21.5 games | 1.86 | loss | -1.0 | 21.5 | 0.35 | 0.5333 | 0.0854 | 15.58 |
| 2026-05-12 | Y. Yuan - M. Sherif | OVER 20.5 games | 1.9 | win | 0.9 | 20.5 | 0.4111 | 0.3713 | 0.1336 | 13.98 |
| 2026-05-13 | L. Midon - B. Hassan | OVER 21.5 games | 1.84 | win | 0.84 | 21.5 | 0.5285 | 0.4178 | 0.15 | 18.55 |
| 2026-05-14 | K. Smith - O. Milic | OVER 22.5 games | 1.87 | loss | -1.0 | 22.5 | 0.4653 | 0.5741 | 0.0479 | 9.79 |
| 2026-05-14 | K. Smith - O. Milic | OVER 23.5 games | 2.17 | loss | -1.0 | 23.5 | 0.5 | 0.5729 | 0.0479 | 4.87 |
| 2026-05-14 | T. Droguet - T. Atmane | OVER 23.5 games | 2.04 | push | 0.0 | 23.5 | 0.4732 | 0.4583 | 0.0133 | 18.75 |
| 2026-05-14 | L. Mikrut - C. Rodesch | OVER 21.5 games | 1.83 | loss | -1.0 | 21.5 | 0.4822 | 0.4047 | 0.073 | 4.64 |
| 2026-05-14 | J. Choinski - D. E. Galan | OVER 22.5 games | 1.97 | win | 0.97 | 22.5 | 0.5 | 0.5714 | 0.1535 | 15.0 |
| 2026-05-14 | L. Mikrut - C. Rodesch | OVER 22.5 games | 2.05 | loss | -1.0 | 22.5 | 0.4822 | 0.4047 | 0.073 | 4.64 |
| 2026-05-15 | J. Choinski - A. Fery | OVER 22.5 games | 2.0 | push | 0.0 | 22.5 | 0.5 | 0.5834 | 0.1676 | 13.0 |
| 2026-05-16 | O. Selekhmeteva - S. Kenin | OVER 21.5 games | 1.96 | win | 0.96 | 21.5 | 0.4722 | 0.5104 | 0.0514 | 18.72 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 0.3448 | 13.95 |
| 2026-05-17 | M. Kessler - O. Selekhmeteva | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.4444 | 0.4259 | 0.0 | 18.44 |
| 2026-05-17 | M. Sakkari - P. Stearns | OVER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.375 | 0.5209 | 0.0168 | 4.5 |
| 2026-05-18 | T. Atmane - T. M. Etcheverry | OVER 22.5 games | 1.93 | loss | -1.0 | 22.5 | 0.4028 | 0.5081 | 0.297 | 4.22 |
| 2026-05-19 | S. Dostanic - F. Forti | OVER 22.5 games | 2.03 | win | 1.03 | 22.5 | 0.5555 | 0.3518 | 0.0306 | 30.55 |
| 2026-05-19 | L. Midon - R. Carballes Baena | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.6507 | 0.3651 | 0.3248 | 22.39 |
| 2026-05-19 | Y. Kabbaj - B. Cengiz | OVER 20.5 games | 1.92 | win | 0.92 | 20.5 | 0.4166 | 0.4713 | 0.3308 | 21.23 |
| 2026-05-19 | N. Fatic - L. Mikrut | OVER 22.5 games | 2.08 | loss | -1.0 | 22.5 | 0.3625 | 0.3604 | 0.0229 | 16.9 |
| 2026-05-20 | W. K. Leong M. - Y. Takahashi | OVER 21.5 games | 1.85 | loss | -1.0 | 21.5 | 0.5 | 0.3148 | 0.0437 | 18.01 |
| 2026-05-21 | H. Stewart - O. Milic | OVER 22.5 games | 1.97 | loss | -1.0 | 22.5 | 0.4722 | 0.4838 | 0.1627 | 11.44 |
| 2026-05-21 | P. Marcinko - J. Bouzas Maneiro | OVER 20.5 games | 1.85 | loss | -1.0 | 20.5 | 0.35 | 0.45 | 0.2101 | 7.0 |
| 2026-05-21 | A. Korneeva - J. Riera | OVER 21.5 games | 1.93 | loss | -1.0 | 21.5 | 0.4583 | 0.3009 | 0.1293 | 4.16 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 22.5 games | 2.06 | win | 1.06 | 22.5 | 0.4334 | 0.4213 | 0.3193 | 0.93 |
| 2026-05-21 | J. Faria - L. Neumayer | OVER 22.5 games | 1.92 | loss | -1.0 | 22.5 | 0.4875 | 0.327 | 0.027 | 10.9 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 21.5 games | 1.8 | win | 0.8 | 21.5 | 0.4236 | 0.3739 | 0.3193 | 0.55 |
| 2026-05-22 | K. Zavatska - L. Bronzetti | OVER 21.5 games | 2.06 | push | 0.0 | 21.5 | 0.4583 | 0.4502 | 0.1767 | 9.39 |
| 2026-05-24 | E. Dalla Valle - F. Forti | OVER 22.5 games | 2.0 | loss | -1.0 | 22.5 | 0.3555 | 0.4926 | 0.0635 | 16.3 |
| 2026-05-24 | M. Frech - G. Ruse | OVER 21.5 games | 1.96 | push | 0.0 | 21.5 | 0.6459 | 0.4016 | 0.1825 | 21.29 |
| 2026-05-24 | S. Sorribes Tormo - T. Korpatsch | OVER 21.5 games | 2.05 | loss | -1.0 | 21.5 | 0.5 | 0.3417 | 0.1097 | 7.8 |
| 2026-05-25 | T. Berkieta - D. Rapagnetta | OVER 21.5 games | 1.91 | win | 0.91 | 21.5 | 0.35 | 0.3833 | 0.078 | 1.4 |
| 2026-05-25 | J. Paolini - D. Yastremska | OVER 20.5 games | 1.82 | win | 0.82 | 20.5 | 0.3929 | 0.4012 | 0.2127 | 10.75 |
| 2026-05-26 | T. Berkieta - S. Kopp | OVER 20.5 games | 1.88 | win | 0.88 | 20.5 | 0.4428 | 0.425 | 0.3473 | 3.79 |
| 2026-05-26 | L. Midon - J. Reis Da Silva | OVER 22.5 games | 2.07 | loss | -1.0 | 22.5 | 0.6285 | 0.4678 | 0.0651 | 7.28 |
| 2026-05-27 | T. Lukas - W. Ewald | OVER 20.5 games | 1.94 | loss | -1.0 | 20.5 | 0.4 | 0.4917 | 0.3076 | 3.3 |
| 2026-05-27 | T. Korpatsch - Xin. Wang | OVER 21.5 games | 1.96 | win | 0.96 | 21.5 | 0.5333 | 0.3111 | 0.0235 | 8.48 |
| 2026-05-27 | E. Ymer - G. A. Olivieri | OVER 22.5 games | 1.99 | loss | -1.0 | 22.5 | 0.4445 | 0.5834 | 0.0173 | 6.67 |
| 2026-05-27 | J. Teichmann - M. Frech | OVER 21.5 games | 1.93 | win | 0.93 | 21.5 | 0.4445 | 0.4074 | 0.153 | 26.89 |
| 2026-05-28 | I. Jovic - E. Navarro | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.4166 | 0.4352 | 0.0444 | 21.88 |
| 2026-05-29 | S. Dols - M. Maquet | OVER 20.5 games | 1.83 | win | 0.83 | 20.5 | 0.4611 | 0.3195 | 0.0405 | 24.36 |
| 2026-05-29 | G. A. Olivieri - L. Nardi | OVER 21.5 games | 1.91 | win | 0.91 | 21.5 | 0.4921 | 0.5542 | 0.3393 | 1.09 |
| 2026-05-30 | M. Vogt - P. Lovric | OVER 20.5 games | 1.96 | loss | -1.0 | 20.5 | 0.375 | 0.4292 | 0.1966 | 3.18 |
| 2026-05-30 | V. Mboko - M. Keys | OVER 21.5 games | 1.88 | win | 0.88 | 21.5 | 0.3667 | 0.4574 | 0.0525 | 6.99 |
| 2026-05-31 | G. Hussey - E. Winter | OVER 22.5 games | 2.07 | pending | 0.0 | 22.5 | 0.4732 | 0.3676 | 0.032 | 16.0 |
| 2026-05-31 | M. Martineau - S. Jong | OVER 22.0 games | 1.82 | pending | 0.0 | 22.0 | 0.4236 | 0.6169 | 0.1262 | 1.75 |
| 2026-05-31 | R. Masarova - C. Naef | OVER 22.5 games | 2.05 | pending | 0.0 | 22.5 | 0.6 | 0.3417 | 0.1666 | 11.8 |

## V2 under breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| under | 61 | 58 | 36 | 18 | 66.67% | 20.47u | 35.29% | 2.0759 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| wta | 19 | 19 | 16 | 2 | 88.89% | 15.01u | 79.0% | 2.0737 |
| atp | 11 | 11 | 9 | 2 | 81.82% | 7.2u | 65.45% | 2.02 |
| itf | 17 | 14 | 6 | 7 | 46.15% | -0.28u | -2.0% | 2.1036 |
| challenger | 14 | 14 | 5 | 7 | 41.67% | -1.46u | -10.43% | 2.095 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| women | 23 | 22 | 16 | 5 | 76.19% | 12.01u | 54.59% | 2.0655 |
| men | 38 | 36 | 20 | 13 | 60.61% | 8.46u | 23.5% | 2.0822 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 26 | 24 | 18 | 5 | 78.26% | 14.15u | 58.96% | 2.0721 |
| 18.5 - 19.5 | 22 | 21 | 11 | 8 | 57.89% | 4.05u | 19.29% | 2.0838 |
| 20.5 - 21.5 | 11 | 11 | 6 | 4 | 60.0% | 2.24u | 20.36% | 2.0755 |
| <= 18.5 | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| 21.5 - 22.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.95 - 2.05 | 31 | 29 | 20 | 8 | 71.43% | 12.36u | 42.62% | 2.0197 |
| 2.05 - 2.2 | 30 | 29 | 16 | 10 | 61.54% | 8.11u | 27.97% | 2.1321 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 86 - 89 | 15 | 14 | 9 | 4 | 69.23% | 5.98u | 42.71% | 2.0936 |
| > 92 | 5 | 5 | 5 | 0 | 100.0% | 5.15u | 103.0% | 2.03 |
| 89 - 92 | 20 | 20 | 12 | 7 | 63.16% | 5.15u | 25.75% | 2.0285 |
| 83 - 86 | 19 | 17 | 9 | 6 | 60.0% | 4.16u | 24.47% | 2.1276 |
| 80 - 83 | 2 | 2 | 1 | 1 | 50.0% | 0.03u | 1.5% | 2.1 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 84 | 23 | 23 | 18 | 3 | 85.71% | 16.29u | 70.83% | 2.0748 |
| 84 - 88 | 10 | 10 | 7 | 2 | 77.78% | 5.74u | 57.4% | 2.113 |
| 72 - 76 | 10 | 9 | 4 | 4 | 50.0% | 0.2u | 2.22% | 2.0589 |
| 76 - 80 | 17 | 15 | 7 | 8 | 46.67% | -0.76u | -5.07% | 2.058 |
| > 88 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.45 - 0.6 | 25 | 24 | 17 | 4 | 80.95% | 14.29u | 59.54% | 2.0717 |
| 0.35 - 0.45 | 13 | 13 | 9 | 4 | 69.23% | 5.29u | 40.69% | 2.0485 |
| 0.25 - 0.35 | 20 | 18 | 9 | 8 | 52.94% | 1.86u | 10.33% | 2.1117 |
| > 0.6 | 3 | 3 | 1 | 2 | 33.33% | -0.97u | -32.33% | 2.0133 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 - 30 | 10 | 8 | 7 | 1 | 87.5% | 6.58u | 82.25% | 2.0725 |
| 10 - 15 | 7 | 7 | 6 | 0 | 100.0% | 6.31u | 90.14% | 2.0529 |
| 5 - 10 | 12 | 12 | 8 | 4 | 66.67% | 4.38u | 36.5% | 2.065 |
| <= 5 | 8 | 8 | 5 | 3 | 62.5% | 2.34u | 29.25% | 2.065 |
| 15 - 20 | 9 | 9 | 4 | 3 | 57.14% | 1.36u | 15.11% | 2.0878 |
| 20 - 25 | 15 | 14 | 6 | 7 | 46.15% | -0.5u | -3.57% | 2.0971 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.2 - 0.25 | 19 | 19 | 12 | 6 | 66.67% | 6.92u | 36.42% | 2.0737 |
| 0.15 - 0.2 | 15 | 13 | 9 | 3 | 75.0% | 6.5u | 50.0% | 2.0631 |
| 0.25 - 0.3 | 8 | 8 | 6 | 1 | 85.71% | 5.44u | 68.0% | 2.0775 |
| 0.3 - 0.35 | 5 | 5 | 5 | 0 | 100.0% | 5.25u | 105.0% | 2.05 |
| <= 0.15 | 14 | 13 | 4 | 8 | 33.33% | -3.64u | -28.0% | 2.1008 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.35 | 27 | 27 | 18 | 7 | 72.0% | 12.06u | 44.67% | 2.0715 |
| 0.2 - 0.3 | 33 | 30 | 17 | 11 | 60.71% | 7.32u | 24.4% | 2.0793 |
| <= 0.2 | 1 | 1 | 1 | 0 | 100.0% | 1.09u | 109.0% | 2.09 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19 - 20 | 24 | 24 | 17 | 6 | 73.91% | 12.39u | 51.62% | 2.0775 |
| 20 - 21 | 10 | 10 | 9 | 1 | 90.0% | 8.44u | 84.4% | 2.058 |
| 18 - 19 | 21 | 21 | 9 | 9 | 50.0% | 0.61u | 2.9% | 2.08 |
| <= 18 | 6 | 3 | 1 | 2 | 33.33% | -0.97u | -32.33% | 2.0933 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.4 | 10 | 10 | 10 | 0 | 100.0% | 10.62u | 106.2% | 2.062 |
| 0.2 - 0.3 | 25 | 25 | 15 | 7 | 68.18% | 9.09u | 36.36% | 2.0764 |
| <= 0.2 | 25 | 22 | 11 | 10 | 52.38% | 1.76u | 8.0% | 2.085 |
| 0.4 - 0.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pncl | 32 | 29 | 20 | 6 | 76.92% | 15.69u | 54.1% | 2.0821 |
| Unibet | 4 | 4 | 3 | 0 | 100.0% | 3.18u | 79.5% | 2.09 |
| Betfair | 3 | 3 | 3 | 0 | 100.0% | 3.0u | 100.0% | 2.0 |
| Superbet | 5 | 5 | 3 | 2 | 60.0% | 1.12u | 22.4% | 2.022 |
| Betano | 10 | 10 | 5 | 5 | 50.0% | 0.35u | 3.5% | 2.08 |
| Marathon | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| 1xBet | 6 | 6 | 2 | 4 | 33.33% | -1.87u | -31.17% | 2.1 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| French Open | 16 | 16 | 14 | 2 | 87.5% | 12.85u | 80.31% | 2.06 |
| Hamburg | 5 | 5 | 5 | 0 | 100.0% | 5.07u | 101.4% | 2.014 |
| Zagreb | 2 | 2 | 2 | 0 | 100.0% | 2.3u | 115.0% | 2.15 |
| Rabat | 2 | 2 | 2 | 0 | 100.0% | 2.11u | 105.5% | 2.055 |
| Bordeaux | 1 | 1 | 1 | 0 | 100.0% | 1.19u | 119.0% | 2.19 |
| M15 Doboj | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| Rome | 6 | 6 | 3 | 2 | 60.0% | 1.15u | 19.17% | 2.075 |
| M15 Kayseri | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M25 Bol | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M15 Kranjska Gora (Slovenia) | 2 | 1 | 1 | 0 | 100.0% | 1.11u | 111.0% | 2.11 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Geneva | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Tunis | 1 | 1 | 1 | 0 | 100.0% | 1.02u | 102.0% | 2.02 |
| M15 Maringa 2 (Brazil) | 4 | 4 | 2 | 2 | 50.0% | 0.21u | 5.25% | 2.115 |
| Little Rock | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.18 |
| M15 Brcko | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.06 |
| W35 Bol 2 | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| M25 Bol 2 | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Cordoba 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |
| Parma | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| Valencia | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| M25 Deauville | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.17 |
| W15 Monastir 14 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.02 |
| W15 Kursumlijska Banja 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.97 |
| Centurion (South Africa) - Qualification | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| M25 Troisdorf (Germany) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.14 |
| Kosice | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.11 |
| M15 Monastir 20 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.12 |
| Bengaluru 3 (India) - Qualification | 3 | 3 | 0 | 2 | 0.0% | -2.0u | -66.67% | 2.0833 |

## V3 over breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| over | 63 | 60 | 27 | 28 | 49.09% | -3.44u | -5.73% | 1.9395 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| atp | 11 | 11 | 7 | 4 | 63.64% | 2.35u | 21.36% | 1.9291 |
| wta | 22 | 22 | 10 | 10 | 50.0% | -0.77u | -3.5% | 1.9423 |
| itf | 3 | 3 | 1 | 2 | 33.33% | -1.17u | -39.0% | 1.91 |
| challenger | 27 | 24 | 9 | 12 | 42.86% | -3.85u | -16.04% | 1.9454 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| women | 28 | 27 | 13 | 12 | 52.0% | -0.17u | -0.63% | 1.9344 |
| men | 35 | 33 | 14 | 16 | 46.67% | -3.27u | -9.91% | 1.9436 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 11 | 11 | 8 | 3 | 72.73% | 4.06u | 36.91% | 1.8918 |
| 20.5 - 21.5 | 28 | 28 | 13 | 12 | 52.0% | -0.22u | -0.79% | 1.9204 |
| > 22.5 | 2 | 2 | 0 | 1 | 0.0% | -1.0u | -50.0% | 2.105 |
| 21.5 - 22.5 | 22 | 19 | 6 | 12 | 33.33% | -6.28u | -33.05% | 1.9779 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.8 - 1.95 | 34 | 33 | 19 | 14 | 57.58% | 2.78u | 8.42% | 1.89 |
| <= 1.8 | 2 | 2 | 1 | 0 | 100.0% | 0.8u | 40.0% | 1.8 |
| 2.05 - 2.2 | 6 | 5 | 1 | 3 | 25.0% | -1.94u | -38.8% | 2.088 |
| 1.95 - 2.05 | 21 | 20 | 6 | 11 | 35.29% | -5.08u | -25.4% | 1.998 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 83 | 8 | 8 | 4 | 3 | 57.14% | 0.48u | 6.0% | 1.9213 |
| 86 - 89 | 9 | 8 | 3 | 3 | 50.0% | -0.11u | -1.38% | 1.9238 |
| 83 - 86 | 8 | 8 | 4 | 4 | 50.0% | -0.37u | -4.62% | 1.92 |
| <= 80 | 3 | 3 | 1 | 2 | 33.33% | -0.97u | -32.33% | 2.0167 |
| > 92 | 28 | 26 | 12 | 12 | 50.0% | -1.03u | -3.96% | 1.95 |
| 89 - 92 | 7 | 7 | 3 | 4 | 42.86% | -1.44u | -20.57% | 1.9286 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 76 - 80 | 11 | 11 | 7 | 4 | 63.64% | 2.24u | 20.36% | 1.8973 |
| <= 72 | 6 | 6 | 4 | 2 | 66.67% | 1.51u | 25.17% | 1.9217 |
| 84 - 88 | 12 | 10 | 4 | 5 | 44.44% | -1.17u | -11.7% | 2.0 |
| 72 - 76 | 5 | 4 | 1 | 2 | 33.33% | -1.2u | -30.0% | 1.85 |
| 80 - 84 | 14 | 14 | 6 | 7 | 46.15% | -1.6u | -11.43% | 1.915 |
| > 88 | 15 | 15 | 5 | 8 | 38.46% | -3.22u | -21.47% | 1.984 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.35 | 14 | 14 | 11 | 3 | 78.57% | 7.11u | 50.79% | 1.9286 |
| 0.2 - 0.25 | 2 | 2 | 1 | 1 | 50.0% | -0.18u | -9.0% | 1.835 |
| <= 0.2 | 47 | 44 | 15 | 24 | 38.46% | -10.37u | -23.57% | 1.9477 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 - 25 | 7 | 7 | 4 | 1 | 80.0% | 2.67u | 38.14% | 1.9057 |
| 10 - 15 | 11 | 10 | 6 | 3 | 66.67% | 2.52u | 25.2% | 1.941 |
| 30 - 35 | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| 25 - 30 | 1 | 1 | 1 | 0 | 100.0% | 0.93u | 93.0% | 1.93 |
| 5 - 10 | 12 | 12 | 4 | 7 | 36.36% | -3.42u | -28.5% | 1.9467 |
| 15 - 20 | 13 | 12 | 4 | 7 | 36.36% | -3.49u | -29.08% | 1.9392 |
| <= 5 | 18 | 17 | 7 | 10 | 41.18% | -3.68u | -21.65% | 1.9429 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.35 - 0.45 | 26 | 25 | 13 | 11 | 54.17% | 0.52u | 2.08% | 1.918 |
| 0.3 - 0.35 | 4 | 4 | 2 | 2 | 50.0% | -0.22u | -5.5% | 1.8725 |
| > 0.45 | 33 | 31 | 12 | 15 | 44.44% | -3.74u | -12.06% | 1.9655 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.35 - 0.4 | 8 | 7 | 6 | 1 | 85.71% | 4.57u | 65.29% | 1.95 |
| > 0.6 | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| 0.3 - 0.35 | 8 | 7 | 3 | 4 | 42.86% | -1.38u | -19.71% | 1.91 |
| 0.4 - 0.5 | 31 | 31 | 13 | 14 | 48.15% | -2.38u | -7.68% | 1.9284 |
| 0.5 - 0.6 | 15 | 15 | 5 | 9 | 35.71% | -4.25u | -28.33% | 1.9713 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 21 - 22 | 13 | 13 | 8 | 4 | 66.67% | 3.08u | 23.69% | 1.8992 |
| > 23 | 24 | 21 | 11 | 8 | 57.89% | 2.31u | 11.0% | 1.9633 |
| 22 - 23 | 26 | 26 | 8 | 16 | 33.33% | -8.83u | -33.96% | 1.9404 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| > 0.6 | 8 | 8 | 4 | 3 | 57.14% | 0.89u | 11.12% | 1.995 |
| 0.3 - 0.4 | 6 | 6 | 3 | 3 | 50.0% | -0.38u | -6.33% | 1.9017 |
| 0.5 - 0.6 | 23 | 21 | 9 | 10 | 47.37% | -1.55u | -7.38% | 1.9581 |
| 0.4 - 0.5 | 26 | 25 | 11 | 12 | 47.83% | -2.4u | -9.6% | 1.9152 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Betfair | 2 | 2 | 2 | 0 | 100.0% | 1.91u | 95.5% | 1.955 |
| 1xBet | 4 | 4 | 3 | 1 | 75.0% | 1.78u | 44.5% | 1.92 |
| BetVictor | 1 | 1 | 1 | 0 | 100.0% | 0.83u | 83.0% | 1.83 |
| bet365 | 4 | 4 | 2 | 1 | 66.67% | 0.7u | 17.5% | 1.8325 |
| Unibet | 4 | 4 | 1 | 2 | 33.33% | -1.08u | -27.0% | 1.9875 |
| Pncl | 38 | 35 | 16 | 16 | 50.0% | -1.36u | -3.89% | 1.9497 |
| Superbet | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 1.9633 |
| Betano | 7 | 7 | 2 | 5 | 28.57% | -3.22u | -46.0% | 1.9343 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kosice | 2 | 2 | 2 | 0 | 100.0% | 1.79u | 89.5% | 1.895 |
| Rome | 12 | 12 | 7 | 5 | 58.33% | 1.32u | 11.0% | 1.9258 |
| Cervia (Italy) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Parma | 1 | 1 | 1 | 0 | 100.0% | 0.9u | 90.0% | 1.9 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 0.87u | 87.0% | 1.87 |
| Hamburg | 3 | 3 | 2 | 1 | 66.67% | 0.86u | 28.67% | 1.93 |
| Brazzaville | 1 | 1 | 1 | 0 | 100.0% | 0.84u | 84.0% | 1.84 |
| W15 Oliva (Spain) | 1 | 1 | 1 | 0 | 100.0% | 0.83u | 83.0% | 1.83 |
| Bordeaux | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.04 |
| Centurion (South Africa) - Qualification | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Heilbronn | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Birmingham | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Rabat | 2 | 2 | 1 | 1 | 50.0% | -0.08u | -4.0% | 1.885 |
| Chisinau | 2 | 2 | 1 | 1 | 50.0% | -0.09u | -4.5% | 1.95 |
| Strasbourg | 4 | 4 | 2 | 2 | 50.0% | -0.11u | -2.75% | 1.945 |
| Oeiras 6 | 2 | 2 | 1 | 1 | 50.0% | -0.16u | -8.0% | 1.85 |
| French Open | 12 | 12 | 5 | 5 | 50.0% | -0.41u | -3.42% | 1.9583 |
| W35 Bol 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.94 |
| W15 Szentendre (Hungary) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.96 |
| Bengaluru 2 | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.02 |
| Bengaluru 3 (India) - Qualification | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 1.91 |
| Vicenza | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.035 |
| Zagreb | 7 | 7 | 1 | 4 | 20.0% | -3.03u | -43.29% | 1.9557 |

## Files generated

- `data/lucija/lucija_v2_backtest_report.md`
- `data/lucija/lucija_v2_backtest_summary.json`
- `data/lucija/lucija_v1_backtest_picks.json`
- `data/lucija/lucija_v2_backtest_picks.json`
- `data/lucija/lucija_v3_over_backtest_picks.json`
- `data/lucija/lucija_v2_backtest_debug.json`

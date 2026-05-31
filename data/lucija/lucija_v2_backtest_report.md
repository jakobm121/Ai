# Lucija Backtest Report

Generated at: **2026-05-31T22:41:53.754845+02:00**

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
  "avg_close_set_max": 0.36,
  "avg_three_set_max": 0.36,
  "confidence_min": 79,
  "h2h_max": 0,
  "market_gap_min": 0.27,
  "quality_min": 70,
  "strength_gap_max": 33
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
| V2 under | 79 | 76 | 3 | 44 | 28 | 4 | 61.11% | 19.07u | 25.09% | 2.0789 | -6.0u |
| V3 over | 63 | 60 | 3 | 27 | 28 | 5 | 49.09% | -3.44u | -5.73% | 1.9395 | -10.59u |

## Train / test

| Model | Split | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | train_75 | 118 | 118 | 73 | 43 | 62.93% | 32.88u | 27.86% | 2.0404 | -5.7u |
| V1 | test_25 | 40 | 35 | 18 | 16 | 52.94% | 3.15u | 9.0% | 2.0877 | -3.0u |
| V2 | train_75 | 59 | 59 | 37 | 19 | 66.07% | 20.41u | 34.59% | 2.0746 | -6.0u |
| V2 | test_25 | 20 | 17 | 7 | 9 | 43.75% | -1.34u | -7.88% | 2.0941 | -3.78u |
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
| 2026-05-08 | D. Vekic - M. Ristic | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.2125 | 0.3542 | 0.4707 | 14.48 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 0.4802 | 16.45 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 0.5758 | 6.45 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 0.433 | 7.3 |
| 2026-05-12 | L. Darderi - A. Zverev | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.2222 | 0.3148 | 0.594 | 22.0 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-12 | J. B. Torres - B. Fernandez | UNDER 19.5 games | 2.0 | loss | -1.0 | 19.5 | 0.2611 | 0.3491 | 0.6325 | 25.81 |
| 2026-05-14 | J. Reis Da Silva - E. Moller | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.2625 | 0.2437 | 0.3466 | 26.38 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 0.5207 | 9.83 |
| 2026-05-14 | D. Dzumhur - J. Munar | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.125 | 0.3229 | 0.4074 | 4.38 |
| 2026-05-15 | C. Ruud - L. Darderi | UNDER 21.5 games | 2.09 | win | 1.09 | 21.5 | 0.1667 | 0.2685 | 0.4702 | 31.89 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 0.7922 | 18.7 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-17 | M. H. Rehberg - F. Comesana | UNDER 21.5 games | 2.06 | win | 1.06 | 21.5 | 0.3095 | 0.3452 | 0.3661 | 31.23 |
| 2026-05-17 | L. Jeanjean - L. Fernandez | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.3541 | 0.3125 | 0.4974 | 12.67 |
| 2026-05-18 | T. Duran - F. Agamenone | UNDER 19.5 games | 2.08 | win | 1.08 | 19.5 | 0.125 | 0.3541 | 0.6349 | 28.25 |
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
| 2026-05-22 | Dar. Blanch - L. Pavlovic | UNDER 22.5 games | 1.95 | win | 0.95 | 22.5 | 0.2666 | 0.3509 | 0.2986 | 21.93 |
| 2026-05-22 | A. Kovacevic - I. Buse | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.3055 | 0.3102 | 0.5238 | 27.17 |
| 2026-05-23 | S. Gulin - L. Gagliardo | UNDER 19.0 games | 2.1 | loss | -1.0 | 19.0 | 0.3143 | 0.2845 | 0.5523 | 22.06 |
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
| 2026-05-24 | N. Berecoechea - A. Dudeney | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.2222 | 0.2315 | 0.3007 | 32.78 |
| 2026-05-24 | S. Kraus - B. Bencic | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.2777 | 0.2871 | 0.5449 | 12.11 |
| 2026-05-24 | U. Hrabavets - A. El Sayed | UNDER 18.5 games | 2.1 | loss | -1.0 | 18.5 | 0.225 | 0.2938 | 0.655 | 16.15 |
| 2026-05-24 | Y. Ghazouani Durand - J. Sels | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2611 | 0.3509 | 0.3128 | 32.96 |
| 2026-05-25 | D. Kasatkina - Z. Sonmez | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2111 | 0.2296 | 0.3753 | 14.26 |
| 2026-05-25 | M. Dhamne - F. Ferreira Silva | UNDER 20.5 games | 2.12 | loss | -1.0 | 20.5 | 0.275 | 0.3584 | 0.3067 | 14.52 |
| 2026-05-25 | P. Zahraj - G. Hussey | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.2111 | 0.3361 | 0.3128 | 6.09 |
| 2026-05-25 | A. Zakharova - K. Muchova | UNDER 18.5 games | 2.1 | loss | -1.0 | 18.5 | 0.2666 | 0.3223 | 0.7329 | 30.6 |
| 2026-05-26 | E. Navarro - J. Tjen | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.1611 | 0.2639 | 0.4534 | 7.3 |
| 2026-05-26 | E. Pridankina - O. Oliynykova | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2611 | 0.3398 | 0.2843 | 24.21 |
| 2026-05-26 | P. Sekulic - M. Krueger | UNDER 21.5 games | 2.18 | push | 0.0 | 21.5 | 0.259 | 0.2843 | 0.3432 | 22.1 |
| 2026-05-27 | C. McNally - B. Bencic | UNDER 20.0 games | 2.09 | win | 1.09 | 20.0 | 0.2056 | 0.1991 | 0.4935 | 3.09 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2222 | 0.3241 | 0.3308 | 25.68 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.0 games | 2.19 | win | 1.19 | 20.0 | 0.2222 | 0.3241 | 0.3341 | 25.68 |
| 2026-05-27 | F. Jones - M. Bouzkova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.1666 | 0.3175 | 0.5142 | 23.32 |
| 2026-05-28 | P. Fajta - F. Roncadelli | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.3095 | 0.3506 | 0.543 | 31.26 |
| 2026-05-28 | D. Vekic - N. Osaka | UNDER 20.5 games | 2.06 | loss | -1.0 | 20.5 | 0.2111 | 0.3565 | 0.4534 | 17.86 |
| 2026-05-28 | L. Wessels - V. Durasovic | UNDER 21.5 games | 2.14 | loss | -1.0 | 21.5 | 0.25 | 0.3166 | 0.3091 | 20.7 |
| 2026-05-28 | A. Kalinskaya - A. Korneeva | UNDER 20.5 games | 2.1 | loss | -1.0 | 20.5 | 0.1125 | 0.2646 | 0.3957 | 24.12 |
| 2026-05-28 | M. Chwalinska - E. Mertens | UNDER 20.5 games | 2.03 | win | 1.03 | 20.5 | 0.1611 | 0.2176 | 0.2938 | 31.19 |
| 2026-05-28 | A. Li - D. Parry | UNDER 20.5 games | 2.04 | win | 1.04 | 20.5 | 0.2429 | 0.3393 | 0.4073 | 20.14 |
| 2026-05-29 | D. Markovina - D. Ajdukovic | UNDER 18.5 games | 2.15 | win | 1.15 | 18.5 | 0.1625 | 0.2125 | 0.7207 | 22.52 |
| 2026-05-29 | S. Pankin - E. Coulibaly | UNDER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.1667 | 0.3518 | 0.3128 | 27.1 |
| 2026-05-29 | N. Tepmahc - R. Matsuda | UNDER 20.5 games | 1.99 | loss | -1.0 | 20.5 | 0.3 | 0.3334 | 0.3393 | 30.7 |
| 2026-05-30 | L. Zaar - L. Samson | UNDER 19.5 games | 2.16 | loss | -1.0 | 19.5 | 0.15 | 0.3583 | 0.3333 | 10.5 |
| 2026-05-30 | M. Homberg - K. Sultanov | UNDER 20.0 games | 2.11 | win | 1.11 | 20.0 | 0.1736 | 0.2755 | 0.3176 | 0.22 |
| 2026-05-30 | M. Fuele - N. Djosic | UNDER 19.5 games | 2.06 | push | 0.0 | 19.5 | 0.1111 | 0.3403 | 0.526 | 11.88 |
| 2026-05-30 | D. Shnaider - O. Oliynykova | UNDER 20.5 games | 1.99 | win | 0.99 | 20.5 | 0.3166 | 0.262 | 0.4414 | 6.69 |
| 2026-05-30 | D. Parry - A. Anisimova | UNDER 19.5 games | 2.1 | loss | -1.0 | 19.5 | 0.2928 | 0.3559 | 0.6017 | 19.27 |
| 2026-05-30 | M. Krumich - M. Erhard | UNDER 20.5 games | 2.2 | loss | -1.0 | 20.5 | 0.2708 | 0.3507 | 0.3957 | 8.71 |
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
| under | 79 | 76 | 44 | 28 | 61.11% | 19.07u | 25.09% | 2.0789 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| wta | 24 | 24 | 18 | 5 | 78.26% | 14.2u | 59.17% | 2.0771 |
| atp | 14 | 14 | 12 | 2 | 85.71% | 10.3u | 73.57% | 2.0229 |
| challenger | 19 | 19 | 7 | 10 | 41.18% | -2.3u | -12.11% | 2.0963 |
| itf | 22 | 19 | 7 | 11 | 38.89% | -3.13u | -16.47% | 2.1053 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| men | 47 | 45 | 25 | 17 | 59.52% | 9.72u | 21.6% | 2.0784 |
| women | 32 | 31 | 19 | 11 | 63.33% | 9.35u | 30.16% | 2.0797 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 30 | 28 | 19 | 8 | 70.37% | 12.11u | 43.25% | 2.0693 |
| 20.5 - 21.5 | 13 | 13 | 8 | 4 | 66.67% | 4.39u | 33.77% | 2.0654 |
| 18.5 - 19.5 | 30 | 29 | 14 | 13 | 51.85% | 2.44u | 8.41% | 2.0976 |
| <= 18.5 | 4 | 4 | 2 | 2 | 50.0% | 0.18u | 4.5% | 2.095 |
| 21.5 - 22.5 | 2 | 2 | 1 | 1 | 50.0% | -0.05u | -2.5% | 2.0 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.95 - 2.05 | 35 | 33 | 22 | 10 | 68.75% | 12.44u | 37.7% | 2.0188 |
| 2.05 - 2.2 | 43 | 42 | 21 | 18 | 53.85% | 5.68u | 13.52% | 2.1293 |
| 1.8 - 1.95 | 1 | 1 | 1 | 0 | 100.0% | 0.95u | 95.0% | 1.95 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 89 - 92 | 24 | 24 | 15 | 8 | 65.22% | 7.22u | 30.08% | 2.0258 |
| > 92 | 5 | 5 | 5 | 0 | 100.0% | 5.15u | 103.0% | 2.03 |
| 86 - 89 | 23 | 22 | 12 | 9 | 57.14% | 4.2u | 19.09% | 2.0886 |
| 83 - 86 | 20 | 18 | 9 | 7 | 56.25% | 3.16u | 17.56% | 2.1372 |
| <= 80 | 2 | 2 | 1 | 1 | 50.0% | 0.15u | 7.5% | 2.125 |
| 80 - 83 | 5 | 5 | 2 | 3 | 40.0% | -0.81u | -16.2% | 2.112 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 84 | 30 | 30 | 19 | 9 | 67.86% | 11.28u | 37.6% | 2.0807 |
| 84 - 88 | 14 | 14 | 9 | 4 | 69.23% | 5.98u | 42.71% | 2.1229 |
| 76 - 80 | 21 | 19 | 12 | 7 | 63.16% | 5.61u | 29.53% | 2.0521 |
| > 88 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| <= 72 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.1 |
| 72 - 76 | 12 | 11 | 4 | 6 | 40.0% | -1.8u | -16.36% | 2.0564 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.45 - 0.6 | 31 | 30 | 20 | 7 | 74.07% | 14.69u | 48.97% | 2.081 |
| 0.35 - 0.45 | 15 | 15 | 10 | 5 | 66.67% | 5.35u | 35.67% | 2.0593 |
| 0.25 - 0.35 | 25 | 23 | 11 | 11 | 50.0% | 0.77u | 3.35% | 2.0917 |
| > 0.6 | 8 | 8 | 3 | 5 | 37.5% | -1.74u | -21.75% | 2.0713 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 - 15 | 11 | 11 | 8 | 2 | 80.0% | 6.62u | 60.18% | 2.0873 |
| 25 - 30 | 11 | 9 | 7 | 2 | 77.78% | 5.54u | 61.56% | 2.0578 |
| 5 - 10 | 13 | 13 | 8 | 5 | 61.54% | 3.38u | 26.0% | 2.0754 |
| <= 5 | 7 | 7 | 5 | 2 | 71.43% | 3.34u | 47.71% | 2.0586 |
| 20 - 25 | 18 | 17 | 8 | 8 | 50.0% | 0.6u | 3.53% | 2.0918 |
| 30 - 35 | 8 | 8 | 4 | 4 | 50.0% | 0.23u | 2.88% | 2.08 |
| 15 - 20 | 11 | 11 | 4 | 5 | 44.44% | -0.64u | -5.82% | 2.0845 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.15 - 0.2 | 18 | 16 | 12 | 3 | 80.0% | 9.77u | 61.06% | 2.06 |
| 0.3 - 0.35 | 8 | 8 | 6 | 2 | 75.0% | 4.31u | 53.87% | 2.07 |
| 0.2 - 0.25 | 22 | 22 | 12 | 9 | 57.14% | 3.95u | 17.95% | 2.08 |
| 0.25 - 0.3 | 15 | 15 | 8 | 6 | 57.14% | 2.44u | 16.27% | 2.0753 |
| 0.35 - 0.45 | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| <= 0.15 | 15 | 14 | 5 | 8 | 38.46% | -2.56u | -18.29% | 2.1021 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.35 | 31 | 31 | 20 | 9 | 68.97% | 12.28u | 39.61% | 2.0723 |
| 0.2 - 0.3 | 36 | 33 | 19 | 12 | 61.29% | 8.47u | 25.67% | 2.0809 |
| <= 0.2 | 1 | 1 | 1 | 0 | 100.0% | 1.09u | 109.0% | 2.09 |
| 0.35 - 0.4 | 11 | 11 | 4 | 7 | 36.36% | -2.77u | -25.18% | 2.0909 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19 - 20 | 28 | 28 | 17 | 10 | 62.96% | 8.35u | 29.82% | 2.0736 |
| 20 - 21 | 19 | 19 | 12 | 7 | 63.16% | 5.59u | 29.42% | 2.0732 |
| 18 - 19 | 23 | 23 | 11 | 9 | 55.0% | 2.85u | 12.39% | 2.0878 |
| 21 - 22 | 2 | 2 | 2 | 0 | 100.0% | 2.22u | 111.0% | 2.11 |
| <= 18 | 7 | 4 | 2 | 2 | 50.0% | 0.06u | 1.5% | 2.0775 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.4 | 17 | 17 | 12 | 5 | 70.59% | 7.77u | 45.71% | 2.0753 |
| <= 0.2 | 28 | 25 | 15 | 9 | 62.5% | 7.11u | 28.44% | 2.086 |
| 0.2 - 0.3 | 33 | 33 | 17 | 13 | 56.67% | 5.19u | 15.73% | 2.0779 |
| 0.4 - 0.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pncl | 42 | 39 | 27 | 9 | 75.0% | 20.41u | 52.33% | 2.0879 |
| Unibet | 3 | 3 | 2 | 0 | 100.0% | 2.06u | 68.67% | 2.08 |
| Betfair | 4 | 4 | 3 | 1 | 75.0% | 2.0u | 50.0% | 2.025 |
| Superbet | 8 | 8 | 4 | 4 | 50.0% | 0.17u | 2.12% | 2.0537 |
| Betano | 14 | 14 | 6 | 8 | 42.86% | -1.7u | -12.14% | 2.0679 |
| 1xBet | 6 | 6 | 2 | 4 | 33.33% | -1.87u | -31.17% | 2.1 |
| Marathon | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.125 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| French Open | 21 | 21 | 16 | 5 | 76.19% | 11.83u | 56.33% | 2.0571 |
| Hamburg | 5 | 5 | 5 | 0 | 100.0% | 5.07u | 101.4% | 2.014 |
| Istanbul (Turkey) - Qualification | 3 | 3 | 3 | 0 | 100.0% | 3.26u | 108.67% | 2.0867 |
| Rome | 7 | 7 | 4 | 2 | 66.67% | 2.24u | 32.0% | 2.0771 |
| Rabat | 2 | 2 | 2 | 0 | 100.0% | 2.11u | 105.5% | 2.055 |
| Geneva | 2 | 2 | 2 | 0 | 100.0% | 2.09u | 104.5% | 2.045 |
| Bordeaux | 1 | 1 | 1 | 0 | 100.0% | 1.19u | 119.0% | 2.19 |
| Zagreb | 1 | 1 | 1 | 0 | 100.0% | 1.18u | 118.0% | 2.18 |
| Strasbourg | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| M15 Doboj | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| M25 Bol 2 | 2 | 1 | 1 | 0 | 100.0% | 1.15u | 115.0% | 2.15 |
| M15 Kayseri | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M25 Bol | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M15 Kranjska Gora (Slovenia) | 2 | 1 | 1 | 0 | 100.0% | 1.11u | 111.0% | 2.11 |
| Tunis | 1 | 1 | 1 | 0 | 100.0% | 1.02u | 102.0% | 2.02 |
| M15 Maringa 2 (Brazil) | 4 | 4 | 2 | 2 | 50.0% | 0.21u | 5.25% | 2.115 |
| Vicenza | 2 | 2 | 1 | 1 | 50.0% | 0.05u | 2.5% | 2.085 |
| Little Rock | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.18 |
| M15 Brcko | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.06 |
| W35 Bol 2 | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Cordoba 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |
| Parma | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| Valencia | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| M15 Kursumlijska Banja 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.1 |
| M25 Deauville | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.17 |
| W15 Monastir 14 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.02 |
| W15 Kursumlijska Banja 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.97 |
| W35 Estepona (Spain) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.17 |
| W15 Hurghada 5 (Egypt) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.1 |
| M25 Troisdorf (Germany) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.14 |

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

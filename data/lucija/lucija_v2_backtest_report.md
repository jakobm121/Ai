# Lucija Backtest Report

Generated at: **2026-05-29T23:13:01.915810+02:00**

## Input

- Source file: `data/tennis_totals_results.json`
- Source picks loaded: **501**
- Settled picks available: **492**

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
  "avg_close_set_max": 0.4,
  "avg_three_set_max": 0.4,
  "confidence_min": 70,
  "market_gap_min": 0.25,
  "quality_min": 0,
  "strength_gap_max": 20
}
```

### V3 over
```json
{
  "side": "over",
  "avg_close_set_min": 0.2,
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
| All settled totals | 492 | 492 | 0 | 220 | 239 | 33 | 47.93% | -8.26u | -1.68% | 2.0567 | -42.43u |
| V1 original | 146 | 144 | 2 | 86 | 55 | 3 | 60.99% | 34.49u | 23.95% | 2.0474 | -7.92u |
| V2 under | 81 | 80 | 1 | 43 | 33 | 4 | 56.58% | 13.29u | 16.61% | 2.0884 | -7.0u |
| V3 over | 62 | 62 | 0 | 27 | 30 | 5 | 47.37% | -5.42u | -8.74% | 1.939 | -11.21u |

## Train / test

| Model | Split | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | train_75 | 109 | 109 | 71 | 36 | 66.36% | 37.68u | 34.57% | 2.0401 | -4.7u |
| V1 | test_25 | 37 | 35 | 15 | 19 | 44.12% | -3.19u | -9.11% | 2.0703 | -6.92u |
| V2 | train_75 | 60 | 60 | 36 | 20 | 64.29% | 18.91u | 31.52% | 2.0918 | -7.0u |
| V2 | test_25 | 21 | 20 | 7 | 13 | 35.0% | -5.62u | -28.1% | 2.078 | -5.62u |
| V3 | train_75 | 46 | 46 | 19 | 24 | 44.19% | -6.46u | -14.04% | 1.9391 | -11.07u |
| V3 | test_25 | 16 | 16 | 8 | 6 | 57.14% | 1.04u | 6.5% | 1.9387 | -2.11u |

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
| 2026-05-07 | H. Medjedovic - V. Royer | UNDER 21.5 games | 2.17 | win | 1.17 | 21.5 | 0.25 | 0.3021 | 0.4233 | 19.88 |
| 2026-05-08 | D. Vekic - M. Ristic | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.2125 | 0.3542 | 0.4707 | 14.48 |
| 2026-05-08 | D. Altmaier - A. Zverev | UNDER 19.5 games | 2.18 | loss | -1.0 | 19.5 | 0.254 | 0.3399 | 0.8096 | 18.43 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 0.4802 | 16.45 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 0.5758 | 6.45 |
| 2026-05-08 | R. Masarova - L. Fernandez | UNDER 20.5 games | 2.17 | loss | -1.0 | 20.5 | 0.3715 | 0.1524 | 0.3459 | 11.03 |
| 2026-05-09 | H. Medjedovic - J. Fonseca | UNDER 22.5 games | 1.99 | win | 0.99 | 22.5 | 0.2847 | 0.3947 | 0.2536 | 16.03 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 0.433 | 7.3 |
| 2026-05-11 | N. McDonald - D. Glinka | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.1736 | 0.3588 | 0.256 | 7.03 |
| 2026-05-11 | L. Draxl - E. Nava | UNDER 20.5 games | 2.09 | loss | -1.0 | 20.5 | 0.2083 | 0.3646 | 0.4955 | 15.55 |
| 2026-05-12 | S. De La Fuente - M. A. Dellien Velasco | UNDER 19.5 games | 2.1 | win | 1.1 | 19.5 | 0.2611 | 0.2028 | 0.4811 | 7.08 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-13 | J. Pegula - I. Swiatek | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.3166 | 0.2703 | 0.3993 | 2.63 |
| 2026-05-13 | R. Collignon - G. Blancaneaux | UNDER 19.5 games | 2.07 | win | 1.07 | 19.5 | 0.0 | 0.381 | 0.7789 | 11.08 |
| 2026-05-13 | F. Urgesi - V. Golubic | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.3333 | 0.2408 | 0.5416 | 2.33 |
| 2026-05-14 | A. Sasnovich - A. Blinkova | UNDER 20.5 games | 1.97 | loss | -1.0 | 20.5 | 0.2167 | 0.375 | 0.3089 | 16.57 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 0.5207 | 9.83 |
| 2026-05-14 | B. Krejcikova - V. Golubic | UNDER 19.5 games | 2.13 | loss | -1.0 | 19.5 | 0.3222 | 0.3287 | 0.4339 | 0.6 |
| 2026-05-14 | D. Dzumhur - J. Munar | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.125 | 0.3229 | 0.4074 | 4.38 |
| 2026-05-14 | M. Landaluce - D. Medvedev | UNDER 21.5 games | 2.04 | loss | -1.0 | 21.5 | 0.3611 | 0.3588 | 0.4218 | 7.44 |
| 2026-05-14 | I. Swiatek - E. Svitolina | UNDER 19.5 games | 2.1 | loss | -1.0 | 19.5 | 0.2611 | 0.1963 | 0.5411 | 10.3 |
| 2026-05-15 | A. Rinderknech - M. Damm | UNDER 22.5 games | 2.19 | loss | -1.0 | 22.5 | 0.1111 | 0.375 | 0.2796 | 6.72 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | M. Schoenhaus - L. van Assche | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.3889 | 0.2778 | 0.3928 | 15.89 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 0.7922 | 18.7 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-17 | D. Dedura - F. Tiafoe | UNDER 20.5 games | 2.2 | win | 1.2 | 20.5 | 0.1984 | 0.3995 | 0.4357 | 1.02 |
| 2026-05-17 | L. Jeanjean - L. Fernandez | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.3541 | 0.3125 | 0.4974 | 12.67 |
| 2026-05-17 | J. Sinner - C. Ruud | UNDER 19.5 games | 2.18 | loss | -1.0 | 19.5 | 0.1111 | 0.2592 | 0.7144 | 3.39 |
| 2026-05-18 | R. Bertrand - D. Glinka | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.0 | 0.3125 | 0.4394 | 1.0 |
| 2026-05-18 | D. Altmaier - R. Hijikata | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2143 | 0.3215 | 0.3966 | 8.72 |
| 2026-05-19 | L. Zaar - J. Bouzas Maneiro | UNDER 19.5 games | 2.06 | win | 1.06 | 19.5 | 0.3222 | 0.2815 | 0.4974 | 16.76 |
| 2026-05-19 | N. Honda - P. Sekulic | UNDER 20.5 games | 2.05 | push | 0.0 | 20.5 | 0.2143 | 0.2262 | 0.5649 | 19.56 |
| 2026-05-19 | I. Burillo Escorihuela - V. Tomova | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2 | 0.3334 | 0.4698 | 17.1 |
| 2026-05-20 | M. Bassols - Ka. Pliskova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.3125 | 0.2292 | 0.5182 | 17.5 |
| 2026-05-20 | R. Collignon - C. Ruud | UNDER 21.5 games | 2.03 | win | 1.03 | 21.5 | 0.0556 | 0.3333 | 0.4205 | 11.84 |
| 2026-05-20 | J. Tjen - C. Osorio | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.1611 | 0.2713 | 0.4865 | 8.84 |
| 2026-05-20 | N. Budkov Kjaer - T. Gentzsch | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2777 | 0.3334 | 0.4374 | 0.11 |
| 2026-05-21 | I. Ivashka - A. Hernandez | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.15 | 0.3778 | 0.6325 | 11.99 |
| 2026-05-21 | P. Makk - D. Milanovic | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.2381 | 0.2738 | 0.4567 | 14.24 |
| 2026-05-21 | A. Popyrin - C. Ruud | UNDER 21.5 games | 2.11 | win | 1.11 | 21.5 | 0.25 | 0.3959 | 0.4835 | 17.38 |
| 2026-05-22 | E. Nava - P. Martinez | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.2361 | 0.3692 | 0.402 | 9.61 |
| 2026-05-23 | L. Vujovic - S. Bojica | UNDER 18.5 games | 2.17 | win | 1.17 | 18.5 | 0.1611 | 0.2185 | 0.6248 | 6.65 |
| 2026-05-23 | O. Roca Batalla - J. Nikles | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.1805 | 0.3218 | 0.4403 | 13.55 |
| 2026-05-23 | F. Tabacco - N. Tepmahc | UNDER 19.0 games | 2.16 | loss | -1.0 | 19.0 | 0.2125 | 0.2334 | 0.4286 | 11.05 |
| 2026-05-23 | F. Tabacco - N. Tepmahc | UNDER 19.5 games | 1.95 | loss | -1.0 | 19.5 | 0.2125 | 0.2334 | 0.4228 | 11.05 |
| 2026-05-23 | L. Petretic - M. Lazarenko | UNDER 18.5 games | 2.15 | loss | -1.0 | 18.5 | 0.1 | 0.2666 | 0.5041 | 16.8 |
| 2026-05-23 | L. Petretic - M. Lazarenko | UNDER 19.0 games | 2.01 | loss | -1.0 | 19.0 | 0.1 | 0.2666 | 0.5598 | 16.8 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 21.5 games | 2.15 | loss | -1.0 | 21.5 | 0.1125 | 0.2521 | 0.3487 | 5.62 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 22.0 games | 2.05 | loss | -1.0 | 22.0 | 0.1125 | 0.2521 | 0.3466 | 5.62 |
| 2026-05-23 | A. Kalinina - P. Marcinko | UNDER 20.0 games | 2.15 | push | 0.0 | 20.0 | 0.1111 | 0.3889 | 0.4018 | 13.34 |
| 2026-05-23 | U. Hrabavets - O. Danilova | UNDER 19.0 games | 1.97 | win | 0.97 | 19.0 | 0.3222 | 0.3453 | 0.5058 | 4.49 |
| 2026-05-23 | A. Kalinina - P. Marcinko | UNDER 19.5 games | 2.17 | push | 0.0 | 19.5 | 0.1111 | 0.3889 | 0.4121 | 13.34 |
| 2026-05-23 | M. Alves - H. Hoeyeraal | UNDER 18.5 games | 2.19 | win | 1.19 | 18.5 | 0.1111 | 0.2778 | 0.4988 | 9.77 |
| 2026-05-23 | M. Alves - H. Hoeyeraal | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.1111 | 0.2778 | 0.4955 | 9.77 |
| 2026-05-23 | M. Alves - H. Hoeyeraal | UNDER 20.0 games | 2.11 | win | 1.11 | 20.0 | 0.1111 | 0.2778 | 0.4675 | 9.77 |
| 2026-05-24 | A. Azkara - P. Schoen | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.0625 | 0.3438 | 0.4408 | 17.87 |
| 2026-05-24 | N. Vukadin - M. Kasnikowski | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.1805 | 0.3067 | 0.5764 | 4.8 |
| 2026-05-24 | A. Kubareva - L. Petretic | UNDER 19.5 games | 2.02 | loss | -1.0 | 19.5 | 0.2 | 0.2666 | 0.4263 | 0.3 |
| 2026-05-24 | L. Vujovic - M. Mettraux | UNDER 19.5 games | 1.97 | loss | -1.0 | 19.5 | 0.25 | 0.2083 | 0.5191 | 19.4 |
| 2026-05-24 | S. Kraus - B. Bencic | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.2777 | 0.2871 | 0.5449 | 12.11 |
| 2026-05-24 | U. Hrabavets - A. El Sayed | UNDER 18.5 games | 2.1 | loss | -1.0 | 18.5 | 0.225 | 0.2938 | 0.655 | 16.15 |
| 2026-05-25 | D. Kasatkina - Z. Sonmez | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2111 | 0.2296 | 0.3753 | 14.26 |
| 2026-05-25 | L. Samsonova - J. Teichmann | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.1736 | 0.382 | 0.4974 | 11.28 |
| 2026-05-25 | M. Dhamne - F. Ferreira Silva | UNDER 20.5 games | 2.12 | loss | -1.0 | 20.5 | 0.275 | 0.3584 | 0.3067 | 14.52 |
| 2026-05-25 | H. Grenier - L. Nardi | UNDER 19.5 games | 2.2 | win | 1.2 | 19.5 | 0.1666 | 0.3646 | 0.573 | 0.88 |
| 2026-05-25 | P. Zahraj - G. Hussey | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.2111 | 0.3361 | 0.3128 | 6.09 |
| 2026-05-25 | H. Guo - M. Kessler | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2381 | 0.3915 | 0.4178 | 1.67 |
| 2026-05-26 | E. Navarro - J. Tjen | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.1611 | 0.2639 | 0.4534 | 7.3 |
| 2026-05-26 | J. Clarke - M. Karol | UNDER 20.5 games | 2.13 | loss | -1.0 | 20.5 | 0.1 | 0.375 | 0.4871 | 9.47 |
| 2026-05-26 | L. Siegemund - N. Osaka | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.15 | 0.4 | 0.5012 | 8.5 |
| 2026-05-27 | C. McNally - B. Bencic | UNDER 20.0 games | 2.09 | win | 1.09 | 20.0 | 0.2056 | 0.1991 | 0.4935 | 3.09 |
| 2026-05-27 | J. Paolini - S. Sierra | UNDER 20.5 games | 2.06 | loss | -1.0 | 20.5 | 0.3667 | 0.3148 | 0.2813 | 15.43 |
| 2026-05-27 | L. Neumayer - T. Boyer | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.3166 | 0.3639 | 0.3688 | 15.7 |
| 2026-05-28 | D. Vekic - N. Osaka | UNDER 20.5 games | 2.06 | loss | -1.0 | 20.5 | 0.2111 | 0.3565 | 0.4534 | 17.86 |
| 2026-05-29 | J. Teichmann - K. Muchova | UNDER 18.5 games | 2.12 | loss | -1.0 | 18.5 | 0.2291 | 0.3889 | 0.7662 | 12.59 |
| 2026-05-29 | S. Sierra - S. Cirstea | UNDER 20.5 games | 1.99 | win | 0.99 | 20.5 | 0.365 | 0.2818 | 0.527 | 10.32 |
| 2026-05-29 | T. Daniel - M. Erhard | UNDER 21.0 games | 2.11 | loss | -1.0 | 21.0 | 0.1714 | 0.2536 | 0.2618 | 1.3 |
| 2026-05-29 | P. Stearns - B. Bencic | UNDER 20.5 games | 2.13 | pending | 0.0 | 20.5 | 0.2 | 0.3667 | 0.447 | 10.0 |

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
| 2026-05-08 | Xin. Wang - A. Eala | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.3555 | 0.2213 | 0.1018 | 0.23 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 0.285 | 3.78 |
| 2026-05-08 | I. Vasa - F. Ribero | OVER 21.5 games | 1.84 | win | 0.84 | 21.5 | 0.4375 | 0.423 | 0.1492 | 19.6 |
| 2026-05-08 | D. Prizmic - N. Djokovic | OVER 21.5 games | 1.83 | win | 0.83 | 21.5 | 0.3958 | 0.4236 | 0.2821 | 4.62 |
| 2026-05-09 | Q. Zheng - J. Ostapenko | OVER 20.5 games | 1.91 | win | 0.91 | 20.5 | 0.5 | 0.5167 | 0.336 | 6.4 |
| 2026-05-09 | J. Paolini - E. Mertens | OVER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.35 | 0.2334 | 0.1018 | 1.8 |
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
| 2026-05-16 | M. Kessler - R. Zarazua | OVER 21.5 games | 1.9 | loss | -1.0 | 21.5 | 0.5834 | 0.2963 | 0.2259 | 0.14 |
| 2026-05-16 | O. Selekhmeteva - S. Kenin | OVER 21.5 games | 1.96 | win | 0.96 | 21.5 | 0.4722 | 0.5104 | 0.0514 | 18.72 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 0.3448 | 13.95 |
| 2026-05-17 | M. Kessler - O. Selekhmeteva | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.4444 | 0.4259 | 0.0 | 18.44 |
| 2026-05-17 | M. Sakkari - P. Stearns | OVER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.375 | 0.5209 | 0.0168 | 4.5 |
| 2026-05-18 | M. Frech - T. Gibson | OVER 21.5 games | 1.9 | win | 0.9 | 21.5 | 0.5 | 0.2963 | 0.0362 | 2.44 |
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

## V2 under breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| under | 81 | 80 | 43 | 33 | 56.58% | 13.29u | 16.61% | 2.0884 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| atp | 16 | 16 | 13 | 3 | 81.25% | 10.8u | 67.5% | 2.075 |
| itf | 16 | 16 | 9 | 7 | 56.25% | 3.1u | 19.38% | 2.0913 |
| wta | 26 | 25 | 11 | 11 | 50.0% | 0.59u | 2.36% | 2.0948 |
| challenger | 23 | 23 | 10 | 12 | 45.45% | -1.2u | -5.22% | 2.0887 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| men | 43 | 43 | 28 | 14 | 66.67% | 16.41u | 38.16% | 2.0933 |
| women | 38 | 37 | 15 | 19 | 44.12% | -3.12u | -8.43% | 2.0827 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20.5 - 21.5 | 13 | 13 | 10 | 3 | 76.92% | 7.59u | 58.38% | 2.0685 |
| 19.5 - 20.5 | 26 | 25 | 13 | 10 | 56.52% | 3.82u | 15.28% | 2.0728 |
| 18.5 - 19.5 | 33 | 33 | 16 | 15 | 51.61% | 2.5u | 7.58% | 2.1021 |
| <= 18.5 | 6 | 6 | 3 | 3 | 50.0% | 0.39u | 6.5% | 2.1267 |
| 21.5 - 22.5 | 3 | 3 | 1 | 2 | 33.33% | -1.01u | -33.67% | 2.0767 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.95 - 2.05 | 31 | 31 | 21 | 9 | 70.0% | 12.26u | 39.55% | 2.0152 |
| 2.05 - 2.2 | 49 | 48 | 22 | 23 | 48.89% | 2.03u | 4.23% | 2.1385 |
| 1.8 - 1.95 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.95 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 83 - 86 | 14 | 14 | 11 | 2 | 84.62% | 10.14u | 72.43% | 2.1107 |
| 89 - 92 | 17 | 17 | 12 | 4 | 75.0% | 8.18u | 48.12% | 2.0265 |
| > 92 | 4 | 4 | 4 | 0 | 100.0% | 4.13u | 103.25% | 2.0325 |
| 80 - 83 | 7 | 7 | 3 | 3 | 50.0% | 0.39u | 5.57% | 2.1229 |
| <= 80 | 12 | 12 | 5 | 7 | 41.67% | -1.33u | -11.08% | 2.1242 |
| 86 - 89 | 27 | 26 | 8 | 17 | 32.0% | -8.22u | -31.62% | 2.0996 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 84 | 22 | 22 | 15 | 6 | 71.43% | 10.16u | 46.18% | 2.0845 |
| 76 - 80 | 21 | 21 | 11 | 8 | 57.89% | 3.54u | 16.86% | 2.0681 |
| 84 - 88 | 14 | 13 | 7 | 5 | 58.33% | 2.73u | 21.0% | 2.1269 |
| 72 - 76 | 14 | 14 | 8 | 6 | 57.14% | 2.73u | 19.5% | 2.0921 |
| <= 72 | 6 | 6 | 2 | 4 | 33.33% | -1.87u | -31.17% | 2.0317 |
| > 88 | 4 | 4 | 0 | 4 | 0.0% | -4.0u | -100.0% | 2.1625 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.45 - 0.6 | 36 | 36 | 21 | 13 | 61.76% | 9.78u | 27.17% | 2.0928 |
| 0.35 - 0.45 | 24 | 23 | 14 | 7 | 66.67% | 7.99u | 34.74% | 2.0722 |
| > 0.6 | 8 | 8 | 4 | 4 | 50.0% | 0.27u | 3.38% | 2.1062 |
| 0.25 - 0.35 | 13 | 13 | 4 | 9 | 30.77% | -4.75u | -36.54% | 2.0938 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 - 15 | 21 | 21 | 12 | 7 | 63.16% | 5.84u | 27.81% | 2.0929 |
| <= 5 | 16 | 16 | 10 | 6 | 62.5% | 4.7u | 29.38% | 2.0744 |
| 5 - 10 | 22 | 21 | 12 | 9 | 57.14% | 3.94u | 18.76% | 2.0971 |
| 15 - 20 | 22 | 22 | 9 | 11 | 45.0% | -1.19u | -5.41% | 2.0859 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.35 | 8 | 8 | 7 | 1 | 87.5% | 6.26u | 78.25% | 2.0488 |
| 0.15 - 0.2 | 19 | 18 | 11 | 6 | 64.71% | 5.99u | 33.28% | 2.1 |
| 0.25 - 0.3 | 7 | 7 | 4 | 3 | 57.14% | 1.14u | 16.29% | 2.0771 |
| 0.35 - 0.45 | 6 | 6 | 3 | 3 | 50.0% | 0.33u | 5.5% | 2.1 |
| 0.2 - 0.25 | 22 | 22 | 10 | 11 | 47.62% | -0.1u | -0.45% | 2.0759 |
| <= 0.15 | 19 | 19 | 8 | 9 | 47.06% | -0.33u | -1.74% | 2.1089 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.35 | 22 | 22 | 14 | 7 | 66.67% | 8.05u | 36.59% | 2.0936 |
| 0.2 - 0.3 | 32 | 32 | 18 | 13 | 58.06% | 6.34u | 19.81% | 2.0769 |
| 0.35 - 0.4 | 24 | 23 | 10 | 11 | 47.62% | -0.19u | -0.83% | 2.0952 |
| <= 0.2 | 3 | 3 | 1 | 2 | 33.33% | -0.91u | -30.33% | 2.12 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 - 21 | 15 | 15 | 10 | 5 | 66.67% | 5.62u | 37.47% | 2.088 |
| <= 18 | 4 | 4 | 4 | 0 | 100.0% | 4.32u | 108.0% | 2.08 |
| 19 - 20 | 31 | 30 | 15 | 13 | 53.57% | 3.2u | 10.67% | 2.093 |
| 21 - 22 | 6 | 6 | 4 | 2 | 66.67% | 2.35u | 39.17% | 2.075 |
| 18 - 19 | 25 | 25 | 10 | 13 | 43.48% | -2.2u | -8.8% | 2.0876 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.4 | 21 | 21 | 16 | 5 | 76.19% | 12.07u | 57.48% | 2.071 |
| <= 0.2 | 30 | 29 | 14 | 13 | 51.85% | 2.18u | 7.52% | 2.1048 |
| 0.2 - 0.3 | 29 | 29 | 13 | 14 | 48.15% | 0.04u | 0.14% | 2.0862 |
| 0.4 - 0.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.04 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pncl | 45 | 44 | 25 | 16 | 60.98% | 11.24u | 25.55% | 2.0984 |
| Betfair | 5 | 5 | 4 | 1 | 80.0% | 3.1u | 62.0% | 2.02 |
| Betano | 12 | 12 | 7 | 5 | 58.33% | 2.44u | 20.33% | 2.0883 |
| Unibet | 2 | 2 | 2 | 0 | 100.0% | 2.02u | 101.0% | 2.01 |
| 1xBet | 8 | 8 | 3 | 4 | 42.86% | -0.73u | -9.12% | 2.0762 |
| Marathon | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.15 |
| Superbet | 7 | 7 | 2 | 5 | 28.57% | -2.78u | -39.71% | 2.0929 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Hamburg | 6 | 6 | 6 | 0 | 100.0% | 6.43u | 107.17% | 2.0717 |
| M15 Maringa 2 (Brazil) | 3 | 3 | 3 | 0 | 100.0% | 3.4u | 113.33% | 2.1333 |
| French Open | 17 | 16 | 9 | 7 | 56.25% | 2.4u | 15.0% | 2.0706 |
| Geneva | 2 | 2 | 2 | 0 | 100.0% | 2.14u | 107.0% | 2.07 |
| Tunis | 2 | 2 | 2 | 0 | 100.0% | 2.09u | 104.5% | 2.045 |
| Bordeaux | 3 | 3 | 2 | 1 | 66.67% | 1.26u | 42.0% | 2.15 |
| Chisinau | 1 | 1 | 1 | 0 | 100.0% | 1.2u | 120.0% | 2.2 |
| Strasbourg | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| M15 Doboj | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| M25 Mataro | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.15u | 115.0% | 2.15 |
| M15 Kayseri | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M25 Bol | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| Cordoba 2 | 1 | 1 | 1 | 0 | 100.0% | 1.1u | 110.0% | 2.1 |
| W15 Kursumlijska Banja 2 | 2 | 2 | 1 | 1 | 50.0% | 0.17u | 8.5% | 2.07 |
| Rabat | 4 | 4 | 1 | 1 | 50.0% | 0.06u | 1.5% | 2.1375 |
| Vicenza | 2 | 2 | 1 | 1 | 50.0% | 0.0u | 0.0% | 2.06 |
| W15 Hurghada 5 (Egypt) | 2 | 2 | 1 | 1 | 50.0% | -0.03u | -1.5% | 2.035 |
| Rome | 12 | 12 | 5 | 6 | 45.45% | -0.8u | -6.67% | 2.0967 |
| Bengaluru 3 (India) - Qualification | 4 | 4 | 1 | 2 | 33.33% | -1.0u | -25.0% | 2.0625 |
| Parma | 3 | 3 | 1 | 2 | 33.33% | -1.0u | -33.33% | 2.06 |
| Oeiras 6 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.09 |
| Paris | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.97 |
| Valencia | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| Centurion (South Africa) - Qualification | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| M15 Monastir 19 | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.055 |
| Kosice | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.12 |
| W15 Monastir 14 | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 2.06 |

## V3 over breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| over | 62 | 62 | 27 | 30 | 47.37% | -5.42u | -8.74% | 1.939 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| atp | 11 | 11 | 7 | 4 | 63.64% | 2.35u | 21.36% | 1.9291 |
| itf | 2 | 2 | 1 | 1 | 50.0% | -0.17u | -8.5% | 1.885 |
| wta | 25 | 25 | 10 | 13 | 43.48% | -3.75u | -15.0% | 1.9416 |
| challenger | 24 | 24 | 9 | 12 | 42.86% | -3.85u | -16.04% | 1.9454 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| women | 29 | 29 | 13 | 14 | 48.15% | -2.15u | -7.41% | 1.9338 |
| men | 33 | 33 | 14 | 16 | 46.67% | -3.27u | -9.91% | 1.9436 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 10 | 10 | 8 | 2 | 80.0% | 5.06u | 50.6% | 1.885 |
| > 22.5 | 2 | 2 | 0 | 1 | 0.0% | -1.0u | -50.0% | 2.105 |
| 20.5 - 21.5 | 31 | 31 | 13 | 15 | 46.43% | -3.2u | -10.32% | 1.9219 |
| 21.5 - 22.5 | 19 | 19 | 6 | 12 | 33.33% | -6.28u | -33.05% | 1.9779 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| <= 1.8 | 2 | 2 | 1 | 0 | 100.0% | 0.8u | 40.0% | 1.8 |
| 1.8 - 1.95 | 35 | 35 | 19 | 16 | 54.29% | 0.8u | 2.29% | 1.8914 |
| 2.05 - 2.2 | 5 | 5 | 1 | 3 | 25.0% | -1.94u | -38.8% | 2.088 |
| 1.95 - 2.05 | 20 | 20 | 6 | 11 | 35.29% | -5.08u | -25.4% | 1.999 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 83 | 8 | 8 | 4 | 3 | 57.14% | 0.48u | 6.0% | 1.9213 |
| 86 - 89 | 8 | 8 | 3 | 3 | 50.0% | -0.11u | -1.38% | 1.9238 |
| 83 - 86 | 8 | 8 | 4 | 4 | 50.0% | -0.37u | -4.62% | 1.9225 |
| <= 80 | 3 | 3 | 1 | 2 | 33.33% | -0.97u | -32.33% | 2.0167 |
| > 92 | 28 | 28 | 13 | 13 | 50.0% | -1.13u | -4.04% | 1.9464 |
| 89 - 92 | 7 | 7 | 2 | 5 | 28.57% | -3.32u | -47.43% | 1.9329 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 76 - 80 | 10 | 10 | 7 | 3 | 70.0% | 3.24u | 32.4% | 1.891 |
| <= 72 | 6 | 6 | 4 | 2 | 66.67% | 1.51u | 25.17% | 1.9217 |
| 72 - 76 | 4 | 4 | 1 | 2 | 33.33% | -1.2u | -30.0% | 1.85 |
| 84 - 88 | 12 | 12 | 5 | 6 | 45.45% | -1.27u | -10.58% | 1.9842 |
| 80 - 84 | 14 | 14 | 5 | 8 | 38.46% | -3.48u | -24.86% | 1.9164 |
| > 88 | 16 | 16 | 5 | 9 | 35.71% | -4.22u | -26.38% | 1.9838 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.35 | 14 | 14 | 11 | 3 | 78.57% | 7.11u | 50.79% | 1.9286 |
| 0.2 - 0.25 | 3 | 3 | 1 | 2 | 33.33% | -1.18u | -39.33% | 1.8567 |
| <= 0.2 | 45 | 45 | 15 | 25 | 37.5% | -11.35u | -25.22% | 1.9478 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 - 25 | 7 | 7 | 4 | 1 | 80.0% | 2.67u | 38.14% | 1.9057 |
| 10 - 15 | 10 | 10 | 6 | 3 | 66.67% | 2.52u | 25.2% | 1.941 |
| 30 - 35 | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| 25 - 30 | 1 | 1 | 1 | 0 | 100.0% | 0.93u | 93.0% | 1.93 |
| 15 - 20 | 12 | 12 | 4 | 7 | 36.36% | -3.49u | -29.08% | 1.9392 |
| 5 - 10 | 11 | 11 | 3 | 7 | 30.0% | -4.3u | -39.09% | 1.9527 |
| <= 5 | 20 | 20 | 8 | 12 | 40.0% | -4.78u | -23.9% | 1.938 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.35 - 0.45 | 24 | 24 | 12 | 11 | 52.17% | -0.36u | -1.5% | 1.9175 |
| 0.3 - 0.35 | 5 | 5 | 2 | 3 | 40.0% | -1.22u | -24.4% | 1.894 |
| > 0.45 | 33 | 33 | 13 | 16 | 44.83% | -3.84u | -11.64% | 1.9615 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.35 - 0.4 | 7 | 7 | 6 | 1 | 85.71% | 4.57u | 65.29% | 1.95 |
| 0.3 - 0.35 | 7 | 7 | 3 | 4 | 42.86% | -1.38u | -19.71% | 1.91 |
| 0.2 - 0.3 | 4 | 4 | 1 | 3 | 25.0% | -2.1u | -52.5% | 1.9225 |
| 0.4 - 0.5 | 29 | 29 | 12 | 13 | 48.0% | -2.26u | -7.79% | 1.929 |
| 0.5 - 0.6 | 15 | 15 | 5 | 9 | 35.71% | -4.25u | -28.33% | 1.9713 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 21 - 22 | 12 | 12 | 8 | 3 | 72.73% | 4.1u | 34.17% | 1.8958 |
| > 23 | 21 | 21 | 11 | 8 | 57.89% | 2.31u | 11.0% | 1.9633 |
| 19 - 20 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.91 |
| 20 - 21 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.98 |
| 22 - 23 | 27 | 27 | 8 | 17 | 32.0% | -9.83u | -36.41% | 1.9389 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| > 0.6 | 8 | 8 | 4 | 3 | 57.14% | 0.89u | 11.12% | 1.995 |
| 0.4 - 0.5 | 25 | 25 | 12 | 11 | 52.17% | -0.5u | -2.0% | 1.9128 |
| 0.5 - 0.6 | 22 | 22 | 9 | 11 | 45.0% | -2.55u | -11.59% | 1.9555 |
| 0.3 - 0.4 | 7 | 7 | 2 | 5 | 28.57% | -3.26u | -46.57% | 1.9171 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Betfair | 2 | 2 | 2 | 0 | 100.0% | 1.91u | 95.5% | 1.955 |
| 1xBet | 4 | 4 | 3 | 1 | 75.0% | 1.78u | 44.5% | 1.92 |
| BetVictor | 1 | 1 | 1 | 0 | 100.0% | 0.83u | 83.0% | 1.83 |
| bet365 | 4 | 4 | 2 | 1 | 66.67% | 0.7u | 17.5% | 1.8325 |
| Unibet | 6 | 6 | 2 | 3 | 40.0% | -1.18u | -19.67% | 1.9583 |
| Pncl | 34 | 34 | 15 | 16 | 48.39% | -2.24u | -6.59% | 1.9503 |
| Superbet | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 1.9633 |
| Betano | 8 | 8 | 2 | 6 | 25.0% | -4.22u | -52.75% | 1.94 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kosice | 2 | 2 | 2 | 0 | 100.0% | 1.79u | 89.5% | 1.895 |
| Cervia (Italy) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Parma | 1 | 1 | 1 | 0 | 100.0% | 0.9u | 90.0% | 1.9 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 0.87u | 87.0% | 1.87 |
| Hamburg | 3 | 3 | 2 | 1 | 66.67% | 0.86u | 28.67% | 1.93 |
| Brazzaville | 1 | 1 | 1 | 0 | 100.0% | 0.84u | 84.0% | 1.84 |
| W15 Oliva (Spain) | 1 | 1 | 1 | 0 | 100.0% | 0.83u | 83.0% | 1.83 |
| Bordeaux | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.04 |
| Rabat | 2 | 2 | 1 | 1 | 50.0% | -0.08u | -4.0% | 1.885 |
| Chisinau | 2 | 2 | 1 | 1 | 50.0% | -0.09u | -4.5% | 1.95 |
| Oeiras 6 | 2 | 2 | 1 | 1 | 50.0% | -0.16u | -8.0% | 1.85 |
| Strasbourg | 6 | 6 | 3 | 3 | 50.0% | -0.21u | -3.5% | 1.93 |
| Rome | 14 | 14 | 7 | 7 | 50.0% | -0.68u | -4.86% | 1.9286 |
| W35 Bol 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.94 |
| French Open | 11 | 11 | 4 | 5 | 44.44% | -1.29u | -11.73% | 1.9655 |
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

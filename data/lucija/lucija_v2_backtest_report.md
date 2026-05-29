# Lucija v2 Backtest Report

Generated at: **2026-05-29T22:33:24.626119+02:00**

## Input

- Source file: `data/tennis_totals_results.json`
- Source picks loaded: **501**
- Settled picks available: **492**

## Rules

### Lucija v1
```json
{
  "avg_close_set_max": 0.55,
  "avg_close_set_min": 0.2,
  "avg_three_set_min": 0.15,
  "confidence_min": 80,
  "h2h_max": 0,
  "market_gap_min": 0.25,
  "quality_min": 72,
  "strength_gap_max": 30
}
```

### Lucija v2
```json
{
  "side": "under",
  "line_min": 20.0,
  "line_max": 21.5,
  "odds_min": 1.95,
  "odds_max": 2.2,
  "confidence_min": 83,
  "quality_min": 76,
  "market_gap_min": 0.25,
  "strength_gap_max": 30,
  "h2h_max": 0,
  "avg_three_set_max": 0.35,
  "avg_close_set_max": 0.5
}
```

## Main comparison

| Model | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All settled totals | 492 | 492 | 0 | 220 | 239 | 33 | 47.93% | -8.26u | -1.68% | 2.0567 | -42.43u |
| Lucija v1 | 110 | 108 | 2 | 68 | 37 | 3 | 64.76% | 33.49u | 31.01% | 2.0475 | -8.12u |
| Lucija v2 | 68 | 66 | 2 | 37 | 26 | 3 | 58.73% | 13.41u | 20.32% | 2.0758 | -6.0u |
| Blocked from v1 by v2 | 55 | 55 | 0 | 36 | 18 | 1 | 66.67% | 18.54u | 33.71% | 2.0258 | -4.95u |

## Train / test

| Model | Split | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | train_75 | 82 | 55 | 25 | 68.75% | 31.91u | 38.91% | 2.0418 | -4.9u |
| V1 | test_25 | 26 | 13 | 12 | 52.0% | 1.58u | 6.08% | 2.0654 | -3.12u |
| V2 | train_75 | 51 | 29 | 19 | 60.42% | 11.78u | 23.1% | 2.0739 | -6.0u |
| V2 | test_25 | 15 | 8 | 7 | 53.33% | 1.63u | 10.87% | 2.082 | -3.96u |

## V2 selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-07 | D. Shapovalov - M. Navone | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.3333 | 0.4167 | 0.2791 | 26.89 |
| 2026-05-08 | B. Van De Zandschulp - A. Kovacevic | UNDER 21.5 games | 2.14 | win | 1.14 | 21.5 | 0.1875 | 0.4062 | 0.5035 | 28.25 |
| 2026-05-09 | G. Heide - A. Holmgren | UNDER 20.5 games | 2.03 | loss | -1.0 | 20.5 | 0.1736 | 0.4896 | 0.5504 | 18.32 |
| 2026-05-09 | O. Oliynykova - L. Noskova | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.325 | 0.3729 | 0.4835 | 23.12 |
| 2026-05-09 | T. M. Etcheverry - M. Bellucci | UNDER 21.5 games | 2.05 | loss | -1.0 | 21.5 | 0.3493 | 0.4828 | 0.4543 | 24.23 |
| 2026-05-10 | D. Vekic - M. Timofeeva | UNDER 20.5 games | 1.97 | win | 0.97 | 20.5 | 0.225 | 0.4146 | 0.3241 | 18.9 |
| 2026-05-11 | N. McDonald - D. Glinka | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.1736 | 0.3588 | 0.256 | 7.03 |
| 2026-05-11 | G. Den Ouden - D. Added | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.275 | 0.4416 | 0.4288 | 9.32 |
| 2026-05-11 | L. Draxl - E. Nava | UNDER 20.5 games | 2.09 | loss | -1.0 | 20.5 | 0.2083 | 0.3646 | 0.4955 | 15.55 |
| 2026-05-12 | L. Darderi - A. Zverev | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.2222 | 0.3148 | 0.594 | 22.0 |
| 2026-05-12 | S. Shimabukuro - Q. Halys | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.0556 | 0.3796 | 0.4499 | 22.72 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-13 | D. Dzumhur - A. Sanchez Quilez | UNDER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.125 | 0.4077 | 0.2835 | 27.4 |
| 2026-05-13 | A. Parks - S. Bandecchi | UNDER 20.5 games | 2.12 | loss | -1.0 | 20.5 | 0.1111 | 0.4021 | 0.4074 | 10.27 |
| 2026-05-14 | J. Reis Da Silva - E. Moller | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.2625 | 0.2437 | 0.3466 | 26.38 |
| 2026-05-14 | D. Dedura - L. Neumayer | UNDER 20.5 games | 2.12 | win | 1.12 | 20.5 | 0.2361 | 0.2291 | 0.2667 | 29.38 |
| 2026-05-14 | D. Dzumhur - J. Munar | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.125 | 0.3229 | 0.4074 | 4.38 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | S. Ofner - K. Feldbausch | UNDER 21.5 games | 2.03 | win | 1.03 | 21.5 | 0.0625 | 0.4896 | 0.4129 | 21.74 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-17 | D. Dedura - F. Tiafoe | UNDER 20.5 games | 2.2 | win | 1.2 | 20.5 | 0.1984 | 0.3995 | 0.4357 | 1.02 |
| 2026-05-17 | M. Kecmanovic - D. Vallejo | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.1667 | 0.4352 | 0.2991 | 24.56 |
| 2026-05-18 | S. Baez - A. Michelsen | UNDER 21.5 games | 2.11 | win | 1.11 | 21.5 | 0.2777 | 0.4074 | 0.2528 | 9.66 |
| 2026-05-18 | M. Houkes - M. Cecchinato | UNDER 21.5 games | 2.12 | win | 1.12 | 21.5 | 0.125 | 0.4722 | 0.279 | 7.81 |
| 2026-05-18 | S. Shimabukuro - S. Sakellaridis | UNDER 21.5 games | 2.16 | loss | -1.0 | 21.5 | 0.1984 | 0.3717 | 0.4171 | 26.66 |
| 2026-05-18 | D. Altmaier - R. Hijikata | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2143 | 0.3215 | 0.3966 | 8.72 |
| 2026-05-19 | N. Honda - P. Sekulic | UNDER 20.5 games | 2.05 | push | 0.0 | 20.5 | 0.2143 | 0.2262 | 0.5649 | 19.56 |
| 2026-05-19 | B. Hassan - F. C. Jianu | UNDER 20.5 games | 2.03 | win | 1.03 | 20.5 | 0.3 | 0.3167 | 0.3106 | 23.6 |
| 2026-05-19 | P. Kudermetova - A. Koevermans | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.3333 | 0.4352 | 0.3254 | 27.11 |
| 2026-05-20 | T. Faurel - J. Clarke | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.2056 | 0.288 | 0.3868 | 21.45 |
| 2026-05-20 | L. Vithoontien - P. Bar Biryukov | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.2 | 0.425 | 0.5894 | 0.9 |
| 2026-05-20 | R. Collignon - C. Ruud | UNDER 21.5 games | 2.03 | win | 1.03 | 21.5 | 0.0556 | 0.3333 | 0.4205 | 11.84 |
| 2026-05-20 | N. Budkov Kjaer - T. Gentzsch | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2777 | 0.3334 | 0.4374 | 0.11 |
| 2026-05-21 | A. Galarneau - F. Cina | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2222 | 0.5 | 0.5251 | 14.89 |
| 2026-05-21 | B. Gadamauri - P. Nesterov | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2361 | 0.4665 | 0.2711 | 1.27 |
| 2026-05-22 | C. Ruud - M. Navone | UNDER 20.5 games | 2.07 | win | 1.07 | 20.5 | 0.2222 | 0.463 | 0.5706 | 23.33 |
| 2026-05-22 | A. Kovacevic - I. Buse | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.3055 | 0.3102 | 0.5238 | 27.17 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 21.5 games | 2.15 | loss | -1.0 | 21.5 | 0.1125 | 0.2521 | 0.3487 | 5.62 |
| 2026-05-23 | A. Kalinina - P. Marcinko | UNDER 20.0 games | 2.15 | push | 0.0 | 20.0 | 0.1111 | 0.3889 | 0.4018 | 13.34 |
| 2026-05-25 | D. Kasatkina - Z. Sonmez | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2111 | 0.2296 | 0.3753 | 14.26 |
| 2026-05-25 | M. Dhamne - F. Ferreira Silva | UNDER 20.5 games | 2.12 | loss | -1.0 | 20.5 | 0.275 | 0.3584 | 0.3067 | 14.52 |
| 2026-05-25 | T. Boyer - M. Damas | UNDER 21.5 games | 2.0 | loss | -1.0 | 21.5 | 0.25 | 0.4584 | 0.3128 | 19.7 |
| 2026-05-25 | P. Zahraj - G. Hussey | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.2111 | 0.3361 | 0.3128 | 6.09 |
| 2026-05-25 | H. Guo - M. Kessler | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2381 | 0.3915 | 0.4178 | 1.67 |
| 2026-05-26 | E. Navarro - J. Tjen | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.1611 | 0.2639 | 0.4534 | 7.3 |
| 2026-05-26 | J. Clarke - M. Karol | UNDER 20.5 games | 2.13 | loss | -1.0 | 20.5 | 0.1 | 0.375 | 0.4871 | 9.47 |
| 2026-05-26 | A. Ruzic - A. Krueger | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.3375 | 0.4021 | 0.2528 | 24.82 |
| 2026-05-26 | M. Brunold - M. Giunta | UNDER 21.5 games | 2.2 | loss | -1.0 | 21.5 | 0.259 | 0.3765 | 0.3128 | 26.62 |
| 2026-05-26 | E. Pridankina - O. Oliynykova | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2611 | 0.3398 | 0.2843 | 24.21 |
| 2026-05-26 | P. Sekulic - M. Krueger | UNDER 21.5 games | 2.18 | push | 0.0 | 21.5 | 0.259 | 0.2843 | 0.3432 | 22.1 |
| 2026-05-27 | C. McNally - B. Bencic | UNDER 20.0 games | 2.09 | win | 1.09 | 20.0 | 0.2056 | 0.1991 | 0.4935 | 3.09 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2222 | 0.3241 | 0.3308 | 25.68 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.0 games | 2.19 | win | 1.19 | 20.0 | 0.2222 | 0.3241 | 0.3341 | 25.68 |
| 2026-05-27 | T. Zeuch - V. Durasovic | UNDER 21.0 games | 2.05 | win | 1.05 | 21.0 | 0.2611 | 0.4176 | 0.3412 | 9.96 |
| 2026-05-27 | L. Neumayer - T. Boyer | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.3166 | 0.3639 | 0.3688 | 15.7 |
| 2026-05-28 | D. Vekic - N. Osaka | UNDER 20.5 games | 2.06 | loss | -1.0 | 20.5 | 0.2111 | 0.3565 | 0.4534 | 17.86 |
| 2026-05-28 | L. Wessels - V. Durasovic | UNDER 21.5 games | 2.14 | loss | -1.0 | 21.5 | 0.25 | 0.3166 | 0.3091 | 20.7 |
| 2026-05-28 | K. Coppejans - F. Agamenone | UNDER 20.5 games | 2.14 | win | 1.14 | 20.5 | 0.1984 | 0.4167 | 0.3152 | 9.58 |
| 2026-05-28 | D. Blanch - S. Kopp | UNDER 21.5 games | 2.1 | win | 1.1 | 21.5 | 0.2083 | 0.4202 | 0.2689 | 4.25 |
| 2026-05-28 | A. Kalinskaya - A. Korneeva | UNDER 20.5 games | 2.1 | loss | -1.0 | 20.5 | 0.1125 | 0.2646 | 0.3957 | 24.12 |
| 2026-05-28 | F. Bondioli - K. Feldbausch | UNDER 20.5 games | 2.1 | loss | -1.0 | 20.5 | 0.2222 | 0.4305 | 0.3439 | 26.75 |
| 2026-05-28 | A. Li - D. Parry | UNDER 20.5 games | 2.04 | win | 1.04 | 20.5 | 0.2429 | 0.3393 | 0.4073 | 20.14 |
| 2026-05-28 | V. Mboko - K. Siniakova | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.1111 | 0.4224 | 0.4127 | 12.64 |
| 2026-05-29 | S. Pankin - E. Coulibaly | UNDER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.1667 | 0.3518 | 0.3128 | 27.1 |
| 2026-05-29 | T. Daniel - M. Erhard | UNDER 21.0 games | 2.11 | loss | -1.0 | 21.0 | 0.1714 | 0.2536 | 0.2618 | 1.3 |
| 2026-05-29 | P. Stearns - B. Bencic | UNDER 20.5 games | 2.13 | pending | 0.0 | 20.5 | 0.2 | 0.3667 | 0.447 | 10.0 |
| 2026-05-29 | M. Mmoh - B. Tomic | UNDER 21.5 games | 2.2 | pending | 0.0 | 21.5 | 0.3472 | 0.4166 | 0.4006 | 25.14 |

## Blocked from v1 by v2

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Quality | Conf |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | L. Pigossi - L. Cortez Llorca | OVER 20.5 games | 1.87 | win | 0.87 | 20.5 | 0.35 | 0.4083 | 78.3 | 85.7 |
| 2026-05-05 | M. Krumich - G. Piraino | OVER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.5786 | 0.3703 | 82.8 | 87.6 |
| 2026-05-05 | A. Li - S. Zhang | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2167 | 0.3223 | 89.4 | 89.7 |
| 2026-05-06 | T. Townsend - N. Brancaccio | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.254 | 0.2976 | 86.0 | 86.9 |
| 2026-05-06 | N. Basiletti - A. Tomljanovic | OVER 20.5 games | 2.15 | win | 1.15 | 20.5 | 0.4778 | 0.4315 | 85.3 | 90.6 |
| 2026-05-08 | A. Tubello - P. Kudermetova | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4778 | 0.3417 | 79.0 | 83.9 |
| 2026-05-08 | L. Pigossi - G. Maristany | OVER 20.5 games | 1.98 | loss | -1.0 | 20.5 | 0.45 | 0.4667 | 83.4 | 85.0 |
| 2026-05-08 | D. Vekic - M. Ristic | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.2125 | 0.3542 | 85.2 | 88.1 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 89.2 | 89.6 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 85.4 | 88.9 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 80.0 | 85.5 |
| 2026-05-09 | D. Vekic - G. Maristany | UNDER 19.5 games | 2.13 | win | 1.13 | 19.5 | 0.15 | 0.4584 | 85.8 | 88.1 |
| 2026-05-09 | H. Medjedovic - J. Fonseca | UNDER 22.5 games | 1.99 | win | 0.99 | 22.5 | 0.2847 | 0.3947 | 78.6 | 89.9 |
| 2026-05-09 | M. Pucinelli de Almeida - F. Roncadelli | UNDER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.4072 | 0.3571 | 77.0 | 87.6 |
| 2026-05-10 | M. Keys - N. Bartunkova | OVER 20.5 games | 1.98 | win | 0.98 | 20.5 | 0.575 | 0.3084 | 87.5 | 88.5 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 75.2 | 89.3 |
| 2026-05-11 | P. Llamas Ruiz - D. Medvedev | OVER 20.5 games | 1.9 | win | 0.9 | 20.5 | 0.4732 | 0.3541 | 81.9 | 91.7 |
| 2026-05-12 | K. Birrell - K. Boulter | OVER 19.5 games | 1.83 | win | 0.83 | 19.5 | 0.4822 | 0.3215 | 73.6 | 87.2 |
| 2026-05-12 | K. Khachanov - D. Prizmic | UNDER 22.5 games | 2.05 | win | 1.05 | 22.5 | 0.2083 | 0.4479 | 81.4 | 90.9 |
| 2026-05-12 | C. Garin - L. Midon | OVER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.6072 | 0.4702 | 87.8 | 93.6 |
| 2026-05-12 | J. B. Torres - B. Fernandez | UNDER 19.5 games | 2.0 | loss | -1.0 | 19.5 | 0.2611 | 0.3491 | 77.6 | 89.3 |
| 2026-05-13 | R. Jodar - L. Darderi | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.3611 | 0.2963 | 83.7 | 89.7 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 81.7 | 90.1 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 82.2 | 87.6 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 73.3 | 82.0 |
| 2026-05-17 | L. Jeanjean - L. Fernandez | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.3541 | 0.3125 | 78.3 | 80.6 |
| 2026-05-18 | N. Mejia - P. Llamas Ruiz | UNDER 19.5 games | 2.01 | loss | -1.0 | 19.5 | 0.25 | 0.2812 | 78.7 | 90.9 |
| 2026-05-19 | L. Midon - R. Carballes Baena | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.6507 | 0.3651 | 76.7 | 80.3 |
| 2026-05-19 | Y. Kabbaj - B. Cengiz | OVER 20.5 games | 1.92 | win | 0.92 | 20.5 | 0.4166 | 0.4713 | 80.1 | 84.4 |
| 2026-05-19 | L. Zaar - J. Bouzas Maneiro | UNDER 19.5 games | 2.06 | win | 1.06 | 19.5 | 0.3222 | 0.2815 | 81.5 | 88.0 |
| 2026-05-20 | Y. Kabbaj - T. Maria | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.1875 | 0.3195 | 84.5 | 91.7 |
| 2026-05-20 | M. Bassols - Ka. Pliskova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.3125 | 0.2292 | 85.2 | 88.1 |
| 2026-05-20 | P. Kudermetova - V. Tomova | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.4125 | 0.3708 | 74.6 | 82.0 |
| 2026-05-21 | I. Ivashka - A. Hernandez | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.15 | 0.3778 | 80.6 | 90.9 |
| 2026-05-21 | J. De Jong - M. Zheng | OVER 20.5 games | 1.8 | win | 0.8 | 20.5 | 0.3403 | 0.5416 | 72.2 | 88.9 |
| 2026-05-21 | P. Makk - D. Milanovic | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.2381 | 0.2738 | 81.8 | 84.2 |
| 2026-05-21 | D. Svrcina - T. Faurel | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.2222 | 0.3056 | 82.0 | 91.7 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 22.5 games | 2.06 | win | 1.06 | 22.5 | 0.4334 | 0.4213 | 86.2 | 87.2 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 21.5 games | 1.8 | win | 0.8 | 21.5 | 0.4236 | 0.3739 | 74.5 | 89.2 |
| 2026-05-22 | Dar. Blanch - L. Pavlovic | UNDER 22.5 games | 1.95 | win | 0.95 | 22.5 | 0.2666 | 0.3509 | 77.1 | 90.9 |
| 2026-05-22 | R. Sramkova - M. L. Carle | OVER 20.5 games | 1.97 | win | 0.97 | 20.5 | 0.4833 | 0.3667 | 91.6 | 92.5 |
| 2026-05-24 | N. Vukadin - M. Kasnikowski | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.1805 | 0.3067 | 80.1 | 86.5 |
| 2026-05-24 | A. Kubareva - L. Petretic | UNDER 19.5 games | 2.02 | loss | -1.0 | 19.5 | 0.2 | 0.2666 | 76.4 | 87.7 |
| 2026-05-24 | L. Vujovic - M. Mettraux | UNDER 19.5 games | 1.97 | loss | -1.0 | 19.5 | 0.25 | 0.2083 | 74.7 | 88.5 |
| 2026-05-24 | S. Kraus - B. Bencic | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.2777 | 0.2871 | 86.7 | 92.5 |
| 2026-05-25 | L. Samsonova - J. Teichmann | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.1736 | 0.382 | 87.0 | 86.4 |
| 2026-05-25 | T. Gibson - Y. Putintseva | UNDER 20.5 games | 2.02 | loss | -1.0 | 20.5 | 0.3611 | 0.3774 | 82.5 | 91.7 |
| 2026-05-26 | I. Jovic - A. Eala | OVER 20.5 games | 1.9 | loss | -1.0 | 20.5 | 0.35 | 0.4646 | 74.2 | 82.4 |
| 2026-05-26 | L. Siegemund - N. Osaka | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.15 | 0.4 | 87.4 | 86.1 |
| 2026-05-26 | T. Berkieta - S. Kopp | OVER 20.5 games | 1.88 | win | 0.88 | 20.5 | 0.4428 | 0.425 | 79.8 | 90.5 |
| 2026-05-27 | F. Jones - M. Bouzkova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.1666 | 0.3175 | 82.7 | 87.3 |
| 2026-05-27 | T. Zink - R. Hohmann | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.3541 | 0.4757 | 78.8 | 89.2 |
| 2026-05-29 | P. Lovric - J. Adams | UNDER 19.5 games | 2.01 | loss | -1.0 | 19.5 | 0.2125 | 0.3938 | 74.1 | 87.7 |
| 2026-05-29 | J. Teichmann - K. Muchova | UNDER 18.5 games | 2.12 | loss | -1.0 | 18.5 | 0.2291 | 0.3889 | 81.2 | 82.3 |
| 2026-05-29 | S. Sierra - S. Cirstea | UNDER 20.5 games | 1.99 | win | 0.99 | 20.5 | 0.365 | 0.2818 | 73.8 | 84.6 |

## V2 breakdowns

### By tour level

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| atp | 18 | 14 | 4 | 77.78% | 10.91u | 60.61% | 2.0628 |
| wta | 15 | 9 | 5 | 64.29% | 4.39u | 29.27% | 2.064 |
| itf | 2 | 1 | 1 | 50.0% | 0.05u | 2.5% | 2.095 |
| challenger | 31 | 13 | 16 | 44.83% | -1.94u | -6.26% | 2.0877 |

### By gender

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| men | 49 | 27 | 20 | 57.45% | 9.05u | 18.47% | 2.0806 |
| women | 17 | 10 | 6 | 62.5% | 4.36u | 25.65% | 2.0618 |

### By line bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20.5 - 21.5 | 29 | 17 | 11 | 60.71% | 7.12u | 24.55% | 2.0755 |
| 19.5 - 20.5 | 37 | 20 | 15 | 57.14% | 6.29u | 17.0% | 2.0759 |

### By odds bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1.95 - 2.05 | 31 | 21 | 9 | 70.0% | 12.33u | 39.77% | 2.0168 |
| 2.05 - 2.2 | 35 | 16 | 17 | 48.48% | 1.08u | 3.09% | 2.128 |

### By confidence bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 89 - 92 | 23 | 15 | 7 | 68.18% | 8.37u | 36.39% | 2.0265 |
| 83 - 86 | 14 | 8 | 4 | 66.67% | 5.13u | 36.64% | 2.1436 |
| > 92 | 4 | 4 | 0 | 100.0% | 4.1u | 102.5% | 2.025 |
| 86 - 89 | 25 | 10 | 15 | 40.0% | -4.19u | -16.76% | 2.0912 |

### By quality bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 80 - 84 | 29 | 20 | 7 | 74.07% | 14.59u | 50.31% | 2.0831 |
| 76 - 80 | 23 | 11 | 11 | 50.0% | 0.16u | 0.7% | 2.0361 |
| 84 - 88 | 14 | 6 | 8 | 42.86% | -1.34u | -9.57% | 2.1257 |

### By market gap bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.35 | 31 | 18 | 12 | 60.0% | 7.4u | 23.87% | 2.0894 |
| 0.35 - 0.45 | 18 | 11 | 6 | 64.71% | 5.69u | 31.61% | 2.0767 |
| 0.45 - 0.6 | 17 | 8 | 8 | 50.0% | 0.32u | 1.88% | 2.05 |

### By strength gap bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5 - 10 | 12 | 9 | 3 | 75.0% | 6.73u | 56.08% | 2.0967 |
| 25 - 30 | 13 | 8 | 5 | 61.54% | 3.76u | 28.92% | 2.0938 |
| 20 - 25 | 15 | 8 | 6 | 57.14% | 2.44u | 16.27% | 2.076 |
| <= 5 | 10 | 6 | 4 | 60.0% | 2.41u | 24.1% | 2.068 |
| 10 - 15 | 9 | 4 | 4 | 50.0% | 0.1u | 1.11% | 2.0667 |
| 15 - 20 | 7 | 2 | 4 | 33.33% | -2.03u | -29.0% | 2.0286 |

### By avg three set bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.3 | 10 | 7 | 2 | 77.78% | 5.44u | 54.4% | 2.094 |
| 0.2 - 0.25 | 23 | 13 | 9 | 59.09% | 4.94u | 21.48% | 2.067 |
| 0.3 - 0.35 | 7 | 5 | 2 | 71.43% | 3.07u | 43.86% | 2.0386 |
| 0.15 - 0.2 | 14 | 8 | 6 | 57.14% | 2.59u | 18.5% | 2.075 |
| <= 0.15 | 12 | 4 | 7 | 36.36% | -2.63u | -21.92% | 2.1 |

### By avg close set bucket

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.4 | 29 | 16 | 12 | 57.14% | 4.98u | 17.17% | 2.0766 |
| 0.2 - 0.3 | 12 | 7 | 3 | 70.0% | 4.47u | 37.25% | 2.0883 |
| 0.4 - 0.5 | 24 | 13 | 11 | 54.17% | 2.87u | 11.96% | 2.0679 |
| <= 0.2 | 1 | 1 | 0 | 100.0% | 1.09u | 109.0% | 2.09 |

### By bookmaker

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pncl | 31 | 17 | 12 | 58.62% | 6.34u | 20.45% | 2.089 |
| Betano | 19 | 11 | 8 | 57.89% | 3.85u | 20.26% | 2.0774 |
| Unibet | 7 | 4 | 2 | 66.67% | 2.18u | 31.14% | 2.0829 |
| 1xBet | 1 | 1 | 0 | 100.0% | 1.02u | 102.0% | 2.02 |
| Superbet | 1 | 1 | 0 | 100.0% | 1.02u | 102.0% | 2.02 |
| Betfair | 6 | 3 | 3 | 50.0% | 0.0u | 0.0% | 2.0 |
| Marathon | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |

### By tournament

| Group | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hamburg | 5 | 5 | 0 | 100.0% | 5.24u | 104.8% | 2.048 |
| French Open | 18 | 11 | 7 | 61.11% | 4.65u | 25.83% | 2.0683 |
| Geneva | 4 | 4 | 0 | 100.0% | 4.24u | 106.0% | 2.06 |
| Tunis | 3 | 3 | 0 | 100.0% | 3.14u | 104.67% | 2.0467 |
| Bordeaux | 2 | 2 | 0 | 100.0% | 2.38u | 119.0% | 2.19 |
| Zagreb | 2 | 2 | 0 | 100.0% | 2.3u | 115.0% | 2.15 |
| Istanbul (Turkey) - Qualification | 2 | 2 | 0 | 100.0% | 2.0u | 100.0% | 2.0 |
| Rome | 5 | 3 | 2 | 60.0% | 1.17u | 23.4% | 2.046 |
| Chisinau | 1 | 1 | 0 | 100.0% | 1.14u | 114.0% | 2.14 |
| Cervia (Italy) - Qualification | 1 | 1 | 0 | 100.0% | 1.0u | 100.0% | 2.0 |
| M25 Troisdorf (Germany) | 2 | 1 | 1 | 50.0% | 0.05u | 2.5% | 2.095 |
| Rabat | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.15 |
| Little Rock | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.18 |
| Francavilla | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.03 |
| Oeiras 6 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.09 |
| Parma | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.12 |
| Kosice | 4 | 1 | 3 | 25.0% | -1.9u | -47.5% | 2.11 |
| Vicenza | 4 | 1 | 3 | 25.0% | -2.0u | -50.0% | 2.08 |
| Bengaluru 3 (India) - Qualification | 3 | 0 | 2 | 0.0% | -2.0u | -66.67% | 2.1033 |
| Centurion (South Africa) - Qualification | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.065 |
| Valencia | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 2.0467 |

## Files generated

- `data/lucija/lucija_v2_backtest_report.md`
- `data/lucija/lucija_v2_backtest_summary.json`
- `data/lucija/lucija_v2_backtest_picks.json`
- `data/lucija/lucija_v2_backtest_blocked_from_v1.json`
- `data/lucija/lucija_v2_backtest_debug.json`


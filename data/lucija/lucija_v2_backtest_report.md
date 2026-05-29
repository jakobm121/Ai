# Lucija Backtest Report

Generated at: **2026-05-29T22:57:14.757612+02:00**

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
  "h2h_max": 0,
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
  "confidence_min": 0,
  "h2h_max": 0,
  "market_gap_min": 0.25,
  "quality_min": 0,
  "strength_gap_max": 30
}
```

### V3 over
```json
{
  "side": "over",
  "avg_close_set_min": 0.35,
  "avg_three_set_min": 0.25,
  "confidence_min": 0,
  "h2h_max": 1,
  "market_gap_max": 0.35,
  "quality_min": 0,
  "strength_gap_max": 35
}
```

## Main comparison

| Model | Picks | Settled | Pending | W | L | Push | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All settled totals | 492 | 492 | 0 | 220 | 239 | 33 | 47.93% | -8.26u | -1.68% | 2.0567 | -42.43u |
| V1 original | 110 | 108 | 2 | 68 | 37 | 3 | 64.76% | 33.49u | 31.01% | 2.0475 | -8.12u |
| V2 under | 64 | 64 | 0 | 38 | 23 | 3 | 62.3% | 17.85u | 27.89% | 2.0792 | -9.03u |
| V3 over | 51 | 50 | 1 | 22 | 22 | 6 | 50.0% | -2.04u | -4.08% | 1.946 | -4.81u |

## Train / test

| Model | Split | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | train_75 | 82 | 82 | 55 | 25 | 68.75% | 31.91u | 38.91% | 2.0418 | -4.9u |
| V1 | test_25 | 28 | 26 | 13 | 12 | 52.0% | 1.58u | 6.08% | 2.0654 | -3.12u |
| V2 | train_75 | 48 | 48 | 28 | 18 | 60.87% | 12.09u | 25.19% | 2.0735 | -9.03u |
| V2 | test_25 | 16 | 16 | 10 | 5 | 66.67% | 5.76u | 36.0% | 2.0962 | -2.0u |
| V3 | train_75 | 38 | 38 | 17 | 17 | 50.0% | -1.47u | -3.87% | 1.9458 | -4.39u |
| V3 | test_25 | 13 | 12 | 5 | 5 | 50.0% | -0.57u | -4.75% | 1.9467 | -3.07u |

## V1 original selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | L. Pigossi - L. Cortez Llorca | OVER 20.5 games | 1.87 | win | 0.87 | 20.5 | 0.35 | 0.4083 | 0.2585 | 18.9 |
| 2026-05-05 | M. Krumich - G. Piraino | OVER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.5786 | 0.3703 | 0.4572 | 17.69 |
| 2026-05-05 | A. Li - S. Zhang | UNDER 19.5 games | 2.15 | loss | -1.0 | 19.5 | 0.2167 | 0.3223 | 0.4751 | 18.35 |
| 2026-05-06 | T. Townsend - N. Brancaccio | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.254 | 0.2976 | 0.4895 | 23.58 |
| 2026-05-06 | N. Basiletti - A. Tomljanovic | OVER 20.5 games | 2.15 | win | 1.15 | 20.5 | 0.4778 | 0.4315 | 0.5697 | 0.17 |
| 2026-05-07 | D. Shapovalov - M. Navone | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.3333 | 0.4167 | 0.2791 | 26.89 |
| 2026-05-08 | A. Tubello - P. Kudermetova | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4778 | 0.3417 | 0.3597 | 2.6 |
| 2026-05-08 | L. Pigossi - G. Maristany | OVER 20.5 games | 1.98 | loss | -1.0 | 20.5 | 0.45 | 0.4667 | 0.3893 | 23.7 |
| 2026-05-08 | D. Vekic - M. Ristic | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.2125 | 0.3542 | 0.4707 | 14.48 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 0.285 | 3.78 |
| 2026-05-08 | B. Van De Zandschulp - A. Kovacevic | UNDER 21.5 games | 2.14 | win | 1.14 | 21.5 | 0.1875 | 0.4062 | 0.5035 | 28.25 |
| 2026-05-08 | T. C. Grant - V. Mboko | UNDER 19.5 games | 2.14 | push | 0.0 | 19.5 | 0.1875 | 0.3229 | 0.4802 | 16.45 |
| 2026-05-08 | J. Pegula - Z. Sonmez | UNDER 19.5 games | 2.03 | win | 1.03 | 19.5 | 0.3111 | 0.3019 | 0.5758 | 6.45 |
| 2026-05-09 | D. Vekic - G. Maristany | UNDER 19.5 games | 2.13 | win | 1.13 | 19.5 | 0.15 | 0.4584 | 0.4767 | 14.6 |
| 2026-05-09 | G. Heide - A. Holmgren | UNDER 20.5 games | 2.03 | loss | -1.0 | 20.5 | 0.1736 | 0.4896 | 0.5504 | 18.32 |
| 2026-05-09 | O. Oliynykova - L. Noskova | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.325 | 0.3729 | 0.4835 | 23.12 |
| 2026-05-09 | T. M. Etcheverry - M. Bellucci | UNDER 21.5 games | 2.05 | loss | -1.0 | 21.5 | 0.3493 | 0.4828 | 0.4543 | 24.23 |
| 2026-05-09 | H. Medjedovic - J. Fonseca | UNDER 22.5 games | 1.99 | win | 0.99 | 22.5 | 0.2847 | 0.3947 | 0.2536 | 16.03 |
| 2026-05-09 | M. Pucinelli de Almeida - F. Roncadelli | UNDER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.4072 | 0.3571 | 0.299 | 26.51 |
| 2026-05-10 | M. Keys - N. Bartunkova | OVER 20.5 games | 1.98 | win | 0.98 | 20.5 | 0.575 | 0.3084 | 0.4488 | 8.78 |
| 2026-05-10 | D. Vekic - M. Timofeeva | UNDER 20.5 games | 1.97 | win | 0.97 | 20.5 | 0.225 | 0.4146 | 0.3241 | 18.9 |
| 2026-05-11 | E. Mertens - M. Andreeva | UNDER 20.5 games | 1.96 | win | 0.96 | 20.5 | 0.2429 | 0.2631 | 0.433 | 7.3 |
| 2026-05-11 | N. McDonald - D. Glinka | UNDER 21.5 games | 2.07 | win | 1.07 | 21.5 | 0.1736 | 0.3588 | 0.256 | 7.03 |
| 2026-05-11 | G. Den Ouden - D. Added | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.275 | 0.4416 | 0.4288 | 9.32 |
| 2026-05-11 | P. Llamas Ruiz - D. Medvedev | OVER 20.5 games | 1.9 | win | 0.9 | 20.5 | 0.4732 | 0.3541 | 0.3695 | 16.14 |
| 2026-05-11 | L. Draxl - E. Nava | UNDER 20.5 games | 2.09 | loss | -1.0 | 20.5 | 0.2083 | 0.3646 | 0.4955 | 15.55 |
| 2026-05-12 | K. Birrell - K. Boulter | OVER 19.5 games | 1.83 | win | 0.83 | 19.5 | 0.4822 | 0.3215 | 0.4625 | 3.95 |
| 2026-05-12 | K. Khachanov - D. Prizmic | UNDER 22.5 games | 2.05 | win | 1.05 | 22.5 | 0.2083 | 0.4479 | 0.2806 | 25.88 |
| 2026-05-12 | C. Garin - L. Midon | OVER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.6072 | 0.4702 | 0.6423 | 2.04 |
| 2026-05-12 | L. Darderi - A. Zverev | UNDER 21.5 games | 2.01 | loss | -1.0 | 21.5 | 0.2222 | 0.3148 | 0.594 | 22.0 |
| 2026-05-12 | P. Martin Tiffon - C. Broom | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1667 | 0.3333 | 0.5662 | 2.78 |
| 2026-05-12 | J. B. Torres - B. Fernandez | UNDER 19.5 games | 2.0 | loss | -1.0 | 19.5 | 0.2611 | 0.3491 | 0.6325 | 25.81 |
| 2026-05-13 | R. Jodar - L. Darderi | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.3611 | 0.2963 | 0.3546 | 24.51 |
| 2026-05-14 | J. Reis Da Silva - E. Moller | UNDER 20.5 games | 2.18 | win | 1.18 | 20.5 | 0.2625 | 0.2437 | 0.3466 | 26.38 |
| 2026-05-14 | D. Salkova - C. Osorio | UNDER 19.5 games | 2.05 | loss | -1.0 | 19.5 | 0.1805 | 0.2372 | 0.5207 | 9.83 |
| 2026-05-14 | D. Dedura - L. Neumayer | UNDER 20.5 games | 2.12 | win | 1.12 | 20.5 | 0.2361 | 0.2291 | 0.2667 | 29.38 |
| 2026-05-15 | R. Collignon - T. Droguet | UNDER 21.5 games | 2.19 | win | 1.19 | 21.5 | 0.2143 | 0.3453 | 0.3191 | 7.86 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 0.3448 | 13.95 |
| 2026-05-16 | I. Buse - N. McDonald | UNDER 18.5 games | 2.03 | win | 1.03 | 18.5 | 0.1805 | 0.316 | 0.7922 | 18.7 |
| 2026-05-16 | M. Topo - H. Gaston | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.1805 | 0.2697 | 0.3171 | 10.05 |
| 2026-05-17 | I. Buse - H. Gaston | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.1875 | 0.2188 | 0.4767 | 14.62 |
| 2026-05-17 | D. Dedura - F. Tiafoe | UNDER 20.5 games | 2.2 | win | 1.2 | 20.5 | 0.1984 | 0.3995 | 0.4357 | 1.02 |
| 2026-05-17 | L. Jeanjean - L. Fernandez | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.3541 | 0.3125 | 0.4974 | 12.67 |
| 2026-05-17 | M. Kecmanovic - D. Vallejo | UNDER 21.5 games | 2.07 | loss | -1.0 | 21.5 | 0.1667 | 0.4352 | 0.2991 | 24.56 |
| 2026-05-18 | S. Baez - A. Michelsen | UNDER 21.5 games | 2.11 | win | 1.11 | 21.5 | 0.2777 | 0.4074 | 0.2528 | 9.66 |
| 2026-05-18 | S. Shimabukuro - S. Sakellaridis | UNDER 21.5 games | 2.16 | loss | -1.0 | 21.5 | 0.1984 | 0.3717 | 0.4171 | 26.66 |
| 2026-05-18 | D. Altmaier - R. Hijikata | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2143 | 0.3215 | 0.3966 | 8.72 |
| 2026-05-18 | N. Mejia - P. Llamas Ruiz | UNDER 19.5 games | 2.01 | loss | -1.0 | 19.5 | 0.25 | 0.2812 | 0.711 | 22.08 |
| 2026-05-19 | L. Midon - R. Carballes Baena | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.6507 | 0.3651 | 0.3248 | 22.39 |
| 2026-05-19 | Y. Kabbaj - B. Cengiz | OVER 20.5 games | 1.92 | win | 0.92 | 20.5 | 0.4166 | 0.4713 | 0.3308 | 21.23 |
| 2026-05-19 | L. Zaar - J. Bouzas Maneiro | UNDER 19.5 games | 2.06 | win | 1.06 | 19.5 | 0.3222 | 0.2815 | 0.4974 | 16.76 |
| 2026-05-19 | N. Honda - P. Sekulic | UNDER 20.5 games | 2.05 | push | 0.0 | 20.5 | 0.2143 | 0.2262 | 0.5649 | 19.56 |
| 2026-05-19 | B. Hassan - F. C. Jianu | UNDER 20.5 games | 2.03 | win | 1.03 | 20.5 | 0.3 | 0.3167 | 0.3106 | 23.6 |
| 2026-05-19 | P. Kudermetova - A. Koevermans | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.3333 | 0.4352 | 0.3254 | 27.11 |
| 2026-05-20 | T. Faurel - J. Clarke | UNDER 20.5 games | 2.1 | win | 1.1 | 20.5 | 0.2056 | 0.288 | 0.3868 | 21.45 |
| 2026-05-20 | L. Vithoontien - P. Bar Biryukov | UNDER 20.5 games | 2.11 | loss | -1.0 | 20.5 | 0.2 | 0.425 | 0.5894 | 0.9 |
| 2026-05-20 | Y. Kabbaj - T. Maria | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.1875 | 0.3195 | 0.5597 | 26.91 |
| 2026-05-20 | M. Bassols - Ka. Pliskova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.3125 | 0.2292 | 0.5182 | 17.5 |
| 2026-05-20 | N. Budkov Kjaer - T. Gentzsch | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2777 | 0.3334 | 0.4374 | 0.11 |
| 2026-05-20 | P. Kudermetova - V. Tomova | UNDER 20.5 games | 2.05 | loss | -1.0 | 20.5 | 0.4125 | 0.3708 | 0.3254 | 26.22 |
| 2026-05-21 | I. Ivashka - A. Hernandez | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.15 | 0.3778 | 0.6325 | 11.99 |
| 2026-05-21 | J. De Jong - M. Zheng | OVER 20.5 games | 1.8 | win | 0.8 | 20.5 | 0.3403 | 0.5416 | 0.3456 | 7.89 |
| 2026-05-21 | P. Makk - D. Milanovic | UNDER 19.5 games | 2.16 | win | 1.16 | 19.5 | 0.2381 | 0.2738 | 0.4567 | 14.24 |
| 2026-05-21 | A. Galarneau - F. Cina | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2222 | 0.5 | 0.5251 | 14.89 |
| 2026-05-21 | B. Gadamauri - P. Nesterov | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.2361 | 0.4665 | 0.2711 | 1.27 |
| 2026-05-21 | D. Svrcina - T. Faurel | UNDER 19.5 games | 2.0 | win | 1.0 | 19.5 | 0.2222 | 0.3056 | 0.5697 | 28.89 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 22.5 games | 2.06 | win | 1.06 | 22.5 | 0.4334 | 0.4213 | 0.3193 | 0.93 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 21.5 games | 1.8 | win | 0.8 | 21.5 | 0.4236 | 0.3739 | 0.3193 | 0.55 |
| 2026-05-22 | C. Ruud - M. Navone | UNDER 20.5 games | 2.07 | win | 1.07 | 20.5 | 0.2222 | 0.463 | 0.5706 | 23.33 |
| 2026-05-22 | Dar. Blanch - L. Pavlovic | UNDER 22.5 games | 1.95 | win | 0.95 | 22.5 | 0.2666 | 0.3509 | 0.2986 | 21.93 |
| 2026-05-22 | R. Sramkova - M. L. Carle | OVER 20.5 games | 1.97 | win | 0.97 | 20.5 | 0.4833 | 0.3667 | 0.4288 | 0.71 |
| 2026-05-22 | A. Kovacevic - I. Buse | UNDER 21.5 games | 2.02 | win | 1.02 | 21.5 | 0.3055 | 0.3102 | 0.5238 | 27.17 |
| 2026-05-24 | N. Vukadin - M. Kasnikowski | UNDER 19.5 games | 2.12 | win | 1.12 | 19.5 | 0.1805 | 0.3067 | 0.5764 | 4.8 |
| 2026-05-24 | A. Kubareva - L. Petretic | UNDER 19.5 games | 2.02 | loss | -1.0 | 19.5 | 0.2 | 0.2666 | 0.4263 | 0.3 |
| 2026-05-24 | L. Vujovic - M. Mettraux | UNDER 19.5 games | 1.97 | loss | -1.0 | 19.5 | 0.25 | 0.2083 | 0.5191 | 19.4 |
| 2026-05-24 | S. Kraus - B. Bencic | UNDER 19.5 games | 2.05 | win | 1.05 | 19.5 | 0.2777 | 0.2871 | 0.5449 | 12.11 |
| 2026-05-25 | D. Kasatkina - Z. Sonmez | UNDER 20.5 games | 2.05 | win | 1.05 | 20.5 | 0.2111 | 0.2296 | 0.3753 | 14.26 |
| 2026-05-25 | L. Samsonova - J. Teichmann | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.1736 | 0.382 | 0.4974 | 11.28 |
| 2026-05-25 | M. Dhamne - F. Ferreira Silva | UNDER 20.5 games | 2.12 | loss | -1.0 | 20.5 | 0.275 | 0.3584 | 0.3067 | 14.52 |
| 2026-05-25 | T. Boyer - M. Damas | UNDER 21.5 games | 2.0 | loss | -1.0 | 21.5 | 0.25 | 0.4584 | 0.3128 | 19.7 |
| 2026-05-25 | T. Gibson - Y. Putintseva | UNDER 20.5 games | 2.02 | loss | -1.0 | 20.5 | 0.3611 | 0.3774 | 0.4442 | 25.14 |
| 2026-05-25 | P. Zahraj - G. Hussey | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.2111 | 0.3361 | 0.3128 | 6.09 |
| 2026-05-25 | H. Guo - M. Kessler | UNDER 20.5 games | 2.0 | loss | -1.0 | 20.5 | 0.2381 | 0.3915 | 0.4178 | 1.67 |
| 2026-05-26 | E. Navarro - J. Tjen | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.1611 | 0.2639 | 0.4534 | 7.3 |
| 2026-05-26 | I. Jovic - A. Eala | OVER 20.5 games | 1.9 | loss | -1.0 | 20.5 | 0.35 | 0.4646 | 0.4178 | 4.98 |
| 2026-05-26 | L. Siegemund - N. Osaka | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.15 | 0.4 | 0.5012 | 8.5 |
| 2026-05-26 | T. Berkieta - S. Kopp | OVER 20.5 games | 1.88 | win | 0.88 | 20.5 | 0.4428 | 0.425 | 0.3473 | 3.79 |
| 2026-05-26 | A. Ruzic - A. Krueger | UNDER 20.5 games | 2.15 | loss | -1.0 | 20.5 | 0.3375 | 0.4021 | 0.2528 | 24.82 |
| 2026-05-26 | M. Brunold - M. Giunta | UNDER 21.5 games | 2.2 | loss | -1.0 | 21.5 | 0.259 | 0.3765 | 0.3128 | 26.62 |
| 2026-05-26 | E. Pridankina - O. Oliynykova | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2611 | 0.3398 | 0.2843 | 24.21 |
| 2026-05-26 | P. Sekulic - M. Krueger | UNDER 21.5 games | 2.18 | push | 0.0 | 21.5 | 0.259 | 0.2843 | 0.3432 | 22.1 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.5 games | 2.02 | win | 1.02 | 20.5 | 0.2222 | 0.3241 | 0.3308 | 25.68 |
| 2026-05-27 | D. Snigur - P. Stearns | UNDER 20.0 games | 2.19 | win | 1.19 | 20.0 | 0.2222 | 0.3241 | 0.3341 | 25.68 |
| 2026-05-27 | F. Jones - M. Bouzkova | UNDER 19.5 games | 2.15 | win | 1.15 | 19.5 | 0.1666 | 0.3175 | 0.5142 | 23.32 |
| 2026-05-27 | T. Zeuch - V. Durasovic | UNDER 21.0 games | 2.05 | win | 1.05 | 21.0 | 0.2611 | 0.4176 | 0.3412 | 9.96 |
| 2026-05-27 | T. Zink - R. Hohmann | UNDER 20.5 games | 2.0 | win | 1.0 | 20.5 | 0.3541 | 0.4757 | 0.5724 | 22.64 |
| 2026-05-27 | L. Neumayer - T. Boyer | UNDER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.3166 | 0.3639 | 0.3688 | 15.7 |
| 2026-05-28 | D. Vekic - N. Osaka | UNDER 20.5 games | 2.06 | loss | -1.0 | 20.5 | 0.2111 | 0.3565 | 0.4534 | 17.86 |
| 2026-05-28 | L. Wessels - V. Durasovic | UNDER 21.5 games | 2.14 | loss | -1.0 | 21.5 | 0.25 | 0.3166 | 0.3091 | 20.7 |
| 2026-05-28 | K. Coppejans - F. Agamenone | UNDER 20.5 games | 2.14 | win | 1.14 | 20.5 | 0.1984 | 0.4167 | 0.3152 | 9.58 |

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
| 2026-05-23 | L. Vujovic - S. Bojica | UNDER 18.5 games | 2.17 | win | 1.17 | 18.5 | 0.1611 | 0.2185 | 0.6248 | 6.65 |
| 2026-05-23 | S. Gulin - L. Gagliardo | UNDER 19.0 games | 2.1 | loss | -1.0 | 19.0 | 0.3143 | 0.2845 | 0.5523 | 22.06 |
| 2026-05-23 | F. Tabacco - N. Tepmahc | UNDER 19.0 games | 2.16 | loss | -1.0 | 19.0 | 0.2125 | 0.2334 | 0.4286 | 11.05 |
| 2026-05-23 | F. Tabacco - N. Tepmahc | UNDER 19.5 games | 1.95 | loss | -1.0 | 19.5 | 0.2125 | 0.2334 | 0.4228 | 11.05 |
| 2026-05-23 | L. Petretic - M. Lazarenko | UNDER 18.5 games | 2.15 | loss | -1.0 | 18.5 | 0.1 | 0.2666 | 0.5041 | 16.8 |
| 2026-05-23 | L. Petretic - M. Lazarenko | UNDER 19.0 games | 2.01 | loss | -1.0 | 19.0 | 0.1 | 0.2666 | 0.5598 | 16.8 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 21.5 games | 2.15 | loss | -1.0 | 21.5 | 0.1125 | 0.2521 | 0.3487 | 5.62 |
| 2026-05-23 | I. Ivashka - P. Bar Biryukov | UNDER 22.0 games | 2.05 | loss | -1.0 | 22.0 | 0.1125 | 0.2521 | 0.3466 | 5.62 |
| 2026-05-23 | U. Hrabavets - O. Danilova | UNDER 19.0 games | 1.97 | win | 0.97 | 19.0 | 0.3222 | 0.3453 | 0.5058 | 4.49 |
| 2026-05-23 | G. Blancaneaux - C. Denolly | UNDER 19.5 games | 2.17 | loss | -1.0 | 19.5 | 0.127 | 0.3359 | 0.4038 | 24.39 |
| 2026-05-23 | S. Giamichelle - G. Ribeiro de Almeida | UNDER 20.0 games | 2.11 | loss | -1.0 | 20.0 | 0.0714 | 0.2262 | 0.3375 | 24.72 |
| 2026-05-23 | S. Giamichelle - G. Ribeiro de Almeida | UNDER 19.5 games | 2.14 | loss | -1.0 | 19.5 | 0.0714 | 0.2262 | 0.3319 | 24.72 |
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
| 2026-05-29 | D. Markovina - D. Ajdukovic | UNDER 18.5 games | 2.15 | win | 1.15 | 18.5 | 0.1625 | 0.2125 | 0.7207 | 22.52 |
| 2026-05-29 | T. Daniel - M. Erhard | UNDER 21.0 games | 2.11 | loss | -1.0 | 21.0 | 0.1714 | 0.2536 | 0.2618 | 1.3 |

## V3 over selected picks

| Date | Match | Bet | Odds | Result | Profit | Line | Avg 3-set | Avg close | Gap | Strength gap |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| 2026-05-05 | L. Pigossi - L. Cortez Llorca | OVER 20.5 games | 1.87 | win | 0.87 | 20.5 | 0.35 | 0.4083 | 0.2585 | 18.9 |
| 2026-05-05 | M. Landaluce - A. Pellegrino | OVER 22.5 games | 1.93 | win | 0.93 | 22.5 | 0.4028 | 0.4259 | 0.1666 | 2.12 |
| 2026-05-06 | Y. Putintseva - T. Valentova | OVER 21.5 games | 1.95 | loss | -1.0 | 21.5 | 0.4018 | 0.4539 | 0.1288 | 9.17 |
| 2026-05-07 | C. Garin - J. M. Cerundolo | OVER 22.5 games | 1.9 | win | 0.9 | 22.5 | 0.4 | 0.4917 | 0.0518 | 13.3 |
| 2026-05-07 | L. Sonego - I. Buse | OVER 22.5 games | 1.94 | loss | -1.0 | 22.5 | 0.5238 | 0.4385 | 0.1995 | 7.1 |
| 2026-05-07 | Z. Bergs - T. Atmane | OVER 22.5 games | 1.95 | loss | -1.0 | 22.5 | 0.3375 | 0.525 | 0.1188 | 5.32 |
| 2026-05-08 | A. Potapova - K. Muchova | OVER 21.5 games | 2.02 | loss | -1.0 | 21.5 | 0.5 | 0.4074 | 0.285 | 3.78 |
| 2026-05-08 | I. Vasa - F. Ribero | OVER 21.5 games | 1.84 | win | 0.84 | 21.5 | 0.4375 | 0.423 | 0.1492 | 19.6 |
| 2026-05-08 | D. Prizmic - N. Djokovic | OVER 21.5 games | 1.83 | win | 0.83 | 21.5 | 0.3958 | 0.4236 | 0.2821 | 4.62 |
| 2026-05-11 | M. Navone - H. Medjedovic | OVER 22.5 games | 1.96 | win | 0.96 | 22.5 | 0.275 | 0.4667 | 0.1443 | 3.32 |
| 2026-05-11 | A. Fery - V. Sachko | OVER 22.5 games | 2.0 | loss | -1.0 | 22.5 | 0.4732 | 0.5416 | 0.0992 | 11.96 |
| 2026-05-12 | T. Monteiro - A. Andrade | OVER 21.5 games | 1.8 | push | 0.0 | 21.5 | 0.3889 | 0.4352 | 0.1645 | 21.56 |
| 2026-05-12 | T. Seyboth Wild - D. E. Galan | OVER 22.5 games | 2.04 | loss | -1.0 | 22.5 | 0.5715 | 0.5476 | 0.1226 | 16.0 |
| 2026-05-12 | K. Coppejans - E. Butvilas | OVER 21.5 games | 1.79 | win | 0.79 | 21.5 | 0.325 | 0.5063 | 0.0322 | 12.45 |
| 2026-05-12 | Y. Yuan - M. Sherif | OVER 20.5 games | 1.9 | win | 0.9 | 20.5 | 0.4111 | 0.3713 | 0.1336 | 13.98 |
| 2026-05-13 | L. Midon - B. Hassan | OVER 21.5 games | 1.84 | win | 0.84 | 21.5 | 0.5285 | 0.4178 | 0.15 | 18.55 |
| 2026-05-14 | K. Smith - O. Milic | OVER 22.5 games | 1.87 | loss | -1.0 | 22.5 | 0.4653 | 0.5741 | 0.0479 | 9.79 |
| 2026-05-14 | K. Smith - O. Milic | OVER 23.5 games | 2.17 | loss | -1.0 | 23.5 | 0.5 | 0.5729 | 0.0479 | 4.87 |
| 2026-05-14 | T. Droguet - T. Atmane | OVER 23.5 games | 2.04 | push | 0.0 | 23.5 | 0.4732 | 0.4583 | 0.0133 | 18.75 |
| 2026-05-14 | L. Mikrut - C. Rodesch | OVER 21.5 games | 1.83 | loss | -1.0 | 21.5 | 0.4822 | 0.4047 | 0.073 | 4.64 |
| 2026-05-14 | J. Choinski - D. E. Galan | OVER 22.5 games | 1.97 | win | 0.97 | 22.5 | 0.5 | 0.5714 | 0.1535 | 15.0 |
| 2026-05-14 | L. Mikrut - C. Rodesch | OVER 22.5 games | 2.05 | loss | -1.0 | 22.5 | 0.4822 | 0.4047 | 0.073 | 4.64 |
| 2026-05-15 | J. Choinski - A. Fery | OVER 22.5 games | 2.0 | push | 0.0 | 22.5 | 0.5 | 0.5834 | 0.1676 | 13.0 |
| 2026-05-15 | D. Yastremska - J. Bouzas Maneiro | OVER 21.5 games | 1.93 | push | 0.0 | 21.5 | 0.3472 | 0.4398 | 0.0554 | 6.19 |
| 2026-05-16 | O. Selekhmeteva - S. Kenin | OVER 21.5 games | 1.96 | win | 0.96 | 21.5 | 0.4722 | 0.5104 | 0.0514 | 18.72 |
| 2026-05-16 | T. Gibson - E. Lys | OVER 20.5 games | 1.93 | win | 0.93 | 20.5 | 0.4667 | 0.3574 | 0.3448 | 13.95 |
| 2026-05-17 | M. Kessler - O. Selekhmeteva | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.4444 | 0.4259 | 0.0 | 18.44 |
| 2026-05-17 | M. Sakkari - P. Stearns | OVER 21.5 games | 1.98 | loss | -1.0 | 21.5 | 0.375 | 0.5209 | 0.0168 | 4.5 |
| 2026-05-18 | T. Atmane - T. M. Etcheverry | OVER 22.5 games | 1.93 | loss | -1.0 | 22.5 | 0.4028 | 0.5081 | 0.297 | 4.22 |
| 2026-05-19 | S. Dostanic - F. Forti | OVER 22.5 games | 2.03 | win | 1.03 | 22.5 | 0.5555 | 0.3518 | 0.0306 | 30.55 |
| 2026-05-19 | L. Midon - R. Carballes Baena | OVER 21.5 games | 2.0 | win | 1.0 | 21.5 | 0.6507 | 0.3651 | 0.3248 | 22.39 |
| 2026-05-19 | Y. Kabbaj - B. Cengiz | OVER 20.5 games | 1.92 | win | 0.92 | 20.5 | 0.4166 | 0.4713 | 0.3308 | 21.23 |
| 2026-05-19 | N. Fatic - L. Mikrut | OVER 22.5 games | 2.08 | loss | -1.0 | 22.5 | 0.3625 | 0.3604 | 0.0229 | 16.9 |
| 2026-05-21 | H. Stewart - O. Milic | OVER 22.5 games | 1.97 | loss | -1.0 | 22.5 | 0.4722 | 0.4838 | 0.1627 | 11.44 |
| 2026-05-21 | J. De Jong - M. Zheng | OVER 20.5 games | 1.8 | win | 0.8 | 20.5 | 0.3403 | 0.5416 | 0.3456 | 7.89 |
| 2026-05-21 | M. Navone - J. Munar | OVER 22.5 games | 2.1 | loss | -1.0 | 22.5 | 0.3333 | 0.4722 | 0.0277 | 2.0 |
| 2026-05-21 | P. Marcinko - J. Bouzas Maneiro | OVER 20.5 games | 1.85 | loss | -1.0 | 20.5 | 0.35 | 0.45 | 0.2101 | 7.0 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 22.5 games | 2.06 | win | 1.06 | 22.5 | 0.4334 | 0.4213 | 0.3193 | 0.93 |
| 2026-05-21 | A. Kovacevic - C. Ugo Carabelli | OVER 21.5 games | 1.8 | win | 0.8 | 21.5 | 0.4236 | 0.3739 | 0.3193 | 0.55 |
| 2026-05-22 | K. Zavatska - L. Bronzetti | OVER 21.5 games | 2.06 | push | 0.0 | 21.5 | 0.4583 | 0.4502 | 0.1767 | 9.39 |
| 2026-05-24 | E. Dalla Valle - F. Forti | OVER 22.5 games | 2.0 | loss | -1.0 | 22.5 | 0.3555 | 0.4926 | 0.0635 | 16.3 |
| 2026-05-24 | M. Frech - G. Ruse | OVER 21.5 games | 1.96 | push | 0.0 | 21.5 | 0.6459 | 0.4016 | 0.1825 | 21.29 |
| 2026-05-25 | T. Berkieta - D. Rapagnetta | OVER 21.5 games | 1.91 | win | 0.91 | 21.5 | 0.35 | 0.3833 | 0.078 | 1.4 |
| 2026-05-26 | T. Berkieta - S. Kopp | OVER 20.5 games | 1.88 | win | 0.88 | 20.5 | 0.4428 | 0.425 | 0.3473 | 3.79 |
| 2026-05-26 | L. Midon - J. Reis Da Silva | OVER 22.5 games | 2.07 | loss | -1.0 | 22.5 | 0.6285 | 0.4678 | 0.0651 | 7.28 |
| 2026-05-27 | T. Lukas - W. Ewald | OVER 20.5 games | 1.94 | loss | -1.0 | 20.5 | 0.4 | 0.4917 | 0.3076 | 3.3 |
| 2026-05-27 | E. Ymer - G. A. Olivieri | OVER 22.5 games | 1.99 | loss | -1.0 | 22.5 | 0.4445 | 0.5834 | 0.0173 | 6.67 |
| 2026-05-27 | J. Teichmann - M. Frech | OVER 21.5 games | 1.93 | win | 0.93 | 21.5 | 0.4445 | 0.4074 | 0.153 | 26.89 |
| 2026-05-28 | I. Jovic - E. Navarro | OVER 21.5 games | 1.91 | loss | -1.0 | 21.5 | 0.4166 | 0.4352 | 0.0444 | 21.88 |
| 2026-05-29 | G. A. Olivieri - L. Nardi | OVER 21.5 games | 1.91 | win | 0.91 | 21.5 | 0.4921 | 0.5542 | 0.3393 | 1.09 |
| 2026-05-29 | E. Cayetano - D. Guzman | OVER 20.5 games | 1.89 | pending | 0.0 | 20.5 | 0.3143 | 0.4035 | 0.1785 | 17.42 |

## V2 under breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| under | 64 | 64 | 38 | 23 | 62.3% | 17.85u | 27.89% | 2.0792 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| wta | 18 | 18 | 15 | 2 | 88.24% | 14.02u | 77.89% | 2.0783 |
| atp | 11 | 11 | 9 | 2 | 81.82% | 7.2u | 65.45% | 2.02 |
| challenger | 14 | 14 | 5 | 7 | 41.67% | -1.46u | -10.43% | 2.095 |
| itf | 21 | 21 | 9 | 12 | 42.86% | -1.91u | -9.1% | 2.1005 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| women | 26 | 26 | 17 | 8 | 68.0% | 10.16u | 39.08% | 2.0712 |
| men | 38 | 38 | 21 | 15 | 58.33% | 7.69u | 20.24% | 2.0847 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 21 | 21 | 16 | 4 | 80.0% | 13.05u | 62.14% | 2.0719 |
| <= 18.5 | 6 | 6 | 4 | 2 | 66.67% | 2.54u | 42.33% | 2.1317 |
| 20.5 - 21.5 | 11 | 11 | 6 | 4 | 60.0% | 2.24u | 20.36% | 2.0755 |
| 18.5 - 19.5 | 25 | 25 | 12 | 12 | 50.0% | 1.02u | 4.08% | 2.0756 |
| 21.5 - 22.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.95 - 2.05 | 30 | 30 | 20 | 9 | 68.97% | 11.34u | 37.8% | 2.0187 |
| 2.05 - 2.2 | 33 | 33 | 18 | 13 | 58.06% | 7.51u | 22.76% | 2.1382 |
| 1.8 - 1.95 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.95 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| > 92 | 5 | 5 | 5 | 0 | 100.0% | 5.15u | 103.0% | 2.03 |
| 86 - 89 | 15 | 15 | 9 | 5 | 64.29% | 4.98u | 33.2% | 2.084 |
| 89 - 92 | 19 | 19 | 11 | 7 | 61.11% | 4.16u | 21.89% | 2.0305 |
| 83 - 86 | 14 | 14 | 8 | 5 | 61.54% | 4.05u | 28.93% | 2.1343 |
| <= 80 | 7 | 7 | 4 | 3 | 57.14% | 1.48u | 21.14% | 2.1271 |
| 80 - 83 | 4 | 4 | 1 | 3 | 25.0% | -1.97u | -49.25% | 2.0775 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 - 84 | 23 | 23 | 18 | 3 | 85.71% | 16.29u | 70.83% | 2.0748 |
| 84 - 88 | 10 | 10 | 7 | 2 | 77.78% | 5.74u | 57.4% | 2.113 |
| 72 - 76 | 13 | 13 | 6 | 7 | 46.15% | -0.44u | -3.38% | 2.0954 |
| 76 - 80 | 13 | 13 | 6 | 7 | 46.15% | -0.71u | -5.46% | 2.0615 |
| > 88 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| <= 72 | 4 | 4 | 1 | 3 | 25.0% | -2.03u | -50.75% | 2.0075 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.45 - 0.6 | 28 | 28 | 19 | 7 | 73.08% | 13.45u | 48.04% | 2.0743 |
| 0.35 - 0.45 | 14 | 14 | 8 | 6 | 57.14% | 2.3u | 16.43% | 2.0536 |
| 0.25 - 0.35 | 16 | 16 | 8 | 7 | 53.33% | 1.75u | 10.94% | 2.1113 |
| > 0.6 | 6 | 6 | 3 | 3 | 50.0% | 0.35u | 5.83% | 2.0767 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 - 30 | 8 | 8 | 7 | 1 | 87.5% | 6.58u | 82.25% | 2.0725 |
| 5 - 10 | 13 | 13 | 9 | 4 | 69.23% | 5.75u | 44.23% | 2.0885 |
| 10 - 15 | 8 | 8 | 6 | 2 | 75.0% | 4.31u | 53.87% | 2.0525 |
| <= 5 | 8 | 8 | 5 | 3 | 62.5% | 2.2u | 27.5% | 2.0475 |
| 20 - 25 | 16 | 16 | 7 | 8 | 46.67% | -0.35u | -2.19% | 2.1006 |
| 15 - 20 | 11 | 11 | 4 | 5 | 44.44% | -0.64u | -5.82% | 2.0845 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.15 - 0.2 | 14 | 14 | 10 | 3 | 76.92% | 7.71u | 55.07% | 2.0736 |
| 0.25 - 0.3 | 8 | 8 | 6 | 1 | 85.71% | 5.44u | 68.0% | 2.0775 |
| 0.3 - 0.35 | 6 | 6 | 5 | 1 | 83.33% | 4.23u | 70.5% | 2.055 |
| 0.2 - 0.25 | 22 | 22 | 12 | 9 | 57.14% | 3.92u | 17.82% | 2.0732 |
| <= 0.15 | 14 | 14 | 5 | 9 | 35.71% | -3.45u | -24.64% | 2.1057 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.35 | 27 | 27 | 19 | 7 | 73.08% | 13.03u | 48.26% | 2.0681 |
| 0.2 - 0.3 | 36 | 36 | 18 | 16 | 52.94% | 3.73u | 10.36% | 2.0872 |
| <= 0.2 | 1 | 1 | 1 | 0 | 100.0% | 1.09u | 109.0% | 2.09 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19 - 20 | 23 | 23 | 15 | 7 | 68.18% | 9.29u | 40.39% | 2.0809 |
| 20 - 21 | 12 | 12 | 10 | 2 | 83.33% | 8.41u | 70.08% | 2.0542 |
| <= 18 | 4 | 4 | 2 | 2 | 50.0% | 0.2u | 5.0% | 2.1125 |
| 18 - 19 | 25 | 25 | 11 | 12 | 47.83% | -0.05u | -0.2% | 2.0844 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 - 0.4 | 11 | 11 | 10 | 1 | 90.91% | 9.6u | 87.27% | 2.0636 |
| 0.2 - 0.3 | 28 | 28 | 15 | 10 | 60.0% | 6.09u | 21.75% | 2.0757 |
| <= 0.2 | 24 | 24 | 13 | 11 | 54.17% | 3.16u | 13.17% | 2.0937 |
| 0.4 - 0.5 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pncl | 26 | 26 | 19 | 5 | 79.17% | 15.74u | 60.54% | 2.0865 |
| Unibet | 4 | 4 | 3 | 0 | 100.0% | 3.18u | 79.5% | 2.09 |
| Betfair | 3 | 3 | 3 | 0 | 100.0% | 3.0u | 100.0% | 2.0 |
| Superbet | 7 | 7 | 4 | 3 | 57.14% | 1.29u | 18.43% | 2.0543 |
| Betano | 10 | 10 | 5 | 5 | 50.0% | 0.35u | 3.5% | 2.08 |
| 1xBet | 11 | 11 | 4 | 7 | 36.36% | -2.71u | -24.64% | 2.08 |
| Marathon | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 2.1333 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| French Open | 15 | 15 | 13 | 2 | 86.67% | 11.86u | 79.07% | 2.0647 |
| Hamburg | 5 | 5 | 5 | 0 | 100.0% | 5.07u | 101.4% | 2.014 |
| Zagreb | 2 | 2 | 2 | 0 | 100.0% | 2.3u | 115.0% | 2.15 |
| Rabat | 2 | 2 | 2 | 0 | 100.0% | 2.11u | 105.5% | 2.055 |
| M15 Maringa 2 (Brazil) | 5 | 5 | 3 | 2 | 60.0% | 1.4u | 28.0% | 2.13 |
| Bordeaux | 1 | 1 | 1 | 0 | 100.0% | 1.19u | 119.0% | 2.19 |
| M15 Doboj | 1 | 1 | 1 | 0 | 100.0% | 1.16u | 116.0% | 2.16 |
| M25 Bol 2 | 1 | 1 | 1 | 0 | 100.0% | 1.15u | 115.0% | 2.15 |
| Rome | 6 | 6 | 3 | 2 | 60.0% | 1.15u | 19.17% | 2.075 |
| M15 Kayseri | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| M25 Bol | 1 | 1 | 1 | 0 | 100.0% | 1.12u | 112.0% | 2.12 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Geneva | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Tunis | 1 | 1 | 1 | 0 | 100.0% | 1.02u | 102.0% | 2.02 |
| W15 Kursumlijska Banja 2 | 2 | 2 | 1 | 1 | 50.0% | 0.17u | 8.5% | 2.07 |
| Little Rock | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.18 |
| W15 Hurghada 5 (Egypt) | 2 | 2 | 1 | 1 | 50.0% | -0.03u | -1.5% | 2.035 |
| Cordoba 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.0 |
| Parma | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| Valencia | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.05 |
| M15 Kursumlijska Banja 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.1 |
| M25 Deauville | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.17 |
| Centurion (South Africa) - Qualification | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.15 |
| M25 Troisdorf (Germany) | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.14 |
| Kosice | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.11 |
| Bengaluru 3 (India) - Qualification | 3 | 3 | 0 | 2 | 0.0% | -2.0u | -66.67% | 2.0833 |
| M15 Monastir 19 | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.055 |
| W15 Monastir 14 | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 2.06 |

## V3 over breakdowns

### By side

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| over | 51 | 50 | 22 | 22 | 50.0% | -2.04u | -4.08% | 1.946 |

### By tour level

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| atp | 13 | 13 | 8 | 5 | 61.54% | 2.28u | 17.54% | 1.9446 |
| itf | 2 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.94 |
| challenger | 24 | 24 | 10 | 10 | 50.0% | -1.06u | -4.42% | 1.9458 |
| wta | 12 | 12 | 4 | 6 | 40.0% | -2.26u | -18.83% | 1.9483 |

### By gender

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| men | 34 | 34 | 16 | 15 | 51.61% | -0.55u | -1.62% | 1.9494 |
| women | 17 | 16 | 6 | 7 | 46.15% | -1.49u | -9.31% | 1.9387 |

### By line bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 19.5 - 20.5 | 9 | 8 | 6 | 2 | 75.0% | 3.3u | 41.25% | 1.8862 |
| 20.5 - 21.5 | 20 | 20 | 10 | 6 | 62.5% | 2.81u | 14.05% | 1.908 |
| > 22.5 | 2 | 2 | 0 | 1 | 0.0% | -1.0u | -50.0% | 2.105 |
| 21.5 - 22.5 | 20 | 20 | 6 | 13 | 31.58% | -7.15u | -35.75% | 1.992 |

### By odds bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| <= 1.8 | 4 | 4 | 3 | 0 | 100.0% | 2.39u | 59.75% | 1.7975 |
| 1.8 - 1.95 | 25 | 24 | 13 | 10 | 56.52% | 1.59u | 6.62% | 1.9 |
| 2.05 - 2.2 | 6 | 6 | 1 | 4 | 20.0% | -2.94u | -49.0% | 2.09 |
| 1.95 - 2.05 | 16 | 16 | 5 | 8 | 38.46% | -3.08u | -19.25% | 1.9981 |

### By confidence bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 86 - 89 | 9 | 9 | 5 | 2 | 71.43% | 2.48u | 27.56% | 1.8978 |
| 83 - 86 | 7 | 7 | 4 | 2 | 66.67% | 1.63u | 23.29% | 1.9243 |
| 80 - 83 | 5 | 5 | 2 | 2 | 50.0% | -0.17u | -3.4% | 1.948 |
| 89 - 92 | 4 | 4 | 2 | 2 | 50.0% | -0.32u | -8.0% | 1.9675 |
| <= 80 | 6 | 5 | 2 | 3 | 40.0% | -1.01u | -20.2% | 2.022 |
| > 92 | 20 | 20 | 7 | 11 | 38.89% | -4.65u | -23.25% | 1.9515 |

### By quality bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 76 - 80 | 11 | 11 | 7 | 4 | 63.64% | 2.24u | 20.36% | 1.91 |
| <= 72 | 7 | 6 | 4 | 2 | 66.67% | 1.61u | 26.83% | 1.9383 |
| 80 - 84 | 9 | 9 | 4 | 3 | 57.14% | 0.69u | 7.67% | 1.9311 |
| 72 - 76 | 4 | 4 | 2 | 1 | 66.67% | 0.6u | 15.0% | 1.835 |
| 84 - 88 | 9 | 9 | 3 | 5 | 37.5% | -2.08u | -23.11% | 2.0122 |
| > 88 | 11 | 11 | 2 | 7 | 22.22% | -5.1u | -46.36% | 1.9845 |

### By market gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.35 | 13 | 13 | 10 | 3 | 76.92% | 6.0u | 46.15% | 1.9146 |
| 0.2 - 0.25 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.85 |
| <= 0.2 | 37 | 36 | 12 | 18 | 40.0% | -7.04u | -19.56% | 1.96 |

### By strength gap bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 - 15 | 8 | 8 | 5 | 2 | 71.43% | 2.49u | 31.13% | 1.9325 |
| 30 - 35 | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| 25 - 30 | 1 | 1 | 1 | 0 | 100.0% | 0.93u | 93.0% | 1.93 |
| 20 - 25 | 5 | 5 | 2 | 1 | 66.67% | 0.92u | 18.4% | 1.918 |
| 15 - 20 | 10 | 9 | 4 | 4 | 50.0% | -0.49u | -5.44% | 1.9533 |
| <= 5 | 16 | 16 | 8 | 8 | 50.0% | -0.72u | -4.5% | 1.9563 |
| 5 - 10 | 10 | 10 | 1 | 7 | 12.5% | -6.2u | -62.0% | 1.941 |

### By avg three set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 - 0.3 | 1 | 1 | 1 | 0 | 100.0% | 0.96u | 96.0% | 1.96 |
| 0.3 - 0.35 | 9 | 8 | 4 | 3 | 57.14% | 0.37u | 4.62% | 1.9 |
| 0.35 - 0.45 | 20 | 20 | 10 | 9 | 52.63% | -0.01u | -0.05% | 1.924 |
| > 0.45 | 21 | 21 | 7 | 10 | 41.18% | -3.36u | -16.0% | 1.9838 |

### By avg close set bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.35 - 0.4 | 7 | 7 | 6 | 1 | 85.71% | 4.57u | 65.29% | 1.95 |
| 0.4 - 0.5 | 30 | 29 | 11 | 13 | 45.83% | -3.04u | -10.48% | 1.941 |
| 0.5 - 0.6 | 14 | 14 | 5 | 8 | 38.46% | -3.57u | -25.5% | 1.9543 |

### By avg total games bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 21 - 22 | 13 | 13 | 8 | 3 | 72.73% | 4.12u | 31.69% | 1.9185 |
| 20 - 21 | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| > 23 | 16 | 16 | 7 | 7 | 50.0% | -0.35u | -2.19% | 1.9825 |
| 22 - 23 | 21 | 21 | 7 | 12 | 36.84% | -5.81u | -27.67% | 1.9352 |

### By avg over 21.5 rate bucket

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 - 0.6 | 15 | 15 | 7 | 6 | 53.85% | 0.58u | 3.87% | 1.968 |
| 0.4 - 0.5 | 24 | 24 | 11 | 10 | 52.38% | -0.33u | -1.38% | 1.9154 |
| > 0.6 | 6 | 6 | 2 | 3 | 40.0% | -1.03u | -17.17% | 2.0067 |
| 0.3 - 0.4 | 6 | 5 | 2 | 3 | 40.0% | -1.26u | -25.2% | 1.954 |

### By bookmaker

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1xBet | 3 | 3 | 3 | 0 | 100.0% | 2.74u | 91.33% | 1.9133 |
| Betfair | 2 | 2 | 2 | 0 | 100.0% | 1.91u | 95.5% | 1.955 |
| bet365 | 5 | 5 | 3 | 1 | 75.0% | 1.5u | 30.0% | 1.826 |
| Pncl | 29 | 28 | 12 | 12 | 50.0% | -0.85u | -3.04% | 1.9636 |
| Unibet | 4 | 4 | 1 | 2 | 33.33% | -1.21u | -30.25% | 1.955 |
| Superbet | 3 | 3 | 0 | 3 | 0.0% | -3.0u | -100.0% | 2.0233 |
| Betano | 5 | 5 | 1 | 4 | 20.0% | -3.13u | -62.6% | 1.93 |

### By tournament

| Group | Picks | Settled | W | L | Winrate | Profit | ROI | Avg odds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kosice | 2 | 2 | 2 | 0 | 100.0% | 1.79u | 89.5% | 1.895 |
| Cervia (Italy) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 1.03u | 103.0% | 2.03 |
| Parma | 2 | 2 | 1 | 0 | 100.0% | 0.9u | 45.0% | 1.915 |
| Istanbul (Turkey) - Qualification | 1 | 1 | 1 | 0 | 100.0% | 0.87u | 87.0% | 1.87 |
| Hamburg | 3 | 3 | 2 | 1 | 66.67% | 0.86u | 28.67% | 1.93 |
| Brazzaville | 1 | 1 | 1 | 0 | 100.0% | 0.84u | 84.0% | 1.84 |
| Oeiras 6 | 1 | 1 | 1 | 0 | 100.0% | 0.84u | 84.0% | 1.84 |
| Tunis | 1 | 1 | 1 | 0 | 100.0% | 0.79u | 79.0% | 1.79 |
| French Open | 7 | 7 | 3 | 2 | 60.0% | 0.73u | 10.43% | 1.9629 |
| Bordeaux | 1 | 1 | 0 | 0 | 0.0% | 0.0u | 0.0% | 2.04 |
| W35 Wichita, KS | 1 | 0 | 0 | 0 | 0.0% | 0u | 0.0% | 0.0 |
| Rabat | 2 | 2 | 1 | 1 | 50.0% | -0.08u | -4.0% | 1.885 |
| Chisinau | 2 | 2 | 1 | 1 | 50.0% | -0.09u | -4.5% | 1.95 |
| Strasbourg | 4 | 4 | 2 | 2 | 50.0% | -0.11u | -2.75% | 1.945 |
| Rome | 8 | 8 | 4 | 4 | 50.0% | -0.38u | -4.75% | 1.935 |
| Bengaluru 3 (India) - Qualification | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.97 |
| Geneva | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 2.1 |
| W35 Bol 2 | 1 | 1 | 0 | 1 | 0.0% | -1.0u | -100.0% | 1.94 |
| Bengaluru 2 | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.02 |
| Vicenza | 2 | 2 | 0 | 2 | 0.0% | -2.0u | -100.0% | 2.035 |
| Zagreb | 7 | 7 | 1 | 4 | 20.0% | -3.03u | -43.29% | 1.9557 |

## Files generated

- `data/lucija/lucija_v2_backtest_report.md`
- `data/lucija/lucija_v2_backtest_summary.json`
- `data/lucija/lucija_v1_backtest_picks.json`
- `data/lucija/lucija_v2_backtest_picks.json`
- `data/lucija/lucija_v3_over_backtest_picks.json`
- `data/lucija/lucija_v2_backtest_debug.json`

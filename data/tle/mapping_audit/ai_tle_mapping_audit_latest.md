# AI TLE Mapping Audit

Generated: `2026-06-19T11:07:39+00:00`
Date range: `2026-06-19` â `2026-06-19`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 279 |
| api_odds_events | 129 |
| odds_events_with_fixture | 129 |
| audited_events | 50 |
| audited_player_appearances | 100 |
| safe_player_appearances | 94 |
| review_player_appearances | 6 |
| safe_events_both_players | 44 |
| review_events_any_player | 6 |
| safe player % | 94.00% |
| review player % | 6.00% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 1 |
| api_mapping | 90 |
| exact_name | 4 |
| unique_surname_initial | 5 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 52653 | A. Nguyen | women | itf | api_key_unmapped | women:api:52653 |  | 1 | A. Nguyen - M. Castillo Meza | W15 Irvine, CA |
| 4363 | A. Aksu | women | qualifying | unique_surname_initial | women:sackmann:213767 | Ayla Aksu | 1 | J. Vandromme - A. Aksu | Figueira Da Foz (Portugal) - Qualification |
| 69230 | M. Slama | women | itf | unique_surname_initial | women:sackmann:260693 | Mia Slama | 1 | M. Vogt - M. Slama | W15 Dinard |
| 9131 | R. Nijboer | men | itf | unique_surname_initial | men:sackmann:207764 | Ryan Nijboer | 1 | M. De Krom - R. Nijboer | M15 Mungia-Laukariz |
| 39199 | R. Quan | men | itf | unique_surname_initial | men:sackmann:211790 | Rudy Quan | 1 | K. Miyoshi - R. Quan | M15 Irvine, CA |
| 14435 | T. Torres | men | itf | unique_surname_initial | men:sackmann:208426 | Tiago Torres | 1 | T. Torres - J. Echeverria | M25 Lourinha (Portugal) |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-19 | 13:30 | itf | men | M. De Krom - R. Nijboer | api_mapping | unique_surname_initial | review_any_player | 9 |
| 2026-06-19 | 13:30 | itf | men | T. Torres - J. Echeverria | unique_surname_initial | api_mapping | review_any_player | 9 |
| 2026-06-19 | 14:30 | itf | women | M. Vogt - M. Slama | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-19 | 15:15 | qualifying | women | J. Vandromme - A. Aksu | api_mapping | unique_surname_initial | review_any_player | 12 |
| 2026-06-19 | 20:00 | itf | women | A. Nguyen - M. Castillo Meza | api_key_unmapped | api_mapping | review_any_player | 6 |
| 2026-06-19 | 22:30 | itf | men | K. Miyoshi - R. Quan | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-19 | 13:10 | itf | women | A. Ibragimova - L. Nguyen Tan | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-19 | 13:10 | itf | women | L. Encheva - C. Buyukakcay | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 13:15 | itf | women | B. Zeltina - N. Senic | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-19 | 13:15 | itf | women | G. Ce - V. Paganetti | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 13:30 | atp_wta | men | A. Zverev - R. Collignon | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 13:30 | challenger | men | D. Svrcina - G. Heide | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-19 | 13:30 | atp_wta | women | Ka. Pliskova - T. Gibson | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 13:30 | challenger | men | Z. Zhang - O. Virtanen | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-19 | 13:40 | itf | men | J. Kovalik - D. Kuzmanov | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 13:45 | qualifying | women | S. Bandecchi - A. Charaeva | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 14:00 | challenger | men | K. Feldbausch - M. Alcala Gurri | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 14:15 | atp_wta | men | H. Medjedovic - U. Humbert | api_mapping | api_mapping | safe_both_players | 13 |
| 2026-06-19 | 14:15 | qualifying | men | T. Droguet - J. Rodionov | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-19 | 14:30 | itf | women | C. Grignac - M. Maquet | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 14:30 | itf | men | G. Kravchenko - G. La Vela | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 14:45 | atp_wta | men | A. Fery - F. Cerundolo | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 15:00 | atp_wta | men | D. Altmaier - D. Medvedev | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 15:00 | atp_wta | women | J. Bouzas Maneiro - E. Navarro | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 15:30 | atp_wta | women | A. Sabalenka - N. Bartunkova | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 15:30 | itf | men | G. Ferrari - F. Tabacco | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 16:00 | qualifying | women | E. Yaneva - E. Gorgodze | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-19 | 16:00 | itf | men | S. Perez Contri - I. Almazan Valiente | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-19 | 16:00 | itf | men | Y. Kelm - M. Zielinski | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 16:15 | atp_wta | men | T. Paul - A. Davidovich Fokina | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 16:30 | atp_wta | women | A. Li - V. Golubic | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 16:30 | itf | women | A. Vergara Rivera - J. Estevez | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 16:30 | atp_wta | men | F. Tiafoe - F. Auger-Aliassime | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 17:00 | challenger | men | L. Djere - S. Ofner | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 17:30 | atp_wta | women | E. Svitolina - A. Eala | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 17:30 | qualifying | women | T. Rakotomanga Rajaonah - M. Sherif | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-19 | 18:00 | itf | men | A. Fenty - B. Shick | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-19 | 18:00 | itf | men | G. Young - M. Dussault | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 18:00 | itf | men | M. Kudernatsch - M. Malaszszak | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-19 | 18:00 | itf | men | P. De Lange - N. Barsukov | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-19 | 18:30 | challenger | men | D. Rincon - L. van Assche | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-19 | 19:30 | itf | men | A. Martin - D. Popko | exact_name | api_mapping | safe_both_players | 3 |
| 2026-06-19 | 19:30 | itf | men | J.J. Wolf - C. Langmo | exact_name | api_mapping | safe_both_players | 7 |
| 2026-06-19 | 20:00 | itf | women | I. Marton - A. Shcherbinina | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-19 | 20:30 | itf | women | A. Kubareva - E. Milovanovic | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-19 | 21:00 | qualifying | men | C. Huertas Del Pino - J. Estevez | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-19 | 21:00 | itf | women | V. Miroshnichenko - K. Carnicella | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-19 | 21:30 | itf | men | S. Johnson - N. Niedner | exact_name | api_mapping | safe_both_players | 5 |
| 2026-06-19 | 21:30 | itf | women | T. Rabman - M. Ekstrand | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-19 | 22:30 | qualifying | men | G. I. Justo - N. Hardt | api_mapping | api_mapping | safe_both_players | 8 |

# AI TLE Mapping Audit

Generated: `2026-06-15T12:54:16+00:00`
Date range: `2026-06-15` â `2026-06-15`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 178 |
| api_odds_events | 125 |
| odds_events_with_fixture | 125 |
| audited_events | 59 |
| audited_player_appearances | 118 |
| safe_player_appearances | 109 |
| review_player_appearances | 9 |
| safe_events_both_players | 51 |
| review_events_any_player | 8 |
| safe player % | 92.37% |
| review player % | 7.63% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 4 |
| api_mapping | 106 |
| exact_name | 3 |
| unique_surname_initial | 5 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 53136 | B. Fernandez | men | qualifying | api_key_unmapped | men:api:53136 |  | 1 | B. Fernandez - N. Hardt | Asuncion 2 (Paraguay) - Qualification |
| 421 | C. O'Connell | men | challenger | api_key_unmapped | men:api:421 |  | 1 | H. Rocha - C. O'Connell | Nottingham |
| 54466 | C. Smith | men | qualifying | api_key_unmapped | men:api:54466 |  | 1 | C. Chidekh - C. Smith | Dublin (Ireland) - Qualification |
| 40904 | T. Lemaitre | women | itf | api_key_unmapped | women:api:40904 |  | 1 | T. Lemaitre - Z. Kardava | W35+H Tauste |
| 39129 | B. Thompson | women | itf | unique_surname_initial | women:sackmann:259858 | Belle Thompson | 1 | B. Thompson - C. Anson Sanchez | W35+H Tauste |
| 69611 | F. Gonzalez Benitez | men | qualifying | unique_surname_initial | men:sackmann:213568 | Federico Gaston Gonzalez Benitez | 1 | F. Gonzalez Benitez - I. Parisca | Asuncion 2 (Paraguay) - Qualification |
| 96534 | S. Massellani | men | itf | unique_surname_initial | men:sackmann:214436 | Simone Massellani | 1 | S. Massellani - G. Bosio | M25 Milano (Italy) |
| 19429 | S. Rutlauka | women | itf | unique_surname_initial | women:sackmann:223404 | Sabine Rutlauka | 1 | V. Turini - S. Rutlauka | W35+H Tauste |
| 11480 | Z. Kardava | women | itf | unique_surname_initial | women:sackmann:216180 | Zoziya Kardava | 1 | T. Lemaitre - Z. Kardava | W35+H Tauste |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-15 | 15:30 | qualifying | men | C. Chidekh - C. Smith | api_mapping | api_key_unmapped | review_any_player | 10 |
| 2026-06-15 | 15:30 | challenger | men | H. Rocha - C. O'Connell | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-15 | 15:30 | itf | men | S. Massellani - G. Bosio | unique_surname_initial | api_mapping | review_any_player | 0 |
| 2026-06-15 | 19:30 | qualifying | men | F. Gonzalez Benitez - I. Parisca | unique_surname_initial | api_mapping | review_any_player | 0 |
| 2026-06-15 | 20:00 | itf | women | T. Lemaitre - Z. Kardava | api_key_unmapped | unique_surname_initial | review_any_player | 0 |
| 2026-06-15 | 21:30 | itf | women | B. Thompson - C. Anson Sanchez | unique_surname_initial | api_mapping | review_any_player | 1 |
| 2026-06-15 | 21:30 | itf | women | V. Turini - S. Rutlauka | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-15 | 22:00 | qualifying | men | B. Fernandez - N. Hardt | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-15 | 15:00 | qualifying | men | G. Onclin - K. Jacquet | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:00 | itf | men | I. Almazan Valiente - L. Talan Lopatic | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 15:00 | challenger | men | J. Faria - M. Echargui | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:00 | qualifying | men | J. P. Ficovich - N. Mejia | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:00 | challenger | men | L. Angelini - R. Tabata | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 15:00 | challenger | men | T. Boyer - J. Clarke | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 15:00 | atp_wta | men | T. Paul - Z. Svajda | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:05 | challenger | men | D. Ajdukovic - D. Svrcina | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:05 | challenger | men | F. Diaz Acosta - F. Roncadelli | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:10 | qualifying | women | M. Leonard - A. Charaeva | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:15 | atp_wta | women | T. Gibson - F. Jones | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:30 | challenger | men | A. Donski - M. H. Rehberg | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 15:30 | challenger | men | C. Wong - B. Harris | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 15:30 | challenger | men | G. Campana Lee - A. Freire Da Silva | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 15:30 | qualifying | women | H. Kinoshita - V. Hruncakova | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 15:30 | atp_wta | men | J. Pinnington Jones - D. Shapovalov | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:30 | atp_wta | women | N. Bartunkova - D. Shnaider | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:30 | challenger | men | O. Milic - T. Faurel | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 15:30 | challenger | men | S. Ofner - R. Brancaccio | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-15 | 15:45 | challenger | men | K. Feldbausch - L. Lokoli | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 16:00 | atp_wta | women | D. Parry - A. Kalinina | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 16:00 | qualifying | women | E. Gorgodze - N. Brancaccio | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 16:00 | atp_wta | men | F. Cobolli - F. Tiafoe | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 16:00 | atp_wta | women | H. Sakatsume - J. Bouzas Maneiro | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 16:00 | atp_wta | women | R. Masarova - M. Pohankova | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 16:00 | qualifying | women | R. Serban - M. Sherif | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 16:00 | qualifying | women | S. Vickery - B. Haddad Maia | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 16:30 | qualifying | men | A. Galarneau - F. Maestrelli | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-15 | 16:30 | challenger | men | A. Matusevich - A. Gea | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 16:30 | challenger | men | N. Sanchez Izquierdo - L. van Assche | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 16:30 | challenger | men | P. Brunclik - S. Nagal | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 16:30 | challenger | men | T. Barrios Vera - B. Bonzi | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 17:00 | qualifying | men | E. Ymer - H. Searle | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 17:00 | challenger | men | F. Agamenone - S. Napolitano | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 17:00 | challenger | men | F. Gill - H. Gaston | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 17:00 | atp_wta | men | G. Mpetshi Perricard - C. Moutet | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 17:00 | challenger | men | P. Delage - S. Gulin | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-15 | 17:15 | challenger | men | C. Sanchez Jover - A. Moro Canas | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 17:30 | atp_wta | women | A. Blinkova - T. Preston | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 17:30 | atp_wta | women | E. Mertens - L. Samsonova | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 17:30 | qualifying | women | S. Bandecchi - V. Zvonareva | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 18:00 | qualifying | men | C. Huertas Del Pino - E. Kohlmann | api_mapping | exact_name | safe_both_players | 1 |
| 2026-06-15 | 18:00 | qualifying | men | I. Monzon - V. Basel | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 18:00 | challenger | men | L. Ratti - C. Hemery | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-15 | 18:00 | challenger | men | M. Kasnikowski - L. Giustino | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 18:00 | qualifying | men | S. Heredia - E. Monferrer | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 18:00 | qualifying | women | T. Rakotomanga Rajaonah - Y. Lizarazo | exact_name | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 18:30 | qualifying | women | C. Ansari - B. Palicova | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-15 | 19:00 | challenger | men | B. Gadamauri - D. Dzumhur | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-15 | 19:30 | qualifying | men | A. Huertas Del Pino Cordova - G. Ribeiro de Almeida | exact_name | api_mapping | safe_both_players | 1 |
| 2026-06-15 | 23:30 | qualifying | men | L. J. Rodriguez - E. Ribeiro | api_mapping | api_mapping | safe_both_players | 6 |

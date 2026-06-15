# AI TLE Mapping Audit

Generated: `2026-06-15T05:17:19+00:00`
Date range: `2026-06-15` â `2026-06-15`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 144 |
| api_odds_events | 92 |
| odds_events_with_fixture | 92 |
| audited_events | 84 |
| audited_player_appearances | 168 |
| safe_player_appearances | 149 |
| review_player_appearances | 19 |
| safe_events_both_players | 65 |
| review_events_any_player | 19 |
| safe player % | 88.69% |
| review player % | 11.31% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 6 |
| api_mapping | 144 |
| exact_name | 5 |
| unique_surname_initial | 13 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 53732 | A. Blus | men | challenger | api_key_unmapped | men:api:53732 |  | 1 | N. Gombos - A. Blus | Poznan |
| 13987 | A. Sobolieva | women | qualifying | api_key_unmapped | women:api:13987 |  | 1 | K. Deichmann - A. Sobolieva | Brescia (Italy) - Qualification |
| 53136 | B. Fernandez | men | qualifying | api_key_unmapped | men:api:53136 |  | 1 | B. Fernandez - N. Hardt | Asuncion 2 (Paraguay) - Qualification |
| 421 | C. O'Connell | men | challenger | api_key_unmapped | men:api:421 |  | 1 | H. Rocha - C. O'Connell | Nottingham |
| 54466 | C. Smith | men | qualifying | api_key_unmapped | men:api:54466 |  | 1 | C. Chidekh - C. Smith | Dublin (Ireland) - Qualification |
| 12869 | M. Timofeeva | women | atp_wta | api_key_unmapped | women:api:12869 |  | 1 | M. Timofeeva - R. Zarazua | Berlin |
| 2972 | B. Van De Zandschulp | men | atp_wta | unique_surname_initial | men:sackmann:122298 | Botic Van De Zandschulp | 1 | B. Van De Zandschulp - H. Wendelken | London |
| 15221 | F. Pieczonka | men | challenger | unique_surname_initial | men:sackmann:210091 | Filip Pieczonka | 1 | A. Donski - F. Pieczonka | Poznan |
| 10909 | H. Kinoshita | women | qualifying | unique_surname_initial | women:sackmann:260171 | Hayu Kinoshita | 1 | H. Kinoshita - V. Hruncakova | Figueira Da Foz (Portugal) - Qualification |
| 154 | J. Bouzas Maneiro | women | atp_wta | unique_surname_initial | women:sackmann:222601 | Jessica Bouzas Maneiro | 1 | H. Sakatsume - J. Bouzas Maneiro | Nottingham |
| 14085 | L. J. Rodriguez | men | qualifying | unique_surname_initial | men:sackmann:202271 | Lorenzo Joaquin Rodriguez | 1 | L. J. Rodriguez - E. Ribeiro | Asuncion 2 (Paraguay) - Qualification |
| 778 | P. Delage | men | challenger | unique_surname_initial | men:sackmann:208265 | Pierre Delage | 1 | P. Delage - S. Gulin | Royan |
| 1807 | R. Serban | women | qualifying | unique_surname_initial | women:sackmann:213779 | Raluka Serban | 1 | R. Serban - M. Sherif | Brescia (Italy) - Qualification |
| 359 | S. Ofner | men | challenger | unique_surname_initial | men:sackmann:124116 | Sebastian Ofner | 1 | S. Ofner - R. Brancaccio | Parma |
| 1790 | S. Vickery | women | qualifying | unique_surname_initial | women:sackmann:203500 | Sachia Vickery | 1 | S. Vickery - B. Haddad Maia | Figueira Da Foz (Portugal) - Qualification |
| 65519 | T. Faurel | men | challenger | unique_surname_initial | men:sackmann:212225 | Thomas Faurel | 1 | O. Milic - T. Faurel | Royan |
| 8976 | T. Valentova | women | atp_wta | unique_surname_initial | women:sackmann:238184 | Tereza Valentova | 1 | M. Bouzkova - T. Valentova | Nottingham |
| 2822 | V. Zvonareva | women | qualifying | unique_surname_initial | women:sackmann:201329 | Vera Zvonareva | 1 | S. Bandecchi - V. Zvonareva | Figueira Da Foz (Portugal) - Qualification |
| 150 | Y. Lizarazo | women | qualifying | unique_surname_initial | women:sackmann:202464 | Yuliana Lizarazo | 1 | T. Rakotomanga Rajaonah - Y. Lizarazo | Brescia (Italy) - Qualification |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-15 | 11:30 | challenger | men | A. Donski - F. Pieczonka | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-15 | 11:30 | atp_wta | women | M. Timofeeva - R. Zarazua | api_key_unmapped | api_mapping | review_any_player | 12 |
| 2026-06-15 | 11:30 | challenger | men | N. Gombos - A. Blus | api_mapping | api_key_unmapped | review_any_player | 0 |
| 2026-06-15 | 12:00 | atp_wta | women | M. Bouzkova - T. Valentova | api_mapping | unique_surname_initial | review_any_player | 12 |
| 2026-06-15 | 12:30 | atp_wta | men | B. Van De Zandschulp - H. Wendelken | unique_surname_initial | api_mapping | review_any_player | 12 |
| 2026-06-15 | 13:30 | qualifying | women | K. Deichmann - A. Sobolieva | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-15 | 13:30 | challenger | men | S. Ofner - R. Brancaccio | unique_surname_initial | api_mapping | review_any_player | 6 |
| 2026-06-15 | 14:00 | qualifying | women | H. Kinoshita - V. Hruncakova | unique_surname_initial | api_mapping | review_any_player | 11 |
| 2026-06-15 | 15:00 | qualifying | men | C. Chidekh - C. Smith | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-15 | 15:00 | challenger | men | H. Rocha - C. O'Connell | api_mapping | api_key_unmapped | review_any_player | 12 |
| 2026-06-15 | 15:00 | atp_wta | women | H. Sakatsume - J. Bouzas Maneiro | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-15 | 15:30 | challenger | men | O. Milic - T. Faurel | api_mapping | unique_surname_initial | review_any_player | 11 |
| 2026-06-15 | 15:30 | qualifying | women | S. Vickery - B. Haddad Maia | unique_surname_initial | api_mapping | review_any_player | 0 |
| 2026-06-15 | 16:00 | qualifying | women | R. Serban - M. Sherif | unique_surname_initial | api_mapping | review_any_player | 0 |
| 2026-06-15 | 17:00 | challenger | men | P. Delage - S. Gulin | unique_surname_initial | api_mapping | review_any_player | 9 |
| 2026-06-15 | 17:00 | qualifying | women | S. Bandecchi - V. Zvonareva | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-15 | 18:00 | qualifying | women | T. Rakotomanga Rajaonah - Y. Lizarazo | exact_name | unique_surname_initial | review_any_player | 0 |
| 2026-06-15 | 22:00 | qualifying | men | B. Fernandez - N. Hardt | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-15 | 23:30 | qualifying | men | L. J. Rodriguez - E. Ribeiro | unique_surname_initial | api_mapping | review_any_player | 6 |
| 2026-06-15 | 10:00 | challenger | men | A. Wazny - D. Yevseyev | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 10:00 | challenger | men | D. Siniakov - B. Hassan | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 10:00 | challenger | men | L. Bocchi - A. Weis | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 10:00 | challenger | men | M. H. Rehberg - A. Marti Pujolras | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 10:00 | challenger | men | M. Vrbensky - M. Karol | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 10:00 | challenger | men | R. Seggerman - M. Tobon | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 10:30 | atp_wta | women | D. Parry - E. Seidel | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 10:30 | qualifying | women | E. Yaneva - G. Pedone | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 10:30 | qualifying | women | J. Ruggeri - T. Pieri | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 10:30 | atp_wta | women | L. Sun - A. Kalinina | exact_name | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 10:30 | atp_wta | women | S. Lamens - D. Galfi | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 11:00 | qualifying | women | A. Kulikova - M. Kobori | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 11:00 | challenger | men | I. Lopez Morillo - O. Wallin | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 11:00 | qualifying | women | W. Osuigwe - A. Voloshchuk | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 11:30 | challenger | men | E. Dalla Valle - J. Paul | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 11:30 | atp_wta | women | L. Zhu - S. Kraus | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 11:30 | challenger | men | M. Martineau - L. Wiedenmann | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 11:30 | challenger | men | M. Mrva - J. Sadzik | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 11:30 | atp_wta | men | M. Schoenhaus - L. Tien | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 11:30 | challenger | men | O. Roca Batalla - A. Sanchez Quilez | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-15 | 12:00 | qualifying | women | E. Kazionova - D. Chiesa | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-15 | 12:00 | atp_wta | women | M. Frech - S. Zhang | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 12:00 | qualifying | men | O. Crawford - N. Visker | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 12:00 | challenger | men | O. Tarvet - R. Safiullin | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 12:00 | atp_wta | women | T. Maria - J. Tjen | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 12:30 | atp_wta | women | Q. Zheng - M. Sakkari | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 12:30 | challenger | men | R. Molleker - M. Erhard | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 13:00 | atp_wta | women | K. Siniakova - Y. Yuan | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:00 | atp_wta | men | N. Basilashvili - D. Altmaier | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:00 | atp_wta | women | P. Marcinko - A. Ito | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:00 | atp_wta | men | T. Atmane - M. Landaluce | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:30 | qualifying | women | A. Mazzola - L. Giovannini | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 13:30 | atp_wta | women | E. Alexandrova - A. Potapova | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:30 | atp_wta | women | M. Joint - Y. Starodubtseva | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 13:30 | atp_wta | women | S. Bejlek - E. Navarro | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 14:00 | qualifying | women | M. Leonard - A. Charaeva | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 14:00 | atp_wta | women | T. Gibson - F. Jones | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 14:00 | atp_wta | men | T. Paul - Z. Svajda | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 14:30 | challenger | men | D. Ajdukovic - D. Svrcina | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 14:30 | atp_wta | men | N. Borges - F. Auger-Aliassime | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 14:30 | atp_wta | women | R. Masarova - M. Pohankova | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:00 | challenger | men | F. Agamenone - S. Napolitano | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:00 | challenger | men | F. Diaz Acosta - F. Roncadelli | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:00 | qualifying | men | G. Onclin - K. Jacquet | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 15:00 | challenger | men | J. Faria - M. Echargui | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-15 | 15:00 | qualifying | men | J. P. Ficovich - N. Mejia | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 15:30 | challenger | men | C. Wong - B. Harris | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:30 | atp_wta | men | J. Pinnington Jones - D. Shapovalov | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 15:30 | challenger | men | K. Feldbausch - L. Lokoli | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 15:30 | atp_wta | women | N. Bartunkova - D. Shnaider | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 16:00 | atp_wta | men | F. Cobolli - F. Tiafoe | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 16:30 | atp_wta | women | A. Blinkova - T. Preston | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 16:30 | qualifying | men | A. Galarneau - F. Maestrelli | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 16:30 | challenger | men | B. Gadamauri - D. Dzumhur | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-15 | 16:30 | qualifying | men | E. Ymer - H. Searle | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 16:30 | challenger | men | N. Sanchez Izquierdo - L. van Assche | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 16:30 | challenger | men | P. Brunclik - S. Nagal | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 16:30 | challenger | men | T. Barrios Vera - B. Bonzi | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 17:00 | qualifying | women | C. Ansari - B. Palicova | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-15 | 17:00 | challenger | men | C. Sanchez Jover - A. Moro Canas | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-15 | 17:00 | challenger | men | F. Gill - H. Gaston | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-15 | 17:00 | atp_wta | men | G. Mpetshi Perricard - C. Moutet | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-15 | 17:30 | atp_wta | women | E. Mertens - L. Samsonova | api_mapping | exact_name | safe_both_players | 12 |
| 2026-06-15 | 18:00 | challenger | men | L. Ratti - C. Hemery | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-15 | 18:00 | challenger | men | M. Kasnikowski - L. Giustino | api_mapping | api_mapping | safe_both_players | 11 |

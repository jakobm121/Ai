# AI TLE Mapping Audit

Generated: `2026-06-14T05:57:21+00:00`
Date range: `2026-06-14` â `2026-06-14`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 159 |
| api_odds_events | 80 |
| odds_events_with_fixture | 80 |
| audited_events | 77 |
| audited_player_appearances | 154 |
| safe_player_appearances | 135 |
| review_player_appearances | 19 |
| safe_events_both_players | 59 |
| review_events_any_player | 18 |
| safe player % | 87.66% |
| review player % | 12.34% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 6 |
| api_mapping | 128 |
| exact_name | 7 |
| unique_surname_initial | 13 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 53732 | A. Blus | men | challenger | api_key_unmapped | men:api:53732 |  | 1 | N. Gombos - A. Blus | Poznan |
| 22522 | A. Teixido Garcia | women | itf | api_key_unmapped | women:api:22522 |  | 1 | A. Teixido Garcia - L. Vujovic | W35 Casablanca |
| 103831 | L. Tombolini | men | challenger | api_key_unmapped | men:api:103831 |  | 1 | L. Tombolini - L. Wiedenmann | Parma |
| 38070 | M. Ristic | women | qualifying | api_key_unmapped | women:api:38070 |  | 1 | M. Ristic - V. Meliss | Brescia (Italy) - Qualification |
| 12869 | M. Timofeeva | women | atp_wta | api_key_unmapped | women:api:12869 |  | 1 | M. Timofeeva - R. Zarazua | Berlin |
| 796 | Y. Bu | men | challenger | api_key_unmapped | men:api:796 |  | 1 | J. Fearnley - Y. Bu | Ilkley |
| 54119 | A. Schuman | women | itf | unique_surname_initial | women:sackmann:260767 | Aspen Schuman | 1 | V. Milovanova - A. Schuman | W15 Monastir 17 |
| 569 | D. Yevseyev | men | challenger | unique_surname_initial | men:sackmann:106187 | Denis Yevseyev | 1 | A. Wazny - D. Yevseyev | Poznan |
| 1985 | E. Kazionova | women | qualifying | unique_surname_initial | women:sackmann:214546 | Ekaterina Kazionova | 1 | J. Struplova - E. Kazionova | Brescia (Italy) - Qualification |
| 88183 | F. Bocci | men | challenger | unique_surname_initial | men:sackmann:214055 | Flavio Bocci | 1 | E. Dalla Valle - F. Bocci | Parma |
| 1966 | J. Paul | men | challenger | unique_surname_initial | men:sackmann:207605 | Jakub Paul | 1 | M. Mecarelli - J. Paul | Parma |
| 88816 | J. Sadzik | men | challenger | unique_surname_initial | men:sackmann:214087 | Jan Sadzik | 1 | M. Mrva - J. Sadzik | Poznan |
| 37992 | M. Bassem Sobhy | men | challenger | unique_surname_initial | men:sackmann:209971 | Michael Bassem Sobhy | 1 | F. Broska - M. Bassem Sobhy | Poznan |
| 2265 | M. Mettraux | women | itf | unique_surname_initial | women:sackmann:221062 | Marie Mettraux | 1 | K. Zaytseva - M. Mettraux | W15 Kursumlijska Banja 4 |
| 9515 | M. Zheng | men | challenger | unique_surname_initial | men:sackmann:210116 | Michael Zheng | 1 | S. Mochizuki - M. Zheng | Nottingham |
| 893 | R. Molleker | men | challenger | unique_surname_initial | men:sackmann:200484 | Rudolf Molleker | 1 | R. Molleker - M. Erhard | Poznan |
| 37897 | R. Sakamoto | men | challenger | unique_surname_initial | men:sackmann:210536 | Rei Sakamoto | 1 | R. Sakamoto - Y. Wu | Nottingham |
| 450 | S. Lamens | women | atp_wta | unique_surname_initial | women:sackmann:215480 | Suzan Lamens | 1 | S. Lamens - D. Galfi | Berlin |
| 2580 | V. Meliss | women | qualifying | unique_surname_initial | women:sackmann:214238 | Verena Meliss | 1 | M. Ristic - V. Meliss | Brescia (Italy) - Qualification |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-14 | 10:00 | itf | women | K. Zaytseva - M. Mettraux | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-14 | 10:30 | itf | women | V. Milovanova - A. Schuman | api_mapping | unique_surname_initial | review_any_player | 9 |
| 2026-06-14 | 11:00 | challenger | men | F. Broska - M. Bassem Sobhy | api_mapping | unique_surname_initial | review_any_player | 8 |
| 2026-06-14 | 11:00 | atp_wta | women | S. Lamens - D. Galfi | unique_surname_initial | api_mapping | review_any_player | 10 |
| 2026-06-14 | 12:00 | qualifying | women | J. Struplova - E. Kazionova | api_mapping | unique_surname_initial | review_any_player | 2 |
| 2026-06-14 | 12:30 | challenger | men | A. Wazny - D. Yevseyev | api_mapping | unique_surname_initial | review_any_player | 7 |
| 2026-06-14 | 13:00 | itf | women | A. Teixido Garcia - L. Vujovic | api_key_unmapped | api_mapping | review_any_player | 10 |
| 2026-06-14 | 13:00 | challenger | men | M. Mecarelli - J. Paul | api_mapping | unique_surname_initial | review_any_player | 5 |
| 2026-06-14 | 13:30 | qualifying | women | M. Ristic - V. Meliss | api_key_unmapped | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 13:30 | atp_wta | women | M. Timofeeva - R. Zarazua | api_key_unmapped | api_mapping | review_any_player | 12 |
| 2026-06-14 | 14:00 | challenger | men | N. Gombos - A. Blus | api_mapping | api_key_unmapped | review_any_player | 0 |
| 2026-06-14 | 14:30 | challenger | men | E. Dalla Valle - F. Bocci | api_mapping | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 14:30 | challenger | men | L. Tombolini - L. Wiedenmann | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-14 | 15:30 | challenger | men | J. Fearnley - Y. Bu | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-14 | 15:30 | challenger | men | M. Mrva - J. Sadzik | api_mapping | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 15:30 | challenger | men | R. Molleker - M. Erhard | unique_surname_initial | api_mapping | review_any_player | 8 |
| 2026-06-14 | 16:00 | challenger | men | S. Mochizuki - M. Zheng | api_mapping | unique_surname_initial | review_any_player | 8 |
| 2026-06-14 | 17:30 | challenger | men | R. Sakamoto - Y. Wu | unique_surname_initial | api_mapping | review_any_player | 8 |
| 2026-06-14 | 09:00 | itf | men | I. Marrero Curbelo - M. McKennon | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 10:00 | challenger | men | M. Cerny - A. Weis | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 10:00 | itf | men | N. McDonald - S. Kopp | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 10:30 | itf | men | D. Mosejczuk - C. Bouchelaghem | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 10:30 | qualifying | women | J. Ruggeri - Y. Kotliar | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 10:30 | qualifying | women | T. Pieri - D. Cherubini | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 11:00 | itf | women | A. Falei - S. Broadus | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 11:00 | atp_wta | women | D. Parry - E. Seidel | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 11:00 | itf | women | J. Avdeeva - E. Vedder | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 11:00 | challenger | men | J. Forejtek - K. Filar | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-14 | 11:00 | challenger | men | L. Castelnuovo - F. Zakaria | api_mapping | exact_name | safe_both_players | 9 |
| 2026-06-14 | 11:00 | atp_wta | men | L. Sonego - N. Basilashvili | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 11:00 | atp_wta | women | L. Sun - A. Kalinina | exact_name | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 11:00 | atp_wta | men | R. Collignon - R. Bautista-Agut | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 11:00 | itf | women | R. Roura Llaverias - B. Ivanova | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 11:00 | itf | women | T. Gadamauri - V. Steiner | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 11:00 | itf | men | Y. Kelm - A. Boros | api_mapping | exact_name | safe_both_players | 9 |
| 2026-06-14 | 11:30 | challenger | men | A. Shevchenko - T. Daniel | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 11:30 | challenger | men | H. S. Callejon - L. Bocchi | exact_name | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 11:30 | itf | men | J. Domingues - P. Martinez Gomez | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 11:30 | challenger | men | M. Topo - R. Seggerman | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 11:30 | challenger | men | Y. Milev - M. Tobon | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 12:00 | challenger | men | J. Watt - A. Gray | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 12:00 | qualifying | women | L. Ciric Bagaric - D. Chiesa | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 12:00 | atp_wta | women | R. Montgomery - B. Krejcikova | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 12:30 | challenger | women | A. Krueger - C. Naef | exact_name | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 12:30 | challenger | men | D. Siniakov - B. Hassan | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 12:30 | atp_wta | women | K. Siniakova - Y. Yuan | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 12:30 | challenger | men | M. Vrbensky - M. Karol | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 12:30 | atp_wta | women | P. Marcinko - A. Ito | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 13:00 | atp_wta | men | A. Vukic - H. Wendelken | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 13:00 | challenger | men | L. Nardi - G. Hussey | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 13:00 | atp_wta | men | M. Bellucci - A. Bolt | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 13:00 | atp_wta | men | M. Landaluce - T. Gentzsch | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 13:00 | challenger | men | O. Roca Batalla - G. Perego | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 13:00 | challenger | men | R. Bertola - J. McCabe | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 13:00 | challenger | men | S. Vincent Ruggeri - A. Sanchez Quilez | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 13:00 | atp_wta | men | Z. Svajda - M. Damm | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 13:30 | atp_wta | women | M. Frech - S. Zhang | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 13:30 | atp_wta | women | P. Kudermetova - S. Kraus | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 13:30 | challenger | men | S. Kwon - A. Matusevich | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 13:30 | challenger | men | Z. Zhang - O. Okonkwo | exact_name | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 14:00 | atp_wta | men | B. Shelton - T. Fritz | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:00 | itf | women | E. Avanesyan - K. Rinaldo Persson | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 14:00 | challenger | men | M. H. Rehberg - A. Marti Pujolras | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 14:30 | atp_wta | men | A. Kovacevic - G. Mpetshi Perricard | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 14:30 | itf | women | C. Burel - J. Lim | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 14:30 | atp_wta | women | D. Vekic - E. Raducanu | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:30 | atp_wta | men | K. Majchrzak - A. De Minaur | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 14:30 | challenger | men | M. Martineau - D. Salazar | api_mapping | exact_name | safe_both_players | 0 |
| 2026-06-14 | 14:30 | atp_wta | men | R. Hijikata - M. Giron | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 15:00 | challenger | men | F. Balshaw - D. Jorda Sanchis | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 15:00 | itf | women | P. Iatcenko - M. Kubka | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 15:00 | atp_wta | women | R. Masarova - M. Pohankova | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 15:30 | challenger | men | I. Lopez Morillo - O. Wallin | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 16:00 | challenger | men | N. Budkov Kjaer - M. McDonald | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 16:00 | qualifying | women | R. Zelnickova - N. Basiletti | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-14 | 16:30 | qualifying | men | J. De Jong - R. Carballes Baena | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 17:00 | itf | women | N. Podoroska - L. Perez Alarcon | api_mapping | api_mapping | safe_both_players | 9 |

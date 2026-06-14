# AI TLE Mapping Audit

Generated: `2026-06-14T10:15:33+00:00`
Date range: `2026-06-14` â `2026-06-14`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 161 |
| api_odds_events | 125 |
| odds_events_with_fixture | 125 |
| audited_events | 91 |
| audited_player_appearances | 182 |
| safe_player_appearances | 160 |
| review_player_appearances | 22 |
| safe_events_both_players | 72 |
| review_events_any_player | 19 |
| safe player % | 87.91% |
| review player % | 12.09% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 9 |
| api_mapping | 155 |
| exact_name | 5 |
| unique_surname_initial | 13 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 53732 | A. Blus | men | challenger | api_key_unmapped | men:api:53732 |  | 1 | N. Gombos - A. Blus | Poznan |
| 22522 | A. Teixido Garcia | women | itf | api_key_unmapped | women:api:22522 |  | 1 | A. Teixido Garcia - L. Vujovic | W35 Casablanca |
| 103798 | J. Coudret | men | challenger | api_key_unmapped | men:api:103798 |  | 1 | J. Coudret - A. Freire Da Silva | Royan |
| 103836 | J. McGloughlin | men | qualifying | api_key_unmapped | men:api:103836 |  | 1 | J. McGloughlin - Y. Zhou | Dublin (Ireland) - Qualification |
| 103831 | L. Tombolini | men | challenger | api_key_unmapped | men:api:103831 |  | 1 | L. Tombolini - L. Wiedenmann | Parma |
| 38070 | M. Ristic | women | qualifying | api_key_unmapped | women:api:38070 |  | 1 | M. Ristic - V. Meliss | Brescia (Italy) - Qualification |
| 12869 | M. Timofeeva | women | atp_wta | api_key_unmapped | women:api:12869 |  | 1 | M. Timofeeva - R. Zarazua | Berlin |
| 11781 | P. Dev S D | men | challenger | api_key_unmapped | men:api:11781 |  | 1 | P. Dev S D - G. Gomez | Royan |
| 796 | Y. Bu | men | challenger | api_key_unmapped | men:api:796 |  | 1 | J. Fearnley - Y. Bu | Ilkley |
| 67455 | A. Hayen | men | qualifying | unique_surname_initial | men:sackmann:212847 | Alejandro Hayen | 1 | A. Hayen - I. Parisca | Asuncion 2 (Paraguay) - Qualification |
| 32064 | A. Johnson | men | itf | unique_surname_initial | men:sackmann:213965 | Andrew Johnson | 1 | K. Bigun - A. Johnson | M15 Los Angeles, CA |
| 14438 | A. Zamarripa | women | qualifying | unique_surname_initial | women:sackmann:221440 | Allura Zamarripa | 1 | K. Sebov - A. Zamarripa | Figueira Da Foz (Portugal) - Qualification |
| 101392 | D. Leeman | men | qualifying | unique_surname_initial | men:sackmann:214535 | Dylan Leeman | 1 | D. Leeman - C. Broom | Dublin (Ireland) - Qualification |
| 5717 | G. Gomez | men | challenger | unique_surname_initial | men:sackmann:119896 | Gabriel Gomez | 1 | P. Dev S D - G. Gomez | Royan |
| 52679 | I. Parisca | men | qualifying | unique_surname_initial | men:sackmann:212306 | Ignacio Parisca | 1 | A. Hayen - I. Parisca | Asuncion 2 (Paraguay) - Qualification |
| 568 | K. Uchida | men | qualifying | unique_surname_initial | men:sackmann:111187 | Kaichi Uchida | 1 | Q. Vandecasteele - K. Uchida | Dublin (Ireland) - Qualification |
| 4259 | L. Dussin | men | challenger | unique_surname_initial | men:sackmann:202128 | Louis Dussin | 1 | L. Angelini - L. Dussin | Royan |
| 15771 | N. Rodrigues | men | qualifying | unique_surname_initial | men:sackmann:208372 | Natan Rodrigues | 1 | E. Kohlmann - N. Rodrigues | Asuncion 2 (Paraguay) - Qualification |
| 103797 | P. Theate | men | challenger | unique_surname_initial | men:sackmann:214399 | Paul Theate | 1 | G. Campana Lee - P. Theate | Royan |
| 70038 | R. Le Meur | men | challenger | unique_surname_initial | men:sackmann:212998 | Robinson Le Meur | 1 | R. Le Meur - R. Tabata | Royan |
| 63487 | R. Tabata | men | challenger | unique_surname_initial | men:sackmann:212944 | Ryo Tabata | 1 | R. Le Meur - R. Tabata | Royan |
| 10020 | V. Basel | men | qualifying | unique_surname_initial | men:sackmann:211761 | Valentin Basel | 1 | V. Basel - T. Cigarran | Asuncion 2 (Paraguay) - Qualification |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-14 | 12:30 | challenger | men | G. Campana Lee - P. Theate | api_mapping | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 13:00 | itf | women | A. Teixido Garcia - L. Vujovic | api_key_unmapped | api_mapping | review_any_player | 10 |
| 2026-06-14 | 13:30 | qualifying | men | Q. Vandecasteele - K. Uchida | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 14:00 | challenger | men | J. Coudret - A. Freire Da Silva | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-14 | 14:00 | challenger | men | R. Le Meur - R. Tabata | unique_surname_initial | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 14:15 | qualifying | women | M. Ristic - V. Meliss | api_key_unmapped | api_mapping | review_any_player | 1 |
| 2026-06-14 | 14:30 | challenger | men | L. Tombolini - L. Wiedenmann | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-14 | 15:00 | qualifying | men | J. McGloughlin - Y. Zhou | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-14 | 15:00 | atp_wta | women | M. Timofeeva - R. Zarazua | api_key_unmapped | api_mapping | review_any_player | 12 |
| 2026-06-14 | 15:00 | challenger | men | P. Dev S D - G. Gomez | api_key_unmapped | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 15:10 | challenger | men | N. Gombos - A. Blus | api_mapping | api_key_unmapped | review_any_player | 0 |
| 2026-06-14 | 15:30 | challenger | men | J. Fearnley - Y. Bu | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-14 | 15:30 | qualifying | women | K. Sebov - A. Zamarripa | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 15:30 | challenger | men | L. Angelini - L. Dussin | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 16:30 | qualifying | men | D. Leeman - C. Broom | unique_surname_initial | api_mapping | review_any_player | 0 |
| 2026-06-14 | 18:00 | qualifying | men | E. Kohlmann - N. Rodrigues | exact_name | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 20:00 | itf | men | K. Bigun - A. Johnson | api_mapping | unique_surname_initial | review_any_player | 1 |
| 2026-06-14 | 21:00 | qualifying | men | V. Basel - T. Cigarran | unique_surname_initial | api_mapping | review_any_player | 1 |
| 2026-06-14 | 22:30 | qualifying | men | A. Hayen - I. Parisca | unique_surname_initial | unique_surname_initial | review_any_player | 0 |
| 2026-06-14 | 12:30 | challenger | women | A. Krueger - C. Naef | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 12:30 | challenger | men | D. Siniakov - B. Hassan | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 12:30 | qualifying | women | V. Losciale - A. Voloshchuk | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 12:30 | qualifying | women | W. Osuigwe - C. Tomai | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 12:35 | atp_wta | women | D. Parry - E. Seidel | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 12:35 | qualifying | women | J. Struplova - E. Kazionova | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-14 | 12:35 | atp_wta | men | L. Sonego - N. Basilashvili | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 12:35 | atp_wta | women | L. Sun - A. Kalinina | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 12:35 | atp_wta | men | R. Collignon - R. Bautista-Agut | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 12:35 | atp_wta | women | S. Lamens - D. Galfi | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 12:50 | qualifying | women | L. Ciric Bagaric - D. Chiesa | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 13:00 | atp_wta | men | A. Vukic - H. Wendelken | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 13:00 | challenger | men | A. Wazny - D. Yevseyev | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 13:00 | challenger | men | L. Nardi - G. Hussey | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 13:00 | challenger | men | M. Mecarelli - J. Paul | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-14 | 13:00 | itf | men | O. Krutykh - G. Kravchenko | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 13:00 | challenger | men | O. Roca Batalla - G. Perego | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 13:00 | challenger | men | R. Bertola - J. McCabe | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 13:00 | atp_wta | men | Z. Svajda - M. Damm | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 13:30 | qualifying | men | E. Butvilas - C. Hewitt | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 13:30 | qualifying | men | H. Mayot - T. Kokkinakis | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 13:30 | challenger | men | S. Kwon - A. Matusevich | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 13:30 | challenger | men | Z. Zhang - O. Okonkwo | exact_name | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 13:40 | challenger | men | M. Vrbensky - M. Karol | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 14:00 | challenger | men | A. Holmgren - J. Clarke | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 14:00 | atp_wta | men | B. Shelton - T. Fritz | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:00 | itf | women | E. Avanesyan - K. Rinaldo Persson | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 14:00 | atp_wta | women | K. Siniakova - Y. Yuan | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 14:00 | challenger | men | M. H. Rehberg - A. Marti Pujolras | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 14:00 | qualifying | women | M. Martinez Vaquero - E. Micic | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 14:00 | atp_wta | women | P. Marcinko - A. Ito | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-14 | 14:00 | challenger | men | S. Vincent Ruggeri - A. Sanchez Quilez | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 14:30 | atp_wta | men | A. Kovacevic - G. Mpetshi Perricard | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 14:30 | atp_wta | women | A. Ruzic - T. Preston | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 14:30 | itf | women | C. Burel - J. Lim | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 14:30 | atp_wta | women | D. Vekic - E. Raducanu | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:30 | challenger | men | E. Dalla Valle - F. Bocci | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 14:30 | atp_wta | men | K. Majchrzak - A. De Minaur | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 14:30 | atp_wta | men | M. Bellucci - A. Bolt | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:30 | atp_wta | men | M. Landaluce - T. Gentzsch | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 14:30 | atp_wta | men | R. Hijikata - M. Giron | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 14:30 | atp_wta | women | V. Golubic - S. Kenin | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 15:00 | challenger | men | F. Balshaw - D. Jorda Sanchis | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 15:00 | atp_wta | women | H. Sakatsume - A. Dudeney | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 15:00 | atp_wta | women | M. Frech - S. Zhang | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 15:00 | itf | women | P. Iatcenko - M. Kubka | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 15:00 | atp_wta | women | P. Kudermetova - S. Kraus | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-14 | 15:00 | qualifying | men | R. Noguchi - P. Jubb | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 15:00 | qualifying | men | Y. H. Hsu - V. Ursu | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 15:00 | atp_wta | women | Z. Sonmez - H. Klugman | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 15:30 | challenger | men | I. Lopez Morillo - O. Wallin | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 15:30 | challenger | men | M. Martineau - D. Salazar | api_mapping | exact_name | safe_both_players | 0 |
| 2026-06-14 | 15:30 | qualifying | women | V. Ryser - S. Garakani | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 16:00 | challenger | men | M. Mrva - J. Sadzik | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 16:00 | challenger | men | N. Budkov Kjaer - M. McDonald | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 16:00 | itf | men | N. Oliveira - A. Hernandez | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 16:00 | qualifying | women | R. Zelnickova - N. Basiletti | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-14 | 16:00 | challenger | men | S. Mochizuki - M. Zheng | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 16:30 | qualifying | men | A. Guerrieri - F. Romano | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 16:30 | qualifying | men | H. Stewart - K. Smith | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 16:30 | qualifying | men | J. De Jong - R. Carballes Baena | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 16:30 | atp_wta | women | R. Masarova - M. Pohankova | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-14 | 16:40 | challenger | men | R. Molleker - M. Erhard | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-14 | 17:00 | itf | women | N. Podoroska - L. Perez Alarcon | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 17:00 | itf | men | S. Gorzny - O. Baris | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 17:30 | challenger | men | R. Sakamoto - Y. Wu | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-14 | 18:00 | qualifying | men | E. Monferrer - W. Leite | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 19:30 | qualifying | men | I. Monzon - J. Cundom | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 20:00 | itf | women | A. Shcherbinina - K. Carnicella | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 20:00 | qualifying | women | K. Kawa - L. Bronzetti | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-14 | 22:30 | qualifying | men | M. Del Pino - G. Ribeiro de Almeida | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-14 | 23:00 | itf | women | A. Vergara Rivera - C. Alves | api_mapping | api_mapping | safe_both_players | 1 |

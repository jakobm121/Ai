# AI TLE Mapping Audit

Generated: `2026-06-13T09:46:03+00:00`
Date range: `2026-06-13` â `2026-06-13`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 203 |
| api_odds_events | 115 |
| odds_events_with_fixture | 115 |
| audited_events | 80 |
| audited_player_appearances | 160 |
| safe_player_appearances | 156 |
| review_player_appearances | 4 |
| safe_events_both_players | 76 |
| review_events_any_player | 4 |
| safe player % | 97.50% |
| review player % | 2.50% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 4 |
| api_mapping | 151 |
| exact_name | 5 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 17463 | Dar. Blanch | men | challenger | api_key_unmapped | men:api:17463 |  | 1 | Dar. Blanch - J. Fearnley | Ilkley |
| 12869 | M. Timofeeva | women | atp_wta | api_key_unmapped | women:api:12869 |  | 1 | M. Timofeeva - R. Zarazua | Berlin |
| 102950 | P. Perez Ramos | men | itf | api_key_unmapped | men:api:102950 |  | 1 | P. Martinez Gomez - P. Perez Ramos | M25 Martos |
| 796 | Y. Bu | men | challenger | api_key_unmapped | men:api:796 |  | 1 | M. Lajal - Y. Bu | Ilkley |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-13 | 12:00 | challenger | men | Dar. Blanch - J. Fearnley | api_key_unmapped | api_mapping | review_any_player | 11 |
| 2026-06-13 | 12:00 | challenger | men | M. Lajal - Y. Bu | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-13 | 12:00 | itf | men | P. Martinez Gomez - P. Perez Ramos | api_mapping | api_key_unmapped | review_any_player | 4 |
| 2026-06-13 | 14:05 | atp_wta | women | M. Timofeeva - R. Zarazua | api_key_unmapped | api_mapping | review_any_player | 8 |
| 2026-06-13 | 11:50 | itf | men | S. Perez Contri - I. Biletic | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 11:55 | itf | men | G. Kravchenko - J. Kumstat | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:00 | atp_wta | men | B. Shelton - S. Shimabukuro | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 12:00 | challenger | men | D. Sweeny - T. Samuel | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:00 | atp_wta | women | E. Arango - A. Bondar | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:00 | challenger | men | H. Jefferson - A. Gray | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:00 | itf | men | J. Sperle - A. Boros | api_mapping | exact_name | safe_both_players | 1 |
| 2026-06-13 | 12:00 | challenger | men | O. Tarvet - F. Romano | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 12:00 | atp_wta | women | S. Kenin - E. Jacquemot | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 12:00 | challenger | men | T. Skatov - J. Watt | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 12:30 | atp_wta | men | D. Medvedev - M. Cilic | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-13 | 12:30 | itf | women | E. Bennemann - T. Gadamauri | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 12:30 | atp_wta | men | J. Mackenzie - A. Bolt | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:35 | atp_wta | men | B. Sanchez Martinez - R. Bautista-Agut | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:35 | atp_wta | women | M. Pohankova - T. Korpatsch | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:35 | atp_wta | women | P. Marcinko - A. Ito | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 12:40 | atp_wta | men | T. Pereira - T. Gentzsch | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 13:00 | atp_wta | men | A. Bublik - T. Fritz | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 13:00 | itf | women | A. Granwehr - J. Lim | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 13:00 | challenger | men | F. Cina - T. Daniel | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 13:00 | itf | women | I. Primorac - E. Avanesyan | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 13:00 | atp_wta | men | M. Damm - D. Merida Aguilar | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 13:00 | itf | men | O. Krutykh - D. Petak | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 13:00 | itf | men | S. Cuenin - B. Djuric | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 13:00 | atp_wta | men | Z. Svajda - L. Broady | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 13:30 | atp_wta | women | A. Ruzic - K. Juvan | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 13:30 | atp_wta | women | E. Raducanu - K. Rakhimova | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 13:30 | atp_wta | women | H. Klugman - A. Zakharova | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 13:30 | challenger | men | L. Nardi - O. Weightman | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 13:30 | challenger | men | P. Brady - G. Hussey | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 14:00 | challenger | women | A. Krueger - D. Vidmanova | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 14:00 | atp_wta | women | D. Kasatkina - A. Blinkova | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:00 | atp_wta | women | D. Parry - E. Seidel | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:05 | atp_wta | women | K. Siniakova - Y. Yuan | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:30 | atp_wta | men | A. Kovacevic - M. Mmoh | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 14:30 | challenger | men | D. Jorda Sanchis - T. Boyer | api_mapping | exact_name | safe_both_players | 11 |
| 2026-06-13 | 14:30 | atp_wta | men | H. Wendelken - A. Walton | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 14:30 | qualifying | men | J. De Jong - E. Dalla Valle | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 14:30 | atp_wta | men | J. Duckworth - A. Vukic | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 14:30 | atp_wta | men | M. Bellucci - M. Kukushkin | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 14:30 | atp_wta | men | M. Landaluce - M. Huesler | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 14:30 | atp_wta | men | R. Collignon - A. Dougaz | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:00 | atp_wta | men | A. Mannarino - A. De Minaur | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | itf | women | A. Prisacariu - L. Perez Alarcon | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 15:00 | atp_wta | women | K. Boulter - D. Vekic | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 15:00 | itf | women | K. Rinaldo Persson - A-L. Friedsam | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 15:00 | challenger | women | M. Stoiana - C. Naef | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | itf | women | N. Podoroska - A. Zantedeschi | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 15:00 | atp_wta | women | P. Udvardy - K. Volynets | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 15:00 | challenger | men | R. Bertola - W. Jansen | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 15:00 | challenger | men | R. Lawlor - J. McCabe | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:00 | challenger | men | S. Kwon - M. Hurrion | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:30 | challenger | men | A. Matusevich - G. Den Ouden | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 16:00 | challenger | men | D. E. Galan - F. Balshaw | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 16:00 | atp_wta | women | L. Sun - A. Kalinina | exact_name | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:00 | atp_wta | women | P. Kudermetova - S. Kraus | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:00 | qualifying | men | R. Carballes Baena - F. Forti | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 16:30 | atp_wta | women | A. Dudeney - Y. Putintseva | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:30 | atp_wta | men | D. Evans - M. Giron | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 16:30 | atp_wta | men | D. Prizmic - R. Hijikata | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 16:30 | atp_wta | men | J. Monday - G. Mpetshi Perricard | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 16:30 | challenger | men | O. Okonkwo - H. Grenier | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 16:30 | atp_wta | women | V. Golubic - V. Erjavec | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:30 | challenger | men | Z. Zhang - M. Ceban | exact_name | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 17:00 | atp_wta | women | C. McNally - M. Stojsavljevic | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 17:00 | itf | men | G. Piraino - F. Tabacco | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 17:00 | itf | men | S. Gorzny - E. Aguiard | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 17:30 | challenger | men | G. I. Justo - L. E. Ambrogi | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 18:00 | challenger | men | A. Holmgren - M. Basing | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | challenger | men | D. Masur - J. Clarke | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | itf | men | O. Baris - A. Fenty | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | atp_wta | women | O. Selekhmeteva - K. Rakhimova | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | atp_wta | women | Z. Sonmez - L. Tararudee | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 18:30 | qualifying | women | V. Jimenez Kasintseva - K. Kawa | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 19:30 | itf | women | M. Brengle - S. Yamalapalli | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 20:00 | qualifying | women | L. Bronzetti - L. Samson | api_mapping | api_mapping | safe_both_players | 4 |

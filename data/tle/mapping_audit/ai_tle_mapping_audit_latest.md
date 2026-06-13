# AI TLE Mapping Audit

Generated: `2026-06-13T06:03:12+00:00`
Date range: `2026-06-13` â `2026-06-13`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 202 |
| api_odds_events | 115 |
| odds_events_with_fixture | 115 |
| audited_events | 111 |
| audited_player_appearances | 222 |
| safe_player_appearances | 214 |
| review_player_appearances | 8 |
| safe_events_both_players | 103 |
| review_events_any_player | 8 |
| safe player % | 96.40% |
| review player % | 3.60% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 8 |
| api_mapping | 206 |
| exact_name | 8 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 22522 | A. Teixido Garcia | women | itf | api_key_unmapped | women:api:22522 |  | 1 | E. Lene - A. Teixido Garcia | W35 Casablanca |
| 17463 | Dar. Blanch | men | challenger | api_key_unmapped | men:api:17463 |  | 1 | Dar. Blanch - J. Fearnley | Ilkley |
| 15344 | J. Adams | women | itf | api_key_unmapped | women:api:15344 |  | 1 | J. Adams - I. Yoruk | W15 Kayseri 4 |
| 103787 | M. Steinkamp | women | atp_wta | api_key_unmapped | women:api:103787 |  | 1 | M. Steinkamp - S. Zhang | Berlin |
| 12869 | M. Timofeeva | women | atp_wta | api_key_unmapped | women:api:12869 |  | 1 | M. Timofeeva - R. Zarazua | Berlin |
| 102950 | P. Perez Ramos | men | itf | api_key_unmapped | men:api:102950 |  | 1 | P. Martinez Gomez - P. Perez Ramos | M25 Martos |
| 1812 | Xin. Wang | women | atp_wta | api_key_unmapped | women:api:1812 |  | 1 | Xin. Wang - D. Galfi | Berlin |
| 796 | Y. Bu | men | challenger | api_key_unmapped | men:api:796 |  | 1 | M. Lajal - Y. Bu | Ilkley |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-13 | 09:00 | itf | women | J. Adams - I. Yoruk | api_key_unmapped | api_mapping | review_any_player | 10 |
| 2026-06-13 | 11:00 | itf | women | E. Lene - A. Teixido Garcia | api_mapping | api_key_unmapped | review_any_player | 9 |
| 2026-06-13 | 11:00 | atp_wta | women | M. Steinkamp - S. Zhang | api_key_unmapped | api_mapping | review_any_player | 0 |
| 2026-06-13 | 12:00 | challenger | men | Dar. Blanch - J. Fearnley | api_key_unmapped | api_mapping | review_any_player | 12 |
| 2026-06-13 | 12:00 | challenger | men | M. Lajal - Y. Bu | api_mapping | api_key_unmapped | review_any_player | 12 |
| 2026-06-13 | 12:00 | itf | men | P. Martinez Gomez - P. Perez Ramos | api_mapping | api_key_unmapped | review_any_player | 4 |
| 2026-06-13 | 14:00 | atp_wta | women | M. Timofeeva - R. Zarazua | api_key_unmapped | api_mapping | review_any_player | 9 |
| 2026-06-13 | 16:00 | atp_wta | women | Xin. Wang - D. Galfi | api_key_unmapped | api_mapping | review_any_player | 8 |
| 2026-06-13 | 08:30 | itf | women | M. Kubka - G. Knutson | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 08:30 | itf | women | P. Iatcenko - A. Tikhonova | api_mapping | exact_name | safe_both_players | 11 |
| 2026-06-13 | 09:00 | itf | men | I. Marrero Curbelo - D. Dinev | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 10:00 | itf | men | A. Thanos - N. McDonald | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 10:00 | itf | women | A. Zolotareva - K. Zaytseva | exact_name | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 10:00 | itf | men | F. Peliwo - G. Dalmasso | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 10:00 | itf | men | H. Bernet - S. Kopp | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 10:00 | itf | men | J. Guilleme - L. Rossi | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 10:00 | itf | men | M. Sharipov - K. Kivattsev | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 10:00 | itf | men | V. Orlov - V. Bielinskyi | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 10:30 | itf | men | M. Walters - D. Mosejczuk | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 10:30 | itf | men | R. Izquierdo Luque - J. Domingues | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 10:30 | itf | men | R. Pascual Ferra - C. Bouchelaghem | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 10:30 | itf | women | V. Milovanova - L. Ayala | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 11:00 | itf | women | A. Falei - M. Leonard | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 11:00 | atp_wta | women | B. Krejcikova - M. Linette | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 11:00 | itf | women | C. Gallardo Guevara - B. Ivanova | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 11:00 | atp_wta | women | C. McNally - A. Tomljanovic | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 11:00 | atp_wta | men | D. Dedura - N. Basilashvili | exact_name | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 11:00 | itf | women | K. Kuzmova - S. Broadus | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 11:00 | atp_wta | men | L. Sonego - F. C. Jianu | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 11:00 | atp_wta | women | M. Frech - A. Sasnovich | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 11:00 | itf | women | M. Weckerle - V. Steiner | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 11:00 | atp_wta | women | N. Bartunkova - N. Noha Akugue | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 11:00 | itf | women | N. Vargova - L. Vujovic | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 11:00 | itf | women | R. Roura Llaverias - M. Soriano Santiago | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 11:30 | challenger | men | A. Shevchenko - V. Sachko | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-13 | 11:30 | itf | men | G. Kravchenko - J. Kumstat | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 11:30 | itf | men | S. Perez Contri - I. Biletic | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:00 | atp_wta | men | B. Shelton - S. Shimabukuro | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 12:00 | challenger | men | D. Sweeny - T. Samuel | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:00 | atp_wta | women | E. Arango - A. Bondar | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 12:00 | challenger | men | H. Jefferson - A. Gray | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:00 | itf | men | J. Sperle - A. Boros | api_mapping | exact_name | safe_both_players | 1 |
| 2026-06-13 | 12:00 | challenger | men | O. Tarvet - F. Romano | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 12:00 | atp_wta | women | S. Kenin - E. Jacquemot | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 12:00 | challenger | men | T. Skatov - J. Watt | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 12:30 | atp_wta | men | B. Sanchez Martinez - R. Bautista-Agut | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:30 | atp_wta | men | D. Medvedev - M. Cilic | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-13 | 12:30 | itf | women | E. Bennemann - T. Gadamauri | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 12:30 | atp_wta | men | J. Mackenzie - A. Bolt | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 12:30 | atp_wta | women | M. Pohankova - T. Korpatsch | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 12:30 | atp_wta | women | P. Marcinko - A. Ito | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 12:30 | atp_wta | men | T. Pereira - T. Gentzsch | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 13:00 | atp_wta | men | A. Bublik - T. Fritz | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-13 | 13:00 | itf | women | A. Granwehr - J. Lim | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 13:00 | challenger | men | F. Cina - T. Daniel | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 13:00 | itf | women | I. Primorac - E. Avanesyan | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 13:00 | atp_wta | men | M. Damm - D. Merida Aguilar | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 13:00 | itf | men | O. Krutykh - D. Petak | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 13:00 | itf | men | S. Cuenin - B. Djuric | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 13:00 | atp_wta | men | Z. Svajda - L. Broady | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 13:30 | atp_wta | women | A. Ruzic - K. Juvan | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 13:30 | atp_wta | women | E. Raducanu - K. Rakhimova | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 13:30 | atp_wta | women | H. Klugman - A. Zakharova | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 13:30 | challenger | men | L. Nardi - O. Weightman | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 13:30 | challenger | men | P. Brady - G. Hussey | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 14:00 | challenger | women | A. Krueger - D. Vidmanova | exact_name | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 14:00 | atp_wta | women | D. Kasatkina - A. Blinkova | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:00 | atp_wta | women | D. Parry - E. Seidel | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:00 | atp_wta | women | K. Siniakova - Y. Yuan | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 14:30 | atp_wta | men | A. Kovacevic - M. Mmoh | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 14:30 | challenger | men | D. Jorda Sanchis - T. Boyer | api_mapping | exact_name | safe_both_players | 11 |
| 2026-06-13 | 14:30 | atp_wta | men | H. Wendelken - A. Walton | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 14:30 | qualifying | men | J. De Jong - E. Dalla Valle | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-13 | 14:30 | atp_wta | men | J. Duckworth - A. Vukic | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 14:30 | atp_wta | men | M. Bellucci - M. Kukushkin | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 14:30 | atp_wta | men | M. Landaluce - M. Huesler | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 14:30 | atp_wta | men | R. Collignon - A. Dougaz | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:00 | atp_wta | men | A. Mannarino - A. De Minaur | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | itf | women | A. Prisacariu - L. Perez Alarcon | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | atp_wta | women | K. Boulter - D. Vekic | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-13 | 15:00 | itf | women | K. Rinaldo Persson - A-L. Friedsam | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | challenger | women | M. Stoiana - C. Naef | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-13 | 15:00 | itf | women | N. Podoroska - A. Zantedeschi | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 15:00 | atp_wta | women | P. Udvardy - K. Volynets | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 15:00 | challenger | men | R. Bertola - W. Jansen | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 15:00 | challenger | men | R. Lawlor - J. McCabe | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:00 | challenger | men | S. Kwon - M. Hurrion | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 15:30 | challenger | men | A. Matusevich - G. Den Ouden | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 16:00 | challenger | men | D. E. Galan - F. Balshaw | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 16:00 | atp_wta | women | L. Sun - A. Kalinina | exact_name | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 16:00 | atp_wta | women | P. Kudermetova - S. Kraus | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:00 | qualifying | men | R. Carballes Baena - F. Forti | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-13 | 16:30 | atp_wta | women | A. Dudeney - Y. Putintseva | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:30 | atp_wta | men | D. Evans - M. Giron | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 16:30 | atp_wta | men | D. Prizmic - R. Hijikata | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-13 | 16:30 | atp_wta | men | J. Monday - G. Mpetshi Perricard | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-13 | 16:30 | challenger | men | O. Okonkwo - H. Grenier | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 16:30 | atp_wta | women | V. Golubic - V. Erjavec | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 16:30 | challenger | men | Z. Zhang - M. Ceban | exact_name | api_mapping | safe_both_players | 0 |
| 2026-06-13 | 17:00 | atp_wta | women | C. McNally - M. Stojsavljevic | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 17:00 | itf | men | G. Piraino - F. Tabacco | api_mapping | api_mapping | safe_both_players | 3 |
| 2026-06-13 | 17:00 | itf | men | O. Baris - A. Fenty | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 17:00 | itf | men | S. Gorzny - E. Aguiard | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 17:30 | challenger | men | G. I. Justo - L. E. Ambrogi | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-13 | 18:00 | challenger | men | A. Holmgren - M. Basing | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | challenger | men | D. Masur - J. Clarke | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | atp_wta | women | O. Selekhmeteva - K. Rakhimova | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-13 | 18:00 | atp_wta | women | Z. Sonmez - L. Tararudee | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-13 | 18:30 | qualifying | women | V. Jimenez Kasintseva - K. Kawa | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-13 | 19:30 | itf | women | M. Brengle - S. Yamalapalli | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-13 | 20:00 | qualifying | women | L. Bronzetti - L. Samson | api_mapping | api_mapping | safe_both_players | 4 |

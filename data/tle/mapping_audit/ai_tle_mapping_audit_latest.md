# AI TLE Mapping Audit

Generated: `2026-06-20T09:52:58+00:00`
Date range: `2026-06-20` â `2026-06-20`

## Summary

| Metric | Value |
|---|---:|
| api_fixture_events | 195 |
| api_odds_events | 104 |
| odds_events_with_fixture | 104 |
| audited_events | 63 |
| audited_player_appearances | 126 |
| safe_player_appearances | 116 |
| review_player_appearances | 10 |
| safe_events_both_players | 53 |
| review_events_any_player | 10 |
| safe player % | 92.06% |
| review player % | 7.94% |

## Resolve methods

| Method | Count |
|---|---:|
| api_key_unmapped | 3 |
| api_mapping | 111 |
| exact_name | 5 |
| unique_surname_initial | 7 |

## Players needing review

| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |
|---:|---|---|---|---|---|---|---:|---|---|
| 13987 | A. Sobolieva | women | qualifying | api_key_unmapped | women:api:13987 |  | 1 | Xiy. Wang - A. Sobolieva | Brescia (Italy) - Qualification |
| 1249 | B. Nakashima | men | itf | api_key_unmapped | men:api:1249 |  | 1 | B. Nakashima - K. Miyoshi | M15 Irvine |
| 421 | C. O'Connell | men | challenger | api_key_unmapped | men:api:421 |  | 1 | O. Virtanen - C. O'Connell | Nottingham |
| 70319 | A. Stoyanov | women | itf | unique_surname_initial | women:sackmann:267422 | Antonia Stoyanov | 1 | M. Maquet - A. Stoyanov | W15 Dinard |
| 54824 | C. Rolland de Ravel | men | challenger | unique_surname_initial | men:sackmann:213977 | Cosme Rolland De Ravel | 1 | C. Rolland de Ravel - M. Alcala Gurri | Royan |
| 447 | L. Noskova | women | atp_wta | unique_surname_initial | women:sackmann:222328 | Linda Noskova | 1 | L. Noskova - A. Eala | Berlin |
| 53046 | L. Tagger | women | atp_wta | unique_surname_initial | women:sackmann:260172 | Lilli Tagger | 1 | A. Zakharova - L. Tagger | Eastbourne |
| 70149 | M. Thamm | women | atp_wta | unique_surname_initial | women:sackmann:265701 | Mariella Thamm | 1 | R. Zarazua - M. Thamm | Bad Homburg |
| 3706 | S. Kirchheimer | men | itf | unique_surname_initial | men:sackmann:126177 | Strong Kirchheimer | 1 | S. Johnson - S. Kirchheimer | M15 Irvine |
| 3214 | T. Townsend | women | atp_wta | unique_surname_initial | women:sackmann:203501 | Taylor Townsend | 1 | M. Trevisan - T. Townsend | Bad Homburg |

## Event audit

| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |
|---|---|---|---|---|---|---|---|---:|
| 2026-06-20 | 13:30 | atp_wta | women | A. Zakharova - L. Tagger | api_mapping | unique_surname_initial | review_any_player | 9 |
| 2026-06-20 | 14:00 | atp_wta | women | L. Noskova - A. Eala | unique_surname_initial | api_mapping | review_any_player | 12 |
| 2026-06-20 | 14:00 | atp_wta | women | M. Trevisan - T. Townsend | api_mapping | unique_surname_initial | review_any_player | 0 |
| 2026-06-20 | 14:00 | atp_wta | women | R. Zarazua - M. Thamm | api_mapping | unique_surname_initial | review_any_player | 6 |
| 2026-06-20 | 14:30 | challenger | men | C. Rolland de Ravel - M. Alcala Gurri | unique_surname_initial | api_mapping | review_any_player | 12 |
| 2026-06-20 | 14:30 | itf | women | M. Maquet - A. Stoyanov | api_mapping | unique_surname_initial | review_any_player | 10 |
| 2026-06-20 | 15:00 | challenger | men | O. Virtanen - C. O'Connell | api_mapping | api_key_unmapped | review_any_player | 11 |
| 2026-06-20 | 16:00 | qualifying | women | Xiy. Wang - A. Sobolieva | exact_name | api_key_unmapped | review_any_player | 12 |
| 2026-06-20 | 20:00 | itf | men | S. Johnson - S. Kirchheimer | exact_name | unique_surname_initial | review_any_player | 1 |
| 2026-06-20 | 21:00 | itf | men | B. Nakashima - K. Miyoshi | api_key_unmapped | api_mapping | review_any_player | 1 |
| 2026-06-20 | 11:55 | itf | women | S. Janicijevic - L. Encheva | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-20 | 12:00 | atp_wta | women | A. Sabalenka - J. Pegula | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 12:00 | atp_wta | women | C. Osorio - A. Tomljanovic | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 12:00 | itf | women | E. Seibold - B. Passola | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-20 | 12:00 | atp_wta | women | I. Spink - K. Birrell | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-20 | 12:00 | atp_wta | women | Ka. Pliskova - M. Bouzkova | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 12:00 | atp_wta | women | L. Tararudee - V. Erjavec | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-20 | 12:00 | itf | women | L. Vujovic - D. Egorova | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 12:00 | atp_wta | men | M. Arnaldi - A. Gray | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 12:00 | itf | men | M. Vankan - M. Zielinski | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-20 | 12:00 | itf | women | N. Vargova - M. Colmegna | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 12:00 | atp_wta | women | O. Oliynykova - S. Johnson | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-20 | 12:00 | itf | men | T. Genier - S. Kopp | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-20 | 12:00 | atp_wta | men | T. Samuel - Q. Halys | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 12:30 | atp_wta | women | A. Blinkova - Y. Putintseva | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-20 | 12:30 | atp_wta | men | A. Shevchenko - A. Shelbayh | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 12:30 | atp_wta | men | A. Walton - F. Bondioli | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-20 | 12:30 | itf | men | P. Martinez Gomez - T. Torres | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 12:30 | atp_wta | women | S. Sierra - E. Seidel | api_mapping | api_mapping | safe_both_players | 10 |
| 2026-06-20 | 13:00 | atp_wta | men | F. Romano - M. Cassone | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 13:30 | qualifying | women | A. Charaeva - A. Aksu | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 13:30 | atp_wta | women | E. Arango - A. Parks | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-20 | 13:30 | atp_wta | men | E. Nava - H. Stewart | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 13:30 | atp_wta | women | E. Navarro - V. Golubic | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 13:30 | atp_wta | men | H. Wendelken - A. Vukic | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 13:30 | atp_wta | women | P. Stearns - E. Appleton | api_mapping | api_mapping | safe_both_players | 5 |
| 2026-06-20 | 13:30 | atp_wta | women | S. Kenin - D. Snigur | api_mapping | api_mapping | safe_both_players | 6 |
| 2026-06-20 | 13:30 | atp_wta | women | Z. Sonmez - H. Vandewinkel | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 14:00 | atp_wta | men | B. Nakashima - F. Cerundolo | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 14:00 | challenger | men | F. Diaz Acosta - G. Heide | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-20 | 14:30 | atp_wta | men | M. Kukushkin - D. Dzumhur | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 15:00 | atp_wta | men | A. Zverev - T. Fritz | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 15:00 | atp_wta | men | F. Gill - M. Trungelliti | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-20 | 15:00 | atp_wta | men | J. Duckworth - G. Hussey | api_mapping | api_mapping | safe_both_players | 4 |
| 2026-06-20 | 15:00 | atp_wta | men | J. Mackenzie - D. Rincon | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-20 | 15:00 | atp_wta | women | K. Rakhimova - O. Selekhmeteva | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 15:00 | atp_wta | women | P. Marcinko - S. Waltert | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-20 | 15:30 | atp_wta | women | P. Badosa - S. Kraus | api_mapping | api_mapping | safe_both_players | 2 |
| 2026-06-20 | 15:30 | atp_wta | women | S. Zhang - G. Ruse | api_mapping | exact_name | safe_both_players | 11 |
| 2026-06-20 | 15:30 | atp_wta | men | T. Paul - U. Humbert | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 16:00 | itf | women | M. Vogt - L. Claeys | api_mapping | api_mapping | safe_both_players | 9 |
| 2026-06-20 | 16:00 | atp_wta | men | Z. Svajda - M. Huesler | api_mapping | api_mapping | safe_both_players | 8 |
| 2026-06-20 | 16:30 | atp_wta | men | D. Altmaier - F. Tiafoe | api_mapping | api_mapping | safe_both_players | 12 |
| 2026-06-20 | 16:30 | atp_wta | men | J. Choinski - Y. Wu | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-20 | 16:30 | atp_wta | men | M. Giron - C. Broom | api_mapping | api_mapping | safe_both_players | 7 |
| 2026-06-20 | 17:30 | qualifying | women | M. Sherif - E. Yaneva | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-20 | 18:00 | itf | men | A. Martin - J.J. Wolf | exact_name | exact_name | safe_both_players | 1 |
| 2026-06-20 | 18:00 | itf | men | G. Young - A. Fenty | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-20 | 18:00 | itf | men | I. Almazan Valiente - R. Nijboer | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-20 | 18:00 | challenger | men | S. Ofner - L. van Assche | api_mapping | api_mapping | safe_both_players | 11 |
| 2026-06-20 | 20:00 | itf | women | A. Shcherbinina - M. Castillo Meza | api_mapping | api_mapping | safe_both_players | 0 |
| 2026-06-20 | 21:00 | itf | women | K. Carnicella - M. Ekstrand | api_mapping | api_mapping | safe_both_players | 1 |
| 2026-06-20 | 23:00 | qualifying | men | N. Hardt - J. Estevez | api_mapping | api_mapping | safe_both_players | 1 |

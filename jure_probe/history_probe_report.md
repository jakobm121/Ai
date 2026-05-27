# API-Tennis History Probe

Generated at: **2026-05-28T00:48:37.060324+02:00**

## Config

- Base URL: `https://api.api-tennis.com/tennis/`
- API key present: **True**
- Main method: `get_fixtures`
- Date range: **2026-05-19 â 2026-05-28**
- Raw sample limit: **300 items**

## Tried query variants

| Variant | OK | Status | Items | API success | Error/message |
|---|---:|---:|---:|---:|---|
| `range_date_start_date_stop` | True | 200 | 3441 | 1 |  |
| `range_from_to` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `single_date` | True | 200 | 2 | None | 1 |
| `get_events_range_date_start_date_stop` | True | 200 | 27 | 1 |  |

## Best variant

- Name: `range_date_start_date_stop`
- Items: **3441**

## Overall

- Total unique match/event items found: **3490**
- Unique fields found: **56**

## Top fields

| Field | Count | Types | Example |
|---|---:|---|---|
| `pointbypoint[].points[].number_point` | 35493 | str:35493 | 1 |
| `pointbypoint[].points[].score` | 35493 | str:35493 | 15 - 0 |
| `pointbypoint[].points[].break_point` | 35493 | null:31443, str:4050 | None |
| `pointbypoint[].points[].set_point` | 35493 | null:35493 | None |
| `pointbypoint[].points[].match_point` | 35493 | null:35493 | None |
| `pointbypoint[].set_number` | 8131 | str:8131 | Set 1 |
| `pointbypoint[].number_game` | 8131 | str:8131 | 1 |
| `pointbypoint[].player_served` | 8131 | str:8131 | Second Player |
| `pointbypoint[].serve_winner` | 8131 | str:8131 | Second Player |
| `pointbypoint[].serve_lost` | 8131 | null:5498, str:2633 | None |
| `pointbypoint[].score` | 8131 | str:8131 | 0 - 1 |
| `pointbypoint[].points` | 8131 | list:8131 | None |
| `pointbypoint[].points[]` | 8131 | list_items:42607 | None |
| `scores[].score_first` | 7277 | str:7277 | 3 |
| `scores[].score_second` | 7277 | str:7277 | 6 |
| `scores[].score_set` | 7277 | str:7277 | 1 |
| `statistics[].player_key` | 4165 | int:4165 | 2169 |
| `statistics[].stat_period` | 4165 | str:4165 | match |
| `statistics[].stat_type` | 4165 | str:4165 | Service |
| `statistics[].stat_name` | 4165 | str:4165 | Aces |
| `statistics[].stat_value` | 4165 | str:4165 | 1 |
| `statistics[].stat_won` | 4165 | null:2501, int:1664 | None |
| `statistics[].stat_total` | 4165 | null:2501, int:1664 | None |
| `_probe_variant` | 3490 | str:3490 | range_date_start_date_stop |
| `_probe_date` | 3490 | null:3470, str:20 | None |
| `event_type_type` | 3468 | str:3468 | Atp Singles |
| `event_key` | 3441 | int:3441 | 12127985 |
| `event_date` | 3441 | str:3441 | 2026-05-19 |
| `event_time` | 3441 | str:3441 | 15:35 |
| `event_first_player` | 3441 | str:3441 | J. Brooksby |
| `first_player_key` | 3441 | int:3441 | 2169 |
| `event_second_player` | 3441 | str:3441 | C. Ruud |
| `second_player_key` | 3441 | int:3441 | 430 |
| `event_final_result` | 3441 | str:3441 | 0 - 2 |
| `event_game_result` | 3441 | str:3441 | - |
| `event_serve` | 3441 | null:3438, str:3 | None |
| `event_winner` | 3441 | str:2965, null:476 | Second Player |
| `event_status` | 3441 | str:3441 | Finished |
| `tournament_name` | 3441 | str:3441 | Geneva |
| `tournament_key` | 3441 | int:3441 | 2207 |
| `tournament_round` | 3441 | str:3438, null:3 | ATP Geneva - 1/16-finals |
| `tournament_season` | 3441 | str:3441 | 2026 |
| `event_live` | 3441 | str:3441 | 0 |
| `event_first_player_logo` | 3441 | str:1784, null:1657 | https://api.api-tennis.com/logo-tennis/2169_j-brooksby.jpg |
| `event_second_player_logo` | 3441 | str:1782, null:1659 | https://api.api-tennis.com/logo-tennis/430_c-ruud.jpg |
| `event_qualification` | 3441 | str:3437, null:4 | False |
| `pointbypoint` | 3441 | list:3441 | None |
| `pointbypoint[]` | 3441 | list_items:42142 | None |
| `scores` | 3441 | list:3441 | None |
| `scores[]` | 3441 | list_items:7277 | None |
| `statistics` | 3441 | list:3441 | None |
| `statistics[]` | 3441 | list_items:107756 | None |
| `event_type_key` | 27 | int:27 | 267 |
| `param` | 22 | str:22 | date_start |
| `msg` | 22 | str:22 | Required parameter missing |
| `cod` | 22 | int:22 | 201 |

## Match samples

| Key | Date | Time | Tournament | Round | Player 1 | Player 2 | Status | Final | Sets |
|---|---|---|---|---|---|---|---|---|---|
| 12127985 | 2026-05-19 | 15:35 | Geneva | None | J. Brooksby | C. Ruud | Finished | 0 - 2 |  |
| 12127986 | 2026-05-19 | 20:00 | Geneva | None | L. Djere | J. M. Cerundolo | Cancelled | - |  |
| 12127987 | 2026-05-19 | 18:10 | Geneva | None | A. Mannarino | R. Collignon | Finished | 0 - 2 |  |
| 12127994 | 2026-05-19 | 12:10 | Strasbourg | None | Kichenok/ Krawczyk | Mihalikova/ Nicholls | Finished | 2 - 0 |  |
| 12127995 | 2026-05-19 | 14:05 | Strasbourg | None | Kozyreva/ Panova | Bucsa/ Melichar-Martinez | Finished | 2 - 1 |  |
| 12128044 | 2026-05-19 | 14:05 | Hamburg | None | F. Auger-Aliassime | V. Kopriva | Finished | 2 - 0 |  |
| 12128046 | 2026-05-19 | 13:10 | Hamburg | None | L. Darderi | R. A. Burruchaga | Finished | 2 - 0 |  |
| 12128049 | 2026-05-19 | 15:50 | Hamburg | None | J. Engel | U. Humbert | Finished | 1 - 2 |  |
| 12128051 | 2026-05-19 | 14:00 | Hamburg | None | M. Kecmanovic | K. Khachanov | Cancelled | - |  |
| 12128056 | 2026-05-19 | 13:05 | Geneva | None | Frantzen/ Haase | Tsitsipas/ Tsitsipas | Finished | 2 - 1 |  |
| 12128057 | 2026-05-19 | 11:10 | Geneva | None | Krajicek/ Mektic | Kirkov/ Stevens | Finished | 1 - 2 |  |
| 12128059 | 2026-05-19 | 12:10 | Geneva | None | Behar/ Pavic | Arends/ Pel | Finished | 1 - 2 |  |
| 12128061 | 2026-05-19 | 15:00 | Geneva | None | Paul/ Stricker | Galloway/ Peers | Finished | 2 - 0 |  |
| 12128075 | 2026-05-19 | 10:40 | Strasbourg | None | D. Parry | E. Raducanu | Finished | 2 - 0 |  |
| 12128076 | 2026-05-19 | 10:00 | Strasbourg | None | M. Keys | C. Bucsa | Cancelled | - |  |
| 12128092 | 2026-05-19 | 15:45 | Rabat | None | Y. Starodubtseva | A. Fita Boluda | Finished | 2 - 0 |  |
| 12128094 | 2026-05-19 | 12:05 | Rabat | None | S. Nahimana | A. Tomljanovic | Finished | 2 - 0 |  |
| 12128095 | 2026-05-19 | 14:45 | Rabat | None | T. Martincova | C. Osorio | Finished | 0 - 2 |  |
| 12128096 | 2026-05-19 | 13:50 | Rabat | None | Y. Kabbaj | B. Cengiz | Finished | 2 - 0 |  |
| 12128097 | 2026-05-19 | 12:05 | Rabat | None | F. Jones | Y. Kotliar | Finished | 1 - 2 |  |
| 12128099 | 2026-05-19 | 15:40 | Rabat | None | D. El Jardi | T. Maria | Finished | 0 - 2 |  |
| 12128100 | 2026-05-19 | 16:25 | Rabat | None | E. Arango | E. Seidel | Finished | 2 - 1 |  |
| 12128159 | 2026-05-19 | 12:55 | Bengaluru 3 (India) - Qualification | None | P. Dev S D | I. Ivashka | Finished | 0 - 2 |  |
| 12128160 | 2026-05-19 | 14:35 | Bengaluru 3 (India) - Qualification | None | O. Jasika | S. Rawat | Finished | 0 - 2 |  |
| 12128161 | 2026-05-19 | 09:45 | Bengaluru 3 (India) - Qualification | None | M. Jones | M. Sasikumar | Finished | 0 - 2 |  |
| 12128162 | 2026-05-19 | 12:15 | Bengaluru 3 (India) - Qualification | None | K. Lee | K. Tyagi | Finished | 0 - 2 |  |
| 12128163 | 2026-05-19 | 08:00 | Bengaluru 3 (India) - Qualification | None | R. Matsuda | Y. Takahashi | Finished | 0 - 2 |  |
| 12128164 | 2026-05-19 | 08:30 | Bengaluru 3 (India) - Qualification | None | D. Palan | K. Isomura | Finished | 2 - 1 |  |
| 12128165 | 2026-05-19 | 06:40 | Bengaluru 3 (India) - Qualification | None | D. Singh | L. Vithoontien | Finished | 0 - 2 |  |
| 12128166 | 2026-05-19 | 07:50 | Bengaluru 3 (India) - Qualification | None | K. Singh | W. K. Leong M. | Finished | 1 - 2 |  |
| 12128167 | 2026-05-19 | 13:55 | Bengaluru 3 (India) - Qualification | None | K. Smith | M. Sureshkumar | Finished | 1 - 2 |  |
| 12128168 | 2026-05-19 | 11:05 | Bengaluru 3 (India) - Qualification | None | H. Stewart | A. Vishal Balsekar | Finished | 2 - 1 |  |
| 12128172 | 2026-05-19 | 11:50 | Cervia (Italy) - Qualification | None | A. Guerrieri | O. Prihodko | Finished | 2 - 1 |  |
| 12128173 | 2026-05-19 | 16:30 | Cervia (Italy) - Qualification | None | I. Ivanov | F. Roncadelli | Cancelled | - |  |
| 12128175 | 2026-05-19 | 18:10 | Cervia (Italy) - Qualification | None | M. Kouame | J. Vasami | Finished | 0 - 2 |  |
| 12128176 | 2026-05-19 | 10:00 | Cervia (Italy) - Qualification | None | L. Marmousez | F. Bondioli | Cancelled | - |  |
| 12128177 | 2026-05-19 | 11:45 | Cervia (Italy) - Qualification | None | L. Rottoli | G. Piraino | Finished | 0 - 2 |  |
| 12128178 | 2026-05-19 | 10:00 | Cervia (Italy) - Qualification | None | I. Xilas | M. Ribecai | Finished | 0 - 2 |  |
| 12128180 | 2026-05-19 | 14:50 | Istanbul (Turkey) - Qualification | None | B. Hassan | F. C. Jianu | Finished | 2 - 0 |  |
| 12128181 | 2026-05-19 | 14:15 | Istanbul (Turkey) - Qualification | None | D. Kuzmanov | D. Rincon | Finished | 2 - 0 |  |
| 12128185 | 2026-05-19 | 10:00 | Istanbul (Turkey) - Qualification | None | T. Monteiro | I. Montes-De La Torre | Cancelled | - |  |
| 12128187 | 2026-05-19 | 13:05 | Istanbul (Turkey) - Qualification | None | A. Nedic | S. Fomin | Finished | 2 - 0 |  |
| 12128192 | 2026-05-19 | 16:20 | Hamburg | None | Arribage/ Olivetti | Jebens/ Ruehl | Finished | 2 - 1 |  |
| 12128193 | 2026-05-19 | 11:10 | Hamburg | None | Krawietz/ Puetz | Nys/ Roger-Vasselin | Finished | 2 - 0 |  |
| 12128195 | 2026-05-19 | 14:35 | Hamburg | None | Cabral/ Salisbury | Schnaitter/ Wallner | Finished | 1 - 2 |  |
| 12128211 | 2026-05-19 | 17:30 | Rabat | None | Aoyama/ Liang | Feng/ Tang | Finished | 2 - 1 |  |
| 12128213 | 2026-05-19 | 18:15 | Rabat | None | Karamoko/ Marcinko | Kichenok/ Ninomiya | Finished | 2 - 1 |  |
| 12128217 | 2026-05-19 | 17:05 | Rabat | None | Sutjiadi/ Zvonareva | Fossa Huergo/ Kulambayeva | Finished | 2 - 0 |  |
| 12128218 | 2026-05-19 | 07:30 | Bengaluru 3 (India) | None | Bouzige/ Jasika | Kalyanpur/ Sasikumar | Cancelled | - |  |
| 12128226 | 2026-05-19 | 17:05 | Istanbul (Turkey) | None | Chandrasekar/ Lammons | Britto/ Saraiva Dos Santos | Finished | 2 - 0 |  |
| 12128231 | 2026-05-19 | 16:05 | Istanbul (Turkey) | None | Barton/ Vrbensky | Jecan/ Pavel | Finished | 1 - 2 |  |
| 12128232 | 2026-05-19 | 17:45 | Istanbul (Turkey) | None | Martos Gornes/ Walkow | Ayeni/ Cook | Finished | 2 - 0 |  |
| 12128234 | 2026-05-19 | 13:20 | Strasbourg | None | A. Li | E. Alexandrova | Finished | 2 - 1 |  |
| 12128239 | 2026-05-19 | 14:45 | Strasbourg | None | Eikeri/ Gleason | Maleckova/ Skoch | Finished | 2 - 0 |  |
| 12128243 | 2026-05-19 | 12:10 | Hamburg | None | F. Cobolli | I. Buse | Finished | 0 - 2 |  |
| 12128244 | 2026-05-19 | 10:00 | Hamburg | None | Z. Bergs | A. Gea | Cancelled | - |  |
| 12128247 | 2026-05-19 | 18:50 | Strasbourg | None | V. Mboko | L. Boisson | Finished | 2 - 0 |  |
| 12128253 | 2026-05-19 | 10:30 | Geneva | None | A. Popyrin | C. Tabur | Finished | 2 - 1 |  |
| 12128254 | 2026-05-19 | 14:05 | Geneva | None | N. Basavareddy | J. Munar | Finished | 0 - 2 |  |
| 12128336 | 2026-05-19 | 09:30 | M15 Klagenfurt | None | S. Zick | A. Oetzbach | Finished | 0 - 2 |  |
| 12128337 | 2026-05-19 | 12:00 | M15 Klagenfurt | None | P. Fajta | M. Plunger | Finished | 2 - 1 |  |
| 12128366 | 2026-05-19 | 18:15 | French Open | None | L. Broady | G. Cadenasso | Finished | 0 - 2 |  |
| 12128367 | 2026-05-19 | 19:55 | French Open | None | N. Budkov Kjaer | G. A. Bailly | Finished | 2 - 1 |  |
| 12128368 | 2026-05-19 | 16:55 | French Open | None | J. Choinski | A. Andrade | Finished | 2 - 0 |  |
| 12128369 | 2026-05-19 | 13:20 | French Open | None | S. Cuenin | H. Dellien | Finished | 0 - 2 |  |
| 12128370 | 2026-05-19 | 13:20 | French Open | None | M. Dodig | Y. Zhou | Finished | 2 - 1 |  |
| 12128371 | 2026-05-19 | 15:15 | French Open | None | A. Dougaz | F. Gill | Finished | 1 - 2 |  |
| 12128372 | 2026-05-19 | 12:40 | French Open | None | J. Faria | G. Dimitrov | Finished | 2 - 1 |  |
| 12128373 | 2026-05-19 | 18:00 | French Open | None | N. Fatic | L. Mikrut | Finished | 2 - 0 |  |
| 12128374 | 2026-05-19 | 16:15 | French Open | None | L. Giustino | K. Jacquet | Finished | 0 - 2 |  |
| 12128375 | 2026-05-19 | 11:45 | French Open | None | B. Gojo | S. Gueymard Wayenburg | Finished | 2 - 0 |  |
| 12128376 | 2026-05-19 | 11:50 | French Open | None | G. Heide | D. Added | Finished | 2 - 0 |  |
| 12128377 | 2026-05-19 | 15:45 | French Open | None | P. Herbert | K. Uchida | Finished | 2 - 0 |  |
| 12128378 | 2026-05-19 | 20:10 | French Open | None | J. Kym | T. Gentzsch | Finished | 0 - 2 |  |
| 12128379 | 2026-05-19 | 17:10 | French Open | None | M. Lajal | R. Safiullin | Finished | 0 - 2 |  |
| 12128380 | 2026-05-19 | 13:10 | French Open | None | F. Maestrelli | R. Noguchi | Finished | 2 - 1 |  |
| 12128381 | 2026-05-19 | 18:40 | French Open | None | H. Mayot | T. Barrios Vera | Finished | 1 - 2 |  |
| 12128382 | 2026-05-19 | 11:45 | French Open | None | J. McCabe | Z. Kolar | Finished | 0 - 2 |  |
| 12128383 | 2026-05-19 | 13:15 | French Open | None | L. Midon | R. Carballes Baena | Finished | 0 - 2 |  |
| 12128384 | 2026-05-19 | 13:05 | French Open | None | A. Molcan | O. Crawford | Finished | 2 - 1 |  |

## Files generated

- `jure_probe/history_raw_sample.json`
- `jure_probe/history_fields.json`
- `jure_probe/history_samples.json`
- `jure_probe/history_probe_debug.json`
- `jure_probe/history_probe_report.md`

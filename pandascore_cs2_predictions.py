import os
import json
import math
import time
import hashlib
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
BASE_URL = "https://api.pandascore.co"
TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
PREDICTIONS_FILE = os.path.join(DATA_DIR, "cs2_predictions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "cs2_results.json")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "cs2_past_snapshot.json")

REQUEST_TIMEOUT = 30
API_SLEEP_SECONDS = 0.8

UPCOMING_PER_PAGE = 100
PAST_PAGES = 8
PAST_PER_PAGE = 100

TIME_WINDOW_MIN_HOURS = 0
TIME_WINDOW_MAX_HOURS = 72
MAX_FINAL_PICKS = 10

MIN_MATCHES_PER_TEAM = 3
MIN_PROB_EDGE = 0.035
MIN_CONFIDENCE = 52.0
MIN_SCORE_DIFF = 3.5

SKIP_BO1 = True

DEBUG = True

TIER_BONUS = {
    "s": 5.0,
    "a": 3.0,
    "b": 1.0,
    "c": 0.0,
    "d": -1.0,
}


def debug(msg):
    if DEBUG:
        print(msg)


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def save_json(path, data):
    ensure_dirs()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def headers():
    if not PANDASCORE_API_KEY:
        raise RuntimeError("Missing PANDASCORE_API_KEY environment variable.")

    return {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}",
        "Accept": "application/json",
    }


def api_get(path, params=None, retries=3):
    url = BASE_URL + path
    params = params.copy() if params else {}

    for attempt in range(retries):
        res = requests.get(
            url,
            headers=headers(),
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if res.status_code in {429, 500, 502, 503, 504}:
            wait = (attempt + 1) * 3
            debug(f"API RETRY {res.status_code} {path} sleep={wait}s")
            time.sleep(wait)
            continue

        if res.status_code >= 400:
            raise RuntimeError(f"HTTP {res.status_code} {path}: {res.text[:500]}")

        return res.json()

    raise RuntimeError(f"API failed after retries: {path} {params}")


def parse_dt(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def local_dt(match):
    dt = parse_dt(match.get("begin_at") or match.get("scheduled_at"))

    if not dt:
        return None

    return dt.astimezone(ZoneInfo(TZ_NAME))


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def normalize_team_name(name):
    text = str(name or "").lower().strip()
    text = text.replace("esports", "")
    text = text.replace("esport", "")
    text = text.replace("gaming", "")
    text = text.replace("team", "")
    text = text.replace("academy", "academy")
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text


def get_team_from_opponent(opponent_item):
    if not isinstance(opponent_item, dict):
        return None

    opponent = opponent_item.get("opponent")

    return opponent if isinstance(opponent, dict) else None


def get_teams(match):
    teams = []

    for item in match.get("opponents") or []:
        team = get_team_from_opponent(item)

        if team and team.get("id"):
            teams.append(team)

    return teams


def match_team_names(match):
    teams = get_teams(match)

    if len(teams) >= 2:
        return teams[0].get("name", "Team A"), teams[1].get("name", "Team B")

    return "Team A", "Team B"


def match_name(match):
    home, away = match_team_names(match)
    return f"{home} - {away}"


def get_results_map(match):
    out = {}

    for item in match.get("results") or []:
        team_id = item.get("team_id")

        if team_id is not None:
            out[int(team_id)] = safe_int(item.get("score"), 0)

    return out


def get_tier(match):
    tournament = match.get("tournament") or {}
    tier = tournament.get("tier") or match.get("tier") or ""
    return str(tier or "").lower()


def get_region(match):
    league = match.get("league") or {}
    serie = match.get("serie") or {}
    tournament = match.get("tournament") or {}

    return (
        tournament.get("region")
        or serie.get("region")
        or league.get("region")
        or "unknown"
    )


def game_count(match):
    return safe_int(match.get("number_of_games"), 1)


def is_valid_cs2_match(match):
    teams = get_teams(match)

    if len(teams) < 2:
        return False

    status = str(match.get("status") or "").lower()

    if status not in {"not_started", "not started", "running", "finished"}:
        return False

    return True


def fetch_upcoming():
    params = {
        "per_page": UPCOMING_PER_PAGE,
        "sort": "begin_at",
    }

    data = api_get("/csgo/matches/upcoming", params)
    time.sleep(API_SLEEP_SECONDS)

    return data if isinstance(data, list) else []


def fetch_past():
    all_matches = []

    for page in range(1, PAST_PAGES + 1):
        params = {
            "per_page": PAST_PER_PAGE,
            "page": page,
            "sort": "-begin_at",
        }

        data = api_get("/csgo/matches/past", params)

        if not isinstance(data, list) or not data:
            break

        all_matches.extend(data)

        debug(f"PAST page={page} matches={len(data)} total={len(all_matches)}")

        time.sleep(API_SLEEP_SECONDS)

    save_json(
        SNAPSHOT_FILE,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "matches": all_matches,
        },
    )

    return all_matches


def team_match_result(match, team_id):
    winner_id = match.get("winner_id")
    results = get_results_map(match)

    score_for = results.get(int(team_id), 0)
    score_against = 0

    for tid, score in results.items():
        if tid != int(team_id):
            score_against = score
            break

    if winner_id is None:
        return None

    return {
        "won": int(winner_id) == int(team_id),
        "score_for": score_for,
        "score_against": score_against,
        "map_diff": score_for - score_against,
        "bo": game_count(match),
        "tier": get_tier(match),
        "region": get_region(match),
        "begin_at": match.get("begin_at"),
    }


def build_team_history(past_matches):
    history_by_id = defaultdict(list)
    history_by_name = defaultdict(list)

    for match in past_matches:
        if str(match.get("status") or "").lower() != "finished":
            continue

        teams = get_teams(match)

        if len(teams) < 2:
            continue

        for team in teams:
            team_id = team.get("id")
            team_name = team.get("name")

            if not team_id or not team_name:
                continue

            result = team_match_result(match, team_id)

            if not result:
                continue

            result["match_id"] = match.get("id")
            result["team_name"] = team_name
            result["team_id"] = team_id

            history_by_id[int(team_id)].append(result)

            name_key = normalize_team_name(team_name)
            if name_key:
                history_by_name[name_key].append(result)

    for team_id in list(history_by_id.keys()):
        history_by_id[team_id].sort(
            key=lambda x: x.get("begin_at") or "",
            reverse=True,
        )

    for name_key in list(history_by_name.keys()):
        history_by_name[name_key].sort(
            key=lambda x: x.get("begin_at") or "",
            reverse=True,
        )

    return history_by_id, history_by_name


def get_team_games(team, history_by_id, history_by_name):
    team_id = team.get("id")
    team_name = team.get("name")

    games = []

    if team_id:
        games = history_by_id.get(int(team_id), [])

    if len(games) >= MIN_MATCHES_PER_TEAM:
        return games, "id"

    name_key = normalize_team_name(team_name)
    fallback_games = history_by_name.get(name_key, [])

    if len(fallback_games) > len(games):
        return fallback_games, "name"

    return games, "id"


def avg(values, default=0.0):
    values = [v for v in values if isinstance(v, (int, float))]

    if not values:
        return default

    return sum(values) / len(values)


def rate(values):
    if not values:
        return 0.0

    return sum(1 for v in values if v) / len(values)


def team_score(team, history_by_id, history_by_name, match_tier=""):
    games, source = get_team_games(team, history_by_id, history_by_name)

    if len(games) < MIN_MATCHES_PER_TEAM:
        return None

    last_3 = games[:3]
    last_5 = games[:5]
    last_10 = games[:10]

    win3 = rate([g["won"] for g in last_3])
    win5 = rate([g["won"] for g in last_5])
    win10 = rate([g["won"] for g in last_10])

    map_diff_5 = avg([g["map_diff"] for g in last_5])
    map_diff_10 = avg([g["map_diff"] for g in last_10])

    map_for_10 = avg([g["score_for"] for g in last_10])
    map_against_10 = avg([g["score_against"] for g in last_10])

    clean_wins = rate([
        g["won"] and g["score_against"] == 0
        for g in last_10
    ])

    close_losses = rate([
        (not g["won"]) and g["score_for"] > 0
        for g in last_10
    ])

    score = 0.0
    score += win10 * 36
    score += win5 * 24
    score += win3 * 12
    score += clamp((map_diff_10 + 1.5) / 3.0, 0, 1) * 14
    score += clamp((map_diff_5 + 1.5) / 3.0, 0, 1) * 8
    score += clean_wins * 4
    score += close_losses * 2

    same_tier_recent = 0

    if match_tier:
        same_tier_recent = sum(
            1 for g in last_10
            if str(g.get("tier") or "").lower() == match_tier
        )
        score += clamp(same_tier_recent / 5, 0, 1) * 3

    return {
        "score": round(clamp(score, 1, 99), 2),
        "matches": len(games),
        "history_source": source,
        "last_3_win_rate": round(win3, 3),
        "last_5_win_rate": round(win5, 3),
        "last_10_win_rate": round(win10, 3),
        "map_diff_5": round(map_diff_5, 3),
        "map_diff_10": round(map_diff_10, 3),
        "map_for_10": round(map_for_10, 3),
        "map_against_10": round(map_against_10, 3),
        "clean_win_rate_10": round(clean_wins, 3),
        "close_loss_rate_10": round(close_losses, 3),
        "same_tier_recent": same_tier_recent,
    }


def probability_from_scores(score_a, score_b, bo, tier):
    diff = score_a - score_b

    scale = 18.0

    if bo >= 5:
        scale = 15.5
    elif bo == 1:
        scale = 24.0

    raw = 1 / (1 + math.exp(-(diff / scale)))

    prob = clamp(raw, 0.38, 0.72)

    if tier in TIER_BONUS:
        prob = clamp(prob + (TIER_BONUS[tier] / 1000.0), 0.38, 0.72)

    return prob


def confidence_from_prob(prob, score_diff, matches_min, bo):
    conf = 42.0
    conf += clamp(abs(prob - 0.5) / 0.18, 0, 1) * 28
    conf += clamp(abs(score_diff) / 22, 0, 1) * 12
    conf += clamp(matches_min / 15, 0, 1) * 10

    if bo >= 3:
        conf += 5

    if bo == 1:
        conf -= 8

    return round(clamp(conf, 1, 94), 1)


def build_pick_id(match_id, team_id):
    raw = f"cs2|{match_id}|winner|{team_id}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def append_unique_history(predictions):
    history = load_json(RESULTS_FILE, [])

    if not isinstance(history, list):
        history = []

    by_id = {
        item.get("pick_id"): idx
        for idx, item in enumerate(history)
        if isinstance(item, dict) and item.get("pick_id")
    }

    added = 0
    updated_pending = 0

    for pick in predictions:
        pick_id = pick.get("pick_id")

        if not pick_id:
            continue

        if pick_id not in by_id:
            history.append(pick.copy())
            by_id[pick_id] = len(history) - 1
            added += 1
            continue

        idx = by_id[pick_id]

        if history[idx].get("result") == "pending":
            old = history[idx]
            new_pick = pick.copy()
            new_pick["result"] = "pending"

            if old.get("created_at"):
                new_pick["created_at"] = old.get("created_at")

            history[idx] = new_pick
            updated_pending += 1

    save_json(RESULTS_FILE, history)

    debug(f"HISTORY added={added} updated_pending={updated_pending} total={len(history)}")


def build_predictions():
    ensure_dirs()

    tz = ZoneInfo(TZ_NAME)
    now = datetime.now(tz)

    start = now + timedelta(hours=TIME_WINDOW_MIN_HOURS)
    end = now + timedelta(hours=TIME_WINDOW_MAX_HOURS)

    debug(f"NOW: {now.isoformat()}")
    debug(f"WINDOW: {start.isoformat()} -> {end.isoformat()}")

    upcoming = fetch_upcoming()
    past = fetch_past()

    debug(f"UPCOMING raw={len(upcoming)}")
    debug(f"PAST raw={len(past)}")

    history_by_id, history_by_name = build_team_history(past)

    debug(f"HISTORY teams_by_id={len(history_by_id)} teams_by_name={len(history_by_name)}")

    candidates = []

    skipped_time = 0
    skipped_bo1 = 0
    skipped_low_history = 0
    skipped_low_edge = 0
    skipped_low_conf = 0
    skipped_low_diff = 0
    checked = 0

    for match in upcoming:
        try:
            if not is_valid_cs2_match(match):
                continue

            checked += 1

            dt = local_dt(match)

            if not dt or dt < start or dt > end:
                skipped_time += 1
                continue

            bo = game_count(match)

            if SKIP_BO1 and bo <= 1:
                skipped_bo1 += 1
                continue

            teams = get_teams(match)

            if len(teams) < 2:
                continue

            tier = get_tier(match)

            team_a, team_b = teams[0], teams[1]

            stat_a = team_score(team_a, history_by_id, history_by_name, tier)
            stat_b = team_score(team_b, history_by_id, history_by_name, tier)

            if not stat_a or not stat_b:
                skipped_low_history += 1

                games_a, src_a = get_team_games(team_a, history_by_id, history_by_name)
                games_b, src_b = get_team_games(team_b, history_by_id, history_by_name)

                debug(
                    f"SKIP low history {match_name(match)} | "
                    f"{team_a.get('name')}={len(games_a)} via {src_a} | "
                    f"{team_b.get('name')}={len(games_b)} via {src_b}"
                )
                continue

            prob_a = probability_from_scores(
                stat_a["score"],
                stat_b["score"],
                bo,
                tier,
            )

            prob_b = 1 - prob_a

            if prob_a >= prob_b:
                pick_team = team_a
                pick_stat = stat_a
                opp_team = team_b
                opp_stat = stat_b
                model_prob = prob_a
                score_diff = stat_a["score"] - stat_b["score"]
            else:
                pick_team = team_b
                pick_stat = stat_b
                opp_team = team_a
                opp_stat = stat_a
                model_prob = prob_b
                score_diff = stat_b["score"] - stat_a["score"]

            prob_edge = model_prob - 0.5

            confidence = confidence_from_prob(
                model_prob,
                score_diff,
                min(pick_stat["matches"], opp_stat["matches"]),
                bo,
            )

            if abs(score_diff) < MIN_SCORE_DIFF:
                skipped_low_diff += 1
                debug(
                    f"SKIP low diff {match_name(match)} | "
                    f"diff={round(score_diff, 2)} prob={round(model_prob, 4)} conf={confidence}"
                )
                continue

            if prob_edge < MIN_PROB_EDGE:
                skipped_low_edge += 1
                debug(
                    f"SKIP low edge {match_name(match)} | "
                    f"edge={round(prob_edge, 4)} prob={round(model_prob, 4)}"
                )
                continue

            if confidence < MIN_CONFIDENCE:
                skipped_low_conf += 1
                debug(
                    f"SKIP low conf {match_name(match)} | "
                    f"conf={confidence} prob={round(model_prob, 4)} diff={round(score_diff, 2)}"
                )
                continue

            league = (match.get("league") or {}).get("name") or "CS2"
            serie = (
                (match.get("serie") or {}).get("full_name")
                or (match.get("serie") or {}).get("name")
                or ""
            )
            tournament = (match.get("tournament") or {}).get("name") or ""
            region = get_region(match)

            pick = {
                "pick_id": build_pick_id(match.get("id"), pick_team.get("id")),
                "match_id": match.get("id"),
                "fixture_id": match.get("id"),
                "sport": "esports",
                "game": "cs2",
                "model_version": "ai77_pandascore_cs2_free_v2",
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "league": league,
                "serie": serie,
                "tournament": tournament,
                "tier": tier or "unknown",
                "region": region,
                "match": match_name(match),
                "bet": pick_team.get("name"),
                "bucket": "match_winner",
                "pick_team_id": pick_team.get("id"),
                "pick_team": pick_team.get("name"),
                "opponent_team_id": opp_team.get("id"),
                "opponent_team": opp_team.get("name"),
                "best_of": bo,
                "model_prob": round(model_prob, 4),
                "prob_edge_vs_coinflip": round(prob_edge, 4),
                "team_score": pick_stat["score"],
                "opponent_score": opp_stat["score"],
                "score_diff": round(score_diff, 2),
                "confidence": confidence,
                "quality_score": round(
                    clamp(
                        confidence
                        + clamp(abs(score_diff) / 25, 0, 1) * 5
                        + clamp(prob_edge / 0.12, 0, 1) * 4,
                        1,
                        99,
                    ),
                    1,
                ),
                "pick_stats": pick_stat,
                "opponent_stats": opp_stat,
                "result": "pending",
                "created_at": datetime.now(tz).isoformat(),
                "reasoning": (
                    f"{pick_team.get('name')} rates higher than {opp_team.get('name')} "
                    f"in the CS2 PandaScore free-plan model. Signal uses recent match win rate, "
                    f"map differential, clean wins, best-of format and tournament context. "
                    f"No odds are used yet, so this tracks prediction accuracy, not betting ROI."
                ),
            }

            candidates.append(pick)

            debug(
                f"CANDIDATE {pick['match']} | {pick['bet']} | "
                f"prob={pick['model_prob']} conf={confidence} "
                f"diff={pick['score_diff']} q={pick['quality_score']} "
                f"hist={pick_stat['matches']}/{opp_stat['matches']}"
            )

        except Exception as e:
            debug(f"MATCH ERROR {match.get('id')}: {e}")

    candidates.sort(
        key=lambda x: (
            x["quality_score"],
            x["confidence"],
            x["prob_edge_vs_coinflip"],
            x["score_diff"],
            x["best_of"],
        ),
        reverse=True,
    )

    final = candidates[:MAX_FINAL_PICKS]
    final.sort(key=lambda x: (x["date"], x["time"]))

    debug("SUMMARY:")
    debug(f"checked={checked}")
    debug(f"candidates={len(candidates)}")
    debug(f"skipped_time={skipped_time}")
    debug(f"skipped_bo1={skipped_bo1}")
    debug(f"skipped_low_history={skipped_low_history}")
    debug(f"skipped_low_diff={skipped_low_diff}")
    debug(f"skipped_low_edge={skipped_low_edge}")
    debug(f"skipped_low_conf={skipped_low_conf}")

    debug("FINAL PICKS:")
    for pick in final:
        debug(
            f"{pick['date']} {pick['time']} | {pick['match']} | "
            f"{pick['bet']} | prob={pick['model_prob']} "
            f"conf={pick['confidence']} q={pick['quality_score']}"
        )

    payload = {
        "generated_at": datetime.now(tz).isoformat(),
        "timezone": TZ_NAME,
        "source": "PandaScore",
        "model": "AI77 PandaScore CS2 Free v2",
        "note": "No betting odds are used. This page tracks prediction accuracy only.",
        "window_hours": {
            "min": TIME_WINDOW_MIN_HOURS,
            "max": TIME_WINDOW_MAX_HOURS,
        },
        "settings": {
            "min_matches_per_team": MIN_MATCHES_PER_TEAM,
            "min_prob_edge": MIN_PROB_EDGE,
            "min_confidence": MIN_CONFIDENCE,
            "min_score_diff": MIN_SCORE_DIFF,
            "skip_bo1": SKIP_BO1,
            "past_pages": PAST_PAGES,
            "past_per_page": PAST_PER_PAGE,
        },
        "picks": final,
    }

    save_json(PREDICTIONS_FILE, payload)
    append_unique_history(final)

    return payload


def main():
    payload = build_predictions()
    print(f"Saved {len(payload['picks'])} CS2 predictions to {PREDICTIONS_FILE}")


if __name__ == "__main__":
    main()

import json
import os
import re
import unicodedata
from difflib import SequenceMatcher


ELO_FILE = "ratings/tennis_elo.json"


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def normalize_name(name):
    text = str(name or "").strip().lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    text = re.sub(r"[^a-z\s\.-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_name(name):
    n = normalize_name(name)
    parts = n.replace(".", "").split()

    if not parts:
        return "", ""

    if len(parts) == 1:
        return "", parts[0]

    first = parts[0]
    last = parts[-1]
    return first, last


def api_name_key(name):
    """
    API names often look like:
    J. Brooksby
    S. Baez

    We convert to:
    initial = j
    last = brooksby
    """
    n = normalize_name(name)
    parts = n.split()

    if not parts:
        return "", ""

    if len(parts) == 1:
        return "", parts[0].replace(".", "")

    first = parts[0].replace(".", "")
    last = parts[-1].replace(".", "")

    initial = first[:1]
    return initial, last


def rating_name_key(player_name):
    """
    Jeff names usually look like:
    Jenson Brooksby

    We convert to:
    initial = j
    last = brooksby
    """
    first, last = split_name(player_name)
    return first[:1], last


def build_lookup_indexes(elo_payload):
    ratings = elo_payload.get("ratings") or {}

    by_exact = {}
    by_initial_last = {}
    by_last = {}

    for rating_key, row in ratings.items():
        name = row.get("player_name") or ""
        norm = normalize_name(name)

        if norm:
            by_exact[norm] = rating_key

        initial, last = rating_name_key(name)

        if initial and last:
            by_initial_last.setdefault((initial, last), []).append(rating_key)

        if last:
            by_last.setdefault(last, []).append(rating_key)

    return {
        "ratings": ratings,
        "by_exact": by_exact,
        "by_initial_last": by_initial_last,
        "by_last": by_last,
    }


def choose_best_candidate(api_name, candidate_keys, ratings):
    """
    If several players share same initial + last name,
    choose by closest full-name string, then more matches.
    """
    if not candidate_keys:
        return None, 0.0

    norm_api = normalize_name(api_name)

    best_key = None
    best_score = -1.0

    for key in candidate_keys:
        row = ratings.get(key) or {}
        candidate_name = row.get("player_name") or ""

        name_score = SequenceMatcher(
            None,
            norm_api,
            normalize_name(candidate_name),
        ).ratio()

        match_bonus = min(float(row.get("matches") or 0), 50.0) / 100.0
        score = name_score + match_bonus

        if score > best_score:
            best_score = score
            best_key = key

    return best_key, round(best_score, 4)


def find_player_rating(name, indexes, tour=None):
    ratings = indexes["ratings"]

    norm = normalize_name(name)

    if not norm:
        return {
            "matched": False,
            "input_name": name,
            "match_method": "empty",
        }

    # 1. Exact full-name match.
    exact_key = indexes["by_exact"].get(norm)
    if exact_key:
        row = ratings.get(exact_key)
        return {
            "matched": True,
            "input_name": name,
            "rating_key": exact_key,
            "matched_name": row.get("player_name"),
            "match_method": "exact",
            "score": 1.0,
            "rating": row,
        }

    # 2. Initial + last name, best for API style names.
    initial, last = api_name_key(name)
    candidate_keys = list(indexes["by_initial_last"].get((initial, last), []))

    if tour:
        tour_l = str(tour).lower()
        filtered = [
            key for key in candidate_keys
            if str((ratings.get(key) or {}).get("tour") or "").lower() == tour_l
        ]
        if filtered:
            candidate_keys = filtered

    if candidate_keys:
        key, score = choose_best_candidate(name, candidate_keys, ratings)
        row = ratings.get(key)
        return {
            "matched": True,
            "input_name": name,
            "rating_key": key,
            "matched_name": row.get("player_name"),
            "match_method": "initial_last",
            "score": score,
            "rating": row,
        }

    # 3. Last-name fallback.
    candidate_keys = list(indexes["by_last"].get(last, []))

    if tour:
        tour_l = str(tour).lower()
        filtered = [
            key for key in candidate_keys
            if str((ratings.get(key) or {}).get("tour") or "").lower() == tour_l
        ]
        if filtered:
            candidate_keys = filtered

    if candidate_keys:
        key, score = choose_best_candidate(name, candidate_keys, ratings)
        row = ratings.get(key)
        return {
            "matched": True,
            "input_name": name,
            "rating_key": key,
            "matched_name": row.get("player_name"),
            "match_method": "last_name",
            "score": score,
            "rating": row,
        }

    return {
        "matched": False,
        "input_name": name,
        "match_method": "not_found",
    }


def surface_key(surface):
    s = str(surface or "").strip().lower()

    if s in {"hard", "clay", "grass", "carpet"}:
        return s

    return "unknown"


def rating_value(row, surface=None):
    if not row:
        return None, None

    overall = row.get("overall_elo")

    s = surface_key(surface)
    surface_elo = (row.get("surface_elo") or {}).get(s)

    if surface_elo is None:
        surface_elo = overall

    return overall, surface_elo


def get_elo_signal(player_name, opponent_name, surface=None, tour=None, elo_file=ELO_FILE):
    payload = load_json(elo_file, {})
    indexes = build_lookup_indexes(payload)

    player = find_player_rating(player_name, indexes, tour=tour)
    opponent = find_player_rating(opponent_name, indexes, tour=tour)

    player_overall, player_surface = rating_value(player.get("rating"), surface)
    opponent_overall, opponent_surface = rating_value(opponent.get("rating"), surface)

    matched = bool(player.get("matched")) and bool(opponent.get("matched"))

    out = {
        "matched": matched,
        "surface": surface_key(surface),
        "player": {
            "input_name": player_name,
            "matched": player.get("matched", False),
            "matched_name": player.get("matched_name"),
            "rating_key": player.get("rating_key"),
            "match_method": player.get("match_method"),
            "match_score": player.get("score"),
            "overall_elo": player_overall,
            "surface_elo": player_surface,
            "matches": (player.get("rating") or {}).get("matches"),
            "confidence": (player.get("rating") or {}).get("confidence"),
        },
        "opponent": {
            "input_name": opponent_name,
            "matched": opponent.get("matched", False),
            "matched_name": opponent.get("matched_name"),
            "rating_key": opponent.get("rating_key"),
            "match_method": opponent.get("match_method"),
            "match_score": opponent.get("score"),
            "overall_elo": opponent_overall,
            "surface_elo": opponent_surface,
            "matches": (opponent.get("rating") or {}).get("matches"),
            "confidence": (opponent.get("rating") or {}).get("confidence"),
        },
        "overall_elo_diff": None,
        "surface_elo_diff": None,
        "agrees_with_pick": None,
    }

    if player_overall is not None and opponent_overall is not None:
        out["overall_elo_diff"] = round(float(player_overall) - float(opponent_overall), 2)

    if player_surface is not None and opponent_surface is not None:
        out["surface_elo_diff"] = round(float(player_surface) - float(opponent_surface), 2)

    if out["overall_elo_diff"] is not None:
        out["agrees_with_pick"] = out["overall_elo_diff"] >= 0

    return out


def main():
    # Quick manual test.
    tests = [
        ("J. Brooksby", "S. Baez", "clay", "atp"),
        ("J. Sinner", "C. Alcaraz", "clay", "atp"),
        ("I. Swiatek", "A. Sabalenka", "hard", "wta"),
    ]

    for player, opponent, surface, tour in tests:
        signal = get_elo_signal(player, opponent, surface=surface, tour=tour)
        print("")
        print(f"{player} vs {opponent} | {surface} | {tour}")
        print(json.dumps(signal, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

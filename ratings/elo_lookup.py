import json
import os
import re
import unicodedata
from difflib import SequenceMatcher


BASE_DIR = os.path.dirname(__file__)
ELO_FILE = os.path.join(BASE_DIR, "tennis_elo.json")

_SURFACE_ALIASES = {
    "hard": "hard",
    "hardcourt": "hard",
    "hard court": "hard",
    "clay": "clay",
    "red clay": "clay",
    "grass": "grass",
    "indoor": "indoor",
    "indoors": "indoor",
    "carpet": "carpet",
}


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def normalize_text(value):
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    # remove brackets/countries/noise
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\[[^\]]*\]", " ", text)

    # common punctuation
    text = text.replace(",", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = text.replace(".", " ")

    # keep letters/numbers/spaces only
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compact_text(value):
    return normalize_text(value).replace(" ", "")


def normalize_surface(surface):
    s = normalize_text(surface)
    return _SURFACE_ALIASES.get(s, s or None)


def detect_tour_from_text(value):
    text = normalize_text(value)

    if not text:
        return None

    if "wta" in text or "women" in text or "woman" in text or "girls" in text:
        return "wta"

    if "atp" in text or "men" in text or "boys" in text:
        return "atp"

    if "challenger" in text:
        return "challenger"

    if "itf" in text:
        return "itf"

    return None


def normalize_tour(tour):
    text = normalize_text(tour)

    if not text:
        return None

    if text in {"atp", "wta", "challenger", "itf"}:
        return text

    return detect_tour_from_text(text)


def split_name_tokens(name):
    n = normalize_text(name)
    if not n:
        return []

    tokens = n.split()

    # Remove obvious non-name words if they sneak in
    bad = {
        "atp", "wta", "itf", "challenger", "men", "women",
        "singles", "doubles", "qualification", "qualifying",
    }
    tokens = [t for t in tokens if t not in bad]
    return tokens


def name_variants(name):
    """
    Returns matching variants:
    - exact normalized full name
    - compact name
    - initial_last
    - last_initial
    - last
    Supports:
      J. Brooksby
      Brooksby J.
      Brooksby, Jenson
      Jenson Brooksby
    """
    raw = str(name or "").strip()
    tokens = split_name_tokens(raw)

    variants = set()

    if not tokens:
        return variants

    full = " ".join(tokens)
    variants.add(("exact", full))
    variants.add(("compact", "".join(tokens)))

    if len(tokens) == 1:
        variants.add(("last", tokens[0]))
        return variants

    first = tokens[0]
    last = tokens[-1]

    # Normal First Last
    variants.add(("initial_last", f"{first[0]} {last}"))
    variants.add(("last_initial", f"{last} {first[0]}"))
    variants.add(("last", last))

    # Reversed: Brooksby J / Brooksby Jenson
    rev_last = tokens[0]
    rev_first = tokens[-1]
    variants.add(("initial_last", f"{rev_first[0]} {rev_last}"))
    variants.add(("last_initial", f"{rev_last} {rev_first[0]}"))
    variants.add(("last", rev_last))

    # Two-token special: "j brooksby" and "brooksby j"
    if len(tokens) == 2:
        a, b = tokens
        if len(a) == 1:
            variants.add(("initial_last", f"{a} {b}"))
            variants.add(("last_initial", f"{b} {a}"))
            variants.add(("last", b))

        if len(b) == 1:
            variants.add(("initial_last", f"{b} {a}"))
            variants.add(("last_initial", f"{a} {b}"))
            variants.add(("last", a))

    return variants


def get_record_name(record, fallback_name=None):
    if not isinstance(record, dict):
        return fallback_name

    for key in [
        "player_name",
        "name",
        "player",
        "player_full_name",
        "full_name",
        "matched_name",
    ]:
        value = record.get(key)
        if value:
            return str(value).strip()

    return fallback_name


def get_record_tour(record, fallback_tour=None):
    if not isinstance(record, dict):
        return normalize_tour(fallback_tour)

    for key in ["tour", "tour_level", "gender", "event_type", "category"]:
        value = record.get(key)
        tour = normalize_tour(value)
        if tour:
            if tour == "atp":
                return "atp"
            if tour == "wta":
                return "wta"
            return tour

    return normalize_tour(fallback_tour)


def get_overall_elo(record):
    if not isinstance(record, dict):
        return None

    for key in [
        "elo",
        "rating",
        "overall_elo",
        "overall",
        "current_elo",
        "current_rating",
        "tennis_elo",
    ]:
        value = safe_float(record.get(key), None)
        if value is not None:
            return value

    return None


def get_surface_elo(record, surface):
    if not isinstance(record, dict):
        return None

    surface = normalize_surface(surface)
    if not surface:
        return None

    # Direct fields
    direct_keys = [
        f"{surface}_elo",
        f"{surface}_rating",
        f"elo_{surface}",
        f"rating_{surface}",
    ]

    for key in direct_keys:
        value = safe_float(record.get(key), None)
        if value is not None:
            return value

    # Nested surface dicts
    for parent_key in ["surface_elo", "surface_elos", "surface_ratings", "surfaces", "by_surface"]:
        parent = record.get(parent_key)
        if not isinstance(parent, dict):
            continue

        # surface: number
        value = safe_float(parent.get(surface), None)
        if value is not None:
            return value

        # surface: {elo: number}
        child = parent.get(surface)
        if isinstance(child, dict):
            for key in ["elo", "rating", "current_elo", "current_rating"]:
                value = safe_float(child.get(key), None)
                if value is not None:
                    return value

    return None


def get_match_count(record):
    if not isinstance(record, dict):
        return 0

    for key in ["matches", "match_count", "n", "played", "games"]:
        value = safe_float(record.get(key), None)
        if value is not None:
            return int(value)

    return 0


def flatten_elo_payload(payload):
    """
    Supports many possible tennis_elo.json shapes:
    - list of player dicts
    - {player_name: rating_dict}
    - {tour: {player_name: rating_dict}}
    - {"players": [...]}
    - {"ratings": [...]}
    """
    rows = []

    def walk(obj, fallback_name=None, fallback_tour=None):
        if isinstance(obj, list):
            for item in obj:
                walk(item, fallback_name=fallback_name, fallback_tour=fallback_tour)
            return

        if not isinstance(obj, dict):
            return

        # Container keys
        for key in ["players", "ratings", "data", "items", "rows"]:
            value = obj.get(key)
            if isinstance(value, list):
                for item in value:
                    walk(item, fallback_tour=fallback_tour)
                return
            if isinstance(value, dict):
                walk(value, fallback_tour=fallback_tour)
                return

        # Player-like record
        name = get_record_name(obj, fallback_name)
        overall = get_overall_elo(obj)

        if name and overall is not None:
            tour = get_record_tour(obj, fallback_tour)
            rows.append({
                "name": name,
                "norm_name": normalize_text(name),
                "compact_name": compact_text(name),
                "tour": tour,
                "overall_elo": overall,
                "record": obj,
                "matches": get_match_count(obj),
            })
            return

        # Dict nesting, often {tour: {...}} or {player: {...}}
        for key, value in obj.items():
            key_tour = normalize_tour(key) or fallback_tour

            if isinstance(value, dict):
                # Could be { "Jannik Sinner": {"elo": 2100}}
                possible_name = key
                possible_overall = get_overall_elo(value)

                if possible_overall is not None:
                    tour = get_record_tour(value, key_tour)
                    rows.append({
                        "name": get_record_name(value, possible_name),
                        "norm_name": normalize_text(get_record_name(value, possible_name)),
                        "compact_name": compact_text(get_record_name(value, possible_name)),
                        "tour": tour,
                        "overall_elo": possible_overall,
                        "record": value,
                        "matches": get_match_count(value),
                    })
                else:
                    walk(value, fallback_name=possible_name, fallback_tour=key_tour)

            elif isinstance(value, list):
                walk(value, fallback_tour=key_tour)

    walk(payload)
    return rows


_ELO_CACHE = None
_INDEX_CACHE = None


def load_elo_rows():
    global _ELO_CACHE

    if _ELO_CACHE is not None:
        return _ELO_CACHE

    payload = load_json(ELO_FILE, {})
    _ELO_CACHE = flatten_elo_payload(payload)
    return _ELO_CACHE


def build_index():
    global _INDEX_CACHE

    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    rows = load_elo_rows()

    index = {
        "exact": {},
        "compact": {},
        "initial_last": {},
        "last_initial": {},
        "last": {},
        "all": rows,
    }

    for row in rows:
        for kind, key in name_variants(row["name"]):
            index.setdefault(kind, {}).setdefault(key, []).append(row)

    _INDEX_CACHE = index
    return index


def tour_matches(row_tour, wanted_tour):
    wanted_tour = normalize_tour(wanted_tour)
    row_tour = normalize_tour(row_tour)

    if not wanted_tour:
        return True

    if not row_tour:
        return True

    if wanted_tour == row_tour:
        return True

    # Challenger je lahko moški tour, ampak za ATP/WTA value model raje ne mešamo preveč.
    # Zato tu NI avtomatskega challenger=atp.
    return False


def choose_best(candidates, query_name, wanted_tour=None):
    if not candidates:
        return None

    wanted_tour = normalize_tour(wanted_tour)

    filtered = [c for c in candidates if tour_matches(c.get("tour"), wanted_tour)]
    if filtered:
        candidates = filtered

    q_norm = normalize_text(query_name)
    q_compact = compact_text(query_name)

    def score(row):
        name_norm = row.get("norm_name") or normalize_text(row.get("name"))
        name_compact = row.get("compact_name") or compact_text(row.get("name"))

        s1 = SequenceMatcher(None, q_norm, name_norm).ratio()
        s2 = SequenceMatcher(None, q_compact, name_compact).ratio()
        s = max(s1, s2)

        # small bonus for wanted tour
        if wanted_tour and normalize_tour(row.get("tour")) == wanted_tour:
            s += 0.05

        # small bonus for more matches / more reliable rating
        s += min((row.get("matches") or 0), 500) / 100000.0

        return s

    return sorted(candidates, key=score, reverse=True)[0]


def find_player(name, tour=None):
    index = build_index()
    variants = name_variants(name)

    attempts = []

    # Strong exact-ish passes
    for kind in ["exact", "compact", "initial_last", "last_initial"]:
        for variant_kind, key in variants:
            if variant_kind != kind:
                continue

            attempts.append(f"{kind}:{key}")
            candidates = index.get(kind, {}).get(key, [])
            if candidates:
                chosen = choose_best(candidates, name, tour)
                if chosen:
                    return {
                        "matched": True,
                        "input_name": name,
                        "matched_name": chosen["name"],
                        "match_method": kind,
                        "tour": chosen.get("tour"),
                        "overall_elo": chosen.get("overall_elo"),
                        "record": chosen.get("record"),
                        "attempts": attempts,
                    }

    # Last name fallback only if not too ambiguous after tour filter
    for variant_kind, key in variants:
        if variant_kind != "last":
            continue

        attempts.append(f"last:{key}")
        candidates = index.get("last", {}).get(key, [])

        if not candidates:
            continue

        tour_candidates = [c for c in candidates if tour_matches(c.get("tour"), tour)]
        use_candidates = tour_candidates or candidates

        if len(use_candidates) == 1:
            chosen = use_candidates[0]
            return {
                "matched": True,
                "input_name": name,
                "matched_name": chosen["name"],
                "match_method": "last_unique",
                "tour": chosen.get("tour"),
                "overall_elo": chosen.get("overall_elo"),
                "record": chosen.get("record"),
                "attempts": attempts,
            }

        chosen = choose_best(use_candidates, name, tour)
        if chosen:
            q = normalize_text(name)
            c = normalize_text(chosen["name"])
            ratio = SequenceMatcher(None, q, c).ratio()

            # Only accept fuzzy last fallback if reasonably strong
            if ratio >= 0.72:
                return {
                    "matched": True,
                    "input_name": name,
                    "matched_name": chosen["name"],
                    "match_method": f"last_fuzzy_{round(ratio, 3)}",
                    "tour": chosen.get("tour"),
                    "overall_elo": chosen.get("overall_elo"),
                    "record": chosen.get("record"),
                    "attempts": attempts,
                }

    # Full fuzzy fallback
    q_norm = normalize_text(name)
    q_compact = compact_text(name)

    best = None
    best_score = 0.0

    for row in index.get("all", []):
        if not tour_matches(row.get("tour"), tour):
            continue

        n_norm = row.get("norm_name") or normalize_text(row.get("name"))
        n_compact = row.get("compact_name") or compact_text(row.get("name"))

        score = max(
            SequenceMatcher(None, q_norm, n_norm).ratio(),
            SequenceMatcher(None, q_compact, n_compact).ratio(),
        )

        if score > best_score:
            best_score = score
            best = row

    if best and best_score >= 0.86:
        return {
            "matched": True,
            "input_name": name,
            "matched_name": best["name"],
            "match_method": f"full_fuzzy_{round(best_score, 3)}",
            "tour": best.get("tour"),
            "overall_elo": best.get("overall_elo"),
            "record": best.get("record"),
            "attempts": attempts,
        }

    return {
        "matched": False,
        "input_name": name,
        "matched_name": None,
        "match_method": None,
        "tour": normalize_tour(tour),
        "overall_elo": None,
        "record": None,
        "attempts": attempts,
    }


def get_player_elo(player_name, surface=None, tour=None):
    player = find_player(player_name, tour=tour)

    if not player.get("matched"):
        return {
            **player,
            "surface_elo": None,
        }

    record = player.get("record") or {}
    surface_elo = get_surface_elo(record, surface)

    return {
        **player,
        "surface_elo": surface_elo,
    }


def get_elo_signal(player_name, opponent_name, surface=None, tour=None):
    """
    Compatible output for existing scripts.

    For match winner:
    - player_name = picked player
    - opponent_name = opponent
    - agrees_with_pick = picked player has higher ELO

    For totals:
    - player_name = first player
    - opponent_name = second player
    - agrees_with_pick only means first player has higher ELO
    """
    player = get_player_elo(player_name, surface=surface, tour=tour)
    opponent = get_player_elo(opponent_name, surface=surface, tour=tour)

    matched = bool(player.get("matched") and opponent.get("matched"))

    overall_elo_diff = None
    surface_elo_diff = None
    agrees_with_pick = None

    if matched:
        p_overall = player.get("overall_elo")
        o_overall = opponent.get("overall_elo")

        if p_overall is not None and o_overall is not None:
            overall_elo_diff = round(float(p_overall) - float(o_overall), 3)
            agrees_with_pick = overall_elo_diff > 0

        p_surface = player.get("surface_elo")
        o_surface = opponent.get("surface_elo")

        if p_surface is not None and o_surface is not None:
            surface_elo_diff = round(float(p_surface) - float(o_surface), 3)

    return {
        "matched": matched,
        "surface": normalize_surface(surface),
        "tour": normalize_tour(tour),
        "overall_elo_diff": overall_elo_diff,
        "surface_elo_diff": surface_elo_diff,
        "abs_overall_elo_diff": abs(overall_elo_diff) if overall_elo_diff is not None else None,
        "abs_surface_elo_diff": abs(surface_elo_diff) if surface_elo_diff is not None else None,
        "agrees_with_pick": agrees_with_pick,
        "player": {
            "matched": player.get("matched"),
            "input_name": player.get("input_name"),
            "matched_name": player.get("matched_name"),
            "match_method": player.get("match_method"),
            "tour": player.get("tour"),
            "overall_elo": player.get("overall_elo"),
            "surface_elo": player.get("surface_elo"),
            "attempts": player.get("attempts", []),
        },
        "opponent": {
            "matched": opponent.get("matched"),
            "input_name": opponent.get("input_name"),
            "matched_name": opponent.get("matched_name"),
            "match_method": opponent.get("match_method"),
            "tour": opponent.get("tour"),
            "overall_elo": opponent.get("overall_elo"),
            "surface_elo": opponent.get("surface_elo"),
            "attempts": opponent.get("attempts", []),
        },
    }


if __name__ == "__main__":
    rows = load_elo_rows()
    print(f"ELO rows loaded: {len(rows)}")

    for q in [
        "J. Brooksby",
        "Brooksby J.",
        "Jenson Brooksby",
        "A. Kalinskaya",
        "Kalinskaya A.",
    ]:
        print("")
        print(q)
        print(find_player(q))

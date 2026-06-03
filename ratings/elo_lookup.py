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

_NOISE_TOKENS = {
    "atp",
    "wta",
    "itf",
    "challenger",
    "men",
    "women",
    "woman",
    "man",
    "boys",
    "girls",
    "singles",
    "single",
    "doubles",
    "double",
    "qualification",
    "qualifying",
    "qualifier",
    "q",
    "main",
    "draw",
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
    """
    Normalizira ime:
    - odstrani accente
    - O'Connell -> o connell
    - Tung-Lin -> tung lin
    - odstrani oklepaje/države
    """
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\[[^\]]*\]", " ", text)

    text = text.replace(",", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = text.replace(".", " ")
    text = text.replace("'", " ")
    text = text.replace("’", " ")
    text = text.replace("`", " ")

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
    tokens = [t for t in tokens if t not in _NOISE_TOKENS]
    return tokens


def is_initial(token):
    return bool(token) and len(token) == 1 and token.isalpha()


def add_variant(variants, kind, value):
    value = normalize_text(value)
    if value:
        variants.add((kind, value))
        variants.add(("compact", value.replace(" ", "")))


def add_token_variant(variants, kind, tokens):
    tokens = [t for t in tokens if t]
    if tokens:
        add_variant(variants, kind, " ".join(tokens))


def name_variants(name):
    """
    Robustno generira variante za:
    - J. Brooksby
    - Brooksby J.
    - Jenson Brooksby
    - C. O'Connell / OConnell C.
    - P. Boscardin Dias
    - J. C. Prado Angelo
    - Wu Tung-Lin / Tung-Lin Wu
    - C. H. Tseng / Chun Hsin Tseng
    """
    tokens = split_name_tokens(name)
    variants = set()

    if not tokens:
        return variants

    full = " ".join(tokens)
    add_variant(variants, "exact", full)

    if len(tokens) == 1:
        add_variant(variants, "last", tokens[0])
        return variants

    first = tokens[0]
    last = tokens[-1]

    initials = [t for t in tokens if is_initial(t)]
    name_parts = [t for t in tokens if not is_initial(t)]

    # Normal first-last and last-first.
    add_token_variant(variants, "exact", tokens)
    add_token_variant(variants, "exact", list(reversed(tokens)))

    add_token_variant(variants, "initial_last", [first[0], last])
    add_token_variant(variants, "last_initial", [last, first[0]])
    add_token_variant(variants, "last", [last])

    # Two token basic cases.
    if len(tokens) == 2:
        a, b = tokens
        add_token_variant(variants, "initial_last", [a[0], b])
        add_token_variant(variants, "last_initial", [b, a[0]])
        add_token_variant(variants, "initial_last", [b[0], a])
        add_token_variant(variants, "last_initial", [a, b[0]])
        add_token_variant(variants, "last", [a])
        add_token_variant(variants, "last", [b])

    # Multi-word surname / initials.
    # P Boscardin Dias -> boscardin dias p, p boscardin dias
    if initials and name_parts:
        initials_joined = "".join(initials)

        # Last name can be one or more final non-initial parts.
        for surname_len in range(1, min(3, len(name_parts)) + 1):
            surname_parts = name_parts[-surname_len:]
            add_token_variant(variants, "initial_last", initials + surname_parts)
            add_token_variant(variants, "initial_last", [initials_joined] + surname_parts)
            add_token_variant(variants, "last_initial", surname_parts + initials)
            add_token_variant(variants, "last_initial", surname_parts + [initials_joined])
            add_token_variant(variants, "last", surname_parts)

        # Full non-initial name + initials reversed.
        add_token_variant(variants, "last_initial", name_parts + initials)
        add_token_variant(variants, "last_initial", name_parts + [initials_joined])
        add_token_variant(variants, "initial_last", initials + name_parts)
        add_token_variant(variants, "initial_last", [initials_joined] + name_parts)

    # Multi-word names without initials.
    # Wu Tung Lin -> Tung Lin Wu, Lin Wu Tung
    if len(tokens) >= 3:
        add_token_variant(variants, "exact", tokens[1:] + tokens[:1])
        add_token_variant(variants, "exact", tokens[-1:] + tokens[:-1])

        # Last two as surname.
        add_token_variant(variants, "last_initial", tokens[-2:] + [tokens[0][0]])
        add_token_variant(variants, "initial_last", [tokens[0][0]] + tokens[-2:])
        add_token_variant(variants, "last", tokens[-2:])

        # First two as surname/name group.
        add_token_variant(variants, "last_initial", tokens[:2] + [tokens[-1][0]])
        add_token_variant(variants, "initial_last", [tokens[-1][0]] + tokens[:2])
        add_token_variant(variants, "last", tokens[:2])

    # Apostrophe/space compact special:
    # o connell -> oconnell and connell are both available.
    for i in range(len(tokens)):
        add_variant(variants, "last", tokens[i])

    # Adjacent token compounds:
    # o connell -> oconnell, tung lin -> tunglin
    if len(tokens) >= 2:
        for i in range(len(tokens) - 1):
            compound = tokens[i] + tokens[i + 1]
            add_variant(variants, "compound", compound)
            if i == len(tokens) - 2:
                add_token_variant(variants, "initial_last", [tokens[0][0], compound])
                add_token_variant(variants, "last_initial", [compound, tokens[0][0]])
                add_variant(variants, "last", compound)

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

    for parent_key in [
        "surface_elo",
        "surface_elos",
        "surface_ratings",
        "surfaces",
        "by_surface",
    ]:
        parent = record.get(parent_key)
        if not isinstance(parent, dict):
            continue

        value = safe_float(parent.get(surface), None)
        if value is not None:
            return value

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
    Podpira različne oblike tennis_elo.json:
    - list igralcev
    - {player_name: rating_dict}
    - {tour: {player_name: rating_dict}}
    - {"players": [...]}
    - {"ratings": [...]}
    """
    rows = []

    def append_row(name, record, fallback_tour=None):
        if not name or not isinstance(record, dict):
            return

        overall = get_overall_elo(record)
        if overall is None:
            return

        final_name = get_record_name(record, name)
        if not final_name:
            return

        tour = get_record_tour(record, fallback_tour)

        rows.append({
            "name": final_name,
            "norm_name": normalize_text(final_name),
            "compact_name": compact_text(final_name),
            "tour": tour,
            "overall_elo": overall,
            "record": record,
            "matches": get_match_count(record),
        })

    def walk(obj, fallback_name=None, fallback_tour=None):
        if isinstance(obj, list):
            for item in obj:
                walk(item, fallback_name=fallback_name, fallback_tour=fallback_tour)
            return

        if not isinstance(obj, dict):
            return

        # Container keys.
        for key in ["players", "ratings", "data", "items", "rows"]:
            value = obj.get(key)
            if isinstance(value, list):
                for item in value:
                    walk(item, fallback_tour=fallback_tour)
                return
            if isinstance(value, dict):
                walk(value, fallback_tour=fallback_tour)
                return

        # Direct player-like dict.
        direct_name = get_record_name(obj, fallback_name)
        direct_overall = get_overall_elo(obj)
        if direct_name and direct_overall is not None:
            append_row(direct_name, obj, fallback_tour=fallback_tour)
            return

        # Nested dict.
        for key, value in obj.items():
            key_tour = normalize_tour(key) or fallback_tour

            if isinstance(value, dict):
                possible_overall = get_overall_elo(value)
                if possible_overall is not None:
                    append_row(key, value, fallback_tour=key_tour)
                else:
                    walk(value, fallback_name=key, fallback_tour=key_tour)

            elif isinstance(value, list):
                walk(value, fallback_tour=key_tour)

    walk(payload)
    return rows


_ELO_CACHE = None
_INDEX_CACHE = None


def clear_cache():
    global _ELO_CACHE, _INDEX_CACHE
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
        "compound": {},
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

    # Namerno ne mešamo challenger = atp.
    # Če boš želel posebej, raje testiramo ločeno.
    return False


def player_score(row, query_name, wanted_tour=None):
    wanted_tour = normalize_tour(wanted_tour)

    q_norm = normalize_text(query_name)
    q_compact = compact_text(query_name)

    name_norm = row.get("norm_name") or normalize_text(row.get("name"))
    name_compact = row.get("compact_name") or compact_text(row.get("name"))

    s_norm = SequenceMatcher(None, q_norm, name_norm).ratio()
    s_compact = SequenceMatcher(None, q_compact, name_compact).ratio()

    # Token overlap pomaga pri multi-word priimkih.
    q_tokens = set(q_norm.split())
    n_tokens = set(name_norm.split())
    overlap = 0.0
    if q_tokens and n_tokens:
        overlap = len(q_tokens & n_tokens) / max(len(q_tokens), len(n_tokens))

    score = max(s_norm, s_compact, overlap)

    if wanted_tour and normalize_tour(row.get("tour")) == wanted_tour:
        score += 0.05

    # Malo preferiramo bolj zanesljive ratinge z več matchi.
    score += min((row.get("matches") or 0), 500) / 100000.0

    return score


def choose_best(candidates, query_name, wanted_tour=None):
    if not candidates:
        return None

    wanted_tour = normalize_tour(wanted_tour)
    filtered = [c for c in candidates if tour_matches(c.get("tour"), wanted_tour)]

    if filtered:
        candidates = filtered

    return sorted(
        candidates,
        key=lambda row: player_score(row, query_name, wanted_tour),
        reverse=True,
    )[0]


def get_suggestions(name, tour=None, limit=5):
    """
    Diagnostika za missing imena.
    Vrne top najbližje igralce iz ELO baze.
    """
    index = build_index()
    rows = index.get("all", [])

    scored = []
    for row in rows:
        if not tour_matches(row.get("tour"), tour):
            continue

        score = player_score(row, name, tour)
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    out = []
    seen = set()

    for score, row in scored:
        key = (row.get("name"), row.get("tour"))
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "name": row.get("name"),
            "tour": row.get("tour"),
            "overall_elo": row.get("overall_elo"),
            "matches": row.get("matches"),
            "score": round(score, 4),
        })

        if len(out) >= limit:
            break

    return out


def _matched_result(name, chosen, method, attempts):
    return {
        "matched": True,
        "input_name": name,
        "matched_name": chosen["name"],
        "match_method": method,
        "tour": chosen.get("tour"),
        "overall_elo": chosen.get("overall_elo"),
        "record": chosen.get("record"),
        "attempts": attempts,
        "suggestions": [],
    }


def _unmatched_result(name, tour, attempts):
    return {
        "matched": False,
        "input_name": name,
        "matched_name": None,
        "match_method": None,
        "tour": normalize_tour(tour),
        "overall_elo": None,
        "record": None,
        "attempts": attempts,
        "suggestions": get_suggestions(name, tour=tour, limit=5),
    }


def find_player(name, tour=None):
    index = build_index()
    variants = name_variants(name)
    attempts = []

    # 1) Najmočnejši matchi.
    for kind in ["exact", "compact", "initial_last", "last_initial", "compound"]:
        for variant_kind, key in variants:
            if variant_kind != kind:
                continue

            attempts.append(f"{kind}:{key}")
            candidates = index.get(kind, {}).get(key, [])

            if not candidates:
                continue

            chosen = choose_best(candidates, name, tour)
            if chosen:
                return _matched_result(name, chosen, kind, attempts)

    # 2) Last-name fallback, ampak samo če ni preveč dvoumno.
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
            return _matched_result(name, chosen, "last_unique", attempts)

        chosen = choose_best(use_candidates, name, tour)
        if chosen:
            ratio = player_score(chosen, name, tour)

            # Last-name fuzzy naj bo strožji, ker je tu največ false positive nevarnosti.
            if ratio >= 0.78:
                return _matched_result(
                    name,
                    chosen,
                    f"last_fuzzy_{round(ratio, 3)}",
                    attempts,
                )

    # 3) Full fuzzy fallback.
    best = None
    best_score = 0.0

    for row in index.get("all", []):
        if not tour_matches(row.get("tour"), tour):
            continue

        score = player_score(row, name, tour)
        if score > best_score:
            best_score = score
            best = row

    # Prag ni prenizek, da ne potrjujemo napačnih igralcev.
    if best and best_score >= 0.88:
        return _matched_result(
            name,
            best,
            f"full_fuzzy_{round(best_score, 3)}",
            attempts,
        )

    return _unmatched_result(name, tour, attempts)


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
    Kompatibilen output za obstoječe skripte.

    Za match winner:
    - player_name = picked player
    - opponent_name = opponent
    - agrees_with_pick = picked player ima višji ELO

    Za totals:
    - player_name = first player
    - opponent_name = second player
    - agrees_with_pick pomeni samo first player ima višji ELO
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
            "suggestions": player.get("suggestions", []),
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
            "suggestions": opponent.get("suggestions", []),
        },
    }


if __name__ == "__main__":
    rows = load_elo_rows()
    print(f"ELO rows loaded: {len(rows)}")

    tests = [
        ("J. Brooksby", "atp"),
        ("Brooksby J.", "atp"),
        ("Jenson Brooksby", "atp"),
        ("A. Kalinskaya", "wta"),
        ("Kalinskaya A.", "wta"),
        ("C. O'Connell", "atp"),
        ("OConnell C.", "atp"),
        ("P. Boscardin Dias", "atp"),
        ("J. C. Prado Angelo", "atp"),
        ("Wu Tung-Lin", "atp"),
        ("C. H. Tseng", "atp"),
    ]

    for q, t in tests:
        print("")
        print(q, t)
        result = find_player(q, tour=t)
        print({
            "matched": result.get("matched"),
            "matched_name": result.get("matched_name"),
            "method": result.get("match_method"),
            "tour": result.get("tour"),
            "overall_elo": result.get("overall_elo"),
            "suggestions": result.get("suggestions"),
        })

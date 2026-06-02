import csv
import json
import math
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "Europe/Ljubljana"

START_YEAR = int(os.getenv("ELO_START_YEAR", "2024"))
END_YEAR = int(os.getenv("ELO_END_YEAR", str(datetime.now().year)))

START_ELO = 1500.0
K_FACTOR = 24.0

RATINGS_DIR = "ratings"
OUTPUT_FILE = os.path.join(RATINGS_DIR, "tennis_elo.json")
REPORT_FILE = os.path.join(RATINGS_DIR, "tennis_elo_report.json")

ATP_BASE = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master"
WTA_BASE = "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master"


def ensure_dirs():
    os.makedirs(RATINGS_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def normalize_surface(surface):
    s = str(surface or "").strip().lower()

    if s in {"hard", "clay", "grass", "carpet"}:
        return s

    if not s:
        return "unknown"

    return s


def expected_score(player_elo, opponent_elo):
    return 1.0 / (1.0 + math.pow(10.0, (opponent_elo - player_elo) / 400.0))


def update_elo(winner_elo, loser_elo, k=K_FACTOR):
    winner_expected = expected_score(winner_elo, loser_elo)
    loser_expected = expected_score(loser_elo, winner_elo)

    new_winner = winner_elo + k * (1.0 - winner_expected)
    new_loser = loser_elo + k * (0.0 - loser_expected)

    return new_winner, new_loser


def read_csv_url(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        text = response.read().decode("utf-8", errors="replace").splitlines()

    return list(csv.DictReader(text))


def load_players(tour):
    if tour == "atp":
        url = f"{ATP_BASE}/atp_players.csv"
    else:
        url = f"{WTA_BASE}/wta_players.csv"

    rows = read_csv_url(url)
    players = {}

    for row in rows:
        player_id = str(row.get("player_id") or "").strip()
        if not player_id:
            continue

        first = str(row.get("first_name") or "").strip()
        last = str(row.get("last_name") or "").strip()
        name = f"{first} {last}".strip()

        players[player_id] = {
            "player_id": player_id,
            "name": name,
            "first_name": first,
            "last_name": last,
            "hand": row.get("hand", ""),
            "birth_date": row.get("birth_date", ""),
            "country_code": row.get("country_code", ""),
        }

    return players


def load_matches_for_year(tour, year):
    if tour == "atp":
        url = f"{ATP_BASE}/atp_matches_{year}.csv"
    else:
        url = f"{WTA_BASE}/wta_matches_{year}.csv"

    try:
        return read_csv_url(url)
    except Exception as e:
        print(f"Skip {tour} {year}: {e}")
        return []


def get_rating(store, tour, player_id, player_name):
    key = f"{tour}:{player_id}"

    if key not in store:
        store[key] = {
            "tour": tour,
            "player_id": str(player_id),
            "player_name": player_name,
            "overall_elo": START_ELO,
            "surface_elo": {},
            "matches": 0,
            "surface_matches": {},
            "wins": 0,
            "losses": 0,
            "last_match_date": None,
            "last_surface": None,
        }

    return store[key]


def confidence_label(matches):
    if matches >= 30:
        return "high"
    if matches >= 10:
        return "medium"
    if matches >= 5:
        return "low"
    return "very_low"


def process_match(row, tour, ratings, players):
    winner_id = str(row.get("winner_id") or "").strip()
    loser_id = str(row.get("loser_id") or "").strip()

    if not winner_id or not loser_id:
        return False

    winner_name = str(row.get("winner_name") or "").strip()
    loser_name = str(row.get("loser_name") or "").strip()

    if not winner_name:
        winner_name = players.get(winner_id, {}).get("name", winner_id)

    if not loser_name:
        loser_name = players.get(loser_id, {}).get("name", loser_id)

    surface = normalize_surface(row.get("surface"))
    date_raw = str(row.get("tourney_date") or "").strip()

    winner = get_rating(ratings, tour, winner_id, winner_name)
    loser = get_rating(ratings, tour, loser_id, loser_name)

    old_winner_elo = safe_float(winner.get("overall_elo"), START_ELO)
    old_loser_elo = safe_float(loser.get("overall_elo"), START_ELO)

    new_winner_elo, new_loser_elo = update_elo(old_winner_elo, old_loser_elo)

    winner["overall_elo"] = new_winner_elo
    loser["overall_elo"] = new_loser_elo

    winner["matches"] += 1
    loser["matches"] += 1
    winner["wins"] += 1
    loser["losses"] += 1

    winner["last_match_date"] = date_raw
    loser["last_match_date"] = date_raw
    winner["last_surface"] = surface
    loser["last_surface"] = surface

    # Surface ELO.
    winner_surface_elo = safe_float(winner["surface_elo"].get(surface), START_ELO)
    loser_surface_elo = safe_float(loser["surface_elo"].get(surface), START_ELO)

    new_winner_surface, new_loser_surface = update_elo(winner_surface_elo, loser_surface_elo)

    winner["surface_elo"][surface] = new_winner_surface
    loser["surface_elo"][surface] = new_loser_surface

    winner["surface_matches"][surface] = winner["surface_matches"].get(surface, 0) + 1
    loser["surface_matches"][surface] = loser["surface_matches"].get(surface, 0) + 1

    return True


def build_elo():
    ensure_dirs()

    ratings = {}
    report = {
        "generated_at": now_iso(),
        "start_year": START_YEAR,
        "end_year": END_YEAR,
        "start_elo": START_ELO,
        "k_factor": K_FACTOR,
        "sources": {
            "atp": ATP_BASE,
            "wta": WTA_BASE,
        },
        "years": {},
    }

    for tour in ["atp", "wta"]:
        print(f"Loading players: {tour}")
        players = load_players(tour)

        for year in range(START_YEAR, END_YEAR + 1):
            print(f"Loading matches: {tour} {year}")
            rows = load_matches_for_year(tour, year)

            rows.sort(
                key=lambda r: (
                    str(r.get("tourney_date") or ""),
                    safe_int(r.get("match_num"), 0),
                )
            )

            processed = 0
            for row in rows:
                if process_match(row, tour, ratings, players):
                    processed += 1

            report["years"][f"{tour}_{year}"] = {
                "loaded": len(rows),
                "processed": processed,
            }

            print(f"{tour} {year}: loaded={len(rows)} processed={processed}")

    output = {
        "generated_at": now_iso(),
        "timezone": TZ_NAME,
        "model": "ai77_simple_tennis_elo_v1",
        "start_year": START_YEAR,
        "end_year": END_YEAR,
        "start_elo": START_ELO,
        "k_factor": K_FACTOR,
        "description": "Simple ATP/WTA ELO built from Jeff Sackmann match results. Overall ELO and surface ELO.",
        "ratings": {},
        "name_index": {},
    }

    for key, row in ratings.items():
        row = dict(row)

        row["overall_elo"] = round(safe_float(row["overall_elo"]), 2)
        row["confidence"] = confidence_label(row.get("matches", 0))

        row["surface_elo"] = {
            surface: round(safe_float(value), 2)
            for surface, value in row.get("surface_elo", {}).items()
        }

        output["ratings"][key] = row

        name_key = str(row.get("player_name") or "").strip().lower()
        if name_key:
            output["name_index"].setdefault(name_key, []).append(key)

    report["rating_count"] = len(output["ratings"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("")
    print("TENNIS ELO DONE")
    print(f"Years:        {START_YEAR}-{END_YEAR}")
    print(f"Ratings:      {len(output['ratings'])}")
    print(f"Output:       {OUTPUT_FILE}")
    print(f"Report:       {REPORT_FILE}")
    print("")


if __name__ == "__main__":
    build_elo()

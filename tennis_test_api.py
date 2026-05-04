import os
import requests
import json
from datetime import datetime

API_KEY = os.getenv("3ce2788e6d9f418f7909a106fd7f75f5839b2666d8f3275a3bf075fef6a4d92f")
BASE_URL = "https://api.api-tennis.com/tennis/"

if not API_KEY:
    raise Exception("Missing API_KEY")

def call_api(params):
    params["APIkey"] = API_KEY
    res = requests.get(BASE_URL, params=params)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()

# 1. GET TODAY MATCHES
today = datetime.utcnow().strftime("%Y-%m-%d")

print("Fetching matches...")
fixtures = call_api({
    "method": "get_fixtures",
    "date_start": today,
    "date_stop": today
})

matches = fixtures.get("result", [])
print(f"Matches found: {len(matches)}")

if not matches:
    print("No matches today")
    exit()

match = matches[0]

print("\nSample match:")
print(match)

event_key = match.get("event_key")
player1 = match.get("event_first_player")
player2 = match.get("event_second_player")

# 2. GET ODDS
print("\nFetching odds...")
odds = call_api({
    "method": "get_odds",
    "event_key": event_key
})

# 3. GET H2H
print("\nFetching H2H...")
h2h = call_api({
    "method": "get_H2H",
    "first_player_key": match.get("first_player_key"),
    "second_player_key": match.get("second_player_key")
})

# SAVE EVERYTHING
data = {
    "match": match,
    "odds": odds,
    "h2h": h2h
}

with open("tennis_sample.json", "w") as f:
    json.dump(data, f, indent=2)

print("\nSaved tennis_sample.json")

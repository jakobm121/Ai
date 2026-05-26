import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_NAME = "Europe/Ljubljana"

DATA_DIR = "data"
OUTPUT_DIR = "jure"

RESULTS_FILE = f"{DATA_DIR}/tennis_results.json"

PROBE_FILE = f"{OUTPUT_DIR}/history_probe.json"
DEBUG_FILE = f"{OUTPUT_DIR}/history_probe_debug.json"
REPORT_FILE = f"{OUTPUT_DIR}/history_probe_report.md"

MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "10"))
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "0.4"))

# Poskusi najti API ključ iz več možnih imen, da ne rabiva takoj vedeti točnega imena secreta.
API_KEY = (
    os.getenv("TENNIS_API_KEY")
    or os.getenv("API_TENNIS_KEY")
    or os.getenv("API_KEY")
    or os.getenv("APISPORTS_KEY")
    or ""
)

# Če imaš API-Sports tennis, bo najverjetneje:
# https://v1.tennis.api-sports.io
API_BASE_URL = os.getenv("TENNIS_API_BASE_URL", "https://v1.tennis.api-sports.io").rstrip("/")

# Pri API-Sports je host ponavadi v headerju x-rapidapi-host ali x-apisports-key.
API_HOST = os.getenv("TENNIS_API_HOST", "v1.tennis.api-sports.io")


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


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


def save_text(path, text):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def unique_players_from_results(results):
    players = {}

    for p in results:
        if not isinstance(p, dict):
            continue

        first_key = p.get("first_player_key")
        second_key = p.get("second_player_key")
        first_name = p.get("first_player_name")
        second_name = p.get("second_player_name")

        if first_key is not None:
            players[str(first_key)] = {
                "player_key": first_key,
                "player_name": first_name,
                "source": "first_player",
            }

        if second_key is not None:
            players[str(second_key)] = {
                "player_key": second_key,
                "player_name": second_name,
                "source": "second_player",
            }

    return list(players.values())


def build_headers():
    headers = {
        "Accept": "application/json",
        "User-Agent": "jure-profile-probe/1.0",
    }

    if API_KEY:
        # Pokrijemo oba pogosta načina.
        headers["x-apisports-key"] = API_KEY
        headers["x-rapidapi-key"] = API_KEY

    if API_HOST:
        headers["x-rapidapi-host"] = API_HOST

    return headers


def api_get(path, params):
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE_URL}{path}"
    if query:
        url = f"{url}?{query}"

    req = urllib.request.Request(url, headers=build_headers(), method="GET")

    started = time.time()

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
            elapsed = round(time.time() - started, 3)

            try:
                body = json.loads(raw_body)
            except Exception:
                body = {
                    "_non_json_body": raw_body[:3000],
                }

            return {
                "ok": True,
                "status": resp.status,
                "elapsed_seconds": elapsed,
                "url": redact_url(url),
                "body": body,
                "error": None,
            }

    except Exception as e:
        elapsed = round(time.time() - started, 3)
        return {
            "ok": False,
            "status": None,
            "elapsed_seconds": elapsed,
            "url": redact_url(url),
            "body": None,
            "error": str(e),
        }


def redact_url(url):
    if API_KEY and API_KEY in url:
        return url.replace(API_KEY, "***")
    return url


def body_has_history(body):
    """
    Ne vemo še strukture API-ja, zato preverimo grobo:
    - ali ima response list
    - ali ima results/result/fixtures/events
    - ali je notri vsaj nekaj podobnega tekmam
    """
    if body is None:
        return False

    if isinstance(body, list):
        return len(body) > 0

    if not isinstance(body, dict):
        return False

    possible_keys = [
        "response",
        "results",
        "result",
        "fixtures",
        "events",
        "data",
        "matches",
    ]

    for key in possible_keys:
        value = body.get(key)
        if isinstance(value, list) and len(value) > 0:
            return True
        if isinstance(value, dict) and len(value) > 0:
            return True

    return False


def summarize_body_shape(body):
    if body is None:
        return {
            "type": "none",
        }

    if isinstance(body, list):
        return {
            "type": "list",
            "length": len(body),
            "first_item_keys": list(body[0].keys())[:30] if body and isinstance(body[0], dict) else [],
        }

    if isinstance(body, dict):
        summary = {
            "type": "dict",
            "top_keys": list(body.keys())[:40],
        }

        for key in ["response", "results", "result", "fixtures", "events", "data", "matches"]:
            value = body.get(key)
            if isinstance(value, list):
                summary[f"{key}_type"] = "list"
                summary[f"{key}_length"] = len(value)
                if value and isinstance(value[0], dict):
                    summary[f"{key}_first_item_keys"] = list(value[0].keys())[:40]
            elif isinstance(value, dict):
                summary[f"{key}_type"] = "dict"
                summary[f"{key}_keys"] = list(value.keys())[:40]

        return summary

    return {
        "type": type(body).__name__,
    }


def candidate_requests(player_key):
    """
    Tukaj namenoma testiramo več možnih endpointov, ker še ne vemo točnega API formata.

    Ko bomo videli kateri dela, bomo kasneje naredili čist in enostaven builder.
    """
    return [
        {
            "label": "fixtures_player",
            "path": "/fixtures",
            "params": {"player": player_key},
        },
        {
            "label": "fixtures_player_id",
            "path": "/fixtures",
            "params": {"player_id": player_key},
        },
        {
            "label": "fixtures_player_key",
            "path": "/fixtures",
            "params": {"player_key": player_key},
        },
        {
            "label": "games_player",
            "path": "/games",
            "params": {"player": player_key},
        },
        {
            "label": "games_player_id",
            "path": "/games",
            "params": {"player_id": player_key},
        },
        {
            "label": "matches_player",
            "path": "/matches",
            "params": {"player": player_key},
        },
        {
            "label": "events_player",
            "path": "/events",
            "params": {"player": player_key},
        },
        {
            "label": "results_player",
            "path": "/results",
            "params": {"player": player_key},
        },
    ]


def probe_player(player):
    player_key = player.get("player_key")

    attempts = []

    for req in candidate_requests(player_key):
        response = api_get(req["path"], req["params"])

        attempts.append({
            "label": req["label"],
            "path": req["path"],
            "params": req["params"],
            "ok": response["ok"],
            "status": response["status"],
            "elapsed_seconds": response["elapsed_seconds"],
            "url": response["url"],
            "error": response["error"],
            "has_history": body_has_history(response["body"]),
            "body_shape": summarize_body_shape(response["body"]),
            "body": response["body"],
        })

        # Če najdemo endpoint, ki očitno vrača zgodovino, ne trošimo naprej za tega igralca.
        if response["ok"] and body_has_history(response["body"]):
            break

        time.sleep(SLEEP_SECONDS)

    working = [a for a in attempts if a["ok"] and a["has_history"]]

    return {
        "player": player,
        "working_endpoint_found": len(working) > 0,
        "best_attempt_label": working[0]["label"] if working else None,
        "attempts": attempts,
    }


def make_report(generated_at, source_count, players, probe_results):
    lines = []

    lines.append("# Jure Player History Probe")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Source file: `{RESULTS_FILE}`")
    lines.append(f"- Source picks loaded: **{source_count}**")
    lines.append(f"- Unique players found: **{len(players)}**")
    lines.append(f"- Players probed: **{len(probe_results)}**")
    lines.append(f"- API base URL: `{API_BASE_URL}`")
    lines.append("")

    found = [r for r in probe_results if r["working_endpoint_found"]]
    lines.append(f"- Players with working history endpoint: **{len(found)} / {len(probe_results)}**")
    lines.append("")

    lines.append("## Endpoint results by player")
    lines.append("")
    lines.append("| Player | Key | Working | Best endpoint |")
    lines.append("|---|---:|---:|---|")

    for r in probe_results:
        p = r["player"]
        lines.append(
            f"| {p.get('player_name') or ''} | {p.get('player_key')} | "
            f"{'yes' if r['working_endpoint_found'] else 'no'} | {r.get('best_attempt_label') or ''} |"
        )

    lines.append("")
    lines.append("## Attempt details")
    lines.append("")

    for r in probe_results:
        p = r["player"]
        lines.append(f"### {p.get('player_name') or ''} / {p.get('player_key')}")
        lines.append("")
        lines.append("| Attempt | OK | Status | Has history | Body type | Main keys | Error |")
        lines.append("|---|---:|---:|---:|---|---|---|")

        for a in r["attempts"]:
            shape = a.get("body_shape") or {}
            main_keys = shape.get("top_keys") or shape.get("first_item_keys") or []
            main_keys_text = ", ".join(str(x) for x in main_keys[:12])
            err = str(a.get("error") or "").replace("|", "/")[:120]

            lines.append(
                f"| {a['label']} | {a['ok']} | {a.get('status') or ''} | "
                f"{a['has_history']} | {shape.get('type', '')} | {main_keys_text} | {err} |"
            )

        lines.append("")

    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{PROBE_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    ensure_dirs()

    raw = load_json(RESULTS_FILE, [])
    if not isinstance(raw, list):
        raw = []

    players = unique_players_from_results(raw)
    selected_players = players[:MAX_PLAYERS]

    probe_results = []

    if not API_KEY:
        debug = {
            "generated_at": now_iso(),
            "error": "Missing API key. Set TENNIS_API_KEY, API_TENNIS_KEY, API_KEY, or APISPORTS_KEY.",
            "source_file": RESULTS_FILE,
            "source_count": len(raw),
            "unique_players_found": len(players),
            "selected_players": selected_players,
        }

        save_json(DEBUG_FILE, debug)

        report = "# Jure Player History Probe\n\nMissing API key. Set `TENNIS_API_KEY` in GitHub Secrets.\n"
        save_text(REPORT_FILE, report)

        print("ERROR: Missing API key. Set TENNIS_API_KEY.")
        return

    for player in selected_players:
        print(f"Probing player {player.get('player_name')} / {player.get('player_key')} ...")
        result = probe_player(player)
        probe_results.append(result)
        time.sleep(SLEEP_SECONDS)

    generated_at = now_iso()

    output = {
        "generated_at": generated_at,
        "source_file": RESULTS_FILE,
        "source_count": len(raw),
        "unique_players_found": len(players),
        "players_probed": len(selected_players),
        "api_base_url": API_BASE_URL,
        "api_host": API_HOST,
        "results": probe_results,
    }

    debug = {
        "generated_at": generated_at,
        "max_players": MAX_PLAYERS,
        "sleep_seconds": SLEEP_SECONDS,
        "source_file_exists": os.path.exists(RESULTS_FILE),
        "source_count": len(raw),
        "unique_players_found": len(players),
        "players_selected": selected_players,
        "api_base_url": API_BASE_URL,
        "api_host": API_HOST,
        "api_key_present": bool(API_KEY),
        "candidate_count_per_player": len(candidate_requests("x")),
    }

    save_json(PROBE_FILE, output)
    save_json(DEBUG_FILE, debug)

    report = make_report(
        generated_at=generated_at,
        source_count=len(raw),
        players=players,
        probe_results=probe_results,
    )
    save_text(REPORT_FILE, report)

    print("")
    print("JURE PROFILE PROBE DONE")
    print(f"source picks: {len(raw)}")
    print(f"unique players: {len(players)}")
    print(f"players probed: {len(selected_players)}")
    print(f"history probe: {PROBE_FILE}")
    print(f"debug: {DEBUG_FILE}")
    print(f"report: {REPORT_FILE}")


if __name__ == "__main__":
    main()

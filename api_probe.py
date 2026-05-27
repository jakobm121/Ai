import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict

TZ_NAME = "Europe/Ljubljana"

OUTPUT_DIR = os.getenv("PROBE_DIR", "jure_probe")

# API-SPORTS / API-Tennis style defaults.
# Put your API key in GitHub Secrets as API_TENNIS_KEY.
API_KEY = os.getenv("API_TENNIS_KEY") or os.getenv("API_KEY") or ""
BASE_URL = os.getenv("API_TENNIS_BASE_URL", "https://v1.tennis.api-sports.io").rstrip("/")
HOST = os.getenv("API_TENNIS_HOST", "v1.tennis.api-sports.io")

# How many past days to probe. Default: last 10 days including today.
DAYS_BACK = int(os.getenv("DAYS_BACK", "10"))

# Endpoint can be changed from workflow if your API uses a different route.
FIXTURES_ENDPOINT = os.getenv("FIXTURES_ENDPOINT", "/fixtures")

# Some APIs use date, some use day. Default is date.
DATE_PARAM = os.getenv("DATE_PARAM", "date")

# Delay between API calls so we do not hammer the API.
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "0.35"))

RAW_FILE = f"{OUTPUT_DIR}/history_raw.json"
FIELDS_FILE = f"{OUTPUT_DIR}/history_fields.json"
SAMPLES_FILE = f"{OUTPUT_DIR}/history_samples.json"
REPORT_FILE = f"{OUTPUT_DIR}/history_probe_report.md"
DEBUG_FILE = f"{OUTPUT_DIR}/history_probe_debug.json"


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def save_json(path, data):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_text(path, text):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def make_headers():
    # API-SPORTS usually accepts x-apisports-key.
    # RapidAPI versions usually accept x-rapidapi-key + x-rapidapi-host.
    headers = {
        "Accept": "application/json",
        "User-Agent": "jure-history-probe/1.0",
    }

    if API_KEY:
        headers["x-apisports-key"] = API_KEY
        headers["x-rapidapi-key"] = API_KEY
        headers["x-rapidapi-host"] = HOST

    return headers


def api_get(endpoint, params):
    url = f"{BASE_URL}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(url, headers=make_headers(), method="GET")

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(body)
            except Exception:
                data = {"_raw_text": body}

            return {
                "ok": 200 <= status < 300,
                "status": status,
                "url": url,
                "data": data,
                "error": None,
            }

    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "url": url,
            "data": None,
            "error": str(e),
        }


def extract_response_list(payload):
    # API-SPORTS format is usually {"response": [...]}
    if isinstance(payload, dict):
        for key in ["response", "data", "results", "fixtures", "matches", "events"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value

        # Some APIs return a dict of items.
        if all(isinstance(v, dict) for v in payload.values()) and payload:
            return list(payload.values())

    if isinstance(payload, list):
        return payload

    return []


def flatten_paths(obj, prefix=""):
    paths = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = f"{prefix}.{key}" if prefix else str(key)
            paths.append(new_prefix)
            paths.extend(flatten_paths(value, new_prefix))

    elif isinstance(obj, list):
        # Use [] marker so field map is not polluted by list indexes.
        new_prefix = f"{prefix}[]" if prefix else "[]"
        paths.append(new_prefix)

        for item in obj[:5]:
            paths.extend(flatten_paths(item, new_prefix))

    return paths


def sample_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def collect_field_info(items):
    path_counter = Counter()
    type_map = defaultdict(Counter)
    examples = {}

    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                path_counter[path] += 1
                type_map[path][sample_type(value)] += 1

                if path not in examples and not isinstance(value, (dict, list)):
                    examples[path] = value

                walk(value, path)

        elif isinstance(obj, list):
            path = f"{prefix}[]" if prefix else "[]"
            path_counter[path] += 1
            type_map[path]["list_items"] += len(obj)

            for item in obj[:5]:
                walk(item, path)

    for item in items:
        walk(item)

    rows = []
    for path, count in path_counter.most_common():
        rows.append({
            "field": path,
            "count": count,
            "types": dict(type_map[path]),
            "example": examples.get(path),
        })

    return rows


def get_nested(data, path, default=None):
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
    return cur if cur is not None else default


def guess_match_identity(item):
    # Try common shapes without depending on exact docs.
    candidates = {
        "fixture_id": (
            item.get("fixture_id")
            or item.get("event_key")
            or item.get("id")
            or get_nested(item, "fixture.id")
            or get_nested(item, "event.id")
            or get_nested(item, "game.id")
        ),
        "date": (
            item.get("date")
            or get_nested(item, "fixture.date")
            or get_nested(item, "event.date")
            or item.get("event_date")
        ),
        "tournament": (
            item.get("tournament")
            or get_nested(item, "league.name")
            or get_nested(item, "tournament.name")
            or get_nested(item, "competition.name")
        ),
        "home": (
            item.get("first_player_name")
            or item.get("home")
            or get_nested(item, "teams.home.name")
            or get_nested(item, "players.first.name")
            or get_nested(item, "home.name")
        ),
        "away": (
            item.get("second_player_name")
            or item.get("away")
            or get_nested(item, "teams.away.name")
            or get_nested(item, "players.second.name")
            or get_nested(item, "away.name")
        ),
        "score": (
            item.get("score")
            or item.get("final_score")
            or get_nested(item, "scores")
            or get_nested(item, "score.fulltime")
        ),
        "status": (
            item.get("status")
            or get_nested(item, "fixture.status.long")
            or get_nested(item, "fixture.status.short")
            or get_nested(item, "status.long")
        ),
    }

    return candidates


def make_dates(days_back):
    today = datetime.now(ZoneInfo(TZ_NAME)).date()
    start = today - timedelta(days=days_back - 1)
    return [(start + timedelta(days=i)).isoformat() for i in range(days_back)]


def make_report(generated_at, dates, raw_calls, items, field_rows, samples):
    lines = []
    lines.append("# Tennis API History Probe")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Probe config")
    lines.append("")
    lines.append(f"- Base URL: `{BASE_URL}`")
    lines.append(f"- Endpoint: `{FIXTURES_ENDPOINT}`")
    lines.append(f"- Date param: `{DATE_PARAM}`")
    lines.append(f"- Days checked: **{len(dates)}**")
    lines.append(f"- Dates: `{', '.join(dates)}`")
    lines.append("")
    lines.append("## API call summary")
    lines.append("")
    lines.append("| Date | OK | Status | Items | Error |")
    lines.append("|---|---:|---:|---:|---|")

    for call in raw_calls:
        err = call.get("error") or ""
        lines.append(
            f"| {call.get('date')} | {call.get('ok')} | {call.get('status')} | "
            f"{call.get('items_count')} | {err[:120]} |"
        )

    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- Total extracted match/event items: **{len(items)}**")
    lines.append(f"- Unique fields found: **{len(field_rows)}**")
    lines.append("")
    lines.append("## Top fields")
    lines.append("")
    lines.append("| Field | Count | Types | Example |")
    lines.append("|---|---:|---|---|")

    for row in field_rows[:80]:
        example = row.get("example")
        if isinstance(example, (dict, list)):
            example = json.dumps(example, ensure_ascii=False)[:80]
        else:
            example = str(example)[:80]
        types = ", ".join([f"{k}:{v}" for k, v in row.get("types", {}).items()])
        lines.append(f"| `{row['field']}` | {row['count']} | {types} | {example} |")

    lines.append("")
    lines.append("## Match samples")
    lines.append("")
    lines.append("| ID | Date | Tournament | Home | Away | Status | Score |")
    lines.append("|---|---|---|---|---|---|---|")

    for sample in samples[:30]:
        score = sample.get("score")
        if isinstance(score, (dict, list)):
            score = json.dumps(score, ensure_ascii=False)[:120]
        lines.append(
            f"| {sample.get('fixture_id','')} | {sample.get('date','')} | {sample.get('tournament','')} | "
            f"{sample.get('home','')} | {sample.get('away','')} | {sample.get('status','')} | {score or ''} |"
        )

    lines.append("")
    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{RAW_FILE}`")
    lines.append(f"- `{FIELDS_FILE}`")
    lines.append(f"- `{SAMPLES_FILE}`")
    lines.append(f"- `{DEBUG_FILE}`")
    lines.append(f"- `{REPORT_FILE}`")
    lines.append("")

    return "\n".join(lines)


def main():
    ensure_dirs()

    generated_at = now_iso()
    dates = make_dates(DAYS_BACK)

    raw_calls = []
    all_items = []

    for date in dates:
        result = api_get(FIXTURES_ENDPOINT, {DATE_PARAM: date})
        items = extract_response_list(result.get("data"))

        raw_calls.append({
            "date": date,
            "ok": result.get("ok"),
            "status": result.get("status"),
            "url": result.get("url"),
            "items_count": len(items),
            "error": result.get("error"),
            "data": result.get("data"),
        })

        for item in items:
            if isinstance(item, dict):
                x = dict(item)
                x["_probe_date"] = date
                all_items.append(x)

        time.sleep(SLEEP_SECONDS)

    field_rows = collect_field_info(all_items)
    samples = [guess_match_identity(item) for item in all_items[:100]]

    raw_out = {
        "generated_at": generated_at,
        "config": {
            "base_url": BASE_URL,
            "endpoint": FIXTURES_ENDPOINT,
            "date_param": DATE_PARAM,
            "days_back": DAYS_BACK,
            "dates": dates,
        },
        "calls": raw_calls,
        "items": all_items,
    }

    debug = {
        "generated_at": generated_at,
        "api_key_present": bool(API_KEY),
        "base_url": BASE_URL,
        "host": HOST,
        "endpoint": FIXTURES_ENDPOINT,
        "date_param": DATE_PARAM,
        "dates": dates,
        "calls": [
            {
                "date": c.get("date"),
                "ok": c.get("ok"),
                "status": c.get("status"),
                "url": c.get("url"),
                "items_count": c.get("items_count"),
                "error": c.get("error"),
            }
            for c in raw_calls
        ],
        "total_items": len(all_items),
        "unique_fields": len(field_rows),
    }

    report = make_report(generated_at, dates, raw_calls, all_items, field_rows, samples)

    save_json(RAW_FILE, raw_out)
    save_json(FIELDS_FILE, field_rows)
    save_json(SAMPLES_FILE, samples)
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, report)

    print("")
    print("TENNIS HISTORY PROBE DONE")
    print(f"API key present: {bool(API_KEY)}")
    print(f"base url: {BASE_URL}")
    print(f"endpoint: {FIXTURES_ENDPOINT}")
    print(f"date param: {DATE_PARAM}")
    print(f"days checked: {len(dates)}")
    print(f"total items: {len(all_items)}")
    print(f"unique fields: {len(field_rows)}")
    print("")
    print(f"Report: {REPORT_FILE}")
    print(f"Raw: {RAW_FILE}")
    print(f"Fields: {FIELDS_FILE}")
    print(f"Samples: {SAMPLES_FILE}")


if __name__ == "__main__":
    main()

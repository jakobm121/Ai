import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict

TZ_NAME = "Europe/Ljubljana"

API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("API_TENNIS_BASE_URL", "https://api.api-tennis.com/tennis/").rstrip("/") + "/"

PROBE_DIR = os.getenv("PROBE_DIR", "jure_probe")
HISTORY_SAMPLE_FILE = os.getenv("HISTORY_SAMPLE_FILE", f"{PROBE_DIR}/history_raw_sample.json")

MAX_EVENTS = int(os.getenv("MAX_EVENTS", "80"))
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "0.35"))

ODDS_METHOD = os.getenv("ODDS_METHOD", "get_odds")

ODDS_RAW_FILE = f"{PROBE_DIR}/odds_probe_raw.json"
ODDS_FIELDS_FILE = f"{PROBE_DIR}/odds_probe_fields.json"
ODDS_REPORT_FILE = f"{PROBE_DIR}/odds_probe_report.md"
ODDS_DEBUG_FILE = f"{PROBE_DIR}/odds_probe_debug.json"


def ensure_dirs():
    os.makedirs(PROBE_DIR, exist_ok=True)


def now_iso():
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
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


def api_get(params):
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "jure-odds-probe/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")

            try:
                data = json.loads(body)
            except Exception:
                data = {"_raw_text": body[:5000]}

            return {
                "ok": 200 <= status < 300,
                "status": status,
                "url": url,
                "params": params,
                "data": data,
                "error": None,
            }

    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "url": url,
            "params": params,
            "data": None,
            "error": str(e),
        }


def extract_response_list(payload):
    if isinstance(payload, dict):
        for key in ["result", "response", "data", "odds", "markets"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value

        for key in ["result", "response", "data", "odds", "markets"]:
            value = payload.get(key)
            if isinstance(value, dict):
                return list(value.values())

    if isinstance(payload, list):
        return payload

    return []


def payload_status(payload):
    if not isinstance(payload, dict):
        return {}

    return {
        "success": payload.get("success"),
        "error": payload.get("error"),
        "message": payload.get("message"),
    }


def compact_payload(payload, limit_items=5):
    if payload is None:
        return None

    if isinstance(payload, dict):
        items = extract_response_list(payload)
        return {
            "success": payload.get("success"),
            "error": payload.get("error"),
            "message": payload.get("message"),
            "items_count": len(items),
            "items_sample": items[:limit_items],
        }

    if isinstance(payload, list):
        return {
            "items_count": len(payload),
            "items_sample": payload[:limit_items],
        }

    return str(payload)[:5000]


def get_history_items(raw_history):
    if isinstance(raw_history, dict):
        for key in ["items_sample", "items", "result", "response", "data"]:
            value = raw_history.get(key)
            if isinstance(value, list):
                return value
    elif isinstance(raw_history, list):
        return raw_history

    return []


def event_key(item):
    return (
        item.get("event_key")
        or item.get("fixture_id")
        or item.get("id")
        or item.get("event_id")
    )


def event_summary(item):
    return {
        "event_key": event_key(item),
        "date": item.get("event_date") or item.get("date"),
        "time": item.get("event_time") or item.get("time"),
        "first_player": item.get("event_first_player") or item.get("first_player"),
        "second_player": item.get("event_second_player") or item.get("second_player"),
        "tournament": item.get("tournament_name") or item.get("tournament"),
        "round": item.get("tournament_round") or item.get("event_round") or item.get("round"),
        "status": item.get("event_status") or item.get("status"),
        "final_result": item.get("event_final_result") or item.get("final_result"),
    }


def collect_field_info(items):
    path_counter = Counter()
    type_map = defaultdict(Counter)
    examples = {}

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


def build_query_variants(key):
    return [
        {
            "name": "event_key",
            "params": {
                "method": ODDS_METHOD,
                "APIkey": API_KEY,
                "event_key": key,
            },
        },
        {
            "name": "match_key",
            "params": {
                "method": ODDS_METHOD,
                "APIkey": API_KEY,
                "match_key": key,
            },
        },
        {
            "name": "fixture_id",
            "params": {
                "method": ODDS_METHOD,
                "APIkey": API_KEY,
                "fixture_id": key,
            },
        },
        {
            "name": "event_id",
            "params": {
                "method": ODDS_METHOD,
                "APIkey": API_KEY,
                "event_id": key,
            },
        },
    ]


def make_report(generated_at, events, calls, odds_items, field_rows):
    lines = []
    lines.append("# API-Tennis Odds Probe")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Config")
    lines.append("")
    lines.append(f"- Base URL: `{BASE_URL}`")
    lines.append(f"- API key present: **{bool(API_KEY)}**")
    lines.append(f"- Odds method: `{ODDS_METHOD}`")
    lines.append(f"- History sample file: `{HISTORY_SAMPLE_FILE}`")
    lines.append(f"- Events tested: **{len(events)}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Odds items found: **{len(odds_items)}**")
    lines.append(f"- Unique odds fields: **{len(field_rows)}**")
    lines.append("")

    if odds_items:
        lines.append("✅ API appears to return odds for historical events.")
    else:
        lines.append("⚠️ No historical odds were returned from tested variants.")
    lines.append("")

    lines.append("## Calls")
    lines.append("")
    lines.append("| Event | Variant | OK | Status | Items | API success | Error/message |")
    lines.append("|---|---|---:|---:|---:|---:|---|")

    for c in calls[:200]:
        msg = c.get("api_error") or c.get("api_message") or c.get("error") or ""
        lines.append(
            f"| {c.get('event_key')} | `{c.get('variant')}` | {c.get('ok')} | {c.get('status')} | "
            f"{c.get('items_count')} | {c.get('api_success')} | {str(msg)[:120]} |"
        )

    lines.append("")
    lines.append("## Odds fields")
    lines.append("")
    lines.append("| Field | Count | Types | Example |")
    lines.append("|---|---:|---|---|")

    for row in field_rows[:120]:
        example = row.get("example")
        if isinstance(example, (dict, list)):
            example = json.dumps(example, ensure_ascii=False)[:80]
        else:
            example = str(example)[:80]
        types = ", ".join([f"{k}:{v}" for k, v in row.get("types", {}).items()])
        lines.append(f"| `{row['field']}` | {row['count']} | {types} | {example} |")

    lines.append("")
    lines.append("## Tested events")
    lines.append("")
    lines.append("| Event key | Date | Match | Tournament | Final |")
    lines.append("|---|---|---|---|---|")

    for e in events[:100]:
        match = f"{e.get('first_player') or ''} - {e.get('second_player') or ''}"
        lines.append(
            f"| {e.get('event_key')} | {e.get('date','')} | {match} | "
            f"{e.get('tournament','')} | {e.get('final_result','')} |"
        )

    lines.append("")
    lines.append("## Files generated")
    lines.append("")
    lines.append(f"- `{ODDS_RAW_FILE}`")
    lines.append(f"- `{ODDS_FIELDS_FILE}`")
    lines.append(f"- `{ODDS_DEBUG_FILE}`")
    lines.append(f"- `{ODDS_REPORT_FILE}`")
    lines.append("")

    return "\n".join(lines)


def main():
    ensure_dirs()
    generated_at = now_iso()

    history = load_json(HISTORY_SAMPLE_FILE, {})
    history_items = get_history_items(history)

    events = []
    seen = set()

    for item in history_items:
        if not isinstance(item, dict):
            continue

        key = event_key(item)
        if not key or key in seen:
            continue

        seen.add(key)
        events.append(event_summary(item))

        if len(events) >= MAX_EVENTS:
            break

    calls = []
    odds_items = []

    for event in events:
        key = event.get("event_key")
        if not key:
            continue

        variants = build_query_variants(key)

        for variant in variants:
            result = api_get(variant["params"])
            items = extract_response_list(result.get("data"))
            status = payload_status(result.get("data"))

            calls.append({
                "event_key": key,
                "variant": variant["name"],
                "ok": result.get("ok"),
                "status": result.get("status"),
                "url": result.get("url"),
                "params": variant["params"],
                "items_count": len(items),
                "api_success": status.get("success"),
                "api_error": status.get("error"),
                "api_message": status.get("message"),
                "error": result.get("error"),
                "data_sample": compact_payload(result.get("data")),
            })

            for item in items:
                if isinstance(item, dict):
                    x = dict(item)
                    x["_probe_event_key"] = key
                    x["_probe_variant"] = variant["name"]
                    odds_items.append(x)

            # If this variant worked for this event, no need to try other parameter names.
            if items:
                break

            time.sleep(SLEEP_SECONDS)

    field_rows = collect_field_info(odds_items)

    raw = {
        "generated_at": generated_at,
        "config": {
            "api_key_present": bool(API_KEY),
            "base_url": BASE_URL,
            "odds_method": ODDS_METHOD,
            "history_sample_file": HISTORY_SAMPLE_FILE,
            "max_events": MAX_EVENTS,
        },
        "events_tested": events,
        "calls": calls,
        "odds_items_sample": odds_items[:300],
        "odds_items_found": len(odds_items),
    }

    debug = {
        "generated_at": generated_at,
        "api_key_present": bool(API_KEY),
        "base_url": BASE_URL,
        "odds_method": ODDS_METHOD,
        "history_sample_file": HISTORY_SAMPLE_FILE,
        "events_tested": len(events),
        "calls_made": len(calls),
        "odds_items_found": len(odds_items),
        "unique_fields": len(field_rows),
        "calls_summary": [
            {
                "event_key": c.get("event_key"),
                "variant": c.get("variant"),
                "ok": c.get("ok"),
                "status": c.get("status"),
                "items_count": c.get("items_count"),
                "api_success": c.get("api_success"),
                "api_error": c.get("api_error"),
                "api_message": c.get("api_message"),
                "error": c.get("error"),
            }
            for c in calls[:300]
        ],
    }

    report = make_report(generated_at, events, calls, odds_items, field_rows)

    save_json(ODDS_RAW_FILE, raw)
    save_json(ODDS_FIELDS_FILE, field_rows)
    save_json(ODDS_DEBUG_FILE, debug)
    save_text(ODDS_REPORT_FILE, report)

    print("")
    print("API-TENNIS ODDS PROBE DONE")
    print(f"API key present: {bool(API_KEY)}")
    print(f"history sample file: {HISTORY_SAMPLE_FILE}")
    print(f"events tested: {len(events)}")
    print(f"calls made: {len(calls)}")
    print(f"odds items found: {len(odds_items)}")
    print(f"unique odds fields: {len(field_rows)}")
    print("")
    print(f"Report: {ODDS_REPORT_FILE}")
    print(f"Raw: {ODDS_RAW_FILE}")
    print(f"Fields: {ODDS_FIELDS_FILE}")
    print(f"Debug: {ODDS_DEBUG_FILE}")


if __name__ == "__main__":
    main()

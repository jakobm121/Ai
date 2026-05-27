import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict

TZ_NAME = "Europe/Ljubljana"

# Your existing API style:
# API_KEY = os.getenv("API_KEY")
# BASE_URL = "https://api.api-tennis.com/tennis/"
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("API_TENNIS_BASE_URL", "https://api.api-tennis.com/tennis/").rstrip("/") + "/"

OUTPUT_DIR = os.getenv("PROBE_DIR", "jure_probe")
DAYS_BACK = int(os.getenv("DAYS_BACK", "10"))
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "0.35"))

# Main method for API-Tennis. The probe will also try backup variants.
MAIN_METHOD = os.getenv("API_METHOD", "get_fixtures")

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


def make_dates(days_back):
    today = datetime.now(ZoneInfo(TZ_NAME)).date()
    start = today - timedelta(days=days_back - 1)
    return start.isoformat(), today.isoformat(), [(start + timedelta(days=i)).isoformat() for i in range(days_back)]


def api_get(params):
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "jure-api-tennis-probe/1.0",
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
                data = {"_raw_text": body}

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
    # API-Tennis usually returns {"success": 1, "result": [...]}
    if isinstance(payload, dict):
        for key in ["result", "response", "data", "fixtures", "matches", "events"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value

        # Sometimes a successful response can be a dict of records.
        for key in ["result", "response", "data"]:
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


def build_query_variants(start_date, end_date, single_dates):
    variants = []

    # Variant 1: most likely API-Tennis range format.
    variants.append({
        "name": "range_date_start_date_stop",
        "params": {
            "method": MAIN_METHOD,
            "APIkey": API_KEY,
            "date_start": start_date,
            "date_stop": end_date,
        },
        "mode": "range",
    })

    # Variant 2: another possible range naming.
    variants.append({
        "name": "range_from_to",
        "params": {
            "method": MAIN_METHOD,
            "APIkey": API_KEY,
            "from": start_date,
            "to": end_date,
        },
        "mode": "range",
    })

    # Variant 3: per-day date.
    for d in single_dates:
        variants.append({
            "name": "single_date",
            "date": d,
            "params": {
                "method": MAIN_METHOD,
                "APIkey": API_KEY,
                "date": d,
            },
            "mode": "daily",
        })

    # Variant 4: if provider uses get_events instead of get_fixtures.
    variants.append({
        "name": "get_events_range_date_start_date_stop",
        "params": {
            "method": "get_events",
            "APIkey": API_KEY,
            "date_start": start_date,
            "date_stop": end_date,
        },
        "mode": "range",
    })

    return variants


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


def get_nested(data, path, default=None):
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
    return cur if cur is not None else default


def guess_match_identity(item):
    first_player = (
        item.get("event_first_player")
        or item.get("first_player")
        or item.get("player1")
        or item.get("player_one")
        or item.get("home")
        or get_nested(item, "players.first.name")
        or get_nested(item, "home.name")
    )

    second_player = (
        item.get("event_second_player")
        or item.get("second_player")
        or item.get("player2")
        or item.get("player_two")
        or item.get("away")
        or get_nested(item, "players.second.name")
        or get_nested(item, "away.name")
    )

    return {
        "event_key": item.get("event_key") or item.get("fixture_id") or item.get("id"),
        "date": item.get("event_date") or item.get("date") or item.get("fixture_date"),
        "time": item.get("event_time") or item.get("time"),
        "tournament": item.get("tournament_name") or item.get("league_name") or item.get("event_tournament") or item.get("tournament"),
        "round": item.get("event_round") or item.get("round"),
        "first_player": first_player,
        "second_player": second_player,
        "status": item.get("event_status") or item.get("status") or item.get("event_final_result"),
        "final_result": item.get("event_final_result") or item.get("final_result") or item.get("score"),
        "first_set": item.get("event_first_set"),
        "second_set": item.get("event_second_set"),
        "third_set": item.get("event_third_set"),
        "fourth_set": item.get("event_fourth_set"),
        "fifth_set": item.get("event_fifth_set"),
    }


def dedupe_items(items):
    seen = set()
    out = []

    for item in items:
        if not isinstance(item, dict):
            continue

        key = (
            item.get("event_key")
            or item.get("fixture_id")
            or item.get("id")
            or json.dumps(item, sort_keys=True, ensure_ascii=False)
        )

        if key in seen:
            continue

        seen.add(key)
        out.append(item)

    return out


def make_report(generated_at, start_date, end_date, variants_log, best_variant, items, field_rows, samples):
    lines = []

    lines.append("# API-Tennis History Probe")
    lines.append("")
    lines.append(f"Generated at: **{generated_at}**")
    lines.append("")
    lines.append("## Config")
    lines.append("")
    lines.append(f"- Base URL: `{BASE_URL}`")
    lines.append(f"- API key present: **{bool(API_KEY)}**")
    lines.append(f"- Main method: `{MAIN_METHOD}`")
    lines.append(f"- Date range: **{start_date} → {end_date}**")
    lines.append("")
    lines.append("## Tried query variants")
    lines.append("")
    lines.append("| Variant | OK | Status | Items | API success | Error/message |")
    lines.append("|---|---:|---:|---:|---:|---|")

    for row in variants_log:
        msg = row.get("api_error") or row.get("api_message") or row.get("error") or ""
        lines.append(
            f"| `{row.get('name')}` | {row.get('ok')} | {row.get('status')} | "
            f"{row.get('items_count')} | {row.get('api_success')} | {str(msg)[:150]} |"
        )

    lines.append("")
    lines.append("## Best variant")
    lines.append("")
    if best_variant:
        lines.append(f"- Name: `{best_variant.get('name')}`")
        lines.append(f"- Items: **{best_variant.get('items_count')}**")
        lines.append("")
    else:
        lines.append("No working variant found.")
        lines.append("")

    lines.append("## Overall")
    lines.append("")
    lines.append(f"- Total unique match/event items: **{len(items)}**")
    lines.append(f"- Unique fields found: **{len(field_rows)}**")
    lines.append("")
    lines.append("## Top fields")
    lines.append("")
    lines.append("| Field | Count | Types | Example |")
    lines.append("|---|---:|---|---|")

    for row in field_rows[:100]:
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
    lines.append("| Key | Date | Time | Tournament | Round | Player 1 | Player 2 | Status | Final | Sets |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for s in samples[:50]:
        sets = " / ".join([
            str(s.get("first_set") or ""),
            str(s.get("second_set") or ""),
            str(s.get("third_set") or ""),
            str(s.get("fourth_set") or ""),
            str(s.get("fifth_set") or ""),
        ]).strip(" /")
        lines.append(
            f"| {s.get('event_key','')} | {s.get('date','')} | {s.get('time','')} | "
            f"{s.get('tournament','')} | {s.get('round','')} | {s.get('first_player','')} | "
            f"{s.get('second_player','')} | {s.get('status','')} | {s.get('final_result','')} | {sets} |"
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
    start_date, end_date, single_dates = make_dates(DAYS_BACK)

    variants = build_query_variants(start_date, end_date, single_dates)
    variants_log = []
    all_items = []

    for variant in variants:
        result = api_get(variant["params"])
        items = extract_response_list(result.get("data"))
        status = payload_status(result.get("data"))

        variants_log.append({
            "name": variant.get("name"),
            "date": variant.get("date"),
            "mode": variant.get("mode"),
            "ok": result.get("ok"),
            "status": result.get("status"),
            "url": result.get("url"),
            "params": variant.get("params"),
            "items_count": len(items),
            "api_success": status.get("success"),
            "api_error": status.get("error"),
            "api_message": status.get("message"),
            "error": result.get("error"),
            "data": result.get("data"),
        })

        # Keep all successful items. If both range and daily work, dedupe later.
        for item in items:
            if isinstance(item, dict):
                x = dict(item)
                x["_probe_variant"] = variant.get("name")
                x["_probe_date"] = variant.get("date")
                all_items.append(x)

        time.sleep(SLEEP_SECONDS)

    all_items = dedupe_items(all_items)

    field_rows = collect_field_info(all_items)
    samples = [guess_match_identity(item) for item in all_items[:200]]

    best_variant = None
    if variants_log:
        best_variant = max(variants_log, key=lambda r: r.get("items_count", 0))
        if best_variant.get("items_count", 0) <= 0:
            best_variant = None

    raw_out = {
        "generated_at": generated_at,
        "config": {
            "base_url": BASE_URL,
            "api_key_present": bool(API_KEY),
            "main_method": MAIN_METHOD,
            "days_back": DAYS_BACK,
            "start_date": start_date,
            "end_date": end_date,
        },
        "variants": variants_log,
        "best_variant": best_variant,
        "items": all_items,
    }

    debug = {
        "generated_at": generated_at,
        "api_key_present": bool(API_KEY),
        "base_url": BASE_URL,
        "main_method": MAIN_METHOD,
        "days_back": DAYS_BACK,
        "start_date": start_date,
        "end_date": end_date,
        "total_items": len(all_items),
        "unique_fields": len(field_rows),
        "best_variant": {
            "name": best_variant.get("name"),
            "items_count": best_variant.get("items_count"),
            "params": best_variant.get("params"),
        } if best_variant else None,
        "variants": [
            {
                "name": v.get("name"),
                "date": v.get("date"),
                "ok": v.get("ok"),
                "status": v.get("status"),
                "items_count": v.get("items_count"),
                "api_success": v.get("api_success"),
                "api_error": v.get("api_error"),
                "api_message": v.get("api_message"),
                "error": v.get("error"),
                "url": v.get("url"),
            }
            for v in variants_log
        ],
    }

    report = make_report(
        generated_at=generated_at,
        start_date=start_date,
        end_date=end_date,
        variants_log=variants_log,
        best_variant=best_variant,
        items=all_items,
        field_rows=field_rows,
        samples=samples,
    )

    save_json(RAW_FILE, raw_out)
    save_json(FIELDS_FILE, field_rows)
    save_json(SAMPLES_FILE, samples)
    save_json(DEBUG_FILE, debug)
    save_text(REPORT_FILE, report)

    print("")
    print("API-TENNIS HISTORY PROBE DONE")
    print(f"API key present: {bool(API_KEY)}")
    print(f"base url: {BASE_URL}")
    print(f"main method: {MAIN_METHOD}")
    print(f"date range: {start_date} -> {end_date}")
    print(f"total items: {len(all_items)}")
    print(f"unique fields: {len(field_rows)}")

    if best_variant:
        print(f"best variant: {best_variant.get('name')} ({best_variant.get('items_count')} items)")
    else:
        print("best variant: none")

    print("")
    print(f"Report: {REPORT_FILE}")
    print(f"Raw: {RAW_FILE}")
    print(f"Fields: {FIELDS_FILE}")
    print(f"Samples: {SAMPLES_FILE}")
    print(f"Debug: {DEBUG_FILE}")


if __name__ == "__main__":
    main()

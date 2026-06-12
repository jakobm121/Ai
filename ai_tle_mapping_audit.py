from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import ai_tle_scanner as tle

ROOT_DIR = Path('.')
DEFAULT_OUTPUT_DIR = ROOT_DIR / 'data' / 'tle' / 'mapping_audit'

SAFE_METHODS = {'api_mapping', 'exact_name'}
REVIEW_METHODS = {'unique_surname_initial', 'api_key_unmapped', 'name_fallback', 'unresolved', 'invalid_gender'}


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def pct(n: int, d: int) -> str:
    if not d:
        return ''
    return f'{(100.0 * n / d):.2f}%'


def method_bucket(method: str) -> str:
    if method in SAFE_METHODS:
        return 'safe'
    if method in REVIEW_METHODS:
        return 'review'
    return 'other'


def display_for_key(key: str | None, display: dict[str, str]) -> str:
    if not key:
        return ''
    return display.get(key, '')


def player_audit_row(
    *,
    fixture: dict[str, Any],
    event_key: str,
    side: str,
    api_key: int | None,
    api_name: str,
    gender: str,
    level: str,
    method: str,
    tle_key: str | None,
    tle_display: str,
) -> dict[str, Any]:
    return {
        'event_key': event_key,
        'date': tle.clean(fixture.get('event_date')),
        'time': tle.clean(fixture.get('event_time')),
        'tournament': tle.clean(fixture.get('tournament_name')),
        'tournament_key': tle.clean(fixture.get('tournament_key')),
        'round': tle.clean(fixture.get('tournament_round')),
        'event_type': tle.clean(fixture.get('event_type_type')),
        'side': side,
        'api_player_key': api_key,
        'api_name': api_name,
        'gender': gender,
        'tour_level': level,
        'resolve_method': method,
        'bucket': method_bucket(method),
        'tle_key': tle_key or '',
        'tle_display_name': tle_display,
    }


def write_md(path: Path, summary: dict[str, Any], review_rows: list[dict[str, Any]], event_rows: list[dict[str, Any]]) -> None:
    lines = [
        '# AI TLE Mapping Audit',
        '',
        f"Generated: `{summary.get('generated_at')}`",
        f"Date range: `{summary.get('scan_date_start')}` â `{summary.get('scan_date_end')}`",
        '',
        '## Summary',
        '',
        '| Metric | Value |',
        '|---|---:|',
    ]

    counters = summary.get('counters', {})
    for key in [
        'api_fixture_events',
        'api_odds_events',
        'odds_events_with_fixture',
        'audited_events',
        'audited_player_appearances',
        'safe_player_appearances',
        'review_player_appearances',
        'safe_events_both_players',
        'review_events_any_player',
    ]:
        lines.append(f"| {key} | {counters.get(key, 0)} |")

    total = int(counters.get('audited_player_appearances') or 0)
    safe = int(counters.get('safe_player_appearances') or 0)
    review = int(counters.get('review_player_appearances') or 0)
    lines.extend([
        f'| safe player % | {pct(safe, total)} |',
        f'| review player % | {pct(review, total)} |',
        '',
        '## Resolve methods',
        '',
        '| Method | Count |',
        '|---|---:|',
    ])

    for method, count in summary.get('resolve_method_counts', {}).items():
        lines.append(f'| {method} | {count} |')

    lines.extend([
        '',
        '## Players needing review',
        '',
        '| API key | API name | Gender | Level | Method | TLE key | TLE display | Seen | Example match | Tournament |',
        '|---:|---|---|---|---|---|---|---:|---|---|',
    ])

    grouped: dict[str, dict[str, Any]] = {}
    for row in review_rows:
        key = f"{row.get('gender')}|{row.get('api_player_key')}|{tle.normalize_name(row.get('api_name'))}"
        if key not in grouped:
            grouped[key] = dict(row)
            grouped[key]['seen'] = 0
            grouped[key]['example_match'] = ''
        grouped[key]['seen'] += 1
        if not grouped[key].get('example_match'):
            ev = next((e for e in event_rows if e.get('event_key') == row.get('event_key')), {})
            grouped[key]['example_match'] = ev.get('match', '')

    sorted_review = sorted(
        grouped.values(),
        key=lambda r: (-int(r.get('seen') or 0), str(r.get('resolve_method')), str(r.get('api_name'))),
    )

    for row in sorted_review[:200]:
        lines.append('| ' + ' | '.join([
            str(row.get('api_player_key') or ''),
            tle.clean(row.get('api_name')).replace('|', '-'),
            tle.clean(row.get('gender')),
            tle.clean(row.get('tour_level')),
            tle.clean(row.get('resolve_method')),
            tle.clean(row.get('tle_key')),
            tle.clean(row.get('tle_display_name')).replace('|', '-'),
            str(row.get('seen') or 0),
            tle.clean(row.get('example_match')).replace('|', '-'),
            tle.clean(row.get('tournament')).replace('|', '-'),
        ]) + ' |')

    lines.extend([
        '',
        '## Event audit',
        '',
        '| Date | Time | Level | Gender | Match | Home method | Away method | Status | Book pairs |',
        '|---|---|---|---|---|---|---|---|---:|',
    ])

    for row in event_rows[:300]:
        lines.append('| ' + ' | '.join([
            tle.clean(row.get('date')),
            tle.clean(row.get('time')),
            tle.clean(row.get('tour_level')),
            tle.clean(row.get('gender')),
            tle.clean(row.get('match')).replace('|', '-'),
            tle.clean(row.get('home_resolve_method')),
            tle.clean(row.get('away_resolve_method')),
            tle.clean(row.get('mapping_status')),
            str(row.get('book_pairs_valid') or 0),
        ]) + ' |')

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit API-Tennis daily fixtures/odds player mapping against Tennis-ELO canonical base.')
    parser.add_argument('--date', default=date.today().isoformat())
    parser.add_argument('--duration', type=int, default=1)
    parser.add_argument('--levels', default='challenger,itf,atp_wta,grand_slam,qualifying,unknown')
    parser.add_argument('--timezone', default='Europe/Ljubljana')
    parser.add_argument('--min-start-minutes', type=float, default=0.0, help='0 audits all not-finished matches; 30 audits scanner-like future matches.')
    parser.add_argument('--min-odds', type=float, default=1.20)
    parser.add_argument('--max-odds', type=float, default=8.00)
    parser.add_argument('--min-overround', type=float, default=-0.03)
    parser.add_argument('--max-overround', type=float, default=0.18)
    parser.add_argument('--max-book-deviation', type=float, default=0.35)
    parser.add_argument('--bookmaker', default='Pncl')
    parser.add_argument('--fallback', choices=['none', 'bookmaker', 'clean_average', 'clean_median', 'best'], default='clean_average')
    parser.add_argument('--canonical-manifest', default=tle.DEFAULT_CANONICAL_MANIFEST)
    parser.add_argument('--api-player-mapping', default=tle.DEFAULT_API_PLAYER_MAPPING)
    parser.add_argument('--tournament-metadata', default=tle.DEFAULT_TOURNAMENT_METADATA)
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument('--sleep', type=float, default=float(os.getenv('API_SLEEP_SECONDS', '0.8')))
    args = parser.parse_args()

    api_key = os.getenv('API_KEY')
    if not api_key:
        raise RuntimeError('Missing API_KEY environment variable.')

    scan_start = date.fromisoformat(args.date)
    scan_end = date.fromordinal(scan_start.toordinal() + max(0, args.duration - 1))
    levels_to_audit = {tle.clean(x).lower() for x in args.levels.split(',') if tle.clean(x)}

    metadata = {}
    try:
        metadata_payload = tle.load_json(args.tournament_metadata)
        raw_meta = metadata_payload.get('tournaments') if isinstance(metadata_payload, dict) else None
        if isinstance(raw_meta, dict):
            metadata = {tle.clean(k): v for k, v in raw_meta.items() if isinstance(v, dict)}
    except Exception:
        metadata = {}

    api_mapping = tle.load_api_player_mapping(args.api_player_mapping)
    exact_index, surname_initial_index, display = tle.build_alias_indexes(args.canonical_manifest)

    counters = Counter()
    method_counts = Counter()
    event_rows: list[dict[str, Any]] = []
    player_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []

    current = scan_start
    while current <= scan_end:
        date_text = current.isoformat()
        fixtures_payload = tle.api_get(api_key, {'method': 'get_fixtures', 'date_start': date_text, 'date_stop': date_text}, sleep_seconds=args.sleep)
        odds_payload = tle.api_get(api_key, {'method': 'get_odds', 'date_start': date_text, 'date_stop': date_text}, sleep_seconds=args.sleep)

        fixtures = tle.fixture_index(fixtures_payload)
        odds_by_event = tle.odds_index(odds_payload)
        counters['api_fixture_events'] += len(fixtures)
        counters['api_odds_events'] += len(odds_by_event)

        for event_key, markets in odds_by_event.items():
            fixture = fixtures.get(event_key)
            if not fixture:
                counters['skipped_missing_fixture'] += 1
                continue
            counters['odds_events_with_fixture'] += 1

            if not tle.is_singles(fixture):
                counters['skipped_not_singles'] += 1
                continue

            status = tle.clean(fixture.get('event_status')).lower()
            if status in {'finished', 'cancelled', 'canceled', 'postponed', 'retired', 'walkover'}:
                counters[f'skipped_status_{status or "missing"}'] += 1
                continue

            mins = tle.minutes_until_start(fixture, args.timezone)
            if mins is not None and mins < args.min_start_minutes:
                counters['skipped_starts_too_soon'] += 1
                continue

            gender = tle.infer_gender(fixture)
            level = tle.infer_level(fixture, metadata)
            surface = tle.infer_surface(fixture, metadata)

            if level not in levels_to_audit:
                counters[f'skipped_level_{level}'] += 1
                continue

            market = tle.get_home_away_market(markets)
            if not market:
                counters['skipped_missing_home_away_market'] += 1
                continue

            home_odds, away_odds, odds_source, odds_details = tle.choose_pair_odds(
                market,
                args.bookmaker,
                args.fallback,
                args.min_odds,
                args.max_odds,
                args.min_overround,
                args.max_overround,
                args.max_book_deviation,
            )
            book_pairs_valid = int((odds_details or {}).get('book_pairs_valid') or 0)

            home_name = tle.clean(fixture.get('event_first_player') or fixture.get('first_player'))
            away_name = tle.clean(fixture.get('event_second_player') or fixture.get('second_player'))
            home_api_key = tle.safe_int(fixture.get('first_player_key'))
            away_api_key = tle.safe_int(fixture.get('second_player_key'))

            home_key, home_method = tle.resolve_player(home_api_key, home_name, gender, api_mapping, exact_index, surname_initial_index)
            away_key, away_method = tle.resolve_player(away_api_key, away_name, gender, api_mapping, exact_index, surname_initial_index)

            method_counts[home_method] += 1
            method_counts[away_method] += 1
            counters['audited_player_appearances'] += 2
            counters['audited_events'] += 1

            home_safe = home_method in SAFE_METHODS
            away_safe = away_method in SAFE_METHODS
            counters['safe_player_appearances'] += int(home_safe) + int(away_safe)
            counters['review_player_appearances'] += int(not home_safe) + int(not away_safe)

            if home_safe and away_safe:
                mapping_status = 'safe_both_players'
                counters['safe_events_both_players'] += 1
            else:
                mapping_status = 'review_any_player'
                counters['review_events_any_player'] += 1

            event_row = {
                'event_key': event_key,
                'date': tle.clean(fixture.get('event_date')),
                'time': tle.clean(fixture.get('event_time')),
                'minutes_until_start': round(float(mins), 2) if mins is not None else None,
                'tournament': tle.clean(fixture.get('tournament_name')),
                'tournament_key': tle.clean(fixture.get('tournament_key')),
                'round': tle.clean(fixture.get('tournament_round')),
                'event_type': tle.clean(fixture.get('event_type_type')),
                'gender': gender,
                'tour_level': level,
                'surface': surface,
                'match': f'{home_name} - {away_name}',
                'home_api_key': home_api_key,
                'away_api_key': away_api_key,
                'home_name': home_name,
                'away_name': away_name,
                'home_tle_key': home_key or '',
                'away_tle_key': away_key or '',
                'home_tle_display_name': display_for_key(home_key, display),
                'away_tle_display_name': display_for_key(away_key, display),
                'home_resolve_method': home_method,
                'away_resolve_method': away_method,
                'mapping_status': mapping_status,
                'odds_source': odds_source or '',
                'book_pairs_valid': book_pairs_valid,
                'odds_details': odds_details,
            }
            event_rows.append(event_row)

            rows = [
                player_audit_row(
                    fixture=fixture,
                    event_key=event_key,
                    side='Home',
                    api_key=home_api_key,
                    api_name=home_name,
                    gender=gender,
                    level=level,
                    method=home_method,
                    tle_key=home_key,
                    tle_display=display_for_key(home_key, display),
                ),
                player_audit_row(
                    fixture=fixture,
                    event_key=event_key,
                    side='Away',
                    api_key=away_api_key,
                    api_name=away_name,
                    gender=gender,
                    level=level,
                    method=away_method,
                    tle_key=away_key,
                    tle_display=display_for_key(away_key, display),
                ),
            ]
            player_rows.extend(rows)
            review_rows.extend([r for r in rows if r['resolve_method'] not in SAFE_METHODS])

        current = date.fromordinal(current.toordinal() + 1)

    event_rows.sort(key=lambda r: (r.get('mapping_status') != 'review_any_player', r.get('date') or '', r.get('time') or '', r.get('match') or ''))
    review_rows.sort(key=lambda r: (r.get('resolve_method') or '', r.get('api_name') or ''))

    summary = {
        'generated_at': tle.now_iso(),
        'scan_date_start': scan_start.isoformat(),
        'scan_date_end': scan_end.isoformat(),
        'settings': {
            'levels': sorted(levels_to_audit),
            'min_start_minutes': args.min_start_minutes,
            'safe_methods': sorted(SAFE_METHODS),
            'bookmaker': args.bookmaker,
            'fallback': args.fallback,
            'min_odds': args.min_odds,
            'max_odds': args.max_odds,
            'min_overround': args.min_overround,
            'max_overround': args.max_overround,
        },
        'counters': dict(sorted(counters.items())),
        'resolve_method_counts': dict(sorted(method_counts.items())),
        'review_players_count': len(review_rows),
        'event_rows_count': len(event_rows),
    }

    payload = {
        'schema_version': 1,
        'file_type': 'ai_tle_mapping_audit',
        'summary': summary,
        'review_players': review_rows,
        'events': event_rows,
        'players': player_rows,
    }

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT_DIR / out_dir

    if args.duration == 1:
        stem = f'ai_tle_mapping_audit_{scan_start.isoformat()}'
    else:
        stem = f'ai_tle_mapping_audit_{scan_start.isoformat()}_{scan_end.isoformat()}'

    dated_json = out_dir / f'{stem}.json'
    latest_json = out_dir / 'ai_tle_mapping_audit_latest.json'
    latest_md = out_dir / 'ai_tle_mapping_audit_latest.md'

    save_json(dated_json, payload)
    save_json(latest_json, payload)
    write_md(latest_md, summary, review_rows, event_rows)

    print('AI TLE MAPPING AUDIT DONE')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f'JSON: {dated_json}')
    print(f'Latest JSON: {latest_json}')
    print(f'MD: {latest_md}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Read-only verification of the committed Homeopathy release on GitHub Pages.

This checks live status/index, HTML bootstrap assets (CSS, preload, icon),
and approved Materia JS bytes. It cannot prove browser route or audio usability.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def check(release: Path, base: str, timeout: int) -> tuple[int, int]:
    manifest = json.loads((release / '.publication-manifest.json').read_text(encoding='utf-8'))
    expected_status = json.loads((release / 'status.json').read_text(encoding='utf-8'))
    positions = (manifest.get('quality_gate') or {}).get('materia_positions') or []
    if not positions or len(positions) != len(set(positions)) or not all(type(p) is int and 39 <= p <= 117 for p in positions):
        raise ValueError('invalid-approved-materia-positions')
    if (expected_status.get('materia_publishable') or {}).get('positions') != positions:
        raise ValueError('committed-status-position-mismatch')
    if manifest.get('source_commit') != expected_status.get('source_commit'):
        raise ValueError('committed-source-identity-mismatch')
    approved = {item['path']: item['sha256'] for item in manifest.get('approved_files', [])}
    if len(approved) != len(manifest.get('approved_files', [])):
        raise ValueError('duplicate-approved-path')
    for path in approved:
        if path.startswith('/') or '..' in Path(path).parts or '\\' in path:
            raise ValueError('unsafe-approved-path')
    index = (release / 'index.html').read_text(encoding='utf-8')
    entry = re.search(r'<script[^>]+type="module"[^>]+src="([^"]+)"', index)
    if not entry:
        raise ValueError('entry-module-missing')
    entry_path = urlparse(entry.group(1)).path
    prefix = urlparse(base).path.rstrip('/') + '/'
    if not entry_path.startswith(prefix):
        raise ValueError('entry-module-outside-reader')
    entry_path = entry_path[len(prefix):]
    # The entry alone is insufficient: missing CSS or modulepreload chunks can
    # leave every lecture broken even when its individual JS asset is served.
    html_refs = re.findall(r'<(?:script|link)\b[^>]*\b(?:src|href)="([^"]+)"', index, re.I)
    if not html_refs:
        raise ValueError('html-asset-references-missing')
    html_paths = []
    for ref in html_refs:
        parsed = urlparse(ref)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not parsed.path.startswith(prefix):
            raise ValueError('html-asset-outside-reader')
        html_paths.append(parsed.path[len(prefix):])
    if entry_path not in html_paths:
        raise ValueError('entry-module-not-in-html-assets')
    # Current approved Reader build emits three JS chunks per Materia lecture.
    # A single matching chunk must never make an incomplete lecture look deployed.
    lecture_assets = []
    for position in positions:
        matched = sorted(path for path in approved
                         if path.startswith(f'assets/{position:03d}-') and path.endswith('.js'))
        if len(matched) != 3:
            raise ValueError(f'approved-materia-asset-count:{position:03d}={len(matched)}')
        lecture_assets.extend(matched)
    paths = list(dict.fromkeys(['status.json', 'index.html', *html_paths, *lecture_assets]))
    if any(path not in approved for path in paths):
        raise ValueError('unapproved-reader-asset')

    for path in paths:
        url = base.rstrip('/') + '/' + quote(path, safe='/') + '?verify=' + str(int(time.time()))
        request = Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'master-ek-live-release-verifier/1'})
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ValueError('live-asset-http-not-200')
            actual = hashlib.sha256(response.read()).hexdigest()
        if actual != approved[path]:
            raise ValueError('live-asset-hash-mismatch:' + path)
    return len(positions), len(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', type=Path, default=Path('release'))
    parser.add_argument('--base', default='https://masterekteachings.github.io/homeopathy/')
    parser.add_argument('--attempts', type=int, default=12)
    parser.add_argument('--delay', type=int, default=15)
    parser.add_argument('--timeout', type=int, default=15)
    args = parser.parse_args()
    if args.attempts < 1 or args.attempts > 30 or args.delay < 0 or args.timeout < 1:
        parser.error('invalid bounded verification parameters')
    for attempt in range(1, args.attempts + 1):
        try:
            positions, files = check(args.release, args.base, args.timeout)
            print(f'LIVE_RELEASE_ASSETS_VERIFIED materia={positions} files={files} (browser route rendering not checked)')
            return 0
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            reason = str(exc)[:120] if isinstance(exc, ValueError) else type(exc).__name__
            print(f'live release not yet verified attempt={attempt}/{args.attempts} reason={reason}', file=sys.stderr)
            if attempt < args.attempts:
                time.sleep(args.delay)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())

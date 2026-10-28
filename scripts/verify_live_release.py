#!/usr/bin/env python3
"""Read-only verification of the committed Homeopathy release on GitHub Pages.

This checks live status/index bytes and every approved Materia JS asset. It cannot
prove that a browser successfully renders each hash route or that audio works.
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
    lecture_assets = sorted(path for path in approved if any(path.startswith(f'assets/{p:03d}-') for p in positions))
    if any(not any(path.startswith(f'assets/{p:03d}-') for path in lecture_assets) for p in positions):
        raise ValueError('approved-materia-asset-missing')
    paths = list(dict.fromkeys(['status.json', 'index.html', entry_path, *lecture_assets]))
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

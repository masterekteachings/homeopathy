"""Deterministic offline regression tests for the existing Pages release verifier.

No network, GitHub Actions, browser, credentials, or public deployment required.
"""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlparse


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'verify_live_release.py'
spec = importlib.util.spec_from_file_location('verify_live_release', SCRIPT)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
BASE = 'https://reader.example/homeopathy/'


class FakeResponse:
    status = 200

    def __init__(self, content, url):
        self.content = content
        self.url = url

    def geturl(self):
        return self.url

    def read(self):
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class VerifyLiveReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.release = Path(self.temp.name)
        self.files = {
            'status.json': json.dumps({'source_commit': 'trusted', 'materia_publishable': {'count': 1, 'positions': [39]}}).encode(),
            'index.html': (b'<html><link rel="stylesheet" href="/homeopathy/assets/site.css">'
                           b'<link rel="modulepreload" href="/homeopathy/assets/preload.js">'
                           b'<script type="module" src="/homeopathy/assets/main.js"></script></html>'),
            'assets/site.css': b'body { color: black; }',
            'assets/preload.js': b'export const ready = true;',
            'assets/main.js': b'import "./preload.js";',
            'assets/039-notes.js': b'export const notes = true;',
            'assets/039-synopsis.js': b'export const synopsis = true;',
            'assets/039-content.js': b'export const content = true;',
        }
        for name, content in self.files.items():
            path = self.release / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.write_manifest()

    def write_manifest(self, positions=None):
        self.manifest = {
            'source_commit': 'trusted',
            'quality_gate': {'materia_positions': [39] if positions is None else positions},
            'approved_files': [{'path': path, 'sha256': hashlib.sha256(content).hexdigest()}
                               for path, content in self.files.items()],
        }
        (self.release / '.publication-manifest.json').write_text(json.dumps(self.manifest))

    def check(self, served=None):
        served = self.files if served is None else served

        def get(request, timeout):
            path = unquote(urlparse(request.full_url).path.removeprefix('/homeopathy/'))
            if path not in served:
                raise OSError('asset missing')
            return FakeResponse(served[path], request.full_url)

        with patch.object(verifier, 'urlopen', side_effect=get):
            return verifier.check(self.release, BASE, timeout=1)

    def test_matching_release_verifies_all_eight_assets(self):
        self.assertEqual(self.check(), (1, 8))

    def test_corrupted_live_stylesheet_fails_closed(self):
        served = dict(self.files, **{'assets/site.css': b'corrupt'})
        with self.assertRaisesRegex(ValueError, 'live-asset-hash-mismatch:assets/site.css'):
            self.check(served)

    def test_off_origin_redirect_fails_even_with_matching_bytes(self):
        # urllib follows redirects, so an identical off-site copy must not
        # satisfy the directly-served Reader release acceptance check.
        with patch.object(verifier, 'urlopen', return_value=FakeResponse(
            self.files['status.json'], 'https://elsewhere.example/homeopathy/status.json'
        )):
            with self.assertRaisesRegex(ValueError, 'live-asset-redirected:status.json'):
                verifier.check(self.release, BASE, timeout=1)

    def test_missing_live_preload_fails_closed(self):
        served = dict(self.files)
        del served['assets/preload.js']
        with self.assertRaises(OSError):
            self.check(served)

    def test_committed_position_drift_fails_before_network(self):
        self.write_manifest(positions=[40])
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'committed-status-position-mismatch'):
                verifier.check(self.release, BASE, timeout=1)

    def test_committed_count_drift_fails_before_network(self):
        status = json.loads(self.files['status.json'])
        status['materia_publishable']['count'] = 2
        self.files['status.json'] = json.dumps(status).encode()
        (self.release / 'status.json').write_bytes(self.files['status.json'])
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'committed-status-count-mismatch'):
                verifier.check(self.release, BASE, timeout=1)

    def test_off_origin_html_asset_fails_before_network(self):
        self.files['index.html'] = self.files['index.html'].replace(
            b'/homeopathy/assets/site.css', b'https://evil.example/site.css')
        (self.release / 'index.html').write_bytes(self.files['index.html'])
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'html-asset-outside-reader'):
                verifier.check(self.release, BASE, timeout=1)

    def test_missing_approved_materia_assets_fails_before_network(self):
        self.files = {path: data for path, data in self.files.items() if not path.startswith('assets/039-')}
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'approved-materia-asset-count:039=0'):
                verifier.check(self.release, BASE, timeout=1)


    def test_partial_approved_materia_assets_fails_before_network(self):
        # Previous verifier accepted one chunk as sufficient for an entire lecture.
        self.files = {path: data for path, data in self.files.items()
                      if path != 'assets/039-synopsis.js'}
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'approved-materia-asset-count:039=2'):
                verifier.check(self.release, BASE, timeout=1)

    def test_extra_approved_materia_chunk_fails_before_network(self):
        self.files['assets/039-unexpected.js'] = b'unexpected chunk'
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'approved-materia-asset-count:039=4'):
                verifier.check(self.release, BASE, timeout=1)

    def test_non_js_placeholder_does_not_count_as_materia_chunk(self):
        self.files = {path: data for path, data in self.files.items()
                      if not path.startswith('assets/039-')}
        self.files['assets/039-placeholder.txt'] = b'not a lecture module'
        self.write_manifest()
        with patch.object(verifier, 'urlopen', side_effect=AssertionError('network must not be used')):
            with self.assertRaisesRegex(ValueError, 'approved-materia-asset-count:039=0'):
                verifier.check(self.release, BASE, timeout=1)


if __name__ == '__main__':
    unittest.main()

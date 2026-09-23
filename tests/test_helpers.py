import contextlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_repos as vr
import build_dashboard as bd


class DOM(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements, self.words = [], []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
    def handle_data(self, data):
        self.words.append(data)


class Helpers(unittest.TestCase):
    def row(self):
        return {'input': 'owner/old', 'repo': 'owner/new', 'verified': True, 'stars': 3,
                'freshness': 'active', 'html_url': 'javascript:alert(1)', 'license': None,
                'license_note': 'present but unrecognised — read it', 'checked_at': '2026-09-23'}

    def test_slug_rejects_unrelated_urls_and_partial_matches(self):
        for bad in ('https://evil.test/owner/repo', 'prefix owner/repo', '/owner/repo', 'owner/..'):
            self.assertIsNone(vr.slug(bad))
        for good in ('owner/repo', 'https://github.com/owner/repo.git', 'git@github.com:owner/repo.git'):
            self.assertEqual(vr.slug(good), 'owner/repo')

    def test_strict_returns_failure_but_preserves_json(self):
        with patch.object(vr, 'verify', return_value={'input': 'x/y', 'verified': False}):
            for flags, expected in (([], 0), (['--strict'], 1)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(vr.main(['verify', *flags, 'x/y']), expected)
                self.assertFalse(json.loads(out.getvalue())[0]['verified'])

    def test_empty_input_file_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'repos'
            p.write_text('# nothing\n')
            with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(io.StringIO()):
                vr.main(['verify', '--strict', '--file', str(p)])
            self.assertEqual(e.exception.code, 2)

    def test_malformed_api_payload_never_verified(self):
        for payload in ([], {}, {'full_name': 'x/y'}, {'message': 'error'}):
            with patch.object(vr, '_via_gh', return_value=payload), patch.object(vr, '_via_http', return_value=(payload, '')):
                self.assertFalse(vr.verify('x/y')['verified'])

    def test_realistic_metadata_and_unrecognized_license(self):
        payload = {'full_name': 'owner/new', 'stargazers_count': 2, 'forks_count': 1,
                   'open_issues_count': 0, 'archived': False, 'license': {'spdx_id': 'NOASSERTION'}}
        with patch.object(vr, '_via_gh', return_value=payload):
            row = vr.verify('owner/old')
        self.assertTrue(row['verified'])
        self.assertIsNone(row['license'])
        self.assertEqual(row['html_url'], 'https://github.com/owner/new')
        self.assertIn('unrecognised', row['license_note'])

    def test_html_preserves_license_and_ignores_executable_urls(self):
        row = self.row()
        row['freshness'] = 'active" onclick="alert(1)'
        row['description'] = '<img src=x onerror=alert(1)>'
        rendered = bd.candidate_html(1, {'repo': 'owner/old', 'why': '<script>bad</script>'}, bd.index([row]))
        dom = DOM(rendered)
        links = [a['href'] for t, a in dom.elements if t == 'a']
        self.assertEqual(links, ['https://github.com/owner/new'])
        self.assertFalse(any(t in ('img', 'script') or 'onclick' in a for t, a in dom.elements))
        self.assertIn('present but unrecognised', ''.join(dom.words))

    def test_alias_full_url_resolves(self):
        repos = bd.index([self.row()])
        dom = DOM(bd.candidate_html(1, {'repo': 'https://github.com/owner/old'}, repos))
        self.assertTrue(any(t == 'a' for t, a in dom.elements))

    def test_unverified_consult_label_and_mixed_dates(self):
        self.assertIn('unverified', ''.join(DOM(bd.consult_html({'repo': 'x/y'}, {})).words))
        row = self.row()
        other = dict(row, repo='owner/second', input='owner/second', checked_at='2026-09-22')
        page = bd.build({'components': []}, [row, other])
        words = ''.join(DOM(page).words)
        self.assertIn('2026-09-22', words)
        self.assertIn('2026-09-23', words)

    def test_invalid_count_is_unverified_not_crash(self):
        row = dict(self.row(), stars=None)
        self.assertEqual(bd.index([row]), {})


if __name__ == '__main__':
    unittest.main()

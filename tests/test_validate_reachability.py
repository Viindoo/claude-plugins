import io, json, os, sys, tempfile
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from validate_reachability import check


def _write(tmp_path, data):
    p = tmp_path / 'marketplace.json'
    p.write_text(json.dumps(data))
    return str(p)


def _marketplace(ref='master'):
    return {
        'name': 'test',
        'plugins': [
            {
                'name': 'my-plugin',
                'source': {
                    'source': 'git-subdir',
                    'url': 'https://github.com/Viindoo/my-repo.git',
                    'path': 'dist/my-plugin',
                    'ref': ref,
                },
            }
        ],
    }


def _mock_resp(status=200):
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_ok_on_200(tmp_path, capsys):
    with patch('urllib.request.urlopen', return_value=_mock_resp(200)):
        errors = check(_write(tmp_path, _marketplace()))
    assert errors == []
    assert 'OK: my-plugin' in capsys.readouterr().out


def test_error_on_403(tmp_path):
    import urllib.error
    http_403 = urllib.error.HTTPError(url='', code=403, msg='Forbidden', hdrs={}, fp=None)
    with patch('urllib.request.urlopen', side_effect=http_403):
        errors = check(_write(tmp_path, _marketplace()))
    assert any('403' in e for e in errors)


def test_ref_not_found_when_both_404(tmp_path):
    import urllib.error
    http_404 = urllib.error.HTTPError(url='', code=404, msg='Not Found', hdrs={}, fp=None)
    with patch('urllib.request.urlopen', side_effect=http_404):
        errors = check(_write(tmp_path, _marketplace()))
    assert any('not found' in e for e in errors)


def test_non_github_url(tmp_path):
    d = _marketplace()
    d['plugins'][0]['source']['url'] = 'https://gitlab.com/some/repo.git'
    errors = check(_write(tmp_path, d))
    assert any('not supported' in e for e in errors)


def test_non_git_subdir_skipped(tmp_path):
    d = {'name': 'test', 'plugins': [{'name': 'p', 'source': 'local'}]}
    with patch('urllib.request.urlopen') as mock_open:
        errors = check(_write(tmp_path, d))
    mock_open.assert_not_called()
    assert errors == []


def test_gh_token_injected_as_auth_header(tmp_path):
    captured_req = {}

    def fake_urlopen(req, timeout=None):
        captured_req['headers'] = req.headers
        return _mock_resp(200)

    with patch.dict(os.environ, {'GH_TOKEN': 'test-token-xyz'}):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen):
            check(_write(tmp_path, _marketplace()))

    assert captured_req['headers'].get('Authorization') == 'Bearer test-token-xyz'


def test_no_token_omits_auth_header(tmp_path):
    captured_req = {}

    def fake_urlopen(req, timeout=None):
        captured_req['headers'] = req.headers
        return _mock_resp(200)

    env = {k: v for k, v in os.environ.items() if k != 'GH_TOKEN'}
    with patch.dict(os.environ, env, clear=True):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen):
            check(_write(tmp_path, _marketplace()))

    assert 'Authorization' not in captured_req['headers']

import json, os, sys, tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from validate_schema import validate


def _write(tmp_path, data):
    p = tmp_path / 'marketplace.json'
    p.write_text(json.dumps(data))
    return str(p)


def _valid():
    return {
        'name': 'test-marketplace',
        'plugins': [
            {
                'name': 'my-plugin',
                'source': {
                    'source': 'git-subdir',
                    'url': 'https://github.com/Viindoo/my-repo.git',
                    'path': 'dist/my-plugin',
                },
                'description': 'A test plugin',
            }
        ],
    }


def test_valid_passes(tmp_path):
    assert validate(_write(tmp_path, _valid())) == []


def test_missing_top_level_name(tmp_path):
    d = _valid()
    del d['name']
    errors = validate(_write(tmp_path, d))
    assert any('name' in e for e in errors)


def test_missing_plugins(tmp_path):
    d = _valid()
    del d['plugins']
    errors = validate(_write(tmp_path, d))
    assert any('plugins' in e for e in errors)


def test_plugin_missing_name(tmp_path):
    d = _valid()
    del d['plugins'][0]['name']
    errors = validate(_write(tmp_path, d))
    assert any('missing name' in e for e in errors)


def test_plugin_missing_source(tmp_path):
    d = _valid()
    del d['plugins'][0]['source']
    errors = validate(_write(tmp_path, d))
    assert any('missing source' in e for e in errors)


def test_git_subdir_missing_url(tmp_path):
    d = _valid()
    del d['plugins'][0]['source']['url']
    errors = validate(_write(tmp_path, d))
    assert any('missing url' in e for e in errors)


def test_git_subdir_missing_path(tmp_path):
    d = _valid()
    del d['plugins'][0]['source']['path']
    errors = validate(_write(tmp_path, d))
    assert any('missing path' in e for e in errors)


def test_non_git_subdir_source_skips_url_check(tmp_path):
    d = _valid()
    d['plugins'][0]['source'] = 'local'
    errors = validate(_write(tmp_path, d))
    assert errors == []


def test_sha_field_optional(tmp_path):
    d = _valid()
    d['plugins'][0]['source']['sha'] = 'abc1234'
    assert validate(_write(tmp_path, d)) == []

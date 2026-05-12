#!/usr/bin/env python3
import json, sys


def validate(path):
    with open(path) as f:
        m = json.load(f)
    errors = []
    if 'name' not in m:
        errors.append('missing top-level name')
    if 'plugins' not in m:
        errors.append('missing top-level plugins')
        return errors
    for p in m['plugins']:
        if 'name' not in p:
            errors.append(f'plugin missing name: {p}')
            continue
        if 'source' not in p:
            errors.append(f'plugin missing source: {p["name"]}')
            continue
        src = p['source']
        if isinstance(src, dict) and src.get('source') == 'git-subdir':
            if 'url' not in src:
                errors.append(f'git-subdir missing url: {p["name"]}')
            if 'path' not in src:
                errors.append(f'git-subdir missing path: {p["name"]}')
    return errors


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <marketplace.json>', file=sys.stderr)
        sys.exit(1)
    errors = validate(sys.argv[1])
    if errors:
        print('ERRORS:', file=sys.stderr)
        for e in errors:
            print(f'  {e}', file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        m = json.load(f)
    print(f'OK: {len(m["plugins"])} plugin(s) validated')

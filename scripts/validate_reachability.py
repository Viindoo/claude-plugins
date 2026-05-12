#!/usr/bin/env python3
import json, os, re, sys, urllib.error, urllib.request


def check(path):
    with open(path) as f:
        m = json.load(f)
    token = os.environ.get('GH_TOKEN', '')
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    errors = []
    for p in m['plugins']:
        src = p['source']
        if not isinstance(src, dict) or src.get('source') != 'git-subdir':
            continue
        url = src['url']
        ref = src.get('ref', 'main')
        name = p['name']
        match = re.match(r'https://github\.com/([^/]+)/([^/.]+)', url)
        if not match:
            errors.append(f'{name}: non-GitHub URL not supported yet: {url}')
            continue
        owner, repo = match.group(1), match.group(2)
        checked = False
        for kind, api_path in [('branch', f'heads/{ref}'), ('tag', f'tags/{ref}')]:
            api_url = f'https://api.github.com/repos/{owner}/{repo}/git/ref/{api_path}'
            req = urllib.request.Request(api_url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 200:
                        print(f'OK: {name} -> {owner}/{repo} ({kind}: {ref})')
                        checked = True
                        break
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    errors.append(f'{name}: API error {e.code} for {kind} {ref}')
                    checked = True
                    break
            except Exception as e:
                errors.append(f'{name}: request failed: {e}')
                checked = True
                break
        if not checked:
            errors.append(f'{name}: ref {ref!r} not found as branch or tag in {owner}/{repo}')
    return errors


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <marketplace.json>', file=sys.stderr)
        sys.exit(1)
    errors = check(sys.argv[1])
    if errors:
        print('ERRORS:', file=sys.stderr)
        for e in errors:
            print(f'  {e}', file=sys.stderr)
        sys.exit(1)

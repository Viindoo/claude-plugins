# Contributing to Viindoo Claude Plugins

## Adding a new plugin

Each Viindoo project hosts its own plugin source. To register it here:

### 1. Prepare your plugin source

In your project repo, create `dist/<plugin-name>/` with:

```
dist/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json      # name, userConfig, mcpServers, skills, agents, commands (no version field — see below)
├── .mcp.json             # MCP server config using ${user_config.*} refs
├── skills/               # SKILL.md files
├── agents/               # agent .md files (optional)
├── commands/             # slash command .md files (optional)
└── README.md
```

Follow the [Claude Code plugin spec](https://code.claude.com/docs/en/plugins-reference).

For HTTP MCP servers requiring authentication, use `userConfig` with `"sensitive": true` — **never hardcode API keys**.

**Do not set `version` in `plugin.json`.** Claude Code uses the pinned SHA as the version identifier. Every time the SHA in `marketplace.json` is updated, users automatically receive the new content. If you set an explicit version string, you would need to bump it manually on every change — the auto-pin workflow would not be enough.

### 2. Open a PR here

Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/Viindoo/<your-repo>.git",
    "path": "dist/<plugin-name>",
    "ref": "master",
    "sha": "<exact-commit-sha-after-your-pr-merges>"
  },
  "description": "One-line description (max 120 chars)"
}
```

Pin `sha` to the exact commit where your plugin landed. This is the anti-drift anchor — the nightly CI checks this SHA is still reachable.

### 3. Set up auto-pinning in your plugin repo

After registering the plugin, wire up the auto-pin workflow so that every merge to `master` that touches `dist/<plugin-name>/` automatically opens a SHA-update PR here.

**Required setup (one-time per plugin repo):**

1. **Create a fine-grained PAT** targeting `Viindoo/claude-plugins` with permissions:
   - `Contents: Read and write`
   - `Pull requests: Read and write`

2. **Add the PAT as a secret** in your plugin repo:
   `Settings → Secrets → Actions → New repository secret`
   Name: `CLAUDE_PLUGINS_PAT`

3. **Create the `auto-pin` label** in `Viindoo/claude-plugins`:
   ```bash
   gh label create auto-pin --repo Viindoo/claude-plugins --color 0075ca --description "Automated SHA pin update"
   ```

4. **Add the workflow** `.github/workflows/pin-sha.yml` to your plugin repo (see template below).

**Template `pin-sha.yml`** (replace `<plugin-name>` and `<plugin-dir>`):

```yaml
name: Pin SHA in claude-plugins

on:
  push:
    branches: [master]
    paths:
      - 'dist/<plugin-dir>/**'

jobs:
  pin-sha:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get SHA
        id: info
        run: echo "sha=$(git rev-parse HEAD)" >> $GITHUB_OUTPUT

      - uses: actions/checkout@v4
        with:
          repository: Viindoo/claude-plugins
          token: ${{ secrets.CLAUDE_PLUGINS_PAT }}
          path: claude-plugins

      - name: Check if already pinned
        id: check
        run: |
          CURRENT=$(python3 -c "
          import json
          m = json.load(open('claude-plugins/.claude-plugin/marketplace.json'))
          for p in m['plugins']:
              if p['name'] == '<plugin-name>':
                  print(p['source'].get('sha', ''))
          ")
          [ "$CURRENT" = "${{ steps.info.outputs.sha }}" ] && echo "skip=true" >> $GITHUB_OUTPUT || echo "skip=false" >> $GITHUB_OUTPUT

      - name: Update marketplace.json
        if: steps.check.outputs.skip == 'false'
        run: |
          python3 -c "
          import json
          path = 'claude-plugins/.claude-plugin/marketplace.json'
          with open(path) as f: m = json.load(f)
          for p in m['plugins']:
              if p['name'] == '<plugin-name>':
                  p['source']['sha'] = '${{ steps.info.outputs.sha }}'
          with open(path, 'w') as f: json.dump(m, f, indent=2); f.write('\n')
          "

      - name: Create PR with auto-merge
        if: steps.check.outputs.skip == 'false'
        working-directory: claude-plugins
        env:
          GH_TOKEN: ${{ secrets.CLAUDE_PLUGINS_PAT }}
        run: |
          SHA="${{ steps.info.outputs.sha }}"
          SHA7="${SHA:0:7}"
          BRANCH="auto-pin/<plugin-name>-${SHA7}"
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git checkout -b "$BRANCH"
          git add .claude-plugin/marketplace.json
          git commit -m "pin <plugin-name> to ${SHA7}"
          git push origin "$BRANCH"
          PR_URL=$(gh pr create \
            --repo Viindoo/claude-plugins \
            --title "pin <plugin-name> to ${SHA7}" \
            --body "Auto-pin: plugin content changed in [${SHA7}](https://github.com/Viindoo/<your-repo>/commit/${SHA})." \
            --label "auto-pin")
          gh pr merge --auto --squash "$PR_URL"
```

**Enable auto-merge in `Viindoo/claude-plugins`** (one-time repo setting):
`Settings → General → Pull Requests → Allow auto-merge` ✓

**Enable branch protection on `master`** (required for auto-merge to work):
`Settings → Branches → Add rule → master → Require status checks → validate`

### 4. After the first PR merges

Subsequent plugin updates are fully automatic — the `pin-sha.yml` workflow handles everything. No manual SHA updates needed.

## Anti-drift CI

`.github/workflows/validate.yml` runs nightly and on every change to `marketplace.json`:
- Validates JSON schema (`scripts/validate_schema.py`)
- Checks each `git-subdir` source URL + ref is still reachable via GitHub API (`scripts/validate_reachability.py`)

If CI fails: the plugin source has moved or been deleted. Update `marketplace.json` to the new location.

## Questions

Open an issue or ping the Viindoo team.

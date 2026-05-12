# Contributing to Viindoo Claude Plugins

## Adding a new plugin

Each Viindoo project hosts its own plugin source. To register it here:

### 1. Prepare your plugin source

In your project repo, create `dist/<plugin-name>/` with:

```
dist/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json      # name, version, userConfig, mcpServers, skills, agents, commands
├── .mcp.json             # MCP server config using ${user_config.*} refs
├── skills/               # SKILL.md files
├── agents/               # agent .md files (optional)
├── commands/             # slash command .md files (optional)
└── README.md
```

Follow the [Claude Code plugin spec](https://code.claude.com/docs/en/plugins-reference).

For HTTP MCP servers requiring authentication, use `userConfig` with `"sensitive": true` — **never hardcode API keys**.

### 2. Open a PR here

Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/Viindoo/<your-repo>.git",
    "path": "dist/<plugin-name>",
    "ref": "main",
    "sha": "<exact-commit-sha-after-your-pr-merges>"
  },
  "description": "One-line description (max 120 chars)"
}
```

Pin `sha` to the exact commit where your plugin landed on `main`. This is the anti-drift anchor — the nightly CI checks this SHA is still reachable.

### 3. After your PR merges

Bump the `sha` here whenever you ship a new plugin version. Open a follow-up PR with the new SHA + updated `ref` if needed.

## Anti-drift CI

`.github/workflows/validate.yml` runs nightly and on every change to `marketplace.json`:
- Validates JSON schema
- Checks each `git-subdir` source URL + ref is still reachable via `git ls-remote`

If CI fails: the plugin source has moved or been deleted. Update `marketplace.json` to the new location.

## Questions

Open an issue or ping the Viindoo team.

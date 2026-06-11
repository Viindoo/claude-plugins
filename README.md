# Viindoo Claude Plugins

Official Claude Code plugin marketplace for Viindoo products.

## Install

```bash
# Add this marketplace (one-time)
claude plugin marketplace add Viindoo/claude-plugins

# Install the Odoo AI Agent Team (auto-installs the odoo-semantic-mcp dependency)
claude plugin install odoo-ai-agents@viindoo-plugins

# Then configure the MCP server connection (API key + URL)
/odoo-semantic-mcp:connect
```

Or in a Claude Code interactive session:
```
/plugin marketplace add Viindoo/claude-plugins
/plugin install odoo-ai-agents@viindoo-plugins
/odoo-semantic-mcp:connect
```

Want only the MCP server tools (no persona skills)? Install just the MCP plugin:
```bash
claude plugin install odoo-semantic-mcp@viindoo-plugins
/odoo-semantic-mcp:connect
```

> Restart Claude Code after `/odoo-semantic-mcp:connect` to load the MCP tools.

## Available Plugins

| Plugin | Description | Source |
|--------|-------------|--------|
| `odoo-ai-agents` | Odoo AI Agent Team — 40 skills + 7 agents + 9 workflow commands across engineering, sales, marketing, strategy. Auto-installs `odoo-semantic-mcp`. | [odoo-mcp-client](https://github.com/Viindoo/odoo-mcp-client) (`plugins/odoo-ai-agents`) |
| `odoo-semantic-mcp` | MCP server connection for Odoo Semantic — semantic code intelligence (inheritance chains, field impact, ORM validation) over HTTP. Configure via `/odoo-semantic-mcp:connect`. | [odoo-mcp-client](https://github.com/Viindoo/odoo-mcp-client) (`plugins/odoo-semantic-mcp`) |

## For Plugin Developers

Each Viindoo project hosts its own plugin source under `plugins/<plugin-name>/` (a repo may host several plugins, each in its own subdirectory). To add a new plugin to this marketplace:

1. Create `plugins/<your-plugin>/` in your project repo with `.claude-plugin/plugin.json`. A `version` field is optional — the pinned `sha` in `marketplace.json` is what drives content delivery, so updates land automatically on every merge regardless of the version string.
2. Open a PR here adding an entry to `.claude-plugin/marketplace.json` (use a `git-subdir` source with `path: plugins/<your-plugin>`).
3. Pin `sha` to the exact commit of your plugin source after it merges.
4. Set up `.github/workflows/pin-sha.yml` in your plugin repo — subsequent updates are then fully automatic.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full setup guide including the auto-pin workflow template.

See [Anti-drift CI](.github/workflows/validate.yml) — nightly validation checks each plugin source is still reachable and schema-valid.

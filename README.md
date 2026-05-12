# Viindoo Claude Plugins

Official Claude Code plugin marketplace for Viindoo products.

## Install

```bash
# Add this marketplace (one-time)
claude plugin marketplace add Viindoo/claude-plugins

# Install a plugin
claude plugin install odoo-semantic@viindoo-plugins
```

Or in Claude Code interactive session:
```
/plugin marketplace add Viindoo/claude-plugins
/plugin install odoo-semantic@viindoo-plugins
```

## Available Plugins

| Plugin | Description | Source |
|--------|-------------|--------|
| `odoo-semantic` | Odoo codebase intelligence — inheritance chains, field impact, upgrade planning | [odoo-semantic-mcp](https://github.com/Viindoo/odoo-semantic-mcp) |

## For Plugin Developers

Each Viindoo project hosts its own plugin source under `dist/<plugin-name>/`. To add a new plugin to this marketplace:

1. Create `dist/<your-plugin>/` in your project repo with `.claude-plugin/plugin.json` (no `version` field — SHA is used as the version identifier)
2. Open a PR here adding an entry to `.claude-plugin/marketplace.json`
3. Pin `sha` to the exact commit of your plugin source after it merges
4. Set up `.github/workflows/pin-sha.yml` in your plugin repo — subsequent updates are then fully automatic

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full setup guide including the auto-pin workflow template.

See [Anti-drift CI](.github/workflows/validate.yml) — nightly validation checks each plugin source is still reachable and schema-valid.

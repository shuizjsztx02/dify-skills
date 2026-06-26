# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Dify CLI** — 命令行工具 for [Dify](https://dify.ai)，支持多服务器配置，可在任意项目文件夹使用。

## Installation

One-time setup (works across all project folders):

```bash
git clone https://github.com/shuizjsztx02/dify-skills.git
cd dify-skills
pip install -e .
dify init   # Interactive setup for server credentials
```

## Commands

### Server Management

```bash
# Interactive configuration (add multiple servers)
dify init

# List configured servers
dify servers

# Set default server
dify servers --set-default work

# Remove a server
dify servers --remove test
```

### Deploy (local YAML → Dify)

```bash
# First time with full URL (auto-saves mapping)
dify deploy <yml_path> <dify_url> [--server <name>] [--version <version_name>]

# Subsequent uses with filename (auto-lookup mapping)
dify deploy <yml_path>
```

Or via Claude Code slash command: `/project:dify-deploy path/to/agent.yml https://dify.example.com/app/<UUID>/workflow`

### Export (Dify → local YAML)

```bash
# First time with full URL (auto-saves mapping)
dify export <dify_url> --output <output_path> [--server <name>] [--force] [--no-secret]

# Subsequent uses with filename (auto-lookup mapping)
dify export <filename>
```

Or via Claude Code slash command: `/project:dify-export https://dify.example.com/app/<UUID>/workflow --output path/to/output.yml`

### Mapping Management

```bash
dify list              # List all mappings
dify unbind <filename> # Delete a mapping
```

### Sync Web App Name

```bash
dify sync-name <dify_url_or_filename> [--server <name>]
```

Auto-syncs Web App name to match the application name. Also runs automatically after deploy.

## Architecture

Modular package structure under `src/dify_cli/`:

```
src/dify_cli/
├── __init__.py       # Package init
├── cli.py            # Main entry point
├── config.py         # Configuration management (~/.dify/config.json)
├── auth.py           # Authentication
├── utils.py          # Utility functions
├── mapping.py        # Mapping management (~/.dify/mapping.json)
└── commands/         # Subcommands
    ├── init_cmd.py
    ├── servers_cmd.py
    ├── deploy_cmd.py
    ├── export_cmd.py
    ├── list_cmd.py
    ├── unbind_cmd.py
    └── sync_name_cmd.py
```

**Global Configuration:**
- Config: `~/.dify/config.json` — server credentials (supports multiple servers)
- Mapping: `~/.dify/mapping.json` — filename → (server, app_id) mappings

**Multi-server support:**
- Config stores multiple servers with a default_server setting
- Each mapping entry includes the server name
- URL matching automatically identifies the correct server
- `--server` flag can override automatic selection

**Flow:**
1. `load_config()` reads from `~/.dify/config.json`
2. `login_with_server()` authenticates with selected server
3. **deploy** path: `import_yml()` → `publish()` → `sync_name()`
4. **export** path: `export_yml()` → write YAML to disk
5. **sync-name** path: `get_app_info()` → `update_site_name()` if needed

## Claude Code Commands

Available in `.claude/commands/`:
- `dify-init.md` — Interactive server configuration
- `dify-servers.md` — Manage server list
- `dify-deploy.md` — Deploy YAML to Dify
- `dify-export.md` — Export YAML from Dify
- `dify-list.md` — List all mappings
- `dify-unbind.md` — Delete a mapping
- `dify-sync-name.md` — Sync Web App name

## Conventions

- All console output is in Chinese (error messages, status lines, etc.)
- Windows UTF-8 stdout fix at script top
- Status prefixes: `[INFO]`, `[OK]`, `[ERROR]`
- Dify import API uses overwrite mode — replaces the entire target app config
- Export defaults to including secret env vars; `--no-secret` excludes them
- Export refuses to overwrite existing files unless `--force` is passed

## Extending

To add new commands:

1. Create `src/dify_cli/commands/new_cmd.py`
2. Implement the command function
3. Register in `src/dify_cli/cli.py`
4. Add Claude Code command in `.claude/commands/`

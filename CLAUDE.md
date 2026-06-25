# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code skill for deploying and exporting [Dify](https://dify.ai) workflows via YAML. Supports self-hosted Dify instances (v0.6+ DSL format, tested through v1.11+).

## Commands

### Deploy (local YAML → Dify)
```bash
# 首次使用完整 URL（自动保存映射）
python dify_deploy.py deploy <yml_path> <dify_url> [--version <version_name>]
# 后续使用文件名（自动查找映射）
python dify_deploy.py deploy <yml_path>
```
Or via Claude Code slash command: `/project:dify-deploy path/to/agent.yml https://dify.example.com/app/<UUID>/workflow`
Or simplified: `/project:dify-deploy agent.yml` (after initial mapping)

### Export (Dify → local YAML)
```bash
# 首次使用完整 URL（自动保存映射）
python dify_deploy.py export <dify_url> --output <output_path> [--force] [--no-secret]
# 后续使用文件名（自动查找映射）
python dify_deploy.py export <filename>
```
Or via Claude Code slash command: `/project:dify-export https://dify.example.com/app/<UUID>/workflow --output path/to/output.yml`
Or simplified: `/project:dify-export agent.yml` (after initial mapping)

### Mapping Management
```bash
python dify_deploy.py list              # 列出所有映射
python dify_deploy.py unbind <filename> # 删除映射
```

### Sync Web App Name
```bash
python dify_deploy.py sync-name <dify_url_or_filename>
```
Or via Claude Code slash command: `/project:dify-sync-name agent.yml`

自动检查并同步 Web App 名称到应用名称，在 deploy 成功后也会自动执行。

### Setup
```bash
cp dify_deploy_config.example.json dify_deploy_config.json
# Edit with: base_url, email, password
pip install requests
```

## Architecture

Single-file Python script (`dify_deploy.py`) with five subcommands. No build step, no tests.

**Flow:**
1. `load_config()` reads credentials from `dify_deploy_config.json` (sibling to script)
2. `login()` POSTs to `/console/api/login` with base64-encoded password (Dify v1.11+ format), extracts `access_token` from cookies or response body
3. **deploy** path: `import_yml()` → `POST /console/api/apps/imports` (mode: yaml-content), then `publish()` → `POST /console/api/apps/{app_id}/workflows/publish`, then `sync_name()` to auto-sync Web App name
4. **export** path: `export_yml()` → `GET /console/api/apps/{app_id}/export`, writes raw YAML string to disk
5. **sync-name** path: `get_app_info()` → `GET /console/api/apps/{app_id}` (site config is embedded in `site` field), then `update_site_name()` → `POST /console/api/apps/{app_id}/site` with full site config if names differ

**Mapping feature:** `dify_app_mapping.json` stores filename → (base_url, app_id) mappings. Deploy/export commands accept either full URL or filename. When given a URL, they auto-save the mapping after success. When given a filename, they look up the mapping via `lookup_mapping()`.

**URL parsing:** `extract_app_id()` pulls the UUID from `/app/<UUID>/workflow` style URLs; `extract_base_url()` extracts scheme+host. Both `sys.exit(1)` on failure. `is_url()` determines whether input is a URL or filename.

**Claude Code commands** (`.claude/commands/`): `dify-deploy.md`, `dify-export.md`, `dify-list.md`, `dify-unbind.md`, and `dify-sync-name.md` are thin wrappers that parse user arguments and invoke `python dify_deploy.py` with the right subcommand. They declare `allowed-tools: Bash(python *), Read`.

## Conventions

- All console output is in Chinese (error messages, status lines, etc.)
- Windows UTF-8 stdout fix at script top: `sys.stdout.reconfigure(encoding="utf-8")`
- Status prefixes: `[INFO]`, `[OK]`, `[ERROR]`
- Dify import API uses overwrite mode — replaces the entire target app config
- Export defaults to including secret env vars; `--no-secret` excludes them
- Export refuses to overwrite existing files unless `--force` is passed

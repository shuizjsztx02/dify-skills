# Dify CLI

命令行工具 for [Dify](https://dify.ai)，支持多服务器配置，可在任意项目文件夹使用。

## Features

- **多服务器支持** — 配置多个 Dify 服务器，随时切换
- **智能映射** — 文件名与 Dify 应用自动映射，简化操作
- **部署发布** — 导入本地 YAML 到 Dify 并发布
- **导出备份** — 从 Dify 导出 YAML 到本地
- **名称同步** — 自动同步 Web App 名称与应用名称
- **YAML 校验** — 检查 YAML 语法和 Dify DSL 结构完整性
- **工作流测试** — 调用工作流并生成测试报告，支持批量测试和 Token 统计

## Prerequisites

- Python 3.10+
- A self-hosted Dify instance with valid credentials

## Installation

```bash
# Clone the repository
git clone https://github.com/shuizjsztx02/dify-skills.git
cd dify-skills

# Install globally
pip install -e .

# Initialize configuration (interactive)
dify init
```

### Configuration Files

After running `init`, configuration is stored in:
- **Config**: `~/.dify/config.json` — server credentials
- **Mapping**: `~/.dify/mapping.json` — filename to app mappings

Example `config.json`:
```json
{
  "default_server": "work",
  "servers": {
    "work": {
      "base_url": "https://dify-work.company.com",
      "email": "user@company.com",
      "password": "password1"
    },
    "personal": {
      "base_url": "https://dify.example.com",
      "email": "user@example.com",
      "password": "password2"
    }
  }
}
```

## Usage

### Server Management

```bash
# Add/modify servers
dify init

# List configured servers
dify servers

# Set default server
dify servers --set-default work

# Remove a server
dify servers --remove test
```

### Deploy (Local → Dify)

```bash
# First time with full URL (auto-saves mapping)
dify deploy path/to/agent.yml https://dify.example.com/app/<APP_UUID>/workflow

# With version name
dify deploy path/to/agent.yml https://dify.example.com/app/<APP_UUID>/workflow --version v2.1

# Specify server
dify deploy path/to/agent.yml https://dify.example.com/app/<APP_UUID>/workflow --server work

# Subsequent uses with filename (auto-lookup mapping)
dify deploy agent.yml
```

### Export (Dify → Local)

```bash
# First time with full URL
dify export https://dify.example.com/app/<APP_UUID>/workflow --output path/to/output.yml

# Force overwrite
dify export https://dify.example.com/app/<APP_UUID>/workflow --output path/to/output.yml --force

# Exclude secrets
dify export https://dify.example.com/app/<APP_UUID>/workflow --output path/to/output.yml --no-secret

# Subsequent uses with filename
dify export output.yml
```

### Mapping Management

```bash
# List all mappings (shows server, app_id, last used)
dify list

# Delete a mapping
dify unbind agent.yml
```

### Sync Web App Name

```bash
# Sync using URL
dify sync-name https://dify.example.com/app/<APP_UUID>/workflow

# Sync using mapped filename
dify sync-name agent.yml
```

### Check YAML

```bash
# Check single file
dify check-yml path/to/agent.yml

# Check multiple files
dify check-yml agent1.yml agent2.yml agent3.yml

# Check all YAML files in directory
dify check-yml path/to/directory
```

### Test Workflow

```bash
# Test with mapped file (auto-login, auto-generate test data)
dify test agent.yml

# Test with count (batch testing)
dify test agent.yml --count 10

# Test with custom test data directory (for file inputs)
dify test agent.yml --test-data path/to/test/images

# Test with URL directly
dify test https://dify.example.com/app/<APP_UUID>/workflow --count 5
```

Test report includes:
- Success/failure status
- Total and average execution time
- Total and average token consumption
- Error details (if any)

## Claude Code Integration

This tool includes Claude Code commands for seamless integration:

- `/project:dify-init` — Interactive server configuration
- `/project:dify-servers` — Manage server list
- `/project:dify-deploy` — Deploy YAML to Dify
- `/project:dify-export` — Export YAML from Dify
- `/project:dify-list` — List all mappings
- `/project:dify-unbind` — Delete a mapping
- `/project:dify-sync-name` — Sync Web App name
- `/project:dify-check-yml` — Check YAML syntax and structure
- `/project:dify-test` — Test workflow with auto-generated data
- `/project:dify-features` — List all available features

## Architecture

```
src/dify_cli/
├── __init__.py
├── cli.py          # Main entry point
├── config.py       # Configuration management
├── auth.py         # Authentication
├── utils.py        # Utility functions
├── mapping.py      # Mapping management
└── commands/       # Subcommands
    ├── init_cmd.py
    ├── servers_cmd.py
    ├── deploy_cmd.py
    ├── export_cmd.py
    ├── list_cmd.py
    ├── unbind_cmd.py
    ├── sync_name_cmd.py
    ├── check_cmd.py
    ├── test_cmd.py
    └── features_cmd.py
```

## Compatibility

Tested on multiple self-hosted Dify instances with different versions. The export and import APIs are stable across Dify versions.

## License

MIT

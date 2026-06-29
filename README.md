# Dify CLI

命令行工具 for [Dify](https://dify.ai)，支持多服务器配置，可在任意项目文件夹使用。

## Features

- **全局安装** — 一次安装，全局生效，支持多项目文件夹使用
- **多服务器支持** — 配置多个 Dify 服务器，随时切换
- **智能映射** — 文件名与 Dify 应用自动映射，简化操作
- **部署发布** — 导入本地 YAML 到 Dify 并发布
- **导出备份** — 从 Dify 导出 YAML 到本地
- **名称同步** — 自动同步 Web App 名称与应用名称
- **应用查询** — 查询 app-id、Web App 链接、API Key（无则自动创建）
- **版本历史** — 查询工作流版本历史（版本名、说明、发布时间）
- **YAML 校验** — 检查 YAML 语法和 Dify DSL 结构完整性
- **工作流测试** — 调用工作流并生成 Markdown 测试报告，支持批量测试和 Token 统计
- **Claude Code 集成** — 全局 slash commands，任意项目中使用

## Prerequisites

- Python 3.10+
- A self-hosted Dify instance with valid credentials
- Claude Code (optional, for slash commands)

## Installation

### 1. 安装 dify-cli（命令行工具）

```bash
# Clone the repository
git clone https://github.com/shuizjsztx02/dify-skills.git
cd dify-skills

# Install globally (editable mode)
pip install -e .

# Initialize configuration (interactive)
dify init
```

安装完成后：
- `dify` 命令全局可用（任意文件夹）
- 配置存储在 `~/.dify/`（跨项目共享）
- Claude Code commands 自动安装到 `~/.claude/commands/`

### 2. 安装 Claude Code Slash Commands（可选）

`dify init` 会自动安装 Claude Code commands。如需手动安装：

```bash
# 手动安装
dify install

# 卸载
dify install --uninstall
```

安装后，在**任意文件夹**下打开 Claude Code，输入 `/` 即可看到 `dify-*` commands。

### Configuration Files

After running `init`, configuration is stored in:
- **Config**: `~/.dify/config.json` — server credentials（全局）
- **Mapping**: `~/.dify/mapping.json` — filename to app mappings（全局）
- **Claude Commands**: `~/.claude/commands/dify-*.md`（全局）

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

### 使用方式

有两种使用方式：

| 方式 | 说明 | 示例 |
|------|------|------|
| **命令行** | 直接在终端执行 | `dify deploy agent.yml <url>` |
| **Claude Code** | 让 Claude 帮你操作 | `/dify-deploy agent.yml <url>` |

命令行方式适合自动化脚本，Claude Code 方式适合交互式开发。

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

### Query App Info (get-msg)

```bash
# Query app-id, Web App link, and API Key
dify get-msg https://dify.example.com/app/<APP_UUID>/workflow

# Query using mapped filename
dify get-msg agent.yml

# Specify server
dify get-msg https://dify.example.com/app/<APP_UUID>/workflow --server work
```

Output includes:
- **app-id** — Dify application UUID
- **Web App 链接** — public share link (mode-aware: workflow/chat/completion)
- **API Key** — existing keys listed, or auto-created if none exist

### Version History (versions)

```bash
# Show latest 10 versions (default)
dify versions https://dify.example.com/app/<APP_UUID>/workflow

# Custom count
dify versions https://dify.example.com/app/<APP_UUID>/workflow --limit 20

# Using mapped filename
dify versions agent.yml
```

Output includes version name, description, publish time, and publisher for each entry.

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

This tool includes Claude Code commands for seamless integration.

### 全局安装（推荐）

运行 `dify init` 或 `dify install` 后，commands 会安装到 `~/.claude/commands/`，在**任意文件夹**下打开 Claude Code 都能使用：

```bash
# 在任意项目文件夹中
cd D:/your-project
claude

# 然后输入 / 可以看到：
/dify-init        # 配置服务器
/dify-deploy      # 部署 YAML
/dify-export      # 导出 YAML
/dify-list        # 列出映射
/dify-check-yml   # 校验 YAML
/dify-test        # 测试工作流
# ... 等等
```

### Commands 列表

| Command | 说明 |
|---------|------|
| `/dify-init` | 交互式配置服务器 |
| `/dify-servers` | 管理服务器列表 |
| `/dify-deploy` | 部署 YAML 到 Dify |
| `/dify-export` | 从 Dify 导出 YAML |
| `/dify-list` | 列出所有映射 |
| `/dify-unbind` | 删除映射 |
| `/dify-sync-name` | 同步 Web App 名称 |
| `/dify-get-msg` | 查询 app-id / Web App 链接 / API Key |
| `/dify-versions` | 查询工作流版本历史 |
| `/dify-check-yml` | 校验 YAML 语法和结构 |
| `/dify-test` | 自动测试工作流 |
| `/dify-features` | 列出所有命令功能 |
| `/dify-install` | 安装/卸载 Claude Code commands |

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
    ├── install_cmd.py    # 安装 Claude Code commands
    ├── servers_cmd.py
    ├── deploy_cmd.py
    ├── export_cmd.py
    ├── list_cmd.py
    ├── unbind_cmd.py
    ├── sync_name_cmd.py
    ├── check_cmd.py
    ├── getmsg_cmd.py       # 查询 app-id / Web App 链接 / API Key
    ├── versions_cmd.py     # 查询工作流版本历史
    ├── test_cmd.py
    └── features_cmd.py

全局存储位置：
~/.dify/
├── config.json     # 服务器配置（全局）
└── mapping.json    # 文件映射（全局，使用 项目目录/文件名 作为 key）

~/.claude/commands/
└── dify-*.md       # Claude Code slash commands（全局）
```

## 全局安装机制

本工具采用全局安装设计：

1. **命令行工具全局可用**：`pip install -e .` 后，`dify` 命令可在任意文件夹使用
2. **配置全局共享**：服务器配置和映射关系存储在 `~/.dify/`，所有项目共享
3. **Claude Code commands 全局安装**：`dify init` 或 `dify install` 会将 commands 复制到 `~/.claude/commands/`
4. **映射使用项目目录名**：不同项目的同名文件不会冲突（如 `project-a/agent.yml` vs `project-b/agent.yml`）

## 给同事的安装说明

```bash
# 1. 克隆仓库（只需一次）
git clone https://github.com/shuizjsztx02/dify-skills.git
cd dify-skills

# 2. 安装（只需一次）
pip install -e .
dify init    # 配置服务器 + 安装 Claude Code commands

# 3. 在任意项目文件夹中使用
cd D:/your-project
dify deploy agent.yml http://dify.com/app/xxx/workflow
# 或者打开 Claude Code
claude
/dify-deploy agent.yml http://dify.com/app/xxx/workflow
```

## Compatibility

Tested on multiple self-hosted Dify instances with different versions. The export and import APIs are stable across Dify versions.

## License

MIT

# Dify Deploy Skill

Claude Code skill for deploying and exporting [Dify](https://dify.ai) workflows via YAML.

Supports self-hosted Dify instances (tested on v0.6+ DSL format).

## Features

- **dify-deploy**: Import a local YAML file to a Dify app and publish it
- **dify-export**: Export a Dify app's YAML configuration to a local file

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Python 3.10+ with `requests` library (`pip install requests`)
- A self-hosted Dify instance with valid credentials

## Setup

1. Clone this repo into your project directory (or add as a submodule):

   ```bash
   git clone https://github.com/shuizjsztx02/dify-skills.git
   ```

   Or copy the files directly into your project root. The key files are:
   ```
   .claude/commands/dify-deploy.md
   .claude/commands/dify-export.md
   dify_deploy.py
   ```

2. Create your config file from the template:

   ```bash
   cp dify_deploy_config.example.json dify_deploy_config.json
   ```

3. Edit `dify_deploy_config.json` with your Dify credentials:

   ```json
   {
       "base_url": "https://your-dify-domain.com",
       "email": "your-email@example.com",
       "password": "your-password"
   }
   ```

   > **Note**: The `base_url` in config is a fallback; the actual target server is determined by the URL you pass to each command.

## Usage

### Deploy (Local → Dify)

Import a local YAML to a Dify app and publish it:

```
/project:dify-deploy path/to/agent.yml https://your-dify.com/app/<APP_UUID>/workflow
```

With a version name:

```
/project:dify-deploy path/to/agent.yml https://your-dify.com/app/<APP_UUID>/workflow --version v2.1
```

### Export (Dify → Local)

Export a Dify app's YAML to a local file:

```
/project:dify-export https://your-dify.com/app/<APP_UUID>/workflow --output path/to/output.yml
```

Force overwrite an existing file:

```
/project:dify-export https://your-dify.com/app/<APP_UUID>/workflow --output path/to/output.yml --force
```

Export without secret environment variables:

```
/project:dify-export https://your-dify.com/app/<APP_UUID>/workflow --output path/to/output.yml --no-secret
```

## Using the Python Script Directly

You can also run the script without Claude Code:

```bash
# Deploy
python dify_deploy.py deploy <yml_path> <dify_url> [--version <version>]

# Export
python dify_deploy.py export <dify_url> --output <output_path> [--force] [--no-secret]
```

## How It Works

1. Reads credentials from `dify_deploy_config.json`
2. Logs into Dify via `/console/api/login` (supports Dify v1.11+ base64 password encoding)
3. For **deploy**: calls `POST /console/api/apps/imports` then `POST /console/api/apps/{app_id}/workflows/publish`
4. For **export**: calls `GET /console/api/apps/{app_id}/export`

## Compatibility

Tested on multiple self-hosted Dify instances with different versions. The export and import APIs (`/console/api/apps/{id}/export` and `/console/api/apps/imports`) are stable across Dify versions.

## License

MIT

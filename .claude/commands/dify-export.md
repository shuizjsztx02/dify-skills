---
description: "从 Dify 智能体导出 YML 到本地"
allowed-tools:
  - Bash(python *)
  - Read
---

从 Dify 智能体导出 YML 配置到本地文件。

参数: $ARGUMENTS

## 使用方式

用户输入格式: `<dify智能体URL> --output <本地保存路径> [--force] [--no-secret]`

示例:
- `/project:dify-export https://dify.example.com/app/xxxxxxxx/workflow --output path/to/agent.yml`
- `/project:dify-export https://dify.example.com/app/xxxxxxxx/workflow --output path/to/agent.yml --force`
- `/project:dify-export https://dify.example.com/app/xxxxxxxx/workflow -o path/to/agent.yml -f`

参数说明:
- `--output` / `-o`: 必填，本地保存路径
- `--force` / `-f`: 可选，目标文件已存在时强制覆盖（默认会报错）
- `--no-secret`: 可选，导出时不包含密钥类环境变量（默认包含）

## 执行步骤

1. 解析用户输入，提取 dify URL、--output 路径和可选的 --force / --no-secret 参数
2. 执行导出脚本:
   ```
   python dify_deploy.py export <dify_url> --output <output_path> [--force] [--no-secret]
   ```
3. 检查输出，确认导出是否成功
4. 如果失败，分析错误信息并给出修复建议

## 注意事项

- 配置文件位于 `dify_deploy_config.json`，包含 Dify 域名、邮箱和密码
- 如果提示配置文件不存在或凭据错误，提醒用户检查 `dify_deploy_config.json`
- 默认不覆盖已存在的文件，需要加 `--force` 参数才会覆盖
- 导出的 YML 包含完整的智能体配置（workflow、节点、环境变量等）
- 如果输出路径的父目录不存在，会自动创建

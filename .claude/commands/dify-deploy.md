---
description: "导入本地 YML 到 Dify 智能体并发布"
allowed-tools:
  - Bash(python *)
  - Read
---

将本地 YML 文件导入到 Dify 智能体并发布。

参数: $ARGUMENTS

## 使用方式

用户输入格式: `<yml文件路径> <dify智能体URL> [--version 版本名称]`

示例:
- `/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow`
- `/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow --version v2.1`

## 执行步骤

1. 解析用户输入，提取 yml 文件路径、dify URL 和可选的 --version 参数
2. 执行部署脚本:
   ```
   python dify_deploy.py deploy <yml_path> <dify_url> [--version <version_name>]
   ```
3. 检查输出，确认导入和发布是否成功
4. 如果失败，分析错误信息并给出修复建议

## 注意事项

- 配置文件位于 `dify_deploy_config.json`，包含 Dify 域名、邮箱和密码
- 如果提示配置文件不存在或凭据错误，提醒用户检查 `dify_deploy_config.json`
- 脚本使用 overwrite 模式，会完全替换目标智能体的配置
- 版本名称是可选的，用于标记发布的版本

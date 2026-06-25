---
description: "从 Dify 智能体导出 YML 到本地。用法: <URL> --output <路径> [--force] [--no-secret] 或 <文件名> [--force]"
allowed-tools:
  - Bash(python *)
  - Read
---

从 Dify 智能体导出 YML 配置到本地文件。

参数: $ARGUMENTS

## 使用方式

方式 1 - 首次使用完整 URL（自动保存映射）:
/dify-export <URL> --output <路径> [--force] [--no-secret]

方式 2 - 后续使用文件名（自动查找映射）:
/dify-export <文件名> [--force] [--no-secret]

参数:
- URL: Dify 应用 URL，如 http://3.19.168.125/app/<UUID>/workflow
- 文件名: 已映射的文件名，如 agent.yml
- --output / -o: 使用 URL 时必填，使用文件名时自动用文件名作为输出路径
- --force / -f: 覆盖已存在的文件
- --no-secret: 不包含密钥环境变量

## 执行步骤

1. 解析用户输入
2. 执行: python dify_deploy.py export $ARGUMENTS
3. 检查结果

## 注意事项

- 配置文件位于 dify_deploy_config.json
- 映射关系保存在 dify_app_mapping.json 中
- 查看映射: python dify_deploy.py list
- 删除映射: python dify_deploy.py unbind <文件名>

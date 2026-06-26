---
description: "从 Dify 智能体导出 YML 到本地（支持多服务器）。用法: <URL> --output <路径> [--server <名称>] [--force] [--no-secret] 或 <文件名> [--force]"
allowed-tools:
  - Bash(dify *)
  - Read
---

从 Dify 智能体导出 YML 配置到本地文件。

参数: $ARGUMENTS

## 使用方式

方式 1 - 首次使用完整 URL（自动保存映射）:
```
/project:dify-export <URL> --output <路径> [--force] [--no-secret]
```

方式 2 - 指定服务器:
```
/project:dify-export <URL> --output <路径> --server work
```

方式 3 - 后续使用文件名（自动查找映射）:
```
/project:dify-export <文件名> [--force] [--no-secret]
```

参数:
- URL: Dify 应用 URL，如 https://dify.example.com/app/<UUID>/workflow
- 文件名: 已映射的文件名，如 agent.yml
- --output / -o: 使用 URL 时必填
- --server / -s: 指定服务器名称
- --force / -f: 覆盖已存在的文件
- --no-secret: 不包含密钥环境变量

## 执行步骤

1. 解析用户输入
2. 执行: `dify export $ARGUMENTS`
3. 检查结果

## 注意事项

- 配置文件位于 `~/.dify/config.json`，支持多服务器
- 映射关系保存在 `~/.dify/mapping.json`
- 查看映射: `dify list`
- 删除映射: `dify unbind <文件名>`

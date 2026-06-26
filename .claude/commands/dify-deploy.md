---
description: "导入本地 YML 到 Dify 智能体并发布（支持多服务器）"
allowed-tools:
  - Bash(dify *)
  - Read
---

将本地 YML 文件导入到 Dify 智能体并发布。

参数: $ARGUMENTS

## 使用方式

### 方式 1: 首次使用完整 URL（会自动保存映射）

```
/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow
/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow --version v2.1
```

### 方式 2: 指定服务器

```
/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow --server work
```

### 方式 3: 后续使用文件名（自动查找映射）

```
/project:dify-deploy agent.yml
/project:dify-deploy agent.yml --version v2.2
```

说明：首次使用完整 URL 部署后，系统会自动保存映射关系（包含服务器信息）。后续只需传文件名即可。

## 执行步骤

1. 解析用户输入，提取 yml 文件路径和 dify URL（或文件名）
2. 执行部署命令:
   ```bash
   dify deploy <yml_path> <dify_url_or_filename> [--server <name>] [--version <version_name>]
   ```
3. 检查输出，确认导入和发布是否成功
4. 如果失败，分析错误信息并给出修复建议

## 服务器管理

- 初始化配置：`dify init`
- 查看服务器：`dify servers`

## 映射管理

- 查看所有映射：`dify list`
- 删除映射：`dify unbind <yml_path>`

## 注意事项

- 配置文件位于 `~/.dify/config.json`，支持多服务器配置
- 如果提示配置不存在，提醒用户运行 `dify init`
- 脚本使用 overwrite 模式，会完全替换目标智能体的配置
- 版本名称是可选的，用于标记发布的版本
- 映射关系保存在 `~/.dify/mapping.json` 中

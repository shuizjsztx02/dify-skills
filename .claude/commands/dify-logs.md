---
description: "查询 Dify 工作流执行日志（含状态/耗时/Token/异常）"
allowed-tools:
  - Bash(dify *)
  - Read
---

查询 Dify 工作流的执行日志，显示每次执行的状态、耗时、Token 消耗、步数、异常数、版本和触发者。

参数: $ARGUMENTS

## 使用方式

### 使用完整 URL
```
/project:dify-logs https://dify.example.com/app/xxxxxxxx/workflow
/project:dify-logs https://dify.example.com/app/xxxxxxxx/workflow --limit 20
/project:dify-logs https://dify.example.com/app/xxxxxxxx/workflow --status failed
```

### 使用已映射的文件名
```
/project:dify-logs agent.yml
```

### 指定服务器
```
/project:dify-logs agent.yml --server work
```

## 执行步骤

1. 解析用户输入，提取 Dify URL 或文件名
2. 如果是文件名，从映射中查找服务器和 app_id
3. 登录 Dify
4. 获取应用信息（仅支持 workflow 类型应用）
5. 查询执行日志（GET /console/api/apps/{app_id}/workflow-runs）
6. 输出每条执行记录及汇总统计

## 输出示例

```
[INFO] 应用: 【生产】IGBG-TCG卡-TCG卡识别  (mode: workflow)
======================================================================
执行日志 (本页 5 条，共 5+ 条)
======================================================================

[ 1]      2026-06-29 16:03:37  成功
       耗时 9.867825s · Tokens 5949 · 步骤 10 · 异常 0
       版本 草稿 · 触发 sebastian

[ 2] [失败] 2026-06-29 15:20:11  失败
       耗时 2.31s · Tokens 270 · 步骤 8 · 异常 1
       版本 v2.1 · 触发 sebastian

======================================================================
汇总: 共 5 条 (失败 1) | 总耗时 18.5s | 总 Tokens 12000 | 平均 2400
======================================================================
```

## 注意事项

- 默认显示最新 10 条，可通过 `--limit` 或 `-n` 调整
- `--status` 可按状态过滤: `succeeded`/`failed`/`running`/`stopped`
- 仅支持 `workflow` 类型应用；chat/agent-chat 应用的日志请通过 Dify 控制台查看
- 失败的执行会用 `[失败]` 标记
- 汇总统计包含总耗时、总 Token、平均 Token、失败数

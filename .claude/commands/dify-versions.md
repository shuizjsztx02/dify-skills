---
description: "查询 Dify 工作流版本历史（默认最新 10 条，含版本名和说明）"
allowed-tools:
  - Bash(dify *)
  - Read
---

查询 Dify 工作流的版本历史，显示版本名、版本说明文案、发布时间、发布者。

参数: $ARGUMENTS

## 使用方式

### 使用完整 URL
```
/project:dify-versions https://dify.example.com/app/xxxxxxxx/workflow
/project:dify-versions https://dify.example.com/app/xxxxxxxx/workflow --limit 5
```

### 使用已映射的文件名
```
/project:dify-versions agent.yml
```

### 指定服务器
```
/project:dify-versions agent.yml --server work
```

## 执行步骤

1. 解析用户输入，提取 Dify URL 或文件名
2. 如果是文件名，从映射中查找服务器和 app_id
3. 登录 Dify
4. 获取应用基本信息
5. 查询版本历史（GET /console/api/apps/{app_id}/workflows）
6. 输出最新 N 条版本：版本名、说明文案、发布时间、发布者

## 输出示例

```
[INFO] 应用: skill-test  (mode: workflow)
======================================================================
版本历史 (最新 3 条，共 11 条)
======================================================================

[ 1] [当前草稿] 2026-06-29 15:54 · sebastian
     版本名: (未命名)
     说  明: (无)

[ 2] [最新发布] 2026-06-29 15:54 · sebastian
     版本名: v2.1
     说  明: 修复了评分逻辑

[ 3] 2026-06-18 17:56 · sebastian
     版本名: (未命名)
     说  明: (无)
======================================================================
```

## 注意事项

- 默认显示最新 10 条，可通过 `--limit` 或 `-n` 调整
- 第 1 条为当前草稿（未发布），第 2 条为最新已发布版本
- 版本名和说明由 `deploy` 命令的 `--version` 参数设置；若未设置则显示"(未命名)/(无)"
- 需要使用完整 URL 或已映射的文件名

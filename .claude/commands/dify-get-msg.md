---
description: "查询 Dify 应用的 app-id / Web App 链接 / API Key（无则创建）"
allowed-tools:
  - Bash(dify *)
  - Read
---

查询 Dify 应用的 app-id、Web App 公开访问链接、API Key。如果应用没有 API Key，会自动创建一个。

参数: $ARGUMENTS

## 使用方式

### 使用完整 URL
```
/project:dify-get-msg https://dify.example.com/app/xxxxxxxx/workflow
```

### 使用已映射的文件名
```
/project:dify-get-msg agent.yml
```

### 指定服务器
```
/project:dify-get-msg agent.yml --server work
```

## 执行步骤

1. 解析用户输入，提取 Dify URL 或文件名
2. 如果是文件名，从映射中查找服务器和 app_id
3. 登录 Dify
4. 获取应用信息（名称、模式、site.code、app_base_url）
5. 列出现有 API Key；如果一个都没有，自动创建一个
6. 输出 app-id / Web App 链接 / API Key

## 输出示例

```
[OK] 应用名称: skill-test  (mode: workflow)
[OK] App ID:  be521716-4c67-4912-9099-8fc36325607b
[OK] Web App: http://3.19.168.125/workflow/2X8H4qcoIeI0RMTV
[OK] API Key: app-xxxxxxxx  (已存在 / 新建)
```

## 注意事项

- Web App 链接按应用模式构造：workflow → `/workflow/{code}`，chat/agent-chat/advanced-chat → `/chat/{code}`，completion → `/completion/{code}`
- 需要使用完整 URL 或已映射的文件名
- 映射关系保存在 `~/.dify/mapping.json` 中

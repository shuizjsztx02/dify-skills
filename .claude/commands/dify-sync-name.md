---
description: "同步 Web App 名称到应用名称"
allowed-tools:
  - Bash(python *)
  - Read
---

检查并同步 Web App 名称，使其与应用名称保持一致。

参数: $ARGUMENTS

## 使用方式

### 使用完整 URL
```
/project:dify-sync-name https://dify.example.com/app/xxxxxxxx/workflow
```

### 使用已映射的文件名
```
/project:dify-sync-name agent.yml
```

## 执行步骤

1. 解析用户输入，提取 dify URL 或文件名
2. 如果是文件名，从映射中查找 base_url 和 app_id
3. 登录 Dify
4. 获取应用信息（应用名称）
5. 获取 Web App 配置（Web App 名称）
6. 如果两者不一致，自动更新 Web App 名称
7. 如果一致，提示已同步

## 注意事项

- 该功能会在 deploy 成功后自动执行
- 也可以手动调用此命令进行同步
- 需要使用完整 URL 或已映射的文件名
- 映射关系保存在 `dify_app_mapping.json` 中

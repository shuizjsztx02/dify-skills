---
description: "查看所有已保存的 YML 文件与 Dify app 映射关系"
allowed-tools:
  - Bash(python *)
  - Read
---

查看所有已保存的映射关系。

参数: $ARGUMENTS

## 使用方式

```
/project:dify-list
```

## 执行步骤

1. 执行查看映射命令:
   ```
   python dify_deploy.py list
   ```
2. 展示所有已保存的映射关系，包括文件名、base_url、app_id 和最后使用时间

## 注意事项

- 映射关系保存在 `dify_app_mapping.json` 中
- 如果没有映射关系，会提示"当前没有映射关系"
- 首次使用完整 URL 进行 deploy 或 export 时会自动创建映射

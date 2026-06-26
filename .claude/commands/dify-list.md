---
description: "查看所有已保存的 YML 文件与 Dify app 映射关系（含服务器信息）"
allowed-tools:
  - Bash(dify *)
  - Read
---

查看所有已保存的映射关系，包含服务器信息。

参数: $ARGUMENTS

## 使用方式

```
/project:dify-list
```

## 执行步骤

1. 执行查看映射命令:
   ```bash
   dify list
   ```
2. 展示所有已保存的映射关系，包括文件名、服务器、app_id 和最后使用时间

## 注意事项

- 映射关系保存在 `~/.dify/mapping.json` 中
- 如果没有映射关系，会提示"当前没有映射关系"
- 首次使用完整 URL 进行 deploy 或 export 时会自动创建映射

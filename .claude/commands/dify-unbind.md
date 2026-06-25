---
description: "删除 YML 文件与 Dify app 的映射关系"
allowed-tools:
  - Bash(python *)
  - Read
---

删除指定的映射关系。

参数: $ARGUMENTS

## 使用方式

```
/project:dify-unbind <文件名>
```

示例:
- `/project:dify-unbind agent.yml`
- `/project:dify-unbind workflow/agent.yml`

## 执行步骤

1. 解析用户输入，提取要删除映射的文件名
2. 执行删除映射命令:
   ```
   python dify_deploy.py unbind <filename>
   ```
3. 确认映射已成功删除

## 注意事项

- 删除映射后，再次使用该文件名时需要重新提供完整 URL
- 如果文件名不存在于映射中，会报错提示
- 可以使用 `/project:dify-list` 查看所有已保存的映射

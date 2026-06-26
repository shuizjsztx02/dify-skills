---
description: "列出 Dify CLI 已实现的所有命令功能"
allowed-tools:
  - Bash(dify *)
  - Read
---

列出 Dify CLI 当前已实现的所有命令功能和使用方法。

## 使用方式

```
/project:dify-features
```

## 执行步骤

1. 执行命令:
   ```bash
   dify features
   ```
2. 展示所有命令功能，按类别分组
3. 显示每个命令的用法示例
4. 列出所有可用的 Claude Code Slash Commands

## 输出内容

- **服务器管理**: init, servers
- **部署**: deploy
- **导出**: export
- **映射管理**: list, unbind
- **同步**: sync-name
- **校验**: check
- **帮助**: features (本命令)

## 注意事项

- 此命令用于快速了解 CLI 当前支持哪些功能
- 每个命令都附带用法示例
- 同时列出对应的 Claude Code Slash Command

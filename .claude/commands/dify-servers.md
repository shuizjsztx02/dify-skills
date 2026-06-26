---
description: "查看和管理已配置的 Dify 服务器列表"
allowed-tools:
  - Bash(dify *)
  - Read
---

查看和管理已配置的 Dify 服务器。

参数: $ARGUMENTS

## 使用方式

### 查看所有服务器
```
/project:dify-servers
```

### 设置默认服务器
```
/project:dify-servers --set-default work
```

### 删除服务器
```
/project:dify-servers --remove test
```

## 执行步骤

1. 执行服务器管理命令:
   ```bash
   dify servers [--set-default <name>] [--remove <name>]
   ```
2. 展示所有已配置的服务器信息

## 注意事项

- 默认服务器会在未指定时自动使用
- 不能删除默认服务器（需先设置其他为默认）
- 使用 `dify init` 添加新服务器

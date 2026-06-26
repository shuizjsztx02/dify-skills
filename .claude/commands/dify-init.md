---
description: "交互式配置 Dify 服务器（支持多服务器）"
allowed-tools:
  - Bash(dify *)
  - Read
---

交互式初始化 Dify 服务器配置。

参数: $ARGUMENTS

## 使用方式

```
/project:dify-init
```

## 执行步骤

1. 执行初始化命令:
   ```bash
   dify init
   ```
2. 按提示输入服务器信息:
   - 服务器名称（如 work, personal）
   - Dify URL
   - 登录邮箱
   - 登录密码
3. 可选择继续添加更多服务器
4. 设置默认服务器

## 配置文件

配置保存在 `~/.dify/config.json`，格式如下:

```json
{
  "default_server": "work",
  "servers": {
    "work": {
      "base_url": "https://dify-work.company.com",
      "email": "user@company.com",
      "password": "password1"
    },
    "personal": {
      "base_url": "https://dify.example.com",
      "email": "user@example.com",
      "password": "password2"
    }
  }
}
```

## 注意事项

- 支持配置多个 Dify 服务器
- 首次使用必须运行此命令
- 配置保存在用户目录，跨项目共享

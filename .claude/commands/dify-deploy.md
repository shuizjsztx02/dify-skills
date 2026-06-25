---
description: "导入本地 YML 到 Dify 智能体并发布"
allowed-tools:
  - Bash(python *)
  - Read
---

将本地 YML 文件导入到 Dify 智能体并发布。

参数: $ARGUMENTS

## 使用方式

### 方式 1: 首次使用完整 URL（会自动保存映射）

```
/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow
/project:dify-deploy path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow --version v2.1
```

### 方式 2: 后续使用文件名（自动查找映射）

```
/project:dify-deploy agent.yml
/project:dify-deploy agent.yml --version v2.2
```

说明：首次使用完整 URL 部署后，系统会自动保存 YML 文件名与 Dify app 的映射关系。后续只需传文件名即可，无需重复输入完整 URL。

## 执行步骤

1. 解析用户输入，提取 yml 文件路径和 dify URL（或文件名）
2. 判断 dify_url 是 URL 还是文件名：
   - 如果是 URL：提取 base_url 和 app_id，执行部署后自动保存映射
   - 如果是文件名：从映射中查找 base_url 和 app_id
3. 执行部署脚本:
   ```
   python dify_deploy.py deploy <yml_path> <dify_url_or_filename> [--version <version_name>]
   ```
4. 检查输出，确认导入和发布是否成功
5. 如果失败，分析错误信息并给出修复建议

## 映射管理

- 查看所有映射：`python dify_deploy.py list`
- 删除映射：`python dify_deploy.py unbind <yml_path>`

## 注意事项

- 配置文件位于 `dify_deploy_config.json`，包含 Dify 域名、邮箱和密码
- 如果提示配置文件不存在或凭据错误，提醒用户检查 `dify_deploy_config.json`
- 脚本使用 overwrite 模式，会完全替换目标智能体的配置
- 版本名称是可选的，用于标记发布的版本
- 映射关系保存在 `dify_app_mapping.json` 中

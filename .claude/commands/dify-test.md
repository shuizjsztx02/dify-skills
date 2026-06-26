---
description: "自动测试 Dify 工作流（解析 YML + 生成测试数据 + 调用 API）"
allowed-tools:
  - Bash(dify *)
  - Read
---

自动测试 Dify 工作流，无需手动在网页上操作。

参数: $ARGUMENTS

## 使用方式

### 自动测试（AI 生成测试数据）
```
/project:dify-test path/to/agent.yml --url https://dify.example.com/app/<UUID>/workflow
```

### 指定自定义输入
```
/project:dify-test path/to/agent.yml --url https://dify.example.com/app/<UUID>/workflow --input "title=人工智能的未来"
```

### 使用已部署的应用（从映射查找）
```
/project:dify-test path/to/agent.yml
```

### 指定服务器
```
/project:dify-test path/to/agent.yml --url https://dify.example.com/app/<UUID>/workflow --server work
```

### 显示详细输出
```
/project:dify-test path/to/agent.yml --url https://dify.example.com/app/<UUID>/workflow --verbose
```

## 执行步骤

1. 解析 YML 文件，提取 start 节点的输入变量
2. 根据变量类型自动生成测试数据（或解析自定义输入）
3. 自动获取/创建 API Key（需要服务器配置）
4. 调用 Dify Workflow API 运行工作流
5. 展示输出结果

## 参数说明

- `yml_path`: YML 文件路径（必需）
- `--url`: Dify 工作流 URL（可选，如果应用已部署可省略）
- `--input`: 自定义输入，格式 `key1=value1,key2=value2`（可选）
- `--server`: 指定服务器名称（可选）
- `--verbose`: 显示详细输出，包括原始 API 响应（可选）

## 自动数据生成规则

| 变量类型 | 生成策略 |
|----------|---------|
| paragraph/text-input | 根据变量名生成合理文本（如 title → "人工智能的未来"） |
| number | 生成数字 100 |
| select | 从 options 中选择第一个 |
| file | 需要用户指定文件路径 |

## 示例输出

```
[INFO] 测试文件: skill-test.yml
============================================================

[INFO] 发现 1 个输入变量:
  - title (paragraph, 必填)

[INFO] 测试数据:
  title: 人工智能的未来

[INFO] 服务器: http://3.19.168.125
[INFO] 登录中...
[OK] 登录成功
[OK] API Key: app-8m6iDoRJfsIbGluk...

[INFO] 运行工作流...

============================================================
[OK] 测试完成!
============================================================

任务 ID: 9221bcc3-791e-4080-aa9e-5d09d9654dbb

输出结果:
------------------------------------------------------------

【text】:
你好，以下是一篇以"人工智能的未来"为题...

------------------------------------------------------------
```

## 注意事项

- 需要预先配置服务器（`dify init`）
- 应用必须是 workflow 或 advanced-chat 模式
- 首次测试会自动创建 API Key
- 文件类型输入需要用户手动指定

---
description: "校验 YAML 文件语法和 Dify DSL 结构"
allowed-tools:
  - Bash(dify *)
  - Read
---

对 YAML 文件进行全面校验，确保语法正确且符合 Dify DSL 结构要求。

参数: $ARGUMENTS

## 使用方式

```
/project:dify-check-yml path/to/agent.yml
```

## 检查内容

### 1. YAML 语法校验
- 缩进是否正确
- 引号是否闭合
- 冒号格式
- 多行文本格式
- 整体语法是否合法

### 2. Dify DSL 结构校验
- 必需顶层字段（app, kind, version, workflow）
- `kind` 必须为 "app"
- `app.name` 和 `app.mode` 检查
- `workflow.graph` 结构完整性
- `nodes` 节点结构检查：
  - 节点 ID 唯一性
  - 节点类型（type）
  - 节点标题（title）
  - start 和 end 节点存在性
- `edges` 边结构检查：
  - source 和 target 节点存在性
  - sourceHandle 完整性
- 节点类型分布统计

### 3. 变量引用检查
- 收集 start 节点输入变量
- 收集环境变量
- 显示可用变量列表

## 执行步骤

1. 解析用户输入，提取 YAML 文件路径
2. 执行检查命令:
   ```bash
   dify check <yml_path>
   ```
3. 分析输出结果：
   - 如果有错误，列出具体的错误信息和位置
   - 如果有警告，列出建议修复的问题
   - 如果通过，确认可以安全导入

## 输出示例

```
[INFO] 检查文件: agent.yml
[INFO] 文件大小: 12345 bytes

[INFO] YAML 语法: 正确
[INFO] DSL 版本: 0.6.0
[INFO] 应用名称: My Agent
[INFO] 节点数量: 10
[INFO] 连接数量: 9
[INFO] 节点类型分布: code: 3, end: 1, llm: 2, start: 1, tool: 3
[INFO] 可用变量: user_input, context

============================================================
[OK] 校验通过! 错误: 0, 警告: 0
============================================================
```

## 注意事项

- 此命令用于在导入 Dify 前进行预检查
- 可以捕获常见的格式错误和结构问题
- 建议在大改动后运行此检查
- 检查通过不代表 Dify 一定会接受，但能大幅降低低级错误概率

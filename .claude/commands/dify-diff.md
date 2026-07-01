---
description: "对比本地 YML 与远程 Dify 应用差异（节点/连接/变量）"
allowed-tools:
  - Bash(dify *)
  - Read
---

对比本地 YML 文件与远程 Dify 应用，显示节点、连接、环境变量、会话变量、应用元数据的差异。

参数: $ARGUMENTS

## 使用方式

### 使用完整 URL
```
/project:dify-diff path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow
```

### 使用已映射的文件名
```
/project:dify-diff path/to/agent.yml agent.yml
```

### 指定服务器
```
/project:dify-diff path/to/agent.yml https://dify.example.com/app/xxxxxxxx/workflow --server work
```

## 执行步骤

1. 解析用户输入，提取本地 YML 路径和 Dify URL 或文件名
2. 如果 dify_url 是文件名，从映射中查找服务器和 app_id
3. 登录 Dify
4. 读取并解析本地 YML
5. 导出远程应用 YML（不含 secret）
6. 对比应用元数据、节点、连接、环境变量、会话变量
7. 输出差异报告

## 输出示例

```
本地 vs 远程 差异对比
  本地: skill-test  (8 节点, 7 连接)
  远程: skill-test  (9 节点, 8 连接)
======================================================================

[应用元数据]
  (无变更)

[节点]
  [新增节点] 1748992  "评分节点" (llm)
  [删除节点] 1748521  "旧节点" (code)
  [修改节点] 1748233  标题: 标题A -> 标题B

[连接]
  [新增连接] 1748901:null -> 1748992:null
  [删除连接] 1748521:null -> 1748522:null

[环境变量]
  [新增] NEW_API_KEY

[会话变量]
  (无变更)

======================================================================
[INFO] 共发现 5 处差异
提示: 节点内部参数的详细差异未展开，如需查看可使用 dify export 后手动对比
======================================================================
```

## 注意事项

- 第一个参数是本地 YML 文件路径，第二个参数是 Dify URL 或已映射文件名
- 对比维度: 应用元数据（名称/描述/模式/图标）、节点增删改、连接增删、环境变量、会话变量
- 节点以 id 为索引，对比标题和类型；节点内部参数的详细差异不展开
- 远程 YML 导出时不包含 secret 环境变量（`--no-secret`）
- 如本地与远程一致，显示"[OK] 本地与远程一致，无差异"

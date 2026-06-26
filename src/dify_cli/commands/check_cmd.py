"""check 命令 - YAML 语法和 Dify DSL 结构校验"""

import sys
from pathlib import Path

import yaml


class CheckResult:
    """检查结果"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def add_error(self, message: str, line: int = None):
        loc = f" (行 {line})" if line else ""
        self.errors.append(f"[ERROR]{loc} {message}")

    def add_warning(self, message: str, line: int = None):
        loc = f" (行 {line})" if line else ""
        self.warnings.append(f"[WARN]{loc} {message}")

    def add_info(self, message: str):
        self.info.append(f"[INFO] {message}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self):
        if self.info:
            for msg in self.info:
                print(msg)
            print()

        if self.errors:
            print("=" * 60)
            print("错误 (必须修复)")
            print("=" * 60)
            for msg in self.errors:
                print(f"  {msg}")
            print()

        if self.warnings:
            print("=" * 60)
            print("警告 (建议修复)")
            print("=" * 60)
            for msg in self.warnings:
                print(f"  {msg}")
            print()

        if self.is_valid:
            print("=" * 60)
            print(f"[OK] 校验通过! 错误: 0, 警告: {len(self.warnings)}")
            print("=" * 60)
        else:
            print("=" * 60)
            print(f"[ERROR] 校验失败! 错误: {len(self.errors)}, 警告: {len(self.warnings)}")
            print("=" * 60)


def check_yaml_syntax(content: str, result: CheckResult):
    """检查 YAML 语法"""
    try:
        yaml.safe_load(content)
        result.add_info("YAML 语法: 正确")
    except yaml.YAMLError as e:
        result.add_error(f"YAML 语法错误: {e}")
        return False
    return True


def check_dify_structure(data: dict, result: CheckResult):
    """检查 Dify DSL 结构"""
    # 1. 检查顶层必需字段
    required_top_fields = ["app", "kind", "version", "workflow"]
    for field in required_top_fields:
        if field not in data:
            result.add_error(f"缺少顶层字段: {field}")

    # 2. 检查 kind 字段
    if data.get("kind") != "app":
        result.add_error(f"kind 字段必须是 'app'，当前值: {data.get('kind')}")

    # 3. 检查 version 字段
    version = data.get("version")
    if version:
        result.add_info(f"DSL 版本: {version}")
    else:
        result.add_warning("缺少 version 字段")

    # 4. 检查 app 字段
    app = data.get("app", {})
    if app:
        if "name" not in app:
            result.add_error("app.name 缺失")
        else:
            result.add_info(f"应用名称: {app.get('name')}")

        if "mode" not in app:
            result.add_warning("app.mode 缺失")
        else:
            mode = app.get("mode")
            if mode not in ["workflow", "chatflow", "advanced-chat"]:
                result.add_warning(f"app.mode 值可能不正确: {mode}")

    # 5. 检查 workflow 字段
    workflow = data.get("workflow", {})
    if not workflow:
        result.add_error("workflow 字段为空")
        return

    # 6. 检查 graph 结构
    graph = workflow.get("graph", {})
    if not graph:
        result.add_error("workflow.graph 缺失")
        return

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if not nodes:
        result.add_error("workflow.graph.nodes 为空")
    else:
        result.add_info(f"节点数量: {len(nodes)}")

    if not edges:
        result.add_warning("workflow.graph.edges 为空（无连接）")
    else:
        result.add_info(f"连接数量: {len(edges)}")

    # 7. 检查节点结构
    node_ids = set()
    node_types = {}
    for i, node in enumerate(nodes):
        node_data = node.get("data", {})
        node_id = node.get("id")

        if not node_id:
            result.add_error(f"节点 #{i+1} 缺少 id")
            continue

        if node_id in node_ids:
            result.add_error(f"节点 ID 重复: {node_id}")
        node_ids.add(node_id)

        node_type = node_data.get("type")
        if not node_type:
            result.add_error(f"节点 {node_id} 缺少 type")
        else:
            node_types[node_id] = node_type

        title = node_data.get("title")
        if not title:
            result.add_warning(f"节点 {node_id} 缺少 title")

    # 8. 检查边结构
    for i, edge in enumerate(edges):
        edge_id = edge.get("id", f"edge-{i+1}")
        source = edge.get("source")
        target = edge.get("target")

        if not source:
            result.add_error(f"边 {edge_id} 缺少 source")
        elif source not in node_ids:
            result.add_error(f"边 {edge_id} 的 source 节点不存在: {source}")

        if not target:
            result.add_error(f"边 {edge_id} 缺少 target")
        elif target not in node_ids:
            result.add_error(f"边 {edge_id} 的 target 节点不存在: {target}")

        source_handle = edge.get("sourceHandle")
        if not source_handle:
            result.add_warning(f"边 {edge_id} 缺少 sourceHandle")

    # 9. 检查 start 和 end 节点（根据模式区分）
    has_start = any(node_types.get(nid) == "start" for nid in node_ids)
    has_end = any(node_types.get(nid) == "end" for nid in node_ids)
    has_answer = any(node_types.get(nid) == "answer" for nid in node_ids)

    mode = app.get("mode", "workflow")

    if not has_start:
        result.add_error("缺少 start 节点")

    # workflow 模式需要 end 节点
    if mode == "workflow":
        if not has_end:
            result.add_error("缺少 end 节点")
    # chatflow/advanced-chat 模式需要 answer 节点
    elif mode in ["advanced-chat", "chatflow"]:
        if not has_answer:
            result.add_warning("缺少 answer 节点（对话模式通常需要 answer 节点回复用户）")

    # 10. 统计节点类型
    type_counts = {}
    for ntype in node_types.values():
        type_counts[ntype] = type_counts.get(ntype, 0) + 1

    if type_counts:
        type_str = ", ".join(f"{k}: {v}" for k, v in sorted(type_counts.items()))
        result.add_info(f"节点类型分布: {type_str}")


def check_variable_references(data: dict, result: CheckResult):
    """检查变量引用"""
    # 收集所有可用变量
    available_vars = set()

    # 从 start 节点收集输入变量
    workflow = data.get("workflow", {})
    graph = workflow.get("graph", {})
    nodes = graph.get("nodes", [])

    for node in nodes:
        node_data = node.get("data", {})
        if node_data.get("type") == "start":
            for var in node_data.get("variables", []):
                var_name = var.get("variable")
                if var_name:
                    available_vars.add(var_name)

    # 从环境变量收集
    env_vars = workflow.get("environment_variables", [])
    for var in env_vars:
        var_name = var.get("name")
        if var_name:
            available_vars.add(f"env.{var_name}")

    if available_vars:
        result.add_info(f"可用变量: {', '.join(sorted(available_vars)[:10])}{'...' if len(available_vars) > 10 else ''}")


def cmd_check(args):
    """执行 check 子命令"""
    yml_path = Path(args.yml_path)

    if not yml_path.exists():
        print(f"[ERROR] 文件不存在: {yml_path}")
        sys.exit(1)

    print(f"[INFO] 检查文件: {yml_path}")
    print(f"[INFO] 文件大小: {yml_path.stat().st_size} bytes")
    print()

    result = CheckResult()

    # 读取文件
    content = yml_path.read_text(encoding="utf-8")

    # 1. YAML 语法检查
    if not check_yaml_syntax(content, result):
        result.print_report()
        sys.exit(1)

    # 解析 YAML
    data = yaml.safe_load(content)

    if not isinstance(data, dict):
        result.add_error("YAML 根节点必须是对象")
        result.print_report()
        sys.exit(1)

    # 2. Dify DSL 结构检查
    check_dify_structure(data, result)

    # 3. 变量引用检查
    check_variable_references(data, result)

    # 输出报告
    print()
    result.print_report()

    # 返回退出码
    if not result.is_valid:
        sys.exit(1)

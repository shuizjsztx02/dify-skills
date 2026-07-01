"""diff 命令 - 对比本地 YML 与远程 Dify 应用的差异"""

import sys
from pathlib import Path

import requests
import yaml

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping
from ..utils import extract_app_id, extract_base_url, is_url
from .export_cmd import export_yml


# 应用元数据对比字段（忽略 id 等不稳定字段）
_APP_FIELDS = ["name", "description", "mode", "icon", "icon_background"]


def _index_nodes(nodes):
    """以 node id 为 key 索引节点"""
    result = {}
    for n in nodes or []:
        nid = n.get("id")
        if nid:
            result[nid] = n
    return result


def _edge_key(e):
    """构造边的唯一 key"""
    src = e.get("source", "")
    src_h = e.get("sourceHandle", "")
    tgt = e.get("target", "")
    tgt_h = e.get("targetHandle", "")
    return f"{src}:{src_h} -> {tgt}:{tgt_h}"


def _short(s, n=40):
    """截断字符串"""
    s = str(s) if s is not None else ""
    return s if len(s) <= n else s[:n] + "..."


def _diff_app(local_app, remote_app):
    """对比应用元数据，返回 (changes, unchanged_count)"""
    changes = []
    unchanged = 0
    for f in _APP_FIELDS:
        lv = local_app.get(f)
        rv = remote_app.get(f)
        if lv != rv:
            changes.append(("变更", f, lv, rv))
        else:
            unchanged += 1
    return changes, unchanged


def _diff_nodes(local_nodes, remote_nodes):
    """对比节点，返回变更列表"""
    local_idx = _index_nodes(local_nodes)
    remote_idx = _index_nodes(remote_nodes)
    changes = []

    # 新增 / 删除
    for nid in remote_idx:
        if nid not in local_idx:
            n = remote_idx[nid]
            changes.append(("新增节点", nid, n.get("data", {}).get("type", ""),
                            n.get("data", {}).get("title", "")))
    for nid in local_idx:
        if nid not in remote_idx:
            n = local_idx[nid]
            changes.append(("删除节点", nid, n.get("data", {}).get("type", ""),
                            n.get("data", {}).get("title", "")))

    # 修改
    for nid in local_idx:
        if nid in remote_idx:
            ln = local_idx[nid].get("data", {})
            rn = remote_idx[nid].get("data", {})
            if ln.get("title") != rn.get("title"):
                changes.append(("修改节点", nid, "标题",
                                f"{_short(ln.get('title'))} -> {_short(rn.get('title'))}"))
            if ln.get("type") != rn.get("type"):
                changes.append(("修改节点", nid, "类型",
                                f"{ln.get('type')} -> {rn.get('type')}"))
    return changes


def _diff_edges(local_edges, remote_edges):
    """对比边，返回 (added, removed)"""
    local_set = {_edge_key(e) for e in (local_edges or [])}
    remote_set = {_edge_key(e) for e in (remote_edges or [])}
    added = remote_set - local_set
    removed = local_set - remote_set
    return sorted(added), sorted(removed)


def _diff_var_list(local_vars, remote_vars, var_name):
    """对比变量列表（按 name 字段索引）"""
    local_names = {v.get("name") for v in (local_vars or []) if v.get("name")}
    remote_names = {v.get("name") for v in (remote_vars or []) if v.get("name")}
    added = remote_names - local_names
    removed = local_names - remote_names
    return sorted(added), sorted(removed)


def cmd_diff(args):
    """执行 diff 子命令"""
    yml_path = Path(args.yml_path)
    if not yml_path.exists():
        print(f"[ERROR] 文件不存在: {yml_path}")
        sys.exit(1)

    config = load_config()

    if is_url(args.dify_url):
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
        server_name = find_server_by_url(config, base_url)
        if not server_name:
            print(f"[ERROR] 未找到匹配的服务器配置: {base_url}")
            print("请先运行: dify init")
            sys.exit(1)
        print(f"[INFO] 匹配到服务器: {server_name}")
    else:
        result = lookup_mapping(args.dify_url)
        if not result:
            print(f"[ERROR] 未找到映射: {args.dify_url}")
            print(f"请使用完整 URL: dify diff <yml_path> <DIFY_URL>")
            sys.exit(1)
        server_name = result["server"]
        app_id = result["app_id"]
        _, server_config = get_server_config(config, server_name)
        base_url = server_config["base_url"]
        print(f"[INFO] 从映射中查找: {args.dify_url} -> {server_name}:{app_id}")

    if args.server:
        server_name, server_config = get_server_config(config, args.server)
        base_url = server_config["base_url"]
        print(f"[INFO] 使用指定服务器: {server_name}")

    _, server_config = get_server_config(config, server_name)
    base_url = server_config["base_url"]

    # 读取本地 YML
    print(f"[INFO] 读取本地: {yml_path}")
    try:
        local_text = yml_path.read_text(encoding="utf-8")
        local = yaml.safe_load(local_text)
    except yaml.YAMLError as e:
        print(f"[ERROR] 本地 YAML 解析失败: {e}")
        sys.exit(1)
    if not isinstance(local, dict):
        print("[ERROR] 本地 YML 结构异常（非对象）")
        sys.exit(1)

    print(f"[INFO] App ID: {app_id}")
    print(f"[INFO] 服务器: {server_name} ({base_url})")

    # 导出远程 YML
    session = requests.Session()
    login_with_server(session, server_config)
    print("[OK] 登录成功")
    print("[INFO] 正在导出远程应用...")
    remote_text = export_yml(session, base_url, app_id, include_secret=False)
    try:
        remote = yaml.safe_load(remote_text)
    except yaml.YAMLError as e:
        print(f"[ERROR] 远程 YAML 解析失败: {e}")
        sys.exit(1)
    if not isinstance(remote, dict):
        print("[ERROR] 远程 YML 结构异常（非对象）")
        sys.exit(1)

    local_app = local.get("app", {}) or {}
    remote_app = remote.get("app", {}) or {}
    local_wf = (local.get("workflow") or {}) if isinstance(local.get("workflow"), dict) else {}
    remote_wf = (remote.get("workflow") or {}) if isinstance(remote.get("workflow"), dict) else {}

    local_graph = local_wf.get("graph", {}) or {}
    remote_graph = remote_wf.get("graph", {}) or {}
    local_nodes = local_graph.get("nodes", []) or []
    remote_nodes = remote_graph.get("nodes", []) or []
    local_edges = local_graph.get("edges", []) or []
    remote_edges = remote_graph.get("edges", []) or []

    print()
    print("=" * 70)
    print(f"本地 vs 远程 差异对比")
    print(f"  本地: {_short(local_app.get('name', ''), 30)}  ({len(local_nodes)} 节点, {len(local_edges)} 连接)")
    print(f"  远程: {_short(remote_app.get('name', ''), 30)}  ({len(remote_nodes)} 节点, {len(remote_edges)} 连接)")
    print("=" * 70)

    total_changes = 0

    # 1. 应用元数据
    print("\n[应用元数据]")
    app_changes, app_unchanged = _diff_app(local_app, remote_app)
    if app_changes:
        for kind, field, lv, rv in app_changes:
            print(f"  [{kind}] {field}: {_short(lv)} -> {_short(rv)}")
            total_changes += 1
    else:
        print("  (无变更)")

    # 2. 节点
    print("\n[节点]")
    node_changes = _diff_nodes(local_nodes, remote_nodes)
    if node_changes:
        for c in node_changes:
            if c[0] in ("新增节点", "删除节点"):
                _, nid, ntype, title = c
                print(f"  [{c[0]}] {nid}  \"{_short(title)}\" ({ntype})")
            else:
                _, nid, field, val = c
                print(f"  [{c[0]}] {nid}  {field}: {val}")
            total_changes += 1
    else:
        print("  (无变更)")

    # 3. 连接
    print("\n[连接]")
    edge_added, edge_removed = _diff_edges(local_edges, remote_edges)
    if edge_added or edge_removed:
        for e in edge_added:
            print(f"  [新增连接] {e}")
            total_changes += 1
        for e in edge_removed:
            print(f"  [删除连接] {e}")
            total_changes += 1
    else:
        print("  (无变更)")

    # 4. 环境变量
    print("\n[环境变量]")
    ev_add, ev_rem = _diff_var_list(
        local_wf.get("environment_variables"), remote_wf.get("environment_variables"), "env")
    if ev_add or ev_rem:
        for v in ev_add:
            print(f"  [新增] {v}")
            total_changes += 1
        for v in ev_rem:
            print(f"  [删除] {v}")
            total_changes += 1
    else:
        print("  (无变更)")

    # 5. 会话变量
    print("\n[会话变量]")
    cv_add, cv_rem = _diff_var_list(
        local_wf.get("conversation_variables"), remote_wf.get("conversation_variables"), "conv")
    if cv_add or cv_rem:
        for v in cv_add:
            print(f"  [新增] {v}")
            total_changes += 1
        for v in cv_rem:
            print(f"  [删除] {v}")
            total_changes += 1
    else:
        print("  (无变更)")

    # 小结
    print()
    print("=" * 70)
    if total_changes == 0:
        print("[OK] 本地与远程一致，无差异")
    else:
        print(f"[INFO] 共发现 {total_changes} 处差异")
        print("提示: 节点内部参数的详细差异未展开，如需查看可使用 dify export 后手动对比")
    print("=" * 70)

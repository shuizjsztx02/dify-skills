"""logs 命令 - 查询 Dify 工作流执行日志"""

import sys
from datetime import datetime

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping
from ..utils import extract_app_id, extract_base_url, is_url


def format_ts(ts) -> str:
    """格式化时间戳"""
    if ts is None:
        return "N/A"
    if isinstance(ts, (int, float)) and ts > 1e9:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return str(ts)


_STATUS_LABEL = {
    "succeeded": "成功",
    "failed": "失败",
    "running": "运行中",
    "stopped": "已停止",
}


def cmd_logs(args):
    """执行 logs 子命令"""
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
            print(f"请使用完整 URL: dify logs <DIFY_URL>")
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

    session = requests.Session()
    login_with_server(session, server_config)
    print("[OK] 登录成功")

    # 应用信息
    resp = session.get(f"{base_url}/console/api/apps/{app_id}", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    app_info = resp.json()
    app_name = app_info.get("name", "")
    mode = app_info.get("mode", "")
    print(f"[INFO] 应用: {app_name}  (mode: {mode})")

    if mode != "workflow":
        print(f"[ERROR] logs 命令仅支持 workflow 类型应用（当前: {mode}）")
        print("chat/agent-chat 应用的日志请通过 Dify 控制台查看")
        sys.exit(1)

    # 查询执行日志
    limit = args.limit or 10
    params = {"limit": limit}
    if args.status:
        params["status"] = args.status

    resp = session.get(
        f"{base_url}/console/api/apps/{app_id}/workflow-runs",
        params=params,
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 查询执行日志失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    data = resp.json()
    runs = data.get("data", []) or []
    has_more = data.get("has_more", False)

    print()
    print("=" * 70)
    status_filter = f"，状态={args.status}" if args.status else ""
    total_label = f"{len(runs)}{'+' if has_more else ''}"
    print(f"执行日志 (本页 {len(runs)} 条{status_filter}，共 {total_label} 条)")
    print("=" * 70)

    if not runs:
        print("(无执行记录)")
        print("=" * 70)
        return

    # 统计
    total_tokens = 0
    total_elapsed = 0.0
    fail_count = 0
    for r in runs:
        try:
            total_tokens += int(r.get("total_tokens") or 0)
        except (TypeError, ValueError):
            pass
        try:
            total_elapsed += float(r.get("elapsed_time") or 0)
        except (TypeError, ValueError):
            pass
        if r.get("status") == "failed":
            fail_count += 1

    for i, r in enumerate(runs, 1):
        status = r.get("status", "")
        label = _STATUS_LABEL.get(status, status)
        elapsed = r.get("elapsed_time", 0)
        tokens = r.get("total_tokens", 0)
        steps = r.get("total_steps", 0)
        ver = r.get("version", "")
        ver_label = "草稿" if ver == "draft" else ver
        created = format_ts(r.get("created_at"))
        account = r.get("created_by_account") or {}
        user = account.get("name", "N/A")
        exc = r.get("exceptions_count", 0)

        mark = "[失败]" if status == "failed" else "     "
        print(f"\n[{i:2}] {mark} {created}  {label}")
        print(f"       耗时 {elapsed}s · Tokens {tokens} · 步骤 {steps} · 异常 {exc}")
        print(f"       版本 {ver_label} · 触发 {user}")

    avg_tokens = total_tokens // len(runs) if runs else 0
    print()
    print("=" * 70)
    print(f"汇总: 共 {len(runs)} 条 (失败 {fail_count}) | 总耗时 {total_elapsed:.1f}s | "
          f"总 Tokens {total_tokens} | 平均 {avg_tokens}")
    print("=" * 70)

"""versions 命令 - 查询工作流版本历史"""

import sys
from datetime import datetime

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping
from ..utils import extract_app_id, extract_base_url, is_url


def format_ts(ts) -> str:
    """将 timestamp（int/float/str）格式化为 YYYY-MM-DD HH:MM"""
    if ts is None:
        return "N/A"
    if isinstance(ts, (int, float)) and ts > 1e9:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    return str(ts)


def cmd_versions(args):
    """执行 versions 子命令"""
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
            print(f"请使用完整 URL: dify versions <DIFY_URL>")
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

    limit = args.limit if args.limit else 10

    session = requests.Session()
    login_with_server(session, server_config)
    print("[OK] 登录成功")

    # 应用信息（取应用名称和模式）
    resp = session.get(f"{base_url}/console/api/apps/{app_id}", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    app_info = resp.json()
    app_name = app_info.get("name", "")
    mode = app_info.get("mode", "")

    # 版本列表
    resp = session.get(
        f"{base_url}/console/api/apps/{app_id}/workflows",
        params={"limit": limit},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 获取版本历史失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    data = resp.json()
    items = data.get("items", [])

    print()
    print(f"[INFO] 应用: {app_name}  (mode: {mode})")
    print("=" * 70)
    total_display = data.get("total", len(items))
    if data.get("has_more") and total_display == len(items):
        total_display = f"{total_display}+"
    print(f"版本历史 (最新 {len(items)} 条，共 {total_display} 条)")
    print("=" * 70)

    if not items:
        print("\n[INFO] 暂无版本记录")
        return

    for i, v in enumerate(items, 1):
        # 标注：第 1 条是草稿，第 2 条是最新发布
        if v.get("version") == "draft":
            tag = "[当前草稿]"
        elif i == 2:
            tag = "[最新发布]"
        else:
            tag = ""

        marked_name = v.get("marked_name") or ""
        marked_comment = v.get("marked_comment") or ""
        created_at = format_ts(v.get("created_at"))
        publisher = v.get("created_by", {}) or {}
        publisher_name = publisher.get("name", "N/A")

        display_name = marked_name if marked_name else "(未命名)"
        display_comment = marked_comment if marked_comment else "(无)"

        print(f"\n[{i:2d}] {tag} {created_at} · {publisher_name}")
        print(f"     版本名: {display_name}")
        print(f"     说  明: {display_comment}")

    print()
    print("=" * 70)

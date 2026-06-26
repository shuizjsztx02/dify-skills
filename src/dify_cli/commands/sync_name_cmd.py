"""sync-name 命令 - 同步 Web App 名称"""

import sys

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping
from ..utils import extract_app_id, extract_base_url, is_url


def cmd_sync_name(args):
    """执行 sync-name 子命令"""
    config = load_config()

    server_name = None
    base_url = None
    app_id = None

    if is_url(args.dify_url):
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
        server_name = find_server_by_url(config, base_url)
        if not server_name:
            print(f"[ERROR] 未找到匹配的服务器配置: {base_url}")
            sys.exit(1)
        print(f"[INFO] 匹配到服务器: {server_name}")
    else:
        result = lookup_mapping(args.dify_url)
        if not result:
            print(f"[ERROR] 未找到映射: {args.dify_url}")
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

    print("\n[INFO] 检查 Web App 名称是否与应用名称一致...")

    resp = session.get(f"{base_url}/console/api/apps/{app_id}", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        sys.exit(1)

    app_info = resp.json()
    app_name = app_info.get("name", "")
    print(f"[INFO] 应用名称: {app_name}")

    site_config = app_info.get("site", {})
    if not site_config:
        print(f"[ERROR] 应用信息中未找到 site 配置")
        sys.exit(1)

    site_title = site_config.get("title", "")
    print(f"[INFO] Web App 名称: {site_title}")

    if app_name == site_title:
        print("[OK] Web App 名称已与应用名称一致，无需更新")
        return

    print(f"[INFO] Web App 名称与应用名称不一致，正在更新...")
    site_config["title"] = app_name
    resp = session.post(f"{base_url}/console/api/apps/{app_id}/site", json=site_config, timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 更新 Web App 名称失败: HTTP {resp.status_code}")
        sys.exit(1)

    print(f"[OK] Web App 名称已更新为: {app_name}")

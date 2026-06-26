"""deploy 命令 - 部署 YAML 到 Dify"""

import sys
from pathlib import Path

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping, save_to_mapping
from ..utils import extract_app_id, extract_base_url, is_url


def import_yml(session: requests.Session, base_url: str, app_id: str, yaml_content: str):
    """导入 YML 到指定 app"""
    resp = session.post(
        f"{base_url}/console/api/apps/imports",
        json={"app_id": app_id, "yaml_content": yaml_content, "mode": "yaml-content"},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 导入失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    result = resp.json()
    status = result.get("status", "")
    if status == "failed":
        print(f"[ERROR] 导入失败: {result.get('error', 'unknown')}")
        sys.exit(1)
    print(f"[OK] 导入成功: status={status}, app_mode={result.get('app_mode')}")


def publish(session: requests.Session, base_url: str, app_id: str, version_name: str | None = None):
    """发布 app"""
    body = {}
    if version_name:
        body["version_name"] = version_name
    resp = session.post(
        f"{base_url}/console/api/apps/{app_id}/workflows/publish",
        json=body,
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 发布失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    print(f"[OK] 发布成功: {resp.json()}")


def sync_name(session: requests.Session, base_url: str, app_id: str) -> bool:
    """同步 Web App 名称到应用名称"""
    print("\n[INFO] 检查 Web App 名称是否与应用名称一致...")

    resp = session.get(f"{base_url}/console/api/apps/{app_id}", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        return False

    app_info = resp.json()
    app_name = app_info.get("name", "")
    print(f"[INFO] 应用名称: {app_name}")

    site_config = app_info.get("site", {})
    if not site_config:
        print(f"[ERROR] 应用信息中未找到 site 配置")
        return False

    site_title = site_config.get("title", "")
    print(f"[INFO] Web App 名称: {site_title}")

    if app_name == site_title:
        print("[OK] Web App 名称已与应用名称一致，无需更新")
        return True

    print(f"[INFO] Web App 名称与应用名称不一致，正在更新...")
    site_config["title"] = app_name
    resp = session.post(f"{base_url}/console/api/apps/{app_id}/site", json=site_config, timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 更新 Web App 名称失败: HTTP {resp.status_code}")
        return False

    print(f"[OK] Web App 名称已更新为: {app_name}")
    return True


def cmd_deploy(args):
    """执行 deploy 子命令"""
    config = load_config()
    yml_path = Path(args.yml_path)

    server_name = None
    base_url = None
    app_id = None

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
            print(f"请先使用完整 URL 进行部署: dify deploy {args.yml_path} <DIFY_URL>")
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

    if not yml_path.exists():
        print(f"[ERROR] YML 文件不存在: {yml_path}")
        sys.exit(1)
    yaml_content = yml_path.read_text(encoding="utf-8")
    print(f"[INFO] 读取 YML: {yml_path} ({len(yaml_content)} chars)")
    print(f"[INFO] App ID: {app_id}")
    print(f"[INFO] 服务器: {server_name} ({base_url})")
    if args.version:
        print(f"[INFO] 版本名称: {args.version}")

    session = requests.Session()
    login_with_server(session, server_config)
    print("[OK] 登录成功")

    import_yml(session, base_url, app_id, yaml_content)
    publish(session, base_url, app_id, args.version)
    sync_name(session, base_url, app_id)

    if is_url(args.dify_url):
        save_to_mapping(str(yml_path), server_name, app_id)

    print(f"\n{'=' * 50}")
    print(f"部署完成! server={server_name}  app_id={app_id}" + (f"  version={args.version}" if args.version else ""))

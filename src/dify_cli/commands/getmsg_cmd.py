"""get-msg 命令 - 查询 Dify 应用的 app-id / Web App 链接 / API Key（无则创建）"""

import sys

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping
from ..utils import extract_app_id, extract_base_url, is_url


# app mode -> Web App 公开访问路径（用 site.code 拼接）
_WEBAPP_PATH = {
    "workflow": "workflow",
    "completion": "completion",
    "chat": "chat",
    "agent-chat": "chat",
    "advanced-chat": "chat",
}


def build_webapp_url(app_info: dict) -> str:
    """根据 app 信息构造 Web App 公开访问 URL"""
    site = app_info.get("site", {}) or {}
    app_base_url = (site.get("app_base_url") or "").rstrip("/")
    code = site.get("code") or site.get("access_token") or ""
    if not app_base_url or not code:
        return ""
    mode = app_info.get("mode", "")
    path = _WEBAPP_PATH.get(mode, "chat")
    return f"{app_base_url}/{path}/{code}"


def list_api_keys(session: requests.Session, base_url: str, app_id: str) -> list[dict]:
    """获取应用的所有 API Key"""
    resp = session.get(f"{base_url}/console/api/apps/{app_id}/api-keys", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取 API Key 失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    return resp.json().get("data", []) or []


def create_api_key(session: requests.Session, base_url: str, app_id: str) -> dict:
    """创建一个新的 API Key"""
    resp = session.post(
        f"{base_url}/console/api/apps/{app_id}/api-keys",
        json={"name": "cli-getmsg-key"},
        timeout=15,
    )
    if resp.status_code != 201:
        print(f"[ERROR] 创建 API Key 失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    return resp.json()


def cmd_getmsg(args):
    """执行 get-msg 子命令"""
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
            print(f"请使用完整 URL: dify get-msg <DIFY_URL>")
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

    # 1. 应用信息
    resp = session.get(f"{base_url}/console/api/apps/{app_id}", timeout=15)
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    app_info = resp.json()
    app_name = app_info.get("name", "")
    mode = app_info.get("mode", "")

    # 2. API Key（无则创建）
    api_keys = list_api_keys(session, base_url, app_id)
    created = False
    if not api_keys:
        print("[INFO] 当前无 API Key，正在创建...")
        new_key = create_api_key(session, base_url, app_id)
        api_keys = [new_key]
        created = True

    # 3. Web App 链接
    webapp_url = build_webapp_url(app_info)

    # 输出
    print()
    print("=" * 60)
    print(f"[OK] 应用名称: {app_name}  (mode: {mode})")
    print(f"[OK] App ID:  {app_id}")
    print(f"[OK] Web App: {webapp_url}")
    if len(api_keys) == 1:
        tag = "新建" if created else "已存在"
        print(f"[OK] API Key: {api_keys[0].get('token', 'N/A')}  ({tag})")
    else:
        print(f"[OK] API Key: 共 {len(api_keys)} 个")
        for i, k in enumerate(api_keys, 1):
            print(f"           {i}. {k.get('token', 'N/A')}")
    print("=" * 60)

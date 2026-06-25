"""Dify YML 导入/导出工具

用法:
    # 部署: 导入本地 YML 到 Dify 并发布
    python dify_deploy.py deploy <yml_path> <dify_url> [--version VERSION_NAME]

    # 导出: 从 Dify 导出 YML 到本地
    python dify_deploy.py export <dify_url> --output <output_path> [--force] [--include-secret]
"""

import argparse
import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 修复 Windows 终端中文输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests


def load_config():
    """加载配置, 优先 dify_deploy_config.json"""
    config_path = Path(__file__).resolve().parent / "dify_deploy_config.json"
    if not config_path.exists():
        print(f"[ERROR] 配置文件不存在: {config_path}")
        print("请复制 dify_deploy_config.example.json 为 dify_deploy_config.json 并填入你的 Dify 域名、邮箱和密码")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_mapping() -> dict:
    """加载映射文件, 不存在则返回空 dict"""
    mapping_path = Path(__file__).resolve().parent / "dify_app_mapping.json"
    if not mapping_path.exists():
        return {}
    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_mapping(mapping: dict):
    """保存映射到文件"""
    mapping_path = Path(__file__).resolve().parent / "dify_app_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def lookup_mapping(yml_path: str) -> tuple[str, str] | None:
    """根据文件名查找映射, 返回 (base_url, app_id) 或 None"""
    mapping = load_mapping()
    # 尝试精确匹配
    if yml_path in mapping:
        entry = mapping[yml_path]
        return entry["base_url"], entry["app_id"]
    # 尝试匹配文件名 (不含路径)
    yml_name = Path(yml_path).name
    if yml_name in mapping:
        entry = mapping[yml_name]
        return entry["base_url"], entry["app_id"]
    return None


def save_to_mapping(yml_path: str, base_url: str, app_id: str):
    """保存或更新映射关系"""
    mapping = load_mapping()
    # 使用文件名作为 key (不含路径)
    yml_name = Path(yml_path).name
    mapping[yml_name] = {
        "base_url": base_url,
        "app_id": app_id,
        "last_used": datetime.now().isoformat(timespec="seconds")
    }
    save_mapping(mapping)
    print(f"[OK] 已保存映射: {yml_name} -> {app_id}")


def is_url(s: str) -> bool:
    """判断字符串是否是 URL (包含 /app/ 或 UUID)"""
    return "/app/" in s or re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s) is not None


def extract_app_id(url: str) -> str:
    """从 Dify URL 中提取 app_id (UUID)"""
    match = re.search(
        r"/app/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        url,
    )
    if not match:
        # 尝试直接匹配 UUID
        match = re.search(
            r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
            url,
        )
    if not match:
        print(f"[ERROR] 无法从 URL 中提取 app_id: {url}")
        print("期望格式: https://your-domain.com/app/<APP_UUID>/workflow")
        sys.exit(1)
    return match.group(1)


def extract_base_url(url: str) -> str:
    """从 URL 中提取 base URL (scheme + host)"""
    m = re.match(r"(https?://[^/]+)", url)
    if not m:
        print(f"[ERROR] 无法解析 base URL: {url}")
        sys.exit(1)
    return m.group(1)


def login(session: requests.Session, base_url: str, email: str, password: str):
    """登录获取 session cookie (access_token + csrf_token)"""
    # Dify v1.11+ 要求密码 Base64 编码
    encoded_password = base64.b64encode(password.encode()).decode()
    resp = session.post(
        f"{base_url}/console/api/login",
        json={"email": email, "password": encoded_password},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 登录失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    # 验证 cookie 中是否有 access_token
    if "access_token" not in session.cookies:
        # 也检查 JSON body (旧版本可能返回在 body 中)
        data = resp.json().get("data", {})
        token = data.get("access_token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"[ERROR] 登录响应中未找到 access_token")
            sys.exit(1)
    # 设置 csrf_token header (如果存在)
    csrf = session.cookies.get("csrf_token")
    if csrf:
        session.headers.update({"X-CSRF-Token": csrf})


# ===================== deploy 子命令 =====================

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


def cmd_deploy(args):
    """执行 deploy 子命令: 导入 YML + 发布"""
    config = load_config()
    yml_path = Path(args.yml_path)

    # 判断 dify_url 是 URL 还是文件名
    if is_url(args.dify_url):
        # 完整 URL 模式
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
    else:
        # 文件名模式，从映射中查找
        result = lookup_mapping(args.dify_url)
        if not result:
            print(f"[ERROR] 未找到映射: {args.dify_url}")
            print(f"请先使用完整 URL 进行部署: python dify_deploy.py deploy {args.yml_path} <DIFY_URL>")
            print(f"例如: python dify_deploy.py deploy {args.yml_path} https://dify.example.com/app/<UUID>/workflow")
            sys.exit(1)
        base_url, app_id = result
        print(f"[INFO] 从映射中查找: {args.dify_url} -> {app_id}")

    if not yml_path.exists():
        print(f"[ERROR] YML 文件不存在: {yml_path}")
        sys.exit(1)
    yaml_content = yml_path.read_text(encoding="utf-8")
    print(f"[INFO] 读取 YML: {yml_path} ({len(yaml_content)} chars)")
    print(f"[INFO] App ID: {app_id}")
    if args.version:
        print(f"[INFO] 版本名称: {args.version}")

    session = requests.Session()
    login(session, base_url, config["email"], config["password"])
    print("[OK] 登录成功")

    import_yml(session, base_url, app_id, yaml_content)
    publish(session, base_url, app_id, args.version)

    # 自动同步 Web App 名称
    sync_name(session, base_url, app_id)

    # 如果是完整 URL 模式，保存到映射
    if is_url(args.dify_url):
        save_to_mapping(str(yml_path), base_url, app_id)

    print(f"\n{'='*50}")
    print(f"部署完成! app_id={app_id}" + (f"  version={args.version}" if args.version else ""))


# ===================== export 子命令 =====================

def export_yml(session: requests.Session, base_url: str, app_id: str, include_secret: bool) -> str:
    """从 Dify 导出 YML 内容"""
    params = {"include_secret": "true" if include_secret else "false"}
    resp = session.get(
        f"{base_url}/console/api/apps/{app_id}/export",
        params=params,
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 导出失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    data = resp.json()
    yaml_content = data.get("data")
    if not yaml_content or not isinstance(yaml_content, str):
        print(f"[ERROR] 导出响应格式异常: {json.dumps(data, ensure_ascii=False)[:300]}")
        sys.exit(1)
    return yaml_content


def cmd_export(args):
    """执行 export 子命令: 从 Dify 导出 YML 到本地"""
    config = load_config()

    # 判断 dify_url 是 URL 还是文件名
    if is_url(args.dify_url):
        # 完整 URL 模式
        if not args.output:
            print("[ERROR] 使用完整 URL 时，必须指定 --output 参数")
            sys.exit(1)
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
        output_path = Path(args.output)
    else:
        # 文件名模式，从映射中查找
        result = lookup_mapping(args.dify_url)
        if not result:
            print(f"[ERROR] 未找到映射: {args.dify_url}")
            print(f"请先使用完整 URL 进行导出: python dify_deploy.py export <DIFY_URL> --output {args.dify_url}")
            print(f"例如: python dify_deploy.py export https://dify.example.com/app/<UUID>/workflow --output {args.dify_url}")
            sys.exit(1)
        base_url, app_id = result
        output_path = Path(args.dify_url)
        print(f"[INFO] 从映射中查找: {args.dify_url} -> {app_id}")

    if output_path.exists() and not args.force:
        print(f"[ERROR] 目标文件已存在: {output_path}")
        print("如需覆盖，请添加 --force 参数")
        sys.exit(1)

    print(f"[INFO] App ID: {app_id}")
    print(f"[INFO] 导出到: {output_path}")
    if args.force and output_path.exists():
        print(f"[INFO] 将覆盖已有文件")

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    login(session, base_url, config["email"], config["password"])
    print("[OK] 登录成功")

    yaml_content = export_yml(session, base_url, app_id, args.include_secret)
    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"[OK] 导出成功: {output_path} ({len(yaml_content)} chars)")

    # 如果是完整 URL 模式，保存到映射
    if is_url(args.dify_url):
        save_to_mapping(str(output_path), base_url, app_id)

    print(f"\n{'='*50}")
    print(f"导出完成! app_id={app_id}  output={output_path}")


# ===================== list 子命令 =====================

def cmd_list(args):
    """执行 list 子命令: 列出所有映射关系"""
    mapping = load_mapping()
    if not mapping:
        print("[INFO] 当前没有映射关系")
        return

    print(f"[INFO] 共 {len(mapping)} 个映射:")
    print("-" * 80)
    for yml_name, info in sorted(mapping.items()):
        print(f"{yml_name}")
        print(f"  base_url: {info['base_url']}")
        print(f"  app_id:   {info['app_id']}")
        print(f"  last_used: {info.get('last_used', 'N/A')}")
        print()


# ===================== unbind 子命令 =====================

def cmd_unbind(args):
    """执行 unbind 子命令: 删除映射关系"""
    mapping = load_mapping()
    yml_name = Path(args.yml_path).name

    if yml_name not in mapping:
        # 尝试精确匹配
        if args.yml_path in mapping:
            yml_name = args.yml_path
        else:
            print(f"[ERROR] 未找到映射: {args.yml_path}")
            sys.exit(1)

    del mapping[yml_name]
    save_mapping(mapping)
    print(f"[OK] 已删除映射: {yml_name}")


# ===================== sync-name 子命令 =====================

def get_app_info(session: requests.Session, base_url: str, app_id: str) -> dict:
    """获取应用信息"""
    resp = session.get(
        f"{base_url}/console/api/apps/{app_id}",
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 获取应用信息失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    return resp.json()


def get_site_config(session: requests.Session, base_url: str, app_id: str) -> dict:
    """获取 Web App 配置 (site 配置) - 从应用信息中获取"""
    app_info = get_app_info(session, base_url, app_id)
    site_config = app_info.get("site", {})
    if not site_config:
        print(f"[ERROR] 应用信息中未找到 site 配置")
        sys.exit(1)
    return site_config


def update_site_name(session: requests.Session, base_url: str, app_id: str, site_config: dict, new_name: str) -> bool:
    """更新 Web App 名称"""
    # 更新 site 配置中的 title 字段
    site_config["title"] = new_name
    resp = session.post(
        f"{base_url}/console/api/apps/{app_id}/site",
        json=site_config,
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 更新 Web App 名称失败: HTTP {resp.status_code}")
        print(resp.text)
        return False
    return True


def sync_name(session: requests.Session, base_url: str, app_id: str) -> bool:
    """同步 Web App 名称到应用名称"""
    print("\n[INFO] 检查 Web App 名称是否与应用名称一致...")

    # 获取应用信息
    app_info = get_app_info(session, base_url, app_id)
    app_name = app_info.get("name", "")
    print(f"[INFO] 应用名称: {app_name}")

    # 获取 Web App 配置
    site_config = get_site_config(session, base_url, app_id)
    site_title = site_config.get("title", "")
    print(f"[INFO] Web App 名称: {site_title}")

    # 检查是否一致
    if app_name == site_title:
        print("[OK] Web App 名称已与应用名称一致，无需更新")
        return True

    # 不一致，更新 Web App 名称
    print(f"[INFO] Web App 名称与应用名称不一致，正在更新...")
    if update_site_name(session, base_url, app_id, site_config, app_name):
        print(f"[OK] Web App 名称已更新为: {app_name}")
        return True
    else:
        print("[ERROR] Web App 名称更新失败")
        return False


def cmd_sync_name(args):
    """执行 sync-name 子命令: 同步 Web App 名称"""
    config = load_config()

    # 判断 dify_url 是 URL 还是文件名
    if is_url(args.dify_url):
        # 完整 URL 模式
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
    else:
        # 文件名模式，从映射中查找
        result = lookup_mapping(args.dify_url)
        if not result:
            print(f"[ERROR] 未找到映射: {args.dify_url}")
            print(f"请先使用完整 URL: python dify_deploy.py sync-name <DIFY_URL>")
            sys.exit(1)
        base_url, app_id = result
        print(f"[INFO] 从映射中查找: {args.dify_url} -> {app_id}")

    session = requests.Session()
    login(session, base_url, config["email"], config["password"])
    print("[OK] 登录成功")

    sync_name(session, base_url, app_id)


# ===================== 入口 =====================

def main():
    parser = argparse.ArgumentParser(description="Dify YML 导入/导出工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_deploy = sub.add_parser("deploy", help="导入本地 YML 到 Dify 并发布")
    p_deploy.add_argument("yml_path", help="本地 YML 文件路径")
    p_deploy.add_argument("dify_url", help="Dify 智能体 URL (含 app UUID) 或已映射的文件名")
    p_deploy.add_argument("--version", "-v", default=None, help="版本名称 (可选)")
    p_deploy.set_defaults(func=cmd_deploy)

    p_export = sub.add_parser("export", help="从 Dify 导出 YML 到本地")
    p_export.add_argument("dify_url", help="Dify 智能体 URL (含 app UUID) 或已映射的文件名")
    p_export.add_argument("--output", "-o", default=None, help="本地保存路径 (当 dify_url 为 URL 时必填)")
    p_export.add_argument("--force", "-f", action="store_true", help="覆盖已存在的文件")
    p_export.add_argument("--include-secret", action="store_true", default=True,
                          help="导出包含密钥的环境变量 (默认 true)")
    p_export.add_argument("--no-secret", dest="include_secret", action="store_false",
                          help="导出时不包含密钥环境变量")
    p_export.set_defaults(func=cmd_export)

    p_list = sub.add_parser("list", help="列出所有映射关系")
    p_list.set_defaults(func=cmd_list)

    p_unbind = sub.add_parser("unbind", help="删除映射关系")
    p_unbind.add_argument("yml_path", help="要删除映射的 YML 文件路径或文件名")
    p_unbind.set_defaults(func=cmd_unbind)

    p_sync = sub.add_parser("sync-name", help="同步 Web App 名称到应用名称")
    p_sync.add_argument("dify_url", help="Dify 智能体 URL (含 app UUID) 或已映射的文件名")
    p_sync.set_defaults(func=cmd_sync_name)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

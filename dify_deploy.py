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
    base_url = extract_base_url(args.dify_url)
    app_id = extract_app_id(args.dify_url)

    yml_path = Path(args.yml_path)
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
    base_url = extract_base_url(args.dify_url)
    app_id = extract_app_id(args.dify_url)

    output_path = Path(args.output)
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

    print(f"\n{'='*50}")
    print(f"导出完成! app_id={app_id}  output={output_path}")


# ===================== 入口 =====================

def main():
    parser = argparse.ArgumentParser(description="Dify YML 导入/导出工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_deploy = sub.add_parser("deploy", help="导入本地 YML 到 Dify 并发布")
    p_deploy.add_argument("yml_path", help="本地 YML 文件路径")
    p_deploy.add_argument("dify_url", help="Dify 智能体 URL (含 app UUID)")
    p_deploy.add_argument("--version", "-v", default=None, help="版本名称 (可选)")
    p_deploy.set_defaults(func=cmd_deploy)

    p_export = sub.add_parser("export", help="从 Dify 导出 YML 到本地")
    p_export.add_argument("dify_url", help="Dify 智能体 URL (含 app UUID)")
    p_export.add_argument("--output", "-o", required=True, help="本地保存路径")
    p_export.add_argument("--force", "-f", action="store_true", help="覆盖已存在的文件")
    p_export.add_argument("--include-secret", action="store_true", default=True,
                          help="导出包含密钥的环境变量 (默认 true)")
    p_export.add_argument("--no-secret", dest="include_secret", action="store_false",
                          help="导出时不包含密钥环境变量")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

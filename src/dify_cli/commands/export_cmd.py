"""export 命令 - 从 Dify 导出 YAML"""

import json
import sys
from pathlib import Path

import requests

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..mapping import lookup_mapping, save_to_mapping
from ..utils import extract_app_id, extract_base_url, is_url


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
    """执行 export 子命令"""
    config = load_config()

    server_name = None
    base_url = None
    app_id = None

    if is_url(args.dify_url):
        if not args.output:
            print("[ERROR] 使用完整 URL 时，必须指定 --output 参数")
            sys.exit(1)
        base_url = extract_base_url(args.dify_url)
        app_id = extract_app_id(args.dify_url)
        output_path = Path(args.output)
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
            print(f"请先使用完整 URL 进行导出: dify export <DIFY_URL> --output {args.dify_url}")
            sys.exit(1)
        server_name = result["server"]
        app_id = result["app_id"]
        _, server_config = get_server_config(config, server_name)
        base_url = server_config["base_url"]
        output_path = Path(args.dify_url)
        print(f"[INFO] 从映射中查找: {args.dify_url} -> {server_name}:{app_id}")

    if args.server:
        server_name, server_config = get_server_config(config, args.server)
        base_url = server_config["base_url"]
        print(f"[INFO] 使用指定服务器: {server_name}")

    _, server_config = get_server_config(config, server_name)
    base_url = server_config["base_url"]

    if output_path.exists() and not args.force:
        print(f"[ERROR] 目标文件已存在: {output_path}")
        print("如需覆盖，请添加 --force 参数")
        sys.exit(1)

    print(f"[INFO] App ID: {app_id}")
    print(f"[INFO] 导出到: {output_path}")
    print(f"[INFO] 服务器: {server_name} ({base_url})")
    if args.force and output_path.exists():
        print(f"[INFO] 将覆盖已有文件")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    login_with_server(session, server_config)
    print("[OK] 登录成功")

    yaml_content = export_yml(session, base_url, app_id, args.include_secret)
    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"[OK] 导出成功: {output_path} ({len(yaml_content)} chars)")

    if is_url(args.dify_url):
        save_to_mapping(str(output_path), server_name, app_id)

    print(f"\n{'=' * 50}")
    print(f"导出完成! server={server_name}  app_id={app_id}  output={output_path}")

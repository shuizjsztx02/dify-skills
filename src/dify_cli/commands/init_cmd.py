"""init 命令 - 交互式配置服务器"""

import json
import sys

from ..config import get_config_path, load_config, save_config
from ..utils import install_claude_commands


def cmd_init(args):
    """交互式初始化配置"""
    config_path = get_config_path()

    # 安装 Claude Code commands 到全局目录
    print("\n[INFO] 安装 Claude Code slash commands...")
    install_claude_commands()

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"[INFO] 加载现有配置: {config_path}")
    else:
        config = {"servers": {}, "default_server": None}
        print(f"[INFO] 创建新配置: {config_path}")

    servers = config.get("servers", {})

    while True:
        print("\n" + "=" * 50)
        print("添加 Dify 服务器")
        print("=" * 50)

        while True:
            name = input("服务器名称（如 work, personal）: ").strip()
            if not name:
                print("[ERROR] 名称不能为空")
            elif name in servers and not args.force:
                print(f"[ERROR] 服务器 '{name}' 已存在，使用 --force 覆盖或使用其他名称")
            else:
                break

        while True:
            base_url = input("Dify URL（如 https://dify.example.com）: ").strip()
            if not base_url:
                print("[ERROR] URL 不能为空")
            elif not base_url.startswith("http"):
                print("[ERROR] URL 必须以 http:// 或 https:// 开头")
            else:
                base_url = base_url.rstrip("/")
                break

        email = input("登录邮箱: ").strip()
        if not email:
            print("[ERROR] 邮箱不能为空")
            continue

        password = input("登录密码: ").strip()
        if not password:
            print("[ERROR] 密码不能为空")
            continue

        servers[name] = {
            "base_url": base_url,
            "email": email,
            "password": password
        }
        print(f"[OK] 已添加服务器: {name}")

        if not config.get("default_server") or len(servers) == 1:
            config["default_server"] = name
            print(f"[OK] 已设为默认服务器: {name}")
        else:
            set_default = input(f"是否设为默认服务器？(y/N, 当前默认: {config.get('default_server')}): ").strip().lower()
            if set_default == 'y':
                config["default_server"] = name
                print(f"[OK] 已设为默认服务器: {name}")

        config["servers"] = servers

        cont = input("\n是否继续添加其他服务器？(y/N): ").strip().lower()
        if cont != 'y':
            break

    save_config(config)
    print(f"\n{'=' * 50}")
    print(f"[OK] 配置已保存到: {config_path}")
    print(f"[INFO] 共配置 {len(servers)} 个服务器")

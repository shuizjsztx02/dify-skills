"""servers 命令 - 管理服务器列表"""

import sys

from ..config import list_servers, load_config, save_config


def cmd_servers(args):
    """管理服务器列表"""
    config = load_config()
    servers = list_servers(config)

    if args.set_default:
        name = args.set_default
        if name not in config.get("servers", {}):
            print(f"[ERROR] 未找到服务器: {name}")
            sys.exit(1)
        config["default_server"] = name
        save_config(config)
        print(f"[OK] 已设置默认服务器: {name}")

    if args.remove:
        name = args.remove
        if name not in config.get("servers", {}):
            print(f"[ERROR] 未找到服务器: {name}")
            sys.exit(1)
        if config.get("default_server") == name:
            print(f"[ERROR] 不能删除默认服务器: {name}")
            print("请先设置其他服务器为默认: dify servers --set-default <name>")
            sys.exit(1)
        del config["servers"][name]
        save_config(config)
        print(f"[OK] 已删除服务器: {name}")

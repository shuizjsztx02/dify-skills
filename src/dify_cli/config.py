"""配置管理模块"""

import json
import sys
from pathlib import Path


def get_dify_dir() -> Path:
    """获取全局配置目录 ~/.dify/"""
    home = Path.home()
    dify_dir = home / ".dify"
    dify_dir.mkdir(exist_ok=True)
    return dify_dir


def get_config_path() -> Path:
    """获取配置文件路径"""
    return get_dify_dir() / "config.json"


def get_mapping_path() -> Path:
    """获取映射文件路径"""
    return get_dify_dir() / "mapping.json"


def load_config() -> dict:
    """加载配置，支持多服务器"""
    config_path = get_config_path()
    if not config_path.exists():
        print(f"[ERROR] 配置文件不存在: {config_path}")
        print("请先运行: dify init")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    """保存配置"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_server_config(config: dict, server_name: str = None) -> tuple[str, dict]:
    """获取指定服务器的配置，返回 (server_name, server_config)"""
    servers = config.get("servers", {})
    if not servers:
        print("[ERROR] 未配置任何服务器")
        print("请先运行: dify init")
        sys.exit(1)

    if server_name:
        if server_name not in servers:
            print(f"[ERROR] 未找到服务器: {server_name}")
            print(f"可用服务器: {', '.join(servers.keys())}")
            sys.exit(1)
        return server_name, servers[server_name]
    else:
        default = config.get("default_server")
        if default and default in servers:
            return default, servers[default]
        name = next(iter(servers))
        return name, servers[name]


def find_server_by_url(config: dict, base_url: str) -> str | None:
    """根据 base_url 查找对应的服务器名称"""
    servers = config.get("servers", {})
    for name, srv in servers.items():
        if srv.get("base_url", "").rstrip("/") == base_url.rstrip("/"):
            return name
    return None


def list_servers(config: dict) -> list[str]:
    """列出所有服务器"""
    servers = config.get("servers", {})
    default = config.get("default_server")
    if not servers:
        print("[INFO] 未配置任何服务器")
        return []

    print(f"[INFO] 共 {len(servers)} 个服务器:")
    print("-" * 60)
    for name, srv in servers.items():
        is_default = " (默认)" if name == default else ""
        print(f"  {name}{is_default}")
        print(f"    URL:   {srv.get('base_url', 'N/A')}")
        print(f"    邮箱:  {srv.get('email', 'N/A')}")
        print()
    return list(servers.keys())

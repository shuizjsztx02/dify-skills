"""映射管理模块"""

import json
from datetime import datetime
from pathlib import Path

from .config import get_mapping_path, load_config


def load_mapping() -> dict:
    """加载映射文件，不存在则返回空 dict"""
    mapping_path = get_mapping_path()
    if not mapping_path.exists():
        return {}
    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_mapping(mapping: dict):
    """保存映射到文件"""
    mapping_path = get_mapping_path()
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def lookup_mapping(yml_path: str) -> dict | None:
    """根据文件名查找映射，返回 {server, app_id} 或 None"""
    mapping = load_mapping()
    if yml_path in mapping:
        return mapping[yml_path]
    yml_name = Path(yml_path).name
    if yml_name in mapping:
        return mapping[yml_name]
    return None


def save_to_mapping(yml_path: str, server_name: str, app_id: str):
    """保存或更新映射关系"""
    mapping = load_mapping()
    yml_name = Path(yml_path).name
    mapping[yml_name] = {
        "server": server_name,
        "app_id": app_id,
        "last_used": datetime.now().isoformat(timespec="seconds")
    }
    save_mapping(mapping)
    print(f"[OK] 已保存映射: {yml_name} -> {server_name}:{app_id}")


def list_mappings() -> list[tuple[str, dict]]:
    """列出所有映射"""
    mapping = load_mapping()
    config = load_config()
    servers = config.get("servers", {})

    if not mapping:
        print("[INFO] 当前没有映射关系")
        return []

    print(f"[INFO] 共 {len(mapping)} 个映射:")
    print("-" * 80)
    for yml_name, info in sorted(mapping.items()):
        server = info.get("server", "N/A")
        server_url = servers.get(server, {}).get("base_url", "N/A")
        print(f"{yml_name}")
        print(f"  服务器:   {server} ({server_url})")
        print(f"  App ID:   {info.get('app_id', 'N/A')}")
        print(f"  最后使用: {info.get('last_used', 'N/A')}")
        print()

    return list(mapping.items())


def delete_mapping(yml_path: str) -> bool:
    """删除映射关系"""
    mapping = load_mapping()
    yml_name = Path(yml_path).name

    if yml_name not in mapping:
        if yml_path in mapping:
            yml_name = yml_path
        else:
            print(f"[ERROR] 未找到映射: {yml_path}")
            return False

    del mapping[yml_name]
    save_mapping(mapping)
    print(f"[OK] 已删除映射: {yml_name}")
    return True

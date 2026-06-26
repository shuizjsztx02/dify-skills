"""工具函数模块"""

import re
import sys


def is_url(s: str) -> bool:
    """判断字符串是否是 URL（包含 /app/ 或 UUID）"""
    return "/app/" in s or re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s
    ) is not None


def extract_app_id(url: str) -> str:
    """从 Dify URL 中提取 app_id（UUID）"""
    match = re.search(
        r"/app/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        url,
    )
    if not match:
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
    """从 URL 中提取 base URL（scheme + host）"""
    m = re.match(r"(https?://[^/]+)", url)
    if not m:
        print(f"[ERROR] 无法解析 base URL: {url}")
        sys.exit(1)
    return m.group(1)

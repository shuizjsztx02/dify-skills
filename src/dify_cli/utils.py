"""工具函数模块"""

import re
import sys
from pathlib import Path


# dify-cli 包的安装目录（项目根目录）
PACKAGE_DIR = Path(__file__).parent.parent.parent


def get_package_dir() -> Path:
    """获取 dify-cli 包的安装目录"""
    return PACKAGE_DIR


def install_claude_commands() -> bool:
    """安装 Claude Code slash commands 到全局目录

    将 .claude/commands/dify-*.md 复制到 ~/.claude/commands/
    这样在任意文件夹下打开 Claude Code 都能使用这些 commands

    Returns:
        bool: 是否成功
    """
    # 源目录：包内的 .claude/commands/
    src_dir = get_package_dir() / ".claude" / "commands"
    if not src_dir.exists():
        print(f"[ERROR] 找不到 commands 目录: {src_dir}")
        return False

    # 目标目录：~/.claude/commands/
    dest_dir = Path.home() / ".claude" / "commands"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 复制所有 dify-*.md 文件
    copied = 0
    for src_file in src_dir.glob("dify-*.md"):
        dest_file = dest_dir / src_file.name
        try:
            content = src_file.read_text(encoding="utf-8")
            dest_file.write_text(content, encoding="utf-8")
            copied += 1
        except Exception as e:
            print(f"[WARN] 复制 {src_file.name} 失败: {e}")

    if copied > 0:
        print(f"[OK] 已安装 {copied} 个 Claude Code commands 到: {dest_dir}")
        return True
    else:
        print("[WARN] 没有复制任何 commands")
        return False


def uninstall_claude_commands() -> bool:
    """卸载全局 Claude Code slash commands

    Returns:
        bool: 是否成功
    """
    dest_dir = Path.home() / ".claude" / "commands"
    if not dest_dir.exists():
        print("[INFO] 没有安装 Claude Code commands")
        return True

    removed = 0
    for dest_file in dest_dir.glob("dify-*.md"):
        try:
            dest_file.unlink()
            removed += 1
        except Exception as e:
            print(f"[WARN] 删除 {dest_file.name} 失败: {e}")

    print(f"[OK] 已卸载 {removed} 个 Claude Code commands")
    return True


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

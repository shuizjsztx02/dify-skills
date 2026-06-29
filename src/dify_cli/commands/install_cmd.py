"""install 命令 - 安装/卸载 Claude Code commands"""

import sys

from ..utils import install_claude_commands, uninstall_claude_commands


def cmd_install(args):
    """安装或卸载 Claude Code slash commands"""

    if hasattr(args, 'uninstall') and args.uninstall:
        # 卸载
        print("[INFO] 卸载 Claude Code slash commands...")
        uninstall_claude_commands()
        return

    # 安装
    print("=" * 60)
    print("安装 Claude Code Slash Commands")
    print("=" * 60)
    print()
    print("这将把 dify-*.md commands 复制到:")
    print(f"  ~/.claude/commands/")
    print()
    print("安装后，你可以在任意文件夹下打开 Claude Code，")
    print("并使用以下 commands:")
    print()
    commands = [
        "/dify-init",
        "/dify-servers",
        "/dify-deploy",
        "/dify-export",
        "/dify-list",
        "/dify-unbind",
        "/dify-sync-name",
        "/dify-get-msg",
        "/dify-versions",
        "/dify-check-yml",
        "/dify-test",
        "/dify-features",
    ]
    for cmd in commands:
        print(f"  {cmd}")
    print()

    install_claude_commands()

    print()
    print("[OK] 安装完成！")
    print()
    print("使用说明:")
    print("  1. 在任意文件夹下打开 Claude Code: claude")
    print("  2. 输入 / 后可以看到 dify-* 命令")
    print("  3. 例如: /dify-deploy agent.yml")

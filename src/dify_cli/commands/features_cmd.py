"""features 命令 - 列出当前 CLI 已实现的所有命令功能"""

def cmd_features(args):
    """列出所有命令功能"""
    print("=" * 60)
    print("Dify CLI - 已实现的命令功能")
    print("=" * 60)
    print()

    features = [
        {
            "name": "init",
            "description": "交互式配置 Dify 服务器",
            "usage": "dify init [--force]",
            "category": "服务器管理"
        },
        {
            "name": "servers",
            "description": "管理服务器列表（查看、设置默认、删除）",
            "usage": "dify servers [--set-default <name>] [--remove <name>]",
            "category": "服务器管理"
        },
        {
            "name": "deploy",
            "description": "导入本地 YML 到 Dify 并发布",
            "usage": "dify deploy <yml_path> [dify_url] [--server <name>] [--version <name>]",
            "category": "部署"
        },
        {
            "name": "export",
            "description": "从 Dify 导出 YML 到本地",
            "usage": "dify export <dify_url> --output <path> [--server <name>] [--force] [--no-secret]",
            "category": "导出"
        },
        {
            "name": "list",
            "description": "列出所有映射关系（文件名 <-> Dify 应用）",
            "usage": "dify list",
            "category": "映射管理"
        },
        {
            "name": "unbind",
            "description": "删除映射关系",
            "usage": "dify unbind <yml_path>",
            "category": "映射管理"
        },
        {
            "name": "sync-name",
            "description": "同步 Web App 名称到应用名称",
            "usage": "dify sync-name <dify_url> [--server <name>]",
            "category": "同步"
        },
        {
            "name": "check",
            "description": "校验 YAML 语法和 Dify DSL 结构",
            "usage": "dify check <yml_path>",
            "category": "校验"
        },
        {
            "name": "test",
            "description": "自动测试 Dify 工作流（生成测试数据 + 调用 API）",
            "usage": "dify test <yml_path> [--url <url>] [--input <data>] [--server <name>]",
            "category": "测试"
        },
    ]

    # 按类别分组
    categories = {}
    for f in features:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)

    # 输出
    for cat, items in categories.items():
        print(f"【{cat}】")
        print("-" * 60)
        for f in items:
            print(f"  {f['name']:15} {f['description']}")
            print(f"                  用法: {f['usage']}")
            print()

    print("=" * 60)
    print("Claude Code Slash Commands")
    print("=" * 60)
    print()

    slash_commands = [
        ("/project:dify-init", "交互式配置服务器"),
        ("/project:dify-servers", "管理服务器列表"),
        ("/project:dify-deploy", "部署 YAML 到 Dify"),
        ("/project:dify-export", "从 Dify 导出 YAML"),
        ("/project:dify-list", "列出所有映射"),
        ("/project:dify-unbind", "删除映射"),
        ("/project:dify-sync-name", "同步 Web App 名称"),
        ("/project:dify-check-yml", "校验 YAML 文件和 DSL 结构"),
        ("/project:dify-test", "自动测试工作流"),
        ("/project:dify-features", "列出所有命令功能"),
    ]

    for cmd, desc in slash_commands:
        print(f"  {cmd:30} {desc}")

    print()

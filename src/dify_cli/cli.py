"""Dify CLI 主入口"""

import argparse
import sys

# 修复 Windows 终端中文输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from .commands.check_cmd import cmd_check
from .commands.deploy_cmd import cmd_deploy
from .commands.export_cmd import cmd_export
from .commands.features_cmd import cmd_features
from .commands.getmsg_cmd import cmd_getmsg
from .commands.init_cmd import cmd_init
from .commands.install_cmd import cmd_install
from .commands.versions_cmd import cmd_versions
from .commands.list_cmd import cmd_list
from .commands.servers_cmd import cmd_servers
from .commands.sync_name_cmd import cmd_sync_name
from .commands.test_cmd import cmd_test
from .commands.unbind_cmd import cmd_unbind


def main():
    parser = argparse.ArgumentParser(
        prog="dify",
        description="Dify CLI - 命令行工具 for Dify（支持多服务器）"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p_init = sub.add_parser("init", help="交互式配置服务器")
    p_init.add_argument("--force", "-f", action="store_true", help="覆盖已存在的服务器配置")
    p_init.set_defaults(func=cmd_init)

    # servers
    p_servers = sub.add_parser("servers", help="管理服务器列表")
    p_servers.add_argument("--set-default", metavar="NAME", help="设置默认服务器")
    p_servers.add_argument("--remove", metavar="NAME", help="删除服务器")
    p_servers.set_defaults(func=cmd_servers)

    # deploy
    p_deploy = sub.add_parser("deploy", help="导入本地 YML 到 Dify 并发布")
    p_deploy.add_argument("yml_path", help="本地 YML 文件路径")
    p_deploy.add_argument("dify_url", nargs="?", help="Dify URL 或已映射的文件名")
    p_deploy.add_argument("--server", "-s", help="指定服务器名称")
    p_deploy.add_argument("--version", "-v", help="版本名称")
    p_deploy.set_defaults(func=cmd_deploy)

    # export
    p_export = sub.add_parser("export", help="从 Dify 导出 YML 到本地")
    p_export.add_argument("dify_url", help="Dify URL 或已映射的文件名")
    p_export.add_argument("--output", "-o", help="本地保存路径")
    p_export.add_argument("--server", "-s", help="指定服务器名称")
    p_export.add_argument("--force", "-f", action="store_true", help="覆盖已存在的文件")
    p_export.add_argument("--include-secret", action="store_true", default=True, help="导出包含密钥（默认）")
    p_export.add_argument("--no-secret", dest="include_secret", action="store_false", help="不包含密钥")
    p_export.set_defaults(func=cmd_export)

    # list
    p_list = sub.add_parser("list", help="列出所有映射关系")
    p_list.set_defaults(func=cmd_list)

    # unbind
    p_unbind = sub.add_parser("unbind", help="删除映射关系")
    p_unbind.add_argument("yml_path", help="YML 文件路径或文件名")
    p_unbind.set_defaults(func=cmd_unbind)

    # sync-name
    p_sync = sub.add_parser("sync-name", help="同步 Web App 名称")
    p_sync.add_argument("dify_url", help="Dify URL 或已映射的文件名")
    p_sync.add_argument("--server", "-s", help="指定服务器名称")
    p_sync.set_defaults(func=cmd_sync_name)

    # get-msg
    p_getmsg = sub.add_parser("get-msg", help="查询 app-id / Web App 链接 / API Key（无则创建）")
    p_getmsg.add_argument("dify_url", help="Dify URL 或已映射的文件名")
    p_getmsg.add_argument("--server", "-s", help="指定服务器名称")
    p_getmsg.set_defaults(func=cmd_getmsg)

    # check
    p_check = sub.add_parser("check", help="校验 YAML 语法和 Dify DSL 结构")
    p_check.add_argument("yml_path", help="YML 文件路径")
    p_check.set_defaults(func=cmd_check)

    # features
    p_features = sub.add_parser("features", help="列出所有已实现的命令功能")
    p_features.set_defaults(func=cmd_features)

    # test
    p_test = sub.add_parser("test", help="自动测试 Dify 工作流（支持批量测试）")
    p_test.add_argument("yml_path", help="YML 文件路径")
    p_test.add_argument("--url", help="Dify 工作流 URL（如果未部署可指定）")
    p_test.add_argument("--input", help="自定义输入，格式: key1=value1,key2=value2")
    p_test.add_argument("--count", "-n", type=int, help="测试用例数量（批量测试）")
    p_test.add_argument("--test-data", help="测试数据文件夹路径（用于文件类型输入）")
    p_test.add_argument("--report", "-r", help="测试报告输出路径")
    p_test.add_argument("--server", "-s", help="指定服务器名称")
    p_test.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    p_test.set_defaults(func=cmd_test)

    # versions
    p_versions = sub.add_parser("versions", help="查询工作流版本历史（默认最新 10 条）")
    p_versions.add_argument("dify_url", help="Dify URL 或已映射的文件名")
    p_versions.add_argument("--limit", "-n", type=int, help="显示条数（默认 10）")
    p_versions.add_argument("--server", "-s", help="指定服务器名称")
    p_versions.set_defaults(func=cmd_versions)

    # install
    p_install = sub.add_parser("install", help="安装/卸载 Claude Code slash commands")
    p_install.add_argument("--uninstall", action="store_true", help="卸载 Claude Code commands")
    p_install.set_defaults(func=cmd_install)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

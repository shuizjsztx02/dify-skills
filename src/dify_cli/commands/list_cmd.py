"""list 命令 - 列出所有映射关系"""

from ..mapping import list_mappings


def cmd_list(args):
    """执行 list 子命令"""
    list_mappings()

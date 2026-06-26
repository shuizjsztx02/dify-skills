"""unbind 命令 - 删除映射关系"""

import sys

from ..mapping import delete_mapping


def cmd_unbind(args):
    """执行 unbind 子命令"""
    if not delete_mapping(args.yml_path):
        sys.exit(1)

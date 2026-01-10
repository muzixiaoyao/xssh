#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xssh CLI 入口
"""

import sys
import argparse
import getpass
from pathlib import Path

from xssh.core import XSSH
from xssh.hosts_manager import HostsManager
from xssh.parser import TargetParser

# 子命令列表
SUBCOMMANDS = ['add', 'delete', 'show', 'connect']


def get_hosts_manager(args):
    """根据 -i 参数获取 HostsManager 实例"""
    csv_path = Path(args.config) if hasattr(args, 'config') and args.config else None
    return HostsManager(csv_path)


def cmd_add(args):
    """添加主机信息"""
    try:
        parser = TargetParser()
        target = parser.parse(args.target)

        if not target.user:
            print("ERROR: 添加主机信息必须指定用户名，格式: user@host[:port]")
            sys.exit(1)

        if not target.port:
            target.port = 22

        # 提示输入密码
        password = getpass.getpass("请输入密码: ")
        confirm = getpass.getpass("确认密码: ")

        if password != confirm:
            print("ERROR: 两次输入的密码不一致")
            sys.exit(1)

        if not password:
            print("ERROR: 密码不能为空")
            sys.exit(1)

        # 添加到 CSV
        manager = get_hosts_manager(args)
        manager.add(target.host, target.port, target.user, password)
        print(f"✓ 已添加主机信息: {target.user}@{target.host}:{target.port}")
    except (EOFError, KeyboardInterrupt):
        print("\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def cmd_delete(args):
    """删除主机信息"""
    try:
        parser = TargetParser()
        target = parser.parse(args.target)

        if not target.user:
            print("ERROR: 删除主机信息必须指定用户名，格式: user@host")
            sys.exit(1)

        manager = get_hosts_manager(args)
        manager.load()
        manager.delete(target.host, target.user)
        print(f"✓ 已删除主机信息: {target.user}@{target.host}")
    except (EOFError, KeyboardInterrupt):
        print("\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def cmd_show(args):
    """显示主机信息"""
    try:
        manager = get_hosts_manager(args)
        manager.load()

        if args.host:
            hosts = manager.find_by_host(args.host)
            if not hosts:
                print(f"ERROR: 未找到主机: {args.host}")
                sys.exit(1)
            print(f"\n主机: {args.host}\n")
            for h in hosts:
                print(f"  - {h.user}@{h.host}:{h.port}")
        else:
            all_hosts = manager.get_all_hosts()
            if not all_hosts:
                print("\n当前没有配置任何主机\n")
            else:
                print("\n所有主机:\n")
                for host, users in all_hosts.items():
                    print(f"{host}:")
                    for h in users:
                        print(f"  - {h.user}@{h.host}:{h.port}")
                print()
    except (EOFError, KeyboardInterrupt):
        print("\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def cmd_connect(args):
    """连接主机"""
    if not args.target:
        print("ERROR: 请指定目标主机")
        sys.exit(1)

    try:
        csv_path = Path(args.config) if hasattr(args, 'config') and args.config else None
        xssh = XSSH(csv_path)
        xssh.connect(args.target)
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def main():
    try:
        # 预处理：检查是否是子命令
        if len(sys.argv) > 1 and sys.argv[1] in SUBCOMMANDS:
            # 是子命令，正常解析
            parser = argparse.ArgumentParser(
                prog='xssh',
                description='基于 CSV 的 SSH 密码快速连接工具',
                epilog="""使用示例:
  xssh root@192.168.1.1              # 连接主机
  xssh root@192.168.1.1:2222         # 指定端口连接
  xssh 192.168.1.1                    # 交互式选择用户
  xssh add root@192.168.1.1:2222        # 添加主机
  xssh delete root@192.168.1.1           # 删除主机
  xssh show                            # 显示所有主机
  xssh show 192.168.1.1               # 显示指定主机
  xssh -i /path/to/hosts.csv root@host # 使用自定义配置文件"""
            )

            subparsers = parser.add_subparsers(dest='command', help='子命令', title='可用子命令')

            # connect 命令
            connect_parser = subparsers.add_parser('connect', help='连接主机',
                description='使用 hosts.csv 中保存的密码连接到远程主机',
                epilog="示例: xssh connect root@192.168.1.1")
            connect_parser.add_argument('target', help='目标主机，格式: user@host[:port]')
            connect_parser.add_argument('-i', '--config', help='指定配置文件路径（默认: ~/.ssh/hosts.csv）')
            connect_parser.set_defaults(func=cmd_connect)

            # add 命令
            add_parser = subparsers.add_parser('add', help='添加主机信息',
                description='交互式添加主机信息到配置文件',
                epilog="示例: xssh add root@192.168.1.1:2222")
            add_parser.add_argument('target', help='目标主机，格式: user@host[:port]')
            add_parser.add_argument('-i', '--config', help='指定配置文件路径（默认: ~/.ssh/hosts.csv）')
            add_parser.set_defaults(func=cmd_add)

            # delete 命令
            delete_parser = subparsers.add_parser('delete', help='删除主机信息',
                description='从配置文件中删除指定的主机记录',
                epilog="示例: xssh delete root@192.168.1.1")
            delete_parser.add_argument('target', help='目标主机，格式: user@host')
            delete_parser.add_argument('-i', '--config', help='指定配置文件路径（默认: ~/.ssh/hosts.csv）')
            delete_parser.set_defaults(func=cmd_delete)

            # show 命令
            show_parser = subparsers.add_parser('show', help='显示主机信息',
                description='显示配置文件中的主机列表',
                epilog="示例:\n  xssh show              # 显示所有主机\n  xssh show 192.168.1.1  # 显示指定主机")
            show_parser.add_argument('host', nargs='?', help='主机名（可选，不指定则显示所有主机）')
            show_parser.add_argument('-i', '--config', help='指定配置文件路径（默认: ~/.ssh/hosts.csv）')
            show_parser.set_defaults(func=cmd_show)

            args = parser.parse_args()
            args.func(args)
        else:
            # 不是子命令，作为连接目标
            parser = argparse.ArgumentParser(
                prog='xssh',
                description='基于 CSV 的 SSH 密码快速连接工具',
                epilog="""使用示例:
  xssh root@192.168.1.1              # 连接主机
  xssh root@192.168.1.1:2222         # 指定端口连接
  xssh 192.168.1.1                    # 交互式选择用户
  xssh -i /path/to/hosts.csv root@host # 使用自定义配置文件"""
            )

            parser.add_argument(
                'target',
                help='目标主机，格式: user@host 或 user@host:port 或 host'
            )

            parser.add_argument(
                '-i', '--config',
                help='指定配置文件路径（默认: ~/.ssh/hosts.csv）',
                metavar='FILE'
            )

            parser.add_argument(
                '-v', '--version',
                action='version',
                version='%(prog)s 1.0.0'
            )

            args = parser.parse_args()

            if not args.target:
                parser.print_help()
                sys.exit(0)

            cmd_connect(args)
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

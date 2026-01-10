#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式用户选择模块
"""

from typing import List

from xssh.models import HostInfo


class UserSelector:
    """用户选择器"""

    @staticmethod
    def select(host: str, hosts: List[HostInfo]) -> HostInfo:
        """
        交互式选择用户

        返回选中的 HostInfo
        """
        print(f"\n发现主机 '{host}' 有多个用户:\n")

        for i, host_info in enumerate(hosts, start=1):
            print(f"  [{i}] {host_info.user}")

        while True:
            try:
                choice = input("\n请选择用户 (输入序号): ").strip()
                index = int(choice) - 1

                if 0 <= index < len(hosts):
                    return hosts[index]
                else:
                    print(f"无效的序号，请输入 1-{len(hosts)} 之间的数字")

            except ValueError:
                print("请输入有效的数字序号")
            except (KeyboardInterrupt, EOFError):
                print("\n操作已取消")
                raise SystemExit(130)

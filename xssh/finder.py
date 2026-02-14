#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主机查找和匹配模块
"""

from typing import Optional, List, Tuple

from xssh.models import HostInfo
from xssh.hosts_manager import HostsManager
from xssh.exceptions import HostNotFoundError, UserNotFoundError, XSSHError


class HostFinder:
    """主机查找器"""

    def __init__(self, hosts_manager: HostsManager):
        self.hosts_manager = hosts_manager

    def find(self, target) -> Tuple[HostInfo, int]:
        """
        查找主机信息

        返回: (host_info, effective_port)
        """
        hosts = self.hosts_manager.find_by_host(target.host)

        if not hosts:
            raise HostNotFoundError(
                f"在 hosts.csv 中未找到主机: {target.host}"
            )

        # 情况1: 指定了 user
        if target.user:
            host_info = self.hosts_manager.find_by_host_user(
                target.host,
                target.user
            )

            if not host_info:
                users = [h.user for h in hosts]
                raise UserNotFoundError(
                    f"主机 '{target.host}' 上未找到用户: {target.user}\n"
                    f"可用用户: {', '.join(users)}"
                )

            return host_info, target.port or host_info.port

        # 情况2: 未指定 user，只有一个用户
        if len(hosts) == 1:
            return hosts[0], target.port or hosts[0].port

        # 情况3: 未指定 user，有多个用户 - 需要交互选择
        raise MultipleUsersError(target.host, hosts)


class MultipleUsersError(XSSHError):
    """多个用户异常 - 用于触发交互选择"""

    def __init__(self, host: str, hosts: List[HostInfo]):
        self.host = host
        self.hosts = hosts
        super().__init__(f"主机 {host} 有多个用户")

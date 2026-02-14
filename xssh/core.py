#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xssh 核心逻辑
"""

import sys

from xssh.models import HostInfo
from xssh.parser import TargetParser
from xssh.hosts_manager import HostsManager
from xssh.finder import HostFinder, MultipleUsersError
from xssh.selector import UserSelector
from xssh.ssh import SSHClient
from xssh.exceptions import SSHPassNotFoundError


class XSSH:
    """xssh 核心类"""

    def __init__(self, csv_path=None):
        from pathlib import Path

        csv_path = Path(csv_path) if csv_path else None
        self.parser = TargetParser()
        self.hosts_manager = HostsManager(csv_path)
        self.finder = None
        self.selector = UserSelector()

    def connect(self, target_str: str):
        """连接到目标主机"""
        try:
            # 检查 sshpass
            if not SSHClient.check_sshpass():
                raise SSHPassNotFoundError(
                    "系统未安装 sshpass\n"
                    "请先安装:\n"
                    "  macOS: brew install hudochenkov/sshpass/sshpass\n"
                    "  Ubuntu/Debian: sudo apt-get install sshpass\n"
                    "  CentOS/RHEL: sudo yum install sshpass"
                )

            # 加载 CSV
            self.hosts_manager.load()

            # 解析目标
            target = self.parser.parse(target_str)

            # 初始化查找器
            self.finder = HostFinder(self.hosts_manager)

            # 查找主机信息
            try:
                host_info, port = self.finder.find(target)
            except MultipleUsersError as e:
                # 多用户选择
                host_info = self.selector.select(e.host, e.hosts)
                port = target.port or host_info.port

            # 连接 SSH
            client = SSHClient(host_info, port)
            client.connect()
        except KeyboardInterrupt:
            print("\n连接已取消")
            sys.exit(130)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH 连接模块
"""

import subprocess
import sys

from xssh.models import HostInfo


class SSHClient:
    """SSH 客户端封装"""

    def __init__(self, host_info: HostInfo, port: int):
        self.host_info = host_info
        self.port = port

    def connect(self):
        """建立 SSH 连接"""
        cmd = self._build_ssh_command()

        try:
            # 直接调用 ssh，让 sshpass 处理密码
            # 使用 os.execvp 替换当前进程，保持终端控制
            import os
            os.execvp(cmd[0], cmd)

        except KeyboardInterrupt:
            print("\n连接已断开")
            sys.exit(130)
        except Exception as e:
            raise Exception(f"SSH 连接失败: {e}")

    def _build_ssh_command(self) -> list:
        """构建 SSH 命令"""
        return [
            "sshpass",
            "-p", self.host_info.password,
            "ssh",
            "-tt",  # 强制分配伪终端
            "-p", str(self.port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{self.host_info.user}@{self.host_info.host}"
        ]

    @classmethod
    def check_sshpass(cls) -> bool:
        """检查系统是否已安装 sshpass"""
        try:
            result = subprocess.run(
                ["which", "sshpass"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

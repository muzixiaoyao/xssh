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
            # 使用 subprocess 运行 ssh，确保终端控制正确
            import signal
            import os

            # 保存原始终端设置
            try:
                import termios
                old_settings = termios.tcgetattr(sys.stdin.fileno())
            except:
                old_settings = None

            # 创建子进程
            process = subprocess.Popen(
                cmd,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )

            # 等待进程结束
            try:
                process.wait()
            except KeyboardInterrupt:
                # 用户中断，发送 SIGINT 到进程组
                try:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(process.pid), signal.SIGINT)
                    else:
                        process.send_signal(signal.SIGINT)
                except:
                    pass
                process.wait()
                sys.exit(130)
            finally:
                # 恢复终端设置
                if old_settings:
                    try:
                        import termios
                        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
                    except:
                        pass

            # 退出时使用 ssh 的退出码
            sys.exit(process.returncode)

        except FileNotFoundError:
            raise Exception("sshpass 未找到，请先安装 sshpass")
        except OSError as e:
            raise Exception(f"无法执行 SSH 命令: {e}")
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行参数解析模块
"""

from typing import Optional, Tuple
from dataclasses import dataclass

from xssh.exceptions import InvalidPortError


@dataclass
class Target:
    """解析后的目标信息"""
    host: str
    user: Optional[str]
    port: Optional[int]

    def __repr__(self):
        parts = []
        if self.user:
            parts.append(f"user={self.user}")
        parts.append(f"host={self.host}")
        if self.port:
            parts.append(f"port={self.port}")
        return f"Target({', '.join(parts)})"


class TargetParser:
    """目标参数解析器"""

    @staticmethod
    def parse(target: str) -> Target:
        """
        解析目标参数

        支持格式:
        1. user@host (标准用法)
        2. user@host:port (指定端口)
        3. host (仅主机名)
        """
        if not target:
            raise ValueError("目标参数不能为空")

        user = None
        port = None
        host = target

        # 解析 user@host[:port] 格式
        if '@' in target:
            user_part, host_part = target.split('@', 1)
            user = user_part.strip()
            host = host_part.strip()

            if not user:
                raise ValueError("用户名不能为空")
            if not host:
                raise ValueError("主机名不能为空")

        # 解析 host:port 格式
        if ':' in host:
            host_part, port_part = host.rsplit(':', 1)
            host = host_part.strip()
            port_str = port_part.strip()

            try:
                port = int(port_str)
            except ValueError:
                raise InvalidPortError(f"端口号必须为整数: {port_str}")

            if port < 1 or port > 65535:
                raise InvalidPortError(f"端口号超出范围 (1-65535): {port}")

            if not host:
                raise ValueError("主机名不能为空")

        return Target(
            host=host,
            user=user,
            port=port
        )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主机信息数据模型
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HostInfo:
    """主机信息"""
    host: str
    port: int
    user: str
    password: str

    def __str__(self):
        return f"{self.user}@{self.host}:{self.port}"

    def __repr__(self):
        return f"HostInfo(host={self.host}, port={self.port}, user={self.user})"

    @property
    def key(self):
        """唯一标识 (host, user)"""
        return f"{self.user}@{self.host}"

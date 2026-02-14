#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 主机信息管理模块
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional

from xssh.models import HostInfo
from xssh.exceptions import (
    CSVFileNotFoundError,
    CSVFormatError,
    DuplicateHostUserError,
    InvalidPortError,
    EmptyPasswordError,
    UserNotFoundError,
    XSSHError
)


class HostsManager:
    """主机信息管理器"""

    CSV_PATH = Path.home() / ".ssh" / "hosts.csv"
    REQUIRED_FIELDS = ["host", "port", "user", "password"]

    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = csv_path or self.CSV_PATH
        self._hosts: Dict[str, List[HostInfo]] = {}
        self._host_user_map: Dict[str, HostInfo] = {}

    def load(self) -> Dict[str, List[HostInfo]]:
        """加载 hosts.csv 文件"""
        if not self.csv_path.exists():
            raise CSVFileNotFoundError(
                f"hosts.csv 文件不存在: {self.csv_path}\n"
                f"请先创建该文件并添加主机信息"
            )

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # 检查必需字段
            if not reader.fieldnames or not all(
                field in reader.fieldnames for field in self.REQUIRED_FIELDS
            ):
                raise CSVFormatError(
                    f"CSV 文件缺少必需字段: {', '.join(self.REQUIRED_FIELDS)}"
                )

            # 清空现有数据
            self._hosts.clear()
            self._host_user_map.clear()

            # 解析每一行
            for row_num, row in enumerate(reader, start=2):
                try:
                    host_info = self._parse_row(row)
                    self._add_host_info(host_info)
                except (InvalidPortError, EmptyPasswordError) as e:
                    raise CSVFormatError(f"第 {row_num} 行: {e}")

        return self._hosts

    def _parse_row(self, row: dict) -> HostInfo:
        """解析单行数据"""
        host = row["host"].strip()
        port_str = row["port"].strip()
        user = row["user"].strip()
        password = row["password"].strip()

        # 验证字段
        if not host:
            raise CSVFormatError("host 字段不能为空")
        if not user:
            raise CSVFormatError("user 字段不能为空")
        if not password:
            raise EmptyPasswordError("password 字段不能为空")

        try:
            port = int(port_str)
        except ValueError:
            raise InvalidPortError(f"端口号必须为整数: {port_str}")

        if port < 1 or port > 65535:
            raise InvalidPortError(f"端口号超出范围 (1-65535): {port}")

        return HostInfo(
            host=host,
            port=port,
            user=user,
            password=password
        )

    def _add_host_info(self, host_info: HostInfo):
        """添加主机信息到内存"""
        key = host_info.key

        # 检查重复
        if key in self._host_user_map:
            raise DuplicateHostUserError(
                f"hosts.csv 中存在重复的 host+user 记录: {key}"
            )

        # 按 host 分组
        if host_info.host not in self._hosts:
            self._hosts[host_info.host] = []
        self._hosts[host_info.host].append(host_info)

        # 建立映射
        self._host_user_map[key] = host_info

    def find_by_host(self, host: str) -> Optional[List[HostInfo]]:
        """根据主机名查找所有用户"""
        return self._hosts.get(host)

    def find_by_host_user(self, host: str, user: str) -> Optional[HostInfo]:
        """根据 host 和 user 精确查找"""
        key = f"{user}@{host}"
        return self._host_user_map.get(key)

    def get_all_hosts(self) -> Dict[str, List[HostInfo]]:
        """获取所有主机信息"""
        return self._hosts

    def add(self, host: str, port: int, user: str, password: str):
        """添加主机信息到 CSV"""
        try:
            # 确保目录存在
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)

            # 加载现有数据检查重复
            if self.csv_path.exists():
                self.load()
                if self.find_by_host_user(host, user):
                    raise DuplicateHostUserError(
                        f"已存在相同的 host+user 记录: {user}@{host}"
                    )
            else:
                # 文件不存在，创建表头
                with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.REQUIRED_FIELDS)

            # 追加新记录
            with open(self.csv_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([host, port, user, password])

            # 重新加载
            self.load()
        except (IOError, OSError) as e:
            raise XSSHError(f"无法写入配置文件: {e}")

    def delete(self, host: str, user: str):
        """删除主机信息"""
        try:
            self.load()

            if not self.find_by_host_user(host, user):
                raise UserNotFoundError(f"未找到主机信息: {user}@{host}")

            # 读取所有行，删除匹配的行
            with open(self.csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                rows = [row for row in reader if not (row['host'] == host and row['user'] == user)]

            # 写回文件
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.REQUIRED_FIELDS)
                writer.writeheader()
                writer.writerows(rows)

            # 重新加载数据
            self.load()
        except (IOError, OSError) as e:
            raise XSSHError(f"无法更新配置文件: {e}")

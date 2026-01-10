#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常
"""


class XSSHError(Exception):
    """xssh 基础异常"""
    pass


class CSVFileNotFoundError(XSSHError):
    """hosts.csv 文件不存在"""
    pass


class CSVFormatError(XSSHError):
    """CSV 格式错误"""
    pass


class DuplicateHostUserError(XSSHError):
    """重复的 host+user 记录"""
    pass


class HostNotFoundError(XSSHError):
    """主机未找到"""
    pass


class UserNotFoundError(XSSHError):
    """用户未找到"""
    pass


class InvalidPortError(XSSHError):
    """无效端口号"""
    pass


class EmptyPasswordError(XSSHError):
    """密码为空"""
    pass

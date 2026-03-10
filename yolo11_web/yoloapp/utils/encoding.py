# -*- coding: utf-8 -*-
"""
全局UTF-8编码强制解决方案

提供简单的全局函数，强制整个Python进程使用UTF-8编码。
解决Windows上'gbk' codec can't encode character错误。
"""

import sys
import os
import io


def force_global_utf8():
    """
    强制全局UTF-8编码
    
    此函数会：
    1. 设置环境变量强制UTF-8编码
    2. 重新配置标准输入输出流
    3. 确保Python解释器使用UTF-8
    """
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Windows特定设置
    if sys.platform == "win32":
        try:
            # 重定向标准输出为UTF-8
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                write_through=True
            )
            
            # 重定向标准错误为UTF-8
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                write_through=True
            )
        except Exception:
            pass  # 如果失败，静默继续
    
    # 设置默认编码
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')


def utf8_safe(func):
    """
    装饰器：确保函数内的字符串操作使用UTF-8编码
    """
    def wrapper(*args, **kwargs):
        # 调用函数前确保UTF-8环境
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # 临时设置UTF-8输出
            force_global_utf8()
            return func(*args, **kwargs)
        finally:
            # 恢复原始设置
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    return wrapper


def ensure_utf8_string(text: str) -> str:
    """
    确保字符串是UTF-8编码，遇到编码错误时安全处理
    
    Args:
        text: 输入的字符串
        
    Returns:
        UTF-8安全的字符串
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # 尝试编码为UTF-8，如果失败则使用replace策略
    try:
        text.encode('utf-8')
        return text
    except UnicodeEncodeError:
        # 使用replace策略处理无法编码的字符
        return text.encode('utf-8', errors='replace').decode('utf-8')


# 自动应用全局UTF-8设置
force_global_utf8()


__all__ = [
    "force_global_utf8",
    "utf8_safe",
    "ensure_utf8_string",
]

# -*- coding: utf-8 -*-
"""
[已废弃] 此模块已迁移到 yoloapp.utils.logger

请使用新的导入路径:
    from yoloapp.utils.logger import *

此文件将在未来版本中移除。
"""

import warnings

warnings.warn(
    "utils.logger 已废弃，请使用 yoloapp.utils.logger 代替。"
    "新的导入方式: from yoloapp.utils.logger import *",
    DeprecationWarning,
    stacklevel=2
)

# 从新位置导入所有内容
from yoloapp.utils.logger import *

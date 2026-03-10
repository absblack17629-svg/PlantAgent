# -*- coding: utf-8 -*-
"""
Flow 模块 - 流程编排

包含所有流程编排类。

注意：DetectionFlow 和 KnowledgeFlow 有外部依赖，需要时请单独导入：
    from yoloapp.flow.detection_flow import DetectionFlow, create_detection_flow
    from yoloapp.flow.knowledge_flow import KnowledgeFlow, create_knowledge_flow
"""

from yoloapp.flow.base import BaseFlow

__all__ = [
    "BaseFlow",
]

# -*- coding: utf-8 -*-
"""
检测记录数据模型
"""

from sqlalchemy import Column, String, Text, DateTime
from models.base import BaseModel


class DetectionLog(BaseModel):
    """检测日志表"""
    
    __tablename__ = "detect_log"
    
    filename = Column(String(255), nullable=True, comment="上传文件名")
    file_path = Column(String(255), nullable=True, comment="文件存储路径")
    question = Column(Text, nullable=True, comment="用户提问文本")
    detections = Column(Text, nullable=True, comment="检测结果JSON字符串")
    ai_analysis = Column(Text, nullable=True, comment="AI分析结果")


# 别名，保持向后兼容
Detection = DetectionLog

# -*- coding: utf-8 -*-
"""
历史记录数据模型
"""

from sqlalchemy import Column, Integer, String, Enum
from models.base import BaseModel


class History(BaseModel):
    """历史记录表"""
    
    __tablename__ = "histories"
    
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    action_type = Column(
        Enum('view_news', 'detection', 'search', name='history_type'),
        nullable=False,
        comment="操作类型"
    )
    item_id = Column(Integer, nullable=True, comment="关联项ID")
    item_title = Column(String(200), nullable=True, comment="项目标题")
    action_detail = Column(String(500), nullable=True, comment="操作详情")

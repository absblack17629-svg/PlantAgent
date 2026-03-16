# -*- coding: utf-8 -*-
"""
收藏数据模型
"""

from sqlalchemy import Column, Integer, String, Enum
from models.base import BaseModel


class Favorite(BaseModel):
    """收藏表"""
    
    __tablename__ = "favorites"
    
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    item_type = Column(
        Enum('news', 'detection', name='favorite_type'),
        nullable=False,
        comment="收藏类型"
    )
    item_id = Column(Integer, nullable=False, comment="收藏项ID")
    item_title = Column(String(200), nullable=True, comment="收藏项标题")
    item_cover = Column(String(255), nullable=True, comment="收藏项封面")
    notes = Column(String(500), nullable=True, comment="收藏备注")

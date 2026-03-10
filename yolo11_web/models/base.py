# -*- coding: utf-8 -*-
"""
数据模型基类
统一主键、时间戳等字段
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from config.db_conf import Base


class BaseModel(Base):
    """模型基类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# -*- coding: utf-8 -*-
"""
历史记录相关数据验证模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import BaseResponseSchema


class HistoryCreate(BaseModel):
    """历史记录创建模型"""
    action_type: str = Field(..., description="操作类型: view_news/detection/search")
    item_id: Optional[int] = Field(None, description="关联项ID")
    item_title: Optional[str] = Field(None, max_length=200, description="项目标题")
    action_detail: Optional[str] = Field(None, max_length=500, description="操作详情")


class HistoryResponse(BaseResponseSchema):
    """历史记录响应模型"""
    user_id: int
    action_type: str
    item_id: Optional[int]
    item_title: Optional[str]
    action_detail: Optional[str]

# -*- coding: utf-8 -*-
"""
收藏相关数据验证模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import BaseResponseSchema


class FavoriteCreate(BaseModel):
    """收藏创建模型"""
    item_type: str = Field(..., description="收藏类型: news/detection")
    item_id: int = Field(..., description="收藏项ID")
    item_title: Optional[str] = Field(None, max_length=200, description="收藏项标题")
    item_cover: Optional[str] = Field(None, description="收藏项封面")
    notes: Optional[str] = Field(None, max_length=500, description="收藏备注")


class FavoriteUpdate(BaseModel):
    """收藏更新模型"""
    notes: Optional[str] = Field(None, max_length=500, description="收藏备注")


class FavoriteResponse(BaseResponseSchema):
    """收藏响应模型"""
    user_id: int
    item_type: str
    item_id: int
    item_title: Optional[str]
    item_cover: Optional[str]
    notes: Optional[str]

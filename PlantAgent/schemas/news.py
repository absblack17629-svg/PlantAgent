# -*- coding: utf-8 -*-
"""
新闻相关数据验证模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from schemas.base import BaseResponseSchema


class NewsBase(BaseModel):
    """新闻基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="新闻标题")
    content: str = Field(..., min_length=1, description="新闻内容")
    summary: Optional[str] = Field(None, max_length=500, description="新闻摘要")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    author: Optional[str] = Field(None, max_length=50, description="作者")
    source: Optional[str] = Field(None, max_length=100, description="来源")
    category: str = Field("other", description="新闻分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class NewsCreate(NewsBase):
    """新闻创建模型"""
    pass


class NewsUpdate(BaseModel):
    """新闻更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="新闻标题")
    content: Optional[str] = Field(None, min_length=1, description="新闻内容")
    summary: Optional[str] = Field(None, max_length=500, description="新闻摘要")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    category: Optional[str] = Field(None, description="新闻分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    is_published: Optional[int] = Field(None, description="是否发布")


class NewsResponse(BaseResponseSchema):
    """新闻响应模型"""
    title: str
    content: str
    summary: Optional[str]
    cover_image: Optional[str]
    author: Optional[str]
    source: Optional[str]
    category: str
    tags: Optional[List[str]]
    view_count: int
    like_count: int
    comment_count: int
    is_published: int
    published_by: Optional[int]


class NewsListResponse(BaseModel):
    """新闻列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")
    items: List[NewsResponse] = Field(..., description="新闻列表")

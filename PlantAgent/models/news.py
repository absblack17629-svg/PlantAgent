# -*- coding: utf-8 -*-
"""
新闻数据模型
"""

from sqlalchemy import Column, String, Text, Integer, Enum, JSON
from models.base import BaseModel


class News(BaseModel):
    """新闻表"""
    
    __tablename__ = "news"
    
    title = Column(String(200), nullable=False, index=True, comment="新闻标题")
    content = Column(Text, nullable=False, comment="新闻内容")
    summary = Column(String(500), nullable=True, comment="新闻摘要")
    cover_image = Column(String(255), nullable=True, comment="封面图片URL")
    author = Column(String(50), nullable=True, comment="作者")
    source = Column(String(100), nullable=True, comment="来源")
    category = Column(
        Enum('科技农业', '植保技术', '设施农业', '有机农业', '畜牧养殖', '节水农业', '质量安全', '农村电商', '病虫害防治', '农业机械', '其他', name='news_category'),
        default='其他',
        comment="新闻分类"
    )
    tags = Column(JSON, nullable=True, comment="标签列表")
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    is_published = Column(Integer, default=1, comment="是否发布 1-已发布 0-草稿")
    published_by = Column(Integer, nullable=True, comment="发布者用户ID")

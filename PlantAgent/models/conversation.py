# -*- coding: utf-8 -*-
"""
对话相关数据模型
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Enum, JSON
from models.base import BaseModel


class ConversationSession(BaseModel):
    """对话会话表"""
    
    __tablename__ = "conversation_sessions"
    
    session_id = Column(String(50), unique=True, nullable=False, index=True, comment="会话ID")
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")
    state = Column(
        Enum('new', 'active', 'paused', 'completed', 'error', name='session_state'),
        default='new',
        comment="会话状态"
    )
    ended_at = Column(DateTime, nullable=True, comment="结束时间")
    message_count = Column(Integer, default=0, comment="消息数量")


class ConversationMessage(BaseModel):
    """对话消息表"""
    
    __tablename__ = "conversation_messages"
    
    message_id = Column(String(50), unique=True, nullable=False, index=True, comment="消息ID")
    session_id = Column(String(50), nullable=False, index=True, comment="会话ID")
    role = Column(Enum('user', 'assistant', name='message_role'), nullable=False, comment="角色")
    content = Column(Text, nullable=False, comment="消息内容")
    intent = Column(String(50), nullable=True, comment="意图")
    sentiment = Column(String(20), nullable=True, comment="情感")
    extra_data = Column(JSON, nullable=True, comment="额外数据")

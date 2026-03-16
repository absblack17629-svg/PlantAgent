# -*- coding: utf-8 -*-
"""
用户数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from models.base import BaseModel


class User(BaseModel):
    """用户表"""
    
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    phone = Column(String(20), nullable=True, comment="手机号")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

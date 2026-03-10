# -*- coding: utf-8 -*-
"""
用户CRUD操作
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase
from models.users import User
from schemas.users import UserCreate, UserUpdate
from utils.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户CRUD"""
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(select(self.model).where(self.model.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """创建用户"""
        db_obj = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            nickname=user_in.nickname,
            phone=user_in.phone
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = await self.get_by_username(db, username)
        if not user:
            user = await self.get_by_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def is_active(self, user: User) -> bool:
        """检查用户是否激活"""
        return user.is_active
    
    async def is_superuser(self, user: User) -> bool:
        """检查是否超级管理员"""
        return user.is_superuser


# 创建CRUD实例
crud_user = CRUDUser(User)

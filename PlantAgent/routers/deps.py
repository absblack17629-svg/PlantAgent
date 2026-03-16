# -*- coding: utf-8 -*-
"""
通用依赖
数据库会话、认证、权限等
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import AsyncSessionLocal
from config.cache_conf import get_redis
import redis.asyncio as aioredis
from utils.security import decode_access_token
from crud.users import crud_user
from models.users import User

# OAuth2密码模式 - 设置auto_error=False允许可选认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)


async def get_token_from_header(request: Request) -> Optional[str]:
    """
    从请求头中提取token
    
    Args:
        request: FastAPI请求对象
    
    Returns:
        token或None
    """
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return None
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    
    return token if token else None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis_client() -> aioredis.Redis:
    """
    获取Redis客户端依赖
    
    Returns:
        Redis客户端
    """
    client = await get_redis()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis服务不可用"
        )
    return client


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选）
    
    Args:
        request: FastAPI请求对象
        db: 数据库会话
    
    Returns:
        当前用户或None
    """
    # 从请求头提取token
    token = await get_token_from_header(request)
    if not token:
        return None
    
    # 解码token
    payload = decode_access_token(token)
    if not payload:
        return None
    
    # 从payload中获取user_id，并转换为整数（因为JWT的sub字段是字符串）
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        return None
    
    # 查询用户
    user = await crud_user.get(db, user_id)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活用户（必需）
    
    Args:
        current_user: 当前用户
    
    Returns:
        当前用户
    
    Raises:
        HTTPException: 未认证或用户未激活
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user

# -*- coding: utf-8 -*-
"""
用户相关API路由
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from routers.deps import get_db, get_current_active_user
from crud.users import crud_user
from schemas.users import UserCreate, UserResponse, UserUpdate, Token, UserLogin
from utils.security import create_access_token
from config.settings import settings
from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/users", tags=["用户"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    Args:
        user_in: 用户注册信息
        db: 数据库会话
    
    Returns:
        创建的用户信息
    """
    # 检查用户名是否已存在
    user = await crud_user.get_by_username(db, user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    user = await crud_user.get_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    user = await crud_user.create_user(db, user_in)
    logger.info(f"新用户注册: {user.username}")
    
    return user


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    Args:
        user_in: 登录信息
        db: 数据库会话
    
    Returns:
        访问令牌
    """
    user = await crud_user.authenticate(db, user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not await crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"用户登录: {user.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
    
    Returns:
        用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_in: 更新信息
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        更新后的用户信息
    """
    user = await crud_user.update(db, current_user.id, user_in)
    logger.info(f"用户更新信息: {current_user.username}")
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户信息
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        用户信息
    """
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

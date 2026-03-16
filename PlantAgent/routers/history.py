# -*- coding: utf-8 -*-
"""
历史记录相关API路由
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from routers.deps import get_db, get_current_active_user
from crud.history import crud_history
from schemas.history import HistoryResponse, HistoryCreate
from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/history", tags=["历史记录"])
logger = get_logger(__name__)


@router.get("/", response_model=List[HistoryResponse])
async def get_my_history(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的历史记录
    
    Args:
        skip: 跳过数量
        limit: 返回数量
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        历史记录列表
    """
    histories = await crud_history.get_by_user(db, current_user.id, skip=skip, limit=limit)
    return histories


@router.post("/", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_history(
    history_in: HistoryCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    添加历史记录
    
    Args:
        history_in: 历史记录信息
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        历史记录
    """
    history = await crud_history.create_history(db, current_user.id, history_in)
    return history


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    清空历史记录
    
    Args:
        current_user: 当前用户
        db: 数据库会话
    """
    await crud_history.clear_user_history(db, current_user.id)
    logger.info(f"用户 {current_user.username} 清空了历史记录")

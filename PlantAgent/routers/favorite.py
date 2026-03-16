# -*- coding: utf-8 -*-
"""
收藏相关API路由
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from routers.deps import get_db, get_current_active_user
from crud.favorite import crud_favorite
from schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteUpdate
from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/favorites", tags=["收藏"])
logger = get_logger(__name__)


@router.get("/", response_model=List[FavoriteResponse])
async def get_my_favorites(
    item_type: Optional[str] = Query(None, description="收藏类型: news/detection"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的收藏列表
    
    Args:
        item_type: 收藏类型
        skip: 跳过数量
        limit: 返回数量
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        收藏列表
    """
    favorites = await crud_favorite.get_by_user(
        db, current_user.id, item_type=item_type, skip=skip, limit=limit
    )
    return favorites


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_in: FavoriteCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    添加收藏
    
    Args:
        favorite_in: 收藏信息
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        收藏记录
    """
    favorite = await crud_favorite.create_favorite(db, current_user.id, favorite_in)
    logger.info(f"用户 {current_user.username} 收藏了 {favorite_in.item_type}:{favorite_in.item_id}")
    
    return favorite


@router.delete("/{item_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    item_type: str,
    item_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消收藏
    
    Args:
        item_type: 收藏类型
        item_id: 收藏项ID
        current_user: 当前用户
        db: 数据库会话
    """
    success = await crud_favorite.remove_favorite(db, current_user.id, item_type, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )
    
    logger.info(f"用户 {current_user.username} 取消收藏 {item_type}:{item_id}")


@router.get("/check/{item_type}/{item_id}")
async def check_favorite(
    item_type: str,
    item_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查是否已收藏
    
    Args:
        item_type: 收藏类型
        item_id: 收藏项ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        是否已收藏
    """
    favorite = await crud_favorite.get_by_item(db, current_user.id, item_type, item_id)
    return {"is_favorited": favorite is not None}

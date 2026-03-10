# -*- coding: utf-8 -*-
"""
新闻相关API路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from routers.deps import get_db, get_current_user
from crud.news import crud_news
from crud.history import crud_history
from schemas.news import NewsCreate, NewsResponse, NewsUpdate, NewsListResponse
from schemas.history import HistoryCreate
from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/news", tags=["新闻"])
logger = get_logger(__name__)


@router.get("/", response_model=NewsListResponse)
@router.get("/list", response_model=NewsListResponse)
async def get_news_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="新闻分类"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表
    
    Args:
        page: 页码
        page_size: 每页数量
        category: 新闻分类
        db: 数据库会话
    
    Returns:
        新闻列表
    """
    try:
        logger.info(f"查询新闻列表: page={page}, page_size={page_size}, category={category}")
        
        skip = (page - 1) * page_size
        news_list = await crud_news.get_published(db, skip=skip, limit=page_size, category=category)
        total = await crud_news.get_total_count(db, category=category)
        
        logger.info(f"查询成功: total={total}, 返回{len(news_list)}条记录")
        
        return NewsListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=news_list
        )
    except Exception as e:
        logger.error(f"查询新闻列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get("/search", response_model=NewsListResponse)
async def search_news(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    搜索新闻
    
    Args:
        keyword: 搜索关键词
        skip: 跳过数量
        limit: 返回数量
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        搜索结果
    """
    news_list = await crud_news.search(db, keyword=keyword, skip=skip, limit=limit)
    
    # 记录搜索历史
    if current_user:
        history_in = HistoryCreate(
            action_type="search",
            action_detail=f"搜索关键词: {keyword}"
        )
        await crud_history.create_history(db, current_user.id, history_in)
    
    return NewsListResponse(total=len(news_list), items=news_list)


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取新闻详情
    
    Args:
        news_id: 新闻ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        新闻详情
    """
    news = await crud_news.get(db, news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在"
        )
    
    # 增加浏览次数
    await crud_news.increment_view_count(db, news_id)
    
    # 记录浏览历史
    if current_user:
        history_in = HistoryCreate(
            action_type="view_news",
            item_id=news_id,
            item_title=news.title
        )
        await crud_history.create_history(db, current_user.id, history_in)
    
    return news


@router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    news_in: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建新闻（需要登录）
    
    Args:
        news_in: 新闻信息
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的新闻
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录"
        )
    
    news = await crud_news.create(db, news_in)
    logger.info(f"创建新闻: {news.title} by {current_user.username}")
    
    return news


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_in: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新新闻（需要登录）
    
    Args:
        news_id: 新闻ID
        news_in: 更新信息
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的新闻
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录"
        )
    
    news = await crud_news.get(db, news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在"
        )
    
    news = await crud_news.update(db, news_id, news_in)
    logger.info(f"更新新闻: {news.title} by {current_user.username}")
    
    return news


@router.post("/{news_id}/like")
async def like_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    点赞新闻
    
    Args:
        news_id: 新闻ID
        db: 数据库会话
    
    Returns:
        点赞后的新闻
    """
    news = await crud_news.increment_like_count(db, news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在"
        )
    
    return {"code": 200, "msg": "点赞成功", "like_count": news.like_count}


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除新闻（需要登录）
    
    Args:
        news_id: 新闻ID
        db: 数据库会话
        current_user: 当前用户
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录"
        )
    
    success = await crud_news.delete(db, news_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在"
        )
    
    logger.info(f"删除新闻: {news_id} by {current_user.username}")

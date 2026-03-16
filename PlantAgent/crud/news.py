# -*- coding: utf-8 -*-
"""
新闻CRUD操作
"""

from typing import List, Optional
from sqlalchemy import select, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase
from models.news import News
from schemas.news import NewsCreate, NewsUpdate


class CRUDNews(CRUDBase[News, NewsCreate, NewsUpdate]):
    """新闻CRUD"""
    
    async def get_published(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20,
        category: Optional[str] = None
    ) -> List[News]:
        """获取已发布的新闻列表"""
        query = select(self.model).where(self.model.is_published == 1)
        
        if category:
            query = query.where(self.model.category == category)
        
        query = query.order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_category(
        self, 
        db: AsyncSession, 
        category: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[News]:
        """根据分类获取新闻"""
        result = await db.execute(
            select(self.model)
            .where(self.model.category == category, self.model.is_published == 1)
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search(
        self,
        db: AsyncSession,
        keyword: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[News]:
        """搜索新闻"""
        result = await db.execute(
            select(self.model)
            .where(
                or_(
                    self.model.title.contains(keyword),
                    self.model.content.contains(keyword)
                ),
                self.model.is_published == 1
            )
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def increment_view_count(self, db: AsyncSession, news_id: int):
        """增加浏览次数"""
        news = await self.get(db, news_id)
        if news:
            news.view_count += 1
            await db.commit()
            await db.refresh(news)
        return news
    
    async def increment_like_count(self, db: AsyncSession, news_id: int):
        """增加点赞数"""
        news = await self.get(db, news_id)
        if news:
            news.like_count += 1
            await db.commit()
            await db.refresh(news)
        return news
    
    async def get_total_count(self, db: AsyncSession, category: Optional[str] = None) -> int:
        """获取新闻总数"""
        query = select(func.count(self.model.id)).where(self.model.is_published == 1)
        if category:
            query = query.where(self.model.category == category)
        result = await db.execute(query)
        return result.scalar()


# 创建CRUD实例
crud_news = CRUDNews(News)

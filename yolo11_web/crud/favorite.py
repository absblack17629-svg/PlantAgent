# -*- coding: utf-8 -*-
"""
收藏CRUD操作
"""

from typing import List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase
from models.favorite import Favorite
from schemas.favorite import FavoriteCreate, FavoriteUpdate


class CRUDFavorite(CRUDBase[Favorite, FavoriteCreate, FavoriteUpdate]):
    """收藏CRUD"""
    
    async def get_by_user(
        self, 
        db: AsyncSession, 
        user_id: int,
        item_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Favorite]:
        """获取用户收藏列表"""
        query = select(self.model).where(self.model.user_id == user_id)
        
        if item_type:
            query = query.where(self.model.item_type == item_type)
        
        query = query.order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_item(
        self,
        db: AsyncSession,
        user_id: int,
        item_type: str,
        item_id: int
    ) -> Optional[Favorite]:
        """检查是否已收藏"""
        result = await db.execute(
            select(self.model).where(
                and_(
                    self.model.user_id == user_id,
                    self.model.item_type == item_type,
                    self.model.item_id == item_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_favorite(
        self,
        db: AsyncSession,
        user_id: int,
        favorite_in: FavoriteCreate
    ) -> Favorite:
        """创建收藏"""
        # 检查是否已收藏
        existing = await self.get_by_item(
            db, user_id, favorite_in.item_type, favorite_in.item_id
        )
        if existing:
            return existing
        
        db_obj = Favorite(
            user_id=user_id,
            item_type=favorite_in.item_type,
            item_id=favorite_in.item_id,
            item_title=favorite_in.item_title,
            item_cover=favorite_in.item_cover,
            notes=favorite_in.notes
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove_favorite(
        self,
        db: AsyncSession,
        user_id: int,
        item_type: str,
        item_id: int
    ) -> bool:
        """取消收藏"""
        favorite = await self.get_by_item(db, user_id, item_type, item_id)
        if favorite:
            await db.delete(favorite)
            await db.commit()
            return True
        return False


# 创建CRUD实例
crud_favorite = CRUDFavorite(Favorite)

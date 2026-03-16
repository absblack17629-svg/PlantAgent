# -*- coding: utf-8 -*-
"""
历史记录CRUD操作
"""

from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase
from models.history import History
from schemas.history import HistoryCreate


class CRUDHistory(CRUDBase[History, HistoryCreate, HistoryCreate]):
    """历史记录CRUD"""
    
    async def get_by_user(
        self, 
        db: AsyncSession, 
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[History]:
        """获取用户历史记录"""
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_history(
        self,
        db: AsyncSession,
        user_id: int,
        history_in: HistoryCreate
    ) -> History:
        """创建历史记录"""
        db_obj = History(
            user_id=user_id,
            action_type=history_in.action_type,
            item_id=history_in.item_id,
            item_title=history_in.item_title,
            action_detail=history_in.action_detail
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def clear_user_history(self, db: AsyncSession, user_id: int) -> bool:
        """清空用户历史记录"""
        result = await db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        histories = result.scalars().all()
        for history in histories:
            await db.delete(history)
        await db.commit()
        return True


# 创建CRUD实例
crud_history = CRUDHistory(History)

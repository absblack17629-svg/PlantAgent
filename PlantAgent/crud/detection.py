# -*- coding: utf-8 -*-
"""
检测记录CRUD操作
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase
from models.detection import DetectionLog
from schemas.detection import DetectionLogSchema


class CRUDDetection(CRUDBase[DetectionLog, DetectionLogSchema, DetectionLogSchema]):
    """检测记录CRUD"""
    
    async def get_history(
        self, 
        db: AsyncSession, 
        limit: int = 100
    ) -> List[DetectionLog]:
        """获取检测历史记录"""
        result = await db.execute(
            select(self.model)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_log(
        self,
        db: AsyncSession,
        filename: Optional[str],
        question: Optional[str],
        detections: Optional[str],
        ai_analysis: Optional[str],
        file_path: Optional[str]
    ) -> DetectionLog:
        """创建检测日志"""
        db_obj = DetectionLog(
            filename=filename,
            question=question,
            detections=detections,
            ai_analysis=ai_analysis,
            file_path=file_path
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


    async def get_user_detections_filtered(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        disease_type: Optional[str] = None,
        limit: int = 10000
    ) -> List[DetectionLog]:
        """获取用户的检测记录（支持筛选）"""
        from datetime import datetime
        
        query = select(self.model).where(self.model.user_id == user_id)
        
        if start_date:
            query = query.where(self.model.created_at >= start_date)
        if end_date:
            query = query.where(self.model.created_at <= end_date)
        # disease_type筛选需要根据实际字段调整
        
        query = query.order_by(desc(self.model.created_at)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


# 创建CRUD实例
crud_detection = CRUDDetection(DetectionLog)


# 辅助函数
async def get_user_detections(
    db: AsyncSession,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    disease_type: Optional[str] = None
) -> List[DetectionLog]:
    """获取用户检测记录"""
    from datetime import datetime
    return await crud_detection.get_user_detections_filtered(
        db, user_id, start_date, end_date, disease_type
    )


async def get_detection_statistics(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> dict:
    """获取检测统计数据"""
    from sqlalchemy import func
    
    # 病害类型统计
    disease_stats_query = select(
        DetectionLog.detections,
        func.count(DetectionLog.id).label('count')
    ).where(
        DetectionLog.created_at >= start_date,
        DetectionLog.created_at <= end_date
    ).group_by(DetectionLog.detections)
    
    result = await db.execute(disease_stats_query)
    disease_types = []
    total = 0
    for row in result:
        count = row.count
        total += count
        disease_types.append({
            'disease_type': row.detections or '未知',
            'count': count
        })
    
    # 计算占比
    for item in disease_types:
        item['percentage'] = item['count'] / total if total > 0 else 0
    
    # 时间趋势统计
    time_trend_query = select(
        func.date(DetectionLog.created_at).label('date'),
        func.count(DetectionLog.id).label('count')
    ).where(
        DetectionLog.created_at >= start_date,
        DetectionLog.created_at <= end_date
    ).group_by(func.date(DetectionLog.created_at))
    
    result = await db.execute(time_trend_query)
    time_trends = [{'date': str(row.date), 'count': row.count} for row in result]
    
    return {
        'disease_types': disease_types,
        'time_trends': time_trends
    }

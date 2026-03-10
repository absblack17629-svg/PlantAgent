# -*- coding: utf-8 -*-
"""
Excel导出API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import os

from config.db_conf import get_db
from crud.detection import get_user_detections
from services.export_service import get_export_service
from models.users import User
from routers.deps import get_current_user


router = APIRouter(prefix="/api/export", tags=["导出"])


@router.get("/detection-records")
async def export_detection_records(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    disease_type: Optional[str] = Query(None, description="病害类型"),
    user_id: Optional[int] = Query(None, description="用户ID（可选）"),
    db: AsyncSession = Depends(get_db)
):
    """
    导出检测记录为Excel文件
    
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    - **disease_type**: 病害类型筛选（可选）
    - **user_id**: 用户ID（可选，不提供则导出所有记录）
    """
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        
        # 查询检测记录
        if user_id:
            detections = await get_user_detections(
                db,
                user_id=user_id,
                start_date=start_dt,
                end_date=end_dt,
                disease_type=disease_type
            )
        else:
            # 如果没有指定用户，查询所有记录（需要实现相应的CRUD函数）
            # 这里暂时返回空列表
            detections = []
        
        if not detections:
            raise HTTPException(status_code=404, detail="没有找到检测记录")
        
        # 转换为字典列表
        records = []
        for detection in detections:
            records.append({
                'created_at': detection.created_at,
                'image_name': detection.image_path.split('/')[-1] if detection.image_path else '',
                'disease_type': detection.result.get('disease_type', '') if detection.result else '',
                'confidence': detection.result.get('confidence', 0) if detection.result else 0,
                'treatment_advice': detection.result.get('treatment_advice', '') if detection.result else ''
            })
        
        # 导出Excel
        export_service = get_export_service()
        filepath = await export_service.export_detection_records(
            records=records,
            user_name=f"user_{user_id}" if user_id else "all_users"
        )
        
        # 返回文件
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/statistics")
async def export_statistics(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    导出统计报表为Excel文件
    
    - **start_date**: 开始日期（必填）
    - **end_date**: 结束日期（必填）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 检查是否有管理员权限（可选）
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 查询统计数据（这里需要实现具体的统计逻辑）
        from crud.detection import get_detection_statistics
        
        statistics = await get_detection_statistics(
            db,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # 导出Excel
        export_service = get_export_service()
        filepath = await export_service.export_statistics(
            statistics=statistics
        )
        
        # 返回文件
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

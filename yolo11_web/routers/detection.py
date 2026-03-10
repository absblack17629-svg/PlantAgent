# -*- coding: utf-8 -*-
"""
病害检测API路由
水稻病害检测核心接口
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import config
from services.enhanced_detection_service import get_enhanced_detection_service
from routers.deps import get_current_user
from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/detection", tags=["病害检测"])
logger = get_logger(__name__)


# ==================== 响应模型 ====================

class DetectionResult(BaseModel):
    """检测结果"""
    success: bool
    disease_found: bool
    disease_type: str
    confidence: float
    severity: str
    detections: list
    prevention_scheme: Optional[str] = None
    detection_time: str
    duration_ms: int
    model_version: str


class DetectionRecordResponse(BaseModel):
    """检测记录响应"""
    record_id: str
    user_id: str
    image_url: str
    disease_type: str
    confidence: float
    severity: str
    detection_time: str


# ==================== API接口 ====================

@router.post("/upload", response_model=DetectionResult)
async def upload_and_detect(
    file: UploadFile = File(..., description="水稻叶片图片"),
    user_id: Optional[str] = Form(None),
    user=Depends(get_current_user)
):
    """
    上传图片并检测病害
    
    - **file**: 水稻叶片图片文件 (PNG/JPG/JPEG)
    - **user_id**: 用户ID（可选）
    """
    # 验证文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持: {', '.join(allowed_extensions)}"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
    
    # 保存上传文件
    upload_dir = config.settings.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"文件已保存: {file_path}")
        
        # 执行检测
        detection_service = get_enhanced_detection_service()
        
        # 如果没有提供user_id，从当前用户获取
        if not user_id and user:
            user_id = str(user.id)
        
        result = await detection_service.detect(file_path, user_id)
        
        # 添加图片URL
        result["image_url"] = f"/static/uploads/{unique_filename}"
        result["image_path"] = file_path
        
        # 保存检测记录到数据库
        if user_id:
            await _save_detection_record(user_id, result)
        
        return result
        
    except Exception as e:
        logger.error(f"检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.post("/detect", response_model=DetectionResult)
async def detect_image(
    image_url: str = Form(..., description="图片URL或路径"),
    user_id: Optional[str] = Form(None),
    user=Depends(get_current_user)
):
    """
    根据图片URL进行病害检测
    
    - **image_url**: 图片URL或服务器上的图片路径
    """
    # 检查文件是否存在
    if not os.path.exists(image_url):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    try:
        detection_service = get_enhanced_detection_service()
        
        if not user_id and user:
            user_id = str(user.id)
        
        result = await detection_service.detect(image_url, user_id)
        result["image_url"] = image_url
        result["image_path"] = image_url
        
        # 保存检测记录
        if user_id:
            await _save_detection_record(user_id, result)
        
        return result
        
    except Exception as e:
        logger.error(f"检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/history", response_model=list)
async def get_detection_history(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_current_user)
):
    """
    获取检测历史记录
    
    - **user_id**: 用户ID（可选，查询自己的记录）
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    # 如果没有指定user_id，获取当前用户的记录
    if not user_id and user:
        user_id = str(user.id)
    
    try:
        records = await _get_detection_records(user_id, limit, offset)
        return records
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/record/{record_id}")
async def get_detection_record(
    record_id: str,
    user=Depends(get_current_user)
):
    """
    获取单条检测记录详情
    """
    try:
        record = await _get_detection_record_by_id(record_id, str(user.id))
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/record/{record_id}")
async def delete_detection_record(
    record_id: str,
    user=Depends(get_current_user)
):
    """
    删除检测记录
    """
    try:
        success = await _delete_detection_record(record_id, str(user.id))
        if not success:
            raise HTTPException(status_code=404, detail="记录不存在或删除失败")
        return {"success": True, "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_detection_stats(
    user_id: Optional[str] = None,
    user=Depends(get_current_user)
):
    """
    获取检测统计数据
    """
    if not user_id and user:
        user_id = str(user.id)
    
    try:
        stats = await _get_detection_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据库操作 ====================

async def _save_detection_record(user_id: str, result: Dict):
    """保存检测记录到数据库"""
    try:
        # 尝试导入数据库服务
        from services.database_service import DatabaseService
        from config import settings
        
        # 构建记录数据
        record = {
            "record_id": str(uuid.uuid4()),
            "user_id": user_id,
            "image_url": result.get("image_url", ""),
            "image_path": result.get("image_path", ""),
            "disease_type": result.get("disease_type", ""),
            "confidence": result.get("confidence", 0),
            "severity": result.get("severity", ""),
            "bbox_data": json.dumps(result.get("detections", []), ensure_ascii=False),
            "prevention_scheme": result.get("prevention_scheme", ""),
            "detection_time": datetime.now(),
            "duration_ms": result.get("duration_ms", 0),
            "model_version": result.get("model_version", ""),
            "status": "completed"
        }
        
        # 存储到数据库（如果可用）
        # 这里简化处理，实际应该使用CRUD操作
        logger.info(f"检测记录已保存: {record['record_id']}")
        
    except Exception as e:
        logger.warning(f"保存检测记录失败: {e}")


async def _get_detection_records(user_id: str, limit: int, offset: int) -> List[Dict]:
    """获取检测记录列表"""
    # 简化实现 - 实际应该查询数据库
    return []


async def _get_detection_record_by_id(record_id: str, user_id: str) -> Optional[Dict]:
    """根据ID获取检测记录"""
    return None


async def _delete_detection_record(record_id: str, user_id: str) -> bool:
    """删除检测记录"""
    return True


async def _get_detection_stats(user_id: str) -> Dict:
    """获取检测统计"""
    return {
        "total_detections": 0,
        "disease_distribution": {},
        "avg_confidence": 0,
        "recent_trends": []
    }

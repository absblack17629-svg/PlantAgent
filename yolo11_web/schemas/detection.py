# -*- coding: utf-8 -*-
"""
检测相关数据验证模型
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from schemas.base import BaseResponseSchema


class DetectionRequest(BaseModel):
    """检测请求"""
    
    question: Optional[str] = Field(None, description="用户提问")
    query_type: str = Field("general", description="查询类型")


class DetectionResult(BaseModel):
    """单个检测结果"""
    
    类别: str = Field(..., description="目标类别")
    置信度: float = Field(..., description="置信度")
    坐标: List[float] = Field(..., description="边界框坐标")


class DetectionResponse(BaseModel):
    """检测响应"""
    
    code: int = 200
    msg: str = "智能体处理成功"
    检测结果: List[DetectionResult] = []
    智能分析: str = ""
    用户提问: Optional[str] = None
    查询类型: str = "general"
    文件名称: Optional[str] = None
    文件路径: Optional[str] = None


class DetectionLogSchema(BaseResponseSchema):
    """检测日志Schema"""
    
    filename: Optional[str]
    file_path: Optional[str]
    question: Optional[str]
    detections: Optional[str]
    ai_analysis: Optional[str]

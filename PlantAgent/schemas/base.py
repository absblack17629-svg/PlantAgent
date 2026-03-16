# -*- coding: utf-8 -*-
"""
Pydantic基础模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """基础Schema"""
    
    model_config = ConfigDict(from_attributes=True)


class BaseResponseSchema(BaseSchema):
    """基础响应Schema"""
    
    id: int
    created_at: datetime
    updated_at: datetime


class ResponseModel(BaseModel):
    """统一响应模型"""
    
    code: int = 200
    msg: str = "success"
    data: Optional[dict] = None

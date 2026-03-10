# -*- coding: utf-8 -*-
"""
自定义异常和全局异常处理
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class NotFoundException(BusinessException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "资源未找到"):
        super().__init__(404, message)


class BadRequestException(BusinessException):
    """请求参数错误异常"""
    
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(400, message)


class UnauthorizedException(BusinessException):
    """未授权异常"""
    
    def __init__(self, message: str = "未授权访问"):
        super().__init__(401, message)


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器"""
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "msg": exc.message, "data": None}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "msg": "请求参数验证失败",
            "data": {"errors": exc.errors()}
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "msg": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )

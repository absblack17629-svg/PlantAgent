# -*- coding: utf-8 -*-
"""
监控API路由

提供系统监控、告警和健康检查的API端点。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.monitoring import (
    get_system_monitor,
    get_alert_manager,
    get_health_checker
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/metrics/current", summary="获取当前系统指标")
async def get_current_metrics() -> Dict[str, Any]:
    """获取当前系统指标
    
    Returns:
        当前系统指标
    """
    try:
        monitor = get_system_monitor()
        metrics = monitor.get_current_metrics()
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"获取当前指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/history", summary="获取历史指标")
async def get_metrics_history(
    limit: int = Query(10, ge=1, le=100, description="返回数量")
) -> Dict[str, Any]:
    """获取历史系统指标
    
    Args:
        limit: 返回数量限制
        
    Returns:
        历史指标列表
    """
    try:
        monitor = get_system_monitor()
        history = monitor.get_metrics_history(limit=limit)
        
        return {
            "success": True,
            "data": history,
            "count": len(history)
        }
    
    except Exception as e:
        logger.error(f"获取历史指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/summary", summary="获取监控摘要")
async def get_monitoring_summary() -> Dict[str, Any]:
    """获取监控摘要
    
    Returns:
        监控摘要数据
    """
    try:
        monitor = get_system_monitor()
        summary = monitor.get_summary()
        
        return {
            "success": True,
            "data": summary
        }
    
    except Exception as e:
        logger.error(f"获取监控摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/active", summary="获取活跃告警")
async def get_active_alerts() -> Dict[str, Any]:
    """获取活跃告警
    
    Returns:
        活跃告警列表
    """
    try:
        alert_manager = get_alert_manager()
        active_alerts = alert_manager.get_active_alerts()
        
        return {
            "success": True,
            "data": [alert.to_dict() for alert in active_alerts],
            "count": len(active_alerts)
        }
    
    except Exception as e:
        logger.error(f"获取活跃告警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/history", summary="获取告警历史")
async def get_alert_history(
    limit: int = Query(50, ge=1, le=200, description="返回数量")
) -> Dict[str, Any]:
    """获取告警历史
    
    Args:
        limit: 返回数量限制
        
    Returns:
        告警历史列表
    """
    try:
        alert_manager = get_alert_manager()
        history = alert_manager.get_alert_history(limit=limit)
        
        return {
            "success": True,
            "data": history,
            "count": len(history)
        }
    
    except Exception as e:
        logger.error(f"获取告警历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/stats", summary="获取告警统计")
async def get_alert_stats() -> Dict[str, Any]:
    """获取告警统计
    
    Returns:
        告警统计数据
    """
    try:
        alert_manager = get_alert_manager()
        stats = alert_manager.get_alert_stats()
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"获取告警统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/resolve/{rule_name}", summary="解决告警")
async def resolve_alert(rule_name: str) -> Dict[str, Any]:
    """解决指定规则的告警
    
    Args:
        rule_name: 规则名称
        
    Returns:
        解决结果
    """
    try:
        alert_manager = get_alert_manager()
        count = alert_manager.resolve_alert(rule_name)
        
        return {
            "success": True,
            "message": f"已解决 {count} 条告警",
            "resolved_count": count
        }
    
    except Exception as e:
        logger.error(f"解决告警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="健康检查")
async def health_check() -> Dict[str, Any]:
    """执行健康检查
    
    Returns:
        健康检查报告
    """
    try:
        health_checker = get_health_checker()
        report = await health_checker.check_all()
        
        return {
            "success": True,
            "data": report
        }
    
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/last", summary="获取上次健康检查结果")
async def get_last_health_check() -> Dict[str, Any]:
    """获取上次健康检查结果
    
    Returns:
        上次健康检查结果
    """
    try:
        health_checker = get_health_checker()
        results = health_checker.get_last_check_results()
        
        if not results:
            return {
                "success": True,
                "message": "暂无健康检查记录",
                "data": {}
            }
        
        return {
            "success": True,
            "data": results
        }
    
    except Exception as e:
        logger.error(f"获取健康检查结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="系统状态概览")
async def get_system_status() -> Dict[str, Any]:
    """获取系统状态概览
    
    Returns:
        系统状态概览
    """
    try:
        monitor = get_system_monitor()
        alert_manager = get_alert_manager()
        health_checker = get_health_checker()
        
        # 获取各项数据
        current_metrics = monitor.get_current_metrics()
        alert_stats = alert_manager.get_alert_stats()
        health_results = health_checker.get_last_check_results()
        
        # 构建状态概览
        status = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_percent": current_metrics.get("cpu", {}).get("percent", 0),
                "memory_percent": current_metrics.get("memory", {}).get("percent", 0),
                "disk_percent": current_metrics.get("disk", {}).get("percent", 0)
            },
            "alerts": {
                "active": alert_stats.get("active", 0),
                "total": alert_stats.get("total", 0)
            },
            "health": {
                "components_checked": len(health_results),
                "last_check": list(health_results.values())[0].get("checked_at") if health_results else None
            }
        }
        
        return {
            "success": True,
            "data": status
        }
    
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

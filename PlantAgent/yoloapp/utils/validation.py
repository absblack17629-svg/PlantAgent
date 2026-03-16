# -*- coding: utf-8 -*-
"""
输入验证模块

简单的验证函数，不需要完整的 Agent
"""

import os
from typing import Dict, Optional, Tuple
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


def validate_input(
    intent: str, user_input: str, image_path: Optional[str] = None
) -> Tuple[bool, str, Dict]:
    """
    验证用户输入

    Args:
        intent: 用户意图
        user_input: 用户输入
        image_path: 图片路径

    Returns:
        (is_valid, message, validation_result)
    """
    issues = []
    validation_result = {
        "intent": intent,
        "has_image": bool(image_path),
        "has_question": bool(user_input),
        "needs_clarification": False,
        "clarification_message": "",
    }

    # 检测意图需要的验证
    if intent == "detect":
        # 检测意图需要图片
        if not image_path:
            issues.append("需要上传图片才能进行病害检测")
            validation_result["needs_clarification"] = True
        elif not os.path.exists(image_path):
            issues.append(f"图片文件不存在: {image_path}")
            validation_result["needs_clarification"] = True
        else:
            # 检查文件扩展名
            valid_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in valid_exts:
                issues.append(f"不支持的图片格式: {ext}")
                validation_result["needs_clarification"] = True

    elif intent == "query":
        # 查询意图需要问题
        if not user_input or len(user_input.strip()) < 2:
            issues.append("请输入您想咨询的问题")
            validation_result["needs_clarification"] = True

    elif intent == "chat":
        # 聊天意图一般不需要特殊验证
        pass

    # 生成消息
    if issues:
        is_valid = False
        message = "; ".join(issues)
        validation_result["clarification_message"] = message
    else:
        is_valid = True
        message = "输入验证通过"

    logger.info(f"[验证] {'通过' if is_valid else '需澄清'}: {message}")

    return is_valid, message, validation_result


def validate_result(
    tool_results: list, expected_tool: Optional[str] = None
) -> Tuple[bool, str, Dict]:
    """
    验证工具执行结果

    Args:
        tool_results: 工具执行结果列表
        expected_tool: 期望的工具名

    Returns:
        (is_valid, message, validation_result)
    """
    validation_result = {
        "has_results": bool(tool_results),
        "result_count": len(tool_results),
        "success_count": 0,
        "failed_count": 0,
        "needs_retry": False,
    }

    if not tool_results:
        return False, "没有执行任何工具", validation_result

    # 统计成功/失败
    for result in tool_results:
        if isinstance(result, dict):
            if result.get("success"):
                validation_result["success_count"] += 1
            else:
                validation_result["failed_count"] += 1

    # 检查是否有失败
    if validation_result["failed_count"] > 0:
        validation_result["needs_retry"] = True
        return (
            False,
            f"有 {validation_result['failed_count']} 个工具执行失败",
            validation_result,
        )

    return True, "结果验证通过", validation_result

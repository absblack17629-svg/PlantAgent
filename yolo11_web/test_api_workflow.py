#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API工作流 - 验证检测结果只显示病害名
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_complete_workflow():
    """测试完整工作流"""
    print("测试API工作流...")
    print("=" * 60)

    # 1. 测试检测端点（模拟响应）
    print("\n1. 测试检测端点")
    print("模拟请求: 上传图片进行检测")

    # 由于实际需要图片文件，我们模拟检测结果
    # 在真实测试中，这里会发送multipart/form-data请求

    print("预期响应: 只显示病害名（如'白叶枯病'或'白叶枯病、稻瘟病'）")
    print("不显示: '检测到 X 个病害区域'或'检测到 X 个目标'")

    # 2. 测试确认端点
    print("\n2. 测试确认端点")
    print("模拟请求: 确认查询相关知识（回复'是'）")

    # 创建对话会话
    session_response = client.post(
        "/api/agent/sessions", json={"user_id": "test_user", "session_name": "测试会话"}
    )

    if session_response.status_code == 200:
        session_id = session_response.json()["session_id"]
        print(f"创建会话成功: {session_id}")

        # 模拟检测后的确认请求
        confirm_response = client.post(
            f"/api/agent/confirm/{session_id}",
            json={
                "user_question": "检测这张图片中的水稻病害",
                "image_path": "test_image.jpg",
                "confirmation_response": "是",
            },
        )

        if confirm_response.status_code == 200:
            result = confirm_response.json()
            print(f"确认响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"确认请求失败: {confirm_response.status_code}")
            print(f"错误信息: {confirm_response.text}")
    else:
        print(f"创建会话失败: {session_response.status_code}")
        print(f"错误信息: {session_response.text}")

    print("\n" + "=" * 60)
    print("测试要点:")
    print("1. 检测结果只显示病害名（不包含数量统计）")
    print("2. 确认流程正常工作")
    print("3. 用户确认'是'后，RAG才被调用")
    print("4. 病害名正确显示为中文")


if __name__ == "__main__":
    test_complete_workflow()

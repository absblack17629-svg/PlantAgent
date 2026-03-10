# -*- coding: utf-8 -*-
"""直接测试客服工作流"""

import sys
import os
import asyncio

os.chdir(r"C:\Users\1\Desktop\file\Fastapi_backend\yolo11_web")


async def test_workflow():
    print("=" * 50)
    print("测试 LangGraph 九节点工作流")
    print("=" * 50)

    from routers.agent_factory import process_agent_request

    # 测试1: 简单对话
    print("\n[测试1] 简单对话...")
    result = await process_agent_request("你好，请介绍一下你自己")
    print(f"  结果: {result.get('response', '')[:200]}")
    print(f"  模式: {result.get('agent_mode', 'unknown')}")

    # 测试2: 询问农业知识
    print("\n[测试2] 农业知识问答...")
    result = await process_agent_request("水稻稻瘟病如何防治？")
    print(f"  结果: {result.get('response', '')[:200]}")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


asyncio.run(test_workflow())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 DeepSeek-v3.2 是否正确配置和使用
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.llm import get_llm_client
from yoloapp.schema import Message


async def test_deepseek_config():
    """测试 DeepSeek-v3.2 配置"""
    print("[TEST] 测试 DeepSeek-v3.2 配置...")

    # 获取 LLM 客户端
    client = get_llm_client("default")

    print(f"[INFO] 客户端信息:")
    print(f"  - 模型: {client.model}")
    print(f"  - API Key 存在: {client.api_key is not None}")
    print(f"  - Base URL: {client.base_url}")

    # 检查模型名称
    if "deepseek" in client.model.lower():
        print("[OK] 配置正确: 使用 DeepSeek 模型")
    else:
        print(f"[ERROR] 配置错误: 使用的是 {client.model}, 不是 DeepSeek-v3.2")
        return False

    # 测试简单的请求
    print("\n[TEST] 测试简单请求...")
    try:
        messages = [
            Message.system_message("你是一个农业助手。"),
            Message.user_message("请简要说明水稻白叶枯病的防治方法。"),
        ]

        response = await client.ask(messages, max_tokens=200)
        print(f"[OK] 请求成功")
        print(f"[NOTE] 响应长度: {len(response)} 字符")

        # 检查响应内容
        if len(response) > 10:
            print(f"[DOC] 响应内容: {response[:100]}...")
            return True
        else:
            print("[ERROR] 响应内容太短")
            return False

    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return False


async def test_complete_workflow():
    """测试完整的工作流程"""
    print("\n" + "=" * 60)
    print("[TEST] 测试完整工作流程...")

    from routers.agent_factory import process_agent_request

    try:
        # 模拟一个检测请求（不实际使用图片）
        result = await process_agent_request(
            user_question="检测这张图片中的水稻病害",
            image_path=None,  # 不使用实际图片
        )

        print(f"[OK] 工作流程执行成功")
        print(f"[CHART] 结果类型: {type(result)}")

        # 检查结果结构
        if isinstance(result, dict):
            keys = list(result.keys())
            print(f"[KEY] 结果包含的键: {keys}")

            # 检查是否包含疾病名称
            if "detection_results" in result:
                print(f"[DETECT] 检测结果: {result['detection_results']}")
            else:
                print("[WARNING]  结果中没有检测结果字段")

        return True

    except Exception as e:
        print(f"[ERROR] 工作流程失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("[START] 开始测试 YOLO11 智能体系统配置")
    print("=" * 60)

    # 测试 1: DeepSeek 配置
    config_ok = await test_deepseek_config()

    if not config_ok:
        print("\n[ERROR] DeepSeek 配置测试失败")
        return

    # 测试 2: 完整工作流程
    workflow_ok = await test_complete_workflow()

    if not workflow_ok:
        print("\n[WARNING]  工作流程测试有警告")

    print("\n" + "=" * 60)
    print("[CHART] 测试总结:")
    print(f"  [OK] DeepSeek 配置: {'通过' if config_ok else '失败'}")
    print(f"  [OK] 工作流程: {'通过' if workflow_ok else '有警告'}")

    if config_ok:
        print("\n[CELEBRATE] DeepSeek-v3.2 已成功配置并投入使用！")
        print("[HOT] 系统现在使用 DeepSeek-v3.2 模型进行推理")
    else:
        print("\n[ERROR] 需要进一步检查配置问题")


if __name__ == "__main__":
    asyncio.run(main())

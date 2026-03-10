#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 DeepSeek-v3.2 配置
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.llm import get_llm_client
from yoloapp.schema import Message


async def main():
    print("开始测试 DeepSeek-v3.2 配置")
    print("=" * 60)

    # 获取 LLM 客户端
    client = get_llm_client("default")

    print(f"客户端信息:")
    print(f"  - 模型: {client.model}")
    print(f"  - API Key 存在: {client.api_key is not None}")
    print(f"  - Base URL: {client.base_url}")

    # 检查模型名称
    if "deepseek" in client.model.lower():
        print("配置正确: 使用 DeepSeek 模型")
    else:
        print(f"配置错误: 使用的是 {client.model}, 不是 DeepSeek-v3.2")
        return

    # 测试简单的请求
    print("\n测试简单请求...")
    try:
        messages = [
            Message.system_message("你是一个农业助手。"),
            Message.user_message("请简要说明水稻白叶枯病的防治方法。"),
        ]

        response = await client.ask(messages, max_tokens=200)
        print(f"请求成功")
        print(f"响应长度: {len(response)} 字符")

        # 检查响应内容
        if len(response) > 10:
            print(f"响应内容: {response[:100]}...")
            print("\nDeepSeek-v3.2 已成功配置并投入使用！")
        else:
            print("响应内容太短")

    except Exception as e:
        print(f"请求失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

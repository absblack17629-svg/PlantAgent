#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试API连接性
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI


async def test_api_connection():
    """测试API连接"""
    print("测试API连接性")
    print("=" * 60)

    # 从环境变量获取配置
    api_key = os.getenv("ZHIPU_API_KEY", "test-key")
    base_url = os.getenv("ZHIPU_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("ZHIPU_MODEL", "deepseek-v3.2")

    print(f"API端点: {base_url}")
    print(f"模型: {model}")
    print(f"API密钥前10位: {api_key[:10]}...")

    try:
        # 创建客户端
        client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=10)

        print("\n测试连接...")
        try:
            # 尝试调用API
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个测试助手。"},
                        {"role": "user", "content": "请回复'测试成功'"},
                    ],
                    max_tokens=10,
                    temperature=0.1,
                ),
                timeout=8,
            )

            print("状态: API连接成功")
            print(f"响应: {response.choices[0].message.content}")
            return True, "连接成功"

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            print(f"状态: API调用失败")
            print(f"错误类型: {error_type}")
            print(f"错误信息: {error_msg[:100]}...")

            # 分析错误类型
            if "401" in error_msg or "authentication" in error_msg.lower():
                return False, "API密钥无效"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return False, "连接超时，API端点可能不可达"
            elif "404" in error_msg:
                return False, "API端点不存在或模型不可用"
            else:
                return False, f"API错误: {error_type}"

    except Exception as e:
        print(f"状态: 客户端初始化失败")
        print(f"错误: {e}")
        return False, f"客户端初始化失败: {type(e).__name__}"


async def main():
    """主测试函数"""
    success, message = await test_api_connection()

    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"成功: {success}")
    print(f"消息: {message}")

    print("\n分析:")
    if success:
        print("- DeepSeek API连接正常")
        print("- API端点: https://api.deepseek.com 可用")
        print("- 模型: deepseek-v3.2 可用")
    else:
        if "API密钥无效" in message:
            print("- API端点可达，但API密钥无效")
            print("- DeepSeek API服务存在，需要有效API密钥")
        elif "连接超时" in message:
            print("- API端点可能不可达")
            print("- 检查网络连接或API端点URL是否正确")
        elif "API端点不存在" in message:
            print("- 指定的API端点可能不存在")
            print("- 检查base_url配置: https://api.deepseek.com")
        else:
            print(f"- 具体错误: {message}")


if __name__ == "__main__":
    asyncio.run(main())

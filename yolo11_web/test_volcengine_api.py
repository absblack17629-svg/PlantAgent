#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试火山引擎API连接性
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI


async def test_volcengine_api():
    """测试火山引擎API连接"""
    print("测试火山引擎API连接性")
    print("=" * 60)

    # 从环境变量获取配置
    api_key = os.getenv("ZHIPU_API_KEY", "cace85f4-6ae0-47fa-a195-6a42b942d769")
    base_url = os.getenv(
        "ZHIPU_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3"
    )
    model = os.getenv("ZHIPU_MODEL", "deepseek-v3.2")

    print(f"API端点: {base_url}")
    print(f"模型: {model}")
    print(f"API密钥: {api_key}")

    try:
        # 创建客户端
        client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=30)

        print("\n1. 测试简单文本生成...")
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个农业专家助手。"},
                        {
                            "role": "user",
                            "content": "水稻病害有哪些常见类型？请简要回答。",
                        },
                    ],
                    max_tokens=100,
                    temperature=0.7,
                ),
                timeout=20,
            )

            print("状态: API调用成功")
            print(f"响应: {response.choices[0].message.content}")
            print(f"使用token数: {response.usage.total_tokens}")
            return True, "API连接成功"

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            print(f"状态: API调用失败")
            print(f"错误类型: {error_type}")

            # 详细错误分析
            if "401" in error_msg or "authentication" in error_msg.lower():
                print("错误: API密钥无效或未授权")
                return False, "API密钥无效"
            elif "404" in error_msg:
                print("错误: API端点或模型不存在")
                return False, "API端点或模型不存在"
            elif "timeout" in error_msg.lower():
                print("错误: 连接超时")
                return False, "连接超时"
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                print("错误: 模型不存在")
                return False, "模型不存在"
            else:
                print(f"错误详情: {error_msg[:200]}")
                return False, f"API错误: {error_type}"

    except Exception as e:
        print(f"状态: 客户端初始化失败")
        print(f"错误: {e}")
        return False, f"客户端初始化失败: {type(e).__name__}"


async def test_with_different_models():
    """测试不同模型的兼容性"""
    print("\n" + "=" * 60)
    print("测试不同模型的兼容性...")

    models_to_test = ["deepseek-v3.2", "glm-4.7", "glm-4-flash", "deepseek-chat"]

    api_key = os.getenv("ZHIPU_API_KEY", "cace85f4-6ae0-47fa-a195-6a42b942d769")
    base_url = os.getenv(
        "ZHIPU_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3"
    )

    for model in models_to_test:
        print(f"\n测试模型: {model}")
        try:
            client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=10)

            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "测试"}],
                    max_tokens=10,
                ),
                timeout=8,
            )
            print(f"  {model}: 可用")
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"  {model}: 不可用 (模型不存在)")
            elif "401" in error_msg:
                print(f"  {model}: 认证失败")
            else:
                print(f"  {model}: 错误 ({type(e).__name__})")


async def main():
    """主测试函数"""
    print("火山引擎API测试")
    print("=" * 60)

    # 测试API连接
    success, message = await test_volcengine_api()

    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"成功: {success}")
    print(f"消息: {message}")

    if not success:
        print("\n问题诊断:")
        if "API密钥无效" in message:
            print("1. API密钥可能无效或已过期")
            print("2. 检查API密钥是否正确")
            print("3. 确认API密钥有访问权限")
        elif "模型不存在" in message:
            print("1. 模型名称可能不正确")
            print("2. 当前配置模型: deepseek-v3.2")
            print("3. 火山引擎可能不支持此模型")
            # 测试其他可能的模型
            await test_with_different_models()
        elif "连接超时" in message:
            print("1. 网络连接问题")
            print("2. API端点可能无法访问")
            print("3. 防火墙或网络限制")
        elif "API端点不存在" in message:
            print("1. API端点URL可能不正确")
            print("2. 当前配置: https://ark.cn-beijing.volces.com/api/coding/v3")
            print("3. 检查URL是否正确")

    print("\n" + "=" * 60)
    print("建议:")
    if success:
        print("1. API配置正确，可以正常使用")
        print("2. 系统将使用deepseek-v3.2模型")
        print("3. 确认流程应该能正常工作")
    else:
        print("1. 检查API密钥的有效性")
        print("2. 确认模型名称是否正确")
        print("3. 如果API不可用，系统会使用降级响应")
        print("4. 降级响应包含实用的农业知识")


if __name__ == "__main__":
    asyncio.run(main())

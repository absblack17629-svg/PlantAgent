#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek API连接性
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI, APIError, APITimeoutError


async def test_deepseek_api():
    """测试DeepSeek API连接"""
    print("测试DeepSeek API连接性...")
    print("=" * 60)

    # 从环境变量获取配置
    api_key = os.getenv("ZHIPU_API_KEY", "sk-cace85f4-6ae0-47fa-a195-6a42b942d769")
    base_url = os.getenv("ZHIPU_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("ZHIPU_MODEL", "deepseek-v3.2")

    print(f"API端点: {base_url}")
    print(f"模型: {model}")
    print(f"API密钥: {api_key[:10]}... (前10位)")

    try:
        # 创建客户端
        client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=30)

        print("\n1. 测试简单文本生成...")
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个测试助手。"},
                        {
                            "role": "user",
                            "content": "请回复'Hello, World!'来测试连接。",
                        },
                    ],
                    max_tokens=20,
                    temperature=0.7,
                ),
                timeout=15,
            )

            print(f"[OK] API连接成功！")
            print(f"响应: {response.choices[0].message.content}")
            return True

        except APITimeoutError as e:
            print(f"[TIME] API超时: {e}")
            print("可能原因: 网络连接问题或API端点不可达")
            return False
        except APIError as e:
            print(f"[RED] API错误: {e}")
            print("可能原因: API密钥无效或模型不可用")
            return False
        except Exception as e:
            print(f"[ERROR] 未知错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            return False

    except Exception as e:
        print(f"[ERROR] 客户端初始化失败: {e}")
        return False


async def test_local_fallback():
    """测试本地降级响应"""
    print("\n" + "=" * 60)
    print("测试本地降级响应...")

    # 模拟降级响应
    fallback_response = """由于API连接问题，我无法获取实时信息。以下是基于本地知识的回复：

**水稻病害防治建议：**

1. **白叶枯病防治**
   - 及时清除病株
   - 使用20%叶枯唑可湿性粉剂500倍液喷雾

2. **稻瘟病防治**
   - 选择抗病品种
   - 使用75%三环唑可湿性粉剂2000倍液

3. **综合管理**
   - 合理密植，保持通风透光
   - 科学施肥，避免偏施氮肥
   - 定期巡查，早发现早防治"""

    print("[OK] 本地降级响应可用")
    print(f"响应长度: {len(fallback_response)} 字符")
    return fallback_response


async def main():
    """主测试函数"""
    print("DeepSeek API连接测试")
    print("=" * 60)

    # 测试API连接
    api_success = await test_deepseek_api()

    if not api_success:
        print("\n[WARNING] API连接失败，测试降级模式...")
        fallback = await test_local_fallback()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("建议:")
    if api_success:
        print("- DeepSeek API连接正常")
    else:
        print("- 需要检查API密钥和网络连接")
        print("- 系统已配置降级响应，可以继续使用")


if __name__ == "__main__":
    asyncio.run(main())

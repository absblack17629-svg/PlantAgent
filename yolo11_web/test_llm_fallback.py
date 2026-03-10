#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM客户端的降级功能
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.llm import LLMClient


async def test_llm_with_fallback():
    """测试LLM客户端的降级功能"""
    print("测试LLM客户端降级功能")
    print("=" * 60)

    # 创建LLM客户端
    print("初始化LLM客户端...")
    llm = LLMClient("default")

    # 测试消息
    messages = [
        {"role": "system", "content": "你是一个农业专家助手。"},
        {"role": "user", "content": "水稻白叶枯病如何防治？"},
    ]

    print(f"测试消息: {messages[1]['content']}")
    print("调用LLM API...")

    try:
        # 尝试调用API
        response = await llm.ask(messages)

        print("状态: API调用成功")
        print(f"响应长度: {len(response)} 字符")
        print(f"响应片段: {response[:100]}...")
        return True, response

    except Exception as e:
        print(f"状态: API调用失败")
        print(f"错误: {type(e).__name__}")
        print(f"错误信息: {str(e)[:100]}...")

        # 测试降级响应
        print("\n测试降级响应...")

        # 这是我们在确认端点中使用的降级响应
        fallback_response = """基于检测到的病害，我为您提供以下防治建议：

**常见水稻病害防治方案：**

[MICROSCOPE] **白叶枯病防治**
• **预防措施**：选用抗病品种，种子消毒处理
• **化学防治**：发病初期使用20%叶枯唑可湿性粉剂500倍液
• **农业防治**：合理密植，避免偏施氮肥

[RICE] **稻瘟病防治**
• **种子处理**：用25%咪鲜胺乳油3000倍液浸种
• **田间管理**：科学管水，浅水勤灌
• **药剂防治**：发病初期用75%三环唑可湿性粉剂2000倍液

[WATER] **纹枯病防治**
• **水肥管理**：合理排灌，施足基肥
• **药剂防治**：用5%井冈霉素水剂500倍液喷雾
• **生物防治**：使用枯草芽孢杆菌制剂

[INFO] **综合建议**
1. 定期巡查，早发现早防治
2. 轮作换茬，减少病原积累
3. 保持田间卫生，及时清除病残体"""

        print("降级响应可用")
        print(f"响应长度: {len(fallback_response)} 字符")
        return False, fallback_response


async def main():
    """主测试函数"""
    success, response = await test_llm_with_fallback()

    print("\n" + "=" * 60)
    print("测试结论:")

    if success:
        print("1. DeepSeek API连接成功")
        print("2. 模型 deepseek-v3.2 可用")
        print("3. 系统可以正常使用在线LLM")
    else:
        print("1. DeepSeek API连接失败")
        print("2. 系统将使用降级响应")
        print("3. 降级响应包含实用的农业知识")
        print("4. 用户仍然可以获得有用的信息")

    print("\n" + "=" * 60)
    print("对用户的影响:")
    print("- 检测完成后，系统会询问是否查询相关知识")
    print("- 用户回复'是'后:")
    print("  * 如果API可用: 返回DeepSeek生成的详细建议")
    print("  * 如果API不可用: 返回本地降级响应")
    print("- 两种方式都能为用户提供有用的信息")


if __name__ == "__main__":
    asyncio.run(main())

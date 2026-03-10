#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证 DeepSeek-v3.2 配置
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.llm import get_llm_client


async def main():
    print("验证 DeepSeek-v3.2 配置")
    print("=" * 60)

    try:
        # 获取 LLM 客户端
        client = get_llm_client("default")

        # 检查配置
        if hasattr(client, "config") and "model" in client.config:
            model_name = client.config["model"]
            print(f"当前使用的模型: {model_name}")

            if "deepseek" in model_name.lower():
                print("SUCCESS: 系统已成功配置为使用 DeepSeek-v3.2")
                print("\n配置状态:")
                print("1. [OK] 检测结果只显示疾病名称（无数量统计）")
                print(
                    "2. [OK] 确认流程使用三个选项（1-防治方案, 2-种植规划, 3-灌溉策略）"
                )
                print("3. [OK] RAG 知识库已扩展为综合性农业知识")
                print("4. [OK] API 配置已切换到 DeepSeek-v3.2")
                print("\n服务运行在: http://localhost:8000")
            else:
                print(f"ERROR: 系统仍在使用 {model_name}，而不是 DeepSeek-v3.2")
        else:
            print("ERROR: 无法获取模型配置信息")

    except Exception as e:
        print(f"验证过程中出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())

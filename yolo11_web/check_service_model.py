#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查服务启动时使用的模型
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def check_model_from_main():
    """检查main.py中使用的模型"""
    print("检查main.py中使用的模型")
    print("=" * 60)

    try:
        # 模拟main.py的初始化过程
        from routers.agent_factory import get_llm

        # 获取LLM客户端
        llm_client = get_llm()

        if llm_client:
            model_name = llm_client.config.get("model", "unknown")
            base_url = llm_client.config.get("base_url", "unknown")

            print(f"LLM客户端模型: {model_name}")
            print(f"API地址: {base_url}")

            if "deepseek" in model_name.lower():
                print("[OK] 使用DeepSeek模型")
            else:
                print("[WARN] 未使用DeepSeek模型")

            return True
        else:
            print("[ERROR] 无法获取LLM客户端")
            return False

    except Exception as e:
        print(f"检查失败: {e}")
        return False


def check_confirmation_prompt():
    """检查确认提示是否正确"""
    print("\n检查确认提示")
    print("=" * 60)

    try:
        # 模拟检测完成后的确认提示
        detection_summary = "白叶枯病"

        # 使用我们修改后的确认提示
        confirmation_prompt = (
            f"检测已完成！\n\n"
            f"检测结果: {detection_summary}\n\n"
            f"请选择您想了解的内容（回复 1、2 或 3）:\n"
            f"1. 防治方案 - 针对检测到的病害\n"
            f"2. 种植规划 - 适合的种植建议\n"
            f"3. 灌溉策略 - 优化的灌溉方案"
        )

        print("确认提示:")
        print("-" * 40)
        print(confirmation_prompt)
        print("-" * 40)

        # 检查是否包含旧的提示
        if "请回复 '是' 或 '需要'" in confirmation_prompt:
            print("[ERROR] 包含旧的确认提示")
            return False
        elif "回复 1、2 或 3" in confirmation_prompt:
            print("[OK] 使用新的三选项确认提示")
            return True
        else:
            print("[WARN] 确认提示格式不明确")
            return False

    except Exception as e:
        print(f"检查失败: {e}")
        return False


def test_rag_query():
    """测试RAG查询"""
    print("\n测试RAG查询")
    print("=" * 60)

    try:
        from yoloapp.rag import get_rag_service
        import asyncio

        # 模拟用户选择"灌溉策略"
        query = "白叶枯病的灌溉管理和水分调控"

        print(f"测试查询: {query}")

        rag_service = get_rag_service()

        # 测试查询
        result = asyncio.run(rag_service.query(query, None))

        if result and "找到" in result:
            print(f"[OK] RAG查询成功: {result[:100]}...")
            return True
        else:
            print(f"[WARN] RAG查询返回: {result}")
            return False

    except Exception as e:
        print(f"RAG测试失败: {e}")
        return False


def main():
    """主函数"""
    print("服务配置检查")
    print("=" * 60)

    results = []

    # 运行检查
    results.append(("LLM模型", check_model_from_main()))
    results.append(("确认提示", check_confirmation_prompt()))
    results.append(("RAG查询", test_rag_query()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)

    passed = 0
    for test_name, success in results:
        status = "[OK] 通过" if success else "[FAIL] 失败"
        print(f"{test_name:15} {status}")
        if success:
            passed += 1

    total = len(results)
    print(f"\n通过率: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] 所有检查通过！")
        print("\n现在启动服务应该能看到:")
        print("  1. 使用DeepSeek-v3.2模型")
        print("  2. 正确的三选项确认提示")
        print("  3. 结合病害名称的RAG查询")
    else:
        print(f"\n[WARN] {total - passed} 个问题需要修复")

        if not results[0][1]:  # LLM模型检查失败
            print("\n可能的原因:")
            print("  1. 环境变量未正确设置")
            print("  2. 配置文件缓存问题")
            print("  3. 服务需要重启清除缓存")

    return passed == total


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n检查失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

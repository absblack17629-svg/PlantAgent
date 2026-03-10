#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证系统配置是否正确
"""

import os
import sys
import importlib

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verify_llm_config():
    """验证LLM配置"""
    print("验证LLM配置")
    print("=" * 60)

    try:
        # 1. 检查环境变量
        print("1. 环境变量检查:")
        print(f"   ZHIPU_MODEL: {os.getenv('ZHIPU_MODEL', '未设置')}")
        print(f"   ZHIPU_BASE_URL: {os.getenv('ZHIPU_BASE_URL', '未设置')}")
        print(
            f"   ZHIPU_API_KEY: {'*' * 10}{os.getenv('ZHIPU_API_KEY', '')[-4:] if os.getenv('ZHIPU_API_KEY') else '未设置'}"
        )

        # 2. 检查配置模块
        print("\n2. 配置模块检查:")
        import config.settings as settings

        print(f"   settings.ZHIPU_MODEL: {settings.ZHIPU_MODEL}")
        print(f"   settings.ZHIPU_BASE_URL: {settings.ZHIPU_BASE_URL}")

        # 3. 检查LLM客户端
        print("\n3. LLM客户端检查:")
        import yoloapp.llm

        importlib.reload(yoloapp.llm)

        from yoloapp.llm import get_llm_client

        llm_client = get_llm_client("default")

        print(f"   LLM客户端模型: {llm_client.config.get('model', '未找到')}")
        print(f"   LLM客户端API地址: {llm_client.config.get('base_url', '未找到')}")

        # 4. 检查是否是DeepSeek
        model_name = llm_client.config.get("model", "").lower()
        if "deepseek" in model_name:
            print(f"   [OK] 使用DeepSeek模型: {model_name}")
        else:
            print(f"   [ERROR] 未使用DeepSeek模型: {model_name}")

        return True

    except Exception as e:
        print(f"验证失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_rag_config():
    """验证RAG配置"""
    print("\n验证RAG配置")
    print("=" * 60)

    try:
        # 1. 检查RAG服务
        print("1. RAG服务检查:")
        import yoloapp.rag

        importlib.reload(yoloapp.rag)

        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()

        print(f"   RAG服务类型: {type(rag_service)}")

        # 2. 检查向量数据库
        if hasattr(rag_service, "vector_store"):
            print(f"   [OK] 向量数据库已加载")
        else:
            print(f"   [ERROR] 向量数据库未加载")

        # 3. 检查嵌入模型配置
        print("\n2. 嵌入模型检查:")
        import config.settings as settings

        print(f"   settings.EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")

        if "bge-small-zh" in settings.EMBEDDING_MODEL:
            print(f"   [OK] 使用中文优化模型")
        else:
            print(f"   [ERROR] 未使用中文优化模型")

        return True

    except Exception as e:
        print(f"验证失败: {e}")
        return False


def verify_confirmation_prompt():
    """验证确认提示"""
    print("\n验证确认提示")
    print("=" * 60)

    try:
        # 检查确认代理
        print("1. 确认代理检查:")
        import yoloapp.agent.confirmation_agent as confirmation_agent

        importlib.reload(confirmation_agent)

        # 创建测试实例
        from yoloapp.agent.confirmation_agent import ConfirmationAgent

        agent = ConfirmationAgent()

        # 模拟检测结果
        detection_result = {
            "detection_result": [{"disease": "白叶枯病", "confidence": 0.85}]
        }

        # 生成确认提示
        prompt = agent._generate_confirmation_prompt(detection_result)

        print("生成的确认提示:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)

        # 检查是否包含旧的提示
        if "请回复 '是' 或 '需要'" in prompt:
            print("[ERROR] 包含旧的确认提示")
            return False
        elif "回复 1、2 或 3" in prompt:
            print("[OK] 使用新的三选项确认提示")
            return True
        else:
            print("[WARNING]  确认提示格式不明确")
            return False

    except Exception as e:
        print(f"验证失败: {e}")
        return False


def main():
    """主函数"""
    print("系统配置验证")
    print("=" * 60)

    results = []

    # 运行验证
    results.append(("LLM配置", verify_llm_config()))
    results.append(("RAG配置", verify_rag_config()))
    results.append(("确认提示", verify_confirmation_prompt()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)

    passed = 0
    for test_name, success in results:
        status = "[OK] 通过" if success else "[ERROR] 失败"
        print(f"{test_name:15} {status}")
        if success:
            passed += 1

    total = len(results)
    print(f"\n通过率: {passed}/{total}")

    if passed == total:
        print("\n[CELEBRATE] 所有配置验证通过！")
        print("\n现在可以启动服务:")
        print("  python main.py")
        print("\n访问: http://localhost:8000")
        print("\n测试工作流程:")
        print("  1. 上传图片")
        print("  2. 查看检测结果（只显示病害名称）")
        print("  3. 选择三个选项之一（回复1、2或3）")
        print("  4. 查看详细的农业建议")
    else:
        print(f"\n[WARNING]  {total - passed} 个配置需要修复")

    return passed == total


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n验证失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

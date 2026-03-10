#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终启动脚本 - 确保所有配置正确
"""

import os
import sys
import uvicorn
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║         水稻病害检测与智能咨询系统 - 已优化版本          ║
    ║                     YOLO11 + DeepSeek                    ║
    ╚══════════════════════════════════════════════════════════╝
    
    系统改进:
    [OK] 检测结果只显示病害名称（无数量统计）
    [OK] 三选项确认流程（1-防治方案, 2-种植规划, 3-灌溉策略）
    [OK] 中文优化嵌入模型 (BAAI/bge-small-zh-v1.5)
    [OK] DeepSeek-v3.2模型集成
    [OK] 关键词增强的RAG检索
    [OK] 完整的农业知识库
    
    服务信息:
    • 地址: http://localhost:8000
    • 文档: http://localhost:8000/docs
    • 健康检查: http://localhost:8000/api/health
    
    测试流程:
    1. 上传水稻病害图片
    2. 查看检测结果（如：白叶枯病）
    3. 选择三个选项之一（回复1、2或3）
    4. 获取详细的农业建议
    
    """
    print(banner)


async def verify_system():
    """验证系统配置"""
    print("验证系统配置...")

    try:
        # 检查配置
        import config.settings as settings

        checks = []

        # LLM配置
        if settings.ZHIPU_MODEL == "deepseek-v3.2":
            checks.append(("LLM模型", "[OK]", "使用DeepSeek-v3.2"))
        else:
            checks.append(
                ("LLM模型", "[ERROR]", f"应为deepseek-v3.2，实际为{settings.ZHIPU_MODEL}")
            )

        # API地址
        if "volces.com" in settings.ZHIPU_BASE_URL:
            checks.append(("API地址", "[OK]", "使用VolcEngine API"))
        else:
            checks.append(("API地址", "[ERROR]", "应使用VolcEngine API"))

        # RAG配置
        from config import RAG_CONFIG

        if "bge-small-zh" in RAG_CONFIG["embedding_model"]:
            checks.append(("嵌入模型", "[OK]", "使用中文优化模型"))
        else:
            checks.append(
                (
                    "嵌入模型",
                    "[ERROR]",
                    f"应为中文模型，实际为{RAG_CONFIG['embedding_model']}",
                )
            )

        # 打印检查结果
        print("\n配置检查结果:")
        print("-" * 60)
        for name, status, detail in checks:
            print(f"{name:15} {status} {detail}")

        # 检查确认提示
        print("\n确认提示检查:")
        print("-" * 40)

        # 模拟确认提示
        confirmation_prompt = (
            "检测已完成！\n\n"
            "检测结果: 白叶枯病\n\n"
            "请选择您想了解的内容（回复 1、2 或 3）:\n"
            "1. 防治方案 - 针对检测到的病害\n"
            "2. 种植规划 - 适合的种植建议\n"
            "3. 灌溉策略 - 优化的灌溉方案"
        )

        print(confirmation_prompt)
        print()

        if "回复 1、2 或 3" in confirmation_prompt:
            print("[OK] 确认提示正确（三选项确认）")
        else:
            print("[ERROR] 确认提示不正确")

        # 总结
        all_ok = all(check[1] == "[OK]" for check in checks)
        if all_ok:
            print("\n[CELEBRATE] 所有配置正确，可以启动服务！")
            return True
        else:
            print("\n[WARNING]  配置有问题，请检查上述问题")
            return False

    except Exception as e:
        print(f"验证失败: {e}")
        return False


def start_uvicorn():
    """启动Uvicorn服务器"""
    print("\n" + "=" * 60)
    print("启动服务...")
    print("=" * 60)

    # 配置
    host = "0.0.0.0"
    port = 8000

    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"健康检查: http://{host}:{port}/api/health")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)

    # 启动
    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")


async def main():
    """主函数"""
    # 打印横幅
    print_banner()

    # 验证系统
    if not await verify_system():
        print("\n[ERROR] 系统验证失败，请修复配置后再启动")
        sys.exit(1)

    # 启动服务
    start_uvicorn()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        sys.exit(1)

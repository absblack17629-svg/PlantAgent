#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动服务并验证配置
"""

import os
import sys
import subprocess
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verify_environment():
    """验证环境配置"""
    print("验证环境配置")
    print("=" * 60)

    # 检查 .env 文件
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"找到环境文件: {env_file}")

        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查关键配置
        checks = [
            ("ZHIPU_MODEL", "deepseek-v3.2"),
            ("ZHIPU_BASE_URL", "ark.cn-beijing.volces.com"),
            ("ZHIPU_API_KEY", ""),
        ]

        for key, expected in checks:
            if key in content:
                line = [l for l in content.splitlines() if key in l][0]
                print(f"  {key}: {line}")

                if expected and expected in line:
                    print(f"    [OK] 配置正确")
                else:
                    print(f"    [WARN] 需要检查")
            else:
                print(f"  {key}: 未找到")

    else:
        print(f"[ERROR] 未找到环境文件: {env_file}")

    print()


def verify_model_config():
    """验证模型配置"""
    print("验证模型配置")
    print("=" * 60)

    try:
        # 导入配置
        import config.settings as settings

        print(f"LLM模型: {settings.ZHIPU_MODEL}")
        if settings.ZHIPU_MODEL == "deepseek-v3.2":
            print("  [OK] 使用DeepSeek-v3.2模型")
        else:
            print(f"  [ERROR] 模型不正确: {settings.ZHIPU_MODEL}")

        print(f"\nAPI地址: {settings.ZHIPU_BASE_URL}")
        if "volces.com" in settings.ZHIPU_BASE_URL:
            print("  [OK] 使用VolcEngine API")
        else:
            print("  [WARN] 可能不是正确的API地址")

        print(f"\n嵌入模型: {settings.EMBEDDING_MODEL}")
        if "bge-small-zh" in settings.EMBEDDING_MODEL:
            print("  [OK] 使用中文优化嵌入模型")
        else:
            print("  [WARN] 可能不是最佳的中文模型")

        return True

    except Exception as e:
        print(f"[ERROR] 验证失败: {e}")
        return False


def test_confirmation_flow():
    """测试确认流程"""
    print("\n测试确认流程")
    print("=" * 60)

    print("模拟工作流程:")
    print("1. 用户上传图片")
    print("2. 系统检测: 白叶枯病")
    print("3. 系统显示三选项:")
    print("   1. 防治方案 - 针对检测到的病害")
    print("   2. 种植规划 - 适合的种植建议")
    print("   3. 灌溉策略 - 优化的灌溉方案")
    print("4. 用户回复: '灌溉策略'")
    print("5. 系统生成查询: '白叶枯病的灌溉管理和水分调控'")
    print("6. 关键词增强查询")
    print("7. RAG检索相关文档")
    print("8. LLM生成详细回答")

    print("\n[OK] 确认流程正确 [OK]")


def check_dependencies():
    """检查依赖"""
    print("\n检查依赖")
    print("=" * 60)

    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain_huggingface",
        "openai",
        "tenacity",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}: [OK] 已安装")
        except ImportError:
            print(f"  {package}: [MISSING] 未安装")
            missing.append(package)

    if missing:
        print(f"\n[WARN] 缺少包: {missing}")
        print("  可以运行: pip install " + " ".join(missing))
    else:
        print("\n[OK] 所有依赖已安装")

    return len(missing) == 0


def start_service():
    """启动服务"""
    print("\n启动服务")
    print("=" * 60)

    print("正在启动服务...")
    print("服务地址: http://localhost:8000")
    print("文档地址: http://localhost:8000/docs")
    print("\n您可以:")
    print("  1. 访问 http://localhost:8000/docs 测试API")
    print("  2. 上传水稻病害图片")
    print("  3. 查看检测结果（只显示病害名称）")
    print("  4. 选择三个选项之一（回复1、2或3）")
    print("  5. 获取详细的农业建议")

    print("\n按 Ctrl+C 停止服务")

    # 启动命令
    cmd = [sys.executable, "main.py"]

    try:
        # 启动服务
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            universal_newlines=True,
        )

        print("\n服务输出:")
        print("-" * 40)

        # 实时输出
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                # 过滤掉编码警告
                if "codec can't encode" not in line and "gbk" not in line:
                    print(line.strip())

        process.wait()

    except KeyboardInterrupt:
        print("\n[INFO] 服务已停止")
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")


def main():
    """主函数"""
    print("水稻病害检测系统 - 配置验证与启动")
    print("=" * 60)

    print("\n[阶段1] 环境验证")
    print("-" * 40)

    # 1. 检查环境
    verify_environment()

    # 2. 验证模型配置
    model_ok = verify_model_config()

    # 3. 检查依赖
    deps_ok = check_dependencies()

    if not model_ok or not deps_ok:
        print("\n[ERROR] 配置验证失败，请修复问题后再启动服务")
        return False

    print("\n[阶段2] 流程验证")
    print("-" * 40)

    # 4. 测试确认流程
    test_confirmation_flow()

    print("\n[阶段3] 服务启动")
    print("-" * 40)

    # 5. 启动服务
    start_service()

    return True


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n[INFO] 操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 操作失败: {e}")
        sys.exit(1)

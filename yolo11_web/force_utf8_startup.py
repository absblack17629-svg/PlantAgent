# -*- coding: utf-8 -*-
"""
强制UTF-8编码启动脚本
在Windows上全局修复编码问题
"""

import os
import sys


def force_utf8_encoding():
    """
    强制所有输出为UTF-8编码
    解决Windows控制台打印emoji报错问题
    """
    if sys.platform == "win32":
        print("[INFO] 检测到Windows系统，修复编码问题...")

        # 方法1：设置标准输出的编码
        try:
            # Python 3.7+ 方法
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            print("[SUCCESS] 使用reconfigure方法修复成功")
        except AttributeError:
            try:
                # Python 3.1+ 方法
                import io

                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace"
                )
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace"
                )
                print("[SUCCESS] 使用TextIOWrapper方法修复成功")
            except Exception as e:
                print(f"[WARNING] 修复编码失败: {e}")

        # 测试emoji显示
        print("[TEST] 测试emoji显示: 🔍 ✅ ❌ ⚠️ 📊")
    else:
        print("[INFO] 非Windows系统，无需修复编码")


def run_main():
    """运行主程序"""
    # 导入并运行主程序
    print("\n" + "=" * 60)
    print("启动YOLO11智能体系统...")
    print("=" * 60 + "\n")

    try:
        # 设置环境变量，强制Python使用UTF-8
        os.environ["PYTHONIOENCODING"] = "utf-8"

        # 导入并运行main
        import main

        print("\n[SUCCESS] 系统启动完成")

    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("强制UTF-8编码启动脚本")
    print("-" * 50)

    # 修复编码
    force_utf8_encoding()

    # 运行主程序
    success = run_main()

    if success:
        print("\n✅ 系统启动成功！")
    else:
        print("\n❌ 系统启动失败！")
        sys.exit(1)

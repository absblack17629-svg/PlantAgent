#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
强制UTF-8编码启动脚本

在启动应用前强制设置全局UTF-8编码，解决Windows上的GBK编码错误。
"""

import os
import sys
import subprocess

def force_utf8_environment():
    """强制UTF-8编码环境"""
    print("设置UTF-8编码环境...")
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Windows特定设置
    if sys.platform == "win32":
        try:
            # Windows控制台设置
            import io
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                write_through=True
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                write_through=True
            )
            print("✅ Windows控制台已设置为UTF-8编码")
        except Exception as e:
            print(f"⚠️ 设置Windows控制台时出错: {e}")
    
    print("✅ UTF-8编码环境已设置完成")

def main():
    """主函数：启动FastAPI应用"""
    force_utf8_environment()
    
    # 启动主应用
    print("启动FastAPI应用...")
    
    try:
        # 直接启动main.py
        import main
        print("✅ 应用已启动，请访问 http://localhost:8000")
        print("✅ 编码问题应已解决")
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"❌ 启动应用时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
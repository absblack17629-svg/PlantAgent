# -*- coding: utf-8 -*-
"""
快速修复GBK编码问题 - 只替换关键文件中的emoji
"""

import os
import sys


def fix_main_file():
    """修复main.py文件"""
    filepath = "main.py"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换所有emoji
        replacements = {
            "🚀": "[START]",
            "✅": "[OK]",
            "🔥": "[HOT]",
            "📦": "[PACKAGE]",
            "🎉": "[CELEBRATE]",
            "🛑": "[STOP]",
            "🔍": "[SEARCH]",
            "🔎": "[SEARCH]",
        }

        for emoji, text in replacements.items():
            content = content.replace(emoji, text)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"File not found: {filepath}")


def fix_detection_service():
    """修复检测服务文件"""
    filepath = "services/detection_service.py"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换所有emoji和添加logger导入
        if "logger = get_logger(__name__)" not in content:
            # 在导入部分添加logger
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "from config.settings import settings" in line:
                    lines.insert(i + 1, "from yoloapp.utils.logger import get_logger")
                    lines.insert(i + 2, "")
                    lines.insert(i + 3, "logger = get_logger(__name__)")
                    break

            content = "\n".join(lines)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"File not found: {filepath}")


def fix_routers():
    """修复路由器文件"""
    files = [
        "routers/detection.py",
        "routers/agent_factory.py",
        "routers/mcp_agent.py",
        "routers/langgraph_api.py",
    ]

    for filepath in files:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换emoji
            replacements = {
                "🔍": "[SEARCH]",
                "✅": "[OK]",
                "❌": "[ERROR]",
                "⚠️": "[WARN]",
                "🚀": "[START]",
            }

            for emoji, text in replacements.items():
                content = content.replace(emoji, text)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed {filepath}")
        else:
            print(f"File not found: {filepath}")


def setup_windows_encoding():
    """设置Windows编码为UTF-8"""
    if sys.platform == "win32":
        print("Setting Windows console to UTF-8...")
        os.system("chcp 65001 > nul")

        # 创建环境修复文件
        fix_env = """
# -*- coding: utf-8 -*-
import sys
import os
import io

if sys.platform == 'win32':
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 重定向标准输出
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("Windows encoding fixed to UTF-8")
"""

        with open("fix_encoding.py", "w", encoding="utf-8") as f:
            f.write(fix_env)
        print("Created fix_encoding.py")


def main():
    """主函数"""
    print("Starting GBK encoding fix...")

    # 修复关键文件
    fix_main_file()
    fix_detection_service()
    fix_routers()

    # 设置Windows编码
    setup_windows_encoding()

    print("\nQuick fix completed!")
    print("Please restart the server and test again.")


if __name__ == "__main__":
    main()

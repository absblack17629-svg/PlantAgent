# -*- coding: utf-8 -*-
"""
最简单测试 - 直接测试emoji问题
"""

import sys
import os

# 强制UTF-8编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

print("测试开始...")
print("Emoji测试: 🔍 ✅ ❌ ⚠️ 📊")
print("中文测试: 你好，世界！")

# 测试中文字符串
chinese_text = "水稻病害检测"
print(f"字符串测试: {chinese_text}")

# 测试包含emoji的字符串
emoji_text = "检测结果: ✅ 成功"
print(f"Emoji字符串: {emoji_text}")

print("测试完成！")

# -*- coding: utf-8 -*-
"""
智能依赖安装脚本
自动检测并安装缺失的依赖
"""
import subprocess
import sys

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误信息: {e.stderr}")
        return False

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("YOLO11 智能体系统 - 智能依赖安装")
    print("=" * 60)
    
    # 步骤 1: 升级 pip
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "升级 pip"
    ):
        print("\n⚠️ pip 升级失败，但继续安装...")
    
    # 步骤 2: 安装依赖
    print("\n" + "=" * 60)
    print("安装依赖（不指定版本，自动解决冲突）")
    print("=" * 60)
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "安装依赖"
    )
    
    if not success:
        print("\n尝试使用 --upgrade 参数重新安装...")
        success = run_command(
            f"{sys.executable} -m pip install -r requirements.txt --upgrade",
            "重新安装依赖"
        )
    
    if not success:
        print("\n❌ 依赖安装失败")
        print("请检查错误信息并手动解决")
        return False
    
    # 步骤 3: 验证核心依赖
    print("\n" + "=" * 60)
    print("验证核心依赖")
    print("=" * 60)
    
    core_packages = [
        ("fastapi", "FastAPI"),
        ("torch", "PyTorch"),
        ("ultralytics", "Ultralytics"),
        ("langchain", "LangChain"),
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
        ("psutil", "psutil"),
        ("pydantic", "Pydantic"),
        ("loguru", "Loguru"),
    ]
    
    all_ok = True
    for import_name, display_name in core_packages:
        if check_package(import_name):
            try:
                module = __import__(import_name)
                version = getattr(module, "__version__", "未知版本")
                print(f"✅ {display_name}: {version}")
            except:
                print(f"✅ {display_name}: 已安装")
        else:
            print(f"❌ {display_name}: 未安装")
            all_ok = False
    
    # 步骤 4: 检查可选依赖
    print("\n" + "=" * 60)
    print("检查可选依赖")
    print("=" * 60)
    
    optional_packages = [
        ("langgraph", "LangGraph", "九节点工作流支持"),
    ]
    
    for import_name, display_name, description in optional_packages:
        if check_package(import_name):
            print(f"✅ {display_name}: 已安装 ({description})")
        else:
            print(f"⚠️ {display_name}: 未安装 ({description})")
            print(f"   如需安装: pip install {import_name}")
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 所有核心依赖安装成功！")
    else:
        print("⚠️ 部分依赖安装失败，请检查上述错误信息")
    print("=" * 60)
    
    print("\n下一步:")
    print("1. 配置 .env 文件")
    print("2. 初始化数据库: python init_database.py")
    print("3. 启动服务: python main.py")
    
    return all_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 安装过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

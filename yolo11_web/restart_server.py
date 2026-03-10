# -*- coding: utf-8 -*-
"""
快速重启服务器
"""
import subprocess
import sys
import time
import psutil

def kill_uvicorn_processes():
    """杀死所有uvicorn进程"""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('uvicorn' in str(cmd).lower() or 'main.py' in str(cmd) for cmd in cmdline):
                print(f"[KILL] 终止进程: PID={proc.info['pid']}, CMD={' '.join(cmdline[:3])}")
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed > 0:
        print(f"[OK] 已终止 {killed} 个进程")
        time.sleep(2)
    else:
        print("[INFO] 没有发现运行中的服务器进程")

def start_server():
    """启动服务器"""
    print("\n[START] 启动服务器...")
    print("=" * 60)
    
    # 使用 subprocess.Popen 启动服务器（不等待）
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"[OK] 服务器已启动 (PID: {process.pid})")
    print("=" * 60)
    print("\n查看实时日志:")
    print("  tail -f logs/app.log")
    print("\n或访问:")
    print("  http://localhost:8000")
    print("  http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 显示前几行输出
        for i, line in enumerate(process.stdout):
            print(line.rstrip())
            if i > 20:  # 只显示前20行
                break
        
        print("\n[INFO] 服务器正在后台运行...")
        print("[INFO] 使用 Ctrl+C 或运行此脚本再次重启")
        
    except KeyboardInterrupt:
        print("\n[STOP] 正在停止服务器...")
        process.terminate()
        process.wait()
        print("[OK] 服务器已停止")

if __name__ == "__main__":
    print("=" * 60)
    print("服务器重启工具")
    print("=" * 60)
    
    # 1. 杀死旧进程
    kill_uvicorn_processes()
    
    # 2. 启动新进程
    start_server()

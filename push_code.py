#!/usr/bin/env python3
"""
自动推送代码到 GitHub 的辅助脚本
"""
import subprocess
import os
import sys

# 设置标准输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.chdir("c:/Users/abc/CodeBuddy/20260614150516/offer_hunter")

# 检查状态
print("[1/3] 检查 Git 状态...")
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    print("发现未提交的更改，正在提交...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Update: Improve project files"], check=True)
    print("提交完成")
else:
    print("所有更改已提交")

# 推送代码
print("\n[2/3] 推送到 GitHub...")
try:
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print("SUCCESS: 推送成功！")
        print(result.stdout)
    else:
        print("ERROR: 推送失败")
        print(result.stderr)
except subprocess.TimeoutExpired:
    print("WARNING: 推送超时，请检查网络连接")
except Exception as e:
    print(f"ERROR: {e}")

print("\n[3/3] 完成")
print("仓库地址: https://github.com/violet2314275/offer-hunter")

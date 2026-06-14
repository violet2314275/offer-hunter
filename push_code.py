#!/usr/bin/env python3
"""
自动推送代码到 GitHub 的辅助脚本
"""
import subprocess
import os

os.chdir("c:/Users/abc/CodeBuddy/20260614150516/offer_hunter")

# 检查状态
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    print("发现未提交的更改，先提交...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Update: 完善项目文件和配置"])
else:
    print("所有更改已提交")

# 推送代码
print("\n开始推送到 GitHub...")
result = subprocess.run(
    ["git", "push", "-u", "origin", "main"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ 推送成功！")
    print(result.stdout)
else:
    print("❌ 推送失败：")
    print(result.stderr)

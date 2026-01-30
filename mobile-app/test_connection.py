#!/usr/bin/env python3
"""
测试后端连接
"""
import requests
from config import API_BASE_URL

print(f"API地址: {API_BASE_URL}")
print("-" * 50)

# 测试1: 基础连接
print("测试1: 基础连接...")
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    print(f"✓ 连接成功! 状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
except Exception as e:
    print(f"✗ 连接失败: {e}")

print()

# 测试2: 登录接口
print("测试2: 登录接口...")
try:
    response = requests.post(
        f"{API_BASE_URL}/api/login",
        json={"username": "test", "password": "123456"},
        timeout=5
    )
    print(f"✓ 请求成功! 状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
except Exception as e:
    print(f"✗ 请求失败: {e}")

print()
print("-" * 50)
print("如果测试1失败，请检查:")
print("1. 后端服务是否已启动 (python main.py)")
print("2. 防火墙是否阻止了8000端口")
print("3. 尝试使用: http://localhost:8000 代替 http://127.0.0.1:8000")

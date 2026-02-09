#!/bin/bash
# 零售市场调研工具停止脚本

echo "=== 停止零售市场调研服务 ==="

# 停止后端服务
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "🛑 停止后端服务..."
    pkill -f "uvicorn main:app"
    sleep 1
    if pgrep -f "uvicorn main:app" > /dev/null; then
        echo "⚠️ 强制停止后端服务..."
        pkill -9 -f "uvicorn main:app"
    fi
    echo "✅ 后端服务已停止"
else
    echo "ℹ️ 后端服务未运行"
fi

# 停止 Nginx
echo "🛑 停止 Nginx..."
systemctl stop nginx
echo "✅ Nginx 已停止"

echo ""
echo "=== 所有服务已停止 ==="

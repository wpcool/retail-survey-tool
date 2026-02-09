#!/bin/bash
# 零售市场调研工具启动脚本

cd /root/workspace/retail-survey-tool/backend

echo "=== 启动零售市场调研服务 ==="

# 检查 uvicorn 是否已在运行
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "⚠️ 后端服务已在运行"
else
    echo "🚀 启动后端服务..."
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
    sleep 2
    if pgrep -f "uvicorn main:app" > /dev/null; then
        echo "✅ 后端服务启动成功 (端口: 8000)"
    else
        echo "❌ 后端服务启动失败"
        exit 1
    fi
fi

# 检查 Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 已在运行 (端口: 80)"
else
    echo "🚀 启动 Nginx..."
    systemctl start nginx
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx 启动成功"
    else
        echo "❌ Nginx 启动失败"
    fi
fi

echo ""
echo "==================================="
echo "服务访问地址:"
echo "  首页:     http://39.97.236.234"
echo "  后台:     http://39.97.236.234/admin"
echo "  API文档:  http://39.97.236.234/docs"
echo "==================================="

#!/bin/bash
# 零售市场调研工具启动脚本

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "=== 启动零售市场调研服务 ==="

# 检查 uvicorn 是否已在运行
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "⚠️ 后端服务已在运行"
else
    echo "🚀 启动后端服务..."
    nohup "$SCRIPT_DIR/preview_env/bin/python" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
    sleep 2
    if pgrep -f "uvicorn main:app" > /dev/null; then
        echo "✅ 后端服务启动成功 (端口: 8000)"
    else
        echo "❌ 后端服务启动失败"
        exit 1
    fi
fi

# 检查 Nginx (支持 macOS 和 Linux)
if command -v systemctl &> /dev/null; then
    # Linux (systemd)
    if systemctl is-active --quiet nginx 2>/dev/null; then
        echo "✅ Nginx 已在运行 (端口: 80)"
    else
        echo "🚀 启动 Nginx..."
        sudo systemctl start nginx 2>/dev/null || echo "⚠️ 无法启动 Nginx，请手动启动"
    fi
elif command -v brew &> /dev/null; then
    # macOS (Homebrew)
    if brew services list | grep nginx | grep started &> /dev/null; then
        echo "✅ Nginx 已在运行"
    else
        echo "🚀 启动 Nginx..."
        brew services start nginx 2>/dev/null || echo "⚠️ 无法启动 Nginx，请手动运行: brew services start nginx"
    fi
else
    echo "⚠️ 无法检测 Nginx 状态，请手动检查"
fi

echo ""
echo "==================================="
echo "服务访问地址:"
echo "  首页:     http://39.97.236.234"
echo "  后台:     http://39.97.236.234/admin"
echo "  API文档:  http://39.97.236.234/docs"
echo "==================================="

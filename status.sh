#!/bin/bash
# 零售市场调研工具状态检查脚本

echo "=== 服务状态检查 ==="
echo ""

# 检查后端服务
if pgrep -f "uvicorn main:app" > /dev/null; then
    PID=$(pgrep -f "uvicorn main:app" | head -1)
    echo "✅ 后端服务: 运行中 (PID: $PID)"
    echo "   本地测试: curl http://127.0.0.1:8000/"
else
    echo "❌ 后端服务: 未运行"
fi

# 检查 Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: 运行中"
    echo "   配置测试: nginx -t"
else
    echo "❌ Nginx: 未运行"
fi

echo ""
echo "=== 端口监听 ==="
ss -tlnp | grep -E ":80|:8000" || netstat -tlnp 2>/dev/null | grep -E ":80|:8000"

echo ""
echo "=== 访问地址 ==="
echo "  首页:     http://39.97.236.234"
echo "  后台:     http://39.97.236.234/admin"
echo "  API文档:  http://39.97.236.234/docs"

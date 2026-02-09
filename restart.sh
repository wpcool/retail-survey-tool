#!/bin/bash
# 零售市场调研工具重启脚本

echo "=== 重启零售市场调研服务 ==="

# 先停止
./stop.sh

echo ""

# 再启动
./start.sh

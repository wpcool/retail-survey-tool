#!/bin/bash
# 同步 admin-web 到 backend/static

cd "$(dirname "$0")"

echo "同步 admin-web/index.html -> backend/static/index.html"
cp admin-web/index.html backend/static/index.html

echo "完成！"
echo ""
echo "访问: http://localhost:8000/admin"
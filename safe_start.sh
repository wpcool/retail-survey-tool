#!/bin/bash
# 安全启动脚本 - 带数据库保护
# 使用方法: ./safe_start.sh

set -e

echo "=========================================="
echo "  零售市场调研工具 - 安全启动"
echo "=========================================="

# 检查数据库文件
DB_FILE="backend/data/survey.db"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    echo "✅ 数据库文件存在: $DB_FILE ($DB_SIZE)"
    
    # 显示数据库统计
    cd backend
    source venv/bin/activate
    python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///data/survey.db')
with engine.connect() as conn:
    tables = ['surveyors', 'survey_records', 'products', 'survey_tasks']
    for t in tables:
        try:
            count = conn.execute(text(f'SELECT COUNT(*) FROM {t}')).fetchone()[0]
            print(f'  📊 {t}: {count} 条记录')
        except:
            print(f'  ⚠️  {t}: 表不存在')
" 2>/dev/null || echo "  ⚠️  无法读取数据库统计"
    cd ..
else
    echo "⚠️  数据库文件不存在: $DB_FILE"
fi

echo ""
echo "=========================================="
echo "  启动服务"
echo "=========================================="

# 杀死旧进程
echo "清理旧进程..."
pkill -f uvicorn 2>/dev/null || true
sleep 1

# 启动服务
cd backend
source venv/bin/activate
echo "🚀 启动后端服务..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

sleep 2

# 检查服务是否启动
if curl -s http://localhost:8000/api/products > /dev/null 2>&1; then
    echo "✅ 后端服务已启动: http://localhost:8000"
else
    echo "❌ 后端服务启动失败，请检查日志: backend/server.log"
    exit 1
fi

cd ..
echo ""
echo "=========================================="
echo "  服务启动完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 后端API: http://localhost:8000"
echo "  - 管理后台: http://localhost:8000/admin"
echo ""
echo "⚠️  数据库保护机制已启用："
echo "  - 删除调研人员需要确认码"
echo "  - 删除调研记录需要确认码"
echo "  - 导入商品数据需要双重确认"
echo ""

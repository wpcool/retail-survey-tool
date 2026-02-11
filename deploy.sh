#!/bin/bash
# 生产环境部署脚本
# 使用方法: ./deploy.sh

set -e

PROJECT_DIR="/opt/retail-survey-tool"
REPO_URL="https://github.com/wpcool/retail-survey-tool.git"

echo "=========================================="
echo "  零售市场调研工具 - 生产环境部署"
echo "=========================================="

# 检查是否在root权限下运行
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  警告: 不建议使用root运行此脚本"
   read -p "是否继续? (y/n): " choice
   if [ "$choice" != "y" ]; then
       exit 1
   fi
fi

# 1. 安装依赖
echo ""
echo "📦 步骤1: 检查依赖..."
if ! command -v git &> /dev/null; then
    echo "安装 git..."
    sudo apt-get update && sudo apt-get install -y git || sudo yum install -y git
fi

if ! command -v python3 &> /dev/null; then
    echo "安装 python3..."
    sudo apt-get install -y python3 python3-pip python3-venv || sudo yum install -y python3 python3-pip
fi

# 2. 克隆或更新代码
echo ""
echo "📥 步骤2: 拉取代码..."
if [ -d "$PROJECT_DIR" ]; then
    echo "项目已存在，更新代码..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "克隆项目..."
    sudo mkdir -p /opt
    sudo git clone "$REPO_URL" "$PROJECT_DIR"
    sudo chown -R $USER:$USER "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 3. 设置后端环境
echo ""
echo "⚙️  步骤3: 配置后端..."
cd "$PROJECT_DIR/backend"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. 检查数据库
echo ""
echo "🗄️  步骤4: 检查数据库..."
if [ -f "data/survey.db" ]; then
    DB_SIZE=$(du -h data/survey.db | cut -f1)
    echo "✅ 数据库文件存在: $DB_SIZE"
else
    echo "⚠️  警告: 数据库文件不存在！"
    echo "   首次部署需要初始化数据库"
fi

# 5. 启动服务
echo ""
echo "🚀 步骤5: 启动服务..."

# 检查端口是否被占用
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "端口8000被占用，尝试停止旧服务..."
    pkill -f uvicorn || true
    sleep 2
fi

# 启动服务
echo "启动后端服务..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > server.log 2>&1 &
sleep 3

# 检查服务是否启动
if curl -s http://localhost:8000/api/products > /dev/null 2>&1; then
    echo "✅ 服务启动成功!"
    echo ""
    echo "=========================================="
    echo "  部署完成!"
    echo "=========================================="
    echo ""
    echo "访问地址:"
    echo "  - 本地: http://localhost:8000"
    echo "  - 公网: http://$(curl -s ifconfig.me || echo 'your-server-ip'):8000"
    echo ""
    echo "管理后台: http://your-server-ip:8000/admin"
    echo ""
    echo "查看日志: tail -f $PROJECT_DIR/backend/server.log"
    echo ""
else
    echo "❌ 服务启动失败，请检查日志:"
    echo "   tail -f $PROJECT_DIR/backend/server.log"
    exit 1
fi

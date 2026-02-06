# retail-survey-tool

零售市场调研工具 - 用于采集超市商品价格、促销信息的完整解决方案。

## 技术架构

- **后端**: Python + FastAPI + SQLite
- **管理后台**: 纯 HTML + CSS + JS
- **移动端**: Android (Java) + Retrofit

## 快速开始

### 方式1：本地启动（推荐开发用）💻

```bash
# 1. 进入后端目录
cd retail-survey-tool/backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 管理后台：http://localhost:8000/admin

### 方式2：Docker 启动 🐳

```bash
cd retail-survey-tool/backend

# 构建并运行
docker build -t retail-survey .
docker run -p 8000:8000 retail-survey
```

### 方式3：后台持续运行（生产环境）🚀

```bash
cd retail-survey-tool/backend

# 使用 nohup 后台运行
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 查看日志
tail -f server.log
```

## 项目结构

```
retail-survey-tool/
├── backend/              # FastAPI 后端服务
│   ├── main.py          # 主入口，API 路由
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── schemas.py       # Pydantic 数据校验
│   └── data/survey.db   # SQLite 数据库
├── admin-web/           # 管理后台
│   └── index.html       # 单页面管理界面（含图表）
├── android-app/         # Android 应用
│   └── app/src/...      # Java 源码
└── preview_images/      # 预览截图
```

## 主要功能

- 📋 **任务管理** - 按日期发布调研任务，包含多个品类/商品
- 📱 **移动端采集** - Android App 支持拍照、定位、价格录入
- 📷 **照片存证** - 商品照片上传并关联记录
- 📊 **数据看板** - 管理后台展示统计数据和图表
- 📍 **GPS 定位** - 自动记录调研地点坐标

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/login | POST | 调研人员登录 |
| /api/tasks | GET | 获取任务列表 |
| /api/records | POST | 提交调研记录 |
| /api/upload/image | POST | 上传照片 |

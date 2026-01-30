# 零售市场调研工具

一款专为超市CTO设计的零售市场调研解决方案，帮助调研人员高效完成价格调研工作。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        零售市场调研系统                           │
├─────────────────┬─────────────────────┬─────────────────────────┤
│   管理后台       │     后端服务         │      移动端App          │
│   (Web)         │    (FastAPI)        │     (Kivy)             │
├─────────────────┼─────────────────────┼─────────────────────────┤
│ • 发布调研任务  │ • RESTful API       │ • 接收每日任务          │
│ • 查看统计数据  │ • 数据存储(SQLite)  │ • 填写价格信息          │
│ • 导出Excel    │ • 图片存储          │ • 拍照上传              │
│ • 人员管理     │ • 任务分发          │ • 离线支持(可扩展)       │
└─────────────────┴─────────────────────┴─────────────────────────┘
```

## 📁 项目结构

```
retail-survey-tool/
├── backend/              # 后端服务
│   ├── main.py          # FastAPI主程序
│   ├── models.py        # 数据模型
│   ├── schemas.py       # 数据验证
│   ├── requirements.txt # Python依赖
│   └── data/            # SQLite数据库和照片存储
│
├── mobile-app/          # Kivy移动应用
│   ├── main.py          # 应用主程序
│   ├── api_client.py    # API客户端
│   ├── config.py        # 配置文件
│   └── requirements.txt # Python依赖
│
├── admin-web/           # 管理后台
│   └── index.html       # 单页面管理后台
│
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务启动后访问：
- API文档: http://localhost:8000/docs
- API服务: http://localhost:8000

### 2. 运行管理后台

直接用浏览器打开 `admin-web/index.html`，或启动一个简易HTTP服务器：

```bash
cd admin-web
python -m http.server 8080
```

然后访问 http://localhost:8080

### 3. 运行移动应用

```bash
cd mobile-app

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 或 Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

## 📱 移动端使用说明

### 默认测试账号
- 用户名: `test`
- 密码: `123456`

### 主要功能
1. **登录**: 使用CTO分配的账号密码登录
2. **查看任务**: 进入首页自动加载今日调研任务
3. **填写数据**: 点击品类进入填写页面
   - 填写超市名称
   - 输入商品价格
   - 添加促销信息（可选）
   - 拍摄商品照片
4. **提交**: 点击提交按钮同步到服务器

## 🔧 配置说明

### 后端配置

编辑 `backend/main.py` 可修改：
- 端口: `uvicorn.run(app, host="0.0.0.0", port=8000)`
- 数据库: 默认SQLite，可修改为MySQL/PostgreSQL

### 移动端配置

编辑 `mobile-app/config.py` 修改API地址：

```python
# 本地开发（Android模拟器）
API_BASE_URL = "http://10.0.2.2:8000"

# 真机测试（替换为你的电脑IP）
API_BASE_URL = "http://192.168.1.xxx:8000"

# 生产环境
API_BASE_URL = "https://your-server.com"
```

## 📦 打包APK（Android）

### 安装Buildozer

```bash
# Linux/macOS
pip install buildozer

# 安装Android依赖
sudo apt-get install -y \
    python3-pip build-essential git \
    ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
```

### 配置打包

在 `mobile-app` 目录创建 `buildozer.spec`：

```bash
cd mobile-app
buildozer init
```

编辑 `buildozer.spec` 关键配置：

```ini
# 应用名称
title = 零售调研工具

# 包名
package.name = retailsurvey
package.domain = com.yourcompany

# 源文件
source.include_exts = py,png,jpg,kv,atlas,ttf

# 依赖
requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests,pillow,urllib3,charset-normalizer,idna,certifi

# Android API版本
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# 权限
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION

# 屏幕方向
orientation = portrait
```

### 执行打包

```bash
# 调试模式（首次建议使用）
buildozer android debug

# 部署到连接的设备
buildozer android debug deploy run

# 发布版本
buildozer android release
```

打包完成后，APK文件位于：`bin/retailsurvey-xxx.apk`

## 🔒 生产环境部署建议

### 1. 后端部署

推荐使用Docker部署：

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["python", "main.py"]
```

或使用Gunicorn+Nginx：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 2. 数据库升级

生产环境建议使用PostgreSQL或MySQL：

```python
# 修改 models.py
# SQLite:
SQLALCHEMY_DATABASE_URL = "sqlite:///data/survey.db"

# PostgreSQL:
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/survey"

# MySQL:
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/survey"
```

### 3. 安全加固

- 启用HTTPS（Let's Encrypt免费证书）
- 添加JWT认证（已预留接口）
- 配置防火墙规则
- 定期备份数据库

## 📊 功能特性

| 功能 | 管理后台 | 移动端 |
|------|---------|--------|
| 发布调研任务 | ✅ | - |
| 管理调研人员 | ✅ | - |
| 查看统计数据 | ✅ | - |
| 导出Excel | ✅ | - |
| 查看调研记录 | ✅ | - |
| 查看照片 | ✅ | - |
| 接收每日任务 | - | ✅ |
| 填写价格数据 | - | ✅ |
| 拍照上传 | - | ✅ |
| GPS定位 | - | ✅ |

## 🛠️ 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **移动端**: Kivy + KivyMD
- **管理后台**: 原生HTML + JavaScript
- **打包工具**: Buildozer

## 📝 注意事项

1. **网络权限**: Android应用需要 `INTERNET` 权限访问服务器
2. **相机权限**: 需要 `CAMERA` 权限拍摄照片
3. **存储权限**: 需要 `WRITE_EXTERNAL_STORAGE` 保存照片
4. **GPS权限**: 需要 `ACCESS_FINE_LOCATION` 获取位置（可选）

## 🔮 后续可扩展功能

- [ ] 离线模式（无网络时暂存本地）
- [ ] 批量导入品类（Excel模板）
- [ ] 价格趋势图表分析
- [ ] 竞品对比报表
- [ ] 消息推送（新任务通知）
- [ ] OCR识别价格标签
- [ ] 多语言支持

## 📧 联系方式

如有问题或建议，欢迎联系CTO办公室。

---

**版本**: 1.0.0  
**更新日期**: 2024-01-30

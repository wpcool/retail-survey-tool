# 微信云托管部署指南

## 优势
- ✅ 免服务器、免域名、免备案
- ✅ 自动HTTPS
- ✅ 免费额度足够小项目使用
- ✅ 微信官方运维，稳定安全

## 部署步骤

### 1. 开通云托管
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 左侧菜单 → **云开发** → **云托管**
3. 点击「开通云托管」
4. 完成实名认证（个人/企业）

### 2. 准备代码
已为你创建好以下文件：
- `Dockerfile` - 容器配置文件
- `container.config.json` - 云托管配置

### 3. 修改后端代码适配云托管

由于云托管容器是临时的，**SQLite数据会丢失**，需要改成云数据库：

**方案A：使用腾讯云MySQL（推荐）**
```python
# backend/database.py 修改
import os

# 从环境变量读取数据库配置
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'survey')

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
```

**方案B：使用云开发数据库（MongoDB）**
```python
from tcb import TCB

db = TCB().database()
```

### 4. 部署到云托管

**方式1：命令行部署（推荐）**
```bash
# 安装云开发CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署
tcb container:deploy
```

**方式2：手动上传**
1. 把项目代码打包成 zip
2. 云托管控制台 → 服务管理 → 新建版本
3. 上传代码包
4. 选择「使用Dockerfile构建」

### 5. 配置数据库

**创建MySQL实例：**
1. 云托管控制台 → 数据库 → 新建MySQL
2. 选择「Serverless MySQL」（按量付费，有免费额度）
3. 创建数据库：`retail_survey`
4. 获取连接地址、用户名、密码

**配置环境变量：**
1. 云托管 → 服务管理 → 版本配置 → 编辑
2. 添加环境变量：
   - `DB_HOST`: 你的MySQL连接地址
   - `DB_USER`: 用户名
   - `DB_PASSWORD`: 密码
   - `DB_NAME`: retail_survey

### 6. 初始化数据

首次部署需要导入数据：
```bash
# 本地导出SQLite数据
sqlite3 data/survey.db .dump > backup.sql

# 在云托管控制台执行SQL导入
```

### 7. 小程序配置

**获取云托管地址：**
部署成功后，云托管会分配地址：
```
https://你的服务名-xxx.gz.apigw.tencentcs.com
```

**修改小程序代码：**
```javascript
// mini-program/app.js
App({
  globalData: {
    baseUrl: 'https://你的服务名-xxx.gz.apigw.tencentcs.com',
    token: null
  }
})
```

**或者使用云调用（推荐）：**
```javascript
// 无需配置baseUrl，直接调用
wx.cloud.callContainer({
  config: { env: '你的环境ID' },
  path: '/api/products',
  method: 'GET',
  success: res => console.log(res.data)
})
```

### 8. 配置安全域名

小程序后台 → 开发 → 开发管理 → 服务器域名：
```
request合法域名: https://你的服务名-xxx.gz.apigw.tencentcs.com
```

## 费用说明

| 资源 | 免费额度 | 超出费用 |
|-----|---------|---------|
| CPU | 前1000核*秒/天 | 0.0001元/核*秒 |
| 内存 | 前2000GB*秒/天 | 0.0001元/GB*秒 |
| 出站流量 | 前1GB/月 | 0.8元/GB |
| MySQL | 基础版免费 | - |

**小项目通常完全免费！**

## 常见问题

### Q: 数据如何迁移？
A: SQLite → MySQL 需要转换，使用工具如 `sqlite3-to-mysql`

### Q: 文件上传怎么办？
A: 使用云存储（Cloud Storage）代替本地存储

### Q: 如何更新代码？
A: 重新部署新版本，云托管支持灰度发布

## 需要帮助？

微信云托管文档：https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/

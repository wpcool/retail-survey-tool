# 零售调研 Android App

使用 Android Studio + Kotlin + Jetpack Compose 开发的零售调研应用。

## 技术栈

- **UI**: Jetpack Compose
- **架构**: MVVM + Hilt 依赖注入
- **网络**: Retrofit2 + OkHttp3
- **图片加载**: Coil
- **相机**: CameraX
- **定位**: Google Play Services Location

## 项目结构

```
app/src/main/java/com/yourcompany/retailsurvey/
├── api/                    # API 接口
├── data/model/            # 数据模型
├── di/                    # 依赖注入
├── ui/
│   ├── screens/          # 界面
│   ├── theme/            # 主题
│   └── viewmodel/        # ViewModel
└── utils/                # 工具类
```

## 快速开始

### 1. 打开项目
使用 Android Studio 打开 `android-app` 目录

### 2. 修改服务器地址
在 `api/RetrofitClient.kt` 中修改 BASE_URL:

```kotlin
// 模拟器测试
private const val BASE_URL = "http://10.0.2.2:8000/"

// 真机测试（替换为你的电脑IP）
// private const val BASE_URL = "http://192.168.x.x:8000/"

// 生产环境
// private const val BASE_URL = "https://your-server.com/"
```

### 3. 同步并运行
点击 "Sync Project with Gradle Files"，然后运行到模拟器或真机

## 功能

- ✅ 调研列表查看
- ✅ 新建调研（门店名称、类型、位置）
- ✅ 相机拍照
- ✅ 相册选择图片
- ✅ GPS 定位
- ✅ 图片上传到后端
- ✅ 调研详情查看

## 权限

应用需要以下权限：
- 网络访问
- 相机
- 定位
- 存储（Android 12 及以下）

## 后端接口

确保后端 FastAPI 服务运行，并开放相应端口。

默认端口：8000

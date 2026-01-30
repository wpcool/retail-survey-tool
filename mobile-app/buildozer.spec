[app]

# 应用标题（英文，避免打包问题）
title = Retail Survey Tool

# 包名
package.name = retailsurvey

# 包域名
package.domain = com.yourcompany

# 源文件目录
source.dir = .

# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,ttf,txt

# 排除的文件/目录
source.exclude_dirs = tests, bin, venv, __pycache__, .git

# 应用版本
version = 1.0.0

# 依赖
requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests==2.31.0,pillow==10.2.0,urllib3,charset-normalizer,idna,certifi

# 设置图标（可选）
# icon.filename = icon.png

# 屏幕方向
orientation = portrait

# 是否全屏
fullscreen = 0

# Android配置
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 29

# 只编译 arm64-v8a 架构（更快，适合测试）
# 正式发布时可以改为：android.archs = arm64-v8a, armeabi-v7a
android.archs = arm64-v8a

# 方案：Buildozer 自动下载 SDK 工具（约150MB），NDK 使用现有的
android.sdk_path = /Users/wangpeng/Documents/WorkSpace/Develop/MyCode/LSR/MarketSearchTools/retail-survey-tool/mobile-app/.buildozer/android/platform/android-sdk
android.ndk_path = /Users/wangpeng/Library/Android/sdk/ndk/29.0.14206865

# Android权限
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Android应用标签（显示在应用列表中的名称）
android.app_label = Retail Survey

# 是否使用AndroidX
android.enable_androidx = True

# iOS配置（暂不需要）
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master
# ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
# ios.ios_deploy_branch = 1.10.0

[buildozer]

# 日志级别 (2 = 详细)
log_level = 2

# 警告颜色
warn_on_root = 1

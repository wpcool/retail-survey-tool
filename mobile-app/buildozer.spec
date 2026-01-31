[app]

# 应用标题
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

# 屏幕方向
orientation = portrait

# 是否全屏
fullscreen = 0

# Android配置
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25
android.archs = arm64-v8a

# SDK/NDK 路径将在 GitHub Actions 中自动设置
# 本地路径已移除

# Android权限
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Android应用标签
android.app_label = Retail Survey

# 使用AndroidX
android.enable_androidx = True

[buildozer]

# 日志级别
log_level = 2
warn_on_root = 1

# python-for-android 配置
p4a.branch = develop

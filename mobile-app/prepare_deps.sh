#!/bin/bash
# 手动准备 Android 打包依赖

set -e

echo "===== 手动准备 Android 打包依赖 ====="

# 创建目录
mkdir -p .buildozer/android/packages
mkdir -p .buildozer/android/platform

# 1. 下载 Android Platform Tools (adb, fastboot 等)
echo "[1/6] 下载 Platform Tools..."
if [ ! -f .buildozer/android/packages/platform-tools-latest-darwin.zip ]; then
    curl -L -o .buildozer/android/packages/platform-tools-latest-darwin.zip \
        "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
fi

# 2. 下载 Android SDK Build Tools
echo "[2/6] 下载 Build Tools..."
if [ ! -f .buildozer/android/packages/build-tools_r33.0.0-macosx.zip ]; then
    curl -L -o .buildozer/android/packages/build-tools_r33.0.0-macosx.zip \
        "https://dl.google.com/android/repository/build-tools_r33.0.0-macosx.zip"
fi

# 3. 下载 Android API 33 平台
echo "[3/6] 下载 Android API 33..."
if [ ! -f .buildozer/android/packages/platform-33_r02.zip ]; then
    curl -L -o .buildozer/android/packages/platform-33_r02.zip \
        "https://dl.google.com/android/repository/platform-33_r02.zip"
fi

# 4. 下载 Python for Android (从 GitHub 镜像)
echo "[4/6] 下载 Python for Android..."
if [ ! -d .buildozer/android/platform/python-for-android ]; then
    # 使用 ghproxy 镜像加速
    git clone --depth 1 -b master \
        https://ghproxy.com/https://github.com/kivy/python-for-android.git \
        .buildozer/android/platform/python-for-android || \
    git clone --depth 1 -b master \
        https://github.com/kivy/python-for-android.git \
        .buildozer/android/platform/python-for-android
fi

# 5. 解压平台工具
echo "[5/6] 解压 Platform Tools..."
if [ ! -d .buildozer/android/platform/android-sdk/platform-tools ]; then
    unzip -q .buildozer/android/packages/platform-tools-latest-darwin.zip \
        -d .buildozer/android/platform/android-sdk/ || true
fi

# 6. 解压 Build Tools
echo "[6/6] 解压 Build Tools..."
if [ ! -d .buildozer/android/platform/android-sdk/build-tools ]; then
    mkdir -p .buildozer/android/platform/android-sdk/build-tools
    unzip -q .buildozer/android/packages/build-tools_r33.0.0-macosx.zip \
        -d temp_build_tools/
    mv temp_build_tools/android-13 .buildozer/android/platform/android-sdk/build-tools/33.0.0 || true
    rm -rf temp_build_tools/
fi

# 7. 解压 API 33
echo "[7/7] 解压 Android API 33..."
if [ ! -d .buildozer/android/platform/android-sdk/platforms/android-33 ]; then
    mkdir -p .buildozer/android/platform/android-sdk/platforms
    unzip -q .buildozer/android/packages/platform-33_r02.zip \
        -d .buildozer/android/platform/android-sdk/platforms/android-33 || true
fi

# 8. 创建 licenses 目录并添加许可
echo "[8/8] 创建 licenses..."
mkdir -p .buildozer/android/platform/android-sdk/licenses
echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > \
    .buildozer/android/platform/android-sdk/licenses/android-sdk-license
echo "84831b9409646a918e30573bab4c9c91346d8abd" > \
    .buildozer/android/platform/android-sdk/licenses/android-sdk-preview-license

echo ""
echo "===== 依赖准备完成！====="
echo "现在可以运行: buildozer android debug"

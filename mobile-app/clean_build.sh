#!/bin/bash
# 清理 Kivy 构建环境脚本

echo "🧹 清理 Kivy/Android 构建环境..."

cd "$(dirname "$0")"

# 删除构建目录
echo "删除 .buildozer/android/platform/build-*..."
rm -rf .buildozer/android/platform/build-arm64-v8a
rm -rf .buildozer/android/platform/build-arm64-v8a_armeabi-v7a

# 删除之前的 APK
echo "删除旧的 APK..."
rm -rf bin/*.apk

# 删除 Python 缓存
echo "删除 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ 清理完成！"
echo ""
echo "现在可以运行: ./build_apk.sh""} > retail-survey-tool/mobile-app/clean_build.sh && chmod +x retail-survey-tool/mobile-app/clean_build.sh
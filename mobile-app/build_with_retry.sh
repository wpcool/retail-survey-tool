#!/bin/bash
# 带重试的APK打包脚本

cd "$(dirname "$0")"
source venv/bin/activate

# 设置环境变量
export JAVA_HOME=/Users/wangpeng/Library/Java/JavaVirtualMachines/jdk-17.0.2+8/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH

# 清理之前的失败构建
rm -rf .buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl2/app/build/outputs/apk

echo "===== 开始打包 (带日志输出) ====="
echo ""

# 执行打包并实时显示输出
buildozer android debug 2>&1 | tee build_log.txt

# 检查是否成功
if ls bin/*.apk 1>/dev/null 2>&1; then
    echo ""
    echo "===== 打包成功! ====="
    ls -lh bin/*.apk
else
    echo ""
    echo "===== 打包可能失败或未完成 ====="
    echo "查看日志: tail -50 build_log.txt"
fi

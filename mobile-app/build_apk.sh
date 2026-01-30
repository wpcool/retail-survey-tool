#!/bin/bash
# APK 打包脚本

cd "$(dirname "$0")"
source venv/bin/activate

# 设置环境变量
export JAVA_HOME=/Users/wangpeng/Library/Java/JavaVirtualMachines/jdk-17.0.2+8/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH

# 显示信息
echo "===== APK 打包开始 ====="
echo "JAVA_HOME: $JAVA_HOME"
java -version
echo ""

# 开始打包
buildozer android debug

echo ""
echo "===== 打包完成 ====="
echo "APK 文件位置: bin/retailsurvey-1.0.0-*.apk"

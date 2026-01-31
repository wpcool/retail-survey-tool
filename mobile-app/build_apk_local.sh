#!/bin/bash
# 本地 APK 构建脚本

set -e  # 遇到错误立即退出

cd "$(dirname "$0")"

echo "🚀 开始本地 APK 构建..."
echo ""

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export JAVA_HOME=/Users/wangpeng/Library/Java/JavaVirtualMachines/jdk-17.0.2+8/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH

echo "📋 环境信息:"
echo "JAVA_HOME: $JAVA_HOME"
java -version
echo ""

# 修复 SDL2_image 的 external 目录问题（如果存在）
echo "🔧 检查并修复 SDL2_image..."
SDL2_IMAGE_DIR=".buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl2/jni/SDL2_image/external"
if [ -d "$SDL2_IMAGE_DIR" ]; then
    echo "清理 SDL2_image external 目录..."
    rm -rf "$SDL2_IMAGE_DIR"
    echo "✅ SDL2_image 目录已清理"
fi

# 修复 pyjnius Python 3 兼容性（如果构建失败时）
echo "🔧 检查 pyjnius 补丁..."
PYNIUS_PATCH_FILE="/tmp/fix_pyjnius.py"
cat > "$PYNIUS_PATCH_FILE" << 'EOF'
import os
import sys

def patch_pyjnius():
    base_paths = [
        os.path.expanduser("~/.buildozer/android/platform/build-arm64-v8a/build/other_builds"),
    ]
    patched = 0
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
        for root, dirs, files in os.walk(base_path):
            if "pyjnius" in root.lower():
                for file in files:
                    if file.endswith((".pxi", ".pyx")):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, "r") as f:
                                content = f.read()
                            if "isinstance(arg, long)" in content:
                                content = content.replace(
                                    "isinstance(arg, long)",
                                    "isinstance(arg, int)"
                                )
                                with open(filepath, "w") as f:
                                    f.write(content)
                                print(f"Patched: {filepath}")
                                patched += 1
                        except Exception as e:
                            print(f"Error: {filepath}: {e}")
    return patched

if __name__ == "__main__":
    patch_pyjnius()
EOF

# 后台运行修补脚本
(
    for i in {1..120}; do
        sleep 3
        python3 "$PYNIUS_PATCH_FILE" 2>/dev/null || true
    done
) &
PATCH_PID=$!

echo "🛠️  开始构建..."
echo ""

# 开始构建
buildozer android debug || {
    echo ""
    echo "⚠️  构建失败，尝试应用补丁后重试..."
    python3 "$PYNIUS_PATCH_FILE" 2>/dev/null || true
    sleep 2
    buildozer android debug
}

# 停止后台修补进程
kill $PATCH_PID 2>/dev/null || true

echo ""
echo "✅ 构建完成！"
echo ""

# 查找 APK
APK_PATH=$(find bin -name "*.apk" -type f 2>/dev/null | head -1)
if [ -n "$APK_PATH" ]; then
    echo "📱 APK 文件: $APK_PATH"
    ls -lh "$APK_PATH"
    echo ""
    echo "安装到设备:"
    echo "  adb install -r $APK_PATH"
else
    echo "❌ 未找到 APK 文件"
    echo "请检查构建日志: .buildozer/android/platform/build-*/build.log"
fi

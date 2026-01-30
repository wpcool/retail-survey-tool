"""
应用配置
"""
# 后端API地址（部署时需要修改）

# macOS/Windows 本地开发（直接在电脑上运行App）：
API_BASE_URL = "http://localhost:8000"

# Android模拟器使用：
# API_BASE_URL = "http://10.0.2.2:8000"

# 真机测试使用（替换为你的电脑实际IP，手机和电脑在同一WiFi）：
# API_BASE_URL = "http://192.168.1.xxx:8000"

# 生产环境：
# API_BASE_URL = "https://your-server.com"

# 应用配置
APP_NAME = "零售调研工具"
APP_VERSION = "1.0.0"

# 本地存储
DATA_DIR = "app_data"

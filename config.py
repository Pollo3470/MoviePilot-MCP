# config.py
import os

# 从环境变量或直接设置 MoviePilot 的基础 URL
# 例如: 'http://localhost:3000' 或 'https://your-moviepilot.com'
MOVIEPILOT_BASE_URL = os.getenv('MOVIEPILOT_BASE_URL', 'http://localhost:3000')

# 可以选择在此处存储默认凭据（不推荐用于生产环境）
MOVIEPILOT_USERNAME = os.getenv('MOVIEPILOT_USERNAME', 'your_username')
MOVIEPILOT_PASSWORD = os.getenv('MOVIEPILOT_PASSWORD', 'your_password')

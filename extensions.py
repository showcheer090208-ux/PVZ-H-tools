# extensions.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化全局拦截器
# 基础防御：任何 IP 每天最多访问 1000 次，每小时最多访问 100 次
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://"
)
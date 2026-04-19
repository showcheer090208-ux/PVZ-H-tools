# app.py
from flask import Flask
from extensions import limiter
from config import Config
from blueprints.unity import unity_bp
from blueprints.forum import forum_bp
from blueprints.home import home_bp
from blueprints.deck_editor import deck_editor_bp
from blueprints.auth import auth_bp
from flask import request
from database import supabase
from blueprints.card_sender import card_sender_bp
from blueprints.pack_buyer import pack_buyer_bp
from blueprints.downloads import downloads_bp

app = Flask(__name__)
app.config.from_object(Config)

limiter.init_app(app)

# 注册蓝图
app.register_blueprint(downloads_bp)
app.register_blueprint(pack_buyer_bp)
app.register_blueprint(card_sender_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(deck_editor_bp)
app.register_blueprint(home_bp) 
app.register_blueprint(unity_bp)
app.register_blueprint(forum_bp)

@app.context_processor
def inject_user():
    token = request.cookies.get('access_token')
    current_user = None
    
    if token:
        try:
            user_res = supabase.auth.get_user(token)
            if user_res and user_res.user:
                profile_res = supabase.table('profiles') \
                    .select('*') \
                    .eq('id', user_res.user.id) \
                    .execute()
                if profile_res.data:
                    raw_user = profile_res.data[0]
                    current_user = {k: (str(v) if k == 'id' else v) for k, v in raw_user.items()}
        except Exception as e:
            pass # 忽略过期错误
            
    return dict(
        current_user=current_user,
        supabase_url=Config.SUPABASE_URL,
        supabase_key=Config.SUPABASE_KEY,
        access_token=token # 🚨 【新增这一行】把后端拿到的 Token 传给前端
    )

@app.after_request
def add_header(response):
    """
    强制禁用敏感页面的浏览器缓存，确保登录/登出状态实时刷新
    """
    # 只要 URL 路径中包含 auth (登录、注册、登出) 或 profile (个人中心)
    if "auth" in request.path or "profile" in request.path:
        # no-store: 告诉浏览器绝对不要在本地存储页面的任何版本
        # no-cache: 每次使用前必须去服务器验证
        # must-revalidate: 一旦过期（此处设为0）必须重新验证
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
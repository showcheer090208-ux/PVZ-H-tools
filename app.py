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

app = Flask(__name__)
app.config.from_object(Config)

limiter.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(deck_editor_bp)
app.register_blueprint(home_bp) 
app.register_blueprint(unity_bp)
app.register_blueprint(forum_bp)

@app.context_processor
def inject_user():
    """
    全局上下文处理器：
    每次渲染 HTML 前都会执行。它会拦截用户的 Cookie，验证身份，
    并将数据库中的 Profile 资料注入为全局变量 `current_user`。
    """
    token = request.cookies.get('access_token')
    current_user = None
    
    if token:
        try:
            # 1. 拿 Token 向 Supabase 验明正身
            user_res = supabase.auth.get_user(token)
            if user_res and user_res.user:
                # 2. 拿到真实的 Auth ID 后，去咱们的业务表 profiles 里查他的昵称和头像
                profile_res = supabase.table('profiles') \
                    .select('*') \
                    .eq('id', user_res.user.id) \
                    .execute()
                
                if profile_res.data:
                    current_user = profile_res.data[0]
        except Exception as e:
            # Token 过期或伪造时会抛出异常，此时静默处理，视为未登录
            print(f"身份验证失败: {e}")
            
    # 把查到的信息装进字典，这样在所有的 html 文件里都能直接写 {{ current_user.username }} 了
    return dict(current_user=current_user)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
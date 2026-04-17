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

app = Flask(__name__)
app.config.from_object(Config)

limiter.init_app(app)

# 注册蓝图
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
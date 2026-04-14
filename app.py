# app.py
from flask import Flask
from config import Config
from blueprints.unity import unity_bp
from blueprints.forum import forum_bp
from blueprints.home import home_bp
from blueprints.deck_editor import deck_editor_bp

app = Flask(__name__)
app.config.from_object(Config)

# 注册蓝图
app.register_blueprint(deck_editor_bp)
app.register_blueprint(home_bp) 
app.register_blueprint(unity_bp)
app.register_blueprint(forum_bp)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
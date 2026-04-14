# blueprints/home.py
from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    # 渲染一个全新的“卡片式导航大厅”
    return render_template('index.html', current_tab='home')

@home_bp.route('/tools')
def tools():
    # 把之前丢失的路由补回来
    return render_template('tab_coming_soon.html', current_tab='tools')
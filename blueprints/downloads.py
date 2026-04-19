# blueprints/downloads.py
from flask import Blueprint, render_template, request, jsonify, redirect, current_app
from extensions import limiter
from database import supabase
import json
import os

downloads_bp = Blueprint('downloads', __name__)

def load_downloads_data():
    """读取本地 JSON 充当临时数据库"""
    file_path = os.path.join(current_app.root_path, 'data', 'downloads.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('tools', [])
    except Exception as e:
        print(f"读取下载列表失败: {e}")
        return []

@downloads_bp.route('/downloads')
def index():
    """资源下载大厅页面"""
    tools = load_downloads_data()
    return render_template('tab_downloads.html', tools=tools)

@downloads_bp.route('/api/download/<item_id>')
@limiter.limit("5 per minute") # 防止脚本恶意狂刷下载链接
def trigger_download(item_id):
    """处理下载请求，进行权限校验并返回真实地址"""
    tools = load_downloads_data()
    target_tool = next((t for t in tools if t['id'] == item_id), None)
    
    if not target_tool:
        return render_template('error.html', msg="未找到该资源，可能已被下架。"), 404
        
    # 如果该资源需要登录才能下载
    if target_tool.get('login_required'):
        token = request.cookies.get('access_token')
        if not token:
            return render_template('error.html', msg="权限不足：此为核心资源，请先登录账号后再下载！"), 401
            
        try:
            # 验证 Token 有效性
            user_res = supabase.auth.get_user(token)
            if not user_res or not user_res.user:
                raise Exception("Token invalid")
        except Exception:
            return render_template('error.html', msg="登录凭证已失效，请重新登录！"), 401

    # 【后期扩展点】目前直接跳转到外部直链。
    # 如果之后你用 Supabase Storage，可以在这里通过 target_tool['id'] 向 Supabase 请求生成一个有时效性的 Signed URL 再跳转。
    return redirect(target_tool['url'])
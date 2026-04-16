# blueprints/auth.py
from flask import Blueprint, request, render_template, redirect, make_response, jsonify
from functools import wraps
from database import supabase

auth_bp = Blueprint('auth', __name__)

# ==================== 装饰器：管理员权限校验 ====================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({"status": "error", "message": "权限不足"}), 403
        
        try:
            # 1. 验证用户身份
            user_res = supabase.auth.get_user(token)
            uid = user_res.user.id
            # 2. 检查 profiles 表里的 is_admin 字段
            profile = supabase.table("profiles").select("is_admin").eq("id", uid).single().execute()
            
            if not profile.data or not profile.data.get('is_admin'):
                return jsonify({"status": "error", "message": "您不是管理员"}), 403
        except Exception as e:
            return jsonify({"status": "error", "message": "鉴权失败"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# ==================== 路由：登录与注册 ====================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if request.cookies.get('access_token'):
            return redirect('/forum')
        return render_template('login.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    action = request.form.get('action') 
    
    try:
        if action == 'register':
            supabase.auth.sign_up({"email": email, "password": password})
            return render_template('login.html', success="🎉 注册成功！系统已自动生成初始昵称，请直接登录。")
            
        elif action == 'login':
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            token = res.session.access_token
            response = make_response(redirect('/forum'))
            response.set_cookie('access_token', token, httponly=True, max_age=60*60*24*7)
            return response
            
    except Exception as e:
        error_msg = "账号或密码错误" if "Invalid login credentials" in str(e) else str(e)
        return render_template('login.html', error=error_msg)

# ==================== 路由：退出登录 ====================
@auth_bp.route('/logout')
def logout():
    response = make_response(redirect('/forum'))
    response.delete_cookie('access_token')
    return response

# ==================== 路由：个人中心页面 ====================
@auth_bp.route('/profile')
def profile():
    return render_template('profile.html')

# ==================== API：更新自定义昵称 ====================
@auth_bp.route('/api/profile/update', methods=['POST'])
def update_profile():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "未登录"}), 401
        
    try:
        user_res = supabase.auth.get_user(token)
        uid = user_res.user.id
        
        data = request.json
        new_username = data.get('username', '').strip()
        
        # 1. 基础长度校验
        if len(new_username) < 2 or len(new_username) > 15:
            return jsonify({"status": "error", "message": "昵称长度需在 2-15 之间"}), 400

        # 2. 查重逻辑：检查是否有其他人（除了自己）用了这个名字
        existing = supabase.table("profiles").select("id").eq("username", new_username).neq("id", uid).execute()
        if existing.data:
            return jsonify({"status": "error", "message": "该昵称已被占用，请换一个吧"}), 400

        # 3. 写入数据库
        supabase.table("profiles").update({"username": new_username}).eq("id", uid).execute()
        return jsonify({"status": "success", "message": "昵称修改成功"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
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
            user_res = supabase.auth.get_user(token)
            uid = user_res.user.id
            profile = supabase.table("profiles").select("is_admin").eq("id", uid).single().execute()
            
            if not profile.data or not profile.data.get('is_admin'):
                return jsonify({"status": "error", "message": "您不是管理员"}), 403
        except Exception as e:
            return jsonify({"status": "error", "message": "鉴权失败"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# ==================== 路由：登录与注册 ====================
# ==================== 路由：登录与注册 ====================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        token = request.cookies.get('access_token')
        
        # 🚨 逻辑优化：不再是“有 Cookie 就跳转”，而是“有【有效】Token 才跳转”
        if token:
            try:
                # 尝试用这个 token 去请求 supabase 验证用户
                user_res = supabase.auth.get_user(token)
                if user_res and user_res.user:
                    # 只有真正拿到了用户信息，才说明已登录，跳转大厅
                    return redirect('/forum')
            except Exception:
                # 如果 token 验证失败（过期或伪造），说明是无效残留
                # 此时我们主动清除这个残留 Cookie，并继续展示登录界面
                resp = make_response(render_template('login.html'))
                resp.delete_cookie('access_token', path='/')
                return resp
        
        return render_template('login.html')
    
    # POST 逻辑部分
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
            
            # 登录成功，跳转大厅
            response = make_response(redirect('/forum'))
            # 确保 path='/' 覆盖全站，max_age 建议设长一点确保稳定性
            response.set_cookie('access_token', token, httponly=True, max_age=60*60*24*7, path='/')
            return response
            
    except Exception as e:
        error_msg = "账号或密码错误" if "Invalid login credentials" in str(e) else str(e)
        return render_template('login.html', error=error_msg)

# ==================== 路由：退出登录 ====================
@auth_bp.route('/logout')
def logout():
    """
    彻底登出：销毁服务端会话 + 强制清除本地状态
    """
    token = request.cookies.get('access_token')
    if token:
        try:
            # 告诉 Supabase 销毁这个 session
            supabase.auth.sign_out()
        except:
            pass
            
    # 跳转回登录页，并强制删除 Cookie
    response = make_response(redirect('/login'))
    response.delete_cookie('access_token', path='/')
    
    # 额外保险：通过 Header 告诉浏览器，登出动作后不要使用缓存
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# ==================== 路由：个人中心 ====================
@auth_bp.route('/profile')
def profile():
    return render_template('profile.html')

# ==================== API：更新昵称 ====================
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
        
        if len(new_username) < 2 or len(new_username) > 15:
            return jsonify({"status": "error", "message": "昵称长度需在 2-15 之间"}), 400

        existing = supabase.table("profiles").select("id").eq("username", new_username).neq("id", uid).execute()
        if existing.data:
            return jsonify({"status": "error", "message": "该昵称已被占用，请换一个吧"}), 400

        supabase.table("profiles").update({"username": new_username}).eq("id", uid).execute()
        return jsonify({"status": "success", "message": "昵称修改成功"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
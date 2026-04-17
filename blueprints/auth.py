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
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if request.method == 'GET':
        token = request.cookies.get('access_token')
        if token:
            try:
                user_res = supabase.auth.get_user(token)
                if user_res and user_res.user:
                    return redirect('/forum')
            except Exception:
                resp = make_response(render_template('login.html'))
                resp.delete_cookie('access_token', path='/')
                return resp
        return render_template('login.html', show_register=False)
    
    action = request.form.get('action') 
    email = request.form.get('email')
    password = request.form.get('password')
    
    try:
        if action == 'register':
            username = request.form.get('username', '').strip()
            confirm_password = request.form.get('confirm_password')

            # 1. 基础校验
            if password != confirm_password:
                return render_template('login.html', error="两次输入的密码不一致", show_register=True)
            if len(username) < 2 or len(username) > 15:
                return render_template('login.html', error="昵称长度需在 2-15 之间", show_register=True)

            # 2. 昵称唯一性查重
            existing = supabase.table("profiles").select("id").eq("username", username).execute()
            if existing.data:
                return render_template('login.html', error="该昵称已被占用，换一个吧！", show_register=True)

            # 3. 执行注册 (将 username 附带在元数据中)
            res = supabase.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {
                    "data": {"username": username}
                }
            })
            
            # 4. 根据后台是否强制验证邮箱，决定后续走向
            if res.user and not res.session:
                # 开启了邮箱验证：没有颁发 session，提示去查收邮件
                return render_template('login.html', success="🎉 注册成功！请查收邮件验证链接（若未收到请检查垃圾箱）。", show_register=False)
            elif res.session:
                # 关闭了邮箱验证：直接拿到 session，尝试同步更新 profiles 并自动登录
                try:
                    supabase.table("profiles").update({"username": username}).eq("id", res.user.id).execute()
                except Exception:
                    pass # 忽略更新错误，因为有些 Supabase 触发器会自动写入
                
                token = res.session.access_token
                response = make_response(redirect('/forum'))
                response.set_cookie('access_token', token, httponly=True, max_age=60*60*24*7, path='/')
                return response
                
        elif action == 'login':
            remember_me = request.form.get('remember_me')
            
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            token = res.session.access_token
            
            response = make_response(redirect('/forum'))
            # 如果勾选记住我，保存7天；否则关闭浏览器失效
            max_age = 60*60*24*7 if remember_me else None
            response.set_cookie('access_token', token, httponly=True, max_age=max_age, path='/')
            return response
            
    except Exception as e:
        error_str = str(e)
        if "Email rate limit exceeded" in error_str:
            error_msg = "请求太频繁啦！邮件服务已达上限，请稍后再试。"
        elif "Invalid login credentials" in error_str:
            error_msg = "邮箱账号或密码错误"
        elif "User already registered" in error_str:
            error_msg = "该邮箱已被注册，请直接登录"
        elif "Password should be" in error_str:
            error_msg = "密码长度不符合安全要求"
        else:
            error_msg = f"系统提示: {error_str}"
            
        # 发生错误时，如果用户刚才是在注册，就让他留在注册 Tab
        is_register = (action == 'register')
        return render_template('login.html', error=error_msg, show_register=is_register)

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
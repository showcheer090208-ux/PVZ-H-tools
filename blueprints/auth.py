# blueprints/auth.py
import secrets
import string
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, render_template, redirect, make_response, jsonify
from functools import wraps
from database import supabase
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

# ==================== 工具函数：生成随机码 ====================
def generate_random_code(length=8):
    """生成带有专属前缀的随机邀请码"""
    chars = string.ascii_uppercase + string.digits
    return 'PVZH-' + ''.join(secrets.choice(chars) for _ in range(length))

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
    email = request.form.get('email', '').strip()
    password = request.form.get('password')
    
    try:
        if action == 'register':
            username = request.form.get('username', '').strip()
            confirm_pwd = request.form.get('confirm_password')
            invite_code = request.form.get('invitation_code', '').strip().upper()

            # 1. 基础校验
            if password != confirm_pwd:
                return render_template('login.html', error="两次输入的密码不一致", show_register=True)
            if not invite_code:
                return render_template('login.html', error="必须填写社区邀请码", show_register=True)
            if len(username) < 2 or len(username) > 15:
                return render_template('login.html', error="昵称长度需在 2-15 之间", show_register=True)
            
            # 2. 核心：邀请码校验
            code_res = supabase.table("invitation_codes").select("*").eq("code", invite_code).execute()
            if not code_res.data:
                return render_template('login.html', error="无效的邀请码，请检查是否拼写错误", show_register=True)
            
            code_info = code_res.data[0]
            if code_info['used_count'] >= code_info['max_uses']:
                return render_template('login.html', error="该邀请码的使用次数已达上限", show_register=True)

            # 3. 昵称唯一性检查
            existing = supabase.table("profiles").select("id").eq("username", username).execute()
            if existing.data:
                return render_template('login.html', error="该昵称已被占用，换一个炫酷的吧", show_register=True)

            # 4. 执行 Supabase 注册
            res = supabase.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {
                    "data": {"username": username} # 将昵称写入元数据
                }
            })
            
            if res.user:
                # 5. 扣除邀请码额度
                supabase.table("invitation_codes").update({
                    "used_count": code_info['used_count'] + 1
                }).eq("code", invite_code).execute()
                
                # 6. 后端兜底：确保 profile 写入
                try:
                    supabase.table("profiles").upsert({
                        "id": res.user.id,
                        "username": username
                    }).execute()
                except Exception:
                    pass
                
                # 7. 登录状态处理
                if res.session: # 如果关闭了邮件验证，直接登录
                    token = res.session.access_token
                    resp = make_response(redirect('/forum'))
                    resp.set_cookie('access_token', token, httponly=True, max_age=60*60*24*7, path='/')
                    return resp
                else: # 如果依然开启邮件验证
                    return render_template('login.html', success="🎉 注册成功！请前往邮箱验证激活账号。", show_register=False)

        elif action == 'login':
            remember_me = request.form.get('remember_me')
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if not res.session:
                 return render_template('login.html', error="账号尚未激活，请查收验证邮件", show_register=False)

            token = res.session.access_token
            response = make_response(redirect('/forum'))
            max_age = 60*60*24*7 if remember_me else None
            response.set_cookie('access_token', token, httponly=True, max_age=max_age, path='/')
            return response
            
    except Exception as e:
        error_str = str(e)
        if "Email rate limit exceeded" in error_str:
            error_msg = "请求太频繁啦！系统繁忙，请 1 小时后再试。"
        elif "Invalid login credentials" in error_str:
            error_msg = "邮箱账号或密码错误"
        elif "User already registered" in error_str:
            error_msg = "该邮箱已被注册，请直接登录"
        else:
            error_msg = f"系统提示: {error_str}"
            
        return render_template('login.html', error=error_msg, show_register=(action == 'register'))


# ==================== 路由：退出登录 ====================
@auth_bp.route('/logout')
def logout():
    token = request.cookies.get('access_token')
    if token:
        try: supabase.auth.sign_out()
        except: pass
            
    response = make_response(redirect('/login'))
    response.delete_cookie('access_token', path='/')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ==================== 路由：个人中心 ====================
@auth_bp.route('/profile')
def profile():
    return render_template('profile.html')


# ==================== API：生成邀请码 ====================
@auth_bp.route('/api/invitation/generate', methods=['POST'])
def api_generate_code():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    
    try:
        user_res = supabase.auth.get_user(token)
        uid = user_res.user.id
        
        # 获取用户状态
        profile = supabase.table("profiles").select("*").eq("id", uid).single().execute()
        is_admin = profile.data.get('is_admin', False)
        
        # 解析 created_at 处理时区兼容性
        created_at_str = profile.data['created_at'].replace('Z', '+00:00')
        created_at = datetime.fromisoformat(created_at_str)
        now = datetime.now(timezone.utc)
        
        if not is_admin:
            # 限制1：注册满24小时
            if now - created_at < timedelta(days=1):
                return jsonify({"status": "error", "message": "萌新指挥官请先熟悉工坊，注册满 24 小时后即可生成邀请码哦"}), 403
            
            # 限制2：每周生成数量限制
            last_week = now - timedelta(days=7)
            recent_codes = supabase.table("invitation_codes") \
                .select("code") \
                .eq("creator_id", uid) \
                .gt("created_at", last_week.isoformat()) \
                .execute()
                
            if recent_codes.data:
                return jsonify({"status": "error", "message": "次数已用尽！由于社区等级限制，您每周只能生成 1 个邀请码"}), 403

        # 生成逻辑
        new_code = generate_random_code()
        
        # 如果前端传了 max_uses 且是管理员，就用前端传的；否则普通用户固定 3 次
        data = request.json or {}
        max_uses = int(data.get('max_uses', 999)) if is_admin else 3
        
        supabase.table("invitation_codes").insert({
            "code": new_code,
            "creator_id": uid,
            "max_uses": max_uses
        }).execute()
        
        return jsonify({"status": "success", "code": new_code, "max_uses": max_uses}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": "系统错误，请稍后再试"}), 500


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
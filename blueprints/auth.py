# blueprints/auth.py
import secrets
import string
import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, render_template, redirect, make_response, jsonify, url_for, current_app
from functools import wraps
from database import supabase
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

# ==================== 常量配置 ====================
COOKIE_MAX_AGE = 7 * 24 * 3600  # 7天
USERNAME_MIN_LEN = 2
USERNAME_MAX_LEN = 15
INVITE_CODE_PREFIX = 'PVZH-'
INVITE_CODE_LENGTH = 8

# ==================== 工具函数 ====================
def generate_random_code(length=INVITE_CODE_LENGTH):
    """生成带有专属前缀的随机邀请码"""
    chars = string.ascii_uppercase + string.digits
    return f'{INVITE_CODE_PREFIX}{"".join(secrets.choice(chars) for _ in range(length))}'

def get_current_user(token=None):
    """获取当前登录用户信息，返回 (user, profile) 或 (None, None)"""
    token = token or request.cookies.get('access_token')
    if not token:
        return None, None
    
    try:
        user_res = supabase.auth.get_user(token)
        if not user_res or not user_res.user:
            return None, None
        
        user = user_res.user
        profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
        return user, profile.data if profile.data else None
    except Exception:
        return None, None

def validate_username(username):
    """校验用户名格式"""
    if not username or len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
        return False, f"昵称长度需在 {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN} 之间"
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', username):
        return False, "昵称只能包含中文、字母、数字和下划线"
    return True, ""

def set_auth_cookie(response, token, max_age=COOKIE_MAX_AGE):
    """安全设置认证 Cookie"""
    response.set_cookie(
        'access_token',
        token,
        httponly=True,      # 防御 XSS
        secure=True,        # 仅 HTTPS 传输（生产环境必须）
        samesite='Lax',     # 防御 CSRF
        max_age=max_age,
        path='/'
    )
    return response

def clear_auth_cookie(response):
    """清除认证 Cookie"""
    response.delete_cookie('access_token', path='/')
    return response

# ==================== 装饰器 ====================
def login_required(f):
    """登录校验装饰器（用于 API）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({"status": "error", "message": "请先登录"}), 401
        
        try:
            supabase.auth.get_user(token)
        except Exception:
            return jsonify({"status": "error", "message": "登录已过期，请重新登录"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限校验装饰器"""
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
        except Exception:
            return jsonify({"status": "error", "message": "凭证无效，请重新登录"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# ==================== 页面路由 ====================
@auth_bp.route('/login', methods=['GET'])
def login_page():
    """登录页面"""
    # 检查是否已登录
    token = request.cookies.get('access_token')
    if token:
        try:
            user_res = supabase.auth.get_user(token)
            if user_res and user_res.user:
                next_url = request.args.get('next', '/')
                return redirect(next_url)
        except Exception:
            pass
    
    next_url = request.args.get('next', '/')
    return render_template('login.html', next=next_url)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """登录处理"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password')
    next_url = request.form.get('next', '/')
    remember_me = request.form.get('remember_me') == 'on'
    
    if not email or not password:
        return render_template('login.html', error="请填写邮箱和密码", next=next_url)
    
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if not res or not res.session:
            return render_template('login.html', error="登录失败，请检查账号密码", next=next_url)
        
        token = res.session.access_token
        
        # 获取用户信息
        user, profile = get_current_user(token)
        username = profile.get('username', '指挥官') if profile else '指挥官'
        
        # 安全设置响应
        max_age = COOKIE_MAX_AGE if remember_me else None
        response = make_response(redirect(next_url))
        response = set_auth_cookie(response, token, max_age) if max_age else set_auth_cookie(response, token, COOKIE_MAX_AGE)
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Login failed for {email}: {e}")
        return render_template('login.html', error="账号或密码错误", next=next_url)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("2 per minute")
def register():
    """注册处理"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')  # 现在能获取到了
    username = request.form.get('username', '').strip()
    
    # 兼容两种字段名：invitation_code（新版）和 invite_code（旧版）
    invite_code = request.form.get('invitation_code', '') or request.form.get('invite_code', '')
    invite_code = invite_code.strip().upper()
    
    # 1. 基础校验
    if not all([email, password, confirm_password, username, invite_code]):
        print(f"[DEBUG] 缺失字段 - email:{email}, password:{bool(password)}, confirm:{bool(confirm_password)}, username:{username}, invite_code:{invite_code}")
        return render_template('login.html', error="请填写所有字段", tab="register")
    
    # 2. 密码一致性校验
    if password != confirm_password:
        return render_template('login.html', error="两次输入的密码不一致", tab="register")
    
    # 3. 密码长度校验
    if len(password) < 6:
        return render_template('login.html', error="密码长度至少为 6 位", tab="register")
    
    # 4. 用户名格式校验
    is_valid, username_error = validate_username(username)
    if not is_valid:
        return render_template('login.html', error=username_error, tab="register")
    
    # 2. 校验邀请码
    try:
        code_res = supabase.table("invitation_codes").select("*").eq("code", invite_code).execute()
        if not code_res.data:
            return render_template('login.html', error="无效的邀请码，请检查是否拼写错误", tab="register")
        
        code_info = code_res.data[0]
        if code_info['used_count'] >= code_info['max_uses']:
            return render_template('login.html', error="该邀请码的使用次数已达上限", tab="register")
    except Exception as e:
        current_app.logger.error(f"Invite code check failed: {e}")
        return render_template('login.html', error="系统错误，请稍后再试", tab="register")
    
    # 3. 昵称唯一性检查
    try:
        existing = supabase.table("profiles").select("id").eq("username", username).execute()
        if existing.data:
            return render_template('login.html', error="该昵称已被占用，换一个炫酷的吧", tab="register")
    except Exception as e:
        current_app.logger.error(f"Username check failed: {e}")
    
    # 4. 执行注册
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"username": username}
            }
        })
        
        if not res.user:
            return render_template('login.html', error="注册失败，请稍后再试", tab="register")
        
        uid = res.user.id
        
        # 5. 创建 Profile（兜底写入）
        try:
            supabase.table("profiles").upsert({
                "id": uid,
                "username": username
            }).execute()
        except Exception as e:
            current_app.logger.error(f"Profile creation failed for {uid}: {e}")
        
        # 6. 更新邀请码使用次数
        try:
            supabase.table("invitation_codes").update({
                "used_count": code_info['used_count'] + 1
            }).eq("code", invite_code).execute()
        except Exception as e:
            current_app.logger.error(f"Invite code update failed: {e}")
        
        # 7. 判断是否需要邮箱验证
        if res.session:
            # 自动登录
            token = res.session.access_token
            response = make_response(redirect('/forum'))
            response = set_auth_cookie(response, token)
            return response
        else:
            return render_template('error.html',
                                 msg="注册成功！请前往邮箱验证激活账号。",
                                 title="注册成功",
                                 type="success",
                                 target="/login")
        
    except Exception as e:
        error_str = str(e)
        current_app.logger.error(f"Registration failed: {error_str}")
        
        if "User already registered" in error_str:
            error_msg = "该邮箱已被注册，请直接登录"
        elif "Password should be at least 6 characters" in error_str:
            error_msg = "密码长度至少为 6 位"
        else:
            error_msg = f"注册失败: {error_str}"
        
        return render_template('login.html', error=error_msg, tab="register")

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("2 per minute")
def forgot_password():
    """忘记密码 - 发送重置邮件"""
    email = request.form.get('reset_email', '').strip()
    
    if not email:
        return render_template('login.html', error="请输入注册邮箱", tab="reset")
    
    try:
        redirect_url = request.url_root.rstrip('/') + '/reset-password-confirm'
        supabase.auth.reset_password_email(email, options={"redirect_to": redirect_url})
        
        return render_template('error.html',
                             msg="重置邮件已发送至您的邮箱，请检查收件箱（或垃圾邮件）。",
                             title="邮件已发送",
                             type="success",
                             target="/login")
    except Exception as e:
        current_app.logger.error(f"Password reset failed for {email}: {e}")
        return render_template('login.html', error="发送重置邮件失败，请确认邮箱是否正确或稍后再试。", tab="reset")

@auth_bp.route('/logout')
def logout():
    """退出登录"""
    token = request.cookies.get('access_token')
    
    # 尝试在服务端登出（不阻塞主流程）
    if token:
        try:
            supabase.auth.admin.sign_out(token)
        except Exception:
            pass
    
    response = make_response(redirect('/login'))
    response = clear_auth_cookie(response)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@auth_bp.route('/profile')
@login_required
def profile_page():
    """个人中心页面"""
    return render_template('profile.html')

# ==================== API 路由 ====================
@auth_bp.route('/api/invitation/generate', methods=['POST'])
@login_required
def api_generate_code():
    """生成邀请码 API"""
    token = request.cookies.get('access_token')
    user, profile = get_current_user(token)
    
    if not user or not profile:
        return jsonify({"status": "error", "message": "用户不存在"}), 401
    
    uid = user.id
    is_admin = profile.get('is_admin', False)
    
    # 时区处理
    created_at_str = profile.get('created_at', '').replace('Z', '+00:00')
    if created_at_str:
        created_at = datetime.fromisoformat(created_at_str)
        now = datetime.now(timezone.utc)
        
        if not is_admin:
            # 限制1：注册满24小时
            if now - created_at < timedelta(days=1):
                return jsonify({
                    "status": "error",
                    "message": "萌新指挥官请先熟悉工坊，注册满 24 小时后即可生成邀请码哦"
                }), 403
            
            # 限制2：每周生成数量限制
            last_week = now - timedelta(days=7)
            recent_codes = supabase.table("invitation_codes") \
                .select("code") \
                .eq("creator_id", uid) \
                .gte("created_at", last_week.isoformat()) \
                .execute()
                
            if recent_codes.data and len(recent_codes.data) >= 1:
                return jsonify({
                    "status": "error",
                    "message": "次数已用尽！由于社区等级限制，您每周只能生成 1 个邀请码"
                }), 403
    
    # 生成邀请码
    try:
        new_code = generate_random_code()
        
        data = request.json or {}
        max_uses = int(data.get('max_uses', 999)) if is_admin else 3
        
        supabase.table("invitation_codes").insert({
            "code": new_code,
            "creator_id": uid,
            "max_uses": max_uses,
            "used_count": 0
        }).execute()
        
        return jsonify({
            "status": "success",
            "code": new_code,
            "max_uses": max_uses
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Invite code generation failed: {e}")
        return jsonify({"status": "error", "message": "系统错误，请稍后再试"}), 500

@auth_bp.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    """更新用户昵称"""
    token = request.cookies.get('access_token')
    user, _ = get_current_user(token)
    
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 401
    
    uid = user.id
    data = request.json
    new_username = data.get('username', '').strip()
    
    # 校验
    is_valid, error_msg = validate_username(new_username)
    if not is_valid:
        return jsonify({"status": "error", "message": error_msg}), 400
    
    # 唯一性检查
    try:
        existing = supabase.table("profiles").select("id").eq("username", new_username).neq("id", uid).execute()
        if existing.data:
            return jsonify({"status": "error", "message": "该昵称已被占用，请换一个吧"}), 400
    except Exception as e:
        current_app.logger.error(f"Username uniqueness check failed: {e}")
    
    # 更新
    try:
        supabase.table("profiles").update({"username": new_username}).eq("id", uid).execute()
        return jsonify({"status": "success", "message": "昵称修改成功"}), 200
    except Exception as e:
        current_app.logger.error(f"Profile update failed: {e}")
        return jsonify({"status": "error", "message": "更新失败，请稍后再试"}), 500

@auth_bp.route('/api/user/info', methods=['GET'])
@login_required
def get_user_info():
    """获取当前用户信息 API"""
    token = request.cookies.get('access_token')
    user, profile = get_current_user(token)
    
    if not user or not profile:
        return jsonify({"status": "error", "message": "用户不存在"}), 401
    
    return jsonify({
        "status": "success",
        "data": {
            "id": user.id,
            "email": user.email,
            "username": profile.get('username'),
            "is_admin": profile.get('is_admin', False),
            "created_at": profile.get('created_at')
        }
    }), 200
    
# ==================== API：校验邀请码有效性 ====================
@auth_bp.route('/api/invitation/check', methods=['POST'])
def api_check_invitation():
    """校验邀请码是否有效（用于前端实时校验）"""
    data = request.json
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({"status": "error", "message": "邀请码不能为空"}), 400
    
    try:
        code_res = supabase.table("invitation_codes").select("*").eq("code", code).execute()
        
        if not code_res.data:
            return jsonify({"status": "error", "message": "无效的邀请码"}), 200  # 返回200便于前端处理
        
        code_info = code_res.data[0]
        if code_info['used_count'] >= code_info['max_uses']:
            return jsonify({"status": "error", "message": "该邀请码已达使用上限"}), 200
        
        return jsonify({"status": "success", "message": "邀请码有效"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": "校验失败，请稍后再试"}), 500
    
# ==================== 路由：密码重置确认页面 ====================
@auth_bp.route('/reset-password-confirm', methods=['GET'])
def reset_password_confirm_page():
    """显示密码重置页面"""
    return render_template('reset_password_confirm.html')

# ==================== API：确认重置密码 ====================
@auth_bp.route('/api/reset-password/confirm', methods=['POST'])
@limiter.limit("3 per minute")
def reset_password_confirm():
    """执行密码重置"""
    data = request.json
    access_token = data.get('access_token')
    new_password = data.get('password')
    
    if not access_token or not new_password:
        return jsonify({"status": "error", "message": "参数不完整"}), 400
    
    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "密码长度至少为 6 位"}), 400
    
    try:
        # 使用 access_token 更新密码
        supabase.auth.update_user({
            "password": new_password
        }, access_token)
        
        return jsonify({"status": "success", "message": "密码重置成功"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Password reset failed: {e}")
        return jsonify({"status": "error", "message": "重置失败，链接可能已过期"}), 400
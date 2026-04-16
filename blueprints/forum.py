# blueprints/forum.py
from flask import Blueprint, render_template, request, jsonify
from blueprints.auth import admin_required
from database import supabase
from datetime import datetime, timedelta

forum_bp = Blueprint('forum', __name__)

# ==================== 路由：社区大厅 (帖子列表) ====================
@forum_bp.route('/forum')
def index():
    try:
        cat_res = supabase.table("categories").select("*").order("sort_order").execute()
        categories = cat_res.data
    except:
        categories = []

    try:
        # 【核心修改点】增加 honor_title 和 honor_icon 的拉取
        post_res = supabase.table("posts") \
            .select("*, profiles:profiles!posts_author_id_fkey(username, avatar_url, honor_title, honor_icon), categories(name, icon)") \
            .order("is_pinned", desc=True) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        posts = post_res.data
        
        for post in posts:
            try:
                time_str = post['created_at'][:19]
                utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                bj_time = utc_time + timedelta(hours=8)
                post['formatted_time'] = bj_time.strftime('%Y-%m-%d %H:%M')
            except Exception:
                post['formatted_time'] = post['created_at'][:10]
    except Exception as e:
        print(f"帖子读取失败: {e}")
        posts = []
        
    return render_template('tab_forum.html', current_tab='forum', categories=categories, posts=posts)

# ==================== 路由：帖子详情页 ====================
@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    try:
        # 1. 查主帖（拉取荣誉勋章信息）
        post_res = supabase.table("posts") \
            .select("*, profiles:profiles!posts_author_id_fkey(username, avatar_url, honor_title, honor_icon), categories(name, icon)") \
            .eq("id", post_id) \
            .execute()
            
        if not post_res.data:
            return render_template('error.html', message="帖子不存在或已被删除"), 404
        post = post_res.data[0]
        
        supabase.table("posts").update({"view_count": post.get("view_count", 0) + 1}).eq("id", post_id).execute()

        # 2. 查回复（同样拉取荣誉勋章信息）
        comments_res = supabase.table("post_comments") \
            .select("*, profiles(username, avatar_url, honor_title, honor_icon)") \
            .eq("post_id", post_id) \
            .order("created_at") \
            .execute()
        comments = comments_res.data

        def format_time(time_str):
            try:
                utc_time = datetime.strptime(time_str[:19], '%Y-%m-%dT%H:%M:%S')
                return (utc_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
            except:
                return time_str[:10]
                
        post['formatted_time'] = format_time(post['created_at'])
        for c in comments:
            c['formatted_time'] = format_time(c['created_at'])

    except Exception as e:
        print(f"详情页加载失败: {e}")
        return render_template('error.html', message="服务器异常"), 500

    return render_template('tab_post_detail.html', post=post, comments=comments)

# ==================== API：发布帖子 ====================
@forum_bp.route('/api/post', methods=['POST'])
def create_post():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
        
    try:
        user_res = supabase.auth.get_user(token)
        user_id = user_res.user.id
        
        data = request.json
        category_id = data.get('category_id')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or not content or not category_id:
            return jsonify({"status": "error", "message": "标题、内容和分区不能为空"}), 400
            
        supabase.table("posts").insert({
            "category_id": category_id,
            "author_id": user_id,
            "title": title[:50],
            "content": content[:1000]
        }).execute()
        return jsonify({"status": "success", "message": "发布成功！"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": "发帖失败"}), 500

# ==================== API：发布回复/楼中楼 ====================
@forum_bp.route('/api/comment', methods=['POST'])
def create_comment():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
        
    try:
        user_res = supabase.auth.get_user(token)
        user_id = user_res.user.id
        
        data = request.json
        post_id = data.get('post_id')
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id') 
        
        if not content or not post_id:
            return jsonify({"status": "error", "message": "回复内容不能为空"}), 400
            
        supabase.table("post_comments").insert({
            "post_id": post_id,
            "author_id": user_id,
            "parent_id": parent_id,
            "content": content[:1000]
        }).execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "回复失败"}), 500
    
# ==================== API：管理员删帖 ====================
@forum_bp.route('/api/post/delete/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_post(post_id):
    try:
        supabase.table("posts").delete().eq("id", post_id).execute()
        return jsonify({"status": "success", "message": "帖子已删除"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
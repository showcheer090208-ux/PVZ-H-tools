# blueprints/forum.py
from flask import Blueprint, redirect, render_template, request, jsonify
from blueprints.auth import admin_required
from database import supabase
from datetime import datetime, timedelta

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/forum')
def index():
    try:
        cat_res = supabase.table("categories").select("*").order("sort_order").execute()
        categories = cat_res.data
    except Exception:
        categories = []

    try:
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
        posts = []

    user_liked_post_ids = []
    token = request.cookies.get('access_token')
    if token:
        try:
            user_res = supabase.auth.get_user(token)
            if user_res and user_res.user:
                uid = user_res.user.id
                likes_res = supabase.table("post_likes").select("post_id").eq("user_id", uid).execute()
                user_liked_post_ids = [item['post_id'] for item in likes_res.data]
        except Exception:
            pass
            
    return render_template('tab_forum.html', current_tab='forum', categories=categories, posts=posts, user_liked_post_ids=user_liked_post_ids)

@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    try:
        post_res = supabase.table("posts") \
            .select("*, profiles:profiles!posts_author_id_fkey(username, avatar_url, honor_title, honor_icon), categories(name, icon)") \
            .eq("id", post_id) \
            .execute()
            
        if not post_res.data:
            return render_template('error.html', message="帖子不存在或已被删除"), 404
        post = post_res.data[0]
        
        supabase.table("posts").update({"view_count": post.get("view_count", 0) + 1}).eq("id", post_id).execute()

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
        return render_template('error.html', message="服务器异常"), 500

    return render_template('tab_post_detail.html', post=post, comments=comments)

@forum_bp.route('/api/post/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    try:
        uid = supabase.auth.get_user(token).user.id
        existing = supabase.table("post_likes").select("user_id").eq("post_id", post_id).eq("user_id", uid).execute()
        
        if existing.data:
            supabase.table("post_likes").delete().eq("post_id", post_id).eq("user_id", uid).execute()
            return jsonify({"status": "success", "action": "unliked"})
        else:
            supabase.table("post_likes").insert({"post_id": post_id, "user_id": uid}).execute()
            return jsonify({"status": "success", "action": "liked"})
    except Exception as e:
        return jsonify({"status": "error", "message": "操作失败"}), 500

@forum_bp.route('/api/post', methods=['POST'])
def create_post():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    try:
        user_res = supabase.auth.get_user(token)
        user_id = user_res.user.id
        data = request.json
        if not data.get('title') or not data.get('content') or not data.get('category_id'):
            return jsonify({"status": "error", "message": "标题、内容和分区不能为空"}), 400
            
        supabase.table("posts").insert({
            "category_id": data.get('category_id'),
            "author_id": user_id,
            "title": data.get('title')[:50],
            "content": data.get('content')[:1000],
            "image_urls": data.get('image_urls', [])
        }).execute()
        return jsonify({"status": "success", "message": "发布成功！"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "发帖失败"}), 500

@forum_bp.route('/api/comment', methods=['POST'])
def create_comment():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    try:
        user_id = supabase.auth.get_user(token).user.id
        data = request.json
        if not data.get('content') or not data.get('post_id'):
            return jsonify({"status": "error", "message": "回复内容不能为空"}), 400
            
        supabase.table("post_comments").insert({
            "post_id": data.get('post_id'),
            "author_id": user_id,
            "parent_id": data.get('parent_id'),
            "content": data.get('content')[:1000]
        }).execute()
        return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error", "message": "回复失败"}), 500
    
@forum_bp.route('/api/post/delete/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_post(post_id):
    try:
        supabase.table("posts").delete().eq("id", post_id).execute()
        return jsonify({"status": "success", "message": "帖子已删除"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🚨 新增：管理员置顶/取消置顶 API
@forum_bp.route('/api/post/pin/<int:post_id>', methods=['POST'])
@admin_required
def toggle_pin_post(post_id):
    try:
        post_res = supabase.table("posts").select("is_pinned").eq("id", post_id).single().execute()
        if not post_res.data:
            return jsonify({"status": "error", "message": "帖子不存在"}), 404
        
        current_status = post_res.data.get('is_pinned', False)
        new_status = not current_status
        
        supabase.table("posts").update({"is_pinned": new_status}).eq("id", post_id).execute()
        return jsonify({"status": "success", "is_pinned": new_status}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@forum_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect('/forum')

    try:
        # 🚨 核心黑科技：Supabase 的 or_ 和 ilike 结合，同时模糊搜索 标题 或 内容
        # ilike 是不区分大小写的模糊匹配
        search_query = f"title.ilike.%{q}%,content.ilike.%{q}%"
        
        post_res = supabase.table("posts") \
            .select("*, profiles:profiles!posts_author_id_fkey(username, avatar_url, honor_title, honor_icon), categories(name, icon)") \
            .or_(search_query) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        posts = post_res.data
        
        for post in posts:
            try:
                time_str = post['created_at'][:19]
                utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                post['formatted_time'] = (utc_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
            except Exception:
                post['formatted_time'] = post['created_at'][:10]
    except Exception as e:
        print(f"搜索失败: {e}")
        posts = []

    # 把点赞记录也查出来，让搜索结果页也能点赞
    user_liked_post_ids = []
    token = request.cookies.get('access_token')
    if token:
        try:
            user_res = supabase.auth.get_user(token)
            if user_res and user_res.user:
                uid = user_res.user.id
                likes_res = supabase.table("post_likes").select("post_id").eq("user_id", uid).execute()
                user_liked_post_ids = [item['post_id'] for item in likes_res.data]
        except Exception:
            pass

    return render_template('search.html', query=q, posts=posts, user_liked_post_ids=user_liked_post_ids)
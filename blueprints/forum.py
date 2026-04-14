# blueprints/forum.py
from flask import Blueprint, render_template, request, redirect
from database import supabase
from datetime import datetime, timedelta

# 创建蓝图对象
forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/forum')
def index():
    try:
        # 获取最新 50 条留言，按时间倒序排列
        response = supabase.table("comments").select("*").order("created_at", desc=True).limit(50).execute()
        comments = response.data
        
        # 将 Supabase 的 UTC 时间转换为北京时间 (UTC+8) 并格式化
        for comment in comments:
            try:
                # 截取掉微秒和时区部分，简化解析
                time_str = comment['created_at'][:19] 
                utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                bj_time = utc_time + timedelta(hours=8)
                comment['formatted_time'] = bj_time.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                comment['formatted_time'] = comment['created_at'][:10] # 降级处理，只显示日期
                
    except Exception as e:
        print(f"数据库读取失败: {e}")
        comments = []
        
    return render_template('tab_forum.html', current_tab='forum', comments=comments)

@forum_bp.route('/api/comment', methods=['POST'])
def add_comment():
    username = request.form.get('username', '匿名植物')
    content = request.form.get('content', '').strip()
    
    if content:
        # 简单防御：防止昵称和内容过长
        username = username[:20] if username else '匿名植物'
        content = content[:500]
        
        try:
            supabase.table("comments").insert({
                "username": username, 
                "content": content
            }).execute()
        except Exception as e:
            print(f"留言写入失败: {e}")
            
    return redirect('/forum')
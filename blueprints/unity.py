# blueprints/unity.py
from flask import Blueprint, render_template, request, send_file, jsonify, redirect
import UnityPy
from io import BytesIO
import json
import json5  # 【新增】引入增强型 JSON 解析器
import zipfile
from functools import wraps
from threading import Lock
from extensions import limiter
from database import supabase  # 确保导入了数据库实例用于鉴权

unity_bp = Blueprint('unity', __name__)

# 【核心新增】全局线程锁，确保引擎同一时间只能处理一个重负载任务
engine_lock = Lock()

# ==================== 装饰器：强制登录校验 ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            if request.method == 'POST':
                return render_template('error.html', msg="权限不足：只有登录用户才能使用资源管理功能，请先登录！"), 401
            return redirect('/login')
        try:
            user_res = supabase.auth.get_user(token)
            if not user_res or not user_res.user:
                raise Exception("Token invalid")
        except Exception:
            if request.method == 'POST':
                return render_template('error.html', msg="登录凭证已失效，请重新登录！"), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ==================== 核心逻辑：智能 JSON 树处理 ====================
def clean_json_string(s):
    """清理 Unity 遗留的隐形控制字符，如 Null 字节或 BOM 头"""
    if not isinstance(s, str):
        return s
    return s.replace('\x00', '').replace('\ufeff', '').strip()

def transform_json_tree(tree, mode='expand'):
    """
    递归处理 Unity TypeTree 中的嵌套 JSON 字符串
    """
    target_keys = {"m_Script", "m_Data", "m_RawData"} # 改用集合提升查找效率
    
    if isinstance(tree, dict):
        for k, v in tree.items():
            if k in target_keys:
                if mode == 'expand' and isinstance(v, str):
                    # 1. 强力清洗隐形字符
                    cleaned_v = clean_json_string(v)
                    # 2. 启发式判断是否为字典或列表的字符串形式
                    if (cleaned_v.startswith('{') and cleaned_v.endswith('}')) or \
                       (cleaned_v.startswith('[') and cleaned_v.endswith(']')):
                        try:
                            # 3. 【核心优化】使用 json5 解析，完美兼容非标准格式、单引号、尾随逗号等
                            tree[k] = json5.loads(cleaned_v)
                            # 4. 递归处理套娃
                            transform_json_tree(tree[k], mode)
                        except Exception as e:
                            # 解析失败则保持原状，说明只是长得像 JSON 的普通字符串
                            pass 
                elif mode == 'collapse' and isinstance(v, (dict, list)):
                    # 先递归收缩内层
                    transform_json_tree(v, mode)
                    # 打包时，恢复为极其严谨且无多余空格的标准 JSON 字符串供 Unity 读取
                    tree[k] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
            else:
                transform_json_tree(v, mode)
    elif isinstance(tree, list):
        for item in tree:
            transform_json_tree(item, mode)
    return tree

# ==================== 接口路由 ====================

# 【新增】供前端查询引擎状态的接口
@unity_bp.route('/api/unity/status')
def engine_status():
    # .locked() 会返回 True 如果锁正在被别人占用
    return jsonify({"is_idle": not engine_lock.locked()})

# 1. 访问 Unity 工具主界面
@unity_bp.route('/unity')
@login_required  # 【安全增强】强制登录才能访问页面
def index():
    return render_template('tab_unity.html', current_tab='unity')

# 2. 独立出来的解包接口
@unity_bp.route('/unpack', methods=['POST'])
@limiter.limit("3 per minute")
@login_required  # 【安全增强】强制登录才能解包
def unpack():
    # 非阻塞尝试获取锁：如果拿不到，说明有其他人在处理，直接返回错误
    if not engine_lock.acquire(blocking=False):
        return render_template('error.html', msg="服务器引擎当前正在处理其他用户的资源，为防止内存溢出已开启保护，请等待 1 分钟后再试！"), 429

    try:
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！解包功能最大支持 10MB 的文件。"), 413
            
        file = request.files.get('bundle')
        if not file: 
            return render_template('error.html', msg="请选择文件后再点击上传。"), 400
        
        # 【内存优化】直接读取文件流，避免 file.read() 复制全量字节到内存
        env = UnityPy.load(file.stream)
        memory_file = BytesIO()
        index_data = {}
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for obj in env.objects:
                try:
                    name = f"Object_{obj.path_id}"
                    
                    # 逻辑回归：优先尝试原版的 TypeTree 提取
                    try:
                        tree = obj.read_typetree()
                        if tree:
                            tree = transform_json_tree(tree, mode='expand')
                            name = tree.get("m_Name", name)
                            file_name = f"{obj.type.name}/{name}_{obj.path_id}.json"
                            # 导出给用户看的 JSON，用标准库 json.dumps，加上缩进，方便阅读
                            zf.writestr(file_name, json.dumps(tree, indent=4, ensure_ascii=False).encode('utf-8'))
                            index_data[str(obj.path_id)] = file_name
                            continue 
                    except Exception:
                        pass # 正常抛出（某些对象没有 TypeTree）

                    # 逻辑回归：原版的图片提取
                    if obj.type.name in ["Texture2D", "Sprite"]:
                        data = obj.read()
                        img_io = BytesIO()
                        data.image.save(img_io, 'PNG')
                        file_name = f"Images/{data.name}_{obj.path_id}.png"
                        zf.writestr(file_name, img_io.getvalue())
                        index_data[str(obj.path_id)] = file_name
                    # 逻辑回归：原版的保底提取
                    else:
                        raw = obj.get_raw_data()
                        file_name = f"Raw/{obj.type.name}_{obj.path_id}.dat"
                        zf.writestr(file_name, raw)
                        index_data[str(obj.path_id)] = file_name
                except Exception as obj_e:
                    # 打印具体哪个对象失败，而不是静默吞噬
                    print(f"[解包警告] 对象 {obj.path_id} 提取跳过: {obj_e}")

            zf.writestr("_index.json", json.dumps(index_data, indent=4, ensure_ascii=False))

        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Unpacked_{file.filename}.zip")
    
    except Exception as e:
        return render_template('error.html', msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500
    finally:
        # 【至关重要】无论成功、报错还是触发文件大小拦截，都必须释放锁！
        engine_lock.release()

# 3. 独立出来的打包回填接口
@unity_bp.route('/repack', methods=['POST'])
@limiter.limit("3 per minute")
@login_required  # 【安全增强】强制登录才能打包
def repack():
    if not engine_lock.acquire(blocking=False):
        return render_template('error.html', msg="服务器引擎当前正在处理其他用户的资源，为防止内存溢出已开启保护，请等待 1 分钟后再试！"), 429

    try:
        if request.content_length and request.content_length > 20 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！回填功能最大支持总计 20MB 的文件。"), 413
            
        orig_file = request.files.get('original_bundle')
        mod_zip = request.files.get('modified_zip')
        
        if not orig_file or not mod_zip: 
            return render_template('error.html', msg="缺少文件！必须同时上传【原始Bundle】和【修改好的ZIP】。"), 400
        
        # 【内存优化】直接使用流加载原包
        env = UnityPy.load(orig_file.stream)
        zip_data = BytesIO(mod_zip.read())
        
        with zipfile.ZipFile(zip_data, 'r') as zf:
            namelist = zf.namelist()
            index_path_in_zip = None
            for name in namelist:
                normalized_name = name.replace('\\', '/')
                if normalized_name.endswith('_index.json') and normalized_name.split('/')[-1] == '_index.json':
                    index_path_in_zip = name
                    break
            
            if not index_path_in_zip:
                raise Exception("ZIP 包中完全没有找到 _index.json 文件！请确认压缩包内容。")
            
            normalized_index_path = index_path_in_zip.replace('\\', '/')
            prefix = normalized_index_path[:-11] 
            
            index_data = json.loads(zf.read(index_path_in_zip).decode('utf-8'))
            
            for obj in env.objects:
                path_id_str = str(obj.path_id)
                if path_id_str in index_data:
                    file_path = index_data[path_id_str]
                    
                    if file_path.endswith('.json'):
                        try:
                            actual_file_path = prefix + file_path.replace('\\', '/')
                            raw_json_str = zf.read(actual_file_path).decode('utf-8')
                            cleaned_str = clean_json_string(raw_json_str)
                            
                            # 【核心优化】使用 json5 读取用户修改的文件！
                            # 这意味着用户可以在 JSON 里面自由写注释 //，保留尾随逗号，都不会报错！
                            new_tree = json5.loads(cleaned_str)
                            collapsed_tree = transform_json_tree(new_tree, mode='collapse')
                            obj.save_typetree(collapsed_tree)
                        except Exception as e:
                            print(f"[打包警告] 回填 {file_path} 失败，可能是用户修改的 JSON 存在严重语法错误: {e}")

        out_bundle = BytesIO()
        out_bundle.write(env.file.save(packer="lz4"))
        out_bundle.seek(0)
        
        return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")
    except Exception as e:
         return render_template('error.html', msg=f"打包失败！请检查文件格式。错误详情: {e}"), 500
    finally:
        engine_lock.release()
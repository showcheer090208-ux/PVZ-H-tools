# blueprints/unity.py
from flask import Blueprint, render_template, request, send_file, jsonify, redirect
import UnityPy
from io import BytesIO
import json
import json5  # 保留 json5 作为备用急救包
import zipfile
from functools import wraps
from extensions import limiter
from database import supabase

unity_bp = Blueprint('unity', __name__)

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

# ==================== 核心逻辑：智能 JSON 树处理 (性能优化版) ====================
def clean_json_string(s):
    """清理 Unity 遗留的隐形控制字符"""
    if not isinstance(s, str):
        return s
    return s.replace('\x00', '').replace('\ufeff', '').strip()

def transform_json_tree(tree, mode='expand'):
    """
    递归处理 Unity TypeTree 中的嵌套 JSON 字符串
    """
    target_keys = {"m_Script", "m_Data", "m_RawData"}
    
    if isinstance(tree, dict):
        for k, v in tree.items():
            if k in target_keys:
                if mode == 'expand' and isinstance(v, str):
                    cleaned_v = clean_json_string(v)
                    if (cleaned_v.startswith('{') and cleaned_v.endswith('}')) or \
                       (cleaned_v.startswith('[') and cleaned_v.endswith(']')):
                        
                        # 【核心优化：混合解析策略】
                        # 1. 先尝试极速原生 C 解析 (光速，覆盖 99% 场景)
                        try:
                            tree[k] = json.loads(cleaned_v)
                            transform_json_tree(tree[k], mode)
                        except json.JSONDecodeError:
                            # 2. 如果原生解析失败，说明有注释/脏格式，启用 json5 紧急救援 (稍慢但极其健壮)
                            try:
                                tree[k] = json5.loads(cleaned_v)
                                transform_json_tree(tree[k], mode)
                            except Exception:
                                pass # 如果连 json5 都救不活，那这就是个普通字符串
                
                elif mode == 'collapse' and isinstance(v, (dict, list)):
                    transform_json_tree(v, mode)
                    # 打包时统一使用原生极速序列化，保证输出绝对标准的 JSON
                    tree[k] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
            else:
                transform_json_tree(v, mode)
    elif isinstance(tree, list):
        for item in tree:
            transform_json_tree(item, mode)
    return tree

# ==================== 接口路由 ====================

@unity_bp.route('/unity')
@login_required
def index():
    return render_template('tab_unity.html', current_tab='unity')

@unity_bp.route('/unpack', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
def unpack():
    # 移除锁，恢复并发处理
    try:
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！解包功能最大支持 10MB 的文件。"), 413
            
        file = request.files.get('bundle')
        if not file: 
            return render_template('error.html', msg="请选择文件后再点击上传。"), 400
        
        env = UnityPy.load(file.stream)
        memory_file = BytesIO()
        index_data = {}
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for obj in env.objects:
                try:
                    name = f"Object_{obj.path_id}"
                    
                    try:
                        tree = obj.read_typetree()
                        if tree:
                            tree = transform_json_tree(tree, mode='expand')
                            name = tree.get("m_Name", name)
                            file_name = f"{obj.type.name}/{name}_{obj.path_id}.json"
                            zf.writestr(file_name, json.dumps(tree, indent=4, ensure_ascii=False).encode('utf-8'))
                            index_data[str(obj.path_id)] = file_name
                            continue 
                    except Exception:
                        pass

                    if obj.type.name in ["Texture2D", "Sprite"]:
                        data = obj.read()
                        img_io = BytesIO()
                        data.image.save(img_io, 'PNG')
                        file_name = f"Images/{data.name}_{obj.path_id}.png"
                        zf.writestr(file_name, img_io.getvalue())
                        index_data[str(obj.path_id)] = file_name
                    else:
                        raw = obj.get_raw_data()
                        file_name = f"Raw/{obj.type.name}_{obj.path_id}.dat"
                        zf.writestr(file_name, raw)
                        index_data[str(obj.path_id)] = file_name
                except Exception as obj_e:
                    print(f"[解包警告] 对象 {obj.path_id} 提取跳过: {obj_e}")

            zf.writestr("_index.json", json.dumps(index_data, indent=4, ensure_ascii=False))

        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Unpacked_{file.filename}.zip")
    except Exception as e:
        return render_template('error.html', msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500


@unity_bp.route('/repack', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
def repack():
    # 移除锁，恢复并发处理
    try:
        if request.content_length and request.content_length > 20 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！回填功能最大支持总计 20MB 的文件。"), 413
            
        orig_file = request.files.get('original_bundle')
        mod_zip = request.files.get('modified_zip')
        
        if not orig_file or not mod_zip: 
            return render_template('error.html', msg="缺少文件！必须同时上传【原始Bundle】和【修改好的ZIP】。"), 400
        
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
                            
                            # 打包读取用户数据时，同样使用极速/兼容混合模式
                            try:
                                new_tree = json.loads(cleaned_str)
                            except json.JSONDecodeError:
                                new_tree = json5.loads(cleaned_str)

                            collapsed_tree = transform_json_tree(new_tree, mode='collapse')
                            obj.save_typetree(collapsed_tree)
                        except Exception as e:
                            print(f"[打包警告] 回填 {file_path} 失败: {e}")

        out_bundle = BytesIO()
        out_bundle.write(env.file.save(packer="lz4"))
        out_bundle.seek(0)
        
        return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")
    except Exception as e:
         return render_template('error.html', msg=f"打包失败！请检查文件格式。错误详情: {e}"), 500
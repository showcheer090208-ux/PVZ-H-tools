# blueprints/unity.py
from flask import Blueprint, render_template, request, send_file, redirect
import UnityPy
import json
import json5  # 保留 json5 作为备用急救包
import zipfile
import tempfile
import re
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

# ==================== 核心逻辑：智能数据清洗与处理 ====================
def clean_json_string(s):
    """
    【防御级数据清洗】专门针对 MT管理器 和 手机输入法 带来的脏数据
    """
    if not isinstance(s, str):
        return s
    
    # 1. 过滤不可见的控制字符 (保留 \n, \r, \t)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    # 2. 剥离可能残留的 BOM 头
    cleaned = cleaned.replace('\ufeff', '').strip()
    # 3. 手机端防御：将误触的全角标点替换为半角标点
    cleaned = cleaned.replace('，', ',').replace('“', '"').replace('”', '"')
    
    return cleaned

def transform_json_tree(tree, mode='expand'):
    """递归处理 Unity TypeTree 中的嵌套 JSON 字符串"""
    target_keys = {"m_Script", "m_Data", "m_RawData"}
    
    if isinstance(tree, dict):
        for k, v in tree.items():
            if k in target_keys:
                if mode == 'expand' and isinstance(v, str):
                    cleaned_v = clean_json_string(v)
                    # 预判是否为 JSON
                    if (cleaned_v.startswith('{') and cleaned_v.endswith('}')) or \
                       (cleaned_v.startswith('[') and cleaned_v.endswith(']')):
                        
                        try:
                            tree[k] = json.loads(cleaned_v)
                            transform_json_tree(tree[k], mode)
                        except json.JSONDecodeError:
                            try:
                                tree[k] = json5.loads(cleaned_v)
                                transform_json_tree(tree[k], mode)
                            except Exception as e:
                                print(f"[JSON解析跳过] 键 {k} 解析失败: {e}")
                                tree[k] = cleaned_v # 救不活就保留原样，避免阻断程序
                
                elif mode == 'collapse' and isinstance(v, (dict, list)):
                    transform_json_tree(v, mode)
                    # 打包时统一使用原生极速序列化，保证输出标准的 JSON
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
    try:
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！解包功能最大支持 10MB 的文件。"), 413
            
        file = request.files.get('bundle')
        if not file: 
            return render_template('error.html', msg="请选择文件后再点击上传。"), 400
        
        # 直接使用 stream，避免读入内存
        env = UnityPy.load(file.stream)
        
        # 【内存保护】：使用 SpooledTemporaryFile，超过 2MB 自动借用硬盘，防 512M 服务器 OOM
        memory_file = tempfile.SpooledTemporaryFile(max_size=2*1024*1024, mode='w+b')
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
                        # 贴图依然需要短暂放内存，但处理完即刻销毁
                        import io
                        img_io = io.BytesIO()
                        data.image.save(img_io, 'PNG')
                        file_name = f"Images/{data.name}_{obj.path_id}.png"
                        zf.writestr(file_name, img_io.getvalue())
                        index_data[str(obj.path_id)] = file_name
                        img_io.close()
                    else:
                        raw = obj.get_raw_data()
                        file_name = f"Raw/{obj.type.name}_{obj.path_id}.dat"
                        zf.writestr(file_name, raw)
                        index_data[str(obj.path_id)] = file_name
                except Exception as obj_e:
                    print(f"[解包警告] 对象 {obj.path_id} 提取跳过: {obj_e}")

            zf.writestr("_index.json", json.dumps(index_data, indent=4, ensure_ascii=False))

        memory_file.seek(0)
        # send_file 发送完毕后会自动 close()，SpooledTemporaryFile 被 close 时会自动从硬盘/内存删除
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Unpacked_{file.filename}.zip")
    except Exception as e:
        return render_template('error.html', msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500


@unity_bp.route('/repack', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
def repack():
    try:
        if request.content_length and request.content_length > 20 * 1024 * 1024:
            return render_template('error.html', msg="文件太大啦！回填功能最大支持总计 20MB 的文件。"), 413
            
        orig_file = request.files.get('original_bundle')
        mod_zip = request.files.get('modified_zip')
        
        if not orig_file or not mod_zip: 
            return render_template('error.html', msg="缺少文件！必须同时上传【原始Bundle】和【修改好的ZIP】。"), 400
        
        # 也是直接读取流
        env = UnityPy.load(orig_file.stream)
        
        # 【内存保护】：把上传的 zip 存入零时文件读取
        zip_temp = tempfile.SpooledTemporaryFile(max_size=2*1024*1024, mode='w+b')
        mod_zip.save(zip_temp)
        zip_temp.seek(0)
        
        with zipfile.ZipFile(zip_temp, 'r') as zf:
            zip_file_map = {}
            index_data = None
            
            # 【扁平化映射】：无视 ZIP 里的文件夹嵌套结构
            for name in zf.namelist():
                # 防御 MT 管理器的缓存与 Mac 脏文件
                if '__MACOSX' in name or name.startswith('.') or name.endswith('.bak'):
                    continue
                    
                normalized_name = name.replace('\\', '/')
                file_name_only = normalized_name.split('/')[-1]
                
                if not file_name_only: 
                    continue
                    
                zip_file_map[file_name_only] = normalized_name
                
                if file_name_only == '_index.json':
                    try:
                        # utf-8-sig 强行消除 BOM 头
                        index_data = json.loads(zf.read(name).decode('utf-8-sig'))
                    except Exception as e:
                        raise Exception(f"解析 _index.json 失败: {e}")

            if not index_data:
                raise Exception("ZIP 包中没有找到 _index.json 文件！请确认补丁包完整。")
            
            # 开始回填
            for obj in env.objects:
                path_id_str = str(obj.path_id)
                if path_id_str in index_data:
                    expected_relative_path = index_data[path_id_str]
                    expected_filename = expected_relative_path.replace('\\', '/').split('/')[-1]
                    
                    actual_zip_path = zip_file_map.get(expected_filename)
                    
                    if actual_zip_path and expected_filename.endswith('.json'):
                        try:
                            # 【MT 防御】：utf-8-sig 读取
                            raw_json_str = zf.read(actual_zip_path).decode('utf-8-sig')
                            cleaned_str = clean_json_string(raw_json_str)
                            
                            try:
                                new_tree = json.loads(cleaned_str)
                            except json.JSONDecodeError:
                                new_tree = json5.loads(cleaned_str)

                            collapsed_tree = transform_json_tree(new_tree, mode='collapse')
                            obj.save_typetree(collapsed_tree)
                        except Exception as e:
                            print(f"[打包警告] 回填 {expected_filename} 失败: {e}")

        # 【内存保护】：打包结果写入零时文件
        out_bundle = tempfile.SpooledTemporaryFile(max_size=2*1024*1024, mode='w+b')
        out_bundle.write(env.file.save(packer="lz4"))
        out_bundle.seek(0)
        zip_temp.close() # 释放 ZIP 的临时内存/磁盘
        
        return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")
    except Exception as e:
         return render_template('error.html', msg=f"打包失败！请检查文件格式。错误详情: {e}"), 500
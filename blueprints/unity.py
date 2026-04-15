# blueprints/unity.py
from flask import Blueprint, render_template, request, send_file
import UnityPy
from io import BytesIO
import json
import zipfile
from extensions import limiter

unity_bp = Blueprint('unity', __name__)

def transform_json_tree(tree, mode='expand'):
    """
    递归处理 Unity TypeTree 中的嵌套 JSON 字符串
    """
    target_keys = ["m_Script", "m_Data", "m_RawData"]
    
    if isinstance(tree, dict):
        for k, v in tree.items():
            if k in target_keys:
                if mode == 'expand' and isinstance(v, str):
                    try:
                        stripped = v.strip()
                        # 启发式判断是否为 JSON 字符串
                        if (stripped.startswith('{') and stripped.endswith('}')) or \
                           (stripped.startswith('[') and stripped.endswith(']')):
                            tree[k] = json.loads(v)
                            # 递归处理套娃
                            transform_json_tree(tree[k], mode)
                    except:
                        pass # 解析失败则保持原状
                elif mode == 'collapse' and isinstance(v, (dict, list)):
                    # 先递归收缩内层
                    transform_json_tree(v, mode)
                    # 压缩为无空格的单行字符串
                    tree[k] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
            else:
                transform_json_tree(v, mode)
    elif isinstance(tree, list):
        for i in range(len(tree)):
            transform_json_tree(tree[i], mode)
    return tree

# 1. 访问 Unity 工具主界面
@unity_bp.route('/unity')
def index():
    return render_template('tab_unity.html', current_tab='unity')

# 2. 独立出来的解包接口
@unity_bp.route('/unpack', methods=['POST'])
@limiter.limit("3 per minute")  # 【核心防御】每个 IP 一分钟最多解包 3 次
def unpack():
    if request.content_length and request.content_length > 10 * 1024 * 1024:
        return render_template('error.html', msg="文件太大啦！解包功能最大支持 10MB 的文件。"), 413
        
    file = request.files.get('bundle')
    if not file: 
        return render_template('error.html', msg="请选择文件后再点击上传。"), 400
    
    try:
        env = UnityPy.load(file.read())
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
                            # 【核心新增】仅在此处进行安全的字符串展开
                            tree = transform_json_tree(tree, mode='expand')
                            
                            name = tree.get("m_Name", name)
                            file_name = f"{obj.type.name}/{name}_{obj.path_id}.json"
                            zf.writestr(file_name, json.dumps(tree, indent=4, ensure_ascii=False).encode('utf-8'))
                            index_data[str(obj.path_id)] = file_name
                            continue # 成功提取为 JSON，跳过后续处理
                    except:
                        pass

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
                except Exception as e:
                    pass

            zf.writestr("_index.json", json.dumps(index_data, indent=4))

        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Unpacked_{file.filename}.zip")
    except Exception as e:
        return render_template('error.html', msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500

# 3. 独立出来的打包回填接口
@unity_bp.route('/repack', methods=['POST'])
@limiter.limit("3 per minute")  # 【核心防御】每个 IP 一分钟最多打包 3 次
def repack():
    if request.content_length and request.content_length > 20 * 1024 * 1024:
        return render_template('error.html', msg="文件太大啦！回填功能最大支持总计 20MB 的文件。"), 413
        
    orig_file = request.files.get('original_bundle')
    mod_zip = request.files.get('modified_zip')
    
    if not orig_file or not mod_zip: 
        return render_template('error.html', msg="缺少文件！必须同时上传【原始Bundle】和【修改好的ZIP】。"), 400
    
    try:
        env = UnityPy.load(orig_file.read())
        zip_data = BytesIO(mod_zip.read())
        with zipfile.ZipFile(zip_data, 'r') as zf:
            # 1. 智能寻找 _index.json (解决 MT 管理器等手机压缩软件的“目录套娃”问题)
            namelist = zf.namelist()
            index_path_in_zip = None
            for name in namelist:
                # 兼容不同操作系统的路径分隔符
                normalized_name = name.replace('\\', '/')
                if normalized_name.endswith('_index.json') and normalized_name.split('/')[-1] == '_index.json':
                    index_path_in_zip = name
                    break
            
            if not index_path_in_zip:
                raise Exception("ZIP 包中完全没有找到 _index.json 文件！请确认压缩包内容。")
            
            # 2. 计算前缀：如果文件在 "文件夹A/_index.json"，前缀就是 "文件夹A/"
            normalized_index_path = index_path_in_zip.replace('\\', '/')
            prefix = normalized_index_path[:-11] # 11 是 "_index.json" 的长度
            
            # 3. 读取索引数据
            index_data = json.loads(zf.read(index_path_in_zip).decode('utf-8'))
            
            # 4. 执行回填逻辑
            for obj in env.objects:
                path_id_str = str(obj.path_id)
                if path_id_str in index_data:
                    file_path = index_data[path_id_str]
                    
                    if file_path.endswith('.json'):
                        try:
                            # 拼接真实路径：前缀 + 索引记录的路径
                            actual_file_path = prefix + file_path.replace('\\', '/')
                            
                            new_tree = json.loads(zf.read(actual_file_path).decode('utf-8'))
                            collapsed_tree = transform_json_tree(new_tree, mode='collapse')
                            obj.save_typetree(collapsed_tree)
                        except Exception as e:
                            print(f"回填 {file_path} 失败，可能文件损坏或路径错误: {e}")
                            pass

        out_bundle = BytesIO()
        out_bundle.write(env.file.save(packer="lz4"))
        out_bundle.seek(0)
        
        return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")
    except Exception as e:
         return render_template('error.html', msg=f"打包失败！请检查文件格式。错误详情: {e}"), 500
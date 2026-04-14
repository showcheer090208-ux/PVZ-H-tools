# blueprints/unity.py
from flask import Blueprint, render_template, request, send_file
import UnityPy
from io import BytesIO
import json
import zipfile

unity_bp = Blueprint('unity', __name__)

# 1. 访问 Unity 工具主界面
@unity_bp.route('/unity')
def index():
    return render_template('tab_unity.html', current_tab='unity')

# 2. 独立出来的解包接口
@unity_bp.route('/unpack', methods=['POST'])
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
                    try:
                        tree = obj.read_typetree()
                        if tree:
                            name = tree.get("m_Name", name)
                            file_name = f"{obj.type.name}/{name}_{obj.path_id}.json"
                            zf.writestr(file_name, json.dumps(tree, indent=4, ensure_ascii=False).encode('utf-8'))
                            index_data[str(obj.path_id)] = file_name
                            continue
                    except:
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
                except Exception as e:
                    pass

            zf.writestr("_index.json", json.dumps(index_data, indent=4))

        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Unpacked_{file.filename}.zip")
    except Exception as e:
        return render_template('error.html', msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500

# 3. 独立出来的打包回填接口
@unity_bp.route('/repack', methods=['POST'])
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
            index_data = json.loads(zf.read("_index.json").decode('utf-8'))
            
            for obj in env.objects:
                path_id_str = str(obj.path_id)
                if path_id_str in index_data:
                    file_path = index_data[path_id_str]
                    if file_path.endswith('.json'):
                        try:
                            new_tree = json.loads(zf.read(file_path).decode('utf-8'))
                            obj.save_typetree(new_tree)
                        except Exception as e:
                            pass

        out_bundle = BytesIO()
        out_bundle.write(env.file.save(packer="lz4"))
        out_bundle.seek(0)
        
        return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")
    except Exception as e:
         return render_template('error.html', msg=f"打包失败！请检查 ZIP 包内的 _index.json 是否被破坏。错误详情: {e}"), 500
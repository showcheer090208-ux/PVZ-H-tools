import os
import json
import zipfile
import shutil
from io import BytesIO
from flask import Flask, request, render_template_string, send_file
import UnityPy

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Unity 通用工具箱</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #f4f7f6; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h2 { color: #1a73e8; border-bottom: 2px solid #e8f0fe; padding-bottom: 10px; }
        .btn { background: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; }
        .desc { font-size: 13px; color: #666; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>📤 第一步：全资源解包</h2>
            <p class="desc">上传 Bundle 文件，导出所有资源的 JSON 和图片。</p>
            <form action="/unpack" method="post" enctype="multipart/form-data">
                <input type="file" name="bundle">
                <button type="submit" class="btn">解包并下载 ZIP</button>
            </form>
        </div>

        <div class="card">
            <h2>📥 第二步：回填打包 (Repack)</h2>
            <p class="desc">上传【原始 Bundle】和【修改后的 ZIP】，生成新 Bundle。</p>
            <form action="/repack" method="post" enctype="multipart/form-data">
                <label>原始文件：</label><input type="file" name="original_bundle"><br><br>
                <label>修改后的 ZIP：</label><input type="file" name="modified_zip"><br>
                <button type="submit" class="btn" style="background: #28a745;">执行回填并下载新 Bundle</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/unpack', methods=['POST'])
def unpack():
    file = request.files.get('bundle')
    if not file: return "未选择文件"
    
    env = UnityPy.load(file.read())
    memory_file = BytesIO()
    index_data = {}
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for obj in env.objects:
            try:
                # 获取对象名称或默认名
                name = f"Object_{obj.path_id}"
                
                # 尝试通过 TypeTree 读取结构化数据（解决 MonoBehaviour 全是 .dat 的问题）
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

                # 处理图片实体
                if obj.type.name in ["Texture2D", "Sprite"]:
                    data = obj.read()
                    img_io = BytesIO()
                    data.image.save(img_io, 'PNG')
                    file_name = f"Images/{data.name}_{obj.path_id}.png"
                    zf.writestr(file_name, img_io.getvalue())
                    index_data[str(obj.path_id)] = file_name
                
                # 其他无法解析的存为 dat
                else:
                    raw = obj.get_raw_data()
                    file_name = f"Raw/{obj.type.name}_{obj.path_id}.dat"
                    zf.writestr(file_name, raw)
                    index_data[str(obj.path_id)] = file_name

            except Exception as e:
                print(f"解析 {obj.path_id} 失败: {e}")

        # 写入索引文件，这是回填的关键
        zf.writestr("_index.json", json.dumps(index_data, indent=4))

    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="unpack_result.zip")

@app.route('/repack', methods=['POST'])
def repack():
    orig_file = request.files.get('original_bundle')
    mod_zip = request.files.get('modified_zip')
    
    if not orig_file or not mod_zip: return "缺少必要文件"
    
    # 加载原始环境
    env = UnityPy.load(orig_file.read())
    
    # 加载 ZIP 中的修改
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
                        # 使用 Typetree 回填数据，这是 logic_unity.py 的核心精髓
                        obj.save_typetree(new_tree)
                    except Exception as e:
                        print(f"回填 {path_id_str} 失败: {e}")
                # 此处可扩展图片回填逻辑 (if file_path.endswith('.png')...)

    # 保存并导出新 Bundle
    out_bundle = BytesIO()
    out_bundle.write(env.file.save(packer="lz4"))
    out_bundle.seek(0)
    
    return send_file(out_bundle, mimetype='application/octet-stream', as_attachment=True, download_name=f"modded_{orig_file.filename}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
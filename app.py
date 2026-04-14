import os
import json
import zipfile
from io import BytesIO
from flask import Flask, request, render_template_string, send_file
import UnityPy

app = Flask(__name__)

# ==========================================
# 1. 漂亮的前端页面 (使用 Tailwind CSS)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PVZH 资源魔改工坊</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        // 简单的交互：点击后按钮变成“处理中...”，防止用户重复点击
        function showLoading(buttonId) {
            const btn = document.getElementById(buttonId);
            btn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> 服务器狂奔中，请稍候...';
            btn.classList.add('cursor-not-allowed', 'opacity-75');
        }
    </script>
</head>
<body class="bg-gray-50 text-gray-800 font-sans antialiased min-h-screen flex flex-col items-center py-10 px-4">
    <div class="max-w-2xl w-full">
        
        <div class="text-center mb-10">
            <h1 class="text-3xl font-extrabold text-blue-600 tracking-tight">PVZH 资源魔改工坊</h1>
            <p class="text-gray-500 mt-2">基于 UnityPy 的全资源解包与回填云端工具</p>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8 mb-8 transition hover:shadow-md">
            <div class="flex items-center mb-4">
                <div class="bg-blue-100 p-2 rounded-lg mr-3">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                </div>
                <h2 class="text-xl font-bold text-gray-800">第一步：全资源解包</h2>
            </div>
            <p class="text-sm text-gray-500 mb-6">上传 Bundle 文件，导出 JSON 配置和图片。限制大小：<span class="font-semibold text-red-500">10MB</span> 以内。</p>
            <form action="/unpack" method="post" enctype="multipart/form-data" onsubmit="showLoading('btn-unpack')">
                <div class="mb-4">
                    <input type="file" name="bundle" required class="block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition">
                </div>
                <button id="btn-unpack" type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition duration-200 shadow-sm">
                    解包并下载 ZIP
                </button>
            </form>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8 transition hover:shadow-md">
            <div class="flex items-center mb-4">
                <div class="bg-green-100 p-2 rounded-lg mr-3">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                </div>
                <h2 class="text-xl font-bold text-gray-800">第二步：回填打包 (Repack)</h2>
            </div>
            <p class="text-sm text-gray-500 mb-6">上传【原始 Bundle】和【修改后的 ZIP】，生成新 Bundle。总大小限制：<span class="font-semibold text-red-500">20MB</span> 以内。</p>
            <form action="/repack" method="post" enctype="multipart/form-data" onsubmit="showLoading('btn-repack')">
                <div class="mb-4 border border-dashed border-gray-300 p-4 rounded-xl hover:border-gray-400 transition">
                    <label class="block text-sm font-medium text-gray-700 mb-2">1. 原始 Bundle 文件</label>
                    <input type="file" name="original_bundle" required class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 transition">
                </div>
                <div class="mb-6 border border-dashed border-gray-300 p-4 rounded-xl hover:border-gray-400 transition">
                    <label class="block text-sm font-medium text-gray-700 mb-2">2. 修改后的 ZIP 文件</label>
                    <input type="file" name="modified_zip" required class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 transition">
                </div>
                <button id="btn-repack" type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-xl transition duration-200 shadow-sm">
                    执行回填并下载新 Bundle
                </button>
            </form>
        </div>
        
        <div class="text-center mt-8 text-xs text-gray-400">
            Deployed on Render | Powered by UnityPy & Flask
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 2. 友好的报错页面
# ==========================================
ERROR_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>操作失败</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-50 h-screen flex flex-col justify-center items-center px-4">
    <div class="bg-white p-8 rounded-2xl shadow-sm text-center max-w-md w-full border border-red-100">
        <svg class="mx-auto h-16 w-16 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <h2 class="text-xl font-bold text-gray-800 mb-2">出错了</h2>
        <p class="text-gray-600 mb-6">{{ msg }}</p>
        <button onclick="window.history.back()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition">返回重试</button>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/unpack', methods=['POST'])
def unpack():
    # 限制 10MB (10 * 1024 * 1024 bytes)
    if request.content_length and request.content_length > 10 * 1024 * 1024:
        return render_template_string(ERROR_PAGE, msg="文件太大啦！解包功能最大支持 10MB 的文件。"), 413
        
    file = request.files.get('bundle')
    if not file: return render_template_string(ERROR_PAGE, msg="请选择文件后再点击上传。"), 400
    
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
        return render_template_string(ERROR_PAGE, msg=f"解包失败，可能是文件损坏或加密。错误详情: {e}"), 500

@app.route('/repack', methods=['POST'])
def repack():
    # 限制 20MB
    if request.content_length and request.content_length > 20 * 1024 * 1024:
        return render_template_string(ERROR_PAGE, msg="文件太大啦！回填功能最大支持总计 20MB 的文件。"), 413
        
    orig_file = request.files.get('original_bundle')
    mod_zip = request.files.get('modified_zip')
    
    if not orig_file or not mod_zip: 
        return render_template_string(ERROR_PAGE, msg="缺少文件！必须同时上传【原始Bundle】和【修改好的ZIP】。"), 400
    
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
         return render_template_string(ERROR_PAGE, msg=f"打包失败！请检查 ZIP 包内的 _index.json 是否被破坏。错误详情: {e}"), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)

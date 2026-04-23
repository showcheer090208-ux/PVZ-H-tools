# blueprints/phantom_editor.py
from flask import Blueprint, render_template, request, jsonify, send_file
import json
import io
from extensions import limiter
# 引入我们刚才修改好的封包工具
from bundle_packer import process_bundle_in_memory

phantom_editor_bp = Blueprint('phantom_editor', __name__)

@phantom_editor_bp.route('/phantom')
def phantom_editor():
    """幻影引擎主界面"""
    return render_template('tab_phantom_editor.html')

@phantom_editor_bp.route('/api/phantom/pack', methods=['POST'])
@limiter.limit("5 per minute") # 安全防线，防止滥用打包把服务器 CPU 跑挂
def pack_phantom_mod():
    """接收前端传来的底包文件和 JSON 数据，返回处理后的新文件流"""
    
    # 1. 检查是否上传了底包文件
    if 'base_bundle' not in request.files:
        return jsonify({"success": False, "msg": "未提供底包文件(base_bundle)"}), 400
        
    file = request.files['base_bundle']
    if file.filename == '':
        return jsonify({"success": False, "msg": "文件名为空"}), 400
        
    # 2. 检查前端发来的修改数据
    cards_data_str = request.form.get('cards_data')
    if not cards_data_str:
        return jsonify({"success": False, "msg": "未提供卡牌修改数据"}), 400
        
    try:
        modded_card_dict = json.loads(cards_data_str)
    except Exception as e:
        return jsonify({"success": False, "msg": f"JSON解析失败: {str(e)}"}), 400

    # 3. 读取底包二进制流
    bundle_bytes = file.read()
    
    # 4. 调用强大的 UnityPy 在内存中开刀手术
    success, msg, out_bytes = process_bundle_in_memory(bundle_bytes, modded_card_dict, target_asset_name="cards")
    
    if not success:
        return jsonify({"success": False, "msg": msg}), 500
        
    # 5. 把做好的新包作为文件流直接返回给用户下载
    return send_file(
        io.BytesIO(out_bytes),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='cards_modded.assets' # 下载后的默认文件名
    )
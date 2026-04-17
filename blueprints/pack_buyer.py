# blueprints/pack_buyer.py
import json
import time
import os
import requests
from flask import Blueprint, render_template, request, jsonify
from extensions import limiter
from database import supabase

pack_buyer_bp = Blueprint('pack_buyer', __name__)

# ===================== 常量配置 =====================
PACK_API_URL = "https://pvz-heroes.awspopcap.com/persistence/v2/inventory/commitSoftPurchase"

CLIENT_ID = "pvzheroes-2015-google-client"
CLIENT_VERSION = "1.64.6"
CONTENT_VERSION = "45a337051e72592e53c9bf8a4b590639"

# 卡包数据文件路径
PACK_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'name_id_cost.txt')


def get_current_user_from_cookie():
    """从 Cookie 中获取当前登录用户"""
    token = request.cookies.get('access_token')
    if not token:
        return None
    
    try:
        user_res = supabase.auth.get_user(token)
        if user_res and user_res.user:
            profile_res = supabase.table('profiles') \
                .select('*') \
                .eq('id', user_res.user.id) \
                .execute()
            if profile_res.data:
                raw_user = profile_res.data[0]
                return {k: (str(v) if k == 'id' else v) for k, v in raw_user.items()}
    except Exception as e:
        pass
    
    return None


def load_packs_from_file():
    """
    从 name_id_cost.txt 解析卡包数据
    格式：4行一组
    [序号]
    name:xxx
    id:xxx
    cost:xxx
    """
    packs = []
    
    if not os.path.exists(PACK_DATA_FILE):
        print(f"卡包数据文件不存在: {PACK_DATA_FILE}")
        return packs
    
    try:
        with open(PACK_DATA_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        for i in range(0, len(lines), 4):
            if i + 3 >= len(lines):
                break
            
            try:
                # [1] 或 [序号]
                serial = lines[i].strip('[]')
                
                # name:xxx
                name_line = lines[i+1]
                if name_line.startswith('name:'):
                    name = name_line[5:].strip()
                else:
                    name = name_line
                
                # id:xxx
                id_line = lines[i+2]
                if id_line.startswith('id:'):
                    sku = id_line[3:].strip()
                else:
                    sku = id_line
                
                # cost:xxx
                cost_line = lines[i+3]
                if cost_line.startswith('cost:'):
                    cost_str = cost_line[5:].strip()
                else:
                    cost_str = cost_line
                
                cost = int(cost_str) if cost_str.isdigit() else 0
                
                packs.append({
                    'serial': serial,
                    'name': name,
                    'sku': sku,
                    'cost': cost
                })
            except Exception as e:
                print(f"解析卡包数据出错: {e}")
                continue
        
        return packs
    except Exception as e:
        print(f"读取卡包文件失败: {e}")
        return packs


@pack_buyer_bp.route('/pack-buyer')
def pack_buyer_page():
    """渲染卡包购买器页面"""
    return render_template('pack_buyer.html', current_tab='pack_buyer')


@pack_buyer_bp.route('/api/packs', methods=['GET'])
def get_packs():
    """获取所有卡包列表"""
    packs = load_packs_from_file()
    return jsonify({
        'success': True,
        'packs': packs,
        'total': len(packs)
    })


@pack_buyer_bp.route('/api/buy-pack', methods=['POST'])
@limiter.limit("5 per minute")  # 用户级限流
def buy_pack():
    """
    购买卡包
    需要登录
    """
    # 登录校验
    current_user = get_current_user_from_cookie()
    if not current_user:
        return jsonify({"success": False, "error": "请先登录后再使用"}), 401
    
    # 获取请求参数
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400
    
    sku = data.get('sku', '').strip()
    cost = data.get('cost', 0)
    token = data.get('token', '').strip()
    persona_id = data.get('persona_id', '').strip()
    
    # 参数校验
    if not token:
        return jsonify({"success": False, "error": "EADP-AUTH-TOKEN 不能为空"}), 400
    
    if not persona_id:
        return jsonify({"success": False, "error": "EADP-PERSONA-ID 不能为空"}), 400
    
    if not sku:
        return jsonify({"success": False, "error": "请选择或填写卡包 SKU"}), 400
    
    try:
        cost = int(cost)
        if cost <= 0:
            return jsonify({"success": False, "error": "卡包花费必须大于 0"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "卡包花费必须是有效的数字"}), 400
    
    # 生成 UTC 时间戳
    utc = str(int(time.time() * 1000))
    
    # 构建请求
    payload = {
        "Sku": sku,
        "EventId": None,
        "Cards": None,
        "ExpectedCost": cost,
        "KeyName": None
    }
    
    headers = {
        "Content-Type": "application/json",
        "EADP-AUTH-TOKEN": token,
        "EADP-PERSONA-ID": persona_id,
        "X-EADP-Client-Id": CLIENT_ID,
        "X-Pvzh-UTC": utc,
        "X-Pvzh-Platform": "Android",
        "X-Pvzh-Content-Version": CONTENT_VERSION,
        "X-Pvzh-Client-Version": CLIENT_VERSION
    }
    
    # 发送请求
    try:
        response = requests.post(
            PACK_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        # 尝试解析响应
        response_text = response.text
        response_json = None
        try:
            response_json = json.loads(response_text)
        except:
            pass
        
        return jsonify({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response_json if response_json else response_text
        })
        
    except requests.Timeout:
        return jsonify({"success": False, "error": "请求超时，请稍后重试"}), 504
    except requests.ConnectionError:
        return jsonify({"success": False, "error": "网络连接失败"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"请求失败: {str(e)}"}), 500
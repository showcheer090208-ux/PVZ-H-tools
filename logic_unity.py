# logic_unity.py
import os
import json
import UnityPy
from io import BytesIO
import zipfile
from logic_data import data_manager

class UnityProcessor:
    def __init__(self):
        # 核心源文件：必须手动放入根目录的 data/ 文件夹下
        self.bundle_names = ["recipe_decks_1", "recipe_definitions_1"]

    def extract_all_to_memory(self):
        """初始化时：提取笔记中包含的卡组 JSON 供前端使用"""
        all_extracted_data = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        valid_ids = data_manager.valid_eng_ids

        for b_name in self.bundle_names:
            bundle_path = os.path.join(base_dir, "data", b_name)
            if not os.path.exists(bundle_path): continue
            
            try:
                env = UnityPy.load(bundle_path)
                for obj in env.objects:
                    if obj.type.name == "MonoBehaviour":
                        try:
                            tree = obj.read_typetree()
                            name_val = tree.get("m_Name", "")
                            for eng_id in valid_ids:
                                if eng_id in name_val:
                                    all_extracted_data[eng_id] = tree
                                    break
                        except: continue
            except Exception as e:
                print(f"解析 {b_name} 失败: {e}")
        return all_extracted_data

    def repack_from_server_data(self, mods_dict):
        """[编辑器专属] 利用服务器底包在内存中回填，实现一键打包"""
        memory_zip = BytesIO()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for b_name in self.bundle_names:
                bundle_path = os.path.join(base_dir, "data", b_name)
                if not os.path.exists(bundle_path): continue
                
                env = UnityPy.load(bundle_path)
                for obj in env.objects:
                    if obj.type.name == "MonoBehaviour":
                        try:
                            tree = obj.read_typetree()
                            m_name = tree.get("m_Name", "")
                            if m_name in mods_dict:
                                tree["Cards"]["CardEntries"] = [{
                                    "Faction": c['faction'], "CardGuid": c['cardguid'],
                                    "Guid": c['guid'], "NumCopies": c['count'], "Filter": ""
                                } for c in mods_dict[m_name]]
                                obj.save_typetree(tree)
                        except: continue
                zf.writestr(b_name, env.file.save(packer="lz4"))
        memory_zip.seek(0)
        return memory_zip

unity_processor = UnityProcessor()
# logic_data.py
import os
import re

class DataManager:
    _instance = None

    # 单例模式：确保全局只加载一次数据
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._init_data()
        return cls._instance

    def _init_data(self):
        self.card_list = []      # 给前端用的扁平化卡牌列表
        self.hero_decks = {}     # 给前端用的卡组树
        self.valid_eng_ids = set() 
        
        # 强制在初始化时加载
        self.load_all_data()

    def load_all_data(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        uuid_path = os.path.join(base_dir, "data", "uuid.txt")
        deck_path = os.path.join(base_dir, "data", "笔记卡组名称.txt")

        # 1. 加载 UUID
        if os.path.exists(uuid_path):
            pattern = re.compile(r"(\d+)\s*[-—]+\s*([a-z0-9A-Za-z\s-]+)\s*[-—]+\s*(.+)")
            with open(uuid_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "——" not in line: continue
                    match = pattern.search(line)
                    if match:
                        guid, uuid, name = match.groups()
                        c_id = int(guid)
                        
                        # 简单的阵营判断 (这里你可以按需优化)
                        zombie_keywords = ["僵尸", "急冻魔", "霹雳舞王", "不死女妖", "无穷小子", "海妖", "教授", "锈铁侠", "超尸", "摔跤狂", "Z机甲", "错误"]
                        faction = 1 if any(kw in name for kw in zombie_keywords) else 0

                        self.card_list.append({
                            "name": name.strip(),
                            "CardGuid": c_id,
                            "Guid": uuid.strip(),
                            "Faction": faction
                        })

        # 2. 加载卡组名称
        if os.path.exists(deck_path):
            with open(deck_path, "r", encoding="utf-8") as f:
                content = f.read()
            blocks = re.split(r'\n\s*\n', content)
            for block in blocks:
                lines = [l.strip() for l in block.split('\n') if l.strip()]
                if not lines or "【卡组ID】" in lines[0]: continue
                
                first_name = lines[0].split('\t')[-1]
                hero_name = re.sub(r'\(.*?\)', '', first_name).strip()
                if hero_name not in self.hero_decks:
                    self.hero_decks[hero_name] = []
                
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        eng_id = parts[0].strip()
                        self.valid_eng_ids.add(eng_id)
                        self.hero_decks[hero_name].append({
                            "eng_id": eng_id,
                            "chn_name": parts[-1].strip()
                        })

# 实例化给其他文件导入使用
data_manager = DataManager()
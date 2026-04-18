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
            # 优化正则：更严格的 UUID 匹配，兼容各类横线/下划线组合
            pattern = re.compile(r"(\d+)\s*[-—_]+\s*([0-9a-fA-F-]+)\s*[-—_]+\s*(.+)")
            
            # 关键修复：使用 utf-8-sig 自动处理并剔除 Windows 的 BOM 头
            with open(uuid_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    # 关键修复：剔除常见的零宽字符及两端空白
                    line = line.strip().replace('\u200b', '')
                    if not line or "——" not in line: continue
                    
                    match = pattern.search(line)
                    if match:
                        guid, uuid_str, name = match.groups()
                        c_id = int(guid.strip())
                        
                        # 清理卡牌名称内部可能多余的连续空格，统归为一个空格
                        clean_name = re.sub(r'\s+', ' ', name.strip())
                        clean_uuid = uuid_str.strip()
                        
                        # 简单的阵营判断
                        zombie_keywords = ["僵尸", "急冻魔", "霹雳舞王", "不死女妖", "无穷小子", "海妖", "教授", "锈铁侠", "超尸", "摔跤狂", "Z机甲", "错误"]
                        # 确保 Faction 输出是干净的整型
                        faction = 1 if any(kw in clean_name for kw in zombie_keywords) else 0

                        self.card_list.append({
                            "name": clean_name,
                            "CardGuid": c_id,
                            "Guid": clean_uuid,
                            "Faction": faction
                        })

        # 2. 加载卡组名称
        if os.path.exists(deck_path):
            with open(deck_path, "r", encoding="utf-8-sig") as f: # 同样加上 -sig 护航
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
                            # 同样清理卡组名称可能带来的脏字符
                            "chn_name": re.sub(r'\s+', ' ', parts[-1].strip())
                        })

# 实例化给其他文件导入使用
data_manager = DataManager()
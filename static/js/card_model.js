// static/js/card_model.js

class CardModel {
    constructor() {
        // --- 基础信息 ---
        this.guid = 929802724;
        this.prefabName = PhantomUtils.generateUUID();
        this.baseId = "Base";
        this.faction = "Plants";
        this.color = "Guardian";
        this.rarityKey = 4;
        this.setName = "Gold";
        this.setAndRarityKey = "ShowCheer";
        this.craftingBuy = 929802724;
        this.craftingSell = 929802724;
        
        // --- 核心数值 ---
        this.cost = 1;
        this.hasAttack = true;
        this.hasHealth = true;
        this.attack = 1;
        this.health = 1;
        
        // --- 杂项与引擎标记 ---
        this.ignoreDeckLimit = false;
        this.isPower = false;
        this.isPrimaryPower = false;
        this.isTrick = false;         
        this.isSurprise = false;      
        this.isEnvironment = false;   
        this.isBoardAbility = false;  
        
        // --- 复杂数据结构 ---
        this.componentsAbilities = {}; 
        this.triggeredAbilities = [];  
        this.rootSpecialAbilities = [];
        
        // --- 种族与标签 ---
        this.logicSubtypes = [];
        this.displaySubtypes = [];
        this.subtypeAffinities = [];
        this.subtypeAffinityWeights = [];
        
        this.logicTags = [];
        this.displayTags = [];
        this.tagAffinities = [];
        this.tagAffinityWeights = [];
    }

    /**
     * 从官方数据字典 (data_card_1.json 中的单卡数据) 还原为 CardModel
     */
    importFromRawData(guid, rawData) {
        this.guid = parseInt(guid);
        this.prefabName = rawData.prefabName || this.prefabName;
        this.baseId = rawData.baseId || this.baseId;
        this.faction = rawData.faction || this.faction;
        
        // 核心数值提取
        this.cost = rawData.cost !== undefined ? rawData.cost : this.cost;
        this.hasAttack = rawData.hasAttack !== undefined ? rawData.hasAttack : this.hasAttack;
        this.hasHealth = rawData.hasHealth !== undefined ? rawData.hasHealth : this.hasHealth;
        this.attack = rawData.attack !== undefined ? rawData.attack : this.attack;
        this.health = rawData.health !== undefined ? rawData.health : this.health;
        
        // 导入逻辑树数组 (交给 LogicAdapter 反向解析)
        if (rawData.triggeredAbilities && Array.isArray(rawData.triggeredAbilities)) {
            this.triggeredAbilities = rawData.triggeredAbilities;
        } else {
            this.triggeredAbilities = [];
        }
        
        // 参考 Python 项目的 _restore_node_dict，继续增加对其他属性的解析
    }

    generateJsonDict() {
        return JSON.parse(JSON.stringify(this));
    }
}
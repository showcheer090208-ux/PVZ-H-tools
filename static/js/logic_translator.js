// static/js/logic_translator.js
// 对应原项目的 logic_translator.py，负责将 JSON 逻辑节点翻译为人类可读文本

const LogicTranslator = {
    // 1. 从长长的装配集名称中提取简短的组件名
    // 例如: "PvZCards.Engine.Components.DamageEffectDescriptor, EngineLib..." -> "DamageEffectDescriptor"
    parseTypeStr(typeStr) {
        if (!typeStr) return "";
        return typeStr.split(',')[0].split('.').pop();
    },

    // 2. 翻译查询条件 (Query)
    parseQuery(queryData) {
        if (!queryData) return "";
        const compName = this.parseTypeStr(queryData.$type);
        const d = queryData.$data || {};

        // --- 复合查询 (递归) ---
        if (compName === "CompositeAllQuery") {
            const queries = d.queries || [];
            return queries.map(q => this.parseQuery(q)).filter(Boolean).join(" 且 ");
        }
        if (compName === "CompositeAnyQuery") {
            const queries = d.queries || [];
            return queries.map(q => this.parseQuery(q)).filter(Boolean).join(" 或 ");
        }
        if (compName === "NotQuery") {
            const inner = this.parseQuery(d.Query);
            return inner ? `不满足【${inner}】` : "否定条件";
        }

        // --- 原子条件查表 ---
        const queryMap = {
            "SelfQuery": "其自身",
            "TargetQuery": "目标",
            "InSameLaneQuery": "同一行的",
            "InLaneSameAsLaneQuery": "相同指定行的",
            "TargetableInPlayFighterQuery": "场上的斗士",
            "AlwaysMatchesQuery": "所有目标",
            "BehindSameLaneQuery": "同行的后面",
            "DrawnCardQuery": "抽到的卡牌"
        };

        return queryMap[compName] || `[未知目标:${compName}]`;
    },

    // 3. 翻译核心效果 (Effect)
    parseEffect(effectData) {
        if (!effectData) return "";
        const compName = this.parseTypeStr(effectData.$type);
        const d = effectData.$data || {};

        let text = "";

        // 根据不同的组件名生成自然语言
        switch (compName) {
            case "DamageEffectDescriptor":
                text = `造成 ${d.Amount || 1} 点伤害`;
                break;
            case "BuffEffectDescriptor":
                const atk = d.AddAttack || 0;
                const hp = d.AddHealth || 0;
                text = `获得 ${atk > 0 ? '+'+atk : atk}攻击 / ${hp > 0 ? '+'+hp : hp}生命`;
                break;
            case "DestroyCardEffectDescriptor":
                text = "直接消灭";
                break;
            case "DrawCardEffectDescriptor":
                text = `抽 ${d.DrawAmount || 1} 张牌`;
                break;
            case "HealEffectDescriptor":
                text = `恢复 ${d.Amount || 1} 点生命值`;
                break;
            default:
                // 如果遇到还没有配置翻译规则的节点，直接显示其中文名或组件名
                text = PhantomConfig.getNodeName(compName);
                break;
        }

        // 检查是否有 Target (目标)
        if (d.Target) {
            const targetStr = this.parseQuery(d.Target);
            text = `对 【${targetStr}】 ${text}`;
        }

        return text;
    }
};
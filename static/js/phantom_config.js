// static/js/phantom_config.js
// 整合了原有的 localization.py, constants.py 和 logic_library.py 的前端静态数据库

const PhantomConfig = {
    // ==================== 1. 基础常量 (constants.py) ====================
    NAMESPACE_ENGINE: "PvZCards.Engine.Components.",
    NAMESPACE_QUERY: "PvZCards.Engine.Queries.",
    ASSEMBLY_SUFFIX: ", EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null",

    // ==================== 2. 中文翻译字典 (localization.py) ====================
    NODE_NAMES: {
        // ==================== Framework 基础框架 ====================
        "EffectEntityGrouping": "⚙️ 基础框架 (EffectEntityGrouping)",
    
        // ==================== Trigger 触发器 ====================
        "PlayTrigger": "🟢 触发: 当打出时",
        "DiscardFromPlayTrigger": "🟢 触发: 当死亡时",
        "BuffTrigger": "🟢 触发: 当获得属性加成时",
        "CombatEndTrigger": "🟢 触发: 战斗结束时",
        "DamageTrigger": "🟢 触发: 受到伤害时",
        "DestroyCardTrigger": "🟢 触发: 消灭卡牌时",
        "DrawCardTrigger": "🟢 触发: 抽牌时",
        "DrawCardFromSubsetTrigger": "🟢 触发: 召唤卡牌触发",
        "EnterBoardTrigger": "🟢 触发: 进场时",
        "ExtraAttackTrigger": "🟢 触发: 额外攻击时",
        "HealTrigger": "🟢 触发: 治疗时",
        "LaneCombatEndTrigger": "🟢 触发: 单路战斗结束时",
        "LaneCombatStartTrigger": "🟢 触发: 单路战斗开始时",
        "MoveTrigger": "🟢 触发: 移动时",
        "ReturnToHandTrigger": "🟢 触发: 返回手牌时",
        "RevealPhaseEndTrigger": "🟢 触发: 揭示阶段结束时",
        "RevealTrigger": "🟢 触发: 揭示时",
        "SlowedTrigger": "🟢 触发: 被冰冻时",
        "SurprisePhaseStartTrigger": "🟢 触发: 奇袭阶段开始时",
        "TurnStartTrigger": "🟢 触发: 回合开始时",
    
        // ==================== Filter 过滤器 ====================
        "TriggerTargetFilter": "🟡 触发目标限制 (TriggerTargetFilter)",
        "TriggerSourceFilter": "🟡 触发来源限制 (TriggerSourceFilter)",
        "QueryEntityCondition": "🟡 实体条件判断 (QueryEntityCondition)",
        "SelfEntityFilter": "🟡 自身实体过滤 (SelfEntityFilter)",
        "PlayerInfoCondition": "🟡 玩家信息条件 (PlayerInfoCondition)",
    
        // ==================== TargetSelector 目标选取 ====================
        "PrimaryTargetFilter": "🟠 执行目标选取 (PrimaryTargetFilter)",
        "SecondaryTargetFilter": "🎯 次要目标选取 (SecondaryTargetFilter)",
    
        // ==================== Condition 限制配置 ====================
        "OncePerGameCondition": "🟣 限制: 每局一次",
        "OncePerTurnCondition": "🟣 限制: 每回合一次",
        "PersistsAfterTransform": "🟣 限制: 变形后保留技能 (PersistsAfterTransform)",
    
        // ==================== CompositeQuery 复合查询 ====================
        "CompositeAllQuery": "🔗 满足所有条件 [AND]",
        "CompositeAnyQuery": "🔗 满足任一条件 [OR]",
        "NotQuery": "🔗 否定 (NOT)",
    
        // ==================== Query 原子查询 ====================
        "AlwaysMatchesQuery": "🔵 条件: 永远匹配",
        "BehindSameLaneQuery": "🔵 范围: 在同行的后面",
        "DrawnCardQuery": "🔵 对象: 抽到的卡牌",
        "FighterQuery": "🔵 条件: 是斗士单位",
        "InEnvironmentQuery": "🔵 范围: 在场地上",
        "InHandQuery": "🔵 范围: 在手牌中",
        "InLaneQuery": "🔵 范围: 在行内",
        "InOneTimeEffectZoneQuery": "🔵 范围: 在一次性效果区",
        "InUnopposedLaneQuery": "🔵 条件: 在无对手的行",
        "IsActiveQuery": "🔵 条件: 处于激活状态",
        "IsAliveQuery": "🔵 条件: 存活状态",
        "LastLaneOfSelfQuery": "🔵 范围: 自身的最后一行",
        "OriginalTargetCardGuidQuery": "🔵 对象: 原始目标卡牌",
        "SameFactionQuery": "🔵 条件: 同阵营",
        "SameLaneAsTargetQuery": "🔵 范围: 与目标同行",
        "SameLaneQuery": "🔵 范围: 在同一行",
        "SelfQuery": "🔵 对象: 自己",
        "SourceQuery": "🔵 对象: 来源",
        "SpringboardedOnSelfQuery": "🔵 条件: 跳板作用于自身",
        "TargetCardGuidQuery": "🔵 对象: 目标的卡牌",
        "TargetQuery": "🔵 对象: 选中的目标",
        "TargetableInPlayFighterQuery": "🔵 条件: 场上可选中单位",
        "TrickQuery": "🔵 条件: 是锦囊/法术",
        "WasInSameLaneAsSelfQuery": "🔵 范围: 曾与自身同行",
        "WillTriggerEffectsQuery": "🔵 条件: 将触发效果",
        "WillTriggerOnDeathEffectsQuery": "🔵 条件: 将触发死亡效果",
    
        // ---------- 单参数 ----------
        "AdjacentLaneQuery": "🔵 范围: 相邻的行 (指定来源)",
        "CardGuidQuery": "🔵 条件: 卡牌GUID匹配",
        "InAdjacentLaneQuery": "🔵 范围: 在相邻的行",
        "InLaneAdjacentToLaneQuery": "🔵 范围: 在相邻的行",
        "InLaneSameAsLaneQuery": "🔵 范围: 行数相同匹配",
        "InSameLaneQuery": "🔵 范围: 在同一行",
        "LaneOfIndexQuery": "🔵 范围: 指定索引的行",
        "QueryMultiplier": "🔵 查询倍率 (QueryMultiplier)",
        "SubsetQuery": "🔵 条件: 属于特定子集",
        "SubtypeQuery": "🔵 条件: 属于特定种族 (Subtype)",
    
        // ---------- 比较运算符 ----------
        "AttackComparisonQuery": "🔵 条件: 攻击力数值判断",
        "BlockMeterValueQuery": "🔵 条件: 格挡值判断",
        "DamageTakenComparisonQuery": "🔵 条件: 已受伤害判断",
        "HealthComparisonQuery": "🔵 条件: 生命值判断 (HealthComparison)",
        "SunCostComparisonQuery": "🔵 条件: 阳光/脑子费用判断",
        "SunCostPlusNComparisonQuery": "🔵 条件: 费用+N 判断",
        "SunCounterComparisonQuery": "🔵 条件: 阳光计数器判断",
        "TurnCountQuery": "🔵 条件: 回合数判断",
    
        // ---------- 组件类型 ----------
        "HasComponentQuery": "🔵 条件: 拥有组件",
        "LacksComponentQuery": "🔵 条件: 缺少组件",
        "OnTerrainQuery": "🔵 条件: 在地形上",
        "OpenLaneQuery": "🔵 条件: 空行判断",
    
        // ---------- 预定义快捷方式 ----------
        "HasZombiesComponent": "🔵 条件: 是僵尸",
        "HasPlantsComponent": "🔵 条件: 是植物",
        "HasPlayerComponent": "🔵 条件: 是英雄/玩家 (Player)",
        "HasLaneComponent": "🔵 条件: 是一整行(地段)",
        "HasFaceDownComponent": "🔵 条件: 是暗置/墓碑",
        "HasEnvironmentComponent": "🔵 条件: 是场地牌",
        "HasWaterTerrainComponent": "🔵 条件: 在水生地形",
        "HasHighgroundTerrainComponent": "🔵 条件: 在高地地形",
        "HasUnhealableComponent": "🔵 条件: 不可治疗",
        "HasSuperpowerComponent": "🔵 条件: 是英雄技能 (Superpower)",
    
        // ==================== Effect 效果 ====================
        "CopyStatsEffect": "🔴 效果: 复制属性",
        "DestroyCardEffect": "🔴 效果: 直接消灭",
        "ExtraAttackEffect": "🔴 效果: 额外攻击",
        "MixedUpGravediggerEffectDescriptor": "🔴 效果: 掘墓人墓碑",
        "MoveCardToLanesEffectDescriptor": "🔴 效果: 移动",
        "ReturnToHandEffect": "🔴 效果: 弹回手牌",
        "SlowEffect": "🔴 效果: 冰冻 (Slow)",
        "TurnIntoGravestoneEffectDescriptor": "🔴 效果: 回到墓碑",
        "AttackInLaneEffectDescriptor": "🔴 效果: 攻击本行 (AttackInLane)",
        "BuffEffect": "🔴 效果: 属性改变 (Buff/Debuff)",
        "ChargeBlockMeterEffectDescriptor": "🔴 效果: 充能格挡值 (ChargeBlockMeter)",
        "CopyCardEffectDescriptor": "🔴 效果: 复制卡牌 (CopyCard)",
        "CreateCardEffect": "🔴 效果: 召唤特定卡牌 (GUID)",
        "CreateCardInDeckEffect": "🔴 效果: 洗入牌库",
        "DamageEffect": "🔴 效果: 造成伤害",
        "DrawCardEffect": "🔴 效果: 抽牌",
        "EffectValueDescriptor": "🔴 效果: 效果值映射 (EffectValueDescriptor)",
        "GainSunEffect": "🔴 效果: 获得阳光/脑子",
        "GrantAbilityEffect": "🔴 效果: 赋予特殊能力 (关键字)",
        "GrantTriggeredAbilityEffectDescriptor": "🔴 效果: 赋予能力 (GrantTriggeredAbility)",
        "HealEffect": "🔴 效果: 治疗",
        "HeroHealthMultiplier": "🔴 效果: 英雄血量倍率 (HeroHealthMultiplier)",
        "ModifySunCostEffect": "🔴 效果: 修改卡牌花费",
        "SetStatEffect": "🔴 效果: 属性数值强制设定 (SetStat)",
        "SunGainedMultiplier": "🔴 效果: 获得阳光倍率 (SunGainedMultiplier)",
        "TargetAttackMultiplier": "🔴 效果: 攻击力翻倍/倍增",
        "TargetHealthMultiplier": "🔴 效果: 生命值翻倍/倍增",
    
        // ==================== ComplexEffect 复合效果 ====================
        "DrawCardFromSubsetEffect": "🟥 复合：召唤",
        "CreateCardFromSubsetEffectDescriptor": "🟥 效果: 生成卡牌 (CreateCardFromSubset)",
        "TransformIntoCardFromSubsetEffectDescriptor": "🟥 效果: 变身 (TransformIntoSubset)",
    
        // ==================== Virtual 虚拟/UI辅助 ====================
        "AdditionalTargetQuery": "📦 额外目标条件",
        "FinderPlaceholder": "🔍 查找范围 (Finder)",
        "QueryPlaceholder": "📋 满足条件 (Query)",
    
        // ==================== 以下为补充节点（兼容旧版/别名） ====================
        "AbilityGuid": "能力 GUID (常用: 562=双重攻击, 564=先攻, 615=远古吸血, 668=狩猎场)",
        "AbilityValueType": "能力数值类型",
        "AbilityValueAmount": "能力数值",
        "CompositeQuery": "🔗 复合查询",
        "Query": "🔵 查询条件",
        "Effect": "🔴 效果",
        "Filter": "🟡 过滤器",
        "TargetSelector": "🎯 目标选择器",
        "BuffEffectDescriptor": "🔴 效果: 属性改变",
        "DamageEffectDescriptor": "🔴 效果: 造成伤害",
        "DestroyCardEffectDescriptor": "🔴 效果: 直接消灭",
        "DrawCardEffectDescriptor": "🔴 效果: 抽牌",
        "HealEffectDescriptor": "🔴 效果: 治疗",
        "ExtraAttackEffectDescriptor": "🔴 效果: 额外攻击",
        "ReturnToHandFromPlayEffectDescriptor": "🔴 效果: 弹回手牌",
        "SlowEffectDescriptor": "🔴 效果: 冰冻",
        "GainSunEffectDescriptor": "🔴 效果: 获得阳光",
        "ModifySunCostEffectDescriptor": "🔴 效果: 修改费用",
        "CreateCardInDeckEffectDescriptor": "🔴 效果: 洗入牌库",
        "GrantAbilityEffectDescriptor": "🔴 效果: 赋予能力",
        "CreateCardEffectDescriptor": "🔴 效果: 召唤卡牌",
        "SetStatEffectDescriptor": "🔴 效果: 设置属性",
        "CopyStatsEffectDescriptor": "🔴 效果: 复制属性",
        "Multishot": "多重射击 (Multishot)",
        "AttacksInAllLanes": "全路攻击 (AttacksInAllLanes)",
        "PlaysFaceDown": "暗置 (PlaysFaceDown)",
        "Aquatic": "水生 (Aquatic)",
        "DoubleStrike": "连击 (DoubleStrike)",
        "AttackOverride": "攻击覆盖 (AttackOverride)",
        "SplashDamage": "溅射伤害 (SplashDamage)",
        "Divider": "倍数/除数",
        "Amount": "数值",
        "ActivationTime": "执行时间",
        "CardGuid": "卡牌 ID (GUID)",
        "AmountToCreate": "生成数量",
        "DeckPosition": "洗入位置",
        "Immediate": "立即执行",
        "NextTurn": "下回合开始",
        "Top": "牌库顶",
        "Bottom": "牌库底",
        "GrantableAbilityType": "赋予的能力类型",
        "StripNoncontinousModifiers": "剥离非持续性加成 (清空临时Buff)",
        "StatType": "修改属性类型",
        "AbilityValue": "特殊修正值 (如免疫类型)",
        "ModifyOperation": "修改方式",
        "ForceFaceDown": "以墓碑/潜行方式召唤",
        "Permanent": "永久",
        "EndOfTurn": "回合结束",
        "Either": "任意侧",
        "ToTheLeft": "左侧",
        "ToTheRight": "右侧",
        "Self": "自身",
        "Source": "来源",
        "Target": "目标",
    },

    PARAM_NAMES: {
        "MappingType": "映射类型",
        "DestToSourceMap": "目标到源映射 (如 HealAmount: DamageAmount)",
        "AbilityGroupId": "技能组 ID",
        "SelectionType": "选择目标方式",
        "NumTargets": "目标数量",
        "TargetScopeType": "目标范围筛选",
        "TargetScopeSortValue": "排序参考数值",
        "TargetScopeSortMethod": "排序方法",
        "AdditionalTargetType": "额外目标类型",
        "OnlyApplyEffectsOnAdditionalTargets": "仅对额外目标生效",
        "OriginEntityType": "基准实体",
        "Side": "相邻方向",
        "ComparisonOperator": "比较符号",
        "AttackValue": "攻击力比较值",
        "DamageAmount": "伤害数值",
        "AttackAmount": "攻击力改变(Buff)",
        "HealthAmount": "生命值改变(Buff)",
        "BuffDuration": "持续时间",
        "SunCost": "阳光/脑子费用",
        "DrawAmount": "抽牌数量",
        "HealAmount": "治疗量",
        "Divider": "倍数",
        "Amount": "数值",
        "ActivationTime": "激活时机",
        "CardGuid": "卡牌GUID",
        "AmountToCreate": "创建数量",
        "DeckPosition": "牌库位置",
        "GrantableAbilityType": "赋予的能力",
        "AbilityValue": "能力参数",
        "ModifyOperation": "修改操作",
        "Value": "数值",
        "ForceFaceDown": "强制暗置",
        "StatType": "属性类型",
        "StripNoncontinousModifiers": "移除非持续修正",
        "Duration": "持续时间",
        "Subtype": "子类型/种族",
        "ConditionEvaluationType": "满足规则的判定方式",
        "Finder": "查找器/来源",
        "ChargeAmount": "充能数值",
        "GrantTeamup": "赋予组队能力",
        "CreateInFront": "在身前创建",
        "AbilityGuid": "能力 GUID",
        "AbilityValueType": "能力数值类型",
        "AbilityValueAmount": "能力数值",
        "HealthValue": "生命值比较值",
    },

    // ==================== 下拉框枚举值翻译 ====================
    ENUM_NAMES: {
        "DamageToHeal": "伤害 → 治疗 (DamageAmount → HealAmount)",
        "HealToDamage": "治疗 → 伤害 (HealAmount → DamageAmount)",
        "Manual": "手动选取 (Manual)",
        "Random": "随机选取 (Random)",
        "All": "全部符合条件者 (All)",
        "Sorted": "按条件排序 (Sorted)",
        "None": "无 (None)",
        "Attack": "攻击力 (Attack)",
        "Health": "生命值 (Health)",
        "Lowest": "最低的 (Lowest)",
        "Highest": "最高的 (Highest)",
        "Query": "自定义查询 (Query)",
        "Self": "自身 (Self)",
        "Source": "来源 (Source)",
        "Target": "目标 (Target)",
        "Either": "任意两侧 (Either)",
        "ToTheLeft": "左侧 (ToTheLeft)",
        "ToTheRight": "右侧 (ToTheRight)",
        "LessOrEqual": "小于等于 (<=)",
        "Equal": "等于 (==)",
        "GreaterOrEqual": "大于等于 (>=)",
        "Permanent": "永久 (Permanent)",
        "EndOfTurn": "回合结束时 (EndOfTurn)",
        "Immediate": "立即 (Immediate)",
        "NextTurn": "下回合 (NextTurn)",
        "Top": "牌库顶 (Top)",
        "Bottom": "牌库底 (Bottom)",
        "Add": "增加 (Add)",
        "Set": "设置为 (Set)",
        "Unhurtable": "无敌 (Unhurtable)",
        "Deadly": "致命 (Deadly)",
        "Frenzy": "狂怒 (Frenzy)",
        "Truestrike": "精准打击 (Truestrike)",
        "Strikethrough": "穿透 (Strikethrough)",
        "Afterlife": "来世 (Afterlife)",
        "MinHealth": "最小生命值 (MinHealth)",
        "NoExtraAttacks": "无法额外攻击 (NoExtraAttacks)",
        "GravestoneSpy": "墓碑侦察 (GravestoneSpy)",
        "Teamup": "组队 (Teamup)",
        "Aquatic": "水生 (Aquatic)",
        "CanPlayFighterInSurprisePhase": "奇袭阶段可打出 (CanPlayFighterInSurprisePhase)",
        "Mustache": "胡子 (Mustache)",
        "AttackOverride": "攻击覆盖 (AttackOverride)",
        "MultiplyDamage": "伤害翻倍 (MultiplyDamage)",
        "Graveyard": "墓地 (Graveyard)",
        "Untrickable": "锦囊免疫 (Untrickable)",
        "Unhealable": "不可治疗 (Unhealable)",
        "BlockMeterValue": "格挡值",
        "DamageTakenValue": "已受伤害值",
        "AdditionalCost": "额外费用",
        "SunCounterValue": "阳光计数器值",
        "TurnCount": "回合数",
        "Plants": "植物阵营",
        "Zombies": "僵尸阵营",
        "PvZCards.Engine.Components.Plants, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null": "植物阵营",
        "PvZCards.Engine.Components.Zombies, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null": "僵尸阵营",
        "GrassTerrain": "草地",
        "WaterTerrain": "水域",
        "HighgroundTerrain": "高地",
        "Environment": "场地",
        "FaceDown": "暗置/墓碑",
        "Any": "任意满足 (Any)",
        "562: 双重攻击 (DoubleStrike)": "562: 双重攻击 (DoubleStrike)",
        "564: 先攻 (FirstStrike)": "564: 先攻 (FirstStrike)",
        "615: 远古吸血僵尸 (AncientVampireZombie)": "615: 远古吸血僵尸 (AncientVampireZombie)",
        "668: 狩猎场 (HuntingGrounds)": "668: 狩猎场 (HuntingGrounds)",
        "0: 自定义 GUID": "0: 自定义 GUID (手动输入)",
        "Damage": "伤害 (Damage)",
    },
    
    // ==================== 效果描述模板（供 logic_translator.py 使用）====================
    EFFECT_DESCRIPTIONS: {
        "DamageEffect": "造成 {damage} 点伤害",
        "BuffEffect": "{duration}获得攻击力 {attack:+d} / 生命值 {health:+d}",
        "DestroyCardEffect": "直接消灭目标",
        "DrawCardEffect": "抽 {amount} 张牌",
        "HealEffect": "恢复 {amount} 点生命值",
        "ExtraAttackEffect": "获得额外一次攻击机会",
        "TargetAttackMultiplier": "攻击力变为 {divider} 倍",
        "TargetHealthMultiplier": "生命值变为 {divider} 倍",
        "ReturnToHandEffect": "将目标弹回手牌",
        "SlowEffect": "冰冻目标",
        "GainSunEffect": "{when}获得 {amount} 点阳光/脑子",
        "ModifySunCostEffect": "{duration}使卡牌花费改变 {amount}",
        "CreateCardInDeckEffect": "将 {amount} 张卡牌 (ID:{card_id}) 洗入牌库的 {position}",
        "GrantAbilityEffect": "{duration}赋予能力【{ability}】{extra}",
        "CreateCardEffect": "{face_down}召唤卡牌 (ID:{card_id})",
        "SetHeroHealthEffect": "{operation}英雄生命值 {amount} 点",
        "CopyStatsEffect": "复制目标的属性数值",
    },

    // ==================== 3. 核心节点定义 (logic_library.py) ====================
    NODE_DEF: {
        // ==================== Framework 基础框架 ====================
        "EffectEntityGrouping": {
            "type": "PvZCards.Engine.Components.EffectEntityGrouping",
            "default_data": {"AbilityGroupId": 0},
            "editable_params": {"AbilityGroupId": {"type": "int", "min": 0, "max": 2147483647}},
            "category": "Framework"
        },
    
        // ==================== Trigger 触发器 ====================
        "PlayTrigger": {
            "type": "PvZCards.Engine.Components.PlayTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "DiscardFromPlayTrigger": {
            "type": "PvZCards.Engine.Components.DiscardFromPlayTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "BuffTrigger": {
            "type": "PvZCards.Engine.Components.BuffTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "CombatEndTrigger": {
            "type": "PvZCards.Engine.Components.CombatEndTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "DamageTrigger": {
            "type": "PvZCards.Engine.Components.DamageTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "DestroyCardTrigger": {
            "type": "PvZCards.Engine.Components.DestroyCardTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "DrawCardTrigger": {
            "type": "PvZCards.Engine.Components.DrawCardTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "DrawCardFromSubsetTrigger": {
            "type": "PvZCards.Engine.Components.DrawCardFromSubsetTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "EnterBoardTrigger": {
            "type": "PvZCards.Engine.Components.EnterBoardTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "ExtraAttackTrigger": {
            "type": "PvZCards.Engine.Components.ExtraAttackTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "HealTrigger": {
            "type": "PvZCards.Engine.Components.HealTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "LaneCombatEndTrigger": {
            "type": "PvZCards.Engine.Components.LaneCombatEndTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "LaneCombatStartTrigger": {
            "type": "PvZCards.Engine.Components.LaneCombatStartTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "MoveTrigger": {
            "type": "PvZCards.Engine.Components.MoveTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "ReturnToHandTrigger": {
            "type": "PvZCards.Engine.Components.ReturnToHandTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "RevealPhaseEndTrigger": {
            "type": "PvZCards.Engine.Components.RevealPhaseEndTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "RevealTrigger": {
            "type": "PvZCards.Engine.Components.RevealTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "SlowedTrigger": {
            "type": "PvZCards.Engine.Components.SlowedTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "SurprisePhaseStartTrigger": {
            "type": "PvZCards.Engine.Components.SurprisePhaseStartTrigger",
            "default_data": {},
            "category": "Trigger"
        },
        "TurnStartTrigger": {
            "type": "PvZCards.Engine.Components.TurnStartTrigger",
            "default_data": {},
            "category": "Trigger"
        },
    
        // ==================== Filter 过滤器 ====================
        "TriggerTargetFilter": {
            "type": "PvZCards.Engine.Components.TriggerTargetFilter",
            "default_data": {},
            "child_prop": "Query",
            "is_list": false,
            "category": "Filter",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "TriggerSourceFilter": {
            "type": "PvZCards.Engine.Components.TriggerSourceFilter",
            "default_data": {},
            "child_prop": "Query",
            "is_list": false,
            "category": "Filter",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "QueryEntityCondition": {
            "type": "PvZCards.Engine.Components.QueryEntityCondition",
            "default_data": {
                "ConditionEvaluationType": "All"
            },
            "editable_params": {
                "ConditionEvaluationType": {"type": "enum", "options": ["All", "Any"]}
            },
            "category": "Filter"
        },
        "SelfEntityFilter": {
            "type": "PvZCards.Engine.Components.SelfEntityFilter",
            "default_data": {},
            "child_prop": "Query",
            "is_list": false,
            "category": "Filter",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "PlayerInfoCondition": {
            "type": "PvZCards.Engine.Components.PlayerInfoCondition",
            "default_data": {
                "Faction": "Plants"
            },
            "editable_params": {
                "Faction": {"type": "enum", "options": ["Plants", "Zombies"]}
            },
            "child_prop": "Query",
            "is_list": false,
            "category": "Filter",
            "allowed_children": ["CompositeQuery", "Query"]
        },
    
        // ==================== TargetSelector 目标选取 ====================
        "PrimaryTargetFilter": {
            "type": "PvZCards.Engine.Components.PrimaryTargetFilter",
            "default_data": {
                "SelectionType": "All",
                "NumTargets": 0,
                "TargetScopeType": "All",
                "TargetScopeSortValue": "None",
                "TargetScopeSortMethod": "None",
                "AdditionalTargetType": "None",
                "AdditionalTargetQuery": null,
                "OnlyApplyEffectsOnAdditionalTargets": false
            },
            "editable_params": {
                "SelectionType": {"type": "enum", "options": ["Manual", "Random", "All"]},
                "NumTargets": {"type": "int", "min": 0, "max": 2147483647},
                "TargetScopeType": {"type": "enum", "options": ["All", "Sorted"]},
                "TargetScopeSortValue": {"type": "enum", "options": ["None", "Attack", "Health"]},
                "TargetScopeSortMethod": {"type": "enum", "options": ["None", "Lowest", "Highest"]},
                "AdditionalTargetType": {"type": "enum", "options": ["None", "Query"]},
                "OnlyApplyEffectsOnAdditionalTargets": {"type": "bool"}
            },
            "child_prop": "Query",
            "is_list": false,
            "category": "TargetSelector",
            "allowed_children": ["CompositeQuery", "Query", "AdditionalTargetQuery"]
        },
        "SecondaryTargetFilter": {
            "type": "PvZCards.Engine.Components.SecondaryTargetFilter",
            "default_data": {
                "SelectionType": "All",
                "NumTargets": 0,
                "TargetScopeType": "All",
                "TargetScopeSortValue": "None",
                "TargetScopeSortMethod": "None",
                "AdditionalTargetType": "None",
                "AdditionalTargetQuery": null,
                "OnlyApplyEffectsOnAdditionalTargets": false
            },
            "editable_params": {
                "SelectionType": {"type": "enum", "options": ["Manual", "Random", "All"]},
                "NumTargets": {"type": "int", "min": 0, "max": 2147483647},
                "TargetScopeType": {"type": "enum", "options": ["All", "Sorted"]},
                "TargetScopeSortValue": {"type": "enum", "options": ["None", "Attack", "Health"]},
                "TargetScopeSortMethod": {"type": "enum", "options": ["None", "Lowest", "Highest"]},
                "AdditionalTargetType": {"type": "enum", "options": ["None", "Query"]},
                "OnlyApplyEffectsOnAdditionalTargets": {"type": "bool"}
            },
            "child_prop": "Query",
            "is_list": false,
            "category": "TargetSelector",
            "allowed_children": ["CompositeQuery", "Query", "AdditionalTargetQuery"]
        },
    
        // ==================== Condition 限制配置 ====================
        "OncePerGameCondition": {
            "type": "PvZCards.Engine.Components.OncePerGameCondition",
            "default_data": {},
            "category": "Condition"
        },
        "OncePerTurnCondition": {
            "type": "PvZCards.Engine.Components.OncePerTurnCondition",
            "default_data": {},
            "category": "Condition"
        },
        "PersistsAfterTransform": {
            "type": "PvZCards.Engine.Components.PersistsAfterTransform",
            "default_data": {},
            "category": "Condition"
        },
    
        // ==================== CompositeQuery 复合查询 ====================
        "CompositeAllQuery": {
            "type": "PvZCards.Engine.Queries.CompositeAllQuery",
            "default_data": {},
            "child_prop": "queries",
            "is_list": true,
            "category": "CompositeQuery",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "CompositeAnyQuery": {
            "type": "PvZCards.Engine.Queries.CompositeAnyQuery",
            "default_data": {},
            "child_prop": "queries",
            "is_list": true,
            "category": "CompositeQuery",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "NotQuery": {
            "type": "PvZCards.Engine.Queries.NotQuery",
            "default_data": {},
            "child_prop": "Query",
            "is_list": false,
            "category": "CompositeQuery",
            "allowed_children": ["CompositeQuery", "Query"]
        },
    
        // ==================== Query 原子查询 ====================
        // ---------- 无参数 ----------
        "AlwaysMatchesQuery": {
            "type": "PvZCards.Engine.Queries.AlwaysMatchesQuery",
            "default_data": {},
            "category": "Query"
        },
        "BehindSameLaneQuery": {
            "type": "PvZCards.Engine.Queries.BehindSameLaneQuery",
            "default_data": {},
            "category": "Query"
        },
        "DrawnCardQuery": {
            "type": "PvZCards.Engine.Queries.DrawnCardQuery",
            "default_data": {},
            "category": "Query"
        },
        "FighterQuery": {
            "type": "PvZCards.Engine.Queries.FighterQuery",
            "default_data": {},
            "category": "Query"
        },
        "InEnvironmentQuery": {
            "type": "PvZCards.Engine.Queries.InEnvironmentQuery",
            "default_data": {},
            "category": "Query"
        },
        "InHandQuery": {
            "type": "PvZCards.Engine.Queries.InHandQuery",
            "default_data": {},
            "category": "Query"
        },
        "InLaneQuery": {
            "type": "PvZCards.Engine.Queries.InLaneQuery",
            "default_data": {},
            "category": "Query"
        },
        "InOneTimeEffectZoneQuery": {
            "type": "PvZCards.Engine.Queries.InOneTimeEffectZoneQuery",
            "default_data": {},
            "category": "Query"
        },
        "InUnopposedLaneQuery": {
            "type": "PvZCards.Engine.Queries.InUnopposedLaneQuery",
            "default_data": {},
            "category": "Query"
        },
        "IsActiveQuery": {
            "type": "PvZCards.Engine.Queries.IsActiveQuery",
            "default_data": {},
            "category": "Query"
        },
        "IsAliveQuery": {
            "type": "PvZCards.Engine.Queries.IsAliveQuery",
            "default_data": {},
            "category": "Query"
        },
        "LastLaneOfSelfQuery": {
            "type": "PvZCards.Engine.Queries.LastLaneOfSelfQuery",
            "default_data": {},
            "category": "Query"
        },
        "OriginalTargetCardGuidQuery": {
            "type": "PvZCards.Engine.Queries.OriginalTargetCardGuidQuery",
            "default_data": {},
            "category": "Query"
        },
        "SameFactionQuery": {
            "type": "PvZCards.Engine.Queries.SameFactionQuery",
            "default_data": {},
            "category": "Query"
        },
        "SameLaneAsTargetQuery": {
            "type": "PvZCards.Engine.Queries.SameLaneAsTargetQuery",
            "default_data": {},
            "category": "Query"
        },
        "SameLaneQuery": {
            "type": "PvZCards.Engine.Queries.SameLaneQuery",
            "default_data": {},
            "category": "Query"
        },
        "SelfQuery": {
            "type": "PvZCards.Engine.Queries.SelfQuery",
            "default_data": {},
            "category": "Query"
        },
        "SourceQuery": {
            "type": "PvZCards.Engine.Queries.SourceQuery",
            "default_data": {},
            "category": "Query"
        },
        "SpringboardedOnSelfQuery": {
            "type": "PvZCards.Engine.Queries.SpringboardedOnSelfQuery",
            "default_data": {},
            "category": "Query"
        },
        "TargetCardGuidQuery": {
            "type": "PvZCards.Engine.Queries.TargetCardGuidQuery",
            "default_data": {},
            "category": "Query"
        },
        "TargetQuery": {
            "type": "PvZCards.Engine.Queries.TargetQuery",
            "default_data": {},
            "category": "Query"
        },
        "TargetableInPlayFighterQuery": {
            "type": "PvZCards.Engine.Queries.TargetableInPlayFighterQuery",
            "default_data": {},
            "category": "Query"
        },
        "TrickQuery": {
            "type": "PvZCards.Engine.Queries.TrickQuery",
            "default_data": {},
            "category": "Query"
        },
        "WasInSameLaneAsSelfQuery": {
            "type": "PvZCards.Engine.Queries.WasInSameLaneAsSelfQuery",
            "default_data": {},
            "category": "Query"
        },
        "WillTriggerEffectsQuery": {
            "type": "PvZCards.Engine.Queries.WillTriggerEffectsQuery",
            "default_data": {},
            "category": "Query"
        },
        "WillTriggerOnDeathEffectsQuery": {
            "type": "PvZCards.Engine.Queries.WillTriggerOnDeathEffectsQuery",
            "default_data": {},
            "category": "Query"
        },
    
        // ---------- 单参数 ----------
        "AdjacentLaneQuery": {
            "type": "PvZCards.Engine.Queries.AdjacentLaneQuery",
            "default_data": {"Side": "Either", "OriginEntityType": "Self"},
            "editable_params": {
                "Side": {"type": "enum", "options": ["Either", "ToTheLeft", "ToTheRight"]},
                "OriginEntityType": {"type": "enum", "options": ["Self", "Source", "Target"]}
            },
            "category": "Query"
        },
        "CardGuidQuery": {
            "type": "PvZCards.Engine.Queries.CardGuidQuery",
            "default_data": {"Guid": 0},
            "editable_params": {"Guid": {"type": "int", "min": 0, "max": 2147483647}},
            "category": "Query"
        },
        "InAdjacentLaneQuery": {
            "type": "PvZCards.Engine.Queries.InAdjacentLaneQuery",
            "default_data": {"Side": "Either"},
            "editable_params": {"Side": {"type": "enum", "options": ["Either", "ToTheLeft", "ToTheRight"]}},
            "category": "Query"
        },
        "InLaneAdjacentToLaneQuery": {
            "type": "PvZCards.Engine.Queries.InLaneAdjacentToLaneQuery",
            "default_data": {"Side": "Either"},
            "editable_params": {"Side": {"type": "enum", "options": ["Either", "ToTheLeft", "ToTheRight"]}},
            "category": "Query"
        },
        "InLaneSameAsLaneQuery": {
            "type": "PvZCards.Engine.Queries.InLaneSameAsLaneQuery",
            "default_data": {},
            "category": "Query"
        },
        "InSameLaneQuery": {
            "type": "PvZCards.Engine.Queries.InSameLaneQuery",
            "default_data": {"OriginEntityType": "Self"},
            "editable_params": {"OriginEntityType": {"type": "enum", "options": ["Self", "Source", "Target"]}},
            "category": "Query"
        },
        "LaneOfIndexQuery": {
            "type": "PvZCards.Engine.Queries.LaneOfIndexQuery",
            "default_data": {"LaneIndex": 0},
            "editable_params": {"LaneIndex": {"type": "int", "min": 0, "max": 2147483647}}, 
            "category": "Query"
        },
        "QueryMultiplier": {
            "type": "PvZCards.Engine.Components.QueryMultiplier",
            "default_data": {
                "Divider": 1
            },
            "editable_params": {
                "Divider": {"type": "int", "min": 1, "max": 2147483647}
            },
            "child_prop": "Query",
            "is_list": false,
            "category": "Query",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "SubsetQuery": {
            "type": "PvZCards.Engine.Queries.SubsetQuery",
            "default_data": {"Subset": ""},
            "editable_params": {"Subset": {"type": "string"}},
            "category": "Query"
        },
        "SubtypeQuery": {
            "type": "PvZCards.Engine.Queries.SubtypeQuery",
            "default_data": {"Subtype": 0},
            "editable_params": {"Subtype": {"type": "int", "min": 0, "max": 2147483647}},
            "category": "Query"
        },
    
        // ---------- 比较运算符 ----------
        "AttackComparisonQuery": {
            "type": "PvZCards.Engine.Queries.AttackComparisonQuery",
            "default_data": {"ComparisonOperator": "LessOrEqual", "AttackValue": 0},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "AttackValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "BlockMeterValueQuery": {
            "type": "PvZCards.Engine.Queries.BlockMeterValueQuery",
            "default_data": {"ComparisonOperator": "GreaterOrEqual", "BlockMeterValue": 10},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "BlockMeterValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "DamageTakenComparisonQuery": {
            "type": "PvZCards.Engine.Queries.DamageTakenComparisonQuery",
            "default_data": {"ComparisonOperator": "GreaterOrEqual", "DamageTakenValue": 1},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "DamageTakenValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "HealthComparisonQuery": {
            "type": "PvZCards.Engine.Queries.HealthComparisonQuery",
            "default_data": {
                "ComparisonOperator": "LessOrEqual",
                "HealthValue": 1
            },
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "HealthValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "SunCostComparisonQuery": {
            "type": "PvZCards.Engine.Queries.SunCostComparisonQuery",
            "default_data": {"ComparisonOperator": "LessOrEqual", "SunCost": 3},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "SunCost": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "SunCostPlusNComparisonQuery": {
            "type": "PvZCards.Engine.Queries.SunCostPlusNComparisonQuery",
            "default_data": {"ComparisonOperator": "Equal", "AdditionalCost": 1},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "AdditionalCost": {"type": "int", "min": -2147483648, "max": 2147483647}
            },
            "category": "Query"
        },
        "SunCounterComparisonQuery": {
            "type": "PvZCards.Engine.Queries.SunCounterComparisonQuery",
            "default_data": {"ComparisonOperator": "GreaterOrEqual", "SunCounterValue": 6},
            "editable_params": {
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]},
                "SunCounterValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Query"
        },
        "TurnCountQuery": {
            "type": "PvZCards.Engine.Queries.TurnCountQuery",
            "default_data": {"TurnCount": 1, "ComparisonOperator": "GreaterOrEqual"},
            "editable_params": {
                "TurnCount": {"type": "int", "min": 0, "max": 2147483647},
                "ComparisonOperator": {"type": "enum", "options": ["LessOrEqual", "Equal", "GreaterOrEqual"]}
            },
            "category": "Query"
        },
    
        // ---------- 组件类型 ----------
        "HasComponentQuery": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": ""},
            "editable_params": {"ComponentType": {"type": "component_picker"}},
            "category": "Query"
        },
        "LacksComponentQuery": {
            "type": "PvZCards.Engine.Queries.LacksComponentQuery",
            "default_data": {
                "ComponentType": "PvZCards.Engine.Components.FaceDown, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"
            },
            "editable_params": {"ComponentType": {"type": "component_picker"}},
            "category": "Query"
        },
        "OnTerrainQuery": {
            "type": "PvZCards.Engine.Queries.OnTerrainQuery",
            "default_data": {
                "TerrainType": "PvZCards.Engine.Components.GrassTerrain"
            },
            "editable_params": {"TerrainType": {"type": "terrain_picker"}},
            "category": "Query"
        },
        "OpenLaneQuery": {
            "type": "PvZCards.Engine.Queries.OpenLaneQuery",
            "default_data": {
                "PlayerFactionType": "PvZCards.Engine.Components.Plants",
                "IsForTeamupCard": false
            },
            "editable_params": {
                "PlayerFactionType": {"type": "enum", "options": ["PvZCards.Engine.Components.Plants, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null", "PvZCards.Engine.Components.Zombies, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"]},
                "IsForTeamupCard": {"type": "bool"}
            },
            "category": "Query"
        },
    
        // ---------- 预定义快捷方式 ----------
        "HasZombiesComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Zombies, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasPlantsComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Plants, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasPlayerComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Player, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasLaneComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Lane, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasFaceDownComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.FaceDown, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasEnvironmentComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Environment, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasWaterTerrainComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.WaterTerrain, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasHighgroundTerrainComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.HighgroundTerrain, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasUnhealableComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Unhealable, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
        "HasSuperpowerComponent": {
            "type": "PvZCards.Engine.Queries.HasComponentQuery",
            "default_data": {"ComponentType": "PvZCards.Engine.Components.Superpower, EngineLib, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"},
            "category": "Query"
        },
    
        // ==================== Effect 效果 ====================
        "CopyStatsEffect": {
            "type": "PvZCards.Engine.Components.CopyStatsEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "DestroyCardEffect": {
            "type": "PvZCards.Engine.Components.DestroyCardEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "ExtraAttackEffect": {
            "type": "PvZCards.Engine.Components.ExtraAttackEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "MixedUpGravediggerEffectDescriptor": {
            "type": "PvZCards.Engine.Components.MixedUpGravediggerEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "MoveCardToLanesEffectDescriptor": {
            "type": "PvZCards.Engine.Components.MoveCardToLanesEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "ReturnToHandEffect": {
            "type": "PvZCards.Engine.Components.ReturnToHandFromPlayEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "SlowEffect": {
            "type": "PvZCards.Engine.Components.SlowEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
        "TurnIntoGravestoneEffectDescriptor": {
            "type": "PvZCards.Engine.Components.TurnIntoGravestoneEffectDescriptor",
            "default_data": {},
            "category": "Effect"
        },
    
        // ---------- 有参数（基础类型）----------
        "AttackInLaneEffectDescriptor": {
            "type": "PvZCards.Engine.Components.AttackInLaneEffectDescriptor",
            "default_data": {
                "DamageAmount": 4
            },
            "editable_params": {
                "DamageAmount": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Effect"
        },
        "BuffEffect": {
            "type": "PvZCards.Engine.Components.BuffEffectDescriptor",
            "default_data": {"AttackAmount": 1, "HealthAmount": 1, "BuffDuration": "Permanent"},
            "editable_params": {
                "AttackAmount": {"type": "int", "min": -2147483648, "max": 2147483647},
                "HealthAmount": {"type": "int", "min": -2147483648, "max": 2147483647},
                "BuffDuration": {"type": "enum", "options": ["Permanent", "EndOfTurn", "NextFighter"]}
            },
            "category": "Effect"
        },
        "ChargeBlockMeterEffectDescriptor": {
            "type": "PvZCards.Engine.Components.ChargeBlockMeterEffectDescriptor",
            "default_data": {
                "ChargeAmount": 10
            },
            "editable_params": {
                "ChargeAmount": {"type": "int", "min": -2147483648, "max": 2147483647}
            },
            "category": "Effect"
        },
        "CopyCardEffectDescriptor": {
            "type": "PvZCards.Engine.Components.CopyCardEffectDescriptor",
            "default_data": {
                "GrantTeamup": false,
                "ForceFaceDown": false,
                "CreateInFront": false
            },
            "editable_params": {
                "GrantTeamup": {"type": "bool"},
                "ForceFaceDown": {"type": "bool"},
                "CreateInFront": {"type": "bool"}
            },
            "category": "Effect"
        },
        "CreateCardEffect": {
            "type": "PvZCards.Engine.Components.CreateCardEffectDescriptor",
            "default_data": {"CardGuid": 0, "ForceFaceDown": false},
            "editable_params": {
                "CardGuid": {"type": "int", "min": 0, "max": 2147483647},
                "ForceFaceDown": {"type": "bool"}
            },
            "category": "Effect"
        },
        "CreateCardInDeckEffect": {
            "type": "PvZCards.Engine.Components.CreateCardInDeckEffectDescriptor",
            "default_data": {"CardGuid": 0, "AmountToCreate": 1, "DeckPosition": "Random"},
            "editable_params": {
                "CardGuid": {"type": "int", "min": 0, "max": 2147483647},
                "AmountToCreate": {"type": "int", "min": 1, "max": 2147483647},
                "DeckPosition": {"type": "enum", "options": ["Random", "Top", "Bottom"]}
            },
            "category": "Effect"
        },
        "DamageEffect": {
            "type": "PvZCards.Engine.Components.DamageEffectDescriptor",
            "default_data": {"DamageAmount": 4},
            "editable_params": {"DamageAmount": {"type": "int", "min": 0, "max": 2147483647}},
            "category": "Effect"
        },
        "DrawCardEffect": {
            "type": "PvZCards.Engine.Components.DrawCardEffectDescriptor",
            "default_data": {"DrawAmount": 1},
            "editable_params": {"DrawAmount": {"type": "int", "min": 1, "max": 2147483647}},
            "category": "Effect"
        },
        "EffectValueDescriptor": {
            "type": "PvZCards.Engine.Components.EffectValueDescriptor",
            "default_data": {
                "MappingType": "DamageToHeal"
            },
            "editable_params": {
                "MappingType": {
                    "type": "enum",
                    "options": [
                        "DamageToHeal",
                        "HealToDamage"
                    ]
                }
            },
            "category": "Effect"
        },
        "GainSunEffect": {
            "type": "PvZCards.Engine.Components.GainSunEffectDescriptor",
            "default_data": {"Amount": 1, "Duration": "Permanent", "ActivationTime": "Immediate"},
            "editable_params": {
                "Amount": {"type": "int", "min": -2147483648, "max": 2147483647},
                "Duration": {"type": "enum", "options": ["Permanent", "EndOfTurn", "NextFighter"]},
                "ActivationTime": {"type": "enum", "options": ["Immediate", "NextTurn"]}
            },
            "category": "Effect"
        },
        "GrantAbilityEffect": {
            "type": "PvZCards.Engine.Components.GrantAbilityEffectDescriptor",
            "default_data": {
                "GrantableAbilityType": "Frenzy",
                "Duration": "Permanent",
                "AbilityValue": 0
            },
            "editable_params": {
                "GrantableAbilityType": {
                    "type": "enum",
                    "options": [
                        "Unhurtable", "Deadly", "Frenzy", "Truestrike",
                        "Strikethrough", "MinHealth", "NoExtraAttacks",
                        "GravestoneSpy", "Teamup", "Aquatic", "CanPlayFighterInSurprisePhase",
                        "Mustache", "AttackOverride", "MultiplyDamage", "Graveyard",
                        "Untrickable", "Unhealable"
                    ]
                },
                "Duration": {"type": "enum", "options": ["Permanent", "EndOfTurn", "NextFighter"]},
                "AbilityValue": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Effect"
        },
        "GrantTriggeredAbilityEffectDescriptor": {
            "type": "PvZCards.Engine.Effects.GrantTriggeredAbilityEffectDescriptor",
            "default_data": {
                "AbilityGuid": 562,
                "AbilityValueType": "None",
                "AbilityValueAmount": 0
            },
            "editable_params": {
                "AbilityGuid": {"type": "int", "min": 0, "max": 2147483647},
                "AbilityValueType": {"type": "enum", "options": ["None", "Damage"]},
                "AbilityValueAmount": {"type": "int", "min": 0, "max": 2147483647}
            },
            "category": "Effect"
        },
        "HealEffect": {
            "type": "PvZCards.Engine.Components.HealEffectDescriptor",
            "default_data": {"HealAmount": 2},
            "editable_params": {"HealAmount": {"type": "int", "min": 1, "max": 2147483647}},
            "category": "Effect"
        },
        "HeroHealthMultiplier": {
            "type": "PvZCards.Engine.Components.HeroHealthMultiplier",
            "default_data": {
                "Faction": "Plants",
                "Divider": 1
            },
            "editable_params": {
                "Faction": {"type": "enum", "options": ["Plants", "Zombies"]},
                "Divider": {"type": "int", "min": 1, "max": 2147483647}
            },
            "category": "Effect"
        },
        "ModifySunCostEffect": {
            "type": "PvZCards.Engine.Components.ModifySunCostEffectDescriptor",
            "default_data": {"SunCostAmount": -1, "BuffDuration": "Permanent"},
            "editable_params": {
                "SunCostAmount": {"type": "int", "min": -2147483648, "max": 2147483647},
                "BuffDuration": {"type": "enum", "options": ["Permanent", "EndOfTurn", "NextFighter"]}
            },
            "category": "Effect"
        },
        "SetStatEffect": {
            "type": "PvZCards.Engine.Components.SetStatEffectDescriptor",
            "default_data": {
                "StatType": "Health",
                "Value": 20,
                "ModifyOperation": "Set",
                "StripNoncontinousModifiers": true
            },
            "editable_params": {
                "StatType": {"type": "enum", "options": ["Attack", "Health", "SunCost"]},
                "ModifyOperation": {"type": "enum", "options": ["Set", "Add"]},
                "Value": {"type": "int", "min": -2147483648, "max": 2147483647},
                "StripNoncontinousModifiers": {"type": "bool"}
            },
            "category": "Effect"
        },
        "SunGainedMultiplier": {
            "type": "PvZCards.Engine.Components.SunGainedMultiplier",
            "default_data": {
                "Faction": "Plants",
                "Divider": 1
            },
            "editable_params": {
                "Faction": {"type": "enum", "options": ["Plants", "Zombies"]},
                "Divider": {"type": "int", "min": 1, "max": 2147483647}
            },
            "category": "Effect"
        },
        "TargetAttackMultiplier": {
            "type": "PvZCards.Engine.Components.TargetAttackMultiplier",
            "default_data": {"Divider": 2},
            "editable_params": {"Divider": {"type": "int", "min": 1, "max": 2147483647}},
            "category": "Effect"
        },
        "TargetHealthMultiplier": {
            "type": "PvZCards.Engine.Components.TargetHealthMultiplier",
            "default_data": {"Divider": 2},
            "editable_params": {"Divider": {"type": "int", "min": 1, "max": 2147483647}},
            "category": "Effect"
        },
    
        // ---------- 有子节点 ----------
        "CreateCardFromSubsetEffectDescriptor": {
            "type": "PvZCards.Engine.Components.CreateCardFromSubsetEffectDescriptor",
            "default_data": {
                "ForceFaceDown": false
            },
            "editable_params": {
                "ForceFaceDown": {"type": "bool"}
            },
            "child_prop": "SubsetQuery",
            "is_list": false,
            "category": "ComplexEffect",
            "allowed_children": ["CompositeQuery", "Query"]
        },
        "TransformIntoCardFromSubsetEffectDescriptor": {
            "type": "PvZCards.Engine.Components.TransformIntoCardFromSubsetEffectDescriptor",
            "default_data": {},
            "child_prop": "SubsetQuery",
            "is_list": false,
            "category": "ComplexEffect",
            "allowed_children": ["CompositeQuery", "Query"]
        },
    
        // ==================== ComplexEffect 复合效果 ====================
        "DrawCardFromSubsetEffect": {
            "type": "PvZCards.Engine.Components.DrawCardFromSubsetEffectDescriptor",
            "default_data": {"DrawAmount": 1},
            "editable_params": {"DrawAmount": {"type": "int", "min": 1, "max": 2147483647}},
            "child_prop": "SubsetQuery",
            "is_list": false,
            "category": "ComplexEffect",
            "allowed_children": ["CompositeQuery", "Query"]
        },
    
        // ==================== Virtual 虚拟/UI辅助 ====================
        "AdditionalTargetQuery": {
            "type": "Virtual.UI.AdditionalTargetQuery",
            "default_data": {},
            "category": "Virtual",
            "allowed_children": ["CompositeQuery", "Query"]
        },
    },

    // ==================== 辅助工具函数 ====================
    getNodeName(key) {
        return this.NODE_NAMES[key] || key;
    },

    getParamName(key) {
        return this.PARAM_NAMES[key] || key;
    }
};
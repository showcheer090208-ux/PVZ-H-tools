// static/js/logic_adapter.js
// 对应原项目的 panel_main.py 中的 LogicNodeAdapter 核心逻辑
// 负责在“前端可视化树状数据”和“Unity底层嵌套 JSON”之间互相转换

const LogicAdapter = {
    /**
     * 将前端的单个 Vue 树节点，编译为 Unity 底层的 Component/Query JSON
     * @param {Object} treeNode - 前端树节点，格式如 { id: "DamageEffect", params: {Amount: 2}, children: [...] }
     * @returns {Object|null} - 返回符合 UnityPy 封包格式的 JSON 对象
     */
    buildEngineJson(treeNode) {
        if (!treeNode || !treeNode.id) return null;
        
        const nodeDef = PhantomConfig.NODE_DEF[treeNode.id];
        if (!nodeDef) {
            console.warn(`未知的节点 ID: ${treeNode.id}`);
            return null;
        }

        // 1. 构建基础骨架
        // 深度合并默认参数和用户编辑的参数
        const dataBody = Object.assign({}, nodeDef.default_data, treeNode.params || {});
        
        let result = {
            $type: nodeDef.type,
            $data: dataBody
        };

        // 2. 递归处理子节点 (嵌套)
        if (nodeDef.child_prop && treeNode.children && treeNode.children.length > 0) {
            if (nodeDef.is_list) {
                // 如果子节点是一个列表 (例如 CompositeAllQuery 的 queries)
                result.$data[nodeDef.child_prop] = treeNode.children
                    .map(child => this.buildEngineJson(child))
                    .filter(childJson => childJson !== null); // 过滤掉解析失败的空节点
            } else {
                // 如果子节点是单对象 (例如 DamageEffect 的 Target)
                // 仅取第一个合法子节点
                result.$data[nodeDef.child_prop] = this.buildEngineJson(treeNode.children[0]);
            }
        }

        return result;
    },

    /**
     * 将整个前端逻辑数组（例如触发器数组），打包为最终发给后端的 JSON
     * @param {Array} treeNodes - 前端大纲中的所有根节点
     * @returns {Array} - 最终引擎认识的字典列表
     */
    buildAll(treeNodes) {
        if (!treeNodes || !Array.isArray(treeNodes)) return [];
        return treeNodes
            .map(node => this.buildEngineJson(node))
            .filter(json => json !== null);
    }, // <--- 就是补上了这个极其关键的逗号！

    /**
     * 【选项 A：反向解析引擎】
     * 将 Unity 底层的深层 JSON 数组，逆向还原为 Vue 前端能看懂的树状结构
     */
    parseUnityNode(unityObj) {
        if (!unityObj || !unityObj.$type) return null;
        const fullType = unityObj.$type;
        const data = unityObj.$data || {};

        let nodeId = null;
        // 遍历配置库，通过匹配 $type 找回节点 ID
        for (const [nid, def] of Object.entries(PhantomConfig.NODE_DEF)) {
            if (fullType.includes(def.type)) {
                // 处理高度重复的组件查询 (比如都是 HasComponentQuery)
                if (fullType.includes("HasComponentQuery") || fullType.includes("LacksComponentQuery") || fullType.includes("OnTerrainQuery") || fullType.includes("OpenLaneQuery")) {
                    if ((def.default_data.ComponentType && def.default_data.ComponentType === data.ComponentType) || 
                        (def.default_data.TerrainType && def.default_data.TerrainType === data.TerrainType) ||
                        (def.default_data.PlayerFactionType && def.default_data.PlayerFactionType === data.PlayerFactionType)) {
                        nodeId = nid;
                        break;
                    }
                } else {
                    nodeId = nid;
                    break;
                }
            }
        }

        if (!nodeId) {
            console.warn(`[反向解析警告] 无法识别的 Unity 类型: ${fullType}`);
            return null;
        }

        const def = PhantomConfig.NODE_DEF[nodeId];
        const node = {
            _uuid: PhantomUtils.generateUUID(),
            id: nodeId,
            params: {},
            children: []
        };

        // 还原参数
        if (def.editable_params) {
            for (const key in def.editable_params) {
                if (data[key] !== undefined) {
                    node.params[key] = data[key];
                } else if (def.default_data && def.default_data[key] !== undefined) {
                    node.params[key] = def.default_data[key];
                }
            }
        }

        // 还原嵌套子节点
        if (def.child_prop && data[def.child_prop]) {
            const rawChildren = data[def.child_prop];
            if (def.is_list && Array.isArray(rawChildren)) {
                node.children = rawChildren.map(c => this.parseUnityNode(c)).filter(Boolean);
            } else {
                const parsedChild = this.parseUnityNode(rawChildren);
                if (parsedChild) node.children.push(parsedChild);
            }
        }

        return node;
    },

    engineJsonToTree(jsonArray) {
        if (!Array.isArray(jsonArray)) return [];
        return jsonArray.map(obj => this.parseUnityNode(obj)).filter(Boolean);
    }
};
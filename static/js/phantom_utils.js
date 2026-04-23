// static/js/phantom_utils.js
// 对应原项目的 core_utils.py 和部分通用工具

const PhantomUtils = {
    /**
     * 深层字典的安全提取器 (等同于 core_utils.py 里的 safe_get)
     * 用法: PhantomUtils.safeGet(data, 'Counters', 0, 'Value', 1)
     * @param {Object} obj - 目标对象
     * @param {...(string|number)} keys - 属性路径
     * @param {*} defaultVal - 默认值 (放在最后一个参数)
     * @returns {*}
     */
    safeGet(obj, ...args) {
        let defaultVal = null;
        let keys = args;
        
        // 最后一个参数作为默认值（如果有传的话）
        if (args.length > 0 && typeof args[args.length - 1] !== 'string' && typeof args[args.length - 1] !== 'number') {
            defaultVal = args.pop();
            keys = args;
        }

        let val = obj;
        for (const key of keys) {
            if (val === null || val === undefined) return defaultVal;
            val = val[key];
        }
        return val !== undefined && val !== null ? val : defaultVal;
    },

// 修改 static/js/phantom_utils.js 中的 generateUUID 方法
    /**
     * 生成安全的 UUID (兼容非 HTTPS 环境)
     * @returns {string}
     */
    generateUUID() {
        // 1. 如果环境支持原生方法，首选原生 (速度最快)
        if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
            return crypto.randomUUID();
        }
        
        // 2. 降级方案：使用随机数和时间戳拼接 (兼容所有环境)
        console.warn("[PhantomEngine] 当前环境不支持 crypto.randomUUID，已切换为降级生成算法。");
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    /**
     * 深度克隆对象 (用于参数和节点的独立拷贝)
     */
    deepClone(obj) {
        if (!obj) return obj;
        return JSON.parse(JSON.stringify(obj));
    }
};
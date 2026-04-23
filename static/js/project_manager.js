// static/js/project_manager.js
// 对应原项目的 project_manager.py
// 负责在浏览器本地内存 (localStorage) 中管理用户的 Mod 工程

class ProjectManager {
    constructor() {
        this.currentProjectName = null;
        // 结构: { "GUID(str)": {card_data_dict} }
        this.projectCards = {}; 
        
        // 初始化时自动加载上次打开的工程
        this.autoLoadLastProject();
    }

    /**
     * 自动加载最后一次打开的工程
     */
    autoLoadLastProject() {
        const lastProj = localStorage.getItem('PhantomEngine_LastProject');
        if (lastProj) {
            this.loadProject(lastProj);
        }
    }

    /**
     * 获取所有本地保存的工程名称
     * @returns {string[]} 工程名称列表
     */
    getAllProjects() {
        const projectsStr = localStorage.getItem('PhantomEngine_ProjectsList');
        return projectsStr ? JSON.parse(projectsStr) : [];
    }

    /**
     * 新建一个空白工程
     * @param {string} name 工程名称
     */
    createProject(name) {
        this.currentProjectName = name;
        this.projectCards = {};
        this.saveCurrentProject();

        // 更新工程列表
        const allProjects = this.getAllProjects();
        if (!allProjects.includes(name)) {
            allProjects.push(name);
            localStorage.setItem('PhantomEngine_ProjectsList', JSON.stringify(allProjects));
        }
    }

    /**
     * 读取指定名称的工程
     * @param {string} name 工程名称
     * @returns {boolean} 是否成功
     */
    loadProject(name) {
        const dataStr = localStorage.getItem(`PhantomProject_${name}`);
        if (dataStr) {
            try {
                this.projectCards = JSON.parse(dataStr);
                this.currentProjectName = name;
                localStorage.setItem('PhantomEngine_LastProject', name);
                return true;
            } catch (e) {
                console.error("读取工程失败，数据可能已损坏:", e);
                return false;
            }
        }
        return false;
    }

    /**
     * 将内存中的工程数据保存到浏览器本地
     */
    saveCurrentProject() {
        if (!this.currentProjectName) return false;
        try {
            localStorage.setItem(`PhantomProject_${this.currentProjectName}`, JSON.stringify(this.projectCards));
            return true;
        } catch (e) {
            console.error("保存工程失败:", e);
            return false;
        }
    }

    /**
     * 从工作台把卡牌保存进工程清单
     * @param {Object} cardModel 当前正在编辑的卡牌实例
     */
    addOrUpdateCard(cardModel) {
        if (!this.currentProjectName) return false;
        
        // 调用 CardModel 的序列化方法获取纯净的 JSON 字典
        const cardDict = cardModel.generateJsonDict();
        const guidStr = String(cardModel.guid);
        
        // 更新到内存
        this.projectCards[guidStr] = cardDict;
        
        // 落盘保存
        this.saveCurrentProject();
        return true;
    }
}
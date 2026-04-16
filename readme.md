这份 `README.md` 见证了我们的工坊从一个简单的脚本演变成了一个真正具备工程化、现代化 UI 以及基础安全防御体系的 Web 应用。

我把我们最近加入的**智能 JSON 格式化、移动端压缩包寻路适配、全站速率限制（防 CC 攻击）、动态数据驱动大厅、以及社区论坛**等核心更新全都整合进去了。

你可以直接复制以下完整的 Markdown 内容来覆盖你的 `readme.md` 文件：

```markdown
# PVZH 云端工坊 (PVZH Cloud Workshop)

本项目是一个基于 Flask + Vue 3 + UnityPy 开发的《植物大战僵尸：英雄》(PVZH) 资源魔改与社区平台。它实现了卡组的可视化编辑、云端母包自动合成、通用 Unity 资源处理、动态数据展示以及社区论坛等功能。

## 📂 项目文件结构

```text
PVZH_Project/
├── app.py                 # 程序入口：负责蓝图注册、中间件配置、全局用户上下文(Context Processor)及服务启动
├── config.py              # 配置中心：通过环境变量管理 Supabase 密钥与上传限制
├── database.py            # 数据库模块：封装了与 Supabase (PostgreSQL) 的交互逻辑
├── extensions.py          # 安全扩展：配置 Flask-Limiter 全局速率限制器，抵御恶意 CC 攻击
├── logic_data.py          # 数据逻辑：解析 TXT 名单，构建内存卡牌与卡组树数据库
├── logic_unity.py         # 【业务定制层】卡组工坊核心：封装 UnityPy，专用于母体底包的内存级定向解析与写入
├── requirements.txt       # 依赖清单：项目运行所需的 Python 第三方库列表
├── .gitignore             # Git 忽略：排除缓存、本地变量及超大原始 Bundle 文件
├── blueprints/            # 后端模块蓝图 (Controllers)
│   ├── auth.py            # 【核心】安全认证：基于 Supabase Auth 的注册/登录、JWT 鉴权、以及管理员路由拦截
│   ├── deck_editor.py     # 卡组编辑器接口：负责初始化数据推送与一键云端打包
│   ├── unity.py           # 资源管理接口：提供泛用的 Bundle 全量解包、JSON 智能展开与定向回填
│   ├── forum.py           # 社区接口：V3 版论坛引擎，支持外键连表查询、分区过滤与异步 API
│   └── home.py            # 导航接口：负责首页 Dashboard 路由及动态新闻数据加载
├── templates/             # 前端 HTML 模板 (Jinja2 + Vue 3 + Tailwind CSS)
│   ├── base.html          # 母版页：定义全局响应式导航、移动端底部 Bottom Nav 及用户状态入口
│   ├── index.html         # 网站大厅：非对称 Dashboard 布局，动态展示工具矩阵与更新日志
│   ├── profile.html       # 个人中心：用户荣誉勋章展示与唯一昵称 (查重) 修改台
│   ├── deck_editor.html   # 卡组工坊：Vue 3 编写的可视化编辑器 (适配移动端 Flex 沉底导航)
│   ├── tab_unity.html     # 资源管理：单文件解包/打包的双列操作引擎 (Fetch 异步防卡死)
│   ├── tab_forum.html     # 社区大厅：双栏响应式布局，支持动态分区切换与无刷新发帖
│   ├── tab_post_detail.html # 帖子详情：沉浸式阅读与带有自动 @ 交互的“楼中楼”回复系统
│   └── error.html         # 错误页：统一的异常反馈界面
└── data/                  # 核心数据资源 (重要)
    ├── uuid.txt           # 卡牌库索引：记录卡牌名称与对应的 Guid 映射
    ├── 笔记卡组名称.txt     # 卡组树定义：定义英雄分类及其卡组对应的英文 ID
    ├── news.json          # 【新增】动态数据源：驱动大厅的置顶公告与时间轴更新日志
    ├── recipe_decks_1     # 原始底包 A (母体文件)
    └── recipe_definitions_1 # 原始底包 B (母体文件)
```

🛠️ 核心功能模块说明
1. 现代化实名社区系统 (Forum V3 & Auth)
经过 V3 版本的底层重构，社区已彻底告别匿名时代，具备了商业级的交互与安全标准：

Supabase 强身份绑定：集成 Supabase Auth 系统，用户的业务资料 (profiles 表) 与底层认证 UUID 深度绑定，并实现了后端的全局 JWT Cookie 拦截，彻底杜绝身份伪造。

贴吧式分区与楼中楼：引入 categories 和 post_comments 的邻接表设计。支持板块动态切换过滤；详情页支持多层级“楼中楼”嵌套回复与精准艾特 (@)。

荣誉与权限系统：内置基于后端的 @admin_required 权限校验，支持管理员无刷新删帖；拥有自定义的“荣誉勋章”系统，为优质创作者发放带有 Material Icons 的高亮专属头衔。

面向未来的存储架构：数据库层面已为所有帖子和回复预留了 image_urls 数组字段，为后续无缝接入 Cloudflare R2 对象存储（免下行流量费图床）打下了完美地基。

2. 云端卡组工坊 (Deck Editor)
高度特化：专为 PVZH 卡组结构设计，直接操作 Cards.CardEntries 节点。

免传底包：通过服务器内置的 recipe 母包，在内存中完成增量修改，极大降低了用户的操作门槛和带宽消耗。

移动端优化：彻底重构的沉底操作栏与 Flex 布局，完美适配刘海屏与安全距离，告别设备遮挡问题。

3. 资源管理中心 (Unity Tools)
绝对通用：不局限于特定游戏，支持任意标准 Unity Bundle 的解析。

智能 JSON 格式化：独创 transform_json_tree 算法，在解包时自动识别并展开 m_Script 中晦涩的嵌套 JSON 字符串为多层级目录；并在打包时自动压缩回流行格式。

深度寻路回填：无视用户压缩软件的习惯（如嵌套文件夹），后端算法自动遍历寻找 _index.json 并智能计算前缀路径，实现 100% 精准匹配覆盖。

4. 稳固的安全防御体系 (Anti-Abuse)
API 速率限制：核心的超大内存消耗接口（如解包/打包）均挂载了 Flask-Limiter 防护，以 memory:// 机制限制单 IP 请求频率，从物理层面断绝了恶意脚本引发的 OOM 及 CC 攻击。

数据驱动视图：公告与更新日志与 HTML 彻底解耦，通过修改 news.json 即可实现全站内容的秒级动态更新。

优雅的异步交互：全面采用 Vue 3 数据绑定与 Fetch API，所有核心增删改操作（发帖、删帖、改名）均实现局部无刷新，网络中断亦能平滑处理异常。

Deployed on Render | Powered by UnityPy & Flask & Vue.js & Supabase
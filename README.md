# 植物养护社群平台

基于基础标签重合度匹配的植物养护社群平台，采用 Python+Django+Vue 技术栈开发。

## 项目简介

本平台是一个轻量化、实用且用户友好的植物养护社群平台，满足普通用户便捷获取养护知识、养护达人高效分享经验的核心需求。

### 核心功能

- **用户管理**：支持管理员、养护达人、普通用户三种角色
- **植物百科**：丰富的植物养护知识库
- **社区交流**：话题圈动态发布与互动
- **问答系统**：养护问题提问与解答
- **智能匹配**：基于标签重合度的用户匹配推荐
- **内容审核**：人工审核与关键词过滤相结合

## 技术栈

### 后端
- Python 3.10+
- Django 4.2（ORM、用户认证、基础视图函数）
- Django REST Framework
- MySQL / SQLite（开发环境使用SQLite）
- JWT认证

### 前端
- Vue.js 3
- Element UI (Element Plus)
- Vue Router
- Pinia（状态管理）
- Axios

## 项目结构

```
plant_community/
├── backend/                 # 后端项目
│   ├── apps/               # 应用模块
│   │   ├── users/          # 用户管理
│   │   ├── plants/         # 植物百科
│   │   ├── community/      # 社区模块
│   │   ├── matching/       # 匹配推荐
│   │   └── analytics/      # 数据分析
│   ├── config/             # 项目配置
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # 前端项目（Vue.js + Element UI）
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 初始化数据
python manage.py init_plant_data
python manage.py init_users

# 启动服务
python manage.py runserver
```

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问系统

- 前端地址：http://localhost:3000
- 后端API：http://localhost:8000/api/
- 管理后台：http://localhost:8000/admin/

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123456 |
| 养护达人 | expert_succulent | expert123456 |
| 养护达人 | expert_foliage | expert123456 |
| 普通用户 | plant_lover1 | user123456 |
| 普通用户 | green_thumb | user123456 |

## 核心功能说明

### 基础标签重合度匹配算法

系统采用"基础标签重合度匹配"方案，逻辑清晰且便于落地：

1. **核心标签提取**：提取用户3-5个核心标签
   - 植物类型（如多肉、月季、绿萝等）
   - 养护经验等级（新手、进阶、资深等）
   - 所在地区（华北、华东、华南等）
   - 养护环境（室内、阳台、庭院等）

2. **匹配计算**：通过标签重合数量与优先级排序
   - 植物类型优先
   - 地区标签次之
   - 养护经验等级补充

3. **匹配类型**：
   - 需求用户 - 同好用户匹配
   - 需求用户 - 养护达人匹配

### 标签体系

用户标签分为四类：
- **植物类型**：多肉植物、观叶植物、开花植物等
- **养护环境**：室内、阳台、庭院、办公室等
- **兴趣方向**：多肉造景、阳台花园、品种收集等
- **常见问题**：黄叶问题、浇水问题、病虫害等

### 角色权限

| 功能 | 管理员 | 养护达人 | 普通用户 |
|------|--------|----------|----------|
| 帖子审核 | ✓ | × | × |
| 达人认证审核 | ✓ | × | × |
| 发布帖子 | ✓ | ✓ | ✓ |
| 回答问题 | ✓ | ✓ | ✓ |
| 申请达人认证 | × | × | ✓ |
| 数据统计 | ✓ | × | × |

## API文档

主要API端点：

- `POST /api/token/` - 获取JWT令牌
- `GET /api/users/me/` - 获取当前用户信息
- `GET /api/plants/` - 植物列表
- `GET /api/community/posts/` - 帖子列表
- `GET /api/community/questions/` - 问题列表
- `GET /api/matching/find/find_experts/` - 匹配养护达人
- `GET /api/matching/find/find_peers/` - 匹配同好用户
- `GET /api/analytics/overview/` - 数据概览（管理员）

## 性能指标

根据开题报告要求，系统满足以下性能指标：

- 前端页面加载时间 ≤ 3秒
- 核心操作响应时间 ≤ 1秒
- 支持300+用户同时在线
- 数据库支持1万级用户数据

## 开发说明

### 添加新的植物数据

编辑 `backend/apps/plants/management/commands/init_plant_data.py`，在 `plants_data` 列表中添加新的植物信息。

### 调整匹配算法权重

编辑 `backend/apps/matching/algorithm.py` 中的 `DEFAULT_WEIGHTS` 和相关参数。

## License

MIT License

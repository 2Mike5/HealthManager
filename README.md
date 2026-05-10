# Health Manager 健康管理

基于 uni-app (Vue 3) + Flask 的跨平台个人健康管理应用，支持 Android / iOS / H5。

## 功能概览

### 健康看板
- **步数环形图** — 日/周/月视图，目标 10000 步达标显示
- **心率折线图** — 最低/平均/最高三条曲线
- **睡眠热力图** — 月历格式，颜色标识睡眠质量
- **健康评分雷达图** — 步数、心率、睡眠、饮水、运动、情绪六维评分
- 支持后端数据与本地 Mock 数据自动切换

### 记一记 — 每日数据录入
- **基础指标** — 步数、心率（最低/平均/最高）、睡眠、饮水、情绪
- **运动记录** — 选择运动类型（跑步/骑行/瑜伽/游泳/力量训练/篮球/足球等）+ 时长
- **体重记录** — 体重 + 体脂率，自动计算 BMI
- **饮食记录** — 添加多餐食物，支持食物库搜索自动填充营养数据

### AI 健康助手
- 自然语言查询健康数据（"今天步数多少"、"近7天心率趋势"）
- 智能图表生成（折线图、柱状图、饼图、环形图、玫瑰图、雷达图、面积图）
- 多轮对话记忆，支持连续追问
- 支持 LLM（通义千问 / DeepSeek）与规则引擎双模式

### 数据分析
- **体重趋势** — 折线图 + BMI 分类 + 目标体重进度
- **饮食分析** — 每日热量汇总 + 三大营养素环图 + 按餐次分类
- **运动统计** — 本周运动时长/天数/最常见类型

### 用户系统
- JWT 用户注册 / 登录 / 个人信息管理
- API 认证保护

### 暗黑模式
- 全局暗黑主题切换，所有页面适配

## 技术栈

| 层 | 技术 |
|------|------|
| 前端框架 | uni-app (Vue 3, Options API) |
| UI 组件 | uni-ui 组件库 + qiun-data-charts (uCharts) |
| 图表库 | uCharts / ECharts (line, column, pie, ring, rose, radar, area) |
| 后端 | Flask (Python 3) |
| 数据库 | SQLite |
| 认证 | JWT (PyJWT) |
| AI | 通义千问 DashScope API (OpenAI 兼容) / 规则引擎降级 |
| CSS | SCSS, Glassmorphism 设计, CSS 变量暗黑模式 |

## 项目结构

```
HealthManager/
├── pages/
│   ├── dashboard/index.vue    # 健康看板
│   ├── record/index.vue       # 记一记 - 数据录入
│   ├── ai/index.vue           # AI 健康助手
│   └── profile/
│       ├── index.vue          # 我的 - 个人中心
│       ├── weight.vue         # 体重追踪
│       ├── diet.vue           # 饮食记录
│       └── exercise.vue       # 运动历史
├── pages/login/index.vue      # 登录
├── pages/register/index.vue   # 注册
├── server/
│   ├── app.py                 # Flask 入口
│   ├── models.py              # 数据库模型
│   ├── auth.py                # JWT 认证
│   ├── routes.py              # 健康记录 CRUD
│   ├── routes_weight.py       # 体重 API
│   ├── routes_diet.py         # 饮食 API + 食物库
│   ├── ai_service.py          # AI 问答引擎
│   ├── llm_service.py         # LLM 集成
│   ├── food_seed_data.py      # 80+ 常见食物营养数据
│   └── config.py              # API Key 配置（已 gitignore）
├── utils/
│   ├── api.js                 # API 客户端
│   └── mock.js                # Mock 数据生成
├── styles/
│   ├── variables.scss         # 设计令牌
│   └── animations.scss        # 动画
├── App.vue                    # 应用入口 + 暗黑模式 CSS
├── pages.json                 # 路由 / TabBar 配置
└── manifest.json              # uni-app 打包配置
```

## 快速开始

### 1. 启动后端

```bash
cd server
pip install -r requirements.txt
python app.py
```

后端运行在 `http://localhost:5001`。

### 2. 配置 AI（可选）

```bash
cp config.example.py config.py
# 编辑 config.py 填入你的 API Key
```

支持通义千问 DashScope 或任何 OpenAI 兼容 API。不配置则使用规则引擎降级。

### 3. 启动前端

用 HBuilderX 打开项目根目录，运行到浏览器 / 模拟器即可。

也可直接编译为 H5：

```bash
npm install -g @dcloudio/uni-cli  # 如未安装
npm run dev:h5
```

## API 概览

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/register` | POST | - | 用户注册 |
| `/api/auth/login` | POST | - | 用户登录 |
| `/api/auth/profile` | GET/PUT | 需要 | 个人信息 |
| `/api/records` | GET/POST | 需要 | 健康记录 CRUD (upsert) |
| `/api/records/<id>` | GET/PUT/DELETE | 需要 | 单条记录操作 |
| `/api/weight` | GET/POST | 需要 | 体重记录 |
| `/api/weight/latest` | GET | 需要 | 最新体重含 BMI |
| `/api/diet/records` | GET/POST | 需要 | 饮食记录 |
| `/api/diet/summary` | GET | 需要 | 每日饮食汇总 |
| `/api/foods` | GET | - | 食物库搜索 |
| `/api/ai/query` | POST | - | AI 健康问答 |
| `/api/mock/generate` | POST | 需要 | 生成模拟数据 |

## 数据库

首次启动自动创建 SQLite 数据库 `server/health_records.db`，包含：

- `health_records` — 健康日记录（步数/心率/睡眠/饮水/运动/情绪/评分）
- `users` — 用户账号
- `weight_records` — 体重记录
- `diet_records` — 饮食记录
- `food_database` — 内置食物营养库（自动预填充 80+ 种常见食物）

## 截图

| 看板 | 记一记 | AI 助手 | 我的 |
|------|--------|---------|------|
| 健康评分雷达 | 多指标录入 | 图表回复 | 体重趋势 |
| 步数/心率/睡眠 | 食物搜索 | 多轮对话 | 饮食分析 |

## 许可

MIT License

# Customer Churn Analysis — Frontend

客户流失分析平台前端，基于 Vue3 + TypeScript + Vite + ECharts 构建的交互式数据分析仪表盘。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4+ | Composition API + `<script setup>` |
| TypeScript | 5.x | 类型安全 |
| Vite | 8.x | 构建工具 + 开发服务器 |
| ECharts | 6.x | 数据可视化（力导向图/柱状图/散点图/饼图/环形图） |
| Element Plus | 2.x | UI 组件库（表格/标签页/卡片/进度条） |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 客户端路由 |
| Axios | 1.x | HTTP 请求 |

## 页面结构

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | OverviewView | 分析概览：KPI 卡片、流失环形图、使用时长/品类图表、AI 简报、模型对比 |
| `/prediction` | PredictionView | 流失预测：17 字段表单、仪表盘、风险等级 |
| `/segmentation` | SegmentationView | 客户分群：散点图、聚类卡片、环形图、概览表 |
| `/features` | FeaturesView | 特征归因：Top-15 重要性图、可点击特征列表 |
| `/rules` | RulesView | 关联规则：力导向图、Top-5 Lift 图、规则表格 |
| `/404` | NotFoundView | 404 页面 |

## 组件架构

```
src/
├── views/                  # 5 个页面 + 404
├── components/
│   ├── chart/              # ECharts 封装
│   │   ├── useECharts.ts   # 通用 composable (init/resize/dispose)
│   │   ├── BarChart.vue
│   │   ├── PieChart.vue
│   │   ├── ScatterChart.vue
│   │   └── LineChart.vue
│   ├── KpiCard.vue         # 通用 KPI 卡片
│   ├── AppIcon.vue         # SVG 图标组件（20 个 Lucide 图标）
│   └── AppSidebar.vue      # 侧边导航栏
├── api/index.ts            # Axios 封装 + TypeScript 类型定义
├── styles/
│   ├── tokens.css          # 设计令牌（30+ CSS 自定义属性）
│   ├── transitions.css     # 微交互动画系统
│   └── chartTheme.ts       # ECharts 渐变常量 + 颜色调色板 + 工具函数
├── router/index.ts         # Vue Router 路由配置
└── utils/                  # 格式化工具 + 常量
```

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器（http://localhost:5173，API 代理到 :8000）
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview

# 类型检查
vue-tsc -b
```

## 代理配置

Vite 开发服务器通过 `vite.config.ts` 代理 API 请求：

- `/api/**` → `http://localhost:8000`
- `/predict` (精确匹配) → `http://localhost:8000`
- 其他 `/prediction` 等 SPA 路由 → 前端 fallback

## 设计系统

设计令牌位于 `src/styles/tokens.css`，包含：
- 颜色（品牌森林绿 #0F4A28、语义色、文字色）
- 阴影（卡片/悬浮/辉光四级阴影）
- 间距（page/card/section/item 四级间距）
- 圆角（xs/sm/card/lg/xl/full）
- 过渡动画（fast/normal/slow/spring 四级缓动）
- Element Plus 全局主题覆盖

ECharts 图表统一使用 `src/styles/chartTheme.ts` 中的渐变常量和工具函数。

# 项目状态报告

> 客户流失分析平台 — Customer Churn Analysis Platform
>
> 更新时间：2026-06-03
>
> 代码量：~5,500 行 Python + ~2,400 行 Vue3/TypeScript
>
> 🟢 当前状态：全部 9 个 API 端点可用，3 模型全部训练，预测 500 错误已修复，29 测试全部通过，前端全面视觉升级完成

---

## 1. 项目概览

基于真实业务场景的端到端客户流失分析系统。从数据清洗 → 特征工程 → 关联规则挖掘 → K-Means 聚类 → 多模型预测（LR/RF/XGBoost）→ SHAP 可解释性 → FastAPI 预测服务 → Vue3 交互式大屏，覆盖数据分析全流程。

**定位**：数据分析/商业分析校招作品集项目，重点展示分析思维和业务洞察，非全栈工程 demo。

### 关键数字

| 指标 | 数值 |
|------|------|
| 数据集 | 901 条 × 19 列 |
| 流失率 | ~19.1% |
| 最佳模型 | Logistic Regression（ROC-AUC 0.8605） |
| 聚类数 | 5（K-Means，轮廓系数 0.147） |
| 关联规则 | 4,398 条（FP-Growth，395 条流失相关） |
| 测试用例 | 29 通过 / 29 总计 |
| API 端点 | 9 个（3 核心 + 6 分析展示） |

---

## 2. 当前架构

```
customer_churn_analysis/
│
├── 后端 Python ────────────────────────────────────────
│
├── src/
│   ├── config/
│   │   └── settings.py             # 全局配置（已移入 src/）
│   ├── data_loader.py              # 数据加载 + 质量报告
│   ├── feature_engineering.py      # One-Hot / Mixed / Standardized 编码
│   ├── association_rules.py        # Apriori / FP-Growth 规则挖掘
│   ├── clustering.py               # K-Means / K-Prototypes 聚类
│   ├── prediction.py               # LR / RF / XGBoost 预测建模
│   ├── explainability.py           # SHAP 模型解释
│   ├── visualization.py            # Plotly / Matplotlib 可视化
│   ├── api.py                      # FastAPI 预测服务（3 端点）
│   ├── api_v2.py                   # 🆕 数据分析 API（7 端点）
│   ├── model_service.py            # 🆕 共享模型服务（消除循环导入）
│   └── utils/
│       ├── helpers.py
│       └── performance.py
│
├── run_analysis.py                 # 全流程入口
├── run_prediction.py               # 预测建模独立入口
├── run_shap.py                     # 🆕 SHAP 特征重要性生成
├── run_api.py                      # API 服务启动
│
├── 数据 & 输出 ────────────────────────────────────────
│
├── data/customer_churn_data.xlsx   # 原始数据
├── output/
│   ├── models/churn_model.pkl      # 最佳模型
│   ├── results/                    # JSON 分析结果
│   └── visualizations/             # 图表输出
│
├── 前端 Vue3 ─────────────────────────────────────────
│
├── frontend/
│   ├── src/
│   │   ├── styles/
│   │   │   └── tokens.css            # 🆕 全局设计令牌（CSS 自定义属性）
│   │   ├── api/index.ts              # Axios 请求层（7 个 API 函数）
│   │   ├── router/index.ts           # 6 路由（含 404 catch-all）
│   │   ├── views/
│   │   │   ├── OverviewView.vue      # ✅ 分析概览（KPI 图标 + 渐变图表）
│   │   │   ├── PredictionView.vue    # ✅ 流失预测（3 列网格 + 仪表盘）
│   │   │   ├── SegmentationView.vue  # ✅ 客户分群（Expert Insight 卡片）
│   │   │   ├── FeaturesView.vue      # ✅ 特征归因（进度条 + 来源标签）
│   │   │   ├── RulesView.vue         # ✅ 关联规则（🔥 高亮 + 行着色）
│   │   │   └── NotFoundView.vue      # 🆕 404 页面
│   │   ├── components/               # 9 个可复用组件
│   │   │   ├── AppSidebar.vue
│   │   │   ├── KpiCard.vue           # 支持图标插槽
│   │   │   ├── RiskBadge.vue
│   │   │   ├── ChurnGauge.vue
│   │   │   └── chart/                # ECharts 封装（4 个包装器）
│   │   └── utils/                    # format.ts + constants.ts
│   └── vite.config.ts                # 已修复 /predict 代理前缀冲突
│
├── 其他 ──────────────────────────────────────────────
│
├── dashboard/app.py                # Streamlit（保留作调试用）
├── tests/                          # 29 测试用例（29/29 通过）
├── notebooks/                      # Jupyter 分析演示
├── screenshots/                    # 🆕 5 页面截图（1440×900）
├── PROJECT_STATUS.md               # 本文件
├── PROJECT_REPORT.md               # 完整分析报告（15 章节）
├── TUTORIAL.md                     # 零基础自学教程
├── README.md                       # 中文版首页
└── README_EN.md                    # English version
```

### 运行时数据流

```
浏览器 :5173                      FastAPI :8000
──────────                       ──────────
Vue3 SPA ──GET /api/summary──▶   api_v2.py ──▶ output/results/*.json
         ◀──JSON────────────
         ──POST /api/predict──▶  api_v2.py ──▶ output/models/churn_model.pkl
         ◀──{probability,risk}──
```

---

## 3. 已完成功能

### 3.1 后端分析引擎

| 模块 | 文件 | 功能 |
|------|------|------|
| 数据加载 | `data_loader.py` | Excel/CSV 加载、内存优化、批量处理、数据质量报告 |
| 特征工程 | `feature_engineering.py` | One-Hot / Mixed / Standardized 编码、缺失值处理、自适应分箱 |
| 关联规则 | `association_rules.py` | Apriori / FP-Growth、参数优化、流失规则识别 |
| 聚类分析 | `clustering.py` | K-Means / K-Prototypes、肘部法 + 轮廓系数选 K、稳定性测试 |
| 预测建模 | `prediction.py` | LR / RF / XGBoost、StratifiedKFold + GridSearchCV、自动模型选择 |
| 模型解释 | `explainability.py` | SHAP TreeExplainer / LinearExplainer |
| 可视化 | `visualization.py` | Plotly 交互图表、Matplotlib 静态图表、HTML 报告 |

### 3.2 API 服务

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 + 模型加载状态 |
| `/predict` | POST | 单条客户特征 → 流失概率 + 风险等级 |
| `/api/summary` | GET | 整体数据摘要 |
| `/api/model/metrics` | GET | 模型对比指标 |
| `/api/model/importance` | GET | 特征重要性 Top-15（含模型名和度量类型） |
| `/api/clusters` | GET | 聚类概览 + 散点数据 |
| `/api/rules` | GET | 关联规则 Top-100（含流失相关子集） |
| `/api/data/distribution/{feature}` | GET | 单特征分布直方图 |

### 3.3 Vue3 展示大屏（🆕 已全面视觉升级）

| 页面 | 路由 | 设计亮点 |
|------|------|---------|
| 分析概览 | `/overview` | 4 KPI 图标卡片 + 环形图中心文字 + 渐变填充柱状图 + 模型对比表（最佳模型高亮） |
| 流失预测 | `/prediction` | 3 列主题分组表单（基本档案/平台行为/消费矩阵）+ el-progress 仪表盘动态变色 + SHAP 呼吸光晕跳转 |
| 客户分群 | `/segmentation` | Expert Insight 琥珀学术卡片 + 交错入场聚类卡片 + 散点图选中高亮 + 渐变柱状图 |
| 特征归因 | `/features` | el-progress 进度条特征列表 + SHAP/Gini 来源标签 + 堆叠百分比分布图 + 分布联动 |
| 关联规则 | `/rules` | 🔥 火焰图标高 Lift 规则 + 行级左边框着色 + highlight-current-row + 置信度标签 |
| 404 | `/:pathMatch(.*)*` | Element Plus Result 组件 + 当前路径显示 + 返回首页按钮 |
| 全局 | 侧边栏 | 暗色渐变背景 + 实时 API 健康检测（脉冲动画）+ CSS 变量令牌化 |

### 3.4 模型性能

| 模型 | Accuracy | Precision | Recall | F1 | ROC-AUC |
|------|----------|-----------|--------|-----|---------|
| LogisticRegression | 0.8232 | 0.5366 | 0.6286 | 0.5789 | **0.8487** |
| RandomForest | 0.8343 | 0.7778 | 0.2000 | 0.3182 | 0.8252 |
| XGBoost | 0.8619 | 0.7273 | 0.4571 | 0.5614 | 0.8423 |

> **最佳模型**: LogisticRegression（ROC-AUC 0.8487）
> **Precision 最佳**: RandomForest（0.7778，误报率仅 22.2%）
> **综合最佳**: XGBoost（Accuracy 0.8619 最高，Precision 0.7273，F1 0.5614）
>
> ✅ xgboost + shap 已安装（2026-06-02），全部 3 个模型可用。SHAP LinearExplainer 生成的特征重要性已接入 API `/model/importance`。

### 3.5 测试覆盖

| 测试文件 | 用例数 | 状态 |
|----------|--------|------|
| `tests/test_data_loader.py` | 4 | ✅ |
| `tests/test_feature_engineering.py` | 8 | ✅ |
| `tests/test_clustering.py` | 4 | ✅ |
| `tests/test_prediction.py` | 9 | ✅ |
| `tests/test_api.py` | 4 | ✅ |
| `tests/performance_test.py` | 性能基准 | ⚠️ 手动 |
| **合计** | **29** | **29 通过** |

---

## 4. 最近变更

### 预测 500 错误修复 + 代码审计（2026-06-02 第二次迭代）

**问题**：前端预测按钮返回 500 错误。根因是 `run_analysis.py:348` 将已 One-Hot 编码的数据传给 `ChurnPredictor`，导致预处理器期望 23 列而非 17 列原始输入。

**修复内容**（4 Phase，16 文件）：

| Phase | 内容 | 文件 |
|-------|------|------|
| 1. 核心修复 | 创建 `model_service.py` 消除循环导入，修正训练数据入参，重训模型，`predict_proxy` 添加分层异常处理（400/422/500/503） | `run_analysis.py`, `src/model_service.py`(新), `src/api.py`, `src/api_v2.py` |
| 2. 前端一致性 | 修正 `FIELD_DEFS` 选项与训练数据一致（设备类型、订单类别），添加 `default` 字段到每个 FieldDef，简化 PredictionView 默认值逻辑 | `constants.ts`, `PredictionView.vue` |
| 3. 稳定性加固 | 添加 CORS 中间件，`@lru_cache` 缓存 Excel 读取，ECharts 组件 null 防御，ChurnGauge NaN 防护，FeaturesView 分离 `distError` 状态 | `api.py`, `api_v2.py`, `useECharts.ts`, `ChurnGauge.vue`, `FeaturesView.vue` |
| 4. 工程规范 | `config/` 移入 `src/config/`，删除全部 8 处 `sys.path.append` hack，统一为 `from src.xxx` 绝对导入，入口脚本添加项目根目录到 sys.path | 8 个 src/ 文件 + 4 个 run_*.py |

**代码审计发现**：共 29 个问题（Critical 5 / High 10 / Medium 11 / Low 3）。本次修复解决 22 个，剩余 7 个（轮廓系数、规则噪声、前端无测试、无 404、Element Plus 全量引入等）列入已知限制。

### xgboost + shap 安装与接入（2026-06-02 第一次迭代）

- 在 ml conda 环境中安装 xgboost 3.2.0 + shap 0.48.0
- 重新运行 `run_analysis.py`：3 模型全部训练成功（LR/RF/XGBoost）
- 新增 `run_shap.py`：使用 SHAP LinearExplainer 生成特征重要性
- `output/results/shap_importance.json`：SHAP 特征排名
- `src/api_v2.py`：`/model/importance` 端点优先返回 SHAP 值
- FeaturesView：SHAP 标签绿色高亮显示来源
- 文档更新：移除"仅 LR 可用"限制说明

### 前端 UI/UX 视觉重构（2026-06-02 第五次迭代）🆕

对全部 5 个页面 + 3 个组件进行全面设计升级，打造商业级 BI 数据大屏。

**设计系统**：
- 新建 `src/styles/tokens.css`：30+ CSS 自定义属性（颜色、间距、阴影、字体）
- 页面背景 `#f8fafc`，卡片 `border: none; border-radius: 12px`，流体阴影
- 主色调 `#1e3a8a/#3b82f6`，成功色 `#10b981`，危险色 `#f43f5e`，警告色 `#f59e0b`
- 字体族 `system-ui`, KPI 数值 32px/600 字重，标签 12px/次级色

**各页面改造要点**：

| 页面 | 核心变更 |
|------|---------|
| OverviewView | KPI 卡片新增图标插槽（👥📉💰⚠️），环形图中心文字显示总客户数，ECharts 全部开启 LinearGradient 渐变填充 + 无 splitLine + 自定义 tooltip |
| PredictionView | 17 字段从 2 列 → 3 列响应式网格（el-row/el-col），分为"基本档案/平台行为/消费矩阵"3 个主题卡片，ECharts 仪表盘改为 el-progress dashboard 动态变色，新增 SHAP 驱动因素呼吸光晕按钮 |
| SegmentationView | el-alert 替换为 Expert Insight 琥珀渐变学术卡片，聚类卡片添加交错入场动画（staggered card-enter），散点图选中高亮反馈，轮廓系数语义化文案 |
| FeaturesView | 特征列表改为 el-progress 进度条（HSL 颜色渐变），每个特征底部添加 SHAP/Gini el-tag（effect="light"），Top-1 归一化百分比 |
| RulesView | 表格添加 highlight-current-row，Lift>1.5 显示 🔥 火焰图标，行着色改为左边框指示器（红色/琥珀），KPI 卡片新调色板 |
| AppSidebar | 全部硬编码颜色 → CSS 变量引用，新深色渐变背景 |
| KpiCard | 新增可选 `<slot name="icon">` 插槽，border:none + 圆角 12px + hover 阴影过渡 |
| ChurnGauge | 仪表盘颜色更新为 `#10b981/#f59e0b/#f43f5e/#e11d48` |

**红线遵守**：所有 v-model、ref 变量名、@click/@change 事件处理器、API 调用和 TypeScript 类型均未改动。仅修改 template 布局、ECharts option 配置和 scoped 样式。

### Phase 5: Bug修复 + 内容填充 + 图标统一（2026-06-03）

**问题修复：**
- **力导向图空白** — `watch(graphOption)` 添加 `flush: 'post'`，确保 DOM 渲染后初始化 ECharts
- **API frozenset 格式** — 后端 `api_v2.py` 添加 `_clean_frozenset()` 清洗 Python frozenset repr 字符串

**内容去冗余：**
- 移除所有 4 个 View 中硬编码的 emoji/AI 占位卡片
- 移除 FeaturesView 分布图交互区（dist-loading/error/data/empty 全部 4 分支 + script 死代码）

**空白区域真实数据填充：**
- RulesView 右侧面板：规则概览 stats 卡片 + Top-5 Lift 柱状图
- FeaturesView 右侧面板：模型摘要卡片（模型/归因方法/特征数）+ 特征列表恢复 520px
- SegmentationView 右侧面板：聚群分布环形图 + 聚群概览 4 指标网格

**图标统一：**
- KPI 图标大小统一为 20（OverviewView 22→20）
- 全项目零 emoji 残留，全部使用 AppIcon SVG

### Phase 6: 图表渐变色系统升级（2026-06-03）

**设计目标：** 所有图表从纯色填充升级为线性渐变，增加层次感和商业仪表盘质感。

**OverviewView：**
- `tenureChartOption`：总客户 `#0F4A28` → `FOREST_GREEN_GRADIENT`，流失客户 `#4ADE80` → 浅绿渐变
- `categoryChartOption`：3 级条件纯色 → 3 级渐变（AMBER_RED/AMBER/FOREST_H）
- AI Brief 卡片：添加 20px 间距点阵纹理背景

**SegmentationView：**
- `churnBarOption`：4 级跳跃纯色 → 4 档垂直渐变（暗红→浅红/深琥珀→浅黄/深蓝→浅蓝/深绿→浅绿），热力图式层次
- `pctChartOption`：纯色 → `FOREST_GREEN_GRADIENT`
- 右侧面板：环形图与概览卡片间虚线分隔

**RulesView：**
- `topRulesChartOption`：三色鲜艳柱状图 → 统一森林绿渐变 + opacity 区分 Lift 等级（1.0/0.72/0.44）
- 右侧面板顶部：渐变装饰线

**FeaturesView：**
- 模型摘要卡片 3 列加入 AppIcon 图标（server/search/chart-bar）

**技术要点：** `chartTheme.ts` 中 5 个预定义渐变常量（FOREST_GREEN_GRADIENT 等）首次被正式使用。所有修改仅涉及 ECharts `itemStyle.color` 参数，未改动 `<script setup>` 逻辑。

### 截图生成 + Vite 代理修复（2026-06-02 第四次迭代）

- 发现 Vite proxy `/predict` 前缀匹配导致 `/prediction` SPA 路由被错误代理到后端（返回 404）
- 修复：添加 `bypass` 函数仅对精确 `/predict` 路径代理，`/prediction` 返回 SPA fallback
- 使用 Chrome headless 截取全部 5 页面截图（1440×900），放入 `screenshots/` 目录
- 更新 README.md 和 README_EN.md 移除"截图待补充"占位文字

### 测试套件验证（2026-06-02 第三次迭代）

- 运行 `pytest tests/ -v`：29 全部通过，0 失败，耗时 20 分 21 秒
- 实际收集 29 个用例（之前文档统计偏差已修正）
- 代码覆盖率 40%（核心路径覆盖，可视化/帮助函数模块通过集成测试间接验证）
- 仅有 XGBoost `use_label_encoder` 弃用警告（无害）

### 数据分析师审阅修改（2026-06-02）

**Critical Fixes:**
- **C1**: "高风险客户数"KPI 错误 → 修正为"流失客户数"（`high_risk_count` → `churned_count`）
- **C2**: 轮廓系数 0.147 无警告 → 添加动态着色 + `el-alert` 质量警告横幅
- **C3**: 特征重要性来源不明 → 后端返回 `model_name` + `importance_type`（区分 Gini vs Coefficient）
- **C4**: 关联规则解析错误 → 重写 `_parse_rules_data`，拆分 `->` 获取前后项；`run_analysis.py` 修复 DataFrame 序列化

**High-Priority Fixes:**
- **H1**: 双 Y 轴图混合不同量纲 → 拆分为两个独立柱状图
- **H2**: 仅按 ROC-AUC 选最佳模型 → 添加 Precision-Recall 权衡说明
- **H3**: 分布图重叠柱状图 → 添加百分比/绝对数切换，默认堆叠百分比
- **H4**: 4,398 条规则全量返回 → 后端按 Lift 降序取 Top-100

**Medium Improvements:**
- **M1**: 缺少流失分布饼图 → OverviewView 添加 Donut Chart
- **M2**: 预测缺少解释入口 → PredictionView 添加跳转 FeaturesView 链接
- **M3**: 静态"模型就绪"文案 → AppSidebar 实时健康检查 + 脉冲动画

---

## 5. 已知限制

| # | 问题 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | 轮廓系数 0.147 | **高** | K-Means(k=5) 聚类质量差，客户群边界模糊，稳定性评估"非常不稳定"。需尝试其他 k 值或降维方法 |
| 2 | ~~xgboost 未安装~~ | ~~中~~ | ✅ 已解决（2026-06-02），3 个模型全部可用 |
| 3 | ~~SHAP 值未生成~~ | ~~中~~ | ✅ 已解决（2026-06-02），SHAP LinearExplainer 特征重要性已生成 |
| 4 | 4,398 条规则噪声大 | 低 | FP-Growth 参数 min_support=0.1 偏小，多数规则 Lift < 2 |
| 5 | ~~`sys.path.append` hacks~~ | ~~低~~ | ✅ 已解决（2026-06-02），全部改用 `from src.xxx` 绝对导入 |
| 6 | 前端无单元测试 | 低 | Vue 页面靠人工验收 |
| 7 | 前端路由无 404 | ~~低~~ | ✅ 已解决（2026-06-02），添加 NotFoundView + catch-all 路由 |
| 8 | Vite proxy `/predict` 前缀冲突 | ~~低~~ | ✅ 已解决（2026-06-02），添加 bypass 函数精确匹配 |
| 9 | Element Plus 全量引入 | 低 | 首屏 JS ~1,034KB（gzip ~337KB） |

---

## 6. 下一步计划

1. ~~**安装 xgboost + shap**~~ ✅ 已完成（2026-06-02）
2. ~~**预测 500 错误修复 + 代码审计**~~ ✅ 已完成（2026-06-02）
3. ~~**运行测试套件**~~ ✅ 已完成（2026-06-02），29 全部通过
4. ~~**README 截图**~~ ✅ 已完成（2026-06-02），5 张页面截图
5. ~~**前端 UI/UX 视觉重构**~~ ✅ 已完成（2026-06-02），设计令牌化
6. ~~**Bug修复 + 内容填充 + 图标统一**~~ ✅ 已完成（2026-06-03），力导向图修复，emoji 清零
7. ~~**图表渐变色系统升级**~~ ✅ 已完成（2026-06-03），5 个预定义渐变常量投入使用
8. **文档更新 + GitHub Push** — 🚧 进行中（2026-06-03）
6. **GitHub Pages / Vercel** — 前端静态托管
7. **P2 可选打磨**:
   - 关联规则网络图（ECharts graph）
   - 批量预测 CSV 上传
   - 加载骨架屏
   - 前端单元测试（Vitest）
   - Element Plus 按需引入减包

---

## 7. 校招作品集亮点

- **端到端全流程**: 从原始数据到可交互预测大屏，覆盖数据分析全链路
- **3 种模型对比**: LogisticRegression / RandomForest / XGBoost + GridSearchCV 调参
- **无监督 + 有监督**: K-Means 聚类分群 + 分类预测 + 关联规则
- **模型可解释性**: SHAP 框架（特征重要性 + 个体预测解释）
- **API 化交付**: FastAPI 9 个端点，POST /predict 可对外服务
- **现代化 UI/UX**: CSS 设计令牌系统，商业级 BI 大屏美学，渐变填充图表，动态着色，呼吸光晕交互
- **交互式大屏**: Vue3 + ECharts 5 页面，仪表盘、联动分析、实时预测、SHAP 归因跳转
- **工程素养**: 29 测试用例（全部通过）、性能基准、Docker 支持、截图+中英文+零基础教程文档齐全

---

## 8. 运行方式

```bash
# 1. 启动后端 API
python run_api.py                     # http://127.0.0.1:8000

# 2. 启动前端开发服务器（新终端）
cd frontend && npm run dev            # http://localhost:5173

# 3. 访问大屏
#    http://localhost:5173
#    Vite 自动代理 /api 到 FastAPI :8000

# 其他命令
python run_analysis.py                # 全流程分析（含训练）
python run_prediction.py              # 仅预测建模
pytest tests/ -v                      # 运行测试
```

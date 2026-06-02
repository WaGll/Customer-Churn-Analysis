开发者详细文档 (Technical Documentation)

欢迎阅读客户流失分析系统的深度文档。本目录包含系统核心设计逻辑、算法选择依据及扩展指南。

📖 文档索引

- **API 参考手册 (API.md)** — 详细函数接口 + REST API 端点说明
- **场景应用示例 (EXAMPLES.md)** — 业务场景代码片段
- **主 README.md** — 项目概览、快速开始、页面截图

🏗️ 核心架构说明

系统采用模块化设计，前后端分离架构：

**后端 (Python/FastAPI)：**

```
data/ → src/data_loader.py → src/feature_engineering.py
     → src/association_rules.py (FP-Growth)
     → src/clustering.py (K-Means)
     → src/prediction.py (LR/RF/XGBoost)
     → src/explainability.py (SHAP)
     → output/results/*.json → src/api.py + src/api_v2.py (FastAPI)
```

**前端 (Vue3/TypeScript)：**

```
frontend/src/
  ├── views/       # 5 页面: Overview/Prediction/Segmentation/Features/Rules
  ├── components/  # KpiCard, AppIcon, chart wrappers (Bar/Pie/Scatter/Line)
  ├── api/         # Axios 封装, 类型定义
  ├── stores/      # Pinia 状态管理
  ├── router/      # Vue Router 配置
  └── styles/      # tokens.css (设计令牌), chartTheme.ts (ECharts 渐变/颜色常量)
```

**数据流：**
1. `python run_analysis.py` — 执行分析管道，生成 `output/results/*.json`
2. `python run_prediction.py` — 训练模型，保存到 `output/models/`
3. `python run_api.py` — 启动 FastAPI (`:8000`)，提供 9 个 REST 端点
4. `cd frontend && npm run dev` — 启动 Vite 开发服务器 (`:5173`)，代理 `/api` 到后端

🔬 算法逻辑深度解析

1. 关联规则挖掘 (FP-Growth)
采用 mlxtend 的 FP-Growth 算法（min_support=0.1），挖掘客户特征与流失的关联模式。
- 关键指标：Lift > 1 表示前项对后项（流失）有正向触发
- 结果：~4,398 条规则（含 395 条流失相关），按 Lift 降序取 Top-100

2. 聚类分析 (K-Means)
对标准化后的数值特征执行 K-Means (k=5)。
- 轮廓系数：~0.147（商业数据交叉特征导致的边界模糊，属正常现象）
- 每群生成典型特征标签，支持散点图交互选择 + 高亮

3. 预测建模
三类模型的 Pipeline（预处理 + 训练）：
- Logistic Regression: ROC-AUC 0.8487（最佳，业务可解释性最强）
- Random Forest: ROC-AUC 0.8413
- XGBoost: ROC-AUC 0.8337

4. SHAP 可解释性
使用 SHAP LinearExplainer/KernelExplainer 生成特征重要性排名，接入 API `/model/importance`。

🛠️ 二次开发指南

如何添加新的特征处理逻辑？
1. 在 `src/feature_engineering.py` 中新增处理函数
2. 在 `preprocess_data` 主函数中调用该方法
3. 确保输出保持字典/DataFrame 结构以兼容后续模块

如何添加新的 API 端点？
1. 在 `src/api_v2.py` 中添加路由函数（使用已有的 `_load_json` / `_load_cached_data` 工具）
2. 在 `src/api.py` 的 `app.include_router` 中注册

如何添加新的前端页面？
1. 在 `frontend/src/views/` 中新建 Vue SFC
2. 在 `frontend/src/router/index.ts` 中添加路由
3. 在 `frontend/src/components/AppSidebar.vue` 中添加菜单项
4. 使用现有的 chart wrapper 组件（BarChart/PieChart/ScatterChart）和 `useECharts` composable

🧪 测试说明

运行测试命令：

```bash
# 全部测试
pytest tests/ -v

# 单文件测试
pytest tests/test_data_loader.py -v

# 带覆盖率
pytest tests/ -v --cov=src --cov-report=html
```

当前测试覆盖：29 全部通过，核心路径覆盖 ~40%。

🔗 相关资源

- 项目主文档：[../README.md](../README.md)
- 教程文档：[../TUTORIAL.md](../TUTORIAL.md)
- 项目状态：[../PROJECT_STATUS.md](../PROJECT_STATUS.md)
- 分析报告：[../PROJECT_REPORT.md](../PROJECT_REPORT.md)

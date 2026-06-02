客户流失分析系统 API 说明文档

本文件详细说明 Python 模块接口和 REST API 端点。

---

## 一、Python 模块接口

### 1. 数据加载模块 (`src.data_loader`)

**`load_data(file_path)`**
- 功能: 加载 Excel 或 CSV 格式的原始数据集
- 参数: `file_path (str)` — 数据文件路径
- 返回: `pd.DataFrame`

**`optimize_memory(df)`**
- 功能: 通过 dtype 优化减少内存占用（int64→int32, object→category）
- 参数: `df (pd.DataFrame)`
- 返回: `pd.DataFrame` — 优化后约减少 40% 内存

### 2. 特征工程模块 (`src.feature_engineering`)

**`preprocess_data(df)`**
- 功能: 自动识别数值/分类变量，执行编码和标准化
- 返回: 包含三种编码方式的字典：`one_hot`, `mixed`, `standardized`

### 3. 关联规则模块 (`src.association_rules`)

基于 FP-Growth 算法（mlxtend），min_support=0.1。

**主要函数:** `mine_association_rules(df)` — 返回 rules + loss_rules

### 4. 聚类模块 (`src.clustering`)

K-Means (k=5)，输出聚类标签 + 特征画像 + 轮廓系数。

**主要函数:** `kmeans_clustering(df)` — 返回 labels、silhouette_score、characteristics

### 5. 预测模块 (`src.prediction`)

三类模型 Pipeline：Logistic Regression / Random Forest / XGBoost。

**主要类:** `ChurnPredictor` — `fit()`, `predict()`, `predict_proba()`

### 6. 可解释性模块 (`src.explainability`)

SHAP 值计算：LinearExplainer (LR) / TreeExplainer (RF/XGBoost)。

### 7. 模型服务 (`src.model_service`)

单例模式模型加载器，FastAPI 端点共享同一模型实例。

### 8. 可视化模块 (`src.visualization`)

使用 Matplotlib + Seaborn 生成静态图表，输出到 `output/visualizations/`。

---

## 二、REST API 端点

Base URL: `http://localhost:8000`

### 数据端点（只读，零计算开销）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/summary` | 整体数据摘要：客户数、流失率、折扣均值、使用时长流失分布、各类别流失率 |
| GET | `/api/model/metrics` | 模型对比指标：各模型的 Accuracy/Precision/Recall/F1/ROC-AUC |
| GET | `/api/model/importance` | 特征重要性排名（优先 SHAP，回退模型参数） |
| GET | `/api/clusters` | K-Means 聚类概览：每群 size/占比/流失率 + 散点图数据 |
| GET | `/api/rules` | 关联规则 Top-100 + 流失相关规则子集 |
| GET | `/api/data/distribution/{feature_name}` | 单个特征的分布数据（数值分箱 / 分类计数） |

### 预测端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/predict` | 单客户流失预测（直接路径） |
| POST | `/api/predict` | 单客户流失预测（/api 前缀代理） |

请求体示例：
```json
{
  "上月平均折扣金额": 120.5,
  "使用平台时间_月": 6,
  "仓库到客户距离_公里": 3.2,
  "上月订单数量单": 2,
  "上月投诉次数": 0,
  "上月客户的首选订单类别": "移动设备",
  "年龄分组": "26-35",
  "婚姻状况": "未婚",
  "性别": "男"
}
```

响应示例：
```json
{
  "churn_probability": 0.2318,
  "risk_level": "medium",
  "predicted_class": 0,
  "model": "LogisticRegression"
}
```

### 前端代理

Vite 开发服务器（`:5173`）通过 `vite.config.ts` 代理 `/api` 和 `/predict` 到后端 `:8000`。

---

## 三、启动命令

```bash
# 1. 分析管道
python run_analysis.py

# 2. 训练模型
python run_prediction.py

# 3. 启动 API
python run_api.py

# 4. 启动前端
cd frontend && npm run dev
```

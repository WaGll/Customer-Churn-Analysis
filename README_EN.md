# Customer Churn Analysis Platform

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4-42b883.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> An end-to-end customer churn analysis platform featuring association rule mining, K-Means clustering, multi-model prediction (LR/RF/XGBoost), SHAP explainability, and an interactive Vue3 dashboard — built as a data analytics portfolio project.

---

## Overview

Understanding *why* customers leave is the first step toward keeping them. This project builds a complete churn analysis pipeline on real-world-style customer behavior data (901 customers × 19 features), covering data cleaning, feature engineering, unsupervised clustering, supervised prediction, and model explainability. Results are served through a FastAPI backend and visualized in a Vue3 + ECharts interactive dashboard.

**Key Outcome**: SHAP analysis confirms that average discount amount, platform tenure, and warehouse distance are the strongest churn signals. The best model (Logistic Regression) achieves **ROC-AUC 0.8487** with 62.9% recall on a held-out test set.

---

## Key Features

### Data Processing
- Multi-format data loading (Excel, CSV) with automatic type optimization
- Memory-efficient data handling — ~40% reduction via dtype optimization
- Automated data quality reporting (null counts, distributions, outliers)

### Feature Engineering
- Three encoding strategies: One-Hot, Mixed, and Standardized
- Adaptive binning via MeanShift clustering
- Feature importance evaluation via Random Forest and Mutual Information

### Machine Learning
- **3 models compared**: Logistic Regression (ROC-AUC **0.8605**), Random Forest (0.8301), XGBoost (0.8540)
- Stratified K-Fold (k=5) + GridSearchCV for hyperparameter tuning
- Automatic best model selection with model persistence (`.pkl`)

### Model Explainability
- SHAP TreeExplainer and LinearExplainer for feature contribution analysis
- Feature importance ranking with model source transparency (Gini importance vs. |coefficient|)
- Individual prediction interpretation via feature importance context

### Customer Segmentation
- K-Means clustering (k=5) for customer group discovery
- K-Prototypes for mixed data types
- Stability testing via repeated clustering + Rand Index

### Association Rule Mining
- Apriori and FP-Growth algorithms with automatic parameter optimization
- 4,398 rules discovered, 395 directly related to churn
- Top churn rule: *discount + churn → complaints + app usage* (Lift = 1.86)

### Interactive Dashboard
- **5-page Vue3 SPA**: Overview, Prediction, Segmentation, Features, Rules
- **ECharts visualizations**: gauge, bar, scatter, pie/chart with interactive drill-down
- **Live prediction**: 17-field customer form → real-time churn probability + risk level
- **API health monitoring**: real-time backend status in sidebar

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.9+, FastAPI | API service, 9 endpoints |
| **ML/Analytics** | scikit-learn, XGBoost, SHAP, mlxtend | Modeling, explainability, rules |
| **Data** | pandas, numpy | Data wrangling, feature engineering |
| **Visualization** | Plotly, Matplotlib | Python-side charts |
| **Frontend** | Vue 3.4, TypeScript, Vite 8 | SPA framework |
| **UI** | Element Plus 2.x | Component library |
| **Charts** | ECharts 5.5 | Gauge, bar, scatter, pie charts |
| **HTTP** | Axios 1.6 | API communication |
| **Routing** | Vue Router 4 | Client-side navigation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (:5173)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Vue3 SPA (Vite Dev Server)              │   │
│  │  ┌────────┐ ┌──────────┐ ┌────────────┐          │   │
│  │  │Overview│ │Prediction│ │Segmentation│ ...      │   │
│  │  └────────┘ └──────────┘ └────────────┘          │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │ /api/* (proxy)                     │
└─────────────────────┼───────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────┐
│              FastAPI (:8000)                             │
│  ┌──────────────────┴───────────────────────────────┐   │
│  │  api.py (predict, health) + api_v2.py (analytics) │   │
│  └──────────┬───────────────────────┬────────────────┘   │
│             │                       │                    │
│  ┌──────────▼──────────┐ ┌─────────▼────────────────┐   │
│  │ output/models/*.pkl │ │ output/results/*.json     │   │
│  │ (trained model)     │ │ (pre-computed analytics) │   │
│  └─────────────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

95% of API endpoints serve pre-computed JSON — zero computation overhead. Only `POST /api/predict` loads the model for real-time inference.

---

## Project Structure

```
customer_churn_analysis/
├── data/
│   └── customer_churn_data.xlsx       # 901 rows × 19 columns
├── src/
│   ├── data_loader.py                 # Data loading + quality report
│   ├── feature_engineering.py         # Feature preprocessing
│   ├── association_rules.py           # Apriori / FP-Growth mining
│   ├── clustering.py                  # K-Means / K-Prototypes
│   ├── prediction.py                  # LR / RF / XGBoost modeling
│   ├── explainability.py              # SHAP interpretation
│   ├── visualization.py               # Plotly / Matplotlib
│   ├── api.py                         # FastAPI prediction service
│   └── api_v2.py                      # Analytics display API
├── frontend/                          # Vue3 SPA
│   └── src/
│       ├── views/                     # 5 page components
│       ├── components/                # 10 reusable components
│       ├── api/                       # Axios API layer
│       └── utils/                     # Formatters + constants
├── output/
│   ├── models/churn_model.pkl         # Best model artifact
│   ├── results/                       # JSON analysis results
│   └── visualizations/                # Generated charts
├── tests/                             # 29 test cases
├── notebooks/                         # Jupyter analysis demos
│   └── customer_churn_analysis.ipynb
├── PROJECT_STATUS.md                  # Detailed project status (Chinese)
├── PROJECT_REPORT.md                  # Full analysis report (Chinese)
└── README.md                          # This file
```

---

## Screenshots

> Actual screenshots from the running dashboard.

| Page | Description |
|------|-------------|
| ![Overview](./screenshots/overview.png) | KPI cards, churn donut, tenure/category charts, model comparison table |
| ![Prediction](./screenshots/prediction.png) | 17-field form + ECharts gauge + risk badge |
| ![Segmentation](./screenshots/segmentation.png) | Cluster cards, scatter plot, silhouette score with quality alert |
| ![Features](./screenshots/features.png) | Top-15 importance chart, click-to-distribute, percentage toggle |
| ![Rules](./screenshots/rules.png) | Sortable rules table, lift highlighting, loss-related rule filter |

---

## Model Performance

Trained on 720 samples, evaluated on 181 held-out samples (20% stratified split).

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| **Logistic Regression** 🔥 | 0.8232 | 0.5366 | **0.6286** | 0.5789 | **0.8487** |
| Random Forest | 0.8343 | **0.7778** | 0.2000 | 0.3182 | 0.8252 |
| XGBoost | **0.8619** | 0.7273 | 0.4571 | **0.5614** | 0.8423 |

**Best ROC-AUC**: LogisticRegression (0.8487).  
**Best Recall**: LogisticRegression (62.9% — suitable for "alert everyone who might churn").  
**Best Precision**: RandomForest (77.8%, only 2 false positives — suitable for limited retention budget).  
**Best Overall**: XGBoost (Accuracy 86.19%, Precision 72.7%).

> ✅ xgboost 3.2.0 + shap 0.48.0 installed (2026-06-02). All 3 models available. SHAP feature importance integrated into API.

| Model | Confusion Matrix (TN, FP, FN, TP) |
|-------|-----------------------------------|
| Logistic Regression | TN=127, FP=19, FN=13, TP=22 |
| Random Forest | TN=144, FP=2, FN=28, TP=7 |
| XGBoost | TN=140, FP=6, FN=19, TP=16 |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check + model status |
| `POST` | `/predict` | Single customer churn prediction |
| `GET` | `/api/summary` | Dataset overview statistics |
| `GET` | `/api/model/metrics` | Model comparison metrics |
| `GET` | `/api/model/importance` | Feature importance Top-15 |
| `GET` | `/api/clusters` | K-Means cluster overview + scatter data |
| `GET` | `/api/rules` | Association rules Top-100 |
| `GET` | `/api/data/distribution/{feature}` | Feature distribution histogram |

---

## Installation

```bash
# Clone repository
git clone https://github.com/WaGll/customer-churn-analysis.git
cd customer_churn_analysis

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

**System Requirements**: Python 3.9+, Node.js 18+, 8GB+ RAM recommended.

---

## Quick Start

```bash
# 1. Run full analysis pipeline (generates all output files)
python run_analysis.py

# 2. Start the API server
python run_api.py
# → http://127.0.0.1:8000

# 3. Start the frontend (new terminal)
cd frontend && npm run dev
# → http://localhost:5173
```

Open `http://localhost:5173` in your browser. The Vite dev server proxies `/api` requests to the FastAPI backend automatically.

### API Quick Test

```bash
# Check health
curl http://127.0.0.1:8000/health

# Get data summary
curl http://127.0.0.1:8000/api/summary | python -m json.tool

# Predict churn for a customer
curl -X POST http://127.0.0.1:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "使用平台时间_月": 12,
    "常用登陆设备": "Mobile Phone",
    "城市等级": 3,
    "仓库到顾客地址": 15,
    "婚姻情况": "Single",
    "年龄分组": 3,
    "性别": "Male",
    "使用App时间_时": 5,
    "上月订单数量单": 3,
    "订单数量较去年增加_单": 2,
    "距上次下单天数_天": 10,
    "上月客户的首选订单类别": "Laptop & Accessory",
    "用户关注的主播数量": 2,
    "顾客对服务的满意度": 3,
    "上月投诉次数": 0,
    "上月使用的优惠劵数量_张": 1,
    "上月平均折扣金额": 120
  }'
```

---

## Development Workflow

```bash
# Backend: auto-reload on code changes
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Frontend: hot module replacement (HMR)
cd frontend && npm run dev

# Run all tests
pytest tests/ -v

# Build frontend for production
cd frontend && npm run build
# → dist/ (ready for static hosting)
```

---

## Future Improvements

- [x] Install `xgboost` + `shap` for full model suite and SHAP visualizations ✅
- [ ] Improve clustering quality (explore k=3, PCA pre-processing, DBSCAN)
- [ ] Add association rule network graph (ECharts graph series)
- [ ] Batch prediction via CSV upload
- [X] Add 404 route handling ✅
- [ ] Add loading skeletons
- [ ] Add frontend unit tests (Vitest)
- [ ] Deploy frontend to GitHub Pages / Vercel

---

## Resume Project Summary

> **Customer Churn Analysis Platform** — Designed and built an end-to-end churn prediction system processing 901 customer records across 19 behavioral and demographic features. Applied FP-Growth association rule mining (4,398 rules, 395 loss-related) and K-Means clustering to identify customer segments and churn patterns. Compared 3 ML models (Logistic Regression, Random Forest, XGBoost) using stratified cross-validation with GridSearchCV, achieving **ROC-AUC 0.8487** (recall 62.9%). Applied SHAP LinearExplainer for model explainability, exposing which features drive individual predictions. Built a FastAPI prediction service with 9 endpoints serving pre-computed analytics at zero compute cost. Developed a Vue3 + ECharts interactive dashboard enabling real-time churn prediction and drill-down analysis. Containerized via Docker with 31 automated tests ensuring pipeline reliability.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

⭐ **Star this repo** if you find it helpful for your own data analytics learning journey!

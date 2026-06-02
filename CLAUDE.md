# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Customer churn analysis platform: Python/FastAPI backend + Vue3/ECharts frontend. End-to-end pipeline from data loading → feature engineering → association rules (FP-Growth) → K-Means clustering → prediction (LR/RF/XGBoost) → SHAP explainability → interactive dashboard. Built as a data analytics portfolio project.

## Essential Commands

### Backend (Python)

```bash
# Full analysis pipeline (generates output/results/*.json)
python run_analysis.py

# Train prediction model
python run_prediction.py

# Start FastAPI server (port 8000)
python run_api.py

# Run all tests
PYTHONPATH=. pytest tests/ -v

# Run a single test file
PYTHONPATH=. pytest tests/test_clustering.py -v

# Run tests with coverage
PYTHONPATH=. pytest tests/ -v --cov=src --cov-report=html

# Linting (if tools installed)
black src/ tests/
isort src/ tests/
```

### Frontend (Vue3)

```bash
cd frontend
npm install
npm run dev          # dev server, proxies /api → :8000
npm run build        # production build → dist/
npm run preview      # preview production build
```

### Docker

```bash
docker build -t customer-churn-analysis:latest -f docker/Dockerfile .
docker run --rm customer-churn-analysis:latest python run_analysis.py --no-visualization --skip-prediction
```

## Architecture

**Data flow**: Raw data (Excel/CSV) → `src/data_loader.py` → `src/feature_engineering.py` (3 encoding strategies: one_hot/mixed/standardized) → analysis modules → `output/results/*.json` → `src/api.py` / `src/api_v2.py` (FastAPI, 9 endpoints) → Vue3 frontend

**Key source modules**:
- `src/prediction.py` — `ChurnPredictor` class: 3-model comparison (LR/RF/XGBoost) with GridSearchCV, auto-selects best model
- `src/clustering.py` — `ClusterAnalyzer` class: K-Means + K-Prototypes + stability testing via Rand Index
- `src/association_rules.py` — `AssociationRuleMiner` class: FP-Growth/Apriori via mlxtend
- `src/explainability.py` — SHAP (LinearExplainer for LR, TreeExplainer for RF/XGBoost)
- `src/api.py` — FastAPI app (prediction + health endpoints)
- `src/api_v2.py` — Analytics REST API (summary, clusters, rules, importance, distributions)
- `src/model_service.py` — Singleton model loader shared across API endpoints
- `src/visualization.py` — Matplotlib/Plotly static chart generation
- `src/config/settings.py` — Configuration dataclass (no `__init__.py` in `src/config/` — namespace package)
- `src/utils/performance.py` — `@monitor_performance` decorator (time + memory tracking)

**Frontend (Vue3 SPA)**:
- `src/views/` — 5 pages: OverviewView, PredictionView, SegmentationView, FeaturesView, RulesView
- `src/components/chart/useECharts.ts` — Shared composable for ECharts lifecycle (init/resize/dispose)
- `src/styles/chartTheme.ts` — ECharts gradient constants (`FOREST_GREEN_GRADIENT`, `AMBER_RED_GRADIENT`, etc.)
- `src/styles/tokens.css` — Design tokens (30+ CSS custom properties)
- `src/api/index.ts` — Axios wrapper with TypeScript types

**Data files** (all gitignored):
- `data/customer_churn_data.xlsx` — 901 rows × 19 columns
- `data/sales.csv` — auxiliary sales data
- `output/models/churn_model.pkl` — trained model artifact
- `output/results/*.json` — pre-computed analytics (served by API with zero compute cost)

## Important Constraints

### Vue Template Editing Rules (红线)
When modifying Vue SFC files in `frontend/src/views/`:
- **DO NOT modify `<script setup>` logic** — only template and scoped CSS
- **DO NOT break TypeScript types** — all template variables must match existing type definitions
- **DO NOT change API request structures** — existing endpoints and request/response formats are fixed
- ECharts visual parameters (colors, gradients, sizes) are safe to modify

### Pandas 3.x Compatibility
String columns can have `'string'` dtype instead of `'object'` in pandas 2.2+/3.x. When checking column types, use `pd.api.types.is_numeric_dtype()` instead of `dtype in ['object', 'category']`. Similarly, `select_dtypes(include=['object', 'category'])` should include `'string'` for full coverage.

### Git-Ignored Content
- `data/*.xlsx`, `data/*.csv`, `data/processed/` — data files (privacy + size)
- `output/models/*`, `output/results/*`, `output/visualizations/*` — generated outputs
- `.claude/`, `frontend/.agents/`, `frontend/skills-lock.json` — Claude Code internal files
- `screenshots/` — screenshots kept locally only
- `PROJECT_STATUS.md` — local project tracking

## Testing

Tests use synthetic data from `tests/conftest.py` (200 rows via `np.random.RandomState(42)`). No real data file needed for test runs.

- `tests/test_data_loader.py` — DataLoader unit tests
- `tests/test_feature_engineering.py` — FeatureEngineer (encoding strategies, missing values)
- `tests/test_clustering.py` — ClusterAnalyzer (K-Means, stability, characteristics)
- `tests/test_prediction.py` — ChurnPredictor (train, evaluate, predict, save/load)
- `tests/test_api.py` — FastAPI endpoints (root, health, predict — skips predict if no model file)
- `tests/performance_test.py` — Performance benchmarks (class `PerformanceTester`, not auto-collected by pytest due to class name pattern `Test*`)

## CI (GitHub Actions)

`.github/workflows/ci.yml` — Test matrix (Python 3.11, 3.12), performance test, Docker build verification.
- Uses `PYTHONPATH: .` for imports
- No data file needed (tests generate synthetic data)
- Docker test uses `--no-visualization --skip-prediction` to run without data
- `fail-fast: false` for independent matrix jobs

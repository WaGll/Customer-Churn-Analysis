"""
客户流失预测模块 - 多分类器集成与自动模型选择

支持:
- Logistic Regression (线性基线)
- Random Forest (集成方法)
- XGBoost (梯度提升)

自动完成:
- Train/Test 分层拆分
- Stratified K-Fold 交叉验证
- GridSearchCV 超参数调优
- 多指标评估与最佳模型自动选择
- 模型持久化与评估结果导出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import json
import pickle
from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV,
    cross_val_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# XGBoost 为可选依赖
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:  # pragma: no cover
    XGB_AVAILABLE = False

import plotly.graph_objects as go
import plotly.io as pio

from config.settings import config
from utils.performance import monitor_performance

# 设置 Plotly 默认主题（与项目保持一致）
pio.templates.default = "plotly_white"

logger = logging.getLogger(__name__)


class ChurnPredictor:
    """客户流失预测器 - 多模型训练、评估与自动选择"""

    def __init__(self, random_state: int = None):
        """
        初始化预测器

        Args:
            random_state: 随机种子，默认使用全局配置
        """
        if random_state is None:
            random_state = config.data.random_seed
        self.random_state = random_state
        self.models: Dict[str, Pipeline] = {}
        self.best_model: Optional[Pipeline] = None
        self.best_model_name: Optional[str] = None
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.cv_results: Dict[str, Any] = {}
        self.feature_names: List[str] = []
        self._preprocessor: Optional[ColumnTransformer] = None
        self._X_train: Optional[np.ndarray] = None
        self._X_test: Optional[np.ndarray] = None
        self._y_train: Optional[np.ndarray] = None
        self._y_test: Optional[np.ndarray] = None
        self._y_prob_train: Dict[str, np.ndarray] = {}
        self._y_prob_test: Dict[str, np.ndarray] = {}

    # ── 数据准备 ──────────────────────────────────────────────

    @monitor_performance
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str = "用户流失标签",
        test_size: float = 0.2,
        id_cols: Optional[List[str]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        准备训练和测试数据

        自动识别数值/分类列，构建 ColumnTransformer 预处理管道，
        分层拆分后返回训练/测试集。

        Args:
            df: 原始数据 DataFrame
            target_col: 目标列名（流失标签）
            test_size: 测试集比例
            id_cols: 需要丢弃的 ID 列名列表

        Returns:
            (X_train, X_test, y_train, y_test)
        """
        logger.info("开始数据准备...")

        # 1. 复制数据，避免副作用
        data = df.copy()

        # 2. 丢弃 ID 列
        if id_cols is None:
            id_cols = ["顾客ID"] if "顾客ID" in data.columns else []
        drop_cols = [c for c in id_cols if c in data.columns]
        if drop_cols:
            data = data.drop(columns=drop_cols)
            logger.info(f"丢弃 ID 列: {drop_cols}")

        # 3. 验证目标列存在
        if target_col not in data.columns:
            raise KeyError(f"目标列 '{target_col}' 不存在于数据中。可用列: {list(data.columns)}")

        # 4. 分离特征和标签
        y = data[target_col].copy()
        X = data.drop(columns=[target_col])

        # 确保 y 为整数类型
        y = y.astype(int)

        self.feature_names = list(X.columns)
        logger.info(f"特征数: {len(self.feature_names)}, 样本数: {len(X)}")
        logger.info(f"正样本(流失)比例: {y.mean():.2%}")

        # 5. 识别列类型
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

        logger.info(f"数值特征: {len(numeric_cols)}, 分类特征: {len(categorical_cols)}")

        # 6. 构建预处理器
        transformers = []
        if numeric_cols:
            transformers.append(("num", StandardScaler(), numeric_cols))
        if categorical_cols:
            transformers.append(
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop="first"),
                 categorical_cols)
            )

        self._preprocessor = ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)

        # 7. 分层拆分
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=y,
            random_state=self.random_state,
            shuffle=True,
        )

        logger.info(f"训练集: {len(X_train)} 样本, 测试集: {len(X_test)} 样本")
        logger.info(f"训练集正样本比例: {y_train.mean():.2%}, 测试集正样本比例: {y_test.mean():.2%}")

        # 8. 拟合并转换（只在训练集上 fit）
        X_train_transformed = self._preprocessor.fit_transform(X_train)
        X_test_transformed = self._preprocessor.transform(X_test)

        # 9. 保存预处理后的特征名
        try:
            self.feature_names = list(self._preprocessor.get_feature_names_out())
        except Exception:
            pass

        self._X_train = X_train_transformed
        self._X_test = X_test_transformed
        self._y_train = y_train.values if hasattr(y_train, "values") else y_train
        self._y_test = y_test.values if hasattr(y_test, "values") else y_test

        logger.info(f"预处理后特征维度: {self._X_train.shape[1]}")
        logger.info("数据准备完成")

        return self._X_train, self._X_test, self._y_train, self._y_test

    # ── 模型训练 ──────────────────────────────────────────────

    @monitor_performance
    def train_models(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        cv_folds: int = 5,
        n_jobs: int = None,
        verbose: int = 0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        训练所有候选模型并使用 GridSearchCV 调优

        Args:
            X: 特征矩阵（如未提供则使用 prepare_data 的结果）
            y: 标签向量
            cv_folds: 交叉验证折数
            n_jobs: 并行任务数
            verbose: GridSearchCV 详细程度

        Returns:
            Dict: 各模型的最佳参数和交叉验证分数
        """
        if X is None:
            if self._X_train is None:
                raise RuntimeError("请先调用 prepare_data() 或传入 X, y 参数")
            X = self._X_train
            y = self._y_train

        if n_jobs is None:
            n_jobs = config.algorithm.n_jobs if config.algorithm.n_jobs > 0 else 1

        logger.info(f"开始模型训练 (CV={cv_folds}, n_jobs={n_jobs})...")

        # 定义模型候选集
        candidates: Dict[str, Tuple[Any, Dict[str, List[Any]]]] = {}

        # ── Logistic Regression ──
        lr_param_grid = {
            "classifier__C": [0.01, 0.1, 1.0, 10.0],
            "classifier__penalty": ["l2"],
            "classifier__solver": ["lbfgs", "liblinear"],
            "classifier__max_iter": [2000],
        }
        candidates["LogisticRegression"] = (
            LogisticRegression(random_state=self.random_state),
            lr_param_grid,
        )

        # ── Random Forest ──
        rf_param_grid = {
            "classifier__n_estimators": [100, 200, 300],
            "classifier__max_depth": [5, 10, 15, None],
            "classifier__min_samples_split": [2, 5, 10],
            "classifier__class_weight": ["balanced", None],
        }
        candidates["RandomForest"] = (
            RandomForestClassifier(random_state=self.random_state),
            rf_param_grid,
        )

        # ── XGBoost ──
        if XGB_AVAILABLE:
            xgb_param_grid = {
                "classifier__n_estimators": [100, 200, 300],
                "classifier__max_depth": [3, 6, 9],
                "classifier__learning_rate": [0.01, 0.1, 0.3],
                "classifier__subsample": [0.8, 1.0],
                "classifier__scale_pos_weight": [1, max(1.0, float((1 - y.mean()) / max(y.mean(), 0.001)))],
            }
            candidates["XGBoost"] = (
                xgb.XGBClassifier(
                    random_state=self.random_state,
                    eval_metric="logloss",
                    use_label_encoder=False,
                ),
                xgb_param_grid,
            )
        else:
            logger.warning("XGBoost 未安装，跳过 XGBoost 模型训练。安装方法: pip install xgboost")

        # 定义 CV 策略
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)

        # 训练每个模型
        for model_name, (estimator, param_grid) in candidates.items():
            logger.info(f"[{model_name}] 开始 GridSearchCV (参数组合数 ≈ {self._count_combinations(param_grid)})...")
            start = time.time()

            # 限制搜索组合数（随机采样），避免搜索空间过大
            param_grid_reduced = self._reduce_param_grid(param_grid, max_combinations=24)

            pipeline = Pipeline([
                ("classifier", estimator),
            ])

            gs = GridSearchCV(
                pipeline,
                param_grid_reduced,
                cv=cv,
                scoring="roc_auc",
                n_jobs=n_jobs,
                verbose=verbose,
                refit=True,
            )
            gs.fit(X, y)

            elapsed = time.time() - start

            # 记录结果
            self.models[model_name] = gs.best_estimator_
            self.cv_results[model_name] = {
                "best_params": self._serialize_params(gs.best_params_),
                "best_cv_score": float(gs.best_score_),
                "cv_mean": float(gs.cv_results_["mean_test_score"].mean()),
                "cv_std": float(gs.cv_results_["mean_test_score"].std()),
                "n_combinations_tested": len(gs.cv_results_["params"]),
                "train_time_seconds": round(elapsed, 2),
            }

            logger.info(
                f"[{model_name}] 完成 - best CV AUC={gs.best_score_:.4f}, "
                f"耗时={elapsed:.1f}s, best_params={self._serialize_params(gs.best_params_)}"
            )

        logger.info(f"模型训练完成，共训练 {len(self.models)} 个模型")
        return self.cv_results

    # ── 模型评估 ──────────────────────────────────────────────

    @monitor_performance
    def evaluate_models(
        self,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        在测试集上评估所有模型，自动选择最佳模型

        Args:
            X_test: 测试集特征
            y_test: 测试集标签

        Returns:
            Dict: 各模型的评估指标
        """
        if X_test is None:
            X_test = self._X_test
        if y_test is None:
            y_test = self._y_test

        if X_test is None or y_test is None:
            raise RuntimeError("请先调用 prepare_data() 或传入 X_test, y_test 参数")

        if not self.models:
            raise RuntimeError("请先调用 train_models() 训练模型")

        logger.info("开始模型评估...")

        best_auc = -1.0
        self._y_prob_test = {}

        for model_name, pipeline in self.models.items():
            # 预测
            y_pred = pipeline.predict(X_test)
            y_prob = pipeline.predict_proba(X_test)[:, 1]

            self._y_prob_test[model_name] = y_prob

            # 计算所有指标
            metrics = {
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "classification_report": classification_report(y_test, y_pred, output_dict=True),
                "best_params": self.cv_results.get(model_name, {}).get("best_params", {}),
            }

            self.metrics[model_name] = metrics

            # 更新最佳模型
            if metrics["roc_auc"] > best_auc:
                best_auc = metrics["roc_auc"]
                self.best_model = pipeline
                self.best_model_name = model_name

            logger.info(
                f"[{model_name}] "
                f"Acc={metrics['accuracy']:.4f} "
                f"Prec={metrics['precision']:.4f} "
                f"Rec={metrics['recall']:.4f} "
                f"F1={metrics['f1']:.4f} "
                f"AUC={metrics['roc_auc']:.4f}"
            )

        logger.info(f"🏆 最佳模型: {self.best_model_name} (ROC-AUC={best_auc:.4f})")

        return self.metrics

    # ── ROC 曲线 ──────────────────────────────────────────────

    def plot_roc_curves(
        self,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        生成交互式 ROC 曲线对比图 (Plotly HTML)

        Args:
            X_test: 测试集特征
            y_test: 测试集标签
            output_path: 输出文件路径

        Returns:
            str: 生成的 HTML 文件路径
        """
        if X_test is None:
            X_test = self._X_test
        if y_test is None:
            y_test = self._y_test

        if X_test is None or y_test is None:
            raise RuntimeError("请先调用 prepare_data()")

        if not self._y_prob_test:
            raise RuntimeError("请先调用 evaluate_models() 以生成预测概率")

        if output_path is None:
            vis_dir = Path(__file__).resolve().parents[1] / "output" / "visualizations"
            vis_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(vis_dir / "roc_curve.html")

        logger.info("生成 ROC 曲线对比图...")

        fig = go.Figure()

        # 颜色方案
        colors = {"LogisticRegression": "#1f77b4", "RandomForest": "#2ca02c", "XGBoost": "#ff7f0e"}

        for model_name, y_prob in self._y_prob_test.items():
            fpr, tpr, thresholds = roc_curve(y_test, y_prob)
            auc = self.metrics[model_name]["roc_auc"]

            fig.add_trace(
                go.Scatter(
                    x=fpr,
                    y=tpr,
                    mode="lines",
                    name=f"{model_name} (AUC={auc:.4f})",
                    line=dict(color=colors.get(model_name, "#333333"), width=2),
                    hovertemplate="FPR=%{x:.3f}<br>TPR=%{y:.3f}<extra></extra>",
                )
            )

        # 对角线
        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="随机分类器 (AUC=0.50)",
                line=dict(color="gray", width=1, dash="dash"),
                showlegend=True,
            )
        )

        fig.update_layout(
            title={
                "text": "ROC Curves — 模型对比",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18},
            },
            xaxis_title="False Positive Rate (1 - Specificity)",
            yaxis_title="True Positive Rate (Sensitivity)",
            width=800,
            height=600,
            legend=dict(x=0.65, y=0.05, bgcolor="rgba(255,255,255,0.8)", bordercolor="#ddd"),
            hovermode="x unified",
            template="plotly_white",
        )

        fig.write_html(output_path)
        logger.info(f"ROC 曲线已保存: {output_path}")

        return output_path

    # ── 持久化 ────────────────────────────────────────────────

    def save_model(self, output_path: Optional[str] = None) -> str:
        """
        保存最佳模型到磁盘

        Args:
            output_path: 输出文件路径

        Returns:
            str: 保存的文件路径
        """
        if self.best_model is None:
            raise RuntimeError("尚未训练或选择最佳模型，请先调用 train_models() + evaluate_models()")

        if output_path is None:
            model_dir = Path(__file__).resolve().parents[1] / "output" / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(model_dir / "churn_model.pkl")

        model_data = {
            "model": self.best_model,
            "model_name": self.best_model_name,
            "metrics": self.metrics.get(self.best_model_name, {}),
            "feature_names": self.feature_names,
            "preprocessor": self._preprocessor,
            "random_state": self.random_state,
        }

        with open(output_path, "wb") as f:
            pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        logger.info(f"模型已保存: {output_path} (类型: {self.best_model_name})")
        return output_path

    def save_metrics(self, output_path: Optional[str] = None) -> str:
        """
        保存模型评估指标到 JSON

        Args:
            output_path: 输出文件路径

        Returns:
            str: 保存的文件路径
        """
        if not self.metrics:
            raise RuntimeError("尚未评估模型，请先调用 evaluate_models()")

        if output_path is None:
            results_dir = Path(__file__).resolve().parents[1] / "output" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(results_dir / "model_metrics.json")

        # 构建报告
        report = {
            "best_model": self.best_model_name,
            "train_info": {
                "train_size": int(len(self._y_train)) if self._y_train is not None else None,
                "test_size": int(len(self._y_test)) if self._y_test is not None else None,
                "cv_folds": 5,
                "n_features": len(self.feature_names),
                "features": self.feature_names[:50],
            },
            "models": {},
        }

        for model_name, model_metrics in self.metrics.items():
            report["models"][model_name] = {
                "accuracy": model_metrics["accuracy"],
                "precision": model_metrics["precision"],
                "recall": model_metrics["recall"],
                "f1": model_metrics["f1"],
                "roc_auc": model_metrics["roc_auc"],
                "confusion_matrix": model_metrics["confusion_matrix"],
                "best_params": model_metrics.get("best_params", {}),
            }

        # 添加 CV 信息
        if self.cv_results:
            report["cross_validation"] = {}
            for model_name, cv_info in self.cv_results.items():
                report["cross_validation"][model_name] = {
                    "best_cv_auc": cv_info["best_cv_score"],
                    "cv_mean_auc": cv_info["cv_mean"],
                    "cv_std_auc": cv_info["cv_std"],
                    "n_combinations_tested": cv_info["n_combinations_tested"],
                    "train_time_seconds": cv_info["train_time_seconds"],
                }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"评估指标已保存: {output_path}")
        return output_path

    # ── 全流程运行 ────────────────────────────────────────────

    @monitor_performance
    def run(
        self,
        df: pd.DataFrame,
        target_col: str = "用户流失标签",
        test_size: float = 0.2,
        cv_folds: int = 5,
        n_jobs: int = None,
        output_model_path: Optional[str] = None,
        output_metrics_path: Optional[str] = None,
        output_roc_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        一键运行完整的预测建模流程

        Args:
            df: 原始数据 DataFrame
            target_col: 目标列名
            test_size: 测试集比例
            cv_folds: 交叉验证折数
            n_jobs: 并行任务数
            output_model_path: 模型保存路径
            output_metrics_path: 指标保存路径
            output_roc_path: ROC 曲线保存路径

        Returns:
            Dict: 包含最佳模型名、指标和文件路径的摘要
        """
        logger.info("=" * 60)
        logger.info("客户流失预测建模启动")
        logger.info("=" * 60)

        # Step 1: 数据准备
        self.prepare_data(df, target_col=target_col, test_size=test_size)

        # Step 2: 模型训练
        self.train_models(cv_folds=cv_folds, n_jobs=n_jobs)

        # Step 3: 模型评估
        self.evaluate_models()

        # Step 4: ROC 曲线
        roc_path = self.plot_roc_curves(output_path=output_roc_path)

        # Step 5: 保存模型
        model_path = self.save_model(output_path=output_model_path)

        # Step 6: 保存指标
        metrics_path = self.save_metrics(output_path=output_metrics_path)

        # 构建摘要
        summary = {
            "best_model": self.best_model_name,
            "best_metrics": self.metrics[self.best_model_name],
            "all_metrics": self.metrics,
            "model_path": model_path,
            "metrics_path": metrics_path,
            "roc_path": roc_path,
        }

        logger.info("=" * 60)
        logger.info(f"🏆 最终结果: 最佳模型 = {self.best_model_name}")
        logger.info(f"   ROC-AUC = {self.metrics[self.best_model_name]['roc_auc']:.4f}")
        logger.info(f"   F1-Score = {self.metrics[self.best_model_name]['f1']:.4f}")
        logger.info(f"   Recall  = {self.metrics[self.best_model_name]['recall']:.4f}")
        logger.info(f"   模型文件: {model_path}")
        logger.info(f"   指标文件: {metrics_path}")
        logger.info(f"   ROC 曲线: {roc_path}")
        logger.info("=" * 60)

        return summary

    def predict(self, X: np.ndarray) -> np.ndarray:
        """使用最佳模型预测类别"""
        if self.best_model is None:
            raise RuntimeError("模型尚未训练")
        return self.best_model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """使用最佳模型预测流失概率"""
        if self.best_model is None:
            raise RuntimeError("模型尚未训练")
        return self.best_model.predict_proba(X)[:, 1]

    # ── 内部工具方法 ──────────────────────────────────────────

    @staticmethod
    def _count_combinations(param_grid: Dict[str, List[Any]]) -> int:
        """计算参数组合总数"""
        count = 1
        for values in param_grid.values():
            count *= len(values)
        return count

    @staticmethod
    def _reduce_param_grid(
        param_grid: Dict[str, List[Any]], max_combinations: int = 24
    ) -> Dict[str, List[Any]]:
        """
        缩减参数网格——当组合数过多时，对连续型参数做降采样

        Args:
            param_grid: 原始参数网格
            max_combinations: 最大允许组合数

        Returns:
            Dict: 缩减后的参数网格
        """
        total = 1
        for v in param_grid.values():
            total *= len(v)

        if total <= max_combinations:
            return param_grid

        # 策略：缩小样本数最多的那个参数维度
        reduced = dict(param_grid)
        sorted_keys = sorted(param_grid.keys(), key=lambda k: len(param_grid[k]), reverse=True)
        for key in sorted_keys:
            if len(reduced[key]) > 2:
                step = max(1, len(reduced[key]) // max_combinations)
                reduced[key] = reduced[key][::step]
                # 确保至少保留首尾
                if len(reduced[key]) < 2:
                    reduced[key] = [param_grid[key][0], param_grid[key][-1]]

            # 重新计算组合数
            total = 1
            for v in reduced.values():
                total *= len(v)
            if total <= max_combinations:
                break

        logger.info(f"参数组合数从 {ChurnPredictor._count_combinations(param_grid)} 缩减至 {total}")
        return reduced

    @staticmethod
    def _serialize_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """将 sklearn 参数序列化为 JSON 兼容格式"""
        result = {}
        for k, v in params.items():
            # 去掉 "classifier__" 前缀
            clean_key = k.replace("classifier__", "")
            if isinstance(v, (int, float, str, bool, type(None))):
                result[clean_key] = v
            else:
                result[clean_key] = str(v)
        return result

    @classmethod
    def load_model(cls, model_path: str) -> "ChurnPredictor":
        """
        加载已保存的模型，返回配置好的 ChurnPredictor 实例

        Args:
            model_path: pickle 模型文件路径

        Returns:
            ChurnPredictor: 已加载模型的预测器实例
        """
        logger.info(f"加载模型: {model_path}")

        with open(model_path, "rb") as f:
            model_data = pickle.load(f)

        predictor = cls(random_state=model_data.get("random_state", 42))
        predictor.best_model = model_data["model"]
        predictor.best_model_name = model_data["model_name"]
        predictor.metrics = {model_data["model_name"]: model_data["metrics"]}
        predictor.feature_names = model_data["feature_names"]
        predictor._preprocessor = model_data.get("preprocessor")

        logger.info(f"模型加载成功: {model_data['model_name']} (ROC-AUC={model_data['metrics']['roc_auc']:.4f})")

        return predictor

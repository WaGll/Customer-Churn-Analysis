"""
模型可解释性模块 — SHAP 分析与可视化

支持:
- TreeExplainer (RandomForest / XGBoost)
- LinearExplainer (LogisticRegression)
- SHAP 摘要图、特征重要性图、依赖图
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

# SHAP 为可选依赖
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:  # pragma: no cover
    SHAP_AVAILABLE = False

from src.config.settings import config

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)


class ModelExplainer:
    """模型可解释性分析器 — 基于 SHAP"""

    def __init__(self, output_dir: str = None):
        """
        Args:
            output_dir: 图表输出目录
        """
        if output_dir is None:
            output_dir = str(
                Path(__file__).resolve().parents[1] / "output" / "visualizations"
            )
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._explainer = None
        self._shap_values = None

    def explain(
        self,
        model: Any,
        X: np.ndarray,
        feature_names: List[str],
        model_type: str = "tree",
        max_display: int = 15,
    ) -> Dict[str, str]:
        """
        对模型进行 SHAP 解释并生成图表

        Args:
            model: 已训练的 sklearn 模型或 Pipeline
            X: 特征矩阵（样本数不超过 200 以避免性能问题）
            feature_names: 特征名列表
            model_type: 模型类型 — "tree", "linear", "auto"
            max_display: 摘要图最多显示的特征数

        Returns:
            Dict: 生成的图像文件路径
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP 未安装，跳过硬解释。安装方法: pip install shap")
            return {}

        logger.info(f"开始 SHAP 分析 (type={model_type}, samples={len(X)})...")

        # 若 Pipeline，提取最终分类器
        if hasattr(model, "named_steps") and "classifier" in model.named_steps:
            estimator = model.named_steps["classifier"]
        else:
            estimator = model

        # 采样以避免性能问题
        if len(X) > 200:
            rng = np.random.RandomState(config.data.random_seed)
            indices = rng.choice(len(X), 200, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X

        # 选择 explainer
        if model_type == "auto":
            if hasattr(estimator, "feature_importances_"):
                model_type = "tree"
            elif hasattr(estimator, "coef_"):
                model_type = "linear"
            else:
                model_type = "tree"

        try:
            if model_type == "tree":
                self._explainer = shap.TreeExplainer(estimator)
                self._shap_values = self._explainer.shap_values(X_sample)
                # TreeExplainer 对二分类返回 [neg, pos] 列表
                if isinstance(self._shap_values, list):
                    self._shap_values = self._shap_values[1]
            elif model_type == "linear":
                # 用少量样本做背景
                bg_size = min(50, len(X_sample))
                background = X_sample[:bg_size]
                self._explainer = shap.LinearExplainer(estimator, background)
                self._shap_values = self._explainer.shap_values(X_sample)
            else:
                logger.error(f"不支持的模型类型: {model_type}")
                return {}
        except Exception as e:
            logger.error(f"SHAP 分析失败: {e}")
            return {}

        # 生成图表
        outputs = {}

        # 1. SHAP 摘要图
        outputs["summary"] = self._plot_summary(
            X_sample, feature_names, max_display
        )

        # 2. 特征重要性条形图
        outputs["importance"] = self._plot_importance(
            X_sample, feature_names, max_display
        )

        # 3. 关键特征依赖图 (top-1 特征)
        outputs["dependence"] = self._plot_dependence(
            X_sample, feature_names
        )

        logger.info(f"SHAP 图表已生成: {list(outputs.values())}")
        return outputs

    def _plot_summary(
        self, X: np.ndarray, feature_names: List[str], max_display: int
    ) -> str:
        """SHAP 摘要散点图"""
        plt.figure(figsize=(10, 8))
        shap.summary_plot(
            self._shap_values,
            X,
            feature_names=feature_names,
            max_display=max_display,
            show=False,
        )
        path = os.path.join(self.output_dir, "shap_summary.png")
        plt.savefig(path, dpi=config.visualization.dpi, bbox_inches='tight')
        plt.close()
        logger.info(f"SHAP 摘要图: {path}")
        return path

    def _plot_importance(
        self, X: np.ndarray, feature_names: List[str], max_display: int
    ) -> str:
        """SHAP 特征重要性条形图"""
        plt.figure(figsize=(10, 8))
        shap.summary_plot(
            self._shap_values,
            X,
            feature_names=feature_names,
            max_display=max_display,
            plot_type="bar",
            show=False,
        )
        path = os.path.join(self.output_dir, "shap_feature_importance.png")
        plt.savefig(path, dpi=config.visualization.dpi, bbox_inches='tight')
        plt.close()
        logger.info(f"SHAP 特征重要性: {path}")
        return path

    def _plot_dependence(
        self, X: np.ndarray, feature_names: List[str]
    ) -> str:
        """Top-1 特征的 SHAP 依赖图"""
        # 找到最重要的特征索引
        mean_abs_shap = np.abs(self._shap_values).mean(axis=0)
        top_idx = int(np.argmax(mean_abs_shap))
        top_name = feature_names[top_idx] if top_idx < len(feature_names) else f"Feature_{top_idx}"

        plt.figure(figsize=(10, 6))
        shap.dependence_plot(
            top_idx,
            self._shap_values,
            X,
            feature_names=feature_names,
            show=False,
        )
        path = os.path.join(self.output_dir, "shap_dependence.png")
        plt.savefig(path, dpi=config.visualization.dpi, bbox_inches='tight')
        plt.close()
        logger.info(f"SHAP 依赖图 (top feature: {top_name}): {path}")
        return path

    def get_top_features(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        返回 Top-N 重要特征及平均 SHAP 值

        Args:
            n: 返回特征数量

        Returns:
            List[Dict]: 特征重要性排名
        """
        if self._shap_values is None:
            return []

        mean_abs_shap = np.abs(self._shap_values).mean(axis=0)
        indices = np.argsort(mean_abs_shap)[::-1][:n]

        result = []
        for rank, idx in enumerate(indices, 1):
            result.append({
                "rank": rank,
                "feature_index": int(idx),
                "mean_abs_shap": float(mean_abs_shap[idx]),
            })
        return result

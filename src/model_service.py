"""
共享模型服务 — api.py 和 api_v2.py 的公共依赖

将 _load_predictor 和 _compute_risk_level 从 api.py 提取到此独立模块，
消除 api.py ↔ api_v2.py 之间的循环导入。
"""

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parents[1] / "output" / "models" / "churn_model.pkl"

_predictor = None
_feature_names: List[str] = []


def get_predictor():
    """加载预测模型（带模块级缓存），返回 (predictor, feature_names) 元组"""
    global _predictor, _feature_names

    if _predictor is not None:
        return _predictor, _feature_names

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"模型文件不存在: {MODEL_PATH}\n"
            f"请先运行预测建模: python run_prediction.py 或 python run_analysis.py"
        )

    from src.prediction import ChurnPredictor

    _predictor = ChurnPredictor.load_model(str(MODEL_PATH))
    _feature_names = _predictor.feature_names

    logger.info(
        "模型已加载: %s (ROC-AUC=%.4f)",
        _predictor.best_model_name,
        _predictor.metrics[_predictor.best_model_name]["roc_auc"],
    )

    return _predictor, _feature_names


def compute_risk_level(probability: float) -> str:
    """根据流失概率确定风险等级"""
    if probability < 0.3:
        return "low"
    elif probability < 0.6:
        return "medium"
    elif probability < 0.8:
        return "high"
    else:
        return "critical"


def invalidate_cache():
    """清除模型缓存（测试用）"""
    global _predictor, _feature_names
    _predictor = None
    _feature_names = []

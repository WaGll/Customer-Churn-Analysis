#!/usr/bin/env python3
"""
生成 SHAP 特征重要性数据并保存为 JSON

在 run_analysis.py 之后运行，将 SHAP 值保存到 output/results/shap_importance.json
"""

import sys
import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# 检查 shap 是否可用
try:
    import shap
except ImportError:
    print("❌ shap 未安装，请先运行: pip install shap")
    sys.exit(1)

from src.data_loader import DataLoader
from src.feature_engineering import FeatureEngineer


def main():
    # 路径
    data_path = PROJECT_ROOT / "data" / "customer_churn_data.xlsx"
    model_path = PROJECT_ROOT / "output" / "models" / "churn_model.pkl"
    output_path = PROJECT_ROOT / "output" / "results" / "shap_importance.json"

    # 1. 加载模型
    print("Loading model...")
    with open(model_path, "rb") as f:
        model_data = pickle.load(f)

    pipeline = model_data["model"]
    model_name = model_data.get("model_name", "Unknown")
    feature_names = model_data.get("feature_names", [])

    print(f"  Model: {model_name}")
    print(f"  Features: {len(feature_names)}")

    # 2. 加载并预处理数据
    print("Loading data...")
    loader = DataLoader()
    df = loader.load_data(str(data_path))

    # 特征工程（只生成 one_hot）
    engineer = FeatureEngineer()
    datasets = engineer.preprocess_data(df)
    df_encoded = datasets["one_hot"]

    # 准备 X
    target_col = "用户流失标签"
    if target_col in df_encoded.columns:
        X = df_encoded.drop(columns=[target_col])
    else:
        X = df_encoded

    # 确保列顺序与训练时一致
    if len(feature_names) == X.shape[1]:
        X = X[feature_names]
    X_array = X.values.astype(float)

    # 采样
    if len(X_array) > 200:
        rng = np.random.RandomState(42)
        indices = rng.choice(len(X_array), 200, replace=False)
        X_sample = X_array[indices]
    else:
        X_sample = X_array

    # 3. 提取 estimator
    if hasattr(pipeline, "named_steps") and "classifier" in pipeline.named_steps:
        estimator = pipeline.named_steps["classifier"]
    else:
        estimator = pipeline

    # 4. SHAP 分析
    print("Computing SHAP values...")

    if hasattr(estimator, "feature_importances_"):
        # 树模型
        explainer = shap.TreeExplainer(estimator)
        shap_values = explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        shap_type = "TreeExplainer"
    elif hasattr(estimator, "coef_"):
        # 线性模型
        bg_size = min(50, len(X_sample))
        background = X_sample[:bg_size]
        explainer = shap.LinearExplainer(estimator, background)
        shap_values = explainer.shap_values(X_sample)
        shap_type = "LinearExplainer"
    else:
        print("❌ 无法确定 SHAP explainer 类型")
        sys.exit(1)

    print(f"  Explainer: {shap_type}")
    print(f"  SHAP values shape: {shap_values.shape}")

    # 5. 计算特征重要性
    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    # 按 SHAP 值排序
    ranked = sorted(
        enumerate(mean_abs_shap),
        key=lambda x: x[1],
        reverse=True,
    )

    features = []
    for rank, (idx, shap_val) in enumerate(ranked, 1):
        feat_name = feature_names[idx] if idx < len(feature_names) else f"Feature_{idx}"
        features.append({
            "rank": rank,
            "name": feat_name,
            "shap_mean_abs": round(float(shap_val), 6),
        })

    # 6. 保存
    result = {
        "model_name": model_name,
        "explainer_type": shap_type,
        "n_samples": len(X_sample),
        "n_features": len(feature_names),
        "features": features,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ SHAP 特征重要性已保存: {output_path}")
    print(f"   Top-5 特征:")
    for feat in features[:5]:
        print(f"   {feat['rank']}. {feat['name']}: {feat['shap_mean_abs']:.6f}")


if __name__ == "__main__":
    main()

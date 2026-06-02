"""
API v2 — 数据分析展示端点

为 Vue3 前端提供数据摘要、模型指标、特征重要性、聚类、关联规则等只读端点。
所有端点优先读取已计算好的 output/results/*.json，零计算开销。
"""

import json
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

# 缓存数据读取，避免每次 API 调用都重新解析 Excel
from functools import lru_cache as _lru_cache


@_lru_cache(maxsize=1)
def _load_cached_data():
    """加载 Excel 数据并缓存（仅首次调用时读取文件）"""
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_PATH = PROJECT_ROOT / "data" / "customer_churn_data.xlsx"
    if not DATA_PATH.exists():
        raise HTTPException(404, f"数据文件不存在: {DATA_PATH}")
    df = pd.read_excel(DATA_PATH)
    if "顾客ID" in df.columns:
        df = df.drop(columns=["顾客ID"])
    return df


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "customer_churn_data.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = OUTPUT_DIR / "results"
MODELS_DIR = OUTPUT_DIR / "models"


def _load_json(filename: str) -> dict:
    """加载 JSON 文件，不存在时抛出 404"""
    path = RESULTS_DIR / filename
    if not path.exists():
        raise HTTPException(
            404,
            f"结果文件 {filename} 不存在，请先运行 python run_analysis.py",
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _bin_tenure(months: int) -> str:
    """将使用月数分箱"""
    if months <= 1:
        return "0-1月"
    elif months <= 3:
        return "2-3月"
    elif months <= 6:
        return "4-6月"
    elif months <= 12:
        return "7-12月"
    else:
        return "12月以上"


# ── 数据摘要 ──────────────────────────────────────────────────


@router.get("/summary")
async def get_summary():
    """
    整体数据摘要：客户数、流失率、折扣均值、高风险客户数、
    使用时长流失分布、各类别流失率
    """
    try:
        df = _load_cached_data()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"数据加载失败: {str(e)}")

    churn_col = "用户流失标签"
    total = len(df)
    churn_rate = float(df[churn_col].mean()) if churn_col in df.columns else 0.0
    churned_count = int(df[churn_col].sum()) if churn_col in df.columns else 0

    discount_col = "上月平均折扣金额"
    avg_discount = float(df[discount_col].mean()) if discount_col in df.columns else 0.0

    # 使用时长流失分布
    tenure_col = "使用平台时间_月"
    tenure_dist = []
    if tenure_col in df.columns and churn_col in df.columns:
        df_temp = df.copy()
        df_temp["tenure_bin"] = df_temp[tenure_col].apply(_bin_tenure)
        for bin_name, grp in df_temp.groupby("tenure_bin"):
            tenure_dist.append({
                "tenure_bin": bin_name,
                "total": len(grp),
                "churned": int(grp[churn_col].sum()),
                "churn_rate": round(float(grp[churn_col].mean()), 4),
            })

    # 各类别流失率
    category_col = "上月客户的首选订单类别"
    cat_churn = []
    if category_col in df.columns and churn_col in df.columns:
        for cat, grp in df.groupby(category_col):
            if len(grp) >= 5:
                cat_churn.append({
                    "category": str(cat),
                    "churn_rate": round(float(grp[churn_col].mean()), 4),
                })
        cat_churn.sort(key=lambda x: -x["churn_rate"])

    return {
        "total_customers": total,
        "churn_rate": round(churn_rate, 4),
        "avg_discount": round(avg_discount, 1),
        "churned_count": churned_count,
        "tenure_churn_distribution": tenure_dist,
        "category_churn": cat_churn,
    }


# ── 模型指标 ──────────────────────────────────────────────────


@router.get("/model/metrics")
async def get_model_metrics():
    """模型对比指标：Best Model + 各模型 Accuracy/Precision/Recall/F1/ROC-AUC"""
    data = _load_json("model_metrics.json")
    return {
        "best_model": data.get("best_model"),
        "models": data.get("models", {}),
    }


@router.get("/model/importance")
async def get_model_importance():
    """
    特征重要性排名

    优先使用 SHAP 值（来自 output/results/shap_importance.json），
    如 SHAP 不可用则回退到模型参数（RF feature_importances_ 或 LR |coef_|）。
    返回模型名和重要性度量类型，避免混淆不同指标。
    """
    model_path = MODELS_DIR / "churn_model.pkl"
    if not model_path.exists():
        raise HTTPException(404, "模型文件不存在，请先运行 python run_prediction.py")

    import pickle
    with open(model_path, "rb") as f:
        data = pickle.load(f)

    # pickle 格式: dict with 'model', 'feature_names', 'model_name', etc.
    if isinstance(data, dict):
        pipeline = data["model"]
        features = data["feature_names"]
        model_name = data.get("model_name", "Unknown")
    else:
        # 兼容旧的 ChurnPredictor 对象格式
        pipeline = getattr(data, "best_model", None)
        features = getattr(data, "feature_names", [])
        model_name = getattr(data, "best_model_name", "Unknown")

    # 尝试加载 SHAP 值
    shap_path = RESULTS_DIR / "shap_importance.json"
    shap_data = None
    if shap_path.exists():
        try:
            with open(shap_path, "r", encoding="utf-8") as f:
                shap_data = json.load(f)
        except Exception:
            shap_data = None

    # 如果 SHAP 可用，优先使用 SHAP 排名
    if shap_data and shap_data.get("features"):
        shap_features = shap_data["features"]
        # 构建 name → shap_mean_abs 的映射
        shap_map = {item["name"]: item["shap_mean_abs"] for item in shap_features}
        result = []
        for item in shap_features:
            result.append({
                "name": item["name"],
                "importance": item["shap_mean_abs"],
                "shap_mean": item["shap_mean_abs"],
            })
        importance_type = f"SHAP ({shap_data.get('explainer_type', 'unknown')})"
        return {
            "model_name": model_name,
            "importance_type": importance_type,
            "shap_available": True,
            "features": result[:15],
        }

    # 回退：从模型参数中提取重要性
    if hasattr(pipeline, "named_steps") and "classifier" in pipeline.named_steps:
        estimator = pipeline.named_steps["classifier"]
    else:
        estimator = pipeline

    importance = None
    importance_type = None
    if estimator is not None:
        if hasattr(estimator, "feature_importances_"):
            importance = estimator.feature_importances_
            importance_type = "feature_importances_ (Gini importance)"
        elif hasattr(estimator, "coef_"):
            importance = np.abs(estimator.coef_[0])
            importance_type = "|coef_| (coefficient magnitude)"

    result = []
    if importance is not None and len(importance) == len(features):
        for i, feat in enumerate(features):
            result.append({
                "name": str(feat),
                "importance": round(float(importance[i]), 6),
                "shap_mean": None,
            })
        result.sort(key=lambda x: -x["importance"])
    else:
        result = [{"name": str(f), "importance": 0, "shap_mean": None} for f in features]

    return {
        "model_name": model_name,
        "importance_type": importance_type or "unknown",
        "shap_available": False,
        "features": result[:15],
    }


# ── 聚类分析 ──────────────────────────────────────────────────


@router.get("/clusters")
async def get_clusters():
    """
    K-Means 聚类概览：每群 size/占比/流失率 + 散点图数据
    """
    data = _load_json("clustering_results.json")
    km = data.get("kmeans", {})
    chars = data.get("characteristics", {})

    n_clusters = int(km.get("n_clusters", 0))
    labels_raw = km.get("labels", [])

    # labels 可能是 numpy 数组的字符串表示: "[1 4 4 1 ...]"
    if isinstance(labels_raw, str):
        labels = np.fromstring(labels_raw.strip("[]"), sep=" ", dtype=int)
    else:
        labels = np.array(labels_raw)

    # 加载原始数据获取流失标签和散点数据
    try:
        df = _load_cached_data()
    except Exception:
        df = None

    clusters = []
    for i in range(n_clusters):
        idx = np.where(labels == i)[0]
        size = len(idx)
        pct = round(size / len(labels) * 100, 1) if len(labels) > 0 else 0

        # 流失率（labels 行数可能 > 原始数据行数，取交集）
        churn_rate = 0.0
        if df is not None and "用户流失标签" in df.columns:
            valid_idx = idx[idx < len(df)]
            if len(valid_idx) > 0:
                churn_rate = round(float(df.iloc[valid_idx]["用户流失标签"].mean()), 4)

        # 聚群画像标签
        char_key = f"cluster_{i}"
        cluster_label = f"聚类 {i}"
        if char_key in chars:
            feats = chars[char_key].get("features", {})
            if isinstance(feats, dict):
                # features 是 {特征名: {type, mean, median, std}} 格式
                # 只取数值型特征，跳过 ID 列和分类特征
                numeric_feats = {}
                for k, v in feats.items():
                    if not isinstance(v, dict) or k == "顾客ID":
                        continue
                    if v.get("type") != "numeric":
                        continue
                    try:
                        numeric_feats[k] = float(v.get("mean", 0))
                    except (ValueError, TypeError):
                        continue
                top_items = sorted(
                    numeric_feats.items(), key=lambda x: abs(x[1]), reverse=True
                )[:3]
                cluster_label = "、".join([f[0] for f in top_items]) if top_items else f"聚类 {i}"

        clusters.append({
            "id": i,
            "size": int(size),
            "pct": pct,
            "churn_rate": churn_rate,
            "label": cluster_label,
        })

    # 散点图数据：折扣金额 vs 使用时长，按聚类着色
    scatter_data = []
    if df is not None and "上月平均折扣金额" in df.columns and "使用平台时间_月" in df.columns:
        n = min(len(df), len(labels))
        for i in range(n):
            churn = int(df.iloc[i]["用户流失标签"]) if "用户流失标签" in df.columns else 0
            scatter_data.append({
                "x": float(df.iloc[i]["上月平均折扣金额"]),
                "y": float(df.iloc[i]["使用平台时间_月"]),
                "cluster": int(labels[i]),
                "churn": churn,
            })

    return {
        "n_clusters": n_clusters,
        "silhouette_score": km.get("silhouette_score",
                                    km.get("metrics", {}).get("silhouette_score", 0)),
        "clusters": clusters,
        "scatter_data": scatter_data,
    }


# ── 关联规则 ──────────────────────────────────────────────────


@router.get("/rules")
async def get_rules():
    """关联规则列表 Top-100，含流失相关规则子集"""
    data = _load_json("association_rules.json")

    def _clean_frozenset(s: str) -> str:
        """将 frozenset({'A', 'B'}) 或 ['A', 'B'] 清洗为 'A, B'"""
        import re
        s = s.strip()
        # frozenset({'A', 'B'}) → 提取 {...} 中的内容
        frozenset_match = re.match(r"frozenset\(\{(.+)\}\)", s)
        if frozenset_match:
            s = frozenset_match.group(1)
        # ['A', 'B'] → 去掉方括号和引号
        s = s.strip("[]").strip()
        # 将 'A', 'B' 或 "A", "B" 清洗为 A, B
        s = re.sub(r"['\"]", "", s)
        return s.strip()

    def _parse_rules_data(rules_data) -> list:
        """解析规则数据（支持 CSV 字符串 + 字典列表两种格式）"""
        if not rules_data:
            return []
        # 字典列表格式（loss_rules）
        if isinstance(rules_data, list):
            result = []
            for item in rules_data:
                if not isinstance(item, dict):
                    continue
                if "rule" in item and " -> " in str(item["rule"]):
                    # 格式: "['A', 'B'] -> ['C', 'D']"
                    parts = str(item["rule"]).split(" -> ", 1)
                    ante = _clean_frozenset(parts[0])
                    cons = _clean_frozenset(parts[1])
                else:
                    ante = _clean_frozenset(str(item.get("antecedents", item.get("rule", ""))))
                    cons = _clean_frozenset(str(item.get("consequents", "")))
                try:
                    result.append({
                        "antecedents": ante,
                        "consequents": cons,
                        "support": round(float(item.get("support", 0)), 4),
                        "confidence": round(float(item.get("confidence", 0)), 4),
                        "lift": round(float(item.get("lift", 0)), 2),
                    })
                except (ValueError, TypeError):
                    continue
            return result
        # CSV 字符串格式（已修复的新格式，来自 DataFrame.to_csv()）
        from io import StringIO
        try:
            df_rules = pd.read_csv(StringIO(rules_data))
        except Exception:
            return []
        result = []
        for _, row in df_rules.iterrows():
            try:
                item = {
                    "antecedents": _clean_frozenset(str(row.get("antecedents", ""))),
                    "consequents": _clean_frozenset(str(row.get("consequents", ""))),
                    "support": round(float(row.get("support", 0)), 4),
                    "confidence": round(float(row.get("confidence", 0)), 4),
                    "lift": round(float(row.get("lift", 0)), 2),
                }
                result.append(item)
            except (ValueError, TypeError):
                continue
        return result

    rules = _parse_rules_data(data.get("rules", ""))
    loss_rules = _parse_rules_data(data.get("loss_rules", ""))

    # 按 lift 降序取 top-100
    rules.sort(key=lambda x: x["lift"], reverse=True)
    loss_rules.sort(key=lambda x: x["lift"], reverse=True)

    return {
        "rule_count": data.get("rule_count", 0),
        "itemset_count": data.get("itemset_count", 0),
        "rules": rules[:100],
        "loss_related": loss_rules[:100],
    }


# ── 预测（代理到主 API） ─────────────────────────────────────


@router.post("/predict")
async def predict_proxy(features: dict):
    """
    预测客户流失概率（与 POST /predict 同逻辑，供 /api 前缀使用）
    """
    # 导入共享模型服务
    try:
        from src.model_service import get_predictor, compute_risk_level
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"无法导入预测模块: {str(e)}")

    # 加载模型
    try:
        predictor, _feature_names = get_predictor()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

    # 构建输入 DataFrame
    try:
        df = pd.DataFrame([features])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"输入数据格式错误: {str(e)}")

    # 预处理
    try:
        if predictor._preprocessor is not None:
            X = predictor._preprocessor.transform(df)
        else:
            X = df.values.astype(float)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"数据预处理失败: {str(e)}")

    # 预测
    try:
        churn_prob = float(predictor.predict_proba(X)[0])
        predicted_class = int(predictor.predict(X)[0])
        risk_level = compute_risk_level(churn_prob)

        return {
            "churn_probability": round(churn_prob, 4),
            "risk_level": risk_level,
            "predicted_class": predicted_class,
            "model": predictor.best_model_name or "Unknown",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


# ── 特征分布 ──────────────────────────────────────────────────


@router.get("/data/distribution/{feature_name}")
async def get_feature_distribution(feature_name: str):
    """
    单个特征的分布数据（直方图用）。
    """
    try:
        df = _load_cached_data()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"数据加载失败: {str(e)}")

    if feature_name not in df.columns:
        raise HTTPException(404, f"特征 '{feature_name}' 不存在")

    churn_col = "用户流失标签"
    series = df[feature_name].dropna()

    if pd.api.types.is_numeric_dtype(series):
        # 数值特征：分箱
        bins = min(20, series.nunique())
        hist, bin_edges = np.histogram(series.values, bins=bins)
        bin_centers = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(bins)]

        # 按流失状态分组
        if churn_col in df.columns:
            churned = df[df[churn_col] == 1][feature_name].dropna()
            not_churned = df[df[churn_col] == 0][feature_name].dropna()
            hist_churned, _ = np.histogram(churned.values, bins=bin_edges)
            hist_not, _ = np.histogram(not_churned.values, bins=bin_edges)
        else:
            hist_churned = np.zeros(bins)
            hist_not = np.zeros(bins)

        return {
            "feature": feature_name,
            "type": "numeric",
            "bins": [{"x": round(float(bin_centers[i]), 2),
                      "total": int(hist[i]),
                      "churned": int(hist_churned[i]),
                      "not_churned": int(hist_not[i])}
                     for i in range(bins)],
        }
    else:
        # 分类特征
        counts = series.value_counts()
        result = []
        for val, cnt in counts.items():
            if churn_col in df.columns:
                subset = df[df[feature_name] == val]
                churned_cnt = int(subset[churn_col].sum())
            else:
                churned_cnt = 0
            result.append({
                "category": str(val),
                "total": int(cnt),
                "churned": churned_cnt,
            })
        return {"feature": feature_name, "type": "categorical", "categories": result}

"""
FastAPI 预测服务 — 客户流失概率预测接口

启动方式:
    python run_api.py
    uvicorn src.api:app --host 0.0.0.0 --port 8000

接口:
    POST /predict  — 预测客户流失概率
    GET  /health    — 健康检查
    GET  /          — 服务信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── 应用初始化 ──────────────────────────────────────────────

app = FastAPI(
    title="客户流失预测服务",
    description="基于 XGBoost / Random Forest / Logistic Regression 的客户流失概率预测",
    version="1.0.0",
)

# 模型路径
MODEL_PATH = Path(__file__).resolve().parents[1] / "output" / "models" / "churn_model.pkl"

# 全局预测器（延迟加载）
_predictor = None
_feature_names: List[str] = []

# ── 数据模型 ────────────────────────────────────────────────


class CustomerFeatures(BaseModel):
    """客户特征输入"""

    使用平台时间_月: int = Field(..., description="平台使用月数")
    常用登陆设备: str = Field(..., description="常用登录设备类型")
    城市等级: int = Field(..., ge=1, le=5, description="城市等级 1-5")
    仓库到顾客地址: int = Field(..., description="仓库到顾客地址距离")
    婚姻情况: str = Field(..., description="婚姻状况")
    年龄分组: int = Field(..., description="年龄分组")
    性别: str = Field(..., description="性别")
    使用App时间_时: int = Field(..., description="App 使用时长(小时)")
    上月订单数量单: int = Field(..., ge=0, description="上月订单数量")
    订单数量较去年增加_单: int = Field(..., description="订单较去年增减")
    距上次下单天数_天: int = Field(..., ge=0, description="距上次下单天数")
    上月客户的首选订单类别: str = Field(..., description="首选订单类别")
    用户关注的主播数量: int = Field(..., ge=0, description="关注主播数量")
    顾客对服务的满意度: int = Field(..., ge=1, le=5, description="满意度评分 1-5")
    上月投诉次数: int = Field(..., ge=0, description="上月投诉次数")
    上月使用的优惠劵数量_张: int = Field(..., ge=0, description="上月优惠券使用数")
    上月平均折扣金额: float = Field(..., ge=0.0, description="上月平均折扣金额")

    class Config:
        json_schema_extra = {
            "example": {
                "使用平台时间_月": 12,
                "常用登陆设备": "Mobile Phone",
                "城市等级": 3,
                "仓库到顾客地址": 8,
                "婚姻情况": "Single",
                "年龄分组": 3,
                "性别": "Male",
                "使用App时间_时": 5,
                "上月订单数量单": 3,
                "订单数量较去年增加_单": -2,
                "距上次下单天数_天": 30,
                "上月客户的首选订单类别": "Laptop & Accessory",
                "用户关注的主播数量": 5,
                "顾客对服务的满意度": 3,
                "上月投诉次数": 1,
                "上月使用的优惠劵数量_张": 0,
                "上月平均折扣金额": 120.5,
            }
        }


class PredictionResponse(BaseModel):
    """预测结果"""

    churn_probability: float = Field(..., description="流失概率 (0-1)")
    risk_level: str = Field(..., description="风险等级: low / medium / high / critical")
    predicted_class: int = Field(..., description="预测类别: 0=留存, 1=流失")
    model: str = Field(..., description="使用的模型名称")


# ── 模型加载 ────────────────────────────────────────────────


def _load_predictor():
    """加载预测模型（带缓存）"""
    global _predictor, _feature_names

    if _predictor is not None:
        return _predictor

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"模型文件不存在: {MODEL_PATH}\n"
            f"请先运行预测建模: python run_prediction.py 或 python run_analysis.py"
        )

    from src.prediction import ChurnPredictor

    _predictor = ChurnPredictor.load_model(str(MODEL_PATH))
    _feature_names = _predictor.feature_names

    logger.info(f"模型已加载: {_predictor.best_model_name} "
                f"(ROC-AUC={_predictor.metrics[_predictor.best_model_name]['roc_auc']:.4f})")

    return _predictor


def _compute_risk_level(probability: float) -> str:
    """根据流失概率确定风险等级"""
    if probability < 0.3:
        return "low"
    elif probability < 0.6:
        return "medium"
    elif probability < 0.8:
        return "high"
    else:
        return "critical"


# ── API 端点 ────────────────────────────────────────────────


@app.get("/")
async def root():
    """服务信息"""
    return {
        "service": "客户流失预测服务",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict",
            "health": "GET /health",
        },
    }


@app.get("/health")
async def health():
    """健康检查"""
    model_available = MODEL_PATH.exists()
    return {
        "status": "healthy",
        "model_loaded": _predictor is not None,
        "model_file_exists": model_available,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: CustomerFeatures):
    """
    预测客户流失概率

    接受客户特征 JSON，返回流失概率和风险等级。
    """
    try:
        predictor = _load_predictor()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

    # 构建 DataFrame
    input_dict = features.model_dump()
    df = pd.DataFrame([input_dict])

    # 确保列顺序与训练时一致
    if _feature_names:
        missing = set(_feature_names) - set(df.columns)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"缺少特征列: {missing}",
            )
        # 添加缺失的 one-hot 列（若可能）
        for col in _feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[_feature_names]

    # 预处理 + 预测
    try:
        if predictor._preprocessor is not None:
            X = predictor._preprocessor.transform(df)
        else:
            X = df.values.astype(float)

        churn_prob = float(predictor.predict_proba(X)[0])
        predicted_class = int(predictor.predict(X)[0])
        risk_level = _compute_risk_level(churn_prob)

        return PredictionResponse(
            churn_probability=round(churn_prob, 4),
            risk_level=risk_level,
            predicted_class=predicted_class,
            model=predictor.best_model_name or "Unknown",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

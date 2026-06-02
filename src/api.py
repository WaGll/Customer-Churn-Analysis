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

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── 应用初始化 ──────────────────────────────────────────────

app = FastAPI(
    title="客户流失预测服务",
    description="基于 XGBoost / Random Forest / Logistic Regression 的客户流失概率预测",
    version="1.0.0",
)

# CORS 中间件（生产环境应限制 allow_origins）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册数据分析展示 API
from src.api_v2 import router as api_v2_router
app.include_router(api_v2_router, prefix="/api")

# 共享模型服务
from src.model_service import get_predictor, compute_risk_level, MODEL_PATH, _predictor

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
        predictor, feature_names = get_predictor()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

    # 构建 DataFrame
    input_dict = features.dict()
    df = pd.DataFrame([input_dict])

    # 预处理 + 预测
    try:
        if predictor._preprocessor is not None:
            X = predictor._preprocessor.transform(df)
        else:
            # 无预处理器时，确保列顺序与训练时一致
            if feature_names:
                for col in feature_names:
                    if col not in df.columns:
                        df[col] = 0
                df = df[feature_names]
            X = df.values.astype(float)

        churn_prob = float(predictor.predict_proba(X)[0])
        predicted_class = int(predictor.predict(X)[0])
        risk_level = compute_risk_level(churn_prob)

        return PredictionResponse(
            churn_probability=round(churn_prob, 4),
            risk_level=risk_level,
            predicted_class=predicted_class,
            model=predictor.best_model_name or "Unknown",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

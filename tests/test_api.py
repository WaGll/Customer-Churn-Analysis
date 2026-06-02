"""
API 端点测试 — FastAPI 预测服务
"""

import os
import sys
import pytest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient


# 检查模型文件是否存在
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "output", "models", "churn_model.pkl"
)
SKIP_API_TESTS = not os.path.exists(MODEL_PATH)


@pytest.fixture
def client():
    """FastAPI TestClient"""
    from src.api import app
    with TestClient(app) as c:
        yield c


class TestAPI:
    """API 端点测试"""

    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "客户流失预测服务"

    def test_health(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.skipif(SKIP_API_TESTS, reason="模型文件不存在，跳过预测测试")
    def test_predict_success(self, client):
        """测试成功预测"""
        payload = {
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
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "churn_probability" in data
        assert "risk_level" in data
        assert "predicted_class" in data
        assert "model" in data
        assert 0 <= data["churn_probability"] <= 1
        assert data["risk_level"] in ("low", "medium", "high", "critical")

    def test_predict_invalid_input(self, client):
        """测试无效输入"""
        payload = {"使用平台时间_月": "not_a_number"}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error

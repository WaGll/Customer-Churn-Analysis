"""
特征工程模块测试 — FeatureEngineer
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.feature_engineering import FeatureEngineer


class TestFeatureEngineer:
    """FeatureEngineer 单元测试"""

    @pytest.fixture
    def engineer(self):
        return FeatureEngineer()

    def test_preprocess_data_output_keys(self, engineer, sample_churn_data):
        """测试 preprocess_data 返回三种编码"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        datasets = engineer.preprocess_data(df)

        assert "one_hot" in datasets
        assert "mixed" in datasets
        assert "standardized" in datasets

    def test_one_hot_output(self, engineer, sample_churn_data):
        """测试 One-Hot 编码输出"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        datasets = engineer.preprocess_data(df)
        one_hot = datasets["one_hot"]

        # 所有列应为数值型
        assert all(one_hot[col].dtype in ['int64', 'float64', 'int32', 'float32']
                   for col in one_hot.columns)

        # 样本数不变
        assert len(one_hot) == len(df)

        # 无缺失值
        assert one_hot.isnull().sum().sum() == 0

    def test_mixed_output(self, engineer, sample_churn_data):
        """测试混合编码输出"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        datasets = engineer.preprocess_data(df)
        mixed = datasets["mixed"]

        assert len(mixed) == len(df)

    def test_standardized_output(self, engineer, sample_churn_data):
        """测试标准化输出"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        datasets = engineer.preprocess_data(df)
        standardized = datasets["standardized"]

        assert len(standardized) == len(df)

    def test_mixed_encoded_no_side_effect(self, engineer, sample_churn_data):
        """测试 _create_mixed_encoded 不会修改原始 DataFrame"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        original_values = df["上月平均折扣金额"].copy()
        original_shape = df.shape

        _ = engineer._create_mixed_encoded(df)

        # 原始 DataFrame 不应被修改
        assert df.shape == original_shape
        assert (df["上月平均折扣金额"] == original_values).all()

    def test_handle_missing_values(self, engineer, sample_churn_data):
        """测试缺失值处理"""
        df = sample_churn_data.drop(columns=["顾客ID"]).copy()
        # 人为制造缺失值
        df.loc[0, "上月投诉次数"] = np.nan
        df.loc[1, "常用登陆设备"] = np.nan

        datasets = engineer.preprocess_data(df)

        # 不应有缺失值
        for name, ds in datasets.items():
            assert ds.isnull().sum().sum() == 0, f"{name} 仍存在缺失值"

    def test_drop_customer_id(self, engineer, sample_churn_data):
        """测试自动丢弃顾客ID列"""
        datasets = engineer.preprocess_data(sample_churn_data)

        for name, ds in datasets.items():
            assert "顾客ID" not in ds.columns, f"{name} 包含顾客ID"

    def test_get_feature_importance(self, engineer, sample_churn_data):
        """测试特征重要性评估"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        y = df["用户流失标签"]
        X = df.drop(columns=["用户流失标签"])

        importance = engineer.get_feature_importance(X, y)

        assert isinstance(importance, dict)
        assert len(importance) > 0
        # 值应在合理范围
        for v in importance.values():
            assert v >= 0

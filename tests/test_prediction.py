"""
预测模块测试 — ChurnPredictor
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.prediction import ChurnPredictor


class TestChurnPredictor:
    """ChurnPredictor 单元测试"""

    @pytest.fixture
    def predictor(self):
        return ChurnPredictor(random_state=42)

    def test_init(self, predictor):
        """测试初始化"""
        assert predictor.random_state == 42
        assert predictor.best_model is None
        assert predictor.best_model_name is None
        assert predictor.models == {}
        assert predictor.metrics == {}

    def test_prepare_data(self, predictor, sample_churn_data):
        """测试数据准备"""
        X_train, X_test, y_train, y_test = predictor.prepare_data(
            sample_churn_data,
            target_col="用户流失标签",
            test_size=0.2,
            id_cols=["顾客ID"],
        )

        # 形状验证
        n_total = len(sample_churn_data)
        assert len(X_train) == int(n_total * 0.8)
        assert len(X_test) == n_total - len(X_train)
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)

        # 类型验证
        assert isinstance(X_train, np.ndarray)
        assert isinstance(y_train, np.ndarray)

        # 分层验证：训练/测试集的正样本比例应接近
        train_pos_rate = y_train.mean()
        test_pos_rate = y_test.mean()
        assert abs(train_pos_rate - test_pos_rate) < 0.15

        # 特征名已记录
        assert len(predictor.feature_names) > 0

    def test_prepare_data_missing_target(self, predictor, sample_churn_data):
        """测试目标列缺失时的错误处理"""
        with pytest.raises(KeyError, match="目标列"):
            predictor.prepare_data(sample_churn_data, target_col="不存在的列")

    def test_train_models(self, predictor, sample_churn_data):
        """测试模型训练"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        cv_results = predictor.train_models(cv_folds=3, n_jobs=1)

        # 至少训练了 LR 和 RF
        assert "LogisticRegression" in predictor.models
        assert "RandomForest" in predictor.models
        assert "LogisticRegression" in cv_results
        assert "RandomForest" in cv_results

        # 验证 CV 结果格式
        for name in cv_results:
            assert "best_cv_score" in cv_results[name]
            assert "best_params" in cv_results[name]
            assert cv_results[name]["best_cv_score"] > 0.0

    def test_evaluate_models(self, predictor, sample_churn_data):
        """测试模型评估"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        predictor.train_models(cv_folds=3, n_jobs=1)
        metrics = predictor.evaluate_models()

        # 验证指标完整性
        for model_name in predictor.models:
            assert model_name in metrics
            m = metrics[model_name]
            assert "accuracy" in m
            assert "precision" in m
            assert "recall" in m
            assert "f1" in m
            assert "roc_auc" in m

        # 最佳模型已选出
        assert predictor.best_model is not None
        assert predictor.best_model_name is not None

    def test_predict_methods(self, predictor, sample_churn_data):
        """测试 predict / predict_proba"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        predictor.train_models(cv_folds=3, n_jobs=1)
        predictor.evaluate_models()

        # 取测试集最后 3 条
        X = predictor._X_test[:3]
        pred_class = predictor.predict(X)
        pred_proba = predictor.predict_proba(X)

        assert len(pred_class) == 3
        assert len(pred_proba) == 3
        assert all(c in (0, 1) for c in pred_class)
        assert all(0 <= p <= 1 for p in pred_proba)

    def test_save_and_load_model(self, predictor, sample_churn_data, tmp_path):
        """测试模型保存与加载"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        predictor.train_models(cv_folds=3, n_jobs=1)
        predictor.evaluate_models()

        # 保存
        model_path = str(tmp_path / "test_model.pkl")
        saved_path = predictor.save_model(output_path=model_path)
        assert os.path.exists(saved_path)

        # 加载
        loaded = ChurnPredictor.load_model(model_path)
        assert loaded.best_model_name == predictor.best_model_name
        assert "roc_auc" in loaded.metrics[loaded.best_model_name]

    def test_save_metrics(self, predictor, sample_churn_data, tmp_path):
        """测试指标保存"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        predictor.train_models(cv_folds=3, n_jobs=1)
        predictor.evaluate_models()

        metrics_path = str(tmp_path / "test_metrics.json")
        saved = predictor.save_metrics(output_path=metrics_path)
        assert os.path.exists(saved)

        import json
        with open(saved) as f:
            report = json.load(f)
        assert "best_model" in report
        assert "models" in report

    def test_plot_roc_curves(self, predictor, sample_churn_data, tmp_path):
        """测试 ROC 曲线生成"""
        predictor.prepare_data(sample_churn_data, test_size=0.2, id_cols=["顾客ID"])
        predictor.train_models(cv_folds=3, n_jobs=1)
        predictor.evaluate_models()

        roc_path = str(tmp_path / "roc.html")
        output = predictor.plot_roc_curves(output_path=roc_path)
        assert os.path.exists(output)

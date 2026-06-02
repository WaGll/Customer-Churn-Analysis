"""
聚类分析模块测试 — ClusterAnalyzer
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.feature_engineering import FeatureEngineer
from src.clustering import ClusterAnalyzer


class TestClusterAnalyzer:
    """ClusterAnalyzer 单元测试"""

    @pytest.fixture
    def analyzer(self):
        return ClusterAnalyzer()

    @pytest.fixture
    def prepared_data(self, sample_churn_data):
        """预处理后的数据集"""
        df = sample_churn_data.drop(columns=["顾客ID"])
        fe = FeatureEngineer()
        return fe.preprocess_data(df)

    def test_kmeans_clustering(self, analyzer, prepared_data):
        """测试 K-Means 聚类"""
        result = analyzer.kmeans_clustering(
            prepared_data["one_hot"],
            max_clusters=4,
        )

        assert "n_clusters" in result
        assert "labels" in result
        assert "metrics" in result
        assert 2 <= result["n_clusters"] <= 4
        assert len(result["labels"]) == len(prepared_data["one_hot"])
        assert "silhouette_score" in result["metrics"]

    def test_stability_test(self, analyzer, prepared_data):
        """测试聚类稳定性"""
        stability = analyzer.stability_test(
            prepared_data["one_hot"],
            algorithm="kmeans",
            n_iterations=3,
        )

        assert "stability_level" in stability
        assert "consistency_scores" in stability
        assert "average_metrics" in stability
        assert stability["consistency_scores"]["adjusted_rand_index"] >= -0.1  # ARI 可略低于 0

    def test_analyze_cluster_characteristics(self, analyzer, prepared_data, sample_churn_data):
        """测试聚类特征分析"""
        result = analyzer.kmeans_clustering(
            prepared_data["one_hot"],
            max_clusters=4,
        )

        df_clean = sample_churn_data.drop(columns=["顾客ID"])
        chars = analyzer.analyze_cluster_characteristics(df_clean, result["labels"])

        n_clusters = result["n_clusters"]
        assert len(chars) == n_clusters

        for cluster_id in range(n_clusters):
            key = f"cluster_{cluster_id}"
            assert key in chars
            assert "size" in chars[key]
            assert "percentage" in chars[key]
            assert "features" in chars[key]

    def test_find_elbow_point(self, analyzer):
        """测试肘部点检测"""
        # 模拟递减的 WCSS
        values = [100.0, 50.0, 30.0, 20.0, 15.0, 12.0]
        idx = analyzer._find_elbow_point(values)
        assert 0 <= idx < len(values)

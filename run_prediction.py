#!/usr/bin/env python3
"""
客户流失预测 — 独立入口脚本

使用方式:
    # 使用默认数据
    python run_prediction.py

    # 指定数据路径
    python run_prediction.py --data-path data/customer_churn_data.xlsx

    # 指定输出目录
    python run_prediction.py --output-dir output

    # 禁用 XGBoost（仅使用 LR + RF）
    python run_prediction.py --no-xgboost

    # 查看帮助
    python run_prediction.py --help
"""

import os
import sys
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.data_loader import DataLoader
from src.prediction import ChurnPredictor

# ── 命令行参数 ──────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(description="客户流失预测建模")

    parser.add_argument(
        "--data-path", "-d",
        default="data/customer_churn_data.xlsx",
        help="数据文件路径",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="输出根目录",
    )
    parser.add_argument(
        "--target-col",
        default="用户流失标签",
        help="目标列名（流失标签）",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="测试集比例 (默认 0.2)",
    )
    parser.add_argument(
        "--cv-folds",
        type=int,
        default=5,
        help="交叉验证折数 (默认 5)",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="并行任务数 (默认 -1, 使用全部核心)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别",
    )
    parser.add_argument(
        "--no-xgboost",
        action="store_true",
        help="禁用 XGBoost (仅使用 LR + RF)",
    )

    return parser.parse_args()


# ── 主流程 ──────────────────────────────────────────────────


def main():
    args = parse_args()

    # 日志配置
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # 如果用户指定禁用 XGBoost，设置环境变量提示
    if args.no_xgboost:
        os.environ["SKIP_XGBOOST"] = "1"
        logger.info("已禁用 XGBoost，仅使用 Logistic Regression 和 Random Forest")

    logger.info("=" * 60)
    logger.info("客户流失预测建模")
    logger.info("=" * 60)
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"数据路径: {args.data_path}")
    logger.info(f"输出目录: {args.output_dir}")

    # 确保输出目录存在
    model_dir = Path(args.output_dir) / "models"
    results_dir = Path(args.output_dir) / "results"
    vis_dir = Path(args.output_dir) / "visualizations"
    for d in [model_dir, results_dir, vis_dir]:
        d.mkdir(parents=True, exist_ok=True)

    try:
        # 1. 加载数据
        logger.info("\n[步骤 1/4] 加载数据...")
        start_time = time.time()

        data_loader = DataLoader()
        df = data_loader.load_data(args.data_path)

        logger.info(f"数据加载完成: {df.shape}, 耗时: {time.time() - start_time:.2f}s")

        # 2. 预测建模
        logger.info("\n[步骤 2/4] 预测建模 (训练 + 评估)...")
        start_time = time.time()

        predictor = ChurnPredictor()

        summary = predictor.run(
            df=df,
            target_col=args.target_col,
            test_size=args.test_size,
            cv_folds=args.cv_folds,
            n_jobs=args.n_jobs if args.n_jobs > 0 else None,
            output_model_path=str(model_dir / "churn_model.pkl"),
            output_metrics_path=str(results_dir / "model_metrics.json"),
            output_roc_path=str(vis_dir / "roc_curve.html"),
        )

        logger.info(f"预测建模完成, 总耗时: {time.time() - start_time:.2f}s")

        # 3. 打印最终报告
        logger.info("\n" + "=" * 60)
        logger.info("📊 最终分析报告")
        logger.info("=" * 60)
        logger.info(f"最佳模型: {summary['best_model']}")

        metrics = summary["best_metrics"]
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1-Score:  {metrics['f1']:.4f}")
        logger.info(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")

        logger.info(f"\n输出文件:")
        logger.info(f"  模型文件: {summary['model_path']}")
        logger.info(f"  指标文件: {summary['metrics_path']}")
        logger.info(f"  ROC 曲线: {summary['roc_path']}")

        # 打印所有模型对比
        logger.info(f"\n模型对比:")
        for name, m in summary["all_metrics"].items():
            marker = " ← 最佳" if name == summary["best_model"] else ""
            logger.info(
                f"  {name}: AUC={m['roc_auc']:.4f}, F1={m['f1']:.4f}, "
                f"Recall={m['recall']:.4f}{marker}"
            )

    except Exception as e:
        logger.error(f"预测建模失败: {e}", exc_info=True)
        sys.exit(1)

    logger.info("\n✅ 客户流失预测建模完成！")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate synthetic customer churn data matching the real data schema.
Used by CI to test the Docker image without the real data file.
"""

import os
import sys

import numpy as np
import pandas as pd


def generate_synthetic_data(n: int = 100, output_path: str = "data/customer_churn_data.xlsx") -> pd.DataFrame:
    """Generate synthetic customer churn data.

    Args:
        n: Number of rows to generate.
        output_path: Path to save the Excel file.

    Returns:
        DataFrame with synthetic data.
    """
    rng = np.random.RandomState(42)

    df = pd.DataFrame({
        "顾客ID": range(1, n + 1),
        "用户流失标签": rng.choice([0, 1], n, p=[0.7, 0.3]),
        "使用平台时间_月": rng.randint(1, 60, n),
        "常用登陆设备": rng.choice(["Mobile Phone", "Phone", "Pad", "PC"], n),
        "城市等级": rng.randint(1, 5, n),
        "仓库到顾客地址": rng.randint(1, 20, n),
        "婚姻情况": rng.choice(["Single", "Married", "Divorced"], n),
        "年龄分组": rng.randint(1, 7, n),
        "性别": rng.choice(["Male", "Female"], n),
        "使用App时间_时": rng.randint(0, 24, n),
        "上月订单数量单": rng.randint(0, 10, n),
        "订单数量较去年增加_单": rng.randint(-5, 10, n),
        "距上次下单天数_天": rng.randint(0, 90, n),
        "上月客户的首选订单类别": rng.choice(
            ["Laptop & Accessory", "Mobile Phone", "Fashion", "Household", "Other"], n
        ),
        "用户关注的主播数量": rng.randint(0, 20, n),
        "顾客对服务的满意度": rng.randint(1, 6, n),
        "上月投诉次数": rng.choice([0, 0, 0, 0, 1, 2], n),
        "上月使用的优惠劵数量_张": rng.randint(0, 5, n),
        "上月平均折扣金额": np.round(rng.uniform(0, 300, n), 2),
    })

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_excel(output_path, index=False)
        print(f"Generated {len(df)} rows of synthetic data -> {output_path}")

    return df


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    path = sys.argv[2] if len(sys.argv) > 2 else "data/customer_churn_data.xlsx"
    generate_synthetic_data(n, path)

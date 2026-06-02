"""
共享测试 Fixture — 所有测试模块共用
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

# 添加 src 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def sample_churn_data() -> pd.DataFrame:
    """生成模拟客户流失数据 (200 条)"""
    rng = np.random.RandomState(42)
    n = 200

    data = {
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
    }

    df = pd.DataFrame(data)

    # 模拟流失模式：投诉多的更可能流失
    mask = (df["上月投诉次数"] > 0) & (rng.random(n) < 0.6)
    df.loc[mask, "用户流失标签"] = 1

    return df

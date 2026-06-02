
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

DATA_PATH = project_root / "data" / "customer_churn_data.xlsx"

# 列名映射：将中文列名映射为 dashboard 易用的英文别名（忠实于数据原意）
COLUMN_MAP = {
    "Churn": "用户流失标签",
    "Tenure": "使用平台时间_月",
    "AvgDiscount": "上月平均折扣金额",
    "PreferredCategory": "上月客户的首选订单类别",
    "LoginDevice": "常用登陆设备",
    "OrderCount": "上月订单数量单",
    "AppUsageHours": "使用App时间_时",
    "ComplaintCount": "上月投诉次数",
    "Satisfaction": "顾客对服务的满意度",
    "DaysSinceLastOrder": "距上次下单天数_天",
    "CouponUsed": "上月使用的优惠劵数量_张",
}

st.set_page_config(
    page_title="客户流失分析大屏",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 客户流失分析智能大屏")
st.markdown("**数据驱动 · 客户保留策略平台**")

with st.sidebar:
    st.header("🔧 控制面板")
    st.caption(f"数据路径: {DATA_PATH}")
    refresh = st.button("🔄 刷新全部数据", type="primary")

@st.cache_data(ttl=300)
def load_data(filepath: Path) -> pd.DataFrame:
    if not filepath.exists():
        st.error(f"❌ 数据文件不存在：{filepath}")
        st.stop()
    try:
        from data_loader import DataLoader
        loader = DataLoader()
        df = loader.load_data(filepath)
        return df
    except Exception as exc:
        st.warning(f"⚠️ src.data_loader 加载失败，使用 pandas 备选方案：{exc}")
        try:
            return pd.read_excel(filepath)
        except Exception as err:
            st.error(f"❌ 数据文件加载失败：{err}")
            st.stop()

if refresh:
    load_data.clear()
    st.experimental_rerun()

df = load_data(DATA_PATH)

# 将中文列名映射为 dashboard 使用的英文别名
for en_name, cn_name in COLUMN_MAP.items():
    if cn_name in df.columns and en_name not in df.columns:
        df[en_name] = df[cn_name]

# 添加 Cluster 列（运行快速 K-Means 聚类）
if "Cluster" not in df.columns:
    try:
        from feature_engineering import FeatureEngineer
        from clustering import ClusterAnalyzer
        fe = FeatureEngineer()
        ca = ClusterAnalyzer()
        df_clean = df.drop(columns=["顾客ID"], errors="ignore")
        datasets = fe.preprocess_data(df_clean)
        kmeans_result = ca.kmeans_clustering(datasets["one_hot"], max_clusters=3)
        df["Cluster"] = kmeans_result["labels"].astype(str)
    except Exception:
        df["Cluster"] = "0"  # fallback

def safe_mean(series):
    return series.dropna().astype(float).mean() if not series.empty else 0.0

total_customers = len(df)
churn_rate = 0.0
high_risk_customers = 0
discount_avg = 0.0

if "Churn" in df.columns:
    churn_series = df["Churn"].astype(bool)
    churn_rate = churn_series.mean() * 100
    high_risk_customers = int(churn_series.sum())

if "AvgDiscount" in df.columns:
    discount_avg = safe_mean(df["AvgDiscount"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总客户数", f"{total_customers:,}")
with col2:
    st.metric("整体流失率", f"{churn_rate:.1f}%")
with col3:
    st.metric("平均折扣金额", f"¥{discount_avg:.1f}")
with col4:
    st.metric("高风险客户", f"{high_risk_customers:,}")

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 概览趋势", "👥 客户分群", "🔍 流失驱动因素"])

with tab1:
    col_a, col_b = st.columns([3, 2])
    with col_a:
        if {"Tenure", "Churn"}.issubset(df.columns):
            fig = px.histogram(
                df,
                x="Tenure",
                color="Churn",
                title="平台使用时长与流失分布",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("数据中缺少 Tenure 或 Churn，无法展示趋势图。")
    with col_b:
        if {"PreferredCategory", "Churn"}.issubset(df.columns):
            cat_churn = (
                df.groupby("PreferredCategory")["Churn"]
                .mean()
                .reset_index()
                .sort_values("Churn", ascending=False)
            )
            fig = px.bar(
                cat_churn,
                x="PreferredCategory",
                y="Churn",
                title="首选订单类别流失率对比",
                text=cat_churn["Churn"].map(lambda x: f"{x:.1%}"),
            )
            fig.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("数据中缺少 PreferredCategory 或 Churn，无法展示类别流失对比。")

with tab2:
    st.subheader("客户分群")
    if {"Cluster", "AvgDiscount", "Tenure"}.issubset(df.columns):
        fig = px.scatter(
            df,
            x="AvgDiscount",
            y="Tenure",
            color="Cluster",
            hover_data=["Churn"] if "Churn" in df.columns else None,
            title="客户聚类分布",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无聚类结果，可先运行 clustering.py 或补充 Cluster 字段。")

with tab3:
    st.subheader("流失关键驱动因素")
    # 尝试从已保存的模型指标中读取真实特征重要性
    metrics_path = project_root / "output" / "results" / "model_metrics.json"
    if metrics_path.exists():
        import json
        with open(metrics_path, "r") as f:
            model_metrics = json.load(f)
        best_model = model_metrics.get("best_model", "Unknown")
        st.caption(f"来源：{best_model} 模型训练结果")
        # 尝试使用 SHAP 图（若存在）
        shap_path = project_root / "output" / "visualizations" / "shap_summary.png"
        if shap_path.exists():
            st.image(str(shap_path), caption="SHAP 特征重要性")
        else:
            st.info("运行 `python run_prediction.py` 生成预测模型后可查看真实特征重要性。")
    else:
        st.info("尚未训练预测模型。请运行 `python run_prediction.py` 生成特征重要性分析。")

st.caption("Customer Churn Analysis Dashboard | Powered by Streamlit")

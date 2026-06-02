场景应用示例

本文件提供常见业务场景的代码示例。

---

## 场景 1：快速分析（一键运行）

```bash
# 1. 运行完整分析管道
python run_analysis.py
# 输出: output/results/ 下生成 4 个 JSON 文件

# 2. 训练预测模型
python run_prediction.py
# 输出: output/models/churn_model.pkl

# 3. 启动 API 服务
python run_api.py
# 启动 FastAPI，访问 http://localhost:8000/docs 查看 Swagger UI

# 4. 启动前端（新终端）
cd frontend && npm run dev
# 访问 http://localhost:5173
```

---

## 场景 2：单客户流失预测

```python
import requests

features = {
    "上月平均折扣金额": 120.5,
    "使用平台时间_月": 6,
    "仓库到客户距离_公里": 3.2,
    "上月订单数量单": 2,
    "上月投诉次数": 0,
    "上月客户的首选订单类别": "移动设备",
    "年龄分组": "26-35",
    "婚姻状况": "未婚",
    "性别": "男"
}

resp = requests.post("http://localhost:8000/predict", json=features)
print(resp.json())
# {'churn_probability': 0.2318, 'risk_level': 'medium', ...}
```

---

## 场景 3：查询特征重要性排名

```python
import requests

resp = requests.get("http://localhost:8000/api/model/importance")
data = resp.json()

print(f"模型: {data['model_name']}")
print(f"归因方法: {data['importance_type']}")

for f in data['features'][:5]:
    print(f"  {f['name']}: {f['importance']:.4f}")
```

---

## 场景 4：查询关联规则

```python
import requests

resp = requests.get("http://localhost:8000/api/rules")
data = resp.json()

for rule in data['loss_related'][:5]:
    print(f"{rule['antecedents']} → {rule['consequents']}")
    print(f"  Lift: {rule['lift']:.2f}, Confidence: {rule['confidence']:.4f}")
```

---

## 场景 5：查询聚类分析

```python
import requests

resp = requests.get("http://localhost:8000/api/clusters")
data = resp.json()

for c in data['clusters']:
    print(f"聚类 {c['id']}: {c['size']} 人 ({c['pct']}%), 流失率 {c['churn_rate']:.1%}")
    print(f"  特征: {c['label']}")

print(f"\n轮廓系数: {data['silhouette_score']:.3f}")
print(f"散点数据量: {len(data['scatter_data'])} 条")
```

---

## 场景 6：前端开发

```bash
# 安装依赖（仅首次）
cd frontend && npm install

# 启动开发服务器（热更新）
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

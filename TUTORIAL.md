# 客户流失分析 — 零基础自学教程

> 本教程面向编程零基础或数据分析初学者，手把手带你从环境配置到运行完整分析大屏。
>
> 预计学习时间：**4-6 小时**（含软件安装时间）
>
> 适用人群：在校学生、转行数据分析、校招求职者

---

## 目录

1. [学前必读：这个项目做了什么](#1-学前必读这个项目做了什么)
2. [第 0 步：认识你的电脑环境](#2-第-0-步认识你的电脑环境)
3. [第 1 步：安装 Python 环境](#3-第-1-步安装-python-环境)
4. [第 2 步：安装 Node.js](#4-第-2-步安装-nodejs)
5. [第 3 步：下载项目代码](#5-第-3-步下载项目代码)
6. [第 4 步：安装 Python 依赖包](#6-第-4-步安装-python-依赖包)
7. [第 5 步：运行数据分析流程](#7-第-5-步运行数据分析流程)
8. [第 6 步：启动后端 API 服务](#8-第-6-步启动后端-api-服务)
9. [第 7 步：安装前端依赖并启动大屏](#9-第-7-步安装前端依赖并启动大屏)
10. [第 8 步：理解项目结构](#10-第-8-步理解项目结构)
11. [第 9 步：核心概念通俗解释](#11-第-9-步核心概念通俗解释)
12. [第 10 步：如何从项目中学习](#12-第-10-步如何从项目中学习)
13. [常见问题排查](#13-常见问题排查)
14. [进阶学习路径](#14-进阶学习路径)

---

## 1. 学前必读：这个项目做了什么

### 用一个故事理解这个项目

假设你是一家电商平台的运营经理。你有 901 个客户，其中约 19% 的客户已经不再来购物了（我们称之为"流失"）。

你想知道三件事：
1. **哪些客户最可能流失？** → 用机器学习模型预测
2. **流失的客户有什么共同特征？** → 用聚类分析找群体
3. **哪些行为组合与流失高度相关？** → 用关联规则挖掘

这个项目就是用一个完整的分析流程来回答这三个问题，并做了一个可以在浏览器里操作的交互式数据大屏。

### 项目用到的技术（不用害怕，后面都会解释）

| 技术 | 作用 | 类比 |
|------|------|------|
| Python | 写分析代码的语言 | 像 Excel，但可以自动化处理大量数据 |
| pandas | Python 的数据处理库 | 代码版的 Excel 数据透视表 |
| scikit-learn | 机器学习库 | 一套做预测的"公式工具箱" |
| FastAPI | 后端服务框架 | 把分析结果通过网络接口提供出去 |
| Vue 3 | 前端框架 | 在浏览器里画界面 |
| ECharts | 图表库 | 在网页里画柱状图、饼图、仪表盘 |

### 学完你能收获什么

- 理解一个完整的数据分析项目是怎么跑的
- 知道机器学习模型是怎么训练和评估的
- 能自己运行和修改这个项目
- 有一份可以写到简历里的项目经历

---

## 2. 第 0 步：认识你的电脑环境

在开始安装任何东西之前，先了解几个基本概念。

### 什么是终端（Terminal）？

终端是一个黑色的文字窗口，你可以在里面输入命令来控制电脑。它看起来像黑客电影里的界面，但其实就是一个文字版的"操作电脑"的方式。

- **Windows**：按 `Win + R`，输入 `cmd`，回车。或者搜索"PowerShell"。
- **macOS**：按 `Cmd + 空格`，搜索"终端"（Terminal）。
- **Linux**：按 `Ctrl + Alt + T`。

后面所有需要输入命令的地方，都是在这个黑色窗口里操作。

### 什么是命令行？

在终端里，你不是用鼠标点来点去，而是输入文字命令。比如：

```bash
# 查看当前在哪个文件夹
pwd

# 看看当前文件夹里有什么
ls        # macOS/Linux
dir       # Windows

# 进入某个文件夹
cd 文件夹名

# 返回上一级文件夹
cd ..
```

> 提示：`#` 开头的是注释，不需要输入。后面的中文是说明。

### 文件路径是什么？

文件路径就是文件在电脑上的"地址"。比如：
- Windows: `C:\Users\你的用户名\Desktop\project`
- macOS/Linux: `/home/你的用户名/project`

后面的教程会频繁用到"路径"，请确保你理解这个概念。

---

## 3. 第 1 步：安装 Python 环境

Python 是运行数据分析代码的语言。这个项目需要 Python 3.9 或更高版本。

### 3.1 检查是否已安装 Python

打开终端，输入：

```bash
python --version
```

如果显示类似 `Python 3.9.x` 或 `Python 3.10.x`，说明已经安装了。跳到 3.3。

如果显示"未找到命令"或版本低于 3.9，继续下面的步骤。

### 3.2 安装 Miniconda（推荐）

Miniconda 是一个 Python 环境管理工具。它最棒的地方是可以创建"虚拟环境"——相当于给每个项目一个独立的 Python 空间，互相不影响。

**Step 1: 下载 Miniconda**

用浏览器打开：https://docs.conda.io/en/latest/miniconda.html

选择你的系统对应的版本（Windows/Mac/Linux），下载安装包。

**Step 2: 安装**

- **Windows**: 双击下载的 `.exe` 文件，一路"下一步"。**注意**：勾选"Add Miniconda to PATH"选项。
- **macOS**: 打开终端，进入下载目录，运行 `bash Miniconda3-latest-MacOSX-x86_64.sh`，一路回车。
- **Linux**: 同 macOS，用 `bash Miniconda3-latest-Linux-x86_64.sh`。

**Step 3: 验证安装**

关闭并重新打开终端，输入：

```bash
conda --version
```

如果显示版本号，安装成功。

### 3.3 创建项目专属的虚拟环境

```bash
# 创建一个名为 churn_analysis 的虚拟环境，指定 Python 3.9
conda create -n churn_analysis python=3.9 -y

# 激活这个环境
conda activate churn_analysis

# 验证：终端提示符前面应该出现 (churn_analysis)
# 再检查一下 Python 版本
python --version
```

> ⚠️ **重要**：每次打开新终端运行这个项目，都需要先执行 `conda activate churn_analysis`！

---

## 4. 第 2 步：安装 Node.js

Node.js 是运行前端代码（网页界面）的环境。

### 4.1 检查是否已安装

```bash
node --version
```

如果显示 `v18.x` 或更高版本，跳过此步。

### 4.2 安装 Node.js

用浏览器打开：https://nodejs.org

下载 **LTS 版本**（长期支持版，更稳定），安装。

安装完成后，关闭并重新打开终端，再次输入 `node --version` 验证。

安装 Node.js 时会自动安装 **npm**（Node 包管理器），验证一下：

```bash
npm --version
```

---

## 5. 第 3 步：下载项目代码

### 方式一：Git 克隆（推荐）

如果你会使用 Git：

```bash
git clone https://github.com/WaGll/customer-churn-analysis.git
cd customer_churn_analysis
```

### 方式二：直接下载

1. 浏览器打开：https://github.com/WaGll/customer-churn-analysis
2. 点击绿色的 "Code" 按钮 → "Download ZIP"
3. 解压到你喜欢的文件夹
4. 在终端中进入解压后的文件夹：

```bash
cd ~/Downloads/customer-churn-analysis   # 示例路径，改成你的实际路径
```

### 确认项目文件完整

在项目文件夹中，输入 `ls`（macOS/Linux）或 `dir`（Windows），你应该看到：

```
data/  src/  frontend/  output/  tests/  notebooks/
run_analysis.py  run_api.py  README.md  requirements.txt
```

---

## 6. 第 4 步：安装 Python 依赖包

"依赖包"就是别人写好的代码库，我们的项目需要用到它们。

### 6.1 确保虚拟环境已激活

```bash
conda activate churn_analysis
```

### 6.2 安装依赖

```bash
# 在项目根目录下执行
pip install -r requirements.txt
```

这会自动安装 pandas、numpy、scikit-learn、fastapi、matplotlib 等包。等待 2-5 分钟。

### 6.3 验证安装

```bash
python -c "import pandas; import sklearn; import fastapi; print('✅ 所有依赖安装成功！')"
```

如果输出了 `✅ 所有依赖安装成功！`，说明一切正常。

> ⚠️ **已知问题**：`xgboost` 和 `shap` 包可能安装失败（尤其在 Windows 上）。这不影响核心功能运行，项目已经做了兼容处理——只用到 Logistic Regression 模型。

---

## 7. 第 5 步：运行数据分析流程

这是整个项目的核心——运行数据分析代码，生成模型和结果。

### 7.1 确认数据文件存在

```bash
ls data/
```

应该能看到 `customer_churn_data.xlsx`。这是我们要分析的原始数据（901 个客户 × 19 个特征）。

### 7.2 运行分析

```bash
python run_analysis.py
```

这个命令会依次执行：
1. **加载数据** → 读取 Excel 文件
2. **数据清洗** → 检查缺失值、优化数据类型
3. **特征工程** → 把数据转换成算法能理解的格式
4. **关联规则挖掘** → 找出行为之间的关联模式
5. **聚类分析** → 把客户分成 5 个群体
6. **预测建模** → 训练 3 个机器学习模型并对比
7. **保存结果** → 把所有结果存到 `output/` 文件夹

**预计运行时间**：3-5 分钟（取决于电脑性能）。

### 7.3 查看分析结果

运行结束后，检查输出文件：

```bash
ls output/results/
```

你应该看到：
- `model_metrics.json` — 模型性能数据
- `clustering_results.json` — 聚类结果
- `association_rules.json` — 关联规则
- `data_report.json` — 数据质量报告

```bash
ls output/models/
```

应该看到：
- `churn_model.pkl` — 训练好的最佳模型文件

> 如果这些文件都存在，恭喜你！🎉 数据分析流程已成功运行。

### 7.4 理解发生了什么（通俗版）

刚才的运行相当于：
1. 你用 Excel 打开了一个客户数据表
2. 你让电脑自动检查了数据有没有缺失、有没有错误
3. 你告诉电脑："帮我找出哪些客户行为组合容易导致流失"
4. 你把客户分成 5 组，看看每组有什么特点
5. 你训练了一个"预测器"，输入客户特征就能预测他会不会流失
6. 你把所有结果保存了下来

只不过你是用代码而不是手动操作鼠标完成的——这就是数据分析师的工作方式。

---

## 8. 第 6 步：启动后端 API 服务

"API"是一套网络接口，让前端（网页）可以跟后端（Python 代码）通信。

### 8.1 启动服务

```bash
# 确保在项目根目录，且虚拟环境已激活
python run_api.py
```

你会看到类似这样的输出：

```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

> `127.0.0.1` 表示"本机"，`8000` 是端口号。合起来就是"在我这台电脑的 8000 号端口提供服务"。

### 8.2 测试 API 是否正常

**保持上面的终端窗口不要关**，新开一个终端窗口，输入：

```bash
curl http://127.0.0.1:8000/health
```

如果返回类似 `{"status":"ok","model_loaded":true}`，说明 API 服务正常。

也可以直接在浏览器里打开：http://127.0.0.1:8000/health

> 提示：`curl` 是一个命令行工具，用来发送网络请求。Windows 如果没有 curl，可以直接用浏览器访问。

---

## 9. 第 7 步：安装前端依赖并启动大屏

### 9.1 进入前端目录

```bash
cd frontend
```

### 9.2 安装前端依赖

```bash
npm install
```

这会下载 Vue、ECharts、Element Plus 等前端库。等待 2-5 分钟。

### 9.3 启动前端开发服务器

```bash
npm run dev
```

你会看到类似这样的输出：

```
VITE v8.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 9.4 打开浏览器

用浏览器打开：**http://localhost:5173**

你应该看到：

- 左侧深色侧边栏，有"分析概览""流失预测""客户分群""特征归因""关联规则"五个菜单
- 右侧是数据大屏的主区域
- 侧边栏底部显示"后端已连接"（绿色圆点）

> 🎉 恭喜！你已经成功运行了整个项目！

### 9.5 当前终端窗口总结

现在你的电脑上应该有 **3 个终端窗口**：

| 窗口 | 运行的命令 | 作用 |
|------|-----------|------|
| 终端 1 | `python run_api.py` | 后端 API 服务（:8000） |
| 终端 2 | `cd frontend && npm run dev` | 前端开发服务器（:5173） |
| 终端 3 | 备用 | 用来执行其他命令 |

> **不要关闭终端 1 和 2**，否则对应服务也会停止。

---

## 10. 第 8 步：理解项目结构

现在你已经把项目跑起来了，我们来看看每个文件是干什么的。

### 10.1 目录结构速览

```
customer_churn_analysis/
│
├── data/                          # 📁 存放原始数据
│   └── customer_churn_data.xlsx   # 901 个客户的 Excel 数据
│
├── src/                           # 📁 Python 源代码（后端）
│   ├── data_loader.py             # 第 1 步：读取数据 + 质量检查
│   ├── feature_engineering.py     # 第 2 步：把数据转成算法能用的格式
│   ├── association_rules.py      # 第 3 步：找出行为之间的关联
│   ├── clustering.py              # 第 4 步：把客户分成不同群体
│   ├── prediction.py              # 第 5 步：训练预测模型
│   ├── explainability.py          # 第 6 步：解释模型为什么做这个预测
│   ├── visualization.py           # 第 7 步：画图
│   ├── api.py                     # 预测 API（/predict）
│   └── api_v2.py                  # 分析数据 API（/api/summary 等）
│
├── frontend/                      # 📁 Vue 前端代码
│   └── src/
│       ├── views/                 # 5 个页面组件
│       │   ├── OverviewView.vue   # 分析概览页
│       │   ├── PredictionView.vue # 流失预测页
│       │   ├── SegmentationView.vue # 客户分群页
│       │   ├── FeaturesView.vue   # 特征归因页
│       │   └── RulesView.vue      # 关联规则页
│       ├── components/            # 可复用的 UI 组件
│       └── api/index.ts           # 前端与后端的通信代码
│
├── output/                        # 📁 运行结果
│   ├── models/churn_model.pkl     # 训练好的预测模型
│   └── results/                   # 各种 JSON 分析结果
│
├── tests/                         # 📁 自动化测试
├── notebooks/                     # 📁 Jupyter Notebook
│
├── run_analysis.py                # 🚀 一键运行全部分析
├── run_api.py                     # 🚀 启动后端服务
└── requirements.txt               # Python 依赖包列表
```

### 10.2 数据流是怎么跑的

```
Excel 原始数据
    ↓  (data_loader.py 读取)
pandas DataFrame
    ↓  (feature_engineering.py 编码)
23 列数值特征
    ↓  ├→ (association_rules.py) → 关联规则
    ↓  ├→ (clustering.py)        → 客户分群
    ↓  └→ (prediction.py)        → 预测模型 → churn_model.pkl
    ↓
output/results/*.json
    ↓  (api_v2.py 读取)
FastAPI 接口
    ↓  (HTTP 请求)
Vue3 大屏展示
```

---

## 11. 第 9 步：核心概念通俗解释

### 什么是特征（Feature）？

特征就是用来描述一个东西的属性。比如描述一个人：
- 年龄 = 28
- 收入 = 15000
- 性别 = 男
- 上月购买次数 = 3

在这个项目里，一个客户有 17 个特征，比如"使用平台时间""上月投诉次数""上月平均折扣金额"等。

### 什么是标签（Label）？

标签就是你想要预测的目标。在这个项目里，标签是"客户是否流失"（0=没流失，1=流失了）。

### 什么是训练模型？

想象你要教一个小孩分辨猫和狗：
1. 你给他看 100 张猫的照片，告诉他"这是猫"
2. 你给他看 100 张狗的照片，告诉他"这是狗"
3. 然后你拿出一张新照片，问他"这是什么？"
4. 他根据之前学到的规律来判断

训练模型就是这个过程：
1. 给模型看 720 个客户的数据 + 他们是否流失的答案（训练集）
2. 模型自己总结规律（比如"投诉多的客户容易流失"）
3. 用 181 个新客户考考它（测试集）
4. 看它答对了多少（准确率、ROC-AUC 等指标）

### 什么是 ROC-AUC？

ROC-AUC 是一个衡量模型好坏的数字，范围是 0.5 到 1.0：
- **0.5**：模型跟瞎猜一样（没用）
- **0.7-0.8**：还行，能用
- **0.8-0.9**：不错，预测比较准
- **0.9+**：非常优秀

我们项目最好的模型达到 0.8605，属于"不错"的水平。

### 什么是 Precision 和 Recall？

- **Precision（精准率）**：模型预测"会流失"的客户中，真的流失了的比例。精准率高 = 误报少。
- **Recall（召回率）**：所有真正流失的客户中，被模型找出来的比例。召回率高 = 漏报少。

这两个指标通常是鱼与熊掌的关系——提高一个就会降低另一个。

**通俗类比**：机场安检找危险物品
- Precision 高：安检响了就真的有危险品（不浪费人力）
- Recall 高：所有危险品都被找出来了（不漏掉）

### 什么是聚类（Clustering）？

聚类就是"把相似的东西放一组"。不需要提前知道分几组，算法自己找规律。

比如你有 901 个客户，你想知道"有哪些类型的客户"：
- 算法根据客户的行为特征，自动把他们分成 5 组
- 你可能发现：第 1 组是"高消费 VIP"，第 2 组是"价格敏感型"，等等

这个项目的聚类质量不太好（轮廓系数 0.147），说明客户之间的界限比较模糊——这也是正常的，人不是非黑即白的。

### 什么是关联规则（Association Rules）？

关联规则就是找"买了 A 的人通常也会买 B"这类规律。

**经典例子**：超市发现买尿布的人经常会买啤酒，于是把尿布和啤酒放在一起。

在我们的项目里，关联规则发现：**"高折扣 + 流失标签"经常和"投诉 + App 使用"一起出现**。

**Support（支持度）**：这个规则在数据中出现的频率。Support=0.1 意味着 10% 的客户符合这个模式。

**Confidence（置信度）**：如果 A 出现，B 出现的概率。Confidence=0.56 意味着 A 出现时，56% 的情况下 B 也会出现。

**Lift（提升度）**：比随机情况高多少倍。Lift=1.86 意味着比随机碰到的概率高 1.86 倍。Lift > 1 才有意义。

---

## 12. 第 10 步：如何从项目中学习

### 12.1 如果你是零基础

建议按顺序学习：

1. **先学会看**：把大屏的 5 个页面都点一遍，理解每个图表在说什么
2. **再看数据**：用 Excel 打开 `data/customer_churn_data.xlsx`，对照大屏理解原始数据
3. **读代码**：打开 `src/data_loader.py`，从最简单的文件开始读，遇到不懂的函数就搜索
4. **改参数**：试着修改 `run_analysis.py` 中的参数（比如把聚类数 k 从 5 改成 3），重新运行看结果
5. **加注释**：给每段代码加中文注释，确保你理解了每一行

### 12.2 如果你想学到面试能说的程度

重点理解：
1. **项目流程**：数据清洗 → 特征工程 → 建模 → 评估 → 解释 → 展示
2. **为什么选了 Logistic Regression**：因为 ROC-AUC 最高（0.8605），但也要提 XGBoost 的 Precision 更好
3. **聚类结果为什么不好**：轮廓系数 0.147，说明数据不够"聚"，但这是一个真实的发现，不是失败
4. **业务价值**：能帮运营部门找出高风险客户，提前干预，降低流失率
5. **技术栈选择**：为什么用 FastAPI（快、自动生成文档）+ Vue3（响应式、组件化）+ ECharts（交互式图表）

### 12.3 可以做的练习

1. **基础**：把聚类数改成 3，重新运行，看看轮廓系数变好了还是变差了
2. **进阶**：在 `PredictionView.vue` 里修改表单的默认值，看预测结果怎么变化
3. **挑战**：给大屏添加第 6 个页面（比如"数据质量报告"页）

---

## 13. 常见问题排查

### Q1: `conda` 命令找不到

**原因**：Miniconda 没有正确安装或没有加入环境变量。

**解决**：
- Windows：在开始菜单搜索 "Anaconda Prompt"，用它打开终端
- macOS/Linux：运行 `~/miniconda3/bin/conda init` 然后重启终端

### Q2: `pip install -r requirements.txt` 报错

**原因**：某个包安装失败。

**解决**：
```bash
# 逐个安装，跳过失败的包
pip install pandas numpy scikit-learn fastapi uvicorn matplotlib plotly mlxtend openpyxl
```

### Q3: `python run_analysis.py` 报 "No module named xxx"

**原因**：虚拟环境没有激活，或者依赖没装全。

**解决**：
```bash
conda activate churn_analysis
pip install 报错里提到的模块名
```

### Q4: 前端 `npm run dev` 后页面是空白的

**原因**：
1. 后端 API 服务没有启动（检查终端 1 是否在运行）
2. 端口 5173 被其他程序占用

**解决**：
- 确保 `python run_api.py` 在一个终端中运行
- 尝试 `npm run dev -- --port 3000` 换个端口

### Q5: 侧边栏显示"后端未连接"（红色圆点）

**原因**：后端 API 服务没有启动或已经停止。

**解决**：回到运行 `python run_api.py` 的终端，确认服务还在运行。如果报错了，根据错误信息排查。

### Q6: `npm install` 很慢或失败

**原因**：npm 默认从国外服务器下载。

**解决**：使用国内镜像：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Q7: 内存不足

**原因**：电脑内存小于 4GB。

**解决**：关闭其他程序（浏览器标签页、办公软件等），释放内存。这个项目本身不会占用太多资源。

---

## 14. 进阶学习路径

当你已经能顺利运行整个项目并理解了基本概念后，可以按以下路径深入学习：

### 阶段 1：Python 基础（1-2 周）

- 学习资源：[廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400)（免费中文）
- 重点：变量、列表、字典、函数、类、文件读写
- 目标：能看懂 `src/` 里的 Python 代码

### 阶段 2：数据分析三件套（2-3 周）

- **pandas**：数据处理和清洗（最重要！）
- **numpy**：数值计算
- **matplotlib**：画图

推荐书籍：《利用 Python 进行数据分析》（Wes McKinney 著）

### 阶段 3：机器学习入门（3-4 周）

- 理解监督学习 vs 无监督学习
- 掌握常用算法：线性回归、逻辑回归、决策树、随机森林、K-Means
- 理解评估指标：准确率、精准率、召回率、ROC-AUC、轮廓系数

推荐课程：Andrew Ng 的《Machine Learning》（Coursera，有中文字幕）

### 阶段 4：全栈数据项目（4-6 周）

- 学习 FastAPI 写后端 API
- 学习 Vue 3 基础（或者选 React）
- 学习 ECharts 画交互图表
- 做一个自己的数据分析项目（从头到尾）

### 推荐学习资源汇总

| 资源 | 适合阶段 | 语言 | 费用 |
|------|---------|------|------|
| 廖雪峰 Python 教程 | 阶段 1 | 中文 | 免费 |
| Python for Data Analysis 书籍 | 阶段 2 | 英文 | 付费 |
| Kaggle 入门课程 | 阶段 2-3 | 英文 | 免费 |
| Andrew Ng ML 课程 | 阶段 3 | 英文（中字） | 免费 |
| FastAPI 官方文档 | 阶段 4 | 英文 | 免费 |
| Vue 3 官方教程 | 阶段 4 | 中文 | 免费 |

---

> **最后的话**
>
> 这个项目展示了一个完整的数据分析项目是什么样的。你不必一开始就理解所有代码。学习是一个循序渐进的过程——先把项目跑起来，然后弄懂一个模块，再弄懂下一个模块。每理解一个概念，你就进步了一点。
>
> 遇到问题不要怕，搜索错误信息是程序员最重要的技能之一。把报错信息复制到 Google/Bing/百度，大概率别人也遇到并解决过。
>
> 祝你学习顺利！🚀

---

> **文档创建时间**：2026-06-02
>
> **配套项目**：[customer-churn-analysis](https://github.com/WaGll/customer-churn-analysis)
>
> **相关文档**：[README.md](./README.md) | [PROJECT_STATUS.md](./PROJECT_STATUS.md) | [PROJECT_REPORT.md](./PROJECT_REPORT.md)

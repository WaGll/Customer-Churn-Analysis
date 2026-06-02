<script setup lang="ts">
import { ref, onMounted } from 'vue'
import KpiCard from '@/components/KpiCard.vue'
import AppIcon from '@/components/AppIcon.vue'
import BarChart from '@/components/chart/BarChart.vue'
import PieChart from '@/components/chart/PieChart.vue'
import { fetchSummary, fetchModelMetrics, type SummaryResponse, type ModelMetricsResponse } from '@/api'
import { toPercent, toThousands, toCNY, toFixed } from '@/utils/format'
import { makeTooltip, BAR_RADIUS, BAR_RADIUS_RIGHT, makeAnimationConfig, FOREST_GREEN_GRADIENT, FOREST_H_GRADIENT, AMBER_GRADIENT, AMBER_RED_GRADIENT } from '@/styles/chartTheme'

const summary = ref<SummaryResponse | null>(null)
const modelMetrics = ref<ModelMetricsResponse | null>(null)
const loading = ref(true)
const error = ref('')

const tenureChartOption = ref<any>({})
const categoryChartOption = ref<any>({})
const donutOption = ref<any>({})

onMounted(async () => {
  try {
    const [s, m] = await Promise.all([fetchSummary(), fetchModelMetrics()])
    summary.value = s
    modelMetrics.value = m

    tenureChartOption.value = {
      tooltip: makeTooltip({ trigger: 'axis' }),
      legend: {
        data: ['总客户', '流失客户'],
        bottom: 0,
        textStyle: { color: '#64748B', fontSize: 12, fontFamily: 'Inter, sans-serif' },
      },
      grid: { left: 48, right: 24, top: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: s.tenure_churn_distribution.map(d => d.tenure_bin),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#94A3B8', fontFamily: 'Inter, sans-serif' },
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        {
          name: '总客户', type: 'bar',
          data: s.tenure_churn_distribution.map(d => d.total),
          itemStyle: { borderRadius: BAR_RADIUS, color: FOREST_GREEN_GRADIENT },
          barGap: '10%',
          ...makeAnimationConfig(1000),
        },
        {
          name: '流失客户', type: 'bar',
          data: s.tenure_churn_distribution.map(d => d.churned),
          itemStyle: { borderRadius: BAR_RADIUS, color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#86EFAC' }, { offset: 1, color: '#22C55E' }] } },
          ...makeAnimationConfig(1000),
        },
      ],
    }

    const churned = s.churned_count
    const retained = s.total_customers - churned
    donutOption.value = {
      tooltip: makeTooltip({
        trigger: 'item',
        formatter: (p: any) =>
          `<div style="display:flex;align-items:center;gap:8px">` +
          `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color}"></span>` +
          `<span style="font-weight:600">${p.name}</span>` +
          `<span style="color:#64748B">${p.value} 人 (${p.percent}%)</span></div>`,
      }),
      series: [{
        type: 'pie',
        radius: ['62%', '78%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 4 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 12, color: '#64748B', fontFamily: 'Inter, sans-serif' },
        emphasis: { scaleSize: 6 },
        data: [
          { value: retained, name: '留存客户', itemStyle: { color: '#0F4A28' } },
          { value: churned, name: '流失客户', itemStyle: { color: '#E2E8F0' } },
        ],
      }],
    }

    const cats = s.category_churn
    categoryChartOption.value = {
      tooltip: makeTooltip({
        trigger: 'axis',
        formatter: (p: any) =>
          `<div style="display:flex;align-items:center;gap:8px">` +
          `<span style="color:#64748B">${p[0].name}</span>` +
          `<span style="font-weight:600;color:#F59E0B">${(p[0].value * 100).toFixed(1)}%</span></div>`,
      }),
      grid: { left: 120, right: 56, top: 12, bottom: 24 },
      xAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { formatter: (v: number) => (v * 100).toFixed(0) + '%', color: '#94A3B8' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'category',
        data: cats.map(c => c.category).reverse(),
        inverse: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#64748B', fontSize: 12, fontFamily: 'Inter, sans-serif' },
      },
      series: [{
        type: 'bar',
        data: cats.map(c => ({
          value: c.churn_rate,
          itemStyle: {
            borderRadius: BAR_RADIUS_RIGHT,
            color: c.churn_rate > 0.3
              ? AMBER_RED_GRADIENT
              : c.churn_rate > 0.2
                ? AMBER_GRADIENT
                : FOREST_H_GRADIENT,
          },
        })).reverse(),
        barMaxWidth: 24,
        ...makeAnimationConfig(900),
        label: {
          show: true,
          formatter: (p: any) => (p.value * 100).toFixed(1) + '%',
          position: 'right',
          color: '#64748B',
          fontSize: 11,
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { type: 'dashed', color: '#94A3B8', width: 1 },
          label: { formatter: '均值', color: '#94A3B8', fontSize: 11 },
          data: [{
            xAxis: cats.reduce((s, c) => s + c.churn_rate, 0) / cats.length,
          }],
        },
      }],
    }
  } catch (e: any) {
    error.value = e.message || '数据加载失败'
  } finally {
    loading.value = false
  }
})

const modelNames: Record<string, string> = {
  LogisticRegression: 'Logistic Regression',
  RandomForest: 'Random Forest',
  XGBoost: 'XGBoost',
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">分析概览</h2>
        <p class="page-desc">客户流失核心指标与数据分布总览</p>
      </div>
    </div>

    <div v-if="loading" class="skeleton-grid">
      <div class="skeleton-card" v-for="i in 4" :key="i">
        <div class="skeleton-line skeleton-line-lg" />
        <div class="skeleton-line skeleton-line-md" />
        <div class="skeleton-line skeleton-line-sm" />
      </div>
    </div>

    <div v-else-if="error" class="status-message status-error">
      <AppIcon name="alert-triangle" :size="32" />
      <p>{{ error }}</p>
      <p class="status-hint">请先运行 <code>python run_analysis.py</code> 生成分析结果</p>
    </div>

    <template v-else-if="summary">
      <!-- Data Snapshot Bar -->
      <div class="snapshot-bar">
        <div class="snapshot-left">
          <AppIcon name="check-circle" :size="16" style="color:#22C55E" />
          <span class="snapshot-text">数据已就绪</span>
          <span class="snapshot-divider" />
          <span class="snapshot-text">分析周期：最近 12 个月</span>
        </div>
        <div class="snapshot-right">
          <span class="snapshot-refresh-hint">数据每 24 小时自动刷新</span>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-row stagger-list">
        <KpiCard label="客户总数" :value="toThousands(summary.total_customers)" color="#4ADE80" featured>
          <template #icon>
            <span class="kpi-icon kpi-icon-featured-bg">
              <AppIcon name="users" :size="20" />
            </span>
          </template>
          <template #trend>
            <span class="trend-pill trend-up">↑ 活跃用户</span>
          </template>
        </KpiCard>
        <KpiCard label="流失率" :value="toPercent(summary.churn_rate)" color="#EF4444">
          <template #icon>
            <span class="kpi-icon">
              <AppIcon name="trending-down" :size="20" />
            </span>
          </template>
          <template #trend>
            <span class="trend-pill trend-down">需关注</span>
          </template>
        </KpiCard>
        <KpiCard label="平均折扣金额" :value="toCNY(summary.avg_discount)" color="#F59E0B">
          <template #icon>
            <span class="kpi-icon">
              <AppIcon name="dollar-sign" :size="20" />
            </span>
          </template>
          <template #trend>
            <span class="trend-pill trend-neutral">用户福利</span>
          </template>
        </KpiCard>
        <KpiCard label="流失客户数" :value="toThousands(summary.churned_count)" color="#0EA5E9">
          <template #icon>
            <span class="kpi-icon">
              <AppIcon name="alert-triangle" :size="20" />
            </span>
          </template>
          <template #trend>
            <span class="trend-pill trend-info">监测中</span>
          </template>
        </KpiCard>
      </div>

      <!-- Donut + AI Insight Row -->
      <div class="donut-row">
        <div class="chart-card donut-card">
          <div class="chart-card-header">整体流失率分布</div>
          <div class="chart-card-body donut-chart-container">
            <PieChart :option="donutOption" height="260px" />
            <div class="donut-center-text">
              <span class="donut-center-value count-up">{{ toThousands(summary.total_customers) }}</span>
              <span class="donut-center-label">总客户</span>
            </div>
          </div>
        </div>

        <!-- AI Engine Insight Brief Card -->
        <div class="ai-brief-card">
          <div class="ai-card-header">
            <span class="ai-breath-dot" />
            <span class="ai-label">AI Engine Insight</span>
          </div>
          <div class="ai-insights">
            <div class="ai-insight-block">
              <p class="ai-insight-title">流失结构分析</p>
              <p class="ai-insight-text">
                基于 <strong style="color:#0F4A28;font-weight:700">901 条客户数据</strong>，整体流失率为
                <strong style="color:#EF4444;font-weight:700">16.7%</strong>。高租期客户
                <strong style="color:#0F4A28">（&gt;24月）</strong>留存显著优于新客，
                <span style="color:#F59E0B;font-weight:600">前 6 个月是流失高危窗口</span>，建议在此阶段加强新客引导与福利触达。
              </p>
            </div>
            <div class="ai-insight-block">
              <p class="ai-insight-title">品类与折扣洞察</p>
              <p class="ai-insight-text">
                <strong style="color:#0F4A28;font-weight:700">移动设备</strong>与
                <strong style="color:#0F4A28;font-weight:700">时尚</strong>品类流失率最高（&gt;22%），
                平均折扣 <strong style="color:#F59E0B;font-weight:700">¥72.4</strong> 显著低于留存客户（¥138.2）。
                <span style="color:#EF4444;font-weight:600">折扣不足可能加速流失</span>，建议对高频品类实施阶梯优惠策略。
              </p>
            </div>
            <div class="ai-insight-block">
              <p class="ai-insight-title">行动建议</p>
              <p class="ai-insight-text">
                1. 对<span style="color:#0F4A28;font-weight:700">租期&lt;6月</span>新客启动自动化 Onboarding<br/>
                2. 对<span style="color:#F59E0B;font-weight:700">低折扣</span>高频客户触发定向优惠券<br/>
                3. 每月监测<span style="color:#EF4444;font-weight:700">高流失品类</span>客户满意度变化
              </p>
            </div>
          </div>
          <div class="ai-card-actions">
            <el-button plain round size="small" class="ai-btn-secondary">导出报告</el-button>
            <el-button type="primary" round size="small" class="ai-btn-primary">
              查看详细分析 →
            </el-button>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="chart-row stagger-list">
        <div class="chart-card">
          <div class="chart-card-header">平台使用时长的流失分布</div>
          <div class="chart-card-body">
            <BarChart :option="tenureChartOption" height="340px" />
          </div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">各类别流失率对比</div>
          <div class="chart-card-body">
            <BarChart :option="categoryChartOption" height="340px" />
          </div>
        </div>
      </div>

      <!-- Model Performance Cards -->
      <div v-if="modelMetrics" class="section-header">
        <h3 class="section-title">模型性能对比</h3>
        <el-tag type="success" size="small" effect="light">
          最佳: {{ modelNames[modelMetrics.best_model] || modelMetrics.best_model }}
        </el-tag>
      </div>
      <div v-if="modelMetrics" class="model-cards stagger-list">
        <div
          v-for="[key, m] in Object.entries(modelMetrics.models)"
          :key="key"
          class="model-card-item"
          :class="{ 'model-best': key === modelMetrics.best_model }"
        >
          <div class="model-card-header">
            <span class="model-name">{{ modelNames[key] || key }}</span>
            <el-tag v-if="key === modelMetrics.best_model" type="success" size="small" effect="dark" round>
              推荐
            </el-tag>
          </div>
          <div class="model-metrics-grid">
            <div class="model-metric">
              <span class="model-metric-label">Accuracy</span>
              <span class="model-metric-value">{{ toFixed(m.accuracy) }}</span>
            </div>
            <div class="model-metric">
              <span class="model-metric-label">Precision</span>
              <span class="model-metric-value">{{ toFixed(m.precision) }}</span>
            </div>
            <div class="model-metric">
              <span class="model-metric-label">Recall</span>
              <span class="model-metric-value">{{ toFixed(m.recall) }}</span>
            </div>
            <div class="model-metric">
              <span class="model-metric-label">F1 Score</span>
              <span class="model-metric-value">{{ toFixed(m.f1) }}</span>
            </div>
            <div class="model-metric model-metric-highlight">
              <span class="model-metric-label">ROC-AUC</span>
              <span class="model-metric-value" :class="{ 'text-primary': key === modelMetrics.best_model }">
                {{ toFixed(m.roc_auc) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <el-alert type="info" :closable="false" class="model-note" show-icon>
        <template #title>
          最佳模型基于 ROC-AUC 选择。实际应用中需综合考虑 Precision 与 Recall 的权衡。
        </template>
      </el-alert>
    </template>
  </div>
</template>

<style scoped>
.page {
  max-width: 1440px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-section-gap);
}
.page-header-left { min-width: 0; }
.page-title {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-heading);
  color: var(--color-text-primary);
  margin-bottom: 4px;
  font-family: var(--font-family-sans);
}
.page-desc {
  font-size: var(--font-size-subtitle);
  color: var(--color-text-secondary);
  margin: 0;
}

/* KPI */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-item-gap);
  margin-bottom: var(--spacing-section-gap);
}
.kpi-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  color: currentColor;
}
.kpi-icon-featured-bg {
  background: rgba(255, 255, 255, 0.15);
}

/* Trend Pills */
.trend-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-family-sans);
  letter-spacing: 0.2px;
}
.trend-up { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.trend-down { background: rgba(239, 68, 68, 0.1); color: #EF4444; }
.trend-neutral { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
.trend-info { background: rgba(14, 165, 233, 0.1); color: #0EA5E9; }

/* Data Snapshot Bar */
.snapshot-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 20px;
  margin-bottom: var(--spacing-section-gap);
}
.snapshot-left, .snapshot-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.snapshot-text { font-size: 13px; color: var(--color-text-secondary); }
.snapshot-divider {
  width: 1px;
  height: 14px;
  background: var(--color-border);
}
.snapshot-refresh-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: var(--font-family-mono);
}

/* Chart Cards — Donezo clean style */
.chart-card {
  background: var(--color-bg-card);
  border: none;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-slow);
  overflow: hidden;
}
.chart-card:hover {
  box-shadow: var(--shadow-card-hover);
}
.chart-card-header {
  padding: 20px var(--spacing-card-padding) 0;
  font-weight: 600;
  font-size: 15px;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  font-family: var(--font-family-sans);
}
.chart-card-body {
  padding: var(--spacing-card-padding);
}

/* Donut + AI Row */
.donut-row {
  display: grid;
  grid-template-columns: 14fr 10fr;
  gap: var(--spacing-item-gap);
  margin-bottom: var(--spacing-section-gap);
}
.donut-card { }
.donut-chart-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.donut-center-text {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
}
.donut-center-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
}
.donut-center-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

/* AI Engine Insight Brief Card */
.ai-brief-card {
  background:
    radial-gradient(circle, rgba(15, 74, 40, 0.03) 1px, transparent 1px),
    linear-gradient(135deg, rgba(255,255,255,0.92), rgba(248,250,252,0.88));
  background-size: 20px 20px, 100% 100%;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(15,74,40,0.06);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card), 0 0 0 1px rgba(74,222,128,0.04);
  padding: var(--spacing-card-padding);
  display: flex;
  flex-direction: column;
  transition: box-shadow var(--transition-slow);
}
.ai-brief-card:hover {
  box-shadow: var(--shadow-card-hover), 0 0 0 1px rgba(74,222,128,0.08);
}

.ai-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
}
.ai-breath-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #4ADE80;
  box-shadow: 0 0 8px rgba(74,222,128,0.4);
  animation: breath-glow 2s ease-in-out infinite;
  flex-shrink: 0;
}
.ai-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-sans);
  letter-spacing: -0.2px;
}

.ai-insights {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ai-insight-block {
  padding: 12px 14px;
  background: rgba(15,74,40,0.02);
  border-radius: var(--radius-sm);
  border-left: 3px solid rgba(15,74,40,0.1);
}
.ai-insight-title {
  font-size: 13px;
  font-weight: 700;
  color: #0F4A28;
  margin: 0 0 6px 0;
  font-family: var(--font-family-sans);
}
.ai-insight-text {
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--color-text-secondary);
  margin: 0;
}

.ai-card-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
}
.ai-btn-secondary {
  border-color: var(--color-border-subtle);
  color: var(--color-text-secondary);
  font-size: 13px;
}
.ai-btn-secondary:hover {
  border-color: #0F4A28;
  color: #0F4A28;
}
.ai-btn-primary {
  background: #0F4A28;
  border-color: #0F4A28;
  font-size: 13px;
  font-weight: 600;
}
.ai-btn-primary:hover {
  background: #0D3E22;
  border-color: #0D3E22;
}

/* Chart Grid */
.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-item-gap);
  margin-bottom: var(--spacing-section-gap);
}

/* Section Header */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: var(--spacing-item-gap);
}
.section-title {
  font-size: var(--font-size-section);
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-family-sans);
}

/* Model Performance Cards */
.model-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-item-gap);
  margin-bottom: var(--spacing-section-gap);
}
.model-card-item {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: var(--spacing-card-padding);
  transition: all var(--transition-slow);
  box-shadow: var(--shadow-card);
}
.model-card-item:hover {
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}
.model-card-item.model-best {
  border-color: rgba(15, 74, 40, 0.2);
  box-shadow: var(--shadow-card), var(--shadow-glow-green);
}
.model-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}
.model-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-family-sans);
}
.model-metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 8px;
}
.model-metric {
  text-align: center;
}
.model-metric-highlight {
  grid-column: 1 / -1;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}
.model-metric-label {
  display: block;
  font-size: 10px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  font-weight: 600;
}
.model-metric-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
}
.model-metric-value.text-primary {
  color: #0F4A28;
}
.model-note { margin-top: 12px; font-size: 13px; }

/* Status */
.status-message { text-align: center; padding: 60px; }
.status-error {
  color: var(--color-danger);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.status-hint { color: var(--color-text-secondary); font-size: 13px; margin-top: 4px; }
.status-hint code {
  background: var(--color-border);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: var(--font-family-mono);
}

@media (max-width: 1024px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .chart-row { grid-template-columns: 1fr; }
  .donut-row { grid-template-columns: 1fr; }
  .model-cards { grid-template-columns: 1fr; }
  .skeleton-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .kpi-row { grid-template-columns: 1fr; }
  .skeleton-grid { grid-template-columns: 1fr; }
}
</style>

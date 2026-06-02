<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import ScatterChart from '@/components/chart/ScatterChart.vue'
import BarChart from '@/components/chart/BarChart.vue'
import PieChart from '@/components/chart/PieChart.vue'
import KpiCard from '@/components/KpiCard.vue'
import AppIcon from '@/components/AppIcon.vue'
import { fetchClusters, type ClustersResponse } from '@/api'
import { toPercent, toThousands, toFixed } from '@/utils/format'
import { RISK_COLORS } from '@/utils/constants'
import { makeTooltip, CLUSTER_COLORS, FOREST_GREEN_GRADIENT } from '@/styles/chartTheme'

const data = ref<ClustersResponse | null>(null)
const loading = ref(true)
const error = ref('')

const scatterOption = ref<any>({})
const pctChartOption = ref<any>({})
const churnBarOption = ref<any>({})
const clusterDonutOption = ref<any>({})
const selectedCluster = ref<number | null>(null)

onMounted(async () => {
  try {
    data.value = await fetchClusters()

    const sc = data.value.scatter_data
    const clusterIds = [...new Set(sc.map(d => d.cluster))].sort()

    scatterOption.value = {
      tooltip: makeTooltip({
        formatter: (p: any) => {
          const d = p.data
          return `<div style="line-height:1.8;font-family:Inter,sans-serif">
            <span style="font-weight:600;color:${p.color}">聚类 ${d[2]}</span><br/>
            折扣: <strong>¥${d[0].toFixed(1)}</strong><br/>
            使用时长: <strong>${d[1].toFixed(1)} 月</strong><br/>
            流失: <span style="color:${d[3] ? '#EF4444' : '#22C55E'};font-weight:600">${d[3] ? '是' : '否'}</span>
          </div>`
        },
      }),
      legend: {
        data: clusterIds.map(i => `聚类 ${i}`),
        bottom: 0,
        textStyle: { color: '#64748B', fontSize: 12, fontFamily: 'Inter, sans-serif' },
      },
      grid: { left: 60, right: 24, top: 24, bottom: 48 },
      xAxis: {
        name: '上月平均折扣金额 (¥)',
        nameLocation: 'center', nameGap: 28,
        nameTextStyle: { color: '#64748B', fontFamily: 'Inter, sans-serif' },
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
      },
      yAxis: {
        name: '使用平台时间 (月)',
        nameLocation: 'center', nameGap: 36,
        nameTextStyle: { color: '#64748B', fontFamily: 'Inter, sans-serif' },
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
      },
      series: clusterIds.map((cid, idx) => ({
        name: `聚类 ${cid}`,
        type: 'scatter',
        data: sc.filter(d => d.cluster === cid).map(d => [d.x, d.y, d.cluster, d.churn]),
        symbolSize: 10,
        itemStyle: { color: CLUSTER_COLORS[idx % CLUSTER_COLORS.length], opacity: 0.75 },
        emphasis: { scale: 1.6, itemStyle: { opacity: 1 } },
      })),
    }

    const clusters = data.value.clusters
    pctChartOption.value = {
      tooltip: makeTooltip({
        trigger: 'axis',
        formatter: (p: any) =>
          `<span style="font-weight:600;color:#0F4A28">${p[0].name}</span>: ${p[0].value}%`,
      }),
      grid: { left: 48, right: 24, top: 16, bottom: 32 },
      xAxis: {
        type: 'category', data: clusters.map(c => `聚类 ${c.id}`),
        axisLabel: { color: '#64748B', fontFamily: 'Inter, sans-serif' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value', name: '客户占比 (%)',
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        name: '客户占比', type: 'bar',
        data: clusters.map(c => c.pct),
        itemStyle: { borderRadius: [10, 10, 0, 0], color: FOREST_GREEN_GRADIENT },
        label: { show: true, formatter: '{c}%', position: 'top', color: '#64748B' },
      }],
    }

    churnBarOption.value = {
      tooltip: makeTooltip({
        trigger: 'axis',
        formatter: (p: any) =>
          `<span style="font-weight:600;color:#EF4444">${p[0].name}</span>: 流失率 ${p[0].value}%`,
      }),
      grid: { left: 48, right: 24, top: 16, bottom: 32 },
      xAxis: {
        type: 'category', data: clusters.map(c => `聚类 ${c.id}`),
        axisLabel: { color: '#64748B', fontFamily: 'Inter, sans-serif' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value', name: '流失率 (%)',
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        name: '流失率', type: 'bar',
        data: clusters.map(c => ({
          value: +(c.churn_rate * 100).toFixed(1),
          itemStyle: {
            borderRadius: [10, 10, 0, 0],
            color: c.churn_rate > 0.3
              ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#DC2626' }, { offset: 1, color: '#FCA5A5' }] }
              : c.churn_rate > 0.2
              ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#D97706' }, { offset: 1, color: '#FDE68A' }] }
              : c.churn_rate > 0.1
              ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#0284C7' }, { offset: 1, color: '#BAE6FD' }] }
              : { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#15803D' }, { offset: 1, color: '#BBF7D0' }] },
          },
        })),
        label: { show: true, formatter: '{c}%', position: 'top', color: '#64748B' },
      }],
    }
    clusterDonutOption.value = {
      tooltip: makeTooltip({
        trigger: 'item',
        formatter: (p: any) =>
          `<span style="font-weight:600;color:${p.color}">${p.name}</span>: ${p.value}%`,
      }),
      series: [{
        type: 'pie',
        radius: ['55%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 10, color: '#64748B' },
        data: clusters.map((c, idx) => ({
          value: c.pct,
          name: `聚类 ${c.id}`,
          itemStyle: { color: CLUSTER_COLORS[idx % CLUSTER_COLORS.length] },
        })),
      }],
    }
  } catch (e: any) {
    error.value = e.message || '数据加载失败'
  } finally {
    loading.value = false
  }
})

// Scatter plot dimming on cluster select
watch(selectedCluster, (sc) => {
  if (!scatterOption.value?.series) return
  const updated = scatterOption.value.series.map((s: any) => ({
    ...s,
    itemStyle: {
      ...s.itemStyle,
      opacity: sc === null ? 0.75 : (s.name === `聚类 ${sc}` ? 0.95 : 0.1),
    },
    symbolSize: sc === null ? 10 : (s.name === `聚类 ${sc}` ? 12 : 7),
  }))
  scatterOption.value = { ...scatterOption.value, series: updated }
})

function getChurnColor(rate: number): string {
  if (rate < 0.1) return RISK_COLORS.low
  if (rate < 0.2) return RISK_COLORS.medium
  if (rate < 0.4) return RISK_COLORS.high
  return RISK_COLORS.critical
}

function getSilhouetteColor(score: number): string {
  if (score < 0.25) return '#EF4444'
  if (score < 0.5) return '#F59E0B'
  return '#22C55E'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">客户分群</h2>
        <p class="page-desc">K-Means 聚类分析 — 发现客户群体特征与流失模式差异</p>
      </div>
    </div>

    <div v-if="loading" class="status-center"><el-skeleton :rows="4" animated /></div>

    <div v-else-if="error" class="status-center status-error">
      <AppIcon name="alert-triangle" :size="32" />
      <p>{{ error }}</p>
      <p class="status-hint">请先运行 <code>python run_analysis.py</code> 生成聚类结果</p>
    </div>

    <template v-else-if="data">
      <div class="kpi-row">
        <KpiCard label="聚群数量" :value="data.n_clusters" color="#0F4A28">
          <template #icon><span class="kpi-icon"><AppIcon name="layout-dashboard" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="轮廓系数" :value="toFixed(data.silhouette_score, 3)" :color="getSilhouetteColor(data.silhouette_score)">
          <template #icon><span class="kpi-icon"><AppIcon name="check-circle" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="最高流失率群" :value="toPercent(Math.max(...data.clusters.map(c => c.churn_rate)))" color="#EF4444">
          <template #icon><span class="kpi-icon"><AppIcon name="alert-triangle" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="最低流失率群" :value="toPercent(Math.min(...data.clusters.map(c => c.churn_rate)))" color="#22C55E">
          <template #icon><span class="kpi-icon"><AppIcon name="trending-down" :size="20" /></span></template>
        </KpiCard>
      </div>

      <!-- Silhouette Score Warning -->
      <div v-if="data.silhouette_score < 0.25" class="silhouette-warning">
        <AppIcon name="alert-triangle" :size="16" style="color:#F59E0B;flex-shrink:0" />
        <div>
          <p class="silhouette-warning-title">轮廓系数 {{ data.silhouette_score.toFixed(3) }} — 聚类质量提示</p>
          <p class="silhouette-warning-text">该得分反映了真实商业场景中客户群落的交叉特征。建议结合业务标签验证聚类结果。</p>
        </div>
      </div>

      <!-- Cluster Cards -->
      <div class="cluster-cards stagger-list">
        <el-card
          v-for="(c, idx) in data.clusters"
          :key="c.id" shadow="hover"
          class="cluster-card"
          :class="{ selected: selectedCluster === c.id }"
          :style="{ animationDelay: idx * 80 + 'ms' }"
          @click="selectedCluster = selectedCluster === c.id ? null : c.id"
        >
          <div class="cluster-header">
            <span class="cluster-id">聚类 {{ c.id }}</span>
            <el-tag
              :type="c.churn_rate > 0.2 ? 'danger' : c.churn_rate > 0.1 ? 'warning' : 'success'"
              size="small" effect="light"
            >{{ toPercent(c.churn_rate) }}</el-tag>
          </div>
          <div class="cluster-size">{{ toThousands(c.size) }} 人</div>
          <div class="cluster-pct">{{ c.pct }}%</div>
          <!-- Mini churn rate bar -->
          <div class="cluster-mini-bar">
            <div
              class="cluster-mini-bar-fill"
              :style="{
                width: (c.churn_rate * 100).toFixed(0) + '%',
                background: getChurnColor(c.churn_rate),
              }"
            />
          </div>
          <div class="cluster-label" :title="c.label">{{ c.label }}</div>
        </el-card>
      </div>

      <!-- Scatter + Insights (14:10 Golden Ratio) -->
      <el-row :gutter="20" class="scatter-row">
        <el-col :span="14">
          <div class="chart-card scatter-block" :class="{ 'scatter-highlighted': selectedCluster !== null }">
            <div class="chart-card-header">折扣金额 × 使用时长（按聚类着色）</div>
            <div class="chart-card-body">
              <ScatterChart :option="scatterOption" height="440px" />
            </div>
          </div>
        </el-col>
        <el-col :span="10">
          <div class="right-panel">
            <!-- Cluster Distribution Donut -->
            <div class="chart-card">
              <div class="chart-card-header">聚群分布</div>
              <div class="chart-card-body">
                <PieChart :option="clusterDonutOption" height="220px" />
              </div>
            </div>
            <div class="section-divider" />
            <!-- Cluster Overview -->
            <div class="chart-card">
              <div class="chart-card-header">聚群概览</div>
              <div class="chart-card-body">
                <div class="cluster-overview-grid">
                  <div class="co-item">
                    <span class="co-label">最高流失群</span>
                    <span class="co-value" style="color:#EF4444">聚类 {{ data.clusters.reduce((a, b) => a.churn_rate > b.churn_rate ? a : b).id }}</span>
                    <span class="co-sub">{{ toPercent(data.clusters.reduce((a, b) => a.churn_rate > b.churn_rate ? a : b).churn_rate) }}</span>
                  </div>
                  <div class="co-item">
                    <span class="co-label">最低流失群</span>
                    <span class="co-value" style="color:#22C55E">聚类 {{ data.clusters.reduce((a, b) => a.churn_rate < b.churn_rate ? a : b).id }}</span>
                    <span class="co-sub">{{ toPercent(data.clusters.reduce((a, b) => a.churn_rate < b.churn_rate ? a : b).churn_rate) }}</span>
                  </div>
                  <div class="co-item">
                    <span class="co-label">轮廓系数</span>
                    <span class="co-value" :style="{ color: data.silhouette_score < 0.25 ? '#EF4444' : data.silhouette_score < 0.5 ? '#F59E0B' : '#22C55E' }">{{ data.silhouette_score.toFixed(3) }}</span>
                    <span class="co-sub">{{ data.silhouette_score < 0.25 ? '结构较弱' : data.silhouette_score < 0.5 ? '结构尚可' : '结构良好' }}</span>
                  </div>
                  <div class="co-item">
                    <span class="co-label">最大聚群</span>
                    <span class="co-value">聚类 {{ data.clusters.reduce((a, b) => a.size > b.size ? a : b).id }}</span>
                    <span class="co-sub">{{ toThousands(data.clusters.reduce((a, b) => a.size > b.size ? a : b).size) }} 人</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Bar Charts -->
      <div class="chart-row stagger-list">
        <div class="chart-card">
          <div class="chart-card-header">各聚群客户占比</div>
          <div class="chart-card-body"><BarChart :option="pctChartOption" height="300px" /></div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">各聚群流失率对比</div>
          <div class="chart-card-body"><BarChart :option="churnBarOption" height="300px" /></div>
        </div>
      </div>

      <!-- Detail Table -->
      <div class="chart-card table-card">
        <div class="chart-card-header">聚类概览表</div>
        <div class="chart-card-body">
          <el-table :data="data.clusters">
            <el-table-column prop="id" label="聚类" width="80">
              <template #default="{ row }">
                <el-tag :type="row.churn_rate > 0.2 ? 'danger' : row.churn_rate > 0.1 ? 'warning' : 'success'" effect="light">
                  聚类 {{ row.id }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="客户数" width="110">
              <template #default="{ row }">{{ toThousands(row.size) }}</template>
            </el-table-column>
            <el-table-column prop="pct" label="占比" width="80">
              <template #default="{ row }">{{ row.pct }}%</template>
            </el-table-column>
            <el-table-column prop="churn_rate" label="流失率" width="180">
              <template #default="{ row }">
                <div class="table-churn-cell">
                  <div class="table-mini-bar">
                    <div
                      class="table-mini-bar-fill"
                      :style="{
                        width: Math.min(row.churn_rate * 100, 100) + '%',
                        background: getChurnColor(row.churn_rate),
                      }"
                    />
                  </div>
                  <span :style="{ color: getChurnColor(row.churn_rate), fontWeight: 600, fontFamily: 'var(--font-family-mono)', fontSize: '12px' }">
                    {{ toPercent(row.churn_rate) }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="label" label="典型特征" min-width="280">
              <template #default="{ row }">
                <span style="font-size:13px">{{ row.label }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 1440px; margin: 0 auto; }
.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: var(--spacing-section-gap);
}
.page-header-left { min-width: 0; }
.page-title {
  font-size: var(--font-size-title); font-weight: var(--font-weight-heading);
  color: var(--color-text-primary); margin-bottom: 4px; font-family: var(--font-family-sans);
}
.page-desc { font-size: var(--font-size-subtitle); color: var(--color-text-secondary); margin: 0; }

/* Status */
.status-center { text-align: center; padding: 60px 20px; }
.status-error {
  color: var(--color-danger); display: flex; flex-direction: column;
  align-items: center; gap: 12px;
}
.status-hint { color: var(--color-text-secondary); font-size: 13px; }
.status-hint code {
  background: var(--color-border); padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-family: var(--font-family-mono);
}

/* KPI */
.kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-item-gap); margin-bottom: var(--spacing-section-gap);
}
.kpi-icon {
  display: flex; align-items: center; justify-content: center;
  width: 48px; height: 48px; border-radius: 12px; color: currentColor;
}

/* Silhouette Warning */
.silhouette-warning {
  display: flex; align-items: flex-start; gap: 12px;
  background: rgba(245, 158, 11, 0.06);
  border-left: 4px solid #F59E0B;
  border-radius: var(--radius-card);
  padding: 16px var(--spacing-card-padding);
  margin-bottom: var(--spacing-section-gap);
}
.silhouette-warning-title {
  font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;
}
.silhouette-warning-text {
  font-size: 13px; color: var(--color-text-secondary); margin: 0; line-height: 1.6;
}

/* Chart Cards */
.chart-card {
  background: var(--color-bg-card); border: none;
  border-radius: var(--radius-card); box-shadow: var(--shadow-card);
  overflow: hidden; transition: box-shadow var(--transition-slow);
}
.chart-card:hover { box-shadow: var(--shadow-card-hover); }
.chart-card-header {
  padding: 20px var(--spacing-card-padding) 0;
  font-weight: 600; font-size: 15px; color: var(--color-text-primary);
  font-family: var(--font-family-sans);
}
.chart-card-body { padding: var(--spacing-card-padding); }

.scatter-block { margin-bottom: var(--spacing-section-gap); }
.scatter-highlighted { box-shadow: 0 0 0 4px rgba(15, 74, 40, 0.08); }

.chart-row {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-item-gap); margin-bottom: var(--spacing-section-gap);
}

/* Cluster Cards */
.cluster-cards {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 240px));
  gap: var(--spacing-item-gap); margin-bottom: var(--spacing-section-gap);
}
.cluster-card {
  border: 2px solid transparent; border-radius: var(--radius-card); cursor: pointer;
  background: var(--color-bg-card); box-shadow: var(--shadow-card);
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), border-color 0.3s, box-shadow 0.3s;
  animation: card-enter 0.5s ease-out both;
}
@keyframes card-enter {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.cluster-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-card-hover); }
.cluster-card.selected {
  border-color: #0F4A28;
  box-shadow: 0 0 0 2px rgba(15,74,40,0.3), 0 0 20px rgba(15,74,40,0.1);
}
.cluster-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.cluster-id { font-weight: 600; font-size: 15px; color: var(--color-text-primary); }
.cluster-size { font-size: 24px; font-weight: 700; color: var(--color-text-primary); font-family: var(--font-family-mono); }
.cluster-pct { font-size: 13px; color: var(--color-text-secondary); margin-top: 2px; }

/* Mini churn bar inside cluster card */
.cluster-mini-bar {
  margin-top: 10px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-border);
  overflow: hidden;
}
.cluster-mini-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.cluster-label {
  font-size: 12px; color: var(--color-text-secondary); margin-top: 8px;
  padding-top: 8px; border-top: 1px solid var(--color-border);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Table mini bar in churn rate column */
.table-churn-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.table-mini-bar {
  width: 60px;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  overflow: hidden;
  flex-shrink: 0;
}
.table-mini-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease-out;
}

/* Table — minimal */
.table-card { margin-bottom: 0; }
:deep(.el-table) {
  --el-table-border-color: transparent;
  --el-table-header-bg-color: transparent;
}
:deep(.el-table th.el-table__cell) {
  background: transparent; border-bottom: 1px solid var(--color-border);
  font-weight: 600; color: var(--color-text-secondary); font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.5px;
}
:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid var(--color-border); border-right: none;
}

/* Scatter row */
.scatter-row {
  margin-bottom: var(--spacing-section-gap);
}

/* Right insights panel */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-item-gap);
}
.section-divider {
  border-top: 1px dashed var(--color-border);
  margin: 0 4px;
}

/* Cluster overview grid */
.cluster-overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.co-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.co-label {
  font-size: 10px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.co-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
}
.co-sub {
  font-size: 11px;
  color: var(--color-text-muted);
}

@media (max-width: 1024px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .chart-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .kpi-row { grid-template-columns: 1fr; }
  .cluster-cards { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
}
</style>

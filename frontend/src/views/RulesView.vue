<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import KpiCard from '@/components/KpiCard.vue'
import BarChart from '@/components/chart/BarChart.vue'
import AppIcon from '@/components/AppIcon.vue'
import { fetchRules, type RulesResponse, type RuleItem } from '@/api'
import { toPercent, toThousands } from '@/utils/format'
import { makeTooltip, FOREST_H_GRADIENT, BAR_RADIUS_RIGHT } from '@/styles/chartTheme'
import { useECharts } from '@/components/chart/useECharts'

const data = ref<RulesResponse | null>(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref<'all' | 'loss'>('all')

onMounted(async () => {
  try { data.value = await fetchRules() }
  catch (e: any) { error.value = e.message || '数据加载失败' }
  finally { loading.value = false }
})

function sortRules(rules: RuleItem[]): RuleItem[] {
  return [...rules].sort((a, b) => b.lift - a.lift)
}

function getLiftClass(lift: number): string {
  if (lift >= 3) return 'lift-high'
  if (lift >= 2) return 'lift-medium'
  return 'lift-normal'
}

function getLiftTag(lift: number): string {
  if (lift >= 3) return 'danger'
  if (lift >= 2) return 'warning'
  return 'info'
}

// Build force-directed graph from rules data
const graphOption = computed(() => {
  if (!data.value) return { series: [] }
  const rules = data.value.loss_related.length > 0 ? data.value.loss_related : data.value.rules
  if (rules.length === 0) return { series: [] }

  const nodeMap = new Map<string, { name: string; category: number }>()
  const edges: any[] = []

  function getNodes(text: string, category: number) {
    const parts = text.split(', ')
    parts.forEach(p => {
      if (!nodeMap.has(p)) {
        nodeMap.set(p, { name: p, category })
      }
    })
  }

  rules.slice(0, 30).forEach(r => {
    getNodes(r.antecedents, 0)
    getNodes(r.consequents, 1)
    edges.push({
      source: r.antecedents.split(', ')[0],
      target: r.consequents.split(', ')[0],
      lineStyle: {
        width: Math.max(1, Math.min(r.lift * 1.5, 6)),
        color: r.lift >= 3 ? '#EF4444' : r.lift >= 2 ? '#F59E0B' : '#94A3B8',
        opacity: 0.4,
        curveness: 0.2,
      },
      value: r.lift,
    })
  })

  const nodes = Array.from(nodeMap.values())

  return {
    tooltip: makeTooltip({
      formatter: (p: any) => {
        if (p.dataType === 'edge') {
          return `<span style="color:#64748B">Lift: <strong>${p.data.value?.toFixed(2)}</strong></span>`
        }
        return `<span style="font-weight:600">${p.name}</span>`
      },
    }),
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      force: { repulsion: 120, edgeLength: [50, 120], gravity: 0.1 },
      data: nodes,
      edges,
      categories: [
        { name: '前项', itemStyle: { color: '#0F4A28' } },
        { name: '后项', itemStyle: { color: '#EF4444' } },
      ],
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      label: { show: true, fontSize: 10, color: '#64748B', fontFamily: 'Inter, sans-serif' },
      lineStyle: { opacity: 0.3 },
      emphasis: { label: { fontSize: 13, fontWeight: 600 }, itemStyle: { borderWidth: 3 } },
    }],
    animationDuration: 1500,
    animationEasingUpdate: 'cubicInOut' as const,
    toolbox: {
      show: true,
      feature: {
        restore: { title: '重置' },
        saveAsImage: { title: '保存', pixelRatio: 2 },
      },
      right: 8,
      top: 0,
    },
  }
})

// Top-5 rules bar chart for right panel
const topRulesChartOption = computed(() => {
  if (!data.value) return {}
  const top5 = sortRules(data.value.rules).slice(0, 5)
  return {
    tooltip: makeTooltip({
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (p: any) => {
        const rule = top5[p[0].dataIndex]
        return `<span style="color:#64748B">${rule.antecedents.split(', ').slice(0, 2).join(' + ')} → ${rule.consequents}</span><br/><strong>Lift: ${rule.lift.toFixed(2)}</strong>`
      },
    }),
    grid: { left: 8, right: 40, top: 8, bottom: 16 },
    xAxis: {
      type: 'value', name: 'Lift',
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#94A3B8', fontSize: 10 },
      axisLine: { show: false }, axisTick: { show: false },
    },
    yAxis: {
      type: 'category', inverse: true,
      data: top5.map(r => r.antecedents.split(', ').slice(0, 2).join('+').slice(0, 16) + '…'),
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'Inter, sans-serif' },
      axisLine: { show: false }, axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: top5.map(r => ({
        value: r.lift,
        itemStyle: {
          borderRadius: BAR_RADIUS_RIGHT,
          color: {
            ...FOREST_H_GRADIENT,
            opacity: r.lift >= 3 ? 1 : r.lift >= 2 ? 0.72 : 0.44,
          } as any,
        },
      })),
      barMaxWidth: 18,
      label: { show: true, formatter: '{c}', position: 'right', color: '#64748B', fontSize: 10 },
    }],
  }
})

// Graph chart instance
const graphChartRef = ref<HTMLElement | null>(null)
const { setOptions: setGraphOptions } = useECharts(graphChartRef, graphOption.value)

watch(graphOption, (opt) => {
  if (opt && Object.keys(opt).length > 0) {
    setGraphOptions(opt as any)
  }
}, { flush: 'post' })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">关联规则</h2>
        <p class="page-desc">挖掘客户特征与流失之间的关联模式 — Lift &gt; 1 表示正向关联，值越大关联越强</p>
      </div>
    </div>

    <div v-if="loading" class="status-center"><el-skeleton :rows="4" animated /></div>

    <div v-else-if="error" class="status-center status-error">
      <AppIcon name="alert-triangle" :size="32" />
      <p>{{ error }}</p>
      <p class="status-hint">请先运行 <code>python run_analysis.py</code> 生成关联规则</p>
    </div>

    <template v-else-if="data">
      <!-- KPI Row -->
      <div class="kpi-row stagger-list">
        <KpiCard label="展示规则数" :value="toThousands(data.rules.length)" color="#0F4A28">
          <template #icon><span class="kpi-icon"><AppIcon name="link" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="流失相关规则" :value="toThousands(data.loss_related.length)" color="#EF4444">
          <template #icon><span class="kpi-icon"><AppIcon name="alert-triangle" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="最高 Lift" :value="data.rules.length > 0 ? sortRules(data.rules)[0].lift.toFixed(2) : '-'" color="#0F4A28">
          <template #icon><span class="kpi-icon"><AppIcon name="bolt" :size="20" /></span></template>
        </KpiCard>
        <KpiCard label="平均置信度" :value="data.rules.length > 0 ? toPercent(data.rules.reduce((s, r) => s + r.confidence, 0) / data.rules.length) : '-'" color="#F59E0B">
          <template #icon><span class="kpi-icon"><AppIcon name="trending-up" :size="20" /></span></template>
        </KpiCard>
      </div>

      <!-- Rule Network Graph + AI Insight (14:10 Golden Ratio) -->
      <el-row v-if="data.loss_related.length > 0 || data.rules.length > 0" :gutter="20" class="graph-row">
        <el-col :span="14">
          <div class="chart-card graph-card">
            <div class="chart-card-header">规则关系网络（力导向图）</div>
            <div class="chart-card-body">
              <div ref="graphChartRef" class="graph-chart-container" />
            </div>
            <div class="graph-legend">
              <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#0F4A28" /> 前项特征</span>
              <span class="graph-legend-item"><span class="graph-legend-dot" style="background:#EF4444" /> 后项（流失）</span>
              <span class="graph-legend-item">线宽 ∝ Lift 值</span>
            </div>
          </div>
        </el-col>
        <el-col :span="10">
          <div class="right-panel">
            <div class="gradient-accent-line" />
            <!-- Rules Overview Stats -->
            <div class="chart-card stats-card">
              <div class="chart-card-header">规则概览</div>
              <div class="chart-card-body">
                <div class="stats-grid">
                  <div class="stat-item">
                    <span class="stat-label">最高 Lift</span>
                    <span class="stat-value text-danger">{{ data.rules.length > 0 ? sortRules(data.rules)[0].lift.toFixed(2) : '—' }}</span>
                    <span class="stat-detail">{{ data.rules.length > 0 ? sortRules(data.rules)[0].antecedents.split(', ').slice(0, 2).join(' + ') : '' }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">最高置信度</span>
                    <span class="stat-value text-success">{{ data.rules.length > 0 ? [...data.rules].sort((a, b) => b.confidence - a.confidence)[0].confidence.toFixed(4) : '—' }}</span>
                    <span class="stat-detail">→ 流失</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">规则总数</span>
                    <span class="stat-value">{{ data.rules.length }}</span>
                    <span class="stat-detail">含 {{ data.loss_related.length }} 条流失相关</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">平均支持度</span>
                    <span class="stat-value">{{ data.rules.length > 0 ? (data.rules.reduce((s, r) => s + r.support, 0) / data.rules.length).toFixed(4) : '—' }}</span>
                    <span class="stat-detail">support</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- Top-5 Rules by Lift -->
            <div class="chart-card">
              <div class="chart-card-header">Top-5 Lift 规则</div>
              <div class="chart-card-body">
                <BarChart :option="topRulesChartOption" height="260px" />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-tabs v-model="activeTab" class="rules-tabs">
        <el-tab-pane label="全部规则" name="all" />
        <el-tab-pane label="流失相关规则" name="loss" />
      </el-tabs>

      <!-- All Rules -->
      <div v-if="activeTab === 'all'" class="table-card chart-card">
        <div class="chart-card-header">
          <span>全部关联规则</span>
          <span class="table-count">按 Lift 降序 · 共 {{ data.rules.length }} 条</span>
        </div>
        <div class="chart-card-body" style="padding-top:0">
          <el-table :data="sortRules(data.rules)" highlight-current-row
            :row-class-name="({ row }: { row: RuleItem }) => getLiftClass(row.lift)"
            max-height="520"
          >
            <el-table-column label="前项" min-width="200">
              <template #default="{ row }"><span :title="row.antecedents">{{ row.antecedents.length > 50 ? row.antecedents.slice(0, 50) + '...' : row.antecedents }}</span></template>
            </el-table-column>
            <el-table-column label="后项" width="140">
              <template #default="{ row }"><span :title="row.consequents">{{ row.consequents.length > 24 ? row.consequents.slice(0, 24) + '...' : row.consequents }}</span></template>
            </el-table-column>
            <el-table-column prop="support" label="支持度" width="110" sortable>
              <template #default="{ row }"><span class="mono-cell">{{ row.support.toFixed(4) }}</span></template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="190" sortable>
              <template #default="{ row }">
                <div class="inline-stat">
                  <div class="inline-bar-track">
                    <div
                      class="inline-bar-fill"
                      :style="{
                        width: Math.min(row.confidence * 100, 100) + '%',
                        background: row.confidence >= 0.7 ? '#EF4444' : row.confidence >= 0.5 ? '#F59E0B' : '#0EA5E9',
                        opacity: 0.3,
                      }"
                    />
                  </div>
                  <span class="mono-cell">{{ row.confidence.toFixed(4) }}</span>
                  <el-tag :type="row.confidence >= 0.7 ? 'danger' : row.confidence >= 0.5 ? 'warning' : 'info'" size="small" effect="light" style="margin-left:4px">{{ toPercent(row.confidence) }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="lift" label="Lift" width="160" sortable>
              <template #default="{ row }">
                <div class="inline-stat">
                  <div class="inline-bar-track lift-track">
                    <div
                      class="inline-bar-fill"
                      :style="{
                        width: Math.min(row.lift / 5 * 100, 100) + '%',
                        background: row.lift >= 3 ? '#EF4444' : row.lift >= 2 ? '#F59E0B' : '#0EA5E9',
                        opacity: 0.25,
                      }"
                    />
                  </div>
                  <el-tag :type="getLiftTag(row.lift)" size="default" effect="light">{{ row.lift.toFixed(2) }}</el-tag>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="data.rules.length === 0" class="empty-table">暂无关联规则</div>
        </div>
      </div>

      <!-- Loss Rules -->
      <div v-if="activeTab === 'loss'" class="table-card chart-card">
        <div class="chart-card-header">
          <span style="color:#EF4444">流失相关规则</span>
          <span class="table-count">按 Lift 降序 · 共 {{ data.loss_related.length }} 条</span>
        </div>
        <div class="chart-card-body" style="padding-top:0">
          <el-table :data="sortRules(data.loss_related)" highlight-current-row
            :row-class-name="({ row }: { row: RuleItem }) => getLiftClass(row.lift)"
            max-height="520"
          >
            <el-table-column label="前项" min-width="220">
              <template #default="{ row }">{{ row.antecedents }}</template>
            </el-table-column>
            <el-table-column label="后项" width="120">
              <template #default="{ row }">{{ row.consequents }}</template>
            </el-table-column>
            <el-table-column prop="support" label="支持度" width="110" sortable>
              <template #default="{ row }"><span class="mono-cell">{{ row.support.toFixed(4) }}</span></template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="190" sortable>
              <template #default="{ row }">
                <div class="inline-stat">
                  <div class="inline-bar-track">
                    <div
                      class="inline-bar-fill"
                      :style="{
                        width: Math.min(row.confidence * 100, 100) + '%',
                        background: row.confidence >= 0.7 ? '#EF4444' : row.confidence >= 0.5 ? '#F59E0B' : '#0EA5E9',
                        opacity: 0.3,
                      }"
                    />
                  </div>
                  <span class="mono-cell">{{ row.confidence.toFixed(4) }}</span>
                  <el-tag :type="row.confidence >= 0.7 ? 'danger' : row.confidence >= 0.5 ? 'warning' : 'info'" size="small" effect="light" style="margin-left:4px">{{ toPercent(row.confidence) }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="lift" label="Lift" width="160" sortable>
              <template #default="{ row }">
                <div class="inline-stat">
                  <div class="inline-bar-track lift-track">
                    <div
                      class="inline-bar-fill"
                      :style="{
                        width: Math.min(row.lift / 5 * 100, 100) + '%',
                        background: row.lift >= 3 ? '#EF4444' : row.lift >= 2 ? '#F59E0B' : '#0EA5E9',
                        opacity: 0.25,
                      }"
                    />
                  </div>
                  <el-tag :type="getLiftTag(row.lift)" size="default" effect="light">{{ row.lift.toFixed(2) }}</el-tag>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="data.loss_related.length === 0" class="empty-table">暂无流失相关规则</div>
        </div>
      </div>

      <!-- Lift Legend -->
      <div class="chart-card legend-card">
        <div class="chart-card-header">Lift 值解读</div>
        <div class="chart-card-body">
          <div class="legend-gradient-bar" />
          <div class="legend-row">
            <div class="legend-item"><span class="legend-color-dot" style="background:#EF4444" /><span class="legend-text"><strong>Lift ≥ 3</strong> — 强关联，前项出现使后项概率提升 3 倍以上</span></div>
            <div class="legend-item"><span class="legend-color-dot" style="background:#F59E0B" /><span class="legend-text"><strong>Lift ≥ 2</strong> — 中等关联，具有一定参考价值</span></div>
            <div class="legend-item"><span class="legend-color-dot" style="background:#0EA5E9" /><span class="legend-text"><strong>Lift &lt; 2</strong> — 弱关联，注意支持度和置信度的实际含义</span></div>
          </div>
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

.status-center { text-align: center; padding: 60px 20px; }
.status-error { color: var(--color-danger); display: flex; flex-direction: column; align-items: center; gap: 12px; }
.status-hint { color: var(--color-text-secondary); font-size: 13px; }
.status-hint code {
  background: var(--color-border); padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-family: var(--font-family-mono);
}

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-item-gap); margin-bottom: var(--spacing-section-gap); }
.kpi-icon { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; color: currentColor; }

.rules-tabs { margin-bottom: var(--spacing-item-gap); }

/* Chart Cards — Donezo clean */
.chart-card {
  background: var(--color-bg-card); border: none;
  border-radius: var(--radius-card); box-shadow: var(--shadow-card); overflow: hidden;
  transition: box-shadow var(--transition-slow);
}
.chart-card:hover { box-shadow: var(--shadow-card-hover); }
.chart-card-header {
  padding: 20px var(--spacing-card-padding) 0;
  font-weight: 600; font-size: 15px; color: var(--color-text-primary);
  display: flex; align-items: center; justify-content: space-between;
  font-family: var(--font-family-sans);
}
.chart-card-body { padding: var(--spacing-card-padding); }

.table-card { margin-bottom: var(--spacing-section-gap); }
.table-count { font-size: 12px; color: var(--color-text-secondary); font-weight: 400; }
.mono-cell { font-family: var(--font-family-mono); font-size: 13px; color: var(--color-text-primary); }
.empty-table { text-align: center; padding: 40px; color: var(--color-text-secondary); font-size: 14px; }

/* Table — minimal row lines */
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
:deep(.el-table tr:hover > td.el-table__cell) {
  background: rgba(15, 23, 42, 0.02);
}

/* Lift Row Highlighting — Donezo */
:deep(.lift-high) {
  background: rgba(239, 68, 68, 0.04) !important;
  border-left: 4px solid #EF4444;
}
:deep(.lift-high:hover) { background: rgba(239, 68, 68, 0.07) !important; }
:deep(.lift-medium) {
  background: rgba(245, 158, 11, 0.04) !important;
  border-left: 4px solid #F59E0B;
}
:deep(.lift-medium:hover) { background: rgba(245, 158, 11, 0.07) !important; }

.legend-card { margin-bottom: 0; }
.legend-row { display: flex; flex-direction: column; gap: 12px; }
.legend-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--color-text-secondary); }
.legend-color-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.legend-text strong { color: var(--color-text-primary); }
.legend-gradient-bar {
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(90deg, #0EA5E9, #F59E0B, #EF4444);
  margin-bottom: 16px;
}

/* Graph Card */
.graph-card { margin-bottom: var(--spacing-section-gap); }
.graph-legend {
  display: flex; align-items: center; gap: 20px;
  padding: 0 var(--spacing-card-padding) 16px;
  font-size: 12px; color: var(--color-text-muted);
}
.graph-legend-item { display: flex; align-items: center; gap: 6px; }
.graph-legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* Inline bars in table cells */
.inline-stat {
  display: flex;
  align-items: center;
  gap: 8px;
}
.inline-bar-track {
  width: 40px;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  overflow: hidden;
  flex-shrink: 0;
}
.inline-bar-track.lift-track {
  width: 50px;
}
.inline-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease-out;
}

/* Graph container — explicit fixed height to prevent zero-size at mount */
.graph-chart-container {
  height: 480px;
  width: 100%;
  min-height: 480px;
}

/* Golden ratio graph row */
.graph-row {
  margin-bottom: var(--spacing-section-gap);
}

/* Right panel */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-item-gap);
}
.gradient-accent-line {
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #0F4A28, #4ADE80, #0F4A28);
  opacity: 0.6;
}

/* Rules stats card */
.stats-card .chart-card-body {
  padding-top: 0;
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-label {
  font-size: 10px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
}
.stat-value.text-danger { color: #EF4444; }
.stat-value.text-success { color: #22C55E; }
.stat-detail {
  font-size: 11px;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1024px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .kpi-row { grid-template-columns: 1fr; } }
</style>

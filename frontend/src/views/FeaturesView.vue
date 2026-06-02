<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BarChart from '@/components/chart/BarChart.vue'
import AppIcon from '@/components/AppIcon.vue'
import { fetchFeatureImportance, type FeatureImportance } from '@/api'
import { makeTooltip } from '@/styles/chartTheme'

const features = ref<FeatureImportance[]>([])
const importanceMeta = ref<{ model_name: string; importance_type: string }>({ model_name: '', importance_type: '' })
const loading = ref(true)
const error = ref('')
const importanceOption = ref<any>({})
const selectedFeature = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await fetchFeatureImportance()
    features.value = res.features
    importanceMeta.value = { model_name: res.model_name, importance_type: res.importance_type }

    const names = res.features.map(f => f.name).reverse()
    const vals = res.features.map(f => f.importance).reverse()

    importanceOption.value = {
      tooltip: makeTooltip({
        trigger: 'axis',
        formatter: (p: any) =>
          `<span style="color:#64748B">${p[0].name}</span>: <strong>${p[0].value.toFixed(4)}</strong>`,
      }),
      grid: { left: 140, right: 60, top: 10, bottom: 20 },
      xAxis: {
        type: 'value', name: 'Importance',
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#94A3B8' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'category', data: names, inverse: true,
        axisLine: { show: false }, axisTick: { show: false },
        axisLabel: { color: '#64748B', fontSize: 12, fontFamily: 'Inter, sans-serif' },
      },
      series: [{
        type: 'bar',
        data: vals.map((v, i) => ({
          value: v,
          itemStyle: {
            borderRadius: [0, 10, 10, 0],
            color: {
              type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: `hsl(${145 + (i / vals.length) * 20}, 60%, ${28 + (i / vals.length) * 12}%)` },
                { offset: 1, color: `hsl(${145 + (i / vals.length) * 20}, 75%, ${42 + (i / vals.length) * 10}%)` },
              ],
            },
          },
        })),
        barMaxWidth: 20,
        animationDelay: (idx: number) => idx * 60,
        animationDuration: 700,
        animationEasing: 'cubicOut',
        label: {
          show: true, formatter: (p: any) => p.value.toFixed(4),
          position: 'right', color: '#64748B', fontSize: 11,
        },
      }],
    }
  } catch (e: any) {
    error.value = e.message || '数据加载失败'
  } finally {
    loading.value = false
  }
})

function selectFeature(feat: FeatureImportance) {
  selectedFeature.value = selectedFeature.value === feat.name ? null : feat.name
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">特征归因</h2>
        <p class="page-desc">
          特征重要性分析 — {{ importanceMeta.model_name }}
          <el-tag size="small" type="success" effect="light" style="margin:0 4px">
            {{ importanceMeta.importance_type }}
          </el-tag>
          <el-tag v-if="selectedFeature" type="success" size="small" effect="light" style="margin-left:6px">
            {{ selectedFeature }}
          </el-tag>
        </p>
      </div>
    </div>

    <div v-if="loading" class="status-center"><el-skeleton :rows="5" animated /></div>

    <div v-else-if="error" class="status-center status-error">
      <AppIcon name="alert-triangle" :size="32" />
      <p>{{ error }}</p>
      <p class="status-hint">请先运行 <code>python run_prediction.py</code> 训练模型</p>
    </div>

    <template v-else>
      <div class="content-grid">
        <!-- Left: Importance Chart -->
        <div class="chart-card">
          <div class="chart-card-header">特征重要性排名（Top-15）</div>
          <div class="chart-card-body">
            <p class="chart-hint">点击右侧特征名称查看其流失 vs 留存分布</p>
            <BarChart :option="importanceOption" height="460px" />
          </div>
        </div>

        <!-- Right Panel -->
        <div class="right-panel">
          <!-- Feature List -->
          <div class="chart-card feature-list-card">
            <div class="chart-card-header">特征列表</div>
            <div class="chart-card-body">
              <div class="feature-list stagger-list">
                <div
                  v-for="(f, i) in features" :key="f.name"
                  class="feature-item"
                  :class="{ selected: selectedFeature === f.name }"
                  @click="selectFeature(f)"
                  role="option" :aria-selected="selectedFeature === f.name"
                  tabindex="0" @keydown.enter="selectFeature(f)"
                >
                  <div class="feature-header-row">
                    <span class="feature-rank" :class="{ 'rank-top': i < 3 }">{{ i + 1 }}</span>
                    <span class="feature-name">{{ f.name }}</span>
                    <span class="feature-val">{{ f.importance.toFixed(4) }}</span>
                  </div>
                  <el-progress
                    :percentage="+(f.importance / features[0].importance * 100).toFixed(1)"
                    color="#22C55E"
                    :stroke-width="4" :show-text="false"
                  />
                  <div class="feature-footer">
                    <el-tag size="small" type="success" effect="light">SHAP</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Model Summary Card -->
          <div class="chart-card model-summary-card">
            <div class="chart-card-header">模型摘要</div>
            <div class="chart-card-body">
              <div class="model-summary-row">
                <div class="model-summary-item">
                  <span class="ms-label"><AppIcon name="server" :size="12" /> 模型</span>
                  <span class="ms-value">{{ importanceMeta.model_name || '—' }}</span>
                </div>
                <div class="model-summary-item">
                  <span class="ms-label"><AppIcon name="search" :size="12" /> 归因方法</span>
                  <span class="ms-value">{{ importanceMeta.importance_type }}</span>
                </div>
                <div class="model-summary-item">
                  <span class="ms-label"><AppIcon name="chart-bar" :size="12" /> 特征数</span>
                  <span class="ms-value">{{ features.length }}</span>
                </div>
              </div>
            </div>
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
.page-desc {
  font-size: var(--font-size-subtitle); color: var(--color-text-secondary);
  margin: 0; line-height: 1.6;
}

.status-center { text-align: center; padding: 60px 20px; }
.status-error { color: var(--color-danger); display: flex; flex-direction: column; align-items: center; gap: 12px; }
.status-hint { color: var(--color-text-secondary); font-size: 13px; }
.status-hint code {
  background: var(--color-border); padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-family: var(--font-family-mono);
}

.content-grid { display: grid; grid-template-columns: 14fr 10fr; gap: var(--spacing-section-gap); align-items: start; }

.chart-card {
  background: var(--color-bg-card); border: none;
  border-radius: var(--radius-card); box-shadow: var(--shadow-card); overflow: hidden;
  transition: box-shadow var(--transition-slow);
}
.chart-card:hover { box-shadow: var(--shadow-card-hover); }
.chart-card-header {
  padding: 20px var(--spacing-card-padding) 0;
  font-weight: 600; font-size: 15px; color: var(--color-text-primary);
  font-family: var(--font-family-sans);
}
.chart-card-body { padding: var(--spacing-card-padding); }
.chart-hint { color: var(--color-text-secondary); font-size: 12px; margin: 0 0 8px; }

.right-panel { display: flex; flex-direction: column; gap: var(--spacing-item-gap); }
.feature-list-card { max-height: 520px; overflow-y: auto; }
.feature-list { display: flex; flex-direction: column; gap: 8px; }

.feature-item {
  display: flex; flex-direction: column; gap: 2px; padding: 8px 10px;
  border-radius: var(--radius-sm); cursor: pointer;
  transition: background var(--transition-normal), box-shadow var(--transition-normal);
  border: 1px solid transparent; border-left: 4px solid transparent;
  outline: none;
}
.feature-item:hover { background: rgba(15, 23, 42, 0.02); }
.feature-item:focus-visible { box-shadow: 0 0 0 2px var(--color-primary-light); }
.feature-item.selected {
  background: var(--color-primary-soft); border-color: rgba(15, 74, 40, 0.15);
  border-left-color: #0F4A28;
}

.feature-header-row { display: flex; align-items: center; gap: 8px; }
.feature-rank {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(15, 23, 42, 0.04); font-size: 12px; font-weight: 600;
  color: var(--color-text-secondary); flex-shrink: 0; font-family: var(--font-family-mono);
}
.feature-rank.rank-top {
  background: #0F4A28; color: #fff;
}
.feature-name { flex: 1; font-size: 13px; color: var(--color-text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feature-val { font-size: 12px; color: var(--color-text-secondary); font-family: var(--font-family-mono); }
.feature-footer { align-self: flex-end; }

/* Model Summary Card */
.model-summary-card { }
.model-summary-row {
  display: flex;
  gap: 16px;
}
.model-summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.ms-label {
  font-size: 10px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}
.ms-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
}

@media (max-width: 1024px) { .content-grid { grid-template-columns: 1fr; } }
</style>

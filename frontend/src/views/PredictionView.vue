<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { predict, type PredictionResult } from '@/api'
import { FIELD_DEFS } from '@/utils/constants'
import RiskBadge from '@/components/RiskBadge.vue'
import AppIcon from '@/components/AppIcon.vue'
import ChurnGauge from '@/components/ChurnGauge.vue'

const form = reactive<Record<string, any>>({})
const result = ref<PredictionResult | null>(null)
const loading = ref(false)
const error = ref('')

FIELD_DEFS.forEach(f => {
  form[f.key] = f.default ?? (f.type === 'number' ? 0 : (f.options?.[0] || ''))
})

async function submit() {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await predict({ ...form })
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '预测失败'
  } finally {
    loading.value = false
  }
}

const basicFields = computed(() => FIELD_DEFS.slice(0, 6))
const behaviorFields = computed(() => FIELD_DEFS.slice(6, 13))
const consumptionFields = computed(() => FIELD_DEFS.slice(13))
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">流失预测</h2>
        <p class="page-desc">输入客户特征，实时预测流失概率</p>
      </div>
    </div>

    <div class="predict-layout">
      <!-- Left: Form -->
      <div class="form-card chart-card">
        <div class="chart-card-header">
          <AppIcon name="search" :size="18" style="margin-right:8px" />
          客户特征输入
        </div>
        <div class="chart-card-body">
          <el-form label-width="130px" label-position="top" size="default">
            <div class="step-indicators">
              <div class="step-item active"><span class="step-num">1</span><span class="step-label">基本档案</span></div>
              <div class="step-line" />
              <div class="step-item"><span class="step-num">2</span><span class="step-label">平台行为</span></div>
              <div class="step-line" />
              <div class="step-item"><span class="step-num">3</span><span class="step-label">消费矩阵</span></div>
            </div>
            <el-row :gutter="16">
              <el-col :xs="24" :sm="24" :md="8">
                <div class="field-group field-group-profile">
                  <h4 class="field-group-title">
                    <AppIcon name="users" :size="14" />
                    基本档案
                  </h4>
                  <el-form-item v-for="f in basicFields" :key="f.key" :label="f.label">
                    <el-select
                      v-if="f.type === 'select'"
                      v-model="form[f.key]"
                      style="width:100%"
                      clearable
                      :placeholder="'请选择' + f.label"
                    >
                      <el-option v-for="o in f.options" :key="o" :label="o" :value="o" />
                    </el-select>
                    <el-input-number
                      v-else
                      v-model="form[f.key]"
                      :min="f.min"
                      :max="f.max"
                      style="width:100%"
                      controls-position="right"
                      :placeholder="f.label"
                    />
                  </el-form-item>
                </div>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8">
                <div class="field-group field-group-behavior">
                  <h4 class="field-group-title">
                    <AppIcon name="trending-up" :size="14" />
                    平台行为
                  </h4>
                  <el-form-item v-for="f in behaviorFields" :key="f.key" :label="f.label">
                    <el-select
                      v-if="f.type === 'select'"
                      v-model="form[f.key]"
                      style="width:100%"
                      clearable
                      :placeholder="'请选择' + f.label"
                    >
                      <el-option v-for="o in f.options" :key="o" :label="o" :value="o" />
                    </el-select>
                    <el-input-number
                      v-else
                      v-model="form[f.key]"
                      :min="f.min"
                      :max="f.max"
                      style="width:100%"
                      controls-position="right"
                      :placeholder="f.label"
                    />
                  </el-form-item>
                </div>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8">
                <div class="field-group field-group-consumption">
                  <h4 class="field-group-title">
                    <AppIcon name="dollar-sign" :size="14" />
                    消费矩阵
                  </h4>
                  <el-form-item v-for="f in consumptionFields" :key="f.key" :label="f.label">
                    <el-select
                      v-if="f.type === 'select'"
                      v-model="form[f.key]"
                      style="width:100%"
                      clearable
                      :placeholder="'请选择' + f.label"
                    >
                      <el-option v-for="o in f.options" :key="o" :label="o" :value="o" />
                    </el-select>
                    <el-input-number
                      v-else
                      v-model="form[f.key]"
                      :min="f.min"
                      :max="f.max"
                      style="width:100%"
                      controls-position="right"
                      :placeholder="f.label"
                    />
                  </el-form-item>
                </div>
              </el-col>
            </el-row>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="submit"
              round
              class="submit-btn"
            >
              <template v-if="!loading">
                <AppIcon name="target" :size="18" style="margin-right:6px" />
                预测流失概率
              </template>
              <template v-else>
                <span class="shimmer-text">预测中...</span>
              </template>
            </el-button>
          </el-form>
        </div>
      </div>

      <!-- Right: Results -->
      <div class="result-area">
        <!-- Empty -->
        <div v-if="!result && !error && !loading" class="result-card result-empty">
          <div class="empty-illustration">
            <AppIcon name="search" :size="48" class="empty-icon" />
            <p class="empty-title">准备开始预测</p>
            <p class="empty-desc">填写左侧表单，AI 将为您预测客户流失概率</p>
          </div>
        </div>

        <!-- Loading — shimmer skeleton -->
        <div v-if="loading" class="skeleton-panel">
          <div class="skeleton-card">
            <div class="skeleton-line skeleton-line-xl" />
            <div class="skeleton-line skeleton-line-md" />
            <div class="skeleton-line skeleton-line-sm" />
          </div>
          <div class="skeleton-card">
            <div class="skeleton-circle" />
            <div class="skeleton-line skeleton-line-md" />
            <div class="skeleton-line skeleton-line-sm" />
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="result-card result-error">
          <div class="error-content">
            <AppIcon name="x-circle" :size="28" style="color:var(--color-danger)" />
            <p>{{ error }}</p>
          </div>
        </div>

        <!-- Result — merged evaluation card -->
        <div v-if="result" class="result-card result-evaluation">
          <div class="chart-card-header">流失概率评估报告</div>
          <div class="chart-card-body">
            <div class="progress-section">
              <ChurnGauge :probability="result.churn_probability" />
            </div>
            <div class="evaluation-summary">
              <div class="eval-risk">
                <span class="risk-level-label">风险等级</span>
                <RiskBadge :level="result.risk_level" />
              </div>
              <div class="eval-grid">
                <div class="eval-item">
                  <span class="eval-label">预测分类</span>
                  <span class="eval-value">
                    <AppIcon
                      :name="result.predicted_class === 1 ? 'alert-triangle' : 'check-circle'"
                      :size="18"
                      :style="{ color: result.predicted_class === 1 ? '#EF4444' : '#22C55E' }"
                    />
                    {{ result.predicted_class === 1 ? '可能流失' : '可能留存' }}
                  </span>
                </div>
                <div class="eval-item">
                  <span class="eval-label">使用模型</span>
                  <span class="eval-value">{{ result.model }}</span>
                </div>
              </div>
              <div class="shap-drivers-section">
                <router-link to="/features">
                  <el-button class="shap-button pulse-glow" type="primary" plain round>
                    <AppIcon name="trending-up" :size="16" style="margin-right:4px" />
                    查看 SHAP 驱动因素
                    <AppIcon name="arrow-right" :size="14" style="margin-left:4px" />
                  </el-button>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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

.predict-layout {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--spacing-section-gap);
  align-items: start;
}

/* Chart Card — Donezo clean */
.chart-card {
  background: var(--color-bg-card);
  border: none;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  overflow: hidden;
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
.chart-card-body { padding: var(--spacing-card-padding); }

/* Form */
.form-card { }
.field-group {
  background: var(--color-bg-page);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-bottom: 8px;
  border-top: 3px solid transparent;
}
.field-group-profile { border-top-color: #0F4A28; }
.field-group-behavior { border-top-color: #0EA5E9; }
.field-group-consumption { border-top-color: #F59E0B; }
.field-group-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-family-sans);
}

/* Step Indicators */
.step-indicators {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-border);
  color: var(--color-text-muted);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  transition: all var(--transition-normal);
}
.step-item.active .step-num {
  background: #0F4A28;
  color: #fff;
}
.step-label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 500;
  transition: color var(--transition-normal);
}
.step-item.active .step-label {
  color: var(--color-text-primary);
  font-weight: 600;
}
.step-line {
  flex: 1;
  height: 1px;
  background: var(--color-border);
  margin: 0 8px;
  margin-bottom: 22px;
}
.submit-btn {
  width: 100%;
  margin-top: 16px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0F4A28;
  border-color: #0F4A28;
}
.submit-btn:hover {
  background: #0D3E22;
  border-color: #0D3E22;
}

/* Result */
.result-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-item-gap);
  position: sticky;
  top: var(--spacing-page-padding);
}
.result-card {
  background: var(--color-bg-card);
  border: none;
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.result-empty,
.result-loading {
  text-align: center;
  padding: 60px 24px;
  color: var(--color-text-secondary);
}
.result-empty .empty-icon {
  color: var(--color-text-muted);
  margin-bottom: 16px;
  opacity: 0.5;
}
.empty-illustration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}
.empty-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.6;
}
.result-error {
  border: 1px solid rgba(239, 68, 68, 0.15);
  text-align: center;
  padding: 40px 20px;
}
.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--color-danger);
}

/* Gauge — enlarged */
.progress-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}
.progress-section :deep(> div) {
  height: 320px !important;
}

/* Evaluation Summary */
.evaluation-summary {
  padding-top: 8px;
}
.eval-risk {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}
.risk-level-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* Eval Grid */
.eval-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-item-gap);
  margin-bottom: 16px;
}
.eval-item { text-align: center; }
.eval-label {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
  font-weight: 500;
}
.eval-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* SHAP CTA */
.shap-drivers-section {
  text-align: center;
}
.shap-button {
  font-weight: 600;
  display: inline-flex;
  align-items: center;
}

.result-evaluation { }
</style>

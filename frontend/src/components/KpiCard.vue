<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  color?: string
  trend?: { direction: 'up' | 'down'; value: string }
  featured?: boolean
}>()
</script>

<template>
  <el-card
    shadow="hover"
    class="kpi-card"
    :class="{ 'kpi-featured': featured }"
    :style="{ '--kpi-accent': color || 'var(--color-primary)' }"
  >
    <div v-if="!featured" class="kpi-accent-bar" />
    <div class="kpi-inner">
      <div v-if="$slots.icon" class="kpi-icon-box" :class="{ 'kpi-icon-featured': featured }">
        <slot name="icon" />
      </div>
      <div class="kpi-content">
        <div class="kpi-label" :class="{ 'kpi-label-featured': featured }">
          {{ label }}
        </div>
        <div
          class="kpi-value"
          :class="{ 'kpi-value-featured': featured }"
          :style="!featured ? { color: color || 'var(--color-text-primary)' } : {}"
        >
          {{ value }}
        </div>
        <div v-if="trend" class="kpi-trend" :class="[trend.direction, { 'kpi-trend-featured': featured }]">
          <span class="trend-arrow">{{ trend.direction === 'up' ? '↗' : '↘' }}</span>
          {{ trend.value }}
        </div>
      </div>
      <div v-if="$slots.sparkline" class="kpi-sparkline">
        <slot name="sparkline" />
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.kpi-card {
  position: relative;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-slow),
              transform var(--transition-normal);
  cursor: default;
  overflow: hidden;
}
.kpi-card:hover {
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

/* Featured variant — Donezo dark forest green with gradient */
.kpi-featured {
  border: none;
  background: linear-gradient(135deg, #0F4A28 0%, #155230 40%, #0F4A28 100%);
  box-shadow: var(--shadow-card), 0 0 0 1px rgba(74,222,128,0.08);
}
.kpi-featured:hover {
  box-shadow: var(--shadow-card-hover), 0 0 0 1px rgba(74,222,128,0.15);
  filter: brightness(1.05);
}

/* Left accent bar */
.kpi-accent-bar {
  position: absolute;
  left: 0;
  top: 16px;
  bottom: 16px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: var(--kpi-accent);
  opacity: 0.9;
}

.kpi-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.04);
  color: var(--kpi-accent);
}
.kpi-icon-featured {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.kpi-content {
  flex: 1;
  min-width: 0;
}

.kpi-label {
  font-size: var(--font-size-kpi-label);
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  letter-spacing: 0.3px;
  font-weight: 500;
}
.kpi-label-featured {
  color: rgba(255, 255, 255, 0.7);
}

.kpi-value {
  font-size: var(--font-size-kpi-value);
  font-weight: var(--font-weight-number);
  line-height: 1.15;
  font-family: var(--font-family-mono);
  font-variant-numeric: tabular-nums;
}
.kpi-value-featured {
  color: #fff;
  font-size: 34px;
}

.kpi-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-family-mono);
}
.kpi-trend.up { color: var(--color-accent-green); }
.kpi-trend.down { color: var(--color-accent-rose); }
.kpi-trend-featured.up {
  color: #4ADE80;
}
.kpi-trend-featured.down {
  color: rgba(255,255,255,0.7);
}
.trend-arrow { font-size: 15px; }

.kpi-sparkline {
  flex-shrink: 0;
  width: 80px;
  height: 40px;
}
</style>

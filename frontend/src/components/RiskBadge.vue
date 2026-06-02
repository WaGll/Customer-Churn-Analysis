<script setup lang="ts">
import { computed } from 'vue'
import { RISK_COLORS, RISK_LABELS } from '@/utils/constants'

const props = defineProps<{ level: string }>()

const color = computed(() => RISK_COLORS[props.level] || '#94A3B8')
const bgColor = computed(() => {
  const hex = RISK_COLORS[props.level] || '#94A3B8'
  return hex + '14'
})
const label = computed(() => RISK_LABELS[props.level] || props.level)
</script>

<template>
  <span class="risk-badge" :style="{ background: bgColor, color: color, borderColor: color }">
    <span class="risk-badge-dot" :style="{ background: color }" />
    {{ label }}
  </span>
</template>

<style scoped>
.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 16px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  border: 1px solid;
  line-height: 1.5;
  font-family: var(--font-family-sans);
}

.risk-badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>

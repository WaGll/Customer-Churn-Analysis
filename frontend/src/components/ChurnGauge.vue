<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { EChartsOption } from 'echarts'
import { useECharts } from './chart/useECharts'
import { GAUGE_COLOR_STOPS } from '@/styles/chartTheme'

const props = defineProps<{ probability: number }>()
const chartRef = ref<HTMLElement | null>(null)

const safeProbability = computed(() => {
  const v = props.probability
  if (v === undefined || v === null || isNaN(v) || !isFinite(v)) return 0
  return Math.max(0, Math.min(1, v))
})

const option = computed<EChartsOption>(() => ({
  series: [{
    type: 'gauge',
    startAngle: 180,
    endAngle: 0,
    min: 0,
    max: 1,
    radius: '82%',
    center: ['50%', '58%'],
    axisLine: {
      lineStyle: {
        width: 24,
        color: GAUGE_COLOR_STOPS,
      },
    },
    pointer: { show: false },
    axisTick: { show: false },
    splitLine: { show: false },
    axisLabel: { show: false },
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { borderWidth: 0 },
    },
    detail: {
      valueAnimation: true,
      formatter: (v: number) => (v * 100).toFixed(1) + '%',
      fontSize: 36,
      offsetCenter: [0, '58%'],
      color: '#0F172A',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 700,
    },
    data: [{ value: safeProbability.value, name: '流失概率' }],
  }],
}))

const { setOptions } = useECharts(chartRef, option.value)

watch(() => props.probability, (v) => {
  const safe = (v === undefined || v === null || isNaN(v) || !isFinite(v)) ? 0 : Math.max(0, Math.min(1, v))
  setOptions({
    series: [{ data: [{ value: safe }] }],
  } as EChartsOption)
})
</script>

<template>
  <div ref="chartRef" style="width: 100%; height: 280px" />
</template>

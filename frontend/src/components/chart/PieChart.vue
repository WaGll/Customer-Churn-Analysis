<script setup lang="ts">
import { ref, watch } from 'vue'
import { useECharts } from './useECharts'

const props = defineProps<{ option: any; height?: string }>()
const chartRef = ref<HTMLElement | null>(null)
const { setOptions } = useECharts(chartRef, props.option)

watch(() => props.option, (v) => setOptions(v), { deep: true })
</script>

<template>
  <div ref="chartRef" :style="{ width: '100%', height: height || '360px' }" />
</template>

import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart, ScatterChart, GaugeChart, GraphChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent, ToolboxComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, PieChart, LineChart, ScatterChart, GaugeChart, GraphChart,
  TitleComponent, TooltipComponent, GridComponent, LegendComponent, ToolboxComponent,
  CanvasRenderer,
])

export function useECharts(
  chartRef: Ref<HTMLElement | null>,
  options: echarts.EChartsCoreOption
) {
  const instance = ref<echarts.ECharts | null>(null)

  function init() {
    if (!chartRef.value) return
    if (!options || !options.series) return
    instance.value = echarts.init(chartRef.value)
    instance.value.setOption(options)
  }

  function resize() {
    instance.value?.resize()
  }

  function setOptions(opts: echarts.EChartsCoreOption) {
    if (!opts) return
    // Lazy init: handle conditional rendering where chartRef
    // becomes available after onMounted (e.g. v-if blocks)
    if (!instance.value) {
      if (chartRef.value && opts.series) {
        instance.value = echarts.init(chartRef.value)
      } else {
        return
      }
    }
    instance.value.setOption(opts, true)
  }

  onMounted(() => {
    init()
    window.addEventListener('resize', resize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', resize)
    instance.value?.dispose()
  })

  return { instance, setOptions, resize }
}

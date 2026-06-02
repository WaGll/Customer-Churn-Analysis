/**
 * Donezo ECharts Theme Configuration
 * Forest Green palette — premium B2B SaaS aesthetic
 */

// ── Color Palettes ──────────────────────────────────────────

/** Forest green gradient — primary bars / healthy metrics */
export const FOREST_GREEN_GRADIENT = {
  type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1,
  colorStops: [
    { offset: 0, color: '#4ADE80' },
    { offset: 1, color: '#0F4A28' },
  ],
}

/** Warm amber-to-red gradient — churn / danger */
export const AMBER_RED_GRADIENT = {
  type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1,
  colorStops: [
    { offset: 0, color: '#F59E0B' },
    { offset: 1, color: '#EF4444' },
  ],
}

/** Neon green gradient — success / low churn */
export const GREEN_GRADIENT = {
  type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1,
  colorStops: [
    { offset: 0, color: '#4ADE80' },
    { offset: 1, color: '#22C55E' },
  ],
}

/** Warm amber gradient — warning / medium churn */
export const AMBER_GRADIENT = {
  type: 'linear' as const, x: 0, y: 0, x2: 1, y2: 0,
  colorStops: [
    { offset: 0, color: '#F59E0B' },
    { offset: 1, color: '#FBBF24' },
  ],
}

/** Forest green horizontal gradient — for horizontal bar charts */
export const FOREST_H_GRADIENT = {
  type: 'linear' as const, x: 0, y: 0, x2: 1, y2: 0,
  colorStops: [
    { offset: 0, color: '#0F4A28' },
    { offset: 1, color: '#4ADE80' },
  ],
}

/** Cluster color palette — 8 distinct colors for segmentation */
export const CLUSTER_COLORS = [
  '#0F4A28', // forest green
  '#0EA5E9', // sky
  '#22C55E', // green
  '#F59E0B', // amber
  '#8B5CF6', // violet
  '#EF4444', // red
  '#06B6D4', // cyan
  '#F97316', // orange
]

/** Churn-specific semantic colors for charts */
export const CHURN_COLORS = {
  low: '#22C55E',
  medium: '#F59E0B',
  high: '#EF4444',
  critical: '#DC2626',
  retained: '#0F4A28',
}

// ── Tooltip & Grid ──────────────────────────────────────────

/** Standard light-theme tooltip — clean card style */
export function makeTooltip(overrides: Record<string, any> = {}) {
  return {
    backgroundColor: '#fff',
    borderColor: '#F1F5F9',
    borderWidth: 1,
    borderRadius: 12,
    padding: [12, 16],
    textStyle: { color: '#0F172A', fontSize: 13, fontFamily: 'Inter, sans-serif' },
    extraCssText:
      'box-shadow: 0 10px 25px -5px rgba(15,23,42,0.06), 0 4px 12px -4px rgba(15,23,42,0.03);',
    ...overrides,
  }
}

/** Standard light-theme grid config */
export function makeGrid(overrides: Record<string, any> = {}) {
  return {
    left: 48,
    right: 24,
    top: 24,
    bottom: 32,
    ...overrides,
  }
}

/** Standard light-theme axis label style */
export const axisLabelStyle = { color: '#94A3B8', fontFamily: 'Inter, sans-serif' }

/** Standard light-theme split line style */
export const splitLineStyle = {
  lineStyle: { color: '#F1F5F9', type: 'dashed' as const },
}

/** Standard legend text style */
export const legendTextStyle = {
  color: '#64748B',
  fontSize: 12,
  fontFamily: 'Inter, sans-serif',
}

/** Bar border radius — pill-shaped tops (Donezo signature) */
export const BAR_RADIUS = [10, 10, 0, 0]

/** Bar border radius — pill-shaped right edges (for horizontal bars) */
export const BAR_RADIUS_RIGHT = [0, 10, 10, 0]

// ── Gauge Stops ─────────────────────────────────────────────

/** Churn gauge color stops: green → amber → red → deep red */
export const GAUGE_COLOR_STOPS: [number, string][] = [
  [0.3, CHURN_COLORS.low],
  [0.6, CHURN_COLORS.medium],
  [0.8, CHURN_COLORS.high],
  [1, CHURN_COLORS.critical],
]

// ── Animation Configs ────────────────────────────────────────

/** Standard bar/line chart growth animation */
export function makeAnimationConfig(duration = 800, easing = 'cubicOut' as const) {
  return {
    animationDuration: duration,
    animationEasing: easing,
    animationDelay: 0,
  }
}

/** Staggered bar chart animation (each bar delayed by ~80ms) */
export function makeStaggerAnimation(baseDuration = 600) {
  return {
    animationDuration: baseDuration,
    animationEasing: 'cubicOut' as const,
    animationDelay: (idx: number) => idx * 80,
    animationDurationUpdate: 400,
    animationEasingUpdate: 'cubicInOut' as const,
  }
}

// ── Sparkline / Mini Chart Defaults ─────────────────────────

/** Minimal sparkline config for KPI card trend indicators */
export const SPARKLINE_DEFAULTS = {
  type: 'line' as const,
  smooth: true,
  symbol: 'none' as const,
  lineStyle: { width: 2 },
  areaStyle: { opacity: 0.08 },
  animation: true,
  animationDuration: 1000,
}

/** Make a sparkline grid (no axes, no labels, compact) */
export function makeSparklineGrid() {
  return {
    left: 0,
    right: 0,
    top: 4,
    bottom: 4,
    containLabel: false,
  }
}

// ── Area Gradient Factory ────────────────────────────────────

/** Create an area gradient fill for area/line charts */
export function makeAreaGradient(color: string, _opacity = 0.15) {
  return {
    type: 'linear' as const,
    x: 0, y: 0, x2: 0, y2: 1,
    colorStops: [
      { offset: 0, color: color },
      { offset: 1, color: 'rgba(255,255,255,0)' },
    ],
  }
}

// ── Mark Line Defaults ───────────────────────────────────────

/** Average reference line */
export function makeAverageMarkLine(value: number, label = '均值') {
  return {
    silent: true,
    symbol: 'none',
    lineStyle: { type: 'dashed' as const, color: '#94A3B8', width: 1 },
    label: { formatter: label, color: '#94A3B8', fontSize: 11 },
    data: [{ yAxis: value, name: label }],
  }
}

// ── Chart Background Pattern ─────────────────────────────────

/** Subtle dot grid pattern for chart backgrounds */
export const DOT_GRID_PATTERN = {
  type: 'pattern' as const,
  repeat: 'repeat',
  image: '',
  backgroundColor: 'transparent',
}

// ── Re-export Aliases (back compat) ─────────────────────────

export const BLUE_GRADIENT = FOREST_GREEN_GRADIENT
export const ROSE_GRADIENT = AMBER_RED_GRADIENT
export const BLUE_H_GRADIENT = FOREST_H_GRADIENT

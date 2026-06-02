/** 格式化为百分比 */
export function toPercent(v: number, decimals = 1): string {
  return (v * 100).toFixed(decimals) + '%'
}

/** 格式化为千分位 */
export function toThousands(v: number): string {
  return v.toLocaleString('zh-CN')
}

/** 格式化为人民币 */
export function toCNY(v: number): string {
  return '¥' + v.toFixed(1)
}

/** 保留 n 位小数 */
export function toFixed(v: number, n = 4): string {
  return v.toFixed(n)
}

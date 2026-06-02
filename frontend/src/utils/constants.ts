/** 中文列名到前端字段名的映射 */
export const COLUMN_MAP: Record<string, string> = {
  '使用平台时间_月': 'tenure',
  '常用登陆设备': 'loginDevice',
  '城市等级': 'cityTier',
  '仓库到顾客地址': 'warehouseDistance',
  '婚姻情况': 'maritalStatus',
  '年龄分组': 'ageGroup',
  '性别': 'gender',
  '使用App时间_时': 'appUsageHours',
  '上月订单数量单': 'orderCount',
  '订单数量较去年增加_单': 'orderDelta',
  '距上次下单天数_天': 'daysSinceLastOrder',
  '上月客户的首选订单类别': 'preferredCategory',
  '用户关注的主播数量': 'streamerFollowed',
  '顾客对服务的满意度': 'satisfaction',
  '上月投诉次数': 'complaintCount',
  '上月使用的优惠劵数量_张': 'couponUsed',
  '上月平均折扣金额': 'avgDiscount',
}

/** 表单字段定义（预测页使用） */
export interface FieldDef {
  key: string
  label: string
  type: 'number' | 'select'
  options?: string[]
  min?: number
  max?: number
  default?: string | number
}

export const FIELD_DEFS: FieldDef[] = [
  { key: '使用平台时间_月', label: '使用平台时间（月）', type: 'number', min: 0, default: 12 },
  { key: '常用登陆设备', label: '常用登陆设备', type: 'select', options: ['Mobile Phone', 'Phone', 'Pad'], default: 'Mobile Phone' },
  { key: '城市等级', label: '城市等级', type: 'number', min: 1, max: 3, default: 3 },
  { key: '仓库到顾客地址', label: '仓库到顾客地址', type: 'number', min: 0, default: 8 },
  { key: '婚姻情况', label: '婚姻情况', type: 'select', options: ['Single', 'Married', 'Divorced'], default: 'Single' },
  { key: '年龄分组', label: '年龄分组', type: 'number', min: 1, max: 5, default: 3 },
  { key: '性别', label: '性别', type: 'select', options: ['Male', 'Female'], default: 'Male' },
  { key: '使用App时间_时', label: '使用App时间（时）', type: 'number', min: 0, max: 5, default: 5 },
  { key: '上月订单数量单', label: '上月订单数量', type: 'number', min: 0, default: 3 },
  { key: '订单数量较去年增加_单', label: '订单较去年增减', type: 'number', default: -2 },
  { key: '距上次下单天数_天', label: '距上次下单天数', type: 'number', min: 0, default: 30 },
  { key: '上月客户的首选订单类别', label: '首选订单类别', type: 'select', options: [
    'Laptop & Accessory', 'Household', 'Fashion', 'Mobile Phone', 'Grocery', 'Others',
  ], default: 'Laptop & Accessory' },
  { key: '用户关注的主播数量', label: '关注主播数量', type: 'number', min: 0, default: 5 },
  { key: '顾客对服务的满意度', label: '满意度评分', type: 'number', min: 1, max: 5, default: 3 },
  { key: '上月投诉次数', label: '上月投诉次数', type: 'number', min: 0, default: 1 },
  { key: '上月使用的优惠劵数量_张', label: '优惠券使用数', type: 'number', min: 0, default: 0 },
  { key: '上月平均折扣金额', label: '平均折扣金额', type: 'number', min: 0, default: 120.5 },
]

/** 风险等级颜色映射 — Donezo design system */
export const RISK_COLORS: Record<string, string> = {
  low: '#22C55E',
  medium: '#F59E0B',
  high: '#EF4444',
  critical: '#DC2626',
}

/** 风险等级中文标签 */
export const RISK_LABELS: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '极高风险',
}

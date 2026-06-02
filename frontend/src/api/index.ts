import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/** 整体数据摘要 */
export interface SummaryResponse {
  total_customers: number
  churn_rate: number
  avg_discount: number
  churned_count: number
  tenure_churn_distribution: Array<{
    tenure_bin: string
    total: number
    churned: number
    churn_rate: number
  }>
  category_churn: Array<{
    category: string
    churn_rate: number
  }>
}

export function fetchSummary(): Promise<SummaryResponse> {
  return http.get('/summary').then(r => r.data)
}

/** 模型指标 */
export interface ModelMetricsResponse {
  best_model: string
  models: Record<string, {
    accuracy: number
    precision: number
    recall: number
    f1: number
    roc_auc: number
  }>
}

export function fetchModelMetrics(): Promise<ModelMetricsResponse> {
  return http.get('/model/metrics').then(r => r.data)
}

/** 特征重要性 */
export interface FeatureImportance {
  name: string
  importance: number
  shap_mean?: number
}

export function fetchFeatureImportance(): Promise<{
  model_name: string
  importance_type: string
  features: FeatureImportance[]
}> {
  return http.get('/model/importance').then(r => r.data)
}

/** 聚类分析 */
export interface ClusterInfo {
  id: number
  size: number
  pct: number
  churn_rate: number
  label: string
}

export interface ClustersResponse {
  n_clusters: number
  silhouette_score: number
  clusters: ClusterInfo[]
  scatter_data: Array<{
    x: number
    y: number
    cluster: number
    churn: number
  }>
}

export function fetchClusters(): Promise<ClustersResponse> {
  return http.get('/clusters').then(r => r.data)
}

/** 关联规则 */
export interface RuleItem {
  antecedents: string
  consequents: string
  support: number
  confidence: number
  lift: number
}

export interface RulesResponse {
  rules: RuleItem[]
  loss_related: RuleItem[]
}

export function fetchRules(): Promise<RulesResponse> {
  return http.get('/rules').then(r => r.data)
}

/** 预测 */
export interface PredictionInput {
  [key: string]: string | number
}

export interface PredictionResult {
  churn_probability: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  predicted_class: number
  model: string
}

export function predict(input: PredictionInput): Promise<PredictionResult> {
  return http.post('/predict', input).then(r => r.data)
}

/** 特征分布 */
export interface DistributionResponse {
  feature: string
  type: 'numeric' | 'categorical'
  bins?: Array<{ x: number; total: number; churned: number; not_churned: number }>
  categories?: Array<{ category: string; total: number; churned: number }>
}

export function fetchDistribution(featureName: string): Promise<DistributionResponse> {
  return http.get(`/data/distribution/${encodeURIComponent(featureName)}`).then(r => r.data)
}

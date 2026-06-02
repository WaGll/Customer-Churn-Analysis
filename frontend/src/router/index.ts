import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/overview',
    },
    {
      path: '/overview',
      name: 'Overview',
      component: () => import('@/views/OverviewView.vue'),
      meta: { title: '分析概览' },
    },
    {
      path: '/prediction',
      name: 'Prediction',
      component: () => import('@/views/PredictionView.vue'),
      meta: { title: '流失预测' },
    },
    {
      path: '/segmentation',
      name: 'Segmentation',
      component: () => import('@/views/SegmentationView.vue'),
      meta: { title: '客户分群' },
    },
    {
      path: '/features',
      name: 'Features',
      component: () => import('@/views/FeaturesView.vue'),
      meta: { title: '特征归因' },
    },
    {
      path: '/rules',
      name: 'Rules',
      component: () => import('@/views/RulesView.vue'),
      meta: { title: '关联规则' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { title: '404' },
    },
  ],
})

export default router

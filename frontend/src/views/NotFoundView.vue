<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

const route = useRoute()
const currentPath = computed(() => route.fullPath)
</script>

<template>
  <div class="not-found">
    <div class="not-found-content">
      <AppIcon name="search" :size="48" class="not-found-icon" />
      <h2 class="not-found-title">404</h2>
      <p class="not-found-desc">页面未找到</p>
      <p class="not-found-path">访问的路径 <code>{{ currentPath }}</code> 不存在</p>
      <el-button type="primary" size="large" @click="$router.push('/overview')">
        <AppIcon name="home" :size="18" style="margin-right:6px" />
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.not-found-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.not-found-icon {
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.not-found-title {
  font-size: 64px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
  line-height: 1;
}

.not-found-desc {
  font-size: 18px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.not-found-path {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.not-found-path code {
  background: var(--color-bg-page);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: var(--font-family-mono);
  font-size: 13px;
}
</style>

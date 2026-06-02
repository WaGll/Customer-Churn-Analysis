<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from './AppIcon.vue'

const route = useRoute()

const lastRefreshed = ref<Date | null>(null)
const isRefreshing = ref(false)

const breadcrumbs = computed(() => {
  const items = [{ title: '首页', path: '/overview' }]
  const metaTitle = route.meta?.title as string | undefined
  if (metaTitle && route.path !== '/overview') {
    items.push({ title: metaTitle, path: route.path })
  }
  return items
})

const todayLabel = computed(() => {
  const d = new Date()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekdays[d.getDay()]}`
})

function handleRefresh() {
  isRefreshing.value = true
  lastRefreshed.value = new Date()
  setTimeout(() => { isRefreshing.value = false }, 600)
  window.location.reload()
}

const searchPlaceholder = '搜索特征、客户、规则...'
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <!-- Breadcrumb -->
      <nav class="breadcrumb" aria-label="面包屑导航">
        <template v-for="(item, idx) in breadcrumbs" :key="item.path">
          <router-link
            :to="item.path"
            class="breadcrumb-item"
            :class="{ current: idx === breadcrumbs.length - 1 }"
          >
            {{ item.title }}
          </router-link>
          <span v-if="idx < breadcrumbs.length - 1" class="breadcrumb-sep">
            <AppIcon name="arrow-right" :size="12" />
          </span>
        </template>
      </nav>
      <!-- Date label -->
      <span class="today-label">{{ todayLabel }}</span>
    </div>

    <div class="header-right">
      <!-- Search -->
      <div class="header-search">
        <AppIcon name="search" :size="16" class="search-icon" />
        <input
          type="text"
          :placeholder="searchPlaceholder"
          class="search-input"
        />
        <kbd class="search-shortcut">⌘K</kbd>
      </div>

      <!-- Refresh -->
      <button class="header-btn" title="刷新数据" @click="handleRefresh">
        <AppIcon name="bolt" :size="18" :class="{ 'spin-once': isRefreshing }" />
      </button>

      <!-- Last updated -->
      <span v-if="lastRefreshed" class="last-updated">
        更新于 {{ lastRefreshed.toLocaleTimeString('zh-CN') }}
      </span>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 28px;
  background: var(--header-bg);
  border-bottom: 1px solid var(--sidebar-divider);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
}
.breadcrumb-item {
  font-size: 13px;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--transition-fast);
}
.breadcrumb-item:hover {
  color: var(--color-text-secondary);
}
.breadcrumb-item.current {
  color: var(--color-text-primary);
  font-weight: 600;
}
.breadcrumb-sep {
  display: flex;
  align-items: center;
  color: var(--color-text-muted);
  opacity: 0.5;
}

.today-label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: var(--font-family-mono);
  letter-spacing: 0.2px;
}

/* Search */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-search {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F1F5F9;
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  padding: 7px 16px;
  width: 280px;
  transition: background var(--transition-fast),
              border-color var(--transition-fast),
              box-shadow var(--transition-fast);
}
.header-search:focus-within {
  border-color: var(--color-border-subtle);
  background: #FFFFFF;
  box-shadow: var(--shadow-soft);
}
.search-icon {
  flex-shrink: 0;
  color: var(--color-text-muted);
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text-primary);
  font-size: 13px;
  font-family: var(--font-family-sans);
}
.search-input::placeholder {
  color: var(--color-text-muted);
}
.search-shortcut {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  font-size: 11px;
  font-family: var(--font-family-mono);
  color: var(--color-text-muted);
  background: rgba(15, 23, 42, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  line-height: 1;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color var(--transition-fast),
              border-color var(--transition-fast),
              background var(--transition-fast);
  position: relative;
  flex-shrink: 0;
}
.header-btn:hover {
  color: var(--color-text-primary);
  border-color: var(--color-primary-light);
  background: var(--color-bg-page);
}

/* Notification dot */
.notification-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #EF4444;
  border: 1px solid #FFFFFF;
}

.last-updated {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: var(--font-family-mono);
  white-space: nowrap;
}
</style>

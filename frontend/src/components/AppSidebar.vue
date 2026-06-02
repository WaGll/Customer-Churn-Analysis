<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import AppIcon from './AppIcon.vue'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const backendStatus = ref<'checking' | 'online' | 'offline'>('checking')

onMounted(async () => {
  try {
    await axios.get('/api/summary', { timeout: 3000 })
    backendStatus.value = 'online'
  } catch {
    backendStatus.value = 'offline'
  }
})

const menuItems = [
  { path: '/overview', title: '分析概览', icon: 'chart-bar' },
  { path: '/prediction', title: '流失预测', icon: 'target' },
  { path: '/segmentation', title: '客户分群', icon: 'users' },
  { path: '/features', title: '特征归因', icon: 'trending-up' },
  { path: '/rules', title: '关联规则', icon: 'link' },
]

function navigate(path: string) {
  router.push(path)
}

const statusIcon = computed(() => {
  if (backendStatus.value === 'online') return 'check-circle'
  if (backendStatus.value === 'offline') return 'x-circle'
  return 'server'
})

const statusLabel = computed(() => {
  if (backendStatus.value === 'checking') return '检测中...'
  if (backendStatus.value === 'online') return 'API 在线'
  return 'API 离线'
})
</script>

<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- Brand -->
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <AppIcon name="shield" :size="20" />
      </div>
      <div v-show="!collapsed" class="sidebar-brand">
        <h1 class="sidebar-title">客户流失分析平台</h1>
        <p class="sidebar-subtitle">Customer Churn Analysis</p>
      </div>
      <button
        class="collapse-btn"
        @click="collapsed = !collapsed"
        :title="collapsed ? '展开侧边栏' : '折叠侧边栏'"
      >
        <AppIcon name="arrow-right" :size="16" :style="{ transform: collapsed ? '' : 'rotate(180deg)', transition: 'transform var(--transition-normal)' }" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav" role="navigation">
      <div class="nav-section-label" v-show="!collapsed">分析模块</div>
      <div
        v-for="item in menuItems"
        :key="item.path"
        :class="['nav-item', { active: route.path === item.path }]"
        @click="navigate(item.path)"
        role="menuitem"
        :tabindex="0"
        :title="collapsed ? item.title : ''"
        @keydown.enter="navigate(item.path)"
        @keydown.space.prevent="navigate(item.path)"
      >
        <span class="nav-active-indicator" />
        <span class="nav-icon">
          <AppIcon :name="item.icon" :size="20" />
        </span>
        <span v-show="!collapsed" class="nav-title">{{ item.title }}</span>
      </div>
    </nav>

    <!-- Footer — Donezo dark gradient API card -->
    <div class="sidebar-footer">
      <div
        v-if="!collapsed"
        class="api-card"
      >
        <div class="api-card-top">
          <AppIcon :name="statusIcon" :size="14" class="api-status-icon" />
          <span class="api-label">{{ statusLabel }}</span>
          <span class="api-dot" :class="'dot-' + backendStatus" />
        </div>
        <p class="api-title">系统健康检查</p>
        <p class="api-desc">实时监控后端服务状态</p>
      </div>
      <div
        v-else
        class="api-card-collapsed"
        :title="statusLabel"
      >
        <span class="api-dot" :class="'dot-' + backendStatus" />
      </div>
    </div>

    <!-- Footer fade mask -->
    <div class="sidebar-footer-mask" v-show="!collapsed" />
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  background: var(--color-bg-sidebar);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  user-select: none;
  border-right: 1px solid var(--sidebar-border);
  transition: width var(--transition-slow), min-width var(--transition-slow);
  overflow: hidden;
  position: relative;
}
.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
  min-width: var(--sidebar-collapsed-width);
}

/* Brand */
.sidebar-header {
  padding: 18px 12px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  flex-shrink: 0;
}
.sidebar-brand { min-width: 0; }
.sidebar-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
  line-height: 1.3;
  white-space: nowrap;
}
.sidebar-subtitle {
  font-size: 10px;
  color: var(--sidebar-text-muted);
  margin: 1px 0 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 8px 10px;
  overflow-y: auto;
}
.nav-section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--sidebar-text-muted);
  padding: 8px 12px 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--sidebar-text);
  transition: all var(--transition-normal);
  font-size: 14px;
  outline: none;
  margin-bottom: 1px;
  position: relative;
}
.nav-item:hover {
  background: var(--color-bg-sidebar-hover);
}
.nav-item:focus-visible {
  box-shadow: 0 0 0 2px var(--color-primary-light);
  outline: none;
}
.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-text-active);
  font-weight: 600;
}

/* Active left indicator bar */
.nav-active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 3px 3px 0;
  background: #0F4A28;
  opacity: 0;
  transition: opacity var(--transition-normal), height var(--transition-normal);
}
.nav-item.active .nav-active-indicator { opacity: 1; }

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  opacity: 0.55;
}
.nav-item:hover .nav-icon { opacity: 0.75; }
.nav-item.active .nav-icon { opacity: 1; }
.nav-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Footer — Donezo dark gradient API card */
.sidebar-footer {
  padding: 0 12px 16px;
  display: flex;
  flex-direction: column;
}

.api-card {
  background: linear-gradient(135deg, #061F11 0%, #0F4A28 100%);
  border: 1px solid rgba(74, 222, 128, 0.12);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  color: #fff;
  position: relative;
  z-index: 1;
}

/* Footer fade mask — smooth transition from nav to footer */
.sidebar-footer-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 24px;
  background: linear-gradient(to top, var(--color-bg-sidebar), transparent);
  pointer-events: none;
  z-index: 0;
}
.api-card-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.api-status-icon { opacity: 0.8; }
.api-label {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.9;
}
.api-dot {
  margin-left: auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-online {
  background: #4ADE80;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
  animation: pulse-green 2s ease-in-out infinite;
}
.dot-offline {
  background: #EF4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
}
.dot-checking {
  background: #F59E0B;
  animation: pulse-green 1.2s ease-in-out infinite;
}
@keyframes pulse-green {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}
.api-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 2px;
}
.api-desc {
  font-size: 10px;
  opacity: 0.6;
  margin: 0;
}

.api-card-collapsed {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--sidebar-border);
  background: transparent;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-left: auto;
  flex-shrink: 0;
}
.collapse-btn:hover {
  color: var(--sidebar-text);
  border-color: var(--color-border);
  background: var(--color-bg-sidebar-hover);
}
</style>

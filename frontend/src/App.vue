<script setup lang="ts">
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <div class="app-right">
      <AppHeader />
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="page-slide-up" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  background: var(--color-bg-page);
}

body {
  font-family: var(--font-family-sans);
  background: var(--color-bg-page);
  color: var(--color-text-primary);
}

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Page transitions — defined in transitions.css (page-slide-up) */
</style>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.app-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-page-padding);
  padding-bottom: 40px;
  background: var(--color-bg-page);
}
</style>

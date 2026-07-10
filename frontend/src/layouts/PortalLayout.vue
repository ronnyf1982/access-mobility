<template>
  <div class="portal-layout">
    <AppSidebar />
    <div class="portal-right">
      <AppTopbar />
      <main class="portal-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
</script>

<style scoped>
.portal-layout {
  display: flex;
  min-height: 100vh;
  background: var(--am-bg-base);
}

.portal-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* verhindert Overflow durch Flex-Kind */
  margin-left: var(--am-sidebar-width);
}

.portal-content {
  flex: 1;
  padding: var(--am-space-l);
  overflow-y: auto;
}
</style>

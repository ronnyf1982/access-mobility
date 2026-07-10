<template>
  <div class="public-layout">
    <PublicHeader />
    <main class="public-main">
      <RouterView />
    </main>
    <PublicFooter />
  </div>
</template>

<script setup lang="ts">
import PublicHeader from '@/components/layout/PublicHeader.vue'
import PublicFooter from '@/components/layout/PublicFooter.vue'
</script>

<style scoped>
.public-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.public-main {
  flex: 1;
}
</style>

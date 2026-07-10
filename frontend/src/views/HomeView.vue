<template>
  <!-- Dev-Hilfsmittel: API Health Check. Nicht im Router, nicht in der Navigation. -->
  <div style="padding: 2rem; font-family: monospace;">
    <p>API: <strong>{{ status }}</strong></p>
    <button @click="check" style="margin-top: 1rem; cursor: pointer;">Prüfen</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '@/api/client'

const status = ref('–')

async function check() {
  try {
    await apiClient.get('/health')
    status.value = '✓ ok'
  } catch {
    status.value = '✗ nicht erreichbar'
  }
}
</script>

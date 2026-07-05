<template>
  <div class="home-wrapper">
    <div class="home-content">
      <div class="home-header">
        <h1 class="home-title">access-mobility</h1>
        <p class="home-subtitle">Barrierefreie Mobilitätsplattform</p>
      </div>

      <Card class="health-card">
        <template #title>API-Verbindung</template>
        <template #subtitle>Backend auf http://localhost:8010</template>
        <template #content>
          <div class="health-status">
            <Tag
              v-if="status === 'ok'"
              severity="success"
              value="API erreichbar"
              icon="pi pi-check-circle"
            />
            <Tag
              v-else-if="status === 'error'"
              severity="danger"
              value="API nicht erreichbar"
              icon="pi pi-times-circle"
            />
            <Tag
              v-else-if="status === 'loading'"
              severity="info"
              value="Verbinde..."
              icon="pi pi-spin pi-spinner"
            />
            <span v-else class="idle-hint">Noch nicht geprüft.</span>
          </div>

          <Button
            label="API-Status prüfen"
            icon="pi pi-refresh"
            :loading="status === 'loading'"
            class="health-button"
            @click="checkHealth"
          />
        </template>
      </Card>

      <p class="sprint-badge">Sprint 1 — Grundgerüst</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import apiClient from '@/api/client'
import type { ApiStatus } from '@/stores/app'

const toast = useToast()
const status = ref<ApiStatus>('idle')

async function checkHealth() {
  status.value = 'loading'
  try {
    await apiClient.get('/health')
    status.value = 'ok'
    toast.add({ severity: 'success', summary: 'Verbunden', detail: 'API antwortet korrekt.', life: 3000 })
  } catch {
    status.value = 'error'
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'API nicht erreichbar. Backend gestartet?', life: 5000 })
  }
}
</script>

<style scoped>
.home-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--p-surface-ground);
}

.home-content {
  width: 100%;
  max-width: 480px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.home-header {
  text-align: center;
}

.home-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  color: var(--p-primary-color);
}

.home-subtitle {
  margin: 0;
  color: var(--p-text-muted-color);
}

.health-status {
  min-height: 2rem;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.idle-hint {
  color: var(--p-text-muted-color);
  font-size: 0.9rem;
}

.health-button {
  width: 100%;
}

.sprint-badge {
  text-align: center;
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
  margin: 0;
}
</style>

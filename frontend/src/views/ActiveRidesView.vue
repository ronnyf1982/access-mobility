<template>
  <div class="ar-view">
    <h1 class="ar-view__title">Aktive Fahrten</h1>

    <!-- Laden -->
    <div v-if="loading" class="ar-view__loading" aria-live="polite">
      <span class="pi pi-spin pi-spinner" aria-hidden="true"></span>
      Lädt…
    </div>

    <!-- Fehler -->
    <div v-else-if="loadError" class="ar-view__error" role="alert">
      <span class="pi pi-exclamation-triangle" aria-hidden="true"></span>
      {{ loadError }}
    </div>

    <!-- Keine aktiven Fahrten -->
    <div v-else-if="activeRides.length === 0" class="ar-view__empty" role="status">
      <span class="pi pi-check-circle ar-view__empty-icon" aria-hidden="true"></span>
      <p>Derzeit haben Sie keine aktiven Fahrten.</p>
      <RouterLink to="/spontaneous-ride" class="ar-view__cta">
        <span class="pi pi-bolt" aria-hidden="true"></span>
        Spontane Fahrt buchen
      </RouterLink>
    </div>

    <!-- Liste aktiver Fahrten -->
    <ul v-else class="ar-view__list">
      <li v-for="ride in activeRides" :key="ride.id" class="ar-view__card">

        <!-- Status-Zeile -->
        <div class="ar-view__status-row">
          <span class="ar-view__status-badge" :class="statusBadgeClass(ride.status)">
            <span class="pi" :class="statusBadgeIcon(ride.status)" aria-hidden="true"></span>
            {{ TRANSPORT_REQUEST_STATUS_LABELS[ride.status] ?? ride.status }}
          </span>
          <span v-if="ride.is_spontaneous" class="ar-view__type-chip">
            <span class="pi pi-bolt" aria-hidden="true"></span>
            Spontan
          </span>
        </div>

        <!-- Spontane Fahrt -->
        <template v-if="ride.is_spontaneous">
          <div class="ar-view__pickup">
            <span class="pi pi-map-marker" aria-hidden="true"></span>
            <span v-if="ride.pickup_latitude != null" class="ar-view__coords">
              Aktueller Standort des Fahrgasts
              <small>{{ ride.pickup_latitude.toFixed(4) }}, {{ ride.pickup_longitude?.toFixed(4) ?? '' }}</small>
            </span>
            <span v-else-if="ride.pickup_address">{{ ride.pickup_address }}</span>
            <span v-else>Standort nicht angegeben</span>
          </div>
          <div class="ar-view__meta">
            <span class="pi pi-clock" aria-hidden="true"></span>
            Angefragt: {{ formatDateTime(ride.created_at) }}
          </div>
          <RouterLink to="/spontaneous-ride" class="ar-view__btn ar-view__btn--primary">
            <span class="pi pi-map" aria-hidden="true"></span>
            Tracking öffnen
          </RouterLink>
        </template>

        <!-- Geplante Fahrt -->
        <template v-else>
          <div class="ar-view__route">
            <div class="ar-view__pickup">
              <span class="pi pi-map-marker" aria-hidden="true"></span>
              {{ ride.pickup_address ?? 'Abholadresse nicht angegeben' }}
            </div>
            <div v-if="ride.destination_address" class="ar-view__destination">
              <span class="pi pi-flag" aria-hidden="true"></span>
              {{ ride.destination_address }}
            </div>
          </div>
          <div v-if="ride.pickup_date" class="ar-view__meta">
            <span class="pi pi-calendar" aria-hidden="true"></span>
            {{ formatDate(ride.pickup_date) }}
            <span v-if="ride.pickup_time"> · {{ ride.pickup_time }}</span>
          </div>
          <RouterLink to="/transport-requests" class="ar-view__btn ar-view__btn--secondary">
            <span class="pi pi-arrow-right" aria-hidden="true"></span>
            Details anzeigen
          </RouterLink>
        </template>

      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getTransportRequests } from '@/api/transportRequests'
import type { TransportRequestListItem, TransportRequestStatus } from '@/types'
import { TRANSPORT_REQUEST_STATUS_LABELS } from '@/types'

const ACTIVE_STATUSES = new Set<TransportRequestStatus>([
  'spontaneous_requested',
  'assigned',
  'requested',
])

const allRides = ref<TransportRequestListItem[]>([])
const loading = ref(true)
const loadError = ref<string | null>(null)

const activeRides = computed(() =>
  allRides.value.filter(r => ACTIVE_STATUSES.has(r.status as TransportRequestStatus))
)

onMounted(async () => {
  try {
    allRides.value = await getTransportRequests()
  } catch {
    loadError.value = 'Fahrten konnten nicht geladen werden. Bitte Seite neu laden.'
  } finally {
    loading.value = false
  }
})

function statusBadgeClass(status: string): string {
  if (status === 'assigned') return 'ar-view__status-badge--active'
  if (status === 'spontaneous_requested' || status === 'requested') return 'ar-view__status-badge--waiting'
  return ''
}

function statusBadgeIcon(status: string): string {
  if (status === 'assigned') return 'pi-car'
  if (status === 'spontaneous_requested') return 'pi-spin pi-spinner'
  if (status === 'requested') return 'pi-clock'
  return 'pi-circle'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('de-DE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  })
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('de-DE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.ar-view {
  max-width: 720px;
}

.ar-view__title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.ar-view__loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--am-text-secondary);
  padding: 2rem 0;
}

.ar-view__error {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: #fca5a5;
}

.ar-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 0;
  text-align: center;
  color: var(--am-text-secondary);
}

.ar-view__empty-icon {
  font-size: 2.5rem;
  color: var(--am-success, #22c55e);
  opacity: 0.6;
}

.ar-view__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.2rem;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.ar-view__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ar-view__card {
  background: var(--am-bg-card);
  border: 1px solid var(--am-border);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

/* Status-Zeile */
.ar-view__status-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ar-view__status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.75rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  color: #d4d4d4;
}

.ar-view__status-badge--waiting {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
  color: #93c5fd;
}

.ar-view__status-badge--active {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.ar-view__type-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid rgba(251, 191, 36, 0.35);
  color: #fde68a;
  font-weight: 600;
}

/* Abholpunkt / Route */
.ar-view__pickup,
.ar-view__destination {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.88rem;
  color: var(--am-text-primary);
}

.ar-view__coords {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.ar-view__coords small {
  font-size: 0.78em;
  opacity: 0.7;
}

.ar-view__route {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.ar-view__meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: var(--am-text-secondary);
}

/* Buttons */
.ar-view__btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.1rem;
  border-radius: 6px;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  align-self: flex-start;
  margin-top: 0.25rem;
  transition: opacity 0.15s, background 0.15s;
}

.ar-view__btn--primary {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.ar-view__btn--primary:hover {
  opacity: 0.88;
}

.ar-view__btn--secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #d4d4d4;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.ar-view__btn--secondary:hover {
  background: rgba(255, 255, 255, 0.13);
}
</style>

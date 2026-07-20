<template>
  <div class="sr-view">
    <h1 class="sr-view__title">Spontane Fahrt buchen</h1>

    <!-- Hinweis: Sprint 12B — noch keine Buchung -->
    <div class="sr-view__notice" role="note">
      <span class="pi pi-info-circle" aria-hidden="true"></span>
      <span>
        <strong>Vorschau:</strong> Buchung und Fahrerannahme folgen im nächsten Sprint.
        Hier sehen Sie bereits, welche Fahrzeuge in Ihrer Nähe verfügbar sind.
      </span>
    </div>

    <!-- Schritt 1: Standortfreigabe -->
    <section v-if="phase === 'idle'" class="sr-view__section">
      <p class="sr-view__intro">
        Um passende Fahrzeuge in Ihrer Nähe zu finden, benötigen wir Ihren aktuellen Standort.
        Der Standort wird <strong>nur für diese Suche</strong> verwendet und nicht dauerhaft gespeichert.
      </p>
      <button class="sr-view__btn sr-view__btn--primary" @click="requestLocation">
        <span class="pi pi-map-marker" aria-hidden="true"></span>
        Jetzt Standort freigeben und suchen
      </button>
    </section>

    <!-- Ladezustand Geolocation -->
    <section v-else-if="phase === 'locating'" class="sr-view__section sr-view__section--centered">
      <span class="pi pi-spin pi-spinner sr-view__spinner" aria-hidden="true"></span>
      <p>Standort wird ermittelt …</p>
    </section>

    <!-- Fehler Geolocation -->
    <section v-else-if="phase === 'geo-error'" class="sr-view__section">
      <div class="sr-view__error" role="alert">
        <span class="pi pi-exclamation-triangle" aria-hidden="true"></span>
        <span>{{ geoErrorMessage }}</span>
      </div>
      <button class="sr-view__btn sr-view__btn--secondary" @click="reset">
        Erneut versuchen
      </button>
    </section>

    <!-- Suche läuft -->
    <section v-else-if="phase === 'searching'" class="sr-view__section sr-view__section--centered">
      <span class="pi pi-spin pi-spinner sr-view__spinner" aria-hidden="true"></span>
      <p>Verfügbare Fahrzeuge werden gesucht …</p>
    </section>

    <!-- Ergebnisse -->
    <section v-else-if="phase === 'results'" class="sr-view__section">
      <div class="sr-view__location-info">
        <span class="pi pi-map-marker" aria-hidden="true"></span>
        Ihr Standort: {{ pickupLat?.toFixed(4) }}, {{ pickupLon?.toFixed(4) }}
        <button class="sr-view__btn-link" @click="reset">Neue Suche</button>
      </div>

      <!-- Karte -->
      <SpontaneousRideMap
        v-if="pickupLat !== null && pickupLon !== null"
        :pickup-lat="pickupLat"
        :pickup-lon="pickupLon"
        :matches="matches"
        class="sr-view__map"
      />
      <p class="sr-view__map-note">
        Karte zeigt verfügbare Fahrzeuge (Demo-Positionen, kein Echtzeit-GPS).
      </p>

      <!-- Keine Ergebnisse -->
      <div v-if="matches.length === 0" class="sr-view__empty" role="status">
        <span class="pi pi-inbox" aria-hidden="true"></span>
        <p>Derzeit sind keine passenden Fahrzeuge verfügbar. Bitte später erneut versuchen.</p>
      </div>

      <!-- Ergebnisliste -->
      <ul v-else class="sr-view__list" aria-label="Verfügbare Fahrzeuge">
        <li v-for="m in matches" :key="m.vehicle_id" class="sr-view__list-item">
          <div class="sr-list-item">
            <div class="sr-list-item__header">
              <span class="sr-list-item__icon pi pi-car" aria-hidden="true"></span>
              <strong class="sr-list-item__name">{{ m.vehicle_label }}</strong>
              <span class="sr-list-item__type">{{ vehicleTypeLabel(m.vehicle_type) }}</span>
            </div>
            <dl class="sr-list-item__details">
              <div class="sr-list-item__detail-row">
                <dt>Entfernung</dt>
                <dd>ca. {{ m.distance_km.toFixed(1) }} km</dd>
              </div>
              <div class="sr-list-item__detail-row">
                <dt>Geschätzte Ankunft</dt>
                <dd>ca. {{ m.estimated_arrival_minutes }} Min.</dd>
              </div>
              <div v-if="m.matched_capabilities.length" class="sr-list-item__detail-row">
                <dt>Passende Ausstattung</dt>
                <dd>{{ m.matched_capabilities.join(' · ') }}</dd>
              </div>
              <div class="sr-list-item__detail-row">
                <dt>Fahrer</dt>
                <dd>{{ m.driver_display_name }}</dd>
              </div>
            </dl>
            <button class="sr-view__btn sr-view__btn--disabled" disabled aria-disabled="true">
              <span class="pi pi-lock" aria-hidden="true"></span>
              Auswählen (folgt in Sprint 12C)
            </button>
          </div>
        </li>
      </ul>

      <!-- Suchergebnis-Fehler -->
      <div v-if="searchError" class="sr-view__error" role="alert">
        <span class="pi pi-exclamation-triangle" aria-hidden="true"></span>
        <span>{{ searchError }}</span>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SpontaneousRideMap from '@/components/SpontaneousRideMap.vue'
import { findSpontaneousMatches } from '@/api/spontaneous'
import type { SpontaneousRideMatchResult } from '@/types'
import { VEHICLE_TYPE_LABELS } from '@/types'

type Phase = 'idle' | 'locating' | 'geo-error' | 'searching' | 'results'

const phase = ref<Phase>('idle')
const pickupLat = ref<number | null>(null)
const pickupLon = ref<number | null>(null)
const matches = ref<SpontaneousRideMatchResult[]>([])
const geoErrorMessage = ref('')
const searchError = ref('')

function vehicleTypeLabel(type: string): string {
  return VEHICLE_TYPE_LABELS[type as keyof typeof VEHICLE_TYPE_LABELS] ?? type
}

function reset(): void {
  phase.value = 'idle'
  pickupLat.value = null
  pickupLon.value = null
  matches.value = []
  geoErrorMessage.value = ''
  searchError.value = ''
}

async function searchMatches(lat: number, lon: number): Promise<void> {
  phase.value = 'searching'
  searchError.value = ''
  try {
    matches.value = await findSpontaneousMatches({
      pickup_latitude: lat,
      pickup_longitude: lon,
    })
    phase.value = 'results'
  } catch {
    searchError.value = 'Die Suche konnte nicht abgeschlossen werden. Bitte erneut versuchen.'
    phase.value = 'results'
  }
}

function requestLocation(): void {
  if (!navigator.geolocation) {
    geoErrorMessage.value = 'Ihr Browser unterstützt keine Standortermittlung.'
    phase.value = 'geo-error'
    return
  }
  phase.value = 'locating'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      pickupLat.value = pos.coords.latitude
      pickupLon.value = pos.coords.longitude
      searchMatches(pos.coords.latitude, pos.coords.longitude)
    },
    (err) => {
      if (err.code === GeolocationPositionError.PERMISSION_DENIED) {
        geoErrorMessage.value =
          'Standortzugriff wurde verweigert. Bitte erlauben Sie den Standortzugriff in den Browser-Einstellungen.'
      } else if (err.code === GeolocationPositionError.POSITION_UNAVAILABLE) {
        geoErrorMessage.value = 'Standort nicht verfügbar. Bitte später erneut versuchen.'
      } else {
        geoErrorMessage.value = 'Standortermittlung fehlgeschlagen. Bitte erneut versuchen.'
      }
      phase.value = 'geo-error'
    },
    { timeout: 10000, maximumAge: 60000 },
  )
}
</script>

<style scoped>
.sr-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

.sr-view__title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.sr-view__notice {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  background: var(--p-blue-50, #eff6ff);
  border: 1px solid var(--p-blue-200, #bfdbfe);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
}

.sr-view__section {
  margin-bottom: 1.5rem;
}

.sr-view__section--centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 0;
}

.sr-view__intro {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.sr-view__spinner {
  font-size: 2rem;
  color: var(--p-primary-color, #3b82f6);
}

.sr-view__btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.sr-view__btn--primary {
  background: var(--p-primary-color, #3b82f6);
  color: #fff;
}

.sr-view__btn--primary:hover {
  opacity: 0.9;
}

.sr-view__btn--secondary {
  background: var(--p-surface-100, #f1f5f9);
  color: var(--p-text-color, #1e293b);
  border: 1px solid var(--p-surface-border, #dee2e6);
}

.sr-view__btn--disabled {
  background: var(--p-surface-200, #e2e8f0);
  color: var(--p-text-muted-color, #94a3b8);
  cursor: not-allowed;
  font-size: 0.85rem;
}

.sr-view__btn-link {
  background: none;
  border: none;
  color: var(--p-primary-color, #3b82f6);
  cursor: pointer;
  padding: 0;
  margin-left: 0.75rem;
  text-decoration: underline;
  font-size: 0.9rem;
}

.sr-view__error {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  background: var(--p-red-50, #fef2f2);
  border: 1px solid var(--p-red-200, #fecaca);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  color: var(--p-red-700, #b91c1c);
}

.sr-view__location-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--p-text-muted-color, #64748b);
  margin-bottom: 0.75rem;
}

.sr-view__map {
  margin-bottom: 0.5rem;
}

.sr-view__map-note {
  font-size: 0.78rem;
  color: var(--p-text-muted-color, #94a3b8);
  margin-bottom: 1rem;
}

.sr-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--p-text-muted-color, #64748b);
  font-size: 0.9rem;
}

.sr-view__empty .pi {
  font-size: 2rem;
}

.sr-view__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sr-list-item {
  background: var(--p-surface-0, #fff);
  border: 1px solid var(--p-surface-border, #dee2e6);
  border-radius: 8px;
  padding: 1rem;
}

.sr-list-item__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.sr-list-item__icon {
  color: var(--p-primary-color, #3b82f6);
  font-size: 1.1rem;
}

.sr-list-item__name {
  font-size: 1rem;
}

.sr-list-item__type {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #64748b);
  background: var(--p-surface-100, #f1f5f9);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.sr-list-item__details {
  margin: 0 0 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.sr-list-item__detail-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.88rem;
}

.sr-list-item__detail-row dt {
  color: var(--p-text-muted-color, #64748b);
  min-width: 9rem;
}

.sr-list-item__detail-row dd {
  margin: 0;
}
</style>
